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
            ("🇺🇸 English", "Welcome to VoxCraft Studio, delivering ultra-fast neural speech synthesis directly on your machine."),
            ("🇮🇳 हिन्दी", "नमस्ते, VoxCraft Studio में आपका स्वागत है। यह वॉइस मॉडल पूरी तरह से ऑफ़लाइन काम करता है।"),
            ("🇪🇸 Español", "¡Hola a todos! Bienvenidos al estudio de generación de voz neuronal totalmente local y seguro."),
            ("🇫🇷 Français", "Bonjour et bienvenue dans VoxCraft Studio, votre studio de synthèse vocale hors ligne.")
        ]:
            btn = QPushButton(name)
            btn.setProperty("class", "SecondaryBtn")
            btn.setStyleSheet("padding: 4px 8px; font-size: 11px;")
            btn.clicked.connect(lambda _, t=text: self.text_editor.setText(t))
            prompts_row.addWidget(btn)

        prompts_row.addStretch()

        btn_import = QPushButton("📄 Import File")
        btn_import.setProperty("class", "SecondaryBtn")
        btn_import.setStyleSheet("padding: 4px 10px; font-size: 11px; background: rgba(139, 92, 246, 0.15); border-color: rgba(139, 92, 246, 0.3);")
        btn_import.clicked.connect(self._import_file)
        prompts_row.addWidget(btn_import)

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

        lbl_controls = QLabel("Voice & Audio Settings")
        lbl_controls.setStyleSheet("font-size: 15px; font-weight: 700; color: #ffffff;")
        right_layout.addWidget(lbl_controls)

        # Single Unified Voice Selector
        right_layout.addWidget(QLabel("Speaker Voice:"))
        self.voice_combo = QComboBox()
        self.voice_combo.setStyleSheet("font-size: 13px; font-weight: 600; padding: 6px 10px;")
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

        # Voice Blending Toggle (Available for Kokoro Studio voices)
        self.blend_check = QCheckBox("🧬 Enable Voice Blending")
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

    def _import_file(self):
        from PySide6.QtWidgets import QFileDialog
        path, _ = QFileDialog.getOpenFileName(self, "Import Text or Script", "", "Text Files (*.txt *.md *.csv);;All Files (*)")
        if path:
            try:
                with open(path, "r", encoding="utf-8") as f:
                    self.text_editor.setText(f.read())
            except Exception as e:
                QMessageBox.warning(self, "Import Error", f"Could not read file:\n{e}")

    def _load_voices(self):
        self.voices = VoiceCatalog.get_tts_voices()
        self.voice_combo.blockSignals(True)
        self.voice_combo.clear()
        for v in self.voices:
            self.voice_combo.addItem(VoiceCatalog.format_label(v), v.get("id", ""))
        self.voice_combo.blockSignals(False)

        # Populate secondary blend combo with Kokoro voices
        self.blend_voice_b.clear()
        kokoro_voices = [v for v in self.voices if v.get("engine") == "kokoro"]
        for v in kokoro_voices:
            self.blend_voice_b.addItem(VoiceCatalog.format_label(v), v.get("id", ""))

        self._on_voice_changed(0)

    def _on_voice_changed(self, idx: int):
        voice_id = self.voice_combo.currentData() or ""
        v = VoiceCatalog.get_by_id(voice_id)
        is_kokoro = (v.get("engine") == "kokoro") if v else True
        self.blend_check.setVisible(is_kokoro)
        if not is_kokoro:
            self.blend_check.setChecked(False)
            self.blend_container.setVisible(False)

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
        if not v_meta:
            return

        # Check if the voice model package is installed locally
        installed, manifest_key = VoiceCatalog.is_model_installed(voice_id)
        if not installed:
            from ..widgets.download_dialog import ModelDownloadDialog
            dlg = ModelDownloadDialog(voice_meta=v_meta, manifest_key=manifest_key, parent=self)
            res = dlg.exec()
            if res == QDialog.Accepted:
                # Successfully downloaded model! Continue with synthesis
                self._start_synthesis(text, voice_id, v_meta)
            else:
                if getattr(dlg, 'download_in_background', False):
                    QMessageBox.information(
                        self, "Downloading in Background",
                        f"Model package for '{v_meta.get('name')}' is downloading in the background.\nYou will be able to use it once completed."
                    )
            return

        self._start_synthesis(text, voice_id, v_meta)

    def _start_synthesis(self, text: str, voice_id: str, v_meta: dict):
        engine_hint = v_meta.get("engine", "kokoro")

        voice_blend = None
        if self.blend_check.isChecked() and engine_hint == "kokoro":
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

