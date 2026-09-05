"""
TTS Studio - Unified TTS Engine Abstraction & Capability System
"""
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Dict, Any, List, Optional, Tuple
import numpy as np


@dataclass
class EngineCapability:
    engine_name: str
    display_name: str
    version: str
    supports_gpu: bool = True
    supports_cpu: bool = True
    supports_multispeaker: bool = False
    supports_voice_cloning: bool = False
    supports_voice_blending: bool = False
    supports_ssml_pauses: bool = True
    min_ram_gb: float = 2.0
    recommended_vram_gb: float = 0.0
    supported_languages: List[str] = field(default_factory=lambda: ["en"])
    default_sample_rate: int = 24000


class TTSEngine(ABC):
    """Abstract Base Class for all offline neural speech engines."""

    def __init__(self, name: str):
        self.name = name
        self.is_loaded = False
        self.active_device = "cpu"
        self.capabilities = self._init_capabilities()

    @abstractmethod
    def _init_capabilities(self) -> EngineCapability:
        """Define static capabilities and hardware profiles."""
        pass

    @abstractmethod
    def is_installed(self) -> bool:
        """Check if required weights and files exist on disk."""
        pass

    @abstractmethod
    def initialize(self, device_preference: str = "Auto") -> bool:
        """Load model session into memory with GPU priority and CPU fallback."""
        pass

    @abstractmethod
    def unload(self):
        """Unload model from RAM/VRAM."""
        pass

    @abstractmethod
    def get_voices(self) -> List[Dict[str, Any]]:
        """List available voices for this engine."""
        pass

    @abstractmethod
    def generate(
        self,
        text: str,
        voice: str,
        speed: float = 1.0,
        pitch: float = 0.0,
        **kwargs
    ) -> Tuple[np.ndarray, int]:
        """
        Synthesize text into raw float32 audio array [-1.0, 1.0] and sample rate.
        """
        pass

    def health_check(self) -> Dict[str, Any]:
        """Verify engine readiness and operational status."""
        installed = self.is_installed()
        return {
            "engine": self.name,
            "installed": installed,
            "loaded": self.is_loaded,
            "device": self.active_device,
            "status": "Ready" if self.is_loaded else ("Installed" if installed else "Missing Models")
        }
