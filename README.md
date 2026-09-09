# 🎙️ VoxCraft Studio — Offline AI Speech & Podcast Studio

<div align="center">

![VoxCraft Studio App Icon](app/resources/icons/app_icon.png)

### **Production-Grade, 100% Offline AI Speech Synthesis & Podcast Studio for Windows**

[![Python 3.10+](https://img.shields.io/badge/Python-3.10%2B-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://www.python.org/)
[![PySide6 / Qt](https://img.shields.io/badge/GUI-PySide6%20%2F%20Qt6-41CD52?style=for-the-badge&logo=qt&logoColor=white)](https://www.qt.io/)
[![ONNX Runtime](https://img.shields.io/badge/Inference-ONNX%20%2F%20DirectML%20%2F%20CUDA-005CED?style=for-the-badge)](https://onnxruntime.ai/)
[![Offline First](https://img.shields.io/badge/Privacy-100%25%20Offline%20Local-10B981?style=for-the-badge)](https://github.com/)
[![License: MIT](https://img.shields.io/badge/License-MIT-purple?style=for-the-badge)](LICENSE)

**Architected & Developed by Shahid**

</div>

---

## 🌟 Highlights

**VoxCraft Studio** brings high-fidelity neural speech synthesis and multi-speaker podcast generation directly to your Windows desktop. Built for creators, developers, and privacy-conscious users, VoxCraft Studio operates **100% locally on your machine with zero cloud latency, zero telemetry, and no active internet connection required during generation**.

---

## 🚀 Key Features & Studio Workspaces

### 1. ⚡ Studio Text-to-Speech (TTS)
- **Ultra-HD Voice Synthesis**: 24kHz neural speech generation across American English, British English, Hindi, Spanish, and French.
- **Dual-Voice Blending Matrix**: Create unique hybrid vocal identities by blending two voice vectors with real-time ratio sliders.
- **Audio Modulation**: Real-time sliders for Pitch adjustment (`-6st` to `+6st`), Speed/Rate (`0.5x` to `2.0x`), and Volume dynamics.
- **File Importer & Quick Prompts**: Instant import of `.txt` / `.md` scripts with multi-lingual greeting templates.

### 2. 📻 Podcast Studio (Multi-Speaker Dialogue Engine)
- **Multi-Cast Workflow**: Configure conversation casts (e.g. Host, Guest, Narrator, Expert) with customizable avatars, colors, and distinct voices.
- **Syntax-Assisted Script Editor**: Seamlessly tag dialogue lines per speaker with one-click speaker tag insertion.
- **Full Episode Assembly**: Generates stitched, production-ready audio dialogue files with natural conversation pacing.

### 3. 📦 Batch Processing Queue
- **High-Throughput Queue**: Add hundreds of `.txt` or `.md` files for background batch conversion.
- **Live Progress & Status HUD**: Real-time duration trackers, success/fail diagnostics, and direct output folder links.

### 4. 🎭 Voice Library Explorer
- **Visual Voice Browser**: Browse curated voice cards with character descriptions, gender, style, and regional accents.
- **Instant Previews**: 1-click audio sample preview generation.
- **Categorized Filters**: Filter by *Studio Ultra-HD*, *Solo Narrators*, and *Cloned Voices*.

### 5. 🧬 Zero-Shot Voice Cloning
- **Acoustic Flow-Matching**: Clone any speaker's vocal characteristics from a 5–15 second reference audio sample (`.wav`, `.mp3`).
- **Local Audio Synthesis**: Generate new speech in the cloned voice without uploading audio to external servers.

### 6. 📦 Offline Voice Packages & Storage Manager
- **One-Click Voice Packages**: Manage and download high-fidelity voice packs directly inside the desktop app.
- **Real-Time Download HUD**: Live download speed (MB/s), progress percentages, and ETA counters with background download capability.
- **Zero Jargon**: Intuitive package titles, language flags, and storage indicators.

### 7. 🎛️ Interactive Waveform Audio Player
- **Real-Time Waveform Visualizer**: Scrub, seek, and inspect audio dynamics visually.
- **Custom Play/Pause Engine**: Crisp vector controls built for seamless playback and looping.
- **Format Exporter**: Save synthesized audio as `.wav`, `.mp3`, or `.flac`.

---

## 📂 Automatic Production Export Organization

Every synthesis run automatically packages all assets into a dedicated folder in `exports/`:

```
exports/A_desperate_tribe_of_Glimmer-Foxes_2026-09-09_12-30-00/
├── audio.wav        # Studio 24kHz synthesized audio
├── text.txt         # Original input text
├── timestamps.json  # Word-level timing metadata
├── subtitles.srt    # SubRip subtitles for video editing (Premiere, DaVinci, CapCut)
└── subtitles.vtt    # WebVTT captions
```

---

## 💻 System Requirements & Acceleration

| Component | Minimum Specification | Recommended Specification |
| :--- | :--- | :--- |
| **OS** | Windows 10 / 11 (64-bit) | Windows 11 (64-bit) |
| **Python** | Python 3.10 – 3.12 | Python 3.11 / 3.12 |
| **RAM** | 8 GB | 16 GB+ |
| **Storage** | 2 GB free disk space | 5 GB SSD storage |
| **Acceleration** | AVX2 / FMA multi-threaded CPU | NVIDIA GPU (CUDA) or DirectML GPU |

---

## 🛠️ Quickstart & Installation

### Option 1: One-Click Windows Launcher (Recommended)

1. Clone or download the repository:
   ```cmd
   git clone https://github.com/mianshahid-official/voxcraft-studio.git
   cd voxcraft-studio
   ```
2. Double-click **`install.bat`** to install dependencies and run the initial setup wizard.
3. Double-click **`run.bat`** to launch VoxCraft Studio!

---

### Option 2: Manual Python Setup

1. **Create and activate a virtual environment (optional but recommended):**
   ```cmd
   python -m venv .venv
   .venv\Scripts\activate
   ```

2. **Install dependencies:**
   ```cmd
   pip install -r requirements.txt
   ```

3. **Launch the Desktop Application:**
   ```cmd
   python run.py
   ```

---

## 🏗️ Project Architecture

```
voxcraft-studio/
├── app/
│   ├── backend/           # Configuration, download manager & storage services
│   ├── config/            # Paths, settings & voice package manifests
│   ├── core/              # Model lifecycle, project management & diagnostic tools
│   ├── engines/           # Neural synthesis backends (Kokoro, Piper, F5-TTS)
│   ├── gui/               # PySide6 Desktop GUI
│   │   ├── views/         # Studio TTS, Podcast, Batch, Library, Voice Packages, Settings
│   │   ├── widgets/       # Waveform player, download modals, sliders, cards
│   │   └── wizard/        # Initial setup wizard & diagnostic tester
│   ├── services/          # Synthesis, batch narration & podcast stitching pipelines
│   └── voices/            # Voice catalog metadata & speaker embeddings
├── models/                # Local offline neural model weights & voice packs
├── exports/               # Automatically organized output audio & subtitle folders
├── installer/             # Setup wizard scripts
├── run.py                 # Primary application entrypoint
├── install.bat            # 1-click Windows installer script
├── run.bat                # 1-click Windows desktop launcher
└── requirements.txt       # Python dependency manifest
```

---

## 📄 License & Credits

- **Architect & Lead Developer**: **Shahid**
- **License**: Released under the **[MIT License](LICENSE)**. Free for personal and commercial use.
