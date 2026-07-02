"""loader.py -- per-file namespaces for the transpiled foundation (Kotlin file-visibility semantics).

THE CAUSE THIS FIXES: the old loaders exec'd all 254 files into ONE dict, so same-named top-level helpers
from different files overwrote each other (SettingsScreen's private SectionHeader got another file's;
ReportBugViewModel's UiState got LogCardio's) -- which one won depended on load order.

THE MODEL (matching Kotlin): each file executes in its OWN namespace. A name used in a file resolves:
  1. the file's own definitions (a private helper always means the one in this file),
  2. the runtime (the seeded wrapper names),
  3. lazily, on first use, via __missing__:
       a. a unique same-package (same-directory) definition,
       b. a unique definition anywhere in the app,
       c. ambiguous -> the file's own Kotlin import table decides (parsed from the matching .kt).
Resolution is LAZY (at first actual use, not at load), which also dissolves load-order and circular-
reference problems; a multipass sweep retries files whose module-level code needed a not-yet-loaded name.

    from loader import Loader
    ld = Loader(); ld.load_all()
    ns = ld.aggregate()          # merged view for harness lookups (screen/VM names are unique)
"""
import ast
import os
import sys
import glob

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import registry   # noqa: E402

ROOT = os.path.expanduser("~/Programming/WFL_MixingCenter")
KT = os.path.join(ROOT, "WFL/app/src/main/java/com/sara/workoutforlife")
APP_PKG = "com.sara.workoutforlife"


def _decl_names(node):
    if isinstance(node, (ast.ClassDef, ast.FunctionDef, ast.AsyncFunctionDef)):
        return [node.name]
    if isinstance(node, ast.Assign):
        return [t.id for t in node.targets if isinstance(t, ast.Name)]
    if isinstance(node, ast.AnnAssign) and isinstance(node.target, ast.Name):
        return [node.target.id]
    return []


class _FileNS(dict):
    """One file's namespace: own defs + runtime seed; anything else resolves lazily via the loader."""
    def __init__(self, loader, key):
        super().__init__(loader._runtime)
        self._loader, self._key = loader, key
        self["__name__"] = key[:-3].replace(os.sep, ".")

    def __missing__(self, k):
        v = self._loader.resolve(self._key, k)       # KeyError here surfaces as NameError at the use site
        self[k] = v
        return v


class Loader:
    def __init__(self, root=ROOT):
        self._runtime = registry.namespace()
        self.root = root
        self.paths = sorted(f for f in glob.glob(root + "/**/*.py", recursive=True)
                            if "/WFL/" not in f and "/__pycache__/" not in f
                            and "/render/" not in f and "/.appdata/" not in f)
        self.keys = [os.path.relpath(p, root) for p in self.paths]
        self.code, self.symbols, self.wants = {}, {}, {}
        for p, k in zip(self.paths, self.keys):
            src = open(p).read()
            self.code[k] = src
            try:
                tree = ast.parse(src)
            except SyntaxError:
                continue
            own = set()
            for n in tree.body:
                for nm in _decl_names(n):
                    own.add(nm)
                    self.symbols.setdefault(nm, [])
                    if k not in self.symbols[nm]:
                        self.symbols[nm].append(k)
            # every name the file READS but doesn't define -- pre-bound eagerly at load, because a CLASS
            # body's lookups (e.g. a default value `unit=WeightUnit.KG`) bypass __missing__ entirely.
            self.wants[k] = {n.id for n in ast.walk(tree)
                             if isinstance(n, ast.Name) and isinstance(n.ctx, ast.Load)} - own
        self.ns, self.loaded, self.loading, self.failed = {}, set(), set(), {}
        self._headers = {}

    # ---- name resolution (the Kotlin-visibility rules) ------------------------------------------ #
    def resolve(self, key, name):
        cands = [c for c in self.symbols.get(name, []) if c != key]   # own defs are already in the dict
        if not cands:
            raise KeyError(name)
        if len(cands) > 1:
            pkg = os.path.dirname(key)
            same = [c for c in cands if os.path.dirname(c) == pkg]
            cands = same if len(same) == 1 else (self._by_import(key, name, cands) or cands)
        if len(cands) != 1:
            raise KeyError(name)                     # ambiguous and no import decides -> fail honestly
        target = cands[0]
        self.load(target)
        d = self.ns.get(target)
        if d is not None and dict.__contains__(d, name):
            return dict.__getitem__(d, name)
        raise KeyError(name)                         # target mid-load and not yet defined -> multipass retries

    def _by_import(self, key, name, cands):
        """The file's Kotlin import table as tiebreak: `import com.sara...pkg.Name` -> the candidate in
        that package's directory."""
        h = self._header(key)
        fqn = (h or {}).get("imports", {}).get(name)
        if fqn and fqn.startswith(APP_PKG + "."):
            rel = os.path.dirname(os.path.join(*fqn[len(APP_PKG) + 1:].split(".")))
            hit = [c for c in cands if os.path.dirname(c) == rel]
            if len(hit) == 1:
                return hit
        for pkg in (h or {}).get("wildcards", []):   # `import com.sara...pkg.*`
            if pkg.startswith(APP_PKG):
                rel = os.path.join(*pkg[len(APP_PKG) + 1:].split(".")) if len(pkg) > len(APP_PKG) else ""
                hit = [c for c in cands if os.path.dirname(c) == rel]
                if len(hit) == 1:
                    return hit
        return None

    def _header(self, key):
        if key not in self._headers:
            self._headers[key] = None
            kt = os.path.join(KT, key[:-3] + ".kt")
            if os.path.exists(kt):
                try:
                    import resolve
                    from parse import parse
                    self._headers[key] = resolve.file_header(parse(open(kt, "rb").read()).root_node)
                except Exception:                    # noqa: BLE001 -- no header -> no tiebreak
                    pass
        return self._headers[key]

    # ---- execution ------------------------------------------------------------------------------ #
    def load(self, key):
        if key in self.loaded or key in self.loading:
            return
        self.loading.add(key)
        nsd = _FileNS(self, key)                     # fresh per attempt: module code is not re-exec-safe
        self.ns[key] = nsd
        for name in self.wants.get(key, ()):         # eager pre-bind (class bodies bypass __missing__);
            if not dict.__contains__(nsd, name):     # unresolvable ones stay lazy / heal on a later pass
                try:
                    dict.__setitem__(nsd, name, self.resolve(key, name))
                except KeyError:
                    pass
        try:
            exec(compile(self.code[key], os.path.join(self.root, key), "exec"), nsd)
            self.loaded.add(key)
            self.failed.pop(key, None)
        except Exception as e:                       # noqa: BLE001 -- recorded; multipass retries
            self.failed[key] = e
        finally:
            self.loading.discard(key)

    def load_all(self, passes=10):
        for _ in range(passes):
            pending = [k for k in self.keys if k not in self.loaded]
            if not pending:
                break
            for k in pending:
                self.load(k)
        return self

    def aggregate(self):
        """A merged name -> value view for harness lookups (screens/VMs -- app-unique names)."""
        out = {}
        for k in self.keys:
            d = self.ns.get(k)
            if d is not None:
                out.update((n, v) for n, v in dict.items(d) if not n.startswith("__"))
        return out


if __name__ == "__main__":
    ld = Loader().load_all()
    ui = [k for k in ld.keys if k.startswith("ui" + os.sep)]
    core = [k for k in ld.keys if not k.startswith("ui" + os.sep)]
    print(f"non-UI loaded: {sum(1 for k in core if k in ld.loaded)} / {len(core)}")
    print(f"ui loaded    : {sum(1 for k in ui if k in ld.loaded)} / {len(ui)}")
    for k, e in list(ld.failed.items())[:8]:
        print(f"  FAIL {k}: {type(e).__name__}: {str(e)[:70]}")