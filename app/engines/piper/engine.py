"""
TTS Studio - Piper Neural Multi-Lingual Engine Implementation
Uses official PiperVoice engine with built-in eSpeak-NG phonemizer.
"""
import os
import sys
import json
import logging
from pathlib import Path
from typing import Dict, Any, List, Optional, Tuple
import numpy as np

from ..base import TTSEngine, EngineCapability
from ...config.paths import PIPER_DIR

logger = logging.getLogger("TTSStudio.Piper")


class PiperEngine(TTSEngine):
    """Piper Fast CPU Neural Speech Synthesis Engine."""

    def __init__(self):
        super().__init__("piper")
        self.voices_cache: Dict[str, Any] = {}
        self.sample_rate = 22050

    def _init_capabilities(self) -> EngineCapability:
        return EngineCapability(
            engine_name="piper",
            display_name="Piper Neural TTS",
            version="1.8.0",
            supports_gpu=False,
            supports_cpu=True,
            supports_multispeaker=True,
            supports_voice_cloning=False,
            supports_voice_blending=False,
            supports_ssml_pauses=True,
            min_ram_gb=0.5,
            recommended_vram_gb=0.0,
            supported_languages=["en_US", "en_GB", "es_ES", "fr_FR", "de_DE", "it_IT", "pt_BR", "ru_RU", "hi_IN", "ar_JO"],
            default_sample_rate=22050
        )

    def is_installed(self) -> bool:
        return len(list(PIPER_DIR.glob("*.onnx"))) > 0

    def initialize(self, device_preference: str = "Auto") -> bool:
        models = list(PIPER_DIR.glob("*.onnx"))
        if not models:
            logger.info("No Piper ONNX models found.")
            return False

        try:
            from piper import PiperVoice
            self.active_device = "CPU (Optimized)"
            self.is_loaded = True
            logger.info("Piper Engine initialized.")
            return True
        except Exception as e:
            logger.error(f"Piper initialization error: {e}", exc_info=True)
            return False

    def unload(self):
        self.voices_cache.clear()
        self.is_loaded = False
        logger.info("Piper Engine unloaded.")

    def get_voices(self) -> List[Dict[str, Any]]:
        return [
            {"id": "piper-en_US-lessac-medium", "name": "Piper Lessac (Narrator)", "gender": "Female", "language": "English (US)", "style": "Audiobook / Educational", "avatar": "📚"},
            {"id": "piper-en_US-libritts_r-medium", "name": "Piper LibriTTS-R (Studio)", "gender": "Neutral / Multi", "language": "English (US)", "style": "Multi-Speaker Pack", "avatar": "🎧"},
            {"id": "piper-en_GB-alan-medium", "name": "Piper Alan (British)", "gender": "Male", "language": "English (UK)", "style": "Classic British", "avatar": "🎩"},
            {"id": "piper-es_ES-davefx-medium", "name": "Piper DaveFX (Spanish)", "gender": "Male", "language": "Spanish", "style": "Castilian Narrator", "avatar": "🇪🇸"},
            {"id": "piper-fr_FR-siwis-medium", "name": "Piper Siwis (French)", "gender": "Female", "language": "French", "style": "Parisian Expressive", "avatar": "🇫🇷"},
            {"id": "piper-de_DE-thorsten-medium", "name": "Piper Thorsten (German)", "gender": "Male", "language": "German", "style": "Clear Audiobook", "avatar": "🇩🇪"},
            {"id": "piper-it_IT-riccardo-medium", "name": "Piper Riccardo (Italian)", "gender": "Male", "language": "Italian", "style": "Italian Narrator", "avatar": "🇮🇹"},
            {"id": "piper-pt_BR-edresson-medium", "name": "Piper Edresson (Portuguese)", "gender": "Male", "language": "Portuguese", "style": "Brazilian Portuguese", "avatar": "🇧🇷"}
        ]

    def generate(
        self,
        text: str,
        voice: str = "piper-en_US-lessac-medium",
        speed: float = 1.0,
        pitch: float = 0.0,
        speaker_id: int = 0,
        **kwargs
    ) -> Tuple[np.ndarray, int]:
        clean_text = text.strip()
        if not clean_text:
            return np.zeros(0, dtype=np.float32), self.sample_rate

        clean_name = voice.replace("piper-", "")
        if clean_name not in self.voices_cache:
            m_path = PIPER_DIR / f"{clean_name}.onnx"
            if m_path.exists():
                try:
                    from piper import PiperVoice
                    pv = PiperVoice.load(str(m_path))
                    self.voices_cache[clean_name] = pv
                except Exception as e:
                    logger.error(f"Failed loading Piper voice {clean_name}: {e}")
            
            if clean_name not in self.voices_cache:
                # Try finding any available piper model
                avail = list(PIPER_DIR.glob("*.onnx"))
                if avail:
                    fallback_name = avail[0].stem
                    if fallback_name not in self.voices_cache:
                        from piper import PiperVoice
                        self.voices_cache[fallback_name] = PiperVoice.load(str(avail[0]))
                    pv = self.voices_cache[fallback_name]
                else:
                    raise RuntimeError(f"Piper voice '{clean_name}' is not installed locally. Please download it from Model Hub.")
            else:
                pv = self.voices_cache[clean_name]
        else:
            pv = self.voices_cache[clean_name]

        sr = pv.config.sample_rate

        try:
            chunks = [chunk.audio_float_array for chunk in pv.synthesize(clean_text)]
            if chunks:
                audio = np.concatenate(chunks).astype(np.float32)
            else:
                audio = np.zeros(0, dtype=np.float32)
            return audio, sr
        except Exception as e:
            logger.error(f"Piper synthesis error: {e}", exc_info=True)
            raise RuntimeError(f"Piper synthesis failed: {e}")
