"""
VoxCraft Studio - Comprehensive Voice Catalog & Metadata Explorer
Contains curated voice profiles for Kokoro (E1), Piper (E2), and F5-TTS (E3) engines.
"""
from typing import List, Dict, Any, Optional

VOICES_CATALOG: List[Dict[str, Any]] = [
    # Engine 1: Kokoro-82M High-Fidelity Voices
    {"id": "af_bella", "name": "Bella", "engine": "kokoro", "gender": "Female", "language": "English", "locale": "en_US", "style": "Podcast / Warm", "avatar": "🎙️", "color": "#ec4899", "sample_text": "Welcome to VoxCraft Studio, the offline neural speech generation engine.", "tags": ["Podcast", "Warm", "Clear"]},
    {"id": "af_sarah", "name": "Sarah", "engine": "kokoro", "gender": "Female", "language": "English", "locale": "en_US", "style": "Audiobook / Story", "avatar": "📖", "color": "#8b5cf6", "sample_text": "Deep in the quiet forest, whispered stories echoed across the valley.", "tags": ["Audiobook", "Calm", "Story"]},
    {"id": "af_nicole", "name": "Nicole", "engine": "kokoro", "gender": "Female", "language": "English", "locale": "en_US", "style": "News / Clear", "avatar": "💼", "color": "#06b6d4", "sample_text": "Today's market report highlights major advances in decentralized AI inference.", "tags": ["Professional", "News", "Crisp"]},
    {"id": "af_sky", "name": "Sky", "engine": "kokoro", "gender": "Female", "language": "English", "locale": "en_US", "style": "Casual / Friendly", "avatar": "✨", "color": "#38bdf8", "sample_text": "Hey everyone! Let's explore how easy speech synthesis can be on your computer.", "tags": ["Casual", "Friendly", "Bright"]},
    {"id": "am_adam", "name": "Adam", "engine": "kokoro", "gender": "Male", "language": "English", "locale": "en_US", "style": "Trailer / Baritone", "avatar": "🎬", "color": "#f59e0b", "sample_text": "In a universe governed by machine intelligence, one studio changed everything.", "tags": ["Deep", "Trailer", "Baritone"]},
    {"id": "am_michael", "name": "Michael", "engine": "kokoro", "gender": "Male", "language": "English", "locale": "en_US", "style": "Podcast Host", "avatar": "🎙️", "color": "#ef4444", "sample_text": "Welcome back to the studio. Today we're joined by top engineers in voice AI.", "tags": ["Podcast", "Host", "Clear"]},
    {"id": "bf_emma", "name": "Emma", "engine": "kokoro", "gender": "Female", "language": "British English", "locale": "en_GB", "style": "Classic Literature", "avatar": "👑", "color": "#f43f5e", "sample_text": "It is a truth universally acknowledged that high fidelity speech brings stories alive.", "tags": ["British", "Classic", "Narrator"]},
    {"id": "bf_isabella", "name": "Isabella", "engine": "kokoro", "gender": "Female", "language": "British English", "locale": "en_GB", "style": "Modern British", "avatar": "☕", "color": "#14b8a6", "sample_text": "Fancy a quick listen to today's top stories? Grab a cuppa and let's begin.", "tags": ["British", "Modern", "Conversational"]},
    {"id": "bm_george", "name": "George", "engine": "kokoro", "gender": "Male", "language": "British English", "locale": "en_GB", "style": "Documentary / Scholarly", "avatar": "🏛️", "color": "#eab308", "sample_text": "Throughout the twentieth century, technology continuously revolutionized media.", "tags": ["British", "Documentary", "Scholarly"]},
    {"id": "bm_lewis", "name": "Lewis", "engine": "kokoro", "gender": "Male", "language": "British English", "locale": "en_GB", "style": "Storyteller / Warm", "avatar": "🏰", "color": "#84cc16", "sample_text": "The clocktower struck twelve as the traveler entered the ancient gates.", "tags": ["British", "Warm", "Storyteller"]},

    # Engine 2: Piper Multi-Lingual Neural Voices
    {"id": "piper-en_US-lessac-medium", "name": "Lessac", "engine": "piper", "gender": "Female", "language": "English", "locale": "en_US", "style": "Audiobook / Educational", "avatar": "📚", "color": "#a78bfa", "sample_text": "Piper provides lightning fast speech generation with negligible CPU footprint.", "tags": ["Fast", "Educational", "Clear"]},
    {"id": "piper-en_US-libritts_r-medium", "name": "LibriTTS", "engine": "piper", "gender": "Neutral / Multi", "language": "English", "locale": "en_US", "style": "Multi-Speaker Studio", "avatar": "🎧", "color": "#0ea5e9", "sample_text": "Studio trained multi-speaker model containing hundreds of distinct timbres.", "tags": ["Multi-Speaker", "Studio"]},
    {"id": "piper-en_GB-alan-medium", "name": "Alan", "engine": "piper", "gender": "Male", "language": "British English", "locale": "en_GB", "style": "Conversational / Classic", "avatar": "🎩", "color": "#eab308", "sample_text": "Having complete speech synthesis directly on your machine is rather brilliant.", "tags": ["British", "Classic", "Conversational"]},
    {"id": "piper-es_ES-davefx-medium", "name": "DaveFX", "engine": "piper", "gender": "Male", "language": "Spanish", "locale": "es_ES", "style": "Castilian Narrator", "avatar": "🇪🇸", "color": "#f97316", "sample_text": "La síntesis de voz neuronal local permite una privacidad total sin conexión a internet.", "tags": ["Spanish", "Castilian", "Narrator"]},
    {"id": "piper-fr_FR-siwis-medium", "name": "Siwis", "engine": "piper", "gender": "Female", "language": "French", "locale": "fr_FR", "style": "Parisian Expressive", "avatar": "🇫🇷", "color": "#a855f7", "sample_text": "Profitez d'une génération vocale ultra-rapide directement sur votre ordinateur.", "tags": ["French", "Expressive"]},
    {"id": "piper-de_DE-thorsten-medium", "name": "Thorsten", "engine": "piper", "gender": "Male", "language": "German", "locale": "de_DE", "style": "Clear Audiobook", "avatar": "🇩🇪", "color": "#eab308", "sample_text": "Die lokale Sprachgenerierung arbeitet vollkommen ohne Cloud-Verbindung.", "tags": ["German", "Audiobook"]},
    {"id": "piper-it_IT-paola-medium", "name": "Paola", "engine": "piper", "gender": "Female", "language": "Italian", "locale": "it_IT", "style": "Italian Narrator", "avatar": "🇮🇹", "color": "#10b981", "sample_text": "Benvenuti nel sistema di sintesi vocale locale di nuova generazione.", "tags": ["Italian", "Narrator"]},
    {"id": "piper-pt_BR-faber-medium", "name": "Faber", "engine": "piper", "gender": "Male", "language": "Portuguese", "locale": "pt_BR", "style": "Brazilian Portuguese", "avatar": "🇧🇷", "color": "#06b6d4", "sample_text": "Geração de voz em alta velocidade com processamento neural local.", "tags": ["Portuguese", "Brazilian"]},

    # Engine 3: F5-TTS Zero-Shot Voice Cloning
    {"id": "f5_preset_studio_host", "name": "Studio Host", "engine": "f5_tts", "gender": "Male", "language": "English", "locale": "en_US", "style": "Radio Broadcast", "avatar": "📻", "color": "#6366f1", "sample_text": "Broadcasting live across all frequencies, you are tuned into the premier AI network.", "tags": ["Radio", "Broadcast", "Studio"]},
    {"id": "f5_preset_british_narrator", "name": "British Narrator", "engine": "f5_tts", "gender": "Male", "language": "British English", "locale": "en_GB", "style": "Storyteller / Classic", "avatar": "🎭", "color": "#f59e0b", "sample_text": "Deep within the historic archives, timeless records were preserved for future generations.", "tags": ["British", "Storyteller", "Classic"]},
    {"id": "f5_clone_custom", "name": "Voice Clone", "engine": "f5_tts", "gender": "Custom", "language": "Multi-Lingual", "locale": "multi", "style": "Zero-Shot Clone", "avatar": "🧬", "color": "#ec4899", "sample_text": "This voice was cloned using flow matching diffusion from a short audio sample.", "tags": ["Clone", "Zero-Shot", "Diffusion"]}
]


def get_all_voices() -> List[Dict[str, Any]]:
    """Returns the full voice catalog."""
    return VOICES_CATALOG


def get_voice_by_id(voice_id: str) -> Optional[Dict[str, Any]]:
    """Retrieve voice metadata by ID."""
    for voice in VOICES_CATALOG:
        if voice["id"] == voice_id:
            return voice
    return None


def filter_voices(
    engine: Optional[str] = None,
    gender: Optional[str] = None,
    language: Optional[str] = None,
    search_query: Optional[str] = None
) -> List[Dict[str, Any]]:
    """Filter voices by multiple criteria."""
    results = []
    query = search_query.lower().strip() if search_query else ""

    for v in VOICES_CATALOG:
        if engine and engine != "all" and v["engine"] != engine:
            continue
        if gender and gender != "all" and v["gender"].lower() != gender.lower():
            continue
        if language and language != "all":
            v_lang = v.get("language", "").lower()
            s_lang = language.lower()
            if s_lang not in v_lang and v_lang not in s_lang:
                continue
        if query:
            match = (
                query in v["name"].lower() or
                query in v["language"].lower() or
                query in v["style"].lower() or
                any(query in tag.lower() for tag in v.get("tags", []))
            )
            if not match:
                continue
        results.append(v)
    return results
