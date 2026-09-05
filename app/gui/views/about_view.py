"""
VoxCraft Studio - PySide6 About & Licenses View
"""
from pathlib import Path
from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QTextEdit, QFrame
from PySide6.QtCore import Qt
from PySide6.QtGui import QPixmap
from ..widgets.cards import GlassCard


class AboutView(QWidget):
    """About page with version, Shahid developer credits, and open-source licenses."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self._init_ui()

    def _init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 24, 24, 24)
        layout.setSpacing(16)

        card = GlassCard()
        c_lay = QVBoxLayout(card)
        c_lay.setContentsMargins(28, 28, 28, 28)
        c_lay.setSpacing(16)

        # Header with Logo
        head_row = QHBoxLayout()
        head_row.setSpacing(16)

        icon_path = Path(__file__).resolve().parent.parent.parent / "resources" / "icons" / "app_icon.png"
        if icon_path.exists():
            logo_img = QLabel()
            pix = QPixmap(str(icon_path)).scaled(64, 64, Qt.KeepAspectRatio, Qt.SmoothTransformation)
            logo_img.setPixmap(pix)
            logo_img.setStyleSheet("background: transparent; border: none;")
            head_row.addWidget(logo_img)

        title_box = QVBoxLayout()
        title_box.setSpacing(2)
        lbl_title = QLabel("VoxCraft Studio")
        lbl_title.setStyleSheet("font-size: 22px; font-weight: 800; color: #ffffff; background: transparent; border: none;")
        lbl_sub = QLabel("Production Desktop Offline Speech Synthesis & Podcast Studio • Version 1.0.0")
        lbl_sub.setStyleSheet("color: #06b6d4; font-weight: 600; font-size: 13px; background: transparent; border: none;")
        title_box.addWidget(lbl_title)
        title_box.addWidget(lbl_sub)
        head_row.addLayout(title_box)
        head_row.addStretch()
        c_lay.addLayout(head_row)

        # Developer Credit Card
        dev_card = QFrame()
        dev_card.setStyleSheet("background-color: rgba(139, 92, 246, 0.12); border: 1px solid rgba(139, 92, 246, 0.35); border-radius: 10px; padding: 12px;")
        d_lay = QHBoxLayout(dev_card)
        d_lay.setContentsMargins(14, 10, 14, 10)
        d_lay.setSpacing(12)

        lbl_spark = QLabel("✨")
        lbl_spark.setStyleSheet("font-size: 20px; background: transparent; border: none;")
        d_lay.addWidget(lbl_spark)

        dev_text = QVBoxLayout()
        dev_text.setSpacing(1)
        lbl_dev_by = QLabel("DEVELOPED & ARCHITECTED BY")
        lbl_dev_by.setStyleSheet("font-size: 10px; font-weight: 800; color: #a78bfa; letter-spacing: 0.5px; background: transparent; border: none;")
        lbl_dev_name = QLabel("Shahid")
        lbl_dev_name.setStyleSheet("font-size: 15px; font-weight: 800; color: #ffffff; background: transparent; border: none;")
        dev_text.addWidget(lbl_dev_by)
        dev_text.addWidget(lbl_dev_name)
        d_lay.addLayout(dev_text)
        d_lay.addStretch()
        c_lay.addWidget(dev_card)

        # Technical Info
        info = (
            "VoxCraft Studio is designed for 100% private, local, offline artificial intelligence speech generation.\n\n"
            "Integrated Neural Engines & Models:\n"
            "• Kokoro-82M (Apache 2.0 / High-Quality ONNX 24kHz Speech)\n"
            "• Piper Neural TTS (MIT License / Ultra-Fast Multi-Lingual CPU Engine)\n"
            "• F5-TTS Flow Matching Diffusion (MIT License / Zero-Shot Voice Cloning)\n\n"
            "Built with PySide6 (Qt for Python), ONNX Runtime, and PyAudio/DSP audio pipelines."
        )
        lbl_info = QLabel(info)
        lbl_info.setStyleSheet("color: #cbd5e1; font-size: 13px; line-height: 1.6; background: transparent; border: none;")
        c_lay.addWidget(lbl_info)

        c_lay.addStretch()
        layout.addWidget(card)
