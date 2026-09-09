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
            supported_languages=["en_US", "hi", "es", "fr"],
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
            # American English (Female)
            {"id": "af_bella", "name": "Bella", "gender": "Female", "language": "English (US)", "style": "Podcast / Warm", "avatar": "🎙️"},
            {"id": "af_sarah", "name": "Sarah", "gender": "Female", "language": "English (US)", "style": "Audiobook / Calm", "avatar": "📖"},
            {"id": "af_nicole", "name": "Nicole", "gender": "Female", "language": "English (US)", "style": "News / Professional", "avatar": "💼"},
            {"id": "af_sky", "name": "Sky", "gender": "Female", "language": "English (US)", "style": "Casual / Friendly", "avatar": "✨"},
            {"id": "af_alloy", "name": "Alloy", "gender": "Female", "language": "English (US)", "style": "Crisp / Clear", "avatar": "⚡"},
            {"id": "af_aoede", "name": "Aoede", "gender": "Female", "language": "English (US)", "style": "Melodic / Narrative", "avatar": "🎵"},
            {"id": "af_heart", "name": "Heart", "gender": "Female", "language": "English (US)", "style": "Empathetic / Warm", "avatar": "💖"},
            {"id": "af_jessica", "name": "Jessica", "gender": "Female", "language": "English (US)", "style": "Conversational", "avatar": "☕"},
            {"id": "af_kore", "name": "Kore", "gender": "Female", "language": "English (US)", "style": "Youthful / Bright", "avatar": "🌸"},
            {"id": "af_nova", "name": "Nova", "gender": "Female", "language": "English (US)", "style": "Energetic / Dynamic", "avatar": "🌟"},
            {"id": "af_river", "name": "River", "gender": "Female", "language": "English (US)", "style": "Calm / Meditative", "avatar": "🌊"},

            # American English (Male)
            {"id": "am_adam", "name": "Adam", "gender": "Male", "language": "English (US)", "style": "Narrator / Deep", "avatar": "🎬"},
            {"id": "am_michael", "name": "Michael", "gender": "Male", "language": "English (US)", "style": "Podcast Host", "avatar": "🎙️"},
            {"id": "am_echo", "name": "Echo", "gender": "Male", "language": "English (US)", "style": "Studio Announcer", "avatar": "📢"},
            {"id": "am_eric", "name": "Eric", "gender": "Male", "language": "English (US)", "style": "Warm / Expressive", "avatar": "🎧"},
            {"id": "am_fenrir", "name": "Fenrir", "gender": "Male", "language": "English (US)", "style": "Resonant / Powerful", "avatar": "🐺"},
            {"id": "am_liam", "name": "Liam", "gender": "Male", "language": "English (US)", "style": "Modern / Youthful", "avatar": "📱"},
            {"id": "am_onyx", "name": "Onyx", "gender": "Male", "language": "English (US)", "style": "Deep Baritone", "avatar": "🗿"},
            {"id": "am_puck", "name": "Puck", "gender": "Male", "language": "English (US)", "style": "Playful / Fast", "avatar": "🎭"},
            {"id": "am_santa", "name": "Santa", "gender": "Male", "language": "English (US)", "style": "Jolly / Mature", "avatar": "🎅"},

            # Hindi (Female & Male)
            {"id": "hf_alpha", "name": "Alpha (अल्फा)", "gender": "Female", "language": "Hindi", "style": "Warm / Natural Hindi", "avatar": "🇮🇳"},
            {"id": "hf_beta", "name": "Beta (बीटा)", "gender": "Female", "language": "Hindi", "style": "Clear / Expressive Hindi", "avatar": "🌸"},
            {"id": "hm_omega", "name": "Omega (ओमेगा)", "gender": "Male", "language": "Hindi", "style": "Deep Narrator Hindi", "avatar": "🎙️"},
            {"id": "hm_psi", "name": "Psi (साई)", "gender": "Male", "language": "Hindi", "style": "Conversational Hindi", "avatar": "🇮🇳"},

            # Spanish (Female & Male)
            {"id": "ef_dora", "name": "Dora", "gender": "Female", "language": "Spanish", "style": "Castilian / Expressive", "avatar": "🇪🇸"},
            {"id": "em_alex", "name": "Alex", "gender": "Male", "language": "Spanish", "style": "Narrator / Neutral Spanish", "avatar": "🎙️"},
            {"id": "em_santa", "name": "Santa (ES)", "gender": "Male", "language": "Spanish", "style": "Warm Spanish Voice", "avatar": "🎅"},

            # French (Female)
            {"id": "ff_siwis", "name": "Siwis", "gender": "Female", "language": "French", "style": "Parisian / Articulate", "avatar": "🇫🇷"}
        ]

    def _resolve_voice_and_lang(self, voice: str) -> Tuple[str, str]:
        """Resolves voice name and language code against available Kokoro voice embeddings."""
        available_voices = {
            "af_alloy", "af_aoede", "af_bella", "af_heart", "af_jessica", "af_kore",
            "af_nicole", "af_nova", "af_river", "af_sarah", "af_sky",
            "am_adam", "am_echo", "am_eric", "am_fenrir", "am_liam", "am_michael",
            "am_onyx", "am_puck", "am_santa",
            "ef_dora", "em_alex", "em_santa",
            "ff_siwis",
            "hf_alpha", "hf_beta", "hm_omega", "hm_psi"
        }

        v_lower = voice.lower().strip()

        # 1. Hindi
        if v_lower.startswith("hf_") or v_lower.startswith("hm_") or "hindi" in v_lower:
            lang = "hi"
            target = voice if voice in available_voices else ("hm_omega" if "hm" in v_lower or "male" in v_lower else "hf_alpha")
            return target, lang

        # 2. Spanish
        if v_lower.startswith("ef_") or v_lower.startswith("em_") or "spanish" in v_lower:
            lang = "es"
            target = voice if voice in available_voices else ("em_alex" if "em" in v_lower or "male" in v_lower else "ef_dora")
            return target, lang

        # 3. French
        if v_lower.startswith("ff_") or v_lower.startswith("fm_") or "french" in v_lower:
            lang = "fr-fr"
            target = "ff_siwis"
            return target, lang

        # 4. American English (Default)
        lang = "en-us"
        if voice in available_voices:
            target = voice
        elif v_lower.startswith("am_") or "male" in v_lower:
            target = "am_adam"
        else:
            target = "af_bella"

        return target, lang

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

