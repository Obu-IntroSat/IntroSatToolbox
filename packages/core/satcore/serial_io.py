"""Thin convenience wrappers around pyserial."""

from __future__ import annotations

import serial
from serial.tools import list_ports


def available_ports() -> list[str]:
    """Return the device names of all detected serial ports."""
    return [port.device for port in list_ports.comports()]


class SerialConnection:
    """A minimal, GUI-friendly serial connection."""

    def __init__(self, port: str, baudrate: int = 115200, timeout: float = 0.1):
        self.port = port
        self.baudrate = baudrate
        self.timeout = timeout
        self._serial: serial.Serial | None = None

    @property
    def is_open(self) -> bool:
        return self._serial is not None and self._serial.is_open

    def open(self) -> None:
        self._serial = serial.Serial(
            self.port, self.baudrate, timeout=self.timeout
        )

    def close(self) -> None:
        if self._serial is not None:
            self._serial.close()
            self._serial = None

    def write_line(self, text: str) -> None:
        if not self.is_open:
            raise RuntimeError("Serial port is not open")
        self._serial.write((text + "\n").encode("utf-8"))

    def read_available(self) -> str:
        """Read whatever bytes are waiting, decoded as UTF-8 (lossy)."""
        if not self.is_open:
            return ""
        waiting = self._serial.in_waiting
        if not waiting:
            return ""
        data = self._serial.read(waiting)
        return data.decode("utf-8", errors="replace")
