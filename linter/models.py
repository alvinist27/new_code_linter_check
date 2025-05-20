"""Module defining dataclasses for linter check."""

from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True, kw_only=True, slots=True)
class DiffChange:
    """Information about changed lines in the file."""

    start_line: int
    end_line: int

    def contains(self, line_number: int) -> bool:
        """Checks if the line number is within the range of changes.

        Args:
            line_number: number of diff change line.

        Returns:
            True if line_number in diff change and False if not.
        """
        return self.start_line <= line_number <= self.end_line


@dataclass(frozen=True, kw_only=True, slots=True)
class LinterError:
    """Information about errors detected by the linter."""

    file_path: Path
    line: int
    code: str
    message: str
    linter_name: str
    severity: str = ''

    def __str__(self) -> str:
        """Return string representation of the LinterError objects.

        Returns:
            Description of error detected by the linter.
        """
        return f'{self.linter_name} {self.file_path}: {self.line} {self.severity} {self.code}\n{self.message}\n'
