"""
TTS Studio - PySide6 Text-to-Speech Studio View
"""
import time
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QTextEdit,
    QPushButton, QComboBox, QCheckBox, QFrame, QSplitter,
    QProgressBar, QMessageBox
)
from PySide6.QtCore import Qt, QThread, Signal

from ..widgets.cards import GlassCard, StatusBadge
from ..widgets.sliders import LabeledSlider
from ...services.tts_service import TTSService, SynthesisResult
from ...voices.catalog import VoiceCatalog
from ...engines.registry import ENGINE_REGISTRY


class SynthesisWorker(QThread):
    """Background worker thread so GUI never freezes during neural synthesis."""
    finished = Signal(object)
    progress = Signal(int, int, str)

    def __init__(self, text: str, voice: str, engine: str, speed: float, pitch: float, volume: float, voice_blend: dict = None):
        super().__init__()
        self.text = text
        self.voice = voice
        self.engine = engine
        self.speed = speed
        self.pitch = pitch
        self.volume = volume
        self.voice_blend = voice_blend

    def run(self):
        res = TTSService.synthesize_text(
            text=self.text,
            voice=self.voice,
            engine_hint=self.engine,
            speed=self.speed,
            pitch=self.pitch,
            volume=self.volume,
            voice_blend=self.voice_blend,
            progress_callback=lambda cur, tot, msg: self.progress.emit(cur, tot, msg)
        )
        self.finished.emit(res)


class TTSView(QWidget):
    """Main Text-to-Speech Studio View."""

    audioGenerated = Signal(str, str, str)  # filepath, title, subtitle

    def __init__(self, parent=None):
        super().__init__(parent)
        self.worker = None
        self._init_ui()
        self._load_voices()

    def _init_ui(self):
        main_layout = QHBoxLayout(self)
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(20)

        # Left Column: Large Text Editor Card
        left_card = GlassCard()
        left_layout = QVBoxLayout(left_card)
        left_layout.setContentsMargins(18, 18, 18, 18)
        left_layout.setSpacing(12)

        header_row = QHBoxLayout()
        lbl_title = QLabel("Text Prompt")
        lbl_title.setStyleSheet("font-size: 15px; font-weight: 700; color: #ffffff;")
        header_row.addWidget(lbl_title)
        header_row.addStretch()
        self.device_badge = StatusBadge("GPU Active", "gpu")
        header_row.addWidget(self.device_badge)
        left_layout.addLayout(header_row)

        self.text_editor = QTextEdit()
        self.text_editor.setPlaceholderText("Type or paste text here to synthesize speech offline...")
        self.text_editor.setText("VoxCraft Studio brings studio-quality neural speech synthesis directly to your desktop. Operating 100% offline with zero cloud latency.")
        self.text_editor.textChanged.connect(self._update_text_stats)
        left_layout.addWidget(self.text_editor, stretch=1)

        # Quick Prompts Row
        prompts_row = QHBoxLayout()
        prompts_row.setSpacing(8)
        lbl_quick = QLabel("Quick:")
        lbl_quick.setStyleSheet("color: #94a3b8; font-size: 11px;")
        prompts_row.addWidget(lbl_quick)

        for name, text in [
            ("🎙️ Podcast Intro", "Welcome back to the studio! Today we are exploring the frontiers of offline machine learning and high fidelity voice synthesis."),
            ("📖 Storyteller", "Deep in the ancient forest, echoes of forgotten stories whispered through the twilight breeze."),
            ("⚡ Tech News", "Today's report highlights breakthroughs in on-device AI models running without internet connectivity.")
        ]:
            btn = QPushButton(name)
            btn.setProperty("class", "SecondaryBtn")
            btn.setStyleSheet("padding: 4px 10px; font-size: 11px;")
            btn.clicked.connect(lambda _, t=text: self.text_editor.setText(t))
            prompts_row.addWidget(btn)
        prompts_row.addStretch()
        left_layout.addLayout(prompts_row)

        # Stats footer
        footer_row = QHBoxLayout()
        self.stats_label = QLabel("0 chars • 0 words • ~0.0s")
        self.stats_label.setStyleSheet("color: #94a3b8; font-size: 11px; font-family: 'Consolas';")
        footer_row.addWidget(self.stats_label)
        footer_row.addStretch()
        lbl_hint = QLabel("Ctrl + Enter to Generate")
        lbl_hint.setStyleSheet("color: #06b6d4; font-size: 11px; font-family: 'Consolas';")
        footer_row.addWidget(lbl_hint)
        left_layout.addLayout(footer_row)

        main_layout.addWidget(left_card, stretch=6)

        # Right Column: Voice & DSP Controls Card
        right_card = GlassCard()
        right_card.setFixedWidth(340)
        right_layout = QVBoxLayout(right_card)
        right_layout.setContentsMargins(18, 18, 18, 18)
        right_layout.setSpacing(14)

        lbl_controls = QLabel("Voice & Engine Settings")
        lbl_controls.setStyleSheet("font-size: 15px; font-weight: 700; color: #ffffff;")
        right_layout.addWidget(lbl_controls)

        # Language Selector Dropdown
        right_layout.addWidget(QLabel("Spoken Language:"))
        self.lang_combo = QComboBox()
        self.lang_combo.addItems(["All Languages", "English", "British English", "Spanish", "French", "German", "Italian", "Portuguese", "Multi-Lingual"])
        self.lang_combo.currentIndexChanged.connect(self._on_filter_changed)
        right_layout.addWidget(self.lang_combo)

        # Engine Selector
        right_layout.addWidget(QLabel("TTS Engine:"))
        self.engine_combo = QComboBox()
        self.engine_combo.addItems([
            "All Engines (Auto-Select)",
            "Engine 1: Kokoro-82M (Studio Quality)",
            "Engine 2: Piper Neural (Multi-Lingual)",
            "Engine 3: F5-TTS (Voice Cloning)"
        ])
        self.engine_combo.currentIndexChanged.connect(self._on_filter_changed)
        right_layout.addWidget(self.engine_combo)

        # Voice Selector
        right_layout.addWidget(QLabel("Speaker Voice:"))
        self.voice_combo = QComboBox()
        self.voice_combo.currentIndexChanged.connect(self._on_voice_changed)
        right_layout.addWidget(self.voice_combo)

        # Sliders
        self.speed_slider = LabeledSlider("Speaking Rate", 0.5, 2.0, 1.0, 0.05, "x")
        self.speed_slider.valueChanged.connect(self._update_text_stats)
        right_layout.addWidget(self.speed_slider)

        self.pitch_slider = LabeledSlider("Pitch Shift", -8.0, 8.0, 0.0, 0.5, " st")
        right_layout.addWidget(self.pitch_slider)

        self.vol_slider = LabeledSlider("Volume Multiplier", 0.2, 2.0, 1.0, 0.05, "x")
        right_layout.addWidget(self.vol_slider)

        # Voice Blending Toggle (Kokoro)
        self.blend_check = QCheckBox("🧬 Enable Voice Blending (Engine 1)")
        self.blend_check.toggled.connect(self._on_blend_toggled)
        right_layout.addWidget(self.blend_check)

        self.blend_container = QFrame()
        self.blend_container.setVisible(False)
        blend_box = QVBoxLayout(self.blend_container)
        blend_box.setContentsMargins(0, 0, 0, 0)
        blend_box.setSpacing(6)

        self.blend_voice_b = QComboBox()
        blend_box.addWidget(QLabel("Blend Secondary Voice:"))
        blend_box.addWidget(self.blend_voice_b)
        self.blend_ratio = LabeledSlider("Blend Ratio (A / B)", 0.0, 1.0, 0.5, 0.05, "")
        blend_box.addWidget(self.blend_ratio)
        right_layout.addWidget(self.blend_container)

        right_layout.addStretch()

        # Progress bar
        self.prog_bar = QProgressBar()
        self.prog_bar.setVisible(False)
        right_layout.addWidget(self.prog_bar)

        # Synthesize Button
        self.generate_btn = QPushButton("▶ Generate Speech")
        self.generate_btn.setProperty("class", "PrimaryBtn")
        self.generate_btn.setFixedHeight(44)
        self.generate_btn.clicked.connect(self.generate_speech)
        right_layout.addWidget(self.generate_btn)

        main_layout.addWidget(right_card, stretch=4)
        self._update_text_stats()

    def _load_voices(self):
        self.voices = VoiceCatalog.get_all()
        self._filter_voices()

    def _on_filter_changed(self, idx: int):
        self._filter_voices()

    def _filter_voices(self):
        eng_idx = self.engine_combo.currentIndex()
        eng_filter = {0: "all", 1: "kokoro", 2: "piper", 3: "f5_tts"}.get(eng_idx, "all")
        lang_idx = self.lang_combo.currentIndex() if hasattr(self, 'lang_combo') else 0
        lang_filter = "all" if lang_idx == 0 else self.lang_combo.currentText()

        self.voice_combo.blockSignals(True)
        self.voice_combo.clear()
        filtered = VoiceCatalog.filter(engine=eng_filter, language=lang_filter)
        for v in filtered:
            self.voice_combo.addItem(VoiceCatalog.format_label(v, include_engine=True), v.get("id", ""))
        self.voice_combo.blockSignals(False)

        # Populate secondary blend combo with Kokoro voices
        self.blend_voice_b.clear()
        kokoro_voices = [v for v in self.voices if v.get("engine") == "kokoro"]
        for v in kokoro_voices:
            self.blend_voice_b.addItem(VoiceCatalog.format_label(v, include_engine=False), v.get("id", ""))

    def _on_voice_changed(self, idx: int):
        pass

    def _on_blend_toggled(self, checked: bool):
        self.blend_container.setVisible(checked)

    def _update_text_stats(self):
        text = self.text_editor.toPlainText()
        chars = len(text)
        words = len(text.strip().split()) if text.strip() else 0
        speed = self.speed_slider.value() if hasattr(self, 'speed_slider') else 1.0
        est_sec = (words / (150 / 60)) / max(0.1, speed)
        self.stats_label.setText(f"{chars} chars • {words} words • ~{est_sec:.1f}s")

    def generate_speech(self):
        text = self.text_editor.toPlainText().strip()
        if not text:
            QMessageBox.warning(self, "Empty Text", "Please enter text to synthesize speech.")
            return

        voice_id = self.voice_combo.currentData() or "af_bella"
        v_meta = VoiceCatalog.get_by_id(voice_id)

        eng_idx = self.engine_combo.currentIndex()
        if eng_idx == 0:
            engine_hint = v_meta.get("engine", "kokoro") if v_meta else "kokoro"
        else:
            engine_hint = {1: "kokoro", 2: "piper", 3: "f5_tts"}.get(eng_idx, "kokoro")

        voice_blend = None
        if self.blend_check.isChecked():
            voice_blend = {
                "voice_a": voice_id,
                "voice_b": self.blend_voice_b.currentData(),
                "weight_a": self.blend_ratio.value()
            }

        self.generate_btn.setEnabled(False)
        self.generate_btn.setText("⏳ Synthesizing...")
        self.prog_bar.setVisible(True)
        self.prog_bar.setValue(0)

        self.worker = SynthesisWorker(
            text=text,
            voice=voice_id,
            engine=engine_hint,
            speed=self.speed_slider.value(),
            pitch=self.pitch_slider.value(),
            volume=self.vol_slider.value(),
            voice_blend=voice_blend
        )
        self.worker.progress.connect(self._on_worker_progress)
        self.worker.finished.connect(self._on_worker_finished)
        self.worker.start()

    def _on_worker_progress(self, cur, tot, msg):
        pct = int((cur / max(1, tot)) * 100)
        self.prog_bar.setValue(pct)

    def _on_worker_finished(self, res: SynthesisResult):
        self.generate_btn.setEnabled(True)
        self.generate_btn.setText("▶ Generate Speech")
        self.prog_bar.setVisible(False)

        if res.success and res.audio_path:
            v_name = self.voice_combo.currentText()
            self.audioGenerated.emit(
                res.audio_path,
                v_name,
                f"{res.duration_sec}s • RTF: {res.realtime_factor}x"
            )
        else:
            QMessageBox.critical(self, "Synthesis Error", f"Speech generation failed:\n{res.error}")
