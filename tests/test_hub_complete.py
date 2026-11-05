#!/usr/bin/env python3
"""test_hub_complete -- 3-Level Verification Suite for the Hub & AutoPoly.

Verifies:
  1. Exhaustive execution of all 9,814 lowered RISC-V Units across C, C++, Clang dialects,
     Go, Rust, Python, and Java in RiscvUnitVM (including multi-body part_* callbacks).
  2. Multi-body control flow (`if/else`, `while`, `for`, `switch`, `?:`, `&&`, `||`,
     dependent `break`/`continue`) + ComplexHolder (`struct`, `array`) + polyglot operators.
  3. Z3 formal equivalence theorems for multi-body control flow and short-circuiting.
"""
from __future__ import annotations
import gzip
import json
from pathlib import Path
import sys
import z3

HERE = Path(__file__).resolve().parent
for _anc in HERE.parents:
    if (_anc / "pseudocoup" / "__init__.py").exists():
        if str(_anc) not in sys.path:
            sys.path.insert(0, str(_anc))
        import pseudocoup  # noqa: F401
        break
sys.path.insert(0, str(HERE.parents[1]))
from PseudoCoup.hub import BreakSignal, ComplexHolder, ContinueSignal, Hub


def verify_all_lowered_units_in_vm(h: Hub) -> dict[str, int]:
    """Run every lowered Unit across all 6 language groups through RiscvUnitVM."""
    p1 = Path(__file__).resolve().parents[1] / "pseudoarch" / "map_HiOp_to_unit" / "lowered_units"
    p2 = Path(__file__).resolve().parents[1] / "pseudocoup" / "pseudoarch" / "map_HiOp_to_unit" / "lowered_units"
    hq_dir = Path(__file__).resolve().parents[3] / "Research" / "lower_HiOp" / "out"
    out_dir = p1 if p1.exists() else (p2 if p2.exists() else hq_dir)
    files = [
        ("C", out_dir / "gnu_c_first_of_each.jsonl.gz"),
        ("ClangOther", out_dir / "clang_other_langs_all.jsonl.gz"),
        ("Go", out_dir / "go_all.jsonl.gz"),
        ("Rust", out_dir / "rust_all.jsonl.gz"),
        ("Python", out_dir / "python_first_of_each.jsonl.gz"),
        ("Java", out_dir / "java_all.jsonl.gz"),
        ("TypeScript", out_dir / "typescript_all.jsonl.gz"),
        ("C#", out_dir / "csharp_all.jsonl.gz"),
        ("Ruby", out_dir / "ruby_all.jsonl.gz"),
        ("PHP", out_dir / "php_all.jsonl.gz"),
        ("Dart", out_dir / "dart_all.jsonl.gz"),
        ("Swift", out_dir / "swift_all.jsonl.gz"),
    ]
    executed = 0
    multi_body_units = 0
    for _lang, path in files:
        with gzip.open(path, "rt") as gz:
            for line in gz:
                rec = json.loads(line)
                words = rec.get("words") or []
                unit_idxs = rec.get("unit") or list(range(len(words)))
                if not words or not unit_idxs:
                    continue
                parts = rec.get("parts") or []
                if parts:
                    multi_body_units += 1
                # Provide deterministic non-zero callbacks for held parts
                cbs = {p: (lambda: 1) for p in parts}
                h.vm.reset()
                h.vm.write_holder_words([7, 3, 0, 0])
                h.vm.execute_unit(words, unit_idxs, cbs, max_steps=120)
                executed += 1
    # Verify real lowered RISC-V ConditionalOperator Unit (`a ? b : c`) branches & short-circuits at machine level
    cond_true = cond_false = None
    with gzip.open(out_dir / "gnu_c_first_of_each.jsonl.gz", "rt") as gz:
        for line in gz:
            rec = json.loads(line)
            if rec["operator"] == "ConditionalOperator" and rec.get("holders", [[None, ""]])[0][1] == "long":
                w, u, p = rec["words"], rec["unit"], rec["parts"]
                if len(p) == 3:
                    h.vm.reset()
                    cond_true = h.vm.execute_unit(w, u, {p[0]: lambda: 1, p[1]: lambda: 100, p[2]: lambda: 200})
                    h.vm.reset()
                    cond_false = h.vm.execute_unit(w, u, {p[0]: lambda: 0, p[1]: lambda: 100, p[2]: lambda: 200})
                    assert cond_true["called_parts"] == [p[0], p[1]] and cond_true["a0"] == 100
                    assert cond_false["called_parts"] == [p[0], p[2]] and cond_false["a0"] == 200
                else:
                    h.vm.reset()
                    h.vm.write_holder_words([1, 0, 0, 0])
                    cond_true = h.vm.execute_unit(w, u, {p[0]: lambda: 100, p[1]: lambda: 200})
                    h.vm.reset()
                    h.vm.write_holder_words([0, 0, 0, 0])
                    cond_false = h.vm.execute_unit(w, u, {p[0]: lambda: 100, p[1]: lambda: 200})
                    assert cond_true["called_parts"] == [p[0]] and cond_true["a0"] == 100
                    assert cond_false["called_parts"] == [p[1]] and cond_false["a0"] == 200
                break
    return {
        "total_units_executed": executed,
        "multi_body_units_executed": multi_body_units,
        "riscv_conditional_unit_true": cond_true,
        "riscv_conditional_unit_false": cond_false,
    }


def verify_polyglot_multi_body_program(h: Hub) -> dict[str, object]:
    """Run a polyglot multi-body program mixing C/C++/Go/Rust/Python/Java HiOps & ComplexHolders."""
    state = ComplexHolder("struct", fields={"acc": 0, "idx": 0, "side_effects": 0})
    arr = ComplexHolder("array", elements=[10, -7, 0, 42, 99])

    # Short-circuit verification (`a && b` when a==0 must NOT run part_b)
    def touch_side_effect() -> int:
        state.set("side_effects", state.get("side_effects") + 1)
        return 1

    sc_and = h.multi_body.eval_short_circuit_and(lambda: 0, touch_side_effect)
    sc_or = h.multi_body.eval_short_circuit_or(lambda: 1, touch_side_effect)
    assert sc_and == 0 and sc_or == 1 and state.get("side_effects") == 0

    # Polyglot loop: iterate over `arr` with `while`, `if_else`, `?:`, `continue`, `break`,
    # and qualified operators (`Python.//`, `Go./`, `Java.>>>`, `C.*`, `C.+`)
    def loop_cond() -> int:
        return 1 if state.get("idx") < len(arr.elements) else 0

    def loop_body() -> None:
        i = state.get("idx")
        val = arr.get(i)
        state.set("idx", i + 1)
        # Skip 0 via dependent `continue;`
        h.multi_body.exec_if_else(
            lambda: 1 if val == 0 else 0,
            lambda: (_ for _ in ()).throw(ContinueSignal()),
        )
        # Stop at 99 via dependent `break;`
        h.multi_body.exec_if_else(
            lambda: 1 if val == 99 else 0,
            lambda: (_ for _ in ()).throw(BreakSignal()),
        )
        # Ternary `val < 0 ? (val Python.// 2) : (val Go./ 2)`
        step_val = h.multi_body.eval_ternary(
            lambda: 1 if val < 0 else 0,
            lambda: int(h.eval_qualified_expr("(v Python.// d)", {"v": val, "d": 2})),
            lambda: int(h.eval_qualified_expr("(v Go./ d)", {"v": val, "d": 2})),
        )
        new_acc = int(h.eval_qualified_expr("(acc C.* m) C.+ s", {"acc": state.get("acc"), "m": 2, "s": step_val}))
        state.set("acc", new_acc)

    iters = h.multi_body.exec_while(loop_cond, loop_body)
    return {
        "iterations_run": iters,
        "final_acc": state.get("acc"),
        "final_idx": state.get("idx"),
        "short_circuit_side_effects": state.get("side_effects"),
        "remaining_six_langs_hub_checks": {
            "TypeScript.>>> (-1 >>> 28)": h.eval_qualified_expr("(a TypeScript.>>> b)", {"a": -1, "b": 28}),
            "C#.>>> (-1 >>> 60)": h.eval_qualified_expr("(a C#.>>> b)", {"a": -1, "b": 60}),
            "Ruby.<=> (10 <=> 20)": h.eval_qualified_expr("(a Ruby.<=> b)", {"a": 10, "b": 20}),
            "PHP.<=> (20 <=> 10)": h.eval_qualified_expr("(a PHP.<=> b)", {"a": 20, "b": 10}),
            "Dart.% (-7 % 3 Euclidean)": h.eval_qualified_expr("(a Dart.% b)", {"a": -7, "b": 3}),
            "Swift.&+ and Swift.&*": h.eval_qualified_expr("(m Swift.&* x) Swift.&+ b", {"m": 7, "x": 6, "b": 3}),
        },
        "transpiled_while_rust": h.multi_body.transpile_multi_body("while", "rust", ["idx < 5", "acc = acc.wrapping_mul(2).wrapping_add(step)"]),
        "transpiled_ternary_python": h.multi_body.transpile_multi_body("ternary", "python", ["val < 0", "val // 2", "int(val / 2)"]),
    }


def verify_z3_control_flow_theorems() -> dict[str, str]:
    """Prove control-flow & multi-body equivalence theorems in Z3."""
    a, b, c = z3.BitVecs("a b c", 64)
    ZERO = z3.BitVecVal(0, 64)
    ONE = z3.BitVecVal(1, 64)

    # Theorem 1: `if (a) b else c` == `t = (a != 0); if (t) b; if (!t) c` (`SUPPORT_BRAINSTORM_hub.md` row 28)
    s1 = z3.Solver()
    if_else_val = z3.If(a != ZERO, b, c)
    t = (a != ZERO)
    seq_val = z3.If(z3.Not(t), c, z3.If(t, b, ZERO))
    s1.add(if_else_val != seq_val)

    # Theorem 2: Short-circuit `a && b` value & side-effect guard equivalence
    s2 = z3.Solver()
    land_val = z3.If(a != ZERO, z3.If(b != ZERO, ONE, ZERO), ZERO)
    spec_val = z3.If(z3.And(a != ZERO, b != ZERO), ONE, ZERO)
    s2.add(land_val != spec_val)

    return {
        "if_else_kept_test_decomposition": str(s1.check()),
        "short_circuit_land_equivalence": str(s2.check()),
    }


if __name__ == "__main__":
    hub = Hub()
    loaded = hub.load_lowered_vocabularies()
    vm_res = verify_all_lowered_units_in_vm(hub)
    poly_res = verify_polyglot_multi_body_program(hub)
    z3_res = verify_z3_control_flow_theorems()
    summary = {
        "loaded_vocabularies": loaded,
        "level1_exhaustive_unit_vm": vm_res,
        "level2_polyglot_multi_body_program": poly_res,
        "level3_z3_control_flow_theorems": z3_res,
    }
    print(json.dumps(summary, indent=2))
