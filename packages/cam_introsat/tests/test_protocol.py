"""Tests for protocol handler."""

import struct
from unittest.mock import MagicMock, patch

import pytest

from cam_introsat.core.config import CameraCommandConfig
from cam_introsat.core.protocol import ProtocolHandler


class TestProtocolHandler:
    """Tests for ProtocolHandler."""

    @pytest.fixture
    def config(self):
        return CameraCommandConfig(name="Test", preamble="ffff00", postamble="00ff00")

    @pytest.fixture
    def protocol(self, config):
        return ProtocolHandler(config)

    def test_initial_state(self, protocol):
        """Test initial state of protocol handler."""
        assert protocol.ser is None
        assert protocol.is_connected is False

    @patch("serial.Serial")
    def test_connect_success(self, mock_serial_class, protocol):
        """Test successful connection."""
        mock_serial = MagicMock()
        mock_serial.is_open = True
        mock_serial_class.return_value = mock_serial

        result = protocol.connect("COM1")
        assert result is True
        assert protocol.is_connected is True
        mock_serial.reset_input_buffer.assert_called_once()
        mock_serial.reset_output_buffer.assert_called_once()

    @patch("serial.Serial")
    def test_connect_failure(self, mock_serial_class, protocol):
        """Test connection failure."""
        mock_serial_class.side_effect = Exception("Port not found")

        result = protocol.connect("COM1")
        assert result is False
        assert protocol.is_connected is False

    def test_disconnect(self, protocol):
        """Test disconnection."""
        mock_ser = MagicMock()
        mock_ser.is_open = True
        protocol.ser = mock_ser

        protocol.disconnect()
        mock_ser.close.assert_called_once()
        assert protocol.ser is None
        assert protocol.is_connected is False

    def test_write_data(self, protocol):
        """Test writing data."""
        mock_ser = MagicMock()
        mock_ser.is_open = True
        protocol.ser = mock_ser

        protocol.write(b"test data")
        mock_ser.write.assert_called_once_with(b"test data")
        mock_ser.flush.assert_called_once()

    def test_write_when_not_connected(self, protocol):
        """Test writing when not connected."""
        protocol.ser = None
        protocol.write(b"test")

    def test_write_command(self, protocol):
        """Test writing command."""
        mock_ser = MagicMock()
        mock_ser.is_open = True
        protocol.ser = mock_ser

        cmd_bytes = protocol.write_command("t")
        assert cmd_bytes == b"t"
        mock_ser.write.assert_called_once_with(b"t")

    def test_write_command_hex(self, protocol):
        """Test writing hex command."""
        mock_ser = MagicMock()
        mock_ser.is_open = True
        protocol.ser = mock_ser

        cmd_bytes = protocol.write_command("0x74")
        assert cmd_bytes == b"t"

    def test_read_until(self, protocol):
        """Test reading until pattern found."""
        mock_ser = MagicMock()
        mock_ser.is_open = True
        mock_ser.in_waiting = 5
        mock_ser.read.side_effect = [b"prefix", b"pattern"]
        protocol.ser = mock_ser

        result = protocol.read_until(b"pattern", timeout=1.0)
        assert result == b"prefixpattern"

    def test_read_until_timeout(self, protocol):
        """Test read_until timeout."""
        mock_ser = MagicMock()
        mock_ser.is_open = True
        mock_ser.in_waiting = 0
        protocol.ser = mock_ser

        result = protocol.read_until(b"pattern", timeout=0.1)
        assert result == b""

    def test_read_exact(self, protocol):
        """Test reading exact number of bytes."""
        mock_ser = MagicMock()
        mock_ser.is_open = True
        mock_ser.in_waiting = 5
        mock_ser.read.return_value = b"12345"
        protocol.ser = mock_ser

        result = protocol.read_exact(5, timeout=1.0)
        assert result == b"12345"

    def test_read_exact_timeout(self, protocol):
        """Test read_exact timeout."""
        mock_ser = MagicMock()
        mock_ser.is_open = True
        mock_ser.in_waiting = 0
        protocol.ser = mock_ser

        result = protocol.read_exact(5, timeout=0.1)
        assert result == b""

    def test_send_set_size(self, protocol):
        """Test sending set size command."""
        mock_ser = MagicMock()
        mock_ser.is_open = True
        protocol.ser = mock_ser
        protocol.config.set_size = "s"

        protocol.send_set_size(640, 480)
        expected = b"s" + struct.pack("<HH", 640, 480)
        mock_ser.write.assert_called_once_with(expected)

    def test_send_set_exposure(self, protocol):
        """Test sending set exposure command."""
        mock_ser = MagicMock()
        mock_ser.is_open = True
        protocol.ser = mock_ser
        protocol.config.set_exposure = "e"

        protocol.send_set_exposure(100)
        expected = b"e" + struct.pack("<H", 100)
        mock_ser.write.assert_called_once_with(expected)
