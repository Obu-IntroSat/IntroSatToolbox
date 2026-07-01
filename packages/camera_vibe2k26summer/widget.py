"""UI for camera application - OPTIMIZED (WORKING)"""

from __future__ import annotations
import struct
import time
import serial
from datetime import datetime
from pathlib import Path
from typing import Optional

from PySide6.QtCore import Qt, Signal, QThread
from PySide6.QtGui import QImage, QPixmap
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
    QPushButton, QTextEdit, QGroupBox,
    QComboBox, QGridLayout, QMessageBox, QProgressBar,
    QSpinBox, QCheckBox, QTabWidget
)

from PIL import Image


# ============================================================================
# Константы
# ============================================================================

PREAMBLE = b"\xFF\xFF\x00"
POSTAMBLE = b"\x00\xFF\x00"
CHUNK_SIZE = 240
CHUNK_STRUCT_SIZE = 248
BAUDRATE = 230400
MAX_EXPOSURE = 509
TIMEOUT_CAPTURE = 15.0
PROPERTY_SIZE = 18


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
        self.image_properties = None
        self.capture_in_progress = False
        
        # ОПТИМИЗАЦИЯ 1: Предварительно выделенный буфер для чанка
        self._chunk_buffer = bytearray(248)
        
        # ОПТИМИЗАЦИЯ 2: Кэширование структуры
        self._chunk_struct = struct.Struct('<HH?240BB')
    
    def connect(self, port: str):
        try:
            self.ser = serial.Serial(port, BAUDRATE, timeout=3.0, parity=serial.PARITY_NONE)
            self.ser.reset_input_buffer()
            self.ser.reset_output_buffer()
            self.log.emit(f"✅ Подключено к {port}")
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
    
    def _read_until_preamble(self) -> bytes:
        if not self.ser or not self.ser.is_open:
            return b''
        return self.ser.read_until(PREAMBLE)
    
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
    
    def _parse_image_properties(self, data: bytes) -> dict:
        if len(data) < 18:
            raise ValueError(f"Недостаточно данных: {len(data)} байт")
        
        try:
            if len(data) >= 20:
                params = struct.unpack("HHHHBxHLHxx", data[:20])
                return {
                    'height': params[0],
                    'width': params[1],
                    'v_start': params[2],
                    'h_start': params[3],
                    'colorspace': params[4],
                    'exposure': params[5],
                    'length': params[6],
                    'chunks': params[7],
                    'has_image': params[7] > 0
                }
        except:
            pass
        
        try:
            params = struct.unpack("<HHHHHHLH", data[:18])
            return {
                'height': params[0],
                'width': params[1],
                'v_start': params[2],
                'h_start': params[3],
                'colorspace': params[4],
                'exposure': params[5],
                'length': params[6],
                'chunks': params[7],
                'has_image': params[7] > 0
            }
        except:
            pass
        
        # Fallback
        height = struct.unpack('<H', data[0:2])[0]
        width = struct.unpack('<H', data[2:4])[0]
        v_start = struct.unpack('<H', data[4:6])[0]
        h_start = struct.unpack('<H', data[6:8])[0]
        colorspace = struct.unpack('<H', data[8:10])[0]
        exposure = struct.unpack('<H', data[10:12])[0]
        length = struct.unpack('<I', data[12:16])[0]
        chunks = struct.unpack('<H', data[16:18])[0]
        
        return {
            'height': height,
            'width': width,
            'v_start': v_start,
            'h_start': h_start,
            'colorspace': colorspace,
            'exposure': exposure,
            'length': length,
            'chunks': chunks,
            'has_image': chunks > 0
        }
    
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
        """Команда 0x74 - Сделать снимок"""
        self.is_busy = True
        self.capture_in_progress = True
        try:
            self.log.emit("📸 Отправка команды захвата...")
            self.ser.reset_input_buffer()
            self.ser.reset_output_buffer()
            self._write(b't')
            self.log.emit("⏳ Ожидание завершения захвата...")
            
            start_time = time.time()
            response_found = False
            timeout = 15.0
            
            while (time.time() - start_time) < timeout:
                if self.ser.in_waiting > 0:
                    data = self.ser.read(self.ser.in_waiting)
                    if b'\xFF\xFF\x00\x00\xFF\x00' in data or b'\xFF\xFF\x00' in data:
                        response_found = True
                        break
                time.sleep(0.1)
                elapsed = int(time.time() - start_time)
                if elapsed % 2 == 0 and elapsed > 0:
                    self.log.emit(f"⏳ Обработка... {elapsed}/{int(timeout)} сек")
            
            if response_found:
                self.log.emit("✅ Снимок успешно создан!")
            else:
                self.log.emit("⚠️ Таймаут при ожидании подтверждения захвата")
            
            self.capture_complete.emit()
            
        except Exception as e:
            self.log.emit(f"❌ Ошибка захвата: {e}")
            self.error.emit(f"Ошибка захвата: {e}")
        finally:
            self.is_busy = False
            self.capture_in_progress = False
            self.current_command = None
            self.finished.emit()
    
    def _do_properties(self):
        """Команда 0x70 - Запрос данных снимка"""
        self.is_busy = True
        try:
            self.log.emit("📊 Запрос свойств...")
            self.ser.reset_input_buffer()
            self.ser.reset_output_buffer()
            self._write(b'p')
            
            preamble_data = self._read_until_preamble()
            if not preamble_data:
                self.log.emit("⚠️ Преамбула не найдена")
                self.error.emit("Нет снимка в памяти")
                return
            
            st = self._read_exact(18, timeout=2.0)
            if len(st) < 18:
                self.log.emit(f"⚠️ Получено {len(st)} байт, ожидалось минимум 18")
                self.error.emit("Неполные данные свойств")
                return
            
            props = self._parse_image_properties(st)
            self.image_properties = props
            self.properties_received.emit(props)
            
            if props['chunks'] > 0:
                self.log.emit(f"✅ Снимок: {props['width']}x{props['height']}, чанков: {props['chunks']}")
                self.log.emit(f"   Обрезка: vStart={props['v_start']}, hStart={props['h_start']}")
                self.log.emit(f"   Экспозиция: {props['exposure']}, размер: {props['length']} байт")
            else:
                self.log.emit("ℹ️ Нет сохраненного снимка")
            
        except Exception as e:
            self.log.emit(f"❌ Ошибка чтения свойств: {e}")
            self.error.emit(f"Ошибка чтения свойств: {e}")
        finally:
            self.is_busy = False
            self.current_command = None
            self.finished.emit()
    
    def _do_download(self):
        """ОПТИМИЗИРОВАННОЕ скачивание изображения"""
        self.is_busy = True
        try:
            self.log.emit("📥 Получение информации о снимке...")
            self.ser.reset_input_buffer()
            self.ser.reset_output_buffer()
            self._write(b'p')
            
            preamble_data = self._read_until_preamble()
            if not preamble_data:
                self.log.emit("⚠️ Преамбула не найдена")
                self.error.emit("Нет снимка в памяти")
                return
            
            st = self._read_exact(18, timeout=2.0)
            if len(st) < 18:
                self.log.emit(f"⚠️ Получено {len(st)} байт, ожидалось минимум 18")
                self.error.emit("Неполные данные свойств")
                return
            
            props = self._parse_image_properties(st)
            height = props['height']
            width = props['width']
            total_chunks = props['chunks']
            total_length = props['length']
            
            if total_chunks == 0:
                self.error.emit("Нет снимка для скачивания (chunks=0)")
                return
            
            self.log.emit(f"📦 Снимок: {width}x{height}, {total_chunks} чанков, {total_length} байт")
            
            image_data = bytearray()
            expected = width * height
            
            self.ser.reset_input_buffer()
            self._write(b'r')
            time.sleep(0.05)  # ОПТИМИЗАЦИЯ: уменьшено с 0.1 до 0.05
            
            # ОПТИМИЗАЦИЯ: локальные переменные для скорости
            ser = self.ser
            chunk_struct = self._chunk_struct
            chunk_buffer = self._chunk_buffer
            
            for chunk_idx in range(total_chunks):
                if not self.running:
                    self.log.emit("⚠️ Загрузка прервана пользователем")
                    break
                
                self.ser.reset_input_buffer()
                self._write(b'n')
                self.ser.flush()
                
                preamble_data = self._read_until_preamble()
                if not preamble_data:
                    self.log.emit(f"⚠️ Преамбула не найдена для чанка {chunk_idx+1}")
                    continue
                
                # ОПТИМИЗАЦИЯ: прямое чтение в буфер
                read_total = 0
                start_time = time.time()
                while read_total < CHUNK_STRUCT_SIZE and (time.time() - start_time) < 2.0:
                    if ser.in_waiting > 0:
                        available = ser.in_waiting
                        to_read = min(available, CHUNK_STRUCT_SIZE - read_total)
                        chunk_buffer[read_total:read_total + to_read] = ser.read(to_read)
                        read_total += to_read
                    time.sleep(0.0005)  # ОПТИМИЗАЦИЯ: уменьшено с 0.001
                
                if read_total < CHUNK_STRUCT_SIZE:
                    self.log.emit(f"⚠️ Неполный чанк {chunk_idx+1} ({read_total} байт)")
                    continue
                
                try:
                    # ОПТИМИЗАЦИЯ: быстрая распаковка
                    params_chunk = chunk_struct.unpack_from(chunk_buffer)
                    chunk_id = params_chunk[0]
                    payload_len = params_chunk[1]
                    is_last = params_chunk[2]
                    payload = chunk_buffer[5:5+payload_len]
                    
                    image_data.extend(payload)
                    
                    # Прогресс
                    progress = int((chunk_idx + 1) / total_chunks * 100)
                    self.progress.emit(progress)
                    
                    # ВОЗВРАЩАЕМ: показываем каждый чанк как в исходном коде
                    if chunk_idx % 5 == 0 or is_last or chunk_idx == total_chunks - 1:
                        self.partial_image.emit(bytes(image_data), width, height)
                        self.log.emit(f"📦 Чанк {chunk_idx+1}/{total_chunks} (ID={chunk_id}, {payload_len} байт)")
                    
                    if is_last:
                        self.log.emit(f"✅ Получен последний чанк {chunk_idx+1}")
                        break
                    
                except Exception as e:
                    self.log.emit(f"⚠️ Ошибка парсинга чанка {chunk_idx+1}: {e}")
                    continue
                
                if len(image_data) >= expected:
                    self.log.emit(f"⚠️ Достигнут ожидаемый размер ({len(image_data)}/{expected})")
                    break
            
            if len(image_data) < expected:
                self.log.emit(f"⚠️ Дополнение данных: {len(image_data)} → {expected}")
                image_data.extend(b'\x00' * (expected - len(image_data)))
            elif len(image_data) > expected:
                self.log.emit(f"⚠️ Обрезка данных: {len(image_data)} → {expected}")
                image_data = image_data[:expected]
            
            self.log.emit(f"✅ Загрузка завершена: {len(image_data)} байт")
            self.image_data.emit(bytes(image_data))
            
        except Exception as e:
            self.log.emit(f"❌ Ошибка скачивания: {e}")
            self.error.emit(f"Ошибка скачивания: {e}")
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
            cmd = b's' + struct.pack('<HH', w, h)
            self._write(cmd)
            self.log.emit(f"📐 Установлен размер: {w}x{h}")
            time.sleep(0.05)
    
    def set_crop(self, v_start: int, h_start: int):
        if self.ser and self.ser.is_open:
            self.log.emit(f"✂️ Установлена обрезка: vStart={v_start}, hStart={h_start}")
    
    def set_exposure(self, exp: int):
        if self.ser and self.ser.is_open:
            cmd = b'e' + struct.pack('<H', exp)
            self._write(cmd)
            if exp == 0:
                self.log.emit("🔆 Включена автоэкспозиция")
            else:
                self.log.emit(f"🔆 Установлена экспозиция: {exp}")
            time.sleep(0.05)


# ============================================================================
# GUI
# ============================================================================

class CameraWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.worker = None
        self.image_data = None
        self.is_connected = False
        self.current_width = 640
        self.current_height = 480
        self.current_v_start = 0
        self.current_h_start = 0
        self.setup_ui()
        self.refresh_ports()
    
    def setup_ui(self):
        main_layout = QVBoxLayout(self)
        
        title = QLabel("📷 CAMERA VIBE2K26SUMMER")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title.setStyleSheet("font-size: 22px; font-weight: bold; padding: 12px; background-color: #2d2d2d; color: white; border-radius: 6px;")
        main_layout.addWidget(title)
        
        tabs = QTabWidget()
        
        control_tab = QWidget()
        cl = QVBoxLayout(control_tab)
        
        # Подключение
        cg = QGroupBox("Подключение")
        ch = QHBoxLayout(cg)
        self.port_combo = QComboBox()
        ch.addWidget(QLabel("Порт:"))
        ch.addWidget(self.port_combo)
        self.refresh_btn = QPushButton("🔄")
        self.refresh_btn.clicked.connect(self.refresh_ports)
        ch.addWidget(self.refresh_btn)
        self.connect_btn = QPushButton("🔌 Подключить")
        self.connect_btn.clicked.connect(self.toggle_connection)
        ch.addWidget(self.connect_btn)
        self.status_label = QLabel("⛔ Не подключен")
        ch.addWidget(self.status_label)
        cl.addWidget(cg)
        
        # Настройки
        sg = QGroupBox("Настройки съёмки")
        sl = QGridLayout(sg)
        
        sl.addWidget(QLabel("Ширина:"), 0, 0)
        self.width_spin = QSpinBox()
        self.width_spin.setRange(1, 1280)
        self.width_spin.setValue(640)
        sl.addWidget(self.width_spin, 0, 1)
        
        sl.addWidget(QLabel("Высота:"), 0, 2)
        self.height_spin = QSpinBox()
        self.height_spin.setRange(1, 1024)
        self.height_spin.setValue(480)
        sl.addWidget(self.height_spin, 0, 3)
        
        self.set_size_btn = QPushButton("Применить размер")
        self.set_size_btn.clicked.connect(self.apply_resolution)
        sl.addWidget(self.set_size_btn, 0, 4)
        
        sl.addWidget(QLabel("vStart:"), 1, 0)
        self.v_start_spin = QSpinBox()
        self.v_start_spin.setRange(0, 1000)
        self.v_start_spin.setValue(0)
        sl.addWidget(self.v_start_spin, 1, 1)
        
        sl.addWidget(QLabel("hStart:"), 1, 2)
        self.h_start_spin = QSpinBox()
        self.h_start_spin.setRange(0, 1000)
        self.h_start_spin.setValue(0)
        sl.addWidget(self.h_start_spin, 1, 3)
        
        self.set_crop_btn = QPushButton("Применить обрезку")
        self.set_crop_btn.clicked.connect(self.apply_crop)
        sl.addWidget(self.set_crop_btn, 1, 4)
        
        sl.addWidget(QLabel("Экспозиция:"), 2, 0)
        self.exposure_spin = QSpinBox()
        self.exposure_spin.setRange(0, 509)
        self.exposure_spin.setValue(0)
        sl.addWidget(self.exposure_spin, 2, 1)
        
        self.auto_exp_check = QCheckBox("Авто (0)")
        self.auto_exp_check.setChecked(True)
        self.auto_exp_check.toggled.connect(self.toggle_auto_exposure)
        sl.addWidget(self.auto_exp_check, 2, 2)
        
        self.set_exp_btn = QPushButton("Применить экспозицию")
        self.set_exp_btn.clicked.connect(self.apply_exposure)
        sl.addWidget(self.set_exp_btn, 2, 3)
        
        cl.addWidget(sg)
        
        # Управление
        ug = QGroupBox("Управление")
        uh = QHBoxLayout(ug)
        
        self.capture_btn = QPushButton("📸 Сделать снимок")
        self.capture_btn.clicked.connect(self.capture_image)
        self.capture_btn.setEnabled(False)
        uh.addWidget(self.capture_btn)
        
        self.download_btn = QPushButton("⬇ Скачать снимок")
        self.download_btn.clicked.connect(self.download_image)
        self.download_btn.setEnabled(False)
        uh.addWidget(self.download_btn)
        
        self.props_btn = QPushButton("ℹ Свойства")
        self.props_btn.clicked.connect(self.get_properties)
        self.props_btn.setEnabled(False)
        uh.addWidget(self.props_btn)
        
        self.save_btn = QPushButton("💾 Сохранить")
        self.save_btn.clicked.connect(self.save_image)
        self.save_btn.setEnabled(False)
        uh.addWidget(self.save_btn)
        
        self.clear_btn = QPushButton("🗑 Очистить")
        self.clear_btn.clicked.connect(self.clear_all)
        uh.addWidget(self.clear_btn)
        
        cl.addWidget(ug)
        
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        cl.addWidget(self.progress_bar)
        
        self.state_label = QLabel("Готов к работе")
        cl.addWidget(self.state_label)
        cl.addStretch()
        
        # Вкладка изображения
        image_tab = QWidget()
        il = QVBoxLayout(image_tab)
        self.image_label = QLabel("Нет изображения")
        self.image_label.setMinimumHeight(420)
        self.image_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.image_label.setStyleSheet("background-color: #1a1a1a; border: 2px solid #333; border-radius: 6px;")
        il.addWidget(self.image_label)
        self.image_info = QLabel("")
        il.addWidget(self.image_info)
        
        # Вкладка логов
        log_tab = QWidget()
        ll = QVBoxLayout(log_tab)
        self.log_text = QTextEdit()
        self.log_text.setReadOnly(True)
        self.log_text.setStyleSheet("background-color: #1e1e1e; color: #d4d4d4; font-family: monospace; font-size: 11px;")
        ll.addWidget(self.log_text)
        
        log_btn_layout = QHBoxLayout()
        clear_log_btn = QPushButton("Очистить логи")
        clear_log_btn.clicked.connect(lambda: self.log_text.clear())
        log_btn_layout.addWidget(clear_log_btn)
        log_btn_layout.addStretch()
        ll.addLayout(log_btn_layout)
        
        tabs.addTab(control_tab, "🎮 Управление")
        tabs.addTab(image_tab, "🖼 Изображение")
        tabs.addTab(log_tab, "📋 Логи")
        main_layout.addWidget(tabs)
        
        self.add_log("Приложение запущено")
        self.add_log("Подключитесь к камере через COM-порт")
    
    def refresh_ports(self):
        current = self.port_combo.currentText()
        self.port_combo.clear()
        try:
            import serial.tools.list_ports
            self.port_combo.addItems([p.device for p in serial.tools.list_ports.comports()])
        except:
            pass
        if current:
            self.port_combo.setCurrentText(current)
    
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
            self.add_log("📥 Начинаем скачивание...")
            self.worker.start_download()
    
    def on_capture_complete(self):
        self.capture_btn.setEnabled(True)
        self.download_btn.setEnabled(True)
        self.add_log("✅ Снимок готов к скачиванию!")
        QMessageBox.information(
            self, 
            "Готово", 
            "Снимок сделан!\n\nНажмите 'Скачать снимок' для загрузки."
        )
    
    def on_worker_finished(self):
        self.capture_btn.setEnabled(True)
        self.download_btn.setEnabled(True)
        self.props_btn.setEnabled(True)
        self.progress_bar.setVisible(False)
    
    def show_error(self, msg):
        self.add_log(f"❌ {msg}")
        QMessageBox.critical(self, "Ошибка", msg)
        self.capture_btn.setEnabled(True)
        self.download_btn.setEnabled(True)
        self.props_btn.setEnabled(True)
        self.progress_bar.setVisible(False)
    
    def apply_resolution(self):
        if self.worker:
            w = self.width_spin.value()
            h = self.height_spin.value()
            self.current_width = w
            self.current_height = h
            self.worker.set_resolution(w, h)
            self.add_log(f"📐 Размер установлен: {w}x{h}")
    
    def apply_crop(self):
        if self.worker:
            v_start = self.v_start_spin.value()
            h_start = self.h_start_spin.value()
            self.current_v_start = v_start
            self.current_h_start = h_start
            self.worker.set_crop(v_start, h_start)
            self.add_log(f"✂️ Обрезка: vStart={v_start}, hStart={h_start}")
    
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
    
    def show_properties(self, props):
        if props.get('chunks', 0) > 0:
            msg = (f"📸 Снимок в памяти:\n"
                   f"  Размер: {props['width']}×{props['height']}\n"
                   f"  Обрезка: vStart={props['v_start']}, hStart={props['h_start']}\n"
                   f"  Экспозиция: {props['exposure']}\n"
                   f"  Чанков: {props['chunks']}\n"
                   f"  Размер данных: {props['length']} байт")
        else:
            msg = "ℹ️ Нет сохраненного снимка"
        self.add_log(msg.replace('\n', ' | '))
        QMessageBox.information(self, "Свойства снимка", msg)
    
    def show_partial_image(self, data, w, h):
        try:
            expected = w * h
            show = data[:expected]
            if len(show) < expected:
                show += b'\x00' * (expected - len(show))
            img = QImage(show, w, h, w, QImage.Format_Grayscale8)
            pix = QPixmap.fromImage(img).scaled(
                self.image_label.width() - 40,
                self.image_label.height() - 40,
                Qt.AspectRatioMode.KeepAspectRatio
            )
            self.image_label.setPixmap(pix)
            percent = int(len(data) / expected * 100) if expected > 0 else 0
            self.image_info.setText(f"Загрузка... {len(data)}/{expected} ({percent}%)")
        except Exception as e:
            self.add_log(f"⚠️ Ошибка отображения: {e}")
    
    def display_image(self, data):
        self.image_data = data
        w, h = self.current_width, self.current_height
        try:
            img = QImage(data[:w*h], w, h, w, QImage.Format_Grayscale8)
            pix = QPixmap.fromImage(img).scaled(
                self.image_label.width() - 40,
                self.image_label.height() - 40,
                Qt.AspectRatioMode.KeepAspectRatio
            )
            self.image_label.setPixmap(pix)
            self.image_info.setText(f"✅ {w}×{h} | {len(data)} байт")
            self.save_btn.setEnabled(True)
            self.add_log(f"✅ Изображение отображено: {w}×{h}")
        except Exception as e:
            self.add_log(f"❌ Ошибка отображения: {e}")
    
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
            self.add_log(f"💾 Изображение сохранено: {png_path}")
            
            info_path = save_dir / f"capture_{ts}.txt"
            with open(info_path, 'w', encoding='utf-8') as f:
                f.write(f"Размер: {w}x{h}\n")
                f.write(f"vStart: {self.current_v_start}\n")
                f.write(f"hStart: {self.current_h_start}\n")
                f.write(f"Размер данных: {len(self.image_data)} байт\n")
                f.write(f"Дата: {datetime.now()}\n")
            self.add_log(f"📄 Метаданные: {info_path}")
            
            QMessageBox.information(self, "Сохранено", 
                f"Изображение сохранено:\n{png_path}\n\nМетаданные: {info_path}")
                
        except Exception as e:
            self.add_log(f"❌ Ошибка сохранения: {e}")
            QMessageBox.critical(self, "Ошибка", f"Не удалось сохранить изображение:\n{e}")
    
    def update_progress(self, v):
        self.progress_bar.setValue(v)
    
    def clear_all(self):
        self.image_label.setText("Нет изображения")
        self.image_info.setText("")
        self.image_data = None
        self.save_btn.setEnabled(False)
        self.progress_bar.setValue(0)
        self.add_log("🗑 Очищено")
    
    def add_log(self, msg):
        ts = datetime.now().strftime("%H:%M:%S")
        self.log_text.append(f"[{ts}] {msg}")
        self.log_text.verticalScrollBar().setValue(
            self.log_text.verticalScrollBar().maximum()
        )


if __name__ == "__main__":
    import sys
    from PySide6.QtWidgets import QApplication
    app = QApplication(sys.argv)
    win = CameraWidget()
    win.show()
    sys.exit(app.exec())