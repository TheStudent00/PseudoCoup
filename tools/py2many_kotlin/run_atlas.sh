#!/usr/bin/env bash
#
# run_atlas.sh -- regenerate Kotlin from the construct atlas with the patched
# py2many backend, then COMPILE it with kotlinc. The compile is the anti-slop
# oracle: "looks idiomatic" is not "is valid Kotlin" (kotlinc caught a val-param
# reassignment that eyeballing missed). Exit 0 only if the jar builds.
#
# Prereqs: the pykt.patch in this dir must be applied to the installed py2many
# (see README). JDK + a kotlinc must exist (we auto-discover the Android Studio
# bundled one if `kotlinc` is not on PATH).
set -euo pipefail
HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$HERE"

export JAVA_HOME="${JAVA_HOME:-/usr/lib/jvm/java-25-openjdk-amd64}"
KOTLINC="$(command -v kotlinc || true)"
if [ -z "$KOTLINC" ]; then
  KOTLINC="$(find /snap/android-studio -name kotlinc -type f 2>/dev/null | sort | tail -1 || true)"
fi
[ -n "$KOTLINC" ] || { echo "FAIL: no kotlinc found"; exit 3; }

# 1. transpile atlas.py -> atlas.kt (ktlint formatter error is cosmetic; ignore)
python3 -m py2many --kotlin atlas.py >/dev/null 2>&1 || true
[ -f atlas.kt ] || { echo "FAIL: py2many produced no atlas.kt"; exit 2; }

# 2. compile -- the real verdict
echo "kotlinc: $KOTLINC"
if "$KOTLINC" atlas.kt -d atlas_out.jar 2>compile.err; then
  echo ">>> PASS: atlas.kt compiles clean (jar built) <<<"
  rm -f atlas_out.jar compile.err
  exit 0
else
  echo ">>> FAIL: kotlinc errors <<<"
  cat compile.err
  exit 1
fi
