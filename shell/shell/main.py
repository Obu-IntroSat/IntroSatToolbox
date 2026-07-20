"""Launcher window: one tab per installed app, discovered automatically."""

from __future__ import annotations

import sys

from PySide6.QtWidgets import (
    QApplication,
    QLabel,
    QMainWindow,
    QTabWidget,
)

from satcore import discover_plugins


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
    window = MainWindow()
    window.show()
    return app.exec()


if __name__ == "__main__":
    sys.exit(main())