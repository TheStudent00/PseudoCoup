"""
measure.py — corpus compile-clean gauge. Transpiles every .kt in the WFL source
copy, py_compiles the output, and reports clean/total plus a failure-reason
histogram (the node kind each Untranspilable named) for ALL files and the NON-UI
domain subset (no `/ui/` package segment -- the layer the JVM test oracle covers).

  python3 measure.py [CORPUS_DIR]

Default corpus: ../../../WFL_MixingCenter/WFL (relative to this file).
"""
import os
import py_compile
import re
import sys
import tempfile
from collections import Counter

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from transpiler import KtToPy  # noqa: E402
from dispatch import Untranspilable  # noqa: E402

DEFAULT_CORPUS = os.path.normpath(
    os.path.join(HERE, "..", "..", "..", "WFL_MixingCenter", "WFL"))
_REASON = re.compile(r"\[(\w+) @")   # pulls the node kind out of an Untranspilable msg


def kt_files(root):
    for dirpath, _, names in os.walk(root):
        if os.sep + "build" + os.sep in dirpath + os.sep:
            continue
        for n in names:
            if n.endswith(".kt"):
                yield os.path.join(dirpath, n)


def result(path):
    """-> ('clean', None) | ('transpile', kind) | ('compile', None)."""
    try:
        with open(path, "rb") as f:
            py = KtToPy().transpile(f.read())
    except Untranspilable as e:
        m = _REASON.search(str(e))
        return "transpile", (m.group(1) if m else "?")
    except Exception:                       # noqa: BLE001 -- any transpiler crash
        return "transpile", "crash"
    tmp = tempfile.NamedTemporaryFile("w", suffix=".py", delete=False)
    tmp.write(py)
    tmp.close()
    try:
        py_compile.compile(tmp.name, doraise=True)
        return "clean", None
    except py_compile.PyCompileError:
        return "compile", None
    finally:
        os.unlink(tmp.name)


def report(label, files):
    clean = 0
    reasons = Counter()
    compile_fail = 0
    for p in files:
        kind, reason = result(p)
        if kind == "clean":
            clean += 1
        elif kind == "compile":
            compile_fail += 1
            reasons["<py_compile>"] += 1
        else:
            reasons[reason] += 1
    total = len(files)
    print(f"\n{label}: {clean}/{total} compile-clean "
          f"({100*clean//total if total else 0}%)")
    for reason, n in reasons.most_common():
        print(f"    {n:3d}  {reason}")


def main():
    root = sys.argv[1] if len(sys.argv) > 1 else DEFAULT_CORPUS
    allf = sorted(kt_files(root))
    domain = [p for p in allf if os.sep + "ui" + os.sep not in p]
    report("ALL", allf)
    report("NON-UI domain", domain)


if __name__ == "__main__":
    main()
