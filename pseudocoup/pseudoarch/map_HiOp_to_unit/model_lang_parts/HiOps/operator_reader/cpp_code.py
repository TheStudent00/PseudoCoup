"""cpp_code -- a lowerer's C++ source read with tree-sitter into `Code`, the
shape ways.py walks. It serves every lowerer written in C++; clang is the
first. It knows C++, and nothing about any one lowerer.

    read_functions(checkout, relative, made)   name -> Function, for every
                                               function the file defines
    same_line_text(output, relative)           the file as its preprocessor
                                               writes it, line for line

A function's first parameter is the node it writes; its name is read as
`Node` everywhere in that function, so a lowerer's table can say `Node`
whatever the function calls it (clang's PrintCallArgs calls it `Call`).

A file is read as the lowerer's own preprocessor writes it
(`preprocessed_file_path`), never as written, so nothing a macro writes is
hidden: every macro is expanded, each line sits at its own line number, and
each list the file #includes is joined onto its #include's line. the owner,
2026-10-16: "lets implement that so we never have to be bothered by these
again." `same_line_text` makes that text from the preprocessor's output.

A switch whose cases a `#define` writes over an `#include`d list (clang's
AtomicExpr) was read before that by our own copy of the preprocessor's rules:
the macro's body once per line of the list that calls the macro, with `made`
giving the list's text, keyed by the name the `#include` uses. It still
serves a file read as written.
"""

import codecs
import functools
import re
from typing import NamedTuple

from ... import preprocessed_file_path
from .source_text import split_outside_literals
from .ways import Code

# The node a function writes, as every Code's text names it.
NODE = "Node"

COMPARISONS = ("==", "!=", "<", ">", "<=", ">=")


class Function(NamedTuple):
    """One function the file defines."""

    name: str      # as written: StmtPrinter::VisitMemberExpr
    body: Code
    line: int      # where it starts


@functools.lru_cache(maxsize=None)
def read_functions(checkout: str, relative: str, made: tuple = ()) -> dict:
    """name -> Function, for every function `relative` defines, read with
    tree-sitter's C++ grammar from the file as the lowerer's preprocessor
    writes it. A function whose parse has an error is still read; the
    statements the grammar could not read become `unread`. `made` is
    ((include name, text), ...): the lists the lowerer's build makes, for a
    switch whose cases a macro writes over one of them in a file read as
    written."""
    import tree_sitter
    import tree_sitter_cpp
    parser = tree_sitter.Parser(tree_sitter.Language(tree_sitter_cpp.language()))
    path = preprocessed_file_path(checkout, relative)
    with open(path, "rb") as source_file:
        tree = parser.parse(source_file.read())
    functions = {}
    pending = [tree.root_node]
    while pending:
        node = pending.pop()
        if node.type != "function_definition":
            pending.extend(node.children)
            continue
        declarator = function_declarator(node)
        body = node.child_by_field_name("body")
        if declarator is None or body is None:
            continue
        name = collapsed(declarator.child_by_field_name("declarator").text.decode())
        reader = Reader(first_parameter(declarator), parser, dict(made))
        functions[name] = Function(name, reader.statement(body), node.start_point[0] + 1)
    return functions


def function_declarator(node):
    """The function_declarator under a definition's declarator."""
    declarator = node.child_by_field_name("declarator")
    while declarator is not None and declarator.type != "function_declarator":
        declarator = declarator.child_by_field_name("declarator")
    return declarator


def first_parameter(declarator) -> str:
    """The name of a function's first parameter, or '' when it has none."""
    parameters = declarator.child_by_field_name("parameters")
    if parameters is None:
        return ""
    for parameter in parameters.named_children:
        if parameter.type == "parameter_declaration":
            name = declared_name(parameter.child_by_field_name("declarator"))
            return name or ""
    return ""


def declared_name(node) -> str:
    """The identifier a declarator declares: `*Spelling` -> Spelling."""
    while node is not None:
        if node.type in ("identifier", "field_identifier"):
            return node.text.decode()
        inner = node.child_by_field_name("declarator")
        if inner is None:
            named = [child for child in node.named_children if child.type != "comment"]
            inner = named[0] if named else None
        node = inner
    return ""


def collapsed(text: str) -> str:
    return re.sub(r"\s+", " ", text).strip()


class Reader:
    """Reads one function's statements and expressions into Code. An
    instance, because every read needs the same three things: the name of
    the node, the parser (to read a macro's expansion), and the made lists."""

    def __init__(self, parameter: str, parser=None, made: dict = None):
        self.parameter = parameter
        self.parser = parser
        self.made = made or {}

    def text(self, node) -> str:
        written = collapsed(node.text.decode())
        if self.parameter and self.parameter != NODE:
            written = re.sub(rf"\b{re.escape(self.parameter)}\b", NODE, written)
        return written

    def code(self, form: str, node, parts: tuple, text: str = None) -> Code:
        return Code(form, self.text(node) if text is None else text, parts, node.start_point[0] + 1)

    # statements

    def statements(self, nodes) -> tuple:
        read = []
        for node in nodes:
            if node.type == "comment":
                continue
            read.append(self.statement(node))
        return tuple(read)

    def statement(self, node) -> Code:
        kind = node.type
        if kind == "compound_statement":
            return self.code("block", node, self.statements(node.named_children))
        if kind == "expression_statement":
            named = [child for child in node.named_children if child.type != "comment"]
            if not named:
                return self.code("empty", node, ())
            return self.code("do", node, (self.expression(named[0]),))
        if kind == "if_statement":
            return self.if_statement(node)
        if kind == "switch_statement":
            return self.switch_statement(node)
        if kind == "for_statement":
            return self.for_statement(node)
        if kind == "for_range_loop":
            loop_type = node.child_by_field_name("type")
            declared = (declared_name(node.child_by_field_name("declarator")),
                        self.text(loop_type) if loop_type is not None else "", None)
            # The loop's variable is declared afresh on every turn.
            header = self.header(node)
            turn = Code("block", header, (self.code("declare", node, (declared,), header),
                                          self.statement(node.child_by_field_name("body"))), node.start_point[0] + 1)
            return Code("loop", header, ("", turn, 0, None), node.start_point[0] + 1)
        if kind == "while_statement":
            return Code("loop", self.header(node), ("", self.statement(node.child_by_field_name("body")), 0, None),
                        node.start_point[0] + 1)
        if kind == "do_statement":
            return Code("loop", self.header(node), ("", self.statement(node.child_by_field_name("body")), 1, None),
                        node.start_point[0] + 1)
        if kind == "return_statement":
            return self.code("return", node, ())
        if kind == "break_statement":
            return self.code("break", node, ())
        if kind == "continue_statement":
            return self.code("continue", node, ())
        if kind == "declaration":
            return self.code("declare", node, self.declarations(node))
        return self.code("unread", node, ())

    def header(self, node) -> str:
        """A loop's text up to its body."""
        body = node.child_by_field_name("body")
        if body is None:
            return self.text(node)
        cut = node.text[: body.start_byte - node.start_byte].decode()
        written = collapsed(cut)
        if self.parameter and self.parameter != NODE:
            written = re.sub(rf"\b{re.escape(self.parameter)}\b", NODE, written)
        return written

    def declarations(self, node) -> tuple:
        """(name, type, value or None) per name declared. `auto x = e` is
        read as C++ means it, the type of `e`: `decltype(e)`."""
        declared_type = self.text(node.child_by_field_name("type")) if node.child_by_field_name("type") else ""
        read = []
        for index, child in enumerate(node.children):
            if node.field_name_for_child(index) != "declarator":
                continue
            if child.type == "init_declarator":
                name = declared_name(child.child_by_field_name("declarator"))
                value = child.child_by_field_name("value")
            else:
                # In a condition, `if (auto *X = e)`, the grammar puts `e`
                # on the declaration itself.
                name = declared_name(child)
                value = node.child_by_field_name("value")
            value_code = self.expression(value) if value is not None else None
            if declared_type == "auto" and value_code is not None:
                read.append((name, f"decltype({value_code.text})", value_code))
            else:
                read.append((name, declared_type, value_code))
        return tuple(read)

    def if_statement(self, node) -> Code:
        clause = node.child_by_field_name("condition")
        value = clause.child_by_field_name("value")
        if value is not None and value.type == "declaration":
            condition = self.code("declared", value, (self.code("declare", value, self.declarations(value)),))
        elif value is not None:
            condition = self.expression(value)
        else:
            condition = self.code("other", clause, ())
        then = self.statement(node.child_by_field_name("consequence"))
        otherwise = None
        alternative = node.child_by_field_name("alternative")
        if alternative is not None:
            inner = [child for child in alternative.named_children if child.type != "comment"]
            otherwise = self.statement(inner[0]) if inner else None
        choice = Code("if", self.text(clause), (condition, then, otherwise), node.start_point[0] + 1)
        initializer = clause.child_by_field_name("initializer")
        if initializer is None:
            return choice
        # `if (T *x = e; cond)`: the grammar wraps the declaration.
        while initializer.type not in ("declaration", "expression_statement") and initializer.named_children:
            initializer = initializer.named_children[0]
        first = self.statement(initializer)
        return Code("block", choice.text, (first, choice), choice.line)

    def switch_statement(self, node) -> Code:
        clause = node.child_by_field_name("condition")
        value = clause.child_by_field_name("value")
        subject = self.expression(value) if value is not None else self.code("other", clause, ())
        cases = []
        macro = None
        for child in node.child_by_field_name("body").named_children:
            if child.type == "comment":
                continue
            if child.type == "preproc_function_def":
                macro = child
                continue
            if child.type == "preproc_include":
                expanded = self.macro_cases(macro, child)
                if expanded is None:
                    return self.code("unread", child, ())
                cases.extend(expanded)
                continue
            if child.type != "case_statement":
                return self.code("unread", child, ())
            cases.append(self.case(child))
        return Code("switch", self.text(clause), (subject, tuple(cases)), node.start_point[0] + 1)

    def case(self, node) -> Code:
        label = node.child_by_field_name("value")
        labels = None if label is None else (self.expression(label),)
        body = [child for index, child in enumerate(node.children)
                if child.is_named and node.field_name_for_child(index) != "value"]
        return self.code("case", node, (labels, self.statements(body)))

    def macro_cases(self, macro, include):
        """The cases `#define M(...) body` writes over the lines of the
        `#include`d list that call M, as the preprocessor writes them: each
        parameter replaced by its argument, `#p` made a string, `a ## b`
        pasted into one word. None when there is no macro, or the list is
        not one the lowerer's build made and `made` gave."""
        if macro is None or self.parser is None:
            return None
        path = include.child_by_field_name("path")
        listed = self.made.get(path.text.decode().strip('"<>')) if path is not None else None
        if listed is None:
            return None
        name = macro.child_by_field_name("name").text.decode()
        parameters = [parameter.text.decode() for parameter in macro.child_by_field_name("parameters").named_children]
        body = macro.child_by_field_name("value").text.decode().replace("\\\n", " ")
        calls = re.findall(rf"^{re.escape(name)}\((.*)\)\s*$", listed, re.M)
        written = [expanded_macro(body, parameters, split_outside_literals(arguments, ",")) for arguments in calls]
        source = "void expanded() { switch (0) {\n" + "\n".join(written) + "\n} }\n"
        tree = self.parser.parse(source.encode())
        line = include.start_point[0] + 1
        cases = []
        pending = [tree.root_node]
        while pending:
            current = pending.pop(0)
            if current.type == "case_statement":
                cases.append(self.case(current)._replace(line=line))
                continue
            pending[0:0] = list(current.children)
        return cases

    def for_statement(self, node) -> Code:
        initializer = node.child_by_field_name("initializer")
        update = node.child_by_field_name("update")
        counter = ""
        first = None
        if initializer is not None and initializer.type == "declaration":
            first = self.statement(initializer)
            declared = first.parts
            if declared and isinstance(declared[0][2], Code) and declared[0][2].text == "0":
                if update is not None and update.type == "update_expression":
                    stepped = update.child_by_field_name("argument")
                    if stepped is not None and stepped.text.decode() == declared[0][0] and "++" in update.text.decode():
                        counter = declared[0][0]
        elif initializer is not None:
            first = self.code("do", initializer, (self.expression(initializer),))
        bound = self.counter_bound(node.child_by_field_name("condition"), counter, first)
        loop = Code("loop", self.header(node), (counter, self.statement(node.child_by_field_name("body")), 0, bound),
                    node.start_point[0] + 1)
        if first is None:
            return loop
        return Code("block", loop.text, (first, loop), loop.line)

    def counter_bound(self, condition, counter: str, first):
        """What a counter runs up to, `e` in `i != e` or `i < e`, as Code; a
        name the loop's own first statement declares stands for its value
        (`e = Call->getNumArgs()`). None when the condition is another
        shape."""
        if not counter or condition is None:
            return None
        if condition.type == "condition_clause":
            condition = condition.child_by_field_name("value")
        if condition is None or condition.type != "binary_expression":
            return None
        left = condition.child_by_field_name("left")
        if condition.child_by_field_name("operator").text.decode() not in ("!=", "<"):
            return None
        if left.type != "identifier" or left.text.decode() != counter:
            return None
        bound = self.expression(condition.child_by_field_name("right"))
        if bound.form == "name" and first is not None and first.form == "declare":
            for name, _declared_type, value in first.parts:
                if name == bound.parts[0] and value is not None:
                    return value
        return bound

    # expressions

    def expression(self, node) -> Code:
        kind = node.type
        if kind == "parenthesized_expression":
            named = [child for child in node.named_children if child.type != "comment"]
            if len(named) == 1:
                return self.expression(named[0])
            return self.code("other", node, ())
        if kind in ("string_literal", "char_literal", "concatenated_string"):
            decoded = literal_text(node)
            if decoded is None:
                return self.code("other", node, ())
            return self.code("text", node, (decoded,))
        if kind == "number_literal":
            return self.code("number", node, (node.text.decode(),))
        if kind in ("true", "false"):
            return self.code("truth", node, (kind == "true",))
        if kind in ("null", "nullptr"):
            return self.code("nothing", node, ())
        if kind == "identifier":
            return self.code("name", node, (self.text(node),))
        if kind == "unary_expression":
            operator = node.child_by_field_name("operator").text.decode()
            if operator == "!":
                return self.code("not", node, (self.expression(node.child_by_field_name("argument")),))
            return self.code("other", node, ())
        if kind == "binary_expression":
            operator = node.child_by_field_name("operator").text.decode()
            left = self.expression(node.child_by_field_name("left"))
            right = self.expression(node.child_by_field_name("right"))
            if operator == "&&":
                return self.code("and", node, (left, right))
            if operator == "||":
                return self.code("or", node, (left, right))
            if operator in COMPARISONS:
                return self.code("compare", node, (operator, left, right))
            return self.code("binary", node, (operator, left, right))
        if kind == "conditional_expression":
            return self.code("choose", node, (self.expression(node.child_by_field_name("condition")),
                                              self.expression(node.child_by_field_name("consequence")),
                                              self.expression(node.child_by_field_name("alternative"))))
        if kind == "call_expression":
            arguments = node.child_by_field_name("arguments")
            read = tuple(self.expression(argument) for argument in arguments.named_children
                         if argument.type != "comment")
            return self.code("call", node, (self.expression(node.child_by_field_name("function")), read))
        if kind == "field_expression":
            return self.code("member", node, (self.expression(node.child_by_field_name("argument")),
                                              node.child_by_field_name("field").text.decode()))
        if kind == "assignment_expression":
            if node.child_by_field_name("operator").text.decode() == "=":
                return self.code("assign", node, (self.expression(node.child_by_field_name("left")),
                                                  self.expression(node.child_by_field_name("right"))))
            return self.code("other", node, ())
        return self.code("other", node, ())


def expanded_macro(body: str, parameters: list, arguments: list) -> str:
    """A macro's body with its arguments in, as the preprocessor writes it:
    `#p` becomes the argument as a string, every other `p` the argument,
    and `a ## b` one word."""
    values = dict(zip(parameters, arguments))
    text = re.sub(r"(?<!#)#\s*(\w+)", lambda found: f'"{values[found.group(1)]}"' if found.group(1) in values
                  else found.group(0), body)
    text = re.sub(r"\b(\w+)\b", lambda found: values.get(found.group(1), found.group(1)), text)
    text = re.sub(r"\s*##\s*", "", text)
    return text


def literal_text(node):
    """The text a string or character literal stands for, or None when it
    holds something other than plain characters and escapes."""
    if node.type == "concatenated_string":
        parts = []
        for child in node.named_children:
            decoded = literal_text(child)
            if decoded is None:
                return None
            parts.append(decoded)
        return "".join(parts)
    pieces = []
    for child in node.named_children:
        if child.type in ("string_content", "character"):
            pieces.append(child.text.decode())
        elif child.type == "escape_sequence":
            pieces.append(codecs.decode(child.text.decode(), "unicode_escape"))
        else:
            return None
    return "".join(pieces)


# A line marker the preprocessor writes into its output, in place of the
# lines it leaves out: # <line> "<file>" <flags>. Flag 1 starts a file; flag
# 2 goes back to the file that #included it.
LINE_MARKER = re.compile(r'^# (\d+) "((?:[^"\\]|\\.)*)"((?: \d+)*)\s*$')

# The files whose text stays where they are #included, joined onto the
# #include's line: the lists a build keeps or makes for a switch or a table,
# never a header.
LIST_ENDINGS = (".inc", ".def")


def same_line_text(output: str, relative: str) -> str:
    """`relative`'s text as the preprocessor wrote it into `output` (its -E
    output, line markers kept): each of the file's lines at its own line
    number, every macro expanded, and each list it #includes joined onto the
    line of its #include. What the headers hold is left out."""
    lines = own_lines(output, relative)
    text = numbered_text(lines)
    return text


def own_lines(output: str, relative: str) -> dict:
    """line number -> text, for every line the output gives `relative`."""
    lines = {}
    files = []
    for written in output.split("\n"):
        marker = LINE_MARKER.match(written)
        if marker is None:
            keep_line(lines, files, written, relative)
        else:
            follow_marker(files, marker)
    return lines


def follow_marker(files: list, marker) -> None:
    """Moves the stack of open files, each [name, next line], as one line
    marker says."""
    line = int(marker.group(1))
    name = marker.group(2)
    flags = marker.group(3).split()
    if "1" in flags:
        files.append([name, line])
        return
    if "2" in flags:
        while files and files[-1][0] != name:
            files.pop()
    if files:
        files[-1] = [name, line]
    else:
        files.append([name, line])


def keep_line(lines: dict, files: list, written: str, relative: str) -> None:
    """Puts one line of the output where it belongs in `relative`'s text,
    then counts it in its own file."""
    if not files:
        return
    own = files[-1]
    depth = depth_of(files, relative)
    if depth == len(files) - 1:
        lines[own[1]] = written
    elif depth >= 0 and is_list(files[depth + 1][0]):
        site = files[depth][1]
        joined_onto(lines, site, written)
    own[1] = own[1] + 1


def depth_of(files: list, relative: str) -> int:
    """Where `relative` stands in the stack of open files, or -1."""
    depth = -1
    for position, entry in enumerate(files):
        if is_the_file(entry[0], relative):
            depth = position
    return depth


def is_the_file(name: str, relative: str) -> bool:
    found = name == relative or name.endswith("/" + relative)
    return found


def is_list(name: str) -> bool:
    found = name.endswith(LIST_ENDINGS)
    return found


def joined_onto(lines: dict, line: int, written: str) -> None:
    """Joins one line of an #included list onto the line of its #include."""
    if not written.strip():
        return
    before = lines.get(line, "")
    joined = before + " " + written
    lines[line] = joined.strip()


def numbered_text(lines: dict) -> str:
    """The lines, each at its own number, the ones the output never gave
    left empty."""
    last = 0
    for line in lines:
        last = max(last, line)
    written = []
    for line in range(1, last + 1):
        written.append(lines.get(line, ""))
    text = "\n".join(written) + "\n"
    return text
