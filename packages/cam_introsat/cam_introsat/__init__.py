"""Camera application for Introsat."""

__version__ = "0.1.0"

from .plugin import CameraPlugin
from .ui.main_window import CameraWidget

__all__ = ["CameraPlugin", "CameraWidget"]