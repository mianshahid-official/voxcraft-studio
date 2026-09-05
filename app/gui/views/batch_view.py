"""
TTS Studio - PySide6 Batch Multi-File Generation View
"""
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QTableWidget, QTableWidgetItem, QFileDialog, QHeaderView,
    QProgressBar, QMessageBox
)
from PySide6.QtCore import Qt, QTimer

from ..widgets.cards import GlassCard
from ...services.batch_service import BATCH_SERVICE


class BatchView(QWidget):
    """Batch multi-file text-to-speech processing queue."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self._init_ui()

    def _init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(16)

        card = GlassCard()
        c_lay = QVBoxLayout(card)
        c_lay.setContentsMargins(18, 16, 18, 16)
        c_lay.setSpacing(12)

        header = QHBoxLayout()
        lbl = QLabel("Batch Text Generation Queue")
        lbl.setStyleSheet("font-size: 15px; font-weight: 700; color: #ffffff;")
        header.addWidget(lbl)
        header.addStretch()

        btn_add = QPushButton("➕ Add Text Files")
        btn_add.setProperty("class", "SecondaryBtn")
        btn_add.clicked.connect(self._add_files)
        header.addWidget(btn_add)

        self.btn_start = QPushButton("▶ Start Batch")
        self.btn_start.setProperty("class", "PrimaryBtn")
        self.btn_start.clicked.connect(self._start_batch)
        header.addWidget(self.btn_start)

        self.btn_clear = QPushButton("Clear")
        self.btn_clear.setProperty("class", "SecondaryBtn")
        self.btn_clear.clicked.connect(self._clear_queue)
        header.addWidget(self.btn_clear)

        c_lay.addLayout(header)

        # Table
        self.table = QTableWidget()
        self.table.setColumnCount(5)
        self.table.setHorizontalHeaderLabels(["Filename", "Engine", "Voice", "Status", "Duration"])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.table.setStyleSheet("""
            QTableWidget {
                background: rgba(11, 14, 23, 0.7);
                border: 1px solid rgba(255, 255, 255, 0.08);
                border-radius: 8px;
            }
            QHeaderView::section {
                background: #111625;
                color: #94a3b8;
                font-weight: 600;
                padding: 6px;
                border: none;
            }
        """)
        c_lay.addWidget(self.table, stretch=1)

        # Summary Bar
        self.summary_label = QLabel("0 Total • 0 Completed • 0 Processing • 0 Waiting")
        self.summary_label.setStyleSheet("color: #94a3b8; font-size: 12px; font-family: 'Consolas';")
        c_lay.addWidget(self.summary_label)

        layout.addWidget(card)

        self.timer = QTimer(self)
        self.timer.timeout.connect(self._refresh_table)

    def _add_files(self):
        files, _ = QFileDialog.getOpenFileNames(self, "Select Text Files for Batch", "", "Text Files (*.txt *.md)")
        if files:
            BATCH_SERVICE.add_files(files, engine="kokoro", voice="af_bella")
            self._refresh_table()

    def _start_batch(self):
        summary = BATCH_SERVICE.get_summary()
        if summary["total"] == 0:
            QMessageBox.warning(self, "Empty Queue", "Please add text files first.")
            return

        self.btn_start.setEnabled(False)
        self.btn_start.setText("⏳ Processing Queue...")
        self.timer.start(1000)
        BATCH_SERVICE.start_processing()

    def _clear_queue(self):
        BATCH_SERVICE.clear()
        self._refresh_table()

    def _refresh_table(self):
        summary = BATCH_SERVICE.get_summary()
        jobs = summary["jobs"]

        self.table.setRowCount(len(jobs))
        for r, j in enumerate(jobs):
            self.table.setItem(r, 0, QTableWidgetItem(j["input_file"]))
            self.table.setItem(r, 1, QTableWidgetItem(j["engine"].upper()))
            self.table.setItem(r, 2, QTableWidgetItem(j["voice"]))
            
            st_item = QTableWidgetItem(j["status"].capitalize())
            if j["status"] == "completed":
                st_item.setForeground(Qt.green)
            elif j["status"] == "failed":
                st_item.setForeground(Qt.red)
            elif j["status"] == "processing":
                st_item.setForeground(Qt.yellow)
            self.table.setItem(r, 3, st_item)

            dur_str = f"{j['duration_sec']:.1f}s" if j["duration_sec"] > 0 else "-"
            self.table.setItem(r, 4, QTableWidgetItem(dur_str))

        self.summary_label.setText(
            f"{summary['total']} Total • {summary['completed']} Completed • "
            f"{summary['processing']} Processing • {summary['waiting']} Waiting • {summary['failed']} Failed"
        )

        if not summary["is_running"] and summary["total"] > 0 and summary["waiting"] == 0:
            self.btn_start.setEnabled(True)
            self.btn_start.setText("▶ Start Batch")
            self.timer.stop()
