# -*- coding: utf-8 -*-
"""
Модель конфигурации команд для камеры и менеджер загрузки/сохранения.
Конфигурация определяет все команды, параметры порта и форматы пакетов.
"""

from __future__ import annotations
import json
from dataclasses import dataclass, asdict
from pathlib import Path
from typing import Dict, Optional


@dataclass
class CameraCommandConfig:
    """
    Набор команд и параметров для общения с конкретной версией камеры.
    Поля соответствуют протоколу CM 2.0.
    """
    name: str                      # Уникальное имя профиля
    description: str = ""          # Краткое описание
    version: str = ""              # Версия прошивки (для автоподбора)

    # ---- Базовые команды (символы или hex-коды) ----
    capture: str = "t"             # 0x74 – сделать снимок
    properties: str = "p"          # 0x70 – запрос свойств снимка
    next_chunk: str = "n"          # 0x6e – запрос следующего чанка
    set_size: str = "s"            # 0x73 – установить размер (только ширина+высота)
    set_exposure: str = "e"        # 0x65 – установить экспозицию
    start_transfer: str = ""       # (зарезервировано, в CM 2.0 не используется)
    get_version: str = "v"         # 0x76 – запрос версии прошивки

    # ---- Параметры UART ----
    baudrate: int = 230400
    preamble: str = "ffff00"       # 3 байта в hex (little-endian порядок)
    postamble: str = "00ff00"      # 3 байта в hex

    # ---- Параметры данных ----
    chunk_size: int = 240          # Размер полезной нагрузки в байтах
    property_size: int = 18        # Размер структуры свойств (байт)
    timeout_capture: float = 15.0  # Таймаут ожидания ответа на захват
    timeout_chunk: float = 2.0     # Таймаут получения одного чанка
    timeout_version: float = 1.0   # Таймаут запроса версии

    # ---- Форматы распаковки (little-endian) ----
    # Структура свойств: height, width, vStart, hStart, colorspace, exposure, length, chunks
    property_format: str = "<HHHHHHLH"
    # Структура чанка: chunkID, payloadLength, isLast, payload[240], checksum
    chunk_format: str = "<HH?240BH"

    # ---- Дополнительные опции ----
    send_chunk_index: bool = False   # Отправлять ли номер чанка вместе с 'n'

    @property
    def chunk_packet_size(self) -> int:
        """Полный размер пакета чанка (с заголовками и контрольной суммой) = 247 байт."""
        return 247

    def get_command_bytes(self, cmd: str) -> bytes:
        """
        Преобразует строковое представление команды в байты.
        Поддерживает:
          - одиночный символ: 't' -> b't'
          - hex с префиксом: '0x74' -> b'\x74'
          - десятичное число: '116' -> b't'
        """
        cmd = cmd.strip()
        if not cmd:
            return b''
        if cmd.startswith('0x'):
            return bytes([int(cmd, 16)])
        elif cmd.isdigit():
            return bytes([int(cmd)])
        else:
            return cmd.encode('ascii')

    def to_dict(self) -> dict:
        """Сериализация в словарь для сохранения в JSON."""
        return asdict(self)

    @classmethod
    def from_dict(cls, data: dict) -> CameraCommandConfig:
        """Десериализация из словаря (загруженного из JSON)."""
        return cls(**data)


class ConfigManager:
    """
    Менеджер конфигураций: загружает/сохраняет JSON-файлы из папки configs/,
    хранит в памяти словарь {имя: CameraCommandConfig}.
    """
    def __init__(self, config_dir: Optional[Path] = None):
        self.configs: Dict[str, CameraCommandConfig] = {}
        self.config_dir = config_dir or Path(__file__).parent.parent / "configs"
        self._load_defaults()

    def _load_defaults(self):
        """Создаёт конфигурацию по умолчанию."""
        self.configs["CM 2.0"] = CameraCommandConfig(
            name="CM 2.0",
            description="Стандартная камера CM 2.0",
            version="default"
        )

    def load_from_folder(self) -> int:
        """Загружает все JSON-файлы из папки configs/."""
        if not self.config_dir.exists():
            self.config_dir.mkdir(parents=True, exist_ok=True)
            self._create_example()
            return 0

        loaded = 0
        for json_path in self.config_dir.glob("*.json"):
            try:
                with open(json_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                config = CameraCommandConfig.from_dict(data)
                self.configs[config.name] = config
                loaded += 1
            except Exception:
                continue
        return loaded

    def _create_example(self):
        """Создаёт пример конфигурации, если папка пуста."""
        example_path = self.config_dir / "example_config.json"
        if not example_path.exists():
            example = CameraCommandConfig(
                name="Example Camera",
                description="Пример конфигурации",
                version="2.0.1"
            )
            with open(example_path, 'w', encoding='utf-8') as f:
                json.dump(example.to_dict(), f, indent=2, ensure_ascii=False)

    def get(self, name: str) -> Optional[CameraCommandConfig]:
        """Возвращает конфигурацию по имени."""
        return self.configs.get(name)

    def add(self, config: CameraCommandConfig) -> bool:
        """Добавляет новую конфигурацию (если имя не занято)."""
        if config.name in self.configs:
            return False
        self.configs[config.name] = config
        self._save_config(config)
        return True

    def update(self, config: CameraCommandConfig):
        """Обновляет существующую конфигурацию (перезаписывает)."""
        self.configs[config.name] = config
        self._save_config(config)

    def _save_config(self, config: CameraCommandConfig):
        """Сохраняет конфигурацию в JSON-файл."""
        file_path = self.config_dir / f"{config.name.replace(' ', '_')}.json"
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(config.to_dict(), f, indent=2, ensure_ascii=False)

    def get_by_version(self, version: str) -> list:
        """Возвращает список (имя, конфиг) для всех профилей с указанной версией."""
        return [(name, cfg) for name, cfg in self.configs.items()
                if cfg.version == version]