# log_85 — oracle reach: dependency closure + enum entries + default params + @Test

Date: 2026-06-27
Type: implementation + measurement. Continuation of log_84 (oracle stood up). The
oracle drives this turn: every change is judged by methods passing, not the compile gate.

## The move — make the oracle load more than one file

log_84 ran each engine in isolation; almost everything was red with `NameError` for the
domain types the engine references. This turn closes that and the gaps it exposed.

### 1. Dependency-closure loading (the headline)
`oracle.py` now builds a corpus **symbol index** (top-level decl name → defining .kt) and
resolves the **transitive closure** of types an engine+test reference. Deps are transpiled
and exec'd into the namespace by a **multi-pass loader** (a module that NameErrors because
its own dep isn't loaded yet is deferred to the next pass — resolves inter-dep ordering
without a real toposort). A dep that doesn't transpile is reported (e.g. `OnboardingScreen`)
rather than crashing the run.

### 2. Transpiler gaps the closure immediately exposed (all general wins)
- **Enum entries were silently dropped.** `enum class X { A, B }` emitted `class X: pass`
  with no `A`/`B` — every enum-using engine failed `X.A`. Now each entry is a class-level
  singleton instance (`X.A = X(args)`), with `.name`/`.ordinal`/`_entries` set (identity
  `==` matches Kotlin enum identity). Also fixed: enum **methods** missing `self`
  (`enum_class_body` wasn't recognized as in-class).
- **Kotlin default parameters were dropped.** The default value is a *sibling* of the
  `parameter` node (after a `=`), not a child. Now paired and emitted as Python defaults.
  A default that references `self.` is NOT def-time-safe in Python (the `def` executes
  during class-body exec) → emit a `None` sentinel + a body guard (`if x is None: x = …`).
- **JUnit `@Test` now survives** as an identity decorator (`kotlin_rt` tags the method),
  so the oracle runs real `@Test` methods and `@Before` setup — not `private fun` helpers
  it was previously executing as tests (a false-error source). `@Before/@After/@Ignore`
  too. Other annotations still dropped.
- `kotlin_rt` grew the obvious stdlib: `Pair`/`Triple`, `emptySet`,
  `mutable{List,Set,Map}Of`, `require`/`check`/`requireNotNull`/`checkNotNull`.

## Reach (oracle.py --all)

| | passing methods | engines fully green |
|---|---:|---:|
| log_84 (isolated) | 5 | 1/10 |
| **this turn** | **22** | 1/10, +3 partial |

NotificationTriggers 5/5 · AutoregulationEngine 6/59 · CalibrationEngine 5/15 ·
RestartEngine 6/17. Each passing method is a JVM-verified assertion now satisfied by the
TRANSPILED engine — genuine behavioral equivalence on those inputs, not compile-clean.

## Next worklist (what the remaining reds bucket into)
1. **Extension-function call sites.** `recv.extFn()` becomes a top-level `def extFn(self)`;
   the call `recv.extFn()` doesn't resolve to it (AttributeError). Needs the call site to
   rewrite `recv.extFn(a)` → `extFn(recv, a)` for known top-level extensions.
2. **Kotlin stdlib METHOD mapping (WRAP).** `xs.isEmpty()`, `n.coerceAtMost(m)`,
   `.coerceIn(...)` — Python builtins can't carry these methods; map at the call site
   (`xs.isEmpty()` → `len(xs)==0`, `coerceAtMost`→min, …).
3. **Nested types.** `private data class Rung` inside `object WarmupEngine`, `VolumeLandmark`
   nested in a periodization type — the index only scans top-level decls, and bare refs
   from the enclosing class's own methods need qualifying (`Rung` → `WarmupEngine.Rung`).

Each is the next iterate-loop turn, oracle-judged. The compile gate is behind us; the
oracle is now the frontier.
