"""Plugin entry point for the firmware Git repo app."""

from __future__ import annotations

from PySide6.QtWidgets import QWidget

from satcore import AppPlugin

from .widget import FirmwareGitRepoWidget


class FirmwareGitRepoPlugin(AppPlugin):
    id = "firmware_gitrepo"
    title = "Прошивка из Git"
    order = 15  # Между Comms (10) и Firmware (20)

    def create_widget(self, parent: QWidget | None = None) -> QWidget:
        return FirmwareGitRepoWidget(parent)