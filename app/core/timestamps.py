"""
TTS Studio - Subtitle, Word Timestamps & Timing Metadata Exporter
Exports timing metadata to JSON (word-level and chunk-level), SRT, VTT, and CSV formats.
Auto-organizes exports into dedicated per-conversion folders with audio, text, and narration timestamps.
"""
import re
import json
import time
from datetime import datetime
from pathlib import Path
from dataclasses import dataclass, asdict
from typing import List, Dict, Any, Union, Optional
import numpy as np

from ..config.paths import EXPORTS_DIR


@dataclass
class TimestampItem:
    index: int
    text: str
    start_sec: float
    end_sec: float
    speaker: Optional[str] = None


def generate_export_slug(text: str, custom_prefix: Optional[str] = None, timestamp_format: str = "%Y-%m-%d_%H-%M-%S") -> str:
    """
    Generates a clean, filesystem-safe slug using the first few words of the text
    combined with the current date and time.
    Example: 'A_desperate_tribe_of_Glimmer-Foxes_2026-09-08_08-41-35'
    """
    now_str = datetime.now().strftime(timestamp_format)

    if custom_prefix and custom_prefix.strip():
        # Sanitize custom prefix
        clean_prefix = re.sub(r'[^\w\-\.]', '_', custom_prefix.strip())
        clean_prefix = re.sub(r'_+', '_', clean_prefix).strip('_')
        return f"{clean_prefix}_{now_str}" if clean_prefix else f"synth_{now_str}"

    clean_text = text.strip() if text else ""
    if not clean_text:
        return f"synthesis_{now_str}"

    # Extract first 4 to 6 words (up to ~35 characters)
    words = clean_text.split()
    chosen_words = words[:min(6, len(words))]
    slug_base = " ".join(chosen_words)

    # Remove quotes, markdown asterisks, brackets, and invalid filename characters
    slug_base = re.sub(r'[*_`\"\'\(\)\[\]\{\}<>:\\/\|\?\*]', '', slug_base)
    # Replace whitespace and commas with underscores, preserve hyphens
    slug_base = re.sub(r'[\s,;:.]+', '_', slug_base)
    slug_base = re.sub(r'_+', '_', slug_base).strip('_')

    if not slug_base or len(slug_base) < 2:
        slug_base = "speech_audio"

    # Truncate if overly long
    if len(slug_base) > 40:
        slug_base = slug_base[:40].rstrip('_')

    return f"{slug_base}_{now_str}"


def compute_word_weight(word: str) -> float:
    """
    Computes an acoustic phonetic weight for a word based on characters,
    vowel/syllable counts, and consonant complexity.
    """
    w_clean = re.sub(r'[*_`\"\'\(\)\[\]]', '', word)
    alpha = re.sub(r'[^a-zA-Z0-9]', '', w_clean).lower()
    if not alpha:
        return 1.0

    vowels = len(re.findall(r'[aeiouy]+', alpha))
    consonants = max(0, len(alpha) - vowels)
    syllables = max(1, vowels)

    # Base duration weight proportional to syllables and phonetic length
    base_weight = 0.15 + (syllables * 0.18) + (consonants * 0.04) + (len(alpha) * 0.02)
    return max(0.18, base_weight)


class TimestampManager:
    """Manages subtitle timing generation, word-level narration timestamps, and format exporters."""

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
    def generate_word_timestamps(
        cls,
        text: str,
        duration_sec: float,
        start_offset: float = 0.0,
        audio_samples: Optional[np.ndarray] = None,
        sample_rate: int = 24000
    ) -> Dict[str, Any]:
        """
        Generates high-precision word-level timestamps (seconds and milliseconds)
        matching the exact narration timestamp JSON schema.
        """
        words = text.split()
        if not words or duration_sec <= 0.05:
            return {
                "text": text,
                "duration_seconds": round(duration_sec, 2),
                "words": []
            }

        weights = [compute_word_weight(w) for w in words]
        total_weight = sum(weights)

        # Detect acoustic pause weighting for punctuation
        pause_weights = []
        for i, w in enumerate(words):
            if i == len(words) - 1:
                p = 0.0
            elif re.search(r'[.!?…]+$', w):
                p = 0.35
            elif re.search(r'[,;:\-—]+$', w):
                p = 0.10
            else:
                p = 0.10
            pause_weights.append(p)

        total_pause = sum(pause_weights)
        lead_in = 0.20
        lead_out = 0.15

        # Check voice onset/offset if audio waveform is provided
        if audio_samples is not None and len(audio_samples) > sample_rate * 0.1:
            try:
                frame_len = int(sample_rate * 0.02)
                hop = frame_len // 2
                if len(audio_samples) > frame_len:
                    frames = [audio_samples[i:i + frame_len] for i in range(0, len(audio_samples) - frame_len, hop)]
                    energies = [np.mean(f ** 2) for f in frames]
                    max_e = max(energies) if energies else 1.0
                    if max_e > 1e-6:
                        threshold = max_e * 0.015
                        # Find voice onset
                        onset_idx = 0
                        for idx, e in enumerate(energies):
                            if e > threshold:
                                onset_idx = idx
                                break
                        measured_lead_in = (onset_idx * hop) / sample_rate
                        lead_in = max(0.08, min(0.35, measured_lead_in))
            except Exception:
                pass

        avail_speech_time = duration_sec - lead_in - lead_out - total_pause
        if avail_speech_time <= 0:
            scale = max(0.1, duration_sec / (total_weight + len(words) * 0.1 + 0.3))
            lead_in = 0.10 * scale
            lead_out = 0.10 * scale
            avail_speech_time = max(0.1, duration_sec - lead_in - lead_out)
            total_pause = 0.0
            pause_weights = [0.05 * scale] * len(words)

        word_items: List[Dict[str, Any]] = []
        curr_time = start_offset + lead_in

        for i, (w, wt, pw) in enumerate(zip(words, weights, pause_weights)):
            dur = (wt / total_weight) * avail_speech_time
            dur = max(0.12, dur)
            w_start = round(curr_time, 3)
            w_end = round(curr_time + dur, 3)

            word_items.append({
                "word": w,
                "start": w_start,
                "end": w_end
            })
            curr_time = w_end + pw

        # Ensure last word does not overflow beyond total chunk/segment duration
        max_allowed_end = start_offset + duration_sec
        if word_items and word_items[-1]["end"] > max_allowed_end:
            excess = word_items[-1]["end"] - max_allowed_end
            total_span = max(0.1, word_items[-1]["end"] - word_items[0]["start"])
            for item in word_items:
                rel = (item["start"] - word_items[0]["start"]) / total_span
                rel_end = (item["end"] - word_items[0]["start"]) / total_span
                item["start"] = round(max(0.0, item["start"] - (excess * rel)), 3)
                item["end"] = round(max(item["start"] + 0.05, item["end"] - (excess * rel_end)), 3)

        return {
            "text": text,
            "duration_seconds": round(duration_sec, 2),
            "words": word_items
        }

    @classmethod
    def generate_chunk_word_timestamps(
        cls,
        chunk_text: str,
        chunk_start_sec: float,
        chunk_duration_sec: float,
        audio_chunk: Optional[np.ndarray] = None,
        sample_rate: int = 24000
    ) -> List[Dict[str, Any]]:
        """Generates word timestamps for a single chunk aligned to its start time in the master audio."""
        res = cls.generate_word_timestamps(
            text=chunk_text,
            duration_sec=chunk_duration_sec,
            start_offset=chunk_start_sec,
            audio_samples=audio_chunk,
            sample_rate=sample_rate
        )
        return res.get("words", [])

    @classmethod
    def export_narration_json(
        cls,
        text: str,
        duration_sec: float,
        words: List[Dict[str, Any]],
        output_path: Union[str, Path]
    ) -> str:
        """
        Export complete narration metadata as a root JSON object with text,
        total duration, and word-level timestamps.
        """
        payload = {
            "text": text,
            "duration_seconds": round(duration_sec, 2),
            "words": words
        }
        out = Path(output_path).with_suffix(".json")
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")
        return str(out)

    @classmethod
    def export_srt(cls, items: List[Dict[str, Any]], output_path: Union[str, Path]) -> str:
        """Export timestamps as SubRip (.srt) subtitle file."""
        lines = []
        for idx, item in enumerate(items, 1):
            start = cls.format_srt_time(item.get("start_sec", item.get("start", item.get("start_time", 0.0))))
            end = cls.format_srt_time(item.get("end_sec", item.get("end", item.get("end_time", 0.0))))
            text = item.get("text", item.get("word", "")).strip()
            speaker = item.get("speaker", item.get("speaker_name", ""))
            caption = f"[{speaker}] {text}" if speaker else text

            lines.append(f"{idx}")
            lines.append(f"{start} --> {end}")
            lines.append(f"{caption}\n")

        content = "\n".join(lines)
        out = Path(output_path).with_suffix(".srt")
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(content, encoding="utf-8")
        return str(out)

    @classmethod
    def export_vtt(cls, items: List[Dict[str, Any]], output_path: Union[str, Path]) -> str:
        """Export timestamps as WebVTT (.vtt) file."""
        lines = ["WEBVTT\n"]
        for idx, item in enumerate(items, 1):
            start = cls.format_vtt_time(item.get("start_sec", item.get("start", item.get("start_time", 0.0))))
            end = cls.format_vtt_time(item.get("end_sec", item.get("end", item.get("end_time", 0.0))))
            text = item.get("text", item.get("word", "")).strip()
            lines.append(f"{start} --> {end}")
            lines.append(f"{text}\n")

        content = "\n".join(lines)
        out = Path(output_path).with_suffix(".vtt")
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(content, encoding="utf-8")
        return str(out)

    @classmethod
    def export_json(cls, items: Any, output_path: Union[str, Path]) -> str:
        """Export timing metadata as JSON."""
        out = Path(output_path).with_suffix(".json")
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(json.dumps(items, indent=2, ensure_ascii=False), encoding="utf-8")
        return str(out)

    @classmethod
    def save_export_bundle(
        cls,
        text: str,
        audio_array: np.ndarray,
        sample_rate: int = 24000,
        custom_slug: Optional[str] = None,
        format_ext: str = "wav",
        word_timestamps: Optional[List[Dict[str, Any]]] = None,
        chunk_timestamps: Optional[List[Dict[str, Any]]] = None
    ) -> Dict[str, Any]:
        """
        Creates a dedicated folder in the exports directory and saves:
        1. Audio file ({slug}.wav / {slug}.mp3)
        2. Full text file ({slug}.txt)
        3. Word-level narration timestamp JSON ({slug}.json)
        4. Subtitles ({slug}.srt and {slug}.vtt)
        """
        from .audio import AudioProcessor

        slug = generate_export_slug(text, custom_prefix=custom_slug)
        folder_path = EXPORTS_DIR / slug
        folder_path.mkdir(parents=True, exist_ok=True)

        total_duration = len(audio_array) / max(1, sample_rate)

        # 1. Generate word-level timestamps if not provided
        if word_timestamps is None:
            ts_data = cls.generate_word_timestamps(
                text=text,
                duration_sec=total_duration,
                audio_samples=audio_array,
                sample_rate=sample_rate
            )
            words = ts_data.get("words", [])
        else:
            words = word_timestamps

        # 2. Save Audio File
        fmt = format_ext.lower().replace(".", "")
        audio_file_path = folder_path / f"{slug}.{fmt}"
        saved_audio = AudioProcessor.export_audio(audio_array, audio_file_path, sample_rate, fmt)

        # 3. Save Entire Text File
        text_file_path = folder_path / f"{slug}.txt"
        text_file_path.write_text(text, encoding="utf-8")

        # 4. Save Narration Timestamp JSON File (exact user format)
        json_file_path = folder_path / f"{slug}.json"
        cls.export_narration_json(text, total_duration, words, json_file_path)

        # 5. Save Subtitles (SRT and VTT)
        subtitle_items = chunk_timestamps if chunk_timestamps else words
        srt_file_path = folder_path / f"{slug}.srt"
        vtt_file_path = folder_path / f"{slug}.vtt"
        if subtitle_items:
            cls.export_srt(subtitle_items, srt_file_path)
            cls.export_vtt(subtitle_items, vtt_file_path)

        return {
            "slug": slug,
            "folder_path": str(folder_path),
            "audio_path": str(saved_audio),
            "text_path": str(text_file_path),
            "json_path": str(json_file_path),
            "srt_path": str(srt_file_path) if srt_file_path.exists() else None,
            "vtt_path": str(vtt_file_path) if vtt_file_path.exists() else None,
            "duration_sec": round(total_duration, 2),
            "words": words
        }
