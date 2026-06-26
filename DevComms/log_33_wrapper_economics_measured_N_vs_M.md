# log_33 — wrapper economics, measured: N (distinct API) << M (call sites), ~7:1 overall

Date: 2026-06-25
Type: measurement + self-correction. In log_32 I wrote that a wrapper "relocates the hand-work,
doesn't delete it." That's true but I pitched it as if the relocation were a wash. It isn't — and
the user called it: wiring **N distinct APIs once** vs hand-patching **M call sites** is a real
compression, because N << M. This logs the measured numbers (imports = the honest N; my earlier
regex distinct-counts were inflated by WFL's own types/methods and are discarded).

## N (distinct framework surface a wrapper implements once) vs M (call sites)

N is measured from `import` statements — the exact framework symbols WFL depends on, no noise:

| subsystem | N (distinct, imported) | M (call sites) | leverage |
|---|---:|---:|---:|
| `kotlinx.coroutines.flow.*` | 21 | 344 | ~16:1 |
| `kotlinx.coroutines.*` (scope/launch/delay) | 29 | 149 | ~5:1 |
| `androidx.compose.*` (composables+modifiers+runtime) | 227 | 1,218 Modifier + 257 @Composable | ~6.5:1 |
| `androidx.room.*` | 21 | all DB access | ~14:1 |
| dagger/hilt/javax.inject | 14 | 159 | ~11:1 |
| **total framework** | **~300** | **~2,000+** | **~7:1** |

The user's "tens of API objects vs hundreds-to-thousands of API calls" framing is correct. The
wrapper layer's cost scales with N (~300), not M (~2,000+). That compression is the entire value of
the shim approach, and log_31/32 undersold it.

## Two refinements (sharpen, don't reverse)

1. **The 227 Compose symbols aren't uniform cost.** Most are trivial value types (`Color`, `Dp`,
   `RoundedCornerShape`, `PaddingValues`, `Alignment`) — near-free. ~10–20 have real runtime depth:
   `LazyColumn`/`LazyRow`/`HorizontalPager` (virtualization + scroll state), the `remember*` family
   (state retention / slot semantics), `detectHorizontalDragGestures`, animation. So cost is
   bounded by N, but a handful of the N are individually expensive. Still N, not M.
2. **The UI slice of N already exists — it's the kit.** PseudoFlutter already implements the Compose
   subset PC's built screens use. Marginal Compose-N to add = only the symbols WFL uses that the kit
   doesn't yet cover, not 227 from scratch.

## What this changes

The economics now favor the wrapper path more clearly than my earlier hedging implied — *for building
new surface*. Concretely:

- **Flow shim is the standout** (21 distinct operators → 344 sites, 16:1) and it's the one wrapper PC
  never built (it hand-lowered Flow→sync). Highest leverage, currently missing. The full operator set
  is small and known: `combine stateIn flatMapLatest mapLatest map filter distinctUntilChanged onEach
  asStateFlow asSharedFlow collect collectLatest first firstOrNull drop debounce flowOf update
  MutableStateFlow MutableSharedFlow SharingStarted`.
- **Room / DI shims** are small-N, high-leverage, tractable.
- **Compose** is the lower-leverage, partly-already-built (kit) piece, with ~10–20 expensive symbols.

Caveat unchanged from log_32: wrappers cover the *runtime* gap (Tier 2/3). The *expression* gap
(Tier 1 — `?.` 488, `?:` 474, `.copy(` 346, `let/…` 242, `when` 108, templates 526) is still owed as
a lowering pass for emitted code to call the wrappers. That pass is also N-bounded (~15 rules), not M.

Pointers: log_31 (tiers + counts), log_32 (the wrapper reframe this corrects), log_30 (the audit).
