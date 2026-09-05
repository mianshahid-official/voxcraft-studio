"""
TTS Studio - Hardware Detection & Resource Manager
Detects CPU, RAM, GPU (CUDA / DirectML), VRAM, and manages device acceleration routing.
"""
import os
import sys
import platform
import psutil
import shutil
import subprocess
from dataclasses import dataclass
from typing import Dict, Any, List, Optional
from pathlib import Path


@dataclass
class HardwareReport:
    os_name: str
    cpu_name: str
    cpu_physical_cores: int
    cpu_logical_threads: int
    ram_total_gb: float
    ram_available_gb: float
    disk_free_gb: float
    gpu_detected: bool
    gpu_name: str
    gpu_vram_gb: float
    cuda_available: bool
    directml_available: bool
    recommended_device: str
    details: str


class HardwareManager:
    """Hardware diagnostic and acceleration provider manager."""

    @staticmethod
    def get_hardware_report(check_path: Optional[Path] = None) -> HardwareReport:
        # 1. CPU info
        try:
            cpu_name = platform.processor() or "Multi-Core x86_64 Processor"
            p_cores = psutil.cpu_count(logical=False) or 4
            l_threads = psutil.cpu_count(logical=True) or 8
        except Exception:
            cpu_name = "x86_64 CPU"
            p_cores, l_threads = 4, 8

        # 2. RAM info
        try:
            mem = psutil.virtual_memory()
            ram_total = round(mem.total / (1024 ** 3), 2)
            ram_avail = round(mem.available / (1024 ** 3), 2)
        except Exception:
            ram_total, ram_avail = 16.0, 8.0

        # 3. Disk info
        try:
            target = str(check_path) if check_path else os.getcwd()
            disk_free = round(shutil.disk_usage(target).free / (1024 ** 3), 2)
        except Exception:
            disk_free = 50.0

        # 4. GPU & Acceleration Detection
        gpu_detected = False
        gpu_name = "None (CPU Optimized)"
        gpu_vram = 0.0
        cuda_avail = False
        directml_avail = False
        rec_device = "cpu"
        details = "Optimized multi-threaded CPU execution"

        # Check ONNX Runtime available execution providers
        try:
            import onnxruntime as ort
            providers = ort.get_available_providers()
            if "CUDAExecutionProvider" in providers:
                cuda_avail = True
            if "DmlExecutionProvider" in providers:
                directml_avail = True
        except Exception:
            pass

        # Check PyTorch CUDA
        try:
            import torch
            if torch.cuda.is_available():
                cuda_avail = True
                gpu_detected = True
                gpu_name = torch.cuda.get_device_name(0)
                vram_bytes = torch.cuda.get_device_properties(0).total_memory
                gpu_vram = round(vram_bytes / (1024 ** 3), 2)
                rec_device = "cuda"
                details = f"{gpu_name} (NVIDIA CUDA Acceleration - {gpu_vram} GB VRAM)"
        except Exception:
            pass

        # Windows DirectX / WMI GPU fallback detection if not CUDA PyTorch
        if sys.platform == "win32" and not cuda_avail:
            try:
                cmd = "powershell -Command \"Get-CimInstance Win32_VideoController | Select-Object -ExpandProperty Name\""
                res = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=3)
                if res.returncode == 0 and res.stdout.strip():
                    names = [line.strip() for line in res.stdout.strip().split("\n") if line.strip()]
                    meaningful = [n for n in names if "Remote" not in n and "Basic" not in n]
                    if meaningful:
                        gpu_detected = True
                        gpu_name = meaningful[0]
                        if directml_avail:
                            rec_device = "directml"
                            details = f"{gpu_name} (DirectML GPU Hardware Acceleration)"
                        else:
                            details = f"{gpu_name} (DirectX Display Adapter)"
            except Exception:
                pass

        return HardwareReport(
            os_name=f"{platform.system()} {platform.release()}",
            cpu_name=cpu_name,
            cpu_physical_cores=p_cores,
            cpu_logical_threads=l_threads,
            ram_total_gb=ram_total,
            ram_available_gb=ram_avail,
            disk_free_gb=disk_free,
            gpu_detected=gpu_detected,
            gpu_name=gpu_name,
            gpu_vram_gb=gpu_vram,
            cuda_available=cuda_avail,
            directml_available=directml_avail,
            recommended_device=rec_device,
            details=details
        )

    @staticmethod
    def get_live_metrics() -> Dict[str, Any]:
        """Real-time CPU, RAM, and GPU utilization for UI Resource Monitor HUD."""
        cpu_pct = psutil.cpu_percent(interval=None)
        mem = psutil.virtual_memory()
        
        gpu_pct = 0.0
        vram_used = 0.0
        vram_total = 0.0

        try:
            import torch
            if torch.cuda.is_available():
                vram_used = round(torch.cuda.memory_allocated(0) / (1024 ** 3), 2)
                vram_total = round(torch.cuda.get_device_properties(0).total_memory / (1024 ** 3), 2)
                gpu_pct = min(100.0, round((vram_used / max(0.1, vram_total)) * 100, 1))
        except Exception:
            pass

        return {
            "cpu_percent": cpu_pct,
            "ram_used_gb": round(mem.used / (1024 ** 3), 2),
            "ram_total_gb": round(mem.total / (1024 ** 3), 2),
            "ram_percent": mem.percent,
            "gpu_percent": gpu_pct,
            "vram_used_gb": vram_used,
            "vram_total_gb": vram_total
        }
