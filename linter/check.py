"""Module for checking modified code with a linter."""

import logging
import sys
from collections import defaultdict
from pathlib import Path

from models import DiffChange, LinterError
from parsers import DiffParser, ReportParser

logger = logging.getLogger()
logging.basicConfig(level=logging.INFO)


class LinterCheck:
    """Class for checking modified code with a linter."""

    def __init__(self, linter_parser_classes: list[type[ReportParser]]) -> None:
        """Initialize LinterCheck object.

        Args:
            linter_parser_class: Parser class instance for linter check.
        """
        self._linter_parser_classes = linter_parser_classes
        self._errors_found: list[LinterError] = []

    def start(self) -> None:
        """Run linter check."""
        logger.info('- Diff parsing is started!')
        changes = DiffParser().parse()
        for linter_parser_class in self._linter_parser_classes:
            logger.info(f'+ Linter check {linter_parser_class.__name__} is started!\n')
            linter_errors = linter_parser_class().parse()
            self._check_affected_linter_errors(changes=changes, linter_errors=linter_errors)
        self.represent_linter_errors()

    def represent_linter_errors(self) -> None:
        """Display errors detected by the linter objects in modified lines."""
        if not self._errors_found:
            logger.info('✓ Linter check is passed\n')
            return None
        logger.error('❌ Linter errors:\n')
        for linter_error in self._errors_found:
            logger.error(f'- {linter_error}')
        logger.error('❌ Linter check is failed!\n')
        sys.exit(1)

    def _check_affected_linter_errors(
        self,
        changes: defaultdict[Path, list[DiffChange]],
        linter_errors: list[LinterError],
    ) -> None:
        """Check for occurrences of errors in modified lines.

        Args:
            changes: mapping changes of file name and list of DiffChange objects.
            linter_errors: list of errors detected by the linter.
        """
        linter_errors_by_file = defaultdict(list)
        for linter_error in linter_errors:
            linter_errors_by_file[linter_error.file_path].append(linter_error)
        for file_path, file_changes in changes.items():
            for linter_error in linter_errors_by_file.get(file_path, []):
                if any(change.contains(linter_error.line) for change in file_changes):
                    self._errors_found.append(linter_error)
