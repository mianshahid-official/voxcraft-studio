"""
TTS Studio - Local Voice Registry & Offline Metadata Catalog
"""
from typing import List, Dict, Any, Optional

VOICE_CATALOG_DATA = [
    # =========================================================================
    # Engine 1: Kokoro-82M High-Fidelity Voices (28 Voices across 4 Languages)
    # =========================================================================
    # 🇺🇸 American English (Female)
    {"id": "af_bella", "name": "Bella", "engine": "kokoro", "gender": "Female", "language": "US English", "style": "Podcast / Warm", "avatar": "🎙️", "color": "#ec4899", "sample": "Welcome to VoxCraft Studio, the offline neural speech generation engine."},
    {"id": "af_sarah", "name": "Sarah", "engine": "kokoro", "gender": "Female", "language": "US English", "style": "Audiobook / Calm", "avatar": "📖", "color": "#8b5cf6", "sample": "Deep in the quiet forest, whispered stories echoed across the valley."},
    {"id": "af_nicole", "name": "Nicole", "engine": "kokoro", "gender": "Female", "language": "US English", "style": "News / Professional", "avatar": "💼", "color": "#06b6d4", "sample": "Today's market report highlights major advances in decentralized AI inference."},
    {"id": "af_sky", "name": "Sky", "engine": "kokoro", "gender": "Female", "language": "US English", "style": "Casual / Friendly", "avatar": "✨", "color": "#38bdf8", "sample": "Hey everyone! Let's explore how easy speech synthesis can be on your computer."},
    {"id": "af_alloy", "name": "Alloy", "engine": "kokoro", "gender": "Female", "language": "US English", "style": "Crisp / Clear", "avatar": "⚡", "color": "#a855f7", "sample": "Precision synthesis allows lightning-fast audio production without cloud overhead."},
    {"id": "af_aoede", "name": "Aoede", "engine": "kokoro", "gender": "Female", "language": "US English", "style": "Melodic / Narrative", "avatar": "🎵", "color": "#f43f5e", "sample": "Music and melody intertwined as the evening sun dipped below the horizon."},
    {"id": "af_heart", "name": "Heart", "engine": "kokoro", "gender": "Female", "language": "US English", "style": "Empathetic / Warm", "avatar": "💖", "color": "#f472b6", "sample": "I'm right here beside you. Whenever you need support, just take a deep breath."},
    {"id": "af_jessica", "name": "Jessica", "engine": "kokoro", "gender": "Female", "language": "US English", "style": "Conversational", "avatar": "☕", "color": "#14b8a6", "sample": "Let's grab a coffee and chat about all the latest project updates."},
    {"id": "af_kore", "name": "Kore", "engine": "kokoro", "gender": "Female", "language": "US English", "style": "Youthful / Bright", "avatar": "🌸", "color": "#fb7185", "sample": "Good morning world! Today is going to be filled with brand new opportunities."},
    {"id": "af_nova", "name": "Nova", "engine": "kokoro", "gender": "Female", "language": "US English", "style": "Energetic / Dynamic", "avatar": "🌟", "color": "#eab308", "sample": "Get ready for a high octane breakdown of next-generation technology!"},
    {"id": "af_river", "name": "River", "engine": "kokoro", "gender": "Female", "language": "US English", "style": "Calm / Meditative", "avatar": "🌊", "color": "#0ea5e9", "sample": "Let the gentle current carry away the tension as you relax and breathe."},

    # 🇺🇸 American English (Male)
    {"id": "am_adam", "name": "Adam", "engine": "kokoro", "gender": "Male", "language": "US English", "style": "Trailer / Baritone", "avatar": "🎬", "color": "#f59e0b", "sample": "In a universe governed by machine intelligence, one studio changed everything."},
    {"id": "am_michael", "name": "Michael", "engine": "kokoro", "gender": "Male", "language": "US English", "style": "Podcast Host", "avatar": "🎙️", "color": "#ef4444", "sample": "Welcome back to the studio. Today we're joined by top engineers in voice AI."},
    {"id": "am_echo", "name": "Echo", "engine": "kokoro", "gender": "Male", "language": "US English", "style": "Studio Announcer", "avatar": "📢", "color": "#6366f1", "sample": "Stand by for an important technical announcement regarding local model execution."},
    {"id": "am_eric", "name": "Eric", "engine": "kokoro", "gender": "Male", "language": "US English", "style": "Warm / Expressive", "avatar": "🎧", "color": "#84cc16", "sample": "Every great idea starts with curiosity and a desire to build something new."},
    {"id": "am_fenrir", "name": "Fenrir", "engine": "kokoro", "gender": "Male", "language": "US English", "style": "Resonant / Powerful", "avatar": "🐺", "color": "#64748b", "sample": "From the frozen northern peaks, the legend began its timeless journey."},
    {"id": "am_liam", "name": "Liam", "engine": "kokoro", "gender": "Male", "language": "US English", "style": "Modern / Youthful", "avatar": "📱", "color": "#10b981", "sample": "Check out this awesome new feature we just shipped in the latest release."},
    {"id": "am_onyx", "name": "Onyx", "engine": "kokoro", "gender": "Male", "language": "US English", "style": "Deep Baritone", "avatar": "🗿", "color": "#475569", "sample": "Solid foundations ensure uninterrupted performance under the heaviest workloads."},
    {"id": "am_puck", "name": "Puck", "engine": "kokoro", "gender": "Male", "language": "US English", "style": "Playful / Fast", "avatar": "🎭", "color": "#f97316", "sample": "Hold on tight, because we are diving straight into the fun part!"},
    {"id": "am_santa", "name": "Santa", "engine": "kokoro", "gender": "Male", "language": "US English", "style": "Jolly / Mature", "avatar": "🎅", "color": "#dc2626", "sample": "Ho ho ho! Wishing everyone joyful moments and great success in their projects."},

    # 🇮🇳 Hindi (Female & Male)
    {"id": "hf_alpha", "name": "Alpha", "engine": "kokoro", "gender": "Female", "language": "Hindi", "style": "Warm / Natural Hindi", "avatar": "🇮🇳", "color": "#f97316", "sample": "नमस्ते, VoxCraft Studio में आपका स्वागत है। यह पूर्णतया ऑफ़लाइन काम करता है।"},
    {"id": "hf_beta", "name": "Beta", "engine": "kokoro", "gender": "Female", "language": "Hindi", "style": "Clear / Expressive Hindi", "avatar": "🌸", "color": "#ec4899", "sample": "आज के समाचार में हम कृत्रिम बुद्धिमत्ता की नई तकनीकों पर चर्चा करेंगे।"},
    {"id": "hm_omega", "name": "Omega", "engine": "kokoro", "gender": "Male", "language": "Hindi", "style": "Deep Narrator Hindi", "avatar": "🎙️", "color": "#8b5cf6", "sample": "इतिहास के पन्नों में छुपी कहानियाँ हमें हमेशा प्रेरणा देती हैं।"},
    {"id": "hm_psi", "name": "Psi", "engine": "kokoro", "gender": "Male", "language": "Hindi", "style": "Conversational Hindi", "avatar": "🇮🇳", "color": "#10b981", "sample": "क्या आप जानते हैं कि यह वॉइस मॉडल आपके कंप्यूटर पर बिना इंटरनेट के चलता है?"},

    # 🇪🇸 Spanish (Female & Male)
    {"id": "ef_dora", "name": "Dora", "engine": "kokoro", "gender": "Female", "language": "Spanish", "style": "Castilian / Expressive", "avatar": "🇪🇸", "color": "#ea580c", "sample": "Hola a todos, bienvenidos al estudio de generación de voz neuronal totalmente local."},
    {"id": "em_alex", "name": "Alex", "engine": "kokoro", "gender": "Male", "language": "Spanish", "style": "Narrator / Neutral Spanish", "avatar": "🎙️", "color": "#0284c7", "sample": "La tecnología de síntesis de voz permite crear contenido de alta calidad en segundos."},
    {"id": "em_santa", "name": "Santa", "engine": "kokoro", "gender": "Male", "language": "Spanish", "style": "Warm Spanish Voice", "avatar": "🎅", "color": "#dc2626", "sample": "Felices fiestas y que tengan un excelente día de trabajo y creatividad."},

    # 🇫🇷 French (Female)
    {"id": "ff_siwis", "name": "Siwis", "engine": "kokoro", "gender": "Female", "language": "French", "style": "Parisian / Articulate", "avatar": "🇫🇷", "color": "#7c3aed", "sample": "Bonjour et bienvenue dans VoxCraft Studio, votre moteur de synthèse vocale hors ligne."},

    # =========================================================================
    # Engine 2: Piper Multi-Lingual Neural Voices
    # =========================================================================
    {"id": "piper-en_US-lessac-medium", "name": "Lessac", "engine": "piper", "gender": "Female", "language": "US English", "style": "Audiobook / Educational", "avatar": "📚", "color": "#a78bfa", "sample": "Piper provides lightning fast speech generation with negligible CPU footprint."},
    {"id": "piper-en_US-libritts_r-medium", "name": "LibriTTS", "engine": "piper", "gender": "Neutral / Multi", "language": "US English", "style": "Multi-Speaker Studio", "avatar": "🎧", "color": "#0ea5e9", "sample": "Studio trained multi-speaker model containing hundreds of distinct timbres."},
    {"id": "piper-en_GB-alan-medium", "name": "Alan", "engine": "piper", "gender": "Male", "language": "British English", "style": "Conversational / Classic", "avatar": "🎩", "color": "#eab308", "sample": "Having complete speech synthesis directly on your machine is rather brilliant."},
    {"id": "piper-es_ES-davefx-medium", "name": "DaveFX", "engine": "piper", "gender": "Male", "language": "Spanish", "style": "Castilian Narrator", "avatar": "🇪🇸", "color": "#f97316", "sample": "La síntesis de voz neuronal local permite una privacidad total sin conexión a internet."},
    {"id": "piper-fr_FR-siwis-medium", "name": "Siwis", "engine": "piper", "gender": "Female", "language": "French", "style": "Parisian Expressive", "avatar": "🇫🇷", "color": "#a855f7", "sample": "Profitez d'une génération vocale ultra-rapide directement sur votre ordinateur."},
    {"id": "piper-de_DE-thorsten-medium", "name": "Thorsten", "engine": "piper", "gender": "Male", "language": "German", "style": "Clear Audiobook", "avatar": "🇩🇪", "color": "#eab308", "sample": "Die lokale Sprachgenerierung arbeitet vollkommen ohne Cloud-Verbindung."},
    {"id": "piper-it_IT-paola-medium", "name": "Paola", "engine": "piper", "gender": "Female", "language": "Italian", "style": "Italian Narrator", "avatar": "🇮🇹", "color": "#10b981", "sample": "Benvenuti nel sistema di sintesi vocale locale di nuova generazione."},
    {"id": "piper-pt_BR-faber-medium", "name": "Faber", "engine": "piper", "gender": "Male", "language": "Portuguese", "style": "Brazilian Portuguese", "avatar": "🇧🇷", "color": "#06b6d4", "sample": "Geração de voz em alta velocidade com processamento neural local."},

    # =========================================================================
    # Engine 3: F5-TTS Zero-Shot Voice Cloning (Used in Voice Cloning Studio)
    # =========================================================================
    {"id": "f5_preset_studio_host", "name": "Studio Host", "engine": "f5_tts", "gender": "Male", "language": "US English", "style": "Radio Broadcast", "avatar": "📻", "color": "#6366f1", "sample": "Broadcasting live across all frequencies, you are tuned into the premier AI network."},
    {"id": "f5_preset_british_narrator", "name": "British Narrator", "engine": "f5_tts", "gender": "Male", "language": "British English", "style": "Storyteller / Classic", "avatar": "🎭", "color": "#f59e0b", "sample": "Deep within the historic archives, timeless records were preserved for future generations."},
    {"id": "f5_clone_custom", "name": "Voice Clone", "engine": "f5_tts", "gender": "Custom", "language": "Multi-Lingual", "style": "Zero-Shot Clone", "avatar": "🧬", "color": "#ec4899", "sample": "This voice was cloned using flow matching diffusion from a short audio sample."}
]


class VoiceCatalog:
    """Local offline voice registry & metadata catalog."""

    @staticmethod
    def get_all() -> List[Dict[str, Any]]:
        return VOICE_CATALOG_DATA

    @staticmethod
    def get_tts_voices() -> List[Dict[str, Any]]:
        """Get voices available for standard TTS Studio (excluding custom voice clone targets)."""
        return [v for v in VOICE_CATALOG_DATA if v.get("engine") in ("kokoro", "piper")]

    @staticmethod
    def get_by_id(voice_id: str) -> Optional[Dict[str, Any]]:
        for v in VOICE_CATALOG_DATA:
            if v["id"] == voice_id:
                return v
        return None

    @staticmethod
    def format_label(v: Dict[str, Any], include_engine: bool = False) -> str:
        """Format friendly label: e.g. '🎬 Adam (US English)' or '🇮🇳 Alpha (Hindi)'."""
        avatar = v.get("avatar", "🎙️")
        name = v.get("name", "Voice")
        lang = v.get("language", "US English")
        return f"{avatar} {name} ({lang})"

    @staticmethod
    def get_languages() -> List[str]:
        """Get unique available languages."""
        langs = []
        for v in VOICE_CATALOG_DATA:
            l = v.get("language", "US English")
            if l not in langs and l != "Multi-Lingual":
                langs.append(l)
        return sorted(langs)

    @staticmethod
    def is_model_installed(voice_id: str) -> tuple:
        """
        Checks whether the offline model weights for a voice are present on disk.
        Returns: (is_installed: bool, manifest_key: str)
        """
        v = VoiceCatalog.get_by_id(voice_id)
        if not v:
            return True, ""

        eng = v.get("engine", "kokoro")
        if eng == "kokoro":
            from ..engines.kokoro.engine import KokoroEngine
            return KokoroEngine().is_installed(), "kokoro-v0_19"
        elif eng == "piper":
            from ..config.paths import PIPER_DIR
            clean_name = voice_id.replace("piper-", "")
            matches = list(PIPER_DIR.glob(f"*{clean_name}*.onnx"))
            return len(matches) > 0, voice_id
        elif eng == "f5_tts":
            from ..config.paths import F5_DIR
            has_f5 = any(F5_DIR.glob("*.safetensors")) or any(F5_DIR.glob("*.pt"))
            return has_f5, "f5-tts-base"
        return True, ""

    @staticmethod
    def filter(engine: str = "all", gender: str = "all", language: str = "all", query: str = "") -> List[Dict[str, Any]]:
        res = []
        q = query.lower().strip()
        for v in VOICE_CATALOG_DATA:
            if engine != "all" and v["engine"] != engine:
                continue
            if gender != "all" and v["gender"].lower() != gender.lower():
                continue
            if language != "all" and language.lower() not in v["language"].lower():
                continue
            if q and (q not in v["name"].lower() and q not in v["style"].lower() and q not in v["language"].lower()):
                continue
            res.append(v)
        return res
