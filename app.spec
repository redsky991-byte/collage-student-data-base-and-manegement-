# app.spec – PyInstaller build specification for College Management System
#
# Usage (from the project root):
#   pip install pyinstaller
#   pyinstaller app.spec
#
# The generated .exe will be in the  dist/CollegeManagement/  folder.
# ─────────────────────────────────────────────────────────────────────────────

import sys
import os

block_cipher = None

# Collect all application .py modules
added_files = [
    # Include any extra data files here if needed, e.g.:
    # ('assets', 'assets'),
]

a = Analysis(
    ['main.py'],
    pathex=[os.path.abspath('.')],
    binaries=[],
    datas=added_files,
    hiddenimports=[
        # tkinter sub-modules that PyInstaller sometimes misses
        'tkinter',
        'tkinter.ttk',
        'tkinter.messagebox',
        'tkinter.filedialog',
        'tkinter.font',
        # application modules
        'database',
        'utils',
        'dashboard_frame',
        'students_frame',
        'fees_frame',
        'salary_frame',
        'invoices_frame',
        'settings_frame',
        # stdlib modules that may need explicit inclusion
        'sqlite3',
        'datetime',
        'os',
        'sys',
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[
        # Exclude heavy packages not used by this app
        'numpy',
        'pandas',
        'matplotlib',
        'scipy',
        'PIL',
        'cv2',
        'PyQt5',
        'wx',
    ],
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
    console=False,           # No black console window – GUI only
    disable_windowed_traceback=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    # icon='assets/icon.ico',   # Uncomment and set path to add a custom icon
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
