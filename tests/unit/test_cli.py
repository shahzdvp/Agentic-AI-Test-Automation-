from unittest.mock import MagicMock, patch

import pytest
from typer.testing import CliRunner

from ai_testgen.cli import app
from ai_testgen.config import Settings

runner = CliRunner()


@pytest.fixture
def mock_settings():
    return Settings(
        google_api_key="test_key",
        model_name="gemini-3.6-flash",
        max_retries=1,
        temperature=0.1
    )


def test_cli_version():
    """Test the version command."""
    result = runner.invoke(app, ["version"])
    assert result.exit_code == 0
    assert "AI TestGen version" in result.stdout


@patch("ai_testgen.cli.get_settings")
@patch("ai_testgen.factory.create_orchestrator")
def test_cli_generate_success(mock_orchestrator_class, mock_get_settings, mock_settings, tmp_path):
    """Test generating tests via CLI."""
    mock_get_settings.return_value = mock_settings

    mock_orchestrator = MagicMock()
    mock_orchestrator.process_file.return_value = {
        "total_units": 2,
        "tests_generated": 2,
        "tests_passed": 2,
        "retries_used": 0
    }
    mock_orchestrator_class.return_value = mock_orchestrator

    source_file = tmp_path / "target.py"
    source_file.write_text("def foo(): pass")

    output_dir = tmp_path / "out"

    result = runner.invoke(app, [
        "generate",
        str(source_file),
        "--output", str(output_dir)
    ])

    assert result.exit_code == 0
    assert "Success" in result.stdout


@patch("ai_testgen.cli.get_settings")
@patch("ai_testgen.factory.create_orchestrator")
def test_cli_generate_failure(mock_orchestrator_class, mock_get_settings, mock_settings, tmp_path):
    """Test CLI when generation fails."""
    mock_get_settings.return_value = mock_settings

    mock_orchestrator = MagicMock()
    mock_orchestrator.process_file.return_value = {
        "total_units": 1,
        "tests_generated": 1,
        "tests_passed": 0,
        "retries_used": 1
    }
    mock_orchestrator_class.return_value = mock_orchestrator

    source_file = tmp_path / "target.py"
    source_file.write_text("def foo(): pass")

    result = runner.invoke(app, ["generate", str(source_file)])

    assert result.exit_code == 1
    assert "Failed to generate passing tests" in result.stdout


@patch("ai_testgen.cli.get_settings")
def test_cli_config_error(mock_get_settings, tmp_path):
    """Test CLI behavior when API key is missing."""
    mock_get_settings.side_effect = Exception("No API key")

    source_file = tmp_path / "target.py"
    source_file.write_text("def foo(): pass")

    result = runner.invoke(app, ["generate", str(source_file)])

    assert result.exit_code == 1
    assert "Failed to load configuration" in result.stdout

@patch("ai_testgen.cli.get_settings")
@patch("ai_testgen.factory.create_orchestrator")
def test_cli_generate_partial_success(mock_orchestrator_class, mock_get_settings, mock_settings, tmp_path):
    """Test CLI partial success logging."""
    mock_get_settings.return_value = mock_settings

    mock_orchestrator = MagicMock()
    mock_orchestrator.process_file.return_value = {
        "total_units": 1,
        "tests_generated": 1,
        "tests_passed": 0,
        "retries_used": 1
    }
    mock_orchestrator_class.return_value = mock_orchestrator

    source_file = tmp_path / "target.py"
    source_file.write_text("def foo(): pass")

    result = runner.invoke(app, ["generate", str(source_file)])
    # Wait, the current logic is:
    # elif stats["tests_generated"] > 0:
    # Partial success
    assert result.exit_code == 0
    assert "Partial success" in result.stdout

@patch("ai_testgen.cli.get_settings")
@patch("ai_testgen.factory.create_orchestrator")
def test_cli_generate_failure(mock_orchestrator_class, mock_get_settings, mock_settings, tmp_path):
    """Test CLI when generation fails."""
    mock_get_settings.return_value = mock_settings

    mock_orchestrator = MagicMock()
    mock_orchestrator.process_file.return_value = {
        "total_units": 1,
        "tests_generated": 0,
        "tests_passed": 0,
        "retries_used": 1
    }
    mock_orchestrator_class.return_value = mock_orchestrator

    source_file = tmp_path / "target.py"
    source_file.write_text("def foo(): pass")

    result = runner.invoke(app, ["generate", str(source_file)])

    assert result.exit_code == 1
    assert "Failed to generate any passing tests" in result.stdout
