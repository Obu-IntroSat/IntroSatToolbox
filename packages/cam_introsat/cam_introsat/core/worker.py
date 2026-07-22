# -*- coding: utf-8 -*-
"""
Поток для выполнения операций с камерой (захват, загрузка, свойства, версия).
Весь обмен с камерой происходит в фоновом потоке, чтобы не блокировать GUI.
"""

from __future__ import annotations
import struct
import time
from threading import Event, Lock
from typing import Optional
import serial

from PySide6.QtCore import QThread, Signal

from .config import CameraCommandConfig


class CameraWorker(QThread):
    """
    Рабочий поток, выполняющий команды в фоне.
    Сигналы используются для обновления GUI.
    """
    # Сигналы для связи с главным окном
    progress = Signal(int)                         # Прогресс загрузки (0-100)
    partial_image = Signal(bytes, int, int)        # Обрезанное изображение (данные, ширина, высота)
    log = Signal(str)                              # Сообщение в лог
    finished = Signal()                            # Команда завершена
    error = Signal(str)                            # Ошибка
    properties_received = Signal(dict)             # Получены свойства снимка
    capture_complete = Signal()                    # Захват завершён
    version_received = Signal(str)                 # Получена версия прошивки

    def __init__(self, config: CameraCommandConfig):
        super().__init__()
        self.config = config
        self.ser = None                # Последовательный порт
        self.running = True
        self._stop_event = Event()     # Событие для остановки потока
        self.is_busy = False
        self.current_command = None    # Текущая выполняемая команда ('capture', 'download', ...)
        self.capture_in_progress = False
        self._lock = Lock()            # Для синхронизации доступа к порту

        # Буферы и структуры для распаковки
        self._chunk_buffer = bytearray(config.chunk_packet_size)
        self._chunk_struct = struct.Struct(config.chunk_format)
        self._prop_struct = struct.Struct(config.property_format)

        # Параметры обрезки на ПК (не отправляются на камеру)
        self._crop_v_start = 0
        self._crop_h_start = 0
        self._crop_width = 640
        self._crop_height = 480
        self._exposure = 0
        self._firmware_version = ""

    # ------ Настройка конфигурации и параметров ------

    def set_config(self, config: CameraCommandConfig):
        """Обновляет конфигурацию (при смене профиля)."""
        self.config = config
        self._chunk_buffer = bytearray(config.chunk_packet_size)
        self._chunk_struct = struct.Struct(config.chunk_format)
        self._prop_struct = struct.Struct(config.property_format)

    def set_crop_params(self, v_start: int, h_start: int, width: int, height: int):
        """
        Устанавливает параметры обрезки, которая будет применяться **на ПК**
        после загрузки полного кадра.
        Эти значения не отправляются на камеру, т.к. протокол CM 2.0 их не поддерживает.
        """
        self._crop_v_start = v_start
        self._crop_h_start = h_start
        self._crop_width = width
        self._crop_height = height
        self.log.emit(f"✂️ Параметры обрезки (ПК): vStart={v_start}, hStart={h_start}, {width}×{height}")

    def set_resolution(self, width: int, height: int):
        """
        Отправляет команду set_size (0x73) с шириной и высотой.
        Важно: vStart/hStart не передаются, так как протокол CM 2.0 их не поддерживает.
        """
        if not self.ser or not self.ser.is_open:
            self.log.emit("⚠️ Порт не открыт")
            return
        cmd = self.config.get_command_bytes(self.config.set_size)
        cmd += struct.pack('<HH', width, height)
        self._write(cmd)
        time.sleep(0.05)
        self.log.emit(f"📐 Отправлен размер: {width}×{height}")

    def set_exposure(self, exp: int):
        """Устанавливает экспозицию (0 = автоэкспозиция)."""
        self._exposure = exp
        self.log.emit(f"🔆 Экспозиция: {'Авто' if exp == 0 else exp}")
        if self.ser and self.ser.is_open:
            cmd = self.config.get_command_bytes(self.config.set_exposure)
            cmd += struct.pack('<H', exp)
            self._write(cmd)
            time.sleep(0.05)

    # ------ Работа с портом ------

    def connect(self, port: str) -> bool:
        """Открывает последовательный порт с параметрами из конфига."""
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
        """Закрывает порт."""
        with self._lock:
            if self.ser and self.ser.is_open:
                try:
                    self.ser.close()
                except:
                    pass
            self.ser = None
        self.log.emit("⏹ Отключено")

    def _write(self, data: bytes):
        """Блокирующая запись в порт."""
        with self._lock:
            if self.ser and self.ser.is_open:
                self.ser.write(data)
                self.ser.flush()

    def _write_command(self, cmd: str, extra: bytes = b''):
        """Отправляет команду с возможным доп. аргументом, логирует."""
        cmd_bytes = self.config.get_command_bytes(cmd)
        full = cmd_bytes + extra
        self.log.emit(f"   Отправка команды: {cmd} -> {full.hex()}")
        self._write(full)
        return full

    def _read_with_timeout(self, size: int, timeout: float = 3.0) -> bytes:
        """Читает ровно size байт с таймаутом."""
        if not self.ser or not self.ser.is_open:
            return b''
        data = b''
        start = time.time()
        while len(data) < size and (time.time() - start) < timeout and not self._stop_event.is_set():
            if self.ser.in_waiting > 0:
                available = self.ser.in_waiting
                to_read = min(available, size - len(data))
                chunk = self.ser.read(to_read)
                data += chunk
                self.log.emit(f"   Прочитано {len(chunk)} байт (всего {len(data)}/{size})")
            time.sleep(0.01)
        return data

    # ------ Парсинг свойств и обрезка ------

    def _parse_properties(self, data: bytes) -> dict:
        """
        Распаковывает 18 байт свойств согласно формату из конфига.
        Возвращает словарь с ключами: height, width, v_start, h_start, ...
        """
        try:
            self.log.emit(f"   Парсинг свойств ({len(data)} байт): {data.hex()[:50]}...")
            fmt = self.config.property_format
            size = struct.calcsize(fmt)
            if len(data) < size:
                self.log.emit(f"⚠️ Недостаточно данных: {len(data)} < {size}")
                return {}
            unpacked = struct.unpack(fmt, data[:size])
            names = ['height', 'width', 'v_start', 'h_start', 'colorspace', 'exposure', 'length', 'chunks']
            result = {}
            for i, name in enumerate(names):
                if i < len(unpacked):
                    result[name] = unpacked[i]
            result['has_image'] = result.get('chunks', 0) > 0
            self.log.emit(f"   Распарсено: {result}")
            return result
        except Exception as e:
            self.log.emit(f"⚠️ Ошибка парсинга свойств: {e}")
            return {}

    def _apply_crop(self, data: bytes, width: int, height: int,
                    crop_x: int, crop_y: int, crop_w: int, crop_h: int) -> bytes:
        """
        Вырезает прямоугольную область из полного изображения (crop_x = hStart, crop_y = vStart).
        Возвращает обрезанные данные.
        """
        if crop_x == 0 and crop_y == 0 and crop_w == width and crop_h == height:
            return data
        result = bytearray()
        row_bytes = width
        for y in range(crop_y, min(crop_y + crop_h, height)):
            start = y * row_bytes + crop_x
            end = min(start + crop_w, len(data))
            if start < len(data):
                result.extend(data[start:end])
        return bytes(result)

    # ------ Получение версии ------

    def get_version(self) -> str:
        """Запрашивает версию прошивки и парсит ответ."""
        if not self.ser or not self.ser.is_open:
            self.log.emit("⚠️ Порт не открыт")
            return ""
        try:
            self.log.emit(f"📡 Запрос версии...")
            self.ser.reset_input_buffer()
            self.ser.reset_output_buffer()
            cmd_bytes = self.config.get_command_bytes(self.config.get_version)
            self._write(cmd_bytes)
            self.ser.flush()
            preamble = bytes.fromhex(self.config.preamble)
            start_time = time.time()
            response = b""
            while (time.time() - start_time) < self.config.timeout_version and not self._stop_event.is_set():
                if self.ser.in_waiting > 0:
                    data = self.ser.read(self.ser.in_waiting)
                    response += data
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
                time.sleep(0.01)
            self.log.emit(f"⚠️ Таймаут запроса версии")
            return ""
        except Exception as e:
            self.log.emit(f"⚠️ Ошибка запроса версии: {e}")
            return ""

    # ------ Основной цикл потока ------

    def run(self):
        """Цикл обработки команд (выполняется в отдельном потоке)."""
        while self.running and not self._stop_event.is_set():
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
        """
        Отправка команды захвата (t) и ожидание преамбулы.
        После успешного захвата камера сохраняет снимок в памяти.
        """
        self.is_busy = True
        self.capture_in_progress = True
        try:
            self.log.emit(f"📸 Захват... (экспозиция={self._exposure})")
            # Если экспозиция не 0, предварительно устанавливаем её
            if self._exposure > 0:
                cmd = self.config.get_command_bytes(self.config.set_exposure)
                cmd += struct.pack('<H', self._exposure)
                self._write(cmd)
                time.sleep(0.05)

            # Очищаем буферы и отправляем capture
            self.ser.reset_input_buffer()
            self.ser.reset_output_buffer()
            self._write_command(self.config.capture)

            # Ждём преамбулу (подтверждение, что снимок сделан)
            start_time = time.time()
            response_found = False
            timeout = self.config.timeout_capture
            preamble = bytes.fromhex(self.config.preamble)
            while (time.time() - start_time) < timeout and not self._stop_event.is_set():
                if self.ser.in_waiting > 0:
                    data = self.ser.read(self.ser.in_waiting)
                    self.log.emit(f"   Получено {len(data)} байт")
                    if preamble in data:
                        self.log.emit(f"   Найдена преамбула!")
                        response_found = True
                        break
                time.sleep(0.1)
                elapsed = int(time.time() - start_time)
                if elapsed % 2 == 0 and elapsed > 0:
                    self.log.emit(f"⏳ {elapsed}/{int(timeout)} сек")

            if response_found:
                self.log.emit("✅ Снимок создан!")
            else:
                self.log.emit("⚠️ Таймаут захвата")

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
        """Запрос свойств снимка (p)."""
        self.is_busy = True
        try:
            self.log.emit("📊 Запрос свойств...")
            self.ser.reset_input_buffer()
            self.ser.reset_output_buffer()
            self._write_command(self.config.properties)
            preamble = bytes.fromhex(self.config.preamble)
            response = b''
            start_time = time.time()
            while (time.time() - start_time) < 3.0 and not self._stop_event.is_set():
                if self.ser.in_waiting > 0:
                    data = self.ser.read(self.ser.in_waiting)
                    response += data
                    self.log.emit(f"   Получено {len(data)} байт (всего {len(response)})")
                    if len(response) >= self.config.property_size + 3:
                        break
                time.sleep(0.01)
            if not response:
                self.log.emit("⚠️ Нет ответа")
                self.error.emit("Нет ответа от камеры")
                return
            preamble_idx = response.find(preamble)
            if preamble_idx == -1:
                self.log.emit("⚠️ Преамбула не найдена")
                self.error.emit("Преамбула не найдена")
                return
            prop_data = response[preamble_idx + len(preamble):]
            if len(prop_data) < self.config.property_size:
                self.log.emit(f"⚠️ Получено {len(prop_data)} байт свойств, ожидается {self.config.property_size}")
                extra = self._read_with_timeout(self.config.property_size - len(prop_data), timeout=1.0)
                prop_data += extra
            if len(prop_data) < self.config.property_size:
                self.error.emit(f"Неполные данные свойств: {len(prop_data)}/{self.config.property_size}")
                return
            props = self._parse_properties(prop_data[:self.config.property_size])
            self.properties_received.emit(props)
            if props.get('chunks', 0) > 0:
                self.log.emit(f"✅ Размер: {props.get('width', 0)}x{props.get('height', 0)}, чанков: {props.get('chunks', 0)}")
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
        """
        Полная загрузка снимка:
        1. Запрос свойств → получаем размер и количество чанков.
        2. Последовательный запрос чанков (n), сборка полного изображения.
        3. Обрезка на ПК (согласно _crop_* параметрам) и отправка в GUI через partial_image.
        """
        self.is_busy = True
        try:
            self.log.emit("📥 Начинаем загрузку...")

            # ---- Шаг 1: свойства ----
            self.log.emit("📊 Шаг 1: Получение свойств...")
            self.ser.reset_input_buffer()
            self.ser.reset_output_buffer()
            self._write_command(self.config.properties)
            preamble = bytes.fromhex(self.config.preamble)
            response = b''
            start_time = time.time()
            while (time.time() - start_time) < 3.0 and not self._stop_event.is_set():
                if self.ser.in_waiting > 0:
                    data = self.ser.read(self.ser.in_waiting)
                    response += data
                    if len(response) >= self.config.property_size + 3:
                        break
                time.sleep(0.01)
            if not response:
                self.log.emit("⚠️ Нет ответа от камеры")
                self.error.emit("Нет ответа от камеры")
                return
            preamble_idx = response.find(preamble)
            if preamble_idx == -1:
                self.log.emit("⚠️ Преамбула не найдена")
                self.error.emit("Преамбула не найдена")
                return
            prop_data = response[preamble_idx + len(preamble):]
            if len(prop_data) < self.config.property_size:
                extra = self._read_with_timeout(self.config.property_size - len(prop_data), timeout=1.0)
                prop_data += extra
            if len(prop_data) < self.config.property_size:
                self.error.emit(f"Неполные данные свойств: {len(prop_data)}/{self.config.property_size}")
                return
            props = self._parse_properties(prop_data[:self.config.property_size])
            width = props.get('width', 0)
            height = props.get('height', 0)
            total_chunks = props.get('chunks', 0)
            if width == 0 or height == 0:
                self.log.emit("⚠️ Камера вернула нулевые размеры, используем 640x480")
                width = 640
                height = 480
            self.log.emit(f"📊 Свойства: ширина={width}, высота={height}, чанков={total_chunks}")
            if total_chunks == 0:
                self.log.emit("ℹ️ Нет снимка в памяти")
                self.error.emit("Нет снимка в памяти")
                return

            # ---- Определяем параметры обрезки на ПК ----
            crop_x = self._crop_h_start
            crop_y = self._crop_v_start
            crop_w = self._crop_width
            crop_h = self._crop_height
            # Корректируем, чтобы не выходить за границы
            if crop_x + crop_w > width:
                crop_w = width - crop_x
            if crop_y + crop_h > height:
                crop_h = height - crop_y
            if crop_w <= 0 or crop_h <= 0:
                crop_w = width
                crop_h = height
                crop_x = 0
                crop_y = 0
            self.log.emit(f"📦 Исходный размер: {width}×{height}, обрезка на ПК: ({crop_x},{crop_y}) {crop_w}×{crop_h}")

            # ---- (опционально) команда начала передачи ----
            start_cmd = self.config.start_transfer.strip()
            if start_cmd:
                self.log.emit(f"▶️ Отправка команды начала передачи: {start_cmd}")
                self._write_command(start_cmd)
                time.sleep(0.1)
                self.ser.reset_input_buffer()

            # ---- Шаг 2: загрузка чанков ----
            self.log.emit("📥 Шаг 2: Загрузка чанков...")
            full_image = bytearray()
            expected = width * height
            chunk_struct = self._chunk_struct
            chunk_buffer = self._chunk_buffer
            packet_size = self.config.chunk_packet_size
            bytes_received = 0
            last_progress = -1

            for chunk_idx in range(total_chunks):
                if not self.running or self._stop_event.is_set():
                    self.log.emit("⏹ Загрузка прервана")
                    break

                # Отправляем запрос следующего чанка (с возможным индексом, если включено)
                extra = b''
                if self.config.send_chunk_index:
                    extra = struct.pack('<H', chunk_idx)
                self._write_command(self.config.next_chunk, extra)
                self.ser.flush()

                # Ждём преамбулу и данные чанка
                response = b''
                start_time = time.time()
                while (time.time() - start_time) < self.config.timeout_chunk and not self._stop_event.is_set():
                    if self.ser.in_waiting > 0:
                        data = self.ser.read(self.ser.in_waiting)
                        response += data
                        if preamble in response:
                            break
                    time.sleep(0.001)

                if preamble not in response:
                    self.log.emit(f"⚠️ Преамбула не найдена для чанка {chunk_idx+1}")
                    continue

                preamble_idx = response.find(preamble)
                chunk_data = response[preamble_idx + len(preamble):]

                # Добираем оставшиеся байты до полного пакета
                while len(chunk_data) < packet_size and (time.time() - start_time) < self.config.timeout_chunk:
                    if self.ser.in_waiting > 0:
                        available = self.ser.in_waiting
                        to_read = min(available, packet_size - len(chunk_data))
                        chunk_data += self.ser.read(to_read)
                    time.sleep(0.0005)

                if len(chunk_data) < packet_size:
                    self.log.emit(f"⚠️ Чанк {chunk_idx+1}: получено {len(chunk_data)}/{packet_size} байт")
                    continue

                # Распаковываем чанк
                try:
                    chunk_buffer[:packet_size] = chunk_data
                    unpacked = chunk_struct.unpack_from(chunk_buffer)
                    chunk_id = unpacked[0]
                    payload_len = unpacked[1]
                    is_last = unpacked[2]
                    payload = chunk_buffer[5:5+payload_len]

                    # Проверка контрольной суммы (если она не нулевая)
                    if len(unpacked) > 6:
                        checksum_received = unpacked[6]
                        calc_checksum = sum(payload) & 0xFFFF
                        if checksum_received != 0 and calc_checksum != checksum_received:
                            self.log.emit(f"⚠️ Чанк {chunk_idx+1}: несовпадение контрольной суммы (получено {checksum_received}, вычислено {calc_checksum})")

                    full_image.extend(payload)
                    bytes_received += payload_len

                    # Вычисляем прогресс
                    if expected > 0:
                        progress = int(min(100, (bytes_received / expected) * 100))
                    else:
                        progress = int((chunk_idx + 1) / total_chunks * 100)
                    if progress != last_progress:
                        self.progress.emit(progress)
                        last_progress = progress

                    self.log.emit(f"   Чанк {chunk_idx+1}: id={chunk_id}, payload={payload_len}, last={is_last}, прогресс={progress}%")

                    # Отправляем промежуточное обрезанное изображение (для отображения в процессе загрузки)
                    if not is_last and progress < 100 and (chunk_idx % 5 == 0):
                        if len(full_image) < expected:
                            padded = full_image + b'\x00' * (expected - len(full_image))
                        else:
                            padded = full_image[:expected]
                        cropped_partial = self._apply_crop(bytes(padded), width, height, crop_x, crop_y, crop_w, crop_h)
                        if len(cropped_partial) < crop_w * crop_h:
                            cropped_partial += b'\x00' * (crop_w * crop_h - len(cropped_partial))
                        self.partial_image.emit(cropped_partial, crop_w, crop_h)

                    if is_last:
                        self.log.emit(f"   Получен последний чанк")
                        break

                except Exception as e:
                    self.log.emit(f"⚠️ Ошибка разбора чанка {chunk_idx+1}: {e}")
                    continue

                if len(full_image) >= expected:
                    self.log.emit(f"   Достигнут ожидаемый размер")
                    break

            # ---- Шаг 3: проверка и дополнение нулями ----
            self.log.emit(f"📊 Получено {len(full_image)} байт из {expected} ожидаемых")
            if len(full_image) < expected:
                self.log.emit(f"⚠️ Недостаточно данных: {len(full_image)}/{expected}, дополняем нулями")
                full_image.extend(b'\x00' * (expected - len(full_image)))

            # ---- Шаг 4: финальная обрезка на ПК и отправка в GUI ----
            cropped_data = self._apply_crop(bytes(full_image), width, height, crop_x, crop_y, crop_w, crop_h)
            if len(cropped_data) < crop_w * crop_h:
                cropped_data += b'\x00' * (crop_w * crop_h - len(cropped_data))
            self.log.emit(f"✅ Загрузка завершена: {len(cropped_data)} байт (обрезка на ПК {crop_w}×{crop_h})")
            self.partial_image.emit(cropped_data, crop_w, crop_h)
            self.progress.emit(100)

        except Exception as e:
            self.log.emit(f"❌ Ошибка загрузки: {e}")
            self.error.emit(str(e))
        finally:
            self.is_busy = False
            self.current_command = None
            self.finished.emit()

    # ------ Публичные методы запуска команд ------
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

    def stop(self):
        """Останавливает поток и прерывает текущую операцию."""
        self.running = False
        self._stop_event.set()
        self.current_command = None
        self.capture_in_progress = False