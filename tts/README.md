# 🎙️ VoxCraft Studio — Offline Neural TTS & Podcast Desktop Studio

**VoxCraft Studio** is a state-of-the-art, fully offline desktop application for Windows designed for high-fidelity speech synthesis and podcast creation using **Kokoro TTS**, **Piper TTS**, and **F5-TTS**.

---

## ✨ Key Features

1. **100% Offline Operation**:
   - Once models are downloaded, VoxCraft Studio requires **no internet connection** or cloud API keys.
   - All voice synthesis and audio processing execute locally on your machine.

2. **Intelligent Hardware Acceleration**:
   - **GPU Priority**: Auto-detects NVIDIA CUDA and Windows DirectML GPU acceleration.
   - **Seamless CPU Fallback**: Automatically optimizes multi-threaded CPU execution if no dedicated GPU is available.

3. **Supported TTS Engines**:
   - **Kokoro-82M (ONNX)**: Ultra-fast 24kHz studio-quality voices (American, British, Japanese, Mandarin, Spanish, French, Italian, Hindi).
   - **Piper Neural TTS**: Lightweight, low-CPU speech synthesis supporting 40+ languages and multi-speaker models.
   - **F5-TTS**: Zero-shot voice cloning using flow-matching diffusion and reference audio samples.

4. **Multi-Speaker Podcast & Dialogue Studio**:
   - Visual script editor for multi-character conversations (Host, Guest, Narrator).
   - Assign custom voice models, pitch, and speaking rates to individual characters.
   - Synchronized timeline with real-time dialogue block highlights during playback.
   - Export full master episode or individual audio tracks/stems.

5. **Acoustic DSP & Voice Customization**:
   - Pitch shifting (-12 to +12 semitones) and Speed stretching (0.5x to 2.5x).
   - Voice Blending: Blend two Kokoro voices with custom ratios (e.g., 60% Bella + 40% Nicole).
   - Equalization (Bass Warmth / Treble Clarity), Room Reverb, and Broadcast Loudness Normalization (-14 LUFS).

6. **Interactive Studio GUI**:
   - Modern Dark Glassmorphism Studio Theme with HTML5 Canvas Waveform visualizer.
   - One-click Voice Library Explorer with instant audio sample previews.
   - Automated Setup & Model Downloader Wizard with live progress bars, transfer speeds, and ETA.

---

## 🚀 Quick Start (Running Locally)

### 1. Launch with 1-Click
Double-click `run.bat` in the root folder.

### 2. Manual Terminal Launch
```bash
# Start Native Desktop Studio Window
python app/main.py

# Or run in Web Browser Mode
python app/main.py --web
```

---

## 📦 Automated Model Setup Wizard

To run the interactive model installer and requirements checker:
```bash
python installer/installer_wizard.py
```

### Models Managed Offline:
- **Kokoro-82M**: `models/kokoro/kokoro-v0_19.onnx` + `voices.bin` (~310 MB)
- **Piper Voices**: `models/piper/en_US-lessac-medium.onnx` (~60 MB)
- **F5-TTS Base**: `models/f5_tts/model_1200000.safetensors` (~1.2 GB)

---

## 🛠️ Building Standalone Windows `.exe` Installer

To package VoxCraft Studio into a standalone executable:
```bash
# Package main application
python installer/build_installer.py

# Package Setup Wizard into VoxCraft_Setup.exe
python installer/build_installer.py wizard
```
The resulting executables will be generated in the `dist/` directory.

---

## 📂 Project Structure

```
d:\Browser\
├── app/
│   ├── backend/
│   │   ├── config.py                 # Paths, manifest URLs, sample rates
│   │   ├── hardware.py               # CPU, RAM, GPU/DirectML diagnostics
│   │   ├── audio_processor.py        # DSP pitch/speed/reverb/export pipeline
│   │   ├── voice_catalog.py          # 60+ voice profiles and metadata
│   │   ├── model_manager.py          # Offline download manager & checksum verifier
│   │   ├── podcast_generator.py      # Multi-speaker dialogue compiler & timeline
│   │   ├── project_store.py          # SQLite persistence for history and presets
│   │   ├── server.py                 # FastAPI & PyWebView API bridge
│   │   └── engines/
│   │       ├── base_engine.py        # Abstract TTS interface
│   │       ├── kokoro_engine.py      # Kokoro ONNX & voice blending
│   │       ├── piper_engine.py       # Piper ONNX neural engine
│   │       └── f5_engine.py          # F5-TTS zero-shot voice cloning
│   ├── frontend/
│   │   ├── index.html                # Modern Glassmorphism Studio UI
│   │   ├── css/                      # Design system, components, layouts
│   │   └── js/                       # API bridge, audio visualizer, studio controllers
│   └── main.py                       # Desktop application entrypoint
├── installer/
│   ├── installer_wizard.py           # GUI installer & requirements wizard
│   └── build_installer.py            # PyInstaller packaging script
├── models/                           # Local offline model cache
├── exports/                          # Output folder for generated WAV/MP3 files
├── run.bat                           # 1-Click launcher
├── install.bat                       # 1-Click setup
└── requirements.txt                  # Python dependencies
```
