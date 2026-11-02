"""test_roundtrip_two_cycles -- verify 2-cycle roundtrip stabilization via Ledgerer + Hub.

Tests:
  lang_x (S_0) --> Hub --> lang_y (T_1) --> Hub --> lang_x (S_1)
               --> Hub --> lang_y (T_2) --> Hub --> lang_x (S_2)

Verifies:
1. Cycle 1 normalizes raw source S_0 into canonical PseudoCoup form S_1 (and T_1).
2. Cycle 2 is strictly idempotent: T_2 == T_1 and S_2 == S_1 (byte-for-byte identical!).
3. Semantic equivalence: for all interior and boundary inputs,
   eval(S_0) == eval(T_1) == eval(S_1) == eval(T_2) == eval(S_2).
"""
from __future__ import annotations
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from pseudocoup.ledgerer import ScriptToLedger, LedgerToScript, eval_ledger


def run_two_cycle_roundtrip(
    name: str,
    s0_script: str,
    lang_x: str,
    lang_y: str,
    test_vectors: list[dict[str, int]],
) -> dict:
    # Cycle 1: S_0 (lang_x) -> L_1 -> T_1 (lang_y) -> L_2 -> S_1 (lang_x)
    l0 = ScriptToLedger.parse(s0_script, lang_x)
    t1_script = LedgerToScript.emit(l0, lang_y)
    l1 = ScriptToLedger.parse(t1_script, lang_y)
    s1_script = LedgerToScript.emit(l1, lang_x)

    # Cycle 2: S_1 (lang_x) -> L_3 -> T_2 (lang_y) -> L_4 -> S_2 (lang_x)
    l2 = ScriptToLedger.parse(s1_script, lang_x)
    t2_script = LedgerToScript.emit(l2, lang_y)
    l3 = ScriptToLedger.parse(t2_script, lang_y)
    s2_script = LedgerToScript.emit(l3, lang_x)

    t_stabilized = (t1_script == t2_script)
    s_stabilized = (s1_script == s2_script)
    assert t_stabilized, f"[{name}] T_1 != T_2:\n{t1_script}\nvs\n{t2_script}"
    assert s_stabilized, f"[{name}] S_1 != S_2:\n{s1_script}\nvs\n{s2_script}"

    eval_checks = []
    for vec in test_vectors:
        v_s0 = eval_ledger(l0, vec)
        v_t1 = eval_ledger(l1, vec)
        v_s1 = eval_ledger(l2, vec)
        v_t2 = eval_ledger(l3, vec)
        l4 = ScriptToLedger.parse(s2_script, lang_x)
        v_s2 = eval_ledger(l4, vec)
        assert v_s0 == v_t1 == v_s1 == v_t2 == v_s2, (
            f"[{name}] Semantic mismatch on {vec}: {v_s0}, {v_t1}, {v_s1}, {v_t2}, {v_s2}"
        )
        eval_checks.append({"inputs": vec, "output": v_s0, "all_5_stages_equal": True})

    return {
        "name": name,
        "lang_x": lang_x,
        "lang_y": lang_y,
        "S_0": s0_script.strip(),
        "T_1": t1_script,
        "S_1": s1_script,
        "T_2": t2_script,
        "S_2": s2_script,
        "S0_changed_to_S1": (s0_script.strip() != s1_script.strip()),
        "T1_equals_T2": t_stabilized,
        "S1_equals_S2": s_stabilized,
        "eval_checks": eval_checks,
    }



def main() -> None:
    go_s0 = """
func shift_and_div(a int64, b int64, c int64) int64 {
    shifted := a << b
    quot := shifted / c
    if quot > 0 {
        quot = quot + 1
    } else {
        quot = quot - 1
    }
    return quot
}
"""
    r_go_c = run_two_cycle_roundtrip(
        "Go <-> C (Saturating Shift + Overflow-Safe Division + Control Flow)",
        go_s0,
        "go",
        "c",
        [
            {"a": 10, "b": 3, "c": 5},
            {"a": 10, "b": 70, "c": 5},  # b >= 64 edge domain!
            {"a": -9223372036854775808, "b": 0, "c": -1},  # INT64_MIN / -1 edge domain!
        ],
    )

    py_s0 = """
def floor_step(a, b):
    q = a // b
    r = a % b
    if r != 0:
        q = q + r
    return q
"""
    r_py_rust = run_two_cycle_roundtrip(
        "Python <-> Rust (Floor Division + Floor Modulo + Branch)",
        py_s0,
        "python",
        "rust",
        [
            {"a": 17, "b": 5},
            {"a": -17, "b": 5},   # Negative dividend floor-div/mod edge domain!
            {"a": 17, "b": -5},   # Negative divisor floor-div/mod edge domain!
            {"a": -20, "b": 5},
        ],
    )

    ts_s0 = """
function bit_accum(n: number, step: number): number {
    let acc: number = 0;
    let i: number = 0;
    while (i < n) {
        acc = acc ^ (i << step);
        i = i + 1;
    }
    return acc;
}
"""
    r_ts_java = run_two_cycle_roundtrip(
        "TypeScript <-> Java (While Loop + Bitwise XOR + Shift)",
        ts_s0,
        "typescript",
        "java",
        [
            {"n": 5, "step": 2},
            {"n": 6, "step": 68},  # step >= 64 mask edge domain!
        ],
    )

    summary = {"suites": [r_go_c, r_py_rust, r_ts_java]}
    out_path = Path(__file__).resolve().parent / "roundtrip_two_cycles_results.json"
    out_path.write_text(json.dumps(summary, indent=2))
    for s in summary["suites"]:
        print(
            f"[PASS] {s['name']}: S0->S1 reshaped={s['S0_changed_to_S1']}, "
            f"T1==T2={s['T1_equals_T2']}, S1==S2={s['S1_equals_S2']}, "
            f"vectors={len(s['eval_checks'])}/5 stages bit-identical"
        )


if __name__ == "__main__":
    main()
