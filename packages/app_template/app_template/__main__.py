"""Run the template app on its own."""

from __future__ import annotations

import sys

from satcore import run_standalone

from app_template.plugin import TemplatePlugin


def main() -> int:
    return run_standalone(TemplatePlugin())


if __name__ == "__main__":
    sys.exit(main())
