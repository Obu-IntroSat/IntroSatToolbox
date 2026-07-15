"""UI module for camera application."""

from .main_window import CameraWidget
from .widgets import ZoomableImageLabel
from .dialogs import CreateConfigDialog

__all__ = [
    "CameraWidget",
    "ZoomableImageLabel",
    "CreateConfigDialog",
]