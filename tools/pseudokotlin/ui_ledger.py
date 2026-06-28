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
    """direct child widget calls inside the trailing lambda (don't descend into a child)."""
    _, lam = _base_and_lambda(call)
    if lam is None:
        return []
    found = []

    def walk(n):
        for c in n.children:
            if c.type == "call_expression" and _is_widget(c):
                found.append(c)
            else:
                walk(c)
    walk(lam)
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


# ── render ───────────────────────────────────────────────────────────────────
def _tag(v):
    if v in ("fill", "wrap") or v.startswith("weight"):
        return "rel"
    return "abs" if _abs(v) or v not in ("?",) else "rel"


def render_node(call, parent_kind, depth, idx, sibs, lines):
    name = _name(call)
    d = _norm(call, parent_kind)
    kids = _children(call)
    kind = "container" if kids else "leaf"
    ind = "  " * depth
    pos = f" [{idx}/{sibs}]" if sibs else ""
    sz = d["size"]
    szs = f"w={sz['w']}({_tag(sz['w'])}) h={sz['h']}({_tag(sz['h'])})"
    lines.append(f"{ind}- {name}  <{kind}>{pos}   size: {szs}")
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
        render_node(c, name, depth + 1, i, len(kids), lines)
    return 1 + sum(_count(c) for c in kids)


def _count(call):
    return 1 + sum(_count(c) for c in _children(call))


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
    L = [f"# UI layout ledger -- {name}", "",
         "Kotlin-side sizing/positioning, read statically from each Composable's Modifier",
         "chain + container args. Normalized vocabulary (target-agnostic). abs = fixed dp/sp/",
         "token; rel = fill/weight/wrap/alignment (parent-relative). The Python/kit side and the",
         "rendered-geometry diff plug into this same schema later.", ""]
    total = 0
    for cname, roots in comps:
        L.append(f"## @Composable {cname}")
        if not roots:
            L.append("  (no layout widgets)\n")
            continue
        for r in roots:
            total += render_node(r, None, 1, 0, 0 if len(roots) == 1 else len(roots), L)
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
