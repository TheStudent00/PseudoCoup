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
from parse import parse                  # noqa: E402
import runtime.kotlin_rt as rt           # noqa: E402

_TP_CACHE = {}      # path -> transpiled Python (or None if it does not transpile)
_INDEX = {}         # top-level Kotlin declaration name -> defining .kt path
_TOP_DECL = ("class_declaration", "object_declaration",
             "function_declaration", "property_declaration", "type_alias")

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
    """Transpile a .kt file, cached. Returns None if it does not transpile (so a
    dep that fails surfaces as an honest NameError downstream, not a crash)."""
    if path not in _TP_CACHE:
        try:
            with open(path, "rb") as f:
                _TP_CACHE[path] = KtToPy().transpile(f.read())
        except Untranspilable:
            _TP_CACHE[path] = None
    return _TP_CACHE[path]


def build_index():
    """name -> defining .kt path, for every top-level declaration in the corpus
    (main preferred over test on collision). Drives dependency-closure resolution."""
    if _INDEX:
        return _INDEX
    for root in (MAIN, TEST):
        for dp, _, names in os.walk(root):
            if os.sep + "build" + os.sep in dp + os.sep:
                continue
            for n in names:
                if not n.endswith(".kt"):
                    continue
                path = os.path.join(dp, n)
                with open(path, "rb") as f:
                    src = f.read()
                for c in parse(src).root_node.named_children:
                    if c.type not in _TOP_DECL:
                        continue
                    ident = next((k for k in c.children
                                  if k.type in ("identifier", "simple_identifier")), None)
                    if ident is not None:
                        _INDEX.setdefault(ident.text.decode(), path)
    return _INDEX


def referenced_names(py):
    return set(re.findall(r"[A-Za-z_]\w*", py)) if py else set()


def closure(seed_paths):
    """Transitive set of corpus files defining every name the seeds (and their deps)
    reference. Returns dep paths only -- the seeds themselves are excluded."""
    index = build_index()
    seeds = set(seed_paths)
    needed, frontier = set(), list(seed_paths)
    while frontier:
        nxt = []
        for path in frontier:
            for name in referenced_names(transpile(path)):
                dep = index.get(name)
                if dep and dep not in needed and dep not in seeds:
                    needed.add(dep)
                    nxt.append(dep)
        frontier = nxt
    return needed


def package_of(path):
    with open(path, encoding="utf-8") as f:
        for line in f:
            m = re.match(r"\s*package\s+([\w.]+)", line)
            if m:
                return m.group(1)
    return None


def _exec_multipass(sources, ns):
    """exec dep modules in any order: a module that NameErrors (its dep not loaded
    yet) is deferred to the next pass; loop until a pass makes no progress. Resolves
    inter-dependency ordering without a real topological sort."""
    pending = [s for s in sources if s]
    while pending:
        still, progressed, last = [], False, None
        for src in pending:
            try:
                exec(compile(src, "<dep>", "exec"), ns)
                progressed = True
            except NameError as e:
                still.append(src)
                last = e
        if not progressed:
            raise last or NameError("unresolvable dependency")
        pending = still


def run_python(engine_py, test_py, dep_pys=()):
    """exec deps + engine + test in a shim-seeded namespace; run each test method.
    -> dict method -> ('pass'|'fail'|'error', detail)."""
    ns = {k: getattr(rt, k) for k in dir(rt) if not k.startswith("_")}
    try:
        _exec_multipass(dep_pys, ns)
        exec(compile(engine_py, "<engine>", "exec"), ns)
        exec(compile(test_py, "<test>", "exec"), ns)
    except Exception as e:                           # noqa: BLE001 -- exec-time gap
        return {"<exec>": ("error", f"{type(e).__name__}: {e}")}
    test_cls = next((v for k, v in ns.items()
                     if isinstance(v, type) and k.endswith("Test")), None)
    if test_cls is None:
        return {"<load>": ("error", "no *Test class produced")}
    members = [(n, v) for n, v in vars(test_cls).items()
               if callable(v) and not n.startswith("_")]
    tests = [n for n, v in members if getattr(v, "_is_test", False)
             and not getattr(v, "_is_ignored", False)]
    if not tests:                                    # no @Test survived -> run all
        tests = [n for n, _ in members]
    setups = [n for n, v in members if getattr(v, "_is_setup", False)]
    results = {}
    for name in tests:
        inst = test_cls()
        try:
            for s in setups:
                getattr(inst, s)()
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
    engine_py, test_py = transpile(eng), transpile(tst)
    if engine_py is None or test_py is None:
        print(f"  {name}: {'engine' if engine_py is None else 'test'} does not transpile")
        return False

    dep_paths = closure([eng, tst])
    dep_pys = [transpile(p) for p in dep_paths]
    missing = [p for p, s in zip(dep_paths, dep_pys) if s is None]
    dep_pys = [s for s in dep_pys if s]
    results = run_python(engine_py, test_py, dep_pys)
    passed = sum(1 for s, _ in results.values() if s == "pass")
    total = len(results)
    dep_note = f", {len(dep_pys)} deps"
    if missing:
        dep_note += f", {len(missing)} non-transpilable: " \
            + ",".join(os.path.basename(m)[:-3] for m in missing[:4])
    print(f"\n=== {name}  (python: {passed}/{total} methods{dep_note}) ===")
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
