"""
TTS Studio - High Quality Audio DSP & Processing Engine
"""
import io
import math
import wave
import base64
from pathlib import Path
from typing import Tuple, List, Optional, Union
import numpy as np

try:
    import soundfile as sf
    HAS_SOUNDFILE = True
except ImportError:
    HAS_SOUNDFILE = False

try:
    from pydub import AudioSegment
    HAS_PYDUB = True
except ImportError:
    HAS_PYDUB = False


class AudioProcessor:
    """Core DSP pipeline for time stretching, pitch shifting, loudness normalization, and exports."""

    @staticmethod
    def numpy_to_wav_bytes(audio_array: np.ndarray, sample_rate: int = 24000) -> bytes:
        """Convert float32 [-1.0, 1.0] to 16-bit PCM WAV bytes."""
        audio = np.clip(np.asarray(audio_array, dtype=np.float32), -1.0, 1.0)
        int16_data = (audio * 32767.0).astype(np.int16)

        buffer = io.BytesIO()
        with wave.open(buffer, 'wb') as wf:
            wf.setnchannels(1)
            wf.setsampwidth(2)
            wf.setframerate(sample_rate)
            wf.writeframes(int16_data.tobytes())
        return buffer.getvalue()

    @staticmethod
    def wav_bytes_to_numpy(wav_bytes: bytes) -> Tuple[np.ndarray, int]:
        """Convert WAV bytes to float32 numpy array and sample rate."""
        buffer = io.BytesIO(wav_bytes)
        with wave.open(buffer, 'rb') as wf:
            sr = wf.getframerate()
            num_channels = wf.getnchannels()
            raw = wf.readframes(wf.getnframes())
            int16_data = np.frombuffer(raw, dtype=np.int16)
            float_data = int16_data.astype(np.float32) / 32767.0
            if num_channels > 1:
                float_data = float_data.reshape(-1, num_channels).mean(axis=1)
            return float_data, sr

    @staticmethod
    def change_speed(audio: np.ndarray, speed: float = 1.0, sample_rate: int = 24000) -> np.ndarray:
        """SOLA-based time stretching without altering pitch."""
        if abs(speed - 1.0) < 0.02 or speed <= 0:
            return audio

        try:
            win_size = int(sample_rate * 0.04)
            if win_size % 2 != 0:
                win_size += 1
            hop_in = int(win_size / 2)
            hop_out = int(hop_in / speed)
            if hop_out <= 0:
                hop_out = 1

            num_frames = int((len(audio) - win_size) / hop_in)
            if num_frames <= 0:
                return audio

            window = np.hanning(win_size)
            output_len = int(len(audio) / speed) + win_size
            output = np.zeros(output_len, dtype=np.float32)
            norm = np.zeros(output_len, dtype=np.float32)

            for i in range(num_frames):
                pos_in = i * hop_in
                pos_out = i * hop_out
                chunk = audio[pos_in:pos_in + win_size] * window
                output[pos_out:pos_out + win_size] += chunk
                norm[pos_out:pos_out + win_size] += window

            mask = norm > 1e-4
            output[mask] /= norm[mask]
            valid_len = int(len(audio) / speed)
            return output[:valid_len]
        except Exception:
            indices = np.round(np.arange(0, len(audio), speed)).astype(int)
            indices = indices[indices < len(audio)]
            return audio[indices]

    @staticmethod
    def shift_pitch(audio: np.ndarray, semitones: float = 0.0, sample_rate: int = 24000) -> np.ndarray:
        """Shift pitch (-12 to +12 semitones) while preserving exact duration."""
        if abs(semitones) < 0.05:
            return audio

        pitch_factor = math.pow(2.0, semitones / 12.0)
        original_len = len(audio)
        new_len = int(original_len / pitch_factor)
        if new_len <= 10:
            return audio

        x_orig = np.linspace(0, 1, original_len)
        x_new = np.linspace(0, 1, new_len)
        resampled = np.interp(x_new, x_orig, audio).astype(np.float32)

        restored = AudioProcessor.change_speed(resampled, speed=1.0 / pitch_factor, sample_rate=sample_rate)
        if len(restored) > original_len:
            restored = restored[:original_len]
        elif len(restored) < original_len:
            restored = np.pad(restored, (0, original_len - len(restored)))
        return restored

    @staticmethod
    def normalize_loudness(audio: np.ndarray, target_db: float = -1.0) -> np.ndarray:
        """Peak amplitude normalization."""
        max_amp = np.max(np.abs(audio))
        if max_amp <= 1e-5:
            return audio
        target_amp = math.pow(10, target_db / 20.0)
        gain = target_amp / max_amp
        return np.clip(audio * gain, -1.0, 1.0)

    @staticmethod
    def trim_silence(audio: np.ndarray, threshold: float = 0.01) -> np.ndarray:
        """Trim leading and trailing silence."""
        mask = np.abs(audio) > threshold
        if not np.any(mask):
            return audio
        start = np.argmax(mask)
        end = len(mask) - np.argmax(mask[::-1])
        return audio[start:end]

    @staticmethod
    def concatenate_segments(segments: List[np.ndarray], pauses: Optional[List[float]] = None, sample_rate: int = 24000) -> np.ndarray:
        """Concatenate speech segments with silence pauses."""
        if not segments:
            return np.zeros(0, dtype=np.float32)

        pieces = []
        for idx, seg in enumerate(segments):
            if len(seg) > 0:
                pieces.append(seg)
            if idx < len(segments) - 1:
                p_sec = pauses[idx] if pauses and idx < len(pauses) else 0.5
                num_silence = int(sample_rate * max(0.0, p_sec))
                if num_silence > 0:
                    pieces.append(np.zeros(num_silence, dtype=np.float32))
        return np.concatenate(pieces) if pieces else np.zeros(0, dtype=np.float32)

    @staticmethod
    def export_audio(audio: np.ndarray, output_path: Union[str, Path], sample_rate: int = 24000, fmt: str = "wav") -> str:
        """Export audio to WAV, MP3, or FLAC."""
        out = Path(output_path).resolve()
        out.parent.mkdir(parents=True, exist_ok=True)
        fmt = fmt.lower().replace(".", "")

        wav_bytes = AudioProcessor.numpy_to_wav_bytes(audio, sample_rate)

        if fmt == "wav":
            with open(out, "wb") as f:
                f.write(wav_bytes)
            return str(out)

        if HAS_PYDUB:
            try:
                seg = AudioSegment.from_file(io.BytesIO(wav_bytes), format="wav")
                seg.export(str(out), format=fmt, bitrate="320k" if fmt == "mp3" else None)
                return str(out)
            except Exception:
                pass

        if HAS_SOUNDFILE and fmt in ["flac", "ogg"]:
            try:
                sf.write(str(out), audio, sample_rate, format=fmt.upper())
                return str(out)
            except Exception:
                pass

        # Fallback to WAV
        fallback = out.with_suffix(".wav")
        with open(fallback, "wb") as f:
            f.write(wav_bytes)
        return str(fallback)
