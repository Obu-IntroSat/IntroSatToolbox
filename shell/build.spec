# PyInstaller spec to build the COMBINED launcher (all installed apps as tabs).
# Build with:  pyinstaller shell/build.spec
#
# The launcher finds apps through entry point metadata, so that metadata must be
# bundled. List every app distribution you want included below.
from PyInstaller.utils.hooks import collect_submodules, copy_metadata
from pathlib import Path
import os
import sys

block_cipher = None

# Apps to bundle into the combined executable.
APP_DISTRIBUTIONS = [
    "app-comms",
    "app-firmware",
    "app-template",
    "app-firmware-gitrepo",
]
APP_PACKAGES = [
    "app_comms",
    "app_firmware",
    "app_template",
    "app_firmware_gitrepo",
]

datas = []
hiddenimports = []

for dist in APP_DISTRIBUTIONS:
    datas += copy_metadata(dist)
for pkg in APP_PACKAGES:
    hiddenimports += collect_submodules(pkg)

# === ADD ST-Link BINARIES ===
# Search for binaries in multiple locations
possible_paths = [
    Path(os.getcwd()).parent / "packages" / "app_firmware_gitrepo" / "app_firmware_gitrepo" / "bin",
    Path(os.getcwd()) / "packages" / "app_firmware_gitrepo" / "app_firmware_gitrepo" / "bin",
    Path(os.getcwd()).parent.parent / "packages" / "app_firmware_gitrepo" / "app_firmware_gitrepo" / "bin",
]

STLINK_BIN_DIR = None
for path in possible_paths:
    if path.exists():
        STLINK_BIN_DIR = path
        break

stlink_binaries = []
if STLINK_BIN_DIR and STLINK_BIN_DIR.exists():
    for file in STLINK_BIN_DIR.iterdir():
        if file.is_file():
            stlink_binaries.append((str(file), "bin"))
            print(f"[build.spec] Added ST-Link binary: {file.name}")
else:
    print(f"[build.spec] WARNING: ST-Link binaries folder not found")

a = Analysis(
    ["shell/main.py"],
    pathex=[],
    binaries=stlink_binaries,
    datas=datas,
    hiddenimports=hiddenimports,
    hookspath=[],
    runtime_hooks=[],
    excludes=[],
    cipher=block_cipher,
)
pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    [],
    name="IntroSatToolbox",
    console=False,
)