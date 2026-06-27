#!/usr/bin/env python3
"""
transpile_app.py -- run the literal K->Py transpiler over the WHOLE WFL app and
place the 1:1 output in WFL_MixingCenter (generalizes run_all.py, which only did
*ViewModel.kt -> build/literal).

Mirrors the Kotlin package tree: every <app>/<pkg>/Foo.kt -> <OUT>/<pkg>/Foo.py
(literal Kotlin names kept). Reports per-file transpile + py-compile status.

Usage:
    python3 tools/transpiler/transpile_app.py [APP_ROOT] [OUT_DIR]

Defaults:
    APP_ROOT = ~/Programming/WFL/app/src/main/java/com/sara/workoutforlife
    OUT_DIR  = ~/Programming/WFL_MixingCenter
"""
import ast
import glob
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from literal_transpiler import LiteralVisitor  # noqa: E402

DEFAULT_APP = os.path.expanduser(
    "~/Programming/WFL/app/src/main/java/com/sara/workoutforlife")
DEFAULT_OUT = os.path.expanduser("~/Programming/WFL_MixingCenter")


def main():
    app_root = os.path.abspath(sys.argv[1]) if len(sys.argv) > 1 else DEFAULT_APP
    out_dir = os.path.abspath(sys.argv[2]) if len(sys.argv) > 2 else DEFAULT_OUT
    kt_files = sorted(glob.glob(os.path.join(app_root, "**", "*.kt"), recursive=True))
    if not kt_files:
        print(f"No .kt found under {app_root}")
        return 1

    total = written = compile_ok = transpile_err = compile_err = 0
    t_fails, c_fails = [], []
    for kt in kt_files:
        total += 1
        rel = os.path.relpath(kt, app_root)[:-3] + ".py"   # mirror pkg tree, .kt->.py
        out = os.path.join(out_dir, rel)
        try:
            with open(kt, "rb") as f:
                code = LiteralVisitor().transpile(f.read())
        except Exception as e:                              # transpiler itself blew up
            transpile_err += 1
            t_fails.append((rel, f"{type(e).__name__}: {e}"))
            continue
        os.makedirs(os.path.dirname(out), exist_ok=True)
        with open(out, "w") as f:
            f.write(code)
        written += 1
        try:
            ast.parse(code)
            compile_ok += 1
        except SyntaxError as e:
            compile_err += 1
            c_fails.append((rel, f"line {e.lineno}: {e.msg}"))

    print(f"app:  {app_root}")
    print(f"out:  {out_dir}")
    print(f"\n{total} .kt files")
    print(f"  written .py        : {written}")
    print(f"  py-compile OK      : {compile_ok}/{written}")
    print(f"  transpiler errored : {transpile_err}")
    print(f"  emitted-but-invalid: {compile_err}")
    if t_fails:
        print("\nTRANSPILER ERRORS (file skipped, no .py written):")
        for rel, msg in t_fails[:40]:
            print(f"  {rel}: {msg}")
        if len(t_fails) > 40:
            print(f"  ... +{len(t_fails) - 40} more")
    if c_fails:
        print("\nEMITTED INVALID PYTHON (written but won't parse):")
        for rel, msg in c_fails[:40]:
            print(f"  {rel}: {msg}")
        if len(c_fails) > 40:
            print(f"  ... +{len(c_fails) - 40} more")
    return 0


if __name__ == "__main__":
    sys.exit(main())
