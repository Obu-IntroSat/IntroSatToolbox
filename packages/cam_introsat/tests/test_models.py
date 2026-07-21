"""Tests for data models."""

import pytest

from cam_introsat.core.models import CameraState, ImageData


class TestCameraState:
    """Tests for CameraState dataclass."""

    def test_default_state(self):
        """Test default camera state values."""
        state = CameraState()
        assert state.connected is False
        assert state.port == ""
        assert state.firmware_version == ""
        assert state.config_name == "CM 2.0"
        assert state.width == 640
        assert state.height == 480
        assert state.v_start == 0
        assert state.h_start == 0
        assert state.exposure == 0
        assert state.is_busy is False

    def test_custom_state(self):
        """Test setting custom state values."""
        state = CameraState(
            connected=True,
            port="COM3",
            firmware_version="2.0.1",
            config_name="Custom",
            width=320,
            height=240,
            v_start=10,
            h_start=20,
            exposure=100,
            is_busy=True
        )
        assert state.connected is True
        assert state.port == "COM3"
        assert state.firmware_version == "2.0.1"
        assert state.config_name == "Custom"
        assert state.width == 320
        assert state.height == 240
        assert state.v_start == 10
        assert state.h_start == 20
        assert state.exposure == 100
        assert state.is_busy is True

    def test_captured_fields(self):
        """Test captured image fields."""
        state = CameraState(
            captured_width=640,
            captured_height=480,
            captured_v_start=0,
            captured_h_start=0,
            captured_exposure=100
        )
        assert state.captured_width == 640
        assert state.captured_height == 480
        assert state.captured_v_start == 0
        assert state.captured_h_start == 0
        assert state.captured_exposure == 100


class TestImageData:
    """Tests for ImageData dataclass."""

    def test_default_image_data(self):
        """Test default image data creation."""
        data = b"\x00" * 100
        img = ImageData(data=data, width=10, height=10)
        assert img.data == data
        assert img.width == 10
        assert img.height == 10
        assert img.v_start == 0
        assert img.h_start == 0
        assert img.exposure == 0

    def test_image_size_property(self):
        """Test size property returns data length."""
        data = b"\x00" * 100
        img = ImageData(data=data, width=10, height=10)
        assert img.size == 100

    def test_expected_size_property(self):
        """Test expected_size property returns width * height."""
        img = ImageData(data=b"", width=10, height=10)
        assert img.expected_size == 100

    def test_is_complete_property(self):
        """Test is_complete property."""
        data = b"\x00" * 100
        img = ImageData(data=data, width=10, height=10)
        assert img.is_complete is True

        data_incomplete = b"\x00" * 50
        img2 = ImageData(data=data_incomplete, width=10, height=10)
        assert img2.is_complete is False

    def test_to_qimage(self):
        """Test conversion to QImage."""
        data = bytes([i % 256 for i in range(100)])
        img = ImageData(data=data, width=10, height=10)
        
        try:
            from PySide6.QtGui import QImage
            qimage = img.to_qimage()
            assert isinstance(qimage, QImage)
            assert qimage.width() == 10
            assert qimage.height() == 10
            assert qimage.format() == QImage.Format_Grayscale8
        except ImportError:
            pytest.skip("PySide6 not available")

    def test_to_qimage_padding(self):
        """Test QImage conversion with padding when data is incomplete."""
        data = b"\x00" * 50
        img = ImageData(data=data, width=10, height=10)
        
        try:
            from PySide6.QtGui import QImage
            qimage = img.to_qimage()
            assert isinstance(qimage, QImage)
        except ImportError:
            pytest.skip("PySide6 not available")
