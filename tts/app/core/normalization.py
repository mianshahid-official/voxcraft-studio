"""
TTS Studio - Text Preprocessing & Pronunciation Dictionary
Handles Unicode normalization, pronunciation replacements, and custom pause tags.
"""
import re
from typing import Dict, List, Tuple, Optional


class TextNormalizer:
    """Cleans and standardizes input text before feeding into TTS neural models."""

    @staticmethod
    def clean_unicode(text: str) -> str:
        """Replace typographic ligatures, smart quotes, and strange dashes."""
        replacements = {
            '“': '"', '”': '"', '‘': "'", '’': "'",
            '—': ', ', '–': ', ', '…': '...',
            '«': '"', '»': '"', '\u200b': '', '\xa0': ' '
        }
        for k, v in replacements.items():
            text = text.replace(k, v)
        # Collapse multiple spaces
        text = re.sub(r'[ \t]+', ' ', text)
        return text.strip()

    @staticmethod
    def apply_pronunciation_dictionary(text: str, custom_dict: Optional[Dict[str, str]] = None) -> str:
        """Replace specific terms/acronyms with phonetic pronunciations."""
        if not custom_dict:
            return text

        processed = text
        for term, replacement in custom_dict.items():
            pattern = re.compile(rf'\b{re.escape(term)}\b', re.IGNORECASE)
            processed = pattern.sub(replacement, processed)
        return processed

    @staticmethod
    def parse_pause_tags(text: str) -> List[Tuple[str, float]]:
        """
        Parses inline pause directives such as '[PAUSE 1.5]' into (text_segment, pause_seconds).
        Example: "Hello world [PAUSE 1.0] how are you?" -> [("Hello world", 1.0), ("how are you?", 0.0)]
        """
        pause_pattern = re.compile(r'\[(?:PAUSE|BREAK)\s*([0-9\.]*)\]', re.IGNORECASE)
        segments = []
        last_pos = 0

        for match in pause_pattern.finditer(text):
            seg_text = text[last_pos:match.start()].strip()
            pause_val = float(match.group(1)) if match.group(1) else 1.0
            if seg_text:
                segments.append((seg_text, pause_val))
            last_pos = match.end()

        remaining = text[last_pos:].strip()
        if remaining:
            segments.append((remaining, 0.0))

        return segments if segments else [(text.strip(), 0.0)]

    @classmethod
    def preprocess(cls, text: str, custom_dict: Optional[Dict[str, str]] = None) -> str:
        """Full text normalization pipeline."""
        t = cls.clean_unicode(text)
        t = cls.apply_pronunciation_dictionary(t, custom_dict)
        return t
