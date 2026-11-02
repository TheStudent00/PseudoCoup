"""cli -- Command-line interface for PseudoCoup (transpile, roundtrip, quickfox)."""
from __future__ import annotations
import argparse
from pathlib import Path
from .ledgerer import ScriptToLedger, LedgerToScript


def main() -> None:
    parser = argparse.ArgumentParser(description="PseudoCoup Universal Cross-Language Transpiler")
    parser.add_argument("--source", type=str, required=True, help="Path to source script")
    parser.add_argument("--source-lang", type=str, default="python", help="Source language")
    parser.add_argument("--target-lang", type=str, required=True, help="Target language")
    parser.add_argument("--roundtrip-cycles", type=int, default=0, help="Run N roundtrip cycles")
    args = parser.parse_args()

    script = Path(args.source).read_text(encoding="utf-8")
    ledger = ScriptToLedger.parse(script, args.source_lang)
    emitted = LedgerToScript.emit(ledger, args.target_lang)

    if args.roundtrip_cycles <= 0:
        print(emitted)
        return

    cur_s = script
    for c in range(1, args.roundtrip_cycles + 1):
        t_code = LedgerToScript.emit(ScriptToLedger.parse(cur_s, args.source_lang), args.target_lang)
        s_code = LedgerToScript.emit(ScriptToLedger.parse(t_code, args.target_lang), args.source_lang)
        print(f"// --- Cycle {c} Target ({args.target_lang}) ---\n{t_code}\n")
        print(f"// --- Cycle {c} Source ({args.source_lang}) ---\n{s_code}\n")
        cur_s = s_code


if __name__ == "__main__":
    main()
