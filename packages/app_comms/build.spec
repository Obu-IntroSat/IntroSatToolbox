# PyInstaller spec to build ONLY the COM interaction app.
# Build with:  pyinstaller packages/app_comms/build.spec
import os

from PyInstaller.utils.hooks import collect_submodules, copy_metadata

block_cipher = None

SPEC_DIR = os.path.dirname(os.path.abspath(SPEC))
PACKAGES = os.path.abspath(os.path.join(SPEC_DIR, ".."))

pathex = [
    os.path.join(PACKAGES, "core"),
    SPEC_DIR,
]

hiddenimports = [
    *collect_submodules("satcore"),
    *collect_submodules("app_comms"),
]

a = Analysis(
    ["app_comms/__main__.py"],
    pathex=pathex,
    binaries=[],
    datas=copy_metadata("satcore") + copy_metadata("app-comms"),
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
    name="app-comms",
    console=False,
)
