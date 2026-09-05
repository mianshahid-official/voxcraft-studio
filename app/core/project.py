"""
TTS Studio - Project Management & Autosave System
"""
import os
import json
import time
import shutil
from pathlib import Path
from dataclasses import dataclass, asdict, field
from typing import List, Dict, Any, Optional

from ..config.paths import PROJECTS_DIR, USER_DATA_DIR

AUTOSAVE_FILE = USER_DATA_DIR / "autosave_draft.json"


@dataclass
class ProjectMetadata:
    id: str
    name: str
    created_at: float
    updated_at: float
    engine: str
    voice: str
    speed: float = 1.0
    pitch: float = 0.0
    duration_sec: float = 0.0
    word_count: int = 0
    project_type: str = "tts"  # tts, podcast, batch


class ProjectManager:
    """Manages project persistence, directory structures, and crash recovery."""

    @staticmethod
    def get_all_projects() -> List[Dict[str, Any]]:
        """List all saved projects sorted by last updated."""
        projects = []
        if not PROJECTS_DIR.exists():
            return []

        for p_dir in PROJECTS_DIR.iterdir():
            if p_dir.is_dir():
                meta_file = p_dir / "project.json"
                if meta_file.exists():
                    try:
                        with open(meta_file, "r", encoding="utf-8") as f:
                            data = json.load(f)
                            data["dir_path"] = str(p_dir)
                            projects.append(data)
                    except Exception:
                        pass
        projects.sort(key=lambda x: x.get("updated_at", 0), reverse=True)
        return projects

    @staticmethod
    def create_project(name: str, engine: str = "kokoro", voice: str = "af_bella", project_type: str = "tts") -> Path:
        """Create a new project folder structure."""
        safe_name = "".join(c for c in name if c.isalnum() or c in (' ', '_', '-')).strip()
        p_dir = PROJECTS_DIR / safe_name
        p_dir.mkdir(parents=True, exist_ok=True)
        (p_dir / "audio").mkdir(exist_ok=True)
        (p_dir / "chunks").mkdir(exist_ok=True)
        (p_dir / "timestamps").mkdir(exist_ok=True)

        meta = ProjectMetadata(
            id=f"proj_{int(time.time())}",
            name=safe_name,
            created_at=time.time(),
            updated_at=time.time(),
            engine=engine,
            voice=voice,
            project_type=project_type
        )
        meta_file = p_dir / "project.json"
        with open(meta_file, "w", encoding="utf-8") as f:
            json.dump(asdict(meta), f, indent=2)

        (p_dir / "script.txt").write_text("", encoding="utf-8")
        return p_dir

    @staticmethod
    def save_project_data(project_path: Path, script_text: str, settings_dict: Dict[str, Any], timestamps: Optional[List] = None):
        """Save script, settings, and metadata to project."""
        p_dir = Path(project_path)
        if not p_dir.exists():
            return

        (p_dir / "script.txt").write_text(script_text, encoding="utf-8")
        meta_file = p_dir / "project.json"
        if meta_file.exists():
            try:
                with open(meta_file, "r", encoding="utf-8") as f:
                    meta = json.load(f)
            except Exception:
                meta = {}
        else:
            meta = {}

        meta["updated_at"] = time.time()
        meta["word_count"] = len(script_text.split())
        meta.update(settings_dict)

        with open(meta_file, "w", encoding="utf-8") as f:
            json.dump(meta, f, indent=2)

        if timestamps:
            ts_file = p_dir / "timestamps" / "timestamps.json"
            with open(ts_file, "w", encoding="utf-8") as f:
                json.dump(timestamps, f, indent=2)

    @staticmethod
    def autosave_draft(data: Dict[str, Any]):
        """Write current active draft to temporary autosave file for crash recovery."""
        try:
            AUTOSAVE_FILE.parent.mkdir(parents=True, exist_ok=True)
            with open(AUTOSAVE_FILE, "w", encoding="utf-8") as f:
                json.dump({**data, "autosave_time": time.time()}, f, indent=2)
        except Exception:
            pass

    @staticmethod
    def get_autosave_draft() -> Optional[Dict[str, Any]]:
        """Check for recovered draft."""
        if AUTOSAVE_FILE.exists():
            try:
                with open(AUTOSAVE_FILE, "r", encoding="utf-8") as f:
                    return json.load(f)
            except Exception:
                pass
        return None
