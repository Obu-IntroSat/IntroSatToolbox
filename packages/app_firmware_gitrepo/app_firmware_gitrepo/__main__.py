"""Run the firmware Git repo app on its own."""

from __future__ import annotations

import sys
import os
from pathlib import Path


def setup_paths():
    if getattr(sys, 'frozen', False):
        app_dir = Path(sys.executable).parent
        plugin_dir = Path(__file__).parent

        possible_paths = [
            plugin_dir.parent.parent / "core",
            plugin_dir.parent / "core",
            app_dir / "packages" / "core",
            app_dir.parent / "packages" / "core",
            app_dir / "core",
        ]

        for path in possible_paths:
            if path.exists():
                path_str = str(path)
                if path_str not in sys.path:
                    sys.path.insert(0, path_str)
                    print(f"[DEBUG] Added path from main: {path}")
                break


setup_paths()

try:
    from satcore import run_standalone
    from app_firmware_gitrepo.plugin import FirmwareGitRepoPlugin
except ImportError as e:
    print(f"[ERROR] Import error: {e}")
    print(f"[DEBUG] sys.path: {sys.path}")
    sys.exit(1)


def main() -> int:
    return run_standalone(FirmwareGitRepoPlugin())


if __name__ == "__main__":
    sys.exit(main())