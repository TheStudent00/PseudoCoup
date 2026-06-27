#!/usr/bin/env python3
"""
extract_table.py -- harvest the DECLARATIVE construct-equivalence table directly
from py2many's source, instead of black-boxing it (snippet in -> read output).

py2many encodes a chunk of the Python<->target mapping as explicit dicts in each
backend: a primitive TYPE_MAP, a CONTAINER_TYPE_MAP, and the stdlib-function
dispatch maps (SMALL_DISPATCH_MAP / DISPATCH_MAP). They are ALL keyed by the same
Python pivot, so reading them yields a multi-language table (Python x N targets)
for free -- no compilation, no snippet running.

What this CANNOT give you (by design): the structural constructs (if/for/while/
ternary/class-shape/operators/assignment). Those live as imperative emit-templates
in visit_* methods, not as dict rows -- capture + VERIFY those with the atlas +
kotlinc compile gate (run_atlas.sh). And note: source tells you what py2many
*intends*, not whether it's *correct* (pristine 0.8 mapped Optional->Nothing, a
wrong row the compile gate catches). So: source for breadth, compile for truth.

Usage:  python3 extract_table.py            # markdown to stdout
"""
import importlib

# backend package -> display language
BACKENDS = {
    "pykt": "Kotlin",
    "pyrs": "Rust",
    "pycpp": "C++",
    "pygo": "Go",
    "pyd": "D",
    "pynim": "Nim",
    "pyjl": "Julia",
    "pydart": "Dart",
    "pyzig": "Zig",
    "pymojo": "Mojo",
}


# Rows where the compile gate (run_atlas.sh) proved the source's declared value
# wrong. The source dict is what py2many *intends*; these are what actually
# compiles. This list is the standing evidence that source != truth.
VERIFIED_OVERRIDES = {
    ("Kotlin", "Optional"): "`T?`  (source says `Nothing` — wrong; fixed in "
                            "pykt.patch, kotlinc-verified)",
}


def _find_dict(mod, suffix, exclude=(), prefer_keys=()):
    """Return a module-level dict whose name ends with `suffix`. When several
    match (e.g. Rust has both a primitive and a pyo3 `&Py*` type map), pick the
    one whose keys best cover `prefer_keys`."""
    cands = []
    for name in dir(mod):
        if name.endswith(suffix) and not any(x in name for x in exclude):
            val = getattr(mod, name)
            if isinstance(val, dict):
                cands.append(val)
    if not cands:
        return {}
    if prefer_keys:
        keyset = set(prefer_keys)
        cands.sort(key=lambda d: sum(1 for k in d if k in keyset), reverse=True)
    return cands[0]


def _key_name(k):
    return getattr(k, "__name__", str(k))


def harvest():
    """language -> {'types': {...}, 'containers': {...}, 'funcs': set()}"""
    out = {}
    for pkg, lang in BACKENDS.items():
        entry = {"types": {}, "containers": {}, "funcs": set()}
        try:
            inf = importlib.import_module(f"py2many.{pkg}.inference")
            tmap = _find_dict(inf, "_TYPE_MAP", exclude=("CONTAINER", "REVERSE", "WIDTH"),
                              prefer_keys=(bool, int, float, str, bytes))
            cmap = _find_dict(inf, "_CONTAINER_TYPE_MAP")
            entry["types"] = {_key_name(k): v for k, v in tmap.items()}
            entry["containers"] = dict(cmap)
        except Exception as e:  # noqa: BLE001
            entry["error"] = f"inference: {e}"
        try:
            plg = importlib.import_module(f"py2many.{pkg}.plugins")
            for dname in ("SMALL_DISPATCH_MAP", "DISPATCH_MAP"):
                d = getattr(plg, dname, {})
                if isinstance(d, dict):
                    entry["funcs"].update(d.keys())
        except Exception:  # noqa: BLE001
            pass
        out[lang] = entry
    return out


def _table(rows, header, pivots):
    langs = list(header)
    out = ["| Python | " + " | ".join(langs) + " |"]
    out.append("|" + "---|" * (len(langs) + 1))
    for p in pivots:
        cells = []
        for lang in langs:
            v = rows.get(lang, {}).get(p)
            cells.append("·" if v is None else str(v).replace("|", "\\|"))
        out.append(f"| `{p}` | " + " | ".join(cells) + " |")
    return "\n".join(out)


def main():
    data = harvest()
    langs = [l for l in data if "error" not in data[l]]

    # union of primitive-type pivots, ordered by first appearance
    type_pivots, seen = [], set()
    for lang in langs:
        for k in data[lang]["types"]:
            if k not in seen:
                seen.add(k)
                type_pivots.append(k)
    types_by_lang = {lang: data[lang]["types"] for lang in langs}

    cont_pivots, seen = [], set()
    for lang in langs:
        for k in data[lang]["containers"]:
            if k not in seen:
                seen.add(k)
                cont_pivots.append(k)
    conts_by_lang = {lang: data[lang]["containers"] for lang in langs}

    print("# Construct-equivalence table (harvested from py2many source)\n")
    print("Declarative rows only. Structural constructs (if/for/while/class/"
          "operators) are imperative emit-templates, not rows -- see run_atlas.sh.\n")
    print(f"Backends read: {len(langs)} ({', '.join(langs)})\n")

    print("## Primitive types\n")
    print(_table(types_by_lang, langs, type_pivots))

    print("\n\n## Container types\n")
    print(_table(conts_by_lang, langs, cont_pivots))

    print("\n\n## Stdlib / builtin functions with a mapping (coverage; "
          "emitted form verified via the compile gate)\n")
    for lang in langs:
        funcs = sorted(data[lang]["funcs"])
        print(f"- **{lang}** ({len(funcs)}): {', '.join('`'+f+'`' for f in funcs)}")

    if VERIFIED_OVERRIDES:
        print("\n\n## Compile-verified overrides (source intent was wrong)\n")
        print("| Language | Pivot | Verified value |")
        print("|---|---|---|")
        for (lang, pivot), val in VERIFIED_OVERRIDES.items():
            print(f"| {lang} | `{pivot}` | {val} |")


if __name__ == "__main__":
    main()
