"""Build and verify the 4-language Polyglot Codec & Telemetry Verifier via URLedger linking."""
from __future__ import annotations

import json
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

from pseudocoup.ledgerer.ur_ledger import LedgerToScript, ScriptToLedger, link_ledgers

HERE = os.path.dirname(os.path.abspath(__file__))
SRC_DIR = os.path.join(HERE, "sources")
OUT_DIR = os.path.join(HERE, "emitted")


def main() -> None:
    os.makedirs(OUT_DIR, exist_ok=True)
    sources = [
        ("01_c_xxhash32.c", "c"),
        ("02_go_zigzag.go", "go"),
        ("03_rust_fxfold.rs", "rust"),
        ("04_py_telemetry_frame.py", "python"),
    ]
    ledgers = []
    for fname, lang in sources:
        with open(os.path.join(SRC_DIR, fname), "r", encoding="utf-8") as f:
            ledgers.append(ScriptToLedger.parse(f.read(), lang))

    linked = link_ledgers(ledgers)
    targets = [
        ("python", "polyglot_codec_unified.py"),
        ("c", "polyglot_codec_unified.c"),
        ("rust", "polyglot_codec_unified.rs"),
        ("go", "polyglot_codec_unified.go"),
        ("typescript", "polyglot_codec_unified.ts"),
    ]

    test_frames = [(-42, 108, 7), (0, -9999, 12345), (32767, -32768, 99)]
    outputs_by_lang: dict[str, list[int]] = {}

    for lang, out_name in targets:
        code = LedgerToScript.emit(linked, lang)
        with open(os.path.join(OUT_DIR, out_name), "w", encoding="utf-8") as f:
            f.write(code + "\n")
        rt_py = code if lang == "python" else LedgerToScript.emit(ScriptToLedger.parse(code, lang), "python")
        ns: dict = {}
        exec(rt_py, ns)
        outputs_by_lang[lang] = [int(ns["verify_telemetry_frame"](a, b, s)) for a, b, s in test_frames]

    ref = outputs_by_lang["python"]
    assert all(-1 not in v and v == ref for v in outputs_by_lang.values()), f"Mismatch: {outputs_by_lang}"
    print(f"[PASS] Polyglot Codec (C u32 + Go i32/u32 + Rust i64/u32 + Python i64): {len(linked.bridge_events)} automated bridges")
    for ev in linked.bridge_events:
        print(f"  - {ev['site']} ({ev['from_lang']} {ev['src_holder']} -> {ev['to_lang']} {ev['dst_holder']}): {ev['bridge_kind']} [{ev['riscv64_lo_op']}]")
    print(f"  Verified bit-identical frame digests across {list(outputs_by_lang.keys())}: {ref}")


if __name__ == "__main__":
    main()
