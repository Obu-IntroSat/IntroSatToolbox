# PyInstaller spec to build the COMBINED launcher (all installed apps as tabs).
# Build with:  pyinstaller shell/build.spec
#
# The launcher finds apps through entry point metadata, so that metadata must be
# bundled. Tab apps are discovered automatically from packages/*/pyproject.toml.
import os
import tomllib

from PyInstaller.utils.hooks import collect_submodules, copy_metadata

block_cipher = None

SPEC_DIR = os.path.dirname(os.path.abspath(SPEC))
PACKAGES = os.path.abspath(os.path.join(SPEC_DIR, "..", "packages"))

CORE_DISTRIBUTION = "satcore"
CORE_PACKAGE = "satcore"


def discover_tab_apps() -> list[tuple[str, str, str]]:
    """Return (distribution name, python package, source dir) for every tab app."""
    apps: list[tuple[str, str, str]] = []
    for name in sorted(os.listdir(PACKAGES)):
        pkg_dir = os.path.join(PACKAGES, name)
        if not os.path.isdir(pkg_dir) or name == "core":
            continue

        pyproject = os.path.join(pkg_dir, "pyproject.toml")
        if not os.path.isfile(pyproject):
            continue

        with open(pyproject, "rb") as f:
            data = tomllib.load(f)

        entry_points = data.get("project", {}).get("entry-points", {})
        tab_entry_points = entry_points.get("introsat.apps")
        if not tab_entry_points:
            continue

        dist_name = data["project"]["name"]
        first_target = next(iter(tab_entry_points.values()))
        pkg_module = first_target.split(":", 1)[0].split(".", 1)[0]
        apps.append((dist_name, pkg_module, pkg_dir))

    return apps


TAB_APPS = discover_tab_apps()
APP_DISTRIBUTIONS = [dist for dist, _, _ in TAB_APPS]
APP_PACKAGES = [pkg for _, pkg, _ in TAB_APPS]

ALL_DISTRIBUTIONS = [CORE_DISTRIBUTION, *APP_DISTRIBUTIONS]
ALL_PACKAGES = [CORE_PACKAGE, *APP_PACKAGES]

# Editable installs are not always visible to PyInstaller; point at sources directly.
pathex = [os.path.join(PACKAGES, "core"), *[pkg_dir for _, _, pkg_dir in TAB_APPS]]

datas = []
hiddenimports = []
for dist in ALL_DISTRIBUTIONS:
    datas += copy_metadata(dist)
for pkg in ALL_PACKAGES:
    hiddenimports += collect_submodules(pkg)

# === ADD ST-Link BINARIES ===
stlink_bin_path = os.path.join(PACKAGES, "app_firmware_gitrepo", "app_firmware_gitrepo", "bin")
binaries = []
if os.path.exists(stlink_bin_path):
    for file in os.listdir(stlink_bin_path):
        full_path = os.path.join(stlink_bin_path, file)
        if os.path.isfile(full_path):
            binaries.append((full_path, "bin"))
            print(f"[build.spec] Added ST-Link binary: {file}")
else:
    print(f"[build.spec] Warning: ST-Link binaries not found at {stlink_bin_path}")

a = Analysis(
    ["shell/main.py"],
    pathex=pathex,
    binaries=binaries,
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