"""
TTS Studio - Local Voice Registry & Offline Metadata Catalog
"""
from typing import List, Dict, Any, Optional

VOICE_CATALOG_DATA = [
    # Engine 1: Kokoro-82M High-Fidelity Voices
    {"id": "af_bella", "name": "Bella", "engine": "kokoro", "gender": "Female", "language": "English", "style": "Podcast / Warm", "avatar": "🎙️", "color": "#ec4899", "sample": "Welcome to VoxCraft Studio, the offline neural speech generation engine."},
    {"id": "af_sarah", "name": "Sarah", "engine": "kokoro", "gender": "Female", "language": "English", "style": "Audiobook / Story", "avatar": "📖", "color": "#8b5cf6", "sample": "Deep in the quiet forest, whispered stories echoed across the valley."},
    {"id": "af_nicole", "name": "Nicole", "engine": "kokoro", "gender": "Female", "language": "English", "style": "News / Clear", "avatar": "💼", "color": "#06b6d4", "sample": "Today's market report highlights major advances in decentralized AI inference."},
    {"id": "af_sky", "name": "Sky", "engine": "kokoro", "gender": "Female", "language": "English", "style": "Casual / Friendly", "avatar": "✨", "color": "#38bdf8", "sample": "Hey everyone! Let's explore how easy speech synthesis can be on your computer."},
    {"id": "am_adam", "name": "Adam", "engine": "kokoro", "gender": "Male", "language": "English", "style": "Trailer / Baritone", "avatar": "🎬", "color": "#f59e0b", "sample": "In a universe governed by machine intelligence, one studio changed everything."},
    {"id": "am_michael", "name": "Michael", "engine": "kokoro", "gender": "Male", "language": "English", "style": "Podcast Host", "avatar": "🎙️", "color": "#ef4444", "sample": "Welcome back to the studio. Today we're joined by top engineers in voice AI."},
    {"id": "bf_emma", "name": "Emma", "engine": "kokoro", "gender": "Female", "language": "British English", "style": "Classic Literature", "avatar": "👑", "color": "#f43f5e", "sample": "It is a truth universally acknowledged that high fidelity speech brings stories alive."},
    {"id": "bf_isabella", "name": "Isabella", "engine": "kokoro", "gender": "Female", "language": "British English", "style": "Modern British", "avatar": "☕", "color": "#14b8a6", "sample": "Fancy a quick listen to today's top stories? Grab a cuppa and let's begin."},
    {"id": "bm_george", "name": "George", "engine": "kokoro", "gender": "Male", "language": "British English", "style": "Documentary / Scholarly", "avatar": "🏛️", "color": "#eab308", "sample": "Throughout the twentieth century, technology continuously revolutionized media."},
    {"id": "bm_lewis", "name": "Lewis", "engine": "kokoro", "gender": "Male", "language": "British English", "style": "Storyteller / Warm", "avatar": "🏰", "color": "#84cc16", "sample": "The clocktower struck twelve as the traveler entered the ancient gates."},

    # Engine 2: Piper Multi-Lingual Neural Voices
    {"id": "piper-en_US-lessac-medium", "name": "Lessac", "engine": "piper", "gender": "Female", "language": "English", "style": "Audiobook / Educational", "avatar": "📚", "color": "#a78bfa", "sample": "Piper provides lightning fast speech generation with negligible CPU footprint."},
    {"id": "piper-en_US-libritts_r-medium", "name": "LibriTTS", "engine": "piper", "gender": "Neutral / Multi", "language": "English", "style": "Multi-Speaker Studio", "avatar": "🎧", "color": "#0ea5e9", "sample": "Studio trained multi-speaker model containing hundreds of distinct timbres."},
    {"id": "piper-en_GB-alan-medium", "name": "Alan", "engine": "piper", "gender": "Male", "language": "British English", "style": "Conversational / Classic", "avatar": "🎩", "color": "#eab308", "sample": "Having complete speech synthesis directly on your machine is rather brilliant."},
    {"id": "piper-es_ES-davefx-medium", "name": "DaveFX", "engine": "piper", "gender": "Male", "language": "Spanish", "style": "Castilian Narrator", "avatar": "🇪🇸", "color": "#f97316", "sample": "La síntesis de voz neuronal local permite una privacidad total sin conexión a internet."},
    {"id": "piper-fr_FR-siwis-medium", "name": "Siwis", "engine": "piper", "gender": "Female", "language": "French", "style": "Parisian Expressive", "avatar": "🇫🇷", "color": "#a855f7", "sample": "Profitez d'une génération vocale ultra-rapide directement sur votre ordinateur."},
    {"id": "piper-de_DE-thorsten-medium", "name": "Thorsten", "engine": "piper", "gender": "Male", "language": "German", "style": "Clear Audiobook", "avatar": "🇩🇪", "color": "#eab308", "sample": "Die lokale Sprachgenerierung arbeitet vollkommen ohne Cloud-Verbindung."},
    {"id": "piper-it_IT-paola-medium", "name": "Paola", "engine": "piper", "gender": "Female", "language": "Italian", "style": "Italian Narrator", "avatar": "🇮🇹", "color": "#10b981", "sample": "Benvenuti nel sistema di sintesi vocale locale di nuova generazione."},
    {"id": "piper-pt_BR-faber-medium", "name": "Faber", "engine": "piper", "gender": "Male", "language": "Portuguese", "style": "Brazilian Portuguese", "avatar": "🇧🇷", "color": "#06b6d4", "sample": "Geração de voz em alta velocidade com processamento neural local."},

    # Engine 3: F5-TTS Zero-Shot Voice Cloning
    {"id": "f5_preset_studio_host", "name": "Studio Host", "engine": "f5_tts", "gender": "Male", "language": "English", "style": "Radio Broadcast", "avatar": "📻", "color": "#6366f1", "sample": "Broadcasting live across all frequencies, you are tuned into the premier AI network."},
    {"id": "f5_preset_british_narrator", "name": "British Narrator", "engine": "f5_tts", "gender": "Male", "language": "British English", "style": "Storyteller / Classic", "avatar": "🎭", "color": "#f59e0b", "sample": "Deep within the historic archives, timeless records were preserved for future generations."},
    {"id": "f5_clone_custom", "name": "Voice Clone", "engine": "f5_tts", "gender": "Custom", "language": "Multi-Lingual", "style": "Zero-Shot Clone", "avatar": "🧬", "color": "#ec4899", "sample": "This voice was cloned using flow matching diffusion from a short audio sample."}
]


class VoiceCatalog:
    """Local offline voice registry."""

    @staticmethod
    def get_all() -> List[Dict[str, Any]]:
        return VOICE_CATALOG_DATA

    @staticmethod
    def get_by_id(voice_id: str) -> Optional[Dict[str, Any]]:
        for v in VOICE_CATALOG_DATA:
            if v["id"] == voice_id:
                return v
        return None

    @staticmethod
    def format_label(v: Dict[str, Any], include_engine: bool = True) -> str:
        """Format friendly label: e.g. '🎬 Adam (English) (E1)' or '📚 Lessac (English) (E2)'."""
        avatar = v.get("avatar", "🎙️")
        name = v.get("name", "Voice")
        lang = v.get("language", "English")
        eng = v.get("engine", "kokoro")
        eng_tag = " (E1)" if eng == "kokoro" else (" (E2)" if eng == "piper" else " (E3)") if include_engine else ""
        return f"{avatar} {name} ({lang}){eng_tag}"

    @staticmethod
    def get_languages() -> List[str]:
        """Get unique available languages."""
        langs = []
        for v in VOICE_CATALOG_DATA:
            l = v.get("language", "English")
            if l not in langs:
                langs.append(l)
        return sorted(langs)

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
