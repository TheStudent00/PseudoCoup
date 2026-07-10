"""Guard tests for walk_service's progress counter + enforcement.

OWNER MANDATE 2026-07-10: the progress display must be REAL (the walk's own counter over its
own budget) and its enforcement must be NON-REMOVABLE. The owner has had to re-demand a
working progress indicator repeatedly because prior versions eroded silently -- nothing
failed when the counter disappeared. These tests are the tripwire: if someone removes the
counter plumbing or the progress_defect enforcement from walk_service.py, this file fails.

Run: cd tools && python3 -m pytest test_walk_service_progress.py -q
"""
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import walk_service as ws  # noqa: E402


# ---------- budget/counter-file detection (both engines) ----------

def test_py_walk_budget_counts_from_own_logfile():
    budget, cfile = ws._progress_source(
        ["xvfb-run", "-a", "python3", "-u", "walker.py", "--steps", "200", "--reset"],
        "/x/render", "/res/001.log")
    assert budget == 200
    assert cfile == "/res/001.log"          # py counter lines are on the run's own stdout


def test_kt_walk_budget_counts_from_kt_activations_log():
    budget, cfile = ws._progress_source(
        ["./gradlew", ":app:testDebugUnitTest", "--tests", "*WalkRecorderTest", "--rerun",
         "-Dwalk.steps=200", "-Dwalk.reset=true"],
        "/x/WFL", "/res/002.log")
    assert budget == 200
    # gradle swallows test stdout -- the counter MUST be read from the walk test's own file
    assert cfile == os.path.join("/x/WFL", "app", "build", "walks", "kt_activations.log")


def test_unbudgeted_run_has_no_counter():
    assert ws._progress_source(["python3", "walk_diff.py"], "/x", "/y.log") == (None, None)


# ---------- end-to-end: run_request enforcement ----------

def _run_stub_walker(tmp_path, monkeypatch, walker_body):
    """Drive a real run_request() against a stub walker.py inside a temp fence."""
    req_dir, res_dir = tmp_path / "requests", tmp_path / "results"
    req_dir.mkdir(), res_dir.mkdir()
    cwd = tmp_path / "work"
    cwd.mkdir()
    (cwd / "walker.py").write_text(walker_body)
    monkeypatch.setattr(ws, "REQ_DIR", str(req_dir))
    monkeypatch.setattr(ws, "RES_DIR", str(res_dir))
    monkeypatch.setattr(ws, "FENCE", str(tmp_path))
    monkeypatch.setattr(ws, "HISTORY", str(tmp_path / "history.log"))
    monkeypatch.setattr(ws, "IS_TTY", False)
    req = req_dir / "001_stub.json"
    req.write_text(json.dumps({"cwd": str(cwd),
                               "cmd": ["python3", "walker.py", "--steps", "3"],
                               "timeout": 60}))
    ws.run_request(str(req))
    return json.loads((res_dir / "001_stub.json").read_text())


def test_green_walk_without_counter_is_flagged_defective(tmp_path, monkeypatch):
    """THE NON-REMOVABILITY GUARD: a budgeted walk that exits 0 without ever printing
    'PROGRESS spent=A/B' must carry progress_defect in its result json. If this test
    fails, someone deleted the enforcement block in run_request() -- restore it."""
    result = _run_stub_walker(tmp_path, monkeypatch,
                              "print('walk ran but the PROGRESS emitter is gone')\n")
    assert result["returncode"] == 0
    assert "progress_defect" in result, (
        "walk_service accepted a green budgeted walk with no progress counter -- "
        "the OWNER-MANDATED enforcement has been removed from run_request()")
    assert result["steps"]["spent"] is None


def test_green_walk_with_counter_is_clean(tmp_path, monkeypatch):
    result = _run_stub_walker(
        tmp_path, monkeypatch,
        "\n".join(f"print('PROGRESS spent={i}/3')" for i in (1, 2, 3)) + "\n")
    assert result["returncode"] == 0
    assert "progress_defect" not in result
    assert result["steps"] == {"spent": 3, "budget": 3,
                               "counter_file": result["steps"]["counter_file"]}
    assert result["steps"]["counter_file"].endswith("001_stub.log")


def test_stale_kt_log_content_is_skipped(tmp_path, monkeypatch):
    """kt_activations.log persists across runs: counter must only read bytes appended
    AFTER the run starts, so a previous run's PROGRESS lines can't fake progress."""
    stale = tmp_path / "stale.log"
    stale.write_text("PROGRESS spent=999/1000\n")
    counter = ws._StepCounter(str(stale))
    done, _ = counter.poll()
    assert counter.spent is None and done == 0    # stale content ignored
    with open(stale, "a") as f:
        f.write("PROGRESS spent=7/200\n")
    counter.poll()
    assert counter.spent == 7                     # fresh content counted
