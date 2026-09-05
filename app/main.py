"""
VoxCraft Studio / TTS Studio - Desktop Application Launcher
Starts native PySide6 desktop studio, with fallback to web or setup wizard.
"""
import os
import sys
import argparse
import logging
from pathlib import Path

# Add project root to path
PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

# Configure logging
LOG_FILE = PROJECT_ROOT / "logs" / "app.log"
LOG_FILE.parent.mkdir(parents=True, exist_ok=True)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler(str(LOG_FILE), encoding="utf-8")
    ]
)
logger = logging.getLogger("VoxCraft.Main")


def _setup_app_environment():
    """Configure Windows taskbar AppUserModelID and high DPI attributes."""
    if sys.platform == "win32":
        try:
            import ctypes
            ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID("Shahid.VoxCraftStudio.TTS.1.0")
        except Exception:
            pass


def launch_pyside6_app():
    """Launch native PySide6 Desktop GUI."""
    try:
        from PySide6.QtWidgets import QApplication
        from PySide6.QtCore import Qt
        from PySide6.QtGui import QIcon
        from app.gui.main_window import MainWindow

        _setup_app_environment()
        QApplication.setHighDpiScaleFactorRoundingPolicy(Qt.HighDpiScaleFactorRoundingPolicy.PassThrough)

        app = QApplication(sys.argv)
        app.setApplicationName("VoxCraft Studio")
        app.setOrganizationName("Shahid")

        icon_path = PROJECT_ROOT / "app" / "resources" / "icons" / "app_icon.png"
        if icon_path.exists():
            app.setWindowIcon(QIcon(str(icon_path)))

        window = MainWindow()
        window.show()

        sys.exit(app.exec())
    except Exception as e:
        logger.error(f"PySide6 desktop launch error: {e}", exc_info=True)
        print(f"\n[!] Failed to launch native PySide6 window: {e}")
        print("[*] Falling back to Web Studio mode...")
        launch_web_app()


def launch_setup_wizard():
    """Launch First-Run Setup & Model Downloader Wizard directly."""
    from PySide6.QtWidgets import QApplication
    from PySide6.QtCore import Qt
    from PySide6.QtGui import QIcon
    from app.gui.wizard.setup_wizard import SetupWizardDialog

    _setup_app_environment()
    QApplication.setHighDpiScaleFactorRoundingPolicy(Qt.HighDpiScaleFactorRoundingPolicy.PassThrough)

    app = QApplication(sys.argv)
    app.setApplicationName("VoxCraft Studio Setup")
    app.setOrganizationName("Shahid")

    icon_path = PROJECT_ROOT / "app" / "resources" / "icons" / "app_icon.png"
    if icon_path.exists():
        app.setWindowIcon(QIcon(str(icon_path)))

    wizard = SetupWizardDialog()
    wizard.show()
    sys.exit(app.exec())


def launch_web_app(port: int = 8765):
    """Launch ASGI Web Server + PyWebView / Browser."""
    import webbrowser
    import uvicorn
    from app.backend.server import api_app

    server_url = f"http://127.0.0.1:{port}"
    logger.info(f"Opening Web Studio: {server_url}")
    webbrowser.open(server_url)

    uvicorn.run(api_app, host="127.0.0.1", port=port, log_level="info")


def main():
    parser = argparse.ArgumentParser(description="VoxCraft Studio - Offline Local TTS Studio")
    parser.add_argument("--web", action="store_true", help="Launch in default web browser")
    parser.add_argument("--wizard", action="store_true", help="Launch Setup & Model Downloader Wizard")
    parser.add_argument("--port", type=int, default=8765, help="Port for server")
    args = parser.parse_args()

    if args.wizard:
        launch_setup_wizard()
    elif args.web:
        launch_web_app(args.port)
    else:
        launch_pyside6_app()


if __name__ == "__main__":
    main()
