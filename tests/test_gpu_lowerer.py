"""test_gpu_lowerer -- Verifies the GPU-Friendly Lowerer across `lang_models` and Cycle-2 `URLedger`."""
from __future__ import annotations

import os
from pathlib import Path
import subprocess
import sys
import tempfile

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from pseudocoup.gpu_lowerer import (
    BRANCHLESS_RISCV_TEMPLATES,
    GPULedgerLowerer,
    audit_and_lower_lang_model_units,
    prove_branchless_identities_z3,
)
from pseudocoup.hub.unit_vm import RiscvUnitVM
from pseudocoup.ledgerer import ScriptToLedger, eval_ledger, link_ledgers


def main() -> None:
    # 1. Z3 formal proofs of all 7 branchless GPU ALU identities
    z3_proofs = prove_branchless_identities_z3()
    assert len(z3_proofs) == 7

    # 2. PseudoArch lang_models audit + RiscvUnitVM execution of branchless RISC-V templates
    audit = audit_and_lower_lang_model_units()
    assert audit["total_units"] == 12164 and audit["warp_divergent_units_eliminated"] == 2156
    vm = RiscvUnitVM()
    for name, words in BRANCHLESS_RISCV_TEMPLATES.items():
        vm.reset()
        vm.set_reg("a0", -17)
        vm.set_reg("a1", 5)
        vm.set_reg("t0", 1)
        vm.set_reg("t1", 100)
        vm.set_reg("t2", 200)
        res = vm.execute_unit(words)
        assert res["steps"] == len(words)

    # 3. Lower Cycle-2 quickfox (5 functions) to branchless GPU kernels
    qf_src = (HERE / "roundtrip_steps" / "00_quickfox.py").read_text(encoding="utf-8")
    qf_ledger = ScriptToLedger.parse(qf_src, "python")
    qf_gpu = GPULedgerLowerer.lower_ledger_to_gpu(qf_ledger, "c")

    out_dir = ROOT / "examples" / "gpu_kernels"
    out_dir.mkdir(parents=True, exist_ok=True)
    qf_py = GPULedgerLowerer.emit_branchless_python(qf_ledger)
    qf_c = GPULedgerLowerer.emit_simd_c(qf_ledger)
    qf_cu = GPULedgerLowerer.emit_cuda_kernel(qf_ledger)
    qf_wgsl = GPULedgerLowerer.emit_wgsl_shader(qf_ledger)

    (out_dir / "quickfox_branchless.py").write_text(qf_py + "\n", encoding="utf-8")
    (out_dir / "quickfox_simd.c").write_text(qf_c + "\n", encoding="utf-8")
    (out_dir / "quickfox_kernel.cu").write_text(qf_cu, encoding="utf-8")
    (out_dir / "quickfox_shader.wgsl").write_text(qf_wgsl, encoding="utf-8")

    # Verify zero `if` statements and zero `? :` ternaries in quickfox_branchless.py & quickfox_simd.c
    assert "if " not in qf_py and "?" not in qf_c and "if (" not in qf_c

    vecs = [(17, 5, 2, 4), (-17, 5, 70, 5), (17, -5, 3, 3), (-20, 5, 64, 2)]
    ns_qf: dict = {}
    exec(qf_py, ns_qf)
    py_vals = [int(ns_qf["quickfox"](*v)) for v in vecs]
    assert py_vals == [717, 3556, -67, 74], f"Expected [717, 3556, -67, 74], got {py_vals}"

    # 4. Lower 4-language Polyglot Codec to branchless GPU kernels
    pc_dir = ROOT / "examples" / "polyglot_codec" / "sources"
    pc_ledgers = [
        ScriptToLedger.parse((pc_dir / "01_c_xxhash32.c").read_text(), "c"),
        ScriptToLedger.parse((pc_dir / "02_go_zigzag.go").read_text(), "go"),
        ScriptToLedger.parse((pc_dir / "03_rust_fxfold.rs").read_text(), "rust"),
        ScriptToLedger.parse((pc_dir / "04_py_telemetry_frame.py").read_text(), "python"),
    ]
    pc_linked = link_ledgers(pc_ledgers)
    pc_py = GPULedgerLowerer.emit_branchless_python(pc_linked)
    pc_c = GPULedgerLowerer.emit_simd_c(pc_linked)
    pc_cu = GPULedgerLowerer.emit_cuda_kernel(pc_linked)
    (out_dir / "polyglot_codec_branchless.py").write_text(pc_py + "\n", encoding="utf-8")
    (out_dir / "polyglot_codec_simd.c").write_text(pc_c + "\n", encoding="utf-8")
    (out_dir / "polyglot_codec_kernel.cu").write_text(pc_cu, encoding="utf-8")

    assert "if " not in pc_py and "?" not in pc_c and "if (" not in pc_c
    ns_pc: dict = {}
    exec(pc_py, ns_pc)
    pc_vals = [int(ns_pc["verify_telemetry_frame"](*f)) for f in [(-42, 108, 7), (0, -9999, 12345), (32767, -32768, 99)]]
    assert pc_vals == [1505307067, 384541866, 1369793549]

    print(f"[PASS] GPU Lowerer: 7/7 Z3 theorems proved, {audit['warp_divergent_units_eliminated']}/{audit['total_units']} warp-divergent units lowered")
    print(f"[PASS] Branchless quickfox (0 `if`/`?:` branches): outputs={py_vals}")
    print(f"[PASS] Branchless polyglot_codec (0 `if`/`?:` branches): outputs={pc_vals}")


if __name__ == "__main__":
    main()
