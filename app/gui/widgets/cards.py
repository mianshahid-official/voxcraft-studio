"""
TTS Studio - PySide6 Custom Card & Badge Widgets
"""
from PySide6.QtWidgets import QFrame, QLabel, QHBoxLayout, QVBoxLayout, QWidget
from PySide6.QtCore import Qt


class GlassCard(QFrame):
    """Modern translucent glass container card."""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setProperty("class", "GlassCard")
        self.setObjectName("GlassCard")


class StatusBadge(QFrame):
    """Badge pill for engine, status, and device indicators."""
    def __init__(self, text: str, badge_type: str = "default", parent=None):
        super().__init__(parent)
        self.layout = QHBoxLayout(self)
        self.layout.setContentsMargins(8, 3, 8, 3)
        self.layout.setSpacing(4)

        colors = {
            "gpu": ("rgba(139, 92, 246, 0.2)", "#c4b5fd", "rgba(139, 92, 246, 0.4)"),
            "success": ("rgba(16, 185, 129, 0.2)", "#6ee7b7", "rgba(16, 185, 129, 0.4)"),
            "warning": ("rgba(245, 158, 11, 0.2)", "#fcd34d", "rgba(245, 158, 11, 0.4)"),
            "error": ("rgba(244, 63, 94, 0.2)", "#fda4af", "rgba(244, 63, 94, 0.4)"),
            "default": ("rgba(255, 255, 255, 0.08)", "#94a3b8", "rgba(255, 255, 255, 0.12)")
        }
        bg, fg, border = colors.get(badge_type, colors["default"])

        self.setStyleSheet(f"""
            QFrame {{
                background-color: {bg};
                border: 1px solid {border};
                border-radius: 12px;
            }}
            QLabel {{
                color: {fg};
                font-size: 11px;
                font-weight: 600;
                background: transparent;
                border: none;
            }}
        """)

        self.label = QLabel(text)
        self.layout.addWidget(self.label)

    def setText(self, text: str):
        self.label.setText(text)
