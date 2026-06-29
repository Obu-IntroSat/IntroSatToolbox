# PyInstaller spec to build ONLY the COM interaction app.
# Build with:  pyinstaller packages/app_comms/build.spec
from PyInstaller.utils.hooks import collect_submodules

block_cipher = None

a = Analysis(
    ["app_comms/__main__.py"],
    pathex=[],
    binaries=[],
    datas=[],
    hiddenimports=collect_submodules("app_comms"),
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
