# log_129 — exercise_detail breadth: nav map added; the SharedFlow-nav gap mapped

Date: 2026-06-28
Type: increment + finding. Advances breadth a bounded step; records the remaining open mechanism so a
steered session can finish it.

## What's done

`NAV_HANDLERS["exercise_detail"]` added (`onNavigateBack` → `_nav_back` → `navigate('exercises')`;
`onNavigateToEdit` → `_nav_edit`). The generated exercise_detail screen now resolves its back handler
(was a bare `onNavigateBack()`). Render unchanged (8 shared); gym_list unregressed (10/10).

## What's captured vs the gap (for a full drop-in)

The IR captures the DIRECT onClicks: back button (`onNavigateBack`) and the dialog/menu VM actions
(`onToggleExcluded`, `confirmSwapNow`, `confirmSwapLater`). It does NOT capture `onNavigateToEdit` —
because exercise_detail's edit-nav is INDIRECT: the VM emits to a `navigateToEdit` SharedFlow, a
`LaunchedEffect` COLLECTS it and calls `onNavigateToEdit(id)`. The generator models direct onClicks,
not the VM-SharedFlow → LaunchedEffect → callback indirection. That's the one new MECHANISM
exercise_detail needs (gym_list was all-direct).

## Roadmap to a full exercise_detail drop-in

1. **Model VM-SharedFlow nav:** when a VM action emits to a `navigate*` SharedFlow, wire it to the
   screen's nav callback (the LaunchedEffect-collect pattern) — a generator-mechanism addition.
2. **Dialog interaction:** `onToggleExcluded` sets `excludePrompt` (MutableStateFlow→State, DONE
   log_123) → dialog renders. Needs the exercise_detail adapter to support `onToggleExcluded`'s repo
   calls (`programRepository.countExerciseOccurrences`, `repository.bestSubstitute`) — adapter extension.
3. **Vendor + route** (like gym_list, logs 117/118) and **swap-under** the transpiled ExerciseRepository.

## Why I stopped here (autonomous)

The SharedFlow-nav mechanism (1) is an open DESIGN choice in the generator (how to model the
collect-and-call indirection) — better decided with the user than guessed autonomously. The back-nav +
dialog-action capture is landed and verified; the rest is documented for a steered session.
