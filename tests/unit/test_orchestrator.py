from pathlib import Path
from unittest.mock import MagicMock

import pytest

from ai_testgen.orchestrator.pipeline import FrameworkOrchestrator
from ai_testgen.parser.base import CodeUnit
from ai_testgen.schemas import GeneratedTestCase, GeneratedTestSuite


@pytest.fixture
def mocks():
    parser = MagicMock()
    generator = MagicMock()
    runner = MagicMock()
    return parser, generator, runner

def test_process_file_success(mocks, tmp_path: Path):
    parser, generator, runner = mocks

    # Setup mocks
    parser.parse.return_value = [CodeUnit(name="func1", unit_type="function", code="def func1(): pass", docstring=None, line_number=1)]
    generator.generate.return_value = GeneratedTestSuite(
        module_name="dummy", required_imports=[],
        test_cases=[GeneratedTestCase(name="test_1", docstring="", code="def test_1(): pass")]
    )
    runner.run_tests.return_value = (True, "")

    orchestrator = FrameworkOrchestrator(parser, generator, runner)

    dummy_file = tmp_path / "dummy.py"
    dummy_file.write_text("def func1(): pass", encoding="utf-8")

    stats = orchestrator.process_file(dummy_file, tmp_path)

    assert stats["tests_passed"] == 1
    assert stats["retries_used"] == 0
    assert (tmp_path / "test_dummy.py").exists()

def test_process_file_retry_on_failure(mocks, tmp_path: Path):
    parser, generator, runner = mocks

    parser.parse.return_value = [CodeUnit(name="func1", unit_type="function", code="def func1(): pass", docstring=None, line_number=1)]
    generator.generate.return_value = GeneratedTestSuite(
        module_name="dummy", required_imports=[],
        test_cases=[GeneratedTestCase(name="test_1", docstring="", code="def test_1(): pass")]
    )
    runner.run_tests.side_effect = [(False, "error"), (True, "")]

    orchestrator = FrameworkOrchestrator(parser, generator, runner)

    dummy_file = tmp_path / "dummy.py"
    dummy_file.write_text("def func1(): pass", encoding="utf-8")

    stats = orchestrator.process_file(dummy_file, tmp_path)

    assert stats["tests_passed"] == 1
    assert stats["retries_used"] == 1
    assert (tmp_path / "test_dummy.py").exists()

def test_process_file_no_units(mocks, tmp_path: Path):
    parser, generator, runner = mocks

    parser.parse.return_value = []

    orchestrator = FrameworkOrchestrator(parser, generator, runner)

    dummy_file = tmp_path / "dummy.py"
    dummy_file.write_text("", encoding="utf-8")

    stats = orchestrator.process_file(dummy_file, tmp_path)

    assert stats["total_units"] == 0
    assert not (tmp_path / "test_dummy.py").exists()

def test_process_file_generation_error(mocks, tmp_path: Path):
    parser, generator, runner = mocks

    parser.parse.return_value = [CodeUnit(name="func1", unit_type="function", code="def func1(): pass", docstring=None, line_number=1)]
    generator.generate.side_effect = Exception("Generation failed")

    orchestrator = FrameworkOrchestrator(parser, generator, runner)

    dummy_file = tmp_path / "dummy.py"
    dummy_file.write_text("def func1(): pass", encoding="utf-8")

    stats = orchestrator.process_file(dummy_file, tmp_path)

    assert stats["tests_passed"] == 0
    assert not (tmp_path / "test_dummy.py").exists()
