"""
TTS Studio - Resource & Concurrency Manager
Prevents Out-Of-Memory crashes, decides job concurrency, and manages model unloading.
"""
import gc
from typing import Dict, Any, Optional

from .hardware import HardwareManager


class ResourceManager:
    """Manages memory budgets, device allocations, and job concurrency limits."""

    @staticmethod
    def get_max_recommended_concurrency(engine_name: str) -> int:
        """
        Dynamically calculates safe concurrency limit based on hardware specs.
        """
        report = HardwareManager.get_hardware_report()

        if engine_name == "f5_tts":
            # Heavy flow matching model requires dedicated memory
            if report.gpu_detected and report.gpu_vram_gb >= 12.0:
                return 2
            return 1
        elif engine_name == "kokoro":
            # Lightweight ONNX model (~300MB RAM)
            if report.ram_available_gb >= 8.0:
                return 4
            elif report.ram_available_gb >= 4.0:
                return 2
            return 1
        elif engine_name == "piper":
            # Very lightweight CPU model (~50MB RAM)
            cores = report.cpu_physical_cores
            return min(4, max(1, cores // 2))

        return 1

    @staticmethod
    def clean_memory():
        """Force garbage collection and clear PyTorch CUDA memory cache if available."""
        gc.collect()
        try:
            import torch
            if torch.cuda.is_available():
                torch.cuda.empty_cache()
                torch.cuda.ipc_collect()
        except Exception:
            pass
