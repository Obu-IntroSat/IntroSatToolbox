"""Run the camera app on its own."""

from __future__ import annotations
import sys
from PySide6.QtWidgets import QApplication
from cam_introsat.ui.main_window import CameraWidget

def main() -> int:
    app = QApplication(sys.argv)
    win = CameraWidget()
    win.setWindowTitle("📷 CAMERA INTROSAT")
    win.setMinimumSize(700, 600)
    win.show()
    return app.exec()

if __name__ == "__main__":
    sys.exit(main())