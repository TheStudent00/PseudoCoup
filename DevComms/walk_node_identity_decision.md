# The next decision: how the kt walker identifies a node at fire time

STATUS: OPEN — owner's decision, not made. This doc explains the decision so it can be made. It does
not make it and does not implement it (protocol §7: an ask for an explanation is an ask for exactly that).

SOURCING (protocol §12): the record / replay / frontier mechanism below is cited to
`DevComms/walker_slice2_kotlin.md`, which lives in THIS repo and I re-read this session. The identity-field
changes — b70d65e added `(label, handlerKind)`, 664017d added `boundsKey` — are described in `HANDOFF.md`'s
two 2026-07-09 blocks. The actual WFL_MixingCenter source (`WalkRecorderTest.kt`, and the
`resolveTarget` / `InteractiveRef` / `PathStep` names inside it) is NOT reachable from this workspace and was
NOT read this session; every claim resting on it carries the mark "(source not read this session)".

---

## Direct answer

The decision is: **when is a node's identity established — reconstructed at fire time from what is on
screen, or assigned once at record time and carried forward in the walk file?**

Two directions:

  (a) keep reconstructing identity at fire time, but from MORE fields, so fewer nodes share one identity.
  (b) stop reconstructing at fire time — every callable emits its own UNIQUE id when it runs (before the
      framework API it wraps, if it wraps one), that id is its unique entry in the ledger, both transpiler
      sides emit the same id for corresponding call sites, and the walker matches on that id alone.

(a) changes WHICH fields make up the identity. (b) changes WHO decides identity and WHEN — the callable
itself, at the moment it runs, not the walker reconstructing it afterward. That is the real fork, and it is
a question about what a node's identity *is* — which is why it is yours, not mine (protocol §6: ontology is
the owner's call). (b) is the design the owner has asked for repeatedly across project versions; this doc's
earlier draft under-reached it, see the correction under Direction (b).

---

## The model you need first

**What the walker does.** From the boot screen the kt recorder enumerates every interactive node, fires each
action, records the resulting state and the edge, and adds each newly-reached screen to a to-do list it
calls the `frontier` (a FIFO `ArrayList<Frame>`, `walker_slice2_kotlin.md:108`). To reach a `frontier` Frame
later it does NOT keep the app parked on that screen — it boots a fresh app and REPLAYS the recorded path of
actions to get back there (`mountFreshApp` / `replayTo`, `walker_slice2_kotlin.md:118`).

So every recorded action runs at least twice: once at **record time** when first discovered, and again each
time a later path replays through it — call that second run **fire time** (glossary below).

**What has to be true for fire time to work.** During replay the walker must find, in the freshly-booted
screen, the SAME node it recorded. It finds it by matching a set of fields stored on the recorded step
(on `PathStep` / `InteractiveRef` — source not read this session; described in `HANDOFF.md`):

  - originally just `ordinal` — the node's position index in the record-time enumeration.
  - b70d65e added `(label, handlerKind)` — because a bare `ordinal` captured against one settled screen
    could drift onto a DIFFERENT node when replayed against a differently-settled screen (`HANDOFF.md`,
    superseded 07-09 block).
  - 664017d added `boundsKey` — the node's on-screen box rounded to whole pixels — used ONLY to narrow an
    already-ambiguous `(label, handlerKind)` match down to one node (`HANDOFF.md`, top block).

The fire-time match, as one call flow:

  `WalkRecorder.replayTo(path)` --> `WalkRecorder.resolveTarget(step)`

`resolveTarget` matches the stored fields against the booted screen. One matching node: fire it. More than
one matching node: the match is **Ambiguous**, and 664017d discards it (same as a node that is missing
entirely).

**Why ambiguity forms — the case that breaks it.** An icon-only floating action button has no text anywhere
in its subtree, so `label` falls back to the generic node kind: the bare string `"Button"`. The pair
(`label="Button"`, `handlerKind="onClick"`) is then shared by many unrelated buttons across many screens.
`177_walk_diff_refix.log` shows exactly this population — nodes logged as `kind='Button' text=''
interactive=True` with nothing to tell them apart (lines 12, 41, 72, 96, 97, and on). 664017d's `boundsKey`
was meant to narrow that set to one node; the run shows it often does not, so these steps resolve Ambiguous,
get discarded, and coverage fell to 7 states (`HANDOFF.md` top block; `177_walk_diff_refix.log:3`).

That is the thing both directions below are trying to fix: at fire time, one recorded node's identity
matches more than one on-screen node.

---

## Direction (a) — a stronger identity, still reconstructed at fire time

**What it is, mechanically.** Add more fields to the identity that `resolveTarget` matches on — specifically
the node's `route` (which screen it is on) and its subtree structure (the shape and text of its
descendants). Two `"Button"` / `"onClick"` nodes on different screens, or sitting over different subtrees, no
longer share one identity.

**Where it lives.** `PathStep` / `InteractiveRef` (the stored fields) and `resolveTarget` (the matching) —
the same two places b70d65e and 664017d already changed, in `WalkRecorderTest.kt` (source not read this
session).

**Why the system would want it.** The FAB case fails precisely because `label` collapses to `"Button"` and
`boundsKey` does not narrow. `route` + subtree carry information that stays distinct even when `label` does
not.

**What we would do.** Extend the stored identity and the match to include `route` + a subtree signature;
keep 664017d's discard-on-ambiguous rule, but expect far fewer Ambiguous results because the identity is now
rarely shared.

**Cost / risk.** Still reconstructed at fire time from what is on screen. If the subtree renders even
slightly differently at fire time than at record time — different seeded data, a changed count — the subtree
signature will not match, and the node becomes Missing instead of Ambiguous: same discard, different reason.
(a) trades ambiguity for fragility to any record-vs-fire rendering difference. It reduces the bug; it does
not remove the class of it.

---

## Direction (b) — every callable emits its own unique id when it runs

**What it is, mechanically.** The identity is NOT reconstructed by the walker and NOT assigned by the walker
at record time — it is emitted by the CALLABLE ITSELF at runtime. Every emitting call site owns a unique id,
which is its one entry in the ledger; when the callable runs it sends that id out — and if the callable
wraps a framework API (e.g. a Compose `FloatingActionButton`), it sends the id BEFORE calling that API. Both
transpiler sides (PC/Python and KT) emit the SAME id for corresponding call sites, so a py run and a kt run
line up entry-for-entry with no mystery. The walker just reads the emitted id; `resolveTarget` matches on it
and nothing else.

**Where it lives.** In the transpiled app code on both sides (each call site wrapped so it emits its id
before the real API), in the ledger that assigns the unique ids, and in the walker (reading the id off the
emission stream instead of reconstructing from `(label, handlerKind, boundsKey)`). What ALREADY exists and
what does NOT, verified in source this session:
  - the runtime emission exists on both sides today — `ACTIVATE` / `MOUNT` lines, `WalkRecorderTest.kt:1130`
    and `render/walker.py:625` — but they carry NO unique id, only `(kind, label, handlerKind, ordinal,
    origin)`, where `origin` is a best-effort bounds-correlated source coordinate (`resolveOrigin`,
    `WalkRecorderTest.kt:1597`), not an id the callable owns.
  - `resolveTarget` (`WalkRecorderTest.kt:591`) reads NONE of that emission — it filters
    `it.label == recordedLabel && it.handlerKind == recordedHandlerKind`, then narrows by `boundsKey`.
  So this direction is not "invent a new mechanism from nothing" — it is: give the existing emission a unique
  id, and wire the walker to read it.

**Why the system would want it.** It removes the reconstruct-at-fire-time step entirely — the source of BOTH
the ambiguity (a) fights and the fragility (a) risks. If every live instance announces a unique id, there is
nothing to guess and nothing to collide.

**What the id must be — and why SOURCE COORDINATE is NOT enough (correcting this doc's earlier draft).** An
earlier draft named the Kotlin source coordinate (`File.kt:line`) the strongest candidate. That was wrong,
and the source proves it: `oracle_registry` (`render/oracle_registry.py`) is deliberately built as
`{coordinate: [name, ...]}` — LIST-valued — because one line legitimately backs MULTIPLE callables. Its own
docstring gives the exact case: `ExtendedFloatingActionButton(icon = { Icon(...) }, text = { Text(...) })`
collapses the outer call and both inner lambdas onto ONE source line. On top of that, repeated instances (a
list of identical cards) all render from one coordinate. So source coordinate reduces ambiguity but does not
remove it — it collides precisely where uniqueness is required. A genuinely unique id therefore needs two
parts:
  - a per-call-site ledger id — stable, assigned once (this is the ledger entry), and
  - a per-instance key — distinguishes repeated renders of that SAME call site at runtime.
Together they are unique per live instance, which is what "unique to its entry in the ledger" requires and
what neither source coordinate nor `boundsKey` gives.

**The essence, in code (illustrative, not the real signatures).** The shape of the idea, both sides:

```kotlin
// LEDGER: one unique id per emitting call site, assigned once (NOT the source line, which collides).
enum class LedgerId { TodayScreen_fab_add, TodayScreen_fab_log, /* ... one per call site ... */ }

// The transpiler rewrites   FloatingActionButton(onClick = add) { Icon(...) }
//                    into    TrackedFab(LedgerId.TodayScreen_fab_add, onClick = add) { Icon(...) }
@Composable
fun TrackedFab(id: LedgerId, onClick: () -> Unit, content: @Composable () -> Unit) {
    val instance = rememberInstanceKey(id)          // distinguishes repeated renders of the SAME call site
    emitId(id, instance, engine = "kt")             // <-- id signal goes out BEFORE the framework API runs
    FloatingActionButton(onClick = onClick, content = content)   // the real API, now behind the signal
}
```

```python
# Same ledger id the KT side emits for this call site -> py and kt line up entry-for-entry.
def TrackedFab(id, on_click, content):
    instance = instance_key(id)
    emit_id(id, instance, engine="py")              # id signal BEFORE the framework API
    return FloatingActionButton(on_click=on_click, content=content)
```

```kotlin
// The walker's recorded identity BECOMES the id -- not (label, handlerKind, boundsKey).
data class PathStep(val id: LedgerId, val instance: InstanceKey)

fun resolveTarget(onScreen: List<InteractiveRef>, step: PathStep): ResolveOutcome {
    val match = onScreen.filter { it.id == step.id && it.instance == step.instance }
    return if (match.size == 1) Exact(match[0]) else Missing   // never Ambiguous: id is unique by construction
}
```

**Cost / risk.** Needs every call site on both sides to carry the wrapper and every live instance to produce
its instance key on a fresh boot. It is a bigger change than (a) — it touches the transpiler's emission on
both sides, the walk file format, and `resolveTarget`. Note `loadProgress` already handles three
progress-file generations (bare-ordinal, then +`(label,handlerKind)`, then +`boundsKey`); this would add a
fourth (`HANDOFF.md` top block, WFL source for `loadProgress` not read this session). But unlike (a) and
unlike source coordinate, it removes the ambiguity by construction rather than shrinking it.

---

## The tradeoff that makes this a real decision

(a) is small and local — two functions, no file-format change — but keeps the walker guessing from
on-screen state, so it can only ever reduce ambiguity, never remove the class of bug, and it opens a new
Missing failure when rendering differs between record and fire.

(b) is larger — the transpiler's emission on both sides + walk-file format + `resolveTarget` — but removes
the guess entirely: each live instance announces a unique id (per-call-site ledger id + per-instance key),
so there is nothing to reconstruct and nothing to collide. Source coordinate alone does NOT achieve this —
the registry is list-valued by design (nested composables and repeated instances share a line), so it only
shrinks the ambiguity.

Recommendation (protocol §6 — a recommendation, not a decision): (b) as described here — every callable
emits its own unique id, unique to its ledger entry, both sides in lockstep, walker matches on the id. This
is the design the owner has asked for repeatedly. The earlier draft's source-coordinate proposal is
retracted: it is a weaker form of (b) that collides exactly where uniqueness is needed. The call is yours.

---

## Glossary

id signal
    the owner's term for the record a callable sends out when it runs, carrying a unique id (and other info).
    example tied to context:
        today the closest thing is the `ACTIVATE` log line (`WalkRecorderTest.kt:1130`, `render/walker.py:625`),
        but it has NO unique id — it emits `(kind, label, handlerKind, ordinal, origin)`. Direction (b) is
        what turns that line into a real id signal.

ledger
    the owner's term for the registry of unique entries an id signal points into, one entry per callable.
    example tied to context:
        the nearest existing thing is `oracle_registry` (`render/oracle_registry.py`), but its key
        (`File.kt:line`) is NON-unique per callable (list-valued by design), so it is not yet a ledger in
        this sense. (Separately, `DevComms/log_62_ledger_v1.md`'s `ledger.json` is an offline KT↔PC matching
        table for the diff tool — a different thing, not the runtime ledger.)

record time
    the walker's first pass over a screen, enumerating its nodes and firing each action for the first time.
    example tied to context:
        `WalkRecorder` enumerating the boot screen and storing a `PathStep` for the icon-only "today" FAB.

fire time
    any LATER execution of an already-recorded action, reached by replaying a path to a `frontier` Frame.
    example tied to context:
        `replayTo()` booting a fresh app and re-running the recorded path to reach the "today" FAB again,
        where its recorded identity must re-match one node.

node identity
    the set of fields the walker uses at fire time to find the same node it recorded.
    example tied to context:
        today it is (`ordinal`, `label`, `handlerKind`, `boundsKey`) on `PathStep`; the whole decision is
        whether to add fields to it (direction a) or replace it with a stable id (direction b).

frontier Frame
    one entry on the walker's to-do list of screens reached but not yet fully explored.
    example tied to context:
        `frontier` is a FIFO `ArrayList<Frame>` (`walker_slice2_kotlin.md:108`); each step replays to one
        Frame and fires one action.

Ambiguous resolution
    a fire-time match where the recorded identity fits MORE THAN ONE node in the booted screen.
    example tied to context:
        (`label="Button"`, `handlerKind="onClick"`) matching several text-less buttons in
        `177_walk_diff_refix.log`; 664017d discards these instead of firing a guessed one.

source coordinate
    the `file:line` in the Kotlin source where a node is declared; stable across boots.
    example tied to context:
        `mount_diff` joins kt and py mounts on it (`178_mount_diff_refix.log` header, "joined on Kotlin
        source coordinate"); the candidate stable id for direction (b).
