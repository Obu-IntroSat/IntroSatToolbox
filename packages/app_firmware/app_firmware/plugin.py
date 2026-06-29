"""Plugin entry point for the firmware flashing app."""

from __future__ import annotations

from PySide6.QtWidgets import QWidget

from satcore import AppPlugin

from .widget import FirmwareWidget


class FirmwarePlugin(AppPlugin):
    id = "firmware"
    title = "Прошивка"
    order = 20

    def create_widget(self, parent: QWidget | None = None) -> QWidget:
        return FirmwareWidget(parent)
