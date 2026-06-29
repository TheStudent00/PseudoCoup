"""pseudoui_run.py -- PseudoUI behaviour layer: control-flow IR + interpreter + runtime verify.

The structural generator (pseudoui.py) flattens a screen to its widgets -- it descends BOTH
branches of every `if`, renders a list's template ONCE, and leaves bindings like `gym.name`
unresolved. That proves STRUCTURE. This proves BEHAVIOUR: it lifts the Compose control flow
(`items(list){}`, `if/else`, `expr?.let{}`) into a small IR, then INTERPRETS that IR against the
app's real seeded data -- looping real rows, taking the branch the real data selects, resolving
each binding to its real value -- and emits the same kind of `define_*` trace the hand-built
screen produces. Comparing the two RESOLVED traces is the dynamic/functional-equivalence check.

Three binding strategies (resolve an IR expression -> a value), increasing in fidelity-to-Kotlin:
  default  reshaped spec   -- hand lambdas mapping Compose->kit (the kit RESHAPED the data path:
                              GymWithEquipment -> profile + equipment_for(id); activeGym -> isActive).
  --1to1   transpiled VM    -- run against KtToPy(GymListViewModel); hand spec is Kotlin-shaped.
  --auto   the TRANSPILER   -- NO hand spec: each IR expression (val RHS, cond, src, leaf) is
                              transpiled Kt->Py and eval'd against kotlin_rt + the transpiled VM.
The --auto path is the repeatable crank: structure, control flow, the viewmodel, AND the bindings
all derive mechanically from Kotlin; only a fixed reactive/DAO/stdlib shim is supplied once.

Usage:  python3 pseudoui_run.py gym_list --ir     # dump the generated IR (incl. val binds)
        python3 pseudoui_run.py gym_list           # reshaped-spec runtime verify vs hand-built
        python3 pseudoui_run.py gym_list --1to1    # transpiled VM + Kotlin-shaped spec
        python3 pseudoui_run.py gym_list --auto    # transpiler-emitted bindings (no hand spec)
"""
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import oracle as O                            # noqa: E402
import ui_ledger as UL                        # noqa: E402
import kit_ledger as KL                       # noqa: E402
import pseudoui as G                           # noqa: E402
from dispatch import Visitor as _V            # noqa: E402

_pysafe = _V._safe                            # Kotlin id -> legal Python (keyword `def` -> `def_`)

OUT = os.path.join(HERE, "ledger_sample")


# ── tree-sitter statement helpers ─────────────────────────────────────────────
def _lambda_literal(lam):
    if lam is None:
        return None
    if lam.type == "lambda_literal":
        return lam
    return next((k for k in lam.children if k.type == "lambda_literal"), None)


def _stmts(node):
    """ordered statement nodes inside a block / lambda_literal / function_body / control body."""
    if node is None:
        return []
    inner = node
    if node.type in ("function_body",):
        inner = next((k for k in node.children if k.type in ("block", "statements")), node)
    if inner.type in ("annotated_lambda", "lambda_literal"):
        inner = _lambda_literal(inner) or inner
    out = []
    for c in inner.children:
        if c.type == "statements":
            out.extend(c.children)
        elif c.type not in ("{", "}", "->", "(", ")", "lambda_parameters", "comment", ";"):
            out.append(c)
    return out


def _lambda_param(lam):
    lit = _lambda_literal(lam)
    if lit is None:
        return None
    lp = next((k for k in lit.children if k.type == "lambda_parameters"), None)
    if lp is None:
        return None
    for k in lp.children:                                 # identifier, or a variable_declaration wrapping one
        if k.type == "identifier":
            return k.text.decode()
        if k.type == "variable_declaration":
            idc = next((c for c in k.children if c.type == "identifier"), None)
            return idc.text.decode() if idc else k.text.decode().strip()
    return None


def _child_stmts(call):
    """ordered child statements of a widget call: its trailing lambda + any slot-arg lambdas."""
    base, lam = UL._base_and_lambda(call)
    out = []
    if lam is not None:
        out += _stmts(lam)
    va = next((k for k in base.children if k.type == "value_arguments"), None)
    if va:
        for a in va.named_children:
            if a.type == "value_argument":
                for k in a.children:
                    if k.type in ("lambda_literal", "annotated_lambda"):
                        out += _stmts(k)
    return out


def _is_let(call):
    nav = next((k for k in call.children if k.type == "navigation_expression"), None)
    return bool(nav and ".let" in nav.text.decode())


def _is_foreach_method(call):
    nav = next((k for k in call.children if k.type == "navigation_expression"), None)
    return bool(nav and re.search(r"\.forEach(Indexed)?$", nav.text.decode()))


def _parse_foreach_method(call):
    """receiver.forEach { var -> body } -> (receiver_expr, var, body_stmts)."""
    nav = next((k for k in call.children if k.type == "navigation_expression"), None)
    recv = re.sub(r"\.forEach(Indexed)?$", "", nav.text.decode()).strip() if nav else None
    lam = next((k for k in call.children if k.type in ("annotated_lambda", "lambda_literal")), None)
    return recv, _lambda_param(lam), (_stmts(lam) if lam else [])


def _parse_let(call):
    nav = next((k for k in call.children if k.type == "navigation_expression"), None)
    subj = re.split(r"\?\.let|\.let", nav.text.decode(), maxsplit=1)[0].strip() if nav else None
    lam = next((k for k in call.children if k.type in ("annotated_lambda", "lambda_literal")), None)
    return subj, _lambda_param(lam), (_stmts(lam) if lam else [])


def _parse_val(pd):
    """a `val X = expr` or `val X by delegate` -> (name, rhs_kotlin_expr)."""
    vd = next((k for k in pd.children if k.type == "variable_declaration"), None)
    name = None
    if vd is not None:
        idc = next((c for c in vd.children if c.type == "identifier"), None)
        name = idc.text.decode() if idc else vd.text.decode().strip()
    delegate = next((k for k in pd.children if k.type == "property_delegate"), None)
    if delegate is not None:                              # `by <expr>` (e.g. collectAsState)
        return name, re.sub(r"^by\s+", "", delegate.text.decode()).strip()
    eq, rhs = False, None                                 # `= <expr>`
    for k in pd.children:
        if k.type == "=":
            eq = True
        elif eq and k.type != ";":
            rhs = k.text.decode(); break
    return name, rhs


def _parse_if(node):
    cond_nodes, blocks, state, seen_else = [], [], "pre", False
    for k in node.children:
        if k.type == "(" and state == "pre":
            state = "cond"
        elif k.type == ")" and state == "cond":
            state = "post"
        elif state == "cond":
            cond_nodes.append(k)
        elif k.type == "else":
            seen_else = True
        elif k.type in ("block", "control_structure_body", "statements", "call_expression"):
            blocks.append((k, seen_else))
    cond = " ".join(n.text.decode() for n in cond_nodes).strip()
    then_b = next((b for b, e in blocks if not e), None)
    else_b = next((b for b, e in blocks if e), None)
    return cond, then_b, else_b


# ── IR build (mirrors pseudoui._emit, but control-flow aware) ──────────────────
def _ir_node(stmt, subst, stack, defs, out):
    """append the IR for one statement node (widget call / if / items / ?.let) to `out`."""
    if stmt.type == "if_expression":
        cond, tb, eb = _parse_if(stmt)
        then_ir, else_ir = [], []
        for s in (_stmts(tb) if tb else []):
            _ir_node(s, subst, stack, defs, then_ir)
        for s in (_stmts(eb) if eb else []):
            _ir_node(s, subst, stack, defs, else_ir)
        out.append({"t": "if", "cond": _sub(cond, subst), "then": then_ir, "else": else_ir})
        return
    if stmt.type == "property_declaration":               # val X = expr  ->  a scope binding
        nm, rhs = _parse_val(stmt)
        if nm and rhs:
            out.append({"t": "bind", "name": _pysafe(nm), "expr": _sub(rhs, subst)})
        return
    if stmt.type != "call_expression":
        return
    name = UL._name(stmt)
    if name == "items":                                   # LazyList items(src){ var -> body }
        src = UL._first_positional(stmt)
        base, lam = UL._base_and_lambda(stmt)
        var = _lambda_param(lam)
        body = []
        for s in _stmts(lam):
            _ir_node(s, subst, stack, defs, body)
        out.append({"t": "foreach", "src": _sub(src, subst), "var": _pysafe(var), "kids": body})
        return
    if name in ("item", "stickyHeader"):                  # LazyListScope.item{} -> transparent wrapper
        base, lam = UL._base_and_lambda(stmt)
        for s in _stmts(lam):
            _ir_node(s, subst, stack, defs, out)
        return
    if _is_foreach_method(stmt):                          # receiver.forEach { var -> body }
        recv, var, body_stmts = _parse_foreach_method(stmt)
        body = []
        for s in body_stmts:
            _ir_node(s, subst, stack, defs, body)
        out.append({"t": "foreach", "src": _sub(recv, subst), "var": _pysafe(var) if var else "it", "kids": body})
        return
    if _is_let(stmt):                                     # expr?.let { var -> body }
        subj, var, body_stmts = _parse_let(stmt)
        body = []
        for s in body_stmts:
            _ir_node(s, subst, stack, defs, body)
        out.append({"t": "let", "subj": _sub(subj, subst), "var": _pysafe(var) if var else "it", "kids": body})
        return
    if not name or not name[0].isupper():                 # lowercase call = handler/helper, not UI
        return
    _ir_widget(stmt, name, subst, stack, defs, out)


def _sub(expr, subst):
    if not expr:
        return expr
    e = expr.strip()
    return subst.get(e, expr)


def _onclick(call, subst):
    """the resolved onClick handler expr of a clickable widget (None / no-op `{}` -> None)."""
    oc = UL._named_args(call).get("onClick")
    if not oc:
        return None
    r = _sub(oc, subst)
    return None if re.sub(r"[\s{}]", "", r) == "" else r


def _ir_widget(call, name, subst, stack, defs, out):
    if name in G.BUTTONS:
        kind, ct, anchor, st, expr = _btn(call, subst)
        out.append({"t": "leaf", "kind": kind, "ctype": ct, "expr": expr, "static": st,
                    "onclick": _onclick(call, subst)})
        return
    if name == "Text":
        e = G._text_expr(call)
        out.append({"t": "leaf", "kind": "text", "ctype": "Text",
                    "expr": _sub(e, subst), "static": G._is_static(e, subst)})
        return
    if name in ("Icon", "Image"):
        d = UL._named_args(call).get("contentDescription")
        on = d and d.strip() != "null"
        out.append({"t": "leaf", "kind": "icon" if name == "Icon" else "image_zone",
                    "ctype": name, "expr": _sub(d, subst) if on else None,
                    "static": G._is_static(d, subst) if on else False})
        return
    if name == "Spacer":
        out.append({"t": "leaf", "kind": "spacer_zone", "ctype": "Spacer", "expr": None, "static": False})
        return
    if name in G.DIVIDERS:
        out.append({"t": "leaf", "kind": "divider_zone", "ctype": "Divider", "expr": None, "static": False})
        return
    if name in G.FIELDS:
        anchor, st = UL.field_anchor(call, subst)
        out.append({"t": "leaf", "kind": "input_zone", "ctype": "TextField", "expr": anchor, "static": st})
        return
    # container / custom composable / unknown -> a box, recurse (control-flow aware)
    orient = G.CONTAINER_ORIENT.get(name, "V")
    kids = []
    if name in defs and name not in stack:                # inline the @Composable BODY (params bound)
        params, body = defs[name]
        argmap = UL._bind(call, params, subst)
        for s in _stmts(body):
            _ir_node(s, argmap, stack + [name], defs, kids)
    for s in _child_stmts(call):                          # call-site slot/trailing content
        _ir_node(s, subst, stack, defs, kids)
    out.append({"t": "box", "orient": orient, "name": name, "kids": kids,
                "onclick": _onclick(call, subst)})        # clickable container (e.g. WflCard onClick=onEdit)


def _btn(call, subst):
    kind, ct, anchor, st = G._btn_leaf(call, subst)
    return kind, ct, anchor, st, anchor


# ── composable bodies (keep the body node for statement walking) ───────────────
_BODIES = None


def _comp_bodies():
    global _BODIES
    if _BODIES is None:
        _BODIES = {}
        for dp, _, fs in os.walk(UL.UIROOT):
            for f in fs:
                if not f.endswith(".kt"):
                    continue
                try:
                    tree = UL.parse(open(os.path.join(dp, f), "rb").read())
                except Exception:                          # noqa: BLE001
                    continue
                UL._TREES.append(tree)
                stack = [tree.root_node]
                while stack:
                    n = stack.pop()
                    if n.type == "function_declaration":
                        mods = next((k for k in n.children if k.type == "modifiers"), None)
                        if mods and "@Composable" in mods.text.decode():
                            nm = next((k.text.decode() for k in n.children if k.type == "identifier"), None)
                            fvp = next((k for k in n.children if k.type == "function_value_parameters"), None)
                            params = []
                            if fvp:
                                for p in fvp.named_children:
                                    if p.type == "parameter":
                                        pn = next((k.text.decode() for k in p.children
                                                   if k.type == "identifier"), None)
                                        if pn:
                                            params.append(pn)
                            body = next((k for k in n.children if k.type == "function_body"), None)
                            if nm and body is not None:
                                _BODIES[nm] = (params, body)
                    stack.extend(n.children)
    return _BODIES


# Representation map: the kit backend draws certain Compose icons as text glyphs (its top_bar/fab/
# chip helpers), and folds an AssistChip's leading check into the label. Applying it to the IR makes
# the generated trace match the hand-built kit's glyph convention -- so generated could REPLACE it.
_GLYPH = {"Back": "←", "Add": "+", "Add gym": "+", "Close": "✕", "Cancel": "✕"}


def _represent(nodes):
    for n in nodes:
        t = n["t"]
        if t == "leaf" and n["kind"] == "icon" and n["static"] and n["expr"]:
            g = _GLYPH.get(_static_lit(n["expr"]))
            if g:
                n.update(kind="text", ctype="Text", expr=f'"{g}"')
        elif t == "box":
            if n.get("name") == "AssistChip" and any(
                    c["t"] == "leaf" and c["kind"] == "icon" for c in n["kids"]):
                for c in n["kids"]:                      # fold the check glyph into the chip label
                    if c["t"] == "leaf" and c["kind"] == "text" and c["static"] and c["expr"]:
                        c["expr"] = f'"✓ {_static_lit(c["expr"])}"'
                        break
            _represent(n["kids"])
        elif t == "if":
            _represent(n["then"]); _represent(n["else"])
        elif t in ("foreach", "let"):
            _represent(n["kids"])


def build_ir(compose_path):
    comps = UL.composables(compose_path)
    cname, _ = G._entry(comps)
    defs = _comp_bodies()
    params, body = defs[cname]
    out = []
    for s in _stmts(body):
        _ir_node(s, {}, [cname], defs, out)
    _represent(out)                                      # kit glyph convention (←/+/✓)
    return cname, out


# ── IR dump (verify before interpreting) ───────────────────────────────────────
def _dump(ir, depth, lines):
    for n in ir:
        ind = "  " * depth
        if n["t"] == "box":
            lines.append(f"{ind}box {n['orient']} ({n['name']})")
            _dump(n["kids"], depth + 1, lines)
        elif n["t"] == "foreach":
            lines.append(f"{ind}FOREACH {n['var']} in {n['src']}:")
            _dump(n["kids"], depth + 1, lines)
        elif n["t"] == "if":
            lines.append(f"{ind}IF {n['cond']}:")
            _dump(n["then"], depth + 1, lines)
            if n["else"]:
                lines.append(f"{ind}ELSE:")
                _dump(n["else"], depth + 1, lines)
        elif n["t"] == "let":
            lines.append(f"{ind}LET {n['var']} = {n['subj']} (if non-null):")
            _dump(n["kids"], depth + 1, lines)
        elif n["t"] == "bind":
            lines.append(f"{ind}val {n['name']} = {n['expr']}")
        elif n["t"] == "leaf":
            tag = "static" if n["static"] else "DYN"
            lines.append(f"{ind}{n['ctype']}<{tag}> {n['expr']!r}")


# ── binding specs: the DECLARED data-path reshaping (explicit, inspectable) ────
# Each maps a Compose expression -> a kit value given `env` (vm + bound loop/let vars). This is
# the part that is NOT mechanical from Compose: the kit reshaped GymWithEquipment -> profile + a
# separate equipment_for(id) query, and activeGym?.id==id -> a per-row isActive flag.
def _gym_list_spec(db):
    from viewmodel.gym_list_view_model import GymListViewModel
    from data.model.gym_type import gym_type_emoji, gym_type_display_name
    vm = GymListViewModel(db)

    def item(env):
        return env["gymWithEquipment"]                    # kit: vm.gyms() yields profiles directly

    def equip(env):
        return vm.equipment_for(item(env).id)

    return {
        "gyms": lambda env: vm.gyms(),
        "gyms.isEmpty()": lambda env: len(vm.gyms()) == 0,
        "activeGym?.id == gymWithEquipment.profile.id": lambda env: item(env).isActive,
        "gym.gymType": lambda env: item(env).gymType,
        "equipmentList.isNotEmpty()": lambda env: len(equip(env)) > 0,
        "onClick != null": lambda env: True,
        "gym.name": lambda env: item(env).name,
        '"${type.emoji} ${type.displayName}"':
            lambda env: gym_type_emoji(env["type"]) + " " + gym_type_display_name(env["type"]),
        '"${equipmentList.size} items"': lambda env: str(len(equip(env))) + " items",
        "equipmentNames": lambda env: ", ".join(e.name for e in equip(env)),
    }


SPECS = {"gym_list": _gym_list_spec}


# ── interpreter: run the IR against real seeded data -> resolved leaves ─────────
# `resolve(expr, env) -> value | _UNRESOLVED` is the binding strategy: either a hand-written spec
# (_spec_resolver) or, for path (c)+, the transpiler itself (_auto_resolver).
_UNRESOLVED = object()


def _static_lit(e):
    m = re.match(r'^"(.*)"$', (e or "").strip())
    return m.group(1) if m else e


def _spec_resolver(spec):
    def r(expr, env):
        f = spec.get(expr)
        return f(env) if f else _UNRESOLVED
    return r


def interpret(ir, resolve, env, out, unresolved):
    for n in ir:
        t = n["t"]
        if t == "bind":                                   # val X = expr -> extend scope (best effort)
            v = resolve(n["expr"], env)
            if v is not _UNRESOLVED:
                env = {**env, n["name"]: v}
        elif t == "box":
            interpret(n["kids"], resolve, env, out, unresolved)
        elif t == "foreach":
            v = resolve(n["src"], env)
            if v is _UNRESOLVED:
                unresolved.append(("src", n["src"])); v = []
            for it in v:
                interpret(n["kids"], resolve, {**env, n["var"]: it}, out, unresolved)
        elif t == "if":
            v = resolve(n["cond"], env)
            if v is _UNRESOLVED:
                unresolved.append(("cond", n["cond"])); v = False
            interpret(n["then"] if v else n["else"], resolve, env, out, unresolved)
        elif t == "let":
            v = resolve(n["subj"], env)
            if v is _UNRESOLVED:
                unresolved.append(("let", n["subj"]))
            elif v is not None:
                interpret(n["kids"], resolve, {**env, n["var"]: v}, out, unresolved)
        elif t == "leaf":
            nt = KL._ntype(n["ctype"])
            if not nt:
                continue
            if n["static"]:
                content = _static_lit(n["expr"])
            elif not n["expr"]:
                continue
            else:
                content = resolve(n["expr"], env)
                if content is _UNRESOLVED:
                    unresolved.append(("leaf", n["expr"])); continue
            if content is not None and str(content) != "":
                out.append((nt, _trunc(content), n["static"]))   # match the ledger's 30-char anchor


def _trunc(s):
    """same anchor normalization the ledgers use, so resolved values compare apples-to-apples."""
    s = " ".join(str(s).split())
    return (s[:30] + "…") if len(s) > 31 else s


class _Router:
    """a hand-built-trace router that carries a selected id (what a detail screen reads to know
    which entity to load), so its trace loads the SAME entity the --auto adapter feeds."""
    def __init__(self, sel): self.selected_id = sel
    def __getattr__(self, n): return lambda *a, **k: None


def _hb_leaves(screen_key, router=None):
    """the hand-built screen's leaves, runtime-traced through the SAME seeded db (resolved)."""
    recs, err = KL.trace(screen_key, router=router)
    roots, _ = KL.build_tree(recs, "content")
    ids = []
    for i, r in enumerate(roots):
        KL.render_tree(r, 1, i, [screen_key], [], ids)
    return [(KL._ntype(t), a) for _, t, a in ids if KL._ntype(t) and a], err


def verify(key):
    path = O.find_one(O.MAIN, f"{''.join(p.capitalize() for p in key.split('_'))}Screen.kt")
    cname, ir = build_ir(path)
    KL._setup_modules()
    db = KL._seeded_db()
    spec = SPECS[key](db)
    leaves, unresolved = [], []
    interpret(ir, _spec_resolver(spec), {}, leaves, unresolved)
    hb, hberr = _hb_leaves(key)

    interp_set = {(nt, c) for nt, c, st in leaves}
    hb_set = set(hb)
    dyn = [(nt, c) for nt, c, st in leaves if not st]      # the RESOLVED dynamic values (the proof)
    dyn_matched = [(nt, c) for nt, c in dyn if (nt, c) in hb_set]
    shared = sorted(interp_set & hb_set)
    interp_only = sorted(interp_set - hb_set)
    hb_only = sorted(hb_set - interp_set)

    L = [f"# PseudoUI runtime verify -- {key}  (IR interpreted vs hand-built, same seeded data)", "",
         f"Interpreted the generated control-flow IR against the app's seeded InMemoryDb and",
         f"compared the RESOLVED leaves to the hand-built screen's runtime trace.", "",
         f"## dynamic values resolved by the interpreter ({len(dyn_matched)}/{len(dyn)} also in hand-built)",
         *[f"  {'OK ' if (nt,c) in hb_set else 'MISS'}  {nt}: {c!r}" for nt, c, st in leaves if not st],
         "", f"## leaf agreement",
         f"- shared (type+content):  {len(shared)}",
         f"- interpreted-only:       {len(interp_only)}   (Compose representation, e.g. 'Active' icon-chip)",
         *[f"    INT {nt}: {c!r}" for nt, c in interp_only],
         f"- hand-built-only:        {len(hb_only)}   (kit glyphs/helpers, e.g. '✓ Active', '←', '+')",
         *[f"    HB  {nt}: {c!r}" for nt, c in hb_only],
         "", f"## unresolved IR exprs (would need a binding-spec entry): {len(unresolved)}",
         *[f"    {kind}: {e!r}" for kind, e in unresolved],
         *( [f"\n(hand-built trace partial: {hberr})"] if hberr else [] ), ""]
    os.makedirs(OUT, exist_ok=True)
    open(os.path.join(OUT, f"{key}.run.md"), "w").write("\n".join(L))
    print(f"  {key}: {len(dyn_matched)}/{len(dyn)} resolved dynamic values match hand-built; "
          f"leaf shared {len(shared)}, interp-only {len(interp_only)}, hb-only {len(hb_only)}, "
          f"unresolved {len(unresolved)}")
    return dyn_matched, dyn, shared


# ── (c) the 1:1 path: run the IR against the TRANSPILED viewmodel ──────────────
# Proves the thesis: when the screen binds to the transpiled (1:1-with-Kotlin) viewmodel + entities
# instead of a hand-reshaped one, the binding spec collapses to the KOTLIN expressions themselves
# (mechanical Kt->Py syntax). The only non-1:1 parts are a FIXED reactive shim (Flow/stateIn/
# coroutine -> pull) and a Room-DAO -> InMemoryDb adapter (a framework boundary, ported once).
def _reactive_ns():
    """the fixed shim the transpiled VM runs against: kotlin_rt (stdlib: emptyList/emptySet/...) +
    a synchronous coroutine/Flow layer (stateIn/launch/MutableStateFlow -> pull). FIXED, reused by
    every screen -- this is the seam that does NOT grow per screen."""
    import runtime.kotlin_rt as rt

    def _notify_recompose():                             # MutableStateFlow write -> request a repaint
        try:                                             # (no-op in the pure sandbox; live under --app)
            from reactive import invalidate as _inv
            _inv()
        except Exception:                                # noqa: BLE001 -- no recompose host
            pass

    class _FlowOps:
        # pull-model Flow operators: transform the LATEST emission, re-read on access (cold Flow)
        def map(self, f): return _Flow(lambda: f(self._read()))
        def mapLatest(self, f): return _Flow(lambda: f(self._read()))
        def filter(self, p):
            def q():
                v = self._read()
                return v if p(v) else None
            return _Flow(q)
        def flatMapLatest(self, f):
            def q():
                inner = f(self._read())
                return inner._read() if hasattr(inner, "_read") else inner
            return _Flow(q)
        def onEach(self, f):
            def q():
                v = self._read(); f(v); return v
            return _Flow(q)
        def onStart(self, *a): return self
        def distinctUntilChanged(self, *a): return self
        def catch(self, *a): return self
        def flowOn(self, *a): return self
        def debounce(self, *a): return self
        def sample(self, *a): return self
        def take(self, *a): return self
        def drop(self, *a): return self
        def collect(self, f):
            v = self._read()
            if v is not None: f(v)
        def collectLatest(self, f): self.collect(f)

    class _StateFlow(_FlowOps):
        # MutableStateFlow -> State: writing `.value` invalidates the recompose frame, so UI-FLAG
        # flows (dialog-open, search query) repaint like Compose snapshot state. Reads stay plain.
        # Doubles as MutableSharedFlow: `collect` registers a handler, `emit` notifies them
        # synchronously -- the pull analog of a LaunchedEffect collecting a nav event.
        def __init__(self, v=None): self._value = v; self._collectors = []
        def _read(self): return self._value
        @property
        def value(self): return self._value
        @value.setter
        def value(self, v):
            changed = self._value != v
            self._value = v
            if changed: _notify_recompose()
        def update(self, f): self.value = f(self._value)
        def stateIn(self, *a): return self
        def asStateFlow(self): return self
        def asSharedFlow(self): return self
        def collectAsStateWithLifecycle(self, *a): return self._value  # Compose `by` delegate -> value
        def collectAsState(self, *a): return self._value
        def first(self): return self._value
        def collect(self, h): self._collectors.append(h)               # SharedFlow: register
        def emit(self, *a):                                            # SharedFlow event -> notify
            for h in list(self._collectors): h(*a)

    class _Flow(_FlowOps):
        # `v` may be a value OR a thunk (re-query function). A Kotlin Flow re-emits on every db
        # change; the pull analog is to re-read on each access. So `.value` calls the thunk fresh,
        # and stateIn returns the SAME lazy flow (not a frozen snapshot).
        def __init__(self, v): self._v = v
        def _read(self): return self._v() if callable(self._v) else self._v
        def _val(self): return self._read()
        def stateIn(self, *a): return self
        def collectAsStateWithLifecycle(self, *a): return self._read()
        def collectAsState(self, *a): return self._read()
        def first(self): return self._read()
        @property
        def value(self): return self._read()

    class _Scope:
        def launch(self, f):
            try:
                return f()
            except Exception:                            # noqa: BLE001 -- best-effort init side effects
                return None

    class _Started:
        @staticmethod
        def WhileSubscribed(*a): return None

    def combine(*args):                                  # combine(flow1..n, transform) -> derived Flow
        *flows, fn = args
        try:
            return _Flow(fn(*[getattr(f, "value", f) for f in flows]))
        except Exception:                                # noqa: BLE001 -- transform gap -> empty
            return _Flow(None)

    class _Permissive:                                   # Screen.X.ARG_*, unused repos, etc.
        def __getattr__(self, n): return _Permissive()
        def __getitem__(self, k): return _Permissive()
        def __call__(self, *a, **k): return _Permissive()

    def flowOf(*xs): return _Flow(lambda: xs[-1] if xs else None)
    def emptyFlow(): return _Flow(lambda: None)

    ns = {k: getattr(rt, k) for k in dir(rt) if not k.startswith("_")}
    ns.update({"viewModelScope": _Scope(), "SharingStarted": _Started,
               "MutableStateFlow": _StateFlow, "MutableSharedFlow": _StateFlow,
               "KtList": rt.KtList, "_Flow": _Flow, "combine": combine,
               "flowOf": flowOf, "emptyFlow": emptyFlow, "Unit": None,
               "Screen": _Permissive(), "checkNotNull": (lambda x, *a: x),
               "_Permissive": _Permissive})
    return ns


def _load_transpiled(files):
    """transpile each .kt and exec into ONE namespace (so the classes see each other + the shim)."""
    from transpiler import KtToPy
    ns = _reactive_ns()
    for f in files:
        p = O.find_one(O.MAIN, f)
        py = KtToPy().transpile(open(p, "rb").read())
        exec(compile(py, f, "exec"), ns)                 # noqa: S102 -- transpiled, trusted
    return ns


# ── general enum lift: kit stores enums as ints; the Kotlin code calls x.displayName() ─────────
# Driven by the Kotlin ENTITY's field types -- no per-screen hand-lifting. A field declared as a
# Kotlin enum (or List<enum>) is lifted from the kit int -> the transpiled enum (EnumCls.entries[i]),
# which carries .displayName()/.emoji/etc. exactly like Kotlin.
_ENUM_REG, _ENUM_FIELDS = {}, {}


def _is_enum_type(name):
    p = O.find_one(O.MAIN, f"{name}.kt")
    try:
        return bool(p) and f"enum class {name}" in open(p).read()
    except Exception:                                    # noqa: BLE001
        return False


def _enum_class(name):
    if name not in _ENUM_REG:
        import runtime.kotlin_rt as rt
        from transpiler import KtToPy
        ns = {k: getattr(rt, k) for k in dir(rt) if not k.startswith("_")}
        try:
            exec(compile(KtToPy().transpile(open(O.find_one(O.MAIN, f"{name}.kt"), "rb").read()),
                         name, "exec"), ns)              # noqa: S102 -- transpiled enum
            _ENUM_REG[name] = ns.get(name)
        except Exception:                                # noqa: BLE001
            _ENUM_REG[name] = None
    return _ENUM_REG[name]


def _enum_field_map(entity_name):
    """{field -> (enum_name, is_list)} for the Kotlin entity's enum-typed constructor fields."""
    if entity_name not in _ENUM_FIELDS:
        p, m = O.find_one(O.MAIN, f"{entity_name}.kt"), {}
        if p:
            for fname, ftype in re.findall(r"val\s+(\w+):\s*(List<\w+>|\w+)\??", open(p).read()):
                base = re.sub(r"List<(\w+)>", r"\1", ftype)
                if _is_enum_type(base):
                    m[fname] = (base, ftype.startswith("List<"))
        _ENUM_FIELDS[entity_name] = m
    return _ENUM_FIELDS[entity_name]


class _LiftProxy:
    """wraps a kit entity, lifting its enum fields (int -> transpiled enum) on access."""
    def __init__(self, obj, fmap): self.__dict__["_o"], self.__dict__["_f"] = obj, fmap

    def __getattr__(self, n):
        v = getattr(self._o, n)
        ef = self._f.get(n)
        if ef and (cls := _enum_class(ef[0])) is not None:
            import runtime.kotlin_rt as rt
            try:
                if ef[1]:
                    return rt.KtList(cls.entries[int(i)] for i in v)
                if v is not None:
                    return cls.entries[int(v)]
            except Exception:                            # noqa: BLE001 -- not int-convertible; pass through
                pass
        return v


def _lift(obj, entity_name):
    fmap = _enum_field_map(entity_name)
    return _LiftProxy(obj, fmap) if (fmap and obj is not None) else obj


def _gym_repo_adapter(ns, db):
    """Room-DAO boundary, ported to the kit InMemoryDb: yields the transpiled Kotlin shapes
    (GymWithEquipment bundling profile+equipment; gymType int -> GymType enum)."""
    from domain.gym_service import GymService
    from data.repository.gym_equipment_repository import GymEquipmentRepository
    import runtime.kotlin_rt as rt                        # KtList so .joinToString/.isNotEmpty work
    GWE, GProf, GT, Flow = ns["GymWithEquipment"], ns["GymProfileEntity"], ns["GymType"], ns["_Flow"]

    def lift(g):
        gt = GT.entries[int(g.gymType)] if g.gymType is not None else None
        return GProf(g.id, g.name, g.isActive, gt, g.createdAt, g.updatedAt)

    class _Repo:                                          # Flows wrap THUNKS -> re-query each read
        def getAllWithEquipment(self):
            def q():
                eq = GymEquipmentRepository(db)
                return rt.KtList(GWE(lift(g), rt.KtList(eq.get_by_gym(g.id)))
                                 for g in GymService(db).get_all())
            return Flow(q)

        def getActive(self):
            def q():
                act = [g for g in GymService(db).get_all() if g.isActive]
                return lift(act[0]) if act else None
            return Flow(q)

        def setActive(self, gid): GymService(db).set_active(gid)
        def deleteGym(self, gid): GymService(db).delete_gym(gid)
    return (_Repo(),)                                     # GymListViewModel(repo)


def _paths_repo_adapter(ns, db):
    """A SECOND screen's boundary -- notably THINNER than gym_list's: PathEntity.name is a string,
    so there is no enum lift and no bundling. Just expose the kit's active paths as a Flow."""
    from domain.path_service import PathService
    import runtime.kotlin_rt as rt
    Flow = ns["_Flow"]

    class _Repo:
        @property
        def activePaths(self):
            return Flow(rt.KtList(PathService(db).active_paths()))

        def seedIfNeeded(self): pass
    return (_Repo(),)                                     # PathsViewModel(repository)


def _exercise_detail_adapter(ns, db):
    """A DYNAMIC second screen with a SIMPLE VM (single-entity derived flow, like gym_list). Reads
    the seeded eSquat exercise; most content is bool->string conditionals. The enum displayName()
    line (movement/equipment/muscle, stored as ints in the kit) is the documented gap."""
    from data.repository.exercise_repository import ExerciseRepository
    Flow, Perm = ns["_Flow"], ns["_Permissive"]
    repo = ExerciseRepository(db)

    def _ex():                                           # thunk: re-lift on each read (Flow re-emit)
        return _lift(repo.get_by_id("eSquat"), "ExerciseEntity")

    class _Repo:
        def getById(self, eid): return Flow(_ex)         # lift enum fields (movement/equipment/muscle)
        def delete(self, ex): repo.delete(ex)            # the mutating menu actions
        def setExcluded(self, ex, v): pass               # (sandbox render proof -- no persistence)
        def toggleFavorite(self, ex): pass
        def duplicate(self, ex): return "dup-1"
        def bestSubstitute(self, eid): return None

    class _Prog:                                         # countExerciseOccurrences>0 -> excludePrompt
        def countExerciseOccurrences(self, eid): return 1

    class _SSH:
        def __getitem__(self, k): return "eSquat"
    # ctor: (savedStateHandle, repository: ExerciseRepository, programRepository)
    return (_SSH(), _Repo(), _Prog())


def _exercise_picker_adapter(ns, db):
    """A DYNAMIC second screen over real data (185 seeded exercises). The VM is a `combine` -- the
    adapter just feeds exerciseDao.getAll(); the filter flows default (blank query / no filter), so
    the transpiled transform yields the non-excluded exercises, sorted."""
    from data.repository.exercise_repository import ExerciseRepository
    import runtime.kotlin_rt as rt
    Flow, Perm = ns["_Flow"], ns["_Permissive"]

    class _Dao:
        def getAll(self):
            return Flow(rt.KtList(ExerciseRepository(db).get_all()))
    # ctor: (savedStateHandle, repository: ProgramRepository [unused in render], exerciseDao)
    return (Perm(), Perm(), _Dao())


# Per-screen config = the honest "what each screen needs" surface for --auto. The IR + binding
# machinery is screen-agnostic; this captures only the transpiled files + the DAO->kit adapter.
SCREEN_CFG = {
    "gym_list": {"files": ["GymType.kt", "GymProfileEntity.kt", "GymListViewModel.kt"],
                 "vm": "GymListViewModel", "adapter": _gym_repo_adapter},
    "paths": {"files": ["PathsViewModel.kt"],
              "vm": "PathsViewModel", "adapter": _paths_repo_adapter},
    "exercise_detail": {"files": ["ExerciseDetailViewModel.kt"], "sel": "eSquat",
                        "vm": "ExerciseDetailViewModel", "adapter": _exercise_detail_adapter},
    "exercise_picker": {"files": ["ExercisePickerViewModel.kt"],
                        "vm": "ExercisePickerViewModel", "adapter": _exercise_picker_adapter},
}


def _gym_list_spec_1to1(vm):
    """The 1:1 binding spec: every value is the KOTLIN expression, syntactically Kt->Py'd against
    the transpiled shapes. NO reshaping -- contrast _gym_list_spec (which reshaped). `gym` is the
    Kotlin `val gym = gymWithEquipment.profile`; `gyms`/`activeGym` are collectAsState() of the
    StateFlows. Each comment is the verbatim Kotlin."""
    def gw(env): return env["gymWithEquipment"]
    return {
        "gyms": lambda env: vm.gyms.value,                                    # viewModel.gyms
        "gyms.isEmpty()": lambda env: len(vm.gyms.value) == 0,                # gyms.isEmpty()
        "activeGym?.id == gymWithEquipment.profile.id":                       # activeGym?.id == ...
            lambda env: vm.activeGym.value is not None and vm.activeGym.value.id == gw(env).profile.id,
        "gym.gymType": lambda env: gw(env).profile.gymType,                   # gym.gymType
        "equipmentList.isNotEmpty()": lambda env: len(gw(env).equipment) > 0,  # equipmentList.isNotEmpty()
        "gym.name": lambda env: gw(env).profile.name,                        # gym.name
        '"${type.emoji} ${type.displayName}"':                               # "${type.emoji} ${type.displayName}"
            lambda env: env["type"].emoji + " " + env["type"].displayName,
        '"${equipmentList.size} items"':                                     # "${equipmentList.size} items"
            lambda env: str(len(gw(env).equipment)) + " items",
        "equipmentNames": lambda env: ", ".join(e.name for e in gw(env).equipment),  # joinToString(", "){it.name}
        "onClick != null": lambda env: True,
    }


def verify_1to1(key="gym_list"):
    path = O.find_one(O.MAIN, f"{''.join(p.capitalize() for p in key.split('_'))}Screen.kt")
    cname, ir = build_ir(path)
    KL._setup_modules()
    db = KL._seeded_db()
    ns = _load_transpiled(["GymType.kt", "GymProfileEntity.kt", "GymListViewModel.kt"])
    vm = ns["GymListViewModel"](*_gym_repo_adapter(ns, db))   # the TRANSPILED VM, real data
    spec = _gym_list_spec_1to1(vm)
    leaves, unresolved = [], []
    interpret(ir, _spec_resolver(spec), {}, leaves, unresolved)
    hb, hberr = _hb_leaves(key)
    interp_set = {(nt, c) for nt, c, st in leaves}
    hb_set = set(hb)
    dyn = [(nt, c) for nt, c, st in leaves if not st]
    dyn_matched = [(nt, c) for nt, c in dyn if (nt, c) in hb_set]
    reshaping = sum(1 for v in _gym_list_spec(db).values() if v)  # entries in the OLD reshaping spec

    L = [f"# PseudoUI 1:1 verify -- {key}: IR bound to the TRANSPILED viewmodel", "",
         "The screen's IR (mechanical) interpreted against the TRANSPILED GymListViewModel + entities",
         "+ GymType (1:1 with Kotlin), over the seeded data. The binding spec is now the KOTLIN",
         "expressions themselves (mechanical Kt->Py), not reshaping judgments.", "",
         f"## result",
         f"- resolved dynamic values matching hand-built: {len(dyn_matched)}/{len(dyn)}",
         *[f"    {'OK ' if (nt,c) in hb_set else 'MISS'}  {nt}: {c!r}" for nt, c, st in leaves if not st],
         f"- unresolved IR exprs: {len(unresolved)}",
         "", "## the collapse (the point of path c)",
         f"- reshaped spec (kit VM):  {reshaping} entries that RE-MAP Compose->kit",
         f"    e.g. activeGym?.id==id  ->  item.isActive   (per-row flag)",
         f"         gymWithEquipment.equipment  ->  vm.equipment_for(id)   (separate query)",
         f"- 1:1 spec (transpiled VM): the SAME {len(_gym_list_spec_1to1(vm))} expressions, but each is",
         f"    the Kotlin source syntactically Kt->Py'd (identity of shape):",
         f"         activeGym?.id==id  ->  vm.activeGym.value.id == gw.profile.id",
         f"         gymWithEquipment.equipment  ->  gymWithEquipment.equipment   (identity)",
         "", "## the only non-1:1 seams (fixed, not per-screen)",
         "- reactive shim: Flow/stateIn/viewModelScope/launch -> synchronous pull (~8 lines).",
         "- Room DAO -> InMemoryDb adapter: getAllWithEquipment bundles profile+equipment and",
         "  lifts gymType int -> GymType enum (the storage boundary the kit reshaped away).",
         *( [f"\n(hand-built trace partial: {hberr})"] if hberr else [] ), ""]
    os.makedirs(OUT, exist_ok=True)
    open(os.path.join(OUT, f"{key}.1to1.md"), "w").write("\n".join(L))
    print(f"  {key} (1:1 transpiled VM): {len(dyn_matched)}/{len(dyn)} dynamic values match hand-built, "
          f"unresolved {len(unresolved)}; binding is now Kotlin-shaped (identity), not reshaping")
    return dyn_matched, dyn


# ── (c)+ AUTO binding: the spec is the TRANSPILER, not hand-written ────────────
# No per-screen lambdas. Each binding expression in the IR (val RHS, if cond, foreach src, ?.let
# subject, dynamic leaf) is transpiled Kt->Py and eval'd against an env of kotlin_rt (the stdlib
# runtime) + the transpiled `viewModel` + the scope's resolved `val`s. This is the repeatable crank.
_TP_EXPR_CACHE = {}


def _resolve_expr(expr, env):
    if expr not in _TP_EXPR_CACHE:
        from transpiler import KtToPy
        try:
            _TP_EXPR_CACHE[expr] = KtToPy().transpile(f"val __r = {expr}".encode())
        except Exception:                                # noqa: BLE001 -- transpile gap -> unresolved
            _TP_EXPR_CACHE[expr] = None
    py = _TP_EXPR_CACHE[expr]
    if not py:
        return _UNRESOLVED
    g = dict(env)
    try:
        exec(compile(py, "<expr>", "exec"), g)           # noqa: S102 -- transpiled, trusted
    except Exception:                                    # noqa: BLE001 -- runtime gap -> unresolved
        return _UNRESOLVED
    return g.get("__r", _UNRESOLVED)


def _auto_env(vm):
    """eval namespace: the Kotlin stdlib runtime (kotlin_rt) + the transpiled viewModel."""
    import runtime.kotlin_rt as rt
    env = {k: getattr(rt, k) for k in dir(rt) if not k.startswith("_")}
    env["viewModel"] = vm
    return env


def verify_auto(key="gym_list"):
    cfg = SCREEN_CFG.get(key)
    if not cfg:
        print(f"  no --auto config for {key!r} (have: {', '.join(SCREEN_CFG)})")
        return None, [], []
    path = O.find_one(O.MAIN, f"{''.join(p.capitalize() for p in key.split('_'))}Screen.kt")
    cname, ir = build_ir(path)
    KL._setup_modules()
    db = KL._seeded_db()
    try:
        ns = _load_transpiled(cfg["files"])
        vm = ns[cfg["vm"]](*cfg["adapter"](ns, db))
    except Exception as e:                               # noqa: BLE001 -- VM transpile/construct gap
        print(f"  {key}: VM did not construct ({type(e).__name__}: {e}) -- transpiler gap, not UI")
        return None, [], []
    leaves, unresolved = [], []
    interpret(ir, _resolve_expr, _auto_env(vm), leaves, unresolved)   # resolver = the TRANSPILER
    hb, hberr = _hb_leaves(key, _Router(cfg["sel"]) if cfg.get("sel") else None)
    interp_set = {(nt, c) for nt, c, st in leaves}
    hb_set = set(hb)
    dyn = [(nt, c) for nt, c, st in leaves if not st]
    dyn_matched = [(nt, c) for nt, c in dyn if (nt, c) in hb_set]
    shared = sorted(interp_set & hb_set)
    interp_only = sorted(interp_set - hb_set)
    hb_only = sorted(hb_set - interp_set)
    samples = sorted(e for e in _TP_EXPR_CACHE if _TP_EXPR_CACHE[e] and not e.startswith('"'))[:8]

    L = [f"# PseudoUI AUTO verify -- {key}: bindings emitted by the TRANSPILER (no hand spec)", "",
         "Every binding expression in the IR was transpiled Kt->Py and eval'd against kotlin_rt +",
         "the transpiled viewModel. There is NO per-screen binding spec -- the transpiler IS the spec.", "",
         f"## leaf agreement vs hand-built (same seeded data)",
         f"- shared (type+content):  {len(shared)}",
         f"- interpreted-only:       {len(interp_only)}   (Compose representation: icon descs etc.)",
         *[f"    INT {nt}: {c!r}" for nt, c in interp_only],
         f"- hand-built-only:        {len(hb_only)}   (kit glyphs/helpers)",
         *[f"    HB  {nt}: {c!r}" for nt, c in hb_only],
         "", f"## dynamic values resolved ({len(dyn_matched)}/{len(dyn)} match hand-built)",
         *[f"    {'OK ' if (nt,c) in hb_set else 'MISS'}  {nt}: {c!r}" for nt, c, st in leaves if not st],
         f"- unresolved IR exprs: {len(unresolved)}",
         *[f"    {kind}: {e!r}" for kind, e in unresolved],
         "", "## sample of the transpiler-emitted bindings (Kotlin -> Python, mechanical)",
         *[f"    {e!r}\n      -> {(_TP_EXPR_CACHE[e] or '').strip()}" for e in samples],
         *( [f"\n(hand-built trace partial: {hberr})"] if hberr else [] ), ""]
    os.makedirs(OUT, exist_ok=True)
    open(os.path.join(OUT, f"{key}.auto.md"), "w").write("\n".join(L))
    print(f"  {key} (AUTO): leaf shared {len(shared)}, interp-only {len(interp_only)}, "
          f"hb-only {len(hb_only)}; dynamic {len(dyn_matched)}/{len(dyn)} match; "
          f"unresolved {len(unresolved)}; NO hand-written spec")
    return dyn_matched, dyn, unresolved


# ── (c)++ EMIT: turn the IR + auto-bindings into a runnable *_screen.py ─────────
# The interpreter PROVES equivalence; this PRODUCES code. It walks the IR and emits a real Python
# build() -- define_* calls wrapped in the screen's actual loops/ifs, with each binding the
# transpiler's Kt->Py output. The result is a generated screen file (the project's deliverable),
# and we run it to confirm it reproduces the verified trace.
_EMIT_CACHE = {}


def _py_expr(kt):
    """transpile a Kotlin expr to a SINGLE-LINE Python expression (RHS), or None if it transpiles
    to a multi-line statement (a Kotlin if/when value) -- those go through _py_stmt instead."""
    if kt not in _EMIT_CACHE:
        from transpiler import KtToPy
        try:
            out = KtToPy().transpile(f"val __r = {kt}".encode()).strip()
        except Exception:                                # noqa: BLE001
            out = None
        _EMIT_CACHE[kt] = (out.split("=", 1)[1].strip()
                           if out and "\n" not in out and out.startswith("__r") else None)
    return _EMIT_CACHE[kt]


def _py_stmt(kt, target):
    """transpiled Python statement(s) assigning `target = <kt>` -- handles the multi-line
    if/when forms. -> list of source lines (indent-0), or None."""
    from transpiler import KtToPy
    try:
        out = KtToPy().transpile(f"val {target} = {kt}".encode()).strip()
    except Exception:                                    # noqa: BLE001
        return None
    return out.splitlines() if out else None


_LEAF_FN = {"text": "define_text", "button": "define_button", "icon": "define_icon",
            "image_zone": "define_image_zone", "spacer_zone": "define_spacer_zone",
            "divider_zone": "define_divider_zone", "input_zone": "define_input_zone"}


def _needed_binds(ir):
    """names of `val`s actually referenced by a rendered binding (cond/src/subj/leaf/other val) --
    so dead styling binds (WflCard's shape/border/colors) are pruned from the generated code."""
    used, binds = [], []

    def walk(nodes):
        for n in nodes:
            t = n["t"]
            if t == "leaf" and n["expr"] and not n["static"]:
                used.append(n["expr"])
            elif t == "bind":
                used.append(n["expr"]); binds.append(n["name"])
            elif t == "if":
                used.append(n["cond"]); walk(n["then"]); walk(n["else"])
            elif t == "foreach":
                used.append(n["src"]); walk(n["kids"])
            elif t == "let":
                used.append(n["subj"]); walk(n["kids"])
            elif t == "box":
                walk(n["kids"])
    walk(ir)
    blob = " ".join(e for e in used if e)
    return {b for b in set(binds) if re.search(rf"\b{re.escape(b)}\b", blob)}


# Per-screen NAV map (the declarative part: which Compose nav-callback -> which app route). The
# route TARGETS live in the app's NavHost, not the screen's Compose, so they are declared here --
# like the data adapter. VM ACTIONS (viewModel.X) are mechanical and need no entry.
NAV_HANDLERS = {
    "gym_list": {
        "subs": {"onNavigateBack": "self._nav_back", "onNavigateToEditor": "self._nav_editor"},
        "methods": [
            "    def _nav_back(self):",
            "        self.router.navigate('you')",
            "    def _nav_editor(self, gymId=None):",
            "        if gymId is None:",
            "            self.router.navigate('gym_create_wizard')",
            "        else:",
            "            self.router.selected_id = gymId",
            "            self.router.navigate('gym_editor')",
        ],
    },
    "exercise_detail": {
        "subs": {"onNavigateBack": "self._nav_back", "onNavigateToEdit": "self._nav_edit"},
        # VM nav SharedFlows -> screen nav callbacks (the LaunchedEffect-collect, declared not parsed)
        "nav_flows": {"navigateBack": "self._nav_back", "navigateToEdit": "self._nav_edit"},
        "methods": [
            "    def _nav_back(self, _=None):",                 # arg: the emitted Unit (ignored)
            "        self.router.navigate('exercises')",
            "    def _nav_edit(self, exerciseId=None):",        # arg: the emitted exercise id
            "        if exerciseId is not None:",
            "            self.router.selected_id = exerciseId",
            "        self.router.navigate('exercise_create')",
        ],
    },
}


def _handler_body(oc, subs):
    """a Kotlin onClick (`{ viewModel.delete(x) }` / `onNavigateBack`) -> a Python expression:
    viewModel -> self.vm, each nav callback -> its declared self._nav_*; a bare ref gets called."""
    body = oc.strip()
    if body.startswith("{") and body.endswith("}"):
        body = body[1:-1].strip()
    py = _py_expr(body) or body
    for k, v in subs.items():
        py = re.sub(rf"\b{re.escape(k)}\b", v, py)
    return py if "(" in body else py + "()"


def emit_py(ir, key):
    """-> Python source of `def build(ui, content, viewModel):` reproducing the screen."""
    lines = ["def _ev(f):", "    try:", "        return f()",
             "    except Exception:", "        return None", "", "",
             "def build(ui, content, viewModel):"]
    ctr = [0]
    needed = _needed_binds(ir)
    subs = {"viewModel": "self.vm", **NAV_HANDLERS.get(key, {}).get("subs", {})}

    def handler(node, zexpr, loopvars, pad):
        oc = node.get("onclick")
        if not oc:
            return
        body = _handler_body(oc, subs)
        if not body:
            return
        m = ctr[0]; ctr[0] += 1
        caps = "".join(f", {v}={v}" for v in loopvars)
        lines.append(f"{pad}def _h{m}(evt{caps}): {body}")
        lines.append(f"{pad}ui.on_click({zexpr}, _h{m})")

    def zid(m, suffix):
        base = f'"{key}_z{m}"'
        return base if suffix == '""' else f'({base} + "_" + {suffix})'

    def assign(kt, target, pad):
        """emit `target = <kt>` -- single-line wrapped in _ev (tolerates unbound params), else the
        transpiled multi-line block (a Kotlin if/when value; references bound vars, so safe)."""
        e = _py_expr(kt)
        if e is not None:
            lines.append(f"{pad}{target} = _ev(lambda: {e})")
            return
        st = _py_stmt(kt, target)
        if st:
            lines.extend(pad + ln for ln in st)
        else:
            lines.append(f"{pad}{target} = None")

    def value(kt, m, pad):
        """-> a Python expression for kt (inline if single-line; else a temp assigned just above)."""
        e = _py_expr(kt)
        if e is not None:
            return f"_ev(lambda: {e})"
        assign(kt, f"_t{m}", pad)
        return f"_t{m}"

    def emit(nodes, sup, suffix, ind, loopvars=()):
        pad = "    " * ind
        wrote = False
        for n in nodes:
            t = n["t"]
            if t == "bind":
                if n["name"] not in needed:              # prune dead styling binds
                    continue
                assign(n["expr"], n["name"], pad); wrote = True
            elif t == "box":
                m = ctr[0]; ctr[0] += 1
                lines.append(f"{pad}_id{m} = {zid(m, suffix)}")
                lines.append(f'{pad}ui.define_box(_id{m}, {sup}, "{n["orient"]}")')
                handler(n, f"_id{m}", loopvars, pad)
                emit(n["kids"], f"_id{m}", suffix, ind, loopvars); wrote = True
            elif t == "foreach":
                m = ctr[0]; ctr[0] += 1
                src = value(n["src"], m, pad)
                nsuf = f"str(_i{m})" if suffix == '""' else f'({suffix} + "_" + str(_i{m}))'
                lines.append(f"{pad}for _i{m}, {n['var']} in enumerate({src} or []):")
                emit(n["kids"], sup, nsuf, ind + 1, loopvars + (n["var"],)) \
                    or lines.append(f"{pad}    pass")
                wrote = True
            elif t == "if":
                m = ctr[0]; ctr[0] += 1
                lines.append(f"{pad}if {value(n['cond'], m, pad)}:")   # value() wraps in _ev itself
                emit(n["then"], sup, suffix, ind + 1, loopvars) or lines.append(f"{pad}    pass")
                if n["else"]:
                    lines.append(f"{pad}else:")
                    emit(n["else"], sup, suffix, ind + 1, loopvars) or lines.append(f"{pad}    pass")
                wrote = True
            elif t == "let":
                assign(n["subj"], n["var"], pad)
                lines.append(f"{pad}if {n['var']} is not None:")
                emit(n["kids"], sup, suffix, ind + 1, loopvars + (n["var"],)) \
                    or lines.append(f"{pad}    pass")
                wrote = True
            elif t == "leaf":
                fn = _LEAF_FN.get(n["kind"])
                if not fn:
                    continue
                spacing = n["kind"] in ("spacer_zone", "divider_zone")
                if not spacing and not n["static"] and not n["expr"]:
                    continue                              # decorative / no content -> skip (as interpreter)
                m = ctr[0]; ctr[0] += 1
                z = zid(m, suffix)
                if spacing:
                    lines.append(f"{pad}ui.{fn}({z}, {sup})")
                else:
                    val = repr(_static_lit(n["expr"])) if n["static"] else value(n["expr"], m, pad)
                    arg = f'"", {val}' if n["kind"] == "input_zone" else val
                    lines.append(f"{pad}ui.{fn}({z}, {sup}, {arg})")
                    handler(n, z, loopvars, pad)
                wrote = True
        return wrote

    if not emit(ir, "content", '""', 1):    # the `content` param/var (the screen's content zone)
        lines.append("    pass")
    return "\n".join(lines)


# ── (c) app migration: the generated screen as a drop-in app Screen class ──────
# The app router mounts `Screen(db).build(ui, content_zone_id, router)`. emit_app_screen wraps the
# generated build() in exactly that contract, backed by the TRANSPILED viewmodel -- so it can
# replace the hand-built screen in the live app. verify_app_mount mounts it the way the router does
# and confirms it produces the same tree as the hand-built screen.
def build_transpiled_vm(key, db):
    """the transpiled (1:1-with-Kotlin) viewmodel for a screen, wired to the kit db via its adapter
    + the fixed reactive/stdlib shim -- the '1:1 backend' a generated app screen runs on."""
    cfg = SCREEN_CFG[key]
    ns = _load_transpiled(cfg["files"])
    return ns[cfg["vm"]](*cfg["adapter"](ns, db))


def emit_app_screen(ir, key, class_name):
    """the generated build() wrapped as an app Screen class (db ctor + router-shaped build),
    tracking owned_ids so the router can tear the screen's zones down on navigate-away."""
    src = emit_py(ir, key)
    lines = src.splitlines()
    bi = next(i for i, l in enumerate(lines) if l.startswith("def build("))
    head = lines[:bi]                                    # the _ev helper
    body = lines[bi + 1:]                                # build() body (indented 4)
    out = head + [
        "", "class _Track:                             # records every define_*'s zone id -> owned_ids",
        "    def __init__(self, ui, owned): self._ui, self._owned = ui, owned",
        "    def __getattr__(self, n):",
        "        fn = getattr(self._ui, n)",
        "        if n.startswith('define_'):",
        "            def w(zid, *a, **k):",
        "                self._owned.append(zid)",
        "                return fn(zid, *a, **k)",
        "            return w",
        "        return fn",
        "", "", f"class {class_name}:",
        "    def __init__(self, db):",
        "        self.db = db",
        f'        self.vm = build_transpiled_vm({key!r}, db)',
        "        self.owned_ids = []",
        "",
        "    def screen_id(self):",
        f"        return {key!r}",
        ""] + NAV_HANDLERS.get(key, {}).get("methods", []) + [
        "",
        "    def build(self, ui, content_zone_id, router):",
        "        self.owned_ids = []",
        "        ui = _Track(ui, self.owned_ids)",
        "        self.router = router",
        "        viewModel = self.vm",
        ] + [f"        self.vm.{flow}.collect({cb})    # LaunchedEffect collect -> nav callback"
             for flow, cb in NAV_HANDLERS.get(key, {}).get("nav_flows", {}).items()] + [
        "        content = content_zone_id"]
    out += ["    " + l for l in body]                    # re-indent body into the method
    return "\n".join(out) + "\n"


def _leaves_of(recs, key):
    roots, _ = KL.build_tree(recs, "content")
    ids = []
    for i, r in enumerate(roots):
        KL.render_tree(r, 1, i, [key], [], ids)
    return {(KL._ntype(t), a) for _, t, a in ids if KL._ntype(t) and a}


def verify_app_mount(key="gym_list"):
    cfg = SCREEN_CFG.get(key)
    if not cfg:
        print(f"  no config for {key!r}")
        return
    cls_name = "".join(p.capitalize() for p in key.split("_")) + "ScreenGen"
    path = O.find_one(O.MAIN, f"{''.join(p.capitalize() for p in key.split('_'))}Screen.kt")
    cname, ir = build_ir(path)
    src = emit_app_screen(ir, key, cls_name)
    os.makedirs(OUT, exist_ok=True)
    open(os.path.join(OUT, f"{key}_screen_gen.py"), "w").write(src)

    KL._setup_modules()
    db = KL._seeded_db()
    g = {"build_transpiled_vm": build_transpiled_vm}
    exec(compile(src, f"{key}_screen_gen.py", "exec"), g)   # noqa: S102 -- generated, trusted
    GenCls = g[cls_name]

    router = _Router(cfg.get("sel")) if cfg.get("sel") else KL._Any()
    gen = GenCls(db)                                     # mounted EXACTLY as AppRouter does
    rec = KL._RecUI()
    err = None
    try:
        gen.build(rec, "content", router)
    except Exception as e:                               # noqa: BLE001
        err = f"{type(e).__name__}: {e}"
    gen_leaves = _leaves_of(rec.recs, key)
    hb_leaves = set(_hb_leaves(key, _Router(cfg.get("sel")) if cfg.get("sel") else None)[0])
    shared = sorted(gen_leaves & hb_leaves)
    print(f"  {key}: generated app Screen class ({cls_name}, db-ctor + router build) mounted -> "
          f"{len(rec.recs)} define_* calls; vs hand-built leaf shared {len(shared)}, "
          f"gen-only {len(gen_leaves - hb_leaves)}, hb-only {len(hb_leaves - gen_leaves)}"
          + (f"  (build err: {err})" if err else ""))


def verify_emitted(key="gym_list"):
    cfg = SCREEN_CFG.get(key)
    if not cfg:
        print(f"  no config for {key!r}")
        return
    path = O.find_one(O.MAIN, f"{''.join(p.capitalize() for p in key.split('_'))}Screen.kt")
    cname, ir = build_ir(path)
    src = emit_py(ir, key)
    os.makedirs(OUT, exist_ok=True)
    open(os.path.join(OUT, f"{key}_screen.gen.py"), "w").write(src + "\n")

    KL._setup_modules()
    db = KL._seeded_db()
    ns = _load_transpiled(cfg["files"])
    vm = ns[cfg["vm"]](*cfg["adapter"](ns, db))
    import runtime.kotlin_rt as rt
    g = {k: getattr(rt, k) for k in dir(rt) if not k.startswith("_")}
    exec(compile(src, f"{key}_screen.gen.py", "exec"), g)   # noqa: S102 -- generated, trusted
    rec = KL._RecUI()
    err = None
    try:
        g["build"](rec, "content", vm)
    except Exception as e:                               # noqa: BLE001
        err = f"{type(e).__name__}: {e}"
    roots, _ = KL.build_tree(rec.recs, "content")
    ids = []
    for i, r in enumerate(roots):
        KL.render_tree(r, 1, i, [key], [], ids)
    gen = {(KL._ntype(t), a) for _, t, a in ids if KL._ntype(t) and a}
    hb, _hberr = _hb_leaves(key)
    hb_set = set(hb)
    shared = sorted(gen & hb_set)
    print(f"  {key}: emitted {key}_screen.gen.py ({len(src.splitlines())} lines), ran -> "
          f"{len(rec.recs)} define_* calls; leaf shared {len(shared)}, gen-only {len(gen - hb_set)}, "
          f"hb-only {len(hb_set - gen)}" + (f"  (build err: {err})" if err else ""))


def main():
    args = [a for a in sys.argv[1:] if not a.startswith("-")]
    key = args[0] if args else "gym_list"
    if "--emit" in sys.argv:
        print(f"PseudoUI EMIT runnable screen -> ledger_sample/{key}_screen.gen.py")
        verify_emitted(key)
        return
    if "--app" in sys.argv:
        print(f"PseudoUI APP-mount generated Screen class -> ledger_sample/{key}_screen_gen.py")
        verify_app_mount(key)
        return
    if "--auto" in sys.argv:
        print(f"PseudoUI AUTO verify (transpiler-emitted bindings) -> ledger_sample/{key}.auto.md")
        verify_auto(key)
        return
    if "--1to1" in sys.argv:
        print(f"PseudoUI 1:1 verify (transpiled VM) -> ledger_sample/{key}.1to1.md")
        verify_1to1(key)
        return
    compose = G._compose_for_key(key) if hasattr(G, "_compose_for_key") else \
        "".join(p.capitalize() for p in key.split("_")) + "Screen"
    path = O.find_one(O.MAIN, f"{compose}.kt")
    if "--ir" in sys.argv:
        cname, ir = build_ir(path)
        lines = [f"# PseudoUI IR -- {key} (from {cname})", ""]
        _dump(ir, 0, lines)
        print("\n".join(lines))
        os.makedirs(OUT, exist_ok=True)
        open(os.path.join(OUT, f"{key}.ir.md"), "w").write("\n".join(lines))
        return
    if key not in SPECS:
        print(f"  no binding spec for {key!r} yet (have: {', '.join(SPECS)}); use --ir to dump the IR")
        return
    print(f"PseudoUI runtime verify -> ledger_sample/{key}.run.md")
    verify(key)


if __name__ == "__main__":
    main()
