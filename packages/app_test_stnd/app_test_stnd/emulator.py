#!/usr/bin/env python3
"""
Эмулятор микроконтроллера для тестирования протокола.
Имитирует работу стенда: принимает команды, отвечает на них.
"""
import serial
import time
import sys
from generated_protocol import (
    GETSTATUS_CODE,
    STATUSRESPONSE_CODE,
    GENERICRESPONSE_CODE,
)

# ===== НАСТРОЙКИ =====
PORT = 'COM16'          # Используйте второй порт из пары (например, COM6)
BAUDRATE = 9600
TIMEOUT = 0.1
# =====================


def calc_crc(data: bytes) -> int:
    """Вычисляет CRC (XOR) для данных."""
    crc = 0
    for b in data:
        crc ^= b
    return crc


def send_response(ser, cmd_code: int, resp_data: bytes):
    """Формирует и отправляет пакет ответа."""
    length = len(resp_data)
    if length > 255:
        raise ValueError("Ответ слишком длинный")
    # CRC вычисляется по полям: код команды, длина, данные
    crc = calc_crc(bytes([cmd_code, length]) + resp_data)
    packet = bytes([0xAA, cmd_code, length]) + resp_data + bytes([crc])
    ser.write(packet)
    print(f"   -> Отправлен ответ: код={cmd_code}, данные={resp_data.hex()}")


def handle_command(cmd_code: int, data: bytes) -> tuple:
    """
    Обрабатывает команду и возвращает (код_ответа, данные_ответа).
    Здесь вы можете добавить логику для других команд.
    """
    if cmd_code == GETSTATUS_CODE:
        # Имитируем, что устройство включено
        return STATUSRESPONSE_CODE, b'\x01'   # powered = True
    else:
        # Неизвестная команда – возвращаем ошибку
        print(f"   Неизвестная команда: {cmd_code}")
        return GENERICRESPONSE_CODE, b'\x01\x02'  # status=1, error_code=2


def main():
    try:
        ser = serial.Serial(PORT, BAUDRATE, timeout=TIMEOUT)
        print(f"Эмулятор запущен на порту {PORT} (скорость {BAUDRATE}). Ожидаем команды...")
    except serial.SerialException as e:
        print(f"Ошибка открытия порта {PORT}: {e}")
        sys.exit(1)

    while True:
        # Ищем стартовый байт
        if ser.in_waiting >= 4:
            b = ser.read(1)
            if b == b'\xAA':
                # Читаем заголовок
                cmd_code = ser.read(1)[0]
                length = ser.read(1)[0]
                # Проверяем, что длина не превышает буфер (можно увеличить)
                if length > 255:
                    print("Некорректная длина, игнорируем")
                    continue
                # Читаем данные и CRC
                data = ser.read(length)
                if len(data) != length:
                    print("Недостаточно данных, игнорируем")
                    continue
                crc_received = ser.read(1)
                if not crc_received:
                    continue
                crc_received = crc_received[0]

                # Проверяем CRC
                expected_crc = calc_crc(bytes([cmd_code, length]) + data)
                if crc_received != expected_crc:
                    print(f"CRC mismatch: ожидалось {expected_crc:02x}, получено {crc_received:02x}")
                    continue

                print(f"Получена команда: код={cmd_code}, данные={data.hex()}")

                # Обрабатываем команду
                resp_code, resp_data = handle_command(cmd_code, data)
                send_response(ser, resp_code, resp_data)
        # Небольшая задержка, чтобы не грузить процессор
        time.sleep(0.01)


if __name__ == '__main__':
    main()
