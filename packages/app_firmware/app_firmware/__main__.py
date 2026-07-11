"""Run the firmware flashing app on its own."""

from __future__ import annotations

import sys

from satcore import run_standalone

from app_firmware.plugin import FirmwarePlugin


def main() -> int:
    return run_standalone(FirmwarePlugin())


if __name__ == "__main__":
    sys.exit(main())
