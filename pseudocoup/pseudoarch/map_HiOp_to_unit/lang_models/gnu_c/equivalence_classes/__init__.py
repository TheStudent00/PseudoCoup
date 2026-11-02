"""equivalence_classes -- GNU C 180-holder fact table and 42+3 gate-predicate equivalence classes."""
import json
from pathlib import Path
from ....model_lang_parts.HiOps.branch_trees import (
    EQUIVALENCE_CLASS_HOLDERS,
    TYPE_ONLY_HOLDERS,
)
from ....model_lang_parts.HiOps.enumerate_branch_candidates import (
    HOLDER_PREAMBLE,
)

HOLDER_FACTS_PATH = Path(__file__).with_name("holder_facts.json")

def load_holder_facts() -> dict:
    return json.loads(HOLDER_FACTS_PATH.read_text())
