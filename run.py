"""
VoxCraft Studio - Root Launcher Entrypoint
Execute: python run.py
"""
import sys
from pathlib import Path

# Add project root to sys.path
PROJECT_ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(PROJECT_ROOT))

from app.main import main

if __name__ == "__main__":
    main()
