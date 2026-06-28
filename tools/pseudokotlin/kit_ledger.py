"""kit_ledger.py -- the Python/kit SIDE of the UI fidelity ledger, + the cross-side compare.

ui_ledger.py read the KOTLIN side (Compose) statically. This reads the kit side by RUNTIME
TRACING: the kit builds screens imperatively as `ui.define_*(zone_id, sup_zone_id, ...)` calls
(every node has an explicit id and parent id), so a recording mock `UI` -- run through the
screen's `build()` -- captures the true tree, including nodes emitted by `ui.widgets` helpers.
This is the kit analog of the exec-and-introspect the engine ledger uses.

It normalizes into the SAME schema as the Compose side (type · size abs/rel · content anchor ·
path-id) and then compares node-for-node, joining on the content anchor (the user-visible
string -- the one key that's reliable across two structurally-different trees). The compare
makes the "wrapping is a mess" concrete: matched / Compose-only (in the design, missing from
the kit) / kit-only (added by the wrapping).

Headless: a stub `kit` module avoids Kivy/display; a permissive mock stands in for the db/VM/
router, so dynamic list content is empty -- the STATIC skeleton (chrome, labels, buttons) is
what's compared. Usage:  python3 kit_ledger.py gym_list [--compose GymListScreen]
"""
import importlib
import os
import sys
import types

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import oracle as O                          # noqa: E402
import ui_ledger as UL                      # noqa: E402

SRC = "/home/lucas/Programming/WFL_PseudoCoup/src"
OUT = os.path.join(HERE, "ledger_sample")

# kit kind -> normalized type (so it lines up with the Compose-side types)
KIND_TYPE = {"box": None, "text": "Text", "button": "Button", "input_zone": "TextField",
             "spacer_zone": "Spacer", "divider_zone": "Divider", "image_zone": "Image",
             "icon": "Icon", "progress": "Progress", "marker": "Marker", "zone": "Zone",
             "layout_zone": "LayoutZone", "canvas_zone": "CanvasZone", "slider_zone": "Slider",
             "absolute_zone": "AbsoluteZone", "overlay": "Overlay", "layer": "Layer"}


class _Any:
    """permissive stand-in for db / VM / router / entities: any access is safe, loops empty."""
    def __getattr__(self, n): return _Any()
    def __call__(self, *a, **k): return _Any()
    def __iter__(self): return iter(())
    def __bool__(self): return False
    def __len__(self): return 0
    def __str__(self): return ""
    def __getitem__(self, k): return _Any()
    def __hash__(self): return 0
    def __eq__(self, o): return False


class _RecUI:
    def __init__(self):
        self.recs = []                       # (kind, zone_id, sup_zone_id, args)

    def __getattr__(self, name):
        if name.startswith("define_"):
            kind = name[len("define_"):]

            def rec(zone_id, sup_zone_id, *a, **k):
                self.recs.append((kind, zone_id, sup_zone_id, a))
                return None
            return rec
        return lambda *a, **k: _Any()


def trace(screen_key, content="content"):
    ks = types.ModuleType("kit")
    ks.UI = _RecUI
    ks.Event = type("Event", (), {})
    sys.modules["kit"] = ks
    if SRC not in sys.path:
        sys.path.insert(0, SRC)
    mod = importlib.import_module(f"ui.{screen_key}_screen")
    cls = next(v for k, v in vars(mod).items()
               if isinstance(v, type) and k.endswith("Screen"))
    try:
        screen = cls(_Any())
    except Exception:                        # noqa: BLE001 -- ctor wants something else
        screen = cls.__new__(cls)
    for attr in ("owned_ids", "_item_zone_ids", "_item_gym_ids",
                 "_setactive_zone_ids", "_setactive_gym_ids"):
        if not hasattr(screen, attr):
            setattr(screen, attr, [])
    if not hasattr(screen, "vm") or isinstance(getattr(screen, "vm"), _Any):
        screen.vm = _Any()
    ui = _RecUI()
    screen.build(ui, content, _Any())
    return ui.recs


# ── tree from the parent links ───────────────────────────────────────────────
def _norm_rec(kind, zid, sup, args):
    t = KIND_TYPE.get(kind, kind)
    content = orient = style = weight = None
    if kind == "box":
        orient = args[0] if len(args) > 0 else None
        style = args[1] if len(args) > 1 else None
        weight = args[2] if len(args) > 2 else 0.0
        t = "Row" if orient == "H" else ("Column" if orient == "V" else "Box")
    elif kind in ("text", "button"):
        content = args[0] if len(args) > 0 else None
        style = args[1] if len(args) > 1 else None
        weight = args[2] if len(args) > 2 else 0.0
    return {"id": zid, "sup": sup, "kind": kind, "type": t, "content": content,
            "style": style, "weight": weight, "orient": orient, "children": []}


def build_tree(recs, content):
    nodes = {}
    order = []
    for kind, zid, sup, args in recs:
        if not isinstance(zid, str):
            continue
        nodes[zid] = _norm_rec(kind, zid, sup, args)
        order.append(zid)
    roots = []
    for zid in order:
        n = nodes[zid]
        p = nodes.get(n["sup"])
        (p["children"] if p else roots).append(n)
    return roots, nodes


def _anchor(n):
    if n["content"]:
        s = " ".join(str(n["content"]).split())
        return (s[:30] + "…") if len(s) > 31 else s
    return None


def _seg(n, idx):
    a = _anchor(n)
    return f"{n['type']}[{a}]" if a else f"{n['type']}[{idx}]"


def _size(n):
    # kit: weight>0 -> proportional (relative); style token -> absolute padding/size; else wrap
    w = "wrap"
    if n["weight"] and float(n["weight"] or 0) > 0:
        w = f"weight({n['weight']})"
    return w


def render_tree(n, depth, idx, path, lines, ids):
    seg = _seg(n, idx)
    full = "/".join(path + [seg])
    ids.append((full, n["type"], _anchor(n)))
    ind = "  " * depth
    sz = _size(n)
    tag = "rel" if (sz.startswith("weight") or sz == "wrap") else "abs"
    kind = "container" if n["children"] else "leaf"
    extra = f"  style={n['style']}(abs)" if n["style"] else ""
    lines.append(f"{ind}- {seg}  <{kind}>   size: {sz}({tag}){extra}")
    for i, c in enumerate(n["children"]):
        render_tree(c, depth + 1, i, path + [seg], lines, ids)


# ── cross-side compare (join on content anchor) ──────────────────────────────
def compare(compose_ids, kit_ids):
    ca = {a for _, _, a in compose_ids if a}
    ka = {a for _, _, a in kit_ids if a}
    return sorted(ca & ka), sorted(ca - ka), sorted(ka - ca)


def run(screen_key, compose_name):
    recs = trace(screen_key)
    roots, nodes = build_tree(recs, "content")
    name = "".join(p.capitalize() for p in screen_key.split("_"))
    L = [f"# UI layout ledger (KIT side) -- {screen_key}", "",
         "Python/kit side, runtime-traced: a recording UI captured every define_* call (incl.",
         "helper-emitted), tree rebuilt from the explicit parent ids. Same normalized schema as",
         "the Compose side. (Mock db/VM -> dynamic list items are empty; static skeleton shown.)", ""]
    kit_ids = []
    for i, r in enumerate(roots):
        render_tree(r, 1, i, [screen_key], L, kit_ids)
    L += ["", "  ids:"] + [f"    {x[0]}" for x in kit_ids] + [""]

    # compare to the Compose side
    cmp_block = []
    if compose_name:
        kt = O.find_one(O.MAIN, f"{compose_name}.kt")
        if kt:
            compose_ids = UL.collect_ids(kt)
            matched, c_only, k_only = compare(compose_ids, kit_ids)
            cmp_block = ["---", f"## cross-side compare: Compose {compose_name} <-> kit {screen_key}",
                         f"- matched (by content anchor): {len(matched)}",
                         *[f"    = {m}" for m in matched[:20]],
                         f"- Compose-only (in design, MISSING from kit): {len(c_only)}",
                         *[f"    KT  {m}" for m in c_only[:20]],
                         f"- kit-only (ADDED by the wrapping): {len(k_only)}",
                         *[f"    PY  {m}" for m in k_only[:20]], ""]
    L += cmp_block
    os.makedirs(OUT, exist_ok=True)
    open(os.path.join(OUT, f"{screen_key}.kit.md"), "w").write("\n".join(L))
    nmatch = len([1 for x in cmp_block if x.startswith("    =")]) if cmp_block else 0
    print(f"  {screen_key}: {len(kit_ids)} kit nodes" +
          (f" · compare vs {compose_name}: {nmatch} matched anchors" if compose_name else "") +
          f" -> ledger_sample/{screen_key}.kit.md")


def main():
    args = [a for a in sys.argv[1:] if not a.startswith("-")]
    compose = None
    if "--compose" in sys.argv:
        compose = sys.argv[sys.argv.index("--compose") + 1]
    key = args[0] if args else "gym_list"
    if compose is None:
        compose = "".join(p.capitalize() for p in key.split("_")) + "Screen"
    print("UI kit-side ledger -> ledger_sample/")
    run(key, compose)


if __name__ == "__main__":
    main()
