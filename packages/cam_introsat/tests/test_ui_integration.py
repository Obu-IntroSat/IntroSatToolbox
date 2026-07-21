"""Integration tests for UI components with backend."""

from unittest.mock import MagicMock, patch

import pytest
from PySide6.QtCore import Qt, QTimer, QEventLoop
from PySide6.QtGui import QPixmap

from cam_introsat.core.config import CameraCommandConfig
from cam_introsat.ui.main_window import CameraWidget


@pytest.fixture(scope="session")
def qapp():
    """Create QApplication for UI tests."""
    from PySide6.QtWidgets import QApplication
    app = QApplication.instance()
    if app is None:
        app = QApplication([])
    return app


class TestMainWindowIntegration:
    """Integration tests for main window."""

    def test_widget_initialization(self, qapp):
        """Test camera widget initialization."""
        widget = CameraWidget()
        assert widget.state.connected is False
        assert widget.state.config_name == "CM 2.0"
        assert widget.width_spin.value() == 640
        assert widget.height_spin.value() == 480
        
    def test_port_refresh(self, qapp):
        """Test port refresh functionality."""
        widget = CameraWidget()
        widget.refresh_ports()

    def test_config_loading(self, qapp):
        """Test config loading."""
        widget = CameraWidget()
        widget.load_configs()
        assert widget.config_combo.count() >= 1

    def test_clear_image(self, qapp):
        """Test clearing image."""
        widget = CameraWidget()
        widget.clear_image()
        assert widget.image_data is None
        assert widget.save_btn.isEnabled() is False

    def test_toggle_auto_exposure(self, qapp):
        """Test auto exposure toggle."""
        widget = CameraWidget()
        
        # First, ensure auto is on (default state)
        # The checkbox should be checked by default
        assert widget.auto_exp_check.isChecked() is True, "Auto exposure should be on by default"
        
        # Process events to ensure any pending signals are processed
        qapp.processEvents()
        
        # Since auto is on, spin box should be disabled
        # But we need to check the actual state after initialization
        # The toggle_auto_exposure slot might not have been called yet
        # Let's call it directly to ensure proper state
        widget.toggle_auto_exposure(True)
        qapp.processEvents()
        assert widget.exposure_spin.isEnabled() is False, "Spin box should be disabled when auto is on"
        assert widget.exposure_spin.value() == 0, "Spin box value should be 0 when auto is on"
        
        # Turn auto off
        widget.auto_exp_check.setChecked(False)
        qapp.processEvents()
        # The slot should be called automatically
        assert widget.exposure_spin.isEnabled() is True, "Spin box should be enabled when auto is off"

    def test_toggle_auto_exposure_alternative(self, qapp):
        """Alternative test for auto exposure toggle using direct method call."""
        widget = CameraWidget()
        
        # Directly call the slot
        widget.toggle_auto_exposure(True)
        qapp.processEvents()
        assert widget.exposure_spin.isEnabled() is False
        
        widget.toggle_auto_exposure(False)
        qapp.processEvents()
        assert widget.exposure_spin.isEnabled() is True

    def test_on_zoom_changed(self, qapp):
        """Test zoom slider."""
        widget = CameraWidget()
        widget.on_zoom_changed(50)
        
        # Create a real QPixmap instead of MagicMock
        pixmap = QPixmap(100, 100)
        pixmap.fill(Qt.GlobalColor.white)
        widget.image_label.set_image(pixmap)
        qapp.processEvents()
        
        widget.on_zoom_changed(100)
        qapp.processEvents()
        assert widget.zoom_label.text() == "100%"

    def test_reset_zoom(self, qapp):
        """Test reset zoom button."""
        widget = CameraWidget()
        widget.reset_zoom()

    def test_add_log(self, qapp):
        """Test adding log messages."""
        widget = CameraWidget()
        widget.add_log("Test log message")
        log_text = widget.log_text.toPlainText()
        assert "Test log message" in log_text
