"""java -- Java language model (Language #3 of remaining queue)."""
import json
from pathlib import Path

CONSOLIDATED_VOCABULARY_PATH = Path(__file__).with_name("consolidated_java_vocabulary.json")
CONSOLIDATED_VOCABULARY_JSONL_GZ = Path(__file__).with_name("consolidated_java_vocabulary.jsonl.gz")


def load_consolidated_vocabulary() -> dict:
    return json.loads(CONSOLIDATED_VOCABULARY_PATH.read_text(encoding="utf-8"))
