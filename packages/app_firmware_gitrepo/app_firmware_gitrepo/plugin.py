"""Plugin entry point for the firmware Git repo app."""

from __future__ import annotations

import sys
from pathlib import Path

from PySide6.QtWidgets import QWidget


def setup_satcore_path():
    if getattr(sys, 'frozen', False):
        app_dir = Path(sys.executable).parent

        possible_paths = [
            app_dir / "packages" / "core",
            app_dir.parent / "packages" / "core",
            app_dir / "core",
            app_dir / ".." / "packages" / "core",
        ]

        for path in possible_paths:
            if path.exists():
                path_str = str(path)
                if path_str not in sys.path:
                    sys.path.insert(0, path_str)
                    print(f"[DEBUG] Added satcore from plugin: {path}")
                return

        print("[DEBUG] satcore path not found from plugin")


setup_satcore_path()

try:
    from satcore import AppPlugin
except ImportError as e:
    print(f"[ERROR] Failed to import satcore: {e}")
    print(f"[DEBUG] sys.path: {sys.path}")
    raise

from .widget import FirmwareGitRepoWidget


class FirmwareGitRepoPlugin(AppPlugin):
    id = "firmware_gitrepo"
    title = "Прошивка из Git"
    order = 15

    def create_widget(self, parent: QWidget | None = None) -> QWidget:
        return FirmwareGitRepoWidget(parent)