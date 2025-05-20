"""Module for running linter check."""

import logging

from check import LinterCheck
from parsers import MyPyReportParser, RuffReportParser

logger = logging.getLogger()
logging.basicConfig(level=logging.INFO)


def main() -> None:
    """Start Ruff and MyPy check."""
    linter_check = LinterCheck(linter_parser_classes=[RuffReportParser, MyPyReportParser])
    linter_check.start()


if __name__ == '__main__':
    main()
