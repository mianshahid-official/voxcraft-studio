"""
TTS Studio - Speech Synthesis Service
Coordinates single text & long-form multi-chunk narration with retryable chunks and timestamps.
"""
import time
from pathlib import Path
from dataclasses import dataclass
from typing import Dict, Any, List, Optional, Tuple, Callable
import numpy as np

from ..config.paths import EXPORTS_DIR, CACHE_DIR
from ..core.audio import AudioProcessor
from ..core.chunking import TextChunker, TextChunk
from ..core.normalization import TextNormalizer
from ..core.timestamps import TimestampManager
from ..engines.registry import ENGINE_REGISTRY


@dataclass
class SynthesisResult:
    success: bool
    audio_path: Optional[str]
    audio_data_uri: Optional[str]
    duration_sec: float
    generation_time_sec: float
    realtime_factor: float
    num_chunks: int
    sample_rate: int
    timestamps: List[Dict[str, Any]]
    error: Optional[str] = None


class TTSService:
    """Service handling text synthesis jobs, long-form chunking, and timestamp generation."""

    @staticmethod
    def synthesize_text(
        text: str,
        voice: str = "af_bella",
        engine_hint: Optional[str] = None,
        speed: float = 1.0,
        pitch: float = 0.0,
        volume: float = 1.0,
        normalize_audio: bool = True,
        custom_dict: Optional[Dict[str, str]] = None,
        voice_blend: Optional[Dict[str, Any]] = None,
        ref_audio_path: Optional[str] = None,
        ref_text: Optional[str] = None,
        output_filename: Optional[str] = None,
        progress_callback: Optional[Callable[[int, int, str], None]] = None
    ) -> SynthesisResult:
        """
        Executes text normalization, chunking if long-form, synthesis, DSP effects, and exports.
        """
        start_time = time.time()
        clean_text = TextNormalizer.preprocess(text, custom_dict)

        if not clean_text:
            return SynthesisResult(
                success=False, audio_path=None, audio_data_uri=None,
                duration_sec=0, generation_time_sec=0, realtime_factor=0,
                num_chunks=0, sample_rate=24000, timestamps=[], error="Text is empty."
            )

        # Chunk text if long
        chunks = TextChunker.chunk_document(clean_text, max_words_per_chunk=60)
        if not chunks:
            chunks = [TextChunk(chunk_id="chunk_0001", index=1, text=clean_text, word_count=len(clean_text.split()), char_count=len(clean_text))]

        total_chunks = len(chunks)
        audio_segments: List[np.ndarray] = []
        pauses: List[float] = []
        timestamps: List[Dict[str, Any]] = []

        current_time = 0.0
        sample_rate = 24000

        for idx, chunk in enumerate(chunks):
            if progress_callback:
                progress_callback(idx + 1, total_chunks, f"Synthesizing chunk {idx+1}/{total_chunks}...")

            raw_audio, sr = ENGINE_REGISTRY.synthesize(
                text=chunk.text,
                voice=voice,
                speed=speed,
                pitch=pitch,
                engine_hint=engine_hint,
                voice_blend=voice_blend,
                ref_audio_path=ref_audio_path,
                ref_text=ref_text
            )
            sample_rate = sr

            # Apply pitch shift / DSP if needed
            processed_chunk = AudioProcessor.shift_pitch(raw_audio, semitones=pitch, sample_rate=sr) if abs(pitch) >= 0.1 else raw_audio

            audio_segments.append(processed_chunk)
            pauses.append(chunk.pause_after)

            chunk_dur = len(processed_chunk) / sr
            start_sec = current_time
            end_sec = start_sec + chunk_dur

            timestamps.append({
                "index": idx + 1,
                "chunk_id": chunk.chunk_id,
                "text": chunk.text,
                "start_sec": round(start_sec, 2),
                "end_sec": round(end_sec, 2),
                "duration_sec": round(chunk_dur, 2),
                "chapter": chunk.chapter
            })

            current_time = end_sec + chunk.pause_after

        # Merge chunks
        master_audio = AudioProcessor.concatenate_segments(audio_segments, pauses=pauses, sample_rate=sample_rate)

        # Volume multiplier & Peak Normalization
        if abs(volume - 1.0) >= 0.02:
            master_audio = master_audio * volume

        if normalize_audio:
            master_audio = AudioProcessor.normalize_loudness(master_audio, target_db=-1.0)

        total_duration = len(master_audio) / sample_rate
        elapsed = max(0.01, time.time() - start_time)
        rtf = round(elapsed / max(0.1, total_duration), 3)

        # Export audio
        out_name = output_filename or f"synth_{int(time.time())}"
        out_path = EXPORTS_DIR / f"{out_name}.wav"
        saved_file = AudioProcessor.export_audio(master_audio, out_path, sample_rate, "wav")

        # Base64 data URI for instant playback
        wav_bytes = AudioProcessor.numpy_to_wav_bytes(master_audio, sample_rate)
        b64 = AudioProcessor.to_base64_data_uri(master_audio, sample_rate) if hasattr(AudioProcessor, 'to_base64_data_uri') else f"data:audio/wav;base64,{import_base64(wav_bytes)}"

        # Save timestamps JSON
        ts_path = EXPORTS_DIR / f"{out_name}_timestamps.json"
        TimestampManager.export_json(timestamps, ts_path)

        return SynthesisResult(
            success=True,
            audio_path=saved_file,
            audio_data_uri=b64,
            duration_sec=round(total_duration, 2),
            generation_time_sec=round(elapsed, 2),
            realtime_factor=rtf,
            num_chunks=total_chunks,
            sample_rate=sample_rate,
            timestamps=timestamps
        )


def import_base64(b: bytes) -> str:
    import base64
    return base64.b64encode(b).decode('utf-8')
