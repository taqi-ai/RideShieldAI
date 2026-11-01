# -*- mode: python ; coding: utf-8 -*-
# Builds the Windows desktop app. From the repository root:
#
#   .venv\Scripts\python.exe -m pip install pyinstaller
#   .venv\Scripts\python.exe -m PyInstaller packaging\RideShield.spec --noconfirm
#
# Output: dist\RideShield\RideShield.exe (a folder, zipped for distribution by packaging\build_windows.ps1).
# Only the files listed in `datas` are bundled. assets\captures (saved snapshots) and database\*.db are
# never bundled: they can hold photos of people and personal event history.
import os
from PyInstaller.utils.hooks import collect_all

ROOT = os.path.abspath(os.path.join(SPECPATH, '..'))

datas = [
    (os.path.join(ROOT, 'assets', 'Bike.png'), 'assets'),
    (os.path.join(ROOT, 'assets', 'Helmet.png'), 'assets'),
    (os.path.join(ROOT, 'assets', 'styles.qss'), 'assets'),
    (os.path.join(ROOT, 'assets', 'brand'), os.path.join('assets', 'brand')),
    (os.path.join(ROOT, 'assets', 'fonts'), os.path.join('assets', 'fonts')),
    (os.path.join(ROOT, 'models', 'helmet_yolo26n.pt'), 'models'),
    (os.path.join(ROOT, 'models', 'best.pt'), 'models'),
    (os.path.join(ROOT, 'models', 'yolo11m.pt'), 'models'),
]
binaries = []
hiddenimports = []

# Ultralytics ships YAML configs and data files that are read at runtime.
d, b, h = collect_all('ultralytics')
datas += d
binaries += b
hiddenimports += h

a = Analysis(
    [os.path.join(ROOT, 'main.py')],
    pathex=[ROOT],
    binaries=binaries,
    datas=datas,
    hiddenimports=hiddenimports,
    hookspath=[],
    runtime_hooks=[],
    excludes=['tkinter', 'IPython', 'jupyter', 'notebook', 'pytest', 'sphinx', 'tensorboard', 'polars', 'onnxruntime'],
    noarchive=False,
    # PyTorch inspects and generates code at import time, so its modules ship as real .py files.
    module_collection_mode={'torch': 'py', 'torchvision': 'py'},
)
pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='RideShield',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=False,
    console=False,
    icon=os.path.join(ROOT, 'packaging', 'RideShield.ico'),
)

coll = COLLECT(
    exe,
    a.binaries,
    a.datas,
    strip=False,
    upx=False,
    name='RideShield',
)
