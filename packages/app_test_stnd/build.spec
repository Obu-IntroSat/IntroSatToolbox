# PyInstaller spec to build ONLY the template app.
# Build with:  pyinstaller packages/app_template/build.spec
from PyInstaller.utils.hooks import collect_submodules

block_cipher = None

a = Analysis(
    ["app_test_stnd/__main__.py"],
    pathex=[],
    binaries=[],
    datas=[],
    hiddenimports=collect_submodules("app_template"),
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
    name="app-test-stnd",
    console=False,
)
