"""
VoxCraft Studio - Offline Model & Language Hub View
Download additional voice models and languages inside the desktop app.
"""
import os
import subprocess
from pathlib import Path
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QLineEdit, QComboBox, QScrollArea, QFrame, QProgressBar,
    QGridLayout, QMessageBox, QApplication
)
from PySide6.QtCore import Qt, QTimer, Signal

from ..widgets.cards import GlassCard, StatusBadge
from ...core.models import ModelManager, ModelStatus
from ...config.paths import MODELS_DIR


class ModelItemCard(QFrame):
    """Detailed interactive card for an offline neural voice model / language pack."""
    downloadRequested = Signal(str)
    cancelRequested = Signal(str)
    deleteRequested = Signal(str)

    def __init__(self, status: ModelStatus, parent=None):
        super().__init__(parent)
        self.status = status
        self.setProperty("class", "GlassCard")
        self._init_ui()

    def _init_ui(self):
        s = self.status
        lay = QVBoxLayout(self)
        lay.setContentsMargins(16, 14, 16, 14)
        lay.setSpacing(10)

        # Top Row: Flag + Name + Engine Badge + Size Tag
        top = QHBoxLayout()
        top.setSpacing(10)

        lbl_flag = QLabel(s.flag)
        lbl_flag.setStyleSheet("font-size: 24px; background: transparent; border: none;")
        top.addWidget(lbl_flag)

        name_box = QVBoxLayout()
        name_box.setSpacing(1)
        lbl_name = QLabel(s.name)
        lbl_name.setStyleSheet("font-weight: 700; font-size: 14px; color: #ffffff; background: transparent; border: none;")
        lbl_lang = QLabel(f"Language: <b>{s.language}</b> • Version: {s.version}")
        lbl_lang.setStyleSheet("font-size: 11px; color: #94a3b8; background: transparent; border: none;")
        name_box.addWidget(lbl_name)
        name_box.addWidget(lbl_lang)
        top.addLayout(name_box, stretch=1)

        eng_label = "ENGINE 1" if s.engine == "kokoro" else ("ENGINE 2" if s.engine == "piper" else "ENGINE 3")
        eng_badge = StatusBadge(eng_label, "gpu" if s.engine in ("kokoro", "f5_tts") else "cpu")
        top.addWidget(eng_badge)

        lbl_sz = QLabel(f"📦 {s.size_mb} MB")
        lbl_sz.setStyleSheet("color: #a78bfa; font-weight: 700; font-size: 11px; background: rgba(139, 92, 246, 0.15); padding: 4px 10px; border-radius: 6px; border: 1px solid rgba(139, 92, 246, 0.3);")
        top.addWidget(lbl_sz)
        lay.addLayout(top)

        # Middle: Description
        lbl_desc = QLabel(s.description)
        lbl_desc.setWordWrap(True)
        lbl_desc.setStyleSheet("color: #cbd5e1; font-size: 12px; line-height: 1.4; background: transparent; border: none;")
        lay.addWidget(lbl_desc)

        # Bottom: Status & Action Buttons
        bot = QHBoxLayout()
        bot.setSpacing(12)

        if s.is_installed:
            lbl_st = QLabel("✓ Ready (Offline)")
            lbl_st.setStyleSheet("color: #34d399; font-weight: 700; font-size: 12px; background: rgba(16, 185, 129, 0.12); padding: 4px 10px; border-radius: 6px; border: 1px solid rgba(16, 185, 129, 0.3);")
            bot.addWidget(lbl_st)
            bot.addStretch()

            btn_del = QPushButton("🗑️ Remove")
            btn_del.setProperty("class", "SecondaryBtn")
            btn_del.setStyleSheet("color: #f87171; border-color: rgba(248, 113, 113, 0.3);")
            btn_del.clicked.connect(lambda: self.deleteRequested.emit(s.key))
            bot.addWidget(btn_del)

        elif s.is_downloading:
            dl_box = QVBoxLayout()
            dl_box.setSpacing(4)

            p_row = QHBoxLayout()
            lbl_dl_st = QLabel(f"⬇️ Downloading: {s.progress_pct:.0f}%")
            lbl_dl_st.setStyleSheet("color: #38bdf8; font-weight: 700; font-size: 11px;")
            p_row.addWidget(lbl_dl_st)
            p_row.addStretch()
            lbl_sp = QLabel(f"{s.speed_mbps:.1f} MB/s • ETA: ~{s.eta_seconds}s")
            lbl_sp.setStyleSheet("color: #94a3b8; font-size: 11px; font-family: 'Consolas';")
            p_row.addWidget(lbl_sp)
            dl_box.addLayout(p_row)

            pbar = QProgressBar()
            pbar.setRange(0, 100)
            pbar.setValue(int(s.progress_pct))
            pbar.setTextVisible(False)
            pbar.setFixedHeight(8)
            dl_box.addWidget(pbar)
            bot.addLayout(dl_box, stretch=1)

            btn_cancel = QPushButton("✕ Cancel")
            btn_cancel.setProperty("class", "SecondaryBtn")
            btn_cancel.clicked.connect(lambda: self.cancelRequested.emit(s.key))
            bot.addWidget(btn_cancel)

        else:
            lbl_st = QLabel("Available to Download")
            lbl_st.setStyleSheet("color: #94a3b8; font-size: 11px;")
            bot.addWidget(lbl_st)
            bot.addStretch()

            btn_dl = QPushButton("⬇️ Download Model")
            btn_dl.setProperty("class", "PrimaryBtn")
            btn_dl.clicked.connect(lambda: self.downloadRequested.emit(s.key))
            bot.addWidget(btn_dl)

        lay.addLayout(bot)


class ModelsView(QWidget):
    """In-App Model & Multi-Lingual Voice Package Download Hub."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self._init_ui()

    def _init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(22, 20, 22, 20)
        layout.setSpacing(14)

        # 1. Top Summary Banner Card
        top_card = GlassCard()
        t_lay = QHBoxLayout(top_card)
        t_lay.setContentsMargins(18, 14, 18, 14)
        t_lay.setSpacing(16)

        title_box = QVBoxLayout()
        title_box.setSpacing(2)
        lbl_head = QLabel("📦 Offline Neural Model & Language Hub")
        lbl_head.setStyleSheet("font-size: 17px; font-weight: 800; color: #ffffff; background: transparent; border: none;")
        lbl_sub = QLabel("Download and manage offline speech engines and international language packages.")
        lbl_sub.setStyleSheet("font-size: 12px; color: #94a3b8; background: transparent; border: none;")
        title_box.addWidget(lbl_head)
        title_box.addWidget(lbl_sub)
        t_lay.addLayout(title_box, stretch=1)

        # Action Buttons
        self.lbl_installed_count = QLabel("Installed: 0")
        self.lbl_installed_count.setStyleSheet("color: #34d399; font-weight: 700; font-size: 12px; background: rgba(16, 185, 129, 0.12); padding: 6px 12px; border-radius: 8px; border: 1px solid rgba(16, 185, 129, 0.3);")
        t_lay.addWidget(self.lbl_installed_count)

        btn_open_folder = QPushButton("📁 Open Models Folder")
        btn_open_folder.setProperty("class", "SecondaryBtn")
        btn_open_folder.clicked.connect(self._open_models_folder)
        t_lay.addWidget(btn_open_folder)

        btn_refresh = QPushButton("🔄 Refresh")
        btn_refresh.setProperty("class", "SecondaryBtn")
        btn_refresh.clicked.connect(self.render_models)
        t_lay.addWidget(btn_refresh)

        layout.addWidget(top_card)

        # 2. Filter & Search Controls Bar
        filter_card = GlassCard()
        f_lay = QHBoxLayout(filter_card)
        f_lay.setContentsMargins(14, 10, 14, 10)
        f_lay.setSpacing(12)

        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("🔍 Search by model name, language, or engine...")
        self.search_input.textChanged.connect(self.render_models)
        f_lay.addWidget(self.search_input, stretch=2)

        self.combo_engine = QComboBox()
        self.combo_engine.addItems(["All Engines", "Engine 1: Kokoro-82M", "Engine 2: Piper Neural", "Engine 3: F5-TTS"])
        self.combo_engine.currentIndexChanged.connect(self.render_models)
        f_lay.addWidget(self.combo_engine)

        self.combo_lang = QComboBox()
        self.combo_lang.addItems(["All Languages", "English", "British English", "Spanish", "French", "German", "Italian", "Portuguese"])
        self.combo_lang.currentIndexChanged.connect(self.render_models)
        f_lay.addWidget(self.combo_lang)

        self.combo_status = QComboBox()
        self.combo_status.addItems(["All Statuses", "Installed (Ready)", "Available for Download"])
        self.combo_status.currentIndexChanged.connect(self.render_models)
        f_lay.addWidget(self.combo_status)

        layout.addWidget(filter_card)

        # 3. Scrollable List of Model Cards
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet("background: transparent; border: none;")

        self.cards_container = QWidget()
        self.cards_container.setStyleSheet("background: transparent;")
        self.cards_layout = QVBoxLayout(self.cards_container)
        self.cards_layout.setContentsMargins(0, 0, 0, 0)
        self.cards_layout.setSpacing(12)
        scroll.setWidget(self.cards_container)

        layout.addWidget(scroll, stretch=1)

        # Auto-refresh timer for live download progress
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.render_models)
        self.timer.start(1000)

        self.render_models()

    def render_models(self):
        # Clear existing
        while self.cards_layout.count():
            item = self.cards_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        all_models = ModelManager.get_all_models_status()
        installed_count = sum(1 for m in all_models if m.is_installed)
        self.lbl_installed_count.setText(f"Installed: {installed_count} / {len(all_models)} Models")

        # Filters
        query = self.search_input.text().strip().lower()
        eng_idx = self.combo_engine.currentIndex()
        eng_filter = {0: "all", 1: "kokoro", 2: "piper", 3: "f5_tts"}.get(eng_idx, "all")
        lang_idx = self.combo_lang.currentIndex()
        lang_filter = self.combo_lang.currentText() if lang_idx > 0 else "all"
        stat_idx = self.combo_status.currentIndex()

        filtered = []
        for m in all_models:
            if eng_filter != "all" and m.engine != eng_filter:
                continue
            if lang_filter != "all" and lang_filter.lower() not in m.language.lower():
                continue
            if stat_idx == 1 and not m.is_installed:
                continue
            if stat_idx == 2 and m.is_installed:
                continue
            if query and (query not in m.name.lower() and query not in m.description.lower() and query not in m.language.lower()):
                continue
            filtered.append(m)

        for s in filtered:
            card = ModelItemCard(s)
            card.downloadRequested.connect(self._on_download)
            card.cancelRequested.connect(self._on_cancel)
            card.deleteRequested.connect(self._on_delete)
            self.cards_layout.addWidget(card)

        self.cards_layout.addStretch()

    def _on_download(self, key: str):
        ModelManager.start_download(key)
        self.render_models()

    def _on_cancel(self, key: str):
        ModelManager.cancel_download(key)
        self.render_models()

    def _on_delete(self, key: str):
        reply = QMessageBox.question(
            self, "Confirm Delete",
            f"Are you sure you want to remove the model '{key}' from local storage?",
            QMessageBox.Yes | QMessageBox.No
        )
        if reply == QMessageBox.Yes:
            ModelManager.delete_model(key)
            self.render_models()

    def _open_models_folder(self):
        path = str(MODELS_DIR)
        if os.name == 'nt':
            os.startfile(path)
        else:
            subprocess.Popen(['xdg-open', path])
