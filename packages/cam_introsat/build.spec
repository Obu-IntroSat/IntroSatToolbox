from PyInstaller.utils.hooks import collect_submodules

block_cipher = None

a = Analysis(
    ['cam_introsat/__main__.py'],
    pathex=['.'],
    binaries=[],
    datas=[],
    hiddenimports=collect_submodules('cam_introsat') + ['satcore'],  # или collect_submodules('satcore')
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
    console=True,   # пока True для отладки
    upx=True,
    strip=False,
    debug=False,
)