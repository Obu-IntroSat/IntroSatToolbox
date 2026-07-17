#!/usr/bin/env python3
"""Контроллер для выполнения тестов через UART."""

from __future__ import annotations

import serial
import time
import yaml
from typing import Optional, List, Dict, Any
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

        # Сбрасываем входной буфер, чтобы удалить возможный мусор
        self.ser.reset_input_buffer()

        crc = 0
        for b in bytes([cmd_code, length]) + data_bytes:
            crc ^= b

        packet = bytes([0xAA, cmd_code, length]) + data_bytes + bytes([crc])
        self.ser.write(packet)

    def read_packet(self, timeout: float = 5.0) -> tuple[int, bytes]:
        """
        Читает пакет, проверяет стартовый байт и CRC.
        Таймаут увеличен до 3 секунд для надёжности.
        """
        if not self.is_connected or not self.ser:
            raise RuntimeError("Не подключено к стенду")

        start = time.time()
        response = b''
        while time.time() - start < timeout:
            if self.ser.in_waiting:
                byte = self.ser.read(1)
                if byte == b'\xAA':
                    # Начинаем сбор пакета
                    response = b'\xAA'
                    # Читаем код и длину (2 байта)
                    while len(response) < 4:
                        if self.ser.in_waiting:
                            response += self.ser.read(1)
                        else:
                            time.sleep(0.001)
                    # Длина данных
                    length = response[2]
                    total_len = 4 + length
                    # Читаем остальные байты
                    while len(response) < total_len:
                        if self.ser.in_waiting:
                            response += self.ser.read(1)
                        else:
                            time.sleep(0.001)
                    # Проверяем CRC
                    crc_calc = 0
                    for b in response[1:3] + response[3:-1]:  # без стартового и последнего CRC
                        crc_calc ^= b
                    if crc_calc == response[-1]:
                        cmd_code = response[1]
                        data = response[3:-1]
                        return cmd_code, data
                    else:
                        print(f"CRC mismatch: expected {crc_calc:02X}, got {response[-1]:02X}, ignoring packet")
                        response = b''
                        # Продолжаем поиск следующего стартового байта
                        continue
            else:
                time.sleep(0.01)

        raise TimeoutError("Ответ не получен")

    def execute_command(self, cmd_name: str, params: dict, timeout: float = 5.0) -> dict:
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
                'response_data': dict,
                'error': str или None
            }
        """
        if not self.is_connected:
            return {'success': False, 'error': 'Не подключено к стенду'}

        try:
            cmd_class = getattr(proto, cmd_name, None)
            if cmd_class is None:
                return {'success': False, 'error': f'Неизвестная команда: {cmd_name}'}

            cmd_obj = cmd_class(**params)
            data_bytes = cmd_obj.to_bytes()

            cmd_code = getattr(proto, f"{cmd_name.upper()}_CODE", None)
            if cmd_code is None:
                return {'success': False, 'error': f'Не найден код для {cmd_name}'}

            self.send_packet(cmd_code, data_bytes)
            resp_code, resp_data = self.read_packet(timeout)

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

    # --- Выполнение YAML-сценария ---
    def run_scenario(self, scenario_path: str, timeout: float = 3.0) -> List[Dict[str, Any]]:
        """Выполняет сценарий из YAML-файла."""
        with open(scenario_path, 'r', encoding='utf-8') as f:
            scenario = yaml.safe_load(f)

        results = []
        for idx, step in enumerate(scenario.get('steps', []), start=1):
            desc = step.get('description', f"Шаг {idx}")
            cmd_name = step['command']
            params = step.get('params', {})

            result = {
                'step_index': idx,
                'description': desc,
                'command': cmd_name,
                'params': params,
            }
            exec_result = self.execute_command(cmd_name, params, timeout)
            result.update(exec_result)
            results.append(result)
        return results


# === ФУНКЦИИ ДЛЯ ВЫЗОВА ИЗ WIDGET ===

def create_controller(port: str = "COM15", baudrate: int = 9600) -> TestController:
    return TestController(port, baudrate)


def format_test_result(result: dict, test_name: str) -> str:
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


def format_scenario_results(results: List[Dict[str, Any]]) -> str:
    lines = []
    for r in results:
        lines.append(f"[{r['step_index']}] {r['description']}")
        lines.append(f"   Команда: {r['command']}")
        if r['success']:
            lines.append("   Успешно")
            for key, value in r.get('response_data', {}).items():
                lines.append(f"      {key}: {value}")
        else:
            lines.append(f"   Ошибка: {r.get('error', 'Неизвестная ошибка')}")
        lines.append("")
    return "\n".join(lines)


# --- НОВЫЕ ТЕСТЫ ДЛЯ РЕАЛЬНОЙ ПЛАТЫ ---

def execute_system_test(controller: TestController) -> str:
    """
    Проверка системных команд: GetVersion и GetStatus.
    Используется как базовая проверка связи.
    """
    lines = []
    lines.append("=== Проверка системных команд ===")
    lines.append("")

    if not controller.connect():
        return "Ошибка: Не удалось подключиться к стенду"

    # GetVersion
    result = controller.execute_command("GetVersion", {})
    if result['success'] and result['response_code'] == 200:
        data = result['response_data']
        version = f"v{data.get('major', 0)}.{data.get('minor', 0)}.{data.get('patch', 0)}"
        lines.append(f"Версия прошивки: {version}")
    else:
        lines.append(f"Ошибка GetVersion: {result.get('error', 'Неизвестная ошибка')}")

    # GetStatus
    result = controller.execute_command("GetStatus", {})
    if result['success'] and result['response_code'] == 201:
        powered = result['response_data'].get('powered', False)
        lines.append(f"Статус питания: {'Включено' if powered else 'Выключено'}")
    else:
        lines.append(f"Ошибка GetStatus: {result.get('error', 'Неизвестная ошибка')}")

    controller.disconnect()
    return "\n".join(lines)


def execute_gpio_test(controller: TestController) -> str:
    """Тестирование GPIO: инициализация, установка, чтение, деинициализация."""
    lines = []
    lines.append("=== GPIO тест ===")
    lines.append("")

    if not controller.connect():
        return "Ошибка: Не удалось подключиться к стенду"

    # Шаг 1: Инициализация пина 13 как output push-pull с начальным состоянием 0
    lines.append("Шаг 1: Инициализация пина 13 как output (push-pull, initial=0)")
    result = controller.execute_command("GpioInitOutput", {"pin": 13, "initial_state": 0, "open_drain": 0})
    if not result['success']:
        lines.append(f"Ошибка: {result.get('error', 'Неизвестная ошибка')}")
        controller.disconnect()
        return "\n".join(lines)
    lines.append("Успешно")
    lines.append("")

    # Шаг 2: Установка пина в 1
    lines.append("Шаг 2: Установка пина 13 в 1")
    result = controller.execute_command("GpioSet", {"pin": 13, "value": 1})
    if not result['success']:
        lines.append(f"Ошибка: {result.get('error', 'Неизвестная ошибка')}")
        controller.disconnect()
        return "\n".join(lines)
    lines.append("Успешно")
    lines.append("")

    # Шаг 3: Чтение пина (должен быть 1)
    lines.append("Шаг 3: Чтение пина 13 (ожидается 1)")
    result = controller.execute_command("GpioRead", {"pin": 13})
    if result['success']:
        value = result['response_data'].get('value', 0)
        if value == 1:
            lines.append("Успешно: значение = 1")
        else:
            lines.append(f"Ошибка: значение = {value} (ожидалось 1)")
    else:
        lines.append(f"Ошибка: {result.get('error', 'Неизвестная ошибка')}")
    lines.append("")

    # Шаг 4: Установка пина в 0
    lines.append("Шаг 4: Установка пина 13 в 0")
    result = controller.execute_command("GpioSet", {"pin": 13, "value": 0})
    if not result['success']:
        lines.append(f"Ошибка: {result.get('error', 'Неизвестная ошибка')}")
        controller.disconnect()
        return "\n".join(lines)
    lines.append("Успешно")
    lines.append("")

    # Шаг 5: Чтение пина (должен быть 0)
    lines.append("Шаг 5: Чтение пина 13 (ожидается 0)")
    result = controller.execute_command("GpioRead", {"pin": 13})
    if result['success']:
        value = result['response_data'].get('value', 0)
        if value == 0:
            lines.append("Успешно: значение = 0")
        else:
            lines.append(f"Ошибка: значение = {value} (ожидалось 0)")
    else:
        lines.append(f"Ошибка: {result.get('error', 'Неизвестная ошибка')}")
    lines.append("")

    # Шаг 6: Деинициализация пина
    lines.append("Шаг 6: Деинициализация пина 13")
    result = controller.execute_command("GpioDeinit", {"pin": 13})
    if not result['success']:
        lines.append(f"Ошибка: {result.get('error', 'Неизвестная ошибка')}")
    else:
        lines.append("Успешно")

    controller.disconnect()
    return "\n".join(lines)


def execute_uart_test(controller: TestController) -> str:
    """Тестирование UART: инициализация, отправка, приём, деинициализация."""
    lines = []
    lines.append("=== UART тест ===")
    lines.append("")

    if not controller.connect():
        return "Ошибка: Не удалось подключиться к стенду"

    # Шаг 1: Инициализация UART1 (9600, 8N1)
    lines.append("Шаг 1: Инициализация UART1 (9600, 8 бит, 1 стоп, без чётности)")
    result = controller.execute_command("InitUart", {
        "uart_num": 1,
        "baudrate": 9600,
        "parity": 0,
        "stop_bits": 1,
        "data_bits": 8
    })
    if not result['success']:
        lines.append(f"Ошибка: {result.get('error', 'Неизвестная ошибка')}")
        controller.disconnect()
        return "\n".join(lines)
    lines.append("Успешно")
    lines.append("")

    # Шаг 2: Отправка данных "Hello" (5 байт)
    lines.append("Шаг 2: Отправка данных (Hello)")
    data_bytes = [0x48, 0x65, 0x6C, 0x6C, 0x6F]  # "Hello"
    # Дополняем массив до 64 байт нулями (требование протокола)
    data_64 = data_bytes + [0] * (64 - len(data_bytes))
    result = controller.execute_command("UartSend", {
        "uart_num": 1,
        "data_len": len(data_bytes),
        "data": data_64
    })
    if not result['success']:
        lines.append(f"Ошибка: {result.get('error', 'Неизвестная ошибка')}")
        controller.disconnect()
        return "\n".join(lines)
    lines.append("Успешно (отправлено 5 байт)")
    lines.append("")

    # Шаг 3: Приём данных (таймаут 500 мс, максимум 10 байт)
    lines.append("Шаг 3: Приём данных (таймаут 500 мс, максимум 10 байт)")
    result = controller.execute_command("UartReceive", {
        "uart_num": 1,
        "timeout_ms": 500,
        "max_len": 10
    })
    if result['success']:
        resp_data = result['response_data']
        data_len = resp_data.get('data_len', 0)
        if data_len > 0:
            received = resp_data.get('data', [])[:data_len]
            lines.append(f"Получено {data_len} байт: {received}")
        else:
            lines.append("Нет данных (таймаут или пустой буфер)")
    else:
        lines.append(f"Ошибка: {result.get('error', 'Неизвестная ошибка')}")
    lines.append("")

    # Шаг 4: Деинициализация UART1
    lines.append("Шаг 4: Деинициализация UART1")
    result = controller.execute_command("DeinitUart", {"uart_num": 1})
    if not result['success']:
        lines.append(f"Ошибка: {result.get('error', 'Неизвестная ошибка')}")
    else:
        lines.append("Успешно")

    controller.disconnect()
    return "\n".join(lines)


# --- СУЩЕСТВУЮЩИЕ ФУНКЦИИ (с изменениями) ---

def execute_connection_check(controller: TestController, target: str) -> str:
    """Проверка подключения к МК или оснастке с использованием системных команд."""
    # Используем execute_system_test вместо YAML-сценария
    return execute_system_test(controller)


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
    """Выполняет I2C тест для устройства, используя YAML-сценарий."""
    if device_name == "LIS2MDL":
        scenario_path = Path(__file__).parent / "../scenarios/test_lis2mdl.yaml"
    elif device_name == "LSM6DS3":
        scenario_path = Path(__file__).parent / "../scenarios/test_lsm6ds3.yaml"
    else:
        return f"Ошибка: Неизвестное устройство {device_name}"

    return execute_scenario(controller, str(scenario_path))


def execute_spi_test(controller: TestController) -> str:
    """Выполняет SPI тест для CC1101, используя YAML-сценарий."""
    scenario_path = Path(__file__).parent / "../scenarios/test_cc1101.yaml"
    return execute_scenario(controller, str(scenario_path))


def execute_scenario(controller: TestController, scenario_path: str) -> str:
    """
    Выполняет YAML-сценарий и возвращает форматированный вывод.
    Эта функция упрощает вызов из GUI: подключается, выполняет сценарий, отключается.
    """
    if not controller.connect():
        return "Ошибка: Не удалось подключиться к стенду"

    results = controller.run_scenario(scenario_path)
    controller.disconnect()

    return format_scenario_results(results)