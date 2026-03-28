# -*- mode: python ; coding: utf-8 -*-
#
# PyInstaller spec for College Management System
# Build with:  pyinstaller college_mgmt.spec
#
# Output:  dist/CollegeManagement/CollegeManagement.exe  (Windows)
#          dist/CollegeManagement/CollegeManagement       (Linux/macOS)
#
# The resulting folder (dist/CollegeManagement/) is fully self-contained.
# Copy it anywhere and run CollegeManagement.exe – no Python required.

import os
from PyInstaller.utils.hooks import collect_data_files, collect_submodules

block_cipher = None

# ── Collect dynamic data files needed by Flask / SQLAlchemy ─────────────────
added_datas = [
    # App templates & static assets
    ('templates', 'templates'),
    ('static',    'static'),
]
added_datas += collect_data_files('flask')
added_datas += collect_data_files('flask_sqlalchemy')
added_datas += collect_data_files('sqlalchemy')
added_datas += collect_data_files('jinja2')
added_datas += collect_data_files('markupsafe')

# ── Hidden imports that PyInstaller's static analysis may miss ───────────────
hidden_imports = [
    'flask',
    'flask_sqlalchemy',
    'sqlalchemy',
    'sqlalchemy.dialects.sqlite',
    'sqlalchemy.orm',
    'sqlalchemy.event',
    'sqlalchemy.pool',
    'jinja2',
    'markupsafe',
    'werkzeug',
    'werkzeug.routing',
    'werkzeug.serving',
    'werkzeug.exceptions',
    'werkzeug.middleware.shared_data',
    'PIL',
    'PIL.Image',
    'click',
    'itsdangerous',
    'email.mime.text',
    'email.mime.multipart',
    'pkg_resources',
    'pkg_resources.py2_warn',
]
hidden_imports += collect_submodules('sqlalchemy')
hidden_imports += collect_submodules('werkzeug')

a = Analysis(
    ['app.py'],
    pathex=[os.path.abspath('.')],
    binaries=[],
    datas=added_datas,
    hiddenimports=hidden_imports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=['tkinter', 'matplotlib', 'numpy', 'pandas', 'scipy', 'IPython'],
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
    name='CollegeManagement',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False,          # No terminal window; app opens silently in browser
    disable_windowed_traceback=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=None,              # Replace with 'icon.ico' if you have one
)

coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='CollegeManagement',
)
