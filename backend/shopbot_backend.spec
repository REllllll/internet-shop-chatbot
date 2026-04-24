# -*- mode: python ; coding: utf-8 -*-

from pathlib import Path

project_root = Path.cwd()
backend_root = project_root / "backend"

a = Analysis(
    [str(backend_root / "pyinstaller_entry.py")],
    pathex=[str(backend_root)],
    binaries=[],
    datas=[],
    hiddenimports=[
        "app.main",
        "app.chat",
        "app.db",
        "app.health",
        "app.internal",
        "app.mcp_tools",
        "uvicorn.logging",
        "uvicorn.loops",
        "uvicorn.loops.auto",
        "uvicorn.protocols",
        "uvicorn.protocols.http",
        "uvicorn.protocols.http.auto",
        "uvicorn.protocols.websockets",
        "uvicorn.protocols.websockets.auto",
        "uvicorn.lifespan",
        "uvicorn.lifespan.on",
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=["pytest"],
    noarchive=False,
)
pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name="shopbot-backend",
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=True,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)
coll = COLLECT(
    exe,
    a.binaries,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name="shopbot-backend",
)
