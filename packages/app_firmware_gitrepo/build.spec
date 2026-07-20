# -*- mode: python ; coding: utf-8 -*-

import sys
import os
from pathlib import Path
import shutil

# Используем SPEC переменную PyInstaller для получения правильного пути
SPEC_DIR = os.path.dirname(os.path.abspath(SPEC))
PACKAGES_DIR = os.path.abspath(os.path.join(SPEC_DIR, ".."))
CORE_DIR = os.path.join(PACKAGES_DIR, "core")
SATCORE_DIR = os.path.join(CORE_DIR, "satcore")
APP_DIR = os.path.join(PACKAGES_DIR, "app_firmware_gitrepo", "app_firmware_gitrepo")

print(f"SPEC_DIR: {SPEC_DIR}")
print(f"PACKAGES_DIR: {PACKAGES_DIR}")
print(f"CORE_DIR: {CORE_DIR}")
print(f"SATCORE_DIR: {SATCORE_DIR}")
print(f"APP_DIR: {APP_DIR}")

datas = []
if os.path.exists(SATCORE_DIR):
    for root, dirs, files in os.walk(SATCORE_DIR):
        for file in files:
            if file.endswith('.py'):
                full_path = os.path.join(root, file)
                rel_path = os.path.relpath(full_path, PACKAGES_DIR)
                datas.append((full_path, os.path.dirname(rel_path)))
                print(f"added: {rel_path}")

config_file = os.path.join(APP_DIR, "..", "firmware_repositories.json")
if os.path.exists(config_file):
    datas.append((config_file, "."))
    print(f"config added: {os.path.basename(config_file)}")

bin_files = []
STLINK_BIN_DIR = os.path.join(APP_DIR, "bin")
if os.path.exists(STLINK_BIN_DIR):
    for file in os.listdir(STLINK_BIN_DIR):
        full_path = os.path.join(STLINK_BIN_DIR, file)
        if os.path.isfile(full_path):
            bin_files.append((full_path, "bin"))
            print(f"bin files added: {file}")

a = Analysis(
    [os.path.join(APP_DIR, "__main__.py")],
    pathex=[
        PACKAGES_DIR,
        CORE_DIR,
        SPEC_DIR,
    ],
    binaries=bin_files,
    datas=datas,
    hiddenimports=[
        'satcore',
        'satcore.plugin',
        'satcore.discovery',
        'satcore.runtime',
        'satcore.serial_io',
        'satcore.process',
        'satcore.worker',
        'app_firmware_gitrepo',
        'app_firmware_gitrepo.plugin',
        'app_firmware_gitrepo.widget',
        'app_firmware_gitrepo.stlink_client',
        'app_firmware_gitrepo.github_release_manager',
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
        'pathlib',
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=None)

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

dist_dir = Path('dist')
dist_dir.mkdir(exist_ok=True)

if os.path.exists(STLINK_BIN_DIR):
    dest_bin_dir = dist_dir / 'bin'
    dest_bin_dir.mkdir(exist_ok=True)
    for file in os.listdir(STLINK_BIN_DIR):
        full_path = os.path.join(STLINK_BIN_DIR, file)
        if os.path.isfile(full_path):
            shutil.copy2(full_path, dest_bin_dir / file)