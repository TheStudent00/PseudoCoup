"""
coverage.py — the worklist report. Enumerates every named grammar kind, assigns
each a bucket, and prints the UNROUTED set: exactly what still needs a handler.
Drive UNROUTED to zero. This is the "nothing hiding" instrument.

Usage:  python3 tools/pseudokotlin/coverage.py
"""
import os
import sys
from collections import Counter

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import parse  # noqa: E402
import classify  # noqa: E402
from transpiler import KtToPy  # noqa: E402


def report():
    kinds = sorted(parse.named_kinds())
    routed = KtToPy.routed_kinds()
    rows = [(k, classify.bucket(k, routed)) for k in kinds]
    tally = Counter(b for _, b in rows)

    print(f"grammar named kinds: {len(kinds)}")
    print("  " + " · ".join(f"{b} {tally.get(b, 0)}" for b in
                            ("ROUTED", "container", "wrap", "out-of-scope", "UNROUTED")))
    unrouted = [k for k, b in rows if b == "UNROUTED"]
    print(f"\nUNROUTED ({len(unrouted)}) — the worklist:")
    for k in unrouted:
        print(f"    {k}")
    return tally


if __name__ == "__main__":
    report()
