"""
TTS Studio - Batch Generation Queue & Job Coordinator
"""
import os
import time
import threading
from pathlib import Path
from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional, Callable
from concurrent.futures import ThreadPoolExecutor

from .tts_service import TTSService, SynthesisResult
from ..core.resources import ResourceManager


@dataclass
class BatchJob:
    job_id: str
    input_file: str
    output_filename: str
    text_content: str
    engine: str
    voice: str
    speed: float = 1.0
    pitch: float = 0.0
    status: str = "waiting"  # waiting, processing, completed, failed, cancelled
    duration_sec: float = 0.0
    error: Optional[str] = None
    output_path: Optional[str] = None


class BatchService:
    """Thread-safe batch generation queue and worker executor."""

    def __init__(self):
        self.jobs: List[BatchJob] = []
        self._lock = threading.Lock()
        self._is_running = False
        self._pause_requested = False
        self._cancel_requested = False

    def add_files(self, file_paths: List[str], engine: str, voice: str, speed: float = 1.0, pitch: float = 0.0):
        with self._lock:
            for p in file_paths:
                path = Path(p)
                if path.exists() and path.is_file():
                    try:
                        text = path.read_text(encoding="utf-8", errors="ignore").strip()
                        if text:
                            job = BatchJob(
                                job_id=f"batch_{int(time.time()*1000)}_{len(self.jobs)}",
                                input_file=path.name,
                                output_filename=f"{path.stem}_audio",
                                text_content=text,
                                engine=engine,
                                voice=voice,
                                speed=speed,
                                pitch=pitch
                            )
                            self.jobs.append(job)
                    except Exception:
                        pass

    def start_processing(self, on_progress_callback: Optional[Callable[[Dict[str, Any]], None]] = None):
        if self._is_running:
            return

        self._is_running = True
        self._pause_requested = False
        self._cancel_requested = False

        def _worker():
            max_workers = ResourceManager.get_max_recommended_concurrency("kokoro")
            
            with ThreadPoolExecutor(max_workers=max_workers) as executor:
                for job in self.jobs:
                    if self._cancel_requested:
                        with self._lock:
                            if job.status == "waiting":
                                job.status = "cancelled"
                        continue

                    while self._pause_requested:
                        time.sleep(0.5)

                    with self._lock:
                        job.status = "processing"

                    if on_progress_callback:
                        on_progress_callback(self.get_summary())

                    # Execute synthesis
                    res = TTSService.synthesize_text(
                        text=job.text_content,
                        voice=job.voice,
                        engine_hint=job.engine,
                        speed=job.speed,
                        pitch=job.pitch,
                        output_filename=job.output_filename
                    )

                    with self._lock:
                        if res.success:
                            job.status = "completed"
                            job.duration_sec = res.duration_sec
                            job.output_path = res.audio_path
                        else:
                            job.status = "failed"
                            job.error = res.error

                    if on_progress_callback:
                        on_progress_callback(self.get_summary())

            self._is_running = False

        threading.Thread(target=_worker, daemon=True).start()

    def pause(self):
        self._pause_requested = True

    def resume(self):
        self._pause_requested = False

    def cancel(self):
        self._cancel_requested = True
        self._is_running = False

    def clear(self):
        with self._lock:
            self.jobs.clear()

    def get_summary(self) -> Dict[str, Any]:
        with self._lock:
            total = len(self.jobs)
            completed = sum(1 for j in self.jobs if j.status == "completed")
            processing = sum(1 for j in self.jobs if j.status == "processing")
            failed = sum(1 for j in self.jobs if j.status == "failed")
            waiting = sum(1 for j in self.jobs if j.status == "waiting")
            return {
                "total": total,
                "completed": completed,
                "processing": processing,
                "failed": failed,
                "waiting": waiting,
                "is_running": self._is_running,
                "is_paused": self._pause_requested,
                "jobs": [j.__dict__ for j in self.jobs]
            }


# Global Batch Service
BATCH_SERVICE = BatchService()
