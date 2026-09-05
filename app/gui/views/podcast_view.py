"""
TTS Studio - PySide6 Podcast & Multi-Speaker Dialogue Studio View
Features full speaker customization (engine, voice, rate, pitch, volume),
dynamic cast manager, syntax-assisted script editor, and full episode synthesis.
"""
from typing import List, Dict, Any, Optional
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QTextEdit,
    QPushButton, QComboBox, QScrollArea, QFrame, QMessageBox,
    QProgressBar, QLineEdit, QDialog
)
from PySide6.QtCore import Qt, QThread, Signal

from ..widgets.cards import GlassCard, StatusBadge
from ..widgets.sliders import LabeledSlider
from ...services.podcast_service import PodcastService
from ...voices.catalog import VoiceCatalog
from ...engines.registry import ENGINE_REGISTRY


class PodcastWorker(QThread):
    finished = Signal(object)
    progress = Signal(int, int, str)

    def __init__(self, speakers: list, dialogue: list, title: str):
        super().__init__()
        self.speakers = speakers
        self.dialogue = dialogue
        self.title = title

    def run(self):
        res = PodcastService.generate_episode(
            speakers=self.speakers,
            dialogue_blocks=self.dialogue,
            episode_title=self.title,
            progress_callback=lambda cur, tot, msg: self.progress.emit(cur, tot, msg)
        )
        self.finished.emit(res)


class SpeakerConfigCard(GlassCard):
    """Interactive card for configuring a single podcast speaker's profile."""

    speakerChanged = Signal()
    deleteRequested = Signal(object)

    def __init__(self, speaker_data: Dict[str, Any], parent=None):
        super().__init__(parent)
        self.speaker = speaker_data
        self._init_ui()

    def _init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(14, 12, 14, 12)
        layout.setSpacing(10)

        # Top Row: Avatar + Name Edit + Engine + Delete
        top_row = QHBoxLayout()
        top_row.setSpacing(8)

        self.lbl_avatar = QLabel(self.speaker.get("avatar", "🎙️"))
        self.lbl_avatar.setStyleSheet("font-size: 18px; background: transparent;")
        top_row.addWidget(self.lbl_avatar)

        self.name_edit = QLineEdit(self.speaker.get("name", "Speaker"))
        self.name_edit.setPlaceholderText("Speaker Name (e.g. Alex)")
        self.name_edit.setStyleSheet("font-weight: 700; font-size: 13px; padding: 5px 8px;")
        self.name_edit.textChanged.connect(self._on_name_changed)
        top_row.addWidget(self.name_edit, stretch=2)

        self.engine_combo = QComboBox()
        self.engine_combo.addItems(["All Engines", "Engine 1: Kokoro-82M", "Engine 2: Piper Neural", "Engine 3: F5-TTS"])
        eng = self.speaker.get("engine", "kokoro")
        eng_idx = 1 if eng == "kokoro" else (2 if eng == "piper" else (3 if eng == "f5_tts" else 0))
        self.engine_combo.setCurrentIndex(eng_idx)
        self.engine_combo.currentIndexChanged.connect(self._on_engine_changed)
        top_row.addWidget(self.engine_combo, stretch=2)

        self.btn_del = QPushButton("✕")
        self.btn_del.setToolTip("Remove Speaker")
        self.btn_del.setStyleSheet("color: #fda4af; background: rgba(244, 63, 94, 0.15); border: 1px solid rgba(244, 63, 94, 0.3); border-radius: 6px; padding: 4px 8px; font-weight: 700;")
        self.btn_del.clicked.connect(lambda: self.deleteRequested.emit(self))
        top_row.addWidget(self.btn_del)

        layout.addLayout(top_row)

        # Middle Row: Voice Selector
        voice_row = QHBoxLayout()
        voice_row.setSpacing(8)
        lbl_v = QLabel("Voice:")
        lbl_v.setStyleSheet("color: #94a3b8; font-size: 12px; font-weight: 600; background: transparent;")
        voice_row.addWidget(lbl_v)

        self.voice_combo = QComboBox()
        self._populate_voices()
        self.voice_combo.currentIndexChanged.connect(self._on_voice_changed)
        voice_row.addWidget(self.voice_combo, stretch=1)
        layout.addLayout(voice_row)

        # Bottom Row: Sliders (Speed, Pitch, Volume)
        sliders_row = QHBoxLayout()
        sliders_row.setSpacing(12)

        self.speed_slider = LabeledSlider("Rate", 0.5, 2.0, float(self.speaker.get("speed", 1.0)), 0.05, "x")
        self.speed_slider.valueChanged.connect(self._on_speed_changed)
        sliders_row.addWidget(self.speed_slider)

        self.pitch_slider = LabeledSlider("Pitch", -6.0, 6.0, float(self.speaker.get("pitch", 0.0)), 0.5, " st")
        self.pitch_slider.valueChanged.connect(self._on_pitch_changed)
        sliders_row.addWidget(self.pitch_slider)

        self.vol_slider = LabeledSlider("Volume", 0.2, 2.0, float(self.speaker.get("volume", 1.0)), 0.05, "x")
        self.vol_slider.valueChanged.connect(self._on_vol_changed)
        sliders_row.addWidget(self.vol_slider)

        layout.addLayout(sliders_row)

    def _populate_voices(self):
        self.voice_combo.blockSignals(True)
        self.voice_combo.clear()

        eng_idx = self.engine_combo.currentIndex()
        cur_eng = {1: "kokoro", 2: "piper", 3: "f5_tts"}.get(eng_idx, "all")
        all_v = VoiceCatalog.get_all()
        filtered = [v for v in all_v if cur_eng == "all" or v.get("engine") == cur_eng]

        target_voice = self.speaker.get("voice", "")
        selected_idx = 0

        for idx, v in enumerate(filtered):
            self.voice_combo.addItem(VoiceCatalog.format_label(v, include_engine=True), v.get("id"))
            if v.get("id") == target_voice:
                selected_idx = idx

        if filtered:
            self.voice_combo.setCurrentIndex(selected_idx)
            self.speaker["voice"] = self.voice_combo.currentData()

        self.voice_combo.blockSignals(False)

    def _on_engine_changed(self, idx: int):
        cur_eng = {1: "kokoro", 2: "piper", 3: "f5_tts"}.get(idx, "all")
        if cur_eng != "all":
            self.speaker["engine"] = cur_eng
        self._populate_voices()
        self.speakerChanged.emit()

    def _on_voice_changed(self, idx: int):
        vid = self.voice_combo.currentData()
        if vid:
            self.speaker["voice"] = vid
            v_meta = VoiceCatalog.get_by_id(vid)
            if v_meta and "engine" in v_meta:
                self.speaker["engine"] = v_meta["engine"]
            self.speakerChanged.emit()

    def _on_name_changed(self, text: str):
        clean_name = text.strip() or "Speaker"
        self.speaker["name"] = clean_name
        self.speaker["id"] = clean_name.lower().replace(" ", "_")
        self.speakerChanged.emit()

    def _on_speed_changed(self, val: float):
        self.speaker["speed"] = val

    def _on_pitch_changed(self, val: float):
        self.speaker["pitch"] = val

    def _on_vol_changed(self, val: float):
        self.speaker["volume"] = val

    def get_data(self) -> Dict[str, Any]:
        return {
            "id": self.speaker.get("id", "speaker"),
            "name": self.name_edit.text().strip() or "Speaker",
            "engine": "kokoro" if self.engine_combo.currentIndex() == 0 else ("piper" if self.engine_combo.currentIndex() == 1 else "f5_tts"),
            "voice": self.voice_combo.currentData() or "af_bella",
            "speed": self.speed_slider.value(),
            "pitch": self.pitch_slider.value(),
            "volume": self.vol_slider.value(),
            "color": self.speaker.get("color", "#8b5cf6"),
            "avatar": self.speaker.get("avatar", "🎙️")
        }


class PodcastView(QWidget):
    """Podcast Multi-Speaker Dialogue Studio."""

    audioGenerated = Signal(str, str, str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.speakers_data = [
            {"id": "alex", "name": "Alex (Host)", "engine": "kokoro", "voice": "am_michael", "speed": 1.0, "pitch": 0.0, "volume": 1.0, "color": "#8b5cf6", "avatar": "🎙️"},
            {"id": "elena", "name": "Dr. Elena (Guest)", "engine": "kokoro", "voice": "af_sarah", "speed": 0.98, "pitch": 0.0, "volume": 1.0, "color": "#06b6d4", "avatar": "🔬"},
            {"id": "narrator", "name": "Narrator", "engine": "piper", "voice": "piper-en_GB-alan-medium", "speed": 1.0, "pitch": 0.0, "volume": 1.0, "color": "#f59e0b", "avatar": "🎬"}
        ]
        self.card_widgets: List[SpeakerConfigCard] = []
        self._init_ui()

    def _init_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(14)

        # -------------------------------------------------------------
        # Section 1: Episode Cast Header & Speaker Cards
        # -------------------------------------------------------------
        cast_container = GlassCard()
        cast_layout = QVBoxLayout(cast_container)
        cast_layout.setContentsMargins(16, 14, 16, 14)
        cast_layout.setSpacing(12)

        cast_header = QHBoxLayout()
        lbl_cast = QLabel("Episode Cast & Speaker Configuration")
        lbl_cast.setStyleSheet("font-size: 15px; font-weight: 700; color: #ffffff; background: transparent;")
        cast_header.addWidget(lbl_cast)
        cast_header.addStretch()

        btn_add_spk = QPushButton("＋ Add Speaker")
        btn_add_spk.setProperty("class", "SecondaryBtn")
        btn_add_spk.setStyleSheet("padding: 5px 12px; font-size: 12px;")
        btn_add_spk.clicked.connect(self._add_speaker)
        cast_header.addWidget(btn_add_spk)

        btn_template = QPushButton("Template Script")
        btn_template.setProperty("class", "SecondaryBtn")
        btn_template.setStyleSheet("padding: 5px 12px; font-size: 12px;")
        btn_template.clicked.connect(self._load_template)
        cast_header.addWidget(btn_template)

        self.generate_btn = QPushButton("▶ Generate Full Podcast")
        self.generate_btn.setProperty("class", "PrimaryBtn")
        self.generate_btn.clicked.connect(self.generate_podcast)
        cast_header.addWidget(self.generate_btn)
        cast_layout.addLayout(cast_header)

        # Scroll area for speaker cards
        speakers_scroll = QScrollArea()
        speakers_scroll.setWidgetResizable(True)
        speakers_scroll.setFrameShape(QFrame.NoFrame)
        speakers_scroll.setFixedHeight(170)
        speakers_scroll.setStyleSheet("background: transparent;")

        self.speakers_holder = QWidget()
        self.speakers_holder.setStyleSheet("background: transparent;")
        self.cards_layout = QHBoxLayout(self.speakers_holder)
        self.cards_layout.setContentsMargins(0, 0, 0, 0)
        self.cards_layout.setSpacing(12)

        # Tag buttons layout
        self.tags_row = QHBoxLayout()
        self.tags_row.setSpacing(6)

        self._rebuild_speaker_cards()
        speakers_scroll.setWidget(self.speakers_holder)
        cast_layout.addWidget(speakers_scroll)

        main_layout.addWidget(cast_container)

        # -------------------------------------------------------------
        # Section 2: Dialogue Script Editor
        # -------------------------------------------------------------
        script_card = GlassCard()
        script_layout = QVBoxLayout(script_card)
        script_layout.setContentsMargins(16, 14, 16, 14)
        script_layout.setSpacing(10)

        editor_header = QHBoxLayout()
        lbl_script = QLabel("Multi-Speaker Script Editor")
        lbl_script.setStyleSheet("font-size: 14px; font-weight: 700; color: #ffffff; background: transparent;")
        editor_header.addWidget(lbl_script)
        editor_header.addStretch()

        editor_header.addLayout(self.tags_row)
        script_layout.addLayout(editor_header)

        self.script_editor = QTextEdit()
        self.script_editor.setPlaceholderText("Prefix each dialogue turn with 'SpeakerName:' (e.g. Alex: Welcome everyone!)...")
        self.script_editor.setText(
            "Narrator: Episode 42: The Dawn of Local Machine Intelligence.\n"
            "Alex: Welcome back everyone. Today we are speaking with Dr. Elena about neural voice synthesis running completely offline on your desktop.\n"
            "Elena: Thanks for having me, Alex! The breakthrough here is delivering ultra-low latency with zero cloud dependencies.\n"
            "Alex: That means complete privacy and limitless audio generation without a single API key."
        )
        script_layout.addWidget(self.script_editor, stretch=1)

        self.prog_bar = QProgressBar()
        self.prog_bar.setVisible(False)
        script_layout.addWidget(self.prog_bar)

        main_layout.addWidget(script_card, stretch=1)

    def _rebuild_speaker_cards(self):
        # Clear existing
        while self.cards_layout.count() > 0:
            item = self.cards_layout.takeAt(0)
            w = item.widget()
            if w:
                w.deleteLater()
        self.card_widgets.clear()

        for s_data in self.speakers_data:
            card = SpeakerConfigCard(s_data)
            card.speakerChanged.connect(self._rebuild_tag_buttons)
            card.deleteRequested.connect(self._remove_speaker_card)
            self.card_widgets.append(card)
            self.cards_layout.addWidget(card)

        self.cards_layout.addStretch()
        self._rebuild_tag_buttons()

    def _rebuild_tag_buttons(self):
        while self.tags_row.count() > 0:
            item = self.tags_row.takeAt(0)
            w = item.widget()
            if w:
                w.deleteLater()

        lbl_ins = QLabel("Insert:")
        lbl_ins.setStyleSheet("color: #94a3b8; font-size: 11px; background: transparent;")
        self.tags_row.addWidget(lbl_ins)

        for card in self.card_widgets:
            s_name = card.name_edit.text().strip() or "Speaker"
            first_name = s_name.split()[0]
            btn = QPushButton(f"＋ {first_name}")
            btn.setProperty("class", "SecondaryBtn")
            btn.setStyleSheet("padding: 3px 8px; font-size: 11px;")
            btn.clicked.connect(lambda _, n=first_name: self._insert_speaker_tag(n))
            self.tags_row.addWidget(btn)

    def _insert_speaker_tag(self, name: str):
        cursor = self.script_editor.textCursor()
        cursor.insertText(f"\n{name}: ")
        self.script_editor.setFocus()

    def _add_speaker(self):
        count = len(self.card_widgets) + 1
        avatars = ["🎙️", "🔬", "🎬", "💼", "✨", "👑", "🎧", "🎩"]
        colors = ["#8b5cf6", "#06b6d4", "#f59e0b", "#10b981", "#ec4899", "#3b82f6"]
        new_spk = {
            "id": f"speaker_{count}",
            "name": f"Speaker {count}",
            "engine": "kokoro",
            "voice": "af_bella",
            "speed": 1.0,
            "pitch": 0.0,
            "volume": 1.0,
            "color": colors[count % len(colors)],
            "avatar": avatars[count % len(avatars)]
        }
        self.speakers_data.append(new_spk)
        self._rebuild_speaker_cards()

    def _remove_speaker_card(self, card: SpeakerConfigCard):
        if len(self.card_widgets) <= 1:
            QMessageBox.warning(self, "Minimum Speakers", "You must have at least one speaker for podcast generation.")
            return
        if card in self.card_widgets:
            idx = self.card_widgets.index(card)
            self.card_widgets.remove(card)
            if idx < len(self.speakers_data):
                self.speakers_data.pop(idx)
            card.deleteLater()
            self._rebuild_tag_buttons()

    def _load_template(self):
        self.script_editor.setText(
            "Narrator: Welcome to the VoxCraft Studio Showcase.\n"
            "Alex: Today we are demonstrating how multiple neural voices can dialogue together seamlessly.\n"
            "Elena: Each speaker maintains their own rate, pitch, and voice profile running 100% offline.\n"
            "Alex: Generating full episodes in seconds without any cloud latency."
        )

    def generate_podcast(self):
        text = self.script_editor.toPlainText().strip()
        if not text:
            QMessageBox.warning(self, "Empty Script", "Please enter dialogue script.")
            return

        current_speakers = [c.get_data() for c in self.card_widgets]
        dialogue = PodcastService.parse_script_text(text, default_speaker_id=current_speakers[0]["id"])

        if not dialogue:
            QMessageBox.warning(self, "Empty Dialogue", "Could not parse any dialogue turns from script.")
            return

        self.generate_btn.setEnabled(False)
        self.generate_btn.setText("⏳ Synthesizing Episode...")
        self.prog_bar.setVisible(True)
        self.prog_bar.setValue(0)

        self.worker = PodcastWorker(current_speakers, dialogue, "Podcast_Master")
        self.worker.progress.connect(lambda cur, tot, msg: self.prog_bar.setValue(int((cur / max(1, tot)) * 100)))
        self.worker.finished.connect(self._on_finished)
        self.worker.start()

    def _on_finished(self, res: dict):
        self.generate_btn.setEnabled(True)
        self.generate_btn.setText("▶ Generate Full Podcast")
        self.prog_bar.setVisible(False)

        if res.get("success") and res.get("master_audio_path"):
            self.audioGenerated.emit(
                res["master_audio_path"],
                "Podcast Master Episode",
                f"{res['total_duration_sec']}s • {res['num_blocks']} Dialogue Turns"
            )
        else:
            QMessageBox.critical(self, "Podcast Error", f"Generation failed:\n{res.get('error')}")
