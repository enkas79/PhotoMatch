# -*- mode: python ; coding: utf-8 -*-
# Build PyInstaller: python -m PyInstaller build.spec

a = Analysis(
    ["photomatch/__main__.py"],
    pathex=["."],
    binaries=[],
    datas=[("docs/GUIDA.md", "docs")],
    hiddenimports=["PIL.ExifTags.BaseExif"],
    hookspath=[],
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
    name="PhotoMatch",
    icon="assets/icon.ico",
    console=False,          # app windowed, niente console
    disable_windowed_traceback=False,
    upx=True,
)
