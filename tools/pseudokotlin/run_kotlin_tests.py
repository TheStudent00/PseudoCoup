#!/usr/bin/env python3
"""
run_kotlin_tests.py -- run the app's OWN JUnit unit-test suite under the KtToPy transpilation
and report pass/fail truthfully.

For each test class we:
  1. transpile the same-named subject engine (if one exists) + the test .kt -> Python
     (reusing oracle.transpile / oracle.closure -- the same machinery the equivalence oracle uses);
  2. exec deps + subject + test into a kotlin_rt-seeded namespace (the JUnit shim -- @Test, Before,
     assertEquals/True/False/Null/NotNull/Throws -- lives in runtime/kotlin_rt.py, general, not per-test);
  3. discover @Test methods, run each in isolation (fresh instance + @Before), and print a
     per-test PASS / FAIL / ERROR table plus a `RESULT: N/M pass` summary.

Unlike oracle.py --all, this targets the exact 11 test files the task names and never lets a
constructor-time gap crash the run: instance construction is inside the per-test try, so a missing
framework class surfaces as an honest ERROR row, not a traceback.

    python3 run_kotlin_tests.py [ClassName ...]
"""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import oracle as O          # noqa: E402  -- transpile / closure / find_one / MAIN / TEST
import registry             # noqa: E402  -- the seeded runtime namespace (JUnit shim included)

# The task's ground-truth suite. ExampleUnitTest (trivial placeholder) is intentionally excluded.
ENGINE_TESTS = [
    "AutoregulationEngineTest", "CalibrationEngineTest", "CardioRecoveryEngineTest",
    "NotificationTriggersTest", "PeriodizationEngineTest", "ReadinessProgressionGateTest",
    "RestartEngineTest", "SubstitutionEngineTest", "WarmupEngineTest",
]
MODEL_TESTS = ["PathDefinitionTest", "SampleProgramDataTest"]
ALL_TESTS = ENGINE_TESTS + MODEL_TESTS


def _load_namespace(test_path):
    """Build the exec namespace for one test file: subject engine (if any) + dependency closure +
    the test itself, seeded with the runtime shim. Returns (ns, note) or (None, error-detail)."""
    name = os.path.basename(test_path)[:-3]              # e.g. AutoregulationEngineTest
    subject = name[:-4] if name.endswith("Test") else name
    eng = O.find_one(O.MAIN, subject + ".kt")
    engine_py = O.transpile(eng) if eng else ""          # transpile subject FIRST (registers its fields)
    test_py = O.transpile(test_path)
    if test_py is None:
        return None, "test does not transpile"
    if eng and engine_py is None:
        return None, f"subject {subject} does not transpile"

    dep_paths = O.closure(([eng] if eng else []) + [test_path])
    dep_pys = [O.transpile(p) for p in dep_paths]
    missing = [p for p, s in zip(dep_paths, dep_pys) if s is None]
    dep_pys = [s for s in dep_pys if s]

    ns = dict(registry.namespace())
    try:
        O._exec_multipass(dep_pys, ns)
        if engine_py:
            exec(compile(engine_py, "<subject>", "exec"), ns)
        exec(compile(test_py, "<test>", "exec"), ns)
    except Exception as e:                               # noqa: BLE001 -- exec-time gap
        return None, f"exec: {type(e).__name__}: {e}"

    note = f"{len(dep_pys)} deps"
    if missing:
        note += f", {len(missing)} non-transpilable: " \
            + ",".join(os.path.basename(m)[:-3] for m in missing[:4])
    return (ns, note)


def _run_methods(ns, class_name):
    """Discover @Test methods on the produced *Test class and run each in isolation.
    -> dict method -> ('pass'|'fail'|'error', detail)."""
    test_cls = next((v for k, v in ns.items()
                     if isinstance(v, type) and k == class_name), None)
    if test_cls is None:                                 # fall back to any *Test class produced
        test_cls = next((v for k, v in ns.items()
                         if isinstance(v, type) and k.endswith("Test")), None)
    if test_cls is None:
        return {"<load>": ("error", "no *Test class produced")}
    members = [(n, v) for n, v in vars(test_cls).items()
               if callable(v) and not n.startswith("_")]
    tests = [n for n, v in members if getattr(v, "_is_test", False)
             and not getattr(v, "_is_ignored", False)]
    if not tests:
        return {"<discover>": ("error", "no @Test methods discovered")}
    setups = [n for n, v in members if getattr(v, "_is_setup", False)]
    results = {}
    for name in tests:
        try:                                             # construction INSIDE the try: a framework-class
            inst = test_cls()                            # gap is an honest ERROR row, not a crash
            for s in setups:
                getattr(inst, s)()
            getattr(inst, name)()
            results[name] = ("pass", "")
        except AssertionError as e:
            results[name] = ("fail", str(e))
        except Exception as e:                           # noqa: BLE001 -- shim/transpile gap
            results[name] = ("error", f"{type(e).__name__}: {e}")
    return results


def run_one(class_name):
    test_path = O.find_one(O.TEST, class_name + ".kt")
    if not test_path:
        return {"<find>": ("error", "test source not found")}, ""
    ns, note = _load_namespace(test_path)
    if ns is None:
        return {"<setup>": ("error", note)}, ""
    return _run_methods(ns, class_name), note


def main():
    targets = sys.argv[1:] or ALL_TESTS
    grand_pass = grand_total = 0
    for cls in targets:
        results, note = run_one(cls)
        passed = sum(1 for s, _ in results.values() if s == "pass")
        total = len(results)
        grand_pass += passed
        grand_total += total
        head = f"=== {cls}  ({passed}/{total})"
        print(head + (f"  [{note}]" if note else "") + " ===")
        for meth, (status, detail) in results.items():
            mark = {"pass": "PASS ", "fail": "FAIL ", "error": "ERROR"}[status]
            print(f"  [{mark}] {meth}" + (f"  -- {detail}" if detail else ""))
    print(f"\nRESULT: {grand_pass}/{grand_total} pass")
    sys.exit(0 if grand_pass == grand_total and grand_total > 0 else 1)


if __name__ == "__main__":
    main()
