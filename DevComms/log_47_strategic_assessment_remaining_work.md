# log_47 — Strategic Assessment: The Final Scope of Conversion

Date: 2026-06-25
Type: strategic assessment (synthesizing log_43, log_44, and the log_46 correction).

## The Pivot Insight
The realization in `log_46` radically simplifies the project's strategic horizon. The transpiler experiment had been operating in a "sandbox" (`build/literal/` and `core/`), which led to the mistaken assumption that the entirety of WFL's Domain layer (Engines, Repositories, DAOs) needed to be ported from scratch or heavily automated. 

However, looking at the actual Python application (`WFL_PseudoCoup/src/`), **~37,000 LOC of the domain layer is already hand-ported into synchronous Python**, along with ~4,500 LOC of hand-ported ViewModels. 

Because `WFL_PseudoCoup` intentionally abandoned Kotlin's reactive `Flow` architecture for a synchronous state paradigm, the transpiler is no longer expected to produce a perfectly "drop-in runnable" reactive product. Instead, its job firmly settles on **Path C**: acting as a hyper-accurate skeleton generator to accelerate the hand-porting process.

---

## What remains to complete the Kotlin-to-Python conversion

### 1. The Transpiler's Remaining Work (Automated Skeleton Generation)
The transpiler has successfully passed the hardest structural hurdles (Instance shaping, scope tracking, Enum generation, lambda extraction). Its remaining work is very finite:
*   **Drain the 46 residual TODOs:** Clear the final edge-case syntax markers (mostly related to missing standard library shims like `java.time`, `maxOf`, or `LinkedHashMap`) so the transpiler produces a 100% perfectly translated AST.
*   **Stop here:** Do *not* build a massive Python Flow runtime (`core/flow.py`). The actual app doesn't use it, so any effort spent building a complex reactive runtime is wasted.

### 2. The Hand-Wiring Remaining Work (The Final Mile)
This is where the actual labor remains. To bring the remaining "Tier 3" (deferred) features into `WFL_PseudoCoup`, a developer will take the transpiler's 1:1 Kotlin-accurate output and manually wire it:
*   **De-Reactification (Flow → Synchronous):** Because the transpiler faithfully reproduces Kotlin's `combine(...)` and `flatMapLatest` logic, a developer must manually strip these out and collapse them into the synchronous `build()` pull-reads that `WFL_PseudoCoup` expects. *(Note: Looking at `WFL_PseudoCoup/src/viewmodel/`, it appears you've already completed this for a large chunk of the 27 ViewModels).*
*   **Dependency Rewiring (The 124 Symbols):** Swapping out the transpiled raw Kotlin imports with the actual Python paths (e.g., pointing to `src.domain.autoregulation_service` instead of the Kotlin import).
*   **Building the UI Screens (The biggest chunk):** There are 87 Compose UI files in the Kotlin app, but currently only ~35 `.py` UI files in `WFL_PseudoCoup`. Hand-building those remaining ~52 "Tier 3" UI screens using the Python UI kit, and wiring them to their respective ViewModels, is the single largest remaining piece of the conversion effort.

## Conclusion
The "Domain Rebuild" panic from `log_44`/`log_45` is cancelled. The remaining work is simply pushing the transpiler to 0 TODOs, manually flattening its output into the app's synchronous paradigm, and hand-building the remaining 52 UI screens.
