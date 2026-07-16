"""Run the firmware Git repo app on its own."""

from __future__ import annotations

import sys
import os
from pathlib import Path


def setup_paths():
    """Add paths to modules for frozen application."""
    if getattr(sys, 'frozen', False):
        app_dir = Path(sys.executable).parent

        possible_paths = [
            app_dir / "packages",
            app_dir.parent / "packages",
            app_dir.parent.parent / "packages",
            Path(os.path.dirname(sys.executable)) / "packages",
            app_dir / "core",
            app_dir.parent / "core",
        ]

        for path in possible_paths:
            if path.exists():
                sys.path.insert(0, str(path))
                print(f"[DEBUG] Added path: {path}")
                break

        core_path = app_dir / "packages" / "core"
        if core_path.exists():
            sys.path.insert(0, str(core_path))
            print(f"[DEBUG] Added core: {core_path}")

        satcore_path = app_dir / "packages" / "core" / "satcore"
        if satcore_path.exists():
            sys.path.insert(0, str(satcore_path.parent))
            print(f"[DEBUG] Added satcore parent: {satcore_path.parent}")


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