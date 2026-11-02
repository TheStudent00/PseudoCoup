#!/usr/bin/env python3
"""build_poly_flex_ui.py -- Cross-Platform Reactive UI Layout & State Engine (`PolyFlexUI`).

Ingests 4 polyglot UI subsystem modules:
  1. 01_c_rect_geometry.c        (C: Rect64 packing, safe-area insets, scissor clip, hit-testing)
  2. 02_dart_flexbox_solver.dart (Dart/Flutter: BoxConstraints, Flexbox Row/Column, Scaffold layout)
  3. 03_rust_scroll_physics.rs   (Rust: iOS BouncingScrollPhysics vs Android ClampingScrollPhysics)
  4. 04_py_ui_reducer.py         (Python: Elm/Redux UI state machine & laptop-to-mobile simulator)

Links via `link_ledgers`, lowers to all 12 languages via BOTH CPU (`LedgerToScript`)
and GPU (`GPUTensorLowerer`), verifies 100% byte-identical output, and writes `emitted/`.
"""
from __future__ import annotations
from pathlib import Path
import sys

REPO_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO_ROOT))

from pseudocoup.ledgerer.ur_ledger import ScriptToLedger, LedgerToScript, link_ledgers
from pseudocoup.gpu_lowerer import DictLUT, RelationalLedgerTable, GPUTensorLowerer, ALL_12_LANGS

HERE = Path(__file__).resolve().parent
SRC_DIR = HERE / "sources"
OUT_DIR = HERE / "emitted"

EXT_MAP = {
    "python": "py", "c": "c", "cpp": "cpp", "rust": "rs",
    "go": "go", "typescript": "ts", "java": "java", "csharp": "cs",
    "dart": "dart", "swift": "swift", "php": "php", "ruby": "rb",
}


def build_unified_ui_ledger():
    specs = [
        ("01_c_rect_geometry.c", "c"),
        ("02_dart_flexbox_solver.dart", "dart"),
        ("03_rust_scroll_physics.rs", "rust"),
        ("04_py_ui_reducer.py", "python"),
    ]
    ledgers = [ScriptToLedger.parse((SRC_DIR / fname).read_text(), lang) for fname, lang in specs]
    return link_ledgers(ledgers)


def main() -> int:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    unified = build_unified_ui_ledger()
    lut = DictLUT(device="cpu")
    rel = RelationalLedgerTable(unified, device="cpu")
    gpu = GPUTensorLowerer(lut)

    print(f"=== PolyFlexUI Unified URLedger ===")
    print(f"Functions linked     : {len(unified.functions)} across C, Dart/Flutter, Rust, Python")
    print(f"Holder bridges       : {len(unified.bridge_events)} automatic URHolderCast nodes")
    print(f"Relational nodes (N) : {rel.nodes.shape[0]} rows x {rel.nodes.shape[1]} cols")
    print(f"GPU pass depth       : max_depth = {rel.max_depth} ({rel.max_depth + 1} parallel passes)")

    for lang in ALL_12_LANGS:
        cpu_code = LedgerToScript.emit(unified, lang)
        gpu_res = gpu.lower(rel, lang)
        assert gpu_res["code"] == cpu_code, f"GPU/CPU mismatch on {lang}"
        out_file = OUT_DIR / f"poly_flex_ui.{EXT_MAP[lang]}"
        out_file.write_text(cpu_code + "\n", encoding="utf-8")
        print(f"  [{lang:10s}] -> {out_file.name:18s} ({len(cpu_code):5d} B) | GPU == CPU PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
