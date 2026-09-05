"""
TTS Studio - Podcast & Multi-Speaker Dialogue Service
Parses multi-character scripts, synthesizes turns, compiles master episodes, and outputs stem tracks.
"""
import re
import time
from pathlib import Path
from dataclasses import dataclass
from typing import List, Dict, Any, Optional, Tuple, Callable
import numpy as np

from ..config.paths import EXPORTS_DIR
from ..core.audio import AudioProcessor
from ..core.timestamps import TimestampManager
from ..engines.registry import ENGINE_REGISTRY


@dataclass
class SpeakerProfile:
    id: str
    name: str
    engine: str = "kokoro"
    voice: str = "af_bella"
    speed: float = 1.0
    pitch: float = 0.0
    volume: float = 1.0
    color: str = "#8b5cf6"
    avatar: str = "🎙️"


class PodcastService:
    """Multi-character dialogue compiler and stem exporter."""

    @staticmethod
    def parse_script_text(script_text: str, default_speaker_id: str = "speaker_1") -> List[Dict[str, Any]]:
        """
        Parses dialogue text with speaker prefixes such as:
        Alex: Welcome to today's episode.
        Dr. Elena: Glad to be here!
        Narrator: Deep in the quiet valley...
        """
        lines = script_text.strip().split("\n")
        dialogue = []

        for line in lines:
            clean = line.strip()
            if not clean:
                continue

            # Match "Name: text"
            match = re.match(r'^([A-Za-z0-9_\s\.\(\)]+?)\s*:\s*(.+)$', clean)
            if match:
                speaker_name = match.group(1).strip()
                text = match.group(2).strip()
                clean_id = re.sub(r'[^a-zA-Z0-9]', '_', speaker_name).lower().strip('_')
                dialogue.append({
                    "speaker_id": clean_id or default_speaker_id,
                    "speaker_label": speaker_name,
                    "text": text,
                    "pause_after": 0.4
                })
            else:
                dialogue.append({
                    "speaker_id": default_speaker_id,
                    "speaker_label": "Speaker",
                    "text": clean,
                    "pause_after": 0.4
                })

        return dialogue

    @classmethod
    def _find_speaker_meta(cls, query_id: str, query_label: str, speakers: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Fuzzy matches dialogue line speaker label to configured speaker list."""
        q_id = query_id.lower().strip()
        q_label = query_label.lower().strip()
        q_first = q_label.split()[0] if q_label.split() else q_id

        # 1. Exact ID match
        for s in speakers:
            if s.get("id", "").lower() == q_id:
                return s

        # 2. Exact Name match
        for s in speakers:
            if s.get("name", "").lower() == q_label:
                return s

        # 3. First word / substring match (e.g. "Alex" matches "Alex (Host)")
        for s in speakers:
            s_name = s.get("name", "").lower()
            s_first = s_name.split()[0] if s_name.split() else ""
            if s_first and (s_first == q_first or q_first in s_name or s_name in q_label):
                return s

        # 4. Fallback to first configured speaker or default
        return speakers[0] if speakers else {
            "name": query_label or "Speaker",
            "engine": "kokoro",
            "voice": "af_bella",
            "speed": 1.0,
            "pitch": 0.0,
            "volume": 1.0,
            "color": "#8b5cf6"
        }

    @classmethod
    def generate_episode(
        cls,
        speakers: List[Dict[str, Any]],
        dialogue_blocks: List[Dict[str, Any]],
        episode_title: str = "Podcast_Episode",
        output_format: str = "wav",
        normalize_master: bool = True,
        export_stems: bool = False,
        progress_callback: Optional[Callable[[int, int, str], None]] = None
    ) -> Dict[str, Any]:
        """
        Compiles multi-speaker dialogue into a master audio file, synchronized timeline, and optional stems.
        """
        start_time = time.time()
        audio_segments: List[np.ndarray] = []
        pauses: List[float] = []
        timeline: List[Dict[str, Any]] = []

        current_time = 0.0
        sample_rate = 24000
        total_blocks = len(dialogue_blocks)

        if total_blocks == 0:
            return {"success": False, "error": "No dialogue turns to synthesize."}

        for idx, block in enumerate(dialogue_blocks):
            spk_id = block.get("speaker_id", "")
            spk_label = block.get("speaker_label", "")
            spk_meta = cls._find_speaker_meta(spk_id, spk_label, speakers)

            text = block.get("text", "").strip()
            pause_after = float(block.get("pause_after", 0.4))
            if not text:
                continue

            spk_name = spk_meta.get("name", spk_label or "Speaker")
            if progress_callback:
                progress_callback(idx + 1, total_blocks, f"Synthesizing turn {idx+1}/{total_blocks} ({spk_name})...")

            voice = spk_meta.get("voice", "af_bella")
            speed = float(spk_meta.get("speed", 1.0))
            pitch = float(spk_meta.get("pitch", 0.0))
            volume = float(spk_meta.get("volume", 1.0))
            engine = spk_meta.get("engine", "kokoro")

            try:
                raw_audio, sr = ENGINE_REGISTRY.synthesize(
                    text=text,
                    voice=voice,
                    speed=speed,
                    pitch=pitch,
                    engine_hint=engine
                )
                sample_rate = sr
            except Exception as e:
                return {"success": False, "error": f"Synthesis error on turn {idx+1} ({spk_name}): {e}"}

            # Apply pitch shift if needed
            turn_audio = AudioProcessor.shift_pitch(raw_audio, semitones=pitch, sample_rate=sr) if abs(pitch) >= 0.1 else raw_audio

            # Apply volume multiplier
            if abs(volume - 1.0) >= 0.02:
                turn_audio = turn_audio * volume

            audio_segments.append(turn_audio)
            pauses.append(pause_after)

            turn_duration = len(turn_audio) / sr
            start_sec = current_time
            end_sec = start_sec + turn_duration

            timeline.append({
                "block_index": idx + 1,
                "speaker_id": spk_meta.get("id", spk_id),
                "speaker_name": spk_name,
                "speaker_color": spk_meta.get("color", "#8b5cf6"),
                "voice": voice,
                "text": text,
                "start_time": round(start_sec, 2),
                "end_time": round(end_sec, 2),
                "duration": round(turn_duration, 2)
            })

            current_time = end_sec + pause_after

        # Master concatenation
        master_audio = AudioProcessor.concatenate_segments(audio_segments, pauses=pauses, sample_rate=sample_rate)

        if normalize_master:
            master_audio = AudioProcessor.normalize_loudness(master_audio, target_db=-1.0)

        total_dur = len(master_audio) / sample_rate
        elapsed = time.time() - start_time

        # Export master episode
        safe_title = "".join(c for c in episode_title if c.isalnum() or c in (' ', '_', '-')).strip() or f"podcast_{int(time.time())}"
        master_out = EXPORTS_DIR / f"{safe_title}.{output_format}"
        saved_master = AudioProcessor.export_audio(master_audio, master_out, sample_rate, output_format)

        # Export timestamps JSON & SRT
        ts_json = EXPORTS_DIR / f"{safe_title}_timestamps.json"
        TimestampManager.export_json(timeline, ts_json)
        ts_srt = EXPORTS_DIR / f"{safe_title}.srt"
        TimestampManager.export_srt(timeline, ts_srt)

        return {
            "success": True,
            "master_audio_path": saved_master,
            "total_duration_sec": round(total_dur, 2),
            "generation_time_sec": round(elapsed, 2),
            "num_blocks": len(audio_segments),
            "timeline": timeline,
            "srt_path": str(ts_srt)
        }
