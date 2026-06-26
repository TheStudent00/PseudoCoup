#!/usr/bin/env python3
"""
run_all.py -- fleet-wide transpile + compile gate (the committed form of the
ad-hoc loop in log_35/36).

Transpiles every *ViewModel.kt under the WFL source tree with the literal
transpiler, then runs `py_compile` on each emitted file. Prints a per-file
table + totals and EXITS 1 if any output is invalid Python, so this can gate CI.

Usage:
    python3 tools/transpiler/run_all.py [WFL_UI_DIR]

Default WFL_UI_DIR: ~/Programming/WFL/app/src/main/java/com/sara/workoutforlife/ui
"""

import glob
import os
import py_compile
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


def main():
    ui_dir = sys.argv[1] if len(sys.argv) > 1 else DEFAULT_UI
    kt_files = sorted(glob.glob(os.path.join(ui_dir, "**", "*ViewModel.kt"), recursive=True))
    if not kt_files:
        print(f"No *ViewModel.kt found under {ui_dir}")
        return 1

    ok = bad = todo_total = 0
    failures = []
    print(f"{'screen':40s} {'compile':8s} {'todos':>6s}")
    print("-" * 56)
    for kt in kt_files:
        name = os.path.basename(kt)[:-3]
        out, code = transpile_one(kt)
        todos = count_todos(code)
        todo_total += todos
        try:
            py_compile.compile(out, doraise=True)
            ok += 1
            status = "OK"
        except py_compile.PyCompileError as e:
            bad += 1
            status = "FAIL"
            failures.append((name, str(e).strip().splitlines()[-1][:70]))
        print(f"{name:40s} {status:8s} {todos:6d}")

    print("-" * 56)
    print(f"COMPILE OK {ok}/{ok + bad}   residual TODO markers: {todo_total}")
    if failures:
        print("\nFAILURES:")
        for name, msg in failures:
            print(f"  {name}: {msg}")
        return 1
    print("All ViewModels emit valid Python.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
