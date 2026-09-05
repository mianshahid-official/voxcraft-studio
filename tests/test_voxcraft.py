"""
VoxCraft Studio - End-to-End Verification Test Suite
"""
import sys
import os
import unittest
import numpy as np
from pathlib import Path

# Add project root to sys.path
PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from app.backend.hardware import get_system_diagnostics, get_gpu_info, get_cpu_info, get_ram_info
from app.backend.audio_processor import AudioProcessor
from app.backend.voice_catalog import get_all_voices, filter_voices, get_voice_by_id
from app.backend.engines import ENGINE_REGISTRY
from app.backend.podcast_generator import PodcastGenerator
from app.backend.project_store import PROJECT_STORE
from app.backend.model_manager import ModelManager


class TestVoxCraftStudio(unittest.TestCase):

    def test_01_hardware_diagnostics(self):
        """Test hardware detection, CPU/RAM stats, and GPU prioritized selection."""
        diag = get_system_diagnostics()
        self.assertIn("cpu", diag)
        self.assertIn("ram", diag)
        self.assertIn("gpu", diag)
        self.assertGreater(diag["cpu"]["physical_cores"], 0)
        self.assertGreater(diag["ram"]["total_gb"], 0)
        self.assertIn("active_device", diag)
        print(f"\n[Hardware Test] Active Device: {diag['active_device']}, OS: {diag['os']}")

    def test_02_audio_processor_dsp(self):
        """Test DSP pipeline: pitch shifting, speed stretching, EQ, base64 encoding."""
        sr = 24000
        # Generate 1 second test sine wave
        t = np.linspace(0, 1.0, sr, endpoint=False, dtype=np.float32)
        audio = 0.5 * np.sin(2 * np.pi * 440.0 * t)

        # 1. Pitch shift (+3 semitones)
        shifted = AudioProcessor.shift_pitch(audio, semitones=3.0, sample_rate=sr)
        self.assertEqual(len(shifted), len(audio))

        # 2. Time stretch (1.5x speed)
        stretched = AudioProcessor.change_speed(audio, speed=1.5, sample_rate=sr)
        self.assertAlmostEqual(len(stretched) / sr, 1.0 / 1.5, delta=0.08)

        # 3. DSP Effects Chain
        processed = AudioProcessor.process_chain(
            audio, sample_rate=sr, speed=1.2, pitch=2.0, bass=1.5, treble=1.0, reverb=0.1
        )
        self.assertTrue(isinstance(processed, np.ndarray))

        # 4. Base64 Data URI
        data_uri = AudioProcessor.to_base64_data_uri(processed, sr)
        self.assertTrue(data_uri.startswith("data:audio/wav;base64,"))

        # 5. Export audio to disk
        test_out = PROJECT_ROOT / "exports" / "test_verification.wav"
        saved = AudioProcessor.export_audio(processed, test_out, sr, "wav")
        self.assertTrue(Path(saved).exists())
        self.assertGreater(Path(saved).stat().st_size, 1000)
        print(f"[Audio DSP Test] Processed & Exported successfully ({len(data_uri)} chars URI).")

    def test_03_voice_catalog(self):
        """Test voice catalog indexing, language filters, and search."""
        voices = get_all_voices()
        self.assertGreater(len(voices), 15)

        female_voices = filter_voices(gender="female")
        self.assertTrue(all(v["gender"].lower() == "female" for v in female_voices))

        kokoro_voices = filter_voices(engine="kokoro")
        self.assertTrue(all(v["engine"] == "kokoro" for v in kokoro_voices))

        bella = get_voice_by_id("af_bella")
        self.assertIsNotNone(bella)
        self.assertEqual(bella["name"], "Bella (Warm & Melodic)")
        print(f"[Voice Catalog Test] Verified {len(voices)} voices across Kokoro, Piper, and F5-TTS.")

    def test_04_tts_engines(self):
        """Test TTS engine dispatching and synthesis."""
        text = "VoxCraft Studio offline synthesis verification test."
        
        # Kokoro synthesis test
        audio_k, sr_k = ENGINE_REGISTRY.synthesize(text, voice="af_bella", speed=1.0, engine_hint="kokoro")
        self.assertGreater(len(audio_k), 0)
        self.assertEqual(sr_k, 24000)

        # Piper synthesis test
        audio_p, sr_p = ENGINE_REGISTRY.synthesize(text, voice="piper-en_US-lessac-medium", speed=1.0, engine_hint="piper")
        self.assertGreater(len(audio_p), 0)

        # F5-TTS synthesis test
        audio_f, sr_f = ENGINE_REGISTRY.synthesize(text, voice="f5_preset_studio_host", speed=1.0, engine_hint="f5_tts")
        self.assertGreater(len(audio_f), 0)

        print(f"[TTS Engine Test] Synthesized audio across Kokoro ({len(audio_k)} samples), Piper ({len(audio_p)} samples), and F5-TTS ({len(audio_f)} samples).")

    def test_05_podcast_generator(self):
        """Test multi-speaker podcast generation and timeline synchronizer."""
        speakers = [
            {"id": "spk_1", "name": "Alex", "engine": "kokoro", "voice": "am_michael", "speed": 1.0, "pitch": 0.0, "color": "#8b5cf6"},
            {"id": "spk_2", "name": "Sarah", "engine": "kokoro", "voice": "af_sarah", "speed": 1.0, "pitch": 0.0, "color": "#06b6d4"}
        ]
        dialogue = [
            {"speaker_id": "spk_1", "text": "Welcome to VoxCraft podcast episode one.", "pause_after": 0.5},
            {"speaker_id": "spk_2", "text": "Glad to be here testing offline speech synthesis.", "pause_after": 0.5}
        ]

        result = PodcastGenerator.generate_podcast(speakers, dialogue)
        self.assertTrue(result["success"])
        self.assertGreater(result["total_duration_sec"], 0)
        self.assertEqual(len(result["timeline"]), 2)
        self.assertTrue(result["audio_data_uri"].startswith("data:audio/wav;base64,"))
        print(f"[Podcast Test] Compiled podcast episode: {result['total_duration_sec']}s with {len(result['timeline'])} synchronized timeline turns.")

    def test_06_project_store(self):
        """Test SQLite persistence for generation history and custom voice presets."""
        entry = {
            "id": "test_history_1",
            "text": "Testing SQLite persistence",
            "engine": "kokoro",
            "voice": "af_bella",
            "speed": 1.0,
            "pitch": 0.0,
            "duration_sec": 3.5,
            "audio_data_uri": "data:audio/wav;base64,UklGRg=="
        }
        ok = PROJECT_STORE.add_history_entry(entry)
        self.assertTrue(ok)

        history = PROJECT_STORE.get_history(limit=5)
        self.assertGreater(len(history), 0)
        self.assertEqual(history[0]["id"], "test_history_1")
        print(f"[Storage Test] SQLite history recorded and retrieved successfully ({len(history)} entries).")

    def test_07_model_manager(self):
        """Test model status scan and manifest metadata."""
        status = ModelManager.get_local_model_status()
        self.assertIn("kokoro", status)
        self.assertIn("piper", status)
        self.assertIn("f5_tts", status)
        self.assertIn("manifest", status)
        self.assertIn("kokoro-v0_19", status["manifest"])
        print(f"[Model Manager Test] Scanned model directories successfully.")


if __name__ == "__main__":
    unittest.main()
