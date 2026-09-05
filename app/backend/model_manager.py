"""
VoxCraft Studio - Offline Model Manager & Download Hub
Manages offline model detection, segmented downloading, progress tracking, and custom model imports.
"""
import os
import sys
import time
import json
import shutil
import hashlib
import threading
from pathlib import Path
from typing import Dict, Any, List, Optional, Callable
import requests

from .config import (
    MODELS_DIR,
    KOKORO_MODELS_DIR,
    PIPER_MODELS_DIR,
    F5_MODELS_DIR,
    MODEL_DOWNLOAD_MANIFEST
)

# Active download status tracker
ACTIVE_DOWNLOADS: Dict[str, Dict[str, Any]] = {}
DOWNLOAD_LOCK = threading.Lock()


class ModelManager:
    """Manages local model scanning, offline downloads with progress streaming, and imports."""

    @staticmethod
    def get_local_model_status() -> Dict[str, Any]:
        """
        Scans local storage to identify which models and voice weights are installed offline.
        Returns detailed status for Kokoro, Piper, and F5-TTS models.
        """
        status: Dict[str, Any] = {
            "kokoro": {
                "installed": False,
                "models": [],
                "voices_available": [],
                "storage_mb": 0.0,
            },
            "piper": {
                "installed": False,
                "models": [],
                "storage_mb": 0.0,
            },
            "f5_tts": {
                "installed": False,
                "models": [],
                "storage_mb": 0.0,
            },
            "manifest": {}
        }

        # 1. Scan Kokoro
        kokoro_files = list(KOKORO_MODELS_DIR.glob("*"))
        kokoro_size = sum(f.stat().st_size for f in kokoro_files if f.is_file()) / (1024 * 1024)
        has_kokoro_onnx = any(f.name.endswith(".onnx") for f in kokoro_files)
        has_kokoro_voices = any(f.name.startswith("voices") for f in kokoro_files)
        status["kokoro"]["installed"] = has_kokoro_onnx and has_kokoro_voices
        status["kokoro"]["storage_mb"] = round(kokoro_size, 2)
        status["kokoro"]["models"] = [f.name for f in kokoro_files if f.name.endswith(".onnx")]

        # 2. Scan Piper
        piper_files = list(PIPER_MODELS_DIR.glob("*.onnx"))
        piper_size = sum(f.stat().st_size for f in PIPER_MODELS_DIR.glob("*") if f.is_file()) / (1024 * 1024)
        status["piper"]["installed"] = len(piper_files) > 0
        status["piper"]["storage_mb"] = round(piper_size, 2)
        status["piper"]["models"] = [f.stem for f in piper_files]

        # 3. Scan F5-TTS
        f5_files = list(F5_MODELS_DIR.glob("*"))
        f5_size = sum(f.stat().st_size for f in f5_files if f.is_file()) / (1024 * 1024)
        has_f5_weights = any(f.name.endswith(".safetensors") or f.name.endswith(".pt") for f in f5_files)
        status["f5_tts"]["installed"] = has_f5_weights
        status["f5_tts"]["storage_mb"] = round(f5_size, 2)
        status["f5_tts"]["models"] = [f.name for f in f5_files if f.is_file()]

        # 4. Check each manifest entry
        for model_key, meta in MODEL_DOWNLOAD_MANIFEST.items():
            all_files_present = True
            total_model_size_mb = 0.0
            
            for item in meta["files"]:
                target_file = Path(item["target_dir"]) / item["filename"]
                if target_file.exists() and target_file.stat().st_size > 1024:
                    total_model_size_mb += target_file.stat().st_size / (1024 * 1024)
                else:
                    all_files_present = False

            is_active_dl = model_key in ACTIVE_DOWNLOADS and ACTIVE_DOWNLOADS[model_key]["status"] == "downloading"
            
            status["manifest"][model_key] = {
                "key": model_key,
                "name": meta["name"],
                "engine": meta["engine"],
                "description": meta["description"],
                "total_size_mb": meta["size_mb"],
                "is_installed": all_files_present,
                "is_downloading": is_active_dl,
                "download_progress": ACTIVE_DOWNLOADS.get(model_key, {}).get("progress", 0.0),
                "speed_mbps": ACTIVE_DOWNLOADS.get(model_key, {}).get("speed_mbps", 0.0),
                "eta_seconds": ACTIVE_DOWNLOADS.get(model_key, {}).get("eta_seconds", 0)
            }

        return status

    @staticmethod
    def start_model_download(model_key: str, progress_callback: Optional[Callable] = None) -> bool:
        """Starts a background thread to download all model files for the given manifest key."""
        if model_key not in MODEL_DOWNLOAD_MANIFEST:
            return False

        with DOWNLOAD_LOCK:
            if model_key in ACTIVE_DOWNLOADS and ACTIVE_DOWNLOADS[model_key]["status"] == "downloading":
                return True  # Already downloading

            ACTIVE_DOWNLOADS[model_key] = {
                "status": "downloading",
                "progress": 0.0,
                "downloaded_bytes": 0,
                "total_bytes": MODEL_DOWNLOAD_MANIFEST[model_key]["size_mb"] * 1024 * 1024,
                "speed_mbps": 0.0,
                "eta_seconds": 0,
                "error": None,
                "cancel_requested": False
            }

        def _worker():
            meta = MODEL_DOWNLOAD_MANIFEST[model_key]
            total_expected_bytes = int(meta["size_mb"] * 1024 * 1024)
            accumulated_bytes = 0
            start_time = time.time()

            try:
                for file_info in meta["files"]:
                    if ACTIVE_DOWNLOADS[model_key].get("cancel_requested"):
                        break

                    target_dir = Path(file_info["target_dir"])
                    target_dir.mkdir(parents=True, exist_ok=True)
                    target_filepath = target_dir / file_info["filename"]
                    temp_filepath = target_dir / f"{file_info['filename']}.part"

                    # Skip if already exists and size matches approximately
                    if target_filepath.exists() and target_filepath.stat().st_size >= file_info["size_mb"] * 1024 * 1024 * 0.95:
                        accumulated_bytes += target_filepath.stat().st_size
                        continue

                    # Attempt URLs in order
                    downloaded_ok = False
                    for url in file_info["urls"]:
                        try:
                            response = requests.get(url, stream=True, timeout=15, headers={"User-Agent": "VoxCraft-Studio/1.0"})
                            response.raise_for_status()
                            
                            file_total = int(response.headers.get('content-length', file_info["size_mb"] * 1024 * 1024))
                            chunk_size = 1024 * 512  # 512KB chunks
                            
                            with open(temp_filepath, "wb") as f:
                                for chunk in response.iter_content(chunk_size=chunk_size):
                                    if ACTIVE_DOWNLOADS[model_key].get("cancel_requested"):
                                        break
                                    if chunk:
                                        f.write(chunk)
                                        accumulated_bytes += len(chunk)
                                        
                                        elapsed = max(0.1, time.time() - start_time)
                                        speed_bps = accumulated_bytes / elapsed
                                        speed_mbps = round(speed_bps / (1024 * 1024), 2)
                                        remaining_bytes = max(0, total_expected_bytes - accumulated_bytes)
                                        eta_sec = int(remaining_bytes / max(1024, speed_bps))
                                        
                                        progress_pct = min(99.0, round((accumulated_bytes / max(1, total_expected_bytes)) * 100, 1))

                                        with DOWNLOAD_LOCK:
                                            ACTIVE_DOWNLOADS[model_key]["progress"] = progress_pct
                                            ACTIVE_DOWNLOADS[model_key]["speed_mbps"] = speed_mbps
                                            ACTIVE_DOWNLOADS[model_key]["eta_seconds"] = eta_sec
                                            ACTIVE_DOWNLOADS[model_key]["downloaded_bytes"] = accumulated_bytes

                            if not ACTIVE_DOWNLOADS[model_key].get("cancel_requested"):
                                if temp_filepath.exists():
                                    if target_filepath.exists():
                                        target_filepath.unlink()
                                    temp_filepath.rename(target_filepath)
                                downloaded_ok = True
                                break
                        except Exception as e:
                            if temp_filepath.exists():
                                try:
                                    temp_filepath.unlink()
                                except Exception:
                                    pass
                            continue

                    if not downloaded_ok and not ACTIVE_DOWNLOADS[model_key].get("cancel_requested"):
                        raise RuntimeError(f"Failed downloading {file_info['filename']} from all mirrors.")

                with DOWNLOAD_LOCK:
                    if ACTIVE_DOWNLOADS[model_key].get("cancel_requested"):
                        ACTIVE_DOWNLOADS[model_key]["status"] = "cancelled"
                    else:
                        ACTIVE_DOWNLOADS[model_key]["status"] = "completed"
                        ACTIVE_DOWNLOADS[model_key]["progress"] = 100.0
                        ACTIVE_DOWNLOADS[model_key]["speed_mbps"] = 0.0
                        ACTIVE_DOWNLOADS[model_key]["eta_seconds"] = 0

            except Exception as ex:
                with DOWNLOAD_LOCK:
                    ACTIVE_DOWNLOADS[model_key]["status"] = "error"
                    ACTIVE_DOWNLOADS[model_key]["error"] = str(ex)

        t = threading.Thread(target=_worker, daemon=True)
        t.start()
        return True

    @staticmethod
    def cancel_model_download(model_key: str) -> bool:
        """Cancel an in-progress download."""
        with DOWNLOAD_LOCK:
            if model_key in ACTIVE_DOWNLOADS:
                ACTIVE_DOWNLOADS[model_key]["cancel_requested"] = True
                ACTIVE_DOWNLOADS[model_key]["status"] = "cancelling"
                return True
        return False

    @staticmethod
    def get_download_progress(model_key: str) -> Dict[str, Any]:
        """Get live download statistics for a model key."""
        with DOWNLOAD_LOCK:
            return ACTIVE_DOWNLOADS.get(model_key, {
                "status": "idle",
                "progress": 0.0,
                "speed_mbps": 0.0,
                "eta_seconds": 0
            })

    @staticmethod
    def import_custom_model(source_file_path: str, engine_type: str) -> Dict[str, Any]:
        """Import custom local model file into the appropriate directory."""
        src = Path(source_file_path).resolve()
        if not src.exists():
            return {"success": False, "error": "Source file does not exist"}

        dest_dir = KOKORO_MODELS_DIR if engine_type == "kokoro" else (PIPER_MODELS_DIR if engine_type == "piper" else F5_MODELS_DIR)
        dest_dir.mkdir(parents=True, exist_ok=True)
        dest = dest_dir / src.name

        try:
            shutil.copy2(str(src), str(dest))
            return {
                "success": True,
                "filename": src.name,
                "engine": engine_type,
                "target_path": str(dest)
            }
        except Exception as e:
            return {"success": False, "error": str(e)}
