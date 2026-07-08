"""Run the firmware Git repo app on its own."""

from __future__ import annotations

import sys
import os
from pathlib import Path


def setup_paths():
    """Добавляет пути к модулям для собранного приложения."""
    if getattr(sys, 'frozen', False):
        # Запущено как собранное приложение
        app_dir = Path(sys.executable).parent
        
        # Пробуем разные варианты путей
        possible_paths = [
            app_dir / "packages",
            app_dir.parent / "packages",
            app_dir.parent.parent / "packages",
            Path(os.path.dirname(sys.executable)) / "packages",
        ]
        
        for path in possible_paths:
            if path.exists():
                sys.path.insert(0, str(path))
                print(f"Добавлен путь: {path}")
                break
        
        # Добавляем core если есть
        core_path = app_dir / "packages" / "core"
        if core_path.exists():
            sys.path.insert(0, str(core_path))
            print(f"Добавлен core: {core_path}")


# Настраиваем пути перед импортом
setup_paths()

try:
    from satcore import run_standalone
    from app_firmware_gitrepo.plugin import FirmwareGitRepoPlugin
except ImportError as e:
    print(f"Ошибка импорта: {e}")
    print(f"Пути поиска: {sys.path}")
    sys.exit(1)


def main() -> int:
    return run_standalone(FirmwareGitRepoPlugin())


if __name__ == "__main__":
    sys.exit(main())