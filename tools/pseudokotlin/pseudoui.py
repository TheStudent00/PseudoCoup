"""pseudoui.py -- PseudoUI: the generator. Compose @Composable tree -> kit define_* calls.

The ledgers MEASURE fidelity; this MECHANIZES the work the kit screens were hand-coding. It
walks the SAME normalized Compose tree ui_ledger reads (inlining the project's own @Composables,
descending slot lambdas) and emits, for each node, the kit
`ui.define_*(zone_id, sup_zone_id, ...)` call that reproduces it -- with content-anchored,
referenceable zone ids. The generated trace plugs straight into the SAME cross-side ledger
(kit_ledger._sig_match) for verification, and is diffed against the hand-built kit screen to show
mechanization reproduces the human's structural work.

This is the STRUCTURAL generator (the tree + its leaves). Behaviour wiring (on_click handlers,
the `items(list){}` loop -> a real Python loop) is the next layer; here a dynamic list renders
its ONE item template, whose leaf signatures match the per-row instances (the ledger is set-based,
so one template == many rendered rows).

The Compose->kit node map (v1):
  Column/LazyColumn/Box/Scaffold/Card/Surface  -> define_box "V"
  Row/LazyRow                                  -> define_box "H"
  Button family (Text label)                   -> define_button   (label consumed, no descent)
  Button family (icon only, e.g. FAB/IconBtn)  -> define_icon     (the icon IS the leaf, == Compose)
  Text                                         -> define_text     (static literal | dynamic binding)
  Icon / Image                                 -> define_icon / define_image_zone (contentDescription)
  Spacer / Divider / TextField                 -> define_spacer_zone / _divider_zone / _input_zone
  a project @Composable (WflCard, LabeledStat) -> define_box, then INLINE its body (params bound)
  any other widget                             -> define_box, then descend (never drop children)

Usage:  python3 pseudoui.py gym/GymListScreen.kt              # by path under the ui/ tree
        python3 pseudoui.py GymListScreen --screen gym_list   # by Compose name + kit screen key
Writes ledger_sample/<screen>.gen.md.
"""
import os
import re
import sys
from collections import deque

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import oracle as O                            # noqa: E402
import ui_ledger as UL                        # noqa: E402
import kit_ledger as KL                       # noqa: E402

OUT = os.path.join(HERE, "ledger_sample")

CONTAINER_ORIENT = {
    "Column": "V", "LazyColumn": "V", "FlowColumn": "V", "Box": "V", "Scaffold": "V",
    "Surface": "V", "Card": "V", "ElevatedCard": "V", "OutlinedCard": "V", "BoxWithConstraints": "V",
    "Row": "H", "LazyRow": "H", "FlowRow": "H",
}
BUTTONS = {"Button", "OutlinedButton", "TextButton", "FilledTonalButton", "ElevatedButton",
           "FloatingActionButton", "ExtendedFloatingActionButton", "IconButton",
           "IconToggleButton", "FilledIconButton", "OutlinedIconButton"}
DIVIDERS = {"Divider", "HorizontalDivider", "VerticalDivider"}
FIELDS = UL.FIELDS_UI                                     # one source of truth (matches the ledger)


# ── value helpers (resolve a param ref through the binding subst, then anchor) ──
def _resolve(expr, subst):
    return subst.get(expr.strip(), expr) if subst else expr


def _anch(expr, subst):
    """content anchor, identical to the Compose side (ui_ledger._anchor), with params resolved."""
    return UL._anchor(_resolve(expr, subst)) if expr else None


def _is_static(expr, subst):
    """static = a pure string literal (no $ interpolation) AFTER resolving any param ref."""
    return bool(re.match(r'^"[^"$]*"$', _resolve(expr, subst).strip())) if expr else False


def _text_expr(call):
    return UL._named_args(call).get("text") or UL._first_positional(call)


def _descend_find(call, pred):
    """first descendant widget (trailing + slot lambdas) matching pred, breadth-first."""
    dq = deque(UL._children(call))
    while dq:
        c = dq.popleft()
        if pred(c):
            return c
        dq.extend(UL._children(c))
    return None


def _btn_leaf(call, subst):
    """a button -> (kind, compose_type, anchor, static). A Text label => it IS the leaf the kit
    renders (define_button content == Compose's inner Text -> same signature). An icon-only
    button (FAB / IconButton) => the Icon is the leaf, matching Compose's Icon leaf by type."""
    t = _descend_find(call, lambda c: UL._name(c) == "Text")
    if t is not None and _text_expr(t):
        e = _text_expr(t)
        return "button", "Button", _anch(e, subst), _is_static(e, subst)
    ic = _descend_find(call, lambda c: UL._name(c) in ("Icon", "Image"))
    if ic is not None:
        d = UL._named_args(ic).get("contentDescription")
        if d and d.strip() != "null":
            return "icon", "Icon", _anch(d, subst), _is_static(d, subst)
    return "button", "Button", None, False


# ── zone-id minting: deterministic, content-anchored, referenceable ────────────
def _slug(s):
    s = re.sub(r"[^a-z0-9]+", "_", (s or "").lower()).strip("_")
    return s[:16] or "x"


def _zid(ctx, hint):
    n = ctx["n"]
    ctx["n"] = n + 1
    return f"{ctx['pfx']}{n:02d}_{_slug(hint)}"


def _add(ctx, kind, zid, sup, args, ctype, anchor, static):
    ctx["recs"].append((kind, zid, sup, args))
    ctx["kit_ids"].append((zid, ctype, anchor))
    if static and anchor:
        ctx["gen_static"].add(anchor)


# ── the emit walk (mirrors ui_ledger.collect_ids, emitting kit calls) ──────────
def _emit(call, sup, subst, stack, ctx):
    name = UL._name(call)
    if name is None:
        return
    defs = ctx["defs"]

    if name in BUTTONS:
        kind, ct, anchor, st = _btn_leaf(call, subst)
        args = (anchor or "",) if kind == "icon" else (anchor or "", "")
        _add(ctx, kind, _zid(ctx, anchor or name), sup, args, ct, anchor, st)
        return
    if name == "Text":
        e = _text_expr(call)
        anchor, st = _anch(e, subst), _is_static(e, subst)
        _add(ctx, "text", _zid(ctx, anchor or "text"), sup, (anchor or "", ""), "Text", anchor, st)
        return
    if name in ("Icon", "Image"):
        d = UL._named_args(call).get("contentDescription")
        on = d and d.strip() != "null"
        anchor, st = (_anch(d, subst), _is_static(d, subst)) if on else (None, False)
        if name == "Icon":
            _add(ctx, "icon", _zid(ctx, anchor or "icon"), sup, (anchor or "",), "Icon", anchor, st)
        else:
            _add(ctx, "image_zone", _zid(ctx, anchor or "image"), sup, (), "Image", anchor, st)
        return
    if name == "Spacer":
        _add(ctx, "spacer_zone", _zid(ctx, "spacer"), sup, (), "Spacer", None, False)
        return
    if name in DIVIDERS:
        _add(ctx, "divider_zone", _zid(ctx, "divider"), sup, (), "Divider", None, False)
        return
    if name in FIELDS:
        anchor, st = UL.field_anchor(call, subst)        # keyed by label, same as the ledger
        _add(ctx, "input_zone", _zid(ctx, anchor or "field"), sup,
             ("", anchor or ""), "TextField", anchor, st)
        return

    # container (known), a project @Composable, or any other widget -> a box, then descend.
    orient = CONTAINER_ORIENT.get(name, "V")
    zid = _zid(ctx, name)
    _add(ctx, "box", zid, sup, (orient, ""), "Row" if orient == "H" else "Column", None, False)
    if name in defs and name not in stack:               # inline the @Composable's body (params bound)
        params, roots = defs[name]
        argmap = UL._bind(call, params, subst)
        for r in roots:
            _emit(r, zid, argmap, stack + [name], ctx)
    for c in UL._children(call):                          # call-site slot/trailing content
        _emit(c, zid, subst, stack, ctx)


def _entry(comps):
    """the screen entry composable: prefer the public *Screen, else the first."""
    for cname, roots in comps:
        if cname.endswith("Screen"):
            return cname, roots
    return comps[0]


def generate(compose_path, screen_key):
    comps = UL.composables(compose_path)
    cname, roots = _entry(comps)
    ctx = {"recs": [], "kit_ids": [], "gen_static": set(), "n": 0,
           "pfx": _slug(screen_key) + "_z", "defs": UL._comp_defs_for(compose_path)}
    for r in roots:
        _emit(r, "content", {}, [cname], ctx)
    return cname, ctx


# ── render the generated screen (the define_* sequence + the tree) ─────────────
_DEF_ARGS = {
    "box": lambda a: f'"{a[0]}"' + (f', "{a[1]}"' if len(a) > 1 and a[1] else ""),
    "text": lambda a: f'{_q(a[0])}' + (f', "{a[1]}"' if len(a) > 1 and a[1] else ""),
    "button": lambda a: f'{_q(a[0])}',
    "icon": lambda a: f'{_q(a[0])}',
    "image_zone": lambda a: "",
    "spacer_zone": lambda a: "",
    "divider_zone": lambda a: "",
    "input_zone": lambda a: f'"", {_q(a[1])}' if len(a) > 1 else '""',
}


def _q(s):
    return f'"{s}"' if s else '""'


def _calls(ctx):
    out = []
    for kind, zid, sup, args in ctx["recs"]:
        a = _DEF_ARGS.get(kind, lambda x: "")(args)
        sep = ", " if a else ""
        out.append(f'ui.define_{kind}("{zid}", "{sup}"{", " + a if a else ""})')
    return out


def _tree_lines(ctx):
    meta = {zid: (ct, an) for zid, ct, an in ctx["kit_ids"]}
    kids, roots = {}, []
    for kind, zid, sup, args in ctx["recs"]:
        kids.setdefault(sup, []).append(zid)
        if sup == "content":
            roots.append(zid)
    lines, orphans = [], []
    seen = set(z for _, z, _, _ in ctx["recs"])
    for sup in kids:
        if sup != "content" and sup not in seen:
            orphans.append(sup)

    def walk(zid, depth):
        ct, an = meta.get(zid, ("?", None))
        seg = f"{ct}[{an}]" if an else f"{ct}[{zid.split('_', 2)[-1]}]"
        leaf = "leaf" if zid not in kids else "container"
        lines.append(f"{'  ' * depth}- {seg}  <{leaf}>")
        for c in kids.get(zid, []):
            walk(c, depth + 1)
    for r in roots:
        walk(r, 1)
    return lines, orphans


# ── verification ───────────────────────────────────────────────────────────────
def _leaf_sigs(kit_ids, comp_static):
    out = set()
    for tup in kit_ids:
        _id, t, a = tup[0], tup[1], tup[2]
        nt = KL._ntype(t)
        if nt and a:
            out.add((nt, a) if a in comp_static else (nt, "·DYN·"))
    return out


def run(compose_path, screen_key, compose_name):
    cname, ctx = generate(compose_path, screen_key)
    calls = _calls(ctx)
    tree, orphans = _tree_lines(ctx)

    # verify vs the Compose source of truth (the same _sig_match the kit ledger uses)
    compose_ids = UL.collect_ids(compose_path)
    matched, comp_sigs, kit_sigs = KL._sig_match(compose_ids, ctx["kit_ids"])
    extra = sorted(kit_sigs - comp_sigs)
    fid = 100 * len(matched) // len(comp_sigs) if comp_sigs else 0

    # diff vs the hand-built kit screen (does mechanization reproduce the human's structure?)
    comp_static = {a for _, t, a, st in compose_ids if st and a and KL._ntype(t)}
    gen_sigs = _leaf_sigs(ctx["kit_ids"], comp_static)
    hb_block, hb_only, gen_only = [], [], []
    try:
        recs, err = KL.trace(screen_key)
        roots, _ = KL.build_tree(recs, "content")
        hb_ids = []
        for i, r in enumerate(roots):
            KL.render_tree(r, 1, i, [screen_key], [], hb_ids)
        hb_sigs = _leaf_sigs(hb_ids, comp_static)
        shared = gen_sigs & hb_sigs
        gen_only = sorted(gen_sigs - hb_sigs)
        hb_only = sorted(hb_sigs - gen_sigs)
        hb_block = [
            "", "---", f"## generated  <->  hand-built kit ({screen_key}_screen.py)",
            f"- leaf signatures shared:        {len(shared)}",
            f"- generated-only (other states / not in this trace): {len(gen_only)}",
            f"- hand-built-only (helper glyphs / human representation): {len(hb_only)}",
            *( [f"    HB-only  {t}:{c}" for t, c in hb_only[:12]] ),
            *( [f"    GEN-only {t}:{c}" for t, c in gen_only[:12]] ),
            *( [f"  (hand-built trace partial: {err.split(':')[0]})"] if err else [] ),
        ]
    except Exception as e:                               # noqa: BLE001
        hb_block = ["", f"(hand-built diff unavailable: {type(e).__name__}: {e})"]

    L = [f"# PseudoUI generated kit screen -- {screen_key}  (from Compose {cname})", "",
         "Mechanically generated from the Compose @Composable tree: each node mapped to a kit",
         "define_* call with a content-anchored, referenceable zone id. NOT hand-written.", "",
         f"## generated define_* sequence  ({len(calls)} calls)", "```python",
         *calls, "```", "",
         "## generated tree", *tree, "",
         "---", f"## verify vs Compose source ({compose_name})",
         f"- distinct leaf signatures matched: {len(matched)}/{len(comp_sigs)} = {fid}%",
         f"- generated signatures NOT in Compose (fabricated): {len(kit_sigs - comp_sigs)}",
         *( [f"    GEN {t}:{c}" for t, c in extra[:12]] ),
         f"- tree validity: {len(ctx['recs'])} nodes, {len(orphans)} orphan parents",
         *hb_block, ""]
    os.makedirs(OUT, exist_ok=True)
    open(os.path.join(OUT, f"{screen_key}.gen.md"), "w").write("\n".join(L))
    print(f"  {screen_key}: generated {len(calls)} calls -> "
          f"vs Compose {len(matched)}/{len(comp_sigs)} ({fid}%), fabricated {len(kit_sigs - comp_sigs)}, "
          f"orphans {len(orphans)}; vs hand-built gen-only {len(gen_only)}, hb-only {len(hb_only)}")
    return matched, comp_sigs, kit_sigs, orphans, gen_only, hb_only


def run_all():
    keys = sorted(f[:-len("_screen.py")] for f in os.listdir(os.path.join(KL.SRC, "ui"))
                  if f.endswith("_screen.py"))
    print("PseudoUI generate ALL paired screens (Compose -> kit define_* + verify):")
    tot_m = tot_c = tot_fab = tot_orph = tot_gen = tot_hb = paired = 0
    rows = []
    for k in keys:
        cn = KL._compose_for(k)
        if not cn:
            continue
        path = O.find_one(O.MAIN, f"{cn}.kt")
        if not path:
            continue
        paired += 1
        try:
            matched, comp, kit, orphans, gen_only, hb_only = run(path, k, cn)
        except Exception as e:                           # noqa: BLE001
            print(f"  {k}: ERROR {type(e).__name__}: {e}")
            continue
        tot_m += len(matched); tot_c += len(comp); tot_fab += len(kit - comp)
        tot_orph += len(orphans); tot_gen += len(gen_only); tot_hb += len(hb_only)
        rows.append((k, len(matched), len(comp), len(orphans), len(hb_only)))
    print(f"\n  per-screen  (Compose-coverage · orphans · hand-built leaves MISSED):")
    for k, m, c, o, hb in sorted(rows, key=lambda r: (r[4], -(r[1] / r[2] if r[2] else 0))):
        flag = "  <- MISSES" if hb else ("  orphan!" if o else "")
        print(f"    {k:22} {m:3}/{c:<3} = {100*m//c if c else 0:3}%   orph {o}   hb-miss {hb}{flag}")
    print(f"\n  AGGREGATE over {paired} paired screens:")
    print(f"    Compose leaf coverage:        {tot_m}/{tot_c} = {100*tot_m//tot_c if tot_c else 0}%")
    print(f"    fabricated (gen not in Compose): {tot_fab}")
    print(f"    invalid trees (orphan parents):  {tot_orph}")
    print(f"    hand-built leaves NOT reproduced: {tot_hb}   (the key number: 0 = mechanization "
          f"covers every hand-built leaf)")


def _resolve_path(arg):
    if os.path.isabs(arg) and os.path.exists(arg):
        return arg
    base = os.path.basename(arg)
    name = base[:-3] if base.endswith(".kt") else base
    p = O.find_one(O.MAIN, f"{name}.kt")
    if p:
        return p
    cand = os.path.join(UL.UIROOT, arg if arg.endswith(".kt") else arg + ".kt")
    return cand if os.path.exists(cand) else None


def main():
    if "--all" in sys.argv:
        run_all()
        return
    args = [a for a in sys.argv[1:] if not a.startswith("-")]
    screen = None
    if "--screen" in sys.argv:
        screen = sys.argv[sys.argv.index("--screen") + 1]
    target = args[0] if args else "gym/GymListScreen.kt"
    path = _resolve_path(target)
    if not path:
        print(f"  could not resolve Compose file for {target!r}")
        return
    compose_name = os.path.basename(path)[:-3]
    if screen is None:
        screen = re.sub(r"(?<!^)(?=[A-Z])", "_",
                        compose_name[:-6] if compose_name.endswith("Screen") else compose_name).lower()
    print(f"PseudoUI generate -> ledger_sample/{screen}.gen.md")
    run(path, screen, compose_name)


if __name__ == "__main__":
    main()
