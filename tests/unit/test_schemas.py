import pytest
from pydantic import ValidationError

from ai_testgen.schemas import GeneratedTestCase, GeneratedTestSuite


def test_test_case_valid():
    tc = GeneratedTestCase(
        name="test_foo",
        docstring="Test foo function.",
        code="def test_foo(): pass"
    )
    assert tc.name == "test_foo"
    assert tc.docstring == "Test foo function."
    assert tc.code == "def test_foo(): pass"

def test_test_case_defaults():
    tc = GeneratedTestCase(
        name="test_foo",
        docstring="Test foo.",
        code="def test_foo(): pass"
    )
    assert tc.is_edge_case is False

def test_test_suite_valid():
    ts = GeneratedTestSuite(
        module_name="my_mod",
        required_imports=["import os"],
        test_cases=[]
    )
    assert ts.module_name == "my_mod"
    assert ts.required_imports == ["import os"]

def test_test_suite_fixtures_default():
    ts = GeneratedTestSuite(
        module_name="my_mod",
        required_imports=[],
        test_cases=[]
    )
    assert ts.fixtures == []

def test_test_case_missing_required_field():
    with pytest.raises(ValidationError):
        GeneratedTestCase(
            docstring="Missing name.",
            code="def missing(): pass"
        )

def test_test_suite_serialization():
    ts = GeneratedTestSuite(
        module_name="my_mod",
        required_imports=[],
        test_cases=[
            GeneratedTestCase(name="test_x", docstring="desc", code="def test_x(): pass")
        ]
    )
    dumped = ts.model_dump()
    assert dumped["module_name"] == "my_mod"
    assert len(dumped["test_cases"]) == 1
    assert dumped["test_cases"][0]["name"] == "test_x"
