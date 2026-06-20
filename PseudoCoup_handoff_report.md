# PseudoCoup — Handoff Report

*Living document. This is the orientation file for any new conversation about
PseudoCoup. A fresh Claude or Gemini session reads this first; it says what the
project is, what already exists, what was decided and why, what is open, and what
is next.*

*This doc points at authoritative artifacts rather than reproducing them. It does
not re-derive decisions that already live in the sub-project docs.*

*Created at the end of the conversation that named the umbrella (PseudoCoup) and
sorted out the OpenFL-vs-Flutter fork. Supersedes the old
`PyHaxeUI_handoff_report.md` as the TOP-LEVEL entry point — that doc is still
valid for PyHaxeUI specifically and is now one tier down.*

---

## 0. What PseudoCoup is (read this first)

PseudoCoup is the **umbrella project**. The name was chosen deliberately: it is a
*coup against un-intentful, un-portable design* — against the fact that writing an
application in any one platform's notation locks you to that platform's runtime,
idioms, and lifespan.

The thesis, stated flatly:

> Write an application **once**, in one good notation, as intentful pseudo-code.
> Render it to **any** platform, through **any** underlying target, and stay as
> future-safe as possible.

Three words carry the whole project, and they are kept distinct on purpose:

```
PseudoCoup    the umbrella / the banner. the movement against un-portable design.
              it owns nothing technical itself; it is the altitude above all targets.

pseudo-code   what you actually write. one notation, platform- and API-agnostic,
              intentful. today this is "disciplined Python" — Python's surface
              notation, constrained to a subset that maps cleanly onto many targets.

intent        the principle that runs through every tier. the code you write
              describes what the app WANTS (intent), never how a particular
              toolkit does it (mechanism). intent survives churn because it does
              not name the mechanism. this is the load-bearing idea, inherited
              verbatim from PyHaxeUI's "intent-not-mechanism rule."
```

The structure of the whole thing:

```
PseudoCoup                          the umbrella: write once, render anywhere.
  |
  +-- PyHaxe                        target: pseudo-code -> Haxe source
  |     |                           (Haxe then reaches Java/C++/JS/etc.)
  |     |
  |     +-- PyHaxeUI                the UI kit family over the Haxe target
  |           +-- (Kivy kit)        debug path. unified one-IDE debugging.
  |           +-- PyHaxeUI-Android  ship path. native Android Views. PROVEN.
  |           +-- PyHaxeUI-OpenFL   ship path candidate. DOES NOT EXIST YET.
  |           +-- PyHaxeUI-iOS      ship path. planned, not started.
  |
  +-- PyFlutter                     target: pseudo-code -> Dart/Flutter
                                    NEW, not started. the other side of the
                                    open fork (section 6).
```

The `Py-` names follow one pattern: `Py` + target = a **transpiler target**. The
umbrella cannot follow that pattern, because it is not tied to one target — that
is why it is "PseudoCoup," not "PySomething."

**A naming caveat recorded at decision time (not a blocker, eyes-open):** "coup"
carries a faint political-violence echo a search might surface, and it is slightly
harder to say aloud than to read. Accepted anyway — it declares a thesis where
alternatives (e.g. "Pseudo-Intent") merely describe one. "Intent" is kept as the
internal principle rather than the badge, because it does better work naming the
rule than naming the project.

---

## 1. Artifact map — what to read, in order

The project's authoritative state lives across several files and folders. Each has
a clear job.

**`PseudoCoup_handoff_report.md`** (this file) — the top-level orientation. What
the umbrella is, the current fork, the decisions log. Start here.

**`PyHaxeUI_development_plan.md`** (one tier down, under PyHaxeUI) — the
architecture and design rationale for the UI layer: one-source-two-paths, the
layered kit, the intent-not-mechanism rule, the Kivy + drawn-widget reasoning.
When a UI-architecture decision needs re-examining, this is the source of truth
for what was already decided and why. Read before proposing UI-architecture
changes.

**`PyHaxeUI_handoff_report.md`** (one tier down) — the PREVIOUS top-level handoff,
now demoted to PyHaxeUI-specific. **Its "Current state" section is STALE** — it
says the ship path is untouched and is the biggest open risk. That is no longer
true (see section 4 below). Read it for the Kivy-kit / debug-path history; ignore
its risk assessment.

**`PyHaxe/`** — the transpiler. `haxe_emitter.py` (AST-walk Python->Haxe text),
`discipline_checker.py` (the linter that defines the disciplined subset),
`discipline.py` (the `@haxe_extern` decorator), `cli.py`. Authoritative for what
"pseudo-code" currently means in practice and how it becomes Haxe. Plus
`docs/DEVELOPMENT_NOTES.md` for transpiler workarounds and gotchas.

**`PyHaxeUI/`** — the UI kit family. Contains the Kivy debug-path kit (`kit.py`),
the development plan, the discipline skill (`PYHAXE_DISCIPLINE.md`), and the
SharedTasks Android app being ported as a translation target. Its `DevComms/log_0`
records the **three-tier kit model** (section 3 below) — required reading before
any kit work.

**`PyHaxeUI-Android/`** — the **proven native Android ship path**. This is the
most important recent artifact and the one the old handoff doesn't know about.
A hand-written Haxe + native-Java kit implementing the kit interface; a transpiled
app renders and is touch-drivable on an emulator. Read `README.md`, then
`docs/M2a_findings.md` -> `M2b_findings.md` -> `M2b2_findings.md` for the proof
trail. Its `DevComms/log_0..log_2` record the three-tier model, the
de-entanglement rule, and theme-as-data.

---

## 2. The two models PseudoCoup can render onto — imperative vs. reactive

This came up directly in conversation and resolved cleanly, so it is recorded as
settled.

```
reactivity
    a UI model where you describe what the screen should show for the current
    data, and the framework figures out what changed and updates the screen.
    you never tell a specific part of the screen to change.
    example tied to context:
        a screen shows "Count: 3" and a button.

        the PyHaxeUI kit (you update the screen):
            the number is a variable. on tap, your handler adds 1, then YOU call
            present("count_zone", "Count: 4"). you named the zone, supplied the
            text, did the update. this is IMPERATIVE.

        a reactive target (the framework updates the screen):
            you write one description: "show 'Count: ' + count". on tap you change
            count 3 -> 4 and stop. the framework re-reads the description and
            changes the text for you. you never named a zone.
```

**The resolution (this is the settled part).** The imperative-vs-reactive
difference is a **transpiler detail, not an architectural wall.** If the target is
reactive, the transpiler emits an empty `present` (or routes the `present` call
into a state-set) and the reactive framework does the screen update. The owner
collapsed this in one line and it holds.

**The consequence, which corrected an earlier wrong framing.** Reactivity is *one
more mechanism the kit hides*, which is exactly the intent-not-mechanism rule
working as designed. So a reactive target (Flutter) is **not** a reason for caution
about PseudoCoup expanding — it is, if anything, a *stronger* case for the umbrella,
because hiding reactivity behind the kit's intent surface is the same move the kit
already makes for every other mechanism. An earlier turn framed reactivity as a
deep mismatch; that was backwards and is retracted here.

---

## 3. The three-tier kit model (vocabulary every kit shares)

From `PyHaxeUI/DevComms/log_0`. This is the boundary structure every platform kit
(Android, OpenFL, Flutter, iOS) implements. It is not Android-specific.

```
primitives          define_text / define_box / define_button / define_marker / ...
                    the FLOOR. every platform kit implements these. intent-over-
                    mechanism at a fine grain: "a styled text leaf," not "an
                    Android TextView." churn-resilience comes from the indirection
                    app -> kit -> platform.

generic components  header, nav, list_row, fab, card, empty_state, switch, chip,
                    stepper, ... (~19-28 app-AGNOSTIC intents). rendered
                    IDIOMATICALLY per platform: a nav_item becomes a native iOS
                    tab-bar item, a Material nav item on Android, a styled box on
                    desktop. the app never specifies how. this tier is where
                    intent-over-mechanism pays its biggest dividend.

app widgets         gym_card, rail_row, task_row, ... the app's OWN domain.
                    NO kit ever knows these. they are transpiled-pseudo-code
                    COMPOSE FUNCTIONS over primitives, living in the app.
```

**The boundary insight (the error to avoid):** do not collapse the two top tiers
in either direction.
- Pushing **app widgets up into components** -> N bespoke renderers per platform.
  This is the exact cost that would make a new platform kit a huge per-widget
  reimplementation.
- Pushing **generic intents down into app-side primitive composition** -> pins
  their structure ("a header is bold text in a box") into portable code and throws
  away the kit's freedom to render them idiomatically per platform.

So: **app widgets compose from primitives; generic intents stay kit-rendered
components; primitives are the shared floor both the kit and apps build from.**

**Theme-as-data (from `PyHaxeUI-Android/DevComms/log_2`).** The kit ships NO design
values. An app installs a serialized token table at startup via `set_theme()`; the
kit resolves every colour/size/spacing from those tokens. The kit is app-agnostic
by construction — no brand palette, no consumer name anywhere in kit code. This is
how "uniform modern look, authored as data" is achieved without the kit knowing
any specific app. It is also the answer to the earlier "how do we not look like
Win95" question: the modern look is a token table, authored once, not a
per-component reverse-engineering job.

---

## 4. Current state — what is actually proven (CORRECTS the old handoff)

*This section is the authoritative answer to "where are we right now?" The old
`PyHaxeUI_handoff_report.md` says the ship path is untouched and is the single
biggest open risk. THAT IS OUT OF DATE. Use this section instead.*

### What is proved

**The transpiler (PyHaxe).** Working through multiple milestones: functions,
classes, inheritance, collections, kwargs resolution, exceptions, type system.
The disciplined-Python subset is enforced by `discipline_checker.py`.

**Unified debugging (PyHaxeUI debug path).** Verified in PyCharm Community.
Breakpoints in both a UI event handler and a back-end pure function hit in one
debug session under a Kivy app. The one-IDE-breakpoints-anywhere goal is met.

**The native Android ship path (PyHaxeUI-Android) — THE BIG ONE.** This retires
what the old doc called the single biggest open risk. Proven, with on-emulator
evidence (logcat + screenshots in `PyHaxeUI-Android/docs/evidence/`):

- pseudo-code -> PyHaxe -> Haxe -> **hxjava (Java)** -> **native Android Views** ->
  APK. A real transpiled app lands as `haxe.root.*` Java classes, dexed into a
  normal APK.
- The app's logic `start()` ran inside a real Activity (M2a).
- A native-Java kit (decision A: `@:native` externs binding the transpiled app to
  hand-written Java) renders a canvas with draggable colored zones, and **drag
  works live** with the Kivy->Android y-flip handled in the kit (M2b).
- The full three-column editor chrome renders with real Android widgets and is
  **drivable by tapping** — spawn, select, zoom-label-update, drag — no injected
  Java calls (M2b2).

**The critical fact this establishes for the fork below:** the Android ship path
did **NOT** go through OpenFL. It went through **hxjava -> native Android Views**.
OpenFL was the *original development plan's* intended drawn-widget renderer, but it
was never used for Android. This matters enormously for section 6.

### What is NOT proved

**Any iOS ship path.** Not started by any route. This is now the central open
problem and the thing that triggered this whole conversation. "Haxe doesn't target
Swift" is what surfaced it.

**PyHaxeUI-OpenFL.** Does not exist as a folder, a kit, or a proof. No OpenFL kit,
no OpenFL mapping, no OpenFL ship. "Continuing OpenFL" is a misnomer — it would be
*starting* OpenFL.

**PyFlutter.** Does not exist. Conceptual only, as of this conversation.

**Two-paths-agree (debug vs ship look/behave the same).** Still cannot be fully
tested until a second ship path on a second platform exists.

### IDE / toolchain state

- **PyCharm Community** — daily-dev IDE for the Python/debug side.
- **Android Studio** — reserved for Android packaging/emulator work.
- **Antigravity IDE (with Gemini as coding agent)** — the environment this handoff
  is being loaded into for PseudoCoup work going forward.
- Android ship-path versions all verified building: AGP 8.7.3, Gradle 8.9,
  compile/targetSdk 36, minSdk 26, JDK 21, no AndroidX/appcompat (dropping it
  fixed a Kotlin-stdlib duplicate-class clash). Details in
  `PyHaxeUI-Android/docs/M2a_findings.md`.

---

## 5. How the candidate targets actually reach platforms (settled facts)

Recorded because the "are Haxe and Dart siblings?" question produced a precise and
useful answer worth keeping.

```
Haxe ship model (SOURCE TRANSLATOR):
    Haxe source --transpiles to--> the target platform's OWN language
    (Java for Android, C++ for native, JS for web), then THAT language's
    normal toolchain compiles it.
    => proven for you: the editor lands as hxjava Java, dexed into an APK,
       using native Android Views.

Flutter ship model (SELF-CONTAINED RUNTIME + RENDERER):
    Dart source --compiles AOT to--> native machine code, shipped ALONGSIDE
    its OWN engine (Impeller/Skia renderer + Dart runtime) that draws every
    pixel itself. Flutter does NOT emit into the platform's language and does
    NOT use the platform's native widgets — it paints its own.
    => one Dart codebase, AOT-compiled per platform, Android and iOS both
       first-class and equally proven.
```

**Haxe and Dart are siblings as languages** (both statically typed, OO, generics,
similar control flow — a Python->Dart transpile is roughly the same difficulty
class as Python->Haxe, slightly easier in spots because Dart has native
async/await, null-safety, and a closer closure model). **But they are opposites in
how they reach a platform:** Haxe hands off to the target's compiler; Flutter
bundles its own engine. You do not "transpile to Flutter" — you compile Dart and
ship the engine with it.

**Flutter's development loop (the part that genuinely beats the current setup).**
In development Dart runs JIT with **hot reload** — save a file, the running app
updates in under a second keeping its state, with a real breakpoint/step debugger.
For release it switches to **AOT native machine code**, no interpreter on device.

**The uncomfortable implication, recorded honestly.** PyHaxe's founding motivation
was "author in fast-to-develop Python, ship fast-to-run compiled, because one
language can't be both." Flutter's Dart spans *both* modes itself (JIT+hot-reload
to develop, AOT-native to ship). So for a PyFlutter, Python-the-notation is the
main thing the transpiler still buys you — the develop-fast/ship-fast runtime split
that justifies PyHaxe is a problem Flutter does not have. This is NOT a verdict
against PyFlutter; it is the precise statement of what PyFlutter is and isn't worth.
The owner's position (recorded): notation matters in its own right — being stuck
writing every language in curly-brace notation is itself the un-intentful design
PseudoCoup is a coup against. Under that position, "Python notation over a stack
that already solves the runtime split" is a feature, not a redundancy. And in a
PyFlutter you never write Dart's braces anyway — they are emitted output you don't
read, the same way Haxe's braces are emitted now.

---

## 6. THE OPEN FORK — how to reach both platforms with one drawn-widget source

This is the live decision. State it correctly: it is **PyHaxeUI-OpenFL mapping vs.
PyFlutter mapping.** Both are genuine like-for-like — both "draw your own widgets,
ship to Android AND iOS, one source." (An earlier turn raised a *third* option —
a native-UIKit iOS kit mirroring the native-Java Android kit — but that is the
native-widget-per-platform path, not the drawn-widget fork, and is set aside here.)

```
PyHaxeUI-OpenFL                         PyFlutter
  draws its own widgets via OpenFL,       draws its own widgets via Flutter's
  runs on Android AND iOS.                engine, runs on Android AND iOS.

  PRO: PyHaxe already emits Haxe;         PRO: two-platform shipping is Flutter's
       OpenFL is Haxe; the transpile           proven, mature core competence —
       half is mostly DONE.                     NOT your risk to carry. better
                                                dev loop (hot reload).
  CON: OpenFL actually reaching iOS,      CON: a whole new transpile target
       drawn-and-working, is UNPROVEN          (Python -> Dart) to build; PyHaxe
       for you. it is the same open            does not feed it. a new
       iOS risk, just relocated.               reactive-shaped kit to design.
```

Each option's PRO is the other's CON. One has the transpile done and the shipping
unproven; the other has the shipping proven and the transpile unbuilt.

**Important nuance on OpenFL:** there is currently **almost no OpenFL
infrastructure** in the project. The Android win was native Android Views, not
OpenFL. So PyHaxeUI-OpenFL is roughly greenfield for the two-platform drawn-widget
goal — its only head start is that it is Haxe, so PyHaxe already produces its input
language.

**Nothing about this fork requires discarding PyHaxe or the existing Android work.**
PyHaxe stays as a target under PseudoCoup regardless. The native Android Views path
remains valid and proven. The fork is only about which *new* drawn-widget,
two-platform path to invest in.

### The one thing genuinely unresolved

Whether **(Python->Dart transpile + a reactive-shaped kit)** is more or less total
work than **(standing up OpenFL as a working, iOS-reaching, drawn-widget ship
path)**. This was explicitly left open — it is a real comparison neither side of
which has been costed yet. It is the recommended next investigation (section 7).

---

## 7. Next move — recommended

**Cost the open fork on real footing, not in the abstract.** Two sub-investigations,
either order:

1. **OpenFL's actual iOS reach.** Can OpenFL stand up as a working drawn-widget
   ship path that reaches iOS, fed by PyHaxe? What is the smallest proof — one
   trivial drawn component on an iOS target/simulator? This answers OpenFL's one
   open risk.
2. **PyFlutter's actual transpile cost.** How much of the existing PyHaxe
   AST-walking spine + discipline checker carries over to a Python->Dart emitter
   (the language transpile), and what does a reactive-shaped kit surface look like
   when the same three-tier model (primitives / generic components / app widgets)
   is mapped onto Flutter widgets?

The deciding question underneath both, which is an owner call (architecture /
ontology), not a Claude/Gemini call:

> Is the value of PseudoCoup the **disciplined-pseudo-code source of truth**
> (notation + portability + future-safety), or was it specifically solving
> Python's develop-fast/ship-slow **runtime split**?
>
> If notation/portability: Flutter is a legitimately strong host and PyFlutter is
> worth prototyping — the braces are emitted output you never read, and reactivity
> is just one more mechanism the kit hides.
> If the runtime split: Flutter dissolves that problem, and OpenFL-under-Haxe keeps
> the project on one coherent transpile spine.

The owner leaned, in conversation, toward notation/portability being the real prize
(the "we're still stuck with curly braces for everything" point). That leaning, if
it holds, tilts toward PyFlutter being worth a real prototype — but the cost
comparison in (1) and (2) should inform it before committing.

---

## 8. Working roles — Claude vs. Gemini (carried over, unchanged)

- **Claude — lead-dev / architect.** Architecture decisions, design reviews,
  ontology and naming calls, intent-not-mechanism analysis, milestone framing,
  surfacing tensions and tradeoffs. Higher decision-density, lower token count.
  Independently verifies Gemini's outputs before the next spec.
- **Gemini — bounded implementation.** Translating an agreed design into code,
  expanding a kit's surface, writing fixtures, iterating against a fixed spec.
  Clear inputs and outputs.

The split is per-task: bring it to Claude when "what should this be?" is the
question; bring it to Gemini when "implement this thing we already agreed on" is
the question. When Gemini takes a task, give it this handoff doc, the specific
files, and the task spec.

---

## 9. Discipline reminders (for any code-generating role)

Applies to all PseudoCoup pseudo-code (app code) and to any kit's public surface.
A kit's GLUE internals (the per-platform wrapping) are looser. When in doubt, run
`discipline_checker.py`; clean output is the bar.

- Type annotations on every parameter and return value.
- Class-level field declarations with type annotations.
- Single inheritance only.
- Named functions, never lambdas.
- No `*args` / `**kwargs` in signatures (kwargs at call sites are fine; the
  transpiler resolves them positionally).
- No tuple unpacking on assignment.
- No `with` statements.
- No generators / `yield`.
- No bare `raise`; use `raise e` with an explicit exception.
- Wrapper required for non-portable libraries (via `@haxe_extern` today; the
  pattern generalizes per target).

**The discipline is pragmatic, not dogmatic.** Standing owner principle: if a
target requires *less* discipline (e.g. a reactive target where explicit `present`
calls become empty), do not force the stricter rule in. The discipline exists to
make pseudo-code mechanically translatable across targets — it bends to that goal,
it is not an end in itself.

---

## 10. Conversation log — what each conversation produced

**(Pre-PseudoCoup, May–June 2026.)** Established PyHaxe (the transpiler) and
PyHaxeUI (the UI layer): one-source-two-paths, the Kivy + drawn-widget pairing, the
layered/three-tier kit, intent-not-mechanism, theme-as-data, M1 unified debugging
proved, and — most significantly — the **native Android Views ship path proved
end-to-end** (M2a/M2b/M2b2). Recorded across `PyHaxeUI_development_plan.md`,
`PyHaxeUI_handoff_report.md`, and the `DevComms` logs.

**This conversation (June 2026) — named the umbrella, sorted the fork.** Outcomes:
- Established that "trace Material components into OpenFL-drawn components" (visual
  + functional) is the wrong problem: appearance isn't in the source, there's no
  programmatic "close enough" checker, so it is manual reconstruction, not an
  automated loop. The real goal — uniform modern look on both platforms — is a
  **theme-as-data** job, not a tracing job.
- Established Feathers UI vs. HaxeUI stability (Feathers = most stable single
  library; HaxeUI = broader/multi-backend, the project's existing fit).
- Clarified Haxe-as-source-translator vs. Flutter-as-bundled-engine, and Flutter's
  JIT-hot-reload-develop / AOT-native-ship loop.
- **Corrected** the reactivity framing: imperative-vs-reactive is a transpiler
  detail (empty `present` on reactive targets), and reactivity is one more
  mechanism the kit hides — strengthening, not weakening, the case for expanding.
- **Corrected** the fork framing to its true form: **PyHaxeUI-OpenFL mapping vs.
  PyFlutter mapping**, both greenfield-ish for the two-platform drawn-widget goal,
  with the OpenFL/iOS reach and the PyFlutter transpile cost both still uncosted.
- **Named the umbrella: PseudoCoup** — a coup against un-intentful, un-portable
  design — keeping the `Py-` names as targets underneath and "intent" as the
  internal principle. This doc created at the end.
