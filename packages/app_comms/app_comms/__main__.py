"""Run the COM interaction app on its own."""

from __future__ import annotations

import sys

from satcore import run_standalone

from app_comms.plugin import CommsPlugin


def main() -> int:
    return run_standalone(CommsPlugin())


if __name__ == "__main__":
    sys.exit(main())
