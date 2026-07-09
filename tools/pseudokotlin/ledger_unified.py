"""ledger_unified.py -- Phase 4: ONE ledger for the WHOLE app, keyed by id (provisional name).

Collapses the three existing, differently-keyed ledgers into a single id-keyed ledger, one
record per node, covering the whole app:

  ledger.py     -- structural/connective ledger for ENGINE+MODEL frames (module/class/
                   function/method): each object's (name, 1-degree connections). Keyed by
                   NAME (per-engine, exec+introspect on the Python side).
  ui_ledger.py  -- UI bucket, Kotlin/Compose side: each composable node's layout intent
                   (size/place, abs vs rel), read statically from the Modifier chain. Keyed
                   by a content-anchored branch-path (render_node/_segment).
  kit_ledger.py -- UI bucket, Python/kit side + a cross-side compare joined on content
                   anchor. NOT reimplemented here -- once both sides carry the same id
                   (Phase 3, via transpile), cross-side matching is id equality, a later
                   phase's concern. Ignored except to understand what it did.

All three kept their own key (name / branch-path-by-anchor / content-anchor) and their own
partial scope. This module instead:

  1. runs idgen (the id source of truth -- a unique positional-path id per Kotlin source
     node, unconditional child-index at every node, no anchor fallback) over the WHOLE app
     package tree (all .kt under com/sara/workoutforlife), not just ui/ -- one record per id.
  2. builds ONE superset record per id: {id, file, node_kind, anchor, span}, then enriches:
       - call_expression nodes that are widget/composable call sites -> UI layout fields,
         by REUSING ui_ledger's own extractors (_norm, _named_args, _name, _is_widget,
         _segment) -- not reimplemented.
       - class_declaration / object_declaration / function_declaration frame nodes ->
         1-degree connectivity, by REUSING ledger.py's static Kotlin-side extractors
         (_kname, _kind, _kt_attrs, _kt_methods_nested, _refs) against the whole-corpus
         name universe (oracle.build_index()). NOTE: this reuses ledger.py's KOTLIN-side
         (static, tree-sitter) extraction only -- ledger.py's Python-side (exec + introspect
         a transpiled engine) is a per-engine, name-keyed cross-check that doesn't fit an
         id-keyed, whole-app, single-pass ledger; folding it in is future work (see the
         "connectivity" field notes below -- KT-side 1-degree refs ARE populated).
     Nodes the enrichment doesn't apply to (e.g. a non-widget call_expression, a
     source_file record) simply leave those fields null/empty -- the intended superset
     schema, not a bug.
  3. writes the result as ONE JSON file, one entry per id.
  4. --check asserts: every id appears exactly once, and entry_count == idgen's node count
     over the same root (nothing tracked-but-missing, nothing extra).

Usage:
    python3 ledger_unified.py --build          # write the ledger JSON
    python3 ledger_unified.py --check          # build in-memory + assert invariants, no write
    python3 ledger_unified.py --build --check  # write AND assert
"""
import argparse
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import oracle as O                          # noqa: E402  (MAIN, build_index)
import idgen                                # noqa: E402  (gen_ids_for_root, check_uniqueness) -- REUSED, not modified
import ui_ledger as UL                      # noqa: E402  (_norm, _named_args, _name, _is_widget, _segment) -- REUSED
import ledger as LG                         # noqa: E402  (_kname, _kind, _kt_attrs, _kt_methods_nested, _refs) -- REUSED

APPROOT = os.path.join(O.MAIN, "java", "com", "sara", "workoutforlife")
UIROOT = os.path.join(APPROOT, "ui")         # ui_ledger._is_widget's heuristic (name[0].isupper())
                                              # is only valid within the Compose UI subtree -- see
                                              # ui_fields() below.
OUT_PATH = os.path.join(HERE, "ledger_sample", "ledger_unified.json")

FRAME_KINDS = ("class_declaration", "object_declaration", "function_declaration")


# ── node resolution: idgen.Record carries span+kind but not the tree-sitter node itself
# (see its __slots__) -- additive-only (idgen.py is not modified), so re-parse each file
# once and index its RECORD_KINDS nodes by (start_byte, end_byte, node_kind), which is a
# deterministic, unique locator within one file's tree (two distinct nodes of the same
# kind never share the exact same byte span). This mirrors idgen's own walk/RECORD_KINDS
# filter -- it doesn't reinterpret or duplicate the id-assignment logic, only recovers the
# live node handle idgen chose not to keep.
from parse import parse as _ts_parse        # noqa: E402


def _index_nodes_by_span(path):
    src = open(path, "rb").read()
    root = _ts_parse(src).root_node
    idx = {}

    def walk(n):
        if n.type in idgen.RECORD_KINDS:
            idx[(n.start_byte, n.end_byte, n.type)] = n
        for c in n.children:
            walk(c)
    walk(root)
    return idx


def resolve_nodes(records):
    """-> {record.id -> tree-sitter node}, resolved per-file via the span index above."""
    by_file = {}
    for r in records:
        by_file.setdefault(r.file, []).append(r)
    out = {}
    for path, recs in by_file.items():
        idx = _index_nodes_by_span(path)
        for r in recs:
            out[r.id] = idx.get((r.start_byte, r.end_byte, r.node_kind))
    return out


# ── UI enrichment (reuses ui_ledger's extractors) ────────────────────────────
def _nearest_call_ancestor_name(node):
    """walk up the tree-sitter parent chain to the nearest enclosing call_expression's
    callee name -- stands in for render_node's `parent_kind` (needed by _norm to resolve
    `weight()`'s Row-vs-Column axis), without redoing ui_ledger's containment walk."""
    p = node.parent
    while p is not None:
        if p.type == "call_expression":
            try:
                return UL._name(p)
            except Exception:                # noqa: BLE001
                return None
        p = p.parent
    return None


def ui_fields(node):
    """-> dict of UI layout fields for a call_expression node that is a widget/composable
    call site (per ui_ledger._is_widget), else None. Reuses ui_ledger._norm/_named_args/
    _name/_is_widget verbatim -- no re-derivation of the size/pad/offset/align vocabulary.

    Caller is expected to only invoke this for call sites inside ui/ (see `build()`):
    ui_ledger._is_widget is just "callee name starts uppercase", a heuristic that only
    holds within the Compose UI tree, where every capitalized call really is a composable/
    widget. Outside ui/ (engine/model/data code) plenty of ordinary calls also start
    uppercase (constructors, `CoroutineScope(...)`, factory functions, enum-like calls) --
    applying the heuristic there produces false "UI" nodes. This isn't a rewrite of
    ui_ledger's logic, just applying it on the same scope it was always designed for."""
    if node.type != "call_expression":
        return None
    try:
        if not UL._is_widget(node):
            return None
        name = UL._name(node)
        parent_kind = _nearest_call_ancestor_name(node)
        d = UL._norm(node, parent_kind)
    except Exception:                        # noqa: BLE001
        return None
    sz = d["size"]
    return {
        "widget_name": name,
        "size": {
            "w": sz["w"], "w_kind": UL._tag(sz["w"]),
            "h": sz["h"], "h_kind": UL._tag(sz["h"]),
        },
        "pad": d["pad"], "pad_kind": ("abs" if d["pad"] and UL._abs(d["pad"]) else ("rel" if d["pad"] else None)),
        "offset": d["offset"], "offset_kind": ("abs" if d["offset"] else None),
        "align": d["align"], "align_kind": ("rel" if d["align"] else None),
        "container": d["container"],
        "nonlayout": d["nonlayout"],
        "other_modifiers": d["other"],
    }


# ── frame connectivity enrichment (reuses ledger.py's static KT-side extractors) ─
def frame_fields(node, universe):
    """-> dict of 1-degree connectivity fields for a class/object/function declaration
    node, reusing ledger.py's static (tree-sitter) Kotlin-side extractors. This is the
    KT-side half of ledger.py's cross-check only (name + attrs + methods + 1-degree
    refs) -- ledger.py's Python-side (exec + introspect a transpiled engine, per-engine)
    is NOT folded in here; see module docstring."""
    try:
        name = LG._kname(node)
        if node.type in ("class_declaration", "object_declaration"):
            kind = LG._kind(node)
            attrs = LG._kt_attrs(node)
            methods, nested = LG._kt_methods_nested(node)
            nested_names = {LG._kname(nn) for nn in nested}
            conns = sorted(LG._refs(node, universe) - {name} - nested_names)
            return {
                "frame_kind": kind, "frame_name": name, "attrs": attrs, "methods": methods,
                "nested": sorted(nested_names), "connects_1deg": conns,
            }
        elif node.type == "function_declaration":
            is_comp = idgen._is_composable(node)
            conns = sorted(LG._refs(node, universe) - ({name} if name else set()))
            return {
                "frame_kind": "@Composable fun" if is_comp else "fun", "frame_name": name,
                "attrs": [], "methods": [], "nested": [], "connects_1deg": conns,
            }
    except Exception:                        # noqa: BLE001
        return None
    return None


# ── build ─────────────────────────────────────────────────────────────────────
def build(approot=APPROOT):
    records, files = idgen.gen_ids_for_root(approot)
    ok, total, distinct, dupes = idgen.check_uniqueness(records)
    assert ok, f"idgen produced {len(dupes)} duplicate id(s) at full-app scale -- id source not unique"

    universe = set(O.build_index())          # whole-corpus (main+test) declared-name universe, static
    nodes_by_id = resolve_nodes(records)      # id -> tree-sitter node (idgen.Record doesn't keep it)

    ledger = {}
    ui_count = frame_count = 0
    for r in records:
        node = nodes_by_id.get(r.id)
        entry = {
            "id": r.id,
            "file": os.path.relpath(r.file, O.CORPUS),
            "node_kind": r.node_kind,
            "anchor": r.anchor,
            "span": {
                "start_line": r.start_point[0] + 1, "start_col": r.start_point[1],
                "end_line": r.end_point[0] + 1, "end_col": r.end_point[1],
                "start_byte": r.start_byte, "end_byte": r.end_byte,
            },
            "ui": None,          # populated below for widget/composable call sites
            "connectivity": None,  # populated below for class/object/function frames
        }
        in_ui_tree = r.file.startswith(UIROOT + os.sep)
        if node is not None and r.node_kind == "call_expression" and in_ui_tree:
            ui = ui_fields(node)
            if ui is not None:
                entry["ui"] = ui
                ui_count += 1
        elif node is not None and r.node_kind in FRAME_KINDS:
            fr = frame_fields(node, universe)
            if fr is not None:
                entry["connectivity"] = fr
                frame_count += 1
        # source_file records: superset base fields only (module root -- no UI, no
        # per-frame connectivity of its own; ledger.py's module-level connects(1deg) is
        # the union of its frames' connects, derivable from this ledger later, not stored
        # redundantly per source_file here).
        ledger[r.id] = entry

    return ledger, records, files, ui_count, frame_count


def write_ledger(ledger, out_path=OUT_PATH):
    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    with open(out_path, "w") as f:
        json.dump(ledger, f, indent=1, sort_keys=True)
    return out_path


def check(approot=APPROOT, out_path=None):
    """-> (ok: bool, report: dict). Rebuilds in-memory (or reads `out_path` if given) and
    asserts: (a) every id in idgen's own node scan appears exactly once in the ledger,
    (b) entry_count == idgen node_count (nothing tracked-but-missing, nothing extra)."""
    records, files = idgen.gen_ids_for_root(approot)
    idok, total, distinct, dupes = idgen.check_uniqueness(records)

    if out_path and os.path.exists(out_path):
        ledger = json.load(open(out_path))
    else:
        ledger, _, _, _, _ = build(approot)

    ledger_ids = list(ledger.keys())
    ledger_distinct = len(set(ledger_ids))
    entry_count = len(ledger_ids)
    idgen_ids = {r.id for r in records}

    dup_in_ledger = entry_count - ledger_distinct           # >0 would mean JSON key collisions (impossible
                                                              # in a dict, kept for symmetry/clarity)
    missing = idgen_ids - set(ledger_ids)                    # tracked by idgen but absent from ledger
    extra = set(ledger_ids) - idgen_ids                       # present in ledger but not produced by idgen

    ok = (idok and dup_in_ledger == 0 and entry_count == total
          and not missing and not extra)

    report = {
        "kt_files": len(files),
        "idgen_total_nodes": total,
        "idgen_distinct_ids": distinct,
        "idgen_duplicate_ids": len(dupes),
        "ledger_entry_count": entry_count,
        "ledger_distinct_ids": ledger_distinct,
        "ledger_duplicate_entries": dup_in_ledger,
        "missing_from_ledger": len(missing),
        "extra_in_ledger": len(extra),
        "entry_count_eq_node_count": entry_count == total,
        "ok": ok,
    }
    return ok, report


# ── CLI ───────────────────────────────────────────────────────────────────────
def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--build", action="store_true", help="build the unified ledger and write it to disk")
    ap.add_argument("--check", action="store_true",
                     help="assert invariants (unique ids, entry_count == idgen node_count)")
    ap.add_argument("--out", default=OUT_PATH, help="output JSON path (with --build)")
    args = ap.parse_args()

    if not (args.build or args.check):
        ap.print_help()
        return

    if args.build:
        ledger, records, files, ui_count, frame_count = build()
        path = write_ledger(ledger, args.out)
        by_kind = {}
        for r in records:
            by_kind[r.node_kind] = by_kind.get(r.node_kind, 0) + 1
        print(f"ledger_unified: {len(files)} .kt files under {APPROOT}")
        print(f"ledger_unified: {len(ledger)} entries -> {os.path.relpath(path)}")
        for k in idgen.RECORD_KINDS:
            print(f"ledger_unified:   {k}: {by_kind.get(k, 0)}")
        print(f"ledger_unified: UI-enriched call_expression entries: {ui_count}")
        print(f"ledger_unified: connectivity-enriched frame entries: {frame_count}")

    if args.check:
        out_path = args.out if (args.build or os.path.exists(args.out)) else None
        ok, report = check(out_path=out_path)
        for k, v in report.items():
            print(f"check: {k} = {v}")
        if ok:
            print("check: OK -- one entry per id, entry_count == idgen node_count, 0 duplicates")
        else:
            print("check: FAIL")
            sys.exit(1)


if __name__ == "__main__":
    main()
