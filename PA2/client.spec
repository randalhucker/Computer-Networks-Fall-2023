# -*- mode: python ; coding: utf-8 -*-
# File: scrapie.spec
# Description: PyInstaller spec file for Scrapie application
# Author: Randy Hucker
# Version: 1.0

a = Analysis(
    ['launch_client.py'],
    pathex=[],
    binaries=[],
    datas=[],
    hiddenimports=[],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
)
pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    [],
    name='client',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    app_name='Client',
    icon='client.ico',
    other_options={
        'pyinstaller': {
            'noconsole': False,  # Set to True for --noconsole
            'onefile': True,    # Set to True for --onefile
        }
    },
)
