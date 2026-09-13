from abc import ABC, abstractmethod
from pathlib import Path


class BaseTestRunner(ABC):
    """Abstract base class for running tests."""

    @abstractmethod
    def run_tests(self, test_code: str, context_dir: Path) -> tuple[bool, str]:
        """Run test code and return (passed, error_output)."""
        ...
