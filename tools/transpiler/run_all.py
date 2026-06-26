#!/usr/bin/env python3
"""
run_all.py -- fleet-wide transpile + compile gate (the committed form of the
ad-hoc loop in log_35/36).

Transpiles every *ViewModel.kt under the WFL source tree with the literal
transpiler, then checks each emitted file on three axes py_compile can't see on
its own. Prints a per-file table + totals and EXITS 1 (gates CI) if any of:
  - compile      : output is invalid Python
  - rt-fatal     : `self.x = ...` at class-body indent (NameError on instantiate)
  - silent-drops : operator calls that lost their trailing lambda (`.map()`,
                   `combine(...)()`) -- dropped logic that should be a loud marker
Also reports (non-gating) `todos` (loud TODO markers) and `enum?` (heuristic:
`Class.CONST` refs to in-file classes that declare no such constant).

Usage:
    python3 tools/transpiler/run_all.py [WFL_UI_DIR]

Default WFL_UI_DIR: ~/Programming/WFL/app/src/main/java/com/sara/workoutforlife/ui
"""

import glob
import os
import py_compile
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from literal_transpiler import LiteralVisitor  # noqa: E402

DEFAULT_UI = os.path.expanduser(
    "~/Programming/WFL/app/src/main/java/com/sara/workoutforlife/ui")
OUT_DIR = os.path.join(HERE, "..", "..", "build", "literal")


def transpile_one(kt_path):
    with open(kt_path, "rb") as f:
        code = LiteralVisitor().transpile(f.read())
    os.makedirs(OUT_DIR, exist_ok=True)
    out = os.path.join(OUT_DIR, os.path.basename(kt_path).replace(".kt", ".py"))
    with open(out, "w") as f:
        f.write(code)
    return out, code


def count_todos(code):
    return sum(code.count(tok) for tok in
               ("__TODO_EXPR__", "TODO_UNHANDLED_KOTLIN_NODE",
                "TODO_UNRESOLVED_ASSIGN_TARGET", "_RAW_ITERABLE_TODO_"))


def classbody_self(code):
    # `self.x = ...` at class-body indent (4 spaces) references `self` before any
    # instance exists -> NameError at class-definition time. py_compile does NOT
    # catch this; it's the bug __init__ generation must fix. Count it so the gate
    # reflects "runnable", not just "parses".
    return sum(1 for ln in code.splitlines()
               if ln.startswith("    self.") and not ln.startswith("        "))


# Operators that, in this codebase, essentially always take a trailing lambda.
# An empty-arg call means the lambda was SILENTLY dropped -- worse than a loud
# TODO, and invisible to py_compile. (Excludes ops with legit no-arg forms like
# any/all/count/first.)
_LAMBDA_OPS = ("map", "filter", "flatMapLatest", "mapLatest", "onEach", "let",
               "also", "apply", "run", "takeIf", "takeUnless", "groupBy",
               "associateBy", "sortedBy", "sortedByDescending", "forEach",
               "flatMap", "mapNotNull", "filterNot", "fold", "partition", "sumOf",
               "minByOrNull", "maxByOrNull", "indexOfFirst", "combine")
_EMPTY_LAMBDA_OP = re.compile(r"\b(" + "|".join(_LAMBDA_OPS) + r")\(\)")
_STRAY_CALL = re.compile(r"\)\(\)")            # `combine(...)()` -- transform dropped
_ENUM_REF = re.compile(r"\b([A-Z][A-Za-z0-9]*)\.([A-Z][A-Z0-9_]+)\b")


def silent_drops(code):
    # the dropped-trailing-lambda signature (finding #3, log_39)
    return len(_EMPTY_LAMBDA_OP.findall(code)) + len(_STRAY_CALL.findall(code))


def dropped_enum_refs(code):
    # `Class.UPPER_CONST` where Class is defined in-file but never declares that
    # constant -> dropped enum entry -> AttributeError at runtime (finding #2).
    # Heuristic (informational, not gating): class-level constants are lines like
    # `    UPPER = ...` under a `class X:`.
    classes = set(re.findall(r"^class ([A-Za-z0-9_]+):", code, re.M))
    defined = set(re.findall(r"^    ([A-Z][A-Z0-9_]+)\s*=", code, re.M))
    missing = {f"{c}.{m}" for c, m in _ENUM_REF.findall(code)
               if c in classes and m not in defined}
    return len(missing)


def main():
    ui_dir = sys.argv[1] if len(sys.argv) > 1 else DEFAULT_UI
    kt_files = sorted(glob.glob(os.path.join(ui_dir, "**", "*ViewModel.kt"), recursive=True))
    if not kt_files:
        print(f"No *ViewModel.kt found under {ui_dir}")
        return 1

    ok = bad = todo_total = rtfatal_total = silent_total = enum_total = 0
    failures = []
    print(f"{'screen':38s} {'compile':8s} {'todos':>6s} {'rt-fatal':>9s} {'silent':>7s} {'enum?':>6s}")
    print("-" * 80)
    for kt in kt_files:
        name = os.path.basename(kt)[:-3]
        out, code = transpile_one(kt)
        todos = count_todos(code)
        rtfatal = classbody_self(code)
        silent = silent_drops(code)
        enums = dropped_enum_refs(code)
        todo_total += todos
        rtfatal_total += rtfatal
        silent_total += silent
        enum_total += enums
        try:
            py_compile.compile(out, doraise=True)
            ok += 1
            status = "OK"
        except py_compile.PyCompileError as e:
            bad += 1
            status = "FAIL"
            failures.append((name, str(e).strip().splitlines()[-1][:70]))
        print(f"{name:38s} {status:8s} {todos:6d} {rtfatal:9d} {silent:7d} {enums:6d}")

    print("-" * 80)
    print(f"COMPILE OK {ok}/{ok + bad}   residual TODOs: {todo_total}   "
          f"rt-fatal: {rtfatal_total}   silent-drops: {silent_total}   enum-refs?: {enum_total}")
    if failures:
        print("\nCOMPILE FAILURES:")
        for name, msg in failures:
            print(f"  {name}: {msg}")
    if rtfatal_total:
        print(f"\nNOT RUNNABLE: {rtfatal_total} class-body `self.` (needs __init__ generation).")
    if silent_total:
        print(f"\nSILENT DROPS: {silent_total} operator calls lost their trailing lambda "
              f"(e.g. `.map()`, `combine(...)()`). Should be a loud marker, never empty args.")
    if enum_total:
        print(f"\nENUM REFS (heuristic, non-gating): {enum_total} `Class.CONST` refs to in-file "
              f"classes that declare no such constant -> likely dropped enum entries (AttributeError).")
    # gating: compile + the two runtime-fatal-but-py_compile-blind classes
    if failures or rtfatal_total or silent_total:
        return 1
    print("\nGREEN: valid Python, no class-body self., no dropped operator lambdas.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
