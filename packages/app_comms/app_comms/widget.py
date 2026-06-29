"""UI for talking to a device over a serial port."""

from __future__ import annotations

from PySide6.QtCore import QTimer
from PySide6.QtWidgets import (
    QComboBox,
    QHBoxLayout,
    QLineEdit,
    QPlainTextEdit,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

from satcore.serial_io import SerialConnection, available_ports

BAUD_RATES = ["9600", "19200", "38400", "57600", "115200", "230400"]


class CommsWidget(QWidget):
    def __init__(self, parent: QWidget | None = None):
        super().__init__(parent)
        self._conn: SerialConnection | None = None

        self.port_box = QComboBox()
        self.baud_box = QComboBox()
        self.baud_box.addItems(BAUD_RATES)
        self.baud_box.setCurrentText("115200")
        self.refresh_btn = QPushButton("Обновить")
        self.connect_btn = QPushButton("Подключить")

        top = QHBoxLayout()
        top.addWidget(self.port_box, 1)
        top.addWidget(self.baud_box)
        top.addWidget(self.refresh_btn)
        top.addWidget(self.connect_btn)

        self.log = QPlainTextEdit()
        self.log.setReadOnly(True)

        self.input = QLineEdit()
        self.input.setPlaceholderText("Команда устройству...")
        self.send_btn = QPushButton("Отправить")
        self.send_btn.setEnabled(False)

        bottom = QHBoxLayout()
        bottom.addWidget(self.input, 1)
        bottom.addWidget(self.send_btn)

        layout = QVBoxLayout(self)
        layout.addLayout(top)
        layout.addWidget(self.log, 1)
        layout.addLayout(bottom)

        self.refresh_btn.clicked.connect(self.refresh_ports)
        self.connect_btn.clicked.connect(self.toggle_connection)
        self.send_btn.clicked.connect(self.send)
        self.input.returnPressed.connect(self.send)

        # Poll the port for incoming data.
        self._timer = QTimer(self)
        self._timer.setInterval(100)
        self._timer.timeout.connect(self._poll)

        self.refresh_ports()

    def refresh_ports(self) -> None:
        current = self.port_box.currentText()
        self.port_box.clear()
        ports = available_ports()
        self.port_box.addItems(ports)
        if current in ports:
            self.port_box.setCurrentText(current)

    def toggle_connection(self) -> None:
        if self._conn and self._conn.is_open:
            self._disconnect()
        else:
            self._connect()

    def _connect(self) -> None:
        port = self.port_box.currentText()
        if not port:
            self._append("Нет доступных портов")
            return
        try:
            self._conn = SerialConnection(port, int(self.baud_box.currentText()))
            self._conn.open()
        except Exception as exc:  # noqa: BLE001
            self._append(f"Ошибка подключения: {exc}")
            self._conn = None
            return
        self._append(f"Подключено к {port}")
        self.connect_btn.setText("Отключить")
        self.send_btn.setEnabled(True)
        self._timer.start()

    def _disconnect(self) -> None:
        self._timer.stop()
        if self._conn:
            self._conn.close()
            self._conn = None
        self._append("Отключено")
        self.connect_btn.setText("Подключить")
        self.send_btn.setEnabled(False)

    def send(self) -> None:
        if not (self._conn and self._conn.is_open):
            return
        text = self.input.text().strip()
        if not text:
            return
        try:
            self._conn.write_line(text)
        except Exception as exc:  # noqa: BLE001
            self._append(f"Ошибка отправки: {exc}")
            return
        self._append(f">> {text}")
        self.input.clear()

    def _poll(self) -> None:
        if not (self._conn and self._conn.is_open):
            return
        data = self._conn.read_available()
        if data:
            self._append(data.rstrip())

    def _append(self, text: str) -> None:
        self.log.appendPlainText(text)
