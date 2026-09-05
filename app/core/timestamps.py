"""
TTS Studio - Subtitle & Timing Metadata Exporter
Exports timing metadata to JSON, SRT, VTT, and CSV formats for video synchronization.
"""
import json
from pathlib import Path
from dataclasses import dataclass, asdict
from typing import List, Dict, Any, Union, Optional


@dataclass
class TimestampItem:
    index: int
    text: str
    start_sec: float
    end_sec: float
    speaker: Optional[str] = None


class TimestampManager:
    """Manages subtitle timing generation and format exporters."""

    @staticmethod
    def format_srt_time(seconds: float) -> str:
        """Format seconds to 00:00:00,000 SRT format."""
        hrs = int(seconds // 3600)
        mins = int((seconds % 3600) // 60)
        secs = int(seconds % 60)
        millis = int(round((seconds - int(seconds)) * 1000))
        return f"{hrs:02d}:{mins:02d}:{secs:02d},{millis:03d}"

    @staticmethod
    def format_vtt_time(seconds: float) -> str:
        """Format seconds to 00:00:00.000 WebVTT format."""
        hrs = int(seconds // 3600)
        mins = int((seconds % 3600) // 60)
        secs = int(seconds % 60)
        millis = int(round((seconds - int(seconds)) * 1000))
        return f"{hrs:02d}:{mins:02d}:{secs:02d}.{millis:03d}"

    @classmethod
    def export_srt(cls, items: List[Dict[str, Any]], output_path: Union[str, Path]) -> str:
        """Export timestamps as SubRip (.srt) subtitle file."""
        lines = []
        for idx, item in enumerate(items, 1):
            start = cls.format_srt_time(item.get("start_sec", item.get("start_time", 0.0)))
            end = cls.format_srt_time(item.get("end_sec", item.get("end_time", 0.0)))
            text = item.get("text", "").strip()
            speaker = item.get("speaker", item.get("speaker_name", ""))
            caption = f"[{speaker}] {text}" if speaker else text

            lines.append(f"{idx}")
            lines.append(f"{start} --> {end}")
            lines.append(f"{caption}\n")

        content = "\n".join(lines)
        out = Path(output_path).with_suffix(".srt")
        out.write_text(content, encoding="utf-8")
        return str(out)

    @classmethod
    def export_vtt(cls, items: List[Dict[str, Any]], output_path: Union[str, Path]) -> str:
        """Export timestamps as WebVTT (.vtt) file."""
        lines = ["WEBVTT\n"]
        for idx, item in enumerate(items, 1):
            start = cls.format_vtt_time(item.get("start_sec", item.get("start_time", 0.0)))
            end = cls.format_vtt_time(item.get("end_sec", item.get("end_time", 0.0)))
            text = item.get("text", "").strip()
            lines.append(f"{start} --> {end}")
            lines.append(f"{text}\n")

        content = "\n".join(lines)
        out = Path(output_path).with_suffix(".vtt")
        out.write_text(content, encoding="utf-8")
        return str(out)

    @classmethod
    def export_json(cls, items: List[Dict[str, Any]], output_path: Union[str, Path]) -> str:
        """Export precise timing metadata as JSON."""
        out = Path(output_path).with_suffix(".json")
        out.write_text(json.dumps(items, indent=2), encoding="utf-8")
        return str(out)
