#!/usr/bin/env python3
"""
build_mixingcenter.py -- run the ADVANCED transpiler (KtToPy) over the whole WFL Kotlin copy
and write the 1:1 Python into WFL_MixingCenter. Replaces the literal-transpiler seed:
this is the "most recent output of the advanced transpiler" half of the MixingCenter.

Input is the meet-in-the-middle Kotlin copy WFL_MixingCenter/WFL/<pkg>/Foo.kt; output mirrors
the package tree at WFL_MixingCenter/<pkg>/Foo.py. Reports per-file transpile + py-compile status.

Usage:
    python3 tools/pseudokotlin/build_mixingcenter.py [APP_ROOT] [OUT_DIR]
"""
import ast
import glob
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from transpiler import KtToPy  # noqa: E402
from nodes import expressions  # noqa: E402

# a py-line -> kt-line marker the transpiler appends to each statement's first line (KtToPy._kt_tag).
# We scan the FINAL module text for these (line numbers are exact here), record the map, and strip
# the markers so the written .py is clean. Stripping a trailing comment never removes a line, so the
# recorded py line numbers stay valid against the written file (which is what the runtime execs).
_MARK_RE = re.compile(r"[ \t]*#@@KTSRC (\d+)[ \t]*$")


def extract_linemap(code):
    """Return (clean_code, {py_line: kt_line}) by pulling the #@@KTSRC markers out of `code`."""
    out_lines, mp = [], {}
    for i, ln in enumerate(code.split("\n"), 1):
        m = _MARK_RE.search(ln)
        if m:
            mp[str(i)] = int(m.group(1))
            ln = ln[:m.start()]
        out_lines.append(ln)
    return "\n".join(out_lines), mp

# a TOP-LEVEL (column-0) extension declaration: `fun Recv.name(` with optional modifiers/generics
_EXT_RE = re.compile(
    r"^(?:(?:public|private|internal|suspend|inline|infix|operator)\s+)*"
    r"fun\s+(?:<[^>\n]+>\s+)?([A-Za-z0-9_.]+)(?:<[^>\n]*>)?\??\.(\w+)\s*\(", re.M)
# receivers that are Python builtins at runtime -- the declarations.py class-patch mechanism
# (`Recv.name = name`) can't reach them, so their call sites go through the runtime's ktext
# dispatcher instead. User-class receivers stay on the patch path (attribute lookup just works,
# and the same extension NAME on several classes would make a bare free-name call ambiguous).
_PRIMITIVE_RECVRS = {"Double", "Float", "Int", "Long", "Short", "Byte", "Number",
                     "String", "CharSequence", "Char", "Boolean"}


def scan_extensions(kt_files):
    """Pre-pass: top-level `fun Recv.name(...)` declarations whose receivers are ALL primitive ->
    the ktext registry (nodes.expressions.EXTENSION_FNS). Mixed/user receivers are excluded: they
    resolve via the class patches the transpiler already emits."""
    by_name = {}
    for kt in kt_files:
        with open(kt) as f:
            for recv, name in _EXT_RE.findall(f.read()):
                by_name.setdefault(name, set()).add(recv.split(".")[-1])
    return {n for n, recvs in by_name.items() if recvs <= _PRIMITIVE_RECVRS}


def scan_last_params(kt_files):
    """Pre-pass: project-wide `fn name -> its LAST parameter name`. Kotlin binds a trailing lambda to the
    callee's last parameter (whatever it is called); a same-file callee is known from self._last_param,
    but a cross-file callee whose last param is (say) `extra` -- invoked with a trailing lambda -- would
    otherwise default to `content=` and blow up as an unexpected kwarg. Reuses the transpiler's own
    tree-sitter param scan (robust to multi-line signatures/defaults), so no fragile regex."""
    from parse import parse
    out = {}
    for kt in kt_files:
        try:
            with open(kt, "rb") as f:
                t = KtToPy()
                t._scan_top_level(parse(f.read()).root_node)
                out.update(t._last_param)
        except Exception:                                      # noqa: BLE001 -- a bad file just contributes nothing
            continue
    return out

DEFAULT_APP = os.path.expanduser(
    "~/Programming/WFL_MixingCenter/WFL/app/src/main/java/com/sara/workoutforlife")
DEFAULT_OUT = os.path.expanduser("~/Programming/WFL_MixingCenter")


def main():
    app_root = os.path.abspath(sys.argv[1]) if len(sys.argv) > 1 else DEFAULT_APP
    out_dir = os.path.abspath(sys.argv[2]) if len(sys.argv) > 2 else DEFAULT_OUT
    kt_files = sorted(glob.glob(os.path.join(app_root, "**", "*.kt"), recursive=True))
    if not kt_files:
        print(f"No .kt found under {app_root}")
        return 1

    expressions.EXTENSION_FNS.update(scan_extensions(kt_files))
    print(f"extension registry: {len(expressions.EXTENSION_FNS)} names")

    expressions.GLOBAL_LAST_PARAM.update(scan_last_params(kt_files))
    print(f"trailing-lambda slot registry: {len(expressions.GLOBAL_LAST_PARAM)} fns")

    total = written = compile_ok = transpile_err = compile_err = 0
    t_fails, c_fails = [], []
    for kt in kt_files:
        total += 1
        rel = os.path.relpath(kt, app_root)[:-3] + ".py"      # mirror pkg tree, .kt -> .py
        out = os.path.join(out_dir, rel)
        try:
            t = KtToPy()
            t._srcmap = True                                   # emit the py->kt line markers
            with open(kt, "rb") as f:
                code = t.transpile(f.read())
            code, linemap = extract_linemap(code)              # strip markers, keep the map
        except Exception as e:                                 # noqa: BLE001 -- transpiler blew up on this file
            transpile_err += 1
            t_fails.append((rel, f"{type(e).__name__}: {e}"))
            continue
        os.makedirs(os.path.dirname(out), exist_ok=True)
        with open(out, "w") as f:
            f.write(code)
        # sidecar: py-line -> kt-line map for the layout inspector's deep links. "kt" is the mirrored
        # Kotlin path relative to the app root, the same tree the inspector reconstructs.
        with open(out + ".linemap.json", "w") as f:
            json.dump({"kt": rel[:-3] + ".kt", "map": linemap}, f)
        written += 1
        try:
            ast.parse(code)
            compile_ok += 1
        except SyntaxError as e:
            compile_err += 1
            c_fails.append((rel, f"line {e.lineno}: {e.msg}"))

    print(f"app:  {app_root}")
    print(f"out:  {out_dir}")
    print(f"\n{total} .kt files (advanced transpiler = KtToPy)")
    print(f"  written .py        : {written}")
    print(f"  py-compile OK      : {compile_ok}/{written}")
    print(f"  transpiler errored : {transpile_err}")
    print(f"  emitted-but-invalid: {compile_err}")
    if t_fails:
        print("\nTRANSPILER ERRORS (file skipped, no .py written):")
        for rel, msg in t_fails[:50]:
            print(f"  {rel}: {msg}")
        if len(t_fails) > 50:
            print(f"  ... +{len(t_fails) - 50} more")
    if c_fails:
        print("\nEMITTED INVALID PYTHON (written but won't parse):")
        for rel, msg in c_fails[:50]:
            print(f"  {rel}: {msg}")
        if len(c_fails) > 50:
            print(f"  ... +{len(c_fails) - 50} more")
    return 0


if __name__ == "__main__":
    sys.exit(main())
