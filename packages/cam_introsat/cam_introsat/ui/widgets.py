# -*- coding: utf-8 -*-
"""
Кастомный виджет для отображения изображения с поддержкой зума колесиком мыши.
Изображение отображается внутри QScrollArea.
"""

from typing import Optional
from PySide6.QtCore import Qt
from PySide6.QtGui import QPixmap, QWheelEvent
from PySide6.QtWidgets import QLabel, QScrollArea, QWidget, QVBoxLayout


class ZoomableImageLabel(QWidget):
    """
    Виджет, содержащий QLabel внутри QScrollArea.
    Поддерживает зум колесиком мыши и кнопку "Fit".
    """
    def __init__(self, parent=None):
        super().__init__(parent)

        self.image_label = QLabel()
        self.image_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.image_label.setScaledContents(False)

        self.scroll_area = QScrollArea()
        self.scroll_area.setWidget(self.image_label)
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.scroll_area.setStyleSheet("""
            QScrollArea {
                border: 1px solid #444;
                background-color: #1a1a1a;
                border-radius: 4px;
            }
            QScrollBar:vertical {
                background: #2a2a2a;
                width: 12px;
            }
            QScrollBar::handle:vertical {
                background: #555;
                border-radius: 6px;
                min-height: 20px;
            }
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
                height: 0px;
            }
            QScrollBar:horizontal {
                background: #2a2a2a;
                height: 12px;
            }
            QScrollBar::handle:horizontal {
                background: #555;
                border-radius: 6px;
                min-width: 20px;
            }
            QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal {
                width: 0px;
            }
        """)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(self.scroll_area)

        self._pixmap: Optional[QPixmap] = None
        self._zoom = 1.0
        self._fit_zoom = 1.0

        self.setMinimumHeight(300)
        self.image_label.setText("Нет изображения")

    def set_image(self, pixmap: QPixmap):
        """Устанавливает новое изображение и подгоняет под размер."""
        self._pixmap = pixmap
        self._fit_zoom = self._calculate_fit_zoom()
        self._zoom = self._fit_zoom
        self.update_display()

    def _calculate_fit_zoom(self) -> float:
        """Вычисляет коэффициент масштаба, чтобы изображение влезло во вьюпорт."""
        if self._pixmap is None:
            return 1.0
        viewport_width = self.scroll_area.viewport().width() - 10
        viewport_height = self.scroll_area.viewport().height() - 10
        if viewport_width <= 0 or viewport_height <= 0:
            return 1.0
        zoom_w = viewport_width / self._pixmap.width()
        zoom_h = viewport_height / self._pixmap.height()
        return min(zoom_w, zoom_h, 1.0)

    def update_display(self):
        """Перерисовывает изображение с текущим коэффициентом масштаба."""
        if self._pixmap is None:
            self.image_label.setText("Нет изображения")
            self.image_label.setPixmap(QPixmap())
            return
        scaled = self._pixmap.scaled(
            int(self._pixmap.width() * self._zoom),
            int(self._pixmap.height() * self._zoom),
            Qt.AspectRatioMode.KeepAspectRatio,
            Qt.TransformationMode.SmoothTransformation
        )
        self.image_label.setPixmap(scaled)
        self.image_label.setFixedSize(scaled.size())
        self.scroll_area.updateGeometry()

    def resizeEvent(self, event):
        """При изменении размера окна пересчитываем fit-зум."""
        super().resizeEvent(event)
        if self._pixmap is not None:
            self._fit_zoom = self._calculate_fit_zoom()
            if self._zoom < self._fit_zoom:
                self._zoom = self._fit_zoom
                self.update_display()

    def wheelEvent(self, event: QWheelEvent):
        """Обработка колесика мыши: масштабирование."""
        if self._pixmap is None:
            return
        delta = event.angleDelta().y()
        self._zoom *= 1.1 if delta > 0 else 0.9
        self._zoom = max(self._fit_zoom, min(5.0, self._zoom))
        self.update_display()

    def set_zoom(self, zoom: float):
        """Устанавливает коэффициент масштаба вручную."""
        self._zoom = max(self._fit_zoom, min(5.0, zoom))
        self.update_display()

    def get_zoom(self) -> float:
        return self._zoom

    def get_fit_zoom(self) -> float:
        return self._fit_zoom

    def reset_zoom(self):
        """Сброс к fit-зуму."""
        if self._pixmap is not None:
            self._zoom = self._fit_zoom
            self.update_display()

    def clear(self):
        """Очищает виджет."""
        self._pixmap = None
        self.image_label.setText("Нет изображения")
        self.image_label.setPixmap(QPixmap())
        self.image_label.setFixedSize(100, 100)