from PyInstaller.utils.hooks import collect_submodules

block_cipher = None

a = Analysis(
    ['cam_introsat/__main__.py'],
    pathex=['.'],                     # можно указать абсолютный путь к проекту
    binaries=[],
    datas=[],
    hiddenimports=collect_submodules('cam_introsat') + ['satcore'],
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
    name='cam-introsat',
    console=False,          # для отладки можно временно поставить True
    upx=True,               # если UPX установлен
    strip=False,
    debug=False,
)