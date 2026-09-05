"""
TTS Studio - PySide6 Hardware & Diagnostics View
"""
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QGridLayout
)
from ..widgets.cards import GlassCard, StatusBadge
from ...core.hardware import HardwareManager


class HardwareView(QWidget):
    """Hardware capabilities and diagnostics report view."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self._init_ui()

    def _init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(16)

        card = GlassCard()
        c_lay = QVBoxLayout(card)
        c_lay.setContentsMargins(20, 20, 20, 20)
        c_lay.setSpacing(16)

        lbl_title = QLabel("🖥️ System Hardware & Device Acceleration Diagnostics")
        lbl_title.setStyleSheet("font-size: 16px; font-weight: 700; color: #ffffff;")
        c_lay.addWidget(lbl_title)

        report = HardwareManager.get_hardware_report()

        grid = QGridLayout()
        grid.setSpacing(14)

        items = [
            ("Operating System", report.os_name),
            ("Central Processor (CPU)", f"{report.cpu_name} ({report.cpu_physical_cores} Cores / {report.cpu_logical_threads} Threads)"),
            ("System Memory (RAM)", f"{report.ram_available_gb} GB Free / {report.ram_total_gb} GB Total"),
            ("Free Disk Storage", f"{report.disk_free_gb} GB Available"),
            ("GPU Acceleration", report.details),
            ("Active Routing Policy", "GPU First with Automatic CPU Fallback")
        ]

        for idx, (k, v) in enumerate(items):
            k_lbl = QLabel(f"<b>{k}:</b>")
            k_lbl.setStyleSheet("color: #94a3b8; font-size: 13px;")
            v_lbl = QLabel(v)
            v_lbl.setStyleSheet("color: #f8fafc; font-size: 13px; font-family: 'Consolas';")
            grid.addWidget(k_lbl, idx, 0)
            grid.addWidget(v_lbl, idx, 1)

        c_lay.addLayout(grid)
        c_lay.addStretch()

        layout.addWidget(card)
