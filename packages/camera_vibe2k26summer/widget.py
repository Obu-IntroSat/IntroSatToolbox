"""Universal Camera Application - Compact with Zoom (FIXED)"""

from __future__ import annotations
import struct
import time
import serial
import json
from datetime import datetime
from pathlib import Path
from typing import Optional, Dict, Any
from dataclasses import dataclass

from PySide6.QtCore import Qt, Signal, QThread
from PySide6.QtGui import QImage, QPixmap, QWheelEvent
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
    QPushButton, QTextEdit, QGroupBox,
    QComboBox, QGridLayout, QMessageBox, QProgressBar,
    QSpinBox, QCheckBox, QTabWidget, QLineEdit,
    QFileDialog, QSplitter, QDialog, QDialogButtonBox,
    QFormLayout, QSlider, QScrollArea
)

from PIL import Image


# ============================================================================
# Конфигурация
# ============================================================================

@dataclass
class CameraCommandConfig:
    """Конфигурация команд для модуля камеры"""
    name: str
    description: str = ""
    
    # Команды
    capture: str = "t"
    properties: str = "p"
    next_chunk: str = "n"
    set_size: str = "s"
    set_exposure: str = "e"
    start_transfer: str = "r"
    
    # Параметры протокола
    baudrate: int = 230400
    preamble: str = "ffff00"
    postamble: str = "00ff00"
    chunk_size: int = 240
    property_size: int = 18
    timeout_capture: float = 15.0
    timeout_chunk: float = 2.0
    
    # Форматы структур
    property_format: str = "<HHHHHHLH"
    chunk_format: str = "<HH?240BB"
    
    def get_command_bytes(self, cmd: str) -> bytes:
        """Преобразует команду в байты"""
        cmd = cmd.strip()
        if cmd.startswith('0x'):
            return bytes([int(cmd, 16)])
        elif cmd.isdigit():
            return bytes([int(cmd)])
        else:
            return cmd.encode('ascii')
    
    def to_dict(self) -> dict:
        return {
            'name': self.name,
            'description': self.description,
            'capture': self.capture,
            'properties': self.properties,
            'next_chunk': self.next_chunk,
            'set_size': self.set_size,
            'set_exposure': self.set_exposure,
            'start_transfer': self.start_transfer,
            'baudrate': self.baudrate,
            'preamble': self.preamble,
            'postamble': self.postamble,
            'chunk_size': self.chunk_size,
            'property_size': self.property_size,
            'timeout_capture': self.timeout_capture,
            'timeout_chunk': self.timeout_chunk,
            'property_format': self.property_format,
            'chunk_format': self.chunk_format
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> CameraCommandConfig:
        return cls(
            name=data.get('name', 'Unknown'),
            description=data.get('description', ''),
            capture=data.get('capture', 't'),
            properties=data.get('properties', 'p'),
            next_chunk=data.get('next_chunk', 'n'),
            set_size=data.get('set_size', 's'),
            set_exposure=data.get('set_exposure', 'e'),
            start_transfer=data.get('start_transfer', 'r'),
            baudrate=data.get('baudrate', 230400),
            preamble=data.get('preamble', 'ffff00'),
            postamble=data.get('postamble', '00ff00'),
            chunk_size=data.get('chunk_size', 240),
            property_size=data.get('property_size', 18),
            timeout_capture=data.get('timeout_capture', 15.0),
            timeout_chunk=data.get('timeout_chunk', 2.0),
            property_format=data.get('property_format', '<HHHHHHLH'),
            chunk_format=data.get('chunk_format', '<HH?240BB')
        )


# ============================================================================
# Диалог создания конфигурации
# ============================================================================

class CreateConfigDialog(QDialog):
    """Диалог создания новой конфигурации"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Создать конфигурацию")
        self.setMinimumWidth(500)
        self.setup_ui()
    
    def setup_ui(self):
        layout = QVBoxLayout(self)
        
        form = QFormLayout()
        
        self.name_edit = QLineEdit()
        self.name_edit.setPlaceholderText("Например: My Camera v1")
        form.addRow("Название:", self.name_edit)
        
        self.desc_edit = QLineEdit()
        self.desc_edit.setPlaceholderText("Описание конфигурации")
        form.addRow("Описание:", self.desc_edit)
        
        # Группа команд
        cmd_group = QGroupBox("Команды")
        cmd_layout = QGridLayout(cmd_group)
        
        self.capture_edit = QLineEdit("t")
        cmd_layout.addWidget(QLabel("Снимок:"), 0, 0)
        cmd_layout.addWidget(self.capture_edit, 0, 1)
        
        self.properties_edit = QLineEdit("p")
        cmd_layout.addWidget(QLabel("Свойства:"), 0, 2)
        cmd_layout.addWidget(self.properties_edit, 0, 3)
        
        self.next_chunk_edit = QLineEdit("n")
        cmd_layout.addWidget(QLabel("Следующий чанк:"), 1, 0)
        cmd_layout.addWidget(self.next_chunk_edit, 1, 1)
        
        self.set_size_edit = QLineEdit("s")
        cmd_layout.addWidget(QLabel("Размер:"), 1, 2)
        cmd_layout.addWidget(self.set_size_edit, 1, 3)
        
        self.set_exposure_edit = QLineEdit("e")
        cmd_layout.addWidget(QLabel("Экспозиция:"), 2, 0)
        cmd_layout.addWidget(self.set_exposure_edit, 2, 1)
        
        self.start_transfer_edit = QLineEdit("r")
        cmd_layout.addWidget(QLabel("Начать передачу:"), 2, 2)
        cmd_layout.addWidget(self.start_transfer_edit, 2, 3)
        
        form.addRow(cmd_group)
        
        # Параметры протокола
        proto_group = QGroupBox("Параметры протокола")
        proto_layout = QGridLayout(proto_group)
        
        self.baudrate_edit = QLineEdit("230400")
        proto_layout.addWidget(QLabel("Baudrate:"), 0, 0)
        proto_layout.addWidget(self.baudrate_edit, 0, 1)
        
        self.preamble_edit = QLineEdit("ffff00")
        proto_layout.addWidget(QLabel("Преамбула (hex):"), 0, 2)
        proto_layout.addWidget(self.preamble_edit, 0, 3)
        
        self.postamble_edit = QLineEdit("00ff00")
        proto_layout.addWidget(QLabel("Постамбула (hex):"), 1, 0)
        proto_layout.addWidget(self.postamble_edit, 1, 1)
        
        self.chunk_size_edit = QLineEdit("240")
        proto_layout.addWidget(QLabel("Размер чанка:"), 1, 2)
        proto_layout.addWidget(self.chunk_size_edit, 1, 3)
        
        self.property_size_edit = QLineEdit("18")
        proto_layout.addWidget(QLabel("Размер свойств:"), 2, 0)
        proto_layout.addWidget(self.property_size_edit, 2, 1)
        
        self.timeout_capture_edit = QLineEdit("15.0")
        proto_layout.addWidget(QLabel("Таймаут захвата:"), 2, 2)
        proto_layout.addWidget(self.timeout_capture_edit, 2, 3)
        
        self.timeout_chunk_edit = QLineEdit("2.0")
        proto_layout.addWidget(QLabel("Таймаут чанка:"), 3, 0)
        proto_layout.addWidget(self.timeout_chunk_edit, 3, 1)
        
        form.addRow(proto_group)
        
        # Форматы структур
        struct_group = QGroupBox("Форматы структур")
        struct_layout = QGridLayout(struct_group)
        
        self.property_format_edit = QLineEdit("<HHHHHHLH")
        struct_layout.addWidget(QLabel("Свойства:"), 0, 0)
        struct_layout.addWidget(self.property_format_edit, 0, 1)
        
        self.chunk_format_edit = QLineEdit("<HH?240BB")
        struct_layout.addWidget(QLabel("Чанк:"), 0, 2)
        struct_layout.addWidget(self.chunk_format_edit, 0, 3)
        
        form.addRow(struct_group)
        
        layout.addLayout(form)
        
        # Подсказка
        hint = QLabel(
            "💡 Команды можно указывать как:\n"
            "  • символ: t, p, n\n"
            "  • hex: 0x74, 0x70, 0x6E\n"
            "  • число: 116, 112, 110"
        )
        hint.setStyleSheet("color: #666; font-size: 10px; padding: 8px; background: #f0f0f0; border-radius: 4px;")
        layout.addWidget(hint)
        
        buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | 
            QDialogButtonBox.StandardButton.Cancel
        )
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)
    
    def get_config(self) -> CameraCommandConfig:
        """Возвращает созданную конфигурацию"""
        return CameraCommandConfig(
            name=self.name_edit.text(),
            description=self.desc_edit.text(),
            capture=self.capture_edit.text(),
            properties=self.properties_edit.text(),
            next_chunk=self.next_chunk_edit.text(),
            set_size=self.set_size_edit.text(),
            set_exposure=self.set_exposure_edit.text(),
            start_transfer=self.start_transfer_edit.text(),
            baudrate=int(self.baudrate_edit.text()),
            preamble=self.preamble_edit.text(),
            postamble=self.postamble_edit.text(),
            chunk_size=int(self.chunk_size_edit.text()),
            property_size=int(self.property_size_edit.text()),
            timeout_capture=float(self.timeout_capture_edit.text()),
            timeout_chunk=float(self.timeout_chunk_edit.text()),
            property_format=self.property_format_edit.text(),
            chunk_format=self.chunk_format_edit.text()
        )


# ============================================================================
# Рабочий поток
# ============================================================================

class CameraWorker(QThread):
    progress = Signal(int)
    partial_image = Signal(bytes, int, int)
    image_data = Signal(bytes)
    log = Signal(str)
    finished = Signal()
    error = Signal(str)
    properties_received = Signal(dict)
    capture_complete = Signal()
    
    def __init__(self):
        super().__init__()
        self.ser = None
        self.running = True
        self.is_busy = False
        self.current_command = None
        self.capture_in_progress = False
        self.config: CameraCommandConfig = CameraCommandConfig("CM 2.0")
        
        self._chunk_buffer = bytearray(248)
        self._chunk_struct = struct.Struct('<HH?240BB')
        self._prop_struct = struct.Struct('<HHHHHHLH')
        self._width = 640
        self._height = 480
    
    def set_config(self, config: CameraCommandConfig):
        self.config = config
        self._chunk_buffer = bytearray(config.chunk_size + 8)
        self._chunk_struct = struct.Struct(config.chunk_format)
        self._prop_struct = struct.Struct(config.property_format)
    
    def connect(self, port: str) -> bool:
        try:
            self.ser = serial.Serial(
                port, 
                self.config.baudrate,
                timeout=3.0,
                parity=serial.PARITY_NONE
            )
            self.ser.reset_input_buffer()
            self.ser.reset_output_buffer()
            self.log.emit(f"✅ Подключено к {port} ({self.config.baudrate} бод)")
            self.log.emit(f"   Профиль: {self.config.name}")
            return True
        except Exception as e:
            self.log.emit(f"❌ {e}")
            return False
    
    def disconnect(self):
        if self.ser and self.ser.is_open:
            self.ser.close()
        self.ser = None
        self.log.emit("⏹ Отключено")
    
    def _write(self, data: bytes):
        if self.ser and self.ser.is_open:
            self.ser.write(data)
            self.ser.flush()
    
    def _write_command(self, cmd: str):
        cmd_bytes = self.config.get_command_bytes(cmd)
        self._write(cmd_bytes)
        return cmd_bytes
    
    def _read_until_preamble(self) -> bytes:
        if not self.ser or not self.ser.is_open:
            return b''
        preamble = bytes.fromhex(self.config.preamble)
        return self.ser.read_until(preamble)
    
    def _read_exact(self, size: int, timeout: float = 3.0) -> bytes:
        if not self.ser or not self.ser.is_open:
            return b''
        data = b''
        start = time.time()
        while len(data) < size and (time.time() - start) < timeout:
            if self.ser.in_waiting > 0:
                available = self.ser.in_waiting
                to_read = min(available, size - len(data))
                data += self.ser.read(to_read)
            time.sleep(0.001)
        return data
    
    def _parse_properties(self, data: bytes) -> dict:
        try:
            unpacked = self._prop_struct.unpack(data[:self.config.property_size])
            field_names = ['height', 'width', 'v_start', 'h_start', 
                          'colorspace', 'exposure', 'length', 'chunks']
            result = {}
            for i, name in enumerate(field_names):
                if i < len(unpacked):
                    result[name] = unpacked[i]
            result['has_image'] = result.get('chunks', 0) > 0
            return result
        except Exception as e:
            self.log.emit(f"⚠️ Ошибка парсинга свойств: {e}")
            return {}
    
    def run(self):
        while self.running:
            if self.current_command == 'capture':
                self._do_capture()
            elif self.current_command == 'download':
                self._do_download()
            elif self.current_command == 'properties':
                self._do_properties()
            time.sleep(0.01)
    
    def _do_capture(self):
        self.is_busy = True
        self.capture_in_progress = True
        try:
            self.log.emit(f"📸 Захват...")
            self.ser.reset_input_buffer()
            self.ser.reset_output_buffer()
            self._write_command(self.config.capture)
            
            start_time = time.time()
            response_found = False
            timeout = self.config.timeout_capture
            preamble = bytes.fromhex(self.config.preamble)
            
            while (time.time() - start_time) < timeout:
                if self.ser.in_waiting > 0:
                    data = self.ser.read(self.ser.in_waiting)
                    if preamble in data:
                        response_found = True
                        break
                time.sleep(0.1)
                elapsed = int(time.time() - start_time)
                if elapsed % 2 == 0 and elapsed > 0:
                    self.log.emit(f"⏳ {elapsed}/{int(timeout)} сек")
            
            if response_found:
                self.log.emit("✅ Снимок создан!")
            else:
                self.log.emit("⚠️ Таймаут")
            
            self.capture_complete.emit()
            
        except Exception as e:
            self.log.emit(f"❌ {e}")
            self.error.emit(str(e))
        finally:
            self.is_busy = False
            self.capture_in_progress = False
            self.current_command = None
            self.finished.emit()
    
    def _do_properties(self):
        self.is_busy = True
        try:
            self.log.emit("📊 Запрос свойств...")
            self.ser.reset_input_buffer()
            self.ser.reset_output_buffer()
            self._write_command(self.config.properties)
            
            preamble = bytes.fromhex(self.config.preamble)
            preamble_data = self.ser.read_until(preamble)
            if not preamble_data:
                self.log.emit("⚠️ Нет ответа")
                self.error.emit("Нет снимка")
                return
            
            size = self.config.property_size
            data = self._read_exact(size, timeout=2.0)
            if len(data) < size:
                self.log.emit(f"⚠️ Получено {len(data)} байт")
                self.error.emit("Неполные данные")
                return
            
            props = self._parse_properties(data)
            self.properties_received.emit(props)
            
            if props.get('chunks', 0) > 0:
                self.log.emit(f"✅ {props.get('width', 0)}x{props.get('height', 0)}, "
                            f"{props.get('chunks', 0)} чанков")
            else:
                self.log.emit("ℹ️ Нет снимка")
            
        except Exception as e:
            self.log.emit(f"❌ {e}")
            self.error.emit(str(e))
        finally:
            self.is_busy = False
            self.current_command = None
            self.finished.emit()
    
    def _do_download(self):
        self.is_busy = True
        try:
            self.log.emit("📥 Загрузка...")
            self.ser.reset_input_buffer()
            self.ser.reset_output_buffer()
            self._write_command(self.config.properties)
            
            preamble = bytes.fromhex(self.config.preamble)
            self.ser.read_until(preamble)
            
            size = self.config.property_size
            data = self._read_exact(size, timeout=2.0)
            if len(data) < size:
                self.error.emit("Неполные данные")
                return
            
            props = self._parse_properties(data)
            height = props.get('height', 0)
            width = props.get('width', 0)
            total_chunks = props.get('chunks', 0)
            
            if total_chunks == 0:
                self.error.emit("Нет снимка")
                return
            
            self.log.emit(f"📦 {width}x{height}, {total_chunks} чанков")
            
            image_data = bytearray()
            expected = width * height
            self.ser.reset_input_buffer()
            
            if self.config.start_transfer:
                self._write_command(self.config.start_transfer)
                time.sleep(0.05)
            
            chunk_size = self.config.chunk_size
            chunk_struct = self._chunk_struct
            chunk_buffer = self._chunk_buffer
            chunk_total = chunk_size + 8
            
            for chunk_idx in range(total_chunks):
                if not self.running:
                    break
                
                self.ser.reset_input_buffer()
                self._write_command(self.config.next_chunk)
                self.ser.flush()
                
                self.ser.read_until(preamble)
                
                read_total = 0
                start_time = time.time()
                timeout = self.config.timeout_chunk
                
                while read_total < chunk_total and (time.time() - start_time) < timeout:
                    if self.ser.in_waiting > 0:
                        available = self.ser.in_waiting
                        to_read = min(available, chunk_total - read_total)
                        chunk_buffer[read_total:read_total + to_read] = self.ser.read(to_read)
                        read_total += to_read
                    time.sleep(0.0005)
                
                if read_total < chunk_total:
                    continue
                
                try:
                    unpacked = chunk_struct.unpack_from(chunk_buffer)
                    chunk_id = unpacked[0]
                    payload_len = unpacked[1]
                    is_last = unpacked[2] if len(unpacked) > 2 else False
                    payload = chunk_buffer[5:5+payload_len]
                    image_data.extend(payload)
                    
                    progress = int((chunk_idx + 1) / total_chunks * 100)
                    self.progress.emit(progress)
                    
                    if chunk_idx % 5 == 0 or is_last:
                        self.partial_image.emit(bytes(image_data), width, height)
                        self.log.emit(f"📦 {chunk_idx+1}/{total_chunks} ({progress}%)")
                    
                    if is_last:
                        break
                    
                except Exception:
                    continue
                
                if len(image_data) >= expected:
                    break
            
            if len(image_data) < expected:
                image_data.extend(b'\x00' * (expected - len(image_data)))
            
            self.log.emit(f"✅ Загрузка завершена")
            self.image_data.emit(bytes(image_data))
            
        except Exception as e:
            self.log.emit(f"❌ {e}")
            self.error.emit(str(e))
        finally:
            self.is_busy = False
            self.current_command = None
            self.progress.emit(0)
            self.finished.emit()
    
    def start_capture(self):
        if not self.is_busy and not self.capture_in_progress:
            self.current_command = 'capture'
            if not self.isRunning():
                self.start()
    
    def start_download(self):
        if not self.is_busy:
            self.current_command = 'download'
            if not self.isRunning():
                self.start()
    
    def start_properties(self):
        if not self.is_busy:
            self.current_command = 'properties'
            if not self.isRunning():
                self.start()
    
    def set_resolution(self, w: int, h: int):
        if self.ser and self.ser.is_open:
            cmd = self.config.get_command_bytes(self.config.set_size)
            cmd += struct.pack('<HH', w, h)
            self._write(cmd)
            self._width, self._height = w, h
            self.log.emit(f"📐 {w}x{h}")
            time.sleep(0.05)
    
    def set_exposure(self, exp: int):
        if self.ser and self.ser.is_open:
            cmd = self.config.get_command_bytes(self.config.set_exposure)
            cmd += struct.pack('<H', exp)
            self._write(cmd)
            self.log.emit(f"🔆 {'Авто' if exp == 0 else exp}")
            time.sleep(0.05)
    
    def set_crop(self, v_start: int, h_start: int):
        if self.ser and self.ser.is_open:
            self.log.emit(f"✂️ vStart={v_start}, hStart={h_start}")


# ============================================================================
# Класс для отображения изображения с зумом
# ============================================================================

class ZoomableImageLabel(QLabel):
    """QLabel с поддержкой зума колесиком мыши"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self._pixmap = None
        self._zoom = 1.0
        self._min_zoom = 0.1
        self._max_zoom = 10.0
        self.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.setMinimumHeight(300)
        self.setStyleSheet(
            "background-color: #1a1a1a; border: 2px solid #333; border-radius: 6px;"
        )
        self.setScaledContents(False)
    
    def set_image(self, pixmap: QPixmap):
        """Установка изображения"""
        self._pixmap = pixmap
        self._zoom = 1.0
        self.update_display()
    
    def update_display(self):
        """Обновление отображения с текущим зумом"""
        if self._pixmap is None:
            self.setText("Нет изображения")
            return
        
        scaled = self._pixmap.scaled(
            int(self._pixmap.width() * self._zoom),
            int(self._pixmap.height() * self._zoom),
            Qt.AspectRatioMode.KeepAspectRatio,
            Qt.TransformationMode.SmoothTransformation
        )
        self.setPixmap(scaled)
    
    def wheelEvent(self, event: QWheelEvent):
        """Обработка колесика мыши для зума"""
        if self._pixmap is None:
            return
        
        delta = event.angleDelta().y()
        if delta > 0:
            self._zoom *= 1.1
        else:
            self._zoom *= 0.9
        
        self._zoom = max(self._min_zoom, min(self._max_zoom, self._zoom))
        self.update_display()
    
    def set_zoom(self, zoom: float):
        """Установка зума вручную"""
        self._zoom = max(self._min_zoom, min(self._max_zoom, zoom))
        self.update_display()
    
    def get_zoom(self) -> float:
        return self._zoom
    
    def reset_zoom(self):
        """Сброс зума"""
        self._zoom = 1.0
        self.update_display()


# ============================================================================
# Главный виджет
# ============================================================================

class CameraWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.worker = None
        self.image_data = None
        self.is_connected = False
        self.current_config = CameraCommandConfig("CM 2.0")
        self.configs: Dict[str, CameraCommandConfig] = {}
        
        self.current_width = 640
        self.current_height = 480
        self.current_v_start = 0
        self.current_h_start = 0
        
        # Сначала создаем UI
        self.setup_ui()
        
        # Потом загружаем конфигурации (уже после создания log_text)
        self.load_default_configs()
        self.load_configs_from_folder()
        
        self.refresh_ports()
        self.add_log("🚀 Универсальная камера запущена")
        self.add_log("💡 Используйте колесико мыши для зума")
    
    def load_default_configs(self):
        """Загрузка конфигурации по умолчанию"""
        self.configs["CM 2.0"] = CameraCommandConfig(
            name="CM 2.0",
            description="Стандартная камера CM 2.0"
        )
        self.current_config = self.configs["CM 2.0"]
        self.update_config_list()
    
    def load_configs_from_folder(self):
        """Загрузка конфигураций из папки configs"""
        config_dir = Path.cwd() / "configs"
        if not config_dir.exists():
            config_dir.mkdir(exist_ok=True)
            example_path = config_dir / "example_config.json"
            if not example_path.exists():
                example = CameraCommandConfig(
                    name="Example Camera",
                    description="Пример конфигурации",
                    capture="t", properties="p", next_chunk="n",
                    set_size="s", set_exposure="e", start_transfer="r"
                )
                with open(example_path, 'w', encoding='utf-8') as f:
                    json.dump(example.to_dict(), f, indent=2, ensure_ascii=False)
        
        for json_path in config_dir.glob("*.json"):
            try:
                with open(json_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                config = CameraCommandConfig.from_dict(data)
                self.configs[config.name] = config
                self.add_log(f"📂 Загружена конфигурация: {config.name}")
            except Exception as e:
                self.add_log(f"⚠️ Ошибка загрузки {json_path.name}: {e}")
        
        self.update_config_list()
    
    def setup_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setSpacing(8)
        
        # Заголовок
        title = QLabel("📷 ИЩИ СЕБЯ В ПРОШМАНОВКАХ АЗЕРБАЙДЖАНА🫦")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title.setStyleSheet(
            "font-size: 18px; font-weight: bold; padding: 8px; "
            "background-color: #2d2d2d; color: white; border-radius: 4px;"
        )
        main_layout.addWidget(title)
        
        # Верхняя панель управления
        control_panel = QWidget()
        control_layout = QHBoxLayout(control_panel)
        control_layout.setSpacing(10)
        
        # Конфигурация
        config_widget = QWidget()
        config_layout = QHBoxLayout(config_widget)
        config_layout.setSpacing(5)
        config_layout.addWidget(QLabel("Профиль:"))
        self.config_combo = QComboBox()
        self.config_combo.currentIndexChanged.connect(self.on_config_changed)
        config_layout.addWidget(self.config_combo)
        
        self.add_config_btn = QPushButton("➕")
        self.add_config_btn.setToolTip("Создать новую конфигурацию")
        self.add_config_btn.setFixedWidth(30)
        self.add_config_btn.clicked.connect(self.create_config)
        config_layout.addWidget(self.add_config_btn)
        
        self.load_config_btn = QPushButton("📂")
        self.load_config_btn.setToolTip("Загрузить конфигурацию из файла")
        self.load_config_btn.setFixedWidth(30)
        self.load_config_btn.clicked.connect(self.load_config_file)
        config_layout.addWidget(self.load_config_btn)
        
        control_layout.addWidget(config_widget)
        control_layout.addStretch()
        
        # Подключение
        conn_widget = QWidget()
        conn_layout = QHBoxLayout(conn_widget)
        conn_layout.setSpacing(5)
        
        self.port_combo = QComboBox()
        self.port_combo.setMinimumWidth(80)
        conn_layout.addWidget(QLabel("Порт:"))
        conn_layout.addWidget(self.port_combo)
        
        self.refresh_btn = QPushButton("🔄")
        self.refresh_btn.setFixedWidth(30)
        self.refresh_btn.clicked.connect(self.refresh_ports)
        conn_layout.addWidget(self.refresh_btn)
        
        self.connect_btn = QPushButton("🔌 Подключить")
        self.connect_btn.clicked.connect(self.toggle_connection)
        conn_layout.addWidget(self.connect_btn)
        
        control_layout.addWidget(conn_widget)
        
        main_layout.addWidget(control_panel)
        
        # Основной сплиттер
        splitter = QSplitter(Qt.Orientation.Vertical)
        
        # Верхняя часть - управление
        control_widget = QWidget()
        control_layout = QVBoxLayout(control_widget)
        control_layout.setSpacing(5)
        
        # Настройки
        settings_group = QGroupBox("Настройки")
        settings_layout = QGridLayout(settings_group)
        settings_layout.setSpacing(5)
        
        settings_layout.addWidget(QLabel("Ширина:"), 0, 0)
        self.width_spin = QSpinBox()
        self.width_spin.setRange(1, 1280)
        self.width_spin.setValue(640)
        self.width_spin.setFixedWidth(60)
        settings_layout.addWidget(self.width_spin, 0, 1)
        
        settings_layout.addWidget(QLabel("Высота:"), 0, 2)
        self.height_spin = QSpinBox()
        self.height_spin.setRange(1, 1024)
        self.height_spin.setValue(480)
        self.height_spin.setFixedWidth(60)
        settings_layout.addWidget(self.height_spin, 0, 3)
        
        self.set_size_btn = QPushButton("Размер")
        self.set_size_btn.clicked.connect(self.apply_resolution)
        self.set_size_btn.setFixedWidth(60)
        settings_layout.addWidget(self.set_size_btn, 0, 4)
        
        settings_layout.addWidget(QLabel("vStart:"), 1, 0)
        self.v_start_spin = QSpinBox()
        self.v_start_spin.setRange(0, 1000)
        self.v_start_spin.setFixedWidth(60)
        settings_layout.addWidget(self.v_start_spin, 1, 1)
        
        settings_layout.addWidget(QLabel("hStart:"), 1, 2)
        self.h_start_spin = QSpinBox()
        self.h_start_spin.setRange(0, 1000)
        self.h_start_spin.setFixedWidth(60)
        settings_layout.addWidget(self.h_start_spin, 1, 3)
        
        self.set_crop_btn = QPushButton("Обрезка")
        self.set_crop_btn.clicked.connect(self.apply_crop)
        self.set_crop_btn.setFixedWidth(60)
        settings_layout.addWidget(self.set_crop_btn, 1, 4)
        
        settings_layout.addWidget(QLabel("Эксп:"), 2, 0)
        self.exposure_spin = QSpinBox()
        self.exposure_spin.setRange(0, 509)
        self.exposure_spin.setValue(0)
        self.exposure_spin.setFixedWidth(60)
        settings_layout.addWidget(self.exposure_spin, 2, 1)
        
        self.auto_exp_check = QCheckBox("Авто")
        self.auto_exp_check.setChecked(True)
        self.auto_exp_check.toggled.connect(self.toggle_auto_exposure)
        settings_layout.addWidget(self.auto_exp_check, 2, 2)
        
        self.set_exp_btn = QPushButton("Экспозиция")
        self.set_exp_btn.clicked.connect(self.apply_exposure)
        self.set_exp_btn.setFixedWidth(70)
        settings_layout.addWidget(self.set_exp_btn, 2, 3)
        
        control_layout.addWidget(settings_group)
        
        # Кнопки управления
        control_btns = QHBoxLayout()
        
        self.capture_btn = QPushButton("📸 Снимок")
        self.capture_btn.clicked.connect(self.capture_image)
        self.capture_btn.setEnabled(False)
        control_btns.addWidget(self.capture_btn)
        
        self.download_btn = QPushButton("⬇ Скачать")
        self.download_btn.clicked.connect(self.download_image)
        self.download_btn.setEnabled(False)
        control_btns.addWidget(self.download_btn)
        
        self.props_btn = QPushButton("ℹ Свойства")
        self.props_btn.clicked.connect(self.get_properties)
        self.props_btn.setEnabled(False)
        control_btns.addWidget(self.props_btn)
        
        self.save_btn = QPushButton("💾 Сохранить")
        self.save_btn.clicked.connect(self.save_image)
        self.save_btn.setEnabled(False)
        control_btns.addWidget(self.save_btn)
        
        self.clear_btn = QPushButton("🗑 Очистить")
        self.clear_btn.clicked.connect(self.clear_all)
        control_btns.addWidget(self.clear_btn)
        
        control_layout.addLayout(control_btns)
        
        # Прогресс
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        self.progress_bar.setFixedHeight(20)
        control_layout.addWidget(self.progress_bar)
        
        # Статус
        self.status_label = QLabel("Готов к работе")
        self.status_label.setStyleSheet("padding: 2px; color: #666;")
        control_layout.addWidget(self.status_label)
        
        control_layout.addStretch()
        splitter.addWidget(control_widget)
        
        # Нижняя часть - вкладки
        tabs = QTabWidget()
        
        # Вкладка изображения
        image_tab = QWidget()
        image_layout = QVBoxLayout(image_tab)
        image_layout.setContentsMargins(5, 5, 5, 5)
        
        image_container = QWidget()
        image_container_layout = QVBoxLayout(image_container)
        image_container_layout.setSpacing(5)
        
        # Ползунок зума
        zoom_widget = QWidget()
        zoom_layout = QHBoxLayout(zoom_widget)
        zoom_layout.setSpacing(5)
        zoom_layout.addWidget(QLabel("🔍"))
        
        self.zoom_slider = QSlider(Qt.Orientation.Horizontal)
        self.zoom_slider.setMinimum(10)
        self.zoom_slider.setMaximum(200)
        self.zoom_slider.setValue(100)
        self.zoom_slider.setTickInterval(10)
        self.zoom_slider.valueChanged.connect(self.on_zoom_changed)
        zoom_layout.addWidget(self.zoom_slider)
        
        self.zoom_label = QLabel("100%")
        self.zoom_label.setFixedWidth(50)
        zoom_layout.addWidget(self.zoom_label)
        
        self.reset_zoom_btn = QPushButton("1:1")
        self.reset_zoom_btn.setFixedWidth(40)
        self.reset_zoom_btn.clicked.connect(self.reset_zoom)
        zoom_layout.addWidget(self.reset_zoom_btn)
        
        zoom_layout.addStretch()
        image_container_layout.addWidget(zoom_widget)
        
        # Изображение
        self.image_label = ZoomableImageLabel()
        image_container_layout.addWidget(self.image_label)
        
        # Информация
        self.image_info = QLabel("")
        self.image_info.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.image_info.setStyleSheet("color: #666; font-size: 10px;")
        image_container_layout.addWidget(self.image_info)
        
        image_layout.addWidget(image_container)
        tabs.addTab(image_tab, "🖼 Изображение")
        
        # Вкладка логов
        log_tab = QWidget()
        log_layout = QVBoxLayout(log_tab)
        log_layout.setContentsMargins(5, 5, 5, 5)
        
        self.log_text = QTextEdit()
        self.log_text.setReadOnly(True)
        self.log_text.setStyleSheet(
            "background-color: #1e1e1e; color: #d4d4d4; "
            "font-family: monospace; font-size: 10px;"
        )
        self.log_text.setMaximumHeight(150)
        log_layout.addWidget(self.log_text)
        
        clear_log_btn = QPushButton("Очистить")
        clear_log_btn.clicked.connect(lambda: self.log_text.clear())
        log_layout.addWidget(clear_log_btn)
        
        tabs.addTab(log_tab, "📋 Логи")
        
        splitter.addWidget(tabs)
        splitter.setSizes([350, 350])
        
        main_layout.addWidget(splitter)
    
    def update_config_list(self):
        """Обновление списка конфигураций"""
        self.config_combo.clear()
        for name in sorted(self.configs.keys()):
            self.config_combo.addItem(name)
        if self.current_config.name in self.configs:
            self.config_combo.setCurrentText(self.current_config.name)
    
    def on_config_changed(self):
        """Смена конфигурации"""
        name = self.config_combo.currentText()
        if name in self.configs:
            self.current_config = self.configs[name]
            if self.worker:
                self.worker.set_config(self.current_config)
            self.add_log(f"📋 Профиль: {name}")
    
    def create_config(self):
        """Создание новой конфигурации"""
        dialog = CreateConfigDialog(self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            config = dialog.get_config()
            if config.name in self.configs:
                reply = QMessageBox.question(
                    self, "Конфигурация существует",
                    f"Конфигурация '{config.name}' уже существует. Перезаписать?",
                    QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
                )
                if reply == QMessageBox.StandardButton.No:
                    return
            
            self.configs[config.name] = config
            self.update_config_list()
            self.config_combo.setCurrentText(config.name)
            self.add_log(f"✅ Создана конфигурация: {config.name}")
            
            config_dir = Path.cwd() / "configs"
            config_dir.mkdir(exist_ok=True)
            file_path = config_dir / f"{config.name.replace(' ', '_')}.json"
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(config.to_dict(), f, indent=2, ensure_ascii=False)
            self.add_log(f"💾 Сохранена в: {file_path}")
    
    def load_config_file(self):
        """Загрузка конфигурации из файла"""
        path, _ = QFileDialog.getOpenFileName(
            self, "Загрузить конфигурацию", "configs", "JSON Files (*.json)"
        )
        if path:
            try:
                with open(path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                config = CameraCommandConfig.from_dict(data)
                self.configs[config.name] = config
                self.update_config_list()
                self.config_combo.setCurrentText(config.name)
                self.add_log(f"✅ Загружена конфигурация: {config.name}")
            except Exception as e:
                self.add_log(f"❌ Ошибка загрузки: {e}")
                QMessageBox.critical(self, "Ошибка", str(e))
    
    def on_zoom_changed(self, value: int):
        """Изменение зума"""
        zoom = value / 100.0
        self.image_label.set_zoom(zoom)
        self.zoom_label.setText(f"{value}%")
    
    def reset_zoom(self):
        """Сброс зума"""
        self.zoom_slider.setValue(100)
        self.zoom_label.setText("100%")
        self.image_label.reset_zoom()
    
    # ------------------------------------------------------------------------
    # Управление портом
    # ------------------------------------------------------------------------
    
    def refresh_ports(self):
        current = self.port_combo.currentText()
        self.port_combo.clear()
        try:
            import serial.tools.list_ports
            ports = [p.device for p in serial.tools.list_ports.comports()]
            self.port_combo.addItems(ports)
        except:
            pass
        if current:
            idx = self.port_combo.findText(current)
            if idx >= 0:
                self.port_combo.setCurrentIndex(idx)
    
    def toggle_connection(self):
        if self.is_connected:
            self.disconnect()
        else:
            self.connect()
    
    def connect(self):
        port = self.port_combo.currentText()
        if not port:
            QMessageBox.warning(self, "Ошибка", "Выберите порт")
            return
        
        self.worker = CameraWorker()
        self.worker.set_config(self.current_config)
        
        self.worker.progress.connect(self.update_progress)
        self.worker.partial_image.connect(self.show_partial_image)
        self.worker.image_data.connect(self.display_image)
        self.worker.log.connect(self.add_log)
        self.worker.error.connect(self.show_error)
        self.worker.properties_received.connect(self.show_properties)
        self.worker.finished.connect(self.on_worker_finished)
        self.worker.capture_complete.connect(self.on_capture_complete)
        
        if self.worker.connect(port):
            self.is_connected = True
            self.connect_btn.setText("🔌 Отключить")
            self.status_label.setText("✅ Подключен")
            self.status_label.setStyleSheet("color: #4CAF50;")
            self.capture_btn.setEnabled(True)
            self.download_btn.setEnabled(True)
            self.props_btn.setEnabled(True)
            self.add_log("✅ Готов к работе")
    
    def disconnect(self):
        if self.worker:
            self.worker.running = False
            if self.worker.isRunning():
                self.worker.quit()
                self.worker.wait(1000)
            self.worker.disconnect()
            self.worker = None
        
        self.is_connected = False
        self.connect_btn.setText("🔌 Подключить")
        self.status_label.setText("⛔ Отключен")
        self.status_label.setStyleSheet("color: #f44336;")
        self.capture_btn.setEnabled(False)
        self.download_btn.setEnabled(False)
        self.props_btn.setEnabled(False)
        self.save_btn.setEnabled(False)
        self.progress_bar.setVisible(False)
    
    # ------------------------------------------------------------------------
    # Действия
    # ------------------------------------------------------------------------
    
    def capture_image(self):
        if self.worker:
            self.capture_btn.setEnabled(False)
            self.download_btn.setEnabled(False)
            self.add_log("📸 Запуск захвата...")
            self.worker.start_capture()
    
    def get_properties(self):
        if self.worker:
            self.worker.start_properties()
    
    def download_image(self):
        if self.worker:
            self.progress_bar.setVisible(True)
            self.progress_bar.setValue(0)
            self.download_btn.setEnabled(False)
            self.capture_btn.setEnabled(False)
            self.add_log("📥 Загрузка...")
            self.worker.start_download()
    
    def apply_resolution(self):
        if self.worker:
            w = self.width_spin.value()
            h = self.height_spin.value()
            self.current_width = w
            self.current_height = h
            self.worker.set_resolution(w, h)
    
    def apply_crop(self):
        self.current_v_start = self.v_start_spin.value()
        self.current_h_start = self.h_start_spin.value()
        if self.worker:
            self.worker.set_crop(self.current_v_start, self.current_h_start)
    
    def apply_exposure(self):
        if self.worker:
            exp = self.exposure_spin.value()
            self.worker.set_exposure(exp)
    
    def toggle_auto_exposure(self, checked):
        self.exposure_spin.setEnabled(not checked)
        if checked:
            self.exposure_spin.setValue(0)
            if self.worker:
                self.worker.set_exposure(0)
    
    def save_image(self):
        if not self.image_data:
            return
        
        save_dir = Path.cwd() / "captures"
        save_dir.mkdir(exist_ok=True)
        ts = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        w = self.current_width
        h = self.current_height
        data = self.image_data[:w*h]
        
        try:
            img = Image.frombytes("L", (w, h), data)
            png_path = save_dir / f"capture_{ts}.png"
            img.save(png_path, "PNG")
            self.add_log(f"💾 Сохранено: {png_path.name}")
            
            info_path = save_dir / f"capture_{ts}.txt"
            with open(info_path, 'w', encoding='utf-8') as f:
                f.write(f"=== Снимок ===\n")
                f.write(f"Профиль: {self.current_config.name}\n")
                f.write(f"Размер: {w}x{h}\n")
                f.write(f"vStart: {self.current_v_start}\n")
                f.write(f"hStart: {self.current_h_start}\n")
                f.write(f"Дата: {datetime.now()}\n")
            
            QMessageBox.information(self, "Сохранено", 
                f"Изображение сохранено:\n{png_path}")
                
        except Exception as e:
            self.add_log(f"❌ Ошибка: {e}")
            QMessageBox.critical(self, "Ошибка", str(e))
    
    def clear_all(self):
        self.image_label.clear()
        self.image_label.setText("Нет изображения")
        self.image_info.setText("")
        self.image_data = None
        self.save_btn.setEnabled(False)
        self.progress_bar.setValue(0)
        self.add_log("🗑 Очищено")
    
    # ------------------------------------------------------------------------
    # Обработчики
    # ------------------------------------------------------------------------
    
    def update_progress(self, v):
        self.progress_bar.setValue(v)
    
    def show_partial_image(self, data, w, h):
        try:
            expected = w * h
            show = data[:expected]
            if len(show) < expected:
                show += b'\x00' * (expected - len(show))
            img = QImage(show, w, h, w, QImage.Format_Grayscale8)
            pix = QPixmap.fromImage(img)
            self.image_label.set_image(pix)
            percent = int(len(data) / expected * 100) if expected > 0 else 0
            self.image_info.setText(f"Загрузка... {percent}% ({len(data)}/{expected})")
        except Exception as e:
            self.add_log(f"⚠️ {e}")
    
    def display_image(self, data):
        self.image_data = data
        w, h = self.current_width, self.current_height
        try:
            img_data = data[:w*h]
            if len(img_data) < w*h:
                img_data += b'\x00' * (w*h - len(img_data))
            img = QImage(img_data, w, h, w, QImage.Format_Grayscale8)
            pix = QPixmap.fromImage(img)
            self.image_label.set_image(pix)
            self.image_info.setText(f"✅ {w}×{h} | {len(data)} байт")
            self.save_btn.setEnabled(True)
            self.add_log(f"✅ Изображение загружено")
        except Exception as e:
            self.add_log(f"❌ {e}")
    
    def show_properties(self, props):
        if props.get('chunks', 0) > 0:
            msg = (f"Снимок: {props.get('width', 0)}×{props.get('height', 0)}\n"
                   f"Чанков: {props.get('chunks', 0)}\n"
                   f"Размер: {props.get('length', 0)} байт")
        else:
            msg = "Нет снимка"
        QMessageBox.information(self, "Свойства", msg)
    
    def on_capture_complete(self):
        self.capture_btn.setEnabled(True)
        self.download_btn.setEnabled(True)
        self.add_log("✅ Снимок готов!")
    
    def on_worker_finished(self):
        self.capture_btn.setEnabled(True)
        self.download_btn.setEnabled(True)
        self.props_btn.setEnabled(True)
        self.progress_bar.setVisible(False)
    
    def show_error(self, msg):
        self.add_log(f"❌ {msg}")
        self.capture_btn.setEnabled(True)
        self.download_btn.setEnabled(True)
        self.props_btn.setEnabled(True)
        self.progress_bar.setVisible(False)
        QMessageBox.critical(self, "Ошибка", msg)
    
    def add_log(self, msg):
        ts = datetime.now().strftime("%H:%M:%S")
        self.log_text.append(f"[{ts}] {msg}")
        scroll = self.log_text.verticalScrollBar()
        scroll.setValue(scroll.maximum())


if __name__ == "__main__":
    import sys
    from PySide6.QtWidgets import QApplication
    
    app = QApplication(sys.argv)
    win = CameraWidget()
    win.setWindowTitle("Универсальная камера")
    win.setMinimumSize(700, 600)
    win.show()
    sys.exit(app.exec())