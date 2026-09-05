"""
TTS Studio - PySide6 Custom Labeled Slider
"""
from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QSlider
from PySide6.QtCore import Qt, Signal


class LabeledSlider(QWidget):
    """Custom slider with title, live value readout, and decimal step conversion."""

    valueChanged = Signal(float)

    def __init__(self, title: str, min_val: float, max_val: float, default_val: float, step: float = 0.1, unit: str = "", parent=None):
        super().__init__(parent)
        self.min_val = min_val
        self.max_val = max_val
        self.step = step
        self.unit = unit

        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setStyleSheet("background: transparent;")

        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(0, 4, 0, 4)
        self.layout.setSpacing(4)

        # Header: Title + Value
        header = QHBoxLayout()
        self.title_label = QLabel(title)
        self.title_label.setStyleSheet("color: #cbd5e1; font-weight: 500; font-size: 12px; background: transparent;")
        
        self.val_label = QLabel()
        self.val_label.setStyleSheet("color: #8b5cf6; font-weight: 700; font-family: 'Consolas', monospace; font-size: 12px; background: rgba(139, 92, 246, 0.12); padding: 2px 6px; border-radius: 4px;")

        header.addWidget(self.title_label)
        header.addStretch()
        header.addWidget(self.val_label)
        self.layout.addLayout(header)

        # Slider
        self.slider = QSlider(Qt.Horizontal)
        self.num_steps = int(round((max_val - min_val) / step))
        self.slider.setRange(0, self.num_steps)
        
        initial_int = int(round((default_val - min_val) / step))
        self.slider.setValue(initial_int)
        self.layout.addWidget(self.slider)

        self.slider.valueChanged.connect(self._on_slider_changed)
        self._update_display(default_val)

    def _on_slider_changed(self, int_val: int):
        float_val = self.min_val + (int_val * self.step)
        self._update_display(float_val)
        self.valueChanged.emit(float_val)

    def _update_display(self, float_val: float):
        if self.step < 0.1:
            val_str = f"{float_val:.2f}"
        elif self.step < 1:
            val_str = f"{float_val:.1f}"
        else:
            val_str = f"{int(float_val)}"

        if self.unit == "st" and float_val > 0:
            val_str = f"+{val_str}"

        self.val_label.setText(f"{val_str}{self.unit}")

    def value(self) -> float:
        return self.min_val + (self.slider.value() * self.step)

    def setValue(self, val: float):
        int_val = int(round((val - self.min_val) / self.step))
        self.slider.setValue(int_val)
