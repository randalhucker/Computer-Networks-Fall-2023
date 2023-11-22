# -*- mode: python ; coding: utf-8 -*-
# File: launch_client.spec
# Description: PyInstaller spec file for Client application
# Author: Randy Hucker, Sam Graler, Steven Habra
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
    name='launch_client',
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
    icon='client.ico',
    app_name='Client',
    other_options={
        'pyinstaller': {
            'onefile': True,    # Set to True for --onefile
        }
    },
)
