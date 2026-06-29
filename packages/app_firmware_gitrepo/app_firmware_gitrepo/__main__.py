"""Run the firmware Git repo app on its own."""

from __future__ import annotations

import sys

from satcore import run_standalone

from .plugin import FirmwareGitRepoPlugin


def main() -> int:
    return run_standalone(FirmwareGitRepoPlugin())


if __name__ == "__main__":
    sys.exit(main())