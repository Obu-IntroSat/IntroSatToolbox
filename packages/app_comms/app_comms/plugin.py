"""Plugin entry point for the COM interaction app."""

from __future__ import annotations

from PySide6.QtWidgets import QWidget

from satcore import AppPlugin

from .widget import CommsWidget


class CommsPlugin(AppPlugin):
    id = "comms"
    title = "Взаимодействие"
    order = 10

    def create_widget(self, parent: QWidget | None = None) -> QWidget:
        return CommsWidget(parent)
