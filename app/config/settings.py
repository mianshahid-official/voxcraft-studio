"""
TTS Studio - Centralized Application Settings & Persistence
"""
import json
from pathlib import Path
from dataclasses import dataclass, field, asdict
from typing import Dict, Any, Optional

from .paths import USER_DATA_DIR

SETTINGS_FILE = USER_DATA_DIR / "settings.json"


@dataclass
class AudioSettings:
    sample_rate: int = 24000
    default_format: str = "wav"  # wav, mp3, flac
    mp3_bitrate: str = "320k"
    normalize_loudness: bool = True
    target_lufs: float = -14.0
    trim_silence: bool = True
    silence_threshold_db: float = -40.0


@dataclass
class GenerationSettings:
    default_engine: str = "kokoro"
    default_voice: str = "af_bella"
    default_speed: float = 1.0
    default_pitch: float = 0.0
    performance_mode: str = "Balanced"  # Quality, Balanced, Fast
    gpu_preference: str = "Auto"  # Auto, GPU_First, CPU_Only
    auto_cpu_fallback: bool = True
    max_concurrent_jobs: int = 2
    chunk_max_words: int = 60
    autosave_interval_sec: int = 30
    keep_chunks_on_disk: bool = True
    duplicate_cache_enabled: bool = True


@dataclass
class AppearanceSettings:
    theme: str = "Dark"  # Dark, Light, System
    accent_color: str = "#8b5cf6"
    font_scale: float = 1.0
    show_waveform: bool = True
    animations_enabled: bool = True


@dataclass
class AppSettings:
    offline_mode: bool = True
    first_run_completed: bool = False
    audio: AudioSettings = field(default_factory=AudioSettings)
    generation: GenerationSettings = field(default_factory=GenerationSettings)
    appearance: AppearanceSettings = field(default_factory=AppearanceSettings)
    custom_dictionaries: Dict[str, str] = field(default_factory=dict)
    favorite_voices: list = field(default_factory=lambda: ["af_bella", "af_sarah", "am_adam"])

    @classmethod
    def load(cls) -> "AppSettings":
        if SETTINGS_FILE.exists():
            try:
                with open(SETTINGS_FILE, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    audio = AudioSettings(**data.get("audio", {}))
                    generation = GenerationSettings(**data.get("generation", {}))
                    appearance = AppearanceSettings(**data.get("appearance", {}))
                    return cls(
                        offline_mode=data.get("offline_mode", True),
                        first_run_completed=data.get("first_run_completed", False),
                        audio=audio,
                        generation=generation,
                        appearance=appearance,
                        custom_dictionaries=data.get("custom_dictionaries", {}),
                        favorite_voices=data.get("favorite_voices", ["af_bella", "af_sarah", "am_adam"])
                    )
            except Exception as e:
                print(f"Warning: Failed to load settings ({e}), using defaults.")
        inst = cls()
        inst.save()
        return inst

    def save(self):
        try:
            SETTINGS_FILE.parent.mkdir(parents=True, exist_ok=True)
            with open(SETTINGS_FILE, "w", encoding="utf-8") as f:
                json.dump(asdict(self), f, indent=2)
        except Exception as e:
            print(f"Error saving settings: {e}")


# Global settings singleton
APP_CONFIG = AppSettings.load()
