"""Worker thread for camera operations."""

from __future__ import annotations
import struct
import time
from threading import Event
from typing import Optional

from PySide6.QtCore import QThread, Signal

from .config import CameraCommandConfig
from .models import CameraState


class CameraWorker(QThread):
    """Рабочий поток для операций с камерой"""
    
    progress = Signal(int)
    partial_image = Signal(bytes, int, int)
    image_data = Signal(bytes)
    log = Signal(str)
    finished = Signal()
    error = Signal(str)
    properties_received = Signal(dict)
    capture_complete = Signal()
    version_received = Signal(str)
    
    def __init__(self, config: CameraCommandConfig):
        super().__init__()
        self.config = config
        self.ser = None  # <-- Добавляем self.ser как в оригинале
        self.running = True
        self._stop_event = Event()
        self.is_busy = False
        self.current_command = None
        self.capture_in_progress = False
        
        self._chunk_buffer = bytearray(config.chunk_size + 8)
        self._chunk_struct = struct.Struct(config.chunk_format)
        self._prop_struct = struct.Struct(config.property_format)
        self._width = 640
        self._height = 480
        self._v_start = 0
        self._h_start = 0
        self._exposure = 0
        self._firmware_version = ""
    
    def set_config(self, config: CameraCommandConfig):
        self.config = config
        self._chunk_buffer = bytearray(config.chunk_size + 8)
        self._chunk_struct = struct.Struct(config.chunk_format)
        self._prop_struct = struct.Struct(config.property_format)
    
    def connect(self, port: str) -> bool:
        try:
            import serial
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
        while len(data) < size and (time.time() - start) < timeout and not self._stop_event.is_set():
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
    
    def get_version(self) -> str:
        """Запрос версии прошивки"""
        if not self.ser or not self.ser.is_open:
            self.log.emit("⚠️ Порт не открыт")
            return ""
        
        try:
            self.log.emit(f"📡 Запрос версии (команда: {self.config.get_version})...")
            self.ser.reset_input_buffer()
            self.ser.reset_output_buffer()
            
            cmd_bytes = self.config.get_command_bytes(self.config.get_version)
            self._write(cmd_bytes)
            self.ser.flush()
            
            preamble = bytes.fromhex(self.config.preamble)
            start_time = time.time()
            response = b""
            attempts = 0
            
            while (time.time() - start_time) < self.config.timeout_version and not self._stop_event.is_set():
                if self.ser.in_waiting > 0:
                    data = self.ser.read(self.ser.in_waiting)
                    response += data
                    attempts += 1
                    if preamble in response:
                        idx = response.find(preamble) + len(preamble)
                        version_data = response[idx:idx+20]
                        version = ""
                        for b in version_data:
                            if 32 <= b <= 126:
                                version += chr(b)
                            else:
                                break
                        if version:
                            self._firmware_version = version.strip()
                            self.log.emit(f"   ✅ Версия: {version}")
                            self.version_received.emit(version)
                            return version
                    elif attempts % 5 == 0:
                        self.log.emit(f"   ⏳ Ожидание ответа... ({int(time.time() - start_time)}с)")
                time.sleep(0.01)
            
            self.log.emit(f"⚠️ Таймаут запроса версии ({self.config.timeout_version}с)")
            return ""
            
        except Exception as e:
            self.log.emit(f"⚠️ Ошибка запроса версии: {e}")
            return ""
    
    def run(self):
        while self.running  and not self._stop_event.is_set():
            if self.current_command == 'capture':
                self._do_capture()
            elif self.current_command == 'download':
                self._do_download()
            elif self.current_command == 'properties':
                self._do_properties()
            elif self.current_command == 'get_version':
                self._do_get_version()
            time.sleep(0.01)
    
    def _do_get_version(self):
        self.is_busy = True
        try:
            version = self.get_version()
            if not version:
                self.version_received.emit("unknown")
        except Exception as e:
            self.log.emit(f"❌ Ошибка: {e}")
            self.version_received.emit("unknown")
        finally:
            self.is_busy = False
            self.current_command = None
            self.finished.emit()
    
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
            
            while (time.time() - start_time) < timeout and not self._stop_event.is_set():
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
                self.log.emit(f"✅ {props.get('width', 0)}x{props.get('height', 0)}, {props.get('chunks', 0)} чанков")
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
        """Загрузка изображения"""
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
            
            if 'v_start' in props:
                self._v_start = props['v_start']
            if 'h_start' in props:
                self._h_start = props['h_start']
            if 'exposure' in props:
                self._exposure = props['exposure']
            if width > 0:
                self._width = width
            if height > 0:
                self._height = height
            
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
            
            bytes_received = 0
            last_progress = -1
            last_log_time = time.time()
            
            for chunk_idx in range(total_chunks):
                if not self.running or self._stop_event.is_set():
                    break
                
                self.ser.reset_input_buffer()
                self._write_command(self.config.next_chunk)
                self.ser.flush()
                
                self.ser.read_until(preamble)
                
                read_total = 0
                start_time = time.time()
                timeout = self.config.timeout_chunk
                
                while read_total < chunk_total and (time.time() - start_time) < timeout and not self._stop_event.is_set():
                    if self.ser.in_waiting > 0:
                        available = self.ser.in_waiting
                        to_read = min(available, chunk_total - read_total)
                        chunk_buffer[read_total:read_total + to_read] = self.ser.read(to_read)
                        read_total += to_read
                    time.sleep(0.0005)
                
                if read_total < chunk_total:
                    self.log.emit(f"⚠️ Чанк {chunk_idx+1}: получено {read_total}/{chunk_total} байт")
                    continue
                
                try:
                    unpacked = chunk_struct.unpack_from(chunk_buffer)
                    chunk_id = unpacked[0]
                    payload_len = unpacked[1]
                    is_last = unpacked[2] if len(unpacked) > 2 else False
                    payload = chunk_buffer[5:5+payload_len]
                    image_data.extend(payload)
                    
                    bytes_received += payload_len
                    
                    if expected > 0:
                        progress = int(min(100, (bytes_received / expected) * 100))
                    else:
                        progress = int((chunk_idx + 1) / total_chunks * 100)
                    
                    if progress != last_progress:
                        self.progress.emit(progress)
                        last_progress = progress
                    
                    current_time = time.time()
                    if chunk_idx % 5 == 0 or is_last or progress >= 100 or (current_time - last_log_time) > 1.0:
                        self.partial_image.emit(bytes(image_data), width, height)
                        self.log.emit(f"📦 {chunk_idx+1}/{total_chunks} ({progress}%) | {bytes_received}/{expected} байт")
                        last_log_time = current_time
                    
                    if is_last:
                        break
                    
                except Exception as e:
                    self.log.emit(f"⚠️ Ошибка разбора чанка {chunk_idx+1}: {e}")
                    continue
                
                if len(image_data) >= expected:
                    break
            
            if len(image_data) < expected:
                self.log.emit(f"⚠️ Получено {len(image_data)} из {expected} байт, дополняем нулями")
                image_data.extend(b'\x00' * (expected - len(image_data)))
                self.progress.emit(100)
            
            self.log.emit(f"✅ Загрузка завершена ({len(image_data)} байт)")
            self.image_data.emit(bytes(image_data))
            
        except Exception as e:
            self.log.emit(f"❌ Ошибка загрузки: {e}")
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
    
    def start_get_version(self):
        if not self.is_busy:
            self.current_command = 'get_version'
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
            self._exposure = exp
            self.log.emit(f"🔆 {'Авто' if exp == 0 else exp}")
            time.sleep(0.05)
    
    def set_crop(self, v_start: int, h_start: int):
        if self.ser and self.ser.is_open:
            self._v_start = v_start
            self._h_start = h_start
            self.log.emit(f"✂️ vStart={v_start}, hStart={h_start}")
    
    def stop(self):
        self.running = False
        self._stop_event.set()
        self.current_command = None
        self.capture_in_progress = False