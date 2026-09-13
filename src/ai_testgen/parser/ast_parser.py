import ast
from pathlib import Path

from loguru import logger

from ai_testgen.parser.base import BaseCodeParser, CodeUnit


class PythonASTParser(BaseCodeParser):
    """Parser for Python source code using the ast module."""

    def parse(self, file_path: Path) -> list[CodeUnit]:
        """Parse a source file and return a list of extractable code units."""
        logger.debug(f"Reading file: {file_path}")
        try:
            source_code = file_path.read_text(encoding='utf-8')
            return self.parse_source(source_code)
        except Exception as e:
            logger.error(f"Failed to read file {file_path}: {e}")
            return []

    def parse_source(self, source_code: str) -> list[CodeUnit]:
        """Parse source code string and return a list of extractable code units."""
        try:
            tree = ast.parse(source_code)
        except SyntaxError as e:
            logger.error(f"Syntax error while parsing source code: {e}")
            return []

        units = []
        for node in tree.body:
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                if not self._should_skip(node.name):
                    units.append(self._create_code_unit(node, "function"))
            elif isinstance(node, ast.ClassDef):
                if not self._should_skip(node.name):
                    units.append(self._create_code_unit(node, "class"))
        return units

    def _should_skip(self, name: str) -> bool:
        """Determine if a function or class should be skipped based on its name."""
        if name == "__init__":
            return False
        return name.startswith("_")

    def _create_code_unit(self, node: ast.AST, unit_type: str) -> CodeUnit:
        """Create a CodeUnit from an AST node."""
        docstring = ast.get_docstring(node)
        try:
            code = ast.unparse(node)
        except AttributeError:
            # Fallback if ast.unparse is not available (Python < 3.9) - though user requested Py3.12 conventions
            code = ""

        name = getattr(node, "name", "<unknown>")
        line_number = getattr(node, "lineno", 0)
        return CodeUnit(
            name=name,
            unit_type=unit_type,
            code=code,
            docstring=docstring,
            line_number=line_number
        )
