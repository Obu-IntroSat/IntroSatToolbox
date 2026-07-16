"""Plugin entry point for the firmware Git repo app."""

from __future__ import annotations

import sys
from pathlib import Path

from PySide6.QtWidgets import QWidget


def setup_satcore_path():
    if getattr(sys, 'frozen', False):
        plugin_dir = Path(__file__).parent
        packages_dir = plugin_dir.parent.parent

        core_path = packages_dir / "core"
        if core_path.exists():
            path_str = str(core_path)
            if path_str not in sys.path:
                sys.path.insert(0, path_str)
                print(f"[DEBUG] Added satcore from plugin: {core_path}")
            return

        app_dir = Path(sys.executable).parent
        alt_core_path = app_dir / "packages" / "core"
        if alt_core_path.exists():
            path_str = str(alt_core_path)
            if path_str not in sys.path:
                sys.path.insert(0, path_str)
                print(f"[DEBUG] Added satcore from app_dir: {alt_core_path}")
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