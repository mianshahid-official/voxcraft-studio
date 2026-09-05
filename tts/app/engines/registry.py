"""
TTS Studio - Unified Engine Registry & Dispatcher
"""
from typing import Dict, Any, List, Optional, Tuple
import numpy as np

from .base import TTSEngine
from .kokoro.engine import KokoroEngine
from .piper.engine import PiperEngine
from .f5tts.engine import F5TTSEngine


class EngineRegistry:
    """Manages lazy instantiation and dispatching across Kokoro, Piper, and F5-TTS engines."""

    def __init__(self):
        self._engines: Dict[str, TTSEngine] = {}

    def get_engine(self, engine_name: str) -> TTSEngine:
        name = engine_name.lower()
        if name not in self._engines:
            if name == "kokoro":
                self._engines["kokoro"] = KokoroEngine()
            elif name == "piper":
                self._engines["piper"] = PiperEngine()
            elif name in ["f5_tts", "f5tts"]:
                self._engines["f5_tts"] = F5TTSEngine()
            else:
                self._engines["kokoro"] = KokoroEngine()
        return self._engines[name if name in self._engines else "kokoro"]

    def resolve_engine_for_voice(self, voice_id: str, hint: Optional[str] = None) -> TTSEngine:
        if hint:
            return self.get_engine(hint)
        if voice_id.startswith("piper-"):
            return self.get_engine("piper")
        elif voice_id.startswith("f5_"):
            return self.get_engine("f5_tts")
        return self.get_engine("kokoro")

    def get_all_voices(self) -> List[Dict[str, Any]]:
        all_voices = []
        for eng_name in ["kokoro", "piper", "f5_tts"]:
            eng = self.get_engine(eng_name)
            for v in eng.get_voices():
                v_copy = dict(v)
                v_copy["engine"] = eng_name
                all_voices.append(v_copy)
        return all_voices

    def unload_all(self):
        for eng in self._engines.values():
            if eng.is_loaded:
                eng.unload()

    def synthesize(
        self,
        text: str,
        voice: str = "af_bella",
        speed: float = 1.0,
        pitch: float = 0.0,
        engine_hint: Optional[str] = None,
        **kwargs
    ) -> Tuple[np.ndarray, int]:
        engine = self.resolve_engine_for_voice(voice, engine_hint)
        return engine.generate(text=text, voice=voice, speed=speed, pitch=pitch, **kwargs)


# Global Engine Registry
ENGINE_REGISTRY = EngineRegistry()
