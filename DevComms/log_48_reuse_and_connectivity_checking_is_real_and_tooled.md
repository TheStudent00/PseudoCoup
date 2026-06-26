# log_48 — the reuse + connectivity-checked workflow is real, already tooled, and ran live

Date: 2026-06-25
Type: assessment (grounded — ran the tools). Answers the user's question: can the already-built PC/UI
objects be swapped into the incomplete screens, with connectivity preserved and checked along the way
so nothing drops? Short answer: **substantially yes, and more true than log_47 implied.**

## Most of the target already exists (so this is fill-in, not build-from-scratch)

- **Domain layer:** done (37k LOC, log_46).
- **Screens:** PC has **30 of WFL's 31** top-level `*Screen`. Only a handful are wholly missing
  (history/settings variants, update_program_wizard, watch_workout, wins_list — modulo naming noise).
- **Reuse library already built:** `src/kit.py` (21 primitives) + `src/ui/widgets.py`
  (**73 reusable components**: card, set_editor, history_card, program_card, list_row, top_bar, fab,
  chip_row, switch_row, dropdown_field, stepper, …), all wired to the existing synchronous services.

**Correction to log_47:** "~52 missing screens" conflated screens with components. WFL's 87 UI files =
31 screens + 56 sheets/dialogs/cards/rows. PC has the 30 screens + fewer components. The real remaining
UI work = per-screen gap-filling in the 30 existing screens + a few whole screens + shared components.

## The connectivity check is real and runs today (ran it live)

`tools/dualgraph/align.py compare(slug)` walks each PC screen's `build()` tree and its WFL Kotlin
blueprint and reports, node by node:

```
gym_list_screen   matched=9   kt_only(gaps)=6    pc_only=7
today_screen      matched=5   kt_only(gaps)=11   pc_only=11
exercises_screen  matched=7   kt_only(gaps)=0    pc_only=1     <- fully covered, "0 gaps" exists
```

- **`kt_only`** = WFL nodes with no PC equivalent = the exact "dropped / not-yet-built" elements.
  gym_list's `kt_only` includes a real `button 'Delete gym' *click->?`.
- **`pc_only`** = PC nodes with no WFL source (PC additions / structural).

So "check connectivity along the way" is not hypothetical — it's a per-screen, node-level diff that
already exists (also: `connectivity/audit.py` for VM state+actions, `uimap/` for the visual map).

## The workflow your instinct describes, made concrete

For each screen, repeat:
1. transpiler -> VM skeleton; de-reactify (Flow->synchronous) and point imports at PC's real services;
2. compose the screen from `widgets.py` components + kit (reuse, don't rebuild);
3. wire handlers/nav to the VM;
4. run `dualgraph compare(slug)`; **drive `kt_only` -> 0**;
5. done when no blueprint node is unaccounted for.

Nothing silently drops because step 4 enumerates every gap. `exercises_screen` already demonstrates a
0-gap end state.

## Honest caveats (no over-promising)

- **"Swap in" = compose from existing *components*, not transplant a whole WFL Compose object.**
  Different framework (Compose vs the kit); reuse is at the widget level.
- **The check is structural, not behavioral.** It proves the same nodes/clickables/nav are present; it
  does NOT prove a handler does the right thing. Last-mile behavior stays developer judgment.
- **"Preserved" is a number you drive down, not a binary.** Some "done" screens still carry `kt_only`
  (gym_list 6, today 11); some of it is layout noise (spacers), not all real gaps.
- **Reuse is uneven:** list/detail screens reuse heavily; novel ones (wizards, watch_workout) need new
  components built once, then reused.
- There is also `WFL_PyHaxe` (an earlier, deprecated port) with ~30 screens — reference material, but
  a different paradigm; I would not bank on lifting from it.

## Net

Your instinct is correct and the pieces are already in place: a reuse library (kit + 73 widgets +
services + 30 screens) and a node-level connectivity gate (`dualgraph`) that makes "nothing gets
dropped" verifiable at each step. The remaining conversion is best run as a **gap-driven, dualgraph-
gated fill-in** of mostly-existing screens — not a from-scratch rebuild.

Pointers (verifiable): `WFL_PseudoCoup/src/ui/widgets.py` (73 components), `src/kit.py`,
`tools/dualgraph/align.py` (`compare(slug)` -> matched/kt_only/pc_only), `tools/connectivity/audit.py`,
`tools/uimap/`. Supersedes log_47's "52 screens" figure.
