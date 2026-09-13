from pathlib import Path
from unittest.mock import MagicMock, patch

from ai_testgen.runner.pytest_runner import PytestRunner


@patch("ai_testgen.runner.pytest_runner.logger")
def test_runner_unlink_error(mock_logger, tmp_path):
    runner = PytestRunner()

    with patch("subprocess.run") as mock_run:
        mock_run.return_value = MagicMock(returncode=0, stdout="pass", stderr="")

        with patch.object(Path, 'unlink', side_effect=OSError("Permission denied")):
            runner.run_tests("test", tmp_path)

    mock_logger.warning.assert_called()
