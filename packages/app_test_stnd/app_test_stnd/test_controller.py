#!/usr/bin/env python3
"""Контроллер для выполнения тестов через UART."""

from __future__ import annotations

import serial
import time
import yaml
from typing import Callable, Optional, List, Dict, Any
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

    # --- НОВЫЙ МЕТОД: выполнение YAML-сценария ---
    def run_scenario(self, scenario_path: str, timeout: float = 2.0) -> List[Dict[str, Any]]:
        """
        Выполняет сценарий из YAML-файла.

        Args:
            scenario_path: Путь к YAML-файлу сценария
            timeout: Таймаут для каждой команды

        Returns:
            Список результатов каждого шага. Каждый результат содержит:
                - step_index (int)
                - description (str)
                - command (str)
                - params (dict)
                - success (bool)
                - response_code (int, если успешно)
                - response_data (dict, если успешно)
                - error (str, если ошибка)
        """
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

            # Выполняем команду
            exec_result = self.execute_command(cmd_name, params, timeout)
            result.update(exec_result)

            results.append(result)

            # Если шаг завершился ошибкой, можно остановить выполнение (по желанию)
            # Здесь мы не останавливаем, чтобы выполнить все шаги.
            # Чтобы остановить, раскомментируйте следующую строку:
            # if not exec_result['success']:
            #     break

        return results


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


def format_scenario_results(results: List[Dict[str, Any]]) -> str:
    """Форматирует результаты выполнения сценария для вывода."""
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


# --- Существующие функции для готовых тестов (без изменений) ---

def execute_connection_check(controller: TestController, target: str) -> str:
    """Проверка подключения к МК или оснастке с использованием YAML-сценария."""
    # Игнорируем target, так как сценарий check_power.yaml уже содержит описание
    scenario_path = Path(__file__).parent / "../scenarios/check_power.yaml"
    return execute_scenario(controller, str(scenario_path))


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
    """Выполняет I2C тест для устройства, используя YAML-сценарий."""
    # Выбираем сценарий в зависимости от device_name
    if device_name == "LIS2MDL":
        scenario_path = Path(__file__).parent / "../scenarios/test_lis2mdl.yaml"
    elif device_name == "LSM6DS3":
        scenario_path = Path(__file__).parent / "../scenarios/test_lsm6ds3.yaml"
    else:
        return f"Ошибка: Неизвестное устройство {device_name}"

    # Вызываем универсальную функцию выполнения сценария
    return execute_scenario(controller, str(scenario_path))


def execute_spi_test(controller: TestController) -> str:
    """Выполняет SPI тест для CC1101, используя YAML-сценарий."""
    # Определяем путь к сценарию относительно текущего файла
    scenario_path = Path(__file__).parent / "../scenarios/test_cc1101.yaml"
    # Вызываем универсальную функцию выполнения сценария
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
