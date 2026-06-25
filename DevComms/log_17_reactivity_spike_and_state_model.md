# log_17 — the reactivity spike: PseudoCoup gets Compose-style auto-observation

Date: 2026-06-25
Type: decision + done. Records the `State`/recompose primitive (spiked, verified, both backends)
and the decision to fold it into the ViewModel rollout so the ports — and the eventual
Kotlin→Python transpiler — ride on it.

## Bottom line

1. **PseudoCoup already had reactivity — the React kind** (`UI = f(state)`, rebuilt on a manual
   `router.remount_current()` call, ≈ `setState`). What it lacked was Compose's **auto-observation**:
   read-subscribe / write-auto-repaint. A handler could *forget* to repaint; Compose can't.
2. **The spike adds auto-observation** via one small primitive (`src/reactive.py`, ~70 lines) + a
   3-line hook in each kit. A ViewModel holds its fields as `State`; a write schedules exactly one
   repaint after the current event. Screens stop calling `remount_current` themselves.
3. **Why it matters for the port:** it makes `MutableStateFlow → State` ~1:1, which turns the
   reactive→pull reshape (the judgment-heavy part of a Kotlin→Python transpiler, per log_16) into a
   near-mechanical mapping. The reactivity upgrade is the prerequisite that makes the transpiler
   tractable — and a write-once framework needs that migration on-ramp to be adoptable.
4. **Decision (made): fold it into the rollout.** Every ported VM uses `State`; every wired screen
   drops its manual remount. `report_bug` is re-ported this way and verified end-to-end.

## The spectrum (where PC was, where it is now)

```
model                      trigger on state change        examples              PC
imperative (old Views)     mutate widgets by hand         findViewById().text=  no
explicit re-render         call a repaint fn              React setState        was here
auto-observation           read=subscribe, write=repaint  Compose, SwiftUI      now here (opt-in)
```

## The primitive (`src/reactive.py`)

```python
recompose = _Recompose()          # one per app; the router wires its host = remount_current

class State:                      # the MutableStateFlow analog
    def __init__(self, value): self.value = value
    def set(self, value):
        if self.value != value:
            self.value = value
            recompose.invalidate()         # marks the frame dirty
```

The kit drives it at the single event choke point — `begin()` before the handler, `flush()` after:

```
kit._deliver_event:  recompose.begin();  handler(evt);  recompose.flush()
```

So N writes in one handler → **one** repaint, *after* the handler returns (never mid-handler) —
exactly Compose's per-event recompose. A screen that still calls `remount_current` never marks the
frame dirty, so `flush()` is a no-op for it → **the two models coexist; migration is incremental.**

The Compose mapping that makes the transpiler mechanical:

```
Kotlin (Compose)            PseudoCoup
MutableStateFlow(x)    →     State(x)
flow.value            →      state.value          (read)
_flow.value = x       →      state.set(x)         (write — auto-notifies)
```

## How it changes PC style — `report_bug`, before → after

```
                        before (React-style)               after (Compose-style)
state field             self.severity: int = 1             self.severity = State(1)
vm action               self.severity = v                  self.severity.set(v)
screen read             self.vm.severity                   self.vm.severity.value
screen handler          mutate; r.remount_current()        mutate; (framework repaints)
result rendering        handler push: u.present(...)       build() renders FROM vm.submission
```

Three shifts: (1) state fields are observable `State`; (2) handlers no longer know about the router —
forgetting to repaint becomes impossible; (3) rendering moves imperative→state-driven, making the
screen a **pure function of state** (the Compose model, and what makes the transpile 1:1).

## Verified (both backends)

```
Python smoke         30/30 build (29 manual-remount + 1 reactive coexisting)
recompose bus        2 writes/handler → 1 repaint · unchanged write → 0 · empty frame → 0
report_bug VM        prefill 'Tester' post-seed · severity=1 · submit→'success' · empty desc gated
transpile → Dart     reactive.dart clean · 144 modules (was 143)
flutter analyze      0 errors · warnings identical to baseline (0 net-new)
```

## Honest boundaries

- **`.value`/`.set()` ceremony** — more verbose than a plain field; the price of staying transpilable
  (Dart has no property interception we can lean on, and the kit isn't `@property`-friendly).
- **Coarse remount caps text reactivity** — PC repaints the whole screen, so a text field can't drive
  state per keystroke (it'd thrash). Live text still reads via `get_value` at submit (same as today,
  not a regression). Fine-grained per-zone reactivity would be a much larger change; whole-screen
  remount is fine for the form-submit / toggle / select flows that dominate WFL.
- **Incremental** — reactive and manual screens coexist; we migrate VM-by-VM, not big-bang.

## The rollout, now riding on `State`

Each remaining screen, simple→complex (harvesting the construct→rule mapping as we go, so we learn
whether a transpiler is buildable — see log_16):

1. Mirror the Kotlin VM → `src/viewmodel/<screen>_view_model.py`, fields as `State`.
2. Wire the screen: read `.value`, call vm actions, **drop manual remount**, call `vm.load()` in `build()`.
3. Verify: smoke 30/30 · transpile clean · analyze 0 errors.

Plus the single app-scoped `AppViewModel` (notifications/`unreadCount`, crash prompt, celebration,
onboarding gate) — backs the notification badge PC is missing.

## Pointers

- primitive: `WFL_PseudoCoup/src/reactive.py`; kit hooks: `src/kit.py` `_deliver_event`,
  `app_flutter/lib/kit.dart` `_deliver`; host wired in `src/ui/app_router.py.__init__`
- exemplar VM + screen: `src/viewmodel/report_bug_view_model.py`, `src/ui/report_bug_screen.py`
- the transpiler-economics analysis this rides on: log_16
