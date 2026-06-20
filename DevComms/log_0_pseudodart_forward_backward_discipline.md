# log_0 — PseudoDart: forward/backward transpile under one discipline

Date: 2026-06-20
Type: brainstorming (raw idea, not a settled decision). Records a direction to
explore for the Dart/Flutter side of PseudoCoup, plus the naming settled for it.
Distinct from `PseudoCoup_handoff_report.md`, which holds only settled decisions.

## Naming settled for the Dart/Flutter side

Mirrors the existing language/kit split on the Haxe side, but with the `Pseudo`
prefix instead of `Py` (`PyDart` is already taken by an unrelated project, and
`Pseudo` sits under the PseudoCoup umbrella anyway):

	PseudoDart      the language transpiler. disciplined Python -> Dart source.
	                the direct analog of PyHaxe.
	PseudoFlutter   the UI kit on top of Dart. the direct analog of PyHaxeUI.

So the pairing is `PseudoDart : PseudoFlutter` exactly as `PyHaxe : PyHaxeUI`.
The transpiler's true target is the *language* (Dart), not the framework
(Flutter) — same point `PseudoCoup_handoff_report.md` section 5 makes ("you don't
transpile to Flutter, you compile Dart").

## The idea: one discipline, two directions

PyHaxe runs one way: disciplined Python --emit--> Haxe. The discipline exists so
that that emit is *mechanical* — "once your code follows the discipline,
translation is mechanical" (PyHaxe README). The brainstorm: for PseudoDart the
same discipline could carry traffic **both** ways.

	forward    disciplined Python  --emit-->   Dart
	backward   Dart                --lift-->   disciplined Python

`forward` is the normal transpile, the PseudoDart analog of `PyHaxe.haxe_emitter`.
`backward` reads Dart and produces disciplined Python — the pseudo-code source of
truth — from it.

### Why the discipline is what makes backward possible

The discipline is a subset of Python chosen so each construct has one clean
target form. If that map is not just one-directional but **one-to-one on the
subset** (each disciplined-Python construct emits to a distinct Dart form, and
that Dart form came from nothing else), then the same correspondence read in
reverse lifts that Dart back to disciplined Python. Backward mapping is not a new
translator invented from scratch; it is the forward correspondence run the other
way, restricted to the Dart that sits inside the forward map's image.

Anchor: `forward` lowers a Python `def classify(value: int) -> str` to a Dart
`String classify(int value)`. If that lowering is one-to-one, `backward` reading
`String classify(int value)` has exactly one disciplined-Python source it could
have come from. The discipline is what removes the guesswork in both directions.

### Why this is more plausible for Dart than it was for Haxe

`PseudoCoup_handoff_report.md` section 5 already records that Dart is the closer
sibling to Python (native `async`/`await`, null-safety, a closer closure model) —
"a Python -> Dart transpile is roughly the same difficulty class as Python ->
Haxe, slightly easier in spots." Two consequences for the round trip:

- The Dart-side discipline (the "disciplined Dart" that is the image of
  disciplined Python) can be **less strict** than PyHaxe's, because fewer Python
  constructs need to be banned or wrapped to reach a clean Dart form.
- A less-strict discipline that is still one-to-one is the more useful one: *more*
  real Dart falls inside the reversible subset, so `backward` can ingest more
  existing Dart without it having to be hand-cleaned first.

## What backward would actually be worth (brainstorm-level, uncosted)

- **Ingest existing Dart/Flutter into the source of truth.** Pull real Dart code
  up into disciplined Python so it joins the write-once notation, instead of being
  stranded in the target language.
- **Round-trip as a transpiler property test.** On the disciplined subset,
  Python --forward--> Dart --backward--> Python should land back on the original
  (up to formatting/comments). That identity is a strong, automatable correctness
  check on `forward` — the kind PyHaxe verifies today only by compiling and
  running output.
- **Two-way sync.** Keep a pseudo-code file and its Dart in step from either end —
  the literal "forwards or backwards" framing.

## Open questions (this is why it's a brainstorm, not a decision)

- **Is the map one-to-one, or only one-way?** `forward` may be many-to-one (two
  different disciplined-Python forms emit the same Dart). Wherever it is,
  `backward` has a genuine choice and the round trip is not an identity there.
  Mapping out where `forward` collapses distinctions is the first real task.
- **Backward needs a Dart parser, not Python's `ast`.** `forward` gets Python's
  stdlib `ast` for free; `backward` has to read Dart (the Dart `analyzer` package
  is the candidate). That is the asymmetric cost — the two directions do not share
  a front end, only the correspondence table.
- **What is "disciplined Dart"?** Backward only accepts Dart inside the forward
  map's image. That subset has to be named and checked, the mirror of what
  `discipline_checker.py` does for Python.
- **What is lost and is that acceptable?** Comments, formatting, and Dart idioms
  with no disciplined-Python form. PyHaxe already keeps comments via `tokenize`
  and re-injects them; the reverse has the same problem pointed the other way.

## Relation to immediate work

The immediate goal is `forward` only — stand up PseudoDart as a Python -> Dart
emitter mirroring PyHaxe, full Flutter SDK installed for compile/verify. `backward`
is parked here as a direction, not on the near-term path. Recording it now so the
`forward` design can leave the door open (e.g. keeping the emit correspondence
explicit and one-to-one where it cheaply can be) rather than foreclosing it.

**Update 2026-06-20 (owner call):** `backward` is explicitly **not** a design
driver. It is "would be super cool," not a constraint, and will not influence
near-term decisions. Revisit only after the bulk of `forward` is built, and only
if it turns out to be reasonably accessible by then. Do not pay any non-trivial
`forward` cost to keep the door open.
