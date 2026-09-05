"""
VoxCraft Studio - Standalone Executable & Installer Packager
Automates bundling the application into a single distributable Windows executable using PyInstaller.
"""
import os
import sys
import shutil
import subprocess
from pathlib import Path

INSTALLER_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = INSTALLER_DIR.parent
APP_DIR = PROJECT_ROOT / "app"
DIST_DIR = PROJECT_ROOT / "dist"
BUILD_DIR = PROJECT_ROOT / "build"


def check_pyinstaller():
    """Verify PyInstaller is installed."""
    try:
        import PyInstaller
        return True
    except ImportError:
        print("Installing PyInstaller...")
        subprocess.run([sys.executable, "-m", "pip", "install", "pyinstaller"], check=True)
        return True


def build_app():
    """Bundle VoxCraft Studio into standalone executable."""
    print("=" * 60)
    print(" Building VoxCraft Studio Standalone Windows Executable...")
    print("=" * 60)

    check_pyinstaller()

    main_script = APP_DIR / "main.py"
    frontend_dir = APP_DIR / "frontend"

    # PyInstaller arguments
    cmd = [
        "pyinstaller",
        "--name=VoxCraftStudio",
        "--noconfirm",
        "--onedir",
        "--windowed",
        f"--add-data={frontend_dir};app/frontend",
        f"--paths={PROJECT_ROOT}",
        "--clean",
        str(main_script)
    ]

    print(f"Running build command: {' '.join(cmd)}")
    subprocess.run(cmd, cwd=str(PROJECT_ROOT), check=True)

    print("\n✓ Build Completed! Standalone executable located in:")
    print(f"  {DIST_DIR / 'VoxCraftStudio' / 'VoxCraftStudio.exe'}\n")


def build_installer_wizard():
    """Bundle Installer Wizard into standalone setup.exe."""
    print("=" * 60)
    print(" Building VoxCraft Setup Wizard Executable...")
    print("=" * 60)

    check_pyinstaller()

    wizard_script = INSTALLER_DIR / "installer_wizard.py"

    cmd = [
        "pyinstaller",
        "--name=VoxCraft_Setup",
        "--noconfirm",
        "--onefile",
        "--windowed",
        f"--paths={PROJECT_ROOT}",
        "--clean",
        str(wizard_script)
    ]

    print(f"Running command: {' '.join(cmd)}")
    subprocess.run(cmd, cwd=str(PROJECT_ROOT), check=True)

    print("\n✓ Setup Wizard Executable created in:")
    print(f"  {DIST_DIR / 'VoxCraft_Setup.exe'}\n")


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "wizard":
        build_installer_wizard()
    else:
        build_app()
