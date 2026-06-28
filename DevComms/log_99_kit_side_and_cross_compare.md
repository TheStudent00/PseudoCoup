# log_99 — kit/Python side of the UI ledger + the cross-side compare

Date: 2026-06-28
Type: new tool (tools/pseudokotlin/kit_ledger.py) + ui_ledger.collect_ids. The second side of
the UI ledger and the first Compose<->kit comparison.

## What it does

ui_ledger read the KOTLIN side (Compose) statically. kit_ledger reads the **kit side by runtime
tracing**: the kit builds screens imperatively as `ui.define_*(zone_id, sup_zone_id, …)` calls
(every node carries an explicit id + parent id), so a recording mock `UI`, run through the
screen's `build()`, captures the true tree — including nodes emitted by `ui.widgets` helpers.
This is the kit analog of the engine ledger's exec-and-introspect.

Headless: a stub `kit` module avoids Kivy/display (verified it imports clean); a permissive mock
stands in for the db/VM/router. Normalizes into the SAME schema (type · size abs/rel · content
anchor · path-id) and compares **node-for-node, joining on the content anchor** — the visible
string, the one key reliable across two structurally different trees.

## It works, and it localizes divergence honestly

Traced 6 screens (4–40 nodes each, no crashes). Sample — report_bug:
```
matched (by content anchor): 4   "How bad is it?" · "Send report" · 2 body strings
Compose-only: 3                  title · body · primaryLabel
kit-only: 7                      Report a bug · Annoying · Blocking · Minor · ← · …
```

The compare runs and pins exactly where the two sides differ. The low match count is **two known,
explainable asymmetries**, not tool error:

1. **Mock-empty VM** — dynamic list content (per-gym cards, per-exercise rows) is empty on the
   traced side, so its text is absent. Only the static skeleton is compared. (Fix: trace with
   real seed data.)
2. **Opaque Compose composables + Compose variables** — the kit, traced at runtime, expands
   helpers to literals ("Report a bug", "Annoying"). The Compose side treats a custom composable
   (a `TopBar`, a segmented row) as ONE component node and does NOT descend into its definition,
   and where Compose passes a variable (`title`, `body`) the anchor is the variable name, not the
   string. So the kit's literals read as kit-only and Compose's variables read as Compose-only.
   (Fix: inline custom composables on the Compose side + resolve param values.)

Both are real, both are fixable, and the path is clear. Even with them, the genuine matches
(static strings) and the genuine differences (e.g. the kit renders chrome as glyphs `←`/`+`
where Compose uses `Icon(contentDescription=…)`) come through.

## UPDATE — refinements done, and the corrected verdict

Earlier I framed this as "forces the wrapping cleanup" / "makes the mess measurable." That
OVERCLAIMED. The comparison does NOT show the kit wrapping is a mess. Two refinements were
applied to remove the confounds:
- (a) **dynamic structure** — the mock yields a couple of items per VM list, so row STRUCTURE
  renders (content still empty); build() is wrapped so a screen that builds a repo directly
  (bypassing the VM) yields a partial trace instead of crashing.
- (b1) **Compose slot APIs** — `_children` now descends named-argument lambdas
  (`Scaffold(topBar={…})`, `TopAppBar(title={Text("Report a bug")})`), not just trailing ones.
- plus kit input-zone labels are now extracted as anchors.

Each fix RAISES the match count (report_bug 4 → 6) and the residue stays explainable. Reading
report_bug after the fixes: the remaining Compose-only / kit-only are **the same widgets** seen
two ways — `Back` (icon contentDescription) vs `←` (kit glyph); `option.label`/`title`/`body`
(Compose variables) vs `Annoying`/`Crash detected` (the kit's resolved literals). **Not wrong
wiring.** The kit screens trace into real, structured trees — so the wrappers are **filled, not
empty**, and there is **no evidence they're mis-wired**. "Mess" was the owner's word about PAST
states (the early hand-built UI, the early transpiler); it does not describe the current kit.

Honest verdict where a clean compare exists (report_bug): the kit wrapping is **substantially
faithful** to the Compose design. Full node-for-node equality still needs variable/loop/param
resolution on the Compose side (so `option.label` resolves to the enum's labels) and real seed
data — that's the remaining work, but the question "mess or empty?" is answered: **neither.**
