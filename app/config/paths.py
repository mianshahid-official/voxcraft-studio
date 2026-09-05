"""
TTS Studio / VoxCraft Studio - Configurable Application & Storage Paths
"""
import os
import sys
from pathlib import Path

# Application Base Directory
APP_ROOT = Path(__file__).resolve().parent.parent.parent
APP_SRC = APP_ROOT / "app"

# User Data & Storage (Defaults to local portable directory or AppData)
PORTABLE_MODE = (APP_ROOT / "portable.flag").exists()

if PORTABLE_MODE:
    USER_DATA_DIR = APP_ROOT / "data"
    MODELS_DIR = APP_ROOT / "models"
    EXPORTS_DIR = APP_ROOT / "exports"
    PROJECTS_DIR = APP_ROOT / "projects"
    LOGS_DIR = APP_ROOT / "logs"
    CACHE_DIR = APP_ROOT / "cache"
else:
    # Standard local project storage or Windows AppData
    USER_DATA_DIR = APP_ROOT / "data"
    MODELS_DIR = APP_ROOT / "models"
    EXPORTS_DIR = APP_ROOT / "exports"
    PROJECTS_DIR = APP_ROOT / "projects"
    LOGS_DIR = APP_ROOT / "logs"
    CACHE_DIR = APP_ROOT / "cache"

# Engine specific model subdirectories
KOKORO_DIR = MODELS_DIR / "kokoro"
PIPER_DIR = MODELS_DIR / "piper"
F5TTS_DIR = MODELS_DIR / "f5tts"
VOICE_PREVIEWS_DIR = USER_DATA_DIR / "previews"
REFERENCE_VOICES_DIR = USER_DATA_DIR / "reference_voices"

# Ensure directories exist
for directory in [
    USER_DATA_DIR,
    MODELS_DIR,
    EXPORTS_DIR,
    PROJECTS_DIR,
    LOGS_DIR,
    CACHE_DIR,
    KOKORO_DIR,
    PIPER_DIR,
    F5TTS_DIR,
    VOICE_PREVIEWS_DIR,
    REFERENCE_VOICES_DIR
]:
    directory.mkdir(parents=True, exist_ok=True)
