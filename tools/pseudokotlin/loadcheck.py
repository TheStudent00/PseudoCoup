"""loadcheck.py — the foundation's *load* gate (the third runnability gate, alongside the
parse gate `build_mixingcenter.py` and the logic gate `oracle.py`).

Execs every non-UI foundation .py in one kotlin_rt-seeded namespace (multipass for ordering)
and reports how many load clean vs. the external names that block the rest. A NameError blocker
is a missing runtime name (a platform shim the foundation needs); a non-NameError blocker is a
transpiler/logic defect to fix. UI files are excluded -- they need the Compose runtime (deferred).

  python3 loadcheck.py            # summary + blocking names
"""
import os, sys, glob, collections

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import runtime.kotlin_rt as rt

ROOT = os.path.expanduser("~/Programming/WFL_MixingCenter")


def main():
    files = [f for f in glob.glob(ROOT + "/**/*.py", recursive=True)
             if "/WFL/" not in f and "/__pycache__/" not in f]
    ui = [f for f in files if "/ui/" in f]
    core = [f for f in files if "/ui/" not in f]                 # the non-UI foundation

    ns = {k: getattr(rt, k) for k in dir(rt) if not k.startswith("_")}
    pending = {f: open(f).read() for f in core}
    loaded, errs = [], {}
    while pending:
        progressed, errs = False, {}
        for f, src in list(pending.items()):
            try:
                exec(compile(src, f, "exec"), ns)
                loaded.append(f); del pending[f]; progressed = True
            except Exception as e:                               # noqa: BLE001
                errs[f] = f"{type(e).__name__}: {e}"
        if not progressed:
            break

    print(f"non-UI foundation files : {len(core)}")
    print(f"  load clean (kotlin_rt) : {len(loaded)}")
    print(f"  blocked                : {len(pending)}")
    print(f"(UI files, deferred)     : {len(ui)}")

    missing = collections.Counter()
    for msg in errs.values():
        if "NameError" in msg and "'" in msg:
            missing[msg.split("'")[1]] += 1
    if missing:
        print("\nblocking names -> need a platform shim:")
        for name, n in missing.most_common(20):
            print(f"  {n:3d}  {name}")
    defects = {f: m for f, m in errs.items() if "NameError" not in m}
    if defects:
        print("\nnon-NameError blockers (transpiler/logic defects to fix):")
        for f, msg in defects.items():
            print(f"  {os.path.relpath(f, ROOT)}: {msg[:90]}")


if __name__ == "__main__":
    main()
