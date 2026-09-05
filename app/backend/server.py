"""
VoxCraft Studio - Desktop API Bridge & Local ASGI Server
Provides dual communication channels: PyWebView Native JS Bridge and FastAPI REST/WebSocket endpoints.
"""
import os
import sys
import time
import json
import uuid
import base64
import logging
from pathlib import Path
from typing import Dict, Any, List, Optional

from fastapi import FastAPI, UploadFile, File, Form, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import JSONResponse, FileResponse
import uvicorn

from .config import (
    BASE_DIR,
    APP_DIR,
    FRONTEND_DIR,
    EXPORTS_DIR,
    SAMPLES_DIR,
    DEFAULT_SAMPLE_RATE
)
from .hardware import get_system_diagnostics
from .model_manager import ModelManager
from .voice_catalog import get_all_voices, filter_voices, get_voice_by_id
from .audio_processor import AudioProcessor
from .engines import ENGINE_REGISTRY
from .podcast_generator import PodcastGenerator
from .project_store import PROJECT_STORE

logger = logging.getLogger("VoxCraft.Server")

# Initialize FastAPI App
api_app = FastAPI(title="VoxCraft Studio API", version="1.0.0")

api_app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class DesktopAPIBridge:
    """
    Exposed directly to window.pywebview.api in Desktop App mode.
    All methods return JSON-serializable dictionaries.
    """

    def get_system_status(self) -> Dict[str, Any]:
        """Hardware specifications and model readiness."""
        diag = get_system_diagnostics()
        models = ModelManager.get_local_model_status()
        engines = ENGINE_REGISTRY.get_all_statuses()
        return {
            "diagnostics": diag,
            "models": models,
            "engines": engines
        }

    def get_voices(self, engine: str = "all", gender: str = "all", language: str = "all", query: str = "") -> List[Dict[str, Any]]:
        """Retrieve filtered voices."""
        return filter_voices(engine=engine, gender=gender, language=language, search_query=query)

    def synthesize_speech(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """
        Synthesize speech for single text or batch blocks.
        """
        text = params.get("text", "").strip()
        voice_id = params.get("voice", "af_bella")
        speed = float(params.get("speed", 1.0))
        pitch = float(params.get("pitch", 0.0))
        volume = float(params.get("volume", 1.0))
        bass = float(params.get("bass", 0.0))
        treble = float(params.get("treble", 0.0))
        reverb = float(params.get("reverb", 0.0))
        engine_hint = params.get("engine", None)
        voice_blend = params.get("voice_blend", None)
        ref_audio_path = params.get("ref_audio_path", None)
        ref_text = params.get("ref_text", None)

        if not text:
            return {"success": False, "error": "Text cannot be empty."}

        start_time = time.time()

        try:
            # 1. Synthesize through engine
            raw_audio, sr = ENGINE_REGISTRY.synthesize(
                text=text,
                voice=voice_id,
                speed=speed,
                pitch=pitch,
                engine_hint=engine_hint,
                voice_blend=voice_blend,
                ref_audio_path=ref_audio_path,
                ref_text=ref_text
            )

            # 2. Apply DSP effects chain
            processed_audio = AudioProcessor.process_chain(
                raw_audio,
                sample_rate=sr,
                speed=1.0,
                pitch=pitch,
                volume=volume,
                bass=bass,
                treble=treble,
                reverb=reverb,
                normalize=True
            )

            duration = len(processed_audio) / sr
            gen_time = time.time() - start_time
            data_uri = AudioProcessor.to_base64_data_uri(processed_audio, sr)
            audio_id = f"gen_{int(time.time() * 1000)}"

            # Save to history
            history_item = {
                "id": audio_id,
                "timestamp": time.time(),
                "text": text,
                "engine": engine_hint or voice_id.split("_")[0],
                "voice": voice_id,
                "speed": speed,
                "pitch": pitch,
                "duration_sec": round(duration, 2),
                "audio_data_uri": data_uri
            }
            PROJECT_STORE.add_history_entry(history_item)

            return {
                "success": True,
                "audio_id": audio_id,
                "audio_data_uri": data_uri,
                "duration_sec": round(duration, 2),
                "generation_time_sec": round(gen_time, 2),
                "sample_rate": sr,
                "engine_used": engine_hint or "kokoro"
            }
        except Exception as e:
            logger.error(f"Synthesis error: {e}", exc_info=True)
            return {"success": False, "error": str(e)}

    def generate_podcast_episode(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """Synthesize multi-speaker podcast script."""
        speakers = payload.get("speakers", [])
        dialogue = payload.get("dialogue", [])
        effects = payload.get("master_effects", {})
        
        try:
            result = PodcastGenerator.generate_podcast(
                speakers=speakers,
                dialogue_blocks=dialogue,
                master_effects=effects
            )
            return result
        except Exception as e:
            return {"success": False, "error": str(e)}

    def trigger_model_download(self, model_key: str) -> Dict[str, Any]:
        """Start downloading model."""
        ok = ModelManager.start_model_download(model_key)
        return {"success": ok, "model_key": model_key}

    def get_download_status(self, model_key: str) -> Dict[str, Any]:
        """Poll model download status."""
        return ModelManager.get_download_progress(model_key)

    def export_audio_file(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Export audio to output file."""
        data_uri = params.get("audio_data_uri", "")
        filename = params.get("filename", "voxcraft_output")
        fmt = params.get("format", "wav")

        if not data_uri.startswith("data:audio/"):
            return {"success": False, "error": "Invalid audio data URI"}

        try:
            b64_data = data_uri.split(",", 1)[1]
            wav_bytes = base64.b64decode(b64_data)
            audio_array, sr = AudioProcessor.wav_bytes_to_numpy(wav_bytes)

            out_file = EXPORTS_DIR / f"{filename}.{fmt}"
            saved_path = AudioProcessor.export_audio(audio_array, out_file, sr, fmt)
            return {"success": True, "saved_path": str(saved_path), "filename": out_file.name}
        except Exception as e:
            return {"success": False, "error": str(e)}

    def get_history_list(self) -> List[Dict[str, Any]]:
        return PROJECT_STORE.get_history(limit=50)

    def clear_history_list(self) -> Dict[str, Any]:
        ok = PROJECT_STORE.clear_history()
        return {"success": ok}

    def save_voice_preset(self, preset: Dict[str, Any]) -> Dict[str, Any]:
        ok = PROJECT_STORE.save_preset(preset)
        return {"success": ok}

    def get_voice_presets(self) -> List[Dict[str, Any]]:
        return PROJECT_STORE.get_presets()

    def save_podcast_project(self, project: Dict[str, Any]) -> Dict[str, Any]:
        ok = PROJECT_STORE.save_podcast_project(project)
        return {"success": ok}

    def get_podcast_projects(self) -> List[Dict[str, Any]]:
        return PROJECT_STORE.get_podcast_projects()


# Instance of API bridge
DESKTOP_BRIDGE = DesktopAPIBridge()


# --- REST API Endpoints ---
@api_app.get("/api/system/status")
async def api_system_status():
    return DESKTOP_BRIDGE.get_system_status()

@api_app.get("/api/voices")
async def api_voices(engine: str = "all", gender: str = "all", language: str = "all", query: str = ""):
    return DESKTOP_BRIDGE.get_voices(engine, gender, language, query)

@api_app.post("/api/tts/synthesize")
async def api_synthesize(payload: Dict[str, Any]):
    return DESKTOP_BRIDGE.synthesize_speech(payload)

@api_app.post("/api/podcast/generate")
async def api_podcast_generate(payload: Dict[str, Any]):
    return DESKTOP_BRIDGE.generate_podcast_episode(payload)

@api_app.post("/api/models/download")
async def api_model_download(payload: Dict[str, Any]):
    model_key = payload.get("model_key", "")
    return DESKTOP_BRIDGE.trigger_model_download(model_key)

@api_app.get("/api/models/progress/{model_key}")
async def api_model_progress(model_key: str):
    return DESKTOP_BRIDGE.get_download_status(model_key)

@api_app.post("/api/export")
async def api_export(payload: Dict[str, Any]):
    return DESKTOP_BRIDGE.export_audio_file(payload)

@api_app.get("/api/history")
async def api_history():
    return DESKTOP_BRIDGE.get_history_list()

@api_app.get("/api/presets")
async def api_presets():
    return DESKTOP_BRIDGE.get_voice_presets()

@api_app.post("/api/presets")
async def api_save_preset(payload: Dict[str, Any]):
    return DESKTOP_BRIDGE.save_voice_preset(payload)

@api_app.get("/api/podcasts")
async def api_podcasts():
    return DESKTOP_BRIDGE.get_podcast_projects()

@api_app.post("/api/podcasts")
async def api_save_podcast(payload: Dict[str, Any]):
    return DESKTOP_BRIDGE.save_podcast_project(payload)

# Mount Frontend Static Assets
if FRONTEND_DIR.exists():
    api_app.mount("/", StaticFiles(directory=str(FRONTEND_DIR), html=True), name="frontend")
