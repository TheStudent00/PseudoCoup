#!/usr/bin/env bash
# add-commit-push for both repos.
#
# Hardened against the recurring block: an interrupted git process (including git run inside
# the Cowork sandbox, whose mount can CREATE .git/index.lock but is DENIED deleting it) leaves
# a stale .git/index.lock behind, which makes `git add`/`git commit` refuse. This script clears
# such a stale lock (only when no git is actually running), tolerates "nothing to commit", and
# keeps going so one repo's problem never blocks the other.
#
# Usage:  ./WFL_and_PseudoCoup_v0_git_push.sh ["commit message"]   (message defaults to "update")

set +e
MSG="${1:-update}"

for repo in ~/Programming/WFL_MixingCenter ~/Programming/PseudoCoup_v0; do
    echo "=== $repo ==="
    cd "$repo" 2>/dev/null || { echo "  cannot cd into $repo, skipping"; continue; }

    if [ -f .git/index.lock ] && ! pgrep -x git >/dev/null 2>&1; then
        echo "  clearing stale .git/index.lock (no git process running)"
        rm -f .git/index.lock
    fi

    git add -A
    if git diff --cached --quiet; then
        echo "  nothing to commit"
    else
        git commit -m "$MSG"
    fi
    git push
done
