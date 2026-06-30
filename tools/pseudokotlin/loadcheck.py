"""loadcheck.py — the foundation's *load* gate (the third runnability gate, alongside the
parse gate `build_mixingcenter.py` and the logic gate `oracle.py`).

Execs every non-UI foundation .py in one kotlin_rt-seeded namespace (multipass for ordering)
and reports how many load clean vs. the external names that block the rest. A NameError blocker
is a missing runtime name (a platform shim the foundation needs); a non-NameError blocker is a
transpiler/logic defect to fix. UI files are excluded -- they need the Compose runtime (deferred).

  python3 loadcheck.py            # summary + blocking names
"""
import os, sys, glob

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import registry

ROOT = os.path.expanduser("~/Programming/WFL_MixingCenter")


def main():
    files = [f for f in glob.glob(ROOT + "/**/*.py", recursive=True)
             if "/WFL/" not in f and "/__pycache__/" not in f]
    ui = [f for f in files if "/ui/" in f]
    core = [f for f in files if "/ui/" not in f]                 # the non-UI foundation

    ns = dict(registry.namespace())
    pending = {f: open(f).read() for f in files}                 # exec ALL (autostub binds every external)
    loaded, errs = set(), {}
    while pending:
        progressed, errs = False, {}
        for f, src in list(pending.items()):
            try:
                exec(compile(src, f, "exec"), ns)
                loaded.add(f); del pending[f]; progressed = True
            except Exception as e:                               # noqa: BLE001
                errs[f] = f"{type(e).__name__}: {e}"
        if not progressed:
            break

    core_ok = sum(1 for f in core if f in loaded)
    ui_ok = sum(1 for f in ui if f in loaded)
    gaps = {f: errs.get(f, "?") for f in pending}                # whatever never loaded

    print(f"non-UI domain load           : {core_ok} / {len(core)}")
    print(f"ui/ load (inert via autostub): {ui_ok} / {len(ui)}")
    print(f"  real gaps                  : {len(gaps)}")
    for f, msg in list(gaps.items())[:20]:
        print(f"    {os.path.relpath(f, ROOT)}: {msg[:80]}")


if __name__ == "__main__":
    main()
