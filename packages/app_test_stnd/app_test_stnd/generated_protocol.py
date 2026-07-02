"""
Автоматически сгенерированный модуль протокола.
Не редактируйте вручную – изменения будут потеряны при перегенерации.
"""
import struct
from typing import Dict, Any, Optional

# ---------- Коды команд ----------
GETVERSION_CODE = 0
GETSTATUS_CODE = 1
RESET_CODE = 2
GPIOINITOUTPUT_CODE = 100
GPIOINITINPUT_CODE = 101
GPIOSET_CODE = 102
GPIOREAD_CODE = 103
GPIODEINIT_CODE = 104
ADCREAD_CODE = 105
EEPROMREAD_CODE = 106
I2CPROBE_CODE = 107
I2CREADREGISTER_CODE = 108
I2CWRITEREGISTER_CODE = 109
I2CWRITE_CODE = 110
I2CREAD_CODE = 111
SPISEND_CODE = 112
SPIRECEIVE_CODE = 113
SPIEXCHANGE_CODE = 114
UARTSEND_CODE = 115
UARTRECEIVE_CODE = 116
INITI2C_CODE = 120
DEINITI2C_CODE = 121
INITSPI_CODE = 122
DEINITSPI_CODE = 123
INITUART_CODE = 124
DEINITUART_CODE = 125
VERSIONINFORESPONSE_CODE = 200
STATUSRESPONSE_CODE = 201
GPIOREADRESPONSE_CODE = 204
ADCREADRESPONSE_CODE = 205
EEPROMREADRESPONSE_CODE = 206
I2CPROBERESPONSE_CODE = 207
I2CREADREGISTERRESPONSE_CODE = 208
I2CREADRESPONSE_CODE = 209
SPIRECEIVERESPONSE_CODE = 210
SPIEXCHANGERESPONSE_CODE = 211
UARTRECEIVERESPONSE_CODE = 212
GENERICRESPONSE_CODE = 250

# ---------- Вспомогательные функции ----------
def _pack_value(value, field_type):
    """Упаковка одного значения в байты (для простых типов)."""
    if field_type == 'uint8':
        return struct.pack('<B', value)
    elif field_type == 'uint16':
        return struct.pack('<H', value)
    elif field_type == 'uint32':
        return struct.pack('<I', value)
    elif field_type == 'int8':
        return struct.pack('<b', value)
    elif field_type == 'int16':
        return struct.pack('<h', value)
    elif field_type == 'int32':
        return struct.pack('<i', value)
    elif field_type == 'float32':
        return struct.pack('<f', value)
    elif field_type == 'bool':
        return struct.pack('<?', value)
    else:
        raise ValueError(f"Unsupported type: {field_type}")

def _unpack_value(data, field_type):
    """Распаковка из байтов (для простых типов)."""
    if field_type == 'uint8':
        return struct.unpack('<B', data[:1])[0]
    elif field_type == 'uint16':
        return struct.unpack('<H', data[:2])[0]
    elif field_type == 'uint32':
        return struct.unpack('<I', data[:4])[0]
    elif field_type == 'int8':
        return struct.unpack('<b', data[:1])[0]
    elif field_type == 'int16':
        return struct.unpack('<h', data[:2])[0]
    elif field_type == 'int32':
        return struct.unpack('<i', data[:4])[0]
    elif field_type == 'float32':
        return struct.unpack('<f', data[:4])[0]
    elif field_type == 'bool':
        return struct.unpack('<?', data[:1])[0]
    else:
        raise ValueError(f"Unsupported type: {field_type}")

# ---------- Классы запросов ----------
class GetVersion:
    """
    Запрос версии прошивки стенда
    Код команды: 0
    (без данных)
    """
    def __init__(self):
        pass

    def to_bytes(self) -> bytes:
        """Упаковывает запрос в байтовую последовательность (без заголовка)."""
        result = b''
        return result

class GetStatus:
    """
    Запрос статуса (включено/выключено тестируемое устройство)
    Код команды: 1
    (без данных)
    """
    def __init__(self):
        pass

    def to_bytes(self) -> bytes:
        """Упаковывает запрос в байтовую последовательность (без заголовка)."""
        result = b''
        return result

class Reset:
    """
    Перезагрузка стенда
    Код команды: 2
    (без данных)
    """
    def __init__(self):
        pass

    def to_bytes(self) -> bytes:
        """Упаковывает запрос в байтовую последовательность (без заголовка)."""
        result = b''
        return result

class GpioInitOutput:
    """
    Инициализация пина как output
    Код команды: 100
    Поля:
      - pin (uint8) – Номер пина (1-40)
      - initial_state (bool) – Начальное состояние (0/1)
      - open_drain (bool) – 0 - push-pull, 1 - open-drain
    """
    def __init__(self, pin, initial_state, open_drain):
        self.pin = pin
        self.initial_state = initial_state
        self.open_drain = open_drain

    def to_bytes(self) -> bytes:
        """Упаковывает запрос в байтовую последовательность (без заголовка)."""
        result = b''
        result += _pack_value(self.pin, 'uint8')
        result += _pack_value(self.initial_state, 'bool')
        result += _pack_value(self.open_drain, 'bool')
        return result

class GpioInitInput:
    """
    Инициализация пина как input
    Код команды: 101
    Поля:
      - pin (uint8) – 
      - pull (uint8) – 0 - no pull, 1 - pull-up, 2 - pull-down
    """
    def __init__(self, pin, pull):
        self.pin = pin
        self.pull = pull

    def to_bytes(self) -> bytes:
        """Упаковывает запрос в байтовую последовательность (без заголовка)."""
        result = b''
        result += _pack_value(self.pin, 'uint8')
        result += _pack_value(self.pull, 'uint8')
        return result

class GpioSet:
    """
    Установка состояния пина
    Код команды: 102
    Поля:
      - pin (uint8) – 
      - value (bool) – 
    """
    def __init__(self, pin, value):
        self.pin = pin
        self.value = value

    def to_bytes(self) -> bytes:
        """Упаковывает запрос в байтовую последовательность (без заголовка)."""
        result = b''
        result += _pack_value(self.pin, 'uint8')
        result += _pack_value(self.value, 'bool')
        return result

class GpioRead:
    """
    Чтение состояния пина
    Код команды: 103
    Поля:
      - pin (uint8) – 
    """
    def __init__(self, pin):
        self.pin = pin

    def to_bytes(self) -> bytes:
        """Упаковывает запрос в байтовую последовательность (без заголовка)."""
        result = b''
        result += _pack_value(self.pin, 'uint8')
        return result

class GpioDeinit:
    """
    Деинициализация пина (возврат в состояние по умолчанию)
    Код команды: 104
    Поля:
      - pin (uint8) – 
    """
    def __init__(self, pin):
        self.pin = pin

    def to_bytes(self) -> bytes:
        """Упаковывает запрос в байтовую последовательность (без заголовка)."""
        result = b''
        result += _pack_value(self.pin, 'uint8')
        return result

class AdcRead:
    """
    Чтение напряжения на канале АЦП
    Код команды: 105
    Поля:
      - channel (uint8) – Номер канала АЦП
    """
    def __init__(self, channel):
        self.channel = channel

    def to_bytes(self) -> bytes:
        """Упаковывает запрос в байтовую последовательность (без заголовка)."""
        result = b''
        result += _pack_value(self.channel, 'uint8')
        return result

class EepromRead:
    """
    Чтение данных из EEPROM оснастки
    Код команды: 106
    Поля:
      - address (uint16) – Адрес в EEPROM
      - len (uint8) – Количество байт для чтения (макс 64)
    """
    def __init__(self, address, len):
        self.address = address
        self.len = len

    def to_bytes(self) -> bytes:
        """Упаковывает запрос в байтовую последовательность (без заголовка)."""
        result = b''
        result += _pack_value(self.address, 'uint16')
        result += _pack_value(self.len, 'uint8')
        return result

class I2cProbe:
    """
    Проверка наличия устройства на шине I2C
    Код команды: 107
    Поля:
      - address (uint8) – 7-битный адрес устройства
    """
    def __init__(self, address):
        self.address = address

    def to_bytes(self) -> bytes:
        """Упаковывает запрос в байтовую последовательность (без заголовка)."""
        result = b''
        result += _pack_value(self.address, 'uint8')
        return result

class I2cReadRegister:
    """
    Чтение данных из регистра устройства I2C
    Код команды: 108
    Поля:
      - address (uint8) – 
      - reg (uint8) – Адрес регистра
      - len (uint8) – Количество байт для чтения (макс 8)
    """
    def __init__(self, address, reg, len):
        self.address = address
        self.reg = reg
        self.len = len

    def to_bytes(self) -> bytes:
        """Упаковывает запрос в байтовую последовательность (без заголовка)."""
        result = b''
        result += _pack_value(self.address, 'uint8')
        result += _pack_value(self.reg, 'uint8')
        result += _pack_value(self.len, 'uint8')
        return result

class I2cWriteRegister:
    """
    Запись данных в регистр I2C
    Код команды: 109
    Поля:
      - address (uint8) – 
      - reg (uint8) – 
      - data_len (uint8) – Длина данных (макс 8)
      - data (uint8[8]) – Данные для записи
    """
    def __init__(self, address, reg, data_len, data):
        self.address = address
        self.reg = reg
        self.data_len = data_len
        self.data = data

    def to_bytes(self) -> bytes:
        """Упаковывает запрос в байтовую последовательность (без заголовка)."""
        result = b''
        result += _pack_value(self.address, 'uint8')
        result += _pack_value(self.reg, 'uint8')
        result += _pack_value(self.data_len, 'uint8')
        # Массив фиксированной длины
        arr_len = 8
        if len(self.data) != arr_len:
            raise ValueError(f"Array data must have length {arr_len}")
        result += struct.pack('<B', *self.data)
        return result

class I2cWrite:
    """
    Отправка данных на устройство I2C без регистра
    Код команды: 110
    Поля:
      - address (uint8) – 
      - data_len (uint8) – Длина данных (макс 64)
      - data (uint8[64]) – Данные для отправки
    """
    def __init__(self, address, data_len, data):
        self.address = address
        self.data_len = data_len
        self.data = data

    def to_bytes(self) -> bytes:
        """Упаковывает запрос в байтовую последовательность (без заголовка)."""
        result = b''
        result += _pack_value(self.address, 'uint8')
        result += _pack_value(self.data_len, 'uint8')
        # Массив фиксированной длины
        arr_len = 64
        if len(self.data) != arr_len:
            raise ValueError(f"Array data must have length {arr_len}")
        result += struct.pack('<B', *self.data)
        return result

class I2cRead:
    """
    Чтение данных с устройства I2C
    Код команды: 111
    Поля:
      - address (uint8) – 
      - len (uint8) – Количество байт для чтения (макс 64)
    """
    def __init__(self, address, len):
        self.address = address
        self.len = len

    def to_bytes(self) -> bytes:
        """Упаковывает запрос в байтовую последовательность (без заголовка)."""
        result = b''
        result += _pack_value(self.address, 'uint8')
        result += _pack_value(self.len, 'uint8')
        return result

class SpiSend:
    """
    Отправка данных по SPI
    Код команды: 112
    Поля:
      - spi_num (uint8) – Номер SPI (1,2...)
      - data_len (uint8) – Длина данных (макс 64)
      - data (uint8[64]) – Данные для отправки
    """
    def __init__(self, spi_num, data_len, data):
        self.spi_num = spi_num
        self.data_len = data_len
        self.data = data

    def to_bytes(self) -> bytes:
        """Упаковывает запрос в байтовую последовательность (без заголовка)."""
        result = b''
        result += _pack_value(self.spi_num, 'uint8')
        result += _pack_value(self.data_len, 'uint8')
        # Массив фиксированной длины
        arr_len = 64
        if len(self.data) != arr_len:
            raise ValueError(f"Array data must have length {arr_len}")
        result += struct.pack('<B', *self.data)
        return result

class SpiReceive:
    """
    Прием данных по SPI (с отправкой dummy байт)
    Код команды: 113
    Поля:
      - spi_num (uint8) – 
      - len (uint8) – Количество байт для приема (макс 64)
    """
    def __init__(self, spi_num, len):
        self.spi_num = spi_num
        self.len = len

    def to_bytes(self) -> bytes:
        """Упаковывает запрос в байтовую последовательность (без заголовка)."""
        result = b''
        result += _pack_value(self.spi_num, 'uint8')
        result += _pack_value(self.len, 'uint8')
        return result

class SpiExchange:
    """
    Полнодуплексный обмен по SPI (отправка и прием одновременно)
    Код команды: 114
    Поля:
      - spi_num (uint8) – 
      - tx_len (uint8) – Длина отправляемых данных (макс 64)
      - tx_data (uint8[64]) – Данные для отправки
    """
    def __init__(self, spi_num, tx_len, tx_data):
        self.spi_num = spi_num
        self.tx_len = tx_len
        self.tx_data = tx_data

    def to_bytes(self) -> bytes:
        """Упаковывает запрос в байтовую последовательность (без заголовка)."""
        result = b''
        result += _pack_value(self.spi_num, 'uint8')
        result += _pack_value(self.tx_len, 'uint8')
        # Массив фиксированной длины
        arr_len = 64
        if len(self.tx_data) != arr_len:
            raise ValueError(f"Array tx_data must have length {arr_len}")
        result += struct.pack('<B', *self.tx_data)
        return result

class UartSend:
    """
    Отправка данных по UART
    Код команды: 115
    Поля:
      - uart_num (uint8) – Номер UART (1,2...)
      - data_len (uint8) – Длина данных (макс 64)
      - data (uint8[64]) – Данные для отправки
    """
    def __init__(self, uart_num, data_len, data):
        self.uart_num = uart_num
        self.data_len = data_len
        self.data = data

    def to_bytes(self) -> bytes:
        """Упаковывает запрос в байтовую последовательность (без заголовка)."""
        result = b''
        result += _pack_value(self.uart_num, 'uint8')
        result += _pack_value(self.data_len, 'uint8')
        # Массив фиксированной длины
        arr_len = 64
        if len(self.data) != arr_len:
            raise ValueError(f"Array data must have length {arr_len}")
        result += struct.pack('<B', *self.data)
        return result

class UartReceive:
    """
    Ожидание и прием данных по UART с таймаутом
    Код команды: 116
    Поля:
      - uart_num (uint8) – 
      - timeout_ms (uint16) – Таймаут ожидания в миллисекундах
      - max_len (uint8) – Максимальное количество байт для приема (макс 64)
    """
    def __init__(self, uart_num, timeout_ms, max_len):
        self.uart_num = uart_num
        self.timeout_ms = timeout_ms
        self.max_len = max_len

    def to_bytes(self) -> bytes:
        """Упаковывает запрос в байтовую последовательность (без заголовка)."""
        result = b''
        result += _pack_value(self.uart_num, 'uint8')
        result += _pack_value(self.timeout_ms, 'uint16')
        result += _pack_value(self.max_len, 'uint8')
        return result

class InitI2c:
    """
    Инициализация модуля I2C
    Код команды: 120
    Поля:
      - i2c_num (uint8) – Номер I2C (1,2...)
      - speed (uint32) – Частота в Гц (например, 100000)
    """
    def __init__(self, i2c_num, speed):
        self.i2c_num = i2c_num
        self.speed = speed

    def to_bytes(self) -> bytes:
        """Упаковывает запрос в байтовую последовательность (без заголовка)."""
        result = b''
        result += _pack_value(self.i2c_num, 'uint8')
        result += _pack_value(self.speed, 'uint32')
        return result

class DeinitI2c:
    """
    Деинициализация модуля I2C
    Код команды: 121
    Поля:
      - i2c_num (uint8) – 
    """
    def __init__(self, i2c_num):
        self.i2c_num = i2c_num

    def to_bytes(self) -> bytes:
        """Упаковывает запрос в байтовую последовательность (без заголовка)."""
        result = b''
        result += _pack_value(self.i2c_num, 'uint8')
        return result

class InitSpi:
    """
    Инициализация модуля SPI
    Код команды: 122
    Поля:
      - spi_num (uint8) – 
      - speed (uint32) – Частота в Гц
      - mode (uint8) – Режим SPI (0-3)
      - bit_order (uint8) – 0 - MSB first, 1 - LSB first
    """
    def __init__(self, spi_num, speed, mode, bit_order):
        self.spi_num = spi_num
        self.speed = speed
        self.mode = mode
        self.bit_order = bit_order

    def to_bytes(self) -> bytes:
        """Упаковывает запрос в байтовую последовательность (без заголовка)."""
        result = b''
        result += _pack_value(self.spi_num, 'uint8')
        result += _pack_value(self.speed, 'uint32')
        result += _pack_value(self.mode, 'uint8')
        result += _pack_value(self.bit_order, 'uint8')
        return result

class DeinitSpi:
    """
    Деинициализация модуля SPI
    Код команды: 123
    Поля:
      - spi_num (uint8) – 
    """
    def __init__(self, spi_num):
        self.spi_num = spi_num

    def to_bytes(self) -> bytes:
        """Упаковывает запрос в байтовую последовательность (без заголовка)."""
        result = b''
        result += _pack_value(self.spi_num, 'uint8')
        return result

class InitUart:
    """
    Инициализация модуля UART
    Код команды: 124
    Поля:
      - uart_num (uint8) – 
      - baudrate (uint32) – Скорость в бод
      - parity (uint8) – 0 - none, 1 - even, 2 - odd
      - stop_bits (uint8) – 1 или 2
      - data_bits (uint8) – 5-8
    """
    def __init__(self, uart_num, baudrate, parity, stop_bits, data_bits):
        self.uart_num = uart_num
        self.baudrate = baudrate
        self.parity = parity
        self.stop_bits = stop_bits
        self.data_bits = data_bits

    def to_bytes(self) -> bytes:
        """Упаковывает запрос в байтовую последовательность (без заголовка)."""
        result = b''
        result += _pack_value(self.uart_num, 'uint8')
        result += _pack_value(self.baudrate, 'uint32')
        result += _pack_value(self.parity, 'uint8')
        result += _pack_value(self.stop_bits, 'uint8')
        result += _pack_value(self.data_bits, 'uint8')
        return result

class DeinitUart:
    """
    Деинициализация модуля UART
    Код команды: 125
    Поля:
      - uart_num (uint8) – 
    """
    def __init__(self, uart_num):
        self.uart_num = uart_num

    def to_bytes(self) -> bytes:
        """Упаковывает запрос в байтовую последовательность (без заголовка)."""
        result = b''
        result += _pack_value(self.uart_num, 'uint8')
        return result


# ---------- Классы ответов ----------
class VersionInfoResponse:
    """
    Ответ на GetVersion
    Код ответа: 200
    Поля:
      - major (uint8) – 
      - minor (uint8) – 
      - patch (uint8) – 
    """
    def __init__(self, data: bytes):
        """Распаковывает данные ответа."""
        offset = 0
        self.major = _unpack_value(data[offset:], 'uint8')
        offset += struct.calcsize('<' + {
            'uint8': 'B', 'uint16': 'H', 'uint32': 'I',
            'int8': 'b', 'int16': 'h', 'int32': 'i',
            'float32': 'f', 'bool': '?'
        }['uint8'])
        self.minor = _unpack_value(data[offset:], 'uint8')
        offset += struct.calcsize('<' + {
            'uint8': 'B', 'uint16': 'H', 'uint32': 'I',
            'int8': 'b', 'int16': 'h', 'int32': 'i',
            'float32': 'f', 'bool': '?'
        }['uint8'])
        self.patch = _unpack_value(data[offset:], 'uint8')
        offset += struct.calcsize('<' + {
            'uint8': 'B', 'uint16': 'H', 'uint32': 'I',
            'int8': 'b', 'int16': 'h', 'int32': 'i',
            'float32': 'f', 'bool': '?'
        }['uint8'])

class StatusResponse:
    """
    Ответ на GetStatus
    Код ответа: 201
    Поля:
      - powered (bool) – Включено ли тестируемое устройство
    """
    def __init__(self, data: bytes):
        """Распаковывает данные ответа."""
        offset = 0
        self.powered = _unpack_value(data[offset:], 'bool')
        offset += struct.calcsize('<' + {
            'uint8': 'B', 'uint16': 'H', 'uint32': 'I',
            'int8': 'b', 'int16': 'h', 'int32': 'i',
            'float32': 'f', 'bool': '?'
        }['bool'])

class GpioReadResponse:
    """
    Ответ на GpioRead
    Код ответа: 204
    Поля:
      - status (uint8) – 0 - OK, 1 - ERROR
      - error_code (uint8) – 
      - value (bool) – Состояние пина
    """
    def __init__(self, data: bytes):
        """Распаковывает данные ответа."""
        offset = 0
        self.status = _unpack_value(data[offset:], 'uint8')
        offset += struct.calcsize('<' + {
            'uint8': 'B', 'uint16': 'H', 'uint32': 'I',
            'int8': 'b', 'int16': 'h', 'int32': 'i',
            'float32': 'f', 'bool': '?'
        }['uint8'])
        self.error_code = _unpack_value(data[offset:], 'uint8')
        offset += struct.calcsize('<' + {
            'uint8': 'B', 'uint16': 'H', 'uint32': 'I',
            'int8': 'b', 'int16': 'h', 'int32': 'i',
            'float32': 'f', 'bool': '?'
        }['uint8'])
        self.value = _unpack_value(data[offset:], 'bool')
        offset += struct.calcsize('<' + {
            'uint8': 'B', 'uint16': 'H', 'uint32': 'I',
            'int8': 'b', 'int16': 'h', 'int32': 'i',
            'float32': 'f', 'bool': '?'
        }['bool'])

class AdcReadResponse:
    """
    Ответ на AdcRead
    Код ответа: 205
    Поля:
      - status (uint8) – 
      - error_code (uint8) – 
      - voltage_mv (uint16) – Напряжение в милливольтах
    """
    def __init__(self, data: bytes):
        """Распаковывает данные ответа."""
        offset = 0
        self.status = _unpack_value(data[offset:], 'uint8')
        offset += struct.calcsize('<' + {
            'uint8': 'B', 'uint16': 'H', 'uint32': 'I',
            'int8': 'b', 'int16': 'h', 'int32': 'i',
            'float32': 'f', 'bool': '?'
        }['uint8'])
        self.error_code = _unpack_value(data[offset:], 'uint8')
        offset += struct.calcsize('<' + {
            'uint8': 'B', 'uint16': 'H', 'uint32': 'I',
            'int8': 'b', 'int16': 'h', 'int32': 'i',
            'float32': 'f', 'bool': '?'
        }['uint8'])
        self.voltage_mv = _unpack_value(data[offset:], 'uint16')
        offset += struct.calcsize('<' + {
            'uint8': 'B', 'uint16': 'H', 'uint32': 'I',
            'int8': 'b', 'int16': 'h', 'int32': 'i',
            'float32': 'f', 'bool': '?'
        }['uint16'])

class EepromReadResponse:
    """
    Ответ на EepromRead
    Код ответа: 206
    Поля:
      - status (uint8) – 
      - error_code (uint8) – 
      - data_len (uint8) – Реальная длина данных
      - data (uint8[64]) – Прочитанные данные
    """
    def __init__(self, data: bytes):
        """Распаковывает данные ответа."""
        offset = 0
        self.status = _unpack_value(data[offset:], 'uint8')
        offset += struct.calcsize('<' + {
            'uint8': 'B', 'uint16': 'H', 'uint32': 'I',
            'int8': 'b', 'int16': 'h', 'int32': 'i',
            'float32': 'f', 'bool': '?'
        }['uint8'])
        self.error_code = _unpack_value(data[offset:], 'uint8')
        offset += struct.calcsize('<' + {
            'uint8': 'B', 'uint16': 'H', 'uint32': 'I',
            'int8': 'b', 'int16': 'h', 'int32': 'i',
            'float32': 'f', 'bool': '?'
        }['uint8'])
        self.data_len = _unpack_value(data[offset:], 'uint8')
        offset += struct.calcsize('<' + {
            'uint8': 'B', 'uint16': 'H', 'uint32': 'I',
            'int8': 'b', 'int16': 'h', 'int32': 'i',
            'float32': 'f', 'bool': '?'
        }['uint8'])
        arr_len = 64
        self.data = list(struct.unpack('<{}B'.format(arr_len), data[offset:offset+arr_len]))
        offset += arr_len

class I2cProbeResponse:
    """
    Ответ на I2cProbe
    Код ответа: 207
    Поля:
      - status (uint8) – 
      - error_code (uint8) – 
      - present (bool) – Устройство обнаружено
    """
    def __init__(self, data: bytes):
        """Распаковывает данные ответа."""
        offset = 0
        self.status = _unpack_value(data[offset:], 'uint8')
        offset += struct.calcsize('<' + {
            'uint8': 'B', 'uint16': 'H', 'uint32': 'I',
            'int8': 'b', 'int16': 'h', 'int32': 'i',
            'float32': 'f', 'bool': '?'
        }['uint8'])
        self.error_code = _unpack_value(data[offset:], 'uint8')
        offset += struct.calcsize('<' + {
            'uint8': 'B', 'uint16': 'H', 'uint32': 'I',
            'int8': 'b', 'int16': 'h', 'int32': 'i',
            'float32': 'f', 'bool': '?'
        }['uint8'])
        self.present = _unpack_value(data[offset:], 'bool')
        offset += struct.calcsize('<' + {
            'uint8': 'B', 'uint16': 'H', 'uint32': 'I',
            'int8': 'b', 'int16': 'h', 'int32': 'i',
            'float32': 'f', 'bool': '?'
        }['bool'])

class I2cReadRegisterResponse:
    """
    Ответ на I2cReadRegister
    Код ответа: 208
    Поля:
      - status (uint8) – 
      - error_code (uint8) – 
      - data_len (uint8) – 
      - data (uint8[8]) – Прочитанные данные регистра
    """
    def __init__(self, data: bytes):
        """Распаковывает данные ответа."""
        offset = 0
        self.status = _unpack_value(data[offset:], 'uint8')
        offset += struct.calcsize('<' + {
            'uint8': 'B', 'uint16': 'H', 'uint32': 'I',
            'int8': 'b', 'int16': 'h', 'int32': 'i',
            'float32': 'f', 'bool': '?'
        }['uint8'])
        self.error_code = _unpack_value(data[offset:], 'uint8')
        offset += struct.calcsize('<' + {
            'uint8': 'B', 'uint16': 'H', 'uint32': 'I',
            'int8': 'b', 'int16': 'h', 'int32': 'i',
            'float32': 'f', 'bool': '?'
        }['uint8'])
        self.data_len = _unpack_value(data[offset:], 'uint8')
        offset += struct.calcsize('<' + {
            'uint8': 'B', 'uint16': 'H', 'uint32': 'I',
            'int8': 'b', 'int16': 'h', 'int32': 'i',
            'float32': 'f', 'bool': '?'
        }['uint8'])
        arr_len = 8
        self.data = list(struct.unpack('<{}B'.format(arr_len), data[offset:offset+arr_len]))
        offset += arr_len

class I2cReadResponse:
    """
    Ответ на I2cRead
    Код ответа: 209
    Поля:
      - status (uint8) – 
      - error_code (uint8) – 
      - data_len (uint8) – 
      - data (uint8[64]) – Прочитанные данные
    """
    def __init__(self, data: bytes):
        """Распаковывает данные ответа."""
        offset = 0
        self.status = _unpack_value(data[offset:], 'uint8')
        offset += struct.calcsize('<' + {
            'uint8': 'B', 'uint16': 'H', 'uint32': 'I',
            'int8': 'b', 'int16': 'h', 'int32': 'i',
            'float32': 'f', 'bool': '?'
        }['uint8'])
        self.error_code = _unpack_value(data[offset:], 'uint8')
        offset += struct.calcsize('<' + {
            'uint8': 'B', 'uint16': 'H', 'uint32': 'I',
            'int8': 'b', 'int16': 'h', 'int32': 'i',
            'float32': 'f', 'bool': '?'
        }['uint8'])
        self.data_len = _unpack_value(data[offset:], 'uint8')
        offset += struct.calcsize('<' + {
            'uint8': 'B', 'uint16': 'H', 'uint32': 'I',
            'int8': 'b', 'int16': 'h', 'int32': 'i',
            'float32': 'f', 'bool': '?'
        }['uint8'])
        arr_len = 64
        self.data = list(struct.unpack('<{}B'.format(arr_len), data[offset:offset+arr_len]))
        offset += arr_len

class SpiReceiveResponse:
    """
    Ответ на SpiReceive
    Код ответа: 210
    Поля:
      - status (uint8) – 
      - error_code (uint8) – 
      - data_len (uint8) – 
      - data (uint8[64]) – Полученные данные
    """
    def __init__(self, data: bytes):
        """Распаковывает данные ответа."""
        offset = 0
        self.status = _unpack_value(data[offset:], 'uint8')
        offset += struct.calcsize('<' + {
            'uint8': 'B', 'uint16': 'H', 'uint32': 'I',
            'int8': 'b', 'int16': 'h', 'int32': 'i',
            'float32': 'f', 'bool': '?'
        }['uint8'])
        self.error_code = _unpack_value(data[offset:], 'uint8')
        offset += struct.calcsize('<' + {
            'uint8': 'B', 'uint16': 'H', 'uint32': 'I',
            'int8': 'b', 'int16': 'h', 'int32': 'i',
            'float32': 'f', 'bool': '?'
        }['uint8'])
        self.data_len = _unpack_value(data[offset:], 'uint8')
        offset += struct.calcsize('<' + {
            'uint8': 'B', 'uint16': 'H', 'uint32': 'I',
            'int8': 'b', 'int16': 'h', 'int32': 'i',
            'float32': 'f', 'bool': '?'
        }['uint8'])
        arr_len = 64
        self.data = list(struct.unpack('<{}B'.format(arr_len), data[offset:offset+arr_len]))
        offset += arr_len

class SpiExchangeResponse:
    """
    Ответ на SpiExchange
    Код ответа: 211
    Поля:
      - status (uint8) – 
      - error_code (uint8) – 
      - rx_len (uint8) – 
      - rx_data (uint8[64]) – Полученные данные
    """
    def __init__(self, data: bytes):
        """Распаковывает данные ответа."""
        offset = 0
        self.status = _unpack_value(data[offset:], 'uint8')
        offset += struct.calcsize('<' + {
            'uint8': 'B', 'uint16': 'H', 'uint32': 'I',
            'int8': 'b', 'int16': 'h', 'int32': 'i',
            'float32': 'f', 'bool': '?'
        }['uint8'])
        self.error_code = _unpack_value(data[offset:], 'uint8')
        offset += struct.calcsize('<' + {
            'uint8': 'B', 'uint16': 'H', 'uint32': 'I',
            'int8': 'b', 'int16': 'h', 'int32': 'i',
            'float32': 'f', 'bool': '?'
        }['uint8'])
        self.rx_len = _unpack_value(data[offset:], 'uint8')
        offset += struct.calcsize('<' + {
            'uint8': 'B', 'uint16': 'H', 'uint32': 'I',
            'int8': 'b', 'int16': 'h', 'int32': 'i',
            'float32': 'f', 'bool': '?'
        }['uint8'])
        arr_len = 64
        self.rx_data = list(struct.unpack('<{}B'.format(arr_len), data[offset:offset+arr_len]))
        offset += arr_len

class UartReceiveResponse:
    """
    Ответ на UartReceive
    Код ответа: 212
    Поля:
      - status (uint8) – 
      - error_code (uint8) – 
      - data_len (uint8) – 
      - data (uint8[64]) – Принятые данные
    """
    def __init__(self, data: bytes):
        """Распаковывает данные ответа."""
        offset = 0
        self.status = _unpack_value(data[offset:], 'uint8')
        offset += struct.calcsize('<' + {
            'uint8': 'B', 'uint16': 'H', 'uint32': 'I',
            'int8': 'b', 'int16': 'h', 'int32': 'i',
            'float32': 'f', 'bool': '?'
        }['uint8'])
        self.error_code = _unpack_value(data[offset:], 'uint8')
        offset += struct.calcsize('<' + {
            'uint8': 'B', 'uint16': 'H', 'uint32': 'I',
            'int8': 'b', 'int16': 'h', 'int32': 'i',
            'float32': 'f', 'bool': '?'
        }['uint8'])
        self.data_len = _unpack_value(data[offset:], 'uint8')
        offset += struct.calcsize('<' + {
            'uint8': 'B', 'uint16': 'H', 'uint32': 'I',
            'int8': 'b', 'int16': 'h', 'int32': 'i',
            'float32': 'f', 'bool': '?'
        }['uint8'])
        arr_len = 64
        self.data = list(struct.unpack('<{}B'.format(arr_len), data[offset:offset+arr_len]))
        offset += arr_len

class GenericResponse:
    """
    Общий ответ для команд без данных (инициализации, установка, запись и т.д.)
    Код ответа: 250
    Поля:
      - status (uint8) – 0 - OK, 1 - ERROR
      - error_code (uint8) – Код ошибки (если status=1)
    """
    def __init__(self, data: bytes):
        """Распаковывает данные ответа."""
        offset = 0
        self.status = _unpack_value(data[offset:], 'uint8')
        offset += struct.calcsize('<' + {
            'uint8': 'B', 'uint16': 'H', 'uint32': 'I',
            'int8': 'b', 'int16': 'h', 'int32': 'i',
            'float32': 'f', 'bool': '?'
        }['uint8'])
        self.error_code = _unpack_value(data[offset:], 'uint8')
        offset += struct.calcsize('<' + {
            'uint8': 'B', 'uint16': 'H', 'uint32': 'I',
            'int8': 'b', 'int16': 'h', 'int32': 'i',
            'float32': 'f', 'bool': '?'
        }['uint8'])


# ---------- Фабрика для разбора ответов ----------
RESPONSE_CLASSES: Dict[int, Any] = {
    200: VersionInfoResponse,
    201: StatusResponse,
    204: GpioReadResponse,
    205: AdcReadResponse,
    206: EepromReadResponse,
    207: I2cProbeResponse,
    208: I2cReadRegisterResponse,
    209: I2cReadResponse,
    210: SpiReceiveResponse,
    211: SpiExchangeResponse,
    212: UartReceiveResponse,
    250: GenericResponse,
}

def parse_response(code: int, data: bytes):
    """Возвращает объект ответа по его коду."""
    cls = RESPONSE_CLASSES.get(code)
    if cls is None:
        raise ValueError(f"Неизвестный код ответа: {code}")
    return cls(data)