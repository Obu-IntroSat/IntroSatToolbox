"""Run the camera app on its own."""

from __future__ import annotations
import sys
from satcore import run_standalone
from .plugin import CameraPlugin

def main() -> int:
    return run_standalone(CameraPlugin())

if __name__ == "__main__":
    sys.exit(main())