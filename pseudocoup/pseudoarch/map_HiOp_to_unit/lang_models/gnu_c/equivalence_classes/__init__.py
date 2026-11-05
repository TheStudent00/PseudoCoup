"""equivalence_classes -- GNU C lowerer-derived holder-sets, non-holder sets,
and dynamically partitioned gate-predicate equivalence classes."""

import json
from pathlib import Path

from ....model_lang_parts.holders.equivalence_classes import (
    EQUIVALENCE_CLASS_HOLDERS,
    TYPE_ONLY_HOLDERS,
    compute_holder_equivalence_classes,
    compute_holder_sets,
    compute_non_holder_sets,
    holder_predicate_signature,
    load_held_facts,
    select_holder_representatives,
)

HOLDER_FACTS_PATH = Path(__file__).with_name("holder_facts.json")


def load_holder_facts() -> dict:
    return json.loads(HOLDER_FACTS_PATH.read_text())


__all__ = [
    "EQUIVALENCE_CLASS_HOLDERS",
    "HOLDER_FACTS_PATH",
    "TYPE_ONLY_HOLDERS",
    "compute_holder_equivalence_classes",
    "compute_holder_sets",
    "compute_non_holder_sets",
    "holder_predicate_signature",
    "load_held_facts",
    "load_holder_facts",
    "select_holder_representatives",
]
