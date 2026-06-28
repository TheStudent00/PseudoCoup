"""pseudoui_run.py -- PseudoUI behaviour layer: control-flow IR + interpreter + runtime verify.

The structural generator (pseudoui.py) flattens a screen to its widgets -- it descends BOTH
branches of every `if`, renders a list's template ONCE, and leaves bindings like `gym.name`
unresolved. That proves STRUCTURE. This proves BEHAVIOUR: it lifts the Compose control flow
(`items(list){}`, `if/else`, `expr?.let{}`) into a small IR, then INTERPRETS that IR against the
app's real seeded data -- looping real rows, taking the branch the real data selects, resolving
each binding to its real value -- and emits the same kind of `define_*` trace the hand-built
screen produces. Comparing the two RESOLVED traces is the dynamic/functional-equivalence check.

The honest seam (discovered from the code -- see DevComms): the kit deliberately RESHAPED Compose's
data path (GymWithEquipment -> profile + a separate equipment_for(id) query; activeGym?.id==id ->
a per-row isActive flag; setActive(gym) -> set_active(gym.id)). So behaviour is NOT purely
mechanical from Compose -- it needs a per-screen BINDING SPEC that declares those reshapings. The
IR (control-flow skeleton) is generated; the binding spec (data-path) is declared, explicit, and
inspectable -- not buried in hand-code. This file proves the loop closes on gym_list.

Usage:  python3 pseudoui_run.py gym_list --ir       # dump the generated IR
        python3 pseudoui_run.py gym_list             # interpret vs hand-built (runtime verify)
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


def _parse_let(call):
    nav = next((k for k in call.children if k.type == "navigation_expression"), None)
    subj = re.split(r"\?\.let|\.let", nav.text.decode(), maxsplit=1)[0].strip() if nav else None
    lam = next((k for k in call.children if k.type in ("annotated_lambda", "lambda_literal")), None)
    return subj, _lambda_param(lam), (_stmts(lam) if lam else [])


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
    if stmt.type != "call_expression":
        return                                            # property_declaration etc. -> binding spec
    name = UL._name(stmt)
    if name == "items":                                   # LazyList items(src){ var -> body }
        src = UL._first_positional(stmt)
        base, lam = UL._base_and_lambda(stmt)
        var = _lambda_param(lam)
        body = []
        for s in _stmts(lam):
            _ir_node(s, subst, stack, defs, body)
        out.append({"t": "foreach", "src": _sub(src, subst), "var": var, "kids": body})
        return
    if _is_let(stmt):                                     # expr?.let { var -> body }
        subj, var, body_stmts = _parse_let(stmt)
        body = []
        for s in body_stmts:
            _ir_node(s, subst, stack, defs, body)
        out.append({"t": "let", "subj": _sub(subj, subst), "var": var, "kids": body})
        return
    if not name or not name[0].isupper():                 # lowercase call = handler/helper, not UI
        return
    _ir_widget(stmt, name, subst, stack, defs, out)


def _sub(expr, subst):
    if not expr:
        return expr
    e = expr.strip()
    return subst.get(e, expr)


def _ir_widget(call, name, subst, stack, defs, out):
    if name in G.BUTTONS:
        kind, ct, anchor, st, expr = _btn(call, subst)
        out.append({"t": "leaf", "kind": kind, "ctype": ct, "expr": expr, "static": st})
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
    out.append({"t": "box", "orient": orient, "name": name, "kids": kids})


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


def build_ir(compose_path):
    comps = UL.composables(compose_path)
    cname, _ = G._entry(comps)
    defs = _comp_bodies()
    params, body = defs[cname]
    out = []
    for s in _stmts(body):
        _ir_node(s, {}, [cname], defs, out)
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
def _resolve_leaf(n, spec, env):
    e = n["expr"]
    if e is None:
        return None
    if n["static"]:
        m = re.match(r'^"(.*)"$', e.strip())
        return m.group(1) if m else e
    f = spec.get(e)
    return f(env) if f else None                          # unresolved binding -> drop (reported)


def interpret(ir, spec, env, out, unresolved):
    for n in ir:
        t = n["t"]
        if t == "box":
            interpret(n["kids"], spec, env, out, unresolved)
        elif t == "foreach":
            src = spec.get(n["src"])
            for it in (src(env) if src else []):
                e2 = dict(env); e2[n["var"]] = it
                interpret(n["kids"], spec, e2, out, unresolved)
        elif t == "if":
            f = spec.get(n["cond"])
            if f is None:
                unresolved.append(("cond", n["cond"]))
            branch = n["then"] if (f and f(env)) else n["else"]
            interpret(branch, spec, env, out, unresolved)
        elif t == "let":
            f = spec.get(n["subj"])
            if f is None:
                unresolved.append(("let", n["subj"]))
            subj = f(env) if f else None
            if subj is not None:
                e2 = dict(env); e2[n["var"]] = subj
                interpret(n["kids"], spec, e2, out, unresolved)
        elif t == "leaf":
            nt = KL._ntype(n["ctype"])
            if not nt:
                continue
            if not n["static"] and n["expr"] and n["expr"] not in spec:
                unresolved.append(("leaf", n["expr"]))
            content = _resolve_leaf(n, spec, env)
            if content is not None and content != "":
                out.append((nt, _trunc(content), n["static"]))   # match the ledger's 30-char anchor


def _trunc(s):
    """same anchor normalization the ledgers use, so resolved values compare apples-to-apples."""
    s = " ".join(str(s).split())
    return (s[:30] + "…") if len(s) > 31 else s


def _hb_leaves(screen_key):
    """the hand-built screen's leaves, runtime-traced through the SAME seeded db (resolved)."""
    recs, err = KL.trace(screen_key)
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
    interpret(ir, spec, {}, leaves, unresolved)
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
    """the fixed reactive shim the transpiled VM runs against (Flow/stateIn/scope -> synchronous)."""
    class _StateFlow:
        def __init__(self, v): self.value = v

    class _Flow:
        def __init__(self, v): self._v = v
        def stateIn(self, *a): return _StateFlow(self._v)

    class _Scope:
        def launch(self, f): return f()

    class _Started:
        @staticmethod
        def WhileSubscribed(*a): return None

    return {"viewModelScope": _Scope(), "SharingStarted": _Started, "emptyList": (lambda: []),
            "KtList": list, "_Flow": _Flow}


def _load_transpiled(files):
    """transpile each .kt and exec into ONE namespace (so the classes see each other + the shim)."""
    from transpiler import KtToPy
    ns = _reactive_ns()
    for f in files:
        p = O.find_one(O.MAIN, f)
        py = KtToPy().transpile(open(p, "rb").read())
        exec(compile(py, f, "exec"), ns)                 # noqa: S102 -- transpiled, trusted
    return ns


def _gym_repo_adapter(ns, db):
    """Room-DAO boundary, ported to the kit InMemoryDb: yields the transpiled Kotlin shapes
    (GymWithEquipment bundling profile+equipment; gymType int -> GymType enum)."""
    from domain.gym_service import GymService
    from data.repository.gym_equipment_repository import GymEquipmentRepository
    GWE, GProf, GT, Flow = ns["GymWithEquipment"], ns["GymProfileEntity"], ns["GymType"], ns["_Flow"]

    def lift(g):
        gt = GT.entries[int(g.gymType)] if g.gymType is not None else None
        return GProf(g.id, g.name, g.isActive, gt, g.createdAt, g.updatedAt)

    class _Repo:
        def getAllWithEquipment(self):
            eq = GymEquipmentRepository(db)
            return Flow([GWE(lift(g), eq.get_by_gym(g.id)) for g in GymService(db).get_all()])

        def getActive(self):
            act = [g for g in GymService(db).get_all() if g.isActive]
            return Flow(lift(act[0]) if act else None)

        def setActive(self, gid): GymService(db).set_active(gid)
        def deleteGym(self, gid): GymService(db).delete_gym(gid)
    return _Repo()


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
    vm = ns["GymListViewModel"](_gym_repo_adapter(ns, db))   # the TRANSPILED VM, real data
    spec = _gym_list_spec_1to1(vm)
    leaves, unresolved = [], []
    interpret(ir, spec, {}, leaves, unresolved)
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


def main():
    args = [a for a in sys.argv[1:] if not a.startswith("-")]
    key = args[0] if args else "gym_list"
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
