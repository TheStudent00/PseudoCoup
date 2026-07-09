# log_136 — AUDIT: is the id-signal → unique-ledger design implemented? Are the ledger IDs unique?

Date: 2026-07-09
Type: findings audit (owner asked to be assured only if true). Source read THIS session unless a line
says otherwise. No code changed by this audit.

## The question (owner's words)

The design: every callable emits an "id signal" about its identity when it runs (before the wrapped API,
if it is behind one), on BOTH transpiler sides, and each id signal is unique to its entry in the "ledger"
so runtime identity is never a mystery. Owner's refinement of HOW the id is generated: "unique branch paths
of the AST from the tree sitter -- as long as a node branch point tracks its own branches, it should be
unique."

Three findings, by cause, each with status + evidence.

## Finding 1 — the runtime id signal is NOT implemented for the walker. STATUS: open (unbuilt).

The emission exists on both sides but carries NO unique id:
  - KT `ACTIVATE` line, `WFL_MixingCenter/WFL/app/src/test/java/com/sara/workoutforlife/walk/WalkRecorderTest.kt:1130`
    — fields `(kind, label, handlerKind, ordinal, origin, outcome)`. `origin` is a best-effort
    bounds-correlated source coordinate (`resolveOrigin`, same file :1597), not an id the callable owns.
  - PY `ACTIVATE` line, `WFL_MixingCenter/render/walker.py:625` — same fields.
The walker's fire-time identity reads none of it. `resolveTarget` (`WalkRecorderTest.kt:591`) matches
`it.label == recordedLabel && it.handlerKind == recordedHandlerKind`, then narrows by `boundsKey` (a
stringified rectangle, :438), else falls back to raw `ordinal`. `PathStep` (:217) stores only
`(ordinal, label, handlerKind, boundsKey)` — no id, no origin, no source coordinate. So the ACTIVATE
`origin` is computed and thrown to a text log; the identity that decides which node to fire never sees it.

The registry the walker cross-checks against is coordinate-keyed and NON-UNIQUE by design:
`render/oracle_registry.py:_register` (:215) APPENDS `name` to `registry[coord]`'s LIST, because one
source line legitimately backs multiple callables (docstring, same function: the outer
`ExtendedFloatingActionButton(icon=(lambda: Icon(...)))` call collapses to the same coordinate as its inner
`Icon(...)` lambda). It is used only as a boolean "known coordinate?" logging check, never for node identity.

## Finding 2 — the branch-path id generator EXISTS but is NOT unique. STATUS: present, broken for uniqueness, and not wired to runtime.

The owner's branch-path scheme is real code. `tools/pseudokotlin/ui_ledger.py:264` (`render_node`) walks the
tree-sitter tree carrying `(depth, idx, path)` and builds each node's id as the root-to-node path:

    seg  = _segment(call, idx, comps)
    full = "/".join(path + [seg])                      # id = parent path + this segment
    ids.append(full)
    for i, c in enumerate(kids):
        render_node(c, name, depth + 1, i, path + [seg], lines, ids, comps)   # child index i passed down

`kit_ledger.py:217` (`render_tree`) does the identical walk on the kit side.

BUT the segment DROPS the child index whenever the node has a content anchor. `ui_ledger.py:238`
(`_segment`):
  - custom composable  -> `name`               (no idx)
  - field              -> `name[label]` else `name[idx]`
  - Icon/Image + desc  -> `name[desc=...]`      (no idx)
  - Text + text        -> `Text[<text>]`        (no idx)
  - fallthrough        -> `name[idx]`           (idx ONLY as last resort)

So the branch point does NOT "track its own branches" when a content anchor is available — the exact rule
the owner named as the uniqueness guarantee is the one not applied. Consequence: identical siblings collide
(same segment -> same `full` path):
  - two `Text["30 min"]` under one parent -> both `Text[30 min]`. Seen live:
    `DevComms/hostruns/results/177_walk_diff_refix.log:30` — `UNRESOLVED [py]: kind='Node' text='30 min'
    interactive=False count=2`.
  - a list of identical `ProgramCard`s -> all `ProgramCard`. That collision is why `ProgramCard ×2` had to
    be HAND-recorded as a special entry — `DevComms/log_62_ledger_v1.md`.

And even this non-unique path is not the identity anything matches on: the cross-side compare joins on the
bare content ANCHOR, not `full` — `kit_ledger.py` `compare`: `ca = {a for _, _, a, _ in compose_ids if a}`.
The runtime walker never touches the branch path at all (Finding 1).

FIX that would honor the owner's model: every segment carries its child index UNCONDITIONALLY (e.g.
`Text[3]:Text["30 min"]`, not the anchor alone), so the root-to-node path is unique by position regardless
of repeated content; THEN that path becomes the id the callable emits at runtime and the walker matches on.
This is direction (b) in `DevComms/walk_node_identity_decision.md` with the branch path as the id generator.

## Finding 3 — "ledger" names several different things. STATUS: inventory, for disambiguation.

  - `tools/pseudokotlin/ledger.py` — the CENTRAL structural/connective fidelity ledger: engine + model
    frames, each object's (name, 1-degree connections), KT static (tree-sitter) vs PY exec-introspect.
    Name-keyed, not runtime ids.
  - `tools/pseudokotlin/ui_ledger.py` + `kit_ledger.py` — the UI bucket of that ledger (see next section).
  - `render/oracle_registry.py` — coordinate registry, NON-unique by design (Finding 1).
  - `tools/dualgraph/ledger.json` — the "ledger v1" from `log_62`: a matcher-side hand-recorded KT↔PC
    correspondence table (3 seed entries). NOT in the live tree this session — the only `ledger.json` files
    present are under `_deprecated/runtime_uimap/`. `tools/dualgraph/` does not exist. STATUS: gone/absent.
  - `_deprecated/runtime_uimap/{pc,wfl}_ledger.json` — state-graph maps keyed by 64-hex STATE hashes
    (`nodes`/`edges`); per-state, not per-callable. STATUS: deprecated.

Net: no live ledger holds unique per-callable runtime ids. The unique-branch-path generator that exists
(Finding 2) is anchor-keyed, so not unique, and not wired to runtime.

## The ui_ledger / kit_ledger split (owner's follow-up: "why are there two?")

They are the two SIDES of the UI half of the central ledger, split because each side is read by a different
method. Not imported sub-modules of `ledger.py` (it stands alone); conceptually they fill the ui/ field it
reserves.

    ledger.py       central structural/connective ledger. ENGINE + MODEL frames only: (name, 1-degree
                    connections), KT static via tree-sitter, PY via exec + introspect. Reserves a
                    sizing/positioning field for ui/ frames, does NOT fill it. Imports neither of the below.
    ui_ledger.py    UI bucket, KOTLIN/Compose side. Fills the KT half of that reserved field: reads each
                    @Composable's layout intent STATICALLY from the Modifier chain. Owns the node-id scheme
                    (_segment / render_node). Writes <name>.ui.md.
    kit_ledger.py   UI bucket, PYTHON/kit side + the cross-side compare. Reads the kit tree by RUNTIME
                    TRACING the kit's ui.define_*(id, parent_id, ...) calls, normalizes into ui_ledger's
                    schema, and joins node-for-node on the content anchor. `import ui_ledger as UL` (:27).

So: ui_ledger = Compose side read statically; kit_ledger = kit side read by runtime trace + it holds the
compare. The only code dependency among the three is kit_ledger -> ui_ledger.
