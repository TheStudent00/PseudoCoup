"""inject_emitid.py -- Phase 2 injector (provisional name/shape).

Splices a `com.sara.workoutforlife.core.debug.WalkEmit.emitId("<id>")` statement immediately
BEFORE each cleanly-injectable composable CALL SITE `idgen.py` assigned an id to, so that id is
proven to actually fire at Compose runtime (not just proven unique statically -- that was Phase 1's
job; see idgen.py's own module docstring: "Runtime per-instance disambiguation ... is explicitly OUT
of scope here -- Phase 2's concern").

WHAT "CLEANLY INJECTABLE" MEANS (Kotlin/Compose statement-position vs argument-position):

  tree-sitter-kotlin parses a composable call site as a `call_expression` node (see idgen.py's own
  RECORD_KINDS / CALL_KIND). Inserting a bare statement (`WalkEmit.emitId("...")` followed by `;` or
  a newline) immediately before that node's start byte is only LEGAL KOTLIN when the call itself sits
  in STATEMENT position, i.e. its immediate parent is one of:

    - "block"           -- a `{ ... }` function/if/lambda BODY that tree-sitter-kotlin parses with an
                            explicit `block` wrapper (function bodies, `if`/`else` bodies, plain
                            trailing-lambda bodies with no parameter list before `->`).
    - "lambda_literal"   -- a lambda literal's OWN body when tree-sitter-kotlin does NOT interpose a
                            `block` node under it (observed directly for both parameterless
                            `{ Text(...) }` -form lambdas AND `{ program -> ... }` -form lambdas with
                            an explicit parameter list -- see this file's own investigation notes /
                            the walk-through in this session). Both shapes are real Compose "trailing
                            lambda content" bodies (`items(...) { program -> ProgramCard(...) }`,
                            `topBar = { TopAppBar(...) }`'s OWN callee's inner call), so both are
                            legitimate statement-position injection points.
    - "source_file"      -- a bare top-level call (rare in this codebase, included for completeness/
                            symmetry with idgen.py's own root handling).

  A call whose parent is any of the following is an ARGUMENT (or an inner wrapper node), and is
  SKIPPED -- inserting a statement there would either put a statement where an expression is
  syntactically required (not legal Kotlin) or duplicate an id on a call_expression that idgen.py
  itself does not treat as the "real" outer call:

    - "value_argument" / "value_arguments"  -- the call is itself a bare positional/named argument
      expression, e.g. `LabeledField(label = "x") { CompactValueField(...) }` -- here the CALL is
      fine (its own PARENT inside the trailing lambda is 'lambda_literal', injectable), but a call
      passed bare as `foo(Bar())` (Bar() as a value_argument's own expression) is not: `Bar()` sits
      where an expression must be, not a statement.
    - "property_declaration"  -- `val y = Foo()` -- Foo() is the initializer expression, not a
      statement; injecting before it would break `val x = <stmt> Foo()`, not legal Kotlin.
    - "call_expression"  -- the OUTER-wrapper shape idgen.py's own `_call_name()`/`_text_anchor()`
      already special-cases: `Card(...) { ... }` parses as `call_expression[call_expression,
      annotated_lambda]` -- the INNER call_expression (the bare `Card(...)` callee+args, no lambda)
      is a structural child of the OUTER call_expression, not a statement in a block. idgen.py issues
      an id to the OUTER node (the one that actually spans the whole `Card(...) { ... }` call); the
      inner wrapper node is a different tree position and is skipped here to avoid a confusing
      double-emit for what is really one logical call site.
    - anything else not in the explicit ALLOWED_PARENTS set (binary_expression operands,
      elvis/safe-call receivers, when-branch bare expressions, etc.) -- conservatively skipped;
      "do not produce code that won't parse" (this file's own mandate) outweighs maximizing coverage.

  Every SKIPPED call site is recorded with its id and a reason string (see `SkipReason`) rather than
  silently dropped -- `main()`'s report prints a per-reason tally, and `inject_file()` returns the
  full list for a caller (or a future test) that wants the detail.

INSERTION MECHANICS: a single file's edits are collected as (byte_offset, text) pairs and applied in
ONE pass, highest offset first (so earlier offsets stay valid as later insertions are spliced in) --
never re-parsing/re-walking after each edit. The inserted text is
`WalkEmit.emitId("<id>")\n<original indentation>` reusing the target call's own start-of-line
indentation (read from the source directly) so the spliced statement lines up with the code around
it -- cosmetic, but keeps a `git diff` of an instrumented file readable.

IMPORT: `inject_file()` also ensures the file imports
`com.sara.workoutforlife.core.debug.WalkEmit` (inserted after the `package` line, or after the last
existing `import` line if any, whichever is later) -- added at most once per file, and left alone if
already present (idempotent re-run).

USAGE:
    python3 inject_emitid.py FILE.kt                  # instrument one file IN PLACE, print a report
    python3 inject_emitid.py FILE.kt --dry-run         # report only, no write
    python3 inject_emitid.py FILE.kt --out OTHER.kt    # write instrumented source elsewhere

This module deliberately instruments ONE file per invocation -- Phase 2's task scope is "instrument
ONE screen only" (see DevComms task notes); a whole-app sweep is future work, not attempted here.
"""
import argparse
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import idgen as I                            # noqa: E402
from parse import parse                      # noqa: E402

EMIT_IMPORT = "import com.sara.workoutforlife.core.debug.WalkEmit"

# Parents a call_expression may sit under and still be a legal statement-position injection point.
ALLOWED_PARENTS = ("block", "lambda_literal", "source_file")


class SkipReason:
    ARGUMENT = "argument-position (value_argument/value_arguments parent)"
    INITIALIZER = "initializer-position (property_declaration RHS)"
    INNER_TRAILING_LAMBDA_WRAPPER = "inner call_expression of a Foo(...) { } trailing-lambda wrapper"
    OTHER_PARENT = "other non-statement parent"


def _skip_reason(parent_kind):
    if parent_kind in ("value_argument", "value_arguments"):
        return SkipReason.ARGUMENT
    if parent_kind == "property_declaration":
        return SkipReason.INITIALIZER
    if parent_kind == "call_expression":
        return SkipReason.INNER_TRAILING_LAMBDA_WRAPPER
    return SkipReason.OTHER_PARENT


def _line_indent(src_text, start_byte):
    """-> the whitespace prefix of the line containing start_byte, as a str, for cosmetic alignment
    of the inserted emitId(...) statement with the call site it precedes."""
    line_start = src_text.rfind("\n", 0, start_byte) + 1
    i = line_start
    while i < len(src_text) and src_text[i] in " \t":
        i += 1
    return src_text[line_start:i]


def plan_injections(path):
    """-> (records_to_inject: [(Record, parent_kind)], skipped: [(Record, reason)])

    Re-walks the SAME tree idgen.gen_ids_for_file() walks (single-file mode: ids are local to this
    file, exactly like idgen.py's own single-file CLI path -- root_prefix_segs=None), this time also
    recording each CALL_KIND node's tree-sitter PARENT kind, which idgen's own Record does not carry.
    Every CALL_KIND record from idgen's real id assignment is preserved verbatim (same id string) --
    this function only ADDS the injectability classification, it does not recompute or renumber ids.
    """
    src = open(path, "rb").read()
    tree = parse(src)
    root = tree.root_node

    # id -> tree-sitter node, built by re-running idgen's exact walk (so ids match 1:1) but keeping a
    # handle to the live node (idgen.Record intentionally does not keep a node reference beyond byte
    # offsets, so we recompute this ourselves rather than reaching into Record internals).
    node_by_id = {}

    def walk(node, segs, node_kind_for_root=None):
        this_kind = node_kind_for_root or node.type
        if this_kind in I.RECORD_KINDS:
            node_by_id["/".join(segs)] = node
        for i, c in enumerate(node.children):
            walk(c, segs + [f"{i}:{c.type}"])

    walk(root, [f"0:{I.FILE_KIND}"], node_kind_for_root=I.FILE_KIND)

    records = I.gen_ids_for_file(path)  # authoritative id list (unchanged from Phase 1)
    to_inject = []
    skipped = []
    for r in records:
        if r.node_kind != I.CALL_KIND:
            continue
        node = node_by_id.get(r.id)
        if node is None or node.parent is None:
            skipped.append((r, SkipReason.OTHER_PARENT))
            continue
        parent_kind = node.parent.type
        if parent_kind in ALLOWED_PARENTS:
            to_inject.append((r, node, parent_kind))
        else:
            skipped.append((r, _skip_reason(parent_kind)))
    return to_inject, skipped


def inject_file(path, out_path=None, dry_run=False):
    """Instrument one .kt file in place (or write to `out_path`). -> (n_injected, skipped, out_text)"""
    to_inject, skipped = plan_injections(path)

    src_bytes = open(path, "rb").read()
    src_text = src_bytes.decode("utf-8")

    # One insertion per injectable call: `WalkEmit.emitId("<id>")\n<indent>` spliced right before the
    # call's own start byte, reusing that line's indentation for a clean diff.
    edits = []  # (byte_offset, text_to_insert)
    for r, node, _parent_kind in to_inject:
        indent = _line_indent(src_text, node.start_byte)
        stmt = f'WalkEmit.emitId("{r.id}")\n{indent}'
        edits.append((node.start_byte, stmt))

    # Highest offset first so earlier offsets/nodes stay valid while we splice.
    edits.sort(key=lambda e: e[0], reverse=True)
    out_bytes = src_bytes
    for offset, text in edits:
        out_bytes = out_bytes[:offset] + text.encode("utf-8") + out_bytes[offset:]

    out_text = out_bytes.decode("utf-8")
    out_text = _ensure_import(out_text)

    if not dry_run:
        target = out_path or path
        with open(target, "w", encoding="utf-8") as f:
            f.write(out_text)

    return len(to_inject), skipped, out_text


def _ensure_import(text):
    if EMIT_IMPORT in text:
        return text
    lines = text.split("\n")
    insert_at = None
    last_import = None
    for i, line in enumerate(lines):
        if line.startswith("package "):
            insert_at = i + 1
        if line.startswith("import "):
            last_import = i
    if last_import is not None:
        insert_at = last_import + 1
    if insert_at is None:
        insert_at = 0
    lines.insert(insert_at, EMIT_IMPORT)
    return "\n".join(lines)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("file", help="a single .kt file (absolute or relative to cwd)")
    ap.add_argument("--dry-run", action="store_true", help="report only, do not write")
    ap.add_argument("--out", default=None, help="write instrumented source to a different path")
    args = ap.parse_args()

    path = args.file if os.path.isabs(args.file) else os.path.abspath(args.file)
    n_injected, skipped, _out_text = inject_file(path, out_path=args.out, dry_run=args.dry_run)

    print(f"inject_emitid: {path}")
    print(f"inject_emitid: injected {n_injected} emitId(...) call site(s)")
    by_reason = {}
    for r, reason in skipped:
        by_reason.setdefault(reason, []).append(r)
    print(f"inject_emitid: skipped {len(skipped)} call site(s)")
    for reason, recs in by_reason.items():
        print(f"inject_emitid:   {len(recs)}x -- {reason}")
        for r in recs[:5]:
            rel = os.path.relpath(r.file)
            print(f"inject_emitid:     {rel}:{r.start_point[0]+1} {r.anchor or ''}")
        if len(recs) > 5:
            print(f"inject_emitid:     ... and {len(recs) - 5} more")
    if args.dry_run:
        print("inject_emitid: --dry-run, no file written")
    else:
        print(f"inject_emitid: wrote {args.out or path}")


if __name__ == "__main__":
    main()
