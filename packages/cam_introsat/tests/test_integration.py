"""Integration tests for camera application."""

import struct
import tempfile
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from cam_introsat.core.config import CameraCommandConfig, ConfigManager
from cam_introsat.core.models import CameraState, ImageData
from cam_introsat.core.protocol import ProtocolHandler
from cam_introsat.core.worker import CameraWorker


class TestIntegration:
    """Integration tests between components."""

    @pytest.fixture
    def config(self):
        return CameraCommandConfig(
            name="CM 2.0",
            preamble="ffff00",
            postamble="00ff00",
            chunk_size=240,
            property_size=18
        )

    @pytest.fixture
    def config_manager(self):
        return ConfigManager()

    def test_config_manager_with_worker(self, config, config_manager):
        """Test config manager integration with worker."""
        config_manager.configs["Test"] = config
        worker = CameraWorker(config)
        
        assert worker.config.name == "CM 2.0"
        assert worker.config.chunk_size == 240
        
        new_config = CameraCommandConfig(name="Updated", chunk_size=128)
        config_manager.update(new_config)
        worker.set_config(new_config)
        assert worker.config.chunk_size == 128

    def test_camera_state_integration(self):
        """Test camera state integration."""
        state = CameraState()
        assert state.connected is False
        
        state.connected = True
        state.port = "COM1"
        state.firmware_version = "2.0"
        
        assert state.connected is True
        assert state.port == "COM1"
        assert state.firmware_version == "2.0"

    def test_protocol_config_integration(self, config):
        """Test protocol handler integration with config."""
        protocol = ProtocolHandler(config)
        
        assert protocol.config.name == "CM 2.0"
        assert protocol.config.preamble == "ffff00"
        
        cmd_bytes = protocol.config.get_command_bytes("t")
        assert cmd_bytes == b"t"

    def test_image_data_crop_integration(self, config):
        """Test image data integration with cropping."""
        data = bytes([i % 256 for i in range(400)])
        img = ImageData(data=data, width=20, height=20)
        
        worker = CameraWorker(config)
        cropped = worker._apply_crop(data, 20, 20, crop_x=5, crop_y=5, crop_w=10, crop_h=10)
        
        assert len(cropped) == 100
        assert cropped[0] == data[5*20 + 5]

    @patch("serial.Serial")
    def test_full_workflow_mock(self, mock_serial_class, config):
        """Test full workflow with mocked serial."""
        mock_ser = MagicMock()
        mock_ser.is_open = True
        mock_serial_class.return_value = mock_ser
        
        worker = CameraWorker(config)
        
        result = worker.connect("COM1")
        assert result is True
        
        worker.set_crop_params(v_start=0, h_start=0, width=320, height=240)
        assert worker._crop_width == 320
        assert worker._crop_height == 240
        
        worker.set_exposure(100)
        assert worker._exposure == 100
        
        worker.stop()
        assert worker.running is False

    def test_config_save_load(self):
        """Test config save and load integration."""
        with tempfile.TemporaryDirectory() as tmpdir:
            config_dir = Path(tmpdir)
            manager = ConfigManager(config_dir=config_dir)
            
            config = CameraCommandConfig(
                name="IntegrationTest",
                description="Test config for integration",
                version="1.0",
                baudrate=115200
            )
            manager.add(config)
            
            manager2 = ConfigManager(config_dir=config_dir)
            manager2.load_from_folder()
            
            loaded = manager2.get("IntegrationTest")
            assert loaded is not None
            assert loaded.baudrate == 115200
            assert loaded.description == "Test config for integration"
