"""
build.py – one-command build script for College Management System
=================================================================
Run on Windows:
    python build.py

Run on Linux / macOS:
    python3 build.py

The finished, self-contained application folder is placed in:
    dist/CollegeManagement/

To distribute:  zip that folder and send it.
To run:         double-click  dist/CollegeManagement/CollegeManagement.exe
                (Windows) or  ./dist/CollegeManagement/CollegeManagement  (Linux/macOS)
"""

import subprocess
import sys
import os
import shutil


def run(cmd):
    print(f"\n>>> {' '.join(cmd)}\n")
    result = subprocess.run(cmd, check=True)
    return result


def main():
    # 1. Install / upgrade PyInstaller
    run([sys.executable, '-m', 'pip', 'install', '--upgrade', 'pyinstaller'])

    # 2. Install runtime requirements
    run([sys.executable, '-m', 'pip', 'install', '-r', 'requirements.txt'])

    # 3. Clean previous build artefacts
    for folder in ('build', os.path.join('dist', 'CollegeManagement')):
        if os.path.exists(folder):
            print(f'Removing {folder}...')
            shutil.rmtree(folder)

    # 4. Run PyInstaller with the spec file
    run([sys.executable, '-m', 'PyInstaller', '--clean', 'college_mgmt.spec'])

    dist_dir = os.path.join('dist', 'CollegeManagement')
    print('\n' + '=' * 60)
    print('Build complete!')
    print(f'Output folder : {os.path.abspath(dist_dir)}')
    if sys.platform == 'win32':
        print('Run the app   : dist\\CollegeManagement\\CollegeManagement.exe')
    else:
        print('Run the app   : ./dist/CollegeManagement/CollegeManagement')
    print('=' * 60)


if __name__ == '__main__':
    main()
