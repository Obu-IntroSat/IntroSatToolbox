"""Run a single app plugin as a standalone window."""

from __future__ import annotations

import sys

from PySide6.QtWidgets import QApplication, QMainWindow

from .plugin import AppPlugin


def run_standalone(plugin: AppPlugin, width: int = 900, height: int = 600) -> int:
    """Open one plugin in its own top-level window.

    Used by each app's ``__main__`` so a developer can run only their app.
    """
    app = QApplication.instance() or QApplication(sys.argv)
    window = QMainWindow()
    window.setWindowTitle(plugin.title)
    window.setCentralWidget(plugin.create_widget())
    window.resize(width, height)
    window.show()
    return app.exec()
