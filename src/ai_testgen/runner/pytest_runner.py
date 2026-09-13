import subprocess
import time
from pathlib import Path

from loguru import logger

from ai_testgen.runner.base import BaseTestRunner


class PytestRunner(BaseTestRunner):
    """Test runner using pytest via subprocess."""

    def run_tests(self, test_code: str, context_dir: Path) -> tuple[bool, str]:
        """Write test code to a file and run pytest on it."""
        temp_file = context_dir / "test_temp_auto_generated.py"
        try:
            temp_file.write_text(test_code, encoding="utf-8")

            logger.info(f"Running pytest on {temp_file}")
            start_time = time.time()

            result = subprocess.run(
                ['python', '-m', 'pytest', str(temp_file), '--tb=short', '-q'],
                capture_output=True,
                text=True,
                timeout=30
            )

            duration = time.time() - start_time
            passed = result.returncode == 0

            if passed:
                logger.info(f"Tests passed in {duration:.2f} seconds.")
                return True, result.stdout
            else:
                logger.warning(f"Tests failed in {duration:.2f} seconds.")
                return False, result.stdout + "\n" + result.stderr

        except subprocess.TimeoutExpired:
            logger.error("Test execution timed out after 30 seconds.")
            return False, "Test execution timed out."
        except Exception as e:
            logger.error(f"Error running tests: {e}")
            return False, str(e)
        finally:
            if temp_file.exists():
                try:
                    temp_file.unlink()
                except OSError as e:
                    logger.warning(f"Failed to delete temp file {temp_file}: {e}")
