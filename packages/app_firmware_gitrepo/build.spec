# -*- mode: python ; coding: utf-8 -*-

import sys
import os
from pathlib import Path
import shutil

SPEC_DIR = Path(os.getcwd())
print(f"SPEC_DIR: {SPEC_DIR}")


PACKAGES_DIR = SPEC_DIR.parent.parent / "packages"
CORE_DIR = PACKAGES_DIR / "core"
SATCORE_DIR = CORE_DIR / "satcore"
APP_DIR = SPEC_DIR / "app_firmware_gitrepo"

print(f"PACKAGES_DIR: {PACKAGES_DIR}")
print(f"CORE_DIR: {CORE_DIR}")
print(f"SATCORE_DIR: {SATCORE_DIR}")
print(f"APP_DIR: {APP_DIR}")


datas = []
if SATCORE_DIR.exists():
    for file in SATCORE_DIR.rglob('*.py'):
        rel_path = file.relative_to(CORE_DIR.parent)
        datas.append((str(file), str(rel_path.parent)))
        print(f"added: {rel_path}")


config_file = SPEC_DIR / "firmware_repositories.json"
if config_file.exists():
    datas.append((str(config_file), "."))
    print(f"config added: {config_file.name}")

#
bin_files = []
STLINK_BIN_DIR = APP_DIR / "bin"
if STLINK_BIN_DIR.exists():
    for file in STLINK_BIN_DIR.iterdir():
        if file.is_file():
            bin_files.append((str(file), "bin"))
            print(f"bin files added: {file.name}")


a = Analysis(
    [str(APP_DIR / "__main__.py")],
    pathex=[
        str(PACKAGES_DIR),
        str(CORE_DIR),
        str(SPEC_DIR),
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

if STLINK_BIN_DIR.exists():
    dest_bin_dir = dist_dir / 'bin'
    dest_bin_dir.mkdir(exist_ok=True)
    for file in STLINK_BIN_DIR.iterdir():
        if file.is_file():
            shutil.copy2(file, dest_bin_dir / file.name)