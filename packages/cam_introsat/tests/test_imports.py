"""Test that all modules can be imported correctly."""

import pytest


def test_import_core():
    """Test importing core modules."""
    from cam_introsat.core import config, models, protocol, worker
    assert config is not None
    assert models is not None
    assert protocol is not None
    assert worker is not None


def test_import_ui():
    """Test importing UI modules."""
    from cam_introsat.ui import main_window, widgets, dialogs
    assert main_window is not None
    assert widgets is not None
    assert dialogs is not None


def test_import_main():
    """Test importing main modules."""
    from cam_introsat import plugin, __main__
    assert plugin is not None
    assert __main__ is not None


def test_import_config_classes():
    """Test importing specific config classes."""
    from cam_introsat.core.config import CameraCommandConfig, ConfigManager
    assert CameraCommandConfig is not None
    assert ConfigManager is not None


def test_import_model_classes():
    """Test importing specific model classes."""
    from cam_introsat.core.models import CameraState, ImageData
    assert CameraState is not None
    assert ImageData is not None
