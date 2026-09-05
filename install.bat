@echo off
title VoxCraft Studio - Environment & Model Installer
cd /d "%~dp0"

echo =========================================================================
echo  VoxCraft Studio - Automated Setup & Dependency Downloader
echo =========================================================================
echo.
echo [*] Checking Python runtime...
python --version
if %errorlevel% neq 0 (
    echo [ERROR] Python is not found on your system PATH!
    echo Please install Python 3.10+ from https://www.python.org/
    pause
    exit /b 1
)

echo [*] Installing required Python packages for offline speech synthesis...
pip install -r requirements.txt

echo.
echo [*] Launching Setup & Model Downloader Wizard...
python installer/installer_wizard.py

echo.
echo [✓] Setup finished! You can now start VoxCraft Studio at any time using run.bat
pause
