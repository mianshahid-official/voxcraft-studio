"""
TTS Studio - PySide6 F5-TTS Zero-Shot Voice Cloning Lab View
"""
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QTextEdit,
    QLineEdit, QPushButton, QFileDialog, QMessageBox, QProgressBar
)
from PySide6.QtCore import Qt, QThread, Signal

from ..widgets.cards import GlassCard
from ...services.tts_service import TTSService, SynthesisResult


class CloningWorker(QThread):
    finished = Signal(object)

    def __init__(self, ref_audio: str, ref_text: str, target_text: str):
        super().__init__()
        self.ref_audio = ref_audio
        self.ref_text = ref_text
        self.target_text = target_text

    def run(self):
        res = TTSService.synthesize_text(
            text=self.target_text,
            voice="f5_clone_custom",
            engine_hint="f5_tts",
            ref_audio_path=self.ref_audio,
            ref_text=self.ref_text
        )
        self.finished.emit(res)


class VoiceCloningView(QWidget):
    """F5-TTS Voice Cloning Lab View."""

    audioGenerated = Signal(str, str, str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.ref_audio_path = ""
        self._init_ui()

    def _init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(16)

        card = GlassCard()
        c_lay = QVBoxLayout(card)
        c_lay.setContentsMargins(20, 20, 20, 20)
        c_lay.setSpacing(14)

        lbl_title = QLabel("🧬 Zero-Shot Voice Cloning Lab (F5-TTS)")
        lbl_title.setStyleSheet("font-size: 16px; font-weight: 700; color: #ffffff;")
        c_lay.addWidget(lbl_title)

        lbl_desc = QLabel("Clone any speaker with 5-15 seconds of clean reference speech using flow-matching diffusion.")
        lbl_desc.setStyleSheet("color: #94a3b8; font-size: 12px;")
        c_lay.addWidget(lbl_desc)

        # Audio Upload Picker
        upload_box = QHBoxLayout()
        self.lbl_file = QLabel("No reference audio selected")
        self.lbl_file.setStyleSheet("color: #cbd5e1; font-family: 'Consolas'; font-size: 12px;")
        upload_box.addWidget(self.lbl_file, stretch=1)

        btn_pick = QPushButton("📂 Select Reference Audio (WAV/MP3)")
        btn_pick.setProperty("class", "SecondaryBtn")
        btn_pick.clicked.connect(self._pick_audio)
        upload_box.addWidget(btn_pick)
        c_lay.addLayout(upload_box)

        # Reference Transcript
        c_lay.addWidget(QLabel("Reference Transcript (What was spoken in the reference audio):"))
        self.ref_text_input = QLineEdit()
        self.ref_text_input.setPlaceholderText("e.g. Welcome to the future of voice technology.")
        c_lay.addWidget(self.ref_text_input)

        # Target Speech
        c_lay.addWidget(QLabel("Target Speech to Synthesize:"))
        self.target_text_input = QTextEdit()
        self.target_text_input.setPlaceholderText("Type the text you want the cloned voice to speak...")
        self.target_text_input.setText("This speech is synthesized using local flow matching diffusion without any cloud APIs.")
        c_lay.addWidget(self.target_text_input, stretch=1)

        self.prog_bar = QProgressBar()
        self.prog_bar.setVisible(False)
        c_lay.addWidget(self.prog_bar)

        self.btn_clone = QPushButton("🧬 Clone Voice & Synthesize")
        self.btn_clone.setProperty("class", "PrimaryBtn")
        self.btn_clone.setFixedHeight(44)
        self.btn_clone.clicked.connect(self._start_clone)
        c_lay.addWidget(self.btn_clone)

        layout.addWidget(card)

    def _pick_audio(self):
        f, _ = QFileDialog.getOpenFileName(self, "Select Voice Sample", "", "Audio Files (*.wav *.mp3)")
        if f:
            self.ref_audio_path = f
            self.lbl_file.setText(f"✓ Selected: {f.split('/')[-1]}")

    def _start_clone(self):
        target = self.target_text_input.toPlainText().strip()
        if not target:
            QMessageBox.warning(self, "Missing Text", "Please enter target text to synthesize.")
            return

        self.btn_clone.setEnabled(False)
        self.btn_clone.setText("⏳ Cloning & Generating...")
        self.prog_bar.setVisible(True)
        self.prog_bar.setRange(0, 0)  # Indeterminate

        self.worker = CloningWorker(
            self.ref_audio_path,
            self.ref_text_input.text().strip(),
            target
        )
        self.worker.finished.connect(self._on_finished)
        self.worker.start()

    def _on_finished(self, res: SynthesisResult):
        self.btn_clone.setEnabled(True)
        self.btn_clone.setText("🧬 Clone Voice & Synthesize")
        self.prog_bar.setVisible(False)

        if res.success and res.audio_path:
            self.audioGenerated.emit(
                res.audio_path,
                "Cloned Voice Output",
                f"{res.duration_sec}s • F5-TTS Diffusion"
            )
        else:
            QMessageBox.critical(self, "Cloning Error", f"Cloning failed:\n{res.error}")
