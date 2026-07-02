#!/usr/bin/env python3
import serial
import yaml
import time
import argparse
import generated_protocol as proto   # импортируем модуль целиком

def send_packet(ser, cmd_code, data_bytes):
    """Отправляет пакет с заголовком, длиной и CRC (CRC XOR)."""
    length = len(data_bytes)
    if length > 255:
        raise ValueError("Данные слишком длинные")
    crc = 0
    for b in bytes([cmd_code, length]) + data_bytes:
        crc ^= b
    packet = bytes([0xAA, cmd_code, length]) + data_bytes + bytes([crc])
    ser.write(packet)

def read_packet(ser, timeout=2):
    """Читает пакет, проверяет стартовый байт и CRC."""
    start = time.time()
    while time.time() - start < timeout:
        if ser.in_waiting >= 4:
            b = ser.read(1)
            if b == b'\xAA':
                cmd_code = ser.read(1)[0]
                length = ser.read(1)[0]
                data = ser.read(length)
                crc = ser.read(1)[0]
                # Проверка CRC
                calc_crc = 0
                for byte in bytes([cmd_code, length]) + data:
                    calc_crc ^= byte
                if calc_crc == crc:
                    return cmd_code, data
                else:
                    print("CRC mismatch, ignoring packet")
        time.sleep(0.01)
    raise TimeoutError("Ответ не получен")

def execute_scenario(scenario_path, port='COM5', baudrate=9600):
    with open(scenario_path, 'r', encoding='utf-8') as f:
        scenario = yaml.safe_load(f)

    print(f"=== Запуск сценария: {scenario.get('name', 'Без имени')} ===")
    print(scenario.get('description', ''))

    ser = serial.Serial(port, baudrate, timeout=1)
    try:
        for step_idx, step in enumerate(scenario['steps']):
            desc = step.get('description', f"Шаг {step_idx+1}")
            cmd_name = step['command']
            params = step.get('params', {})

            print(f"\n[{step_idx+1}] {desc}")
            print(f"   Команда: {cmd_name}")
            print(f"   Параметры: {params}")

            # Получаем класс команды из модуля proto
            cmd_class = getattr(proto, cmd_name, None)
            if cmd_class is None:
                raise ValueError(f"Неизвестная команда: {cmd_name}")

            try:
                cmd_obj = cmd_class(**params)
            except TypeError as e:
                print(f"   Ошибка в параметрах: {e}")
                continue

            data_bytes = cmd_obj.to_bytes()
            cmd_code = getattr(proto, f"{cmd_name.upper()}_CODE", None)
            if cmd_code is None:
                raise ValueError(f"Не найден код для {cmd_name}")

            send_packet(ser, cmd_code, data_bytes)
            print(f"   Отправлено {len(data_bytes)+4} байт")

            try:
                resp_code, resp_data = read_packet(ser)
                print(f"   Получен ответ, код={resp_code}, длина={len(resp_data)}")
                # Парсим ответ через фабрику из модуля proto
                try:
                    resp_obj = proto.parse_response(resp_code, resp_data)
                    print("   Ответ:")
                    for attr, value in vars(resp_obj).items():
                        print(f"      {attr}: {value}")
                except ValueError as e:
                    print(f"   Ошибка парсинга ответа: {e}")
            except TimeoutError:
                print("   [Таймаут] Ответ не получен")
    finally:
        ser.close()
    print("\n=== Сценарий завершён ===")


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('scenario', help='Путь к YAML-файлу сценария')
    parser.add_argument('--port', default='COM15', help='UART порт')
    parser.add_argument('--baud', type=int, default=9600, help='Скорость')
    args = parser.parse_args()
    execute_scenario(args.scenario, args.port, args.baud)
