"""Module with constants using for linter check."""

import re
from pathlib import Path

BASE_DIR = Path(__file__).resolve(strict=True).parent.parent

LINTER_DIR_PATH = BASE_DIR / 'linter'
RUFF_REPORT_FILE_PATH = LINTER_DIR_PATH / 'ruff-report.json'
CURRENT_GIT_DIFF_FILE_PATH = LINTER_DIR_PATH / 'current_diff.txt'

CHANGED_LINES_RANGE_PATTERN = re.compile(r'^@@ -\d+(?:,\d+)? \+(\d+)(?:,(\d+))? @@')
MYPY_ERROR_PARTS_PATTERN = re.compile(
    r'^(?P<file>.+?):(?P<line>\d+): (?P<severity>error|note): '
    r'(?P<message>.+?)( \[(?P<code>.+?)])?$',
)
MYPY_REPORT_STDOUT_INDEX = 0

CHANGED_FILE_NAME_GIT_DIFF_PREFIX = '+++ b/'
CHANGED_FILE_NAME_GIT_DIFF_START_INDEX = len(CHANGED_FILE_NAME_GIT_DIFF_PREFIX)
CHANGED_LINES_RANGE_DIFF_PREFIX = '@@'
