"""Data models for camera application."""

from dataclasses import dataclass


@dataclass
class CameraState:
    """Состояние камеры"""
    connected: bool = False
    port: str = ""
    firmware_version: str = ""
    config_name: str = "CM 2.0"
    is_busy: bool = False
    
    width: int = 640
    height: int = 480
    v_start: int = 0
    h_start: int = 0
    exposure: int = 0
    
    captured_width: int = 640
    captured_height: int = 480
    captured_v_start: int = 0
    captured_h_start: int = 0
    captured_exposure: int = 0


@dataclass
class ImageData:
    """Данные изображения"""
    data: bytes
    width: int
    height: int
    v_start: int = 0
    h_start: int = 0
    exposure: int = 0
    
    @property
    def size(self) -> int:
        return len(self.data)
    
    @property
    def expected_size(self) -> int:
        return self.width * self.height
    
    @property
    def is_complete(self) -> bool:
        return self.size >= self.expected_size
    
    def to_qimage(self):
        from PySide6.QtGui import QImage
        img_data = self.data[:self.expected_size]
        if len(img_data) < self.expected_size:
            img_data += b'\x00' * (self.expected_size - len(img_data))
        return QImage(img_data, self.width, self.height, 
                     self.width, QImage.Format_Grayscale8)