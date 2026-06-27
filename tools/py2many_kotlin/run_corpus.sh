#!/usr/bin/env bash
#
# run_corpus.sh -- measure our patched py2many Kotlin backend against py2many's
# OWN test corpus (the curated, maintained construct set), not our toy atlas.
# Clones py2many shallow, runs the granular compile gate over tests/cases/*.py,
# and cross-references failures against which cases ship a committed Kotlin
# expected output (i.e. which constructs py2many actually claims to support).
#
# This is the external-validation measurement: it shows (a) our patches hold
# across py2many's supported Kotlin surface and (b) exactly which constructs
# py2many does NOT support for Kotlin (the real beyond-py2many backlog).
set -euo pipefail
HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
WORK="${1:-/tmp/py2many_corpus}"

if [ ! -d "$WORK/py2many_src" ]; then
  mkdir -p "$WORK"
  git clone --depth 1 https://github.com/py2many/py2many.git "$WORK/py2many_src"
fi
CASES="$WORK/py2many_src/tests/cases"
rm -f "$CASES"/*.kt

python3 "$HERE/gate.py" "$CASES" | tee "$WORK/corpus_gate.txt"

echo
echo "=== cross-ref: of cases py2many ships Kotlin support for (committed .kt), which fail? ==="
ls "$WORK/py2many_src/tests/expected/"*.kt | xargs -n1 basename | sed 's/.kt$//' | sort > "$WORK/_have.txt"
grep '✗' "$WORK/corpus_gate.txt" | awk '{print $2}' | sort > "$WORK/_fail.txt"
echo "supported-but-failing: $(comm -12 "$WORK/_have.txt" "$WORK/_fail.txt" | tr '\n' ' ')"
echo "failures with NO Kotlin support claimed: $(comm -13 "$WORK/_have.txt" "$WORK/_fail.txt" | wc -l)"
