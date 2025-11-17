# -*- mode: python ; coding: utf-8 -*-

block_cipher = None

a = Analysis(
    ['taxon.py'],
    pathex=[],
    binaries=[],
    datas=[],
    hiddenimports=[
        'models.organizer',
        'models.rules',
        'utils.config_manager',
        'utils.file_utils',
        'typer',
        'rich',
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
    name='taxon',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=True,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)

# 注意：单文件模式不需要 COLLECT 步骤
# EXE 已经包含了所有必要的文件