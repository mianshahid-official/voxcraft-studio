"""
VoxCraft Studio - Configuration & Path Management
"""
from pathlib import Path
import os
import sys

# Base Application Directories
BASE_DIR = Path(__file__).resolve().parent.parent.parent
APP_DIR = BASE_DIR / "app"
BACKEND_DIR = APP_DIR / "backend"
FRONTEND_DIR = APP_DIR / "frontend"

# User Data & Storage Directories
MODELS_DIR = BASE_DIR / "models"
KOKORO_MODELS_DIR = MODELS_DIR / "kokoro"
PIPER_MODELS_DIR = MODELS_DIR / "piper"
F5_MODELS_DIR = MODELS_DIR / "f5_tts"

EXPORTS_DIR = BASE_DIR / "exports"
SAMPLES_DIR = BASE_DIR / "samples"
DATA_DIR = BASE_DIR / "data"

# Ensure essential directories exist
for directory in [
    MODELS_DIR,
    KOKORO_MODELS_DIR,
    PIPER_MODELS_DIR,
    F5_MODELS_DIR,
    EXPORTS_DIR,
    SAMPLES_DIR,
    DATA_DIR,
]:
    directory.mkdir(parents=True, exist_ok=True)

# Audio Standards
DEFAULT_SAMPLE_RATE = 24000
KOKORO_SAMPLE_RATE = 24000
PIPER_SAMPLE_RATE = 22050
F5_SAMPLE_RATE = 24000

# Remote Official Model Sources (Offline Downloader Manifest)
MODEL_DOWNLOAD_MANIFEST = {
    # Kokoro ONNX Models & Voice Embeddings
    "kokoro-v0_19": {
        "engine": "kokoro",
        "name": "Kokoro TTS v0.19 (ONNX)",
        "description": "High quality 82M param lightweight TTS model (English, Spanish, French, Japanese, Mandarin, etc.)",
        "size_mb": 310,
        "files": [
            {
                "filename": "kokoro-v0_19.onnx",
                "target_dir": KOKORO_MODELS_DIR,
                "urls": [
                    "https://github.com/thewh1teagle/kokoro-onnx/releases/download/model-files/kokoro-v0_19.onnx",
                    "https://huggingface.co/hexgrad/Kokoro-82M/resolve/main/kokoro-v0_19.onnx",
                ],
                "size_mb": 310,
            },
            {
                "filename": "voices.bin",
                "target_dir": KOKORO_MODELS_DIR,
                "urls": [
                    "https://github.com/thewh1teagle/kokoro-onnx/releases/download/model-files/voices.bin",
                    "https://huggingface.co/hexgrad/Kokoro-82M/resolve/main/voices.bin",
                ],
                "size_mb": 28,
            },
            {
                "filename": "voices.json",
                "target_dir": KOKORO_MODELS_DIR,
                "urls": [
                    "https://github.com/thewh1teagle/kokoro-onnx/releases/download/model-files/voices.json",
                    "https://huggingface.co/hexgrad/Kokoro-82M/resolve/main/voices.json",
                ],
                "size_mb": 1,
            },
        ],
    },
    "kokoro-v1_0": {
        "engine": "kokoro",
        "name": "Kokoro TTS v1.0 (ONNX Enhanced)",
        "description": "Latest release of Kokoro TTS with expanded multi-lingual voices and improved prosody",
        "size_mb": 320,
        "files": [
            {
                "filename": "kokoro-v1.0.onnx",
                "target_dir": KOKORO_MODELS_DIR,
                "urls": [
                    "https://github.com/thewh1teagle/kokoro-onnx/releases/download/model-files-v1.0/kokoro-v1.0.onnx",
                    "https://huggingface.co/hexgrad/Kokoro-82M/resolve/main/kokoro-v1.0.onnx",
                ],
                "size_mb": 320,
            },
            {
                "filename": "voices-v1.0.bin",
                "target_dir": KOKORO_MODELS_DIR,
                "urls": [
                    "https://github.com/thewh1teagle/kokoro-onnx/releases/download/model-files-v1.0/voices-v1.0.bin",
                    "https://huggingface.co/hexgrad/Kokoro-82M/resolve/main/voices-v1.0.bin",
                ],
                "size_mb": 32,
            },
        ],
    },
    # Piper Neural Voices (Curated Popular Packs)
    "piper-en_US-libritts_r-medium": {
        "engine": "piper",
        "name": "Piper English (US) - LibriTTS-R Studio Multi-Speaker",
        "description": "Studio quality US English with over 900 distinctive speaker voices",
        "size_mb": 65,
        "files": [
            {
                "filename": "en_US-libritts_r-medium.onnx",
                "target_dir": PIPER_MODELS_DIR,
                "urls": [
                    "https://huggingface.co/rhasspy/piper-voices/resolve/main/en/en_US/libritts_r/medium/en_US-libritts_r-medium.onnx"
                ],
                "size_mb": 63,
            },
            {
                "filename": "en_US-libritts_r-medium.onnx.json",
                "target_dir": PIPER_MODELS_DIR,
                "urls": [
                    "https://huggingface.co/rhasspy/piper-voices/resolve/main/en/en_US/libritts_r/medium/en_US-libritts_r-medium.onnx.json"
                ],
                "size_mb": 2,
            },
        ],
    },
    "piper-en_US-lessac-medium": {
        "engine": "piper",
        "name": "Piper English (US) - Lessac Clean Narrator",
        "description": "Clear, crisp, articulate female narration voice ideal for audiobooks and podcasts",
        "size_mb": 58,
        "files": [
            {
                "filename": "en_US-lessac-medium.onnx",
                "target_dir": PIPER_MODELS_DIR,
                "urls": [
                    "https://huggingface.co/rhasspy/piper-voices/resolve/main/en/en_US/lessac/medium/en_US-lessac-medium.onnx"
                ],
                "size_mb": 56,
            },
            {
                "filename": "en_US-lessac-medium.onnx.json",
                "target_dir": PIPER_MODELS_DIR,
                "urls": [
                    "https://huggingface.co/rhasspy/piper-voices/resolve/main/en/en_US/lessac/medium/en_US-lessac-medium.onnx.json"
                ],
                "size_mb": 2,
            },
        ],
    },
    "piper-en_GB-alan-medium": {
        "engine": "piper",
        "name": "Piper English (GB) - Alan British Narrator",
        "description": "Warm, refined British male voice with natural intonation",
        "size_mb": 60,
        "files": [
            {
                "filename": "en_GB-alan-medium.onnx",
                "target_dir": PIPER_MODELS_DIR,
                "urls": [
                    "https://huggingface.co/rhasspy/piper-voices/resolve/main/en/en_GB/alan/medium/en_GB-alan-medium.onnx"
                ],
                "size_mb": 58,
            },
            {
                "filename": "en_GB-alan-medium.onnx.json",
                "target_dir": PIPER_MODELS_DIR,
                "urls": [
                    "https://huggingface.co/rhasspy/piper-voices/resolve/main/en/en_GB/alan/medium/en_GB-alan-medium.onnx.json"
                ],
                "size_mb": 2,
            },
        ],
    },
    "piper-es_ES-davefx-medium": {
        "engine": "piper",
        "name": "Piper Spanish (ES) - Davefx Male Voice",
        "description": "Natural European Spanish male voice for dialogue and tutorials",
        "size_mb": 58,
        "files": [
            {
                "filename": "es_ES-davefx-medium.onnx",
                "target_dir": PIPER_MODELS_DIR,
                "urls": [
                    "https://huggingface.co/rhasspy/piper-voices/resolve/main/es/es_ES/davefx/medium/es_ES-davefx-medium.onnx"
                ],
                "size_mb": 56,
            },
            {
                "filename": "es_ES-davefx-medium.onnx.json",
                "target_dir": PIPER_MODELS_DIR,
                "urls": [
                    "https://huggingface.co/rhasspy/piper-voices/resolve/main/es/es_ES/davefx/medium/es_ES-davefx-medium.onnx.json"
                ],
                "size_mb": 2,
            },
        ],
    },
    "piper-fr_FR-siwis-medium": {
        "engine": "piper",
        "name": "Piper French (FR) - Siwis Female Voice",
        "description": "Smooth, professional Parisian French female voice",
        "size_mb": 62,
        "files": [
            {
                "filename": "fr_FR-siwis-medium.onnx",
                "target_dir": PIPER_MODELS_DIR,
                "urls": [
                    "https://huggingface.co/rhasspy/piper-voices/resolve/main/fr/fr_FR/siwis/medium/fr_FR-siwis-medium.onnx"
                ],
                "size_mb": 60,
            },
            {
                "filename": "fr_FR-siwis-medium.onnx.json",
                "target_dir": PIPER_MODELS_DIR,
                "urls": [
                    "https://huggingface.co/rhasspy/piper-voices/resolve/main/fr/fr_FR/siwis/medium/fr_FR-siwis-medium.onnx.json"
                ],
                "size_mb": 2,
            },
        ],
    },
    "piper-de_DE-eva_k-medium": {
        "engine": "piper",
        "name": "Piper German (DE) - Eva K Female Voice",
        "description": "Clear standard German female voice",
        "size_mb": 58,
        "files": [
            {
                "filename": "de_DE-eva_k-medium.onnx",
                "target_dir": PIPER_MODELS_DIR,
                "urls": [
                    "https://huggingface.co/rhasspy/piper-voices/resolve/main/de/de_DE/eva_k/medium/de_DE-eva_k-medium.onnx"
                ],
                "size_mb": 56,
            },
            {
                "filename": "de_DE-eva_k-medium.onnx.json",
                "target_dir": PIPER_MODELS_DIR,
                "urls": [
                    "https://huggingface.co/rhasspy/piper-voices/resolve/main/de/de_DE/eva_k/medium/de_DE-eva_k-medium.onnx.json"
                ],
                "size_mb": 2,
            },
        ],
    },
    # F5-TTS Voice Cloning Flow Matching Model
    "f5-tts-base": {
        "engine": "f5_tts",
        "name": "F5-TTS Base Zero-Shot Voice Cloning Model",
        "description": "State-of-the-art flow matching voice cloning model with Vocos vocoder (~1.2GB)",
        "size_mb": 1250,
        "files": [
            {
                "filename": "model_1200000.safetensors",
                "target_dir": F5_MODELS_DIR,
                "urls": [
                    "https://huggingface.co/SWivid/F5-TTS/resolve/main/F5TTS_Base/model_1200000.safetensors"
                ],
                "size_mb": 1180,
            },
            {
                "filename": "vocab.txt",
                "target_dir": F5_MODELS_DIR,
                "urls": [
                    "https://huggingface.co/SWivid/F5-TTS/resolve/main/F5TTS_Base/vocab.txt"
                ],
                "size_mb": 1,
            },
        ],
    },
}
