#!/usr/bin/env python3
"""PyInstaller Specification."""
# Run `pyinstaller pyinstaller.spec` to generate the binary.

block_cipher = None

a = Analysis(
    ["main.py"],
    pathex=["dotgit_sync"],
    binaries=[],
    datas=[
        ("dotgit_sync/migrations", "dotgit_sync/schemas"),
        ("dotgit_sync/schemas", "dotgit_sync/schemas"),
        ("dotgit_sync/templates", "dotgit_sync/templates"),
        ("dotgit_sync/utils", "dotgit_sync/utils"),
        ("LICENSE*", "."),
        ("README.md", "."),
        ("CHANGELOG.md", "."),
        ("AUTHORS", "."),
    ],
    hiddenimports=[],
    hookspath=[],
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
    name="dotgit-sync",
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=True,
)

# vim: ft=python
