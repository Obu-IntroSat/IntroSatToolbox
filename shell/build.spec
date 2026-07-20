# PyInstaller spec to build the COMBINED launcher (all installed apps as tabs).
# Build with:  pyinstaller shell/build.spec
#
# The launcher finds apps through entry point metadata, so that metadata must be
# bundled. List every app distribution you want included below.
from PyInstaller.utils.hooks import collect_submodules, copy_metadata
import os

block_cipher = None

SPEC_DIR = os.path.dirname(os.path.abspath(SPEC))
PACKAGES = os.path.abspath(os.path.join(SPEC_DIR, "..", "packages"))

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

pathex = [
    PACKAGES,
    os.path.join(PACKAGES, "core"),
    SPEC_DIR,
]

datas = []
hiddenimports = []

# CRITICAL: Add metadata for each distribution (includes entry points)
for dist in APP_DISTRIBUTIONS:
    metadata = copy_metadata(dist)
    datas += metadata
    print(f"[build.spec] Added metadata for: {dist} ({len(metadata)} files)")

# Add submodules for each package
for pkg in APP_PACKAGES:
    hiddenimports += collect_submodules(pkg)
    print(f"[build.spec] Added submodules for: {pkg}")

hiddenimports += collect_submodules('satcore')
print("[build.spec] Added satcore submodules")

# Add satcore source files
try:
    import satcore
    satcore_path = os.path.dirname(satcore.__file__)
    if os.path.exists(satcore_path):
        for root, dirs, files in os.walk(satcore_path):
            for file in files:
                if file.endswith('.py'):
                    full_path = os.path.join(root, file)
                    rel_path = os.path.relpath(full_path, PACKAGES)
                    datas.append((full_path, os.path.dirname(rel_path)))
        print("[build.spec] Added satcore files to datas")
except Exception as e:
    print(f"[build.spec] Warning: Could not add satcore: {e}")

# Add app source files
for pkg in APP_PACKAGES:
    pkg_internal_dir = os.path.join(PACKAGES, pkg, pkg)
    if os.path.exists(pkg_internal_dir):
        for root, dirs, files in os.walk(pkg_internal_dir):
            for file in files:
                if file.endswith('.py'):
                    full_path = os.path.join(root, file)
                    rel_path = os.path.relpath(full_path, PACKAGES)
                    datas.append((full_path, os.path.dirname(rel_path)))
                    print(f"[build.spec] Added app file: {rel_path}")
    else:
        print(f"[build.spec] Warning: internal package not found at {pkg_internal_dir}")

# Also add .egg-info directories explicitly (they contain entry_points.txt)
for pkg in APP_PACKAGES:
    egg_info_dir = os.path.join(PACKAGES, pkg, f"{pkg}.egg-info")
    if os.path.exists(egg_info_dir):
        for root, dirs, files in os.walk(egg_info_dir):
            for file in files:
                full_path = os.path.join(root, file)
                rel_path = os.path.relpath(full_path, PACKAGES)
                datas.append((full_path, os.path.dirname(rel_path)))
                print(f"[build.spec] Added egg-info: {rel_path}")
    else:
        print(f"[build.spec] Warning: egg-info not found at {egg_info_dir}")

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
    console=True,
)