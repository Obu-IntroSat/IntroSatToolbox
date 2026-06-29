"""Minimal widget - replace the contents with your app's UI."""

from __future__ import annotations

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QLabel, QVBoxLayout, QWidget


class TemplateWidget(QWidget):
    def __init__(self, parent: QWidget | None = None):
        super().__init__(parent)

        layout = QVBoxLayout(self)
        title = QLabel("Пустая вкладка-шаблон")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)

        hint = QLabel(
            "Скопируйте папку packages/app_template, переименуйте её и пакет, "
            "затем стройте свой интерфейс здесь, в widget.py."
        )
        hint.setAlignment(Qt.AlignmentFlag.AlignCenter)
        hint.setWordWrap(True)

        layout.addStretch(1)
        layout.addWidget(title)
        layout.addWidget(hint)
        layout.addStretch(1)
