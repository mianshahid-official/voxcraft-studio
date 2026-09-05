"""
TTS Studio - End-to-End Pipeline & PySide6 Architecture Verification Test Suite
"""
import sys
import unittest
from pathlib import Path
import numpy as np

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from app.config.settings import APP_CONFIG
from app.config.paths import MODELS_DIR, EXPORTS_DIR
from app.core.hardware import HardwareManager
from app.core.models import ModelManager
from app.core.audio import AudioProcessor
from app.core.chunking import TextChunker
from app.core.normalization import TextNormalizer
from app.core.timestamps import TimestampManager
from app.core.resources import ResourceManager
from app.core.project import ProjectManager
from app.voices.catalog import VoiceCatalog
from app.engines.registry import ENGINE_REGISTRY
from app.services.tts_service import TTSService
from app.services.podcast_service import PodcastService
from app.services.batch_service import BATCH_SERVICE
from app.services.storage_service import StorageService


class TestCompleteArchitecture(unittest.TestCase):

    def test_01_hardware_manager(self):
        report = HardwareManager.get_hardware_report()
        self.assertGreater(report.cpu_physical_cores, 0)
        self.assertGreater(report.ram_total_gb, 0)
        metrics = HardwareManager.get_live_metrics()
        self.assertIn("cpu_percent", metrics)
        self.assertIn("ram_percent", metrics)
        print(f"[Hardware] OS: {report.os_name} | CPU: {report.cpu_name} | Recommended: {report.recommended_device}")

    def test_02_text_chunking_and_normalization(self):
        text = "Hello world! “Smart quotes” &mdash; and acronyms like SQL should be normalized. [PAUSE 1.0] This is sentence two."
        normalized = TextNormalizer.preprocess(text, custom_dict={"SQL": "S Q L"})
        self.assertIn('"', normalized)
        self.assertIn("S Q L", normalized)

        chunks = TextChunker.chunk_document(normalized, max_words_per_chunk=10)
        self.assertGreaterEqual(len(chunks), 1)
        self.assertEqual(chunks[0].chunk_id, "chunk_0001")
        print(f"[Chunking] Segmented into {len(chunks)} retryable chunks.")

    def test_03_timestamps_export(self):
        sample_items = [
            {"index": 1, "text": "First chunk test", "start_sec": 0.0, "end_sec": 1.5},
            {"index": 2, "text": "Second chunk test", "start_sec": 2.0, "end_sec": 3.8}
        ]
        srt_out = EXPORTS_DIR / "test_subs.srt"
        vtt_out = EXPORTS_DIR / "test_subs.vtt"
        json_out = EXPORTS_DIR / "test_subs.json"

        TimestampManager.export_srt(sample_items, srt_out)
        TimestampManager.export_vtt(sample_items, vtt_out)
        TimestampManager.export_json(sample_items, json_out)

        self.assertTrue(srt_out.exists())
        self.assertTrue(vtt_out.exists())
        self.assertTrue(json_out.exists())
        print("[Timestamps] SRT, VTT, and JSON generated successfully.")

    def test_04_tts_service_synthesis(self):
        res = TTSService.synthesize_text(
            text="Testing full TTS service pipeline with chunking and metadata.",
            voice="af_bella",
            engine_hint="kokoro",
            speed=1.0,
            pitch=1.0
        )
        self.assertTrue(res.success)
        self.assertGreater(res.duration_sec, 0)
        self.assertGreater(len(res.timestamps), 0)
        self.assertTrue(Path(res.audio_path).exists())
        print(f"[TTSService] Generated {res.duration_sec}s audio (RTF: {res.realtime_factor}x) -> {res.audio_path}")

    def test_05_podcast_service(self):
        script = (
            "Alex: Hello and welcome.\n"
            "Sarah: Glad to be here testing speech synthesis."
        )
        dialogue = PodcastService.parse_script_text(script)
        self.assertEqual(len(dialogue), 2)
        self.assertEqual(dialogue[0]["speaker_label"], "Alex")

        speakers = [
            {"id": "alex", "name": "Alex", "engine": "kokoro", "voice": "am_michael", "speed": 1.0, "pitch": 0.0, "color": "#8b5cf6"},
            {"id": "sarah", "name": "Sarah", "engine": "kokoro", "voice": "af_sarah", "speed": 1.0, "pitch": 0.0, "color": "#06b6d4"}
        ]
        res = PodcastService.generate_episode(speakers, dialogue, "Test_Episode")
        self.assertTrue(res["success"])
        self.assertGreater(res["total_duration_sec"], 0)
        self.assertEqual(len(res["timeline"]), 2)
        print(f"[PodcastService] Generated multi-speaker podcast ({res['total_duration_sec']}s).")

    def test_06_storage_service(self):
        breakdown = StorageService.get_storage_breakdown()
        self.assertIn("models_gb", breakdown)
        self.assertIn("total_gb", breakdown)
        print(f"[Storage] Footprint: {breakdown['total_gb']} GB total.")

    def test_07_pyside6_app_import_and_instantiation(self):
        """Verify PySide6 imports, main window, and setup wizard creation without errors."""
        from PySide6.QtWidgets import QApplication
        from app.gui.main_window import MainWindow
        from app.gui.wizard.setup_wizard import SetupWizardDialog

        app = QApplication.instance() or QApplication(sys.argv)
        win = MainWindow(check_first_run=False)
        self.assertIsNotNone(win)
        self.assertEqual(win.stack.count(), 7)  # 7 views (Projects removed, About & Hardware merged into Settings)
        self.assertIsNotNone(win.view_tts)
        self.assertIsNotNone(win.view_podcast)
        self.assertIsNotNone(win.view_settings)

        wizard = SetupWizardDialog()
        self.assertIsNotNone(wizard)
        self.assertEqual(wizard.stack.count(), 5)  # 5 step setup wizard
        print(f"[PySide6 GUI] Verified MainWindow ({win.stack.count()} views) and SetupWizard ({wizard.stack.count()} steps).")


if __name__ == "__main__":
    unittest.main()
