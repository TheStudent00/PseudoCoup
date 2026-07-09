"""idgen.py -- Kotlin-side unique-id generator (Phase 1).

For every node in the Kotlin UI containment tree

    module/file -> class/object -> function/method (incl. @Composable) ->
    composable CALL SITES inside a composable body (Button, Icon, Text,
    Card, custom composables, ...)

this assigns a UNIQUE id that is a positional branch path through the
tree-sitter parse tree, and proves that path is unique across the whole
UI tree.

THE ID (this is the whole point):
  Walk the tree-sitter parse tree top-down. Each node's id SEGMENT is
      "<childIndex>:<nodeKind>"
  where childIndex is the node's index among ALL of its parent's children
  (tree-sitter's own `node.children`, named AND anonymous alike) -- recorded
  at EVERY node, unconditionally. There is no fallback-to-anchor and no
  anchor-replaces-index special case anywhere in this walk (that was the bug
  in ui_ledger.py's `_segment`: it used the child index only when no content
  anchor -- composable name, field label, icon desc, Text literal -- was
  available, so identical siblings with the same anchor collided).

  The id of a node = the "/"-joined segments from the tree ROOT (the
  source_file) down to that node, e.g.

      0:file/2:class_declaration/1:function_declaration/3:call_expression/0:call_expression

  A human-readable anchor (composable name, Text literal, contentDescription,
  field label) MAY be attached as separate metadata for readability/debugging,
  but it is never part of, and never substitutes for, the positional segment.

SCOPE: records are emitted for the containment-tree node kinds the plan
cares about -- source_file (module/file root), class_declaration /
object_declaration, function_declaration (incl. @Composable), and
call_expression (composable call sites, at any nesting depth inside a
composable body: directly, or through if/when/lambda/binary-expression
wrappers -- Kotlin/Compose control flow does not stop a call site from being
a real widget node). Every OTHER node kind on the path (blocks, lambdas,
value_arguments, operators, ...) still consumes a position in the index
count and in the walk (the walker recurses into everything), it is simply
not emitted as its own record. This keeps the id a faithful positional path
through the REAL tree-sitter tree (matching the shape tree-sitter itself
exposes) while keeping the output focused on the nodes the plan calls "the
containment tree".

Runtime per-instance disambiguation (repeated renders of the same call site
in a loop) is explicitly OUT of scope here -- Phase 2's concern. This module
only proves STATIC id assignment is unique.

Usage:
    python3 idgen.py FILE.kt              # print records for one file
    python3 idgen.py --scan               # walk the whole UIROOT, print a summary
    python3 idgen.py --check              # --scan + assert uniqueness (exit 1 on dup)
"""
import argparse
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import oracle as O                          # noqa: E402  (MAIN, CORPUS)
from parse import parse                     # noqa: E402

UIROOT = os.path.join(O.MAIN, "java", "com", "sara", "workoutforlife", "ui")

# Node kinds that get their own record in the containment tree.
FILE_KIND = "source_file"
CONTAINER_KINDS = ("class_declaration", "object_declaration")
FUNCTION_KIND = "function_declaration"
CALL_KIND = "call_expression"
RECORD_KINDS = (FILE_KIND, ) + CONTAINER_KINDS + (FUNCTION_KIND, CALL_KIND)


def _is_composable(fn_node):
    mods = next((k for k in fn_node.children if k.type == "modifiers"), None)
    return bool(mods and "@Composable" in mods.text.decode())


def _fn_name(fn_node):
    idc = next((k for k in fn_node.children if k.type == "identifier"), None)
    return idc.text.decode() if idc else None


def _call_name(call_node):
    """the callee name of a call_expression, whether it's a bare call
    (`Text(...)`) or the outer wrapper of a trailing-lambda call
    (`Card(...) { ... }` parses as call_expression[call_expression, lambda])."""
    inner = next((k for k in call_node.children if k.type == "call_expression"), None)
    base = inner if inner is not None else call_node
    idc = next((k for k in base.children if k.type == "identifier"), None)
    if idc:
        return idc.text.decode()
    nav = next((k for k in base.children if k.type == "navigation_expression"), None)
    return nav.text.decode() if nav is not None else None


def _text_anchor(call_node):
    """best-effort human-readable anchor for a call site: string-literal args
    (Text("..."), contentDescription = "..."), else None. Metadata ONLY --
    never part of the id."""
    for a in call_node.children:
        if a.type in ("call_expression",):
            r = _text_anchor(a)
            if r:
                return r
        if a.type == "value_arguments":
            for va in a.named_children:
                if va.type == "value_argument":
                    lit = next((k for k in va.children if k.type == "string_literal"), None)
                    if lit is not None:
                        return lit.text.decode()
    return None


class Record:
    __slots__ = ("id", "file", "start_byte", "end_byte", "start_point", "end_point",
                 "node_kind", "anchor")

    def __init__(self, id_, file_, node, node_kind, anchor):
        self.id = id_
        self.file = file_
        self.start_byte = node.start_byte
        self.end_byte = node.end_byte
        self.start_point = node.start_point   # (row, col), 0-based
        self.end_point = node.end_point
        self.node_kind = node_kind
        self.anchor = anchor

    def as_dict(self):
        return {
            "id": self.id,
            "file": self.file,
            "start_byte": self.start_byte,
            "end_byte": self.end_byte,
            "start_line": self.start_point[0] + 1,
            "start_col": self.start_point[1],
            "end_line": self.end_point[0] + 1,
            "end_col": self.end_point[1],
            "node_kind": self.node_kind,
            "anchor": self.anchor,
        }

    def __repr__(self):
        a = f" anchor={self.anchor!r}" if self.anchor else ""
        return f"<{self.id} {self.node_kind}{a}>"


def gen_ids_for_file(path, root_prefix_segs=None):
    """-> [Record] for one .kt file: the full positional-path walk of its
    tree-sitter tree, with a record emitted at every RECORD_KINDS node
    (file root, class/object, function incl. @Composable, and every
    call_expression -- the composable call sites -- at any depth).

    `root_prefix_segs` is the id segment list for the file's OWN position in
    the surrounding module tree (see `gen_ids_for_root`); the file's
    `source_file` node id is that prefix, and every node inside the file is
    addressed relative to it. When None (single-file / standalone use) the
    file is its own root at "0:source_file", exactly like ui_ledger's walk --
    NOTE this alone is not globally unique across multiple files (two files
    with an identical top few lines produce the identical local path) --
    `gen_ids_for_root` supplies the real prefix so ids are unique across the
    WHOLE UI tree, not just within one file.
    """
    src = open(path, "rb").read()
    tree = parse(src)
    root = tree.root_node
    out = []

    root_segs = root_prefix_segs if root_prefix_segs is not None else [f"0:{FILE_KIND}"]

    def walk(node, segs, node_kind_for_root=None):
        # segs already includes THIS node's own segment.
        this_kind = node_kind_for_root or node.type
        if this_kind in RECORD_KINDS:
            anchor = None
            if this_kind == FUNCTION_KIND:
                nm = _fn_name(node)
                anchor = (f"@Composable {nm}" if _is_composable(node) else nm) if nm else None
            elif this_kind == CALL_KIND:
                nm = _call_name(node)
                txt = _text_anchor(node)
                anchor = f"{nm}[{txt}]" if (nm and txt) else nm
            elif this_kind in CONTAINER_KINDS:
                idc = next((k for k in node.children if k.type == "identifier"), None)
                anchor = idc.text.decode() if idc else None
            out.append(Record("/".join(segs), path, node, this_kind, anchor))
        for i, c in enumerate(node.children):
            walk(c, segs + [f"{i}:{c.type}"])

    walk(root, root_segs, node_kind_for_root=FILE_KIND)
    return out


def gen_ids_for_root(uiroot=UIROOT):
    """-> ([Record], [file paths]) for every .kt file under uiroot.

    The id of a node is a positional path from the TRUE tree root, and the
    tree root here is the module tree: UIROOT is the root "module" node,
    each subdirectory is a "package" child, and each .kt file is a "file"
    child -- each addressed by its own index among ITS parent's (sorted,
    deterministic) children, same rule as every other node ("<idx>:<kind>",
    unconditionally). Without this, two files with structurally identical
    prefixes (e.g. two ViewModels that both start `class X { val _state =
    MutableStateFlow(...) }`) would produce identical LOCAL ids -- the file
    itself has to be a positioned node, not an implicit, uncounted, "0:"
    restart, or uniqueness only holds within one file, not across the tree.
    """
    out = []
    files = []

    def walk_dir(dirpath, segs):
        entries = sorted(os.listdir(dirpath))
        dirs = [e for e in entries if os.path.isdir(os.path.join(dirpath, e))]
        kt_files = [e for e in entries if e.endswith(".kt")]
        # index children in one deterministic combined order: subdirectories
        # first (alpha), then files (alpha) -- as long as it's stable and
        # unconditional it satisfies "index at every node"; order choice
        # itself carries no special meaning.
        idx = 0
        for d in dirs:
            walk_dir(os.path.join(dirpath, d), segs + [f"{idx}:package"])
            idx += 1
        for fname in kt_files:
            fpath = os.path.join(dirpath, fname)
            files.append(fpath)
            file_segs = segs + [f"{idx}:{FILE_KIND}"]
            out.extend(gen_ids_for_file(fpath, root_prefix_segs=file_segs))
            idx += 1

    walk_dir(uiroot, [])
    return out, files


def check_uniqueness(records):
    """-> (ok: bool, total: int, distinct: int, dupes: {id: [Record,...]})"""
    by_id = {}
    for r in records:
        by_id.setdefault(r.id, []).append(r)
    dupes = {k: v for k, v in by_id.items() if len(v) > 1}
    return (len(dupes) == 0), len(records), len(by_id), dupes


def _print_records(records, limit=None):
    for r in records[:limit] if limit else records:
        rel = os.path.relpath(r.file, UIROOT)
        print(f"{r.id}\t{r.node_kind}\t{rel}:{r.start_point[0]+1}\t{r.anchor or ''}")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("file", nargs="?", help="a single .kt file (absolute or relative to UIROOT)")
    ap.add_argument("--scan", action="store_true", help="walk the whole UIROOT, print a summary")
    ap.add_argument("--check", action="store_true",
                     help="--scan + assert global uniqueness (nonzero exit on duplicate ids)")
    args = ap.parse_args()

    if args.check or args.scan:
        records, files = gen_ids_for_root()
        ok, total, distinct, dupes = check_uniqueness(records)
        n_files = len(files)
        print(f"idgen: scanned {n_files} .kt files under {UIROOT}")
        print(f"idgen: total nodes (records) = {total}, distinct ids = {distinct}, "
              f"duplicate ids = {len(dupes)}")
        by_kind = {}
        for r in records:
            by_kind[r.node_kind] = by_kind.get(r.node_kind, 0) + 1
        for k in RECORD_KINDS:
            print(f"idgen:   {k}: {by_kind.get(k, 0)}")
        if dupes:
            print(f"idgen: FAIL -- {len(dupes)} duplicate id(s):")
            for id_, recs in list(dupes.items())[:20]:
                print(f"  {id_}")
                for r in recs:
                    print(f"    {os.path.relpath(r.file, UIROOT)}:{r.start_point[0]+1} {r.node_kind} {r.anchor}")
            if args.check:
                sys.exit(1)
        else:
            print("idgen: OK -- all ids unique")
        return

    if args.file:
        path = args.file if os.path.isabs(args.file) else os.path.join(UIROOT, args.file)
        records = gen_ids_for_file(path)
        _print_records(records)
        ok, total, distinct, dupes = check_uniqueness(records)
        print(f"# {total} records, {distinct} distinct ids, {len(dupes)} duplicate ids", file=sys.stderr)
        return

    ap.print_help()


if __name__ == "__main__":
    main()
