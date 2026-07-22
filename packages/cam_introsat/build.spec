# PyInstaller spec for the cam_introsat application.
# Build with:  pyinstaller build.spec

from PyInstaller.utils.hooks import collect_submodules

block_cipher = None

a = Analysis(
    ["cam_introsat/__main__.py"],
    pathex=['.', '../core'],                # чтобы PyInstaller нашёл satcore при анализе
    binaries=[],
    datas=[],
    hiddenimports=collect_submodules('cam_introsat') + collect_submodules('satcore'),  # добавили satcore
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
    name="cam-introsat",
    console=False,
)