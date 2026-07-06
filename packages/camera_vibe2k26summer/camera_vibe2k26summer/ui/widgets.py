"""Custom UI widgets for camera application."""

from typing import Optional

from PySide6.QtCore import Qt
from PySide6.QtGui import QPixmap, QWheelEvent
from PySide6.QtWidgets import QLabel


class ZoomableImageLabel(QLabel):
    """QLabel с поддержкой зума колесиком мыши"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self._pixmap: Optional[QPixmap] = None
        self._zoom = 1.0
        self._min_zoom = 0.1
        self._max_zoom = 10.0
        self.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.setMinimumHeight(300)
        self.setScaledContents(False)
        self.setObjectName("image_label")
        self.setText("Нет изображения")
    
    def set_image(self, pixmap: QPixmap):
        self._pixmap = pixmap
        self._zoom = 1.0
        self.update_display()
    
    def update_display(self):
        if self._pixmap is None:
            self.setText("Нет изображения")
            return
        
        scaled = self._pixmap.scaled(
            int(self._pixmap.width() * self._zoom),
            int(self._pixmap.height() * self._zoom),
            Qt.AspectRatioMode.KeepAspectRatio,
            Qt.TransformationMode.SmoothTransformation
        )
        self.setPixmap(scaled)
    
    def wheelEvent(self, event: QWheelEvent):
        if self._pixmap is None:
            return
        
        delta = event.angleDelta().y()
        self._zoom *= 1.1 if delta > 0 else 0.9
        self._zoom = max(self._min_zoom, min(self._max_zoom, self._zoom))
        self.update_display()
    
    def set_zoom(self, zoom: float):
        self._zoom = max(self._min_zoom, min(self._max_zoom, zoom))
        self.update_display()
    
    def get_zoom(self) -> float:
        return self._zoom
    
    def reset_zoom(self):
        self._zoom = 1.0
        self.update_display()
    
    def clear(self):
        self._pixmap = None
        self.setText("Нет изображения")