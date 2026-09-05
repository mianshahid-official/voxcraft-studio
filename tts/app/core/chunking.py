"""
TTS Studio - Intelligent Long-Form Text Chunking & Scheduler
Segments long documents into natural, retryable synthesis chunks.
"""
import re
import hashlib
from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional


@dataclass
class TextChunk:
    chunk_id: str
    index: int
    text: str
    word_count: int
    char_count: int
    pause_after: float = 0.5
    chapter: Optional[str] = None
    status: str = "pending"  # pending, completed, failed
    audio_path: Optional[str] = None
    duration_sec: float = 0.0
    error: Optional[str] = None

    @property
    def content_hash(self) -> str:
        return hashlib.sha256(self.text.strip().encode('utf-8')).hexdigest()[:12]


class TextChunker:
    """Splits long text documents into natural sentence/paragraph chunks for robust batch synthesis."""

    @staticmethod
    def split_into_sentences(text: str) -> List[str]:
        """Splits paragraph text by punctuation boundaries while respecting abbreviations."""
        # Simple robust sentence boundary regex
        raw_sentences = re.split(r'(?<=[.!?…])\s+(?=[A-Z0-9"\'\(\[\¿\¡])', text.strip())
        return [s.strip() for s in raw_sentences if s.strip()]

    @classmethod
    def chunk_document(cls, full_text: str, max_words_per_chunk: int = 60, default_pause: float = 0.5) -> List[TextChunk]:
        """
        Segments long-form document into coherent, bounded TextChunks.
        """
        if not full_text or not full_text.strip():
            return []

        paragraphs = full_text.strip().split("\n")
        chunks: List[TextChunk] = []
        chunk_idx = 1
        current_chapter = "Chapter 1"

        current_sentences = []
        current_words = 0

        for p in paragraphs:
            clean_p = p.strip()
            if not clean_p:
                continue

            # Chapter heading detection
            if re.match(r'^(chapter\s+\d+|act\s+\d+|part\s+\d+|section\s+\d+|#+)', clean_p, re.IGNORECASE):
                current_chapter = clean_p.lstrip("#").strip()
                continue

            sentences = cls.split_into_sentences(clean_p)
            for s in sentences:
                words_in_s = len(s.split())

                if current_words + words_in_s > max_words_per_chunk and current_sentences:
                    # Flush current chunk
                    combined_text = " ".join(current_sentences)
                    c_id = f"chunk_{chunk_idx:04d}"
                    chunks.append(TextChunk(
                        chunk_id=c_id,
                        index=chunk_idx,
                        text=combined_text,
                        word_count=len(combined_text.split()),
                        char_count=len(combined_text),
                        pause_after=default_pause,
                        chapter=current_chapter
                    ))
                    chunk_idx += 1
                    current_sentences = []
                    current_words = 0

                current_sentences.append(s)
                current_words += words_in_s

            # Paragraph boundary flush
            if current_sentences:
                combined_text = " ".join(current_sentences)
                c_id = f"chunk_{chunk_idx:04d}"
                chunks.append(TextChunk(
                    chunk_id=c_id,
                    index=chunk_idx,
                    text=combined_text,
                    word_count=len(combined_text.split()),
                    char_count=len(combined_text),
                    pause_after=default_pause * 1.5,
                    chapter=current_chapter
                ))
                chunk_idx += 1
                current_sentences = []
                current_words = 0

        return chunks
