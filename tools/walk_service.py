#!/usr/bin/env python3
"""walk_service.py -- the host-side run loop that removes the user from the build loop.

MECHANISM (full, no magic):
  * This script runs on the HOST (the user's machine), where gradle / the Android
    toolchain / long-running python are available. The Cowork assistant runs in a
    sandbox that cannot execute those, but it CAN read and write this repo's files.
  * The assistant writes request files:   DevComms/hostruns/requests/<id>.json
        {"id": "003_walkrecorder", "cwd": "~/Programming/WFL_MixingCenter/WFL",
         "cmd": ["./gradlew", ":app:testDebugUnitTest", "--tests",
                  "com.sara.workoutforlife.walk.WalkRecorderTest", "--rerun",
                  "-Dwalk.steps=60"],
         "timeout": 1800}
  * This loop picks up each request ONCE (ordered by id), runs it, and writes:
        DevComms/hostruns/results/<id>.log     -- merged stdout+stderr, live-appended
        DevComms/hostruns/results/<id>.json    -- {"id", "returncode", "seconds",
                                                    "started", "finished"}
    The assistant polls the results directory, reads the log, fixes code, writes the
    next request. The user's only job: start this script, and ctrl-C it when done.

PROGRESS DISPLAY (why the terminal now always shows what is happening):
  * On a TTY, a single live status line (carriage-return updated ~1/s) shows, per run:
        [hh:mm:ss] > <id> <spinner> <elapsed>s/~<est>s [====----] NN% <KB> | <last log line>
    The <est> is the MEDIAN of every prior run's recorded seconds, so the bar is a real
    (if rough) estimate that fills as the run proceeds; it caps at 99% until the child
    actually exits, then a persistent DONE line is printed (kept in scrollback).
  * When idle (no pending requests) it shows a slow "idle -- watching (last <id> rc=..)"
    line, so an idle service reads as idle, not as a hang.
  * Every RUN start and DONE/REFUSE is ALSO appended to DevComms/hostruns/service_history.log
    -- a persistent chronological record that survives terminal scrollback, so no run is
    silently "dropped" from the history.
  * Not a TTY (piped/redirected): falls back to a plain newline heartbeat every ~20s.

SAFETY RAILS:
  * cmd is exec'd directly (no shell), so no shell-injection surface.
  * cwd must resolve inside ~/Programming -- anything else is refused.
  * argv[0] of cmd must be on the ALLOWED list below -- this loop builds and tests,
    it does not administrate the machine.
  * A request id is processed at most once (results/<id>.json is the marker).

Usage:  python3 ~/Programming/PseudoCoup_v0/tools/walk_service.py
Stop:   ctrl-C  (or create DevComms/hostruns/STOP -- checked between runs)
"""
import json
import os
import shutil
import subprocess
import sys
import time
from datetime import datetime, timezone

HERE = os.path.dirname(os.path.abspath(__file__))
HOSTRUNS = os.path.join(os.path.dirname(HERE), "DevComms", "hostruns")
REQ_DIR = os.path.join(HOSTRUNS, "requests")
RES_DIR = os.path.join(HOSTRUNS, "results")
STOP = os.path.join(HOSTRUNS, "STOP")
HISTORY = os.path.join(HOSTRUNS, "service_history.log")
FENCE = os.path.realpath(os.path.expanduser("~/Programming"))
ALLOWED = {"./gradlew", "gradlew", "python3", "python", "xvfb-run", "adb", "git"}
POLL_SECONDS = 3
SPINNER = "⠋⠙⠹⠸⠼⠴⠦⠧⠇⠏"
IS_TTY = sys.stdout.isatty()
_status_shown = False   # a transient \r status line is currently on screen


def _ts():
    return datetime.now().strftime("%H:%M:%S")


def _clear():
    """Erase a transient status line if one is showing, so a persistent line prints clean."""
    global _status_shown
    if IS_TTY and _status_shown:
        sys.stdout.write("\r\033[K")
        sys.stdout.flush()
        _status_shown = False


def log(msg):
    """A PERSISTENT line (stays in scrollback)."""
    _clear()
    print(f"[walk_service {_ts()}] {msg}", flush=True)


def status(msg):
    """A TRANSIENT line (overwritten in place). No-op when not a TTY."""
    global _status_shown
    if not IS_TTY:
        return
    width = shutil.get_terminal_size((100, 20)).columns
    sys.stdout.write("\r\033[K" + msg[:max(0, width - 1)])
    sys.stdout.flush()
    _status_shown = True


def history(line):
    """Append a persistent chronological record that survives terminal scrollback."""
    try:
        with open(HISTORY, "a") as f:
            f.write(f"{datetime.now(timezone.utc).isoformat()}  {line}\n")
    except Exception:                      # noqa: BLE001 -- history must never kill the run
        pass


def _bar(frac, width=22):
    frac = 0.0 if frac < 0 else (1.0 if frac > 1 else frac)
    full = int(frac * width)
    return "█" * full + "░" * (width - full)


def _step_budget(cmd):
    """If this request is a walker.py run with an explicit --steps N budget, return N, else None.
    This is the real progress denominator: the walker prints one 'STEP ' line per consumed step,
    so completed-steps / budget is an actual completion fraction, unlike the time estimate."""
    names = [os.path.basename(str(a)) for a in cmd]
    if not any(n == "walker.py" for n in names):
        return None
    for i, a in enumerate(cmd):
        if a == "--steps" and i + 1 < len(cmd):
            try:
                return int(cmd[i + 1])
            except ValueError:
                return None
    return None


class _StepCounter:
    """Reads the walker's own 'PROGRESS spent=A/B' lines from the growing logfile (appended bytes
    only, so 1s polling stays cheap on multi-MB logs) -- the walker prints its ACTUAL budget
    counter, so this can never disagree with the walk (unlike counting 'STEP ' lines, which
    overcounted: some STEP-prefixed lines are non-budget markers like crash tracebacks).
    Falls back to counting 'STEP ' lines only if the log has no PROGRESS lines (older walker).
    Also tracks when the log last grew, so the status line can announce a stall."""
    def __init__(self, logfile):
        self.logfile, self.offset = logfile, 0
        self.step_count, self.spent = 0, None       # spent stays None until a PROGRESS line appears
        self.last_growth = time.time()
        self._partial = b""
    def poll(self):
        try:
            size = os.path.getsize(self.logfile)
            if size > self.offset:
                self.last_growth = time.time()
                with open(self.logfile, "rb") as rf:
                    rf.seek(self.offset)
                    chunk = self._partial + rf.read(size - self.offset)
                self.offset = size
                lines = chunk.split(b"\n")
                self._partial = lines.pop()            # tail may be a half-written line
                for l in lines:
                    if l.startswith(b"PROGRESS spent="):
                        try:
                            self.spent = int(l[len(b"PROGRESS spent="):].split(b"/")[0])
                        except ValueError:
                            pass
                    elif l.startswith(b"STEP "):
                        self.step_count += 1
        except Exception:                  # noqa: BLE001 -- display must never kill the run
            pass
        done = self.spent if self.spent is not None else self.step_count
        return done, time.time() - self.last_growth


def _estimate_seconds():
    """Median of every prior run's recorded seconds -- the progress-bar denominator."""
    vals = []
    for fn in os.listdir(RES_DIR):
        if not fn.endswith(".json"):
            continue
        try:
            s = json.load(open(os.path.join(RES_DIR, fn))).get("seconds")
            if isinstance(s, (int, float)) and s > 0:
                vals.append(s)
        except Exception:                  # noqa: BLE001
            pass
    if not vals:
        return 90.0
    vals.sort()
    return vals[len(vals) // 2]


def _tail(logfile):
    try:
        with open(logfile, "rb") as rf:
            rf.seek(max(0, os.path.getsize(logfile) - 4096))
            lines = [l for l in rf.read().decode("utf-8", "replace").splitlines() if l.strip()]
            return lines[-1][:80] if lines else "(no output yet)"
    except Exception:                      # noqa: BLE001 -- display must never kill the run
        return "(log unreadable)"


def refuse(req_id, reason):
    with open(os.path.join(RES_DIR, req_id + ".json"), "w") as f:
        json.dump({"id": req_id, "returncode": None, "refused": reason}, f, indent=2)
    log(f"REFUSED {req_id}: {reason}")
    history(f"REFUSED {req_id}: {reason}")
    return (req_id, None)


def run_request(path):
    req_id = os.path.basename(path)[:-len(".json")]   # filename IS the identity; the "id" field, when
    try:                                              # present, must agree (results are keyed by it)
        with open(path) as f:
            req = json.load(f)
    except Exception as e:                            # noqa: BLE001 -- malformed request: refuse, don't die
        return refuse(req_id, f"unparseable request JSON: {type(e).__name__}: {e}")
    if not isinstance(req, dict) or "cwd" not in req or "cmd" not in req:
        return refuse(req_id, "request must be a JSON object with at least cwd and cmd")
    if req.get("id", req_id) != req_id:
        return refuse(req_id, f"id field {req.get('id')!r} disagrees with filename -- rename one")
    cwd = os.path.realpath(os.path.expanduser(req["cwd"]))
    cmd = req["cmd"]
    timeout = int(req.get("timeout", 1800))
    if not (cwd == FENCE or cwd.startswith(FENCE + os.sep)):
        return refuse(req_id, f"cwd escapes ~/Programming: {cwd}")
    if not isinstance(cmd, list) or not cmd or os.path.basename(cmd[0]) not in \
            {os.path.basename(a) for a in ALLOWED}:
        return refuse(req_id, f"cmd[0] not on the allowed list: {cmd[:1]}")
    logfile = os.path.join(RES_DIR, req_id + ".log")
    started = datetime.now(timezone.utc).isoformat()
    t0 = time.time()
    est = _estimate_seconds()
    log(f"RUN {req_id}: {' '.join(cmd)}  (cwd={cwd}, timeout={timeout}s, est~{int(est)}s)")
    history(f"RUN {req_id}: {' '.join(cmd)}")
    env = dict(os.environ, **{k: str(v) for k, v in req.get("env", {}).items()})
    spin = 0
    last_beat = time.time()
    budget = _step_budget(cmd)
    stepper = _StepCounter(logfile) if budget else None
    with open(logfile, "w") as lf:
        try:
            proc = subprocess.Popen(cmd, cwd=cwd, env=env, stdout=lf, stderr=subprocess.STDOUT)
            while True:
                try:
                    rc = proc.wait(timeout=1)
                    break
                except subprocess.TimeoutExpired:
                    pass
                el = time.time() - t0
                if el > timeout:
                    proc.kill()
                    proc.wait()
                    rc = -9
                    lf.write(f"\nwalk_service: TIMEOUT after {timeout}s\n")
                    break
                spin = (spin + 1) % len(SPINNER)
                size = os.path.getsize(logfile)
                if stepper:
                    done, quiet = stepper.poll()
                    frac = min(done / budget, 0.99) if budget > 0 else 0.0
                    stall = f" ⚠ log quiet {int(quiet)}s" if quiet >= 30 else ""
                    prog = f"step {done}/{budget} [{_bar(frac)}] {int(frac * 100):>2}%{stall}"
                else:
                    frac = min(el / est, 0.99) if est > 0 else 0.0
                    prog = f"~{int(est)}s-est [{_bar(frac)}] {int(frac * 100):>2}%"
                if IS_TTY:
                    status(f"[{_ts()}] ▶ {req_id} {SPINNER[spin]} {int(el)}s "
                           f"{prog} {size // 1024}KB | {_tail(logfile)}")
                elif time.time() - last_beat >= 20:      # non-TTY fallback: sparse newline heartbeat
                    last_beat = time.time()
                    log(f"  … {req_id} {int(el)}s  {prog}  {size}B  | {_tail(logfile)}")
        except Exception as e:                            # noqa: BLE001
            rc = -1
            lf.write(f"\nwalk_service: LAUNCH FAILED: {type(e).__name__}: {e}\n")
    secs = round(time.time() - t0, 1)
    with open(os.path.join(RES_DIR, req_id + ".json"), "w") as f:
        json.dump({"id": req_id, "returncode": rc, "seconds": secs,
                   "started": started, "finished": datetime.now(timezone.utc).isoformat()},
                  f, indent=2)
    log(f"DONE {req_id}: rc={rc} ({secs}s) -> results/{req_id}.log")
    history(f"DONE {req_id}: rc={rc} ({secs}s)")
    return (req_id, rc)


def main():
    os.makedirs(REQ_DIR, exist_ok=True)
    os.makedirs(RES_DIR, exist_ok=True)
    log(f"watching {REQ_DIR} (stop: ctrl-C, or touch {STOP})")
    processed = 0
    last = "none yet"
    spin = 0
    while True:
        if os.path.exists(STOP):
            log("STOP file present -- exiting. (delete DevComms/hostruns/STOP to allow restart)")
            return 0
        pending = sorted(f for f in os.listdir(REQ_DIR) if f.endswith(".json")
                         and not os.path.exists(os.path.join(RES_DIR, f)))
        if pending:
            for name in pending:
                rid, rc = run_request(os.path.join(REQ_DIR, name))
                processed += 1
                last = f"{rid} rc={rc}"
        else:
            spin = (spin + 1) % len(SPINNER)
            status(f"[{_ts()}] {SPINNER[spin]} idle -- watching requests/ "
                   f"(processed {processed} this session, last: {last})")
        time.sleep(POLL_SECONDS)


if __name__ == "__main__":
    sys.exit(main())
