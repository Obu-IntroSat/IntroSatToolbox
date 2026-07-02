#!/usr/bin/env python3
"""Контроллер для выполнения тестов через UART."""

from __future__ import annotations

import serial
import time
from typing import Callable, Optional
from pathlib import Path

from . import generated_protocol as proto


class TestController:
    """Управляет подключением к стенду и выполнением команд."""

    def __init__(self, port: str = "COM15", baudrate: int = 9600):
        self.port = port
        self.baudrate = baudrate
        self.ser: Optional[serial.Serial] = None
        self.is_connected = False

    def connect(self) -> bool:
        """Подключение к стенду."""
        try:
            self.ser = serial.Serial(self.port, self.baudrate, timeout=1)
            self.is_connected = True
            return True
        except serial.SerialException as e:
            print(f"Ошибка подключения: {e}")
            return False

    def disconnect(self) -> None:
        """Отключение от стенда."""
        if self.ser and self.ser.is_open:
            self.ser.close()
        self.is_connected = False

    def send_packet(self, cmd_code: int, data_bytes: bytes) -> None:
        """Отправляет пакет с заголовком, длиной и CRC."""
        if not self.is_connected or not self.ser:
            raise RuntimeError("Не подключено к стенду")

        length = len(data_bytes)
        if length > 255:
            raise ValueError("Данные слишком длинные")

        crc = 0
        for b in bytes([cmd_code, length]) + data_bytes:
            crc ^= b

        packet = bytes([0xAA, cmd_code, length]) + data_bytes + bytes([crc])
        self.ser.write(packet)

    def read_packet(self, timeout: float = 2.0) -> tuple[int, bytes]:
        """Читает пакет, проверяет стартовый байт и CRC."""
        if not self.is_connected or not self.ser:
            raise RuntimeError("Не подключено к стенду")

        start = time.time()
        while time.time() - start < timeout:
            if self.ser.in_waiting >= 4:
                b = self.ser.read(1)
                if b == b'\xAA':
                    cmd_code = self.ser.read(1)[0]
                    length = self.ser.read(1)[0]
                    data = self.ser.read(length)
                    crc_byte = self.ser.read(1)[0]

                    # Проверка CRC
                    calc_crc = 0
                    for byte in bytes([cmd_code, length]) + data:
                        calc_crc ^= byte

                    if calc_crc == crc_byte:
                        return cmd_code, data
                    else:
                        print("CRC mismatch, ignoring packet")
            time.sleep(0.01)

        raise TimeoutError("Ответ не получен")

    def execute_command(self, cmd_name: str, params: dict, timeout: float = 2.0) -> dict:
        """
        Выполняет команду и возвращает результат.

        Args:
            cmd_name: Имя команды (совпадает с классом в generated_protocol)
            params: Параметры команды
            timeout: Таймаут ожидания ответа

        Returns:
            dict: {
                'success': bool,
                'response_code': int,
                'response_data': dict,  # распарсенный ответ
                'error': str или None
            }
        """
        if not self.is_connected:
            return {'success': False, 'error': 'Не подключено к стенду'}

        try:
            # Получаем класс команды
            cmd_class = getattr(proto, cmd_name, None)
            if cmd_class is None:
                return {'success': False, 'error': f'Неизвестная команда: {cmd_name}'}

            # Создаем объект команды
            cmd_obj = cmd_class(**params)
            data_bytes = cmd_obj.to_bytes()

            # Получаем код команды
            cmd_code = getattr(proto, f"{cmd_name.upper()}_CODE", None)
            if cmd_code is None:
                return {'success': False, 'error': f'Не найден код для {cmd_name}'}

            # Отправляем команду
            self.send_packet(cmd_code, data_bytes)

            # Читаем ответ
            resp_code, resp_data = self.read_packet(timeout)

            # Парсим ответ
            try:
                resp_obj = proto.parse_response(resp_code, resp_data)
                return {
                    'success': True,
                    'response_code': resp_code,
                    'response_data': vars(resp_obj)
                }
            except ValueError as e:
                return {
                    'success': False,
                    'error': f'Ошибка парсинга ответа: {e}',
                    'response_code': resp_code,
                    'raw_data': resp_data.hex()
                }

        except TimeoutError:
            return {'success': False, 'error': 'Таймаут: ответ не получен'}
        except Exception as e:
            return {'success': False, 'error': str(e)}


# === ФУНКЦИИ ДЛЯ ВЫЗОВА ИЗ WIDGET ===

def create_controller(port: str = "COM15", baudrate: int = 9600) -> TestController:
    """Создает контроллер с заданными параметрами."""
    return TestController(port, baudrate)


def format_test_result(result: dict, test_name: str) -> str:
    """Форматирует результат теста для вывода в QTextEdit."""
    lines = []
    lines.append(f"=== {test_name} ===")
    lines.append("")

    if result.get('success', False):
        lines.append("Тест пройден успешно!")
        lines.append("")
        lines.append("Ответ:")
        for key, value in result.get('response_data', {}).items():
            lines.append(f"  {key}: {value}")
    else:
        lines.append("Ошибка!")
        lines.append(f"  {result.get('error', 'Неизвестная ошибка')}")

    lines.append("")
    return "\n".join(lines)


def execute_connection_check(controller: TestController, target: str) -> str:
    """
    Проверка подключения к МК или оснастке.
    """
    lines = []
    lines.append(f"Проверка подключения: {target}")
    lines.append("")

    if not controller.connect():
        return "Ошибка: Не удалось подключиться к стенду"

    # Отправляем GetStatus для проверки связи
    result = controller.execute_command("GetStatus", {})

    if result['success']:
        powered = result['response_data'].get('powered', False)
        status_text = "Включено" if powered else "Выключено"
        lines.append(f"Связь установлена")
        lines.append(f"  Статус питания: {status_text}")
    else:
        lines.append(f"Ошибка: {result.get('error', 'Неизвестная ошибка')}")

    controller.disconnect()
    return "\n".join(lines)


def execute_firmware_version(controller: TestController) -> str:
    """Запрос версии прошивки."""
    lines = []
    lines.append("Запрос версии прошивки...")
    lines.append("")

    if not controller.connect():
        return "Ошибка: Не удалось подключиться к стенду"

    result = controller.execute_command("GetVersion", {})

    if result['success']:
        data = result['response_data']
        major = data.get('major', 0)
        minor = data.get('minor', 0)
        patch = data.get('patch', 0)
        lines.append(f"Версия прошивки: v{major}.{minor}.{patch}")
    else:
        lines.append(f"Ошибка: {result.get('error', 'Неизвестная ошибка')}")

    controller.disconnect()
    return "\n".join(lines)


def execute_stand_version(controller: TestController) -> str:
    """Запрос версии стенда."""
    lines = []
    lines.append("Запрос версии стенда...")
    lines.append("")

    if not controller.connect():
        return "Ошибка: Не удалось подключиться к стенду"

    # Используем GetVersion как версию стенда
    result = controller.execute_command("GetVersion", {})

    if result['success']:
        data = result['response_data']
        major = data.get('major', 0)
        minor = data.get('minor', 0)
        patch = data.get('patch', 0)
        lines.append(f"Версия стенда: v{major}.{minor}.{patch}")
    else:
        lines.append(f"Ошибка: {result.get('error', 'Неизвестная ошибка')}")

    controller.disconnect()
    return "\n".join(lines)


def execute_i2c_test(controller: TestController, device_name: str, i2c_address: int) -> str:
    """Выполняет I2C тест для устройства."""
    lines = []
    lines.append(f"Тест: {device_name}")
    lines.append("")

    if not controller.connect():
        return "Ошибка: Не удалось подключиться к стенду"

    # Шаг 1: Проверка наличия устройства
    lines.append("Шаг 1: Проверка наличия устройства на шине I2C")
    result = controller.execute_command("I2cProbe", {"address": i2c_address})

    if not result['success']:
        lines.append(f"Ошибка: {result.get('error', 'Неизвестная ошибка')}")
        controller.disconnect()
        return "\n".join(lines)

    present = result['response_data'].get('present', False)
    if not present:
        lines.append("Устройство не обнаружено!")
        controller.disconnect()
        return "\n".join(lines)

    lines.append("Устройство обнаружено")
    lines.append("")

    # Шаг 2: Чтение WHO_AM_I (для LIS2MDL регистр 0x4F)
    lines.append("Шаг 2: Чтение WHO_AM_I регистра")
    result = controller.execute_command("I2cReadRegister", {
        "address": i2c_address,
        "reg": 0x4F,
        "len": 1
    })

    if not result['success']:
        lines.append(f"Ошибка: {result.get('error', 'Неизвестная ошибка')}")
        controller.disconnect()
        return "\n".join(lines)

    data = result['response_data'].get('data', [])
    if data and len(data) > 0:
        who_am_i = data[0]
        if device_name == "LIS2MDL" and who_am_i == 0x40:
            lines.append(f"WHO_AM_I: 0x{who_am_i:02X} (верно)")
        elif device_name == "LSM6DS3" and who_am_i == 0x69:
            lines.append(f"WHO_AM_I: 0x{who_am_i:02X} (верно)")
        else:
            lines.append(f"WHO_AM_I: 0x{who_am_i:02X} (неизвестное устройство)")
    else:
        lines.append("Не удалось прочитать WHO_AM_I")
        controller.disconnect()
        return "\n".join(lines)

    # Шаг 3: Проверка данных датчика
    lines.append("")
    lines.append("Шаг 3: Чтение данных датчика")
    result = controller.execute_command("I2cRead", {
        "address": i2c_address,
        "len": 6
    })

    if not result['success']:
        lines.append(f"Ошибка: {result.get('error', 'Неизвестная ошибка')}")
        controller.disconnect()
        return "\n".join(lines)

    data = result['response_data'].get('data', [])
    if len(data) >= 6:
        values = [data[i] for i in range(6)]
        lines.append(f"Данные: {values}")
    else:
        lines.append("Данные получены, но недостаточной длины")
        controller.disconnect()
        return "\n".join(lines)

    lines.append("")
    lines.append("Тест пройден успешно!")

    controller.disconnect()
    return "\n".join(lines)


def execute_spi_test(controller: TestController) -> str:
    """Выполняет SPI тест для CC1101."""
    lines = []
    lines.append("Тест: CC1101 (SPI)")
    lines.append("")

    if not controller.connect():
        return "Ошибка: Не удалось подключиться к стенду"

    # Шаг 1: Инициализация SPI
    lines.append("Шаг 1: Инициализация SPI1")
    result = controller.execute_command("InitSpi", {
        "spi_num": 1,
        "speed": 1000000,
        "mode": 0,
        "bit_order": 0
    })

    if not result['success']:
        lines.append(f"Ошибка: {result.get('error', 'Неизвестная ошибка')}")
        controller.disconnect()
        return "\n".join(lines)
    lines.append("SPI инициализирован")
    lines.append("")

    # Шаг 2: Проверка версии чипа
    lines.append("Шаг 2: Проверка версии чипа")
    # Для CC1101: читаем регистр 0x0F (VERSION)
    # Формируем 64 байта для отправки: первый байт - команда чтения (0x0F), остальные - dummy (0x00)
    tx_data = [0x0F] + [0x00] * 63  # 64 байта

    result = controller.execute_command("SpiExchange", {
        "spi_num": 1,
        "tx_len": 64,  # Отправляем все 64 байта
        "tx_data": tx_data
    })

    if result['success']:
        rx_data = result['response_data'].get('rx_data', [])
        if len(rx_data) >= 2:
            version = rx_data[1]  # Второй байт - ответ
            lines.append(f"Версия чипа: 0x{version:02X}")
        else:
            lines.append("Данные получены, но недостаточной длины")
            controller.disconnect()
            return "\n".join(lines)
    else:
        lines.append(f"Ошибка: {result.get('error', 'Неизвестная ошибка')}")
        controller.disconnect()
        return "\n".join(lines)

    lines.append("")
    lines.append("Тест пройден успешно!")

    controller.disconnect()
    return "\n".join(lines)