"""
test_coverage.py — the exhaustiveness gate (the OCaml-match analog).

Every named grammar kind must be classified into exactly one bucket. Two checks:
  1. consistency  — no kind is both ROUTED and container/out-of-scope (always on).
  2. exhaustiveness — no kind is UNROUTED (flips to a hard assert at the end of P1;
     until then it reports the worklist count without failing the build).
"""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))  # the pseudokotlin package dir
import parse  # noqa: E402
import classify  # noqa: E402
from transpiler import KtToPy  # noqa: E402

EXHAUSTIVENESS_ENFORCED = False  # flip True at end of P1


def test_no_kind_double_classified():
    routed = KtToPy.routed_kinds()
    overlap = routed & (classify.CONTAINER | classify.OUT_OF_SCOPE | classify.WRAP)
    assert not overlap, f"kinds both routed and classified elsewhere: {sorted(overlap)}"


def test_exhaustiveness():
    kinds = parse.named_kinds()
    classified = (KtToPy.routed_kinds() | classify.CONTAINER
                  | classify.WRAP | classify.OUT_OF_SCOPE)
    unrouted = sorted(kinds - classified)
    if EXHAUSTIVENESS_ENFORCED:
        assert not unrouted, f"unrouted grammar kinds: {unrouted}"
    else:
        # P0/P1 in progress: surface the worklist, don't fail the build yet.
        print(f"[coverage] {len(unrouted)} kinds still UNROUTED (worklist)")
