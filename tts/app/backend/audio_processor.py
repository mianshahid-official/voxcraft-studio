"""
VoxCraft Studio - DSP Audio Processing & Effects Engine
Handles pitch shifting, time stretching, multi-track mixing, studio effects, and audio format exports.
"""
import io
import math
import base64
import os
import wave
import struct
from pathlib import Path
from typing import List, Dict, Any, Optional, Tuple, Union
import numpy as np

# Optional high-level audio libraries with fallback to pure numpy/wave
try:
    import soundfile as sf
    HAS_SOUNDFILE = True
except ImportError:
    HAS_SOUNDFILE = False

try:
    from pydub import AudioSegment
    from pydub.effects import normalize as pydub_normalize
    HAS_PYDUB = True
except ImportError:
    HAS_PYDUB = False

try:
    from scipy import signal
    from scipy.ndimage import zoom
    HAS_SCIPY = True
except ImportError:
    HAS_SCIPY = False


class AudioProcessor:
    """High quality audio processing pipeline for offline TTS and podcast workflows."""

    @staticmethod
    def numpy_to_wav_bytes(audio_array: np.ndarray, sample_rate: int = 24000) -> bytes:
        """Convert float32 numpy array [-1.0, 1.0] to standard 16-bit PCM WAV bytes."""
        audio = np.asarray(audio_array, dtype=np.float32)
        # Ensure clipping to prevent overflow
        audio = np.clip(audio, -1.0, 1.0)
        int16_audio = (audio * 32767.0).astype(np.int16)
        
        buffer = io.BytesIO()
        with wave.open(buffer, 'wb') as wav_file:
            wav_file.setnchannels(1)  # Mono
            wav_file.setsampwidth(2)  # 16-bit
            wav_file.setframerate(sample_rate)
            wav_file.writeframes(int16_audio.tobytes())
        
        return buffer.getvalue()

    @staticmethod
    def wav_bytes_to_numpy(wav_bytes: bytes) -> Tuple[np.ndarray, int]:
        """Convert WAV bytes to float32 numpy array and sample rate."""
        buffer = io.BytesIO(wav_bytes)
        with wave.open(buffer, 'rb') as wav_file:
            sample_rate = wav_file.getframerate()
            num_channels = wav_file.getnchannels()
            num_frames = wav_file.getnframes()
            raw_data = wav_file.readframes(num_frames)
            
            # Read int16 or int8
            sampwidth = wav_file.getsampwidth()
            if sampwidth == 2:
                int_audio = np.frombuffer(raw_data, dtype=np.int16)
                float_audio = int_audio.astype(np.float32) / 32767.0
            elif sampwidth == 1:
                int_audio = np.frombuffer(raw_data, dtype=np.uint8)
                float_audio = (int_audio.astype(np.float32) - 128.0) / 128.0
            else:
                float_audio = np.frombuffer(raw_data, dtype=np.int16).astype(np.float32) / 32767.0
            
            if num_channels > 1:
                float_audio = float_audio.reshape(-1, num_channels).mean(axis=1)
                
            return float_audio, sample_rate

    @staticmethod
    def change_speed(audio: np.ndarray, speed: float = 1.0, sample_rate: int = 24000) -> np.ndarray:
        """
        Time stretch audio by a speed factor (e.g. 0.5x to 2.0x) without altering pitch.
        Uses SOLA (Synchronized Overlap-Add) algorithm for pure numpy / scipy execution.
        """
        if abs(speed - 1.0) < 0.01 or speed <= 0:
            return audio

        # Fast and robust SOLA-based time stretching
        try:
            # Overlap-add window parameters
            win_size = int(sample_rate * 0.04)  # 40ms window
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

            # Normalize overlap
            mask = norm > 1e-4
            output[mask] /= norm[mask]
            
            # Trim trailing zero padding
            valid_len = int(len(audio) / speed)
            return output[:valid_len]
        except Exception:
            # Fallback simple interpolation
            indices = np.round(np.arange(0, len(audio), speed)).astype(int)
            indices = indices[indices < len(audio)]
            return audio[indices]

    @staticmethod
    def shift_pitch(audio: np.ndarray, semitones: float = 0.0, sample_rate: int = 24000) -> np.ndarray:
        """
        Shift pitch by semitones (-12 to +12) while maintaining tempo.
        Formula: factor = 2 ^ (semitones / 12). Resamples then time-stretches inversely.
        """
        if abs(semitones) < 0.05:
            return audio

        pitch_factor = math.pow(2.0, semitones / 12.0)
        
        # 1. Resample audio by pitch_factor (changes pitch + speed)
        original_len = len(audio)
        new_len = int(original_len / pitch_factor)
        if new_len <= 10:
            return audio

        x_orig = np.linspace(0, 1, original_len)
        x_new = np.linspace(0, 1, new_len)
        resampled = np.interp(x_new, x_orig, audio).astype(np.float32)

        # 2. Time-stretch by 1.0 / pitch_factor to restore original duration
        restored = AudioProcessor.change_speed(resampled, speed=1.0 / pitch_factor, sample_rate=sample_rate)
        if len(restored) > original_len:
            restored = restored[:original_len]
        elif len(restored) < original_len:
            restored = np.pad(restored, (0, original_len - len(restored)))
        return restored

    @staticmethod
    def apply_reverb(audio: np.ndarray, room_size: float = 0.3, damping: float = 0.5, sample_rate: int = 24000) -> np.ndarray:
        """Apply lightweight synthetic room reverberation."""
        if room_size <= 0.05:
            return audio

        delays = [int(sample_rate * d) for d in [0.0297, 0.0371, 0.0411, 0.0437]]
        gains = [0.7 * (1.0 - damping), 0.6 * (1.0 - damping), 0.5 * (1.0 - damping), 0.4 * (1.0 - damping)]
        
        wet = np.zeros(len(audio) + max(delays), dtype=np.float32)
        wet[:len(audio)] += audio
        
        for delay, gain in zip(delays, gains):
            wet[delay:delay + len(audio)] += audio * gain * room_size

        # Blend dry and wet
        out = audio.copy()
        out = out + wet[:len(audio)] * room_size
        max_val = np.max(np.abs(out)) + 1e-6
        if max_val > 1.0:
            out /= max_val
        return out

    @staticmethod
    def apply_eq(audio: np.ndarray, bass_gain: float = 0.0, treble_gain: float = 0.0, sample_rate: int = 24000) -> np.ndarray:
        """
        Apply simple 2-band equalizer (Bass / Treble shelf).
        Gains are in dB (e.g. -6.0 to +6.0).
        """
        if abs(bass_gain) < 0.2 and abs(treble_gain) < 0.2:
            return audio

        if not HAS_SCIPY:
            return audio

        try:
            out = audio.copy()
            nyquist = sample_rate / 2.0
            
            # Low shelf (Bass around 250Hz)
            if abs(bass_gain) >= 0.2:
                b_bass, a_bass = signal.butter(1, 250.0 / nyquist, btype='low')
                bass_comp = signal.lfilter(b_bass, a_bass, audio)
                linear_bass = math.pow(10, bass_gain / 20.0) - 1.0
                out += bass_comp * linear_bass

            # High shelf (Treble around 4000Hz)
            if abs(treble_gain) >= 0.2:
                b_treble, a_treble = signal.butter(1, 4000.0 / nyquist, btype='high')
                treble_comp = signal.lfilter(b_treble, a_treble, audio)
                linear_treble = math.pow(10, treble_gain / 20.0) - 1.0
                out += treble_comp * linear_treble

            max_val = np.max(np.abs(out)) + 1e-6
            if max_val > 1.0:
                out /= max_val
            return out
        except Exception:
            return audio

    @staticmethod
    def normalize_loudness(audio: np.ndarray, target_db: float = -1.0) -> np.ndarray:
        """Normalize peak amplitude to target dB."""
        max_amp = np.max(np.abs(audio))
        if max_amp <= 1e-5:
            return audio
        target_amp = math.pow(10, target_db / 20.0)
        gain = target_amp / max_amp
        return np.clip(audio * gain, -1.0, 1.0)

    @staticmethod
    def trim_silence(audio: np.ndarray, threshold: float = 0.01) -> np.ndarray:
        """Trim silent chunks from start and end."""
        mask = np.abs(audio) > threshold
        if not np.any(mask):
            return audio
        start = np.argmax(mask)
        end = len(mask) - np.argmax(mask[::-1])
        return audio[start:end]

    @staticmethod
    def process_chain(
        audio: np.ndarray,
        sample_rate: int = 24000,
        speed: float = 1.0,
        pitch: float = 0.0,
        volume: float = 1.0,
        bass: float = 0.0,
        treble: float = 0.0,
        reverb: float = 0.0,
        normalize: bool = True
    ) -> np.ndarray:
        """Apply complete DSP effects chain."""
        out = audio.copy()
        
        # 1. Pitch shift
        if abs(pitch) >= 0.1:
            out = AudioProcessor.shift_pitch(out, semitones=pitch, sample_rate=sample_rate)

        # 2. Speed / Tempo stretch
        if abs(speed - 1.0) >= 0.02 and speed > 0:
            out = AudioProcessor.change_speed(out, speed=speed, sample_rate=sample_rate)

        # 3. EQ
        if abs(bass) >= 0.2 or abs(treble) >= 0.2:
            out = AudioProcessor.apply_eq(out, bass_gain=bass, treble_gain=treble, sample_rate=sample_rate)

        # 4. Reverb
        if reverb > 0.05:
            out = AudioProcessor.apply_reverb(out, room_size=reverb, sample_rate=sample_rate)

        # 5. Volume multiplier
        if abs(volume - 1.0) >= 0.02:
            out = out * volume

        # 6. Normalize peak
        if normalize:
            out = AudioProcessor.normalize_loudness(out, target_db=-1.0)

        return np.clip(out, -1.0, 1.0)

    @staticmethod
    def concatenate_segments(
        segments: List[np.ndarray],
        pause_seconds_list: Optional[List[float]] = None,
        sample_rate: int = 24000
    ) -> np.ndarray:
        """
        Concatenates multiple speech clips with designated silence pauses between them.
        Perfect for multi-speaker dialogues and podcasts.
        """
        if not segments:
            return np.zeros(0, dtype=np.float32)

        pieces = []
        for idx, seg in enumerate(segments):
            if len(seg) > 0:
                pieces.append(seg)
            
            # Insert pause between segments
            if idx < len(segments) - 1:
                pause_sec = 0.5  # default 500ms
                if pause_seconds_list and idx < len(pause_seconds_list):
                    pause_sec = pause_seconds_list[idx]
                
                num_silence_samples = int(sample_rate * max(0.0, pause_sec))
                if num_silence_samples > 0:
                    pieces.append(np.zeros(num_silence_samples, dtype=np.float32))

        if not pieces:
            return np.zeros(0, dtype=np.float32)
        return np.concatenate(pieces)

    @staticmethod
    def to_base64_data_uri(audio_array: np.ndarray, sample_rate: int = 24000) -> str:
        """Encode float numpy audio to a base64 audio/wav Data URI for instant browser player playback."""
        wav_bytes = AudioProcessor.numpy_to_wav_bytes(audio_array, sample_rate)
        b64_str = base64.b64encode(wav_bytes).decode('utf-8')
        return f"data:audio/wav;base64,{b64_str}"

    @staticmethod
    def export_audio(
        audio_array: np.ndarray,
        output_filepath: Union[str, Path],
        sample_rate: int = 24000,
        format_ext: str = "wav"
    ) -> str:
        """Export audio array to disk in WAV, MP3, FLAC, or OGG format."""
        out_path = Path(output_filepath).resolve()
        out_path.parent.mkdir(parents=True, exist_ok=True)
        fmt = format_ext.lower().replace(".", "")

        wav_bytes = AudioProcessor.numpy_to_wav_bytes(audio_array, sample_rate)

        if fmt == "wav":
            with open(out_path, "wb") as f:
                f.write(wav_bytes)
            return str(out_path)

        # Convert using pydub / ffmpeg / soundfile if available
        if HAS_PYDUB:
            try:
                segment = AudioSegment.from_file(io.BytesIO(wav_bytes), format="wav")
                segment.export(str(out_path), format=fmt, bitrate="320k" if fmt == "mp3" else None)
                return str(out_path)
            except Exception:
                pass

        if HAS_SOUNDFILE and fmt in ["flac", "ogg"]:
            try:
                sf.write(str(out_path), audio_array, sample_rate, format=fmt.upper())
                return str(out_path)
            except Exception:
                pass

        # Fallback to WAV
        fallback_path = out_path.with_suffix(".wav")
        with open(fallback_path, "wb") as f:
            f.write(wav_bytes)
        return str(fallback_path)
