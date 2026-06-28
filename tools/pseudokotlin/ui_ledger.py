"""ui_ledger.py -- UI sizing/positioning extractor for the fidelity ledger (bucket 3).

The structural ledger (ledger.py) records names + 1-degree connections for engine/model frames.
For `ui/` frames the ledger record reserves a sizing/positioning field; this fills the KOTLIN
side of it by reading each @Composable's layout INTENT statically from the Compose `Modifier`
chain and container arguments, normalized into a target-agnostic vocabulary so the SAME schema
can later check Compose<->Kivy and Kivy<->Flutter (the pipeline is two hops).

Two honest layers (see DevComms): this is the POLICY layer (static, from the Modifier chain --
`48.dp` absolute, `fillMaxWidth()`/`weight(1f)` relative). The GEOMETRY layer (render both sides,
diff the boxes) is the rung above and needs render harnesses; not built here.

What it captures per widget node, each tagged absolute|relative:
  size   w,h         fill / weight(n) / wrap  (relative) · Ndp / token  (absolute)
  place  pad,offset  dp / token               (absolute)
         align,arrange,index-in-parent        (relative -- position within the parent)

Usage:  python3 ui_ledger.py ui/components/WflSectionHeader.kt [more.kt ...]
        python3 ui_ledger.py --scan          # a few representative screens
Writes ledger_sample/<name>.ui.md.
"""
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import oracle as O                          # noqa: E402
from parse import parse                     # noqa: E402

OUT = os.path.join(HERE, "ledger_sample")
UIROOT = os.path.join(O.MAIN, "java", "com", "sara", "workoutforlife", "ui")

# Modifier methods that affect layout (everything else -- clickable/background/clip/... -- is
# noted as non-layout so nothing is silently dropped).
SIZE_FILL = {"fillMaxWidth": "w", "fillMaxHeight": "h", "fillMaxSize": "wh"}
SIZE_ABS = {"width": "w", "height": "h", "size": "wh", "requiredWidth": "w",
            "requiredHeight": "h", "requiredSize": "wh", "defaultMinSize": "wh",
            "heightIn": "h", "widthIn": "w", "sizeIn": "wh"}
WRAP = {"wrapContentWidth": "w", "wrapContentHeight": "h", "wrapContentSize": "wh"}
NONLAYOUT = {"clickable", "background", "clip", "border", "testTag", "semantics", "alpha",
             "shadow", "then", "graphicsLayer", "zIndex", "rotate", "scale", "focusable",
             "selectable", "toggleable", "horizontalScroll", "verticalScroll", "pointerInput"}


def _abs(v):
    """is this size/pad value an ABSOLUTE measure (dp/sp literal or a design token)?"""
    return bool(re.search(r"\d+\s*\.\s*(dp|sp)", v) or "tokens." in v or ".dp" in v or ".sp" in v)


# A labeled text field is ONE widget, identified by its label (the static, stable, user-visible
# string) -- not by descending its label/placeholder slot into a separate Text. Both ledger sides
# and the generator key it the same way (-> type "F"), so they line up.
FIELDS_UI = {"TextField", "OutlinedTextField", "BasicTextField", "BasicSecureTextField"}


def field_anchor(call, subst=None):
    """a text field's content anchor + static-ness, from its label (else placeholder/support)."""
    a = _named_args(call)
    lab = a.get("label") or a.get("placeholder") or a.get("supportingText")
    if not lab:
        return None, False
    if subst and lab.strip() in subst:
        lab = subst[lab.strip()]
    lits = re.findall(r'"([^"$]*)"', lab)                 # a STATIC literal inside the slot lambda
    if lits:
        return _anchor('"' + lits[0] + '"'), True
    return _anchor(lab), False


# ── tree-sitter call-tree walk ───────────────────────────────────────────────
def _base_and_lambda(call):
    """trailing-lambda form parses as outer call = [inner_call(args), annotated_lambda]."""
    inner = next((k for k in call.children if k.type == "call_expression"), None)
    lam = next((k for k in call.children if k.type in ("annotated_lambda", "lambda_literal")), None)
    base = inner if inner is not None else call
    return base, lam


def _name(call):
    base, _ = _base_and_lambda(call)
    idc = next((k for k in base.children if k.type == "identifier"), None)
    return idc.text.decode() if idc else None


def _named_args(call):
    base, _ = _base_and_lambda(call)
    va = next((k for k in base.children if k.type == "value_arguments"), None)
    out = {}
    if va:
        for a in va.named_children:
            if a.type == "value_argument":
                kids = a.children
                if len(kids) >= 3 and kids[0].type == "identifier" and kids[1].type == "=":
                    out[kids[0].text.decode()] = kids[2].text.decode()
    return out


def _is_widget(call):
    n = _name(call)
    return bool(n and n[0].isupper())


def _children(call):
    """direct child widget calls -- from the trailing lambda AND from named-argument lambdas
    (Compose slot APIs: Scaffold(topBar={…}), TopAppBar(title={…}), Button(content)…). Don't
    descend into a found child (handled when it's processed)."""
    base, lam = _base_and_lambda(call)
    found = []

    def walk(n):
        for c in n.children:
            if c.type == "call_expression" and _is_widget(c):
                found.append(c)
            else:
                walk(c)
    if lam is not None:
        walk(lam)
    va = next((k for k in base.children if k.type == "value_arguments"), None)
    if va:
        for a in va.named_children:
            if a.type == "value_argument":
                for k in a.children:
                    if k.type in ("lambda_literal", "annotated_lambda"):
                        walk(k)
    return found


# ── modifier-chain normalization (the policy layer) ──────────────────────────
def _split_chain(text):
    segs, depth, cur = [], 0, ""
    for ch in text:
        if ch in "([{":
            depth += 1
        elif ch in ")]}":
            depth -= 1
        if ch == "." and depth == 0:
            segs.append(cur)
            cur = ""
        else:
            cur += ch
    segs.append(cur)
    return [s.strip() for s in segs if s.strip()]


def _norm(call, parent_kind):
    """-> normalized layout descriptor for one widget node."""
    args = _named_args(call)
    size = {"w": "wrap", "h": "wrap"}
    pad = offset = align = None
    other = []
    mod = args.get("modifier", "")
    for seg in _split_chain(mod):
        m = seg.split("(", 1)[0].strip()
        inside = seg[len(m) + 1:-1].strip() if "(" in seg else ""
        if m in ("modifier", "Modifier", ""):
            continue
        if m in SIZE_FILL:
            for d in SIZE_FILL[m]:
                size[d] = "fill"
        elif m in SIZE_ABS:
            for d in SIZE_ABS[m]:
                size[d] = inside or "?"
        elif m in WRAP:
            for d in WRAP[m]:
                size[d] = "wrap"
        elif m == "weight":
            d = "w" if parent_kind == "Row" else ("h" if parent_kind == "Column" else "w")
            size[d] = f"weight({inside})"
        elif m == "padding":
            pad = inside
        elif m == "offset":
            offset = inside
        elif m == "align":
            align = inside
        elif m not in NONLAYOUT:
            other.append(m)
    # container args that position CHILDREN
    cont = {k: args[k] for k in ("verticalAlignment", "horizontalAlignment",
                                 "horizontalArrangement", "verticalArrangement",
                                 "contentAlignment") if k in args}
    return {"size": size, "pad": pad, "offset": offset, "align": align,
            "container": cont, "nonlayout": [m for m in NONLAYOUT if f"{m}(" in mod or f".{m}" in mod],
            "other": other}


# ── widget identity: a content-anchored path-id (no source annotation needed) ─
_COMPS = None


def composable_names():
    """names of the project's own @Composable functions -- these are the component-level
    identifiers (a call to one is a component reference, id'd by name, not by position)."""
    global _COMPS
    if _COMPS is None:
        _COMPS = set()
        for dp, _, fs in os.walk(UIROOT):
            for f in fs:
                if f.endswith(".kt"):
                    try:
                        for cn, _ in composables(os.path.join(dp, f)):
                            _COMPS.add(cn)
                    except Exception:                    # noqa: BLE001
                        pass
    return _COMPS


def _first_positional(call):
    base, _ = _base_and_lambda(call)
    va = next((k for k in base.children if k.type == "value_arguments"), None)
    if not va:
        return None
    for a in va.named_children:
        if a.type == "value_argument":
            kids = a.children
            if not (len(kids) >= 2 and kids[0].type == "identifier" and kids[1].type == "="):
                return a.text.decode()
    return None


def _anchor(expr):
    """human handle from an arg value: prefer string literals (an `if/else` yields a|b),
    else the raw expression; normalized + truncated."""
    lits = re.findall(r'"([^"]*)"', expr)
    s = "|".join(lits) if lits else expr.strip()
    s = re.sub(r"\s+", " ", s)
    return (s[:30] + "…") if len(s) > 31 else s


def _resolve_anchor(expr, subst):
    """resolve a bare param reference (e.g. `label`) to its bound literal before anchoring."""
    e = expr.strip()
    if subst and e in subst:
        e = subst[e]
    return _anchor(e)


def _segment(call, idx, comps, subst=None):
    """this node's id segment: component name · Type[desc=…] · Text[\"…\"] · Type[index]."""
    name = _name(call)
    if name in comps:                                    # a custom composable -> id by name
        return name
    if name in FIELDS_UI:                                # a field -> id by its label
        fa, _ = field_anchor(call, subst)
        return f"{name}[{fa}]" if fa else f"{name}[{idx}]"
    args = _named_args(call)
    cd = args.get("contentDescription")
    if name in ("Icon", "Image") and cd and cd.strip() != "null":   # null desc = decorative
        return f"{name}[desc={_resolve_anchor(cd, subst)}]"
    if name == "Text":
        txt = args.get("text") or _first_positional(call)
        if txt:
            return f"Text[{_resolve_anchor(txt, subst)}]"
    return f"{name}[{idx}]"


# ── render ───────────────────────────────────────────────────────────────────
def _tag(v):
    if v in ("fill", "wrap") or v.startswith("weight"):
        return "rel"
    return "abs" if _abs(v) or v not in ("?",) else "rel"


def render_node(call, parent_kind, depth, idx, path, lines, ids, comps):
    name = _name(call)
    seg = _segment(call, idx, comps)
    full = "/".join(path + [seg])
    ids.append(full)
    d = _norm(call, parent_kind)
    kids = _children(call)
    kind = "container" if kids else "leaf"
    ind = "  " * depth
    sz = d["size"]
    szs = f"w={sz['w']}({_tag(sz['w'])}) h={sz['h']}({_tag(sz['h'])})"
    lines.append(f"{ind}- {seg}  <{kind}>   size: {szs}")
    extra = []
    if d["pad"]:
        extra.append(f"pad={d['pad']} ({'abs' if _abs(d['pad']) else 'rel'})")
    if d["offset"]:
        extra.append(f"offset={d['offset']} (abs)")
    if d["align"]:
        extra.append(f"align={d['align']} (rel)")
    if d["container"]:
        extra.append("children: " + ", ".join(f"{k}={v}" for k, v in d["container"].items()) + " (rel)")
    if d["nonlayout"]:
        extra.append("non-layout: " + ", ".join(d["nonlayout"]))
    if extra:
        lines.append(f"{ind}    " + " · ".join(extra))
    for i, c in enumerate(kids):
        render_node(c, name, depth + 1, i, path + [seg], lines, ids, comps)
    return 1 + sum(_count(c) for c in kids)


def _count(call):
    return 1 + sum(_count(c) for c in _children(call))


_DEFS = None
_TREES = []                                              # keep parsed trees alive (nodes ref them)


def _comp_defs():
    """{composable name -> (param_names, root_widget_calls)} across the whole ui/ tree, so a
    call like LabeledField(label="…") can be inlined to its definition's widgets."""
    global _DEFS
    if _DEFS is None:
        _DEFS = {}
        for dp, _, fs in os.walk(UIROOT):
            for f in fs:
                if not f.endswith(".kt"):
                    continue
                try:
                    tree = parse(open(os.path.join(dp, f), "rb").read())
                except Exception:                        # noqa: BLE001
                    continue
                _TREES.append(tree)
                stack = [tree.root_node]
                while stack:
                    n = stack.pop()
                    if n.type == "function_declaration":
                        mods = next((k for k in n.children if k.type == "modifiers"), None)
                        if mods and "@Composable" in mods.text.decode():
                            nm = next((k.text.decode() for k in n.children
                                       if k.type == "identifier"), None)
                            fvp = next((k for k in n.children
                                        if k.type == "function_value_parameters"), None)
                            params = []
                            if fvp:
                                for p in fvp.named_children:
                                    if p.type == "parameter":
                                        pn = next((k.text.decode() for k in p.children
                                                   if k.type == "identifier"), None)
                                        if pn:
                                            params.append(pn)
                            body = next((k for k in n.children
                                         if k.type == "function_body"), None)
                            roots = []
                            if body:
                                def w(x):
                                    for c in x.children:
                                        if c.type == "call_expression" and _is_widget(c):
                                            roots.append(c)
                                        else:
                                            w(c)
                                w(body)
                            if nm:
                                _DEFS[nm] = (params, roots)
                    stack.extend(n.children)
    return _DEFS


def _bind(call, params, subst):
    """{param_name -> bound arg value} for a custom-composable call site. An arg that is itself
    a param reference is resolved through the CURRENT subst first, so a literal chains down
    (LabeledField(label="X") -> FieldLabel(label) -> Text(label) all resolve to "X")."""
    base, _ = _base_and_lambda(call)
    va = next((k for k in base.children if k.type == "value_arguments"), None)
    out, pos = {}, 0

    def res(v):
        return subst.get(v.strip(), v)

    if va:
        for a in va.named_children:
            if a.type != "value_argument":
                continue
            kids = a.children
            if len(kids) >= 3 and kids[0].type == "identifier" and kids[1].type == "=":
                out[kids[0].text.decode()] = res(kids[2].text.decode())
            else:
                if pos < len(params):
                    out[params[pos]] = res(a.text.decode())
                pos += 1
    return out


def collect_ids(path):
    """-> [(full_path_id, type, content_anchor|None)] for the cross-side compare. Inlines custom
    composables (binding literal params) so a slot/param text resolves to the same literal the
    kit renders -- e.g. LabeledField(label="Your name") -> Text[Your name]."""
    cnames = composable_names()
    defs = _comp_defs()
    out = []

    def anchor_of(call, subst):
        """-> (anchor, is_static). static = a pure string literal (no $ interpolation, no
        surrounding expression); dynamic = a binding/variable, which the kit renders resolved
        and so can only be matched structurally (by type+position), not by string."""
        name = _name(call)
        if name in FIELDS_UI:
            return field_anchor(call, subst)
        expr = None
        if name == "Text":
            expr = _named_args(call).get("text") or _first_positional(call)
        elif name in ("Icon", "Image"):
            expr = _named_args(call).get("contentDescription")
        if not expr:
            return None, False
        e = expr.strip()
        if subst and e in subst:
            e = subst[e]
        if e.strip() == "null":                          # decorative icon/image -> no content leaf
            return None, False
        static = bool(re.match(r'^"[^"$]*"$', e.strip()))
        return _anchor(e), static

    def walk(call, idx, path, subst, stack):
        name = _name(call)
        seg = _segment(call, idx, cnames, subst)
        full = "/".join(path + [seg])
        anchor, static = anchor_of(call, subst)
        out.append((full, name, anchor, static))
        if name in FIELDS_UI:                            # field = one leaf; don't descend its slots
            return
        if name in defs and name not in stack:           # inline the composable's definition
            params, roots = defs[name]
            argmap = _bind(call, params, subst)
            for i, r in enumerate(roots):
                walk(r, i, path + [seg], argmap, stack + [name])
        for i, c in enumerate(_children(call)):           # trailing + slot children
            walk(c, i, path + [seg], subst, stack)

    for cname, roots in composables(path):
        for i, r in enumerate(roots):
            walk(r, i, [cname], {}, [cname])
    return out


def composables(path):
    root = parse(open(path, "rb").read()).root_node
    out = []
    stack = [root]
    while stack:
        n = stack.pop()
        if n.type == "function_declaration":
            mods = next((k for k in n.children if k.type == "modifiers"), None)
            if mods and "@Composable" in mods.text.decode():
                name = next((k.text.decode() for k in n.children if k.type == "identifier"), "?")
                body = next((k for k in n.children if k.type == "function_body"), None)
                roots = []
                if body:
                    def walk(x):
                        for c in x.children:
                            if c.type == "call_expression" and _is_widget(c):
                                roots.append(c)
                            else:
                                walk(c)
                    walk(body)
                out.append((name, roots))
        stack.extend(n.children)
    return out


def run(rel):
    path = rel if os.path.isabs(rel) else os.path.join(O.MAIN, rel)
    if not os.path.exists(path):
        path = os.path.join(UIROOT, rel)
    comps = composables(path)
    name = os.path.basename(path)[:-3]
    cnames = composable_names()
    L = [f"# UI layout ledger -- {name}", "",
         "Kotlin-side sizing/positioning, read statically from each Composable's Modifier",
         "chain + container args. Normalized vocabulary (target-agnostic). abs = fixed dp/sp/",
         "token; rel = fill/weight/wrap/alignment (parent-relative). The Python/kit side and the",
         "rendered-geometry diff plug into this same schema later.", "",
         "Each node carries a content-anchored path-id (no source annotation needed): a custom",
         "composable -> its name; Icon/Image -> [desc=…]; Text -> [\"…\"]; else Type[index]. The",
         "full id is the path from the composable root -- a stable handle for the cross-side match.", ""]
    total = 0
    for cname, roots in comps:
        L.append(f"## @Composable {cname}")
        if not roots:
            L.append("  (no layout widgets)\n")
            continue
        ids = []
        for i, r in enumerate(roots):
            total += render_node(r, None, 1, i, [cname], L, ids, cnames)
        L.append("  ids:")
        L += [f"    {x}" for x in ids]
        L.append("")
    L += ["---", f"summary: {len(comps)} composables, {total} widget nodes", ""]
    os.makedirs(OUT, exist_ok=True)
    open(os.path.join(OUT, f"{name}.ui.md"), "w").write("\n".join(L))
    print(f"  {name}: {len(comps)} composables, {total} widget nodes -> ledger_sample/{name}.ui.md")


SCAN = ["components/WflSectionHeader.kt", "execution/components/ExerciseQueue.kt",
        "execution/components/RestTimerOverlay.kt", "theme/WflCard.kt"]


def main():
    args = sys.argv[1:]
    targets = SCAN if (not args or args == ["--scan"]) else [a for a in args if not a.startswith("-")]
    print(f"UI layout ledger -> ledger_sample/")
    for t in targets:
        try:
            run(t)
        except Exception as e:                           # noqa: BLE001
            print(f"  {t}: ERROR {type(e).__name__}: {e}")


if __name__ == "__main__":
    main()
