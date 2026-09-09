"""
VoxCraft Studio - Offline Voice Package Manifest & Metadata Registry
Defines voice packages, language packs, download endpoints, and storage requirements.
"""
from pathlib import Path
from .paths import KOKORO_DIR, PIPER_DIR, F5TTS_DIR

MODEL_REGISTRY_MANIFEST = {
    # -------------------------------------------------------------
    # Studio Multi-Lingual Core Package (28 Voices)
    # -------------------------------------------------------------
    "kokoro-v0_19": {
        "engine": "kokoro",
        "name": "Studio Multi-Lingual Voice Pack (28 Voices)",
        "version": "1.0",
        "category": "Studio High-Fidelity (24kHz)",
        "language": "Multi-Lingual (US, Hindi, Spanish, French)",
        "flag": "✨",
        "voice_count": 28,
        "description": "Premium 24kHz ultra-HD neural voices featuring 28 expressive characters across US English, Hindi, Spanish, and French with dynamic multi-voice blending.",
        "size_mb": 325,
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
                "filename": "voices-v1.0.bin",
                "target_dir": KOKORO_DIR,
                "size_mb": 14,
                "sha256": None,
                "urls": [
                    "https://github.com/thewh1teagle/kokoro-onnx/releases/download/model-files-v1.0/voices-v1.0.bin",
                    "https://huggingface.co/hexgrad/Kokoro-82M/resolve/main/voices.bin"
                ]
            }
        ]
    },

    # -------------------------------------------------------------
    # Offline Voice Packages
    # -------------------------------------------------------------
    "piper-en_US-lessac-medium": {
        "engine": "piper",
        "name": "US English Narrator — Lessac",
        "version": "1.0",
        "category": "Solo Narrator",
        "language": "US English",
        "flag": "🇺🇸",
        "voice_count": 1,
        "description": "Crisp, balanced American English female narration voice crafted for audiobooks, long-form reading, and clear tutorials.",
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
        "name": "US English Studio Broadcaster — LibriTTS",
        "version": "1.0",
        "category": "Multi-Speaker Cast",
        "language": "US English",
        "flag": "🎧",
        "voice_count": 900,
        "description": "Extensive studio broadcast voice collection featuring diverse tonal registers and character variations.",
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
        "name": "British English Narrator — Alan",
        "version": "1.0",
        "category": "Solo Narrator",
        "language": "British English",
        "flag": "🇬🇧",
        "voice_count": 1,
        "description": "Rich, authoritative British gentleman narrator voice with distinguished articulation for documentaries and stories.",
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
        "name": "Spanish Castilian Voice — Dave",
        "version": "1.0",
        "category": "Solo Narrator",
        "language": "Spanish",
        "flag": "🇪🇸",
        "voice_count": 1,
        "description": "Natural European Spanish male voice with energetic cadence and clean pronunciation for media and dubbing.",
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
        "name": "French Parisian Voice — Siwis",
        "version": "1.0",
        "category": "Solo Narrator",
        "language": "French",
        "flag": "🇫🇷",
        "voice_count": 1,
        "description": "Smooth, eloquent Parisian French female voice with refined cadence for audiobooks and e-learning.",
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
        "name": "German Professional Voice — Thorsten",
        "version": "1.0",
        "category": "Solo Narrator",
        "language": "German",
        "flag": "🇩🇪",
        "voice_count": 1,
        "description": "Deep, articulate Standard German male voice designed for technical presentations and audio narration.",
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
        "name": "Italian Expressive Voice — Paola",
        "version": "1.0",
        "category": "Solo Narrator",
        "language": "Italian",
        "flag": "🇮🇹",
        "voice_count": 1,
        "description": "Warm, expressive Italian female voice crafted for dialogue, storytelling, and podcast productions.",
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
        "name": "Portuguese Brazilian Voice — Faber",
        "version": "1.0",
        "category": "Solo Narrator",
        "language": "Portuguese",
        "flag": "🇧🇷",
        "voice_count": 1,
        "description": "Clear Brazilian Portuguese narrator voice with natural intonation and balanced rhythm.",
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
    # Zero-Shot Voice Cloning System Package
    # -------------------------------------------------------------
    "f5-tts-base": {
        "engine": "f5_tts",
        "name": "Neural Voice Cloning Package",
        "version": "1.0",
        "category": "Voice Cloning",
        "language": "Multi-Lingual Universal",
        "flag": "🧬",
        "voice_count": 1,
        "description": "Advanced acoustic flow-matching neural package enabling instant 1-click voice cloning from any reference audio clip.",
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
