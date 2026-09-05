"""
TTS Studio - Download Manifest & Model Metadata Registry
"""
from pathlib import Path
from .paths import KOKORO_DIR, PIPER_DIR, F5TTS_DIR

MODEL_REGISTRY_MANIFEST = {
    # -------------------------------------------------------------
    # Kokoro-82M ONNX Package
    # -------------------------------------------------------------
    "kokoro-v0_19": {
        "engine": "kokoro",
        "name": "Engine 1: Kokoro-82M Studio Package (24kHz)",
        "version": "0.19",
        "description": "High-fidelity, ultra-fast 24kHz neural speech model with English, Spanish, French, Japanese, Mandarin voices",
        "size_mb": 310,
        "recommended": True,
        "files": [
            {
                "filename": "kokoro-v0_19.onnx",
                "target_dir": KOKORO_DIR,
                "size_mb": 310,
                "sha256": None,
                "urls": [
                    "https://github.com/thewh1teagle/kokoro-onnx/releases/download/model-files/kokoro-v0_19.onnx",
                    "https://huggingface.co/hexgrad/Kokoro-82M/resolve/main/kokoro-v0_19.onnx"
                ]
            },
            {
                "filename": "voices.bin",
                "target_dir": KOKORO_DIR,
                "size_mb": 28,
                "sha256": None,
                "urls": [
                    "https://github.com/thewh1teagle/kokoro-onnx/releases/download/model-files/voices.bin",
                    "https://huggingface.co/hexgrad/Kokoro-82M/resolve/main/voices.bin"
                ]
            },
            {
                "filename": "voices.json",
                "target_dir": KOKORO_DIR,
                "size_mb": 1,
                "sha256": None,
                "urls": [
                    "https://github.com/thewh1teagle/kokoro-onnx/releases/download/model-files/voices.json",
                    "https://huggingface.co/hexgrad/Kokoro-82M/resolve/main/voices.json"
                ]
            }
        ]
    },

    # -------------------------------------------------------------
    # Piper Neural Voice Packs
    # -------------------------------------------------------------
    "piper-en_US-lessac-medium": {
        "engine": "piper",
        "name": "Engine 2: Piper English — Lessac",
        "version": "1.0",
        "language": "English",
        "flag": "🇺🇸",
        "description": "Crisp, balanced American English female voice optimized for audiobooks & narration",
        "size_mb": 58,
        "recommended": True,
        "files": [
            {
                "filename": "en_US-lessac-medium.onnx",
                "target_dir": PIPER_DIR,
                "size_mb": 56,
                "sha256": None,
                "urls": [
                    "https://huggingface.co/rhasspy/piper-voices/resolve/main/en/en_US/lessac/medium/en_US-lessac-medium.onnx"
                ]
            },
            {
                "filename": "en_US-lessac-medium.onnx.json",
                "target_dir": PIPER_DIR,
                "size_mb": 2,
                "sha256": None,
                "urls": [
                    "https://huggingface.co/rhasspy/piper-voices/resolve/main/en/en_US/lessac/medium/en_US-lessac-medium.onnx.json"
                ]
            }
        ]
    },
    "piper-en_US-libritts_r-medium": {
        "engine": "piper",
        "name": "Engine 2: Piper English — LibriTTS Multi-Speaker",
        "version": "1.0",
        "language": "English",
        "flag": "🎧",
        "description": "Studio multi-speaker pack containing 900+ distinct speaker voices",
        "size_mb": 65,
        "recommended": False,
        "files": [
            {
                "filename": "en_US-libritts_r-medium.onnx",
                "target_dir": PIPER_DIR,
                "size_mb": 63,
                "sha256": None,
                "urls": [
                    "https://huggingface.co/rhasspy/piper-voices/resolve/main/en/en_US/libritts_r/medium/en_US-libritts_r-medium.onnx"
                ]
            },
            {
                "filename": "en_US-libritts_r-medium.onnx.json",
                "target_dir": PIPER_DIR,
                "size_mb": 2,
                "sha256": None,
                "urls": [
                    "https://huggingface.co/rhasspy/piper-voices/resolve/main/en/en_US/libritts_r/medium/en_US-libritts_r-medium.onnx.json"
                ]
            }
        ]
    },
    "piper-en_GB-alan-medium": {
        "engine": "piper",
        "name": "Engine 2: Piper British English — Alan",
        "version": "1.0",
        "language": "British English",
        "flag": "🇬🇧",
        "description": "Refined British gentleman voice for history and storytelling",
        "size_mb": 60,
        "recommended": False,
        "files": [
            {
                "filename": "en_GB-alan-medium.onnx",
                "target_dir": PIPER_DIR,
                "size_mb": 58,
                "sha256": None,
                "urls": [
                    "https://huggingface.co/rhasspy/piper-voices/resolve/main/en/en_GB/alan/medium/en_GB-alan-medium.onnx"
                ]
            },
            {
                "filename": "en_GB-alan-medium.onnx.json",
                "target_dir": PIPER_DIR,
                "size_mb": 2,
                "sha256": None,
                "urls": [
                    "https://huggingface.co/rhasspy/piper-voices/resolve/main/en/en_GB/alan/medium/en_GB-alan-medium.onnx.json"
                ]
            }
        ]
    },
    "piper-es_ES-davefx-medium": {
        "engine": "piper",
        "name": "Engine 2: Piper Spanish — DaveFX",
        "version": "1.0",
        "language": "Spanish",
        "flag": "🇪🇸",
        "description": "Natural Castilian Spanish neutral narrator voice",
        "size_mb": 62,
        "recommended": False,
        "files": [
            {
                "filename": "es_ES-davefx-medium.onnx",
                "target_dir": PIPER_DIR,
                "size_mb": 60,
                "sha256": None,
                "urls": [
                    "https://huggingface.co/rhasspy/piper-voices/resolve/main/es/es_ES/davefx/medium/es_ES-davefx-medium.onnx"
                ]
            },
            {
                "filename": "es_ES-davefx-medium.onnx.json",
                "target_dir": PIPER_DIR,
                "size_mb": 2,
                "sha256": None,
                "urls": [
                    "https://huggingface.co/rhasspy/piper-voices/resolve/main/es/es_ES/davefx/medium/es_ES-davefx-medium.onnx.json"
                ]
            }
        ]
    },
    "piper-fr_FR-siwis-medium": {
        "engine": "piper",
        "name": "Engine 2: Piper French — Siwis",
        "version": "1.0",
        "language": "French",
        "flag": "🇫🇷",
        "description": "Smooth, articulate Parisian French female voice",
        "size_mb": 64,
        "recommended": False,
        "files": [
            {
                "filename": "fr_FR-siwis-medium.onnx",
                "target_dir": PIPER_DIR,
                "size_mb": 62,
                "sha256": None,
                "urls": [
                    "https://huggingface.co/rhasspy/piper-voices/resolve/main/fr/fr_FR/siwis/medium/fr_FR-siwis-medium.onnx"
                ]
            },
            {
                "filename": "fr_FR-siwis-medium.onnx.json",
                "target_dir": PIPER_DIR,
                "size_mb": 2,
                "sha256": None,
                "urls": [
                    "https://huggingface.co/rhasspy/piper-voices/resolve/main/fr/fr_FR/siwis/medium/fr_FR-siwis-medium.onnx.json"
                ]
            }
        ]
    },
    "piper-de_DE-thorsten-medium": {
        "engine": "piper",
        "name": "Engine 2: Piper German — Thorsten",
        "version": "1.0",
        "language": "German",
        "flag": "🇩🇪",
        "description": "High clarity German male speech for podcasts and audiobooks",
        "size_mb": 61,
        "recommended": False,
        "files": [
            {
                "filename": "de_DE-thorsten-medium.onnx",
                "target_dir": PIPER_DIR,
                "size_mb": 59,
                "sha256": None,
                "urls": [
                    "https://huggingface.co/rhasspy/piper-voices/resolve/main/de/de_DE/thorsten/medium/de_DE-thorsten-medium.onnx"
                ]
            },
            {
                "filename": "de_DE-thorsten-medium.onnx.json",
                "target_dir": PIPER_DIR,
                "size_mb": 2,
                "sha256": None,
                "urls": [
                    "https://huggingface.co/rhasspy/piper-voices/resolve/main/de/de_DE/thorsten/medium/de_DE-thorsten-medium.onnx.json"
                ]
            }
        ]
    },
    "piper-it_IT-paola-medium": {
        "engine": "piper",
        "name": "Engine 2: Piper Italian — Paola",
        "version": "1.0",
        "language": "Italian",
        "flag": "🇮🇹",
        "description": "Warm, expressive Italian narrator voice",
        "size_mb": 60,
        "recommended": False,
        "files": [
            {
                "filename": "it_IT-paola-medium.onnx",
                "target_dir": PIPER_DIR,
                "size_mb": 58,
                "sha256": None,
                "urls": [
                    "https://huggingface.co/rhasspy/piper-voices/resolve/main/it/it_IT/paola/medium/it_IT-paola-medium.onnx"
                ]
            },
            {
                "filename": "it_IT-paola-medium.onnx.json",
                "target_dir": PIPER_DIR,
                "size_mb": 2,
                "sha256": None,
                "urls": [
                    "https://huggingface.co/rhasspy/piper-voices/resolve/main/it/it_IT/paola/medium/it_IT-paola-medium.onnx.json"
                ]
            }
        ]
    },
    "piper-pt_BR-faber-medium": {
        "engine": "piper",
        "name": "Engine 2: Piper Portuguese — Faber",
        "version": "1.0",
        "language": "Portuguese",
        "flag": "🇧🇷",
        "description": "Brazilian Portuguese clear neural voice model",
        "size_mb": 63,
        "recommended": False,
        "files": [
            {
                "filename": "pt_BR-faber-medium.onnx",
                "target_dir": PIPER_DIR,
                "size_mb": 61,
                "sha256": None,
                "urls": [
                    "https://huggingface.co/rhasspy/piper-voices/resolve/main/pt/pt_BR/faber/medium/pt_BR-faber-medium.onnx"
                ]
            },
            {
                "filename": "pt_BR-faber-medium.onnx.json",
                "target_dir": PIPER_DIR,
                "size_mb": 2,
                "sha256": None,
                "urls": [
                    "https://huggingface.co/rhasspy/piper-voices/resolve/main/pt/pt_BR/faber/medium/pt_BR-faber-medium.onnx.json"
                ]
            }
        ]
    },

    # -------------------------------------------------------------
    # F5-TTS Flow Matching Diffusion Voice Cloning Model
    # -------------------------------------------------------------
    "f5-tts-base": {
        "engine": "f5_tts",
        "name": "Engine 3: F5-TTS Zero-Shot Voice Cloning Model",
        "version": "1.0",
        "language": "Multi-Lingual",
        "flag": "🧬",
        "description": "Diffusion-based zero-shot voice cloning model (GPU recommended for realtime inference)",
        "size_mb": 1250,
        "recommended": False,
        "files": [
            {
                "filename": "model_1200000.safetensors",
                "target_dir": F5TTS_DIR,
                "size_mb": 1180,
                "sha256": None,
                "urls": [
                    "https://huggingface.co/SWivid/F5-TTS/resolve/main/F5TTS_Base/model_1200000.safetensors"
                ]
            },
            {
                "filename": "vocab.txt",
                "target_dir": F5TTS_DIR,
                "size_mb": 1,
                "sha256": None,
                "urls": [
                    "https://huggingface.co/SWivid/F5-TTS/resolve/main/F5TTS_Base/vocab.txt"
                ]
            }
        ]
    }
}
