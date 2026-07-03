"""fidelity.py -- the layout-fidelity GAUGE: re-run the two-engine dump + diff, print one summary line.

For each instrumented screen:
  1. the Kotlin ground truth: gradle LayoutDumpTest renders it with the REAL Compose engine (Robolectric,
     headless) and dumps every component's exact box;
  2. the Python side: inspect_layout.py renders it with the kivy kit at the same display size and dumps
     the same format;
  3. layout_diff.py normalizes both to percent-of-display and passes components within a tolerance band.

track.py runs this like any other gauge and charts the number -- measured, never hand-typed.
"""
import os
import re
import subprocess
import sys

SCREENS = ["GymListScreen"]          # extend as more screens get a fixture in LayoutDumpTest
WFL = os.path.expanduser("~/Programming/WFL_MixingCenter/WFL")
RENDER = os.path.expanduser("~/Programming/WFL_MixingCenter/render")
JAVA_HOME = "/usr/lib/jvm/java-25-openjdk-amd64"


def run(cmd, cwd, env_extra=None, timeout=420):
    env = dict(os.environ, **(env_extra or {}))
    r = subprocess.run(cmd, cwd=cwd, env=env, capture_output=True, text=True, timeout=timeout)
    return r.returncode, r.stdout + r.stderr


def main():
    rc, out = run(["./gradlew", ":app:testDebugUnitTest", "--tests",
                   "com.sara.workoutforlife.layout.LayoutDumpTest"], WFL,
                  {"JAVA_HOME": JAVA_HOME})
    if rc != 0:
        print(out[-1500:])
        raise SystemExit("fidelity.py: the compose ground-truth dump failed (above)")
    passed = total = 0
    for screen in SCREENS:
        rc, out = run(["xvfb-run", "-a", "python3", "inspect_layout.py", screen], RENDER,
                      {"DISPLAY_SIZE": "411x915"})
        if rc != 0:
            print(out[-1500:])
            raise SystemExit(f"fidelity.py: the kivy dump failed for {screen} (above)")
        rc, out = run([sys.executable, "layout_diff.py", screen], RENDER)
        m = re.search(r"LAYOUT FIDELITY:\s*\d+%\s*\((\d+)/(\d+)\)", out)
        if rc != 0 or m is None:
            print(out[-1500:])
            raise SystemExit(f"fidelity.py: the diff failed for {screen} (above)")
        p, t = int(m.group(1)), int(m.group(2))
        passed += p
        total += t
        print(f"  {screen}: {p}/{t} within tolerance")
    print(f"FIDELITY ALL: {passed}/{total} components within tolerance "
          f"({len(SCREENS)} screen{'s' if len(SCREENS) != 1 else ''})")


if __name__ == "__main__":
    main()
