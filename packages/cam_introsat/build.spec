# PyInstaller spec for the cam_introsat application.
# Build with:  pyinstaller build.spec

from PyInstaller.utils.hooks import collect_submodules

block_cipher = None

a = Analysis(
    ["cam_introsat/__main__.py"],          # путь к точке входа
    pathex=[],
    binaries=[],
    datas=[],                              # можно добавить данные, например ('cam_introsat/configs/*', 'configs')
    hiddenimports=collect_submodules("cam_introsat"),  # собираем все подмодули
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
    name="cam-introsat",                   # имя исполняемого файла (без .exe на Windows)
    console=False,                         # если нужна консоль – поставьте True
)