# -*- mode: python ; coding: utf-8 -*-
import os
import sys
from PyInstaller.utils.hooks import collect_all, collect_submodules, collect_data_files

def collect_all_data(package_name):
    datas, binaries, hiddenimports = collect_all(package_name)
    return datas, binaries, hiddenimports

# Asosiy kutubxonalarni to'liq yig'ish
packages = [
    'streamlit', 
    'sentence_transformers', 
    'faster_whisper', 
    'faiss', 
    'torch', 
    'elevenlabs', 
    'requests',
    'onnxruntime',
    'transformers',
    'tokenizers',
    'numpy'
]

datas = [
    ('video_ai_search', 'video_ai_search'),
    ('.env', '.'),
    ('.streamlit/config.toml', '.streamlit')
]

binaries = []
hiddenimports = [
    'streamlit.web.cli',
    'speech_to_text',
    'video_processor',
    'semantic_search',
    'utils',
    'ai_labs_api',
    'dotenv',
    'sklearn.utils._cython_blas',
    'sklearn.neighbors.typedefs',
    'sklearn.neighbors.quad_tree',
    'sklearn.tree._utils',
]

for pkg in packages:
    d, b, h = collect_all(pkg)
    datas += d
    binaries += b
    hiddenimports += h

# Qo'shimcha yashirin modullar
hiddenimports += collect_submodules('streamlit')
hiddenimports += collect_submodules('transformers')

block_cipher = None

a = Analysis(
    ['run_app.py'],
    pathex=[os.getcwd()],
    binaries=binaries,
    datas=datas,
    hiddenimports=hiddenimports,
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

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='video_ai_search',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=True, # Xatoliklarni ko'rish uchun True
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)
coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='video_ai_search',
)
