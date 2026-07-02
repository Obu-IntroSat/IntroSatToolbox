#!/usr/bin/env python3
"""
Эмулятор микроконтроллера для тестирования протокола.
Поддерживает I2C (LIS2MDL, LSM6DS3) и SPI (CC1101).
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

    INITSPI_CODE,
    DEINITSPI_CODE,
    SPISEND_CODE,
    SPIRECEIVE_CODE,
    SPIEXCHANGE_CODE,

    SPIRECEIVERESPONSE_CODE,
    SPIEXCHANGERESPONSE_CODE,

    GPIOINITOUTPUT_CODE,
    GPIOINITINPUT_CODE,
    GPIOSET_CODE,
    GPIOREAD_CODE,
    GPIODEINIT_CODE,

    ADCREAD_CODE,
    EEPROMREAD_CODE,
    UARTSEND_CODE,
    UARTRECEIVE_CODE,
)

# ===== НАСТРОЙКИ =====
PORT = 'COM16'          # Второй порт из пары
BAUDRATE = 9600
TIMEOUT = 0.1
ERROR_MODE = False      # Установите True для имитации ошибок
# =====================

# Глобальное состояние GPIO (пин -> значение)
gpio_pins = {}
# Состояние CS (пин 2) по умолчанию высокое
gpio_pins[2] = 1


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
    global gpio_pins, ERROR_MODE

    # ---- Системные команды ----
    if cmd_code == GETSTATUS_CODE:
        return STATUSRESPONSE_CODE, b'\x01'

    # ---- GPIO ----
    if cmd_code == GPIOINITOUTPUT_CODE or cmd_code == GPIOINITINPUT_CODE:
        # Просто имитируем успех
        return GENERICRESPONSE_CODE, b'\x00\x00'

    if cmd_code == GPIOSET_CODE:
        if len(data) >= 2:
            pin = data[0]
            value = data[1]
            gpio_pins[pin] = value
            print(f"   GPIO: пин {pin} установлен в {value}")
        return GENERICRESPONSE_CODE, b'\x00\x00'

    if cmd_code == GPIOREAD_CODE:
        # Для простоты возвращаем текущее состояние или 0
        pin = data[0] if len(data) > 0 else 0
        val = gpio_pins.get(pin, 0)
        return GENERICRESPONSE_CODE, bytes([0x00, 0x00, val])  # status=0, error=0, value

    if cmd_code == GPIODEINIT_CODE:
        return GENERICRESPONSE_CODE, b'\x00\x00'

    # ---- I2C команды ----
    if cmd_code == INITI2C_CODE or cmd_code == DEINITI2C_CODE:
        return GENERICRESPONSE_CODE, b'\x00\x00'

    if cmd_code == I2CPROBE_CODE:
        address = data[0] if len(data) > 0 else 0
        if address in (0x1E, 0x6A):
            return I2CPROBERESPONSE_CODE, b'\x00\x00\x01'  # present=1
        else:
            return I2CPROBERESPONSE_CODE, b'\x00\x00\x00'

    if cmd_code == I2CREADREGISTER_CODE:
        if len(data) < 3:
            return GENERICRESPONSE_CODE, b'\x01\x01'
        address = data[0]
        reg = data[1]
        if address == 0x1E and reg == 0x4F:   # LIS2MDL
            return I2CREADREGISTERRESPONSE_CODE, b'\x00\x00\x01' + b'\x40' + b'\x00' * 7
        elif address == 0x6A and reg == 0x0F:  # LSM6DS3
            if ERROR_MODE:
                # имитация ошибки: неверный WHO_AM_I
                return I2CREADREGISTERRESPONSE_CODE, b'\x00\x00\x01' + b'\x00' + b'\x00' * 7
            else:
                return I2CREADREGISTERRESPONSE_CODE, b'\x00\x00\x01' + b'\x69' + b'\x00' * 7
        else:
            return GENERICRESPONSE_CODE, b'\x01\x02'

    if cmd_code == I2CREAD_CODE:
        if len(data) < 2:
            return GENERICRESPONSE_CODE, b'\x01\x01'
        address = data[0]
        length = data[1]
        if address == 0x1E:
            sample = bytes([0x01, 0x02, 0x03, 0x04, 0x05, 0x06])
            return I2CREADRESPONSE_CODE, b'\x00\x00\x06' + sample + b'\x00' * 58
        elif address == 0x6A:
            sample = bytes([0x10, 0x00, 0x20, 0x00, 0x30, 0x00])
            return I2CREADRESPONSE_CODE, b'\x00\x00\x06' + sample + b'\x00' * 58
        else:
            return GENERICRESPONSE_CODE, b'\x01\x02'

    if cmd_code in (I2CWRITEREGISTER_CODE, I2CWRITE_CODE):
        return GENERICRESPONSE_CODE, b'\x00\x00'

    # ---- SPI команды ----
    if cmd_code == INITSPI_CODE or cmd_code == DEINITSPI_CODE:
        return GENERICRESPONSE_CODE, b'\x00\x00'

    if cmd_code == SPISEND_CODE:
        # Просто имитация успешной отправки
        return GENERICRESPONSE_CODE, b'\x00\x00'

    if cmd_code == SPIRECEIVE_CODE:
        # Возвращаем массив нулей длины len (data[1])
        if len(data) < 2:
            return GENERICRESPONSE_CODE, b'\x01\x01'
        length = data[1] if len(data) > 1 else 1
        # Ограничим 64 байта
        if length > 64:
            length = 64
        return SPIRECEIVERESPONSE_CODE, b'\x00\x00' + bytes([length]) + b'\x00' * length + b'\x00' * (64 - length)

    if cmd_code == SPIEXCHANGE_CODE:
        # Проверяем, что CS (пин 2) низкий
        if gpio_pins.get(2, 1) != 0:
            # CS не активирован – ошибка
            return GENERICRESPONSE_CODE, b'\x01\x03'  # ошибка: CS не в низком уровне

        # data содержит: spi_num, tx_len, tx_data (до 64 байт)
        if len(data) < 3:
            return GENERICRESPONSE_CODE, b'\x01\x01'
        tx_len = data[1]
        # tx_data начинается с индекса 2
        tx_data = data[2:2+tx_len]
        if not tx_data:
            return GENERICRESPONSE_CODE, b'\x01\x01'

        # Анализируем команду: первый байт – адрес/команда
        cmd_byte = tx_data[0]
        if cmd_byte == 0xB0:  # Чтение регистра версии CC1101
            if ERROR_MODE:
                # имитация неверной версии
                version = 0x00
            else:
                version = 0x04
            # Ответ: статус SPI (1 байт, например 0x00) + данные (version)
            # В CC1101 при чтении возвращается статус и данные регистра
            # Мы вернём 2 байта: статус (0x00) и version
            response_data = bytes([0x00, version])
            # Упакуем в формат ответа SpiExchangeResponse: status, error, rx_len, rx_data (64 байта)
            rx_len = len(response_data)
            full_data = response_data + b'\x00' * (64 - rx_len)
            return SPIEXCHANGERESPONSE_CODE, b'\x00\x00' + bytes([rx_len]) + full_data
        else:
            # Другие команды – возвращаем нули
            return SPIEXCHANGERESPONSE_CODE, b'\x00\x00\x00' + b'\x00' * 64

    # ---- Прочие заглушки ----
    if cmd_code in (ADCREAD_CODE, EEPROMREAD_CODE, UARTSEND_CODE, UARTRECEIVE_CODE):
        return GENERICRESPONSE_CODE, b'\x00\x00'

    # ---- Неизвестная команда ----
    print(f"   Неизвестная команда: {cmd_code}")
    return GENERICRESPONSE_CODE, b'\x01\x02'

def main():
    try:
        ser = serial.Serial(PORT, BAUDRATE, timeout=TIMEOUT)
        print(f"Эмулятор запущен на порту {PORT} (скорость {BAUDRATE}). Ожидаем команды...")
        print(f"Режим ошибок: {'ВКЛЮЧЕН' if ERROR_MODE else 'ВЫКЛЮЧЕН'}")
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