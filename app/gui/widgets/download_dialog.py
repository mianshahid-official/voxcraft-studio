"""
VoxCraft Studio - On-Demand Model Download Modal Dialog
Displays model information, file size, real-time download progress, and options to cancel or download in background.
"""
from typing import Dict, Any, Optional
from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QProgressBar, QFrame
)
from PySide6.QtCore import Qt, QTimer, Signal

from ...backend.model_manager import ModelManager
from ...backend.config import MODEL_DOWNLOAD_MANIFEST


class ModelDownloadDialog(QDialog):
    """
    Sleek dark-themed modal dialog for on-demand model downloads.
    Provides real-time progress, speed, ETA, and background downloading.
    """
    downloadCompleted = Signal(str)

    def __init__(self, voice_meta: Dict[str, Any], manifest_key: str, parent=None):
        super().__init__(parent)
        self.voice_meta = voice_meta
        self.manifest_key = manifest_key
        self.manifest_data = MODEL_DOWNLOAD_MANIFEST.get(manifest_key, {})
        self.is_downloading = False
        self.download_in_background = False

        self._init_window()
        self._init_ui()
        self._init_timer()

    def _init_window(self):
        self.setWindowTitle("Voice Package Required — VoxCraft Studio")
        self.setFixedSize(500, 340)
        self.setWindowFlags(self.windowFlags() & ~Qt.WindowContextHelpButtonHint)
        self.setStyleSheet("""
            QDialog {
                background-color: #0b0e17;
                color: #f8fafc;
                font-family: 'Segoe UI', sans-serif;
            }
        """)

    def _init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 24, 24, 24)
        layout.setSpacing(14)

        # Header: Icon + Title
        hdr = QHBoxLayout()
        icon_lbl = QLabel("📦")
        icon_lbl.setStyleSheet("font-size: 26px; background: transparent;")
        hdr.addWidget(icon_lbl)

        title_box = QVBoxLayout()
        title_lbl = QLabel("Voice Package Required")
        title_lbl.setStyleSheet("font-size: 16px; font-weight: 700; color: #ffffff;")
        sub_lbl = QLabel("This voice requires a 1-time offline package download before generating speech.")
        sub_lbl.setStyleSheet("font-size: 12px; color: #94a3b8;")
        title_box.addWidget(title_lbl)
        title_box.addWidget(sub_lbl)
        hdr.addLayout(title_box, stretch=1)
        layout.addLayout(hdr)

        # Details Card
        card = QFrame()
        card.setStyleSheet("""
            QFrame {
                background-color: #111625;
                border: 1px solid rgba(255, 255, 255, 0.08);
                border-radius: 10px;
                padding: 10px;
            }
        """)
        card_lay = QVBoxLayout(card)
        card_lay.setContentsMargins(14, 12, 14, 12)
        card_lay.setSpacing(6)

        v_name = self.voice_meta.get("name", "Selected Voice")
        v_lang = self.voice_meta.get("language", "Standard")
        v_avatar = self.voice_meta.get("avatar", "🎙️")
        m_name = self.manifest_data.get("name", self.manifest_key)
        m_size = self.manifest_data.get("size_mb", 60)

        card_lay.addWidget(self._create_info_row("Selected Voice:", f"{v_avatar} {v_name} ({v_lang})"))
        card_lay.addWidget(self._create_info_row("Voice Package:", m_name))
        card_lay.addWidget(self._create_info_row("Package Size:", f"~{m_size} MB"))
        card_lay.addWidget(self._create_info_row("Storage Location:", "Local Storage (100% Offline)"))
        layout.addWidget(card)

        # Progress Area
        self.progress_frame = QFrame()
        self.progress_frame.setVisible(False)
        p_lay = QVBoxLayout(self.progress_frame)
        p_lay.setContentsMargins(0, 4, 0, 4)
        p_lay.setSpacing(6)

        self.prog_bar = QProgressBar()
        self.prog_bar.setFixedHeight(8)
        self.prog_bar.setTextVisible(False)
        self.prog_bar.setStyleSheet("""
            QProgressBar {
                background-color: #1e293b;
                border-radius: 4px;
                border: none;
            }
            QProgressBar::chunk {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #8b5cf6, stop:1 #06b6d4);
                border-radius: 4px;
            }
        """)
        p_lay.addWidget(self.prog_bar)

        self.status_lbl = QLabel("0% — Connecting...")
        self.status_lbl.setStyleSheet("font-size: 11px; color: #cbd5e1; font-family: 'Consolas', monospace;")
        p_lay.addWidget(self.status_lbl)
        layout.addWidget(self.progress_frame)

        layout.addStretch()

        # Action Buttons Row
        self.btn_row = QHBoxLayout()
        self.btn_row.setSpacing(10)

        self.btn_cancel = QPushButton("Cancel")
        self.btn_cancel.setStyleSheet("""
            QPushButton {
                background-color: #1e293b;
                color: #cbd5e1;
                border: 1px solid rgba(255, 255, 255, 0.08);
                border-radius: 8px;
                padding: 8px 16px;
                font-weight: 600;
                font-size: 12px;
            }
            QPushButton:hover { background-color: #334155; }
        """)
        self.btn_cancel.clicked.connect(self._on_cancel_clicked)
        self.btn_row.addWidget(self.btn_cancel)

        self.btn_bg = QPushButton("📥 Download in Background")
        self.btn_bg.setVisible(False)
        self.btn_bg.setStyleSheet("""
            QPushButton {
                background-color: rgba(6, 182, 212, 0.15);
                color: #38bdf8;
                border: 1px solid rgba(6, 182, 212, 0.3);
                border-radius: 8px;
                padding: 8px 14px;
                font-weight: 600;
                font-size: 12px;
            }
            QPushButton:hover { background-color: rgba(6, 182, 212, 0.25); }
        """)
        self.btn_bg.clicked.connect(self._on_background_clicked)
        self.btn_row.addWidget(self.btn_bg)

        self.btn_primary = QPushButton("⬇ Install Voice Package")
        self.btn_primary.setStyleSheet("""
            QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #8b5cf6, stop:1 #7c3aed);
                color: #ffffff;
                border: none;
                border-radius: 8px;
                padding: 8px 20px;
                font-weight: 700;
                font-size: 12px;
            }
            QPushButton:hover { background: #7c3aed; }
        """)
        self.btn_primary.clicked.connect(self._start_download)
        self.btn_row.addWidget(self.btn_primary)

        layout.addLayout(self.btn_row)

    def _create_info_row(self, label: str, value: str) -> QFrame:
        row = QFrame()
        r_lay = QHBoxLayout(row)
        r_lay.setContentsMargins(0, 2, 0, 2)
        
        lbl_k = QLabel(label)
        lbl_k.setStyleSheet("color: #94a3b8; font-size: 12px; font-weight: 600; border: none; background: transparent;")
        lbl_k.setFixedWidth(130)
        r_lay.addWidget(lbl_k)

        lbl_v = QLabel(value)
        lbl_v.setStyleSheet("color: #f8fafc; font-size: 12px; border: none; background: transparent;")
        r_lay.addWidget(lbl_v, stretch=1)
        return row

    def _init_timer(self):
        self.poll_timer = QTimer(self)
        self.poll_timer.setInterval(200)
        self.poll_timer.timeout.connect(self._poll_progress)

    def _start_download(self):
        self.is_downloading = True
        self.progress_frame.setVisible(True)
        self.btn_primary.setEnabled(False)
        self.btn_primary.setText("Downloading...")
        self.btn_bg.setVisible(True)

        # Start downloading through ModelManager
        ModelManager.start_model_download(self.manifest_key)
        self.poll_timer.start()

    def _poll_progress(self):
        prog = ModelManager.get_download_progress(self.manifest_key)
        status = prog.get("status", "idle")
        pct = int(prog.get("progress", 0))
        speed = prog.get("speed_mbps", 0.0)
        eta = prog.get("eta_seconds", 0)

        self.prog_bar.setValue(pct)

        if status == "downloading":
            self.status_lbl.setText(f"{pct}% — {speed} MB/s (ETA: ~{eta}s)")
        elif status == "completed":
            self.poll_timer.stop()
            self.prog_bar.setValue(100)
            self.status_lbl.setText("✓ Download complete! Initializing...")
            self.status_lbl.setStyleSheet("font-size: 11px; color: #10b981; font-weight: 700;")
            self.downloadCompleted.emit(self.manifest_key)
            QTimer.singleShot(600, self.accept)
        elif status == "error":
            self.poll_timer.stop()
            err = prog.get("error", "Download failed.")
            self.status_lbl.setText(f"✕ Error: {err}")
            self.status_lbl.setStyleSheet("font-size: 11px; color: #ef4444;")
            self.btn_primary.setEnabled(True)
            self.btn_primary.setText("Retry Download")
            self.btn_bg.setVisible(False)

    def _on_background_clicked(self):
        self.download_in_background = True
        self.poll_timer.stop()
        self.reject()  # Dismiss modal without cancelling worker

    def _on_cancel_clicked(self):
        if self.is_downloading:
            ModelManager.cancel_model_download(self.manifest_key)
        self.poll_timer.stop()
        self.reject()
