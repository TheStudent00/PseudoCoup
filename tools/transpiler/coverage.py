#!/usr/bin/env python3
"""
coverage.py -- transpiler coverage report over a Kotlin corpus.

"Nothing hiding": parses every .kt with tree-sitter, then transpiles each while
instrumenting the transpiler's fallthroughs, so EVERY distinct grammar node type
is listed with (a) how often it appears and (b) how often the transpiler PUNTED on
it (dropped the expression as `"__TODO_EXPR__"`, or the statement as
`# TODO_UNHANDLED_KOTLIN_NODE`). This is the measure of "how complete is the
transpiler over the grammar" -- drive the PUNT counts to zero.

Usage:  python3 tools/transpiler/coverage.py [APP_ROOT]
Default APP_ROOT: ~/Programming/WFL/app/src/main/java/com/sara/workoutforlife
"""
import glob
import os
import re
import sys
from collections import Counter

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import literal_transpiler as L  # noqa: E402

DEFAULT_APP = os.path.expanduser(
    "~/Programming/WFL/app/src/main/java/com/sara/workoutforlife")

# Handlers that exist but key on node TYPE only (not child structure), so they
# emit one shape for every sub-case -- correct for the common case, wrong for some
# (navigation 'foo.bar' OK but '16.dp' invalid; call w/ trailing-lambda-after-kwargs
# invalid; assignment to a null-safe LHS invalid). These need structure-aware
# sub-dispatch, NOT a new node-type rule.
OVER_GENERAL = {"navigation_expression", "call_expression", "assignment"}

# Type-system nodes: matter for faithful Python annotations, not run-time logic.
TYPE_SYS = {"user_type", "nullable_type", "function_type", "function_type_parameters",
            "type_arguments", "type_projection", "type_parameters", "type_parameter",
            "parenthesized_type", "type_modifiers", "delegation_specifier",
            "delegation_specifiers"}

# Containers / modifiers / trivia consumed by a parent rule (not emitted directly).
CONTAINER = {"value_argument", "value_arguments", "string_content", "import",
             "variable_declaration", "annotated_lambda", "modifiers",
             "function_value_parameters", "line_comment", "block", "class_parameter",
             "function_body", "block_comment", "visibility_modifier",
             "lambda_parameters", "constructor_invocation", "enum_entry",
             "source_file", "package_header", "primary_constructor", "class_parameters",
             "class_modifier", "class_body", "property_delegate", "property_modifier",
             "escape_sequence", "member_modifier", "getter", "function_modifier",
             "multi_variable_declaration", "type_test", "inheritance_modifier",
             "use_site_target", "spread_expression", "parameter_modifiers"}


def main():
    app = os.path.abspath(sys.argv[1]) if len(sys.argv) > 1 else DEFAULT_APP

    punt_expr = Counter()
    orig = L.LiteralVisitor.parse_expression

    def wrapped(self, node, sb):
        r = orig(self, node, sb)
        if r == '"__TODO_EXPR__"' and node is not None:
            punt_expr[node.type] += 1
        return r
    L.LiteralVisitor.parse_expression = wrapped

    corpus, punt_stmt = Counter(), Counter()
    parser = L.build_parser()
    files = sorted(glob.glob(os.path.join(app, "**", "*.kt"), recursive=True))
    for kt in files:
        raw = open(kt, "rb").read()
        tree = parser.parse(raw)
        stack = [tree.root_node]
        while stack:
            n = stack.pop()
            if n.is_named:
                corpus[n.type] += 1
            stack.extend(n.children)
        code = L.LiteralVisitor().transpile(raw)
        for m in re.finditer(r"TODO_UNHANDLED_KOTLIN_NODE: \[(\w+)\]", code):
            punt_stmt[m.group(1)] += 1

    def tag(t):
        if t in punt_expr or t in punt_stmt:
            return "PUNT"
        if t in OVER_GENERAL:
            return "OVER-GENERAL"
        if t in TYPE_SYS:
            return "TYPE-SYS"
        if t in CONTAINER:
            return "container"
        return "handled"

    cat = Counter(tag(t) for t in corpus)
    print(f"corpus: {len(files)} files, {len(corpus)} distinct node types")
    print(f"  handled {cat['handled']} · over-general {cat['OVER-GENERAL']} · "
          f"punt {cat['PUNT']} · type-sys {cat['TYPE-SYS']} · container {cat['container']}")
    print(f"  dropped expressions: {sum(punt_expr.values())}   "
          f"dropped statements: {sum(punt_stmt.values())}\n")
    print(f"  {'freq':>7} {'category':13} node_type [drops expr/stmt]")
    print("  " + "-" * 60)
    for t, c in corpus.most_common():
        pe, ps = punt_expr.get(t, 0), punt_stmt.get(t, 0)
        extra = f"  [{pe}/{ps}]" if (pe or ps) else ""
        print(f"  {c:7d} {tag(t):13} {t}{extra}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
