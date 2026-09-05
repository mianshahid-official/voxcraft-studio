"""
VoxCraft Studio - Podcast & Multi-Speaker Dialogue Compiler
Compiles multi-character scripts into unified podcast episodes and synchronized timelines.
"""
import time
import uuid
from typing import List, Dict, Any, Optional, Tuple
from pathlib import Path
import numpy as np

from .engines import ENGINE_REGISTRY
from .audio_processor import AudioProcessor
from .config import EXPORTS_DIR, DEFAULT_SAMPLE_RATE


class PodcastGenerator:
    """Manages multi-speaker dialogue synthesis, timeline compilation, and stem exports."""

    @staticmethod
    def generate_podcast(
        speakers: List[Dict[str, Any]],
        dialogue_blocks: List[Dict[str, Any]],
        master_effects: Optional[Dict[str, Any]] = None,
        progress_callback: Optional[Any] = None
    ) -> Dict[str, Any]:
        """
        Synthesizes each dialogue turn and mixes them into a continuous master audio track with timeline markers.
        """
        # Map speakers by ID
        speaker_map = {s["id"]: s for s in speakers}
        
        sample_rate = DEFAULT_SAMPLE_RATE
        audio_segments: List[np.ndarray] = []
        pause_list: List[float] = []
        timeline: List[Dict[str, Any]] = []

        current_time_sec = 0.0
        total_blocks = len(dialogue_blocks)

        for idx, block in enumerate(dialogue_blocks):
            speaker_id = block.get("speaker_id")
            text = block.get("text", "").strip()
            pause_after = float(block.get("pause_after", 0.6))
            
            if not text:
                continue

            speaker_meta = speaker_map.get(speaker_id, {
                "name": "Speaker",
                "engine": "kokoro",
                "voice": "af_bella",
                "speed": 1.0,
                "pitch": 0.0,
                "color": "#8b5cf6"
            })

            # Custom block overrides or speaker defaults
            speed = float(block.get("speed", speaker_meta.get("speed", 1.0)))
            pitch = float(block.get("pitch", speaker_meta.get("pitch", 0.0)))
            voice_id = speaker_meta.get("voice", "af_bella")
            engine_hint = speaker_meta.get("engine", "kokoro")

            # Synthesize turn
            raw_audio, sr = ENGINE_REGISTRY.synthesize(
                text=text,
                voice=voice_id,
                speed=speed,
                pitch=pitch,
                engine_hint=engine_hint
            )

            # Apply per-turn pitch / speed DSP if not handled in-engine
            processed_turn = AudioProcessor.process_chain(
                raw_audio,
                sample_rate=sr,
                speed=1.0,  # speed already applied in engine
                pitch=pitch,
                volume=1.0,
                normalize=False
            )

            audio_segments.append(processed_turn)
            pause_list.append(pause_after)

            turn_duration = len(processed_turn) / sr
            start_time = current_time_sec
            end_time = start_time + turn_duration

            timeline.append({
                "block_index": idx,
                "speaker_id": speaker_id,
                "speaker_name": speaker_meta.get("name", "Speaker"),
                "speaker_color": speaker_meta.get("color", "#8b5cf6"),
                "speaker_avatar": speaker_meta.get("avatar", "🎙️"),
                "text": text,
                "start_time": round(start_time, 2),
                "end_time": round(end_time, 2),
                "duration": round(turn_duration, 2)
            })

            current_time_sec = end_time + pause_after

            if progress_callback:
                progress_callback(idx + 1, total_blocks)

        # Concatenate all segments with pauses
        master_audio = AudioProcessor.concatenate_segments(
            audio_segments,
            pause_seconds_list=pause_list,
            sample_rate=sample_rate
        )

        # Apply master effects if requested (e.g. Master Reverb, Compression, Normalization)
        if master_effects:
            master_audio = AudioProcessor.process_chain(
                master_audio,
                sample_rate=sample_rate,
                speed=float(master_effects.get("speed", 1.0)),
                pitch=float(master_effects.get("pitch", 0.0)),
                volume=float(master_effects.get("volume", 1.0)),
                bass=float(master_effects.get("bass", 0.0)),
                treble=float(master_effects.get("treble", 0.0)),
                reverb=float(master_effects.get("reverb", 0.0)),
                normalize=master_effects.get("normalize", True)
            )

        # Generate base64 audio URI for immediate browser playback
        audio_uri = AudioProcessor.to_base64_data_uri(master_audio, sample_rate)
        total_duration = len(master_audio) / sample_rate

        return {
            "success": True,
            "total_duration_sec": round(total_duration, 2),
            "num_blocks": len(dialogue_blocks),
            "audio_data_uri": audio_uri,
            "timeline": timeline,
            "sample_rate": sample_rate
        }

    @staticmethod
    def export_podcast_episode(
        master_audio_array: np.ndarray,
        episode_title: str,
        format_ext: str = "mp3",
        sample_rate: int = DEFAULT_SAMPLE_RATE
    ) -> str:
        """Export master podcast episode to exports directory."""
        safe_title = "".join(c for c in episode_title if c.isalnum() or c in (' ', '_', '-')).strip()
        if not safe_title:
            safe_title = f"Podcast_{int(time.time())}"
        filename = f"{safe_title}.{format_ext}"
        out_path = EXPORTS_DIR / filename
        return AudioProcessor.export_audio(master_audio_array, out_path, sample_rate, format_ext)
