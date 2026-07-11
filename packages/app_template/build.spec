# PyInstaller spec to build ONLY the template app.
# Build with:  pyinstaller packages/app_template/build.spec
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
    *collect_submodules("app_template"),
]

a = Analysis(
    ["app_template/__main__.py"],
    pathex=pathex,
    binaries=[],
    datas=copy_metadata("satcore") + copy_metadata("app-template"),
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
    name="app-template",
    console=False,
)
