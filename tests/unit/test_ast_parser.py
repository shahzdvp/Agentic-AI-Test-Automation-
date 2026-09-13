from pathlib import Path

from ai_testgen.parser.ast_parser import PythonASTParser


def test_parse_simple_function():
    parser = PythonASTParser()
    source = "def my_func():\n    pass\n"
    units = parser.parse_source(source)
    assert len(units) == 1
    assert units[0].name == "my_func"
    assert units[0].unit_type == "function"

def test_parse_class():
    parser = PythonASTParser()
    source = "class MyClass:\n    pass\n"
    units = parser.parse_source(source)
    assert len(units) == 1
    assert units[0].name == "MyClass"
    assert units[0].unit_type == "class"

def test_parse_multiple_units():
    parser = PythonASTParser()
    source = "def func1(): pass\ndef func2(): pass\nclass Cls1: pass\n"
    units = parser.parse_source(source)
    assert len(units) == 3

def test_parse_skips_private_functions():
    parser = PythonASTParser()
    source = "def _private_func(): pass\n"
    units = parser.parse_source(source)
    assert len(units) == 0

def test_parse_keeps_dunder_init():
    parser = PythonASTParser()
    source = "class MyClass:\n    def __init__(self): pass\n"
    units = parser.parse_source(source)
    assert len(units) == 1
    assert units[0].name == "MyClass"
    assert units[0].unit_type == "class"

def test_parse_empty_source():
    parser = PythonASTParser()
    units = parser.parse_source("")
    assert len(units) == 0

def test_parse_syntax_error():
    parser = PythonASTParser()
    units = parser.parse_source("def oops(:\n")
    assert len(units) == 0

def test_parse_captures_docstring():
    parser = PythonASTParser()
    source = 'def my_func():\n    """My docstring."""\n    pass\n'
    units = parser.parse_source(source)
    assert len(units) == 1
    assert units[0].docstring == "My docstring."

def test_parse_file(tmp_path: Path):
    parser = PythonASTParser()
    test_file = tmp_path / "test_source.py"
    test_file.write_text("def my_func():\n    pass\n", encoding="utf-8")
    units = parser.parse(test_file)
    assert len(units) == 1
    assert units[0].name == "my_func"
