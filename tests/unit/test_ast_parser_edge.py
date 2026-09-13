from unittest.mock import patch

from ai_testgen.parser.ast_parser import PythonASTParser


@patch("ai_testgen.parser.ast_parser.logger")
def test_ast_parser_syntax_error(mock_logger, tmp_path):
    parser = PythonASTParser()
    bad_file = tmp_path / "bad.py"
    bad_file.write_text("def foo( :  # invalid python")

    units = parser.parse(bad_file)
    assert len(units) == 0
    mock_logger.error.assert_called()

def test_ast_parser_skips_private():
    parser = PythonASTParser()
    source = "def _private(): pass\nclass _PrivateClass: pass"
    units = parser.parse_source(source)
    assert len(units) == 0

def test_ast_parser_handles_empty_class():
    parser = PythonASTParser()
    source = "class MyClass:\n    pass"
    units = parser.parse_source(source)
    assert len(units) == 1
    assert units[0].unit_type == "class"
