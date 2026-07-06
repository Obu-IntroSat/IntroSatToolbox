"""Configuration management for camera."""

from __future__ import annotations
import json
from dataclasses import dataclass, asdict
from pathlib import Path
from typing import Dict, Optional


@dataclass
class CameraCommandConfig:
    """Конфигурация команд для модуля камеры"""
    name: str
    description: str = ""
    version: str = ""
    
    capture: str = "t"
    properties: str = "p"
    next_chunk: str = "n"
    set_size: str = "s"
    set_exposure: str = "e"
    start_transfer: str = "r"
    get_version: str = "v"
    
    baudrate: int = 230400
    preamble: str = "ffff00"
    postamble: str = "00ff00"
    chunk_size: int = 240
    property_size: int = 18
    timeout_capture: float = 15.0
    timeout_chunk: float = 2.0
    timeout_version: float = 1.0
    
    property_format: str = "<HHHHHHLH"
    chunk_format: str = "<HH?240BB"
    
    def get_command_bytes(self, cmd: str) -> bytes:
        cmd = cmd.strip()
        if cmd.startswith('0x'):
            return bytes([int(cmd, 16)])
        elif cmd.isdigit():
            return bytes([int(cmd)])
        else:
            return cmd.encode('ascii')
    
    def to_dict(self) -> dict:
        return asdict(self)
    
    @classmethod
    def from_dict(cls, data: dict) -> CameraCommandConfig:
        return cls(**data)


class ConfigManager:
    """Менеджер конфигураций"""
    
    def __init__(self, config_dir: Optional[Path] = None):
        self.configs: Dict[str, CameraCommandConfig] = {}
        self.config_dir = config_dir or Path(__file__).parent.parent / "configs"
        self._load_defaults()
    
    def _load_defaults(self):
        self.configs["CM 2.0"] = CameraCommandConfig(
            name="CM 2.0",
            description="Стандартная камера CM 2.0",
            version="default"
        )
    
    def load_from_folder(self) -> int:
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
        return self.configs.get(name)
    
    def add(self, config: CameraCommandConfig) -> bool:
        if config.name in self.configs:
            return False
        self.configs[config.name] = config
        self._save_config(config)
        return True
    
    def update(self, config: CameraCommandConfig):
        self.configs[config.name] = config
        self._save_config(config)
    
    def _save_config(self, config: CameraCommandConfig):
        file_path = self.config_dir / f"{config.name.replace(' ', '_')}.json"
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(config.to_dict(), f, indent=2, ensure_ascii=False)
    
    def get_by_version(self, version: str) -> list:
        return [(name, cfg) for name, cfg in self.configs.items() 
                if cfg.version == version]