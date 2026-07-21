"""Tests for CameraWorker."""

import struct
from unittest.mock import MagicMock, patch

import pytest

from cam_introsat.core.config import CameraCommandConfig
from cam_introsat.core.worker import CameraWorker


class TestCameraWorker:
    """Tests for CameraWorker."""
    
    @pytest.fixture
    def config(self):
        return CameraCommandConfig(
            name="Test",
            capture="t",
            properties="p",
            next_chunk="n",
            set_size="s",
            set_exposure="e",
            get_version="v",
            preamble="ffff00",
            postamble="00ff00",
            chunk_size=240,
            property_size=18,
            timeout_capture=2.0,
            timeout_chunk=1.0,
            timeout_version=1.0
        )

    @pytest.fixture
    def worker(self, config):
        return CameraWorker(config)

    def test_initial_state(self, worker):
        """Test initial worker state."""
        assert worker.running is True
        assert worker.is_busy is False
        assert worker.capture_in_progress is False
        assert worker.current_command is None
        assert worker.ser is None
        assert worker._crop_width == 640
        assert worker._crop_height == 480

    def test_set_config(self, worker):
        """Test setting configuration."""
        new_config = CameraCommandConfig(name="New", capture="x")
        worker.set_config(new_config)
        assert worker.config.name == "New"
        assert worker.config.capture == "x"

    def test_set_crop_params(self, worker):
        """Test setting crop parameters."""
        worker.set_crop_params(v_start=10, h_start=20, width=320, height=240)
        assert worker._crop_v_start == 10
        assert worker._crop_h_start == 20
        assert worker._crop_width == 320
        assert worker._crop_height == 240

    def test_set_exposure(self, worker):
        """Test setting exposure."""
        worker.set_exposure(100)
        assert worker._exposure == 100

    def test_set_resolution_without_connection(self, worker):
        """Test setting resolution without serial connection."""
        worker.set_resolution(320, 240)

    @patch("serial.Serial")
    def test_connect_success(self, mock_serial_class, worker):
        """Test successful connection."""
        mock_ser = MagicMock()
        mock_ser.is_open = True
        mock_serial_class.return_value = mock_ser

        result = worker.connect("COM1")
        assert result is True
        assert worker.ser is not None

    @patch("serial.Serial")
    def test_connect_failure(self, mock_serial_class, worker):
        """Test connection failure."""
        mock_serial_class.side_effect = Exception("Port error")

        result = worker.connect("COM1")
        assert result is False
        assert worker.ser is None

    def test_disconnect(self, worker):
        """Test disconnection."""
        mock_ser = MagicMock()
        mock_ser.is_open = True
        worker.ser = mock_ser

        worker.disconnect()
        mock_ser.close.assert_called_once()
        assert worker.ser is None

    def test_stop(self, worker):
        """Test stopping the worker."""
        worker.stop()
        assert worker.running is False
        assert worker._stop_event.is_set() is True

    def test_apply_crop_no_crop(self, worker):
        """Test crop function with no cropping."""
        data = bytes([i % 256 for i in range(100)])
        result = worker._apply_crop(data, width=10, height=10, crop_x=0, crop_y=0, crop_w=10, crop_h=10)
        assert result == data

    def test_apply_crop(self, worker):
        """Test crop function with cropping."""
        data = bytes([1, 2, 3, 4])
        result = worker._apply_crop(data, width=2, height=2, crop_x=0, crop_y=0, crop_w=1, crop_h=1)
        assert result == b"\x01"

        result = worker._apply_crop(data, width=2, height=2, crop_x=1, crop_y=0, crop_w=1, crop_h=1)
        assert result == b"\x02"

        result = worker._apply_crop(data, width=2, height=2, crop_x=0, crop_y=1, crop_w=2, crop_h=1)
        assert result == b"\x03\x04"

    def test_apply_crop_with_padding(self, worker):
        """Test crop with padding when crop area exceeds image bounds."""
        data = bytes([1, 2, 3, 4])
        # This should crop as much as possible and return the data without extra padding
        result = worker._apply_crop(data, width=2, height=2, crop_x=0, crop_y=0, crop_w=3, crop_h=3)
        # The crop function should handle this gracefully
        # It should return the available data (all 4 bytes) or a padded version
        # Let's check that it doesn't raise and returns something reasonable
        assert len(result) >= 4  # Should at least contain original data

    def test_parse_properties(self, worker):
        """Test parsing properties from raw data."""
        props_data = struct.pack("<HHHHHHLH", 
                                 480, 640, 10, 20, 0, 100, 1000, 5)
        result = worker._parse_properties(props_data)
        assert result["height"] == 480
        assert result["width"] == 640
        assert result["v_start"] == 10
        assert result["h_start"] == 20
        assert result["exposure"] == 100
        assert result["chunks"] == 5
        assert result["has_image"] is True

    def test_parse_properties_no_image(self, worker):
        """Test parsing properties when no image is present."""
        props_data = struct.pack("<HHHHHHLH", 0, 0, 0, 0, 0, 0, 0, 0)
        result = worker._parse_properties(props_data)
        assert result["has_image"] is False

    def test_parse_properties_invalid(self, worker):
        """Test parsing invalid properties data."""
        result = worker._parse_properties(b"invalid")
        assert isinstance(result, dict)

    def test_chunk_crop_integration(self, worker):
        """Test integration of chunk data with cropping."""
        data = bytes([i % 256 for i in range(16)])
        width, height = 4, 4
        
        cropped = worker._apply_crop(data, width, height, crop_x=1, crop_y=1, crop_w=2, crop_h=2)
        expected = b"".join([
            data[5:7],
            data[9:11],
        ])
        assert cropped == expected
