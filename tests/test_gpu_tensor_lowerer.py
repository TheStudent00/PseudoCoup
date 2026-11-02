"""test_gpu_tensor_lowerer -- Verifies `max_depth`-Pass GPU Tensor Lowerer == CPU Lowerer."""
from __future__ import annotations

import copy
from pathlib import Path
import sys

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from pseudocoup.gpu_lowerer import ALL_12_LANGS, DictLUT, GPUTensorLowerer, RelationalLedgerTable
from pseudocoup.ledgerer import LedgerToScript, ScriptToLedger, URLedger, link_ledgers


def verify_ledger_across_all_12_langs(
    label: str, ledger: URLedger, gpu_lowerer: GPUTensorLowerer
) -> dict[str, object]:
    table = RelationalLedgerTable(ledger)
    hist = table.depth_histogram()
    last_metrics = []
    for lang in ALL_12_LANGS:
        cpu_code = LedgerToScript.emit(ledger, lang)
        gpu_res = gpu_lowerer.lower(table, lang)
        gpu_code = gpu_res["code"]
        assert gpu_code == cpu_code, (
            f"[{label} -> {lang}] Mismatch!\n--- GPU ---\n{gpu_code}\n--- CPU ---\n{cpu_code}"
        )
        last_metrics = gpu_res["pass_metrics"]
    print(
        f"[PASS] {label:32s}: 12/12 languages 100% byte-identical to CPU lowerer | "
        f"nodes={table.nodes.shape[0]:4d} | max_depth={table.max_depth:2d} | "
        f"gpu_passes={len(last_metrics):2d} | depth_hist={hist}"
    )
    return {"nodes": int(table.nodes.shape[0]), "max_depth": table.max_depth, "passes": last_metrics}


def main() -> None:
    lut = DictLUT(device="cpu")
    gpu_lowerer = GPUTensorLowerer(lut)

    qf_dir = HERE / "roundtrip_steps"
    s0 = (qf_dir / "00_quickfox.py").read_text(encoding="utf-8")
    l_c1 = ScriptToLedger.parse(s0, "python")
    verify_ledger_across_all_12_langs("Cycle-1 00_quickfox.py", l_c1, gpu_lowerer)

    s2 = (qf_dir / "cycle2" / "12_quickfox.py").read_text(encoding="utf-8")
    l_c2 = ScriptToLedger.parse(s2, "python")
    verify_ledger_across_all_12_langs("Cycle-2 12_quickfox.py", l_c2, gpu_lowerer)

    pc_dir = ROOT / "examples" / "polyglot_codec" / "sources"
    l_pc = link_ledgers([
        ScriptToLedger.parse((pc_dir / "01_c_xxhash32.c").read_text(), "c"),
        ScriptToLedger.parse((pc_dir / "02_go_zigzag.go").read_text(), "go"),
        ScriptToLedger.parse((pc_dir / "03_rust_fxfold.rs").read_text(), "rust"),
        ScriptToLedger.parse((pc_dir / "04_py_telemetry_frame.py").read_text(), "python"),
    ])
    verify_ledger_across_all_12_langs("Linked 4-Lang Polyglot Codec", l_pc, gpu_lowerer)

    batch_funcs = []
    for k in range(15):
        for fn in l_c2.functions:
            fn_copy = copy.deepcopy(fn)
            fn_copy.func_name = f"{fn.func_name}_b{k}"
            batch_funcs.append(fn_copy)
    l_batch = copy.deepcopy(l_c2)
    l_batch.functions = batch_funcs
    verify_ledger_across_all_12_langs("Batch 75-Func Cycle-2 Module", l_batch, gpu_lowerer)


if __name__ == "__main__":
    main()
