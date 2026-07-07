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

SAFETY RAILS:
  * cmd is exec'd directly (no shell), so no shell-injection surface.
  * cwd must resolve inside ~/Programming -- anything else is refused.
  * argv[0] of cmd must be on the ALLOWED list below -- this loop builds and tests,
    it does not administrate the machine.
  * A request id is processed at most once (results/<id>.json is the marker).

Usage:  python3 ~/Programming/PseudoCoup/tools/walk_service.py
Stop:   ctrl-C  (or create DevComms/hostruns/STOP -- checked between runs)
"""
import json
import os
import subprocess
import sys
import time
from datetime import datetime, timezone

HERE = os.path.dirname(os.path.abspath(__file__))
HOSTRUNS = os.path.join(os.path.dirname(HERE), "DevComms", "hostruns")
REQ_DIR = os.path.join(HOSTRUNS, "requests")
RES_DIR = os.path.join(HOSTRUNS, "results")
STOP = os.path.join(HOSTRUNS, "STOP")
FENCE = os.path.realpath(os.path.expanduser("~/Programming"))
ALLOWED = {"./gradlew", "gradlew", "python3", "python", "xvfb-run", "adb", "git"}
POLL_SECONDS = 3


def log(msg):
    print(f"[walk_service {datetime.now().strftime('%H:%M:%S')}] {msg}", flush=True)


def refuse(req_id, reason):
    with open(os.path.join(RES_DIR, req_id + ".json"), "w") as f:
        json.dump({"id": req_id, "returncode": None, "refused": reason}, f, indent=2)
    log(f"REFUSED {req_id}: {reason}")


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
    log(f"RUN {req_id}: {' '.join(cmd)}  (cwd={cwd}, timeout={timeout}s)")
    env = dict(os.environ, **{k: str(v) for k, v in req.get("env", {}).items()})
    with open(logfile, "w") as lf:
        try:
            # Popen + poll loop (not subprocess.run) so the terminal shows a HEARTBEAT while a long
            # run is in flight: every ~20s, print the log's size and its last non-blank line -- the
            # user can see at a glance that the child is producing output, not hanging.
            proc = subprocess.Popen(cmd, cwd=cwd, env=env, stdout=lf, stderr=subprocess.STDOUT)
            last_beat = time.time()
            while True:
                try:
                    rc = proc.wait(timeout=2)
                    break
                except subprocess.TimeoutExpired:
                    pass
                if time.time() - t0 > timeout:
                    proc.kill()
                    proc.wait()
                    rc = -9
                    lf.write(f"\nwalk_service: TIMEOUT after {timeout}s\n")
                    break
                if time.time() - last_beat >= 20:
                    last_beat = time.time()
                    tail = ""
                    try:
                        with open(logfile, "rb") as rf:
                            rf.seek(max(0, os.path.getsize(logfile) - 4096))
                            lines = [l for l in rf.read().decode("utf-8", "replace").splitlines()
                                     if l.strip()]
                            tail = lines[-1][:110] if lines else "(no output yet)"
                    except Exception:                             # noqa: BLE001 -- heartbeat must never kill the run
                        tail = "(log unreadable)"
                    log(f"  … {req_id} {int(time.time() - t0)}s  {os.path.getsize(logfile)}B  | {tail}")
        except Exception as e:                                    # noqa: BLE001
            rc = -1
            lf.write(f"\nwalk_service: LAUNCH FAILED: {type(e).__name__}: {e}\n")
    with open(os.path.join(RES_DIR, req_id + ".json"), "w") as f:
        json.dump({"id": req_id, "returncode": rc, "seconds": round(time.time() - t0, 1),
                   "started": started, "finished": datetime.now(timezone.utc).isoformat()},
                  f, indent=2)
    log(f"DONE {req_id}: rc={rc} ({round(time.time() - t0, 1)}s) -> results/{req_id}.log")


def main():
    os.makedirs(REQ_DIR, exist_ok=True)
    os.makedirs(RES_DIR, exist_ok=True)
    log(f"watching {REQ_DIR} (stop: ctrl-C, or touch {STOP})")
    while True:
        if os.path.exists(STOP):
            log("STOP file present -- exiting. (delete DevComms/hostruns/STOP to allow restart)")
            return 0
        pending = sorted(f for f in os.listdir(REQ_DIR) if f.endswith(".json")
                         and not os.path.exists(os.path.join(RES_DIR, f)))
        for name in pending:
            run_request(os.path.join(REQ_DIR, name))
        time.sleep(POLL_SECONDS)


if __name__ == "__main__":
    sys.exit(main())
