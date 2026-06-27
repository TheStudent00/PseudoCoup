"""
oracle.py — the runtime equivalence oracle (verification ladder rung 2, above the
compile gate). For an engine + its JUnit test:

  1. transpile BOTH engine and test Kotlin -> Python;
  2. exec them into one namespace seeded with the kotlin_rt shim;
  3. run each test method -- a JVM-verified assertion that now runs against the
     TRANSPILED engine. If Python passes every assertion the JVM passes, the
     transpilation is behaviorally equivalent on those inputs;
  4. with --jvm, also run the Gradle test for the same class, so "both sides" is
     literal: green/green == equivalent, green/red == a real divergence localized
     to the failing method.

Compile-clean only proves the Python parses; this proves it BEHAVES. Usage:

  python3 oracle.py NotificationTriggers          # python side only (fast)
  python3 oracle.py NotificationTriggers --jvm     # cross-check vs the JVM test
  python3 oracle.py --all                          # every engine with a *Test
"""
import os
import re
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from transpiler import KtToPy            # noqa: E402
from dispatch import Untranspilable      # noqa: E402
import runtime.kotlin_rt as rt           # noqa: E402

CORPUS = os.path.normpath(os.path.join(HERE, "..", "..", "..", "WFL_MixingCenter", "WFL"))
MAIN = os.path.join(CORPUS, "app", "src", "main")
TEST = os.path.join(CORPUS, "app", "src", "test")


def find_one(root, leaf):
    for dp, _, names in os.walk(root):
        if os.sep + "build" + os.sep in dp + os.sep:
            continue
        if leaf in names:
            return os.path.join(dp, leaf)
    return None


def transpile(path):
    with open(path, "rb") as f:
        return KtToPy().transpile(f.read())


def package_of(path):
    with open(path, encoding="utf-8") as f:
        for line in f:
            m = re.match(r"\s*package\s+([\w.]+)", line)
            if m:
                return m.group(1)
    return None


def run_python(engine_py, test_py):
    """exec engine+test in a shim-seeded namespace; run each test method.
    -> dict method -> ('pass'|'fail'|'error', detail)."""
    ns = {k: getattr(rt, k) for k in dir(rt) if not k.startswith("_")}
    try:
        exec(compile(engine_py, "<engine>", "exec"), ns)
        exec(compile(test_py, "<test>", "exec"), ns)
    except Exception as e:                           # noqa: BLE001 -- exec-time gap
        return {"<exec>": ("error", f"{type(e).__name__}: {e}")}
    test_cls = next((v for k, v in ns.items()
                     if isinstance(v, type) and k.endswith("Test")), None)
    if test_cls is None:
        return {"<load>": ("error", "no *Test class produced")}
    results = {}
    methods = [n for n, v in vars(test_cls).items()
               if callable(v) and not n.startswith("_")]
    for name in methods:
        inst = test_cls()
        try:
            getattr(inst, name)()
            results[name] = ("pass", "")
        except AssertionError as e:
            results[name] = ("fail", str(e))
        except Exception as e:                       # noqa: BLE001 -- shim/transpile gap
            results[name] = ("error", f"{type(e).__name__}: {e}")
    return results


def run_jvm(test_path):
    pkg = package_of(test_path)
    cls = os.path.basename(test_path)[:-3]
    fqcn = f"{pkg}.{cls}" if pkg else cls
    proc = subprocess.run(
        ["./gradlew", ":app:testDebugUnitTest", "--tests", fqcn, "--rerun-tasks", "-q"],
        cwd=CORPUS, capture_output=True, text=True)
    return proc.returncode == 0, proc


def oracle(name, jvm=False):
    eng = find_one(MAIN, f"{name}.kt")
    tst = find_one(TEST, f"{name}Test.kt")
    if not eng or not tst:
        print(f"  {name}: missing {'engine' if not eng else 'test'} source")
        return False
    try:
        engine_py, test_py = transpile(eng), transpile(tst)
    except Untranspilable as e:
        print(f"  {name}: does not transpile -- {e}")
        return False

    results = run_python(engine_py, test_py)
    passed = sum(1 for s, _ in results.values() if s == "pass")
    total = len(results)
    print(f"\n=== {name}  (python: {passed}/{total} methods) ===")
    for meth, (status, detail) in results.items():
        mark = {"pass": "ok  ", "fail": "FAIL", "error": "ERR "}[status]
        print(f"  [{mark}] {meth}" + (f"  -- {detail}" if detail else ""))

    py_green = passed == total
    if not jvm:
        return py_green

    ok, proc = run_jvm(tst)
    verdict = {(True, True): "EQUIVALENT (both green)",
               (True, False): "DIVERGENCE (python green, JVM red)",
               (False, True): "DIVERGENCE (python red, JVM green)",
               (False, False): "both red (test or shim broken, not a divergence proof)"}
    print(f"  JVM: {'green' if ok else 'red'}  ->  {verdict[(py_green, ok)]}")
    if not ok and "FAILED" in proc.stdout:
        for line in proc.stdout.splitlines():
            if "FAILED" in line:
                print("       " + line.strip())
    return py_green and ok


def all_engines():
    names = []
    for dp, _, fs in os.walk(TEST):
        if os.sep + "build" + os.sep in dp + os.sep:
            continue
        for f in fs:
            if f.endswith("Test.kt") and find_one(MAIN, f[:-7] + ".kt"):
                names.append(f[:-7])
    return sorted(set(names))


def main():
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    jvm = "--jvm" in sys.argv
    names = all_engines() if "--all" in sys.argv else args
    if not names:
        print("usage: oracle.py <EngineName> [--jvm] | --all")
        return
    verdicts = [oracle(n, jvm=jvm) for n in names]   # list, not generator: run them ALL
    ok = all(verdicts)
    print(f"\n{'ALL GREEN' if ok else 'some red/divergent'} "
          f"({sum(verdicts)}/{len(verdicts)} engines fully green)")
    sys.exit(0 if ok else 1)


if __name__ == "__main__":
    main()
