"""
VoxCraft Studio - Local SQLite Storage & Project Persistence
Handles generation history, custom voice presets, and saved podcast studio projects.
"""
import sqlite3
import json
import time
from pathlib import Path
from typing import List, Dict, Any, Optional

from .config import DATA_DIR

DB_PATH = DATA_DIR / "voxcraft_studio.db"


class ProjectStore:
    """Manages SQLite storage for history, custom voice presets, and podcast scripts."""

    def __init__(self, db_path: Path = DB_PATH):
        self.db_path = db_path
        self._init_db()

    def _get_connection(self) -> sqlite3.Connection:
        conn = sqlite3.connect(str(self.db_path))
        conn.row_factory = sqlite3.Row
        return conn

    def _init_db(self):
        with self._get_connection() as conn:
            cursor = conn.cursor()
            
            # 1. History Table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS generation_history (
                    id TEXT PRIMARY KEY,
                    timestamp REAL,
                    text TEXT,
                    engine TEXT,
                    voice TEXT,
                    speed REAL,
                    pitch REAL,
                    duration_sec REAL,
                    audio_path TEXT,
                    audio_data_uri TEXT
                )
            """)

            # 2. Voice Presets Table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS voice_presets (
                    id TEXT PRIMARY KEY,
                    name TEXT,
                    engine TEXT,
                    base_voice TEXT,
                    speed REAL,
                    pitch REAL,
                    voice_blend_json TEXT,
                    tags_json TEXT,
                    created_at REAL
                )
            """)

            # 3. Podcast Projects Table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS podcast_projects (
                    id TEXT PRIMARY KEY,
                    title TEXT,
                    description TEXT,
                    speakers_json TEXT,
                    script_json TEXT,
                    updated_at REAL
                )
            """)

            conn.commit()

    # --- History Management ---
    def add_history_entry(self, entry: Dict[str, Any]) -> bool:
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    INSERT OR REPLACE INTO generation_history 
                    (id, timestamp, text, engine, voice, speed, pitch, duration_sec, audio_path, audio_data_uri)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    entry.get("id", str(time.time())),
                    entry.get("timestamp", time.time()),
                    entry.get("text", ""),
                    entry.get("engine", "kokoro"),
                    entry.get("voice", "af_bella"),
                    entry.get("speed", 1.0),
                    entry.get("pitch", 0.0),
                    entry.get("duration_sec", 0.0),
                    entry.get("audio_path", ""),
                    entry.get("audio_data_uri", "")[:100000] if entry.get("audio_data_uri") else ""
                ))
                conn.commit()
                return True
        except Exception:
            return False

    def get_history(self, limit: int = 50) -> List[Dict[str, Any]]:
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM generation_history ORDER BY timestamp DESC LIMIT ?", (limit,))
            rows = cursor.fetchall()
            return [dict(r) for r in rows]

    def clear_history(self) -> bool:
        with self._get_connection() as conn:
            conn.cursor().execute("DELETE FROM generation_history")
            conn.commit()
            return True

    # --- Preset Management ---
    def save_preset(self, preset: Dict[str, Any]) -> bool:
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT OR REPLACE INTO voice_presets
                (id, name, engine, base_voice, speed, pitch, voice_blend_json, tags_json, created_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                preset.get("id", f"preset_{int(time.time())}"),
                preset.get("name", "Custom Voice"),
                preset.get("engine", "kokoro"),
                preset.get("base_voice", "af_bella"),
                preset.get("speed", 1.0),
                preset.get("pitch", 0.0),
                json.dumps(preset.get("voice_blend", {})),
                json.dumps(preset.get("tags", [])),
                time.time()
            ))
            conn.commit()
            return True

    def get_presets(self) -> List[Dict[str, Any]]:
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM voice_presets ORDER BY created_at DESC")
            rows = cursor.fetchall()
            results = []
            for r in rows:
                item = dict(r)
                item["voice_blend"] = json.loads(item.get("voice_blend_json") or "{}")
                item["tags"] = json.loads(item.get("tags_json") or "[]")
                results.append(item)
            return results

    # --- Podcast Project Management ---
    def save_podcast_project(self, project: Dict[str, Any]) -> bool:
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT OR REPLACE INTO podcast_projects
                (id, title, description, speakers_json, script_json, updated_at)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (
                project.get("id", f"podcast_{int(time.time())}"),
                project.get("title", "Untitled Podcast"),
                project.get("description", ""),
                json.dumps(project.get("speakers", [])),
                json.dumps(project.get("script", [])),
                time.time()
            ))
            conn.commit()
            return True

    def get_podcast_projects(self) -> List[Dict[str, Any]]:
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM podcast_projects ORDER BY updated_at DESC")
            rows = cursor.fetchall()
            results = []
            for r in rows:
                item = dict(r)
                item["speakers"] = json.loads(item.get("speakers_json") or "[]")
                item["script"] = json.loads(item.get("script_json") or "[]")
                results.append(item)
            return results


# Global store instance
PROJECT_STORE = ProjectStore()
