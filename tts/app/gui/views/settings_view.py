"""
TTS Studio - PySide6 Settings & Hardware Diagnostics View
Combines application configuration, offline engine parameters, storage/cache management,
and system hardware & device acceleration diagnostics in a unified interface.
"""
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QComboBox,
    QCheckBox, QPushButton, QMessageBox, QGridLayout, QScrollArea,
    QFrame
)
from PySide6.QtCore import Qt
from ..widgets.cards import GlassCard, StatusBadge
from ...config.settings import APP_CONFIG
from ...services.storage_service import StorageService
from ...core.hardware import HardwareManager


class SettingsView(QWidget):
    """Unified application preferences, storage manager, and hardware diagnostics."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self._init_ui()

    def _init_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(16)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.NoFrame)
        scroll.setStyleSheet("background: transparent;")

        container = QWidget()
        container.setStyleSheet("background: transparent;")
        c_lay = QVBoxLayout(container)
        c_lay.setContentsMargins(0, 0, 10, 0)
        c_lay.setSpacing(16)

        # -------------------------------------------------------------
        # Section 1: Studio Preferences
        # -------------------------------------------------------------
        pref_card = GlassCard()
        pref_layout = QVBoxLayout(pref_card)
        pref_layout.setContentsMargins(20, 20, 20, 20)
        pref_layout.setSpacing(16)

        lbl_pref = QLabel("⚙️ Application Settings & Preferences")
        lbl_pref.setStyleSheet("font-size: 16px; font-weight: 700; color: #ffffff; background: transparent;")
        pref_layout.addWidget(lbl_pref)

        grid = QGridLayout()
        grid.setSpacing(14)

        # Performance Mode
        lbl_p = QLabel("Performance Mode:")
        lbl_p.setStyleSheet("color: #94a3b8; font-weight: 600; background: transparent;")
        grid.addWidget(lbl_p, 0, 0)
        self.perf_combo = QComboBox()
        self.perf_combo.addItems(["Maximum Quality", "Balanced", "Fast"])
        self.perf_combo.setCurrentText(APP_CONFIG.generation.performance_mode)
        grid.addWidget(self.perf_combo, 0, 1)

        # GPU Acceleration Preference
        lbl_g = QLabel("Acceleration Preference:")
        lbl_g.setStyleSheet("color: #94a3b8; font-weight: 600; background: transparent;")
        grid.addWidget(lbl_g, 1, 0)
        self.gpu_combo = QComboBox()
        self.gpu_combo.addItems(["Auto (GPU Priority with CPU Fallback)", "Force CPU Only"])
        grid.addWidget(self.gpu_combo, 1, 1)

        # Output Format
        lbl_f = QLabel("Default Audio Format:")
        lbl_f.setStyleSheet("color: #94a3b8; font-weight: 600; background: transparent;")
        grid.addWidget(lbl_f, 2, 0)
        self.fmt_combo = QComboBox()
        self.fmt_combo.addItems(["WAV (Lossless 16-bit PCM)", "MP3 (320kbps High-Bitrate)", "FLAC (Lossless Compressed)"])
        grid.addWidget(self.fmt_combo, 2, 1)

        # Offline Mode Checkbox
        self.offline_check = QCheckBox("Strict Offline Mode (Block all remote network requests)")
        self.offline_check.setChecked(APP_CONFIG.offline_mode)
        grid.addWidget(self.offline_check, 3, 0, 1, 2)

        pref_layout.addLayout(grid)

        # Storage & Cache Management
        lbl_storage_title = QLabel("Disk Footprint & Local Cache")
        lbl_storage_title.setStyleSheet("font-size: 14px; font-weight: 700; color: #cbd5e1; background: transparent; margin-top: 8px;")
        pref_layout.addWidget(lbl_storage_title)

        breakdown = StorageService.get_storage_breakdown()
        self.lbl_footprint = QLabel(f"Models: {breakdown['models_gb']} GB • Projects: {breakdown['projects_gb']} GB • Cache: {breakdown['cache_mb']} MB")
        self.lbl_footprint.setStyleSheet("color: #94a3b8; font-family: 'Consolas'; background: transparent;")
        pref_layout.addWidget(self.lbl_footprint)

        btn_row = QHBoxLayout()
        btn_clear_cache = QPushButton("🗑️ Clear Audio Cache")
        btn_clear_cache.setProperty("class", "SecondaryBtn")
        btn_clear_cache.clicked.connect(self._clear_cache)
        btn_row.addWidget(btn_clear_cache)

        btn_save = QPushButton("💾 Save Preferences")
        btn_save.setProperty("class", "PrimaryBtn")
        btn_save.setFixedHeight(38)
        btn_save.clicked.connect(self._save)
        btn_row.addWidget(btn_save)
        btn_row.addStretch()

        pref_layout.addLayout(btn_row)
        c_lay.addWidget(pref_card)

        # -------------------------------------------------------------
        # Section 2: Hardware & GPU Diagnostics (Merged)
        # -------------------------------------------------------------
        hw_card = GlassCard()
        hw_layout = QVBoxLayout(hw_card)
        hw_layout.setContentsMargins(20, 20, 20, 20)
        hw_layout.setSpacing(16)

        hw_header = QHBoxLayout()
        lbl_hw = QLabel("🖥️ System Hardware & Device Acceleration Diagnostics")
        lbl_hw.setStyleSheet("font-size: 16px; font-weight: 700; color: #ffffff; background: transparent;")
        hw_header.addWidget(lbl_hw)
        hw_header.addStretch()

        report = HardwareManager.get_hardware_report()
        badge_text = "CUDA GPU" if report.cuda_available else ("DirectML GPU" if report.directml_available else "CPU Multi-Core")
        badge_type = "gpu" if (report.cuda_available or report.directml_available) else "default"
        hw_header.addWidget(StatusBadge(badge_text, badge_type))
        hw_layout.addLayout(hw_header)

        hw_grid = QGridLayout()
        hw_grid.setSpacing(14)

        items = [
            ("Operating System", report.os_name),
            ("Central Processor (CPU)", f"{report.cpu_name} ({report.cpu_physical_cores} Cores / {report.cpu_logical_threads} Threads)"),
            ("System Memory (RAM)", f"{report.ram_available_gb} GB Free / {report.ram_total_gb} GB Total"),
            ("Free Disk Storage", f"{report.disk_free_gb} GB Available"),
            ("Hardware Acceleration", report.details),
            ("Active Routing Policy", "GPU First with Automatic Multi-Core CPU Fallback")
        ]

        for idx, (k, v) in enumerate(items):
            k_lbl = QLabel(f"{k}:")
            k_lbl.setStyleSheet("color: #94a3b8; font-size: 13px; font-weight: 600; background: transparent;")
            v_lbl = QLabel(v)
            v_lbl.setStyleSheet("color: #f8fafc; font-size: 13px; font-family: 'Consolas'; background: transparent;")
            hw_grid.addWidget(k_lbl, idx, 0)
            hw_grid.addWidget(v_lbl, idx, 1)

        hw_layout.addLayout(hw_grid)
        c_lay.addWidget(hw_card)

        # -------------------------------------------------------------
        # Section 3: About VoxCraft Studio & Credits (Merged)
        # -------------------------------------------------------------
        about_card = GlassCard()
        ab_layout = QVBoxLayout(about_card)
        ab_layout.setContentsMargins(20, 20, 20, 20)
        ab_layout.setSpacing(14)

        ab_header = QHBoxLayout()
        ab_header.setSpacing(14)
        lbl_logo = QLabel("🎙️")
        lbl_logo.setStyleSheet("font-size: 28px; background: transparent; border: none;")
        ab_header.addWidget(lbl_logo)

        ab_title_box = QVBoxLayout()
        ab_title_box.setSpacing(1)
        lbl_ab_name = QLabel("VoxCraft Studio v1.0.0")
        lbl_ab_name.setStyleSheet("font-size: 16px; font-weight: 800; color: #ffffff; background: transparent; border: none;")
        lbl_ab_sub = QLabel("100% Offline Neural Speech Synthesis & Production Audio Studio")
        lbl_ab_sub.setStyleSheet("font-size: 11px; color: #06b6d4; font-weight: 600; background: transparent; border: none;")
        ab_title_box.addWidget(lbl_ab_name)
        ab_title_box.addWidget(lbl_ab_sub)
        ab_header.addLayout(ab_title_box, stretch=1)
        ab_layout.addLayout(ab_header)

        dev_box = QFrame()
        dev_box.setStyleSheet("background-color: rgba(139, 92, 246, 0.1); border: 1px solid rgba(139, 92, 246, 0.25); border-radius: 8px; padding: 10px;")
        d_lay = QHBoxLayout(dev_box)
        d_lay.setContentsMargins(10, 8, 10, 8)
        d_lay.setSpacing(10)

        lbl_spark = QLabel("✨")
        lbl_spark.setStyleSheet("font-size: 18px; background: transparent; border: none;")
        d_lay.addWidget(lbl_spark)

        dev_text = QVBoxLayout()
        dev_text.setSpacing(1)
        lbl_dev_by = QLabel("DEVELOPED & ARCHITECTED BY")
        lbl_dev_by.setStyleSheet("font-size: 9px; font-weight: 800; color: #a78bfa; letter-spacing: 0.5px; background: transparent; border: none;")
        lbl_dev_name = QLabel("Shahid")
        lbl_dev_name.setStyleSheet("font-size: 14px; font-weight: 800; color: #ffffff; background: transparent; border: none;")
        dev_text.addWidget(lbl_dev_by)
        dev_text.addWidget(lbl_dev_name)
        d_lay.addLayout(dev_text)
        d_lay.addStretch()
        ab_layout.addWidget(dev_box)

        lbl_engine_info = QLabel(
            "<b>Neural Engines & Offline Stack:</b><br>"
            "• <b>Engine 1 (Kokoro-82M):</b> High-fidelity 24kHz studio speech synthesis with multi-voice blending.<br>"
            "• <b>Engine 2 (Piper Neural):</b> Ultra-fast multi-lingual local speech generation (EN, ES, FR, DE, IT, PT).<br>"
            "• <b>Engine 3 (F5-TTS):</b> Flow-matching diffusion zero-shot voice cloning with reference audio adaptation.<br>"
            "• <b>Framework:</b> PySide6 (Qt for Python), ONNX Runtime, DirectML/CUDA, PyAudio & SoundFile."
        )
        lbl_engine_info.setWordWrap(True)
        lbl_engine_info.setStyleSheet("color: #cbd5e1; font-size: 12px; line-height: 1.5; background: transparent; border: none;")
        ab_layout.addWidget(lbl_engine_info)

        c_lay.addWidget(about_card)

        scroll.setWidget(container)
        main_layout.addWidget(scroll)

    def _clear_cache(self):
        count = StorageService.clear_cache()
        breakdown = StorageService.get_storage_breakdown()
        self.lbl_footprint.setText(f"Models: {breakdown['models_gb']} GB • Projects: {breakdown['projects_gb']} GB • Cache: {breakdown['cache_mb']} MB")
        QMessageBox.information(self, "Cache Cleared", f"Cleared {count} temporary audio cache files.")

    def _save(self):
        APP_CONFIG.generation.performance_mode = self.perf_combo.currentText()
        APP_CONFIG.offline_mode = self.offline_check.isChecked()
        APP_CONFIG.save()
        QMessageBox.information(self, "Settings Saved", "Preferences updated successfully.")
