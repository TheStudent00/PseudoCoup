"""holder_bridge -- Automated Ledger-Level Holder Bridging across multi-language tools.

Demonstrates how `link_ledgers` operates directly on `URLedger` data:
1. Ingresses 4 functions from Python (`i64`), Go (`i64 -> u32`), C (`i32 -> i64`), and Rust (`i64`).
2. `link_ledgers([l_py, l_go, l_c, l_rust])` walks all `URCall` edges and `URReturn` nodes in the
   ledger, compares caller/callee `HolderDecl`s, and automatically splices `URHolderCast`
   (`UniversalRichNode`) bridges into the `URLedger` wherever holders differ (`i64 -> u32`,
   `u32 -> i32`, `i64 -> i32`).
3. Emits the linked `URLedger` into a single unified target script and verifies execution.
"""
from __future__ import annotations
import json
from typing import Any
from ..ledgerer import ScriptToLedger, LedgerToScript, link_ledgers, eval_ledger


def run_cross_language_tool_demo() -> dict[str, Any]:
    py_tool = """
def py_grid_cell(coord: i64, step: i64) -> i64:
    cell = coord % step
    bucket = coord // step
    return (cell * 100) + bucket
"""
    go_tool = """
func go_pack_u32(val int64, sh int64) uint32 {
    shifted := val << sh
    return shifted | 2147483648
}
"""
    c_tool = """
int64_t c_mix_i32(int32_t packed_i32, int32_t salt) {
    int64_t mixed = (packed_i32 ^ salt) + (packed_i32 >> 4);
    return mixed;
}
"""
    rust_orchestrator = """
fn run_polyglot_pipeline(coord: i64, step: i64, sh: i64, salt: i64) -> i64 {
    let mut cell_idx: i64 = py_grid_cell(coord, step);
    let mut packed_u32: u32 = go_pack_u32(cell_idx, sh);
    let mut digest: i64 = c_mix_i32(packed_u32, salt);
    return digest;
}
"""
    l_py = ScriptToLedger.parse(py_tool, "python")
    l_go = ScriptToLedger.parse(go_tool, "go")
    l_c = ScriptToLedger.parse(c_tool, "c")
    l_rust = ScriptToLedger.parse(rust_orchestrator, "rust")

    # Automated ledger-level linking: inspects HolderDecls and splices URHolderCast into URLedger!
    linked = link_ledgers([l_py, l_go, l_c, l_rust])
    assert len(linked.bridge_events) == 4, f"Expected 4 automated bridges, got {linked.bridge_events}"

    # Execute the linked URLedger directly and also transpile the entire linked ledger to Rust and C
    inputs = {"coord": -17, "step": 5, "sh": 2, "salt": 37}
    val_direct = eval_ledger(linked, inputs, "run_polyglot_pipeline")

    unified_rust = LedgerToScript.emit(linked, "rust")
    unified_c = LedgerToScript.emit(linked, "c")

    val_from_emitted_rust = eval_ledger(ScriptToLedger.parse(unified_rust, "rust"), inputs, "run_polyglot_pipeline")
    val_from_emitted_c = eval_ledger(ScriptToLedger.parse(unified_c, "c"), inputs, "run_polyglot_pipeline")
    assert val_direct == val_from_emitted_rust == val_from_emitted_c == -2281700145

    return {
        "automated_bridge_events": linked.bridge_events,
        "pipeline_output": val_direct,
        "unified_rust_script": unified_rust,
        "unified_c_script": unified_c,
    }


if __name__ == "__main__":
    res = run_cross_language_tool_demo()
    print(f"[PASS] Automated Ledger Linking ({len(res['automated_bridge_events'])} URHolderCast nodes spliced into URLedger):")
    for ev in res["automated_bridge_events"]:
        print(f"  - {ev['site']} ({ev['from_lang']} {ev['src_holder']} -> {ev['to_lang']} {ev['dst_holder']}): {ev['bridge_kind']} [{ev['riscv64_lo_op']}]")
    print(f"  pipeline_output = {res['pipeline_output']} (verified bit-identical in unified Rust & C emissions)")
