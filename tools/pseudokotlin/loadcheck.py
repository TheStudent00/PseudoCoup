"""loadcheck.py — the foundation's *load* gate (the third runnability gate, alongside the
parse gate `build_mixingcenter.py` and the logic gate `oracle.py`).

Loads every foundation .py through loader.Loader -- PER-FILE namespaces with Kotlin file-visibility
(a private helper always resolves to the one in its own file; cross-file names resolve by same-package,
then unique-anywhere, then the file's Kotlin import table). Reports how many load clean and what blocks
the rest. A NameError blocker is a missing runtime name; anything else is a transpiler/logic defect.

  python3 loadcheck.py            # summary + blockers
"""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from loader import Loader   # noqa: E402


def main():
    ld = Loader().load_all()
    ui = [k for k in ld.keys if k.startswith("ui" + os.sep)]
    core = [k for k in ld.keys if not k.startswith("ui" + os.sep)]
    print(f"non-UI domain load           : {sum(1 for k in core if k in ld.loaded)} / {len(core)}")
    print(f"ui/ load (per-file namespaces): {sum(1 for k in ui if k in ld.loaded)} / {len(ui)}")
    gaps = {k: e for k, e in ld.failed.items() if k not in ld.loaded}
    print(f"  real gaps                  : {len(gaps)}")
    for k, e in list(gaps.items())[:20]:
        print(f"    {k}: {type(e).__name__}: {str(e)[:80]}")


if __name__ == "__main__":
    main()
