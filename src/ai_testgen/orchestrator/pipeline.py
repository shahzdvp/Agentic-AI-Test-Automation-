import time
from pathlib import Path
from typing import Any

from loguru import logger

from ai_testgen.generator.base import BaseTestGenerator
from ai_testgen.parser.base import BaseCodeParser
from ai_testgen.runner.base import BaseTestRunner
from ai_testgen.schemas import GeneratedTestSuite


class FrameworkOrchestrator:
    """Orchestrates the parsing, generation, and running of tests."""

    def __init__(
        self,
        parser: BaseCodeParser,
        generator: BaseTestGenerator,
        runner: BaseTestRunner,
        max_retries: int = 3
    ):
        self.parser = parser
        self.generator = generator
        self.runner = runner
        self.max_retries = max_retries

    def process_file(self, target_file: Path, output_dir: Path) -> dict[str, Any]:
        """Process a source file by generating tests for each parsed unit."""
        logger.info(f"Processing file: {target_file}")
        start_time = time.time()

        units = self.parser.parse(target_file)
        logger.info(f"Found {len(units)} extractable code units.")

        if not units:
            logger.warning("No code units found. Skipping.")
            return {"total_units": 0, "tests_generated": 0, "tests_passed": 0, "retries_used": 0}

        try:
            abs_target = target_file.resolve()
            rel_path = abs_target.relative_to(Path.cwd().resolve())
            module_name = ".".join(rel_path.with_suffix("").parts)
        except ValueError:
            module_name = target_file.stem

        successful_suites: list[GeneratedTestSuite] = []
        total_retries = 0

        # Process each unit granularly
        for unit in units:
            logger.info(f"Generating tests for unit: {unit.name} ({unit.unit_type})")
            
            # We pass only the unit's code to the LLM to save tokens and increase focus
            source_code = f"# Absolute Module Path: {module_name}\n# Target Unit: {unit.name}\n\n{unit.code}"
            
            feedback = None
            passed = False
            
            for attempt in range(self.max_retries + 1):
                if attempt > 0:
                    logger.info(f"Retry attempt {attempt}/{self.max_retries} for {unit.name}")
                    total_retries += 1

                try:
                    suite = self.generator.generate(source_code, feedback=feedback)
                except Exception as e:
                    logger.error(f"Generation failed for {unit.name}: {e}")
                    break

                # Test this specific suite in isolation
                temp_code = self._assemble_test_file([suite])
                passed, error_report = self.runner.run_tests(temp_code, output_dir)

                if passed:
                    logger.info(f"Tests for {unit.name} passed successfully!")
                    successful_suites.append(suite)
                    break
                else:
                    logger.debug(f"Test failure output for {unit.name}:\n{error_report}")
                    feedback = error_report

        # Combine all successful suites into the final file
        total_cases = sum(len(suite.test_cases) for suite in successful_suites)
        stats = {
            "total_units": len(units),
            "tests_generated": total_cases,
            "tests_passed": total_cases,
            "retries_used": total_retries
        }

        if successful_suites:
            final_code = self._assemble_test_file(successful_suites)
            test_file_name = f"test_{target_file.stem}.py"
            output_path = output_dir / test_file_name

            try:
                output_path.write_text(final_code, encoding="utf-8")
                logger.info(f"Successfully wrote combined test file to {output_path}")
            except Exception as e:
                logger.error(f"Failed to write test file: {e}")
        else:
            logger.error("Failed to generate passing tests for any units.")

        duration = time.time() - start_time
        logger.info(f"Processing completed in {duration:.2f} seconds.")

        return stats

    def _assemble_test_file(self, suites: list[GeneratedTestSuite]) -> str:
        """Combine multiple test suites into a single python file string."""
        imports = set()
        fixtures = []
        test_cases = []

        for suite in suites:
            for imp in suite.required_imports:
                imports.add(imp)
            for fix in suite.fixtures:
                fixtures.append(fix)
            for tc in suite.test_cases:
                test_cases.append(tc.code)

        lines = list(imports)
        lines.append("")

        if fixtures:
            lines.extend([f.replace("\\n", "\n") for f in fixtures])
            lines.append("")

        for tc_code in test_cases:
            lines.append(tc_code.replace("\\n", "\n"))
            lines.append("")

        return "\n".join(lines)
