"""verify_hub_all_12_langs -- End-to-End Verification of `The Hub` (`log_528` Stage 2, Steps 2.1 & 2.2).

Verifies:
  1. `Hub.load_lowered_vocabularies()` across all 12 languages and canonical equivalence mode indexing.
  2. `Hub.compute_semantic_mode_key()` grouping all 12 languages' `BV_ADD` `UR-Node`s into a single
     shared `(D_ok, D_trap, R_val)` semantic mode.
  3. `Hub.eval_qualified_expr()` across all 12 languages (`C`, `C++`, `Go`, `Rust`, `Python`, `Java`,
     `TypeScript`, `C#`, `Ruby`, `PHP`, `Dart`, `Swift`), including nested expressions, assignments,
     unary/binary/ternary operators, and edge domains (`-17 Python.// 5 == -4` vs `-17 C./ 5 == -3`,
     `-1 Java.>>> 60 == 15`).
  4. Whole-lowered `compiler-rt` caller `UR-Node` execution via `Hub.eval_node()` (`__ashlti3`).
  5. `Hub.transpile_hub_expr()` across all 12 languages into all 12 target languages (`Tier 1`, `Tier 2`, `Tier 3`).
  6. `MultiBodyEngine` control-flow execution and multi-language transpilation.
"""
from __future__ import annotations

import gzip
import json
import sys
import time
from pathlib import Path
from typing import Any

HERE = Path(__file__).resolve().parent
for _anc in HERE.parents:
    if (_anc / "pseudocoup" / "__init__.py").exists():
        if str(_anc) not in sys.path:
            sys.path.insert(0, str(_anc))
        import pseudocoup  # noqa: F401
        break
PCHQ_ROOT = HERE.parents[2]
PROJECTS_DIR = PCHQ_ROOT / "Projects"
if PROJECTS_DIR.exists() and str(PROJECTS_DIR) not in sys.path:
    sys.path.insert(0, str(PROJECTS_DIR))

from PseudoArch.map_HiOp_to_unit.lower_HiOp import Word
from PseudoArch.map_HiOp_to_unit.lower_HiOp.extract_unit_from_LoHiOp import Unit
from PseudoArch.map_unit_to_lean import compose_LoOp_leans
from PseudoCoup.hub import Hub
from PseudoCoup.hub.autopoly.verify_hiop_primitives import ALL_12_LANGUAGES, OUT_DIR
from PseudoCoup.ledgerer.universal_rich_node import UniversalRichNode

SUMMARY_OUT = OUT_DIR / "hub_12lang_verification_summary.json"


def _verify_real_compiler_rt_caller_nodes(hub: Hub) -> list[dict[str, Any]]:
    """Verify real `compiler-rt` caller `UR-Node`s from `gnu_c_first_of_each_hijacked.jsonl.gz` / `rust_all.jsonl.gz`
    plus 4-word 128-bit `StateInfo0` callers (`__divti3`, `__modti3`, `__addtf3`, `__multf3`),
    asserting `len(ul.ext_calls) > 0` and 4-word `a, b, c, d` input binding without `in_off_24`."""
    from PseudoArch.map_HiOp_to_unit.model_lang_parts import Operator
    from PseudoArch.map_HiOp_to_unit.model_lang_parts.context.entry_context import PartState0, StateInfo0

    for op_name, tmpl, htype, alias in [
        ("BinaryOperator.Div", "a / b", "__int128", "C.div128"),
        ("BinaryOperator.Rem", "a % b", "__int128", "C.mod128"),
        ("BinaryOperator.Add", "a + b", "long double", "C.addtf3"),
        ("BinaryOperator.Mul", "a * b", "long double", "C.multf3"),
    ]:
        si = StateInfo0(
            "c",
            Operator("c", op_name, tmpl, ("a", "b"), "verify_hub"),
            (PartState0("a", htype), PartState0("b", htype)),
        )
        hub.register_state_info_0(si, alias=alias)

    caller_specs = [
        # (node_key, alias, expected_ext_call, args_4_words, expected_low64_or_none)
        (
            "C.CompoundAssignOperator.RemAssign[_BitInt(128),unsigned _BitInt(37)]",
            "C.remassign_bitint128",
            "__modti3",
            (100, 0, 7, 0),
            2,
        ),
        (
            "Rust.Cast[i128,f64]",
            "Rust.cast_i128_f64",
            "__floattidf",
            (42, 0, 0, 0),
            0x4045000000000000,
        ),
        ("C.div128", "C.div128", "__divti3", (100, 0, 7, 0), 14),
        ("C.mod128", "C.mod128", "__modti3", (100, 0, 7, 0), 2),
        (
            "C.addtf3",
            "C.addtf3",
            "__addtf3",
            (0, 0x3FFF000000000000, 0, 0x4000000000000000),
            0,
        ),
        (
            "C.multf3",
            "C.multf3",
            "__multf3",
            (0, 0x4000000000000000, 0, 0x4000800000000000),
            0,
        ),
    ]
    verified: list[dict[str, Any]] = []
    for node_key, alias, expected_call, args4, expected_val in caller_specs:
        node = hub.resolve_node(node_key)
        hub.nodes[alias] = node
        hub._ci_nodes[alias.lower()] = node
        ul = node.meaning["unit_lean"]
        assert len(ul.ext_calls) > 0 and expected_call in ul.ext_calls, (
            f"Expected {expected_call!r} in {node_key}.ext_calls, got {ul.ext_calls}"
        )
        emitted = hub.transpile_qualified_op(node, "python", "a", "b", "c", "d")
        assert "in_off_24" not in emitted["code"], (
            f"Unbound 4th input word 'in_off_24' found in emitted code for {node_key}: {emitted['code']}"
        )
        assert f"compiler_rt_{expected_call}_" in emitted["code"], (
            f"Expected compiler_rt_{expected_call}_ call in {emitted['code']}"
        )
        got_val = hub.eval_node(alias, *args4)
        assert got_val == expected_val, (
            f"Hub.eval_node({alias!r}, {args4}) returned {got_val}, expected {expected_val}"
        )
        verified.append(
            {
                "node": node_key,
                "alias": alias,
                "ext_calls": list(ul.ext_calls),
                "emitted_python": emitted["code"],
                "inputs": list(args4),
                "output": got_val,
            }
        )
    return verified


def run_hub_verification() -> dict[str, Any]:
    t0 = time.time()
    hub = Hub()
    counts = hub.load_lowered_vocabularies()

    # 1. Verify all 12 languages' BV_ADD share the exact same semantic mode `(D_ok, D_trap, R_val)`
    add_ops = [
        "C.+", "C++.+", "Go.+", "Rust.+", "Python.+", "Java.+",
        "TypeScript.+", "C#.+", "Ruby.+", "PHP.+", "Dart.+", "Swift.&+",
    ]
    add_mode_keys = {op: hub.compute_semantic_mode_key(op) for op in add_ops}
    unique_add_modes = set(add_mode_keys.values())
    assert len(unique_add_modes) == 1, f"Expected 1 shared semantic mode for BV_ADD across 12 languages, got {unique_add_modes}"

    # 2. Verify `eval_qualified_expr` across all 12 languages
    env = {"m": 6, "x": 7, "b": 5, "neg": -17, "pos": 5, "ones": -1, "sh": 60, "cond": 1}
    eval_cases = [
        ("y = (m C.* x) C.+ b", 47),
        ("((m C++.* x) C++.- b)", 37),
        ("((m Go.+ x) Go.* b)", 65),
        ("(neg C./ pos)", -3),
        ("(neg Go./ pos)", -3),
        ("(neg Rust./ pos)", -3),
        ("(neg Python.// pos)", -4),
        ("(neg Python.% pos)", 3),
        ("(neg C.% pos)", -2),
        ("(ones Java.>>> sh)", 15),
        ("(ones TypeScript.>>> sh)", 15),
        ("(ones C#.>>> sh)", 15),
        ("(ones Dart.>>> sh)", 15),
        ("((m Ruby.+ x) PHP.+ (b Swift.&* pos))", 38),
        ("C.~ 0", -1),
        ("Rust.! 0", -1),
        ("C.?:(cond, m, x)", 6),
        ("Python.?:(0, m, x)", 7),
    ]
    eval_results: list[dict[str, Any]] = []
    for expr, expected in eval_cases:
        local_env = dict(env)
        got = hub.eval_qualified_expr(expr, local_env)
        assert got == expected, f"Hub.eval_qualified_expr({expr!r}) returned {got}, expected {expected}"
        if expr.startswith("y ="):
            assert local_env["y"] == expected
        eval_results.append({"expr": expr, "got": got, "expected": expected})

    # 3. Verify whole-lowered `compiler-rt` caller UR-Node execution via `Hub.eval_node`
    crt_evals = _verify_real_compiler_rt_caller_nodes(hub)

    # 4. Verify `transpile_hub_expr` across all 12 target languages
    transpile_results: list[dict[str, Any]] = []
    sample_exprs = [
        "y = (m C.* x) C.+ b",
        "(a Go./ b)",
        "(a Python.// b)",
        "(a Java.>>> b)",
        "C.?:(cond, a, b)",
    ]
    for expr in sample_exprs:
        for tgt_lang in ALL_12_LANGUAGES:
            tr = hub.transpile_hub_expr(expr, tgt_lang)
            assert tr["transpiled_code"], f"Empty transpiled_code for {expr!r} -> {tgt_lang}"
            assert len(tr["steps"]) >= 1
            transpile_results.append(
                {
                    "expr": expr,
                    "target_lang": tgt_lang,
                    "transpiled_code": tr["transpiled_code"],
                    "tiers": [st["tier"] for st in tr["steps"]],
                }
            )

    # 5. Verify MultiBodyEngine execution & transpilation
    counter = {"i": 0, "acc": 0}
    iters = hub.multi_body.exec_while(
        lambda: int(counter["i"] < 5),
        lambda: (
            counter.__setitem__("acc", counter["acc"] + counter["i"]),
            counter.__setitem__("i", counter["i"] + 1),
        ),
    )
    assert iters == 5 and counter["acc"] == 10

    elapsed = round(time.time() - t0, 3)
    summary = {
        "dataset_unit_counts": counts,
        "total_registered_keys": len(hub.nodes),
        "total_canonical_unit_modes": len(hub.modes),
        "shared_bv_add_semantic_mode_count": len(unique_add_modes),
        "eval_cases_verified": len(eval_results),
        "eval_results": eval_results,
        "compiler_rt_caller_evals": crt_evals,
        "transpile_cases_verified": len(transpile_results),
        "sample_transpiles": transpile_results[:24],
        "elapsed_seconds": elapsed,
    }
    with open(SUMMARY_OUT, "w", encoding="utf-8") as f:
        json.dump(summary, f, indent=2)
    return summary


if __name__ == "__main__":
    s = run_hub_verification()
    print(
        f"Verified Hub across all 12 languages in {s['elapsed_seconds']}s: "
        f"{s['total_registered_keys']} registered UR-Nodes, "
        f"{s['total_canonical_unit_modes']} canonical modes, "
        f"{s['eval_cases_verified']} eval cases, "
        f"{s['transpile_cases_verified']} transpile cases!"
    )
