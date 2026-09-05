"""
TTS Studio - PySide6 Live Resource Monitor Widget
"""
from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QProgressBar, QFrame
from PySide6.QtCore import Qt, QTimer

from ...core.hardware import HardwareManager


class ResourceMonitorWidget(QFrame):
    """Real-time CPU, RAM, and GPU utilization HUD."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setStyleSheet("""
            QFrame {
                background-color: rgba(0, 0, 0, 0.4);
                border: 1px solid rgba(255, 255, 255, 0.05);
                border-radius: 8px;
            }
            QLabel {
                font-size: 11px;
                color: #94a3b8;
                background: transparent;
                border: none;
            }
            QProgressBar {
                background-color: rgba(255, 255, 255, 0.08);
                border-radius: 3px;
                height: 5px;
                border: none;
            }
            QProgressBar::chunk {
                background-color: #8b5cf6;
                border-radius: 3px;
            }
        """)

        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(10, 8, 10, 8)
        self.layout.setSpacing(6)

        # CPU Row
        cpu_row = QHBoxLayout()
        cpu_row.addWidget(QLabel("CPU"))
        self.cpu_label = QLabel("0%")
        self.cpu_label.setStyleSheet("color: #f8fafc; font-family: 'Consolas'; font-weight: 600;")
        cpu_row.addStretch()
        cpu_row.addWidget(self.cpu_label)
        self.layout.addLayout(cpu_row)

        self.cpu_bar = QProgressBar()
        self.cpu_bar.setRange(0, 100)
        self.layout.addWidget(self.cpu_bar)

        # RAM Row
        ram_row = QHBoxLayout()
        ram_row.addWidget(QLabel("RAM"))
        self.ram_label = QLabel("0 / 0 GB")
        self.ram_label.setStyleSheet("color: #f8fafc; font-family: 'Consolas'; font-weight: 600;")
        ram_row.addStretch()
        ram_row.addWidget(self.ram_label)
        self.layout.addLayout(ram_row)

        self.ram_bar = QProgressBar()
        self.ram_bar.setRange(0, 100)
        self.layout.addWidget(self.ram_bar)

        # Timer for polling
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_metrics)
        self.timer.start(2000)
        self.update_metrics()

    def update_metrics(self):
        metrics = HardwareManager.get_live_metrics()
        cpu_p = int(metrics["cpu_percent"])
        self.cpu_bar.setValue(cpu_p)
        self.cpu_label.setText(f"{cpu_p}%")

        ram_p = int(metrics["ram_percent"])
        self.ram_bar.setValue(ram_p)
        self.ram_label.setText(f"{metrics['ram_used_gb']}/{metrics['ram_total_gb']}G")
