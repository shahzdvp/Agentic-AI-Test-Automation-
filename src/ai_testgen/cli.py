import sys
from pathlib import Path

import typer
from loguru import logger

from ai_testgen.config import get_settings
from ai_testgen.generator.langchain_gen import LangChainTestGenerator
from ai_testgen.orchestrator.pipeline import FrameworkOrchestrator
from ai_testgen.parser.ast_parser import PythonASTParser
from ai_testgen.runner.pytest_runner import PytestRunner

app = typer.Typer(help="AI-Powered Test Automation Framework")

def setup_logging(verbose: bool):
    """Configure loguru logging."""
    logger.remove()
    level = "DEBUG" if verbose else "INFO"
    logger.add(sys.stderr, level=level)

@app.command()
def generate(
    source: Path = typer.Argument(..., help="Source file or directory to test", exists=True, dir_okay=True),
    output: Path | None = typer.Option(None, "--output", "-o", help="Output directory"),
    model: str = typer.Option("gemini-3.6-flash", "--model", "-m", help="Model name"),
    max_retries: int = typer.Option(3, "--max-retries", "-r", help="Maximum generation retries"),
    verbose: bool = typer.Option(False, "--verbose", "-v", help="Enable verbose logging")
):
    """Generate tests for a given Python file or an entire directory."""
    setup_logging(verbose)

    if output:
        output.mkdir(parents=True, exist_ok=True)
    else:
        output = source.parent if source.is_file() else source

    try:
        settings = get_settings()
    except Exception:
        typer.secho("Failed to load configuration. Check GOOGLE_API_KEY.", fg=typer.colors.RED)
        raise typer.Exit(1)

    parser = PythonASTParser()
    generator = LangChainTestGenerator(
        model_name=model,
        api_key=settings.google_api_key,
        temperature=settings.temperature
    )
    runner = PytestRunner()

    orchestrator = FrameworkOrchestrator(
        parser=parser,
        generator=generator,
        runner=runner,
        max_retries=max_retries
    )

    if source.is_file():
        files_to_process = [source]
    else:
        ignore_dirs = {".git", "venv", ".venv", "build", "htmlcov", "node_modules", ".pytest_cache", ".ruff_cache"}
        files_to_process = [
            f for f in source.rglob("*.py")
            if f.is_file() 
            and not f.name.startswith("test_") 
            and f.name != "__init__.py"
            and not any(part in ignore_dirs for part in f.parts)
        ]
        
    if not files_to_process:
        typer.secho(f"No valid Python files found in {source}", fg=typer.colors.YELLOW)
        raise typer.Exit(0)

    total_stats = {"total_units": 0, "tests_generated": 0, "tests_passed": 0, "retries_used": 0}

    for file_path in files_to_process:
        typer.secho(f"Generating tests for {file_path}...", fg=typer.colors.BLUE)
        stats = orchestrator.process_file(file_path, output)
        for k in total_stats:
            total_stats[k] += stats.get(k, 0)

    if total_stats["tests_passed"] > 0:
        typer.secho(
            f"\nSuccess! Generated {total_stats['tests_passed']} tests across {len(files_to_process)} files (total retries: {total_stats['retries_used']})",
            fg=typer.colors.GREEN
        )
    elif total_stats["tests_generated"] > 0:
        typer.secho(
            f"\nPartial success. Generated {total_stats['tests_generated']} tests but they failed to pass.",
            fg=typer.colors.YELLOW
        )
    else:
        typer.secho("\nFailed to generate any passing tests.", fg=typer.colors.RED)
        raise typer.Exit(1)

@app.command()
def version():
    """Print the version of AI TestGen."""
    from ai_testgen import __version__
    typer.echo(f"AI TestGen version {__version__}")

if __name__ == "__main__":
    app()
