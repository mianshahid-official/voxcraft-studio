import sys
import os
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent.resolve()))
import logging

logging.basicConfig(level=logging.INFO)

print("--- Testing Piper Engine ---", flush=True)
from app.engines.piper.engine import PiperEngine

pe = PiperEngine()
print("Piper is_installed:", pe.is_installed(), flush=True)
initialized = pe.initialize()
print("Piper initialize():", initialized, flush=True)
print("Piper loaded voices:", list(pe.voices_cache.keys()), flush=True)

test_voices = [
    "piper-en_US-lessac-medium",
    "piper-en_GB-alan-medium",
    "piper-de_DE-thorsten-medium",
    "piper-es_ES-davefx-medium",
    "piper-fr_FR-siwis-medium"
]

text = "VoxCraft Studio brings high quality speech to your computer."

for v in test_voices:
    try:
        audio, sr = pe.generate(text, voice=v)
        dur = len(audio) / sr if sr else 0
        print(f"SUCCESS {v}: duration={dur:.2f}s, sample_rate={sr}, non_zero={(audio != 0).sum()}", flush=True)
    except Exception as e:
        print(f"ERROR {v}: {e}", flush=True)

print("--- Testing Kokoro Engine ---", flush=True)
from app.engines.kokoro.engine import KokoroEngine

ke = KokoroEngine()
print("Kokoro is_installed:", ke.is_installed(), flush=True)
initialized = ke.initialize()
print("Kokoro initialize():", initialized, flush=True)

kokoro_test_voices = ["af_bella", "am_adam", "bf_emma", "ef_dora"]
for v in kokoro_test_voices:
    try:
        audio, sr = ke.generate(text, voice=v)
        dur = len(audio) / sr if sr else 0
        print(f"SUCCESS {v}: duration={dur:.2f}s, sample_rate={sr}, non_zero={(audio != 0).sum()}", flush=True)
    except Exception as e:
        print(f"ERROR {v}: {e}", flush=True)
