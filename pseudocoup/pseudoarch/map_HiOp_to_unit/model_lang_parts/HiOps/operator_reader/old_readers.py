"""old_readers -- the readers written on 2026-09-28 for go, rust, python and
java, kept exactly as they were. They are not yet split into operator_reader's
five parts, so read_operators() refuses these languages until each one is
(c first, one language at a time). Each reader's Declaration and parse are
here, unchanged, for that split.
"""

import re

from ... import Declaration, Operator, declaring_file_path, placeholders_of
from . import VALUE_OPERANDS
from .source_text import literal_text, read_function_body, split_outside_literals, without_literals


# go's compiler, cmd/compile, declares its own syntax in
# src/cmd/compile/internal/syntax: every expression kind in nodes.go, every
# token and operator with its spelling in tokens.go, and its printer
# (printer.go, printRawNode) writes each kind out:
#
#     case *IndexExpr:
#         p.print(n.X, _Lbrack, n.Index, _Rbrack)
#
# An Operation is one of tokens.go's Operator constants. The binary ones sit
# under a precedence comment (precOrOr .. precMul); the unary ones are the
# parser's own list (parser.go, unaryExpr), receive included (`o.Op = Recv`).
# An Operator under precAdd or precMul also has an assignment form, `a += b`
# (the grammar's assign_op), and Add and Sub have `a++` and `a--` (nodes.go,
# AssignStmt: "Rhs == nil means Lhs++ (Op == Add) or Lhs-- (Op == Sub)").
# Those are statements in go, not expressions, and are named `AssignStmt.*`
# so the standard form writes them as statements.
GO_OPERATOR = re.compile(r"^\t(\w+)\s*//\s*(\S+)\s*$")
GO_TOKEN = re.compile(r"^\t(_\w+)\s*//\s*(\S+)\s*$")
GO_PRECEDENCE_COMMENT = re.compile(r"^\t//\s*(prec\w+)\s*$")
GO_KIND_START = re.compile(r"^\t(\w+) struct \{")
GO_FIELD = re.compile(r"^\t\t((?:\w+, )*\w+)\s+(\S+)")
GO_CASE = re.compile(r"^\tcase \*(\w+):\s*$")
GO_PRINT_CALL = re.compile(r"^p\.print\((.*)\)$")
GO_UNARY_CASE = re.compile(r"^\t\tcase ([A-Z]\w*(?:, [A-Z]\w*)*):")
GO_OP_ASSIGNED = re.compile(r"\b\w+\.Op = ([A-Z]\w*)\b")
GO_ASSIGNABLE_GROUPS = ("precAdd", "precMul")
GO_TYPE_FIELDS = ("Type", "Elem")


def read_go_tokens(checkout: str, relative: str) -> tuple:
    """(token spellings, operators): every `_Token // spelling` of the token
    block, and every Operator with its spelling, precedence group and line."""
    path = declaring_file_path(checkout, relative)
    spellings = {}
    operators = []
    group = None
    inside_operators = False
    with open(path, encoding="utf-8") as declaring_file:
        for line_number, line in enumerate(declaring_file, start=1):
            if line.startswith("type Operator uint"):
                inside_operators = True
                continue
            token = GO_TOKEN.match(line)
            if token is not None and not inside_operators:
                spellings[token.group(1)] = token.group(2)
                continue
            if not inside_operators:
                continue
            if line.startswith(")"):
                break
            precedence = GO_PRECEDENCE_COMMENT.match(line)
            if precedence is not None:
                group = precedence.group(1)
                continue
            operator = GO_OPERATOR.match(line)
            if operator is not None:
                operators.append((operator.group(1), operator.group(2), group, line_number))
    found = (spellings, operators)
    return found


def read_go_unary(checkout: str, relative: str) -> tuple:
    """(Operator names the parser takes as unary, line of unaryExpr)."""
    body, first_line = read_go_function(checkout, relative, "func (p *parser) unaryExpr() Expr {")
    unary = []
    for line in body.split("\n"):
        case = GO_UNARY_CASE.match(line)
        if case is not None:
            for name in case.group(1).split(", "):
                unary.append(name)
        assigned = GO_OP_ASSIGNED.search(line)
        if assigned is not None and assigned.group(1) not in unary:
            unary.append(assigned.group(1))
    found = (unary, first_line)
    return found


def read_go_function(checkout: str, relative: str, start: str) -> tuple:
    """(text, first line) of the go function that begins with `start`."""
    path = declaring_file_path(checkout, relative)
    lines = []
    first_line = 0
    with open(path, encoding="utf-8") as source_file:
        for line_number, line in enumerate(source_file, start=1):
            if first_line == 0:
                if line.startswith(start):
                    first_line = line_number
                continue
            if line.startswith("}"):
                break
            lines.append(line.rstrip("\n"))
    if first_line == 0:
        message = f"read_operators: `{start}` is not in {relative}"
        raise LookupError(message)
    body = "\n".join(lines)
    return body, first_line


def read_go_kinds(checkout: str, relative: str) -> dict:
    """kind -> (fields, line): every struct in nodes.go that embeds `expr`,
    with its fields as (name, type) in order."""
    path = declaring_file_path(checkout, relative)
    kinds = {}
    current = None
    fields = []
    start_line = 0
    is_expression = False
    with open(path, encoding="utf-8") as declaring_file:
        for line_number, line in enumerate(declaring_file, start=1):
            start = GO_KIND_START.match(line)
            if start is not None:
                current = start.group(1)
                fields = []
                start_line = line_number
                is_expression = False
                continue
            if current is None:
                continue
            if line.startswith("\t}"):
                if is_expression:
                    kinds[current] = (tuple(fields), start_line)
                current = None
                continue
            if line.strip() == "expr":
                is_expression = True
                continue
            field = GO_FIELD.match(line)
            if field is not None:
                for name in field.group(1).split(","):
                    fields.append((name.strip(), field.group(2)))
    return kinds


def read_go_printer(checkout: str, relative: str) -> dict:
    """kind -> (statements, line): each `case *Kind:` of printRawNode, its
    statements without comments."""
    body, first_line = read_go_function(checkout, relative, "func (p *printer) printRawNode(n Node) {")
    cases = {}
    current = None
    statements = []
    case_line = 0
    for offset, line in enumerate(body.split("\n"), start=1):
        case = GO_CASE.match(line)
        if case is not None or line.startswith("\tdefault:") or line.startswith("\t}"):
            if current is not None:
                cases[current] = (statements, case_line)
            current = None
            if case is not None:
                current = case.group(1)
                statements = []
                case_line = first_line + offset
            continue
        if current is None:
            continue
        code = line.split("//")[0].strip()
        if code:
            statements.append(code)
    return cases


def go_template(kind: str, fields: tuple, statements: list, spellings: dict) -> tuple:
    """(spelling, operands, reason): the printer's case as a template, or why
    it is not one."""
    field_types = dict(fields)
    pieces = []
    operands = []
    values_seen = 0
    for statement in statements:
        call = GO_PRINT_CALL.match(statement)
        if call is None:
            return "", (), f"its printer case branches or calls `{statement[:50]}`"
        for argument in split_outside_literals(call.group(1), ","):
            if argument == "blank":
                pieces.append(" ")
            elif argument in spellings:
                pieces.append(spellings[argument])
            elif argument.startswith("n."):
                name = argument[2:]
                kind_of_field = field_types.get(name, "")
                if kind_of_field != "Expr":
                    return "", (), f"its printer writes the field `{name}` ({kind_of_field or 'unknown'}), which is not an operand"
                if name in GO_TYPE_FIELDS:
                    pieces.append("T")
                    operands.append("T")
                    continue
                operand = VALUE_OPERANDS[values_seen]
                values_seen += 1
                pieces.append(operand)
                operands.append(operand)
            else:
                return "", (), f"its printer writes `{argument[:40]}`"
    template = "".join(pieces)
    return template, tuple(operands), None


def go_expression_kinds(declaration: Declaration) -> tuple:
    """(operators, unread) over nodes.go's expression kinds, other than
    Operation and CallExpr, which read_go_operations expands."""
    tokens_file, nodes_file, printer_file, parser_file = declaration.files
    spellings, go_operators = read_go_tokens(declaration.checkout, tokens_file)
    unary, _unary_line = read_go_unary(declaration.checkout, parser_file)
    kinds = read_go_kinds(declaration.checkout, nodes_file)
    printers = read_go_printer(declaration.checkout, printer_file)
    operators = []
    unread = []
    for name, _spelling, group, _line_number in go_operators:
        if group is None and name not in unary:
            unread.append((f"Operator.{name}", "neither binary (no precedence group) nor unary (not in the parser's list)"))
    for kind, (fields, line_number) in kinds.items():
        if kind in ("Operation", "CallExpr"):
            continue
        if kind not in printers:
            unread.append((kind, "its printer has no case for it"))
            continue
        statements, printer_line = printers[kind]
        spelling, operands, reason = go_template(kind, fields, statements, spellings)
        if reason is not None:
            unread.append((kind, reason))
            continue
        if not operands:
            unread.append((kind, "it takes no operand"))
            continue
        source = f"{nodes_file}:{line_number}, printed at {printer_file}:{printer_line}"
        operators.append((kind, spelling, operands, source))
    found = (operators, unread)
    return found


def read_go_operations(lang: str, declaration: Declaration) -> tuple:
    """go's operators: the Operations, their assignment and increment
    statements, the conversion, then every other expression kind whose
    printer case reads as a template."""
    tokens_file, nodes_file, printer_file, parser_file = declaration.files
    spellings, go_operators = read_go_tokens(declaration.checkout, tokens_file)
    unary, unary_line = read_go_unary(declaration.checkout, parser_file)
    kinds = read_go_kinds(declaration.checkout, nodes_file)
    printers = read_go_printer(declaration.checkout, printer_file)
    operators = []
    for name, spelling, group, line_number in go_operators:
        source = f"{tokens_file}:{line_number}"
        if group is not None:
            operators.append(Operator(lang, f"Operation.{name}", f"a {spelling} b", ("a", "b"), source))
        if name in unary:
            unary_source = f"{source}, unary at {parser_file}:{unary_line}"
            operators.append(Operator(lang, f"Operation.{name}.unary", f"{spelling}a", ("a",), unary_source))
    for name, spelling, group, line_number in go_operators:
        if group not in GO_ASSIGNABLE_GROUPS:
            continue
        source = f"{tokens_file}:{line_number}, assignment printed at {printer_file}:{printers['AssignStmt'][1]}"
        operators.append(Operator(lang, f"AssignStmt.{name}", f"a {spelling}= b", ("a", "b"), source))
    assign_line = go_struct_line(declaration.checkout, nodes_file, "AssignStmt")
    for name, spelling, _group, line_number in go_operators:
        if name not in ("Add", "Sub"):
            continue
        source = f"{nodes_file}:{assign_line}, AssignStmt with no Rhs; printed at {printer_file}:{printers['AssignStmt'][1]}"
        operators.append(Operator(lang, f"AssignStmt.{name}.{name}", f"a{spelling}{spelling}", ("a",), source))
    conversion_source = f"{nodes_file}:{kinds_line(kinds, 'CallExpr')}, printed at {printer_file}:{printers['CallExpr'][1]}"
    operators.append(Operator(lang, "CallExpr.conversion", "T(a)", ("T", "a"), conversion_source))
    expression_operators, _unread = go_expression_kinds(declaration)
    for kind, spelling, operands, source in expression_operators:
        operators.append(Operator(lang, kind, spelling, operands, source))
    declared = tuple(operators)
    return declared


def go_struct_line(checkout: str, relative: str, name: str) -> int:
    """The line nodes.go declares the struct `name` on."""
    path = declaring_file_path(checkout, relative)
    with open(path, encoding="utf-8") as declaring_file:
        for line_number, line in enumerate(declaring_file, start=1):
            if line.startswith(f"\t{name} struct {{"):
                return line_number
    message = f"read_operators: {name} is not declared in {relative}"
    raise LookupError(message)


def kinds_line(kinds: dict, kind: str) -> int:
    """The line nodes.go declares `kind` on."""
    _fields, line_number = kinds[kind]
    return line_number


# The go the judge runs is go1.26.0, whose own source is in the runner image
# at /usr/lib/go-1.26/src; read with PSEUDOARCH_SOURCES=/usr/lib.
GO_OPERATIONS = Declaration(
    checkout="go-1.26",
    files=(
        "src/cmd/compile/internal/syntax/tokens.go",
        "src/cmd/compile/internal/syntax/nodes.go",
        "src/cmd/compile/internal/syntax/printer.go",
        "src/cmd/compile/internal/syntax/parser.go",
    ),
    parse=read_go_operations,
)


# rustc declares every expression kind in compiler/rustc_ast/src/ast.rs,
# `pub enum ExprKind`, and its operators in the same file, each with its
# spelling: BinOpKind, AssignOpKind and UnOp, `fn as_str`. Its printer,
# compiler/rustc_ast_pretty/src/pprust/state/expr.rs, writes each kind out in
# one arm of `match &expr.kind`:
#
#     ast::ExprKind::Index(expr, index, _) => {
#         self.print_expr_cond_paren(expr, ...);
#         self.word("[");
#         self.print_expr(index, FixupContext::default());
#         self.word("]");
#     }
#
# The template is read from the printing calls an arm makes at its own level;
# a helper it calls (print_expr_binary) is read the same way. A call that
# prints only inside a branch makes the arm unread, named. `op.as_str()` is
# the operator, expanded over the enum the kind carries.
RUST_ENUM_START = re.compile(r"^pub enum (\w+) \{")
RUST_VARIANT = re.compile(r"^    ([A-Z]\w*)\s*(?:\((.*)\))?\s*(?:\{|,)?\s*$")
RUST_AS_STR_ARM = re.compile(r'^\s+(?:\w+::)?(\w+) => "([^"]+)",')
RUST_ARM = re.compile(r"^            ast::ExprKind::(\w+)\b.*=>\s*(\{)?\s*(.*)$")
RUST_CALL = re.compile(r"self\.(\w+)\(")
RUST_LAYOUT = ("cbox", "ibox", "end", "hardbreak_if_not_bol", "zerobreak", "break_offset_if_not_bol")
RUST_OPERAND_PRINTS = ("print_expr", "print_expr_cond_paren", "print_expr_maybe_paren")


def read_rust_enums(checkout: str, relative: str) -> dict:
    """enum -> {variant: spelling}, for every enum in ast.rs whose
    `fn as_str` spells its variants."""
    path = declaring_file_path(checkout, relative)
    spelled = {}
    current = None
    with open(path, encoding="utf-8") as declaring_file:
        for line in declaring_file:
            start = RUST_ENUM_START.match(line)
            if start is not None:
                current = start.group(1)
                continue
            if line.startswith("impl ") or line.startswith("pub enum "):
                continue
            arm = RUST_AS_STR_ARM.match(line)
            if arm is not None and current is not None:
                spelled.setdefault(current, {})[arm.group(1)] = arm.group(2)
    return spelled


def read_rust_expr_kinds(checkout: str, relative: str) -> dict:
    """variant -> (first payload type or None, line), every variant of
    `pub enum ExprKind`."""
    path = declaring_file_path(checkout, relative)
    kinds = {}
    inside = False
    with open(path, encoding="utf-8") as declaring_file:
        for line_number, line in enumerate(declaring_file, start=1):
            if line.startswith("pub enum ExprKind {"):
                inside = True
                continue
            if not inside:
                continue
            if line.startswith("}"):
                break
            variant = RUST_VARIANT.match(line.rstrip("\n"))
            if variant is None:
                continue
            payload = variant.group(2)
            first = None
            if payload:
                first = payload.split(",")[0].strip()
            kinds[variant.group(1)] = (first, line_number)
    return kinds


def rust_calls(body: str) -> list:
    """(depth, method, arguments) for every `self.method(...)` in `body`,
    `depth` counting the braces it sits inside."""
    calls = []
    depth = 0
    index = 0
    while index < len(body):
        character = body[index]
        if character == '"':
            end = index + 1
            while end < len(body) and body[end] != '"':
                if body[end] == "\\":
                    end += 1
                end += 1
            index = end + 1
            continue
        if character == "{":
            depth += 1
        elif character == "}":
            depth -= 1
        elif body.startswith("self.", index):
            call = RUST_CALL.match(body, index)
            if call is not None:
                open_at = call.end() - 1
                level = 0
                close_at = open_at
                while close_at < len(body):
                    if body[close_at] == "(":
                        level += 1
                    elif body[close_at] == ")":
                        level -= 1
                        if level == 0:
                            break
                    close_at += 1
                calls.append((depth, call.group(1), body[open_at + 1:close_at]))
                index = close_at + 1
                continue
        index += 1
    return calls


def read_rust_printer(checkout: str, relative: str) -> tuple:
    """(arms, helpers, main line): each arm of the printer's
    `match &expr.kind` as (body, line), and each `fn print_expr_*` helper
    as (body, line)."""
    path = declaring_file_path(checkout, relative)
    with open(path, encoding="utf-8") as printer_file:
        lines = printer_file.read().split("\n")
    helpers = {}
    for number, line in enumerate(lines, start=1):
        helper = re.match(r"^    (?:pub\(crate\) )?fn (print_expr_\w+)\(", line)
        if helper is None:
            continue
        # The body starts after the line that opens it: a signature can run
        # over several lines and end in `) {`.
        opened = line.rstrip().endswith("{")
        body = []
        for following in lines[number:]:
            if not opened:
                opened = following.rstrip().endswith("{")
                continue
            if following.startswith("    }"):
                break
            body.append(following)
        helpers[helper.group(1)] = ("\n".join(body), number)
    arms = {}
    main_line = 0
    inside = False
    current = None
    body = []
    arm_line = 0
    for number, line in enumerate(lines, start=1):
        if not inside:
            if line == "        match &expr.kind {":
                inside = True
                main_line = number
            continue
        if line == "        }":
            if current is not None:
                arms[current] = ("\n".join(body), arm_line)
            break
        arm = RUST_ARM.match(line)
        if arm is not None:
            if current is not None:
                arms[current] = ("\n".join(body), arm_line)
            current = arm.group(1)
            arm_line = number
            body = [arm.group(3)] if arm.group(2) is None else []
            continue
        if current is not None:
            body.append(line)
    printer = (arms, helpers, main_line)
    return printer


def rust_pieces(body: str, helpers: dict, seen: tuple) -> tuple:
    """(pieces, reason) of one arm or helper body."""
    without_comments = re.sub(r"//[^\n]*", "", body)
    pieces = []
    for depth, method, arguments in rust_calls(without_comments):
        if method in RUST_LAYOUT:
            continue
        if depth > 0:
            return [], f"it prints `self.{method}` only inside a branch"
        if method == "popen":
            pieces.append(("text", "("))
        elif method == "pclose":
            pieces.append(("text", ")"))
        elif method in ("space", "nbsp"):
            pieces.append(("text", " "))
        elif method in ("word", "word_space", "word_nbsp"):
            literal = re.fullmatch(r'\s*"((?:[^"\\]|\\.)*)"\s*', arguments)
            if "as_str()" in arguments:
                pieces.append(("opcode",))
            elif literal is not None:
                pieces.append(("text", literal.group(1)))
            else:
                return [], f"it writes `{arguments.strip()[:40]}`"
            if method != "word":
                pieces.append(("text", " "))
        elif method in RUST_OPERAND_PRINTS:
            pieces.append(("value",))
        elif method == "print_type":
            pieces.append(("type",))
        elif method in helpers and method not in seen:
            helper_body, _line = helpers[method]
            inner, reason = rust_pieces(helper_body, helpers, seen + (method,))
            if reason is not None:
                return [], f"its helper {method}: {reason}"
            pieces.extend(inner)
        else:
            return [], f"it calls `self.{method}`"
    return pieces, None


def rust_template(pieces: list, opcode: str) -> tuple:
    """(spelling, operands) of rust printer pieces."""
    spelling = []
    operands = []
    values_seen = 0
    for piece in pieces:
        if piece[0] == "text":
            spelling.append(piece[1])
        elif piece[0] == "value":
            operand = VALUE_OPERANDS[values_seen]
            values_seen += 1
            spelling.append(operand)
            operands.append(operand)
        elif piece[0] == "type":
            spelling.append("T")
            operands.append("T")
        elif piece[0] == "opcode":
            spelling.append(opcode)
    template = ("".join(spelling), tuple(operands))
    return template


def rust_kinds(declaration: Declaration) -> tuple:
    """(operators, unread) over every ExprKind variant."""
    ast_file, printer_file = declaration.files
    enums = read_rust_enums(declaration.checkout, ast_file)
    kinds = read_rust_expr_kinds(declaration.checkout, ast_file)
    arms, helpers, _main_line = read_rust_printer(declaration.checkout, printer_file)
    operators = []
    unread = []
    for kind, (payload, line_number) in kinds.items():
        if kind not in arms:
            unread.append((kind, "the printer has no arm of its own for it"))
            continue
        body, arm_line = arms[kind]
        pieces, reason = rust_pieces(body, helpers, ())
        if reason is not None:
            unread.append((kind, reason))
            continue
        source = f"{ast_file}:{line_number}, printed at {printer_file}:{arm_line}"
        if ("opcode",) in pieces:
            enum = payload if payload in enums else f"{payload}Kind"
            if enum not in enums:
                unread.append((kind, f"its operator enum `{payload}` has no spelled variants"))
                continue
            for variant, spelled in enums[enum].items():
                spelling, operands = rust_template(pieces, spelled)
                operators.append((f"{kind}.{variant}", spelling, operands, source))
            continue
        spelling, operands = rust_template(pieces, "")
        has_text = any(piece[0] == "text" and piece[1].strip() for piece in pieces)
        if not operands:
            unread.append((kind, "it takes no operand"))
            continue
        if not has_text:
            unread.append((kind, "a program never writes it: its printer writes no text"))
            continue
        if tuple(placeholders_of(spelling)) != tuple(operands):
            unread.append((kind, f"its printer joins an operand to text (`{spelling}`)"))
            continue
        operators.append((kind, spelling, operands, source))
    found = (operators, unread)
    return found


def read_rust_operations(lang: str, declaration: Declaration) -> tuple:
    """rust's operators: every ExprKind whose printer arm reads as a
    template, the operator kinds expanded over their enums."""
    kind_operators, _unread = rust_kinds(declaration)
    operators = []
    for name, spelling, operands, source in kind_operators:
        operators.append(Operator(lang, name, spelling, operands, source))
    declared = tuple(operators)
    return declared


# The rustc the judge runs is 1.96.1; its files were fetched at the tag
# 1.96.1 (sparse: the syntax tree, its printer, the primitive types).
RUST_OPERATIONS = Declaration(
    checkout="rust-1.96.1",
    files=(
        "compiler/rustc_ast/src/ast.rs",
        "compiler/rustc_ast_pretty/src/pprust/state/expr.rs",
    ),
    parse=read_rust_operations,
)


# python's lowerer is the interpreter itself, and it can be asked. Its
# syntax tree is its own `ast` module: every expression kind is a subclass of
# ast.expr with typed fields (`_field_types`), and `ast.unparse` is its own
# printer. A kind's template is the printer's text for the kind built with a
# Name in each expression field, expanded over every operator class a field
# takes (ast.operator, ast.unaryop, ast.cmpop, ast.boolop). The augmented
# assignment `a += b` is a statement kind (ast.AugAssign) and is read the
# same way, named `AugAssign.*` so the standard form runs it as a statement.
#
# So this reader must run IN the python that judges; it refuses otherwise.
PYTHON_OPERATOR_FAMILIES = ("operator", "unaryop", "cmpop", "boolop")
PYTHON_STATEMENT_KINDS = ("AugAssign",)


def python_is_the_judge(declaration: Declaration) -> str:
    """The running interpreter's version, if it is the one that judges."""
    import sys
    version = sys.version.split()[0]
    if declaration.checkout != f"python-{version}":
        message = f"read_operators: python must be read by the python that judges ({declaration.checkout}); this is {version}"
        raise LookupError(message)
    return version


def python_node(kind_class, family_choice: dict, list_length: int):
    """(node, reason): `kind_class` built with a Name in each expression
    field (a list field gets `list_length` of them), the chosen operator in
    each operator field. An expr_context field is left to its default, the
    context of reading."""
    import ast
    import typing
    placeholders = list(VALUE_OPERANDS)
    arguments = {}
    for field, field_type in getattr(kind_class, "_field_types", {}).items():
        origin = typing.get_origin(field_type)
        members = typing.get_args(field_type)
        inner = field_type
        if origin is list:
            inner = members[0]
        if typing.get_origin(inner) is not None or isinstance(inner, typing._UnionGenericAlias if hasattr(typing, "_UnionGenericAlias") else ()):
            others = [member for member in typing.get_args(inner) if member is not type(None)]
            inner = others[0] if others else None
        elif origin is not list and type(None) in members:
            others = [member for member in members if member is not type(None)]
            inner = others[0] if others else None
        if isinstance(inner, type) and issubclass(inner, ast.expr_context):
            continue
        if isinstance(inner, type) and issubclass(inner, ast.expr):
            count = list_length if origin is list else 1
            if len(placeholders) < count:
                return None, "it has more expression fields than placeholders"
            names = []
            for _ in range(count):
                names.append(ast.Name(id=placeholders.pop(0), ctx=ast.Load()))
            arguments[field] = names if origin is list else names[0]
            continue
        if isinstance(inner, type) and inner.__name__ in PYTHON_OPERATOR_FAMILIES:
            chosen = family_choice[inner.__name__]()
            arguments[field] = [chosen] if origin is list else chosen
            continue
        if origin is list:
            arguments[field] = []
            continue
        if type(None) in members:
            arguments[field] = None
            continue
        return None, f"its field `{field}` needs a {getattr(inner, '__name__', inner)}, not an operand"
    node = kind_class(**arguments)
    return node, None


def python_parses_back(kind_class, spelling: str, node) -> str:
    """None if the interpreter's own parser reads `spelling` back as the
    kind (and operator) it was built as; else what it reads it as."""
    import ast
    mode = "exec" if issubclass(kind_class, ast.stmt) else "eval"
    try:
        parsed = ast.parse(spelling, mode=mode)
    except SyntaxError as problem:
        return f"SyntaxError: {problem.msg}"
    back = parsed.body[0] if mode == "exec" else parsed.body
    if type(back) is not kind_class:
        return type(back).__name__
    if python_shape(back) != python_shape(node):
        return f"{type(back).__name__} of another shape"
    return None


def python_shape(node) -> str:
    """The node's dump with every naming context read as a read: whether a
    name is read or stored is not part of the expression's kind."""
    import ast
    import copy
    shaped = copy.deepcopy(node)
    for inner in ast.walk(shaped):
        if hasattr(inner, "ctx"):
            inner.ctx = ast.Load()
    dumped = ast.dump(shaped)
    return dumped


def python_kinds(declaration: Declaration) -> tuple:
    """(operators, unread) over every ast.expr kind and the statement kinds
    read beside them. Each template is read back by the interpreter's own
    parser: one that comes back as another kind is unread, and says what it
    came back as."""
    import ast
    import itertools
    version = python_is_the_judge(declaration)
    kinds = list(ast.expr.__subclasses__())
    for name in PYTHON_STATEMENT_KINDS:
        kinds.append(getattr(ast, name))
    operators = []
    unread = []
    for kind_class in kinds:
        kind = kind_class.__name__
        families = []
        for field_type in getattr(kind_class, "_field_types", {}).values():
            for candidate in (field_type,) + tuple(getattr(field_type, "__args__", ())):
                if isinstance(candidate, type) and candidate.__name__ in PYTHON_OPERATOR_FAMILIES:
                    families.append(candidate.__name__)
        choices = []
        for family in families:
            choices.append(getattr(ast, family).__subclasses__())
        combinations = list(itertools.product(*choices)) if choices else [()]
        source = f"ast.{kind} (Python {version}), printed by ast.unparse, {ast.__file__.split('/lib/')[-1]}"
        for combination in combinations:
            family_choice = dict(zip(families, combination))
            found = None
            reason = None
            for list_length in (1, 2):
                node, reason = python_node(kind_class, family_choice, list_length)
                if reason is not None:
                    break
                try:
                    spelling = ast.unparse(ast.fix_missing_locations(node))
                except Exception as problem:
                    reason = f"ast.unparse refuses it: {type(problem).__name__}"
                    break
                back = python_parses_back(kind_class, spelling, node)
                if back is None:
                    found = spelling
                    break
                reason = f"its printed form `{spelling}` parses back as {back}"
            if found is None:
                unread.append((kind, reason))
                break
            operands = tuple(placeholders_of(found))
            if not operands:
                unread.append((kind, "it takes no operand"))
                break
            suffix = "".join(f".{chosen.__name__}" for chosen in combination)
            operators.append((f"{kind}{suffix}", found, operands, source))
    result = (operators, unread)
    return result


def read_python_operations(lang: str, declaration: Declaration) -> tuple:
    """python's operators, asked of the running interpreter."""
    kind_operators, _unread = python_kinds(declaration)
    operators = []
    for name, spelling, operands, source in kind_operators:
        operators.append(Operator(lang, name, spelling, operands, source))
    declared = tuple(operators)
    return declared


# The python the judge runs is 3.13.15, the runner image's own.
PYTHON_OPERATIONS = Declaration(
    checkout="python-3.13.15",
    files=(),
    parse=read_python_operations,
)


# javac declares its tree kinds in com/sun/tools/javac/tree/JCTree.java (one
# JC class per kind, and the Tag enum), puts every operator tag in its
# syntactic class in TreeInfo.opPrec (prefixPrec, postfixPrec, assignopPrec,
# and one precedence per binary level), spells each in Pretty.operatorName,
# and writes each kind out in one Pretty.visit method:
#
#     public void visitTypeCast(JCTypeCast tree) {
#         try { open(prec, TreeInfo.prefixPrec); print('('); printExpr(tree.clazz);
#               print(')'); printExpr(tree.expr, TreeInfo.prefixPrec); ... }
#
# The template is read from the prints; `printExpr(tree.clazz)` and
# `printExpr(tree.getType())` name a type (`T`). Binary, unary and compound
# assignment kinds are expanded over the tags TreeInfo.opPrec classes them in.
JAVA_CLASS = re.compile(r"^    public (?:abstract )?static (?:abstract )?class (JC\w+)(?:<[^>]*>)? extends (\w+)")
JAVA_VISIT = re.compile(r"^    public void visit(\w+)\((JC\w+) tree\) \{")
JAVA_CASE = re.compile(r"\bcase (\w+):")
JAVA_RETURN = re.compile(r"\breturn (\w+);")
JAVA_SPELLING = re.compile(r'\bcase (\w+):\s*return "([^"]*)";')
JAVA_ASSIGN_TAG = re.compile(r"^\s+(\w+_ASG)\((\w+)\),")
JAVA_BINARY_CLASSES = ("orPrec", "andPrec", "eqPrec", "ordPrec", "bitorPrec", "bitxorPrec", "bitandPrec", "shiftPrec", "addPrec", "mulPrec")
JAVA_TYPE_FIELDS = ("tree.clazz", "tree.getType()", "tree.type")


def read_java_classes(checkout: str, relative: str) -> dict:
    """JC class -> the class it extends, every one JCTree.java declares."""
    path = declaring_file_path(checkout, relative)
    classes = {}
    with open(path, encoding="utf-8") as declaring_file:
        for line in declaring_file:
            declared = JAVA_CLASS.match(line)
            if declared is not None:
                classes[declared.group(1)] = declared.group(2)
    return classes


def read_java_switch(checkout: str, relative: str, start: str) -> tuple:
    """(case -> returned name or string, first line) of the switch in the
    method that begins with `start`: TreeInfo.opPrec, Pretty.operatorName."""
    body, first_line = read_function_body(checkout, relative, start)
    answers = {}
    for spelled in JAVA_SPELLING.finditer(body):
        answers[spelled.group(1)] = spelled.group(2)
    pending = []
    for line in body.split("\n"):
        code = line.split("//")[0]
        for case in JAVA_CASE.finditer(code):
            pending.append(case.group(1))
        returned = JAVA_RETURN.search(code)
        if returned is not None and pending:
            for tag in pending:
                answers.setdefault(tag, returned.group(1))
            pending = []
    found = (answers, first_line)
    return found


def read_java_visits(checkout: str, relative: str) -> dict:
    """JC class -> (visit name, body, line), every Pretty.visit method."""
    path = declaring_file_path(checkout, relative)
    with open(path, encoding="utf-8") as printer_file:
        lines = printer_file.read().split("\n")
    visits = {}
    for number, line in enumerate(lines, start=1):
        visit = JAVA_VISIT.match(line)
        if visit is None:
            continue
        body = []
        for following in lines[number:]:
            if following.startswith("    }"):
                break
            body.append(following)
        visits[visit.group(2)] = (visit.group(1), "\n".join(body), number)
    return visits


def java_pieces(body: str) -> tuple:
    """(pieces, reason) of one Pretty.visit body."""
    code = re.sub(r"//[^\n]*", "", body)
    code = code.replace("try {", "").replace("} catch (IOException e) {", "").replace("throw new UncheckedIOException(e);", "")
    if re.search(r"\b(if|for|while|switch)\b", without_literals(code)):
        return [], "its printer branches"
    pieces = []
    for statement in split_outside_literals(code, ";"):
        statement = statement.strip().strip("}").strip()
        if not statement:
            continue
        if statement.startswith(("open(", "close(", "int ", "String ")):
            continue
        if statement.startswith("printExpr("):
            argument = split_outside_literals(statement[len("printExpr("):-1], ",")[0]
            pieces.append(("type",) if argument in JAVA_TYPE_FIELDS else ("value",))
            continue
        if statement.startswith("print(") and statement.endswith(")"):
            argument = statement[len("print("):-1]
            text = literal_text(argument)
            if text is not None:
                pieces.append(("text", text))
            elif argument == "opname" or argument.startswith("operatorName("):
                pieces.append(("opcode",))
            else:
                return [], f"it prints `{argument[:40]}`"
            continue
        return [], f"it calls `{statement[:50]}`"
    return pieces, None


def java_kinds(declaration: Declaration) -> tuple:
    """(operators, unread) over every expression kind Pretty writes out."""
    tree_file, info_file, printer_file = declaration.files
    classes = read_java_classes(declaration.checkout, tree_file)
    precedence, precedence_line = read_java_switch(declaration.checkout, info_file, "public static int opPrec(JCTree.Tag op) {")
    spellings, spelling_line = read_java_switch(declaration.checkout, printer_file, "public String operatorName(JCTree.Tag tag) {")
    visits = read_java_visits(declaration.checkout, printer_file)
    assign_base = {}
    with open(declaring_file_path(declaration.checkout, tree_file), encoding="utf-8") as tree_source:
        for line in tree_source:
            tag = JAVA_ASSIGN_TAG.match(line)
            if tag is not None:
                assign_base[tag.group(1)] = tag.group(2)
    operators = []
    unread = []
    for class_name, (visit_name, body, visit_line) in visits.items():
        chain = [class_name]
        while chain[-1] in classes:
            chain.append(classes[chain[-1]])
        if "JCExpression" not in chain:
            continue
        kind = class_name[2:]
        source = f"{tree_file} ({class_name}), printed at {printer_file}:{visit_line}"
        expanded_before = len(operators)
        if class_name == "JCUnary":
            for tag, precedence_class in precedence.items():
                if precedence_class not in ("prefixPrec", "postfixPrec") or tag not in spellings:
                    continue
                spelled = spellings[tag]
                template = f"{spelled}a" if precedence_class == "prefixPrec" else f"a{spelled}"
                operators.append((f"Unary.{tag}", template, ("a",), f"{source}; {info_file}:{precedence_line}"))
            if len(operators) == expanded_before:
                unread.append((kind, "no tag of its operator family was both classed and spelled"))
            continue
        pieces, reason = java_pieces(body)
        if reason is not None:
            unread.append((kind, reason))
            continue
        if ("opcode",) in pieces:
            for tag, precedence_class in precedence.items():
                if class_name == "JCBinary" and precedence_class in JAVA_BINARY_CLASSES and tag in spellings:
                    spelled = spellings[tag]
                elif class_name == "JCAssignOp" and precedence_class == "assignopPrec" and assign_base.get(tag) in spellings:
                    spelled = spellings[assign_base[tag]]
                else:
                    continue
                template, operands = rust_template(pieces, spelled)
                operators.append((f"{kind}.{tag}", template, operands, f"{source}; {info_file}:{precedence_line}"))
            if len(operators) == expanded_before:
                unread.append((kind, "no tag of its operator family was both classed and spelled"))
            continue
        template, operands = rust_template(pieces, "")
        if not operands:
            unread.append((kind, "it takes no operand"))
            continue
        if tuple(placeholders_of(template)) != tuple(operands):
            unread.append((kind, f"its printer joins an operand to text (`{template}`)"))
            continue
        operators.append((kind, template, operands, source))
    found = (operators, unread)
    return found


def read_java_operations(lang: str, declaration: Declaration) -> tuple:
    """java's operators, from javac's own tree, precedence table and printer."""
    kind_operators, _unread = java_kinds(declaration)
    operators = []
    for name, spelling, operands, source in kind_operators:
        operators.append(Operator(lang, name, spelling, operands, source))
    declared = tuple(operators)
    return declared


# The javac the judge runs is 25.0.4; its files were fetched at the tag
# jdk-25.0.4-ga (sparse).
JAVA_OPERATIONS = Declaration(
    checkout="jdk-25.0.4",
    files=(
        "src/jdk.compiler/share/classes/com/sun/tools/javac/tree/JCTree.java",
        "src/jdk.compiler/share/classes/com/sun/tools/javac/tree/TreeInfo.java",
        "src/jdk.compiler/share/classes/com/sun/tools/javac/tree/Pretty.java",
    ),
    parse=read_java_operations,
)
