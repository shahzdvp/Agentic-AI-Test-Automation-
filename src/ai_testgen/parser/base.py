from abc import ABC, abstractmethod
from dataclasses import dataclass
from pathlib import Path


@dataclass
class CodeUnit:
    """Represents a single extractable code unit (function or class)."""
    name: str
    unit_type: str  # 'function' or 'class'
    code: str
    docstring: str | None
    line_number: int

class BaseCodeParser(ABC):
    """Abstract base class for source code parsers."""

    @abstractmethod
    def parse(self, file_path: Path) -> list[CodeUnit]:
        """Parse a source file and return a list of extractable code units."""
        ...

    @abstractmethod
    def parse_source(self, source_code: str) -> list[CodeUnit]:
        """Parse source code string and return a list of extractable code units."""
        ...
