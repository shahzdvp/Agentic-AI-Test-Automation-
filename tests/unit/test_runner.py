import subprocess
from unittest.mock import patch

import pytest

from ai_testgen.runner.pytest_runner import PytestRunner


@pytest.fixture
def temp_dir(tmp_path):
    return tmp_path


def test_runner_success(temp_dir):
    """Test the runner when pytest succeeds."""
    runner = PytestRunner()
    test_code = "def test_pass():\n    assert True"

    with patch("subprocess.run") as mock_run:
        mock_run.return_value = subprocess.CompletedProcess(
            args=["pytest"], returncode=0, stdout="1 passed", stderr=""
        )

        passed, output = runner.run_tests(test_code, temp_dir)

        assert passed is True
        assert "1 passed" in output
        mock_run.assert_called_once()
        # Verify it passed the temp file correctly
        args = mock_run.call_args[0][0]
        assert "pytest" in args
        assert str(temp_dir / "test_temp_auto_generated.py") in args


def test_runner_failure(temp_dir):
    """Test the runner when pytest fails."""
    runner = PytestRunner()

    with patch("subprocess.run") as mock_run:
        mock_run.return_value = subprocess.CompletedProcess(
            args=["pytest"], returncode=1, stdout="F", stderr="1 failed"
        )

        passed, output = runner.run_tests("def test_fail(): assert False", temp_dir)

        assert passed is False
        assert "1 failed" in output


def test_runner_timeout(temp_dir):
    """Test the runner when execution times out."""
    runner = PytestRunner()

    with patch("subprocess.run") as mock_run:
        mock_run.side_effect = subprocess.TimeoutExpired(cmd="pytest", timeout=30)

        passed, output = runner.run_tests("test", temp_dir)

        assert passed is False
        assert "timed out" in output


def test_runner_exception(temp_dir):
    """Test the runner when an unexpected exception occurs."""
    runner = PytestRunner()

    with patch("subprocess.run") as mock_run:
        mock_run.side_effect = Exception("OS Error")

        passed, output = runner.run_tests("test", temp_dir)

        assert passed is False
        assert "OS Error" in output
