"""unreached_paths -- the GNU C unreached_paths record (0 open branches across all 1,806 HiOps)
and consolidated GNU C vocabulary index.
"""
import json
from pathlib import Path

UNREACHED_PATHS_PATH = Path(__file__).with_name("unreached_paths.json")
CONSOLIDATED_VOCABULARY_PATH = Path(__file__).with_name("consolidated_gnu_c_vocabulary.json")


def load_unreached_paths() -> dict:
    return json.loads(UNREACHED_PATHS_PATH.read_text(encoding="utf-8"))


def load_consolidated_vocabulary() -> dict:
    return json.loads(CONSOLIDATED_VOCABULARY_PATH.read_text(encoding="utf-8"))
