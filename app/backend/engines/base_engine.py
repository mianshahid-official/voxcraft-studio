"""
VoxCraft Studio - Base TTS Engine Interface
Defines standard synthesis contract, hardware provider management, and common utilities.
"""
from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional, Tuple
import numpy as np
from pathlib import Path

from ..hardware import get_best_onnx_providers, get_gpu_info


class BaseTTSEngine(ABC):
    """Abstract Base Class for all offline local TTS engines in VoxCraft Studio."""

    def __init__(self, engine_name: str):
        self.engine_name = engine_name
        self.is_loaded = False
        self.active_device = "cpu"
        self.hardware_info = get_gpu_info()
        self.onnx_providers = get_best_onnx_providers()

    @abstractmethod
    def is_available(self) -> bool:
        """Check if required model files are present on disk."""
        pass

    @abstractmethod
    def load(self) -> bool:
        """Load model weights and initialize inference session."""
        pass

    @abstractmethod
    def synthesize(
        self,
        text: str,
        voice: str,
        speed: float = 1.0,
        pitch: float = 0.0,
        **kwargs
    ) -> Tuple[np.ndarray, int]:
        """
        Synthesize text into raw float32 audio array and sample rate.
        Returns: (audio_array_float32, sample_rate)
        """
        pass

    @abstractmethod
    def get_supported_voices(self) -> List[str]:
        """List of voice IDs supported by this engine."""
        pass

    def get_status(self) -> Dict[str, Any]:
        """Return engine readiness and device info."""
        return {
            "engine": self.engine_name,
            "is_available": self.is_available(),
            "is_loaded": self.is_loaded,
            "active_device": self.active_device,
            "providers": self.onnx_providers
        }
