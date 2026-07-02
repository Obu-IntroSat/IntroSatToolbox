#!/usr/bin/env python3
"""
Эмулятор микроконтроллера для тестирования протокола.
Имитирует работу стенда: принимает команды, отвечает на них.
Поддерживает команды для LIS2MDL (I2C).
"""
import serial
import time
import sys
from generated_protocol import (
    GETSTATUS_CODE,
    STATUSRESPONSE_CODE,
    GENERICRESPONSE_CODE,

    INITI2C_CODE,
    DEINITI2C_CODE,
    I2CPROBE_CODE,
    I2CREADREGISTER_CODE,
    I2CREAD_CODE,
    I2CWRITEREGISTER_CODE,
    I2CWRITE_CODE,

    I2CPROBERESPONSE_CODE,
    I2CREADREGISTERRESPONSE_CODE,
    I2CREADRESPONSE_CODE,

    SPISEND_CODE,
    SPIRECEIVE_CODE,
    SPIEXCHANGE_CODE,
    UARTSEND_CODE,
    UARTRECEIVE_CODE,
    GPIOINITOUTPUT_CODE,
    GPIOINITINPUT_CODE,
    GPIOSET_CODE,
    GPIOREAD_CODE,
    GPIODEINIT_CODE,
    ADCREAD_CODE,
    EEPROMREAD_CODE,
)

# ===== НАСТРОЙКИ =====
PORT = 'COM16'          # Второй порт из пары
BAUDRATE = 9600
TIMEOUT = 0.1
# =====================

def calc_crc(data: bytes) -> int:
    crc = 0
    for b in data:
        crc ^= b
    return crc

def send_response(ser, cmd_code: int, resp_data: bytes):
    length = len(resp_data)
    if length > 255:
        raise ValueError("Ответ слишком длинный")
    crc = calc_crc(bytes([cmd_code, length]) + resp_data)
    packet = bytes([0xAA, cmd_code, length]) + resp_data + bytes([crc])
    ser.write(packet)
    print(f"   -> Отправлен ответ: код={cmd_code}, длина={length}, данные={resp_data.hex()}")

def handle_command(cmd_code: int, data: bytes) -> tuple:
    # ---- Системные команды ----
    if cmd_code == GETSTATUS_CODE:
        return STATUSRESPONSE_CODE, b'\x01'

    # ---- I2C команды ----
    if cmd_code == INITI2C_CODE or cmd_code == DEINITI2C_CODE:
        return GENERICRESPONSE_CODE, b'\x00\x00'

    if cmd_code == I2CPROBE_CODE:
        return I2CPROBERESPONSE_CODE, b'\x00\x00\x01'

    if cmd_code == I2CREADREGISTER_CODE:
        # Ответ: status=0, error=0, data_len=1, data = 8 байт: 0x40 + 7 нулей
        return I2CREADREGISTERRESPONSE_CODE, b'\x00\x00\x01' + b'\x40' + b'\x00' * 7

    if cmd_code == I2CREAD_CODE:
        # Ответ: status=0, error=0, data_len=6, data = 64 байта: 6 байт значений + 58 нулей
        sample_data = bytes([0x01, 0x02, 0x03, 0x04, 0x05, 0x06])
        return I2CREADRESPONSE_CODE, b'\x00\x00\x06' + sample_data + b'\x00' * 58

    if cmd_code in (I2CWRITEREGISTER_CODE, I2CWRITE_CODE):
        return GENERICRESPONSE_CODE, b'\x00\x00'

    # ---- Заглушки для других команд ----
    if cmd_code in (SPISEND_CODE, SPIRECEIVE_CODE, SPIEXCHANGE_CODE,
                    UARTSEND_CODE, UARTRECEIVE_CODE,
                    GPIOINITOUTPUT_CODE, GPIOINITINPUT_CODE,
                    GPIOSET_CODE, GPIOREAD_CODE, GPIODEINIT_CODE,
                    ADCREAD_CODE, EEPROMREAD_CODE):
        return GENERICRESPONSE_CODE, b'\x00\x00'

    # ---- Неизвестная команда ----
    print(f"   Неизвестная команда: {cmd_code}")
    return GENERICRESPONSE_CODE, b'\x01\x02'

def main():
    try:
        ser = serial.Serial(PORT, BAUDRATE, timeout=TIMEOUT)
        print(f"Эмулятор запущен на порту {PORT} (скорость {BAUDRATE}). Ожидаем команды...")
    except serial.SerialException as e:
        print(f"Ошибка открытия порта {PORT}: {e}")
        sys.exit(1)

    while True:
        if ser.in_waiting >= 4:
            b = ser.read(1)
            if b == b'\xAA':
                cmd_code = ser.read(1)[0]
                length = ser.read(1)[0]
                if length > 255:
                    print("Некорректная длина, игнорируем")
                    continue
                data = ser.read(length)
                if len(data) != length:
                    print("Недостаточно данных, игнорируем")
                    continue
                crc_received = ser.read(1)
                if not crc_received:
                    continue
                crc_received = crc_received[0]

                expected_crc = calc_crc(bytes([cmd_code, length]) + data)
                if crc_received != expected_crc:
                    print(f"CRC mismatch: ожидалось {expected_crc:02x}, получено {crc_received:02x}")
                    continue

                print(f"Получена команда: код={cmd_code}, данные={data.hex()}")
                resp_code, resp_data = handle_command(cmd_code, data)
                send_response(ser, resp_code, resp_data)
        time.sleep(0.01)

if __name__ == '__main__':
    main()