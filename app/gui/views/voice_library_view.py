"""
VoxCraft Studio - PySide6 Voice Library & Explorer View
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

        # Top row: Avatar + Name + Quality Badge
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
        if eng == "kokoro":
            badge = StatusBadge("⭐ Studio HD", "gpu")
        elif eng == "f5_tts":
            badge = StatusBadge("🧬 Cloned", "gpu")
        else:
            badge = StatusBadge("🎙️ Narrator", "cpu")
        top.addWidget(badge)
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

        self.combo_type = QComboBox()
        self.combo_type.addItems(["All Voice Types", "⭐ Studio HD Voices", "🎙️ Narrator Voices", "🧬 Cloned Voices"])
        self.combo_type.currentIndexChanged.connect(self._render_grid)
        f_lay.addWidget(self.combo_type)

        self.combo_gen = QComboBox()
        self.combo_gen.addItems(["All Genders", "Female", "Male"])
        self.combo_gen.currentIndexChanged.connect(self._render_grid)
        f_lay.addWidget(self.combo_gen)

        self.combo_lang = QComboBox()
        self.combo_lang.addItem("All Languages")
        for lang in VoiceCatalog.get_languages():
            self.combo_lang.addItem(lang)
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

        type_map = {0: "all", 1: "kokoro", 2: "piper", 3: "f5_tts"}
        cur_type = type_map.get(self.combo_type.currentIndex(), "all")
        cur_gen = "all" if self.combo_gen.currentIndex() == 0 else ("female" if self.combo_gen.currentIndex() == 1 else "male")
        cur_lang = "all" if self.combo_lang.currentIndex() == 0 else self.combo_lang.currentText()
        query = self.search_box.text().strip()

        filtered = VoiceCatalog.filter(engine=cur_type, gender=cur_gen, language=cur_lang, query=query)

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

        installed, manifest_key = VoiceCatalog.is_model_installed(voice_id)
        if not installed:
            from ..widgets.download_dialog import ModelDownloadDialog
            from PySide6.QtWidgets import QDialog
            dlg = ModelDownloadDialog(voice_meta=v, manifest_key=manifest_key, parent=self)
            if dlg.exec() != QDialog.Accepted:
                return

        sample_text = v.get("sample", "Welcome to offline speech synthesis with VoxCraft Studio.")
        res = TTSService.synthesize_text(sample_text, voice=voice_id, engine_hint=engine)
        if res.success and res.audio_path:
            self.audioPreviewGenerated.emit(res.audio_path, f"{v.get('avatar', '🎙️')} {v['name']} ({v['language']})", f"{v['language']} • Preview")

    def _on_select_requested(self, voice_id: str, engine: str):
        self.voiceSelected.emit(voice_id, engine)
