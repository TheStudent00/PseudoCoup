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

# Compose/Hilt/Nav names. A non-UI-path file blocked by one of these is UI-orchestration that
# just lives outside ui/ (e.g. navigation/AppNavigation) -> it defers WITH the UI, not a real gap.
UI_NAMES = {"Icons", "hiltViewModel", "remember", "Modifier", "Composable", "Scaffold",
            "MaterialTheme", "NavHost", "rememberNavController", "collectAsStateWithLifecycle",
            "collectAsState", "LaunchedEffect", "Text", "Column", "Row", "Box"}


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

    def blocker(msg):
        return msg.split("'")[1] if "NameError" in msg and "'" in msg else None

    deferred = {f: m for f, m in errs.items() if blocker(m) in UI_NAMES}   # UI-orchestration
    gaps = {f: m for f, m in errs.items() if f not in deferred}            # real blockers
    domain = len(core) - len(deferred)

    print(f"non-UI domain files          : {domain}")
    print(f"  load clean                 : {len(loaded)} / {domain}")
    print(f"  real gaps                  : {len(gaps)}")
    print(f"UI-layer outside ui/ (deferred): {len(deferred)}   {[os.path.relpath(f, ROOT) for f in deferred]}")
    print(f"ui/ files (deferred)         : {len(ui)}")

    missing = collections.Counter(blocker(m) for m in gaps.values() if blocker(m))
    if missing:
        print("\nreal gaps -> need a stand-in / fix:")
        for name, n in missing.most_common(20):
            print(f"  {n:3d}  {name}")
    defects = {f: m for f, m in gaps.items() if "NameError" not in m}
    if defects:
        print("\nnon-NameError blockers (transpiler/logic defects to fix):")
        for f, msg in defects.items():
            print(f"  {os.path.relpath(f, ROOT)}: {msg[:90]}")


if __name__ == "__main__":
    main()
