"""
resolve.py — the RESOLVE phase: figure out what every name refers to, before anything is translated.

Two tables come out of it:
  - per file:    the import table  {simple name -> fully-qualified name}  (+ wildcards, + package)
  - per project: the app symbol table  {declared name -> the module that declares it}

An `import java.text.SimpleDateFormat` binds the bare name `SimpleDateFormat`, IN THAT FILE, to the
external symbol `java.text.SimpleDateFormat`. Kotlin's default imports (kotlin.*, java.lang, …) are the
same thing, implicit -- a fixed set listed below. With these tables, any name a file uses is classifiable
as local / member / app class / external(+origin), and the external-dependency set is a printable fact
rather than something discovered by running the output and watching it fail.
"""
import os
import sys
import glob

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from parse import parse  # noqa: E402

# Kotlin's default imports -- names from these packages are in scope with NO import line.
KOTLIN_DEFAULT_PACKAGES = (
    "kotlin", "kotlin.annotation", "kotlin.collections", "kotlin.comparisons",
    "kotlin.io", "kotlin.ranges", "kotlin.sequences", "kotlin.text", "kotlin.math",
    "java.lang", "kotlin.jvm",
)

APP_ROOT_PACKAGE = "com.sara.workoutforlife"

# fully-qualified-name prefix -> origin label (the wrapper bucket / runtime module it belongs to).
# Order matters: the first matching prefix wins, so the specific androidx.* rules precede the general one.
_ORIGIN_RULES = (
    (APP_ROOT_PACKAGE, "app"),
    ("androidx.compose", "compose"),
    ("androidx.room", "androidx_room"),
    ("androidx.navigation", "androidx_navigation"),
    ("androidx.lifecycle", "androidx_lifecycle"),
    ("androidx.hilt", "androidx_hilt"),
    ("androidx.work", "androidx_work"),
    ("androidx.datastore", "androidx_datastore"),
    ("androidx", "androidx"),
    ("dagger", "dagger_hilt"),
    ("javax.inject", "dagger_hilt"),
    ("android", "android"),
    ("kotlinx.coroutines", "kotlinx_coroutines"),
    ("kotlinx", "kotlinx"),
    ("kotlin", "kotlin"),
    ("java", "java"),
    ("javax", "javax"),
    ("com.google", "google"),
    ("org", "org"),
)


def origin(fqn):
    """The origin bucket for a fully-qualified name -- 'app' for the project's own code, else the
    library family (java, kotlin, compose, androidx_room, …) that owns it."""
    for prefix, label in _ORIGIN_RULES:
        if fqn == prefix or fqn.startswith(prefix + "."):
            return label
    return "other"


def _qi_text(node):
    """A qualified_identifier node -> its dotted text ('java.text.SimpleDateFormat')."""
    return node.text.decode().strip()


def _decl_name(node):
    """The declared name of a top-level class/object/function/property declaration."""
    direct = next((c for c in node.children if c.type == "identifier"), None)
    if direct is not None:
        return direct.text.decode()
    vd = next((c for c in node.children if c.type == "variable_declaration"), None)   # property
    if vd is not None:
        ident = next((c for c in vd.children if c.type == "identifier"), None)
        if ident is not None:
            return ident.text.decode()
    return None


def file_header(root):
    """Parse a source file's header -> {package, imports {simple: fqn}, wildcards [pkg], aliases}.
    Handles `import a.b.C`, `import a.b.C as D`, and `import a.b.C.*`."""
    package, imports, wildcards = "", {}, []
    for c in root.children:
        if c.type in ("package_header", "package"):
            qi = next((k for k in c.children if k.type == "qualified_identifier"), None)
            if qi is not None:
                package = _qi_text(qi)
        elif c.type in ("import", "import_header"):
            qi = next((k for k in c.children if k.type == "qualified_identifier"), None)
            if qi is None:
                continue
            fqn = _qi_text(qi)
            if any(k.type == "*" for k in c.children):                 # import a.b.C.*
                wildcards.append(fqn)
            elif any(k.type == "as" for k in c.children):              # import a.b.C as D
                alias = next((k.text.decode() for k in c.children if k.type == "identifier"), None)
                if alias:
                    imports[alias] = fqn
            else:                                                      # import a.b.C
                imports[fqn.rsplit(".", 1)[-1]] = fqn
    return {"package": package, "imports": imports, "wildcards": wildcards}


def top_level_names(root):
    """The names a source file declares at the top level (its public surface to other files)."""
    kinds = ("class_declaration", "object_declaration", "function_declaration", "property_declaration")
    return [n for n in (_decl_name(c) for c in root.children if c.type in kinds) if n]


def app_symbols(kt_root):
    """{declared name -> relative module path that declares it} across every .kt under kt_root.
    The module path mirrors the file tree (data/db/WorkoutDatabase.kt -> data/db/WorkoutDatabase)."""
    syms = {}
    for path in glob.glob(os.path.join(kt_root, "**", "*.kt"), recursive=True):
        if os.sep + "build" + os.sep in path or path.endswith("Test.kt"):
            continue
        rel = os.path.relpath(path, kt_root)[:-3].replace(os.sep, "/")
        root = parse(open(path, "rb").read()).root_node
        for nm in top_level_names(root):
            syms.setdefault(nm, rel)
    return syms


# ---- smoke test: print the resolve-phase tables for the WFL copy -------------------------------- #
if __name__ == "__main__":
    import collections
    KT = os.path.expanduser(
        "~/Programming/WFL_MixingCenter/WFL/app/src/main/java/com/sara/workoutforlife")
    by_origin = collections.Counter()
    external_names = collections.defaultdict(set)
    files = [p for p in glob.glob(os.path.join(KT, "**", "*.kt"), recursive=True)
             if os.sep + "build" + os.sep not in p]
    for path in files:
        h = file_header(parse(open(path, "rb").read()).root_node)
        for name, fqn in h["imports"].items():
            o = origin(fqn)
            if o != "app":
                by_origin[o] += 1
                external_names[o].add(name)
        for w in h["wildcards"]:
            if origin(w) != "app":
                by_origin[origin(w) + " (.*)"] += 1
    syms = app_symbols(KT)
    print(f"files scanned          : {len(files)}")
    print(f"app symbols (decls)    : {len(syms)}   e.g. " +
          ", ".join(f"{k}->{v}" for k, v in list(syms.items())[:3]))
    print("\nexternal imports by origin (the wrapper buckets):")
    for o, n in by_origin.most_common():
        ex = ", ".join(sorted(external_names[o])[:5]) if o in external_names else ""
        print(f"  {n:4d}  {o:24s} {ex}")
