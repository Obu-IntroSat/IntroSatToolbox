"""Launcher window: one tab per installed app, discovered automatically."""

from __future__ import annotations

import sys
from pathlib import Path

from PySide6.QtCore import Qt
from PySide6.QtGui import QColor, QPalette
from PySide6.QtWidgets import (
    QApplication,
    QLabel,
    QMainWindow,
    QTabWidget,
)

from satcore import discover_plugins

def setup_paths():
    if getattr(sys, 'frozen', False):
        app_dir = Path(sys.executable).parent
        packages_path = app_dir / "packages"
        if packages_path.exists():
            sys.path.insert(0, str(packages_path))
            print(f"[DEBUG] Added packages path: {packages_path}")

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("IntroSat Toolbox")
        self.resize(1000, 680)

        tabs = QTabWidget()
        plugins = discover_plugins()

        if not plugins:
            tabs.addTab(
                QLabel("Не найдено ни одного приложения.\n"
                       "Установите пакеты приложений (pip install -e packages/...)."),
                "Нет приложений",
            )
        else:
            for plugin in plugins:
                try:
                    tabs.addTab(plugin.create_widget(), plugin.title)
                except Exception as exc:  # noqa: BLE001
                    tabs.addTab(QLabel(f"Ошибка загрузки: {exc}"), plugin.title)

        self.setCentralWidget(tabs)


def main() -> int:
    app = QApplication(sys.argv)

    # === ГЛОБАЛЬНЫЙ СТИЛЬ ДЛЯ ВСЕГО ПРИЛОЖЕНИЯ ===
    app.setStyle("Fusion")

    # Настройка палитры
    palette = QPalette()

    # Основные цвета
    palette.setColor(QPalette.ColorRole.Window, QColor(54, 54, 82))  # #363652
    palette.setColor(QPalette.ColorRole.WindowText, Qt.GlobalColor.white)
    palette.setColor(QPalette.ColorRole.Base, QColor(54, 54, 82))
    palette.setColor(QPalette.ColorRole.AlternateBase, QColor(44, 44, 72))
    palette.setColor(QPalette.ColorRole.Text, Qt.GlobalColor.white)
    palette.setColor(QPalette.ColorRole.Button, QColor(117, 245, 234))  # #75f5ea
    palette.setColor(QPalette.ColorRole.ButtonText, QColor(54, 54, 82))
    palette.setColor(QPalette.ColorRole.BrightText, Qt.GlobalColor.red)
    palette.setColor(QPalette.ColorRole.Highlight, QColor(117, 245, 234))
    palette.setColor(QPalette.ColorRole.HighlightedText, QColor(54, 54, 82))

    app.setPalette(palette)

    # Путь к папке с ресурсами
    resources_dir = Path(__file__).parent.parent / "resources"
    down_arrow = resources_dir / "arrow_down.png"
    up_arrow = resources_dir / "arrow_up.png"

    # Преобразуем путь в формат с прямыми слешами для QSS
    down_arrow_path = down_arrow.as_posix()
    up_arrow_path = up_arrow.as_posix()

    print(f"down_arrow_path: {down_arrow_path}")
    print(f"up_arrow_path: {up_arrow_path}")

    # Глобальные стили через QSS
    app.setStyleSheet(f"""
        /* Общий фон */
        QMainWindow, QWidget, QDialog, QGroupBox {{
            background-color: #363652;
            color: white;
        }}
        
        /* Вкладки */
        QTabWidget::pane {{
            border: 2px solid #75f5ea;
            background-color: #363652;
        }}
        QTabBar::tab {{
            background-color: #2a2a4a;
            color: white;
            padding: 8px 16px;
            margin-right: 2px;
            border-top-left-radius: 4px;
            border-top-right-radius: 4px;
        }}
        QTabBar::tab:selected {{
            background-color: #75f5ea;
            color: #363652;
            font-weight: bold;
        }}
        QTabBar::tab:hover:!selected {{
            background-color: #3a3a5a;
        }}
        
        /* ===== ВСЕ ПОЛЯ ВВОДА ===== */
        QLineEdit, QTextEdit, QPlainTextEdit {{
            background-color: #2a2a4a;
            color: white;
            border: 2px solid #75f5ea;
            border-radius: 6px;
            padding: 6px 10px;
            selection-background-color: #75f5ea;
            selection-color: #363652;
        }}
        QLineEdit:focus, QTextEdit:focus, QPlainTextEdit:focus {{
            border-color: #5dd5ca;
        }}
        
        /* ===== ВСЕ ВЫПАДАЮЩИЕ МЕНЮ ===== */
        QComboBox {{
            background-color: white;
            color: #363652;
            border: 2px solid #75f5ea;
            border-radius: 6px;
            padding: 6px 30px 6px 12px;
            min-height: 20px;
        }}
        QComboBox:hover {{
            border-color: #5dd5ca;
        }}
        QComboBox::drop-down {{
            border: none;
            width: 30px;
            background: transparent;
            subcontrol-origin: padding;
            subcontrol-position: right center;
        }}
        QComboBox::down-arrow {{
            image: url({down_arrow_path});
            width: 12px;
            height: 8px;
        }}
        QComboBox::down-arrow:on {{
            image: url({up_arrow_path});
            width: 12px;
            height: 8px;
        }}
        /* Список выпадающего меню */
        QComboBox QAbstractItemView {{
            background-color: white;
            color: #363652;
            border: 2px solid #75f5ea;
            border-radius: 6px;
            selection-background-color: #75f5ea;
            selection-color: #363652;
            padding: 4px;
            outline: none;
        }}
        QComboBox QAbstractItemView::item {{
            background-color: white;
            color: #363652;
            padding: 6px 12px;
            min-height: 20px;
        }}
        QComboBox QAbstractItemView::item:hover {{
            background-color: #75f5ea;
            color: #363652;
        }}
        QComboBox QAbstractItemView::item:selected {{
            background-color: #75f5ea;
            color: #363652;
        }}
        
        /* ===== ВСЕ КНОПКИ ===== */
        QPushButton {{
            background-color: #75f5ea;
            color: #363652;
            border: none;
            border-radius: 6px;
            padding: 8px 16px;
            font-weight: bold;
        }}
        QPushButton:hover {{
            background-color: #5dd5ca;
        }}
        QPushButton:pressed {{
            background-color: #4abfb4;
        }}
        QPushButton:disabled {{
            background-color: #4a6a7a;
            color: #888;
        }}
        
        /* ===== ВСЕ ЛЕЙБЛЫ ===== */
        QLabel {{
            color: white;
        }}
        
        /* ===== ВСЕ ФРЕЙМЫ ===== */
        QFrame {{
            background-color: #363652;
            color: white;
        }}
        
        /* ===== СПИСКИ И ТАБЛИЦЫ ===== */
        QListWidget, QTableWidget, QTreeWidget {{
            background-color: #2a2a4a;
            color: white;
            border: 2px solid #75f5ea;
            border-radius: 6px;
            padding: 4px;
            selection-background-color: #75f5ea;
            selection-color: #363652;
        }}
        QListWidget::item, QTableWidget::item, QTreeWidget::item {{
            padding: 4px;
        }}
        QListWidget::item:hover, QTableWidget::item:hover, QTreeWidget::item:hover {{
            background-color: rgba(117, 245, 234, 0.2);
        }}
        
        /* ===== СПИНБОКСЫ ===== */
        QSpinBox, QDoubleSpinBox {{
            background-color: #2a2a4a;
            color: white;
            border: 2px solid #75f5ea;
            border-radius: 6px;
            padding: 4px 8px;
        }}
        QSpinBox:focus, QDoubleSpinBox:focus {{
            border-color: #5dd5ca;
        }}
        QSpinBox::up-button, QDoubleSpinBox::up-button,
        QSpinBox::down-button, QDoubleSpinBox::down-button {{
            background-color: #2a2a4a;
            border: none;
            width: 16px;
        }}
        QSpinBox::up-button:hover, QDoubleSpinBox::up-button:hover,
        QSpinBox::down-button:hover, QDoubleSpinBox::down-button:hover {{
            background-color: #75f5ea;
        }}
        
        /* ===== СЛАЙДЕРЫ ===== */
        QSlider::groove:horizontal {{
            background: #2a2a4a;
            height: 6px;
            border-radius: 3px;
        }}
        QSlider::handle:horizontal {{
            background: #75f5ea;
            width: 16px;
            height: 16px;
            margin: -5px 0;
            border-radius: 8px;
        }}
        QSlider::groove:vertical {{
            background: #2a2a4a;
            width: 6px;
            border-radius: 3px;
        }}
        QSlider::handle:vertical {{
            background: #75f5ea;
            height: 16px;
            width: 16px;
            margin: 0 -5px;
            border-radius: 8px;
        }}
        
        /* ===== ПРОГРЕСС БАР ===== */
        QProgressBar {{
            background-color: #2a2a4a;
            border: 2px solid #75f5ea;
            border-radius: 6px;
            text-align: center;
            color: white;
            height: 20px;
        }}
        QProgressBar::chunk {{
            background-color: #75f5ea;
            border-radius: 4px;
        }}
        
        /* ===== ЧЕКБОКСЫ И РАДИОКНОПКИ ===== */
        QCheckBox, QRadioButton {{
            color: white;
            spacing: 8px;
        }}
        QCheckBox::indicator, QRadioButton::indicator {{
            width: 18px;
            height: 18px;
            border: 2px solid #75f5ea;
            border-radius: 4px;
            background-color: #2a2a4a;
        }}
        QCheckBox::indicator:checked, QRadioButton::indicator:checked {{
            background-color: #75f5ea;
        }}
        QRadioButton::indicator {{
            border-radius: 10px;
        }}
        QRadioButton::indicator:checked {{
            background-color: #75f5ea;
        }}
        
        /* ===== SCROLLBAR ===== */
        QScrollBar:vertical {{
            background-color: #2a2a4a;
            width: 12px;
            border-radius: 6px;
        }}
        QScrollBar::handle:vertical {{
            background-color: #75f5ea;
            border-radius: 6px;
            min-height: 20px;
        }}
        QScrollBar::handle:vertical:hover {{
            background-color: #5dd5ca;
        }}
        QScrollBar:horizontal {{
            background-color: #2a2a4a;
            height: 12px;
            border-radius: 6px;
        }}
        QScrollBar::handle:horizontal {{
            background-color: #75f5ea;
            border-radius: 6px;
            min-width: 20px;
        }}
        QScrollBar::handle:horizontal:hover {{
            background-color: #5dd5ca;
        }}
        
        /* ===== ГРУППЫ ===== */
        QGroupBox {{
            border: 2px solid #75f5ea;
            border-radius: 8px;
            margin-top: 12px;
            padding-top: 12px;
            color: white;
            font-weight: bold;
        }}
        QGroupBox::title {{
            subcontrol-origin: margin;
            left: 15px;
            padding: 0 10px;
            background-color: #363652;
            color: #75f5ea;
        }}
    """)

    window = MainWindow()
    window.show()
    return app.exec()


if __name__ == "__main__":
    sys.exit(main())