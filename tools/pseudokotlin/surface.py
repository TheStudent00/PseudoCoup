"""
surface.py — the EXTERNAL-SURFACE map: classify every external name the foundation imports through autostub
by its KIND, from how the transpiled Python actually USES it (its AST). This is the type-specific view of
the wrapper surface: it says what each un-wrapped name *is*, so a stub is shaped to match (a Kotlin `object`
becomes a singleton, not a class), and so the kit work has a spec -- instead of one generic stub for all.

  obj    -- a Kotlin object / namespace: only ever dotted into     (Icons.Filled, MaterialTheme.typography)
  func   -- a function: called, lower-camel                        (dp, hiltViewModel, remember, items)
  class  -- a class: constructed and/or used as a type             (PaddingValues, BorderStroke)
  value  -- only read / passed, never called or dotted

  python3 surface.py            # the surface report, grouped by origin
"""
import ast
import os
import sys
import glob
import collections

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import resolve   # noqa: E402  -- origin() buckets a name by its library

ROOT = os.path.expanduser("~/Programming/WFL_MixingCenter")
_KINDS = None


def _usage():
    """{name -> {'called','attrs','typed','files'}} for every name imported from runtime.autostub, scanned
    from the transpiled Python (read as text + ast.parse -- never imported, so no circular dependency)."""
    u = collections.defaultdict(lambda: {"called": 0, "attrs": set(), "typed": 0, "files": 0})
    for f in glob.glob(ROOT + "/**/*.py", recursive=True):
        if "/WFL/" in f or "/__pycache__/" in f:
            continue
        try:
            tree = ast.parse(open(f).read())
        except SyntaxError:
            continue
        names = set()
        for n in ast.walk(tree):
            if isinstance(n, ast.ImportFrom) and n.module == "runtime.autostub":
                names.update(a.asname or a.name for a in n.names)
        if not names:
            continue
        for n in ast.walk(tree):
            if isinstance(n, ast.Call) and isinstance(n.func, ast.Name):
                if n.func.id in names:
                    u[n.func.id]["called"] += 1
                elif n.func.id == "isinstance" and len(n.args) >= 2 \
                        and isinstance(n.args[1], ast.Name) and n.args[1].id in names:
                    u[n.args[1].id]["typed"] += 1
            elif isinstance(n, ast.Attribute) and isinstance(n.value, ast.Name) and n.value.id in names:
                u[n.value.id]["attrs"].add(n.attr)
        for nm in names:
            u[nm]["files"] += 1
    return u


def _classify(name, r):
    if r["typed"]:
        return "class"                               # isinstance / base -> MUST be a real class
    if r["attrs"] and not r["called"]:
        return "obj"                                 # only dotted into -> a Kotlin object / namespace
    if r["called"]:
        return "class" if (name[:1].isupper() and not r["attrs"]) else "func"
    return "value"


def kinds():
    """{external name -> kind}, computed once from the transpiled output (cached)."""
    global _KINDS
    if _KINDS is None:
        _KINDS = {n: _classify(n, r) for n, r in _usage().items()}
    return _KINDS


def report():
    u = _usage()
    by_origin = collections.defaultdict(list)
    try:
        import registry
        provided = set(registry.provided())
    except Exception:                                # noqa: BLE001
        provided = set()
    for name, r in sorted(u.items()):
        kind = _classify(name, r)
        real = name in provided
        by_origin[_origin_of(name)].append((name, kind, real, r))
    print(f"external surface: {len(u)} names across the foundation\n")
    for origin in sorted(by_origin):
        rows = by_origin[origin]
        tally = collections.Counter(k for _, k, _, _ in rows)
        print(f"{origin}  ({len(rows)}: " + " ".join(f"{k} {n}" for k, n in tally.most_common()) + ")")
        for name, kind, real, r in sorted(rows, key=lambda x: (x[1], x[0])):
            tag = "REAL" if real else kind
            extra = (" ." + ",.".join(sorted(r["attrs"])[:4])) if kind == "obj" else \
                    (f" /{r['called']}" if r["called"] else "")
            print(f"    {tag:6s} {name}{extra}")
        print()


_ORIGIN = None


def _origin_of(name):
    """Best-effort origin for a simple name -- map it back through the foundation's imports."""
    global _ORIGIN
    if _ORIGIN is None:
        _ORIGIN = {}
        for path in glob.glob(os.path.expanduser(
                "~/Programming/WFL_MixingCenter/WFL/**/*.kt"), recursive=True):
            if os.sep + "build" + os.sep in path or path.endswith("Test.kt"):
                continue
            try:
                h = resolve.file_header(__import__("parse").parse(open(path, "rb").read()).root_node)
            except Exception:                        # noqa: BLE001
                continue
            for simple, fqn in h["imports"].items():
                _ORIGIN.setdefault(simple, resolve.origin(fqn))
    return _ORIGIN.get(name, "?")


if __name__ == "__main__":
    report()
