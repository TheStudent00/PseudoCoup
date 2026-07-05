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
import ast
import os
import re
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from transpiler import KtToPy            # noqa: E402
from dispatch import Untranspilable      # noqa: E402
from parse import parse                  # noqa: E402
import registry                          # noqa: E402  (the merged runtime namespace, by origin)

_TP_CACHE = {}      # path -> transpiled Python (or None if it does not transpile)
_INDEX = {}         # top-level Kotlin declaration name -> defining .kt path
_TOP_DECL = ("class_declaration", "object_declaration",
             "function_declaration", "property_declaration", "type_alias")
_TYPE_DECL = ("class_declaration", "object_declaration", "type_alias")

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
    """Transpile a .kt file, cached. Returns None if it does not transpile OR emits Python that
    doesn't parse (so an unusable dep -- e.g. an incomplete UI file -- surfaces as an honest NameError
    downstream, not a crash). The engine files themselves emit valid Python and run."""
    if path not in _TP_CACHE:
        try:
            with open(path, "rb") as f:
                code = KtToPy().transpile(f.read())
            ast.parse(code)                      # emitted-but-invalid dep -> treated as not-transpiled
            _TP_CACHE[path] = code
        except (Untranspilable, SyntaxError):
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
                _index_decls(parse(src).root_node, path)
    return _INDEX


def _index_decls(node, path, types_only=False):
    """Index declaration name -> file, descending into class/object bodies so NESTED
    TYPES (e.g. ConfidenceTier inside AutoregulationEngine) resolve too. Inside a body
    only nested TYPES are indexed, never members -- indexing member functions/props
    (`size`, `name`, …) would make the closure pull in the whole corpus."""
    kinds = _TYPE_DECL if types_only else _TOP_DECL
    for c in node.named_children:
        if c.type in kinds:
            ident = next((k for k in c.children
                          if k.type in ("identifier", "simple_identifier")), None)
            if ident is not None:
                _INDEX.setdefault(ident.text.decode(), path)
        if c.type in ("class_declaration", "object_declaration"):
            body = next((k for k in c.children
                         if k.type in ("class_body", "enum_class_body")), None)
            if body is not None:
                _index_decls(body, path, types_only=True)


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
            break               # remaining deps can't resolve (e.g. a UI file referencing a name
            # absent in this engine namespace, like hiltViewModel) -> drop them; if an engine truly
            # needs one, its own test fails honestly downstream rather than crashing the whole run.
        pending = still


def run_python(engine_py, test_py, dep_pys=()):
    """exec deps + engine + test in a shim-seeded namespace; run each test method.
    -> dict method -> ('pass'|'fail'|'error', detail)."""
    ns = dict(registry.namespace())
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
        try:
            inst = test_cls()               # construct INSIDE the try: a class whose ctor
            # touches an unshimmed name (e.g. java.util.TimeZone) yields an ERROR row for
            # this test, not an aborted whole-corpus run.
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
    tst = find_one(TEST, f"{name}Test.kt")
    if not tst:
        print(f"  {name}: missing test source")
        return False
    # A test's subject need not be a same-named main file: e.g. ReadinessProgressionGateTest
    # exercises methods ON AutoregulationEngine. When there's no `{name}.kt`, the subject
    # arrives via the test's own dependency closure instead of as a named engine seed.
    eng = find_one(MAIN, f"{name}.kt")
    # Transpile the engine BEFORE the test: transpile() populates global type/field
    # registries as a side effect, and the test's references (e.g. WarmupEngine.loadKg)
    # resolve correctly only once the engine's fields are registered.
    engine_py = transpile(eng) if eng else ""
    test_py = transpile(tst)
    if test_py is None:
        print(f"  {name}: test does not transpile")
        return False
    if eng and engine_py is None:
        print(f"  {name}: engine does not transpile")
        return False

    dep_paths = closure(([eng] if eng else []) + [tst])
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
    main_syms = {n for n, p in build_index().items() if p.startswith(MAIN)}
    names = []
    for dp, _, fs in os.walk(TEST):
        if os.sep + "build" + os.sep in dp + os.sep:
            continue
        for f in fs:
            if not f.endswith("Test.kt"):
                continue
            name = f[:-7]
            if find_one(MAIN, name + ".kt"):
                names.append(name)
                continue
            # No same-named engine: include iff the test references a MAIN symbol (its
            # subject is a nested type elsewhere, e.g. ReadinessProgressionGate -> Auto-
            # regulationEngine). Excludes Android's ExampleUnitTest, which references none.
            tp = transpile(os.path.join(dp, f))
            if tp and (referenced_names(tp) & main_syms):
                names.append(name)
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
