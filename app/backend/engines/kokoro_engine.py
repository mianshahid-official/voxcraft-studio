"""
VoxCraft Studio - Kokoro-82M High-Fidelity TTS Engine
Accelerated with ONNX Runtime (GPU / DirectML / CPU) with voice embedding blending.
"""
import os
import sys
import json
import logging
from pathlib import Path
from typing import Dict, Any, List, Optional, Tuple
import numpy as np

from .base_engine import BaseTTSEngine
from ..config import KOKORO_MODELS_DIR, KOKORO_SAMPLE_RATE
from ..hardware import get_best_onnx_providers, get_gpu_info

logger = logging.getLogger("VoxCraft.Kokoro")


class KokoroEngine(BaseTTSEngine):
    """Kokoro TTS Engine supporting standard voices and custom multi-voice blending."""

    def __init__(self):
        super().__init__("kokoro")
        self.kokoro_instance = None
        self.voices_data = {}
        self.sample_rate = KOKORO_SAMPLE_RATE
        self.model_path: Optional[Path] = None
        self.voices_path: Optional[Path] = None

    def _locate_files(self) -> bool:
        """Find local Kokoro ONNX model and voices file."""
        onnx_candidates = [
            KOKORO_MODELS_DIR / "kokoro-v1.0.onnx",
            KOKORO_MODELS_DIR / "kokoro-v0_19.onnx",
        ]
        for c in onnx_candidates:
            if c.exists() and c.stat().st_size > 1024 * 1024:
                self.model_path = c
                break

        voices_candidates = [
            KOKORO_MODELS_DIR / "voices-v1.0.bin",
            KOKORO_MODELS_DIR / "voices.bin",
            KOKORO_MODELS_DIR / "voices.json",
        ]
        for v in voices_candidates:
            if v.exists() and v.stat().st_size > 1024:
                self.voices_path = v
                break

        return (self.model_path is not None) and (self.voices_path is not None)

    def is_available(self) -> bool:
        """Returns True if Kokoro weights exist locally."""
        return self._locate_files()

    def load(self) -> bool:
        """Initializes Kokoro-ONNX session with hardware acceleration."""
        if self.is_loaded and self.kokoro_instance is not None:
            return True

        if not self._locate_files():
            logger.info("Kokoro model files not found locally.")
            return False

        try:
            from kokoro_onnx import Kokoro
            import onnxruntime as ort

            providers = get_best_onnx_providers()
            logger.info(f"Initializing Kokoro with ONNX providers: {providers}")

            # Initialize Kokoro instance
            self.kokoro_instance = Kokoro(
                model_path=str(self.model_path),
                voices_path=str(self.voices_path)
            )

            # Determine active hardware acceleration
            gpu_info = get_gpu_info()
            if "CUDAExecutionProvider" in providers and gpu_info.get("cuda_available"):
                self.active_device = f"GPU (CUDA: {gpu_info.get('name', 'NVIDIA')})"
            elif "DmlExecutionProvider" in providers and gpu_info.get("directml_available"):
                self.active_device = f"GPU (DirectML: {gpu_info.get('name', 'GPU')})"
            else:
                self.active_device = "CPU (Multi-Threaded)"

            self.is_loaded = True
            logger.info(f"Kokoro Engine loaded successfully on {self.active_device}")
            return True

        except Exception as e:
            logger.error(f"Failed to load Kokoro Engine: {e}", exc_info=True)
            self.is_loaded = False
            return False

    def synthesize(
        self,
        text: str,
        voice: str = "af_bella",
        speed: float = 1.0,
        pitch: float = 0.0,
        voice_blend: Optional[Dict[str, Any]] = None,
        **kwargs
    ) -> Tuple[np.ndarray, int]:
        """
        Synthesize speech from text.
        Supports single voice or continuous voice blend.
        """
        cleaned_text = text.strip()
        if not cleaned_text:
            return np.zeros(0, dtype=np.float32), self.sample_rate

        # Ensure engine is loaded
        if not self.is_loaded:
            if not self.load():
                # If weights are missing, generate synthetic preview audio
                return self._generate_preview_placeholder(cleaned_text, voice, speed)

        try:
            # Handle voice blending if requested
            selected_voice = voice
            if voice_blend and "voice_a" in voice_blend and "voice_b" in voice_blend:
                v_a = voice_blend.get("voice_a", "af_bella")
                v_b = voice_blend.get("voice_b", "af_nicole")
                w_a = float(voice_blend.get("weight_a", 0.5))
                w_b = 1.0 - w_a
                
                try:
                    style_a = self.kokoro_instance.get_voice_style(v_a)
                    style_b = self.kokoro_instance.get_voice_style(v_b)
                    # Interpolate voice vectors
                    blended_style = (style_a * w_a) + (style_b * w_b)
                    
                    samples, sample_rate = self.kokoro_instance.create(
                        text=cleaned_text,
                        voice=blended_style,
                        speed=speed,
                        lang="en-us"
                    )
                    return samples.astype(np.float32), sample_rate
                except Exception as ex:
                    logger.warning(f"Voice blend interpolation failed, fallback to {voice}: {ex}")

            # Standard single voice synthesis
            # Detect language prefix (e.g. jf_ -> ja, zf_ -> zh, ef_ -> es, ff_ -> fr)
            lang = "en-us"
            if voice.startswith("jf_") or voice.startswith("jm_"):
                lang = "ja"
            elif voice.startswith("zf_") or voice.startswith("zm_"):
                lang = "zh"
            elif voice.startswith("ef_") or voice.startswith("em_"):
                lang = "es"
            elif voice.startswith("ff_") or voice.startswith("fm_"):
                lang = "fr"
            elif voice.startswith("bf_") or voice.startswith("bm_"):
                lang = "en-gb"
            elif voice.startswith("hf_") or voice.startswith("hm_"):
                lang = "hi"
            elif voice.startswith("if_") or voice.startswith("im_"):
                lang = "it"
            elif voice.startswith("pf_") or voice.startswith("pm_"):
                lang = "pt-br"

            samples, sample_rate = self.kokoro_instance.create(
                text=cleaned_text,
                voice=selected_voice,
                speed=speed,
                lang=lang
            )
            return samples.astype(np.float32), sample_rate

        except Exception as e:
            logger.error(f"Kokoro synthesis error: {e}", exc_info=True)
            return self._generate_preview_placeholder(cleaned_text, voice, speed)

    def _generate_preview_placeholder(self, text: str, voice: str, speed: float) -> Tuple[np.ndarray, int]:
        """
        Generates pleasant synthetic FM acoustic preview tones when models are downloading or offline.
        """
        duration = max(1.2, min(8.0, len(text.split()) * 0.35 / speed))
        num_samples = int(self.sample_rate * duration)
        t = np.linspace(0, duration, num_samples, endpoint=False, dtype=np.float32)

        # Base tone derived from voice name
        is_female = voice.startswith("af_") or voice.startswith("bf_") or "female" in voice
        base_freq = 240.0 if is_female else 140.0

        # Modulated speech-like acoustic envelope
        carrier = np.sin(2 * np.pi * base_freq * t)
        modulator = 0.5 * np.sin(2 * np.pi * (base_freq * 2.0) * t)
        harmonic = 0.25 * np.sin(2 * np.pi * (base_freq * 3.0) * t)
        
        envelope = np.sin(np.pi * t / duration) ** 0.5
        # Add syllabic rhythmic pulsing
        syllable_pulse = 0.6 + 0.4 * np.abs(np.sin(2 * np.pi * 3.5 * t))
        
        audio = (carrier + modulator + harmonic) * envelope * syllable_pulse * 0.3
        return audio.astype(np.float32), self.sample_rate

    def get_supported_voices(self) -> List[str]:
        """List of all Kokoro voice identifiers."""
        return [
            "af_bella", "af_sarah", "af_nicole", "af_sky", "af_heart", "af_alloy", "af_aoede", "af_kore",
            "am_adam", "am_michael", "am_fenrir", "am_liam", "am_echo", "am_eric", "am_onyx", "am_puck",
            "bf_emma", "bf_isabella", "bf_alice", "bf_lily",
            "bm_george", "bm_lewis", "bm_fable", "bm_daniel",
            "jf_tepra", "jm_kumo", "zf_xiaoyan", "zm_yunjian",
            "ef_dora", "em_alex", "ff_siwis", "hf_alpha", "if_sara"
        ]
