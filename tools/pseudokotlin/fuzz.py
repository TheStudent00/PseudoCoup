"""Differential-fuzzing oracle for the Kotlin->Python transpiler.

The runtime oracle (oracle.py) proves equivalence on the engines' HAND-WRITTEN JUnit
cases. This pushes further: generate random inputs in each target's domain, run the SAME
cases on BOTH sides -- the transpiled Python engine and the JVM Kotlin engine -- and diff
the outputs. A divergence is a real behavioural bug the hand-written tests didn't reach.

  python3 fuzz.py            # all targets, default case count
  python3 fuzz.py 500        # 500 cases per target

How the JVM side runs: we emit a throwaway JUnit test that calls the engine on the embedded
cases and writes results to a temp file, run it through the existing Gradle setup (so the
classpath/deps just work), then read + compare. The harness file is always cleaned up.
"""
import os, sys, subprocess

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import oracle as O
import runtime.kotlin_rt as rt

SCRATCH = os.environ.get("FUZZ_SCRATCH", "/tmp/claude-1000/-home-lucas-Programming-PseudoCoup/"
                         "f58ef2fa-366b-4c58-a62b-7997a2fc21af/scratchpad")
RESULTS = os.path.join(SCRATCH, "jvm_fuzz_results.tsv")
HARNESS = os.path.join(O.TEST, "java", "com", "sara", "workoutforlife", "engine",
                       "FuzzHarnessTest.kt")

# A deterministic LCG so Python and the case stream never depend on hash seeding or
# platform RNG details -- same seed -> same cases, every run, every machine.
class Rng:
    def __init__(self, seed): self.s = seed & 0xFFFFFFFF
    def _next(self):
        self.s = (1103515245 * self.s + 12345) & 0x7FFFFFFF
        return self.s
    def uniform(self, lo, hi): return lo + (hi - lo) * (self._next() / 0x7FFFFFFF)
    def randint(self, lo, hi): return lo + self._next() % (hi - lo + 1)


def D(lo, hi, nd=1):   # Double arg in [lo,hi], rounded to nd decimals
    return ("Double", lambda r: round(r.uniform(lo, hi), nd))
def I(lo, hi):         # Int arg in [lo,hi]
    return ("Int", lambda r: r.randint(lo, hi))


# (engine, method, [arg specs], return type). All pure primitive -> scalar.
TARGETS = [
    ("AutoregulationEngine", "computeE1rm",      [D(20, 300), I(1, 15), I(0, 5)],        "Double"),
    ("AutoregulationEngine", "suggestRawWeight",  [D(40, 400), I(0, 5), I(1, 12)],        "Double"),
    ("AutoregulationEngine", "predictReps",       [D(40, 400), D(20, 380), I(0, 5)],      "Int"),
    ("AutoregulationEngine", "roundToIncrement",  [D(20, 400), D(0.5, 5, 1)],             "Double"),
    ("AutoregulationEngine", "applyReadinessProgressionHold",
                                                  [D(20, 400), D(20, 400), ("Boolean", lambda r: r.randint(0, 1) == 1)], "Double"),
    ("AutoregulationEngine", "isReadinessGood",   [I(0, 3), I(0, 3)],                     "Boolean"),
    # Other engines -- the fuzzer is a general multi-engine tool, not Autoregulation-specific.
    ("CardioRecoveryEngine", "durationFactor",    [I(0, 180)],                            "Double"),
    ("CardioRecoveryEngine", "recencyDecay",      [D(0, 200, 2)],                         "Double"),
    ("PeriodizationEngine",  "volumeWaveFraction", [I(0, 11), I(1, 12), I(40, 100)],      "Double"),
    ("PeriodizationEngine",  "setTargetForWeek",  [I(1, 8), I(0, 11), I(1, 12), I(40, 100)], "Int"),
]


def kt_lit(typ, v):
    if typ == "Boolean":
        return "true" if v else "false"
    if typ == "Int":
        return str(int(v))
    s = repr(float(v))
    return s if ("." in s or "e" in s or "E" in s) else s + ".0"


def gen_cases(target, n, seed=0x5EED):
    _, _, specs, _ = target
    r = Rng(seed)
    return [tuple(spec[1](r) for spec in specs) for _ in range(n)]


def py_run(engine_name, method, cases):
    eng = O.find_one(O.MAIN, f"{engine_name}.kt")
    ns = {k: getattr(rt, k) for k in dir(rt) if not k.startswith("_")}
    O._exec_multipass([O.transpile(p) for p in O.closure([eng])], ns)
    exec(compile(O.transpile(eng), "<eng>", "exec"), ns)
    obj = ns[engine_name]
    out = []
    for args in cases:
        try:
            out.append(("ok", obj.__getattribute__(method)(*args)))
        except Exception as e:                       # noqa: BLE001
            out.append(("err", type(e).__name__))
    return out


def jvm_run(plan):
    """plan: list of (target_idx, engine, method, specs, cases). Emit one harness that runs
    every case on the JVM and writes `ti<TAB>ci<TAB>ok|err<TAB>value` lines; return parsed."""
    lines = []
    for ti, (engine, method, specs, _ret, cases) in enumerate(plan):
        for ci, args in enumerate(cases):
            call = f"{engine}.{method}(" + ", ".join(kt_lit(s[0], v) for s, v in zip(specs, args)) + ")"
            lines.append(f"        emit({ti}, {ci}, {{ {call} }})")
    # Chunk into separate methods: a single method with thousands of calls blows the JVM's
    # 64 KB per-method bytecode limit ("internal compiler error"). One method per ~300 calls.
    CHUNK = 300
    chunks = [lines[i:i + CHUNK] for i in range(0, len(lines), CHUNK)] or [[]]
    methods = "\n".join(f"    private fun c{i}() {{\n" + "\n".join(c) + "\n    }"
                        for i, c in enumerate(chunks))
    calls = "\n".join(f"        c{i}()" for i in range(len(chunks)))
    src = f"""package com.sara.workoutforlife.engine
import org.junit.Test
import java.io.File

class FuzzHarnessTest {{
    private val sb = StringBuilder()
    private fun emit(ti: Int, ci: Int, f: () -> Any?) {{
        val v = try {{ "ok\\t" + f() }} catch (e: Throwable) {{ "err\\t" + e.javaClass.simpleName }}
        sb.append("$ti\\t$ci\\t$v\\n")
    }}
{methods}
    @Test fun run() {{
{calls}
        File("{RESULTS}").writeText(sb.toString())
    }}
}}
"""
    os.makedirs(os.path.dirname(HARNESS), exist_ok=True)
    if os.path.exists(RESULTS):
        os.remove(RESULTS)
    with open(HARNESS, "w") as f:
        f.write(src)
    try:
        proc = subprocess.run(
            ["./gradlew", ":app:testDebugUnitTest", "--tests",
             "com.sara.workoutforlife.engine.FuzzHarnessTest", "--rerun-tasks", "-q"],
            cwd=O.CORPUS, capture_output=True, text=True)
    finally:
        os.remove(HARNESS)
    if not os.path.exists(RESULTS):
        sys.stderr.write(proc.stdout[-3000:] + "\n" + proc.stderr[-2000:] + "\n")
        raise SystemExit("JVM harness produced no results (see Gradle output above)")
    res = {}
    with open(RESULTS) as f:
        for ln in f:
            ti, ci, status, val = ln.rstrip("\n").split("\t", 3)
            res[(int(ti), int(ci))] = (status, val)
    return res


def same(ret, py, jvm):
    (ps, pv), (js, jv) = py, jvm
    if ps != js:
        return False
    if ps == "err":
        return True                                  # both errored -> agree (type name may differ)
    if ret == "Double":
        a, b = float(pv), float(jv)
        return abs(a - b) <= 1e-9 * max(1.0, abs(a), abs(b))
    if ret == "Int":
        return int(pv) == int(float(jv))
    if ret == "Boolean":
        return (pv is True or str(pv).lower() == "true") == (str(jv).lower() == "true")
    return str(pv) == str(jv)


def main():
    n = int(sys.argv[1]) if len(sys.argv) > 1 and sys.argv[1].isdigit() else 150
    plan = []
    for engine, method, specs, ret in TARGETS:
        plan.append((engine, method, specs, ret, gen_cases((engine, method, specs, ret), n)))

    print(f"differential fuzz: {len(TARGETS)} targets x {n} cases = {len(TARGETS)*n} total")
    py = {(ti, ci): r for ti, (_, m, _, _, cases) in enumerate(plan)
          for ci, r in enumerate(py_run(plan[ti][0], m, cases))}
    jvm = jvm_run(plan)

    total_div = 0
    for ti, (engine, method, specs, ret, cases) in enumerate(plan):
        divs = []
        for ci, args in enumerate(cases):
            pr, jr = py.get((ti, ci)), jvm.get((ti, ci))
            if jr is None or not same(ret, pr, jr):
                divs.append((args, pr, jr))
        mark = "ok  " if not divs else "DIVERGE"
        print(f"  [{mark}] {engine}.{method}: {len(cases)-len(divs)}/{len(cases)} agree")
        for args, pr, jr in divs[:5]:
            print(f"        {args}  py={pr}  jvm={jr}")
        total_div += len(divs)

    print(f"\n{'ALL EQUIVALENT' if total_div == 0 else f'{total_div} DIVERGENCES'} "
          f"across {len(TARGETS)*n} random cases")
    return 0 if total_div == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
