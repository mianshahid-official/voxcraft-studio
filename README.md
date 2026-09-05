# 🎙️ VoxCraft Studio — Offline Neural TTS & Podcast Desktop Studio

<div align="center">

![VoxCraft Studio App Icon](app/resources/icons/app_icon.png)

### **Production-Grade, 100% Offline Multi-Engine Text-to-Speech & Podcast Studio for Windows**

[![Python 3.10+](https://img.shields.io/badge/Python-3.10%2B-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://www.python.org/)
[![PySide6 / Qt](https://img.shields.io/badge/GUI-PySide6%20%2F%20Qt-41CD52?style=for-the-badge&logo=qt&logoColor=white)](https://www.qt.io/)
[![ONNX Runtime](https://img.shields.io/badge/Inference-ONNX%20%2F%20DirectML%20%2F%20CUDA-005CED?style=for-the-badge)](https://onnxruntime.ai/)
[![Offline First](https://img.shields.io/badge/Privacy-100%25%20Offline%20Local-10B981?style=for-the-badge)](https://github.com/)
[![License: MIT](https://img.shields.io/badge/License-MIT-purple?style=for-the-badge)](LICENSE)

**Developed by Shahid**

</div>

<div align="center">

![VoxCraft Studio UI Preview](docs/screenshots/app_preview.png)

</div>

---

## 🌟 Highlights

**VoxCraft Studio** brings studio-grade neural speech synthesis directly to your Windows desktop. Designed for privacy, speed, and creative freedom, VoxCraft Studio operates **100% locally with zero cloud latency and no internet connection required**.

### ⚡ 3 Integrated Neural Speech Engines:
1. **Engine 1 (Kokoro-82M ONNX)**:
   - Ultra-fast 24kHz studio-quality voice generation.
   - Dual-Voice Blending vector matrix (mix two distinct voice styles with custom blend ratios).
2. **Engine 2 (Piper Neural Multi-Lingual)**:
   - Extremely lightweight, low-latency CPU speech synthesis.
   - Multi-lingual neural models: English, British English, Spanish, French, German, Italian, Portuguese, and more.
3. **Engine 3 (F5-TTS Flow Matching Diffusion)**:
   - Zero-shot neural voice cloning from short 5–15s reference audio samples.
   - Built-in studio presets for narration and broadcast speech.

---

## 🚀 Key Features

- 🔒 **100% Offline Privacy**: Zero telemetry, zero cloud APIs, zero subscription fees.
- ⚡ **Intelligent Acceleration**: Automatic detection for **NVIDIA CUDA** and **Windows DirectML**, with optimized multi-threaded CPU fallback.
- 📻 **Podcast Studio**: Multi-speaker conversation writer (Host, Guest, Narrator) with per-speaker voice, rate, pitch, and volume controls.
- 📦 **Batch File Narration**: Queue multiple text files (`.txt`, `.md`) for bulk speech conversion with real-time status tracking.
- 🎭 **Voice Library Explorer**: Browse and search voice models with instant audio sample previews.
- 🌐 **Multi-Language Selector**: Filter voices and languages with a single click.
- 📦 **In-App Model Hub**: Download and manage additional international language packages directly inside the desktop app.
- 🎛️ **Live Audio HUD**: Waveform playback bar with seekable scrubber, volume slider, playback speed controls, and WAV export.

---

## 🛠️ Quick Start

### Prerequisites
- Windows 10 / 11 (64-bit)
- Python 3.10 or higher

### 1. Clone the Repository
```bash
git clone https://github.com/mianshahid-official/voxcraft-studio.git
cd voxcraft-studio
```

### 2. Install Dependencies
```bash
pip install -r requirements.txt
```

### 3. Launch Application
```bash
# Option A: Run via root launcher
python run.py

# Option B: Run 1-click batch launcher
run.bat

# Option C: Direct module execution
python -m app.main
```

---

## 📦 First-Run Setup & Model Downloader Wizard

When you first launch VoxCraft Studio, the built-in **Setup Wizard** automatically:
1. Performs hardware diagnostics (CPU cores, RAM, GPU/DirectML support).
2. Lets you choose your neural models (Kokoro-82M, Piper Multi-Lingual, F5-TTS).
3. Downloads and verifies model weights with SHA256 integrity checksums.
4. Synthesizes a test audio sample to verify your offline audio pipeline.

To run the Setup Wizard at any time:
```bash
python run.py --wizard
```

---

## 📂 Project Structure

```
voxcraft-studio/
├── app/
│   ├── config/               # Settings, paths, and download manifests
│   ├── core/                 # Audio DSP, chunking, timestamps, hardware detection
│   ├── engines/              # Engine implementations (Kokoro, Piper, F5-TTS)
│   ├── gui/
│   │   ├── views/            # PySide6 Studio views (TTS, Podcast, Batch, Voice Library, etc.)
│   │   ├── widgets/          # Glassmorphism cards, sliders, audio player HUD
│   │   ├── wizard/           # Setup & Model Installer Wizard
│   │   └── theme.py          # Dark Studio glassmorphism design system
│   ├── services/             # TTS synthesis, podcast assembly, storage & cache
│   ├── voices/               # Local voice catalog & language registry
│   └── main.py               # Main application launcher
├── data/
│   └── reference_voices/     # Built-in reference audio for voice cloning
├── models/                   # Local offline neural model weights
├── exports/                  # Output directory for generated WAV/MP3 files
├── tests/                    # End-to-end pipeline verification test suite
├── .gitignore                # Git exclusions for models and exports
├── run.py                    # Root entrypoint
├── run.bat                   # 1-click Windows launcher
├── install.bat               # 1-click Windows installer
├── requirements.txt          # Python dependencies
└── README.md                 # Documentation
```

---

## 🧪 Running Automated Tests

Run the test suite to verify offline neural synthesis, chunking, audio DSP, and UI instantiation:
```bash
python tests/test_pyside_pipeline.py
```

---

## 📜 License

Distributed under the **MIT License**. See `LICENSE` for more information.

---

<div align="center">

**VoxCraft Studio** • Developed with ❤️ by **Shahid**

</div>
