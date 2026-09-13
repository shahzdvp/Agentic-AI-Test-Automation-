
from pydantic import BaseModel, Field


class GeneratedTestCase(BaseModel):
    """A single generated test case."""
    name: str = Field(description="Name of the test function, e.g. test_add_positive_numbers")
    docstring: str = Field(description="Brief description of what this test verifies")
    code: str = Field(description="Complete executable pytest function code including the def line")
    is_edge_case: bool = Field(default=False, description="Whether this targets an edge or boundary condition")

class GeneratedTestSuite(BaseModel):
    """A complete generated test suite for a module."""
    module_name: str = Field(description="Name of the source module being tested")
    required_imports: list[str] = Field(description="List of import lines needed, e.g. ['import pytest', 'from math import sqrt']")
    fixtures: list[str] = Field(default_factory=list, description="Optional pytest fixture code snippets")
    test_cases: list[GeneratedTestCase] = Field(description="List of generated test cases")
