# -*- mode: python ; coding: utf-8 -*-

from PyInstaller.utils.hooks import collect_submodules, collect_data_files

block_cipher = None

# Путь к корню монорепозитория (если build.spec лежит в packages/camera/)
# или укажите абсолютный путь, если структура иная.
pathex_extra = ['..']  # поднимаемся на уровень выше, чтобы найти core/satcore

a = Analysis(
    ["cam_introsat/__main__.py"],
    pathex=['.'] + pathex_extra,   # добавляем путь к родительской папке
    binaries=[],
    datas=[] + collect_data_files('satcore'),  # если satcore содержит свои data-файлы
    hiddenimports=collect_submodules('cam_introsat') + collect_submodules('satcore'),  # включаем всё из satcore
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
    console=False,   # True, если нужна консоль
    icon=None,
)