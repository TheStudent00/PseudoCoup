"""
externals.py — the build-time external-reference checklist. Walks every file's imports (RESOLVE),
classifies each external name by origin, and asks the REGISTRY whether a wrapper covers it. This is the
deterministic replacement for the runtime load-gate hunt: every external dependency, and whether it is
wrapped, known before the code runs.

A file is "UI-layer" if it sits under ui/ or navigation/ -- those defer with the UI phase, so their
external gaps are the UI's runtime work, separate from the non-UI foundation's.

  python3 externals.py            # the checklist
"""
import os
import re
import sys
import glob
import builtins
import collections

BUILTINS = set(dir(builtins))   # kotlin.math.abs etc. resolve to a Python builtin -> already covered

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from parse import parse  # noqa: E402
import resolve           # noqa: E402
import registry          # noqa: E402

KT = os.path.expanduser(
    "~/Programming/WFL_MixingCenter/WFL/app/src/main/java/com/sara/workoutforlife")
PY = os.path.expanduser("~/Programming/WFL_MixingCenter")


def _is_ui(path):
    return "/ui/" in path or "/navigation/" in path


def referenced_in_output():
    """Bare names (not attribute accesses) that survive into the non-UI Python output. A Kotlin import
    whose name is dropped by translation -- a Room/Hilt annotation like @Dao or @Inject -- never appears
    here, so it isn't a real runtime gap; a value/function used in a method body (MutableStateFlow,
    Context, LocalDate) does. Heuristic, but it separates dropped annotations from live references."""
    names = set()
    for f in glob.glob(os.path.join(PY, "**", "*.py"), recursive=True):
        if "/WFL/" in f or "/__pycache__/" in f or _is_ui(f):
            continue
        names |= set(re.findall(r"(?<![.\w])([A-Za-z_]\w*)", open(f).read()))
    return names


def scan():
    """-> list of (origin, name, fqn, is_ui) for every external import across the app."""
    rows = []
    for path in glob.glob(os.path.join(KT, "**", "*.kt"), recursive=True):
        if os.sep + "build" + os.sep in path or path.endswith("Test.kt"):
            continue
        h = resolve.file_header(parse(open(path, "rb").read()).root_node)
        ui = _is_ui(path)
        for name, fqn in h["imports"].items():
            o = resolve.origin(fqn)
            if o != "app":
                rows.append((o, name, fqn, ui))
    return rows


def main():
    rows = scan()
    prov = registry.provided()
    live = referenced_in_output()                # names that survive into the non-UI Python

    # (origin, name) -> {covered, live (referenced in non-UI output), ui_only}
    names = {}
    for origin, name, fqn, ui in rows:
        rec = names.setdefault((origin, name),
                               {"covered": name in prov or name in BUILTINS,
                                "live": name in live, "ui_only": True})
        if not ui:
            rec["ui_only"] = False

    by_origin = collections.defaultdict(lambda: [0, 0, 0])   # origin -> [imported, wrapped, real_gaps]
    for (origin, name), r in names.items():
        agg = by_origin[origin]
        agg[0] += 1
        agg[1] += 1 if r["covered"] else 0
        if r["live"] and not r["covered"] and not r["ui_only"]:   # imported by a non-UI file, live, unwrapped
            agg[2] += 1

    print(f"{'origin':22s} {'import':>7} {'wrapped':>8} {'live gap':>9}")
    tot = [0, 0, 0]
    for origin in sorted(by_origin, key=lambda k: -by_origin[k][2]):
        d, c, rg = by_origin[origin]
        print(f"  {origin:20s} {d:7d} {c:8d} {rg:9d}")
        for i in range(3):
            tot[i] += (d, c, rg)[i]
    print(f"  {'TOTAL':20s} {tot[0]:7d} {tot[1]:8d} {tot[2]:9d}")

    real = sorted({(o, n) for (o, n), r in names.items()
                   if r["live"] and not r["covered"] and not r["ui_only"]})
    print(f"\nREAL non-UI foundation gaps -- external names used in the foundation's Python, unwrapped: "
          f"{len(real)}")
    cur = None
    for o, n in real:
        if o != cur:
            print(f"  {o}:"); cur = o
        print(f"      {n}")
    dropped = sorted({n for (o, n), r in names.items()
                      if not r["live"] and not r["covered"] and not r["ui_only"]})
    print(f"\nimported but DROPPED by translation (annotations etc., not runtime gaps): {len(dropped)}")
    print("   " + ", ".join(dropped[:20]) + (" ..." if len(dropped) > 20 else ""))
    print("\nUI-layer externals (compose/hilt/nav) defer with the UI -- a known list, not counted above.")


if __name__ == "__main__":
    main()
