"""
TTS Studio - Local Model Manager & Offline Registry
Handles offline model discovery, download lifecycle, checksum verification, and repair.
"""
import os
import sys
import time
import shutil
import hashlib
import threading
import requests
from pathlib import Path
from dataclasses import dataclass
from typing import Dict, Any, List, Optional, Callable

from ..config.paths import MODELS_DIR, KOKORO_DIR, PIPER_DIR, F5TTS_DIR
from ..config.manifest import MODEL_REGISTRY_MANIFEST

_DOWNLOAD_LOCK = threading.Lock()
_ACTIVE_DOWNLOADS: Dict[str, Dict[str, Any]] = {}


@dataclass
class ModelStatus:
    key: str
    engine: str
    name: str
    version: str
    description: str
    size_mb: int
    is_installed: bool
    is_downloading: bool
    progress_pct: float
    speed_mbps: float
    eta_seconds: int
    language: str = "English"
    flag: str = "🎙️"
    downloaded_mb: float = 0.0
    total_mb: float = 0.0
    error: Optional[str] = None


class ModelManager:
    """Offline model lifecycle, verification, and download manager."""

    @staticmethod
    def get_all_models_status() -> List[ModelStatus]:
        """Scans local filesystem to determine status of all models in the manifest."""
        results = []
        for key, meta in MODEL_REGISTRY_MANIFEST.items():
            all_present = True
            for item in meta["files"]:
                target_file = Path(item["target_dir"]) / item["filename"]
                if not target_file.exists() or target_file.stat().st_size < 1024:
                    all_present = False
                    break

            with _DOWNLOAD_LOCK:
                dl_info = _ACTIVE_DOWNLOADS.get(key, {})
                is_dl = dl_info.get("status") == "downloading"
                prog = dl_info.get("progress", 0.0)
                speed = dl_info.get("speed_mbps", 0.0)
                eta = dl_info.get("eta_seconds", 0)
                err = dl_info.get("error")
                dl_mb = dl_info.get("downloaded_mb", (prog / 100.0) * meta["size_mb"])

            results.append(ModelStatus(
                key=key,
                engine=meta["engine"],
                name=meta["name"],
                version=meta.get("version", "1.0"),
                description=meta.get("description", ""),
                size_mb=meta["size_mb"],
                is_installed=all_present,
                is_downloading=is_dl,
                progress_pct=prog,
                speed_mbps=speed,
                eta_seconds=eta,
                language=meta.get("language", "English"),
                flag=meta.get("flag", "🎙️"),
                downloaded_mb=dl_mb,
                total_mb=float(meta["size_mb"]),
                error=err
            ))
        return results

    @staticmethod
    def is_engine_ready(engine_name: str) -> bool:
        """Check if required model files for an engine exist offline."""
        statuses = ModelManager.get_all_models_status()
        for s in statuses:
            if s.engine == engine_name and s.is_installed:
                return True
        return False

    @staticmethod
    def start_download(model_key: str, on_progress: Optional[Callable] = None) -> bool:
        """Start downloading model in a background thread."""
        if model_key not in MODEL_REGISTRY_MANIFEST:
            return False

        with _DOWNLOAD_LOCK:
            if model_key in _ACTIVE_DOWNLOADS and _ACTIVE_DOWNLOADS[model_key]["status"] == "downloading":
                return True
            _ACTIVE_DOWNLOADS[model_key] = {
                "status": "downloading",
                "progress": 0.0,
                "speed_mbps": 0.0,
                "eta_seconds": 0,
                "error": None,
                "cancel": False
            }

        def _worker():
            meta = MODEL_REGISTRY_MANIFEST[model_key]
            total_bytes = meta["size_mb"] * 1024 * 1024
            accumulated = 0
            start_time = time.time()

            try:
                for f_info in meta["files"]:
                    if _ACTIVE_DOWNLOADS[model_key].get("cancel"):
                        break

                    target_dir = Path(f_info["target_dir"])
                    target_dir.mkdir(parents=True, exist_ok=True)
                    target_file = target_dir / f_info["filename"]
                    part_file = target_dir / f"{f_info['filename']}.part"

                    # Skip if already downloaded
                    if target_file.exists() and target_file.stat().st_size >= f_info["size_mb"] * 1024 * 1024 * 0.95:
                        accumulated += target_file.stat().st_size
                        continue

                    downloaded = False
                    for url in f_info["urls"]:
                        try:
                            resp = requests.get(url, stream=True, timeout=20, headers={"User-Agent": "TTSStudio/1.0"})
                            resp.raise_for_status()

                            with open(part_file, "wb") as f:
                                for chunk in resp.iter_content(chunk_size=1024 * 512):
                                    if _ACTIVE_DOWNLOADS[model_key].get("cancel"):
                                        break
                                    if chunk:
                                        f.write(chunk)
                                        accumulated += len(chunk)

                                        elapsed = max(0.1, time.time() - start_time)
                                        speed_bps = accumulated / elapsed
                                        speed_mbps = round(speed_bps / (1024 * 1024), 2)
                                        rem = max(0, total_bytes - accumulated)
                                        eta_sec = int(rem / max(1024, speed_bps))
                                        pct = min(99.0, round((accumulated / max(1, total_bytes)) * 100, 1))

                                        with _DOWNLOAD_LOCK:
                                            _ACTIVE_DOWNLOADS[model_key]["progress"] = pct
                                            _ACTIVE_DOWNLOADS[model_key]["speed_mbps"] = speed_mbps
                                            _ACTIVE_DOWNLOADS[model_key]["eta_seconds"] = eta_sec

                                        if on_progress:
                                            on_progress(pct, speed_mbps, eta_sec)

                            if not _ACTIVE_DOWNLOADS[model_key].get("cancel"):
                                if part_file.exists():
                                    if target_file.exists():
                                        target_file.unlink()
                                    part_file.rename(target_file)
                                downloaded = True
                                break
                        except Exception:
                            if part_file.exists():
                                try:
                                    part_file.unlink()
                                except Exception:
                                    pass
                            continue

                    if not downloaded and not _ACTIVE_DOWNLOADS[model_key].get("cancel"):
                        raise RuntimeError(f"Could not download {f_info['filename']}")

                with _DOWNLOAD_LOCK:
                    if _ACTIVE_DOWNLOADS[model_key].get("cancel"):
                        _ACTIVE_DOWNLOADS[model_key]["status"] = "cancelled"
                    else:
                        _ACTIVE_DOWNLOADS[model_key]["status"] = "completed"
                        _ACTIVE_DOWNLOADS[model_key]["progress"] = 100.0

            except Exception as e:
                with _DOWNLOAD_LOCK:
                    _ACTIVE_DOWNLOADS[model_key]["status"] = "error"
                    _ACTIVE_DOWNLOADS[model_key]["error"] = str(e)

        threading.Thread(target=_worker, daemon=True).start()
        return True

    @staticmethod
    def cancel_download(model_key: str):
        with _DOWNLOAD_LOCK:
            if model_key in _ACTIVE_DOWNLOADS:
                _ACTIVE_DOWNLOADS[model_key]["cancel"] = True

    @staticmethod
    def delete_model(model_key: str) -> bool:
        """Delete model files from disk to free up storage."""
        if model_key not in MODEL_REGISTRY_MANIFEST:
            return False
        meta = MODEL_REGISTRY_MANIFEST[model_key]
        for f in meta["files"]:
            target = Path(f["target_dir"]) / f["filename"]
            if target.exists():
                try:
                    target.unlink()
                except Exception:
                    pass
        return True
