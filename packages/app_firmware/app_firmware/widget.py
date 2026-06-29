"""UI for flashing firmware through an external programmer tool."""

from __future__ import annotations

import shlex

from PySide6.QtWidgets import (
    QComboBox,
    QFileDialog,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPlainTextEdit,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

from satcore.process import run_command
from satcore.worker import Worker, run_in_thread

# Command templates per tool. {file} is replaced with the chosen firmware path.
# Edit these to match your real hardware / programmer.
FLASH_COMMANDS = {
    "avrdude (Arduino/AVR)": 'avrdude -c usbasp -p m328p -U flash:w:{file}:i',
    "OpenOCD (ARM)": 'openocd -f interface/stlink.cfg -f target/stm32f1x.cfg '
    '-c "program {file} verify reset exit"',
    "esptool (ESP32)": "esptool --chip esp32 write_flash 0x1000 {file}",
    "st-flash (STM32)": "st-flash write {file} 0x8000000",
}


class FirmwareWidget(QWidget):
    def __init__(self, parent: QWidget | None = None):
        super().__init__(parent)
        self._thread = None

        self.tool_box = QComboBox()
        self.tool_box.addItems(FLASH_COMMANDS.keys())
        self.tool_box.currentTextChanged.connect(self._apply_template)

        self.file_edit = QLineEdit()
        self.file_edit.setPlaceholderText("Файл прошивки (.hex / .bin / .elf)")
        self.browse_btn = QPushButton("Обзор...")

        file_row = QHBoxLayout()
        file_row.addWidget(self.file_edit, 1)
        file_row.addWidget(self.browse_btn)

        self.cmd_edit = QLineEdit()

        self.flash_btn = QPushButton("Прошить")

        self.log = QPlainTextEdit()
        self.log.setReadOnly(True)

        layout = QVBoxLayout(self)
        layout.addWidget(QLabel("Программатор / инструмент:"))
        layout.addWidget(self.tool_box)
        layout.addWidget(QLabel("Файл прошивки:"))
        layout.addLayout(file_row)
        layout.addWidget(QLabel("Команда (можно отредактировать):"))
        layout.addWidget(self.cmd_edit)
        layout.addWidget(self.flash_btn)
        layout.addWidget(self.log, 1)

        self.browse_btn.clicked.connect(self.browse)
        self.flash_btn.clicked.connect(self.flash)

        self._apply_template()

    def _apply_template(self) -> None:
        self.cmd_edit.setText(FLASH_COMMANDS[self.tool_box.currentText()])

    def browse(self) -> None:
        path, _ = QFileDialog.getOpenFileName(
            self,
            "Выберите файл прошивки",
            "",
            "Прошивки (*.hex *.bin *.elf);;Все файлы (*)",
        )
        if path:
            self.file_edit.setText(path)

    def flash(self) -> None:
        if self._thread is not None:
            self._append("Прошивка уже выполняется...")
            return

        file_path = self.file_edit.text().strip()
        if not file_path:
            self._append("Укажите файл прошивки")
            return

        command = self.cmd_edit.text().replace("{file}", file_path)
        try:
            argv = shlex.split(command)
        except ValueError as exc:
            self._append(f"Не удалось разобрать команду: {exc}")
            return

        self._append(f"$ {command}")
        self.flash_btn.setEnabled(False)

        worker = Worker(self._run_flash, argv)
        worker.output.connect(self._append)
        worker.finished.connect(self._on_finished)
        worker.failed.connect(self._on_failed)
        self._thread = run_in_thread(self, worker)

    @staticmethod
    def _run_flash(argv, report) -> int:
        return run_command(argv, on_output=report)

    def _on_finished(self, code) -> None:
        self._append(f"Готово (код выхода: {code})")
        self._reset()

    def _on_failed(self, message: str) -> None:
        self._append(f"Ошибка: {message}")
        self._reset()

    def _reset(self) -> None:
        self._thread = None
        self.flash_btn.setEnabled(True)

    def _append(self, text: str) -> None:
        self.log.appendPlainText(text)
