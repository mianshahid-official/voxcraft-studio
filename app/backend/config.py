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
    # Studio Multi-Lingual Core Package
    "kokoro-v0_19": {
        "engine": "kokoro",
        "name": "Studio Multi-Lingual Voice Pack (28 Voices)",
        "description": "Premium 24kHz ultra-HD neural voices featuring 28 expressive characters across US English, Hindi, Spanish, and French with dynamic voice blending.",
        "size_mb": 325,
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
                "filename": "voices-v1.0.bin",
                "target_dir": KOKORO_MODELS_DIR,
                "urls": [
                    "https://github.com/thewh1teagle/kokoro-onnx/releases/download/model-files-v1.0/voices-v1.0.bin",
                    "https://huggingface.co/hexgrad/Kokoro-82M/resolve/main/voices.bin",
                ],
                "size_mb": 14,
            },
        ],
    },
    # Offline Voice Packages
    "piper-en_US-libritts_r-medium": {
        "engine": "piper",
        "name": "US English Studio Broadcaster — LibriTTS",
        "description": "Extensive studio broadcast voice collection featuring diverse tonal registers and character variations.",
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
        "name": "US English Narrator — Lessac",
        "description": "Crisp, balanced American English female narration voice crafted for audiobooks and tutorials.",
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
        "name": "British English Narrator — Alan",
        "description": "Rich, authoritative British gentleman narrator voice with distinguished articulation.",
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
        "name": "Spanish Castilian Voice — Dave",
        "description": "Natural European Spanish male voice with energetic cadence and clean articulation.",
        "size_mb": 62,
        "files": [
            {
                "filename": "es_ES-davefx-medium.onnx",
                "target_dir": PIPER_MODELS_DIR,
                "urls": [
                    "https://huggingface.co/rhasspy/piper-voices/resolve/main/es/es_ES/davefx/medium/es_ES-davefx-medium.onnx"
                ],
                "size_mb": 60,
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
        "name": "French Parisian Voice — Siwis",
        "description": "Smooth, eloquent Parisian French female voice with natural cadence for audiobooks and media.",
        "size_mb": 64,
        "files": [
            {
                "filename": "fr_FR-siwis-medium.onnx",
                "target_dir": PIPER_MODELS_DIR,
                "urls": [
                    "https://huggingface.co/rhasspy/piper-voices/resolve/main/fr/fr_FR/siwis/medium/fr_FR-siwis-medium.onnx"
                ],
                "size_mb": 62,
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
    "piper-de_DE-thorsten-medium": {
        "engine": "piper",
        "name": "German Professional Voice — Thorsten",
        "description": "Deep, articulate Standard German male voice designed for presentations and narration.",
        "size_mb": 61,
        "files": [
            {
                "filename": "de_DE-thorsten-medium.onnx",
                "target_dir": PIPER_MODELS_DIR,
                "urls": [
                    "https://huggingface.co/rhasspy/piper-voices/resolve/main/de/de_DE/thorsten/medium/de_DE-thorsten-medium.onnx"
                ],
                "size_mb": 59,
            },
            {
                "filename": "de_DE-thorsten-medium.onnx.json",
                "target_dir": PIPER_MODELS_DIR,
                "urls": [
                    "https://huggingface.co/rhasspy/piper-voices/resolve/main/de/de_DE/thorsten/medium/de_DE-thorsten-medium.onnx.json"
                ],
                "size_mb": 2,
            },
        ],
    },
    "piper-it_IT-paola-medium": {
        "engine": "piper",
        "name": "Italian Expressive Voice — Paola",
        "description": "Warm, expressive Italian female voice crafted for dialogue and podcast narration.",
        "size_mb": 60,
        "files": [
            {
                "filename": "it_IT-paola-medium.onnx",
                "target_dir": PIPER_MODELS_DIR,
                "urls": [
                    "https://huggingface.co/rhasspy/piper-voices/resolve/main/it/it_IT/paola/medium/it_IT-paola-medium.onnx"
                ],
                "size_mb": 58,
            },
            {
                "filename": "it_IT-paola-medium.onnx.json",
                "target_dir": PIPER_MODELS_DIR,
                "urls": [
                    "https://huggingface.co/rhasspy/piper-voices/resolve/main/it/it_IT/paola/medium/it_IT-paola-medium.onnx.json"
                ],
                "size_mb": 2,
            },
        ],
    },
    "piper-pt_BR-faber-medium": {
        "engine": "piper",
        "name": "Portuguese Brazilian Voice — Faber",
        "description": "Clear Brazilian Portuguese narrator voice with natural intonation.",
        "size_mb": 63,
        "files": [
            {
                "filename": "pt_BR-faber-medium.onnx",
                "target_dir": PIPER_MODELS_DIR,
                "urls": [
                    "https://huggingface.co/rhasspy/piper-voices/resolve/main/pt/pt_BR/faber/medium/pt_BR-faber-medium.onnx"
                ],
                "size_mb": 61,
            },
            {
                "filename": "pt_BR-faber-medium.onnx.json",
                "target_dir": PIPER_MODELS_DIR,
                "urls": [
                    "https://huggingface.co/rhasspy/piper-voices/resolve/main/pt/pt_BR/faber/medium/pt_BR-faber-medium.onnx.json"
                ],
                "size_mb": 2,
            },
        ],
    },
    # Neural Voice Cloning System
    "f5-tts-base": {
        "engine": "f5_tts",
        "name": "Neural Voice Cloning Package",
        "description": "Advanced acoustic flow-matching neural package enabling instant 1-click voice cloning from any reference audio clip.",
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
