"""equivalence_classes -- dynamic partitioning of a language's holder pool and
non-holder sets from the lowerer's own gate predicates (zero by-hand classes).

Plan: `.../node_0_0_0_0_2_1_1_2_equivalence_classes/`.
"""

from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Dict, FrozenSet, Tuple

from . import accepted_signatures

DEFAULT_FACTS_PATH = (
    Path(__file__).resolve().parent.parent.parent
    / "lang_models"
    / "gnu_c"
    / "equivalence_classes"
    / "holder_facts.json"
)

TYPE_ONLY_HOLDERS = ("fntype", "void", "struct I")


def load_held_facts(path: str = "") -> Dict[str, accepted_signatures.Held]:
    """Load `Held` facts extracted from the lowerer's AST (`holder_facts.json`)."""
    target = path or os.environ.get("PSEUDOIR_HOLDER_FACTS") or str(DEFAULT_FACTS_PATH)
    return accepted_signatures.facts_read(target)


def holder_predicate_signature(held: accepted_signatures.Held) -> Tuple:
    """The complete lowerer-predicate signature of one holder `held`: its
    answers on every Clang `Type::is*Type()` and `llvm::Type::is*Ty()` gate
    predicate, its structural kind/sign/size/qualifiers, and its `.inner`
    pointee/element predicate answers."""
    if held is None:
        return ("none",)
    outer_answers = accepted_signatures.type_answers(held)
    outer_items = tuple(sorted(outer_answers.items()))
    inner_items = ()
    if held.inner is not None:
        inner_answers = accepted_signatures.type_answers(held.inner)
        inner_items = (
            held.inner.kind,
            held.inner.signed,
            held.inner.size,
            held.inner.const,
            held.inner.volatile,
            tuple(sorted(inner_answers.items())),
        )
    return (
        held.kind,
        held.signed,
        held.size,
        held.const,
        held.volatile,
        held.bits,
        held.count,
        outer_items,
        inner_items,
    )


def compute_holder_sets(held_facts: dict = None) -> Dict[str, FrozenSet[str]]:
    """Every holder-set S_p = {h | p(h) = True} defined by the lowerer's
    `Type::is*Type()` and `llvm::Type::is*Ty()` gate predicates, for both
    outer holders (`isIntegerType`) and `.inner` holders (`inner.isIntegerType`)."""
    if held_facts is None:
        held_facts = load_held_facts()
    sets: Dict[str, set] = {}
    for spelling, held in held_facts.items():
        if held is None:
            continue
        for pred, val in accepted_signatures.type_answers(held).items():
            if val is True:
                sets.setdefault(pred, set()).add(spelling)
        if held.inner is not None:
            for pred, val in accepted_signatures.type_answers(held.inner).items():
                if val is True:
                    sets.setdefault(f"inner.{pred}", set()).add(spelling)
    return {k: frozenset(v) for k, v in sets.items()}


def _representative_sort_key(spelling: str, held: accepted_signatures.Held) -> Tuple:
    """Deterministic ordering within one lowerer-defined equivalence class:
    non-pointer before pointer, unqualified before qualified, fewest tokens,
    shortest spelling, alphabetical."""
    is_ptr = 1 if "*" in spelling else 0
    is_qual = 1 if (held and (held.const or held.volatile)) else 0
    is_ext = 1 if spelling.startswith("_") else 0
    return (is_ptr, is_qual, is_ext, len(spelling.split()), len(spelling), spelling)


def compute_holder_equivalence_classes(held_facts: dict = None) -> Dict[str, Tuple[str, ...]]:
    """Partition the lowerer's holder pool dynamically by `holder_predicate_signature`.
    Returns {canonical_representative: (all_holders_in_class, ...)}."""
    if held_facts is None:
        held_facts = load_held_facts()
    by_sig: Dict[Tuple, list] = {}
    for spelling, held in held_facts.items():
        if held is None:
            continue
        if held.kind in ("void", "function", "builtin_other") and spelling not in TYPE_ONLY_HOLDERS:
            continue
        sig = holder_predicate_signature(held)
        by_sig.setdefault(sig, []).append(spelling)

    classes: Dict[str, Tuple[str, ...]] = {}
    for sig, members in by_sig.items():
        members_sorted = sorted(members, key=lambda s: _representative_sort_key(s, held_facts.get(s)))
        rep = members_sorted[0]
        classes[rep] = tuple(members_sorted)
    return dict(sorted(classes.items(), key=lambda kv: _representative_sort_key(kv[0], held_facts.get(kv[0]))))


def select_holder_representatives(held_facts: dict = None) -> Tuple[str, ...]:
    """Select one canonical element from each lowerer-defined holder equivalence class."""
    classes = compute_holder_equivalence_classes(held_facts)
    return tuple(classes.keys())


def compute_non_holder_sets() -> Dict[str, Dict[str, FrozenSet[str]]]:
    """Non-holder sets checked by Clang gates (derived from Specifiers.h, Expr.h,
    CGValue.h, LangOptions.def, Sanitizers.def)."""
    return {
        "value_category_sets": {
            "isGLValue": frozenset({"place", "parenthesis"}),
            "isRValue": frozenset({"constant 0", "constant 1", "constant 2", "constant 3", "constant 4", "constant 5", "literal"}),
        },
        "constant_value_sets": {
            "ConstantInt": frozenset({"constant 0", "constant 1", "constant 2", "constant 3", "constant 4", "constant 5", "literal"}),
            "non_constant": frozenset({"place", "parenthesis"}),
            "case_0": frozenset({"constant 0"}),
            "case_1": frozenset({"constant 1"}),
            "case_2": frozenset({"constant 2"}),
            "case_3": frozenset({"constant 3"}),
            "case_4": frozenset({"constant 4"}),
            "case_5": frozenset({"constant 5"}),
        },
        "place_sets": {
            "isSimple": frozenset({"field"}),
            "isBitField": frozenset({"bit-field", "signed bit-field"}),
            "isVectorElt": frozenset({"vector element"}),
            "isExtVectorElt": frozenset({"ext vector element"}),
            "isMatrixElt": frozenset({"matrix element"}),
            "isGlobalReg": frozenset({"global register"}),
        },
        "scope_and_option_sets": {
            "loop_scope": frozenset({"BreakContinueStack"}),
            "switch_scope": frozenset({"SwitchInsn", "BreakContinueStack"}),
            "label_scope": frozenset({"AddrLabelMap"}),
        },
    }


EQUIVALENCE_CLASS_HOLDERS = select_holder_representatives()

__all__ = [
    "EQUIVALENCE_CLASS_HOLDERS",
    "TYPE_ONLY_HOLDERS",
    "compute_holder_equivalence_classes",
    "compute_holder_sets",
    "compute_non_holder_sets",
    "holder_predicate_signature",
    "load_held_facts",
    "select_holder_representatives",
]
