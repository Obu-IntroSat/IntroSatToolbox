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

for dist in APP_DISTRIBUTIONS:
    datas += copy_metadata(dist)
    print(f"[build.spec] Added metadata for: {dist}")

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
    pkg_dir = os.path.join(PACKAGES, pkg)
    if os.path.exists(pkg_dir):
        for root, dirs, files in os.walk(pkg_dir):
            for file in files:
                if file.endswith('.py'):
                    full_path = os.path.join(root, file)
                    rel_path = os.path.relpath(full_path, PACKAGES)
                    datas.append((full_path, os.path.dirname(rel_path)))
                    print(f"[build.spec] Added app file: {rel_path}")
    else:
        print(f"[build.spec] Warning: package not found at {pkg_dir}")

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