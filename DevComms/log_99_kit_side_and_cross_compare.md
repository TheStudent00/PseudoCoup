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

## Where this lands

The UI ledger now has BOTH sides and a working comparison — this is the rung that "forces the
wrapping cleanup": it makes the divergence between the Compose design and the kit reality
measurable and localized. Next refinements (owner's call): (a) trace with seed data so dynamic
rows compare; (b) inline Compose composables + resolve params so both sides are fully expanded;
then the match becomes a true node-for-node correspondence rather than a content-anchor join.
