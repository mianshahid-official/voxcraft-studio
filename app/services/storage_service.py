"""
TTS Studio - Storage & Cache Management Service
"""
import os
import shutil
from pathlib import Path
from typing import Dict, Any

from ..config.paths import MODELS_DIR, PROJECTS_DIR, CACHE_DIR, EXPORTS_DIR, USER_DATA_DIR


class StorageService:
    """Calculates disk footprints and manages cache eviction."""

    @staticmethod
    def get_dir_size_mb(path: Path) -> float:
        if not path.exists():
            return 0.0
        total = 0
        for entry in path.glob("**/*"):
            if entry.is_file():
                try:
                    total += entry.stat().st_size
                except Exception:
                    pass
        return round(total / (1024 * 1024), 2)

    @classmethod
    def get_storage_breakdown(cls) -> Dict[str, Any]:
        models_mb = cls.get_dir_size_mb(MODELS_DIR)
        projects_mb = cls.get_dir_size_mb(PROJECTS_DIR)
        exports_mb = cls.get_dir_size_mb(EXPORTS_DIR)
        cache_mb = cls.get_dir_size_mb(CACHE_DIR)
        total_mb = models_mb + projects_mb + exports_mb + cache_mb

        return {
            "models_gb": round(models_mb / 1024, 2),
            "projects_gb": round(projects_mb / 1024, 2),
            "exports_gb": round(exports_mb / 1024, 2),
            "cache_mb": cache_mb,
            "total_gb": round(total_mb / 1024, 2)
        }

    @staticmethod
    def clear_cache() -> int:
        """Clear temporary and cached generation files."""
        count = 0
        if CACHE_DIR.exists():
            for f in CACHE_DIR.iterdir():
                try:
                    if f.is_file():
                        f.unlink()
                        count += 1
                except Exception:
                    pass
        return count
