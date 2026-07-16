# PyInstaller spec to build the COMBINED launcher (all installed apps as tabs).
# Build with:  pyinstaller shell/build.spec
#
# The launcher finds apps through entry point metadata, so that metadata must be
# bundled. List every app distribution you want included below.
from PyInstaller.utils.hooks import collect_submodules, copy_metadata
from pathlib import Path
import os

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
    print(f"[build.spec] Added metadata for: {dist}")

for pkg in APP_PACKAGES:
    hiddenimports += collect_submodules(pkg)
    print(f"[build.spec] Added submodules for: {pkg}")

hiddenimports += collect_submodules('satcore')
print("[build.spec] Added satcore submodules")

try:
    import satcore
    satcore_path = Path(satcore.__file__).parent
    if satcore_path.exists():
        for file in satcore_path.rglob('*.py'):
            datas.append((str(file), "satcore"))
        print("[build.spec] Added satcore files to datas")
except Exception as e:
    print(f"[build.spec] Warning: Could not add satcore: {e}")

spec_dir = Path(os.getcwd())
packages_dir = spec_dir.parent / "packages"

for pkg in APP_PACKAGES:
    pkg_dir = packages_dir / pkg / pkg
    if pkg_dir.exists():
        for file in pkg_dir.rglob('*.py'):
            datas.append((str(file), f"{pkg}"))
            print(f"[build.spec] Added app file: {file}")
    else:
        print(f"[build.spec] Warning: app package not found at {pkg_dir}")

for pkg in APP_PACKAGES:
    egg_info_path = packages_dir / pkg / f"{pkg}.egg-info"
    if egg_info_path.exists():
        for file in egg_info_path.rglob('*'):
            if file.is_file():
                datas.append((str(file), f"{pkg}.egg-info"))
                print(f"[build.spec] Added egg-info: {file}")
    else:
        print(f"[build.spec] Warning: egg-info not found for {pkg} at {egg_info_path}")

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
    console=True,
)