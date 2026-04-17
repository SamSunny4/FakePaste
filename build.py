"""
FakePaste - Build Script
Builds standalone .exe using PyInstaller.
"""

import PyInstaller.__main__
import os
import sys

# Get project directory
project_dir = os.path.dirname(os.path.abspath(__file__))


def build():
    """Build the standalone executable."""
    args = [
        os.path.join(project_dir, 'main.py'),
        '--name=FakePaste',
        '--onefile',
        '--windowed',
        '--noconfirm',
        '--clean',
        f'--distpath={os.path.join(project_dir, "dist")}',
        f'--workpath={os.path.join(project_dir, "build")}',
        f'--specpath={project_dir}',
        # Hidden imports
        '--hidden-import=pynput.keyboard._win32',
        '--hidden-import=pynput.mouse._win32',
        '--hidden-import=pynput._util.win32',
        # Collect all needed modules
        '--collect-all=pynput',
    ]

    # Add icon if it exists
    icon_path = os.path.join(project_dir, 'assets', 'icon.ico')
    if os.path.exists(icon_path):
        args.append(f'--icon={icon_path}')

    print("=" * 60)
    print("  Building FakePaste Executable")
    print("=" * 60)
    print(f"\nProject: {project_dir}")
    print(f"Output:  {os.path.join(project_dir, 'dist', 'FakePaste.exe')}")
    print()

    PyInstaller.__main__.run(args)

    print()
    print("=" * 60)
    print("  Build Complete!")
    print(f"  EXE: {os.path.join(project_dir, 'dist', 'FakePaste.exe')}")
    print("=" * 60)


if __name__ == "__main__":
    build()
