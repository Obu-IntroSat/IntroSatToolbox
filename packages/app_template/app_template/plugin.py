"""Plugin entry point for a new app.

To make a real app from this template:
  1. Set a unique ``id`` and a ``title`` (shown on the tab).
  2. Pick an ``order`` to control where the tab appears.
  3. Build your UI in widget.py.
"""

from __future__ import annotations

from PySide6.QtWidgets import QWidget

from satcore import AppPlugin

from .widget import TemplateWidget


class TemplatePlugin(AppPlugin):
    id = "template"
    title = "Шаблон"
    order = 1000

    def create_widget(self, parent: QWidget | None = None) -> QWidget:
        return TemplateWidget(parent)
