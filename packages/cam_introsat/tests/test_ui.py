"""Tests for UI components."""

import pytest
from PySide6.QtCore import Qt
from PySide6.QtGui import QPixmap

from cam_introsat.ui.widgets import ZoomableImageLabel


@pytest.fixture(scope="session")
def qapp():
    """Create QApplication for UI tests."""
    from PySide6.QtWidgets import QApplication
    app = QApplication.instance()
    if app is None:
        app = QApplication([])
    return app


class TestZoomableImageLabel:
    """Tests for ZoomableImageLabel widget."""

    def test_initial_state(self, qapp):
        """Test initial widget state."""
        widget = ZoomableImageLabel()
        assert widget._pixmap is None
        assert widget._zoom == 1.0
        assert widget.image_label.text() == "Нет изображения"

    def test_set_image(self, qapp):
        """Test setting image."""
        widget = ZoomableImageLabel()
        pixmap = QPixmap(100, 100)
        pixmap.fill(Qt.GlobalColor.white)
        
        widget.set_image(pixmap)
        assert widget._pixmap is not None
        assert widget.image_label.pixmap() is not None

    def test_clear(self, qapp):
        """Test clearing image."""
        widget = ZoomableImageLabel()
        pixmap = QPixmap(100, 100)
        pixmap.fill(Qt.GlobalColor.white)
        
        widget.set_image(pixmap)
        widget.clear()
        
        # After clear, either the text should be set or pixmap should be null
        # Check both conditions
        text_empty = widget.image_label.text() == "Нет изображения"
        pixmap_null = widget.image_label.pixmap() is None or widget.image_label.pixmap().isNull()
        
        # Also check that _pixmap is None
        assert widget._pixmap is None
        # At least one of the conditions should be true
        assert text_empty or pixmap_null, "Image label should be cleared"

    def test_get_fit_zoom_no_image(self, qapp):
        """Test get_fit_zoom when no image is set."""
        widget = ZoomableImageLabel()
        assert widget.get_fit_zoom() == 1.0

    def test_set_zoom(self, qapp):
        """Test setting zoom."""
        widget = ZoomableImageLabel()
        pixmap = QPixmap(100, 100)
        pixmap.fill(Qt.GlobalColor.white)
        widget.set_image(pixmap)
        
        initial_zoom = widget.get_zoom()
        widget.set_zoom(2.0)
        assert widget.get_zoom() >= initial_zoom

    def test_reset_zoom(self, qapp):
        """Test resetting zoom."""
        widget = ZoomableImageLabel()
        pixmap = QPixmap(100, 100)
        pixmap.fill(Qt.GlobalColor.white)
        widget.set_image(pixmap)
        
        initial_zoom = widget.get_zoom()
        widget.set_zoom(2.0)
        widget.reset_zoom()
        assert widget.get_zoom() == initial_zoom

    def test_zoom_limits(self, qapp):
        """Test zoom limits."""
        widget = ZoomableImageLabel()
        pixmap = QPixmap(100, 100)
        pixmap.fill(Qt.GlobalColor.white)
        widget.set_image(pixmap)
        
        fit_zoom = widget.get_fit_zoom()
        widget.set_zoom(0.1)
        assert widget.get_zoom() >= fit_zoom
        
        widget.set_zoom(10.0)
        assert widget.get_zoom() <= 5.0
