"""Tests for configuration management."""

import json
import tempfile
from pathlib import Path

import pytest

from cam_introsat.core.config import CameraCommandConfig, ConfigManager


class TestCameraCommandConfig:
    """Tests for CameraCommandConfig dataclass."""

    def test_default_config(self):
        """Test default configuration values."""
        config = CameraCommandConfig(name="Test")
        assert config.name == "Test"
        assert config.baudrate == 230400
        assert config.capture == "t"
        assert config.properties == "p"
        assert config.next_chunk == "n"
        assert config.set_size == "s"
        assert config.set_exposure == "e"
        assert config.chunk_size == 240
        assert config.property_size == 18
        assert config.timeout_capture == 15.0

    def test_get_command_bytes_hex(self):
        """Test command conversion from hex string."""
        config = CameraCommandConfig(name="Test")
        assert config.get_command_bytes("0x74") == b't'
        assert config.get_command_bytes("0x70") == b'p'
        assert config.get_command_bytes("0x6e") == b'n'
        assert config.get_command_bytes("0x73") == b's'

    def test_get_command_bytes_ascii(self):
        """Test command conversion from ASCII string."""
        config = CameraCommandConfig(name="Test")
        assert config.get_command_bytes("t") == b't'
        assert config.get_command_bytes("p") == b'p'
        assert config.get_command_bytes("n") == b'n'

    def test_get_command_bytes_empty(self):
        """Test empty command returns empty bytes."""
        config = CameraCommandConfig(name="Test")
        assert config.get_command_bytes("") == b''

    def test_chunk_packet_size(self):
        """Test chunk packet size calculation."""
        config = CameraCommandConfig(name="Test")
        assert config.chunk_packet_size == 247

    def test_to_dict(self):
        """Test conversion to dictionary."""
        config = CameraCommandConfig(name="Test", description="Test config")
        data = config.to_dict()
        assert data["name"] == "Test"
        assert data["description"] == "Test config"
        assert "baudrate" in data

    def test_from_dict(self):
        """Test creation from dictionary."""
        data = {
            "name": "Test",
            "description": "From dict",
            "version": "1.0",
            "baudrate": 115200,
        }
        config = CameraCommandConfig.from_dict(data)
        assert config.name == "Test"
        assert config.description == "From dict"
        assert config.version == "1.0"
        assert config.baudrate == 115200


class TestConfigManager:
    """Tests for ConfigManager."""

    @pytest.fixture
    def temp_config_dir(self):
        """Create temporary directory for configs."""
        with tempfile.TemporaryDirectory() as tmpdir:
            yield Path(tmpdir)

    def test_init_loads_defaults(self):
        """Test that default config is loaded on init."""
        manager = ConfigManager()
        assert "CM 2.0" in manager.configs
        assert manager.configs["CM 2.0"].name == "CM 2.0"

    def test_get_existing_config(self):
        """Test retrieving existing config by name."""
        manager = ConfigManager()
        config = manager.get("CM 2.0")
        assert config is not None
        assert config.name == "CM 2.0"

    def test_get_non_existing_config(self):
        """Test retrieving non-existing config returns None."""
        manager = ConfigManager()
        config = manager.get("NonExisting")
        assert config is None

    def test_add_new_config(self, temp_config_dir):
        """Test adding a new config."""
        manager = ConfigManager(config_dir=temp_config_dir)
        config = CameraCommandConfig(name="NewConfig", description="Test")
        assert manager.add(config) is True
        assert "NewConfig" in manager.configs

    def test_add_existing_config_fails(self, temp_config_dir):
        """Test adding an existing config returns False."""
        manager = ConfigManager(config_dir=temp_config_dir)
        config = CameraCommandConfig(name="CM 2.0")
        assert manager.add(config) is False

    def test_update_config(self, temp_config_dir):
        """Test updating existing config."""
        manager = ConfigManager(config_dir=temp_config_dir)
        config = CameraCommandConfig(name="CM 2.0", description="Updated")
        manager.update(config)
        updated = manager.get("CM 2.0")
        assert updated.description == "Updated"

    def test_load_from_folder(self, temp_config_dir):
        """Test loading configs from folder."""
        config = CameraCommandConfig(name="TestLoad", description="Loaded")
        config_path = temp_config_dir / "TestLoad.json"
        with open(config_path, "w", encoding="utf-8") as f:
            json.dump(config.to_dict(), f, indent=2)

        manager = ConfigManager(config_dir=temp_config_dir)
        manager._load_defaults()
        loaded = manager.load_from_folder()
        assert loaded >= 1
        assert "TestLoad" in manager.configs

    def test_get_by_version(self):
        """Test getting configs by version."""
        manager = ConfigManager()
        config1 = CameraCommandConfig(name="Config1", version="1.0")
        config2 = CameraCommandConfig(name="Config2", version="1.0")
        config3 = CameraCommandConfig(name="Config3", version="2.0")
        manager.configs["Config1"] = config1
        manager.configs["Config2"] = config2
        manager.configs["Config3"] = config3

        matches = manager.get_by_version("1.0")
        assert len(matches) == 2
        names = [name for name, _ in matches]
        assert "Config1" in names
        assert "Config2" in names
