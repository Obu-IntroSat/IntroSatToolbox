import serial
import time
import sys
import struct
import argparse

# ===== Вспомогательные функции =====


def calc_crc(data: bytes) -> int:
    crc = 0
    for b in data:
        crc ^= b
    return crc


def pack_fields(fields_def, values):
    """
    Упаковывает поля в байтовую строку согласно спецификации.
    fields_def: список кортежей (имя, тип, описание) – можно взять из протокола.
    values: словарь {имя: значение}
    """
    result = b''
    for name, ftype in fields_def:
        if ftype == 'uint8':
            result += struct.pack('<B', values[name])
        elif ftype == 'uint16':
            result += struct.pack('<H', values[name])
        elif ftype == 'uint32':
            result += struct.pack('<I', values[name])
        elif ftype == 'bool':
            result += struct.pack('<?', values[name])
        elif ftype.startswith('uint8['):
            # массив фиксированной длины, например "uint8[8]"
            length = int(ftype.split('[')[1].split(']')[0])
            arr = values[name]
            if len(arr) != length:
                raise ValueError(f"Array {name} length mismatch: expected {length}, got {len(arr)}")
            result += struct.pack(f'<{length}B', *arr)
        else:
            raise ValueError(f"Unsupported type: {ftype}")
    return result

# Описания полей для команд (для автоматической упаковки)
# Здесь перечислены только те команды, которые мы будем тестировать.
# Можно добавить все команды из протокола.
FIELD_DEFS = {
    # Системные команды (без полей)
    'GetVersion': [],
    'GetStatus': [],
    'Reset': [],
    # GPIO
    'GpioInitOutput': [('pin', 'uint8'), ('initial_state', 'bool'), ('open_drain', 'bool')],
    'GpioInitInput': [('pin', 'uint8'), ('pull', 'uint8')],
    'GpioSet': [('pin', 'uint8'), ('value', 'bool')],
    'GpioRead': [('pin', 'uint8')],
    'GpioDeinit': [('pin', 'uint8')],
    # I2C (обновлённые поля)
    'I2cProbe': [('i2c_interface', 'uint8'), ('address', 'uint16')],
    'I2cReadRegister': [('i2c_interface', 'uint8'), ('address', 'uint16'), ('reg', 'uint8'), ('len', 'uint8')],
    'I2cWriteRegister': [('i2c_interface', 'uint8'), ('address', 'uint16'), ('reg', 'uint8'), ('data_len', 'uint8'), ('data', 'uint8[8]')],
    'I2cWrite': [('i2c_interface', 'uint8'), ('address', 'uint16'), ('data_len', 'uint8'), ('data', 'uint8[64]')],
    'I2cRead': [('i2c_interface', 'uint8'), ('address', 'uint16'), ('len', 'uint8')],
    # SPI
    'SpiSend': [('spi_num', 'uint8'), ('data_len', 'uint8'), ('data', 'uint8[64]')],
    'SpiReceive': [('spi_num', 'uint8'), ('len', 'uint8')],
    'SpiExchange': [('spi_num', 'uint8'), ('tx_len', 'uint8'), ('tx_data', 'uint8[64]')],
    # UART
    'UartSend': [('uart_num', 'uint8'), ('data_len', 'uint8'), ('data', 'uint8[64]')],
    'UartReceive': [('uart_num', 'uint8'), ('timeout_ms', 'uint16'), ('max_len', 'uint8')],
    # Инициализация
    'InitI2c': [('i2c_interface', 'uint8'), ('speed', 'uint32'), ('addressing_mode', 'uint8')],
    'DeinitI2c': [('i2c_interface', 'uint8')],
    'InitSpi': [('spi_num', 'uint8'), ('speed', 'uint32'), ('mode', 'uint8'), ('bit_order', 'uint8')],
    'DeinitSpi': [('spi_num', 'uint8')],
    'InitUart': [('uart_num', 'uint8'), ('baudrate', 'uint32'), ('parity', 'uint8'), ('stop_bits', 'uint8'), ('data_bits', 'uint8')],
    'DeinitUart': [('uart_num', 'uint8')],
}


def build_packet(cmd_code: int, fields: dict) -> bytes:
    """Формирует полный пакет (старт, код, длина, данные, CRC)."""
    # Определяем список полей по коду (упрощённо – по имени команды, но здесь мы передаём имя)
    # Для универсальности добавим отдельный параметр cmd_name или будем искать по коду.
    # В этом скрипте мы будем передавать имя команды отдельно.
    pass  # Реализуем в send_command_with_fields


def send_command_with_fields(ser, cmd_name: str, cmd_code: int, params: dict):
    """
    Отправляет команду с параметрами, автоматически упаковывая поля.
    """
    fields_def = FIELD_DEFS.get(cmd_name)
    if fields_def is None:
        raise ValueError(f"Неизвестная команда: {cmd_name}")
    data = pack_fields(fields_def, params)
    length = len(data)
    header = bytes([0xAA, cmd_code, length])
    crc = calc_crc(bytes([cmd_code, length]) + data)
    packet = header + data + bytes([crc])
    ser.write(packet)
    ser.flush()
    print(f"Отправлено ({cmd_name}): {' '.join(f'{b:02X}' for b in packet)}")
    return packet


def read_response(ser, timeout=2.0):
    response = b''
    start = time.time()
    while time.time() - start < timeout:
        if ser.in_waiting:
            byte = ser.read(1)
            response += byte
            if len(response) >= 4 and response[0] == 0xAA:
                length_byte = response[2]
                total_len = 4 + length_byte
                if len(response) >= total_len:
                    # Проверка CRC
                    crc_calc = calc_crc(response[1:3] + response[3:-1])  # без стартового байта и без последнего CRC
                    if crc_calc == response[-1]:
                        return response
                    else:
                        print("CRC mismatch, ignoring packet")
                        response = b''
                        continue
        else:
            time.sleep(0.01)
    return b''  # таймаут


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('port', help='COM-порт (например, COM5)')
    parser.add_argument('--baud', type=int, default=9600, help='Скорость UART')
    parser.add_argument('--test', choices=['system', 'i2c'], default='system', help='Какой тест запустить')
    args = parser.parse_args()

    try:
        ser = serial.Serial(args.port, args.baud, timeout=1)
        print(f"Подключено к {args.port} на {args.baud} бод")
    except serial.SerialException as e:
        print(f"Ошибка: {e}")
        sys.exit(1)

    if args.test == 'system':
        print("\n=== Тест системных команд ===")

        # GetVersion
        send_command_with_fields(ser, 'GetVersion', 0, {})
        resp = read_response(ser)
        if resp:
            print("Ответ:", ' '.join(f'{b:02X}' for b in resp))
        else:
            print("Ответ не получен")

        # GetStatus
        send_command_with_fields(ser, 'GetStatus', 1, {})
        resp = read_response(ser)
        if resp:
            print("Ответ:", ' '.join(f'{b:02X}' for b in resp))
        else:
            print("Ответ не получен")

        # Неизвестная команда (код 99)
        # Для этого используем ручную отправку без имени
        cmd_code = 99
        data = b''
        length = 0
        header = bytes([0xAA, cmd_code, length])
        crc = calc_crc(bytes([cmd_code, length]) + data)
        packet = header + data + bytes([crc])
        ser.write(packet)
        ser.flush()
        print(f"Отправлено (неизвестная): {' '.join(f'{b:02X}' for b in packet)}")
        resp = read_response(ser)
        if resp:
            print("Ответ:", ' '.join(f'{b:02X}' for b in resp))
        else:
            print("Ответ не получен")

    elif args.test == 'i2c':
        print("\n=== Тест I2C (пример) ===")
        # Пример: инициализация I2C интерфейса 1 (PB6/PB7)
        send_command_with_fields(ser, 'InitI2c', 120, {
            'i2c_interface': 1,
            'speed': 100000,
            'addressing_mode': 0  # 7-бит
        })
        resp = read_response(ser)
        print("InitI2c ответ:", ' '.join(f'{b:02X}' for b in resp) if resp else "нет ответа")

        # Проверка наличия устройства по адресу 0x1E (LIS2MDL)
        send_command_with_fields(ser, 'I2cProbe', 107, {
            'i2c_interface': 1,
            'address': 0x1E
        })
        resp = read_response(ser)
        print("I2cProbe ответ:", ' '.join(f'{b:02X}' for b in resp) if resp else "нет ответа")

        # Деинициализация
        send_command_with_fields(ser, 'DeinitI2c', 121, {'i2c_interface': 1})
        resp = read_response(ser)
        print("DeinitI2c ответ:", ' '.join(f'{b:02X}' for b in resp) if resp else "нет ответа")

    ser.close()


if __name__ == '__main__':
    main()
