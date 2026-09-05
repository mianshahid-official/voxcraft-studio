from pathlib import Path
import sys
from PySide6.QtWidgets import (
    QMainWindow, QWidget, QHBoxLayout, QVBoxLayout, QStackedWidget,
    QPushButton, QLabel, QFrame, QApplication, QButtonGroup
)
from PySide6.QtCore import Qt
from PySide6.QtGui import QIcon, QPixmap

from .theme import DARK_STUDIO_QSS
from .widgets.audio_player import AudioPlayerWidget
from .widgets.resource_monitor import ResourceMonitorWidget
from .views.tts_view import TTSView
from .views.podcast_view import PodcastView
from .views.batch_view import BatchView
from .views.voice_library_view import VoiceLibraryView
from .views.voice_cloning_view import VoiceCloningView
from .views.models_view import ModelsView
from .views.settings_view import SettingsView
from .wizard.setup_wizard import SetupWizardDialog
from ..config.settings import APP_CONFIG


class MainWindow(QMainWindow):
    """Production PySide6 Desktop Studio Main Window."""

    def __init__(self, check_first_run: bool = True):
        super().__init__()
        self.setWindowTitle("VoxCraft Studio — Offline Neural TTS & Podcast Engine")
        self.resize(1300, 850)
        self.setMinimumSize(1080, 700)

        # Apply Global Dark Studio Theme
        self.setStyleSheet(DARK_STUDIO_QSS)

        # Set Application Icon
        icon_path = Path(__file__).resolve().parent.parent / "resources" / "icons" / "app_icon.png"
        if icon_path.exists():
            self.setWindowIcon(QIcon(str(icon_path)))

        self._init_ui()
        if check_first_run:
            self._check_first_run()

    def _init_ui(self):
        central = QWidget()
        self.setCentralWidget(central)
        root_layout = QVBoxLayout(central)
        root_layout.setContentsMargins(0, 0, 0, 0)
        root_layout.setSpacing(0)

        # Top Body: Sidebar + Main Workspace
        body = QHBoxLayout()
        body.setContentsMargins(0, 0, 0, 0)
        body.setSpacing(0)

        # 1. Left Sidebar
        self.sidebar = QFrame()
        self.sidebar.setObjectName("Sidebar")
        self.sidebar.setFixedWidth(250)
        side_layout = QVBoxLayout(self.sidebar)
        side_layout.setContentsMargins(14, 18, 14, 14)
        side_layout.setSpacing(6)

        # Brand Header
        brand_row = QHBoxLayout()
        brand_row.setSpacing(10)

        icon_path = Path(__file__).resolve().parent.parent / "resources" / "icons" / "app_icon.png"
        if icon_path.exists():
            logo_img = QLabel()
            pix = QPixmap(str(icon_path)).scaled(36, 36, Qt.KeepAspectRatio, Qt.SmoothTransformation)
            logo_img.setPixmap(pix)
            logo_img.setStyleSheet("background: transparent; border: none;")
            brand_row.addWidget(logo_img)
        else:
            logo_lbl = QLabel("🎙️")
            logo_lbl.setStyleSheet("font-size: 24px; background: transparent; border: none;")
            brand_row.addWidget(logo_lbl)

        brand_text = QVBoxLayout()
        brand_text.setSpacing(0)
        b_title = QLabel("VoxCraft Studio")
        b_title.setStyleSheet("font-size: 15px; font-weight: 800; color: #ffffff; background: transparent; border: none;")
        b_sub = QLabel("Offline Neural Audio")
        b_sub.setStyleSheet("font-size: 10px; color: #06b6d4; font-weight: 600; background: transparent; border: none;")
        brand_text.addWidget(b_title)
        brand_text.addWidget(b_sub)
        brand_row.addLayout(brand_text)
        brand_row.addStretch()
        side_layout.addLayout(brand_row)
        side_layout.addSpacing(10)

        # Navigation Buttons Group
        self.nav_group = QButtonGroup(self)
        self.nav_group.setExclusive(True)

        nav_items = [
            ("⚡ Studio TTS", 0),
            ("📻 Podcast Studio", 1),
            ("📦 Batch Processing", 2),
            ("🎭 Voice Library", 3),
            ("🧬 Voice Cloning", 4),
            ("📦 Model Hub", 5),
            ("⚙️ Settings", 6)
        ]

        self.nav_buttons = []
        for text, idx in nav_items:
            btn = QPushButton(text)
            btn.setObjectName("NavBtn")
            btn.setCheckable(True)
            if idx == 0:
                btn.setChecked(True)
            btn.clicked.connect(lambda _, i=idx: self.switch_view(i))
            self.nav_group.addButton(btn)
            self.nav_buttons.append(btn)
            side_layout.addWidget(btn)

        side_layout.addStretch()

        # Sidebar Resource Monitor HUD
        self.res_monitor = ResourceMonitorWidget()
        side_layout.addWidget(self.res_monitor)
        side_layout.addSpacing(6)

        # Developer Signature
        author_box = QFrame()
        author_box.setStyleSheet("background-color: rgba(139, 92, 246, 0.08); border: 1px solid rgba(139, 92, 246, 0.2); border-radius: 8px; padding: 4px;")
        auth_lay = QHBoxLayout(author_box)
        auth_lay.setContentsMargins(8, 6, 8, 6)
        auth_lay.setSpacing(6)
        lbl_sparkle = QLabel("✨")
        lbl_sparkle.setStyleSheet("font-size: 14px; background: transparent; border: none;")
        auth_lay.addWidget(lbl_sparkle)
        auth_text = QVBoxLayout()
        auth_text.setSpacing(0)
        lbl_by = QLabel("DEVELOPED BY")
        lbl_by.setStyleSheet("font-size: 8px; font-weight: 800; color: #06b6d4; letter-spacing: 0.5px; background: transparent; border: none;")
        lbl_name = QLabel("Shahid")
        lbl_name.setStyleSheet("font-size: 11px; font-weight: 700; color: #ffffff; background: transparent; border: none;")
        auth_text.addWidget(lbl_by)
        auth_text.addWidget(lbl_name)
        auth_lay.addLayout(auth_text)
        auth_lay.addStretch()
        side_layout.addWidget(author_box)

        body.addWidget(self.sidebar)

        # 2. Center Workspace (Stacked Views)
        self.stack = QStackedWidget()

        self.view_tts = TTSView()
        self.view_podcast = PodcastView()
        self.view_batch = BatchView()
        self.view_voices = VoiceLibraryView()
        self.view_cloning = VoiceCloningView()
        self.view_models = ModelsView()
        self.view_settings = SettingsView()

        self.stack.addWidget(self.view_tts)       # 0
        self.stack.addWidget(self.view_podcast)   # 1
        self.stack.addWidget(self.view_batch)     # 2
        self.stack.addWidget(self.view_voices)    # 3
        self.stack.addWidget(self.view_cloning)   # 4
        self.stack.addWidget(self.view_models)    # 5
        self.stack.addWidget(self.view_settings)  # 6

        body.addWidget(self.stack, stretch=1)
        root_layout.addLayout(body, stretch=1)

        # 3. Bottom Audio Player Bar
        self.player_bar = AudioPlayerWidget()
        root_layout.addWidget(self.player_bar)

        # Connect view audio generation signals to global player bar
        self.view_tts.audioGenerated.connect(self.player_bar.load_audio)
        self.view_podcast.audioGenerated.connect(self.player_bar.load_audio)
        self.view_voices.audioPreviewGenerated.connect(self.player_bar.load_audio)
        self.view_cloning.audioGenerated.connect(self.player_bar.load_audio)
        self.view_voices.voiceSelected.connect(self._on_voice_selected_from_library)

    def switch_view(self, index: int):
        self.stack.setCurrentIndex(index)
        if index < len(self.nav_buttons):
            self.nav_buttons[index].setChecked(True)

    def _on_voice_selected_from_library(self, voice_id: str, engine: str):
        self.switch_view(0)
        # Select voice in TTS view
        eng_idx = 1 if engine == "kokoro" else (2 if engine == "piper" else (3 if engine == "f5_tts" else 0))
        self.view_tts.engine_combo.setCurrentIndex(eng_idx)
        idx = self.view_tts.voice_combo.findData(voice_id)
        if idx >= 0:
            self.view_tts.voice_combo.setCurrentIndex(idx)

    def _check_first_run(self):
        if not APP_CONFIG.first_run_completed:
            wizard = SetupWizardDialog(self)
            wizard.exec()
