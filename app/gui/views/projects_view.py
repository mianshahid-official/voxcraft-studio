"""
TTS Studio - PySide6 Projects Manager View
"""
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QTableWidget, QTableWidgetItem, QHeaderView, QInputDialog, QMessageBox
)
from PySide6.QtCore import Qt

from ..widgets.cards import GlassCard
from ...core.project import ProjectManager


class ProjectsView(QWidget):
    """Project manager and draft history view."""

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
        lbl = QLabel("Saved Projects & Audio Drafts")
        lbl.setStyleSheet("font-size: 15px; font-weight: 700; color: #ffffff;")
        header.addWidget(lbl)
        header.addStretch()

        btn_new = QPushButton("➕ New Project")
        btn_new.setProperty("class", "PrimaryBtn")
        btn_new.clicked.connect(self._create_project)
        header.addWidget(btn_new)
        c_lay.addLayout(header)

        self.table = QTableWidget()
        self.table.setColumnCount(4)
        self.table.setHorizontalHeaderLabels(["Project Name", "Engine", "Word Count", "Type"])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        c_lay.addWidget(self.table, stretch=1)

        layout.addWidget(card)
        self.refresh_projects()

    def refresh_projects(self):
        projects = ProjectManager.get_all_projects()
        self.table.setRowCount(len(projects))
        for r, p in enumerate(projects):
            self.table.setItem(r, 0, QTableWidgetItem(p.get("name", "Untitled")))
            self.table.setItem(r, 1, QTableWidgetItem(p.get("engine", "kokoro").upper()))
            self.table.setItem(r, 2, QTableWidgetItem(str(p.get("word_count", 0))))
            self.table.setItem(r, 3, QTableWidgetItem(p.get("project_type", "tts").upper()))

    def _create_project(self):
        name, ok = QInputDialog.getText(self, "New Project", "Enter project name:")
        if ok and name.strip():
            ProjectManager.create_project(name.strip())
            self.refresh_projects()
