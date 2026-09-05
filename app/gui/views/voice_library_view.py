"""
TTS Studio - PySide6 Voice Library & Explorer View
"""
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit,
    QComboBox, QScrollArea, QGridLayout, QFrame, QPushButton, QMessageBox
)
from PySide6.QtCore import Qt, Signal

from ..widgets.cards import GlassCard, StatusBadge
from ...voices.catalog import VoiceCatalog
from ...services.tts_service import TTSService


class VoiceCardWidget(GlassCard):
    previewRequested = Signal(str, str)
    selectRequested = Signal(str, str)

    def __init__(self, voice_meta: dict, parent=None):
        super().__init__(parent)
        self.voice_meta = voice_meta
        self._init_ui()

    def _init_ui(self):
        v = self.voice_meta
        layout = QVBoxLayout(self)
        layout.setContentsMargins(14, 14, 14, 14)
        layout.setSpacing(8)

        # Top row: Avatar + Name + Engine Badge
        top = QHBoxLayout()
        avatar = QLabel(v.get("avatar", "🎙️"))
        avatar.setStyleSheet("font-size: 24px; background: transparent; border: none;")
        top.addWidget(avatar)

        name_box = QVBoxLayout()
        lbl_name = QLabel(f"{v.get('name', 'Voice')} ({v.get('language', 'English')})")
        lbl_name.setStyleSheet("font-weight: 700; font-size: 14px; color: #fff; border: none; background: transparent;")
        lbl_sub = QLabel(f"{v.get('gender')} • {v.get('style', 'Natural')}")
        lbl_sub.setStyleSheet("font-size: 11px; color: #94a3b8; border: none; background: transparent;")
        name_box.addWidget(lbl_name)
        name_box.addWidget(lbl_sub)
        top.addLayout(name_box, stretch=1)

        eng = v.get("engine", "kokoro")
        eng_label = "ENGINE 1" if eng == "kokoro" else ("ENGINE 2" if eng == "piper" else "ENGINE 3")
        eng_badge = StatusBadge(eng_label, "gpu" if eng in ("kokoro", "f5_tts") else "cpu")
        top.addWidget(eng_badge)
        layout.addLayout(top)

        # Sample preview sentence
        lbl_desc = QLabel(f"<i>\"{v.get('sample', '')}\"</i>")
        lbl_desc.setWordWrap(True)
        lbl_desc.setStyleSheet("color: #cbd5e1; font-size: 11px; border: none; background: transparent; line-height: 1.3;")
        layout.addWidget(lbl_desc)

        # Action Buttons
        btn_row = QHBoxLayout()
        btn_prev = QPushButton("▶ Preview")
        btn_prev.setProperty("class", "SecondaryBtn")
        btn_prev.clicked.connect(lambda: self.previewRequested.emit(v.get("id", ""), v.get("engine", "kokoro")))
        btn_row.addWidget(btn_prev, stretch=1)

        btn_sel = QPushButton("Select Voice")
        btn_sel.setProperty("class", "PrimaryBtn")
        btn_sel.clicked.connect(lambda: self.selectRequested.emit(v.get("id", ""), v.get("engine", "kokoro")))
        btn_row.addWidget(btn_sel)
        layout.addLayout(btn_row)


class VoiceLibraryView(QWidget):
    """Voice Explorer & Browser View."""

    audioPreviewGenerated = Signal(str, str, str)
    voiceSelected = Signal(str, str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.voices = VoiceCatalog.get_all()
        self._init_ui()

    def _init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(16)

        # Filter Bar Card
        filter_card = GlassCard()
        f_lay = QHBoxLayout(filter_card)
        f_lay.setContentsMargins(14, 12, 14, 12)
        f_lay.setSpacing(12)

        self.search_box = QLineEdit()
        self.search_box.setPlaceholderText("🔍 Search voice by character name, language, or style...")
        self.search_box.textChanged.connect(self._render_grid)
        f_lay.addWidget(self.search_box, stretch=2)

        self.combo_eng = QComboBox()
        self.combo_eng.addItems(["All Engines", "Engine 1: Kokoro-82M", "Engine 2: Piper Neural", "Engine 3: F5-TTS"])
        self.combo_eng.currentIndexChanged.connect(self._render_grid)
        f_lay.addWidget(self.combo_eng)

        self.combo_gen = QComboBox()
        self.combo_gen.addItems(["All Genders", "Female", "Male"])
        self.combo_gen.currentIndexChanged.connect(self._render_grid)
        f_lay.addWidget(self.combo_gen)

        self.combo_lang = QComboBox()
        self.combo_lang.addItems(["All Languages", "English", "British English", "Spanish", "French", "German", "Italian", "Portuguese"])
        self.combo_lang.currentIndexChanged.connect(self._render_grid)
        f_lay.addWidget(self.combo_lang)

        layout.addWidget(filter_card)

        # Scrollable Voice Cards Grid
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet("background: transparent; border: none;")

        self.grid_container = QWidget()
        self.grid_container.setStyleSheet("background: transparent;")
        self.grid_layout = QGridLayout(self.grid_container)
        self.grid_layout.setSpacing(14)
        scroll.setWidget(self.grid_container)

        layout.addWidget(scroll, stretch=1)
        self._render_grid()

    def _render_grid(self):
        # Clear existing
        while self.grid_layout.count():
            item = self.grid_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        eng_map = {0: "all", 1: "kokoro", 2: "piper", 3: "f5_tts"}
        cur_eng = eng_map.get(self.combo_eng.currentIndex(), "all")
        cur_gen = "all" if self.combo_gen.currentIndex() == 0 else ("female" if self.combo_gen.currentIndex() == 1 else "male")
        cur_lang = "all" if self.combo_lang.currentIndex() == 0 else self.combo_lang.currentText()
        query = self.search_box.text().strip()

        filtered = VoiceCatalog.filter(engine=cur_eng, gender=cur_gen, language=cur_lang, query=query)

        cols = 3
        for idx, v in enumerate(filtered):
            card = VoiceCardWidget(v)
            card.previewRequested.connect(self._on_preview_requested)
            card.selectRequested.connect(self._on_select_requested)
            self.grid_layout.addWidget(card, idx // cols, idx % cols)

    def _on_preview_requested(self, voice_id: str, engine: str):
        v = VoiceCatalog.get_by_id(voice_id)
        if not v:
            return
        sample_text = v.get("sample", "Welcome to offline speech synthesis with VoxCraft Studio.")
        res = TTSService.synthesize_text(sample_text, voice=voice_id, engine_hint=engine)
        if res.success and res.audio_path:
            self.audioPreviewGenerated.emit(res.audio_path, f"{v.get('avatar', '🎙️')} {v['name']} ({v['language']})", f"{v['language']} • Preview")

    def _on_select_requested(self, voice_id: str, engine: str):
        self.voiceSelected.emit(voice_id, engine)
