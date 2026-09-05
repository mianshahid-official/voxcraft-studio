"""
VoxCraft Studio - Hardware Acceleration & System Requirements Diagnostics
Prioritizes GPU (CUDA / DirectML) for heavy compute loads (F5-TTS, large batches) with seamless CPU fallback.
"""
import os
import sys
import platform
import psutil
import shutil
from typing import Dict, Any, List, Optional
from pathlib import Path

def get_cpu_info() -> Dict[str, Any]:
    """Retrieve detailed CPU specifications."""
    try:
        cpu_count_physical = psutil.cpu_count(logical=False) or 4
        cpu_count_logical = psutil.cpu_count(logical=True) or 8
        cpu_percent = psutil.cpu_percent(interval=0.1)
        
        # Processor brand name
        proc_name = platform.processor() or "Multi-Core x86_64 Processor"
        
        return {
            "name": proc_name,
            "physical_cores": cpu_count_physical,
            "logical_threads": cpu_count_logical,
            "usage_percent": cpu_percent,
            "architecture": platform.machine()
        }
    except Exception as e:
        return {
            "name": "Standard CPU",
            "physical_cores": 4,
            "logical_threads": 8,
            "usage_percent": 0.0,
            "architecture": "x64"
        }

def get_ram_info() -> Dict[str, Any]:
    """Retrieve system RAM information."""
    try:
        mem = psutil.virtual_memory()
        return {
            "total_gb": round(mem.total / (1024 ** 3), 2),
            "available_gb": round(mem.available / (1024 ** 3), 2),
            "used_gb": round(mem.used / (1024 ** 3), 2),
            "percent": mem.percent
        }
    except Exception:
        return {
            "total_gb": 16.0,
            "available_gb": 8.0,
            "used_gb": 8.0,
            "percent": 50.0
        }

def get_disk_info(path: Optional[Path] = None) -> Dict[str, Any]:
    """Retrieve disk space for application/models directory."""
    try:
        check_path = str(path) if path else os.getcwd()
        usage = shutil.disk_usage(check_path)
        return {
            "total_gb": round(usage.total / (1024 ** 3), 2),
            "free_gb": round(usage.free / (1024 ** 3), 2),
            "used_gb": round(usage.used / (1024 ** 3), 2),
            "path": check_path
        }
    except Exception:
        return {
            "total_gb": 256.0,
            "free_gb": 100.0,
            "used_gb": 156.0,
            "path": "/"
        }

def get_gpu_info() -> Dict[str, Any]:
    """
    Detect GPU capabilities (NVIDIA CUDA, DirectML, or CPU fallback).
    Checks ONNX Runtime execution providers and PyTorch CUDA.
    """
    gpu_data = {
        "has_gpu": False,
        "type": "none",
        "name": "None (Using CPU)",
        "vram_gb": 0.0,
        "cuda_available": False,
        "directml_available": False,
        "onnx_providers": ["CPUExecutionProvider"],
        "recommended_device": "cpu",
        "details": "Running with optimized CPU multi-threading"
    }

    # 1. Check ONNX Runtime available execution providers
    try:
        import onnxruntime as ort
        available_providers = ort.get_available_providers()
        gpu_data["onnx_providers"] = available_providers
        
        if "CUDAExecutionProvider" in available_providers:
            gpu_data["has_gpu"] = True
            gpu_data["cuda_available"] = True
            gpu_data["type"] = "cuda"
            gpu_data["recommended_device"] = "cuda"
        elif "DmlExecutionProvider" in available_providers:
            gpu_data["has_gpu"] = True
            gpu_data["directml_available"] = True
            gpu_data["type"] = "directml"
            gpu_data["recommended_device"] = "directml"
    except Exception:
        pass

    # 2. Check PyTorch CUDA if installed
    try:
        import torch
        if torch.cuda.is_available():
            gpu_data["has_gpu"] = True
            gpu_data["cuda_available"] = True
            gpu_data["type"] = "cuda"
            gpu_data["recommended_device"] = "cuda"
            device_name = torch.cuda.get_device_name(0)
            gpu_data["name"] = device_name
            
            # VRAM
            vram_bytes = torch.cuda.get_device_properties(0).total_memory
            gpu_data["vram_gb"] = round(vram_bytes / (1024 ** 3), 2)
            gpu_data["details"] = f"NVIDIA CUDA Hardware Acceleration ({gpu_data['vram_gb']} GB VRAM)"
            return gpu_data
    except Exception:
        pass

    # 3. Check Windows WMI / DirectX GPU info if on Windows and PyTorch wasn't CUDA
    if sys.platform == "win32" and not gpu_data["cuda_available"]:
        try:
            import subprocess
            cmd = "powershell -Command \"Get-CimInstance Win32_VideoController | Select-Object -ExpandProperty Name\""
            res = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=3)
            if res.returncode == 0 and res.stdout.strip():
                gpu_names = [line.strip() for line in res.stdout.strip().split("\n") if line.strip()]
                # Filter out basic display adapters
                meaningful_gpus = [g for g in gpu_names if "Remote" not in g and "Basic" not in g]
                if meaningful_gpus:
                    primary_gpu = meaningful_gpus[0]
                    gpu_data["name"] = primary_gpu
                    if "NVIDIA" in primary_gpu.upper():
                        gpu_data["has_gpu"] = True
                        gpu_data["type"] = "nvidia"
                        gpu_data["details"] = f"{primary_gpu} (DirectX / DirectML GPU Acceleration)"
                    elif "AMD" in primary_gpu.upper() or "RADEON" in primary_gpu.upper():
                        gpu_data["has_gpu"] = True
                        gpu_data["type"] = "amd"
                        gpu_data["details"] = f"{primary_gpu} (DirectML GPU Acceleration)"
                    elif "INTEL" in primary_gpu.upper() and ("ARC" in primary_gpu.upper() or "IRIS" in primary_gpu.upper()):
                        gpu_data["has_gpu"] = True
                        gpu_data["type"] = "intel"
                        gpu_data["details"] = f"{primary_gpu} (DirectML GPU Acceleration)"
        except Exception:
            pass

    if not gpu_data["has_gpu"]:
        gpu_data["details"] = "Optimized multi-threaded CPU inference"
        gpu_data["name"] = "CPU Acceleration"

    return gpu_data

def get_system_diagnostics(models_path: Optional[Path] = None) -> Dict[str, Any]:
    """Full hardware diagnostic report for the UI and model engine."""
    cpu = get_cpu_info()
    ram = get_ram_info()
    disk = get_disk_info(models_path)
    gpu = get_gpu_info()
    
    # Assess readiness
    is_ready_for_heavy = (gpu["has_gpu"] and gpu.get("vram_gb", 0) >= 4) or ram["available_gb"] >= 8
    
    return {
        "os": f"{platform.system()} {platform.release()} ({platform.version()})",
        "python_version": platform.python_version(),
        "cpu": cpu,
        "ram": ram,
        "disk": disk,
        "gpu": gpu,
        "active_device": "GPU (" + gpu["name"] + ")" if gpu["has_gpu"] else "CPU",
        "is_ready_for_heavy": is_ready_for_heavy,
        "status": "Optimal" if (ram["available_gb"] >= 4 and disk["free_gb"] >= 5) else "Warning"
    }

def get_best_onnx_providers() -> List[str]:
    """
    Returns prioritized list of ONNX Runtime execution providers.
    Order: CUDA -> DirectML -> CPU.
    """
    providers = []
    try:
        import onnxruntime as ort
        avail = ort.get_available_providers()
        if "CUDAExecutionProvider" in avail:
            providers.append("CUDAExecutionProvider")
        if "DmlExecutionProvider" in avail:
            providers.append("DmlExecutionProvider")
        providers.append("CPUExecutionProvider")
    except Exception:
        providers = ["CPUExecutionProvider"]
    return providers
