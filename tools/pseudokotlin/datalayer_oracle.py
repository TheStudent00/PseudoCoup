"""
datalayer_oracle.py — runs the instrumented androidTest DAO/repository/db classes AS WRITTEN, headless,
against the sqlite3 Room engine. Extends the proven-runnable set beyond the 11 pure-logic engines to the
data layer, using the project's OWN tests. Reuses oracle's transpile / closure / run_python (seeded from
the runtime), pointed at src/androidTest.

  python3 datalayer_oracle.py [TestName ...]
"""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import oracle as O  # noqa: E402

ANDROIDTEST = os.path.join(O.CORPUS, "app", "src", "androidTest")

TESTS = [
    "ExerciseDaoMuscleGroupTest",
    "GymRepositoryTransactionTest",
    "BackupRepositoryRoundTripTest",
    "MigrationTest",
]


def run_one(name):
    tpath = O.find_one(ANDROIDTEST, name + ".kt")
    if not tpath:
        return {"<find>": ("error", "test not found in androidTest")}
    test_py = O.transpile(tpath)
    if test_py is None:
        return {"<transpile>": ("error", "test does not transpile")}
    dep_pys = [O.transpile(p) for p in O.closure([tpath])]
    return O.run_python("", test_py, [d for d in dep_pys if d])


def main():
    targets = sys.argv[1:] or TESTS
    all_green = True
    for name in targets:
        results = run_one(name)
        passed = sum(1 for s, _ in results.values() if s == "pass")
        total = len(results)
        all_green = all_green and passed == total and total > 0
        print(f"=== {name}  ({passed}/{total}) ===")
        for meth, (status, detail) in results.items():
            mark = {"pass": "ok  ", "fail": "FAIL", "error": "ERR "}[status]
            print(f"  [{mark}] {meth}" + (f"  -- {detail}" if detail else ""))
    print("\n" + ("ALL GREEN" if all_green else "some red") + " (data-layer instrumented tests)")
    sys.exit(0 if all_green else 1)


if __name__ == "__main__":
    main()
