# PyInstaller spec to build the COMBINED launcher (all installed apps as tabs).
# Build with:  pyinstaller shell/build.spec
#
# The launcher finds apps through entry point metadata, so that metadata must be
# bundled. List every app distribution you want included below.
import os

from PyInstaller.utils.hooks import collect_submodules, copy_metadata

block_cipher = None

SPEC_DIR = os.path.dirname(os.path.abspath(SPEC))
PACKAGES = os.path.abspath(os.path.join(SPEC_DIR, "..", "packages"))

CORE_DISTRIBUTION = "satcore"
CORE_PACKAGE = "satcore"

# Apps to bundle into the combined executable.
APP_DISTRIBUTIONS = ["app-comms", "app-firmware", "app-template"]
APP_PACKAGES = ["app_comms", "app_firmware", "app_template"]

ALL_DISTRIBUTIONS = [CORE_DISTRIBUTION, *APP_DISTRIBUTIONS]
ALL_PACKAGES = [CORE_PACKAGE, *APP_PACKAGES]

# Editable installs are not always visible to PyInstaller; point at sources directly.
pathex = [
    os.path.join(PACKAGES, "core"),
    os.path.join(PACKAGES, "app_comms"),
    os.path.join(PACKAGES, "app_firmware"),
    os.path.join(PACKAGES, "app_template"),
]

datas = []
hiddenimports = []
for dist in ALL_DISTRIBUTIONS:
    datas += copy_metadata(dist)
for pkg in ALL_PACKAGES:
    hiddenimports += collect_submodules(pkg)

a = Analysis(
    ["shell/main.py"],
    pathex=pathex,
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
