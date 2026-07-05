# SemiBold ≤12sp band fix — ProgramEditorScreen MACROCYCLE (31/32 → 32/32)

## Cause
The MACROCYCLE header (12sp / labelMedium / SemiBold annotated string) rendered 3.5% too wide in
Kivy. The kit's `_SHAPER_CAL` applied a SemiBold factor of **1.042** to the ≤12sp band. That 1.042 is
a *24sp-derived* number (synthetic-emboldening advance at large sizes). The specimen shows the SemiBold
widening is **size-dependent** — at 12sp compose barely widens for SemiBold. Applying the 24sp factor
at 12sp is the overshoot.

## Specimen measurements (added 3 cases to both halves)
Kotlin `dumpSpecimen()` / Python `_specimen()` — identical lines, same order:
- `Text("MACROCYCLE 1 · Foundations", labelMedium, SemiBold)`
- `Text("MACROCYCLE 1 · Foundations", labelMedium)` (plain twin, isolates size factor)
- `Text("MACROCYCLE 1 · Foundations", labelSmall, SemiBold)` (11sp band edge)

| case | compose px | kivy px (w/ current cal) | current cal | raw kivy px | true ratio compose/raw |
|------|-----------:|-------------------------:|------------:|------------:|-----------------------:|
| labelMedium SemiBold 12sp | 180 | 187.27 | 1.035×1.042=1.0785 | 173.64 | **1.0366** |
| labelMedium plain 12sp    | 179 | 180.14 | 1.035              | 174.05 | 1.0285 |
| labelSmall SemiBold 11sp  | 168 | 173.69 | 1.035×1.042=1.0785 | 161.05 | 1.0431 |

Key reading: **compose SemiBold 180 vs plain 179 = 1.006** — the SemiBold delta at ≤12sp is ~0.6%,
not 4.2%. The size factor (plain, 1.028 measured) is left at the existing specimen-checked 1.035
(plain 12sp already passes; unchanged to avoid touching all plain small text).

## Band change (`kivy_kit.py`, `_SHAPER_CAL`)
Made the weight factor size-banded — SemiBold/bold now 1.006 for fs≤12, 1.042 otherwise:
```
_SHAPER_CAL = ((1.035 if fs <= 12 else 1.021 if fs >= 16 else 1.0)
               * (1.0 if _wt not in ("semibold", "bold")
                  else 1.006 if fs <= 12 else 1.042))
```
1.006 is derived directly from the specimen pair (180/179). Resulting specimen fit: all three cases
within ±0.3% of display; MACROCYCLE cases diff at 1.8% / 0.7% / 1.4% (all PASS).

## Verification (all gates hold)
- Specimen: **24/24 PASS** (grew from 21; new cases pass)
- SpecimenList: **5/5**
- ProgramEditorScreen: **32/32** (MACROCYCLE FAIL gone, no new FAILs)
- SettingsScreen 41/41 · LogCardioScreen 25/25 · WorkoutCooldownScreen 25/25 ·
  ExercisePickerScreen 26/26 · WorkoutWarmupScreen 32/32 · HistoryScreen 7/7 — no regressions.

No commit/push per instructions.
