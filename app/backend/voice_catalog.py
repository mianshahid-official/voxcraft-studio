"""
VoxCraft Studio - Comprehensive Voice Catalog & Metadata Explorer
Contains curated voice profiles for Kokoro, Piper, and F5-TTS engines with language, gender, accent, and style filters.
"""
from typing import List, Dict, Any, Optional

VOICES_CATALOG: List[Dict[str, Any]] = [
    # -------------------------------------------------------------
    # Kokoro-82M High-Fidelity Neural Voices (24kHz Studio Quality)
    # -------------------------------------------------------------
    {
        "id": "af_bella",
        "name": "Bella (Warm & Melodic)",
        "engine": "kokoro",
        "gender": "Female",
        "language": "English (US)",
        "locale": "en_US",
        "accent": "American",
        "style": "Podcast Host / Commercial",
        "avatar": "🎙️",
        "color": "#ec4899",
        "description": "Warm, expressive, high-energy tone. Ideal for podcast hosting, audio intros, and YouTube voiceovers.",
        "sample_text": "Welcome to the future of offline artificial intelligence audio synthesis, where speed meets studio fidelity.",
        "tags": ["Podcast", "Energetic", "Modern", "Clear"]
    },
    {
        "id": "af_sarah",
        "name": "Sarah (Articulate Narrator)",
        "engine": "kokoro",
        "gender": "Female",
        "language": "English (US)",
        "locale": "en_US",
        "accent": "American",
        "style": "Audiobook / Documentary",
        "avatar": "📖",
        "color": "#8b5cf6",
        "description": "Smooth, articulate, calm tone with exceptional prosody for deep storytelling and long-form narrations.",
        "sample_text": "Deep in the heart of the ancient forest, echoes of forgotten stories whispered through the twilight breeze.",
        "tags": ["Audiobook", "Calm", "Documentary", "Story"]
    },
    {
        "id": "af_nicole",
        "name": "Nicole (Sophisticated & Crisp)",
        "engine": "kokoro",
        "gender": "Female",
        "language": "English (US)",
        "locale": "en_US",
        "accent": "American",
        "style": "News / Corporate",
        "avatar": "💼",
        "color": "#06b6d4",
        "description": "Professional, authoritative, crisp diction suited for tech presentations, corporate overviews, and news.",
        "sample_text": "Today's market report highlights significant breakthroughs in decentralized on-device machine learning inference.",
        "tags": ["Professional", "Corporate", "News", "Crisp"]
    },
    {
        "id": "af_sky",
        "name": "Sky (Dynamic & Casual)",
        "engine": "kokoro",
        "gender": "Female",
        "language": "English (US)",
        "locale": "en_US",
        "accent": "American",
        "style": "Casual / Conversational",
        "avatar": "✨",
        "color": "#38bdf8",
        "description": "Bright, youthful, friendly voice with natural conversational cadence.",
        "sample_text": "Hey everyone! Let's dive right into today's awesome tutorial on building offline voice applications.",
        "tags": ["Casual", "Youthful", "Friendly", "YouTube"]
    },
    {
        "id": "af_heart",
        "name": "Heart (Soft & Empathetic)",
        "engine": "kokoro",
        "gender": "Female",
        "language": "English (US)",
        "locale": "en_US",
        "accent": "American",
        "style": "Meditation / Empathy",
        "avatar": "🌿",
        "color": "#10b981",
        "description": "Gentle, soothing, breathy timbre designed for guided relaxation, wellness apps, and poetry.",
        "sample_text": "Take a slow, deep breath in... and as you exhale, let go of any tension held in your shoulders.",
        "tags": ["Meditation", "Soothing", "Gentle", "Sleep"]
    },
    {
        "id": "am_adam",
        "name": "Adam (Deep & Authoritative)",
        "engine": "kokoro",
        "gender": "Male",
        "language": "English (US)",
        "locale": "en_US",
        "accent": "American",
        "style": "Narrator / Documentary",
        "avatar": "🎬",
        "color": "#f59e0b",
        "description": "Resonant, deep baritone voice with commanding presence. Perfect for film trailers, crime podcasts, and sci-fi.",
        "sample_text": "In a world driven by automated intelligence, one studio unlocked the power of limitless local speech generation.",
        "tags": ["Deep", "Trailer", "Documentary", "Baritone"]
    },
    {
        "id": "am_michael",
        "name": "Michael (Charismatic Host)",
        "engine": "kokoro",
        "gender": "Male",
        "language": "English (US)",
        "locale": "en_US",
        "accent": "American",
        "style": "Podcast / Interviewer",
        "avatar": "🎙️",
        "color": "#ef4444",
        "description": "Warm, engaging, conversational male voice with confident cadence.",
        "sample_text": "Welcome back to Tech Horizon. Today we are joined by lead engineers reshaping local speech synthesis.",
        "tags": ["Podcast", "Engaging", "Interviewer", "Warm"]
    },
    {
        "id": "am_fenrir",
        "name": "Fenrir (Gritty & Dramatic)",
        "engine": "kokoro",
        "gender": "Male",
        "language": "English (US)",
        "locale": "en_US",
        "accent": "American",
        "style": "Gaming / Drama",
        "avatar": "⚔️",
        "color": "#a855f7",
        "description": "Dark, intense, textured vocal timbre for video game character dialogue, fantasy, and dramatic fiction.",
        "sample_text": "The shadows are lengthening. Prepare your defenses before the midnight bell strikes.",
        "tags": ["Gaming", "Dramatic", "Character", "Intense"]
    },
    {
        "id": "am_liam",
        "name": "Liam (Friendly & Tech Casual)",
        "engine": "kokoro",
        "gender": "Male",
        "language": "English (US)",
        "locale": "en_US",
        "accent": "American",
        "style": "Explainer / YouTube",
        "avatar": "💡",
        "color": "#6366f1",
        "description": "Clear, modern, relatable tone ideal for educational videos, software walkthroughs, and casual vlogs.",
        "sample_text": "Let's check out how easily we can configure multi-speaker dialogues in VoxCraft Studio.",
        "tags": ["Explainer", "Modern", "Friendly", "Tutorial"]
    },
    {
        "id": "bf_emma",
        "name": "Emma (Refined British Female)",
        "engine": "kokoro",
        "gender": "Female",
        "language": "English (UK)",
        "locale": "en_GB",
        "accent": "British (RP)",
        "style": "Classic Literature / Audiobooks",
        "avatar": "👑",
        "color": "#f43f5e",
        "description": "Polished, elegant British Received Pronunciation. Ideal for classic audiobooks, period dramas, and luxury branding.",
        "sample_text": "It is a truth universally acknowledged, that a single man in possession of a good fortune, must be in want of a wife.",
        "tags": ["British", "Elegant", "Audiobook", "Refined"]
    },
    {
        "id": "bf_isabella",
        "name": "Isabella (Modern Londoner)",
        "engine": "kokoro",
        "gender": "Female",
        "language": "English (UK)",
        "locale": "en_GB",
        "accent": "British (Modern)",
        "style": "Podcast / Lifestyle",
        "avatar": "☕",
        "color": "#14b8a6",
        "description": "Contemporary British female tone with a warm, lively conversational touch.",
        "sample_text": "Fancy a quick dive into today's most interesting cultural shifts? Grab a cuppa and let's get started.",
        "tags": ["British", "Modern", "Lifestyle", "Warm"]
    },
    {
        "id": "bm_george",
        "name": "George (Distinguished British Male)",
        "engine": "kokoro",
        "gender": "Male",
        "language": "English (UK)",
        "locale": "en_GB",
        "accent": "British (RP)",
        "style": "Historical / Documentary",
        "avatar": "🏛️",
        "color": "#eab308",
        "description": "Distinguished, scholarly British gentleman voice for history documentaries, museum guides, and academia.",
        "sample_text": "Throughout the late nineteenth century, industrial innovation transformed cities across the British Isles.",
        "tags": ["British", "Scholarly", "History", "Documentary"]
    },
    {
        "id": "bm_lewis",
        "name": "Lewis (Warm British Storyteller)",
        "engine": "kokoro",
        "gender": "Male",
        "language": "English (UK)",
        "locale": "en_GB",
        "accent": "British",
        "style": "Audiobook / Fantasy",
        "avatar": "🏰",
        "color": "#84cc16",
        "description": "Rich, comforting British narrator voice for mystery novels, bedtime stories, and historical fiction.",
        "sample_text": "The old clocktower struck midnight as the lone traveler stepped through the castle gates.",
        "tags": ["British", "Storyteller", "Comforting", "Mystery"]
    },
    {
        "id": "jf_tepra",
        "name": "Tepra (Japanese Studio Female)",
        "engine": "kokoro",
        "gender": "Female",
        "language": "Japanese",
        "locale": "ja_JP",
        "accent": "Standard Japanese",
        "style": "Anime / Assistant",
        "avatar": "🌸",
        "color": "#fb7185",
        "description": "Clear and polite Japanese voice suitable for dialogue, anime character lines, and assistant announcements.",
        "sample_text": "ローカル環境で動作する高品質な音声合成スタジオへようこそ。",
        "tags": ["Japanese", "Anime", "Clear", "Multi-lingual"]
    },
    {
        "id": "zf_xiaoyan",
        "name": "Xiaoyan (Mandarin Studio Female)",
        "engine": "kokoro",
        "gender": "Female",
        "language": "Mandarin Chinese",
        "locale": "zh_CN",
        "accent": "Standard Mandarin",
        "style": "Broadcast / Narration",
        "avatar": "🏮",
        "color": "#f87171",
        "description": "Standard Mandarin broadcast voice with crisp tones and natural rhythm.",
        "sample_text": "欢迎使用本地离线语音合成工作室，体验极致音质与超快速度。",
        "tags": ["Mandarin", "Broadcast", "Fluent", "Multi-lingual"]
    },
    {
        "id": "ef_dora",
        "name": "Dora (Spanish Studio Female)",
        "engine": "kokoro",
        "gender": "Female",
        "language": "Spanish",
        "locale": "es_ES",
        "accent": "Castilian Spanish",
        "style": "Podcast / Narration",
        "avatar": "💃",
        "color": "#fb923c",
        "description": "Passionate and fluid Castilian Spanish voice.",
        "sample_text": "Bienvenidos al estudio de síntesis de voz sin conexión más avanzado del mundo.",
        "tags": ["Spanish", "Fluid", "Warm", "Multi-lingual"]
    },
    {
        "id": "ff_siwis",
        "name": "Siwis (French Studio Female)",
        "engine": "kokoro",
        "gender": "Female",
        "language": "French",
        "locale": "fr_FR",
        "accent": "Standard French",
        "style": "Documentary / Luxury",
        "avatar": "🥐",
        "color": "#c084fc",
        "description": "Melodic, elegant French voice with flawless Parisian articulation.",
        "sample_text": "Bienvenue dans le studio de synthèse vocale locale hors-ligne de nouvelle génération.",
        "tags": ["French", "Elegant", "Parisian", "Multi-lingual"]
    },

    # -------------------------------------------------------------
    # Piper Neural Voices (Lightweight, Multi-Lingual, Fast CPU)
    # -------------------------------------------------------------
    {
        "id": "piper-en_US-libritts_r-medium",
        "name": "Piper LibriTTS-R (Studio US)",
        "engine": "piper",
        "gender": "Neutral / Multi",
        "language": "English (US)",
        "locale": "en_US",
        "accent": "American",
        "style": "Multi-Speaker Studio Pack",
        "avatar": "🎧",
        "color": "#0ea5e9",
        "description": "Studio trained multi-speaker model containing hundreds of distinct speaker timbres.",
        "sample_text": "Piper provides lightning fast speech generation with negligible CPU footprint.",
        "tags": ["Fast", "Multi-Speaker", "Clean", "Lightweight"]
    },
    {
        "id": "piper-en_US-lessac-medium",
        "name": "Piper Lessac (Narrator Female)",
        "engine": "piper",
        "gender": "Female",
        "language": "English (US)",
        "locale": "en_US",
        "accent": "American",
        "style": "Audiobook Narration",
        "avatar": "📚",
        "color": "#a78bfa",
        "description": "Consistently praised for clear, balanced narration in educational material and e-learning.",
        "sample_text": "Chapter One: The fundamentals of acoustic modeling and neural waveform vocoding.",
        "tags": ["Narrator", "Crisp", "Educational", "Audiobook"]
    },
    {
        "id": "piper-en_GB-alan-medium",
        "name": "Piper Alan (British Male)",
        "engine": "piper",
        "gender": "Male",
        "language": "English (UK)",
        "locale": "en_GB",
        "accent": "British",
        "style": "Conversational / Audio",
        "avatar": "🎩",
        "color": "#eab308",
        "description": "Warm, natural English gentleman voice for general reading and assistant responses.",
        "sample_text": "I say, having complete speech synthesis directly on your local device is rather brilliant.",
        "tags": ["British", "Natural", "Friendly", "Fast"]
    },
    {
        "id": "piper-es_ES-davefx-medium",
        "name": "Piper Davefx (Spanish Male)",
        "engine": "piper",
        "gender": "Male",
        "language": "Spanish (ES)",
        "locale": "es_ES",
        "accent": "European Spanish",
        "style": "Tutorials / Podcast",
        "avatar": "🇪🇸",
        "color": "#f97316",
        "description": "Clear Spanish male voice optimized for rapid synthesis.",
        "sample_text": "Generación de voz ultrarrápida y totalmente privada sin conexión a internet.",
        "tags": ["Spanish", "Fast", "Tutorials", "Clear"]
    },
    {
        "id": "piper-fr_FR-siwis-medium",
        "name": "Piper Siwis (French Female)",
        "engine": "piper",
        "gender": "Female",
        "language": "French (FR)",
        "locale": "fr_FR",
        "accent": "French",
        "style": "Assistant / Narration",
        "avatar": "🇫🇷",
        "color": "#d946ef",
        "description": "Ultra-lightweight French voice for rapid audio generation.",
        "sample_text": "Une synthèse vocale rapide et efficace directement sur votre machine locale.",
        "tags": ["French", "Fast", "Lightweight", "Clear"]
    },
    {
        "id": "piper-de_DE-eva_k-medium",
        "name": "Piper Eva K (German Female)",
        "engine": "piper",
        "gender": "Female",
        "language": "German (DE)",
        "locale": "de_DE",
        "accent": "Standard German",
        "style": "Audiobook / Assistant",
        "avatar": "🇩🇪",
        "color": "#22c55e",
        "description": "Precise German articulation with natural sentence rhythm.",
        "sample_text": "Willkommen bei VoxCraft Studio. Ihre lokale Plattform für künstliche Sprachausgabe.",
        "tags": ["German", "Clear", "Precise", "Fast"]
    },

    # -------------------------------------------------------------
    # F5-TTS Zero-Shot Voice Cloning & Custom Persona Models
    # -------------------------------------------------------------
    {
        "id": "f5_clone_custom",
        "name": "F5-TTS Instant Voice Clone (Upload / Mic)",
        "engine": "f5_tts",
        "gender": "Custom / Dynamic",
        "language": "Multi-Lingual (Cross-Lingual)",
        "locale": "multi",
        "accent": "Matches Reference Audio",
        "style": "Zero-Shot Voice Cloning",
        "avatar": "🧬",
        "color": "#ec4899",
        "description": "Clone any voice with only 5-15 seconds of audio reference! Emulates emotion, tone, and vocal characteristics.",
        "sample_text": "This voice was synthesized through state-of-the-art flow matching zero-shot neural cloning.",
        "tags": ["Voice Cloning", "Zero-Shot", "Custom", "High Fidelity"]
    },
    {
        "id": "f5_preset_studio_host",
        "name": "F5-TTS Preset: Studio Radio Host",
        "engine": "f5_tts",
        "gender": "Male",
        "language": "English (US)",
        "locale": "en_US",
        "accent": "Broadcast American",
        "style": "Dynamic Radio Host",
        "avatar": "📻",
        "color": "#6366f1",
        "description": "High-fidelity broadcast voice cloned from professional studio master recordings.",
        "sample_text": "Broadcasting live across all frequencies, you're tuned into the premier AI audio network.",
        "tags": ["Broadcast", "Radio", "Cloned", "Punchy"]
    },
    {
        "id": "f5_preset_anime_narrator",
        "name": "F5-TTS Preset: Anime Storyteller",
        "engine": "f5_tts",
        "gender": "Female",
        "language": "English / Japanese",
        "locale": "multi",
        "accent": "Expressive / Melodic",
        "style": "Character / Dramatic",
        "avatar": "⭐",
        "color": "#f43f5e",
        "description": "Highly emotional and dynamic character voice suitable for gaming cutscenes and animation.",
        "sample_text": "Even when the skies turned to ash, the spark of courage never faded from our hearts.",
        "tags": ["Character", "Anime", "Emotional", "Cloned"]
    }
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
        if language and language != "all" and language.lower() not in v["language"].lower():
            continue
        if query:
            match = (
                query in v["name"].lower() or
                query in v["description"].lower() or
                query in v["language"].lower() or
                query in v["style"].lower() or
                any(query in tag.lower() for tag in v.get("tags", []))
            )
            if not match:
                continue
        results.append(v)
    return results
