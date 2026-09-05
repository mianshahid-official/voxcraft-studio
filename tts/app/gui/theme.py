"""
TTS Studio - PySide6 Dark Studio Theme & QSS Stylesheet
Refined ultra-clean dark glassmorphism styling with seamless label blending.
"""

DARK_STUDIO_QSS = """
/* Window & Central Root Background */
QMainWindow, QWidget#CentralWidget, QWidget#MainWindow {
    background-color: #080b12;
}

/* Global Reset */
QWidget {
    color: #f1f5f9;
    font-family: 'Segoe UI', 'Outfit', 'Inter', -apple-system, sans-serif;
    font-size: 13px;
    selection-background-color: #8b5cf6;
    selection-color: #ffffff;
}

/* Ensure Labels & Frames are fully transparent by default */
QLabel {
    background: transparent;
    background-color: transparent;
}

QFrame {
    background: transparent;
}

QGroupBox {
    background: transparent;
    border: 1px solid rgba(255, 255, 255, 0.08);
    border-radius: 8px;
    margin-top: 10px;
    padding-top: 12px;
}

QGroupBox::title {
    subcontrol-origin: margin;
    subcontrol-position: top left;
    padding: 0 6px;
    color: #a78bfa;
    font-weight: 600;
}

/* Sidebar Navigation */
QFrame#Sidebar {
    background-color: #06080e;
    border-right: 1px solid rgba(255, 255, 255, 0.06);
}

QPushButton#NavBtn {
    background-color: transparent;
    color: #94a3b8;
    text-align: left;
    padding: 10px 16px;
    border-radius: 8px;
    font-weight: 600;
    font-size: 13px;
    border: 1px solid transparent;
}

QPushButton#NavBtn:hover {
    background-color: rgba(255, 255, 255, 0.04);
    color: #ffffff;
}

QPushButton#NavBtn:checked {
    background-color: rgba(139, 92, 246, 0.15);
    color: #c4b5fd;
    border: 1px solid rgba(139, 92, 246, 0.35);
}

/* Cards & Glass Panels */
QFrame.GlassCard, QFrame#GlassCard {
    background-color: #0f1523;
    border: 1px solid rgba(255, 255, 255, 0.08);
    border-radius: 12px;
}

QFrame.GlassCard:hover, QFrame#GlassCard:hover {
    border: 1px solid rgba(139, 92, 246, 0.3);
}

/* Metric Diagnostic Tiles */
QFrame.MetricTile {
    background-color: #131b2e;
    border: 1px solid rgba(255, 255, 255, 0.07);
    border-radius: 10px;
}

QFrame.MetricTile:hover {
    background-color: #1a243d;
    border: 1px solid rgba(139, 92, 246, 0.4);
}

/* Model Selectable Cards */
QFrame.ModelSelectCard {
    background-color: #111827;
    border: 1.5px solid rgba(255, 255, 255, 0.08);
    border-radius: 12px;
}

QFrame.ModelSelectCard:hover {
    background-color: #172033;
    border-color: rgba(139, 92, 246, 0.5);
}

QFrame.ModelSelectCardActive {
    background-color: rgba(139, 92, 246, 0.12);
    border: 1.5px solid #8b5cf6;
    border-radius: 12px;
}

/* Wizard Sidebar */
QFrame#WizardSidebar {
    background-color: #05070c;
    border-right: 1px solid rgba(255, 255, 255, 0.07);
}

/* Terminal / Log Box */
QFrame.TerminalLog {
    background-color: #060913;
    border: 1px solid rgba(255, 255, 255, 0.08);
    border-radius: 8px;
    font-family: 'Cascadia Code', 'Consolas', 'Courier New', monospace;
    font-size: 11px;
}

/* Standard Buttons */
QPushButton.PrimaryBtn {
    background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #8b5cf6, stop:1 #7c3aed);
    color: #ffffff;
    font-weight: 700;
    font-size: 13px;
    padding: 10px 22px;
    border-radius: 8px;
    border: none;
}

QPushButton.PrimaryBtn:hover {
    background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #9333ea, stop:1 #6b21a8);
}

QPushButton.PrimaryBtn:disabled {
    background: rgba(255, 255, 255, 0.08);
    color: #64748b;
}

QPushButton.SecondaryBtn {
    background-color: rgba(255, 255, 255, 0.05);
    color: #cbd5e1;
    font-weight: 600;
    padding: 9px 18px;
    border-radius: 8px;
    border: 1px solid rgba(255, 255, 255, 0.12);
}

QPushButton.SecondaryBtn:hover {
    background-color: rgba(255, 255, 255, 0.1);
    color: #ffffff;
    border-color: rgba(255, 255, 255, 0.25);
}

/* Input Fields & TextEdit */
QTextEdit, QPlainTextEdit, QLineEdit {
    background-color: #080b14;
    border: 1px solid rgba(255, 255, 255, 0.12);
    border-radius: 8px;
    padding: 10px;
    color: #f8fafc;
    font-size: 13px;
}

QTextEdit:focus, QPlainTextEdit:focus, QLineEdit:focus {
    border: 1px solid #8b5cf6;
    background-color: #0b0f1b;
}

/* ComboBox */
QComboBox {
    background-color: #141c2c;
    border: 1px solid rgba(255, 255, 255, 0.14);
    border-radius: 8px;
    padding: 8px 12px;
    color: #f8fafc;
    font-weight: 500;
}

QComboBox:focus {
    border: 1px solid #8b5cf6;
}

QComboBox::drop-down {
    border: none;
    padding-right: 10px;
}

QComboBox QAbstractItemView {
    background-color: #0f172a;
    border: 1px solid rgba(255, 255, 255, 0.15);
    border-radius: 8px;
    selection-background-color: #8b5cf6;
    color: #f8fafc;
    padding: 4px;
}

/* Sliders */
QSlider::groove:horizontal {
    height: 6px;
    background: rgba(255, 255, 255, 0.1);
    border-radius: 3px;
}

QSlider::sub-page:horizontal {
    background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #8b5cf6, stop:1 #06b6d4);
    border-radius: 3px;
}

QSlider::handle:horizontal {
    background: #ffffff;
    border: 2px solid #8b5cf6;
    width: 16px;
    height: 16px;
    margin: -5px 0;
    border-radius: 8px;
}

QSlider::handle:horizontal:hover {
    background: #c4b5fd;
}

/* Scrollbars */
QScrollBar:vertical {
    background: transparent;
    width: 6px;
    border-radius: 3px;
}

QScrollBar:handle:vertical {
    background: rgba(255, 255, 255, 0.15);
    border-radius: 3px;
    min-height: 20px;
}

QScrollBar:handle:vertical:hover {
    background: #8b5cf6;
}

QScrollBar:add-line:vertical, QScrollBar:sub-line:vertical {
    height: 0px;
}

/* CheckBox Styling */
QCheckBox {
    color: #f8fafc;
    spacing: 10px;
    font-size: 13px;
    background: transparent;
}

QCheckBox::indicator {
    width: 18px;
    height: 18px;
    border-radius: 5px;
    border: 1.5px solid rgba(255, 255, 255, 0.25);
    background: rgba(15, 23, 42, 0.8);
}

QCheckBox::indicator:hover {
    border-color: #8b5cf6;
    background: rgba(139, 92, 246, 0.1);
}

QCheckBox::indicator:checked {
    background-color: #8b5cf6;
    border-color: #8b5cf6;
    image: none;
}

/* Progress Bar */
QProgressBar {
    background-color: rgba(255, 255, 255, 0.08);
    border: 1px solid rgba(255, 255, 255, 0.06);
    border-radius: 7px;
    height: 14px;
    text-align: center;
    color: #ffffff;
    font-size: 11px;
    font-weight: 700;
}

QProgressBar::chunk {
    background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #8b5cf6, stop:1 #06b6d4);
    border-radius: 6px;
}
"""
