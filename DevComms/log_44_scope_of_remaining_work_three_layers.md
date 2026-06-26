# log_44 — scope of the remaining work: the API wrappers are 1 of 3 layers, and the smallest

Date: 2026-06-25
Type: scope (grounded — counts from the real WFL tree). Answers: "show me the scope; I assume the
remaining work is wiring up the logic of the API wrappers."

## Direct answer to the assumption

Wiring up the API wrappers (the **Flow runtime**) is real work — but it's **one of three remaining
layers, and the smallest.** It's invisible from where the wrappers sit because the wrappers are at the
*bottom*; the bulk of the work is the **domain layer in the middle** that the VMs call into, which
doesn't exist in Python at all yet (0 stubs today). Here's the whole picture, measured.

## What's DONE

The **VM logic layer** — all 27 ViewModels — transpiles to valid, instance-shaped, no-silent-drop
Python. Gate-green. That's the layer we've been working; it's finished enough to build on.

## What's LEFT to make it actually RUN (Path B), by layer

| layer | what it is | size (measured) | nature |
|---|---|---|---|
| **1. Flow runtime** (the wrappers you named) | make `core/flow.py`+`core/coroutines.py` actually carry data: `combine` re-emit, `stateIn`/`SharingStarted`, `flatMapLatest` cancel-previous, `collect`, scopes | **~2 files**, ~21 operators — a bounded library (log_33) | new engineering, but *finite and knowable* |
| **2. Domain closure** (data + engine) | the entities/DAOs/repositories/engines the VMs import | **144 files / ~15,700 LOC** (data 135/13.8k + engine 9/1.9k); **0 exist in Python today** | a *second transpile pass*, bigger than the VM layer |
| **3. Screens** (Tier 3) | the actual UI | **60 Compose files** → hand-built on the kit | not transpiler work; hand UI |

Plus cleanup: the **46 residual VM TODOs**, the **`combine` keyword-only bug** (log_42), and
**stdlib shims** the transpiled code calls bare (`java.time` — Instant/LocalDate/ZoneId/DayOfWeek —
`maxOf`, `listOf`/`mapOf`, `LinkedHashMap`, …).

## Why layer 2 is the real cost (and why it's not "wiring wrappers")

The VMs don't just call the Flow operators — they call into a whole domain layer. Concretely:

- **TodayViewModel alone imports 33 in-project symbols** that don't exist in Python: 6 DAOs, 4
  entities, 3 relations, 9 model enums, 5 repositories, 2 engines.
- **Across all 27 VMs: 124 distinct in-project symbols** imported. Their transitive closure is
  essentially the entire 144-file data+engine layer.
- That layer is **harder than the VMs in places**, not just bigger:
  - **27 `@Entity` tables + 26 `@Dao` interfaces with 149 `@Query` SQL statements** (154 multiline).
    To run, these must execute against a real database (sqlite) or be stubbed — i.e. you're porting
    persistence, not translating logic.
  - **81 `@TypeConverter`s** (enum/date/json <-> column mappings) to reproduce.
  - **18 repositories + 9 engines** of business logic (the engines transpile like VMs; the
    repositories wrap DAOs + Flows).

So: to make even *one* VM instantiate and run, you need its full dependency closure ported. There is
no "just wire the wrappers" shortcut, because the wrappers are the floor — the house above them
(domain) is what's missing.

## Honest proportions

If the VM layer we just finished is "1 unit" of effort:
- **Layer 1 (Flow runtime):** ~0.3-0.5 unit — bounded, but genuinely new (reactivity semantics).
- **Layer 2 (domain):** **~1.5-2 units** — larger than the VMs, plus the persistence/SQL execution
  that has no analog in the VM work. **This is the dominant cost.**
- **Layer 3 (screens):** ~1-1.5 units of *hand* UI work on the kit (60 files), independent of the
  transpiler.

So "wiring up the API wrappers" is roughly **10-15%** of what remains. The other 85% is the domain
port (layer 2) and the screens (layer 3).

## Why this maps back to the fork (log_43)

This is exactly why **Path B is months-scale** and why **Path C (hybrid) sidesteps most of it**: in
C you never build all of layer 1+2 up front — for a given feature you transpile its VM, **lower its
Flow→synchronous** (so no Flow runtime needed), **stub only that feature's domain deps** (not all 144
files), and hand-build its one screen. You pay layer-2 cost per-feature, only for features you
actually ship, instead of porting the entire data layer to run anything.

If the goal is "all of WFL, auto-synced" → that's the full layers 1+2+3 (Path B). If it's "more
features, pragmatically" → C amortizes layer 2 across only what you build.

Pointers: log_43 (the fork), log_33 (the Flow-runtime/wrapper economics), log_42 (current state).
Measurements: `~/Programming/WFL/.../{data,engine}` (144 files / 15.7k LOC), 124 distinct VM imports.
