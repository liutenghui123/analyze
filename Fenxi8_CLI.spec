# -*- mode: python ; coding: utf-8 -*-
import os
SPEC_DIR = os.path.dirname(os.path.abspath(SPEC))
block_cipher = None

a = Analysis(
    ['main.py'],  # CLI版本作为主入口
    pathex=[],
    binaries=[],
    datas=[
        ('assets', 'assets'),  # 包含ECharts库
        ('README.md', '.'),    # 包含帮助文档
    ],
    hiddenimports=[
        'pandas',
        'numpy',
        'requests',
    ],
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
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='Fenxi8_CLI',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=True,  # CLI模式，显示控制台
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=os.path.join(SPEC_DIR, 'assets', 'logo.ico'),
)
