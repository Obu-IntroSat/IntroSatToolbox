# PyInstaller spec to build the COMBINED launcher (all installed apps as tabs).
# Build with:  pyinstaller shell/build.spec
#
# The launcher finds apps through entry point metadata, so that metadata must be
# bundled. List every app distribution you want included below.
from PyInstaller.utils.hooks import collect_submodules, copy_metadata

block_cipher = None

# Apps to bundle into the combined executable.
APP_DISTRIBUTIONS = ["app-comms", "app-firmware", "app-template"]
APP_PACKAGES = ["app_comms", "app_firmware", "app_template"]

datas = []
hiddenimports = []
for dist in APP_DISTRIBUTIONS:
    datas += copy_metadata(dist)
for pkg in APP_PACKAGES:
    hiddenimports += collect_submodules(pkg)

a = Analysis(
    ["shell/main.py"],
    pathex=[],
    binaries=[],
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
