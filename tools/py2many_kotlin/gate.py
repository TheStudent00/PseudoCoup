#!/usr/bin/env python3
"""
gate.py -- granular compile gate over a directory of one-construct-per-file
Python sources. For each constructs/*.py: transpile with the patched py2many
--kotlin backend, then COMPILE the result with kotlinc in isolation, and record
PASS / FAIL(+first error). The compile is the oracle: a construct "maps cleanly"
only if its Kotlin compiles.

This is how the atlas grows toward WFL's real construct inventory -- add a
construct file, re-run, and any new py2many gap shows up as a FAIL with the exact
kotlinc error to fix (in pykt.patch) or to route to the wrap-layer.

Usage:  python3 gate.py [constructs_dir]
Exit 0 iff every construct compiles.
"""
import os
import shutil
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
JAVA_HOME = os.environ.get("JAVA_HOME", "/usr/lib/jvm/java-25-openjdk-amd64")


def find_kotlinc():
    for p in os.environ.get("PATH", "").split(":"):
        c = os.path.join(p, "kotlinc")
        if os.path.exists(c):
            return c
    hits = []
    for root, _, files in os.walk("/snap/android-studio"):
        if "kotlinc" in files:
            hits.append(os.path.join(root, "kotlinc"))
    return sorted(hits)[-1] if hits else None


def main():
    cdir = sys.argv[1] if len(sys.argv) > 1 else os.path.join(HERE, "constructs")
    kotlinc = find_kotlinc()
    if not kotlinc:
        print("FAIL: no kotlinc found")
        return 3
    env = dict(os.environ, JAVA_HOME=JAVA_HOME)
    out = os.path.join(HERE, "_gate_out")
    os.makedirs(out, exist_ok=True)

    files = sorted(f for f in os.listdir(cdir) if f.endswith(".py"))
    results = []
    for f in files:
        name = f[:-3]
        src = os.path.join(cdir, f)
        kt = os.path.join(out, name + ".kt")
        # transpile (ktlint formatter error is cosmetic; the .kt still writes)
        subprocess.run([sys.executable, "-m", "py2many", "--kotlin", src],
                       cwd=out, env=env, capture_output=True)
        gen = os.path.join(cdir, name + ".kt")
        if os.path.exists(gen):
            # shutil.move (not os.replace) to tolerate a cases dir on a
            # different filesystem than _gate_out (cross-device link).
            if os.path.exists(kt):
                os.remove(kt)
            shutil.move(gen, kt)
        if not os.path.exists(kt):
            results.append((name, "NO-KT", ""))
            continue
        # compile in isolation
        r = subprocess.run([kotlinc, kt, "-d", os.path.join(out, name + ".jar")],
                           env=env, capture_output=True, text=True)
        if r.returncode == 0:
            results.append((name, "PASS", ""))
        else:
            err = ""
            for line in r.stderr.splitlines():
                if ": error:" in line:
                    err = line.split(": error:", 1)[1].strip()
                    break
            results.append((name, "FAIL", err))

    npass = sum(1 for _, s, _ in results if s == "PASS")
    print(f"\n=== construct compile gate: {npass}/{len(results)} PASS ===\n")
    for name, status, err in results:
        mark = "✓" if status == "PASS" else "✗"
        line = f"  {mark} {name:22} {status}"
        if err:
            line += f"  — {err[:70]}"
        print(line)
    return 0 if npass == len(results) else 1


if __name__ == "__main__":
    sys.exit(main())
