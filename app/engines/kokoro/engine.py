"""
TTS Studio - Kokoro-82M High-Fidelity ONNX Engine Implementation
"""
import os
import sys
import logging
from pathlib import Path
from typing import Dict, Any, List, Optional, Tuple
import numpy as np

from ..base import TTSEngine, EngineCapability
from ...config.paths import KOKORO_DIR
from ...core.hardware import HardwareManager

logger = logging.getLogger("TTSStudio.Kokoro")


class KokoroEngine(TTSEngine):
    """Kokoro 82M Parameter ONNX Neural Speech Engine."""

    def __init__(self):
        super().__init__("kokoro")
        self.kokoro_instance = None
        self.sample_rate = 24000
        self.model_path = None
        self.voices_path = None

    def _init_capabilities(self) -> EngineCapability:
        return EngineCapability(
            engine_name="kokoro",
            display_name="Kokoro-82M Neural TTS",
            version="0.19",
            supports_gpu=True,
            supports_cpu=True,
            supports_multispeaker=False,
            supports_voice_cloning=False,
            supports_voice_blending=True,
            supports_ssml_pauses=True,
            min_ram_gb=1.5,
            recommended_vram_gb=2.0,
            supported_languages=["en_US", "en_GB", "ja", "zh", "es", "fr", "hi", "it", "pt_BR"],
            default_sample_rate=24000
        )

    def _locate_files(self) -> bool:
        onnx_candidates = [
            KOKORO_DIR / "kokoro-v1.0.onnx",
            KOKORO_DIR / "kokoro-v0_19.onnx",
        ]
        for c in onnx_candidates:
            if c.exists() and c.stat().st_size > 1024 * 1024:
                self.model_path = c
                break

        voices_candidates = [
            KOKORO_DIR / "voices-v1.0.bin",
            KOKORO_DIR / "voices.bin",
            KOKORO_DIR / "voices.json",
        ]
        for v in voices_candidates:
            if v.exists() and v.stat().st_size > 1024:
                self.voices_path = v
                break

        return (self.model_path is not None) and (self.voices_path is not None)

    def is_installed(self) -> bool:
        return self._locate_files()

    def initialize(self, device_preference: str = "Auto") -> bool:
        if self.is_loaded and self.kokoro_instance is not None:
            return True

        if not self._locate_files():
            logger.info("Kokoro model files not found locally.")
            return False

        try:
            from kokoro_onnx import Kokoro
            import onnxruntime as ort

            # Build providers list based on hardware & preference
            report = HardwareManager.get_hardware_report()
            providers = []

            if device_preference != "CPU_Only":
                if report.cuda_available:
                    providers.append("CUDAExecutionProvider")
                if report.directml_available:
                    providers.append("DmlExecutionProvider")
            providers.append("CPUExecutionProvider")

            logger.info(f"Loading Kokoro with providers: {providers}")

            self.kokoro_instance = Kokoro(
                model_path=str(self.model_path),
                voices_path=str(self.voices_path)
            )

            if "CUDAExecutionProvider" in providers and report.cuda_available and device_preference != "CPU_Only":
                self.active_device = f"GPU (CUDA: {report.gpu_name})"
            elif "DmlExecutionProvider" in providers and report.directml_available and device_preference != "CPU_Only":
                self.active_device = f"GPU (DirectML: {report.gpu_name})"
            else:
                self.active_device = "CPU (Multi-Threaded)"

            self.is_loaded = True
            logger.info(f"Kokoro Engine initialized on {self.active_device}")
            return True
        except Exception as e:
            logger.error(f"Failed initializing Kokoro: {e}", exc_info=True)
            self.is_loaded = False
            return False

    def unload(self):
        self.kokoro_instance = None
        self.is_loaded = False
        logger.info("Kokoro Engine unloaded.")

    def get_voices(self) -> List[Dict[str, Any]]:
        return [
            {"id": "af_bella", "name": "Bella", "gender": "Female", "language": "English (US)", "style": "Podcast / Warm", "avatar": "🎙️"},
            {"id": "af_sarah", "name": "Sarah", "gender": "Female", "language": "English (US)", "style": "Audiobook / Calm", "avatar": "📖"},
            {"id": "af_nicole", "name": "Nicole", "gender": "Female", "language": "English (US)", "style": "News / Professional", "avatar": "💼"},
            {"id": "af_sky", "name": "Sky", "gender": "Female", "language": "English (US)", "style": "Casual / Friendly", "avatar": "✨"},
            {"id": "am_adam", "name": "Adam", "gender": "Male", "language": "English (US)", "style": "Narrator / Deep", "avatar": "🎬"},
            {"id": "am_michael", "name": "Michael", "gender": "Male", "language": "English (US)", "style": "Podcast / Charismatic", "avatar": "🎙️"},
            {"id": "bf_emma", "name": "Emma", "gender": "Female", "language": "English (UK)", "style": "Classic Literature", "avatar": "👑"},
            {"id": "bf_isabella", "name": "Isabella", "gender": "Female", "language": "English (UK)", "style": "Modern British", "avatar": "☕"},
            {"id": "bm_george", "name": "George", "gender": "Male", "language": "English (UK)", "style": "Scholarly / History", "avatar": "🏛️"},
            {"id": "bm_lewis", "name": "Lewis", "gender": "Male", "language": "English (UK)", "style": "Storyteller / Warm", "avatar": "🏰"}
        ]

    def _resolve_voice_and_lang(self, voice: str) -> Tuple[str, str]:
        """Resolves voice name and language code against available Kokoro voice embeddings."""
        known_voices = {
            "af_bella", "af_sarah", "af_nicole", "af_sky", "af",
            "am_adam", "am_michael", "bf_emma", "bf_isabella", "bm_george", "bm_lewis"
        }

        lang = "en-us"
        if voice.startswith("jf_") or voice.startswith("jm_") or "japanese" in voice.lower():
            lang = "ja"
        elif voice.startswith("zf_") or voice.startswith("zm_") or "chinese" in voice.lower() or "mandarin" in voice.lower():
            lang = "zh"
        elif voice.startswith("ef_") or voice.startswith("em_") or "spanish" in voice.lower():
            lang = "es"
        elif voice.startswith("ff_") or voice.startswith("fm_") or "french" in voice.lower():
            lang = "fr"
        elif voice.startswith("bf_") or voice.startswith("bm_") or "british" in voice.lower() or "uk" in voice.lower():
            lang = "en-gb"
        elif voice.startswith("hf_") or voice.startswith("hm_") or "hindi" in voice.lower():
            lang = "hi"
        elif voice.startswith("if_") or voice.startswith("im_") or "italian" in voice.lower():
            lang = "it"
        elif voice.startswith("pf_") or voice.startswith("pm_") or "portuguese" in voice.lower():
            lang = "pt-br"

        target_voice = voice
        if target_voice not in known_voices:
            if target_voice.startswith("am_") or target_voice.startswith("bm_") or target_voice.startswith("em_") or target_voice.startswith("fm_"):
                target_voice = "am_adam"
            elif target_voice.startswith("bf_"):
                target_voice = "bf_emma"
            else:
                target_voice = "af_bella"

        return target_voice, lang

    def generate(
        self,
        text: str,
        voice: str = "af_bella",
        speed: float = 1.0,
        pitch: float = 0.0,
        voice_blend: Optional[Dict[str, Any]] = None,
        **kwargs
    ) -> Tuple[np.ndarray, int]:
        clean_text = text.strip()
        if not clean_text:
            return np.zeros(0, dtype=np.float32), self.sample_rate

        if not self.is_loaded:
            if not self.initialize():
                raise RuntimeError("Kokoro Engine is not initialized. Please ensure model files are downloaded.")

        try:
            target_voice, lang = self._resolve_voice_and_lang(voice)

            # Voice blend
            if voice_blend and "voice_a" in voice_blend and "voice_b" in voice_blend:
                v_a_resolved, _ = self._resolve_voice_and_lang(voice_blend["voice_a"])
                v_b_resolved, _ = self._resolve_voice_and_lang(voice_blend["voice_b"])
                w_a = float(voice_blend.get("weight_a", 0.5))
                style_a = self.kokoro_instance.get_voice_style(v_a_resolved)
                style_b = self.kokoro_instance.get_voice_style(v_b_resolved)
                blended = (style_a * w_a) + (style_b * (1.0 - w_a))
                samples, sr = self.kokoro_instance.create(clean_text, voice=blended, speed=speed, lang=lang)
                return samples.astype(np.float32), sr

            samples, sr = self.kokoro_instance.create(clean_text, voice=target_voice, speed=speed, lang=lang)
            return samples.astype(np.float32), sr
        except Exception as e:
            logger.error(f"Kokoro generation error: {e}", exc_info=True)
            raise RuntimeError(f"Kokoro synthesis failed: {e}")
