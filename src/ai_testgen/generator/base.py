from abc import ABC, abstractmethod

from ai_testgen.schemas import GeneratedTestSuite


class BaseTestGenerator(ABC):
    """Abstract base class for test generators."""

    @abstractmethod
    def generate(self, source_code: str, feedback: str | None = None) -> GeneratedTestSuite:
        """Generate a test suite for the given source code."""
        ...
