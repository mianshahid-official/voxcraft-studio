@echo off
setlocal
title VoxCraft Studio - Environment and Model Installer
cd /d "%~dp0"

echo =========================================================================
echo  VoxCraft Studio - Automated Setup and Dependency Downloader
echo =========================================================================
echo.

:: Ensure project root directory is added to PYTHONPATH
set "PYTHONPATH=%~dp0;%PYTHONPATH%"

echo [*] Checking Python runtime...
python --version
if %errorlevel% neq 0 (
    echo [ERROR] Python is not found on your system PATH!
    echo Please install Python 3.10+ from https://www.python.org/
    echo Make sure to check the box "Add Python to PATH" during installation.
    pause
    exit /b 1
)

echo.
echo [*] Upgrading pip...
python -m pip install --upgrade pip

echo.
echo [*] Installing required Python packages for offline speech synthesis...
python -m pip install -r "%~dp0requirements.txt"

echo.
echo [*] Launching Setup and Model Downloader Wizard...
python "%~dp0installer\installer_wizard.py"

echo.
echo [✓] Setup finished! You can now start VoxCraft Studio at any time using run.bat
pause
