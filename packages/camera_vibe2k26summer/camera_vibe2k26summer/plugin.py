"""Plugin entry point for the camera app."""

from __future__ import annotations
from PySide6.QtWidgets import QWidget
from satcore import AppPlugin
from .widget import CameraWidget

class CameraPlugin(AppPlugin):
    id = "camera_vibe2k26summer"
    title = "📷 CAMERA VIBE2K26SUMMER"
    order = 30

    def create_widget(self, parent: QWidget | None = None) -> QWidget:
        return CameraWidget(parent)