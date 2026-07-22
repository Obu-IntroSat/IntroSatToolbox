import subprocess
import sys
import os
import time

# Определяем путь к исполняемому файлу относительно этого скрипта
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
EXECUTABLE_PATH = os.path.join(SCRIPT_DIR, "..", "testUART", "Core", "Src", "test_protocol.exe")
# Нормализуем путь (убираем лишние разделители)
EXECUTABLE_PATH = os.path.normpath(EXECUTABLE_PATH)

# Проверяем, существует ли файл
if not os.path.exists(EXECUTABLE_PATH):
    print(f"Ошибка: Исполняемый файл не найден по пути: {EXECUTABLE_PATH}")
    sys.exit(1)

# Запускаем процесс
proc = subprocess.Popen(
    [EXECUTABLE_PATH],
    stdin=subprocess.PIPE,
    stdout=subprocess.PIPE,
    stderr=subprocess.PIPE,
    bufsize=0
)

def send_command(cmd_code, data=b''):
    """Отправляет команду и возвращает ответ (сырые байты)."""
    length = len(data)
    header = bytes([0xAA, cmd_code, length])
    crc = 0
    for b in bytes([cmd_code, length]) + data:
        crc ^= b
    packet = header + data + bytes([crc])
    proc.stdin.write(packet)
    proc.stdin.flush()

    # Читаем ответ: сначала ищем стартовый байт
    response = b''
    while True:
        byte = proc.stdout.read(1)
        if not byte:
            break
        response += byte
        if len(response) >= 4:
            if response[0] == 0xAA:
                length_byte = response[2]
                total = 4 + length_byte
                if len(response) >= total:
                    break
            else:
                response = b''
                continue
    return response

def print_packet(packet, label):
    print(f"{label}: " + " ".join(f"{b:02X}" for b in packet))

# Тест 1: GetVersion (код 0)
print("=== Тест GetVersion ===")
resp = send_command(0)
print_packet(resp, "Ответ")
expected = bytes([0xAA, 0xC8, 0x03, 0x00, 0x01, 0x00])
crc_expected = 0
for b in expected[1:]:
    crc_expected ^= b
expected_with_crc = expected + bytes([crc_expected])
if resp == expected_with_crc:
    print("✅ GetVersion ответ совпадает с ожидаемым")
else:
    print("❌ GetVersion ответ не совпадает")
    print("Ожидалось:", " ".join(f"{b:02X}" for b in expected_with_crc))

# Тест 2: GetStatus (код 1)
print("\n=== Тест GetStatus ===")
resp = send_command(1)
print_packet(resp, "Ответ")
expected = bytes([0xAA, 0xC9, 0x01, 0x00])
crc_expected = 0
for b in expected[1:]:
    crc_expected ^= b
expected_with_crc = expected + bytes([crc_expected])
if resp == expected_with_crc:
    print("✅ GetStatus ответ совпадает с ожидаемым")
else:
    print("❌ GetStatus ответ не совпадает")
    print("Ожидалось:", " ".join(f"{b:02X}" for b in expected_with_crc))

# Тест 3: Неизвестная команда (код 99)
print("\n=== Тест Неизвестная команда ===")
resp = send_command(99)
print_packet(resp, "Ответ")
expected = bytes([0xAA, 0xFA, 0x02, 0x01, 0x64])  # status=1, error_code=100
crc_expected = 0
for b in expected[1:]:
    crc_expected ^= b
expected_with_crc = expected + bytes([crc_expected])
if resp == expected_with_crc:
    print("✅ Неизвестная команда ответ совпадает с ожидаемым")
else:
    print("❌ Неизвестная команда ответ не совпадает")
    print("Ожидалось:", " ".join(f"{b:02X}" for b in expected_with_crc))

# Завершаем процесс
proc.terminate()
print("\nТестирование завершено.")