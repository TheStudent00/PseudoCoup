"""ledger.py -- structural / connective fidelity ledger for the Kt->Py transpiler.

The oracle proves the FUNCTIONAL half (does the Python BEHAVE like the Kotlin). This is
the STRUCTURAL / CONNECTIVE half (does each Python object have the same SHAPE and WIRING as
its Kotlin object), tracked for every object whether or not it has a test. Two artifacts:

  1. in-output TAGS -- a correspondence docstring injected into each FRAME (module, class,
     function/method) of the transpiled Python: the frame's own Kotlin equivalent, its
     divergence kind, and a compact attribute map. "Frames" carry docstrings; "smaller
     objects" (attributes) fold into their owning frame's docstring; locals untracked.
  2. an external LEDGER (meta-data, separate file) -- one record per object: Kotlin {name,
     1-degree connections} and Python {name, 1-degree connections}. Connectivity is DERIVED
     from each side and compared, so a dropped reference surfaces as a mismatch.

Method: Kotlin shape is read statically (tree-sitter = the source spec); Python shape is read
by EXECing the transpiled module and introspecting the real objects (ground truth -- the same
modules the oracle already runs), so externally-assigned members (enum entries) and data-class
fields are seen exactly as they exist at runtime.

Divergence kinds the transpiler introduces:
  object->instance   Kotlin `object Foo`      -> Python `class Foo` + `Foo = Foo()`
  overload-split     Kotlin `fun f` (xN)      -> Python `_f__0.._f__{N-1}` + `f` wrapper
  extension-hoist    Kotlin `fun Recv.f()`    -> Python top-level `def f` (off the receiver)
  rename / missing / extra

Usage:  python3 ledger.py AutoregulationEngine [WarmupEngine ...]
Writes ledger_sample/<Engine>.tagged.py and ledger_sample/<Engine>.ledger.md.
"""
import ast
import inspect
import os
import sys
from collections import Counter

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import oracle as O                          # noqa: E402
from parse import parse                     # noqa: E402

OUT = os.path.join(HERE, "ledger_sample")


# ── Kotlin side (tree-sitter = the source spec) ──────────────────────────────
def _kname(node):
    return next((c.text.decode() for c in node.children if c.type == "identifier"), None)


def _kind(node):
    if node.type == "object_declaration":
        return "object"
    mods = next((c for c in node.children if c.type == "modifiers"), None)
    txt = mods.text.decode() if mods else ""
    return "enum class" if "enum" in txt else ("data class" if "data" in txt else "class")


def _kt_attrs(node):
    """primary-constructor params (under class_parameters) + body val/var + enum entries."""
    out = []
    pc = next((c for c in node.children if c.type == "primary_constructor"), None)
    if pc:
        stack = [pc]
        while stack:
            n = stack.pop()
            if n.type == "class_parameter":
                nm = next((k.text.decode() for k in n.children if k.type == "identifier"), None)
                if nm:
                    out.append(nm)
            else:
                stack.extend(n.children)
    body = next((c for c in node.children
                 if c.type in ("class_body", "enum_class_body")), None)
    if body:
        for c in body.named_children:
            if c.type == "property_declaration":
                vd = next((k for k in c.children if k.type == "variable_declaration"), None)
                nm = (next((k.text.decode() for k in vd.children
                            if k.type == "identifier"), None) if vd else None)
                if nm:
                    out.append(nm)
            elif c.type == "enum_entry":
                nm = next((k.text.decode() for k in c.children if k.type == "identifier"), None)
                if nm:
                    out.append(nm)
    return out


def _kt_methods_nested(node):
    methods, nested = [], []
    body = next((c for c in node.children
                 if c.type in ("class_body", "enum_class_body")), None)
    if body:
        for c in body.named_children:
            if c.type == "function_declaration":
                methods.append(_kname(c))
            elif c.type in ("class_declaration", "object_declaration"):
                nested.append(c)
    return [m for m in methods if m], nested


def _refs(node, universe):
    """corpus objects this subtree references at RUNTIME (1-degree connections). Skips
    `user_type` subtrees -- those are type annotations, which Python drops, so counting
    them would falsely diverge from the Python side."""
    out, stack = set(), [node]
    while stack:
        n = stack.pop()
        if n.type == "user_type":
            continue
        if n.type == "identifier" and n.text.decode() in universe:
            out.add(n.text.decode())
        stack.extend(n.children)
    return out


def kt_extract(path, universe):
    root = parse(open(path, "rb").read()).root_node
    frames, top_funcs = [], []
    for c in root.named_children:
        if c.type in ("class_declaration", "object_declaration"):
            name = _kname(c)
            methods, nested = _kt_methods_nested(c)
            nested_names = {_kname(nn) for nn in nested}
            frame = {"name": name, "kind": _kind(c), "attrs": _kt_attrs(c), "methods": methods,
                     "conns": sorted(_refs(c, universe) - {name} - nested_names), "nested": []}
            for nn in nested:
                nm, _ = _kt_methods_nested(nn)
                frame["nested"].append({"name": _kname(nn), "kind": _kind(nn),
                                        "attrs": _kt_attrs(nn), "methods": nm})
            frames.append(frame)
        elif c.type == "function_declaration":           # top-level fun (maybe an extension)
            top_funcs.append(_kname(c))
    return frames, [f for f in top_funcs if f]


# ── Python side (exec + introspect the real objects = ground truth) ──────────
def _shape(cls):
    own = vars(cls)
    methods = {n for n, x in own.items() if callable(x) and not n.startswith("__")}
    nested = {n: _shape(x) for n, x in own.items() if isinstance(x, type)}
    class_attrs = {n for n, x in own.items()
                   if not callable(x) and not isinstance(x, type) and not n.startswith("__")}
    fields = set()
    try:
        fields = {p for p in inspect.signature(cls.__init__).parameters
                  if p != "self" and not p.startswith("*")}
    except (ValueError, TypeError):
        pass
    return {"methods": methods, "nested": nested, "attrs": class_attrs | fields}


def py_runtime(engine, own_names):
    eng = O.find_one(O.MAIN, f"{engine}.kt")
    ns = {k: getattr(O.rt, k) for k in dir(O.rt) if not k.startswith("_")}
    O._exec_multipass([O.transpile(p) for p in O.closure([eng])], ns)
    exec(compile(O.transpile(eng), "<eng>", "exec"), ns)
    classes, funcs, instances = {}, set(), set()
    for name in own_names:
        v = ns.get(name)
        if isinstance(v, type):
            classes[name] = _shape(v)
        elif callable(v):
            funcs.add(name)
        elif v is not None and type(v).__name__ == name:    # Foo = Foo()  -> object->instance
            instances.add(name)
            sh = _shape(type(v))
            sh["attrs"] |= {k for k in vars(v) if not k.startswith("__")}  # object's self.X consts
            classes[name] = sh
    return classes, funcs, instances


def py_own_and_conns(py_src, universe):
    tree = ast.parse(py_src)
    own, conns = set(), {}
    module_refs = {x.id for x in ast.walk(tree) if isinstance(x, ast.Name) and x.id in universe}
    for n in tree.body:
        if isinstance(n, (ast.ClassDef, ast.FunctionDef)):
            own.add(n.name)
        elif isinstance(n, ast.Assign):
            own |= {t.id for t in n.targets if isinstance(t, ast.Name)}
        if isinstance(n, ast.ClassDef):
            nested = {x.name for x in n.body if isinstance(x, ast.ClassDef)}   # own nested types
            conns[n.name] = sorted({x.id for x in ast.walk(n)
                                    if isinstance(x, ast.Name) and x.id in universe}
                                   - {n.name} - nested)
    return own, conns, module_refs


# ── alignment / divergence ───────────────────────────────────────────────────
def classify_methods(kt_methods, py_methods, py_funcs):
    """-> list of (kind, kt_name, detail). kind: exact/overload-split/extension-hoist/missing."""
    rows = []
    for name, n in Counter(kt_methods).items():
        impls = sorted(m for m in py_methods if m.startswith(f"_{name}__"))
        if n > 1 and name in py_methods and impls:
            rows.append(("overload-split", name, f"{name} (wrapper) + {', '.join(impls)}"))
        elif name in py_methods:
            rows.append(("exact", name, name))
        elif name in py_funcs:
            rows.append(("extension-hoist", name, f"top-level def {name}"))
        else:
            rows.append(("missing", name, "-"))
    return rows


# ── tag rendering ────────────────────────────────────────────────────────────
def class_doc(kt, py_shape, divergence):
    lines = [f'"""≡KT  {kt["kind"]} {kt["name"]}  -> {divergence}']
    a_kt, a_py = kt.get("attrs", []), (py_shape["attrs"] if py_shape else set())
    if a_kt:
        matched = [a for a in a_kt if a in a_py]
        miss = [a for a in a_kt if a not in a_py]
        lines.append(f"attrs ({len(matched)}/{len(a_kt)}): {', '.join(matched)}"
                     + (f"   MISSING: {', '.join(miss)}" if miss else ""))
    if kt.get("conns"):
        lines.append(f"connects(1deg): {', '.join(kt['conns'])}")
    lines.append('"""')
    return lines


def func_doc(kind, name, detail):
    if kind == "overload-split":
        return [f'"""≡KT  fun {name} (overloaded)  -> overload-split', f"impls: {detail}", '"""']
    if kind == "extension-hoist":
        return [f'"""≡KT  fun (extension) {name}  -> hoisted to {detail}"""']
    return [f'"""≡KT  fun {name}  -> exact"""']


# ── docstring injection (preserve transpiler formatting) ─────────────────────
def inject(py_src, tags_by_lineno, module_header):
    lines = py_src.splitlines()
    for lineno in sorted(tags_by_lineno, reverse=True):       # splice bottom-up
        col, doc = tags_by_lineno[lineno]
        lines[lineno - 1:lineno - 1] = [(" " * col) + d for d in doc]
    return "\n".join(module_header + lines) + "\n"


def build_tags(py_src, kt_frames, classes, funcs, instances):
    tree = ast.parse(py_src)
    kt_by_name, shape_by_name = {}, dict(classes)
    for f in kt_frames:                                   # include nested frames -- every frame tags
        kt_by_name[f["name"]] = f
        for nn in f["nested"]:
            kt_by_name[nn["name"]] = nn
            if f["name"] in classes:
                shape_by_name[nn["name"]] = classes[f["name"]]["nested"].get(nn["name"])
    tags = {}
    for n in ast.walk(tree):
        if isinstance(n, ast.ClassDef) and n.name in kt_by_name:
            kt = kt_by_name[n.name]
            div = ("object->instance" if (kt["kind"] == "object" and n.name in instances)
                   else f'{kt["kind"]} (exact)')
            b0 = n.body[0]
            tags[b0.lineno] = (b0.col_offset, class_doc(kt, shape_by_name.get(n.name), div))
            py_methods = {m.name for m in n.body if isinstance(m, ast.FunctionDef)}
            rows = {r[1]: r for r in classify_methods(kt["methods"], py_methods, funcs)}
            for m in n.body:
                if isinstance(m, ast.FunctionDef) and m.name in rows:
                    k, knm, detail = rows[m.name]
                    mb0 = m.body[0]
                    tags[mb0.lineno] = (mb0.col_offset, func_doc(k, knm, detail))
    return tags


# ── ledger rendering ─────────────────────────────────────────────────────────
def render(engine, kt_frames, top_funcs, classes, funcs, instances, py_conns, module_refs):
    L = [f"# Fidelity ledger -- {engine}", "",
         "Structural + connective correspondence, Kotlin <-> Python. Kotlin shape read",
         "statically; Python shape read by introspecting the exec'd module. Behaviour is",
         "proven separately by oracle.py; this is the shape/wiring half.", ""]
    c = Counter()
    conn_ok = True
    for kt in kt_frames:
        py = classes.get(kt["name"])
        if not py:
            L.append(f"## {kt['kind']} {kt['name']}  -> MISSING IN PYTHON\n"); c["missing"] += 1
            continue
        is_inst = kt["kind"] == "object" and kt["name"] in instances
        div = "object->instance" if is_inst else f"{kt['kind']} (exact)"
        c["object->instance" if is_inst else "frame-exact"] += 1
        head = f"class {kt['name']}" + (f" + {kt['name']}={kt['name']}()" if is_inst else "")
        L.append(f"## {kt['kind']} {kt['name']}  ==  {head}   [{div}]")
        kc, pc = set(kt["conns"]), set(py_conns.get(kt["name"], []))
        dropped = (kc - pc) - module_refs        # in KT frame, absent from the whole PY module
        relocated = (kc - pc) & module_refs       # moved to another PY frame (e.g. companion hoist)
        if dropped:
            status, conn_ok = "DROPPED (broken): " + ", ".join(sorted(dropped)), False
        elif relocated:
            status = "relocated to another frame: " + ", ".join(sorted(relocated))
        else:
            status = "match"
        L.append(f"- connects(1deg) KT: {', '.join(sorted(kc)) or '--'}")
        L.append(f"- connects(1deg) PY: {', '.join(sorted(pc)) or '--'}   [{status}]")
        ak = kt["attrs"]
        if ak:
            am = sum(1 for a in ak if a in py["attrs"])
            miss = [a for a in ak if a not in py["attrs"]]
            L.append(f"- attrs {am}/{len(ak)}" + (f"   MISSING: {', '.join(miss)}" if miss else ""))
        for k, knm, detail in classify_methods(kt["methods"], py["methods"], funcs):
            if k == "exact":
                c["method-exact"] += 1
            elif k == "overload-split":
                c["overload-split"] += 1
                L.append(f"  - overload-split  fun {knm}  ==  {detail}")
            elif k == "extension-hoist":
                c["extension-hoist"] += 1
                L.append(f"  - extension-hoist  fun {knm}  ==  {detail}")
            else:
                c["missing"] += 1
                L.append(f"  - MISSING  fun {knm}")
        for nn in kt["nested"]:
            pn = py["nested"].get(nn["name"])
            if pn is None:
                L.append(f"  - nested {nn['kind']} {nn['name']}  -> MISSING"); c["missing"] += 1
                continue
            c["nested-exact"] += 1
            am = sum(1 for a in nn["attrs"] if a in pn["attrs"])
            flag = "" if am == len(nn["attrs"]) else "  <-- attr gap"
            L.append(f"  - nested {nn['kind']} {nn['name']}  ==  class {nn['name']}"
                     f"   [attrs {am}/{len(nn['attrs'])}]{flag}")
        L.append("")
    for f in top_funcs:
        kind = "extension-hoist" if f in funcs else ("exact" if f in funcs else "MISSING")
        L.append(f"## top-level fun {f}  ==  def {f}   [{'exact' if f in funcs else 'MISSING'}]")
        c["frame-exact" if f in funcs else "missing"] += 1
    L += ["---", "## summary",
          f"- frames: {len(kt_frames)} top + {len(top_funcs)} top-level fun · "
          f"object->instance {c['object->instance']} · nested classes {c['nested-exact']}",
          f"- methods: exact {c['method-exact']} · overload-split {c['overload-split']} · "
          f"extension-hoist {c['extension-hoist']} · missing {c['missing']}",
          f"- connectivity (1deg sets match both sides): {'all frames match' if conn_ok else 'MISMATCH above'}",
          "- UI sizing/positioning: n/a (engine layer is non-UI; populated for ui/ frames later)", ""]
    return "\n".join(L), c, conn_ok


# ── driver ───────────────────────────────────────────────────────────────────
def run(engine):
    universe = set(O.build_index())
    eng = O.find_one(O.MAIN, f"{engine}.kt")
    kt_frames, top_funcs = kt_extract(eng, universe)
    py_src = O.transpile(eng)
    own, py_conns, module_refs = py_own_and_conns(py_src, universe)
    classes, funcs, instances = py_runtime(engine, own)

    tags = build_tags(py_src, kt_frames, classes, funcs, instances)
    all_conns = sorted(set().union(*[set(f["conns"]) for f in kt_frames]) if kt_frames else set())
    header = [f"# ≡KT module  {os.path.relpath(eng, O.MAIN)}  ->  {engine}.py",
              f"# connects(1deg): {', '.join(all_conns) or '--'}", ""]
    tagged = inject(py_src, tags, header)
    ledger_md, c, conn_ok = render(engine, kt_frames, top_funcs, classes, funcs,
                                   instances, py_conns, module_refs)

    os.makedirs(OUT, exist_ok=True)
    open(os.path.join(OUT, f"{engine}.tagged.py"), "w").write(tagged)
    open(os.path.join(OUT, f"{engine}.ledger.md"), "w").write(ledger_md)
    print(f"  {engine}: object->instance {c['object->instance']} · methods exact {c['method-exact']} · "
          f"overload-split {c['overload-split']} · extension-hoist {c['extension-hoist']} · "
          f"nested {c['nested-exact']} · missing {c['missing']} · "
          f"connectivity {'OK' if conn_ok else 'MISMATCH'}")
    return c, conn_ok


def main():
    names = [a for a in sys.argv[1:] if not a.startswith("-")] or ["AutoregulationEngine"]
    print(f"fidelity ledger -> {os.path.relpath(OUT)}/")
    for n in names:
        run(n)


if __name__ == "__main__":
    main()
