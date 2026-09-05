"""
VoxCraft Studio - Unified Engine Registry & Dispatcher
"""
from typing import Dict, Any, Optional, Tuple
import numpy as np

from .base_engine import BaseTTSEngine
from .kokoro_engine import KokoroEngine
from .piper_engine import PiperEngine
from .f5_engine import F5TTSEngine


class EngineRegistry:
    """Manages lazy instantiation and dispatching across Kokoro, Piper, and F5-TTS engines."""

    def __init__(self):
        self._kokoro = None
        self._piper = None
        self._f5 = None

    @property
    def kokoro(self) -> KokoroEngine:
        if self._kokoro is None:
            self._kokoro = KokoroEngine()
        return self._kokoro

    @property
    def piper(self) -> PiperEngine:
        if self._piper is None:
            self._piper = PiperEngine()
        return self._piper

    @property
    def f5(self) -> F5TTSEngine:
        if self._f5 is None:
            self._f5 = F5TTSEngine()
        return self._f5

    def get_engine_for_voice(self, voice_id: str, engine_hint: Optional[str] = None) -> BaseTTSEngine:
        """Determines which engine to execute based on voice ID prefix or explicit hint."""
        if engine_hint == "kokoro" or voice_id.startswith("af_") or voice_id.startswith("am_") or voice_id.startswith("bf_") or voice_id.startswith("bm_") or voice_id.startswith("jf_") or voice_id.startswith("zf_") or voice_id.startswith("ef_") or voice_id.startswith("ff_") or voice_id.startswith("hf_") or voice_id.startswith("if_"):
            return self.kokoro
        elif engine_hint == "piper" or voice_id.startswith("piper-"):
            return self.piper
        elif engine_hint == "f5_tts" or voice_id.startswith("f5_"):
            return self.f5
        # Default to Kokoro
        return self.kokoro

    def synthesize(
        self,
        text: str,
        voice: str = "af_bella",
        speed: float = 1.0,
        pitch: float = 0.0,
        engine_hint: Optional[str] = None,
        **kwargs
    ) -> Tuple[np.ndarray, int]:
        """Routes synthesis request to the appropriate engine."""
        engine = self.get_engine_for_voice(voice, engine_hint)
        return engine.synthesize(text=text, voice=voice, speed=speed, pitch=pitch, **kwargs)

    def get_all_statuses(self) -> Dict[str, Any]:
        """Return readiness for all engines."""
        return {
            "kokoro": self.kokoro.get_status(),
            "piper": self.piper.get_status(),
            "f5_tts": self.f5.get_status()
        }


# Global engine registry instance
ENGINE_REGISTRY = EngineRegistry()
