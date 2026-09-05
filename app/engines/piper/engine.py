"""
TTS Studio - Piper Neural Multi-Lingual Engine Implementation
Uses official PiperVoice engine with eSpeak phonemizer and SynthesisConfig.
Supports multi-language speech synthesis for English, British English, Spanish, French, German, Italian, and Portuguese.
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
    """Piper Fast CPU/GPU Neural Speech Synthesis Engine."""

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
            supported_languages=["en_US", "en_GB", "es_ES", "fr_FR", "de_DE", "it_IT", "pt_BR"],
            default_sample_rate=22050
        )

    def is_installed(self) -> bool:
        return len(list(PIPER_DIR.glob("*.onnx"))) > 0

    def _get_or_load_voice(self, clean_name: str) -> Optional[Any]:
        if clean_name in self.voices_cache:
            return self.voices_cache[clean_name]

        model_path = PIPER_DIR / f"{clean_name}.onnx"
        config_path = PIPER_DIR / f"{clean_name}.onnx.json"

        if not model_path.exists():
            matches = list(PIPER_DIR.glob(f"*{clean_name}*.onnx"))
            if matches:
                model_path = matches[0]
                config_path = model_path.with_suffix(".onnx.json")
            else:
                return None

        try:
            from piper import PiperVoice
            c_arg = str(config_path) if config_path.exists() else None
            pv = PiperVoice.load(str(model_path), config_path=c_arg)
            self.voices_cache[clean_name] = pv
            logger.info(f"Loaded PiperVoice '{clean_name}' at {pv.config.sample_rate}Hz")
            return pv
        except Exception as e:
            logger.error(f"Failed loading PiperVoice '{clean_name}': {e}")
            return None

    def initialize(self, device_preference: str = "Auto") -> bool:
        models = list(PIPER_DIR.glob("*.onnx"))
        if not models:
            logger.info("No Piper ONNX models found locally.")
            return False

        self.active_device = "CPU (Optimized Neural)"
        self.is_loaded = True
        return True

    def unload(self):
        self.voices_cache.clear()
        self.is_loaded = False
        logger.info("Piper Engine unloaded.")

    def get_voices(self) -> List[Dict[str, Any]]:
        return [
            {"id": "piper-en_US-lessac-medium", "name": "Lessac", "gender": "Female", "language": "English", "style": "Audiobook / Educational", "avatar": "📚"},
            {"id": "piper-en_US-libritts_r-medium", "name": "LibriTTS", "gender": "Neutral / Multi", "language": "English", "style": "Multi-Speaker Pack", "avatar": "🎧"},
            {"id": "piper-en_GB-alan-medium", "name": "Alan", "gender": "Male", "language": "British English", "style": "Classic British", "avatar": "🎩"},
            {"id": "piper-es_ES-davefx-medium", "name": "DaveFX", "gender": "Male", "language": "Spanish", "style": "Castilian Narrator", "avatar": "🇪🇸"},
            {"id": "piper-fr_FR-siwis-medium", "name": "Siwis", "gender": "Female", "language": "French", "style": "Parisian Expressive", "avatar": "🇫🇷"},
            {"id": "piper-de_DE-thorsten-medium", "name": "Thorsten", "gender": "Male", "language": "German", "style": "Clear Audiobook", "avatar": "🇩🇪"},
            {"id": "piper-it_IT-paola-medium", "name": "Paola", "gender": "Female", "language": "Italian", "style": "Italian Narrator", "avatar": "🇮🇹"},
            {"id": "piper-pt_BR-faber-medium", "name": "Faber", "gender": "Male", "language": "Portuguese", "style": "Brazilian Portuguese", "avatar": "🇧🇷"}
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
        pv = self._get_or_load_voice(clean_name)

        if pv is None:
            # Try any available piper voice
            avail = list(PIPER_DIR.glob("*.onnx"))
            if avail:
                pv = self._get_or_load_voice(avail[0].stem)

        if pv is not None:
            try:
                # Use Piper synthesis with speed config
                try:
                    from piper.config import SynthesisConfig
                    length_scale = float(1.0 / max(0.2, speed))
                    spk = speaker_id if speaker_id and speaker_id > 0 else None
                    syn_cfg = SynthesisConfig(length_scale=length_scale, speaker_id=spk)
                    chunks = [chunk.audio_float_array for chunk in pv.synthesize(clean_text, syn_config=syn_cfg)]
                except Exception:
                    chunks = [chunk.audio_float_array for chunk in pv.synthesize(clean_text)]

                if chunks:
                    audio = np.concatenate(chunks).astype(np.float32)
                    return audio, pv.config.sample_rate
            except Exception as e:
                logger.error(f"Piper synthesis error: {e}", exc_info=True)

        # Fallback to Kokoro Neural synthesis for clear, natural audio
        logger.info(f"Routing Piper voice '{voice}' to Kokoro neural engine for clear synthesis.")
        from ..kokoro.engine import KokoroEngine
        kokoro = KokoroEngine()
        kokoro_voice = "bf_emma" if any(k in voice for k in ["alan", "gb"]) else ("bm_george" if "thorsten" in voice else "af_bella")
        return kokoro.generate(clean_text, voice=kokoro_voice, speed=speed, pitch=pitch)
