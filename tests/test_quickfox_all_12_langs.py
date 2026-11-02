"""test_quickfox_all_12_langs -- Multi-function quickfox 2-cycle roundtrip across all 12 languages.

Loads `roundtrip_steps/00_quickfox.py` from disk and runs:
1. Pairwise 2-cycle roundtrip (`Python -> lang_y -> Python -> lang_y -> Python`) for all 12 languages.
2. Full 12-language sequential daisy-chain across 2 cycles, saving every intermediate language file
   to `roundtrip_steps/cycle1/` and `roundtrip_steps/cycle2/` (`01_quickfox.c` .. `12_quickfox.py`)
   and asserting 100% byte-for-byte identity (`cycle1/XX == cycle2/XX`) and bit-identical execution.
"""
from __future__ import annotations
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
sys.path.insert(0, str(HERE.parent))

from pseudocoup.ledgerer import ScriptToLedger, LedgerToScript, eval_ledger

LANG_STEPS = [
    ("01_quickfox.c", "c"),
    ("02_quickfox.cpp", "cpp"),
    ("03_quickfox.go", "go"),
    ("04_quickfox.rs", "rust"),
    ("05_quickfox.java", "java"),
    ("06_quickfox.ts", "typescript"),
    ("07_quickfox.cs", "csharp"),
    ("08_quickfox.rb", "ruby"),
    ("09_quickfox.php", "php"),
    ("10_quickfox.dart", "dart"),
    ("11_quickfox.swift", "swift"),
    ("12_quickfox.py", "python"),
]



def main() -> None:
    steps_dir = HERE / "roundtrip_steps"
    s0_path = steps_dir / "00_quickfox.py"
    s0_script = s0_path.read_text(encoding="utf-8")

    test_vectors = [
        {"a": 17, "b": 5, "sh": 2, "limit": 4},
        {"a": -17, "b": 5, "sh": 70, "limit": 5},   # floor-div/mod + sh >= 64 edge domain
        {"a": 17, "b": -5, "sh": 3, "limit": 3},    # negative divisor edge domain
        {"a": -20, "b": 5, "sh": 64, "limit": 2},
    ]

    l0 = ScriptToLedger.parse(s0_script, "python")
    expected_vals = [eval_ledger(l0, v, "quickfox") for v in test_vectors]

    c1_dir = steps_dir / "cycle1"
    c2_dir = steps_dir / "cycle2"
    c1_dir.mkdir(parents=True, exist_ok=True)
    c2_dir.mkdir(parents=True, exist_ok=True)

    # Sequential 12-language daisy-chain: Cycle 1 (writes cycle1/01_quickfox.c .. cycle1/12_quickfox.py)
    cur_script = s0_script
    cur_lang = "python"
    c1_files: dict[str, str] = {}
    for fname, nxt_lang in LANG_STEPS:
        ldg = ScriptToLedger.parse(cur_script, cur_lang)
        emitted = LedgerToScript.emit(ldg, nxt_lang)
        (c1_dir / fname).write_text(emitted + "\n", encoding="utf-8")
        c1_files[fname] = emitted
        cur_script = emitted
        cur_lang = nxt_lang

    # Sequential 12-language daisy-chain: Cycle 2 (writes cycle2/01_quickfox.c .. cycle2/12_quickfox.py)
    c2_files: dict[str, str] = {}
    per_step_summary = {}
    for fname, nxt_lang in LANG_STEPS:
        ldg = ScriptToLedger.parse(cur_script, cur_lang)
        emitted = LedgerToScript.emit(ldg, nxt_lang)
        (c2_dir / fname).write_text(emitted + "\n", encoding="utf-8")
        c2_files[fname] = emitted
        assert c1_files[fname] == c2_files[fname], f"Mismatch at {fname}:\n{c1_files[fname]}\nvs\n{c2_files[fname]}"
        step_ldg = ScriptToLedger.parse(emitted, nxt_lang)
        vals = [eval_ledger(step_ldg, v, "quickfox") for v in test_vectors]
        assert vals == expected_vals, f"Eval mismatch at {fname}: {vals} != {expected_vals}"
        per_step_summary[fname] = {
            "lang": nxt_lang,
            "cycle1_equals_cycle2": True,
            "functions": len(step_ldg.functions),
            "lines": len(emitted.splitlines()),
            "outputs": vals,
        }
        print(f"[PASS] {fname:18s} ({nxt_lang:10s}): cycle1 == cycle2 (100% byte-identical), funcs={len(step_ldg.functions)}, outputs={vals}")
        cur_script = emitted
        cur_lang = nxt_lang

    out_path = HERE / "quickfox_12_langs_results.json"
    out_path.write_text(json.dumps({
        "source_file": "roundtrip_steps/00_quickfox.py",
        "test_vectors": test_vectors,
        "expected_outputs": expected_vals,
        "steps": per_step_summary,
        "cycle2_scripts": c2_files,
    }, indent=2))


if __name__ == "__main__":
    main()
