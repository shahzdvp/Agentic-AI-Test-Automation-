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
    source: Path = typer.Argument(..., help="Source file to test", exists=True, dir_okay=False),
    output: Path | None = typer.Option(None, "--output", "-o", help="Output directory"),
    model: str = typer.Option("gemini-3.6-flash", "--model", "-m", help="Model name"),
    max_retries: int = typer.Option(3, "--max-retries", "-r", help="Maximum generation retries"),
    verbose: bool = typer.Option(False, "--verbose", "-v", help="Enable verbose logging")
):
    """Generate tests for a given Python file."""
    setup_logging(verbose)

    if output:
        output.mkdir(parents=True, exist_ok=True)
    else:
        output = source.parent

    try:
        settings = get_settings()
    except Exception as e:
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

    typer.secho(f"Generating tests for {source}...", fg=typer.colors.BLUE)
    stats = orchestrator.process_file(source, output)

    if stats["tests_passed"] > 0:
        typer.secho(
            f"Success! Generated {stats['tests_passed']} tests (retries: {stats['retries_used']})",
            fg=typer.colors.GREEN
        )
    elif stats["tests_generated"] > 0:
        typer.secho(
            f"Partial success. Generated {stats['tests_generated']} tests but they failed to pass.",
            fg=typer.colors.YELLOW
        )
    else:
        typer.secho("Failed to generate passing tests.", fg=typer.colors.RED)
        raise typer.Exit(1)

@app.command()
def version():
    """Print the version of AI TestGen."""
    from ai_testgen import __version__
    typer.echo(f"AI TestGen version {__version__}")

if __name__ == "__main__":
    app()
