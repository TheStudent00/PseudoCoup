"""entry_context -- structured `state_info[0]` (`EntryContext`) token descriptor
inferred from `state_info` and the selection of elements from lowerer-defined
holder-sets and non-holder sets.

Plan: `.../node_0_0_0_0_2_1_3_context/node_0_0_0_0_2_1_3_0_entry_context/`.
"""

import functools
import json
import os
import re
import sys
from typing import Dict, List, NamedTuple, Optional, Tuple

from ..holders.equivalence_classes import (
    TYPE_ONLY_HOLDERS,
    load_held_facts,
    select_holder_representatives,
)

KEY = "k"
PLACEHOLDER_RE = re.compile(r"\b([a-hTUVWmn])\b")

HQ_ROOT = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "..", "..", ".."))
PLACES_JSON = os.path.join(HQ_ROOT, "Research", "extract_lang_vocabulary", "dependent_HiOp_reader", "out", "places.json")
BODIES_JSON = os.path.join(HQ_ROOT, "Research", "extract_lang_vocabulary", "dependent_HiOp_reader", "out", "bodies.json")
CONFIGS_JSON = os.path.join(HQ_ROOT, "Research", "extract_lang_vocabulary", "HiOp_configuration_solver", "out", "configurations.json")


class Operator(NamedTuple):
    """The HiOp: the lowerer's identifier for it, its spelling, and its parts."""

    name: str
    spelling: str
    operands: tuple
    lang: str = "c"
    source: str = ""


class PartState0(NamedTuple):
    """One operand part's entry state in `state_info[0]`, selected from the
    surviving holder-set and non-holder sets along a path."""

    slot: str
    holder: str
    place: str = "field"
    value_category: str = "lvalue"
    constant_value: Optional[str] = None


class StateInfo0(NamedTuple):
    """Structured `state_info[0]` token descriptor supplied to `hijack_lowerer`
    at the HiOp entry point."""

    lang: str
    operator: Operator
    parts: Tuple[PartState0, ...]
    options: Tuple[str, ...] = ()
    target: str = "riscv64"
    enclosing_scope: Optional[str] = None
    path_signature: str = ""


EntryContext = StateInfo0


PLACE_ORDER = (
    "field",
    "bit-field",
    "signed bit-field",
    "vector element",
    "ext vector element",
    "matrix element",
    "global register",
)

CONSTANT_MAP = {
    "constant 0": "0",
    "constant 1": "1",
    "constant 2": "2",
    "constant 3": "3",
    "constant 4": "4",
    "constant 5": "5",
    "literal": "1",
}


@functools.lru_cache(maxsize=1)
def load_hiop_relations() -> Dict[str, dict]:
    """Load the lowerer-derived HiOp relations (bodies, constants, function
    return context, jumps, and dependent scope/stack/label requirements) from
    dependent_HiOp_reader (`bodies.json`, `places.json`) and
    HiOp_configuration_solver (`configurations.json`)."""
    bundled_gz = os.path.join(os.path.dirname(os.path.abspath(__file__)), "hiop_relations.json.gz")
    if not (os.path.isfile(CONFIGS_JSON) and os.path.isfile(BODIES_JSON) and os.path.isfile(PLACES_JSON)):
        if os.path.isfile(bundled_gz):
            import gzip
            with gzip.open(bundled_gz, "rt", encoding="utf-8") as f:
                return json.load(f)
        return {}
    with open(CONFIGS_JSON, encoding="utf-8") as f:
        cfg = json.load(f)
    with open(BODIES_JSON, encoding="utf-8") as f:
        bodies_doc = json.load(f)
    with open(PLACES_JSON, encoding="utf-8") as f:
        places_doc = json.load(f)

    bodies_by_tpl = {
        item["template"]: item
        for item in bodies_doc["by_file"]["kinds_forms.json"]["listings"]
    }
    by_listing: Dict[str, dict] = {}
    for l in cfg["listings"]:
        if l.get("role") == "declaration":
            continue
        tpl = l["listing"]
        b_info = bodies_by_tpl.get(tpl, {})
        body_slots = set((l.get("configuration") or {}).get("bodies") or [])
        for p in b_info.get("parts", []):
            if p.get("place") == "before":
                body_slots.add(p["letter"])
        const_slots = set()
        if l.get("fill") == "constant":
            for comp in l.get("components", []):
                const_slots.update(comp.get("takes", []))
        for ph, ov in (l.get("fill_overrides") or {}).items():
            if ov.get("form") == "constant":
                const_slots.add(ph)
        alone = (l.get("signal_2") or {}).get("alone") or {}
        fn_ctx = alone.get("context", "void f(void)")
        never_bodies = tuple(
            p["letter"]
            for p in alone.get("parts", [])
            if p.get("reading") == "never" and p["letter"] in body_slots
        )
        p_info = places_doc["by_listing"].get(tpl, {})
        asks = ((p_info.get("asks") or {}).get("asks") or {})
        ask_target = asks.get("getter") or asks.get("stack")
        needs_fn = tuple(((p_info.get("needs_in_the_same_function") or {}).get("kinds") or []))
        by_listing[tpl] = {
            "kind": l["kind"].split(".")[0],
            "is_statement": bool(l.get("is_statement")),
            "bodies": tuple(sorted(body_slots)),
            "constants": tuple(sorted(const_slots)),
            "function_context": fn_ctx,
            "never_bodies": never_bodies,
            "asks": ask_target,
            "needs_in_function": needs_fn,
        }
    return by_listing


def enclosing_scope_for_operator(operator: Operator) -> Optional[str]:
    """Infer from the lowerer-derived `places.json` / `configurations.json`
    relations what scope/stack/label token `state_info[0]` must carry."""
    rels = load_hiop_relations()
    info = rels.get(operator.spelling, {})
    asks = info.get("asks")
    needs_fn = info.get("needs_in_function", ())
    if asks == "getBreakParent":
        return "break"
    if asks == "getContinueParent":
        return "continue"
    if asks == "SwitchStack":
        return "switch"
    if "AddrLabelExpr" in needs_fn:
        return "addrlabel"
    if "LabelStmt" in needs_fn:
        return "label"
    return None


def select_part_state_0(
    slot: str,
    part_constraint,
    representatives: Tuple[str, ...],
    is_type_slot: bool = False,
) -> Optional[PartState0]:
    """Select one element from each surviving set in `part_constraint` (`holders`,
    `places`, `value_forms`) using the lowerer-derived equivalence classes."""
    chosen_holder = None
    for rep in representatives:
        if rep not in part_constraint.holders:
            continue
        if not is_type_slot and rep in TYPE_ONLY_HOLDERS:
            continue
        chosen_holder = rep
        break
    if chosen_holder is None and part_constraint.holders:
        candidates = sorted(
            h for h in part_constraint.holders
            if is_type_slot or h not in TYPE_ONLY_HOLDERS
        )
        if candidates:
            chosen_holder = candidates[0]
    if chosen_holder is None:
        return None

    if is_type_slot:
        return PartState0(slot=slot, holder=chosen_holder, place="field", value_category="lvalue", constant_value=None)

    chosen_place = "field"
    for p in PLACE_ORDER:
        if p in part_constraint.places:
            chosen_place = p
            break

    # Only select a constant from constant_value_sets when runtime 'place' is excluded by a gate
    if "place" in part_constraint.value_forms:
        return PartState0(slot=slot, holder=chosen_holder, place=chosen_place, value_category="lvalue", constant_value=None)
    if "parenthesis" in part_constraint.value_forms:
        return PartState0(slot=slot, holder=chosen_holder, place=chosen_place, value_category="lvalue", constant_value=None)

    for form_name, const_str in CONSTANT_MAP.items():
        if form_name in part_constraint.value_forms:
            return PartState0(slot=slot, holder=chosen_holder, place="field", value_category="prvalue", constant_value=const_str)

    return PartState0(slot=slot, holder=chosen_holder, place=chosen_place, value_category="lvalue", constant_value=None)


def infer_state_info_0_from_constraint(
    operator: Operator,
    constraint,
    held_facts: dict = None,
    path_signature: str = "",
) -> List[StateInfo0]:
    """Infer structured `StateInfo0` (`state_info[0]`) descriptors from a path's
    intersected `AbstractConstraint` by selecting elements from the lowerer-derived
    holder equivalence classes and non-holder sets."""
    if held_facts is None:
        held_facts = load_held_facts()
    representatives = select_holder_representatives(held_facts)
    slots = list(operator.operands) if operator.operands else PLACEHOLDER_RE.findall(operator.spelling)
    part_count = len(constraint.parts)
    while len(slots) < part_count:
        slots.append(chr(ord("a") + len(slots)))

    base_parts = []
    for i in range(part_count):
        slot = slots[i]
        is_type = slot in ("T", "U", "V", "W")
        ps = select_part_state_0(slot, constraint.parts[i], representatives, is_type_slot=is_type)
        if ps is None:
            return []
        base_parts.append(ps)

    options = tuple(sorted(opt for opt in constraint.options if not opt.startswith("not ")))
    target = "riscv64"
    for t in ("riscv64", "x86-64", "aarch64"):
        if t in constraint.targets:
            target = t.replace("-", "_")
            break
    scope = enclosing_scope_for_operator(operator)

    results = [
        StateInfo0(
            lang=getattr(operator, "lang", "c") or "c",
            operator=operator,
            parts=tuple(base_parts),
            options=options,
            target=target,
            enclosing_scope=scope,
            path_signature=path_signature,
        )
    ]

    # When a part's holder-set was narrowed by a gate, also emit up to 3 distinct
    # lowerer-derived equivalence-class representatives that survive the gate
    total_holders = sum(1 for v in held_facts.values() if v is not None)
    for i in range(part_count):
        slot = slots[i]
        is_type = slot in ("T", "U", "V", "W")
        if len(constraint.parts[i].holders) >= total_holders - 5:
            continue
        added = 0
        for rep in representatives:
            if rep not in constraint.parts[i].holders or rep == base_parts[i].holder:
                continue
            if not is_type and rep in TYPE_ONLY_HOLDERS:
                continue
            alt_parts = list(base_parts)
            alt_parts[i] = base_parts[i]._replace(holder=rep)
            results.append(
                StateInfo0(
                    lang=getattr(operator, "lang", "c") or "c",
                    operator=operator,
                    parts=tuple(alt_parts),
                    options=options,
                    target=target,
                    enclosing_scope=scope,
                    path_signature=path_signature,
                )
            )
            added += 1
            if added >= 3:
                break
    return results


class Setup(NamedTuple):
    command: str
    preamble: tuple = ()


class Context(NamedTuple):
    operator: Operator
    holders: tuple
    setup: Setup
    program: str = ""


def our_setup() -> Setup:
    return Setup("clang -x c --target=riscv64-linux-gnu -std=gnu17 -O0 -g -c")


def setup_with(options: str, preamble: tuple = ()) -> Setup:
    base = our_setup()
    return Setup((base.command + " " + options).strip(), preamble)


def command_for(context: Context, clang: str, source: str, output: str) -> list:
    words = context.setup.command.split()
    words[0] = clang
    return words + ["-o", output, source]


def standard_source(context: Context) -> str:
    if context.program:
        return context.program
    from ...lang_models.gnu_c.entry_points import synthesize_entry_program
    parts = tuple(
        PartState0(slot=s, holder=h)
        for s, h in zip(context.operator.operands, context.holders)
    )
    s0 = StateInfo0("c", context.operator, parts)
    return synthesize_entry_program(s0)


HERE = os.path.dirname(os.path.abspath(__file__))
PROJECTS = os.path.normpath(os.path.join(HERE, "..", "..", "..", ".."))
if PROJECTS not in sys.path:
    sys.path.insert(0, PROJECTS)
