# log_96 — where everything is at, and a glossary so the vocabulary stops getting in the way

Date: 2026-06-27
Type: status briefing + glossary. Written to the communication protocol
(`DevComms/LLM_communication_protocol.md`): glossary entries in the §4 format, your words
kept, every abstract term anchored to a real file or result.

Your ask: "everything except UI stuff completely transpiled and WFL meeting the transpiler in
the middle." Your concern: "large structures will be imported that break connectivity and/or
are invalid objects to swap in." You don't want to get into Track A yet. This log says where
things stand against that.

---

## 1. Glossary (read this first — it's most of the confusion)

```
WFL
    the original Workout-For-Life app, in Kotlin. The source of truth: every Python
    file must trace back to a Kotlin original.
    example: WFL_MixingCenter/WFL/app/.../engine/AutoregulationEngine.kt

PseudoCoup
    THIS repo. Holds the transpiler and the logs. It is NOT the app.
    example: tools/pseudokotlin/ (the transpiler) and DevComms/ (these logs).

WFL_MixingCenter
    a SEPARATE repo. Holds WFL's Kotlin AND the Python copy of it (254 .py for 254 .kt).
    The transpiler reads the Kotlin from here; the Python lands here; meet-in-the-middle
    edits to the Kotlin happen here.
    example: SampleProgramData.kt + its transpiled SampleProgramData.py both live here.

pseudokotlin
    the transpiler engine in this repo. Reads Kotlin, writes Python.
    example: tools/pseudokotlin/transpiler.py + nodes/*.py.

compile-clean
    a WEAK status: the transpiled Python is valid Python syntax — it loads. Says NOTHING
    about whether the logic is right.
    example: 192 of 254 files are compile-clean today.

verified  (= "proven-equivalent", = your "working logic")
    a STRONG status: the transpiled Python actually RUNS and produces the same answers as
    the Kotlin.
    example: 11 classes are verified; the other ~180 compile-clean files are NOT.

oracle
    the checker that earns "verified". It runs a class's existing Kotlin JUnit tests
    against the TRANSPILED Python, and (with --jvm) on the real Kotlin too, and compares.
    example: tools/pseudokotlin/oracle.py -> "ALL GREEN (11/11 engines)".

differential fuzzing
    a stronger checker: thousands of RANDOM inputs through both the Python and the Kotlin,
    every result compared.
    example: tools/pseudokotlin/fuzz.py -> 5000 random cases, 0 divergences.

meet-in-the-middle   (your phrase: "WFL meeting the transpiler in the middle")
    editing the WFL Kotlin so it transpiles cleanly WITHOUT changing what it does. Used
    only where the Kotlin leans on type information the transpiler can't see.
    example: SampleProgramData.kt -- `groups += listOf(a,b)` rewritten to `groups.add(...)`;
    identical Kotlin behaviour, confirmed by its own JUnit suite on the JVM.

swap-in   (your phrase: "invalid objects to swap in")
    wiring a piece of transpiled Python into the assembled app. An "invalid" swap-in is a
    file that loads but behaves wrong, or doesn't load at all.
    example: a compile-clean-but-unverified repository swapped in could return wrong data
    and nothing today would catch it.

connectivity   (your phrase: "break connectivity")
    how objects reference and wire into each other (screen -> viewmodel -> engine). Breaking
    it = a swapped-in object whose references no longer line up.
    example: if a transpiled data class drops a field the rest of the code reads, every
    caller of that field breaks.

Track A
    the EARLIER, hand-built UI: ~30 screens written by hand on the kit in WFL_PseudoCoup
    (the "65/65 goldens"). NOT Kt->Py transpilation. You don't want to get into it yet.

Track B
    the CURRENT work: the transpiler-driven Kt->Py center (WFL_MixingCenter) with the oracle
    + fuzz proof. Everything this session is Track B.

kit  (PseudoFlutter kit)
    the hand-written renderer that draws the screens. It belongs to Track A. Out of scope now.

PseudoUI
    the NOT-yet-built mechanized wiring that would connect transpiled UI screens to the kit.
    This is "bucket 3". Out of scope until non-UI is done.
```

---

## 2. Where everything physically lives (3 repos)

| repo | holds | role |
|---|---|---|
| `WFL` | the Kotlin app (254 files) | source of truth, read-only |
| `WFL_MixingCenter` | the Kotlin + its Python copy (254 + 254) | where transpilation lands; meet-in-the-middle edits go here |
| `PseudoCoup` (here) | transpiler + oracle + fuzz + logs | the tooling, no app |

---

## 3. Where everything is AT (two qualities, by layer)

Two separate questions per file: does it **compile-clean** (loads), and is it **verified**
(runs correct). They are not the same, and the gap between them is your concern.

| layer | compile-clean | verified | what it is |
|---|---|---|---|
| engine | 9 / 9 | yes (10 classes) | the domain math — the proven core |
| data | 132 / 135 | 1 class (SampleProgramData) | entities, models, repositories, Room database |
| core | 14 / 15 | none | utilities |
| di / navigation / root | 7 / 8 | none | wiring glue |
| **non-UI subtotal** | **162 / 167** | **11 classes** | **everything you care about right now** |
| ui | 30 / 87 | none | Compose screens — Track-A / bucket-3, out of scope |
| **TOTAL** | **192 / 254** | **11 classes** | |

Read the non-UI row: **162 of 167 non-UI files compile-clean (97%)**, but only **11 classes
are verified**. The gap — ~150 files that load but were never run against the Kotlin — is
exactly the "invalid objects to swap in" risk.

---

## 4. Your concern, mapped to the numbers

> "large structures will be imported that break connectivity and/or are invalid objects to
> swap in."

That risk lives entirely in the **compile-clean-but-unverified** set (the ~150 files in the
non-UI subtotal that aren't among the 11 verified). compile-clean guarantees the Python
*loads* — it does not guarantee the fields, methods, and wiring match the Kotlin. A large
transpiled structure (say a repository or a deep data builder) can load fine and still return
wrong values or drop a field a caller needs — and today nothing runs it, so the break only
shows up after swap-in.

The 11 verified classes are NOT at this risk: they were run and matched. SampleProgramData is
the proof that even a 320-line "large structure" can be driven to verified.

---

## 5. The goal, made concrete

> "everything except UI stuff completely transpiled and WFL meeting the transpiler in the middle."

That breaks into two concrete pieces:

**Piece 1 — close the last 5 non-UI files that aren't compile-clean** (meet-in-the-middle
where needed):

```
core/CrashlyticsBridge.kt        Firebase crash-reporting API wrapper
data/AutoregulationRepository.kt  Room repository
data/BackupRepository.kt          Room backup repository
data/WorkoutDatabase.kt           Room database definition
navigation/AppNavigation.kt       Compose-Navigation graph (UI-adjacent, lives in navigation/)
```

That takes non-UI from 162/167 to 167/167 compile-clean.

**Piece 2 — verify the unverified middle**, so a swap-in can't be silently wrong. The tools
exist (oracle, fuzz); the work is pointing them at the data/model layer. Three of the five
files above are Room (database) — those need a database swap-in/shim to run, which is the
larger part of this piece.

**One decision for you (it's an architecture/scope call, so it's yours):** does "completely
transpiled" mean *compile-clean* (Piece 1 only) or *verified* (Piece 1 + Piece 2)? Your
swap-in concern points at the second. I did not assume — say which bar and that sets the work.

---

## Net
Non-UI is 97% compile-clean and its core is proven, but most of it is loads-but-unrun. Your
"break connectivity / invalid swap-in" worry is precisely that unrun middle. Closing it is 5
files to compile-clean plus verifying the data/model layer — the UI (bucket 3 / Track A /
PseudoUI / kit) stays out until then.
