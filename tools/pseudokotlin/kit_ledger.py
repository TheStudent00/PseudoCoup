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
    """permissive stand-in for db / VM / router / entities: any access is safe; iterating a
    list-returning VM call yields a couple of mock items so dynamic ROW STRUCTURE renders
    (content stays empty -- structure is what the cross-side compare needs)."""
    def __getattr__(self, n): return _Any()
    def __call__(self, *a, **k): return _Any()
    def __iter__(self): return iter((_Any(), _Any()))
    def __bool__(self): return False
    def __len__(self): return 0
    def __str__(self): return ""
    def __format__(self, spec): return ""
    def __getitem__(self, k): return _Any()
    def __hash__(self): return 0
    def __eq__(self, o): return False
    def __int__(self): return 0                  # survive numeric coercion / arithmetic in build()
    def __float__(self): return 0.0
    def __index__(self): return 0
    def __add__(self, o): return _Any()
    def __radd__(self, o): return _Any()
    def __sub__(self, o): return _Any()
    def __rsub__(self, o): return _Any()
    def __mul__(self, o): return _Any()
    def __rmul__(self, o): return _Any()
    def __truediv__(self, o): return _Any()
    def __rtruediv__(self, o): return _Any()
    def __floordiv__(self, o): return _Any()
    def __mod__(self, o): return _Any()
    def __lt__(self, o): return False
    def __gt__(self, o): return False
    def __le__(self, o): return False
    def __ge__(self, o): return False


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


_STUBBED = False
_SEEDED_DB = None


def _setup_modules():
    """stub `kit` (avoid Kivy/display) and `pseudodart.discipline` (the engines import a no-op
    discipline decorator) so the whole app -- engines included -- imports headlessly."""
    global _STUBBED
    if _STUBBED:
        return
    ks = types.ModuleType("kit")
    ks.UI = _RecUI
    ks.Event = type("Event", (), {})
    sys.modules["kit"] = ks
    pd = types.ModuleType("pseudodart")
    disc = types.ModuleType("pseudodart.discipline")

    def dart_extern(*a, **k):
        return a[0] if (len(a) == 1 and callable(a[0]) and not k) else (lambda f: f)
    disc.dart_extern = dart_extern
    pd.discipline = disc
    sys.modules["pseudodart"] = pd
    sys.modules["pseudodart.discipline"] = disc
    if SRC not in sys.path:
        sys.path.insert(0, SRC)
    _STUBBED = True


def _seeded_db():
    """the app's OWN seed (AppMain._seed) on a fresh InMemoryDb -- the real faithful state
    (185 exercises, 3 programs, 4 paths, gym, sessions, program hierarchy). One call seeds
    every screen; no per-screen seeders."""
    global _SEEDED_DB
    if _SEEDED_DB is None:
        from data.db.db import InMemoryDb
        am = importlib.import_module("ui.app_main")
        db = InMemoryDb()
        app = am.AppMain.__new__(am.AppMain)
        app.db = db
        app._seed()
        _SEEDED_DB = db
    return _SEEDED_DB


def trace(screen_key, content="content"):
    _setup_modules()
    db = _seeded_db()
    mod = importlib.import_module(f"ui.{screen_key}_screen")
    cls = next(v for k, v in vars(mod).items()
               if isinstance(v, type) and k.endswith("Screen"))
    try:                                     # faithful: real seeded Db -> real VM -> real rows
        screen = cls(db)
    except Exception:                        # noqa: BLE001 -- a different ctor; fall back to mock
        try:
            screen = cls(_Any())
        except Exception:                    # noqa: BLE001
            screen = cls.__new__(cls)
        for attr in ("owned_ids", "_item_zone_ids", "_item_gym_ids",
                     "_setactive_zone_ids", "_setactive_gym_ids"):
            if not hasattr(screen, attr):
                setattr(screen, attr, [])
        if not hasattr(screen, "vm"):
            screen.vm = _Any()
        if not hasattr(screen, "db"):
            screen.db = db
    ui = _RecUI()
    err = None
    try:
        screen.build(ui, content, _Any())
    except Exception as e:                   # noqa: BLE001
        err = f"{type(e).__name__}: {e}"
    return ui.recs, err


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
    elif kind == "input_zone":               # (default_text, label_text) -> id by its label
        content = (args[1] if len(args) > 1 and args[1] else (args[0] if args else None))
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
    ca = {a for _, _, a, _ in compose_ids if a}
    ka = {a for _, _, a in kit_ids if a}
    return sorted(ca & ka), sorted(ca - ka), sorted(ka - ca)


def _ntype(t):
    if t in ("Text", "Button"):
        return "T"
    if t in ("Icon", "Image"):
        return "I"
    if t in ("TextField", "OutlinedTextField", "BasicTextField", "input_zone"):
        return "F"
    return None                              # container / non-content node


def _compose_leaves(compose_ids):
    return [(nt, a, st) for _, typ, a, st in compose_ids
            if (nt := _ntype(typ))]


def _kit_leaves(kit_ids):
    return [(nt, a) for _, typ, a in kit_ids if (nt := _ntype(typ)) and a]


def _lcs(comp, kit):
    """longest common subsequence of the leaf sequences. A static Compose leaf matches by
    content; a DYNAMIC leaf (a binding the kit renders resolved) matches by type+order only --
    so a faithfully-reproduced dynamic row counts, even though its strings differ."""
    def m(c, k):
        return c[0] == k[0] and ((not c[2]) or c[1] == k[1])
    n, M = len(comp), len(kit)
    dp = [[0] * (M + 1) for _ in range(n + 1)]
    for i in range(n - 1, -1, -1):
        for j in range(M - 1, -1, -1):
            dp[i][j] = (1 + dp[i + 1][j + 1] if m(comp[i], kit[j])
                        else max(dp[i + 1][j], dp[i][j + 1]))
    return dp[0][0]


def _sig_match(compose_ids, kit_ids):
    """instance-count-robust: compare the SETS of distinct leaf signatures. A static leaf ->
    (type, content); a dynamic binding -> (type, DYN). kit content that isn't a Compose static
    literal is treated as DYN (the kit renders bindings resolved). -> (matched, comp, kit)."""
    comp_static = {a for _, t, a, st in compose_ids if st and a and _ntype(t)}
    comp_sigs, kit_sigs = set(), set()
    for _, t, a, st in compose_ids:
        if (nt := _ntype(t)) and a:          # anchorless leaf (decorative icon) -> not a content sig
            comp_sigs.add((nt, a) if st else (nt, "·DYN·"))
    for _, t, a in kit_ids:
        if (nt := _ntype(t)) and a:
            kit_sigs.add((nt, a) if a in comp_static else (nt, "·DYN·"))
    return comp_sigs & kit_sigs, comp_sigs, kit_sigs


def run(screen_key, compose_name):
    recs, err = trace(screen_key)
    roots, nodes = build_tree(recs, "content")
    L = [f"# UI layout ledger (KIT side) -- {screen_key}", "",
         "Python/kit side, runtime-traced through the app's OWN seeded InMemoryDb (real data).",
         "A recording UI captured every define_* call; tree rebuilt from the explicit parent ids.",
         *( [f"(partial trace -- build raised {err} after the nodes below)"] if err else [] ), ""]
    kit_ids, tree = [], []
    for i, r in enumerate(roots):
        render_tree(r, 1, i, [screen_key], tree, kit_ids)
    CAP = 80
    L += tree[:CAP] + ([f"  … (+{len(tree)-CAP} more nodes; {len(kit_ids)} total)"] if len(tree) > CAP else [])

    cmp_block, comp = [], None
    if compose_name and (kt := O.find_one(O.MAIN, f"{compose_name}.kt")):
        compose_ids = UL.collect_ids(kt)
        matched, comp_sigs, kit_sigs = _sig_match(compose_ids, kit_ids)
        extra = sorted(kit_sigs - comp_sigs)
        fid = 100 * len(matched) // len(comp_sigs) if comp_sigs else 0
        comp = (len(matched), len(comp_sigs), len(kit_sigs))
        cmp_block = ["", "---", f"## cross-side compare: Compose {compose_name} <-> kit {screen_key}",
                     f"- distinct widget signatures matched: {len(matched)}/{len(comp_sigs)} = {fid}%",
                     "  (static leaf by content; dynamic binding by type -- instance counts ignored)",
                     f"- kit signatures NOT in Compose: {len(kit_sigs - comp_sigs)}",
                     *[f"    PY  {t}:{c}" for t, c in extra[:15]], ""]
    L += cmp_block
    os.makedirs(OUT, exist_ok=True)
    open(os.path.join(OUT, f"{screen_key}.kit.md"), "w").write("\n".join(L))
    print(f"  {screen_key}: {len(kit_ids)} kit nodes" +
          (f" · vs {compose_name}: {comp[0]}/{comp[1]} sigs "
           f"({100*comp[0]//comp[1] if comp[1] else 0}%) · kit-extra {comp[2]-comp[0]}"
           if comp else "") + (f"  (partial: {err.split(':')[0]})" if err else ""))
    return comp


def _compose_for(key):
    cand = "".join(p.capitalize() for p in key.split("_")) + "Screen"
    return cand if O.find_one(O.MAIN, f"{cand}.kt") else None


def run_all():
    keys = sorted(f[:-len("_screen.py")] for f in os.listdir(os.path.join(SRC, "ui"))
                  if f.endswith("_screen.py"))
    print(f"UI kit-side ledger, ALL screens with a Compose counterpart (app-seeded):")
    matched_tot, sig_tot, extra_tot = 0, 0, 0
    paired = 0
    rows = []
    for k in keys:
        cn = _compose_for(k)
        if not cn:
            continue
        paired += 1
        try:
            comp = run(k, cn)
        except Exception as e:                           # noqa: BLE001
            print(f"  {k}: ERROR {type(e).__name__}")
            continue
        if comp:
            matched_tot += comp[0]
            sig_tot += comp[1]
            extra_tot += comp[2] - comp[0]
            rows.append((k, comp[0], comp[1]))
    print(f"\n  per-screen signature fidelity (matched/Compose-distinct):")
    for k, m, s in sorted(rows, key=lambda r: -(r[1] / r[2] if r[2] else 0)):
        print(f"    {k:22} {m:3}/{s:<3} = {100*m//s if s else 0:3}%")
    print(f"\n  AGGREGATE over {paired} app-seeded screens:")
    print(f"    distinct widget signatures matched: {matched_tot}/{sig_tot} = "
          f"{100*matched_tot//sig_tot if sig_tot else 0}%")
    print(f"    kit signatures not in Compose:      {extra_tot}  (glyphs/helper extras/representation)")


def main():
    if "--all" in sys.argv:
        run_all()
        return
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
