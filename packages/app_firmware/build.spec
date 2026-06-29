# PyInstaller spec to build ONLY the firmware flashing app.
# Build with:  pyinstaller packages/app_firmware/build.spec
from PyInstaller.utils.hooks import collect_submodules

block_cipher = None

a = Analysis(
    ["app_firmware/__main__.py"],
    pathex=[],
    binaries=[],
    datas=[],
    hiddenimports=collect_submodules("app_firmware"),
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
    name="app-firmware",
    console=False,
)
