@echo off
setlocal
title VoxCraft Studio - Launching...
cd /d "%~dp0"

echo =========================================================================
echo  VoxCraft Studio - Offline Neural Speech and Podcast Desktop Studio
echo =========================================================================
echo.

:: Ensure project root directory is added to PYTHONPATH
set "PYTHONPATH=%~dp0;%PYTHONPATH%"

python -c "import PySide6, onnxruntime, numpy" 2>nul
if %errorlevel% neq 0 (
    echo [!] Dependencies missing. Running automatic setup...
    call "%~dp0install.bat"
)

echo [*] Starting VoxCraft Studio Desktop Application...
python "%~dp0app\main.py"
if %errorlevel% neq 0 (
    echo [!] Desktop window could not open in native mode. Falling back to web mode...
    python "%~dp0app\main.py" --web
)
pause
