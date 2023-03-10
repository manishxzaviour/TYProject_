from kivy_deps import sdl2, glew
import numpy
import cv2
import requests
import math
import time
import json
	
# -*- mode: python ; coding: utf-8 -*-
	

block_cipher = None


a = Analysis(
    ['main.py'],
    pathex=['D:\\my stuff\\TYProject\\pythonProject'],
    binaries=[],
    datas=[('laraApp.kv','DATA'),('logo.png','DATA'),('logo2.png','DATA'),('config.json','DATA'),('play.png','DATA'),('pause.png','DATA'),('warning.png','DATA')],
    hiddenimports=[],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)
pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)


a.datas+=[('Code\laraApp.kv',"D:\\my stuff\\TYProject\\pythonProject\laraApp.kv",'DATA')]

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='Lara',
    debug=True,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)
coll = COLLECT(
    exe,
	Tree("D:\\my stuff\\TYProject\\pythonProject\\"),
    a.binaries,
    a.zipfiles,
    a.datas,
	*[Tree(p) for p in (sdl2.dep_bins + glew.dep_bins)],
    strip=False,
    upx=True,
    upx_exclude=[],
    name='main',
)
