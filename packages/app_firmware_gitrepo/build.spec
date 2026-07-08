# -*- mode: python ; coding: utf-8 -*-

import sys
import os
from pathlib import Path
import shutil

# Получаем путь к папке, где находится build.spec
try:
    SPEC_DIR = Path(__spec__.origin).parent if hasattr(__spec__, 'origin') else Path.cwd()
except Exception:
    SPEC_DIR = Path.cwd()

if not SPEC_DIR or not SPEC_DIR.exists():
    SPEC_DIR = Path(os.getcwd())

print(f"SPEC_DIR: {SPEC_DIR}")

# Путь к папке с core (satcore) - поднимаемся на два уровня вверх
CORE_DIR = SPEC_DIR.parent.parent / "core"
if CORE_DIR.exists():
    print(f"CORE_DIR: {CORE_DIR}")
else:
    print(f"Предупреждение: core не найден по пути {CORE_DIR}")

# Определяем путь к папке с бинарниками ST-Link
STLINK_BIN_DIR = SPEC_DIR / "app_firmware_gitrepo" / "bin"

# Список бинарников для включения в сборку
bin_files = []
if STLINK_BIN_DIR.exists():
    for file in STLINK_BIN_DIR.iterdir():
        if file.is_file():
            bin_files.append((str(file), "bin"))
            print(f"Добавлен бинарник: {file.name}")
else:
    print(f"Предупреждение: папка с бинарниками не найдена: {STLINK_BIN_DIR}")

# Файлы данных (firmware_repositories.json)
datas = []
config_file = SPEC_DIR / "firmware_repositories.json"
if config_file.exists():
    datas.append((str(config_file), "."))
    print(f"Добавлен конфиг: {config_file.name}")
else:
    print(f"Предупреждение: файл конфигурации не найден: {config_file}")

# Добавляем весь core как данные
if CORE_DIR.exists():
    # Добавляем всю папку satcore в сборку
    satcore_dir = CORE_DIR / "satcore"
    if satcore_dir.exists():
        for file in satcore_dir.rglob('*.py'):
            # Сохраняем структуру папок
            rel_path = file.relative_to(CORE_DIR.parent)  # от packages/
            datas.append((str(file), str(rel_path.parent)))
            print(f"Добавлен core файл: {rel_path}")

# Анализ основного скрипта
a = Analysis(
    ['app_firmware_gitrepo/__main__.py'],
    pathex=[
        str(SPEC_DIR),
        str(CORE_DIR.parent),  # Добавляем packages в путь
        str(CORE_DIR),         # Добавляем core в путь
    ],
    binaries=bin_files,
    datas=datas,
    hiddenimports=[
        'app_firmware_gitrepo.plugin',
        'app_firmware_gitrepo.widget',
        'app_firmware_gitrepo.stlink_client',
        'app_firmware_gitrepo.github_release_manager',
        'satcore',
        'satcore.plugin',
        'satcore.discovery',
        'satcore.runtime',
        'satcore.serial_io',
        'satcore.process',
        'satcore.worker',
        'PySide6',
        'PySide6.QtCore',
        'PySide6.QtWidgets',
        'requests',
        'pyserial',
        'shutil',
        'zipfile',
        'hashlib',
        'json',
        're',
        'subprocess',
        'datetime',
        'typing',
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
)

# Создаем PYZ
pyz = PYZ(a.pure, a.zipped_data, cipher=None)

# Создаем исполняемый файл
exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='app_firmware_gitrepo',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=True,
    disable_windowed_traceback=False,
    argv_emulation=False,
    cofile=None,
    icon=None,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)

# Копируем бинарники в папку dist/bin
dist_dir = Path('dist')
dist_dir.mkdir(exist_ok=True)

if STLINK_BIN_DIR.exists():
    dest_bin_dir = dist_dir / 'bin'
    dest_bin_dir.mkdir(exist_ok=True)
    
    for file in STLINK_BIN_DIR.iterdir():
        if file.is_file():
            shutil.copy2(file, dest_bin_dir / file.name)
            print(f"Скопирован бинарник в dist/bin/: {file.name}")
else:
    print("Предупреждение: бинарники не скопированы (папка bin не найдена)")