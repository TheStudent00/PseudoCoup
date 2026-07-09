"""inject_emitid.py -- Phase 5 injector (walkId stamping; supersedes the Phase 2 preceding-statement
shape this file used to have -- see git history for that version).

PHASE 5 DECISION (owner-made, see WalkEmit.kt's module doc / DevComms task notes): the walker's target
IDENTITY moved off (label, handlerKind, boundsKey) heuristics onto a node's actual RUNTIME identity,
`"<idgen id>#<instance index>"`, carried as a dedicated Compose semantics property (`WalkId`, see
core/debug/WalkEmit.kt) that the walk harness reads straight off `SemanticsNode.config`. This file's
job changed to match: instead of splicing a `WalkEmit.emitId("<id>")` STATEMENT immediately before each
injectable composable CALL SITE, it now STAMPS the call itself by attaching
`.walkTag("<id>")` to that call's `modifier` ARGUMENT --

  - if the call already passes `modifier = <expr>` (named) OR a bare positional `Modifier`-rooted
    expression (Compose's own "modifier is the first unnamed parameter" convention, e.g.
    `Box(Modifier.fillMaxSize(), contentAlignment = ...)` -- see `_positional_modifier_arg`): rewritten
    in place to `...expr.walkTag("<id>")` (chained onto whatever modifier chain was already there --
    `.walkTag()` is just another Modifier extension, so this is exactly as safe as any other
    `.something()` appended to an existing chain). Both shapes are handled identically once found --
    detecting the positional form is NOT optional: skipping it would silently fall through to the
    "add a new named `modifier =` argument" branch below and produce a DUPLICATE modifier parameter
    (a real compile error), not a merely-missed opportunity.
  - if the call has NO existing modifier argument (named OR positional) but is a composable call this
    file can POSITIVELY
    confirm plausibly takes one (see "WHAT COUNTS AS A SAFE MODIFIER-ADD TARGET" below): a new
    `modifier = Modifier.walkTag("<id>")` named argument is appended to its (non-empty-syntax)
    argument list.
  - otherwise: SKIPPED, with a reason recorded (see `SkipReason`) -- "do not produce code that won't
    parse, and do not guess at a callee's parameter list without positive syntactic evidence" outweighs
    maximizing coverage, exactly as this file's Phase 2 predecessor already held for statement-position
    injection legality.

WHAT COUNTS AS A SAFE MODIFIER-ADD TARGET (no `modifier = <expr>` argument already present):

  tree-sitter-kotlin has no type information -- it cannot tell us whether some callee `Foo(...)`
  actually declares a `modifier: Modifier = Modifier` parameter. Absent that, this file uses two
  purely-syntactic signals, BOTH required:

    1. The call's own PARENTHESIZED argument list must already exist in source (`value_arguments` is
       present, i.e. the call spells `Foo(...)`, not bare `Foo { ... }` with no parens at all). Adding
       a modifier argument to a call with NO existing parens would also require inserting a fresh
       `()` pair -- a strictly riskier edit (two insertion points instead of one, and a bare
       `Foo { ... }` skipped-lambda shape is easy to mis-splice against an `annotated_lambda` sibling).
       Conservatively SKIPPED (`SkipReason.NO_ARG_LIST`) -- rare in practice (1 site total across both
       Phase 5 screens; confirmed by direct count before writing this rule).
    2. The call's own callee must be a BARE `identifier` (not a `navigation_expression` like
       `item.durationMinutes?.let` or `viewModel.selectTab`, which are scope-function/method calls, not
       composable invocations) whose first character is UPPERCASE -- this codebase's own Kotlin/Compose
       naming convention (`Text`, `Row`, `WflCard`, `MetricStat`, `AnalyticsContent`, `FilterChip`, ...
       are all PascalCase; `repeat`, `mutableStateOf`, `remember`, `LaunchedEffect`'s OWN callee is
       actually PascalCase too and IS a legitimate positive here even though it takes no Modifier in
       practice -- see the false-positive note below) are camelCase/lowercase. Confirmed directly
       against both Phase 5 screens' full CALL_KIND record list: every camelCase/receiver-navigation
       call site in that survey (`repeat`, `mutableStateOf`, `item.durationMinutes?.let`,
       `viewModel.selectTab`, `points.forEachIndexed`, ...) is a plain Kotlin stdlib/scope-function
       call, never a Compose UI composable -- PascalCase is a reliable (if not perfect) discriminator
       IN THIS CODEBASE's own convention.

  KNOWN FALSE-POSITIVE RISK, accepted deliberately: a small number of PascalCase, parenthesized calls
  are Composable functions that do NOT declare a `modifier` parameter at all (`LaunchedEffect(Unit) { }`,
  `CircularProgressIndicator()` variants without one, etc.) -- adding `modifier = Modifier.walkTag(id)`
  to such a call is a REAL compile error (unresolved parameter), not silently wrong. This is why
  RE-INSTRUMENTATION MUST tree-sitter-PARSE-CHECK (already required) but is NOT sufficient on its own --
  the task's own step 3 additionally required the actual gradle host-run compile+test to be the real
  correctness gate (queued as hostrun 181, not run in this sandbox). If host compilation surfaces an
  unresolved-parameter error on one of these PascalCase-no-existing-modifier adds, the fix is to add
  that specific callee name to `NO_MODIFIER_PARAM` below (a small denylist of confirmed
  Compose calls known NOT to take `Modifier`, e.g. `LaunchedEffect`), not to weaken the general rule.

INSERTION MECHANICS: unchanged in spirit from the Phase 2 file -- a single file's edits are collected as
(byte_offset, text) pairs and applied in ONE pass, highest offset first, never re-parsing/re-walking
after each edit.

IMPORT: `inject_file()` still ensures the file imports `com.sara.workoutforlife.core.debug.WalkEmit`
(needed for `WalkEmit.tag`, referenced transitively through `Modifier.walkTag`) AND now additionally
`com.sara.workoutforlife.core.debug.walkTag` (the extension function itself -- Kotlin does not resolve
an extension function through a wildcard/object import the way `WalkEmit.emitId(...)`'s qualified call
did, so this is a genuinely NEW required import, not cosmetic) -- both inserted after the `package` line
or after the last existing `import` line, whichever is later, added at most once per file, idempotent.

USAGE:
    python3 inject_emitid.py FILE.kt                  # instrument one file IN PLACE, print a report
    python3 inject_emitid.py FILE.kt --dry-run         # report only, no write
    python3 inject_emitid.py FILE.kt --out OTHER.kt    # write instrumented source elsewhere

This module deliberately instruments ONE file per invocation -- same single-screen scope as its Phase 2
predecessor; a whole-app sweep is future work, not attempted here.
"""
import argparse
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import idgen as I                            # noqa: E402
from parse import parse                      # noqa: E402

WALKEMIT_IMPORT = "import com.sara.workoutforlife.core.debug.WalkEmit"
WALKTAG_IMPORT = "import com.sara.workoutforlife.core.debug.walkTag"
REQUIRED_IMPORTS = (WALKEMIT_IMPORT, WALKTAG_IMPORT)

# Confirmed-by-name Compose calls that are PascalCase, parenthesized, but do NOT declare a `modifier`
# parameter -- see module doc "KNOWN FALSE-POSITIVE RISK". Grown as real compile failures surface;
# empty/aspirational at authoring time is fine (see that same doc section), the mechanism it plugs into
# already exists.
NO_MODIFIER_PARAM = frozenset({
    "LaunchedEffect",
    "DisposableEffect",
    "SideEffect",
    "remember",
    "rememberSaveable",
    "rememberCoroutineScope",
    "derivedStateOf",
    "produceState",
})


class SkipReason:
    NO_ARG_LIST = "no existing parenthesized argument list (bare `Foo { ... }`, unsafe to splice parens)"
    NOT_IDENTIFIER_CALLEE = "callee is not a bare identifier (navigation/receiver call, e.g. `x.let { }`)"
    NOT_PASCAL_CASE = "callee identifier is not PascalCase (stdlib/scope-function convention, not a composable)"
    KNOWN_NO_MODIFIER_PARAM = "callee is on the confirmed no-modifier-parameter denylist"
    UNRESOLVED_NODE = "id did not resolve to a live tree-sitter node (should not happen; defensive)"
    INNER_TRAILING_LAMBDA_WRAPPER = ("inner call_expression of a Foo(...) { } trailing-lambda wrapper "
                                      "(same node/args the outer wrapper's own record already targets)")


def _line_indent(src_text, start_byte):
    """-> the whitespace prefix of the line containing start_byte, as a str. Unused for the modifier-arg
    rewrite itself (that edit is a same-line splice with no new line to indent), kept for parity/possible
    future multi-line insertions and because SkipReason reporting still wants source line numbers."""
    line_start = src_text.rfind("\n", 0, start_byte) + 1
    i = line_start
    while i < len(src_text) and src_text[i] in " \t":
        i += 1
    return src_text[line_start:i]


def _call_base_and_args(node):
    """-> (base_node, value_arguments_node_or_None) for a CALL_KIND node, unwrapping the
    `call_expression[call_expression, annotated_lambda]` outer-wrapper shape idgen.py's own
    `_call_name()` already special-cases (see idgen.py) -- the INNER call_expression carries the
    callee identifier + the real value_arguments; the OUTER node (what idgen.py assigns the id to) is
    just the wrapper spanning callee+args+trailing-lambda together."""
    inner = next((c for c in node.children if c.type == "call_expression"), None)
    base = inner if inner is not None else node
    va = next((c for c in base.children if c.type == "value_arguments"), None)
    return base, va


def _existing_modifier_arg(va_node):
    """-> the `value_argument` node for an existing `modifier = <expr>` argument, or None."""
    if va_node is None:
        return None
    for va in va_node.named_children:
        if va.type != "value_argument":
            continue
        idc = next((k for k in va.children if k.type == "identifier"), None)
        if idc is not None and idc.text.decode() == "modifier":
            return va
    return None


def _callee_identifier(base_node):
    """-> the bare `identifier` node naming this call's callee, or None if the callee is a
    navigation_expression (`x.y.let`) or anything else that is not a plain identifier."""
    return next((k for k in base_node.children if k.type == "identifier"), None)


def _leftmost_identifier_name(expr_node):
    """-> the name of the LEFTMOST plain `identifier` reachable by descending a chain of
    navigation_expression/call_expression FIRST children, or None. For `Modifier.padding(4.dp)
    .fillMaxWidth()` this walks call_expression -> navigation_expression -> call_expression ->
    navigation_expression -> identifier("Modifier") -- i.e. the RECEIVER the whole chain is rooted at,
    which is exactly what's needed to recognize a bare positional `Modifier` (or `Modifier`-chain)
    argument (see `_positional_modifier_arg`'s own doc: Compose's own convention of passing `modifier`
    as an unnamed first positional argument, e.g. `Box(Modifier.fillMaxSize(), ...)`)."""
    n = expr_node
    seen = set()
    while n is not None and id(n) not in seen:
        seen.add(id(n))
        if n.type == "identifier":
            return n.text.decode()
        if n.type in ("navigation_expression", "call_expression"):
            n = n.children[0] if n.children else None
        else:
            return None
    return None


def _positional_modifier_arg(va_node):
    """-> the `value_argument` node holding a bare (unnamed) `Modifier`-rooted expression passed as a
    positional argument (Compose's own "modifier is the first unnamed parameter" convention -- e.g.
    `Box(Modifier.fillMaxSize(), contentAlignment = ...)` or the bare `Box(Modifier, ...)` form), or
    None if no such positional argument exists. Treated the SAME as an explicit `modifier = <expr>`
    argument (see `classify`) -- appending `.walkTag(id)` to it is exactly as safe as the named-arg
    rewrite case, and NOT detecting this shape would have added a SECOND, conflicting `modifier =`
    named argument alongside an already-present positional Modifier value (a real duplicate-parameter
    compile error) -- confirmed directly: ProgressScreen.kt's own `Box(Modifier.fillMaxSize(),
    contentAlignment = Alignment.Center) { ... }` is exactly this shape."""
    if va_node is None:
        return None
    for va in va_node.named_children:
        if va.type != "value_argument":
            continue
        # A NAMED argument has an `identifier "=" <expr>` shape (3+ children incl. the "=" token); a
        # POSITIONAL argument is just the bare expression node(s) with no "=" child at all.
        has_eq = any(c.type == "=" for c in va.children)
        if has_eq:
            continue
        expr_node = va.children[-1] if va.children else None
        if expr_node is not None and _leftmost_identifier_name(expr_node) == "Modifier":
            return va
    return None


def classify(record, node):
    """-> ("rewrite", value_argument_node) | ("add", value_arguments_node) | ("skip", SkipReason)

    Classifies ONE CALL_KIND record+node for the STAMP-not-STATEMENT injection scheme -- see module doc.
    """
    if node is None:
        return ("skip", SkipReason.UNRESOLVED_NODE)
    # INNER-WRAPPER SKIP (bugfix vs. an earlier version of this function): idgen.py assigns a record to
    # EVERY call_expression node, including the INNER call_expression of a `Foo(...) { }`
    # trailing-lambda wrapper (`call_expression[call_expression, annotated_lambda]` -- see
    # `_call_base_and_args`'s own doc comment). `_call_base_and_args` already unwraps an OUTER
    # wrapper's own record down to that SAME inner node/value_arguments -- so without this check, the
    # inner node's OWN record (a separate CALL_KIND entry with its own distinct id) resolved to the
    # IDENTICAL value_arguments/modifier-argument object the outer record already targets, and BOTH
    # ids got spliced onto the SAME modifier expression (`modifier = X.walkTag(outerId).walkTag(innerId)`,
    # or worse -- the "add" path duplicated with no separator, producing unparseable
    # `modifier = ...)modifier = ...)` text -- confirmed directly against TodayScreen.kt's own
    # AnimalIconVisualization/PreCheckInSheet/CheckInButtonRow call sites before this check was added).
    # Skipped here with the SAME reasoning inject_emitid.py's Phase 2 predecessor already applied via
    # its ALLOWED_PARENTS/SkipReason.INNER_TRAILING_LAMBDA_WRAPPER check (a call whose PARENT is a
    # call_expression is this same inner-wrapper node) -- this is that identical rule, re-derived for
    # the STAMP scheme's own node-identity (not parent-position) classification path.
    if node.parent is not None and node.parent.type == "call_expression":
        return ("skip", SkipReason.INNER_TRAILING_LAMBDA_WRAPPER)
    base, va = _call_base_and_args(node)
    existing = _existing_modifier_arg(va) or _positional_modifier_arg(va)
    if existing is not None:
        return ("rewrite", existing)
    if va is None:
        return ("skip", SkipReason.NO_ARG_LIST)
    idc = _callee_identifier(base)
    if idc is None:
        return ("skip", SkipReason.NOT_IDENTIFIER_CALLEE)
    name = idc.text.decode()
    if not (name[:1].isalpha() and name[:1].isupper()):
        return ("skip", SkipReason.NOT_PASCAL_CASE)
    if name in NO_MODIFIER_PARAM:
        return ("skip", SkipReason.KNOWN_NO_MODIFIER_PARAM)
    return ("add", va)


def plan_injections(path):
    """-> (to_rewrite: [(Record, value_argument_node)], to_add: [(Record, value_arguments_node)],
           skipped: [(Record, reason)])

    Re-walks the SAME tree idgen.gen_ids_for_file() walks (single-file mode: ids are local to this
    file, exactly like idgen.py's own single-file CLI path -- root_prefix_segs=None), this time also
    classifying each CALL_KIND node's modifier-arg shape (see `classify`). Every CALL_KIND record from
    idgen's real id assignment is preserved verbatim (same id string) -- this function only ADDS the
    injectability classification, it does not recompute or renumber ids.
    """
    src = open(path, "rb").read()
    tree = parse(src)
    root = tree.root_node

    node_by_id = {}

    def walk(node, segs, node_kind_for_root=None):
        this_kind = node_kind_for_root or node.type
        if this_kind in I.RECORD_KINDS:
            node_by_id["/".join(segs)] = node
        for i, c in enumerate(node.children):
            walk(c, segs + [f"{i}:{c.type}"])

    walk(root, [f"0:{I.FILE_KIND}"], node_kind_for_root=I.FILE_KIND)

    records = I.gen_ids_for_file(path)  # authoritative id list (unchanged from Phase 1)
    to_rewrite = []
    to_add = []
    skipped = []
    for r in records:
        if r.node_kind != I.CALL_KIND:
            continue
        node = node_by_id.get(r.id)
        kind, payload = classify(r, node)
        if kind == "rewrite":
            to_rewrite.append((r, payload))
        elif kind == "add":
            to_add.append((r, payload))
        else:
            skipped.append((r, payload))
    return to_rewrite, to_add, skipped


def inject_file(path, out_path=None, dry_run=False):
    """Instrument one .kt file in place (or write to `out_path`).
    -> (n_injected, skipped, out_text)  (n_injected = len(to_rewrite) + len(to_add), matching the old
    single-count return shape callers/tests already expect)."""
    to_rewrite, to_add, skipped = plan_injections(path)

    src_bytes = open(path, "rb").read()

    edits = []  # (byte_offset, text_to_insert)  -- pure insertions, nothing deleted, so highest-offset-
    # first splicing (no re-parse between edits) stays valid exactly as the Phase 2 file relied on.
    for r, modifier_arg_node in to_rewrite:
        # `modifier = <expr>` -- append `.walkTag("<id>")` immediately after <expr>'s own end_byte (the
        # value_argument's last child, i.e. everything after the `=`). No parsing of <expr>'s own text
        # is needed: splicing a `.walkTag(...)` call after ANY valid Kotlin expression byte range is
        # itself always valid Kotlin (member-access chaining), regardless of what the expression is.
        expr_node = modifier_arg_node.children[-1]
        edits.append((expr_node.end_byte, f'.walkTag("{r.id}")'))
    for r, va_node in to_add:
        # No existing modifier arg: append `modifier = Modifier.walkTag("<id>")` as a new trailing named
        # argument. va_node is `(` ... [args separated by ,] ... `)` -- its LAST child is always the `)`
        # anonymous token (value_arguments always ends with `)`, confirmed against every observed shape,
        # empty or not). Insert immediately BEFORE that closing paren.
        close_paren = va_node.children[-1]
        assert close_paren.type == ")", f"expected ')' as last value_arguments child, got {close_paren.type!r}"
        has_existing_args = any(c.type == "value_argument" for c in va_node.children)
        # TRAILING-COMMA CHECK (bugfix vs. an earlier version of this function): Kotlin's own
        # multi-line-call convention (`Foo(\n    a = 1,\n    b = 2,\n)`, common throughout this
        # codebase) already ends its argument list with a `,` token as the LAST non-`)` child --
        # unconditionally prepending another `, ` in that case produced `b = 2,\n, modifier = ...)`,
        # a stray leading comma before `modifier` that tree-sitter-kotlin (and kotlinc) both reject.
        # The child immediately before `)` is checked directly rather than inspecting raw source text,
        # since that child IS the authoritative trailing-comma token when present.
        second_to_last = va_node.children[-2] if len(va_node.children) >= 2 else None
        already_has_trailing_comma = second_to_last is not None and second_to_last.type == ","
        if not has_existing_args or already_has_trailing_comma:
            prefix = ""
        else:
            prefix = ", "
        edits.append((close_paren.start_byte, f'{prefix}modifier = Modifier.walkTag("{r.id}")'))

    edits.sort(key=lambda e: e[0], reverse=True)
    out_bytes = src_bytes
    for offset, text in edits:
        out_bytes = out_bytes[:offset] + text.encode("utf-8") + out_bytes[offset:]

    out_text = out_bytes.decode("utf-8")
    out_text = _ensure_imports(out_text)

    if not dry_run:
        target = out_path or path
        with open(target, "w", encoding="utf-8") as f:
            f.write(out_text)

    return len(to_rewrite) + len(to_add), skipped, out_text


def _ensure_imports(text):
    lines = text.split("\n")
    missing = [imp for imp in REQUIRED_IMPORTS if imp not in text]
    if not missing:
        return text
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
    for imp in missing:
        lines.insert(insert_at, imp)
        insert_at += 1
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
    print(f"inject_emitid: injected (stamped) {n_injected} call site(s) with walkTag")
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
