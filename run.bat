@echo off
title VoxCraft Studio - Launching...
cd /d "%~dp0"

echo =========================================================================
echo  VoxCraft Studio - Offline Neural Speech & Podcast Desktop Studio
echo =========================================================================
echo.

python -c "import PySide6, onnxruntime, numpy" 2>nul
if %errorlevel% neq 0 (
    echo [!] Dependencies missing. Running automatic setup...
    call install.bat
)

echo [*] Starting VoxCraft Studio Desktop Application...
python app/main.py
if %errorlevel% neq 0 (
    echo [!] Desktop window could not open in native mode. Falling back to web mode...
    python app/main.py --web
)
pause
