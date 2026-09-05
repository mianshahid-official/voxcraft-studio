"""
TTS Studio - PySide6 Interactive Waveform Audio Player Widget
"""
import os
import random
from pathlib import Path
from typing import Optional, List

from PySide6.QtWidgets import (
    QWidget, QHBoxLayout, QVBoxLayout, QPushButton, QLabel,
    QSlider, QComboBox, QFileDialog, QFrame, QStyle
)
from PySide6.QtCore import Qt, QUrl, QTimer, Signal
from PySide6.QtGui import QPainter, QColor, QLinearGradient, QPen, QBrush
from PySide6.QtMultimedia import QMediaPlayer, QAudioOutput


class WaveformVisualizer(QWidget):
    """Custom interactive waveform visualizer painted via QPainter."""

    seekRequested = Signal(float)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedHeight(48)
        self.setCursor(Qt.PointingHandCursor)
        self.peaks: List[float] = [random.uniform(0.2, 0.9) for _ in range(120)]
        self.progress = 0.0

    def set_progress(self, pct: float):
        self.progress = max(0.0, min(1.0, pct))
        self.update()

    def set_peaks(self, num_bars: int = 120):
        self.peaks = [max(0.15, min(0.95, random.uniform(0.2, 0.85))) for _ in range(num_bars)]
        self.update()

    def mousePressEvent(self, event):
        pct = event.position().x() / max(1, self.width())
        self.seekRequested.emit(max(0.0, min(1.0, pct)))

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)

        w = self.width()
        h = self.height()

        num_bars = len(self.peaks)
        bar_w = max(2.0, (w / num_bars) * 0.65)
        step = w / num_bars

        for idx, peak in enumerate(self.peaks):
            x = idx * step
            bar_h = peak * (h * 0.75)
            y = (h - bar_h) / 2

            is_played = (idx / num_bars) <= self.progress

            if is_played:
                grad = QLinearGradient(x, y, x, y + bar_h)
                grad.setColorAt(0.0, QColor("#8b5cf6"))
                grad.setColorAt(1.0, QColor("#06b6d4"))
                painter.setBrush(QBrush(grad))
                painter.setPen(Qt.NoPen)
            else:
                painter.setBrush(QColor(255, 255, 255, 30))
                painter.setPen(Qt.NoPen)

            painter.drawRoundedRect(x, y, bar_w, bar_h, 2, 2)

        # Draw playhead cursor
        if self.progress > 0:
            cx = self.progress * w
            painter.setPen(QPen(QColor("#06b6d4"), 2))
            painter.drawLine(int(cx), 0, int(cx), h)


class AudioPlayerWidget(QFrame):
    """Full-featured Studio Audio Player bar with waveform and playback controls."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedHeight(84)
        self.setStyleSheet("""
            QFrame {
                background-color: #07090e;
                border-top: 1px solid rgba(255, 255, 255, 0.08);
            }
        """)

        self.player = QMediaPlayer(self)
        self.audio_output = QAudioOutput(self)
        self.player.setAudioOutput(self.audio_output)

        self.current_file: Optional[str] = None
        self.duration_ms = 0

        self._init_ui()
        self._init_signals()

    def _init_ui(self):
        layout = QHBoxLayout(self)
        layout.setContentsMargins(20, 8, 20, 8)
        layout.setSpacing(16)

        # 1. Left: Play button & Track Title
        left_widget = QWidget()
        left_widget.setFixedWidth(240)
        left_widget.setStyleSheet("background: transparent; border: none;")
        left_layout = QHBoxLayout(left_widget)
        left_layout.setContentsMargins(0, 0, 0, 0)
        left_layout.setSpacing(12)

        self.play_btn = QPushButton("▶")
        self.play_btn.setFixedSize(42, 42)
        self.play_btn.setStyleSheet("""
            QPushButton {
                background-color: #8b5cf6;
                color: #ffffff;
                font-size: 16px;
                font-weight: bold;
                border-radius: 21px;
                border: none;
            }
            QPushButton:hover {
                background-color: #7c3aed;
            }
        """)
        left_layout.addWidget(self.play_btn)

        meta_layout = QVBoxLayout()
        meta_layout.setSpacing(2)
        self.title_label = QLabel("No Audio Loaded")
        self.title_label.setStyleSheet("color: #ffffff; font-weight: 700; font-size: 13px; border: none; background: transparent;")
        self.sub_label = QLabel("Synthesize speech to play")
        self.sub_label.setStyleSheet("color: #94a3b8; font-size: 11px; border: none; background: transparent;")
        meta_layout.addWidget(self.title_label)
        meta_layout.addWidget(self.sub_label)
        left_layout.addLayout(meta_layout)
        layout.addWidget(left_widget)

        # 2. Middle: Waveform Canvas & Time Label
        mid_layout = QVBoxLayout()
        mid_layout.setSpacing(2)
        self.waveform = WaveformVisualizer()
        mid_layout.addWidget(self.waveform)

        time_row = QHBoxLayout()
        self.time_label = QLabel("0:00 / 0:00")
        self.time_label.setStyleSheet("color: #94a3b8; font-family: 'Consolas'; font-size: 11px; border: none; background: transparent;")
        time_row.addWidget(self.time_label)
        time_row.addStretch()
        time_row.addWidget(QLabel("Click waveform to scrub"))
        mid_layout.addLayout(time_row)
        layout.addLayout(mid_layout, stretch=1)

        # 3. Right: Rate, Volume & Export
        right_layout = QHBoxLayout()
        right_layout.setSpacing(10)

        self.rate_combo = QComboBox()
        self.rate_combo.addItems(["0.75x", "1.00x", "1.25x", "1.50x", "2.00x"])
        self.rate_combo.setCurrentIndex(1)
        self.rate_combo.setFixedWidth(75)
        right_layout.addWidget(self.rate_combo)

        # Volume
        vol_label = QLabel("🔊")
        # Volume
        vol_label = QLabel("🔊")
        vol_label.setStyleSheet("border: none; background: transparent;")
        right_layout.addWidget(vol_label)
        self.vol_slider = QSlider(Qt.Horizontal)
        self.vol_slider.setRange(0, 100)
        self.vol_slider.setValue(100)
        self.vol_slider.setFixedWidth(80)
        right_layout.addWidget(self.vol_slider)

        # Initialize audio output volume
        self.audio_output.setVolume(1.0)

        # Save As / Export Button
        self.export_btn = QPushButton("💾 Export")
        self.export_btn.setProperty("class", "SecondaryBtn")
        self.export_btn.setFixedHeight(34)
        right_layout.addWidget(self.export_btn)

        layout.addLayout(right_layout)

    def _init_signals(self):
        self.play_btn.clicked.connect(self.toggle_play)
        self.waveform.seekRequested.connect(self.seek_to_pct)
        self.rate_combo.currentIndexChanged.connect(self._on_rate_changed)
        self.vol_slider.valueChanged.connect(lambda v: self.audio_output.setVolume(v / 100.0))
        self.export_btn.clicked.connect(self._on_export_clicked)

        self.player.positionChanged.connect(self._on_position_changed)
        self.player.durationChanged.connect(self._on_duration_changed)
        self.player.playbackStateChanged.connect(self._on_state_changed)
        self.player.mediaStatusChanged.connect(self._on_media_status_changed)
        self.player.errorOccurred.connect(self._on_player_error)

    def load_audio(self, filepath: str, title: str = "Synthesized Voice", subtitle: str = "Ready for playback"):
        self.current_file = filepath
        self.title_label.setText(title)
        self.sub_label.setText(subtitle)
        self.waveform.set_peaks()
        self.waveform.set_progress(0.0)

        url = QUrl.fromLocalFile(os.path.abspath(filepath))
        self.player.setSource(url)
        self.audio_output.setVolume(self.vol_slider.value() / 100.0)
        self.player.setPosition(0)
        self.player.play()

    def toggle_play(self):
        if not self.current_file or not os.path.exists(self.current_file):
            return

        # If audio is at the end or stopped, rewind to start
        if self.duration_ms > 0 and (self.player.position() >= self.duration_ms - 200 or self.player.playbackState() == QMediaPlayer.StoppedState):
            self.player.setPosition(0)
            self.waveform.set_progress(0.0)

        if self.player.playbackState() == QMediaPlayer.PlayingState:
            self.player.pause()
        else:
            self.audio_output.setVolume(self.vol_slider.value() / 100.0)
            self.player.play()

    def seek_to_pct(self, pct: float):
        if self.duration_ms > 0:
            target_pos = int(pct * self.duration_ms)
            self.player.setPosition(target_pos)
            self.waveform.set_progress(pct)
            cur = self.format_time(target_pos // 1000)
            dur = self.format_time(self.duration_ms // 1000)
            self.time_label.setText(f"{cur} / {dur}")

    def _on_rate_changed(self, idx: int):
        rates = [0.75, 1.0, 1.25, 1.5, 2.0]
        self.player.setPlaybackRate(rates[idx])

    def _on_position_changed(self, pos_ms: int):
        if self.duration_ms > 0:
            pct = pos_ms / max(1, self.duration_ms)
            self.waveform.set_progress(pct)
            cur = self.format_time(pos_ms // 1000)
            dur = self.format_time(self.duration_ms // 1000)
            self.time_label.setText(f"{cur} / {dur}")

    def _on_duration_changed(self, dur_ms: int):
        self.duration_ms = dur_ms
        dur = self.format_time(dur_ms // 1000)
        self.time_label.setText(f"0:00 / {dur}")

    def _on_state_changed(self, state):
        if state == QMediaPlayer.PlayingState:
            self.play_btn.setText("⏸")
        else:
            self.play_btn.setText("▶")

    def _on_media_status_changed(self, status):
        if status == QMediaPlayer.EndOfMedia:
            self.play_btn.setText("▶")
            self.player.setPosition(0)
            self.waveform.set_progress(0.0)
            dur = self.format_time(self.duration_ms // 1000)
            self.time_label.setText(f"0:00 / {dur}")

    def _on_player_error(self, error, error_string=""):
        # Fallback to Windows native playback if DirectShow/QtMultimedia fails
        if sys.platform == "win32" and self.current_file and os.path.exists(self.current_file):
            try:
                import winsound
                winsound.PlaySound(self.current_file, winsound.SND_FILENAME | winsound.SND_ASYNC)
            except Exception:
                pass

    def _on_export_clicked(self):
        if not self.current_file or not os.path.exists(self.current_file):
            return
        dest, _ = QFileDialog.getSaveFileName(self, "Save Audio File", "", "WAV Audio (*.wav);;MP3 Audio (*.mp3);;FLAC Audio (*.flac)")
        if dest:
            import shutil
            shutil.copy2(self.current_file, dest)

    @staticmethod
    def format_time(sec: int) -> str:
        m = sec // 60
        s = sec % 60
        return f"{m}:{s:02d}"
