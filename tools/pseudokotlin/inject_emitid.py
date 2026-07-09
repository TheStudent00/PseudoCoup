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
import ui_ledger as UL                       # noqa: E402  (_is_widget -- REUSED, the exact predicate
                                              # Phase 4's ledger_unified.py used for UI-enrichment
                                              # eligibility; see WIDGET GATING below)
from parse import parse                      # noqa: E402

WALKEMIT_IMPORT = "import com.sara.workoutforlife.core.debug.WalkEmit"
WALKTAG_IMPORT = "import com.sara.workoutforlife.core.debug.walkTag"
REQUIRED_IMPORTS = (WALKEMIT_IMPORT, WALKTAG_IMPORT)

# WIDGET GATING (bugfix vs. an earlier version of this file -- see host-run 181's compile failures,
# "No parameter with name 'modifier' found" x28 and "None of the following candidates is applicable"
# x22): `ui_ledger._is_widget` is PascalCase-callee-name test, REUSED verbatim -- the SAME predicate
# `ledger_unified.py`'s `ui_fields()` already gates UI-enrichment eligibility with (see that file's own
# comment: "only valid within the Compose UI subtree ... outside ui/ ... plenty of ordinary calls also
# start uppercase"). Scoped the SAME way here: only applied to files under a `ui/` path segment (see
# `_in_ui_scope`), matching ledger_unified's own UIROOT scoping.
#
# PascalCase alone is NOT sufficient inside ui/ either -- data classes declared/used there (`AnimalTier`
# in TodayScreen.kt), Compose VALUE types (`PaddingValues`, `Stroke`, `Path`, `BorderStroke`, `Offset`,
# `RoundedCornerShape`, ...) and misc stdlib-ish PascalCase calls (`Pair`, `MutableInteractionSource`)
# are ALL PascalCase call sites inside ui/ that are NOT composable widget invocations and do NOT accept
# a `modifier` parameter -- confirmed directly: every run-181 compile failure traced back to exactly
# this set. `_is_widget`'s own heuristic cannot tell those apart from `Box`/`Text`/`WflCard`/... by name
# shape alone (see ledger_unified.py's ui_fields() comment -- same limitation, just not consequential
# there because ui_fields() only ever *reads* an existing modifier arg, it never *writes* one). Since
# THIS file can WRITE code, closing that specific gap matters here in a way it didn't for
# ledger_unified.py, so a real widget test is layered on top of `_is_widget` (see `_is_real_widget`):
# reused custom-composable-name universe (`ui_ledger.composable_names()`, an @Composable-annotated
# `fun` scan of the whole ui/ tree -- confirmed AnimalTier/BorderStroke/PaddingValues/Stroke/Path/
# Offset/Pair/MutableInteractionSource/RoundedCornerShape are ALL absent from it) UNION a small
# allowlist of confirmed Compose/Material3 BUILTIN widget names (`Box`, `Text`, `FilterChip`, ...) that
# are never locally declared and so composable_names() alone would never confirm.
BUILTIN_COMPOSE_WIDGETS = frozenset({
    "Box", "Row", "Column", "LazyColumn", "LazyRow", "LazyVerticalGrid", "LazyHorizontalGrid",
    "Text", "Icon", "IconButton", "IconToggleButton", "Image", "Spacer", "Divider",
    "HorizontalDivider", "VerticalDivider", "Button", "OutlinedButton", "TextButton",
    "ElevatedButton", "FilledTonalButton", "ExtendedFloatingActionButton", "FloatingActionButton",
    "Surface", "Card", "ElevatedCard", "OutlinedCard", "Scaffold", "TopAppBar", "BottomAppBar",
    "NavigationBar", "NavigationBarItem", "NavigationRail", "NavigationRailItem",
    "TextField", "OutlinedTextField", "BasicTextField", "BasicSecureTextField",
    "Checkbox", "RadioButton", "Switch", "Slider", "RangeSlider",
    "CircularProgressIndicator", "LinearProgressIndicator",
    "AlertDialog", "Dialog", "ModalBottomSheet", "DropdownMenu", "DropdownMenuItem",
    "ExposedDropdownMenuBox", "Chip", "FilterChip", "AssistChip", "InputChip", "SuggestionChip",
    "Tab", "TabRow", "ScrollableTabRow", "HorizontalPager", "VerticalPager",
    "Canvas", "Box.Companion",
    "SnackbarHost", "Snackbar", "Badge", "BadgedBox", "Tooltip", "PlainTooltip", "RichTooltip",
})

# Confirmed-by-name PascalCase call sites inside ui/ that are POSITIVELY known to be non-widget
# constructor/value-type calls (Compose value types, local data classes, stdlib) -- consulted only as
# a defensive belt-and-suspenders denylist; `_is_real_widget`'s own two-signal test (composable_names()
# union BUILTIN_COMPOSE_WIDGETS) already excludes all of these by construction (neither set contains
# them), so this frozenset currently only documents the confirmed false positives from host-run 181 and
# gives `NOT_A_WIDGET`'s skip-reason report a direct name to cite.
KNOWN_NON_WIDGET_CALLS = frozenset({
    "PaddingValues", "Stroke", "Path", "BorderStroke", "Offset", "Pair",
    "RoundedCornerShape", "MutableInteractionSource",
})


def _in_ui_scope(path):
    """-> True if `path` has a `ui` path segment (same scoping `ledger_unified.py` applies before
    trusting `ui_ledger._is_widget`'s PascalCase heuristic -- see WIDGET GATING above)."""
    parts = os.path.normpath(path).split(os.sep)
    return "ui" in parts


def _is_real_widget(name):
    """-> True if `name` (a PascalCase bare-identifier callee, already confirmed by
    `ui_ledger._is_widget`/the caller) is a CONFIRMED composable widget: either a custom @Composable
    function declared somewhere under the whole ui/ tree (`ui_ledger.composable_names()`, REUSED, not
    reimplemented) or a known built-in Compose/Material3 widget (`BUILTIN_COMPOSE_WIDGETS`). False for
    everything else -- data classes, Compose value types (`PaddingValues`, `Stroke`, `Path`, ...),
    stdlib calls (`Pair`) -- see `KNOWN_NON_WIDGET_CALLS` for the confirmed false-positive set this
    closes off."""
    return name in UL.composable_names() or name in BUILTIN_COMPOSE_WIDGETS

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
    NOT_A_WIDGET = ("callee is PascalCase but not a confirmed composable widget (per ui_ledger._is_widget "
                     "+ composable_names()/BUILTIN_COMPOSE_WIDGETS gating -- e.g. a data class or Compose "
                     "value-type constructor like PaddingValues/Stroke/Path/AnimalTier/BorderStroke)")
    NO_MODIFIER_ARG = ("REWRITE-ONLY: no existing `modifier = <expr>` (named) or leading positional "
                        "Modifier-rooted argument at this call site -- this injector never fabricates a "
                        "new modifier argument (see module doc), so a genuine widget call with no "
                        "modifier plumbed through is conservatively skipped, not guessed at")
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


def classify(record, node, file_path):
    """-> ("rewrite-named", value_argument_node) | ("rewrite-positional", value_argument_node)
         | ("skip", SkipReason)

    Classifies ONE CALL_KIND record+node for the STAMP-not-STATEMENT, REWRITE-ONLY injection scheme --
    see module doc. There is NO "add" outcome any more (bugfix vs. an earlier version of this function
    that fabricated a new `modifier = Modifier.walkTag(id)` named argument onto ANY PascalCase call --
    see host-run 181's compile failures, "No parameter with name 'modifier' found" x28 and "None of the
    following candidates is applicable" x22, both traced to that fabrication path firing on non-widget
    PascalCase calls -- PaddingValues/Stroke/Path/AnimalTier/BorderStroke/... -- and on control-flow-
    embedded widget calls with no modifier plumbed through). This function now only ever REWRITES an
    ALREADY-PRESENT modifier argument in place; a widget call with none is SKIPPED
    (`SkipReason.NO_MODIFIER_ARG`), never guessed at.
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
    # or worse -- the old "add" path duplicated with no separator, producing unparseable
    # `modifier = ...)modifier = ...)` text -- confirmed directly against TodayScreen.kt's own
    # AnimalIconVisualization/PreCheckInSheet/CheckInButtonRow call sites before this check was added).
    # Skipped here with the SAME reasoning inject_emitid.py's Phase 2 predecessor already applied via
    # its ALLOWED_PARENTS/SkipReason.INNER_TRAILING_LAMBDA_WRAPPER check (a call whose PARENT is a
    # call_expression is this same inner-wrapper node) -- this is that identical rule, re-derived for
    # the STAMP scheme's own node-identity (not parent-position) classification path.
    if node.parent is not None and node.parent.type == "call_expression":
        return ("skip", SkipReason.INNER_TRAILING_LAMBDA_WRAPPER)
    base, va = _call_base_and_args(node)

    # WIDGET GATING (bugfix -- see module-level comment above BUILTIN_COMPOSE_WIDGETS): only reached
    # for files under a `ui/` path segment (ui_ledger._is_widget's PascalCase heuristic is only valid
    # there -- see ledger_unified.py's own identical scoping). A call whose callee is not a bare
    # PascalCase identifier, or IS PascalCase but not a confirmed widget (composable_names() union
    # BUILTIN_COMPOSE_WIDGETS), is skipped OUTRIGHT here -- before even looking at its modifier arg --
    # so a non-widget call that happens to also carry a same-named `modifier` parameter of its own
    # (unlikely, but not this file's business to assume) is never touched either.
    idc = _callee_identifier(base)
    if _in_ui_scope(file_path):
        if idc is None:
            return ("skip", SkipReason.NOT_IDENTIFIER_CALLEE)
        name = idc.text.decode()
        if not (name[:1].isalpha() and name[:1].isupper()):
            return ("skip", SkipReason.NOT_PASCAL_CASE)
        if not _is_real_widget(name):
            return ("skip", SkipReason.NOT_A_WIDGET)

    named = _existing_modifier_arg(va)
    if named is not None:
        return ("rewrite-named", named)
    positional = _positional_modifier_arg(va)
    if positional is not None:
        return ("rewrite-positional", positional)

    # REWRITE-ONLY: no existing modifier argument (named or positional) -- never fabricate one, even
    # for a confirmed widget call site with a real, present `value_arguments` list. See module doc.
    if va is None:
        return ("skip", SkipReason.NO_ARG_LIST)
    if idc is None:
        return ("skip", SkipReason.NOT_IDENTIFIER_CALLEE)
    name = idc.text.decode()
    if not (name[:1].isalpha() and name[:1].isupper()):
        return ("skip", SkipReason.NOT_PASCAL_CASE)
    if name in NO_MODIFIER_PARAM:
        return ("skip", SkipReason.KNOWN_NO_MODIFIER_PARAM)
    return ("skip", SkipReason.NO_MODIFIER_ARG)


def plan_injections(path):
    """-> (to_rewrite_named: [(Record, value_argument_node)],
           to_rewrite_positional: [(Record, value_argument_node)],
           skipped: [(Record, reason)])

    Re-walks the SAME tree idgen.gen_ids_for_file() walks (single-file mode: ids are local to this
    file, exactly like idgen.py's own single-file CLI path -- root_prefix_segs=None), this time also
    classifying each CALL_KIND node's modifier-arg shape (see `classify`). Every CALL_KIND record from
    idgen's real id assignment is preserved verbatim (same id string) -- this function only ADDS the
    injectability classification, it does not recompute or renumber ids. NOTE: no "to_add" list any
    more -- this injector is REWRITE-ONLY (see `classify`'s own doc); a call site with no existing
    modifier argument is always in `skipped` (SkipReason.NO_MODIFIER_ARG), never fabricated.
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
    to_rewrite_named = []
    to_rewrite_positional = []
    skipped = []
    for r in records:
        if r.node_kind != I.CALL_KIND:
            continue
        node = node_by_id.get(r.id)
        kind, payload = classify(r, node, path)
        if kind == "rewrite-named":
            to_rewrite_named.append((r, payload))
        elif kind == "rewrite-positional":
            to_rewrite_positional.append((r, payload))
        else:
            skipped.append((r, payload))
    return to_rewrite_named, to_rewrite_positional, skipped


def inject_file(path, out_path=None, dry_run=False):
    """Instrument one .kt file in place (or write to `out_path`).
    -> (n_injected, skipped, out_text, report)

    `n_injected` = len(to_rewrite_named) + len(to_rewrite_positional), matching the old single-count
    return shape callers/tests already expect. `report` is a dict of per-kind/per-reason COUNTS (see
    `build_report`) -- the minimal tracking mechanism task step 2.4 asked for, layered on top of the
    `skipped` list this function already returned (that list itself is unchanged: [(Record, reason)]).

    REWRITE-ONLY (bugfix vs. an earlier version of this function): there is no more "add" edit path --
    a widget call site with no existing modifier argument is left COMPLETELY untouched (it shows up in
    `skipped` with SkipReason.NO_MODIFIER_ARG, not in any edit list). The TRAILING-COMMA handling the
    old "add" path needed (inserting a brand new argument before `)`, which had to worry about whether
    a preceding trailing comma was already present) is gone WITH that path -- a same-in-place rewrite of
    an existing argument's expression never inserts a new argument, so there is no comma to get right or
    wrong any more.
    """
    to_rewrite_named, to_rewrite_positional, skipped = plan_injections(path)

    src_bytes = open(path, "rb").read()

    edits = []  # (byte_offset, text_to_insert)  -- pure insertions, nothing deleted, so highest-offset-
    # first splicing (no re-parse between edits) stays valid exactly as the Phase 2 file relied on.
    for r, modifier_arg_node in to_rewrite_named + to_rewrite_positional:
        # `modifier = <expr>` (named) OR a bare positional Modifier-rooted `<expr>` -- append
        # `.walkTag("<id>")` immediately after <expr>'s own end_byte (the value_argument's last child,
        # i.e. the expression itself for a positional arg, or everything after the `=` for a named
        # one). No parsing of <expr>'s own text is needed: splicing a `.walkTag(...)` call after ANY
        # valid Kotlin expression byte range is itself always valid Kotlin (member-access chaining),
        # regardless of what the expression is.
        expr_node = modifier_arg_node.children[-1]
        edits.append((expr_node.end_byte, f'.walkTag("{r.id}")'))

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

    report = build_report(to_rewrite_named, to_rewrite_positional, skipped)
    return len(to_rewrite_named) + len(to_rewrite_positional), skipped, out_text, report


def build_report(to_rewrite_named, to_rewrite_positional, skipped):
    """-> {"rewrite_named": n, "rewrite_positional": n, "skipped_total": n,
           "skipped_by_reason": {reason_str: n, ...}}

    The minimal per-file counts mechanism task step 2.4 asked for: named-rewrite vs positional-rewrite
    vs skipped-by-reason (in particular NOT_A_WIDGET and NO_MODIFIER_ARG, called out explicitly, but
    every SkipReason is tallied here, not just those two)."""
    by_reason = {}
    for _r, reason in skipped:
        by_reason[reason] = by_reason.get(reason, 0) + 1
    return {
        "rewrite_named": len(to_rewrite_named),
        "rewrite_positional": len(to_rewrite_positional),
        "skipped_total": len(skipped),
        "skipped_by_reason": by_reason,
    }


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
    n_injected, skipped, _out_text, report = inject_file(path, out_path=args.out, dry_run=args.dry_run)

    print(f"inject_emitid: {path}")
    print(f"inject_emitid: injected (stamped) {n_injected} call site(s) with walkTag")
    print(f"inject_emitid:   {report['rewrite_named']}x rewrite-named (existing `modifier = <expr>`)")
    print(f"inject_emitid:   {report['rewrite_positional']}x rewrite-positional "
          f"(existing leading positional Modifier arg)")
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
