"""Module defining parser classes for linter check."""

import json
from abc import ABC, abstractmethod
from collections import defaultdict
from pathlib import Path
from typing import Any

import consts
from models import DiffChange, LinterError
from mypy import api


class DiffParser:
    """Git diff parser to detect changed lines."""

    def __init__(self) -> None:
        """Initialize DiffParser object."""
        self._changes: defaultdict[Path, list[DiffChange]] = defaultdict(list)
        self._current_file: Path | None = None
        self._diff_content: str = Path(consts.CURRENT_GIT_DIFF_FILE_PATH).read_text(encoding='utf-8')

    def parse(self) -> defaultdict[Path, list[DiffChange]]:
        """Analyzes the contents of a diff.

        Returns:
            mapping changes of file name and list of DiffChange objects.
        """
        for diff_content_line in self._diff_content.split('\n'):
            self._process_line(diff_content_line)
        return self._changes

    def _process_line(self, line: str) -> None:
        """Processes single line of diff.

        Args:
            line: the diff line to be processed
        """
        if line.startswith(consts.CHANGED_FILE_NAME_GIT_DIFF_PREFIX):
            self._handle_file_line(line)
        elif line.startswith(consts.CHANGED_LINES_RANGE_DIFF_PREFIX):
            self._handle_range_line(line)

    def _handle_file_line(self, line: str) -> None:
        """Process a line with a file name.

        Args:
            line: the diff line to be processed containing file name.
        """
        self._current_file = Path(line[consts.CHANGED_FILE_NAME_GIT_DIFF_START_INDEX:].strip())

    def _handle_range_line(self, line: str) -> None:
        """Process a line with range of diff line numbers.

        Args:
            line: the diff line to be processed containing diff line numbers.
        """
        if not self._current_file:
            return
        match = consts.CHANGED_LINES_RANGE_PATTERN.match(line)
        if match:
            start_line_number = int(match.group(1))
            range_lines_count = int(match.group(2) or 1)
            self._changes[self._current_file].append(
                DiffChange(
                    start_line=start_line_number,
                    end_line=start_line_number + range_lines_count - 1,
                ),
            )


class ReportParser(ABC):
    """Abstract class for linter report parsers."""

    @abstractmethod
    def parse(self) -> list[LinterError]:
        """Parse Linter check report into a list of LinterErrors."""


class RuffReportParser(ReportParser):
    """Ruff JSON-report parser."""

    def __init__(self) -> None:
        """Initialize ReportParser object."""
        self._errors: list[LinterError] = []
        self._report_path: Path = consts.RUFF_REPORT_FILE_PATH
        self._validate_report_path()

    def parse(self) -> list[LinterError]:
        """Parse JSON into a list of errors.

        Returns:
            list of LinterError object detected by the linter.
        """
        raw_data = self._parse_json()
        self._create_linter_errors(raw_data)
        return self._errors

    def _create_linter_errors(self, raw_data: list[dict[str, Any]]) -> None:
        """Create LinterError objects.

        Args:
            raw_data: dict as list of errors
        """
        for item in raw_data:
            self._errors.append(
                LinterError(
                    file_path=Path(item['filename']).relative_to(consts.BASE_DIR),
                    line=item['location']['row'],
                    code=item['code'],
                    message=item['message'],
                    linter_name=self.__class__.__name__,
                ),
            )

    def _validate_report_path(self) -> None:
        """Validate report path from init method."""
        if not self._report_path.exists():
            raise RuntimeError(f'Файл отчета не найден: {self._report_path}')

        if not self._report_path.is_file():
            raise RuntimeError(f'Указанный путь не является файлом: {self._report_path}')

    @staticmethod
    def _parse_json() -> Any:
        """Parses JSON content of report path."""
        try:
            return json.loads(Path(consts.RUFF_REPORT_FILE_PATH).read_text(encoding='utf-8'))
        except json.JSONDecodeError as exc:
            raise RuntimeError(f'Ошибка парсинга JSON: {exc}')


class MyPyReportParser(ReportParser):
    """MyPy check report parser."""

    def __init__(self) -> None:
        """Initialize MyPyReportParser object."""
        self._errors:  list[LinterError] = []

    def parse(self) -> list[LinterError]:
        """Parse MyPy check errors into a list of errors.

        Returns:
            list of LinterError object detected by the linter.
        """
        result = api.run(['--strict', '--show-error-codes', str(consts.BASE_DIR.absolute())])
        for line in result[consts.MYPY_REPORT_STDOUT_INDEX].splitlines():
            match = consts.MYPY_ERROR_PARTS_PATTERN.match(line)
            if match:
                self._errors.append(
                    LinterError(
                        file_path=Path(match.group('file')),
                        line=int(match.group('line')),
                        severity=match.group('severity'),
                        code=match.group('code') or 'mypy',
                        message=match.group('message').strip(),
                        linter_name=self.__class__.__name__,
                    ),
                )
        return self._errors
