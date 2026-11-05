#!/usr/bin/env python3
"""lean_reader.py -- A READER OF THE LEAN THE SAIL COMPILER EMITS, into z3
terms (task sl1, route (b) of the brief).

Node: hq.research.arch_unit_oracle.architectures.riscv64.lifter_from_sail.

WHAT THIS FILE IS, one sentence, in relation: the small interpreter that
knows the dozen constructs of the Lean the sail compiler writes for the
model's `execute` clauses -- application, let, bind, if, match, the
integer and bit-vector operators of Lean's own library, a register read
and a register write -- and nothing about any instruction; it turns one
emitted definition, applied to concrete fields and symbolic register
values, into the z3 term each written register receives.

HOW IT READS.  Stage 1 tokenizes and parses every `def` of the emit into
a small expression tree.  Stage 2 evaluates a definition's body with an
environment: fields bound to concrete values (the decoded word's), the
register file a mapping name -> z3 term (a read of an unbound register
seeds a fresh symbol), and every Lean library primitive it meets mapped
to the z3 operation of the same meaning by a fixed table (`PRIMITIVES`)
-- Lean's `Int` operations at a fixed wide width (`INT_WIDTH`), which is
the widening rule of log_274: every integer of a definition came from a
register, so it is bounded, and a width that loses nothing is chosen
once for all of them.  A call of an emitted definition is evaluated by
binding its parameters and reading its body; a primitive with no entry
in the table is a refusal, by name, never a guess.

THE SPELLING BAN, pasted verbatim as required:

"THE SPELLING BAN, ABSOLUTE (the owner, restated in anger 2026-08-25 after a
second violation).  No operator token may appear in ANY key, grouping,
pairing, row structure, candidate selection, or comparison scope,
anywhere in this line -- not in matching, not in "which pairs get
compared", not in report rows, not in dropdowns.  The candidate set for
comparison comes from machine-form evidence (clusters, connections,
type pairs) or from ratified intention -- never from the token.  The
token appears exactly once per unit: as a display label on the member.
HISTORY OF VIOLATIONS, so the pattern is visible: (1) the arch
campaign's cross-language matrix (caught by the owner 2026-08-24); (2)
verdicts.py's row pairing (caught by the owner 2026-08-25 -- the fix brief
itself reintroduced it as "same-operator pairs").  MECHANICAL GUARD
REQUIRED: every pipeline stage that groups or pairs units must run the
spelling-key check (op_pipeline/check_no_spelling_keys.py) and refuse
its own output on failure.  A brief handed to any subagent for this
line MUST paste this paragraph verbatim."

HOW THIS FILE OBEYS IT: nothing here is keyed by a mnemonic; a
definition is found by the constructor the model's own decoder names
for a word, and the primitive table is keyed by Lean library function
names, which are constructs, not instructions.

Coding discipline (the owner's ruling): no complex/compound one-liner statements.
"""
import gzip
import os
import re
import sys

import z3

sys.setrecursionlimit(50000)

INT_WIDTH = 132
"""the one width every Lean `Int` of a definition is carried at: wide
enough for a 64 by 64 product (128 bits) with sign and room, chosen once."""

MAX_DEPTH = 400


class ReadRefused(Exception):
    """the reader met something it does not know, and says what."""


class EarlyReturn(Exception):
    """a Lean `return`: the definition's value is decided here."""

    def __init__(self, value):
        Exception.__init__(self, "return")
        self.value = value


# ==================================================================
# section 1: tokens
# ==================================================================

OPERATORS = [
    "+++", "≥b", "≤b", "<b", ">b", "+i", "-i", "*i", "^i", "/i", "%i",
    "&&&", "|||", "^^^", "<<<", ">>>", "++", "&&", "||", "==", "!=",
    "≠", "≥", "≤", ">=", "<=", ":=", "=>", "←", "->", "→", "+", "-",
    "*", "/", "%", "^", "<", ">", "=", "|", "&", "!", "¬", "$",
]
PUNCTUATION = ["(", ")", "[", "]", "{", "}", ",", ":", "@", "#", ".", ";", "⟨", "⟩"]

IDENT_RE = re.compile(r"[A-Za-z_Ͱ-Ͽ][A-Za-z0-9_'!?Ͱ-Ͽ]*(?:\.[A-Za-z_][A-Za-z0-9_'!?]*)*")
NUMBER_RE = re.compile(r"0x[0-9a-fA-F_]+|0b[01_]+|[0-9][0-9_]*")


class Token(object):
    def __init__(self, kind, text, line, column):
        self.kind = kind
        self.text = text
        self.line = line
        self.column = column

    def __repr__(self):
        return "Token(%s, %r, %d:%d)" % (self.kind, self.text, self.line,
                                         self.column)


def tokenize(text):
    """[Token]; kinds: ident, number, string, op, punct, newline."""
    out = []
    line = 1
    column = 0
    index = 0
    length = len(text)
    while index < length:
        char = text[index]
        if char == "\n":
            out.append(Token("newline", "\n", line, column))
            line = line + 1
            column = 0
            index = index + 1
            continue
        if char in " \t\r":
            index = index + 1
            column = column + 1
            continue
        if text.startswith("--", index):
            end = text.find("\n", index)
            if end < 0:
                end = length
            column = column + (end - index)
            index = end
            continue
        if text.startswith("/-", index):
            end = text.find("-/", index)
            if end < 0:
                end = length
            else:
                end = end + 2
            skipped = text[index:end]
            line = line + skipped.count("\n")
            index = end
            continue
        if char == '"':
            end = index + 1
            while end < length and text[end] != '"':
                if text[end] == "\\":
                    end = end + 1
                end = end + 1
            out.append(Token("string", text[index + 1:end], line, column))
            column = column + (end + 1 - index)
            index = end + 1
            continue
        hit = NUMBER_RE.match(text, index)
        if hit is not None and not (char.isalpha() or char == "_"):
            out.append(Token("number", hit.group(0), line, column))
            column = column + len(hit.group(0))
            index = hit.end()
            continue
        hit = IDENT_RE.match(text, index)
        if hit is not None:
            out.append(Token("ident", hit.group(0), line, column))
            column = column + len(hit.group(0))
            index = hit.end()
            continue
        matched = None
        for op in OPERATORS:
            if text.startswith(op, index):
                matched = op
                break
        if matched is not None and matched not in PUNCTUATION:
            out.append(Token("op", matched, line, column))
            column = column + len(matched)
            index = index + len(matched)
            continue
        if char in PUNCTUATION:
            out.append(Token("punct", char, line, column))
            column = column + 1
            index = index + 1
            continue
        out.append(Token("weird", char, line, column))
        column = column + 1
        index = index + 1
    out.append(Token("newline", "\n", line, column))
    return out


# ==================================================================
# section 2: the expression tree
# ==================================================================
#
# A node is a tuple whose first element names its kind:
#   ("var", name)                     ("num", text)          ("str", text)
#   ("app", head, [args])             head is a node; args are nodes or
#                                     ("named", name, node) for `(l := 64)`
#   ("binop", op, left, right)        ("neg", node)
#   ("if", c, a, b)                   ("match", scrutinee, [(pattern, node)])
#   ("let", name, value, body)        a `let` in a do-block or term
#   ("bind", name, value, body)       `let name ← value; body`
#   ("seq", first, rest)              a do-block statement then the rest
#   ("ascribe", node, typetext)       `(e : T)`
#   ("bindexpr", node)                `(← e)`
#   ("fun", [params], body)
#   ("tuple", [nodes])
#   ("unit",)
# A pattern is ("pvar", name) | ("pwild",) | ("pctor", name, [patterns])
# | ("ptuple", [patterns]) | ("pnum", text) | ("pstr", text).

LOWERCASE_CONSTRUCTORS = frozenset([
    "none", "some", "true", "false",
    "float_class_negative_inf", "float_class_negative_normal",
    "float_class_negative_subnormal", "float_class_negative_zero",
    "float_class_positive_zero", "float_class_positive_subnormal",
    "float_class_positive_normal", "float_class_positive_inf",
    "float_class_snan", "float_class_qnan",
])


class Parser(object):
    def __init__(self, tokens):
        self.tokens = tokens
        self.position = 0

    # -- helpers -------------------------------------------------------

    def peek(self, offset=0):
        index = self.position + offset
        if index < len(self.tokens):
            return self.tokens[index]
        return Token("eof", "", -1, -1)

    def advance(self):
        token = self.peek()
        self.position = self.position + 1
        return token

    def at(self, kind, text=None):
        token = self.peek()
        if token.kind != kind:
            return False
        if text is not None and token.text != text:
            return False
        return True

    def expect(self, kind, text=None):
        if not self.at(kind, text):
            token = self.peek()
            raise ReadRefused("expected %s %r, found %s %r at %d:%d"
                              % (kind, text, token.kind, token.text,
                                 token.line, token.column))
        return self.advance()

    def skip_newlines(self):
        while self.at("newline"):
            self.advance()

    def next_significant(self):
        """the next token that is not a newline, without consuming."""
        offset = 0
        while self.peek(offset).kind == "newline":
            offset = offset + 1
        return self.peek(offset)

    # -- top level -----------------------------------------------------

    def definitions(self):
        """{name: (params, body)} for every `def`/`noncomputable def` and
        every `abbrev`/`instance`-free definition of the file; everything
        else at top level is skipped to the next top-level keyword."""
        out = {}
        order = []
        while not self.at("eof"):
            token = self.peek()
            if token.kind == "ident" and token.text in ("def", "abbrev") \
                    and token.column == 0:
                start = self.position
                try:
                    name, params, body = self.definition()
                except ReadRefused as problem:
                    self.position = start
                    self.unread.append((self.peek(1).text, "%s" % problem))
                    self.skip_to_next_top_level()
                    continue
                if name not in out:
                    out[name] = (params, body)
                    self.keywords[name] = self.last_keyword
                    order.append(name)
                elif self.keywords.get(name) == "abbrev" and \
                        self.last_keyword == "def":
                    # the emit declares a few names twice: an `abbrev` in
                    # its types file and a `def` in its functions file;
                    # the def is the computed value and wins
                    out[name] = (params, body)
                    self.keywords[name] = "def"
                continue
            if token.kind == "ident" and token.text == "noncomputable" \
                    and token.column == 0:
                self.advance()
                following = self.peek()
                if following.kind == "ident" and following.text in ("def", "abbrev"):
                    following.column = 0
                continue
            self.skip_to_next_top_level()
        return out, order

    def skip_to_next_top_level(self):
        self.advance()
        while not self.at("eof"):
            token = self.peek()
            if token.column == 0 and token.kind == "ident" and \
                    token.text in ("def", "abbrev", "noncomputable",
                                   "theorem", "instance", "structure",
                                   "inductive", "open", "namespace",
                                   "end", "set_option", "import",
                                   "section", "mutual", "termination_by",
                                   "decreasing_by", "deriving", "class",
                                   "@[", "private", "protected",
                                   "partial", "unsafe", "opaque",
                                   "axiom", "example", "attribute",
                                   "initialize", "syntax", "macro",
                                   "elab", "notation", "infix", "infixl",
                                   "infixr", "prefix", "postfix",
                                   "variable", "universe", "export",
                                   "scoped", "local", "where"):
                return
            self.advance()

    def definition(self):
        keyword = self.advance().text           # def / abbrev
        name = self.expect("ident").text
        self.last_keyword = keyword
        params = []
        while self.at("punct", "(") or self.at("punct", "{") or \
                self.at("punct", "["):
            close = {"(": ")", "{": "}", "[": "]"}[self.advance().text]
            names = []
            while self.at("ident"):
                names.append(self.advance().text)
            typetext = ""
            if self.at("punct", ":"):
                self.advance()
                typetext = self.type_text(close)
            self.expect("punct", close)
            for item in names:
                params.append((item, typetext))
        typetext = ""
        if self.at("punct", ":"):
            self.advance()
            typetext = self.type_text_until_assign()
        self.expect("op", ":=")
        body = self.expression()
        return name, params, body

    def type_text(self, close):
        depth = 0
        parts = []
        while True:
            token = self.peek()
            if token.kind == "eof":
                break
            if token.kind == "punct" and token.text in "([{":
                depth = depth + 1
            if token.kind == "punct" and token.text in ")]}":
                if depth == 0:
                    break
                depth = depth - 1
            if token.kind != "newline":
                parts.append(token.text)
            self.advance()
        return " ".join(parts)

    def type_text_until_assign(self):
        depth = 0
        parts = []
        while True:
            token = self.peek()
            if token.kind == "eof":
                break
            if token.kind == "op" and token.text == ":=" and depth == 0:
                break
            if token.kind == "punct" and token.text in "([{":
                depth = depth + 1
            if token.kind == "punct" and token.text in ")]}":
                depth = depth - 1
            if token.kind != "newline":
                parts.append(token.text)
            self.advance()
        return " ".join(parts)

    # -- expressions ---------------------------------------------------

    def expression(self):
        self.skip_newlines()
        token = self.peek()
        if token.kind == "ident" and token.text == "do":
            self.advance()
            return self.do_block()
        if token.kind == "ident" and token.text == "if":
            return self.if_expression()
        if token.kind == "ident" and token.text == "match":
            return self.match_expression()
        if token.kind == "ident" and token.text == "let":
            return self.let_expression()
        if token.kind == "ident" and token.text == "fun":
            return self.fun_expression()
        return self.binary(0)

    def do_block(self):
        """statements at one indentation column, each a `let`, a bind, or
        an expression; the last is the block's value."""
        self.skip_newlines()
        column = self.peek().column
        statements = []
        while not self.at("eof"):
            self.skip_newlines()
            token = self.peek()
            if token.kind == "eof" or token.column != column:
                break
            if token.kind == "punct" and token.text in ")]}":
                break
            if token.kind == "op" and token.text == "|":
                break
            statements.append(self.statement(column))
        return self.fold_statements(statements)

    def statement(self, column):
        token = self.peek()
        if token.kind == "ident" and token.text == "for":
            return self.for_statement(column)
        if token.kind == "ident" and self.peek(1).kind == "op" and \
                self.peek(1).text in (":=", "←"):
            name = self.advance().text
            kind = self.advance().text
            value = self.expression_until_column(column)
            return ("assignstmt", name, value, kind)
        if token.kind == "ident" and token.text == "let":
            self.advance()
            mutable = False
            if self.at("ident", "mut"):
                self.advance()
                mutable = True
            name = self.pattern_or_name()
            if mutable:
                if self.at("punct", ":"):
                    self.advance()
                    self.type_text_until_binder()
                kind = self.advance().text
                value = self.expression_until_column(column)
                return ("mutstmt", name, value, kind)
            if self.at("punct", ":"):
                self.advance()
                self.type_text_until_binder()
            if self.at("op", "←"):
                self.advance()
                value = self.expression_until_column(column)
                return ("bindstmt", name, value)
            self.expect("op", ":=")
            value = self.expression_until_column(column)
            return ("letstmt", name, value)
        value = self.expression_until_column(column)
        return ("exprstmt", value)

    def for_statement(self, column):
        """`for i in [lo:hi:step]i do` and its block, the bounds inclusive
        as Sail's foreach is."""
        self.expect("ident", "for")
        variable = self.expect("ident").text
        self.expect("ident", "in")
        self.expect("punct", "[")
        lower = self.expression()
        self.expect("punct", ":")
        upper = self.expression()
        step = ("num", "1")
        if self.at("punct", ":"):
            self.advance()
            step = self.expression()
        self.expect("punct", "]")
        if self.at("ident", "i"):
            self.advance()
        self.expect("ident", "do")
        block = self.do_block()
        return ("forstmt", variable, lower, upper, step, block)

    def pattern_or_name(self):
        if self.at("punct", "(") or self.at("punct", "."):
            return self.pattern()
        return ("pvar", self.expect("ident").text)

    def type_text_until_binder(self):
        parts = []
        depth = 0
        while True:
            token = self.peek()
            if token.kind == "eof":
                break
            if depth == 0 and token.kind == "op" and \
                    token.text in (":=", "←"):
                break
            if token.kind == "punct" and token.text in "([{":
                depth = depth + 1
            if token.kind == "punct" and token.text in ")]}":
                depth = depth - 1
            parts.append(token.text)
            self.advance()
        return " ".join(parts)

    def expression_until_column(self, column):
        """an expression that ends at the first newline followed by a token
        at `column` or less (the next statement), or at a closing bracket."""
        node = self.expression_bounded(column)
        return node

    def expression_bounded(self, column):
        self.bound_columns.append(column)
        try:
            return self.expression()
        finally:
            self.bound_columns.pop()

    def fold_statements(self, statements):
        if not statements:
            return ("unit",)
        last = statements[-1]
        if last[0] != "exprstmt":
            body = ("unit",)
        else:
            body = last[1]
            statements = statements[:-1]
        for statement in reversed(statements):
            if statement[0] == "letstmt":
                body = ("let", statement[1], statement[2], body)
            elif statement[0] == "bindstmt":
                body = ("bind", statement[1], statement[2], body)
            elif statement[0] == "mutstmt":
                body = ("mut", statement[1], statement[2], body)
            elif statement[0] == "assignstmt":
                body = ("assign", statement[1], statement[2], body)
            elif statement[0] == "forstmt":
                body = ("for", statement[1], statement[2], statement[3],
                        statement[4], statement[5], body)
            else:
                body = ("seq", statement[1], body)
        return body

    def if_expression(self):
        self.expect("ident", "if")
        condition = self.expression()
        self.skip_newlines()
        self.expect("ident", "then")
        yes = self.expression()
        self.skip_newlines()
        self.expect("ident", "else")
        no = self.expression()
        return ("if", condition, yes, no)

    def match_expression(self):
        self.expect("ident", "match")
        scrutinees = [self.expression()]
        while self.at("punct", ","):
            self.advance()
            scrutinees.append(self.expression())
        self.skip_newlines()
        self.expect("ident", "with")
        arms = []
        while True:
            self.skip_newlines()
            if not self.at("op", "|"):
                break
            token = self.peek()
            if self.bound_columns and token.column < self.bound_columns[-1]:
                break
            self.advance()
            patterns = [self.pattern()]
            while self.at("punct", ","):
                self.advance()
                patterns.append(self.pattern())
            self.expect("op", "=>")
            body = self.expression()
            if len(patterns) == 1:
                arms.append((patterns[0], body))
            else:
                arms.append((("ptuple", patterns), body))
        if len(scrutinees) == 1:
            return ("match", scrutinees[0], arms)
        return ("match", ("tuple", scrutinees), arms)

    def pattern(self):
        token = self.peek()
        if token.kind == "punct" and token.text == "(":
            self.advance()
            if self.at("punct", ")"):
                self.advance()
                return ("pwild",)
            items = [self.pattern()]
            while self.at("punct", ","):
                self.advance()
                items.append(self.pattern())
            self.expect("punct", ")")
            if len(items) == 1:
                return items[0]
            return ("ptuple", items)
        if token.kind == "number":
            self.advance()
            return ("pnum", token.text)
        if token.kind == "string":
            self.advance()
            return ("pstr", token.text)
        if token.kind == "punct" and token.text == ".":
            self.advance()
            name = self.expect("ident").text
            return self.constructor_pattern(name)
        if token.kind == "ident":
            self.advance()
            if token.text == "_":
                return ("pwild",)
            return self.constructor_pattern(token.text)
        raise ReadRefused("cannot read a pattern at %d:%d (%r)"
                          % (token.line, token.column, token.text))

    def constructor_pattern(self, name):
        args = []
        while True:
            token = self.peek()
            if token.kind == "ident" and token.text not in ("with",):
                if token.text == "_":
                    self.advance()
                    args.append(("pwild",))
                    continue
                self.advance()
                args.append(("pvar", token.text))
                continue
            if token.kind == "punct" and token.text == "(":
                args.append(self.pattern())
                continue
            if token.kind == "punct" and token.text == ".":
                self.advance()
                inner = self.expect("ident").text
                args.append(("pctor", inner, []))
                continue
            break
        if not args and (name[:1].islower() or name[:1] == "_") and \
                "." not in name and name not in LOWERCASE_CONSTRUCTORS:
            return ("pvar", name)
        return ("pctor", name, args)

    def let_expression(self):
        column = self.expect("ident", "let").column
        name = self.pattern_or_name()
        if self.at("punct", ":"):
            self.advance()
            self.type_text_until_binder()
        kind = "let"
        if self.at("op", "←"):
            self.advance()
            kind = "bind"
        else:
            self.expect("op", ":=")
        value = self.expression_bounded(column)
        self.skip_newlines()
        if self.at("punct", ";"):
            self.advance()
        body = self.expression()
        return (kind, name, value, body)

    def fun_expression(self):
        self.expect("ident", "fun")
        params = []
        while not self.at("op", "=>"):
            if self.at("punct", "("):
                self.advance()
                while self.at("ident"):
                    params.append(self.advance().text)
                if self.at("punct", ":"):
                    self.advance()
                    self.type_text(")")
                self.expect("punct", ")")
                continue
            params.append(self.expect("ident").text)
        self.expect("op", "=>")
        body = self.expression()
        return ("fun", params, body)

    BINARY = [
        ["||"], ["&&"], ["==", "!=", "≠", "=", "<", ">", "<=", ">=", "≤", "≥",
                        "<b", ">b", "≤b", "≥b"],
        ["|||"], ["^^^"], ["&&&"], ["<<<", ">>>"], ["++", "+++"],
        ["+", "-", "+i", "-i"], ["*", "/", "%", "*i", "/i", "%i"],
        ["^", "^i"],
    ]

    def binary(self, level):
        if level >= len(self.BINARY):
            return self.application()
        left = self.binary(level + 1)
        while True:
            token = self.next_significant()
            if token.kind == "op" and token.text in self.BINARY[level]:
                if self.newline_ends_here():
                    break
                self.skip_newlines()
                self.advance()
                right = self.binary(level + 1)
                left = ("binop", token.text, left, right)
                continue
            break
        return left

    def newline_ends_here(self):
        """a newline followed by a token at or left of the bound column
        ends the current expression (the next do-statement or match arm);
        a token at column 0 (the next top-level item) always does."""
        if not self.at("newline"):
            return False
        token = self.next_significant()
        if token.column == 0:
            return True
        if not self.bound_columns:
            return False
        return token.column <= self.bound_columns[-1]

    def application(self):
        head = self.atom()
        args = []
        while True:
            if self.at("newline"):
                if self.newline_ends_here():
                    break
                token = self.next_significant()
                if not self.starts_atom(token):
                    break
                self.skip_newlines()
            token = self.peek()
            if not self.starts_atom(token):
                break
            args.append(self.atom())
        if args:
            return ("app", head, args)
        return head

    def starts_atom(self, token):
        if token.column == 0:
            return False
        if token.kind in ("ident", "number", "string"):
            if token.kind == "ident" and token.text in (
                    "then", "else", "with", "if", "match",
                    "let", "in", "from", "at", "where"):
                return False
            return True
        if token.kind == "punct" and token.text in ("(", "[", ".", "⟨", "{"):
            return True
        if token.kind == "punct" and token.text == "#":
            return True
        if token.kind == "op" and token.text in ("←", "!", "¬"):
            return True
        return False

    def atom(self):
        node = self.bare_atom()
        while self.at("punct", ".") and self.peek(1).kind in ("ident", "number") \
                and self.peek(1).column == self.peek().column + 1:
            self.advance()
            node = ("proj", node, self.advance().text)
        return node

    def bare_atom(self):
        self.skip_newlines()
        token = self.peek()
        if token.kind == "punct" and token.text == "⟨":
            self.advance()
            items = []
            while not self.at("punct", "⟩"):
                items.append(self.expression())
                self.skip_newlines()
                if self.at("punct", ","):
                    self.advance()
            self.expect("punct", "⟩")
            return ("tuple", items)
        if token.kind == "punct" and token.text == "#" and \
                self.peek(1).kind == "ident" and self.peek(1).text == "v" and \
                self.peek(2).kind == "punct" and self.peek(2).text == "[":
            self.advance()
            self.advance()
            self.advance()
            items = []
            while not self.at("punct", "]"):
                items.append(self.expression())
                self.skip_newlines()
                if self.at("punct", ","):
                    self.advance()
            self.expect("punct", "]")
            return ("list", items)
        if token.kind == "punct" and token.text == "{":
            self.advance()
            fields = []
            self.skip_newlines()
            column = self.peek().column
            while not self.at("punct", "}"):
                name = self.expect("ident").text
                self.expect("op", ":=")
                fields.append((name, self.expression_bounded(column)))
                self.skip_newlines()
                if self.at("punct", ","):
                    self.advance()
                    self.skip_newlines()
            self.expect("punct", "}")
            return ("struct", fields)
        if token.kind == "number":
            self.advance()
            if self.at("punct", "#"):
                self.advance()
                width = self.expect("number").text
                return ("bv", token.text, width)
            return ("num", token.text)
        if token.kind == "string":
            self.advance()
            return ("str", token.text)
        if token.kind == "ident":
            self.advance()
            if token.text == "if":
                self.position = self.position - 1
                return self.if_expression()
            if token.text == "match":
                self.position = self.position - 1
                return self.match_expression()
            if token.text == "fun":
                self.position = self.position - 1
                return self.fun_expression()
            if token.text == "do":
                return self.do_block()
            if token.text == "let":
                self.position = self.position - 1
                return self.let_expression()
            return ("var", token.text)
        if token.kind == "punct" and token.text == ".":
            self.advance()
            name = self.expect("ident").text
            return ("var", "." + name)
        if token.kind == "op" and token.text in ("!", "¬"):
            self.advance()
            return ("app", ("var", "Bool.not"), [self.atom()])
        if token.kind == "op" and token.text == "-":
            self.advance()
            return ("app", ("var", "Neg.neg"), [self.atom()])
        if token.kind == "op" and token.text == "←":
            self.advance()
            return ("bindexpr", self.expression())
        if token.kind == "punct" and token.text == "[":
            self.advance()
            items = []
            while not self.at("punct", "]"):
                items.append(self.expression())
                if self.at("punct", ","):
                    self.advance()
            self.expect("punct", "]")
            return ("list", items)
        if token.kind == "punct" and token.text == "(":
            self.advance()
            self.skip_newlines()
            if self.at("punct", ")"):
                self.advance()
                return ("unit",)
            # named argument `(l := 64)`
            if self.at("ident") and self.peek(1).kind == "op" and \
                    self.peek(1).text == ":=":
                name = self.advance().text
                self.advance()
                value = self.expression()
                self.skip_newlines()
                self.expect("punct", ")")
                return ("named", name, value)
            self.bound_columns.append(-1)
            try:
                inner = self.expression()
                self.skip_newlines()
                if self.at("punct", ":"):
                    self.advance()
                    typetext = self.type_text(")")
                    self.expect("punct", ")")
                    return ("ascribe", inner, typetext)
                if self.at("punct", ","):
                    items = [inner]
                    while self.at("punct", ","):
                        self.advance()
                        items.append(self.expression())
                        self.skip_newlines()
                    self.expect("punct", ")")
                    return ("tuple", items)
                self.expect("punct", ")")
            finally:
                self.bound_columns.pop()
            return inner
        raise ReadRefused("cannot read an expression at %d:%d (%s %r)"
                          % (token.line, token.column, token.kind,
                             token.text))


def parse_file(text):
    parser = Parser(tokenize(text))
    parser.bound_columns = []
    parser.unread = []
    parser.keywords = {}
    parser.last_keyword = "def"
    found, order = parser.definitions()
    return found, order, parser.unread, parser.keywords


WIDTH_ARM = re.compile(r"^\s*\|\s*\.([A-Za-z_][A-Za-z0-9_]*)\s*=>\s*(.*?)\s*$")
ABBREV = re.compile(r"^abbrev\s+([A-Za-z_][A-Za-z0-9_]*)\s*:=\s*(.*?)\s*$")
BITVEC_N = re.compile(r"^\(?BitVec\s+(\d+)\)?$")
BITVEC_IF = re.compile(r"^\(?BitVec\s*\(if\s*\(\s*(true|false)\s*:\s*Bool\s*\)\s*then\s*(\d+)\s*else\s*(\d+)\s*\*\s*(\d+)\s*\)\)?$")


def open_lean_file(path):
    if path.endswith(".lean.gz"):
        return gzip.open(path, "rt", encoding="utf-8")
    return open(path, encoding="utf-8")


def register_widths(directory):
    """{register name: width} for every register whose type in the emit's
    own `RegisterType` table is a bit-vector of a stated width, the
    abbreviations of the emit resolved."""
    abbrevs = {}
    arms = {}
    inside = False
    for root, _dirs, files in os.walk(directory):
        for name in sorted(files):
            if not (name.endswith(".lean") or name.endswith(".lean.gz")):
                continue
            for line in open_lean_file(os.path.join(root, name)):
                hit = ABBREV.match(line)
                if hit is not None:
                    abbrevs[hit.group(1)] = hit.group(2)
                if line.startswith("abbrev RegisterType"):
                    inside = True
                    continue
                if inside:
                    hit = WIDTH_ARM.match(line)
                    if hit is None:
                        if line.strip() and not line.startswith(" "):
                            inside = False
                        continue
                    arms[hit.group(1)] = hit.group(2)
    widths = {}
    for register, typetext in arms.items():
        width = width_of_type(typetext, abbrevs, 0)
        if width is not None:
            widths[register] = width
    return widths


def width_of_type(typetext, abbrevs, depth):
    text = typetext.strip()
    hit = BITVEC_N.match(text)
    if hit is not None:
        return int(hit.group(1))
    hit = BITVEC_IF.match(text.replace("\n", " "))
    if hit is not None:
        # the printer writes `if c then A else B * C` for `(if c then A
        # else B) * C`: the bytes of the width times eight
        chosen = int(hit.group(2)) if hit.group(1) == "true" else int(hit.group(3))
        return chosen * int(hit.group(4))
    if text in abbrevs and depth < 8:
        return width_of_type(abbrevs[text], abbrevs, depth + 1)
    return None


def parse_emit(directory):
    """{name: (params, body)} over every .lean file of the emit, and the
    file each came from."""
    definitions = {}
    origin = {}
    for root, _dirs, files in os.walk(directory):
        for name in sorted(files):
            if not (name.endswith(".lean") or name.endswith(".lean.gz")):
                continue
            path = os.path.join(root, name)
            rel_path = os.path.relpath(path, directory)
            if rel_path.endswith(".gz"):
                rel_path = rel_path[:-3]
            text = open_lean_file(path).read()
            found, order, unread, keywords = parse_file(text)
            for key in order:
                if key not in definitions:
                    definitions[key] = found[key]
                    origin[key] = rel_path
                    origin.setdefault("KEYWORD", {})[key] = keywords.get(key)
                elif origin.get("KEYWORD", {}).get(key) == "abbrev" and \
                        keywords.get(key) == "def":
                    definitions[key] = found[key]
                    origin[key] = rel_path
                    origin["KEYWORD"][key] = "def"
            for name, cause in unread:
                origin.setdefault("UNREAD", []).append(
                    (rel_path, name, cause))
    return definitions, origin


if __name__ == "__main__":
    definitions, origin = parse_emit(sys.argv[1])
    print("definitions parsed: %d" % len(definitions))
    unread = origin.get("UNREAD", [])
    print("definitions the parser could not read: %d" % len(unread))
    for item in unread[:40]:
        print("  UNREAD %s %s: %s" % item)
    for name in sorted(definitions):
        if name.startswith("execute_"):
            print(name, [p[0] for p in definitions[name][0]], origin[name])


# ==================================================================
# section 3: values and the machine
# ==================================================================

class LInt(object):
    """a Lean `Int` or `Nat`, carried as a z3 bit-vector of INT_WIDTH bits,
    two's complement (the widening rule, one width for all)."""

    def __init__(self, term):
        self.term = term

    def __repr__(self):
        return "LInt(%s)" % self.term


class EmptyBits(object):
    """a bit-vector of width zero (Lean allows it; z3 does not): the unit
    of append, and what an extract of an empty range yields."""

    def __repr__(self):
        return "EmptyBits()"


class Ctor(object):
    """a value of an inductive type: a constructor name and its arguments
    (an enum member has none)."""

    def __init__(self, name, args):
        self.name = name
        self.args = list(args)

    def __repr__(self):
        return "Ctor(%s, %r)" % (self.name, self.args)


class Closure(object):
    def __init__(self, params, body, env, name="(closure)"):
        self.params = params
        self.body = body
        self.env = env
        self.name = name


class Cell(object):
    """a `let mut` variable: one shared box, so an assignment inside a
    loop body reaches the binding outside it."""

    def __init__(self, value):
        self.value = value


class RegisterName(object):
    """an unevaluated register identifier handed to readReg / writeReg."""

    def __init__(self, name):
        self.name = name


class Machine(object):
    """the register file the reader threads: name -> value; an unbound
    register reads a fresh symbol of the width the definition asks for
    (recorded in `seeds`), and every write is recorded in `writes`."""

    def __init__(self, widths=None, initial=None):
        self.registers = {}
        if initial:
            self.registers.update(initial)
        self.widths = widths or {}
        self.seeds = {}
        self.writes = []
        self.reads = []

    def read(self, name, width=None):
        if name in self.registers:
            self.reads.append(name)
            return self.registers[name]
        if width is None:
            width = self.widths.get(name)
        if width is None:
            raise ReadRefused("register %s read before any write and its "
                              "width is not known" % name)
        # a register the model never wrote reads ZERO, as the model's own C
        # simulator starts (every register zero-initialised); the walk's
        # inputs -- the x and f registers, the program counter -- are
        # bound before any read and never reach this line
        value = z3.BitVecVal(0, width)
        self.seeds[name] = value
        self.registers[name] = value
        self.reads.append(name)
        return value

    def write(self, name, value):
        self.registers[name] = value
        self.writes.append((name, value))

    def copy(self):
        other = self.__class__.__new__(self.__class__)
        other.__dict__.update(self.__dict__)
        other.registers = dict(self.registers)
        other.writes = list(self.writes)
        other.reads = list(self.reads)
        return other


def int_of(value):
    if isinstance(value, LInt):
        return value.term
    if isinstance(value, int):
        return z3.BitVecVal(value, INT_WIDTH)
    if z3.is_bv(value):
        if value.size() == INT_WIDTH:
            return value
        raise ReadRefused("a %d-bit vector where an integer was wanted"
                          % value.size())
    raise ReadRefused("not an integer: %r" % (value,))


def lint(term):
    if isinstance(term, int):
        term = z3.BitVecVal(term, INT_WIDTH)
    return LInt(term)


def bv_of(value):
    if z3.is_bv(value):
        return value
    if isinstance(value, Closure):
        raise ReadRefused("not a bit-vector: the definition %s, applied to "
                          "too few arguments (%d left)"
                          % (value.name, len(value.params)))
    if isinstance(value, bool):
        return z3.BitVecVal(1 if value else 0, 1)
    if z3.is_bool(value):
        return z3.If(value, z3.BitVecVal(1, 1), z3.BitVecVal(0, 1))
    raise ReadRefused("not a bit-vector: %r" % (value,))


def bool_of(value):
    if isinstance(value, bool):
        return z3.BoolVal(value)
    if z3.is_bool(value):
        return value
    if z3.is_bv(value) and value.size() == 1:
        return value == z3.BitVecVal(1, 1)
    raise ReadRefused("not a boolean: %r" % (value,))


def concrete_int(value):
    """the Python integer a value holds, when it is constant."""
    if isinstance(value, int):
        return value
    term = value.term if isinstance(value, LInt) else value
    if z3.is_bv(term):
        simplified = z3.simplify(term)
        if z3.is_bv_value(simplified):
            width = simplified.size()
            raw = simplified.as_long()
            if isinstance(value, LInt) and raw >= (1 << (width - 1)):
                raw = raw - (1 << width)
            return raw
    raise ReadRefused("a constant integer was needed and %r is symbolic"
                      % (value,))


def int_to_bv(value, width):
    term = int_of(value)
    if width <= INT_WIDTH:
        return z3.Extract(width - 1, 0, term)
    return z3.SignExt(width - INT_WIDTH, term)


def bv_to_int_signed(bits):
    bits = bv_of(bits)
    if bits.size() >= INT_WIDTH:
        return lint(z3.Extract(INT_WIDTH - 1, 0, bits))
    return lint(z3.SignExt(INT_WIDTH - bits.size(), bits))


def bv_to_int_unsigned(bits):
    bits = bv_of(bits)
    if bits.size() >= INT_WIDTH:
        return lint(z3.Extract(INT_WIDTH - 1, 0, bits))
    return lint(z3.ZeroExt(INT_WIDTH - bits.size(), bits))


def same_width(left, right):
    left = bv_of(left)
    right = bv_of(right)
    if left.size() == right.size():
        return left, right
    raise ReadRefused("bit-vectors of widths %d and %d combined"
                      % (left.size(), right.size()))


def power_of_two(exponent):
    """2 ^ e at INT_WIDTH, e an LInt (symbolic shifts allowed)."""
    one = z3.BitVecVal(1, INT_WIDTH)
    return lint(one << int_of(exponent))


def int_pow(base, exponent):
    base_c = None
    try:
        base_c = concrete_int(base)
    except ReadRefused:
        base_c = None
    if base_c == 2:
        return power_of_two(exponent)
    exp_c = concrete_int(exponent)
    result = z3.BitVecVal(1, INT_WIDTH)
    for _ in range(exp_c):
        result = result * int_of(base)
    return lint(result)


def shift_amount_bits(amount, width):
    """a shift amount (LInt or bit-vector) brought to `width` bits."""
    if isinstance(amount, LInt) or (z3.is_bv(amount) and
                                    amount.size() == INT_WIDTH and
                                    width != INT_WIDTH):
        term = int_of(amount)
        if width <= INT_WIDTH:
            return z3.Extract(width - 1, 0, term)
        return z3.ZeroExt(width - INT_WIDTH, term)
    amount = bv_of(amount)
    if amount.size() == width:
        return amount
    if amount.size() < width:
        return z3.ZeroExt(width - amount.size(), amount)
    return z3.Extract(width - 1, 0, amount)


# ==================================================================
# section 4: the primitive table -- Lean's own library, by name
# ==================================================================

def prim_bv_add(a, b):
    a, b = same_width(a, b)
    return a + b


def prim_bv_sub(a, b):
    a, b = same_width(a, b)
    return a - b


def prim_bv_mul(a, b):
    a, b = same_width(a, b)
    return a * b


def prim_bv_and(a, b):
    a, b = same_width(a, b)
    return a & b


def prim_bv_or(a, b):
    a, b = same_width(a, b)
    return a | b


def prim_bv_xor(a, b):
    a, b = same_width(a, b)
    return a ^ b


def prim_bv_not(a):
    if isinstance(a, EmptyBits):
        return a
    return ~bv_of(a)


def prim_bv_shl(a, n):
    a = bv_of(a)
    return a << shift_amount_bits(n, a.size())


def prim_bv_lshr(a, n):
    a = bv_of(a)
    return z3.LShR(a, shift_amount_bits(n, a.size()))


def prim_bv_ashr(a, n):
    a = bv_of(a)
    return a >> shift_amount_bits(n, a.size())


def prim_bv_append(a, b):
    if isinstance(a, EmptyBits):
        return b
    if isinstance(b, EmptyBits):
        return a
    return z3.Concat(bv_of(a), bv_of(b))


def prim_extract(v, hi, lo):
    hi = concrete_int(hi)
    lo = concrete_int(lo)
    if hi < lo:
        return EmptyBits()
    return z3.Extract(hi, lo, bv_of(v))


def prim_sign_extend(v, n):
    n = concrete_int(n)
    if isinstance(v, EmptyBits):
        return z3.BitVecVal(0, n) if n > 0 else v
    v = bv_of(v)
    if n == v.size():
        return v
    if n < v.size():
        return z3.Extract(n - 1, 0, v)
    return z3.SignExt(n - v.size(), v)


def prim_zero_extend(v, n):
    n = concrete_int(n)
    if isinstance(v, EmptyBits):
        return z3.BitVecVal(0, n) if n > 0 else v
    v = bv_of(v)
    if n == v.size():
        return v
    if n < v.size():
        return z3.Extract(n - 1, 0, v)
    return z3.ZeroExt(n - v.size(), v)


def prim_truncate(v, n):
    v = bv_of(v)
    n = concrete_int(n)
    if n == v.size():
        return v
    return z3.Extract(n - 1, 0, v)


def prim_to_int(v):
    return bv_to_int_signed(v)


def prim_to_nat(v):
    return bv_to_int_unsigned(v)


def prim_of_int(n, i):
    return int_to_bv(i, concrete_int(n))


def prim_of_nat(n, i):
    return int_to_bv(i, concrete_int(n))


def prim_int_add(a, b):
    return lint(int_of(a) + int_of(b))


def prim_int_sub(a, b):
    return lint(int_of(a) - int_of(b))


def prim_int_mul(a, b):
    return lint(int_of(a) * int_of(b))


def prim_int_tdiv(a, b):
    """truncating division: z3's signed division rounds toward zero."""
    return lint(int_of(a) / int_of(b))


def prim_int_tmod(a, b):
    return lint(z3.SRem(int_of(a), int_of(b)))


def prim_int_ediv(a, b):
    """Euclidean division: the remainder is never negative."""
    a = int_of(a)
    b = int_of(b)
    q = a / b
    r = z3.SRem(a, b)
    zero = z3.BitVecVal(0, INT_WIDTH)
    one = z3.BitVecVal(1, INT_WIDTH)
    fixed = z3.If(r < zero, z3.If(b > zero, q - one, q + one), q)
    return lint(fixed)


def prim_int_emod(a, b):
    a = int_of(a)
    b = int_of(b)
    r = z3.SRem(a, b)
    zero = z3.BitVecVal(0, INT_WIDTH)
    fixed = z3.If(r < zero, z3.If(b > zero, r + b, r - b), r)
    return lint(fixed)


def prim_int_neg(a):
    return lint(-int_of(a))


def prim_int_pow(a, b):
    return int_pow(a, b)


def prim_int_lt(a, b):
    return int_of(a) < int_of(b)


def prim_int_le(a, b):
    return int_of(a) <= int_of(b)


def prim_int_gt(a, b):
    return int_of(a) > int_of(b)


def prim_int_ge(a, b):
    return int_of(a) >= int_of(b)


def prim_int_max(a, b):
    a = int_of(a)
    b = int_of(b)
    return lint(z3.If(a >= b, a, b))


def prim_int_min(a, b):
    a = int_of(a)
    b = int_of(b)
    return lint(z3.If(a <= b, a, b))


def prim_int_abs(a):
    a = int_of(a)
    return lint(z3.If(a < 0, -a, a))


def prim_int_shl(a, b):
    return lint(int_of(a) << int_of(b))


def prim_int_shr(a, b):
    return lint(int_of(a) >> int_of(b))


def prim_bool_not(a):
    return z3.Not(bool_of(a))


def prim_bool_and(a, b):
    return z3.And(bool_of(a), bool_of(b))


def prim_bool_or(a, b):
    return z3.Or(bool_of(a), bool_of(b))


def prim_bool_to_bv(a):
    return z3.If(bool_of(a), z3.BitVecVal(1, 1), z3.BitVecVal(0, 1))


def prim_get_slice_int(n, i, lo):
    """the n bits of integer i starting at bit lo."""
    term = int_of(i) >> int_of(lo)
    return int_to_bv(lint(term), concrete_int(n))


def prim_bv_ult(a, b):
    a, b = same_width(a, b)
    return z3.ULT(a, b)


def prim_bv_ule(a, b):
    a, b = same_width(a, b)
    return z3.ULE(a, b)


def prim_bv_slt(a, b):
    a, b = same_width(a, b)
    return a < b


def prim_bv_sle(a, b):
    a, b = same_width(a, b)
    return a <= b


def prim_bv_msb(a):
    a = bv_of(a)
    return z3.Extract(a.size() - 1, a.size() - 1, a) == z3.BitVecVal(1, 1)


def prim_bv_getlsb(a, i):
    a = bv_of(a)
    i = concrete_int(i)
    return z3.Extract(i, i, a) == z3.BitVecVal(1, 1)


def prim_bv_size(a):
    if isinstance(a, EmptyBits):
        return lint(0)
    return lint(bv_of(a).size())


def prim_identity(a):
    return a


PRIMITIVES = {
    # bit-vector arithmetic and logic (Lean's BitVec, as Sail's Lean
    # backend names them)
    "HAdd.hAdd": None, "HSub.hSub": None, "HMul.hMul": None,
    "BitVec.add": prim_bv_add, "BitVec.sub": prim_bv_sub,
    "BitVec.mul": prim_bv_mul,
    "BitVec.and": prim_bv_and, "BitVec.or": prim_bv_or,
    "BitVec.xor": prim_bv_xor, "BitVec.not": prim_bv_not,
    "Complement.complement": prim_bv_not,
    "BitVec.shiftLeft": prim_bv_shl, "BitVec.ushiftRight": prim_bv_lshr,
    "BitVec.sshiftRight": prim_bv_ashr, "BitVec.append": prim_bv_append,
    "HAppend.hAppend": prim_bv_append,
    "BitVec.toInt": prim_to_int, "BitVec.toNat": prim_to_nat,
    "BitVec.toNatInt": prim_to_nat, "BitVec.toFin": prim_to_nat,
    "BitVec.ofInt": prim_of_int, "BitVec.ofNat": prim_of_nat,
    "BitVec.ofNatLT": prim_of_nat,
    "BitVec.msb": prim_bv_msb, "BitVec.getLsb": prim_bv_getlsb,
    "BitVec.getLsbD": prim_bv_getlsb, "BitVec.getLsb'": prim_bv_getlsb,
    "BitVec.ult": prim_bv_ult, "BitVec.ule": prim_bv_ule,
    "BitVec.slt": prim_bv_slt, "BitVec.sle": prim_bv_sle,
    "BitVec.signExtend": prim_sign_extend,
    "BitVec.zeroExtend": prim_zero_extend,
    "BitVec.setWidth": prim_zero_extend,
    "BitVec.truncate": prim_truncate,
    # the Sail Lean support library
    "Sail.BitVec.extractLsb": prim_extract,
    "Sail.BitVec.signExtend": prim_sign_extend,
    "Sail.BitVec.zeroExtend": prim_zero_extend,
    "Sail.BitVec.truncate": prim_truncate,
    "Sail.BitVec.truncateLsb": None,
    "Sail.BitVec.append": prim_bv_append,
    "Sail.BitVec.toNat": prim_to_nat, "Sail.BitVec.toInt": prim_to_int,
    "Sail.BitVec.length": prim_bv_size, "BitVec.length": prim_bv_size,
    "Sail.BitVec.msb": prim_bv_msb,
    "Sail.BitVec.getLsb": prim_bv_getlsb,
    # integers
    "Int.add": prim_int_add, "Int.sub": prim_int_sub,
    "Int.mul": prim_int_mul, "Int.tdiv": prim_int_tdiv,
    "Int.tmod": prim_int_tmod, "Int.ediv": prim_int_ediv,
    "Int.emod": prim_int_emod, "Int.div": prim_int_ediv,
    "Int.mod": prim_int_emod, "Int.fdiv": None, "Int.fmod": None,
    "Int.neg": prim_int_neg, "Neg.neg": prim_int_neg,
    "Int.pow": prim_int_pow, "HPow.hPow": prim_int_pow,
    "Int.natAbs": prim_int_abs, "Int.toNat": prim_identity,
    "Int.ofNat": prim_identity, "Nat.cast": prim_identity,
    "Int.cast": prim_identity, "IntCast.intCast": prim_identity,
    "NatCast.natCast": prim_identity, "Int.toInt": prim_identity,
    "Nat.toInt": prim_identity, "Nat.add": prim_int_add,
    "Nat.sub": prim_int_sub, "Nat.mul": prim_int_mul,
    "Nat.div": prim_int_tdiv, "Nat.mod": prim_int_tmod,
    "Nat.pow": prim_int_pow, "Nat.pred": None, "Nat.succ": None,
    "Int.shiftLeft": prim_int_shl, "Int.shiftRight": prim_int_shr,
    "Nat.shiftLeft": prim_int_shl, "Nat.shiftRight": prim_int_shr,
    "max": prim_int_max, "min": prim_int_min, "Max.max": prim_int_max,
    "Min.min": prim_int_min, "Int.max": prim_int_max,
    "Int.min": prim_int_min,
    "Int.lt": prim_int_lt, "Int.le": prim_int_le,
    "Int.decLt": prim_int_lt, "Int.decLe": prim_int_le,
    "Nat.lt": prim_int_lt, "Nat.le": prim_int_le,
    # booleans
    "not": prim_bool_not, "Bool.not": prim_bool_not, "!": prim_bool_not,
    "Bool.and": prim_bool_and, "Bool.or": prim_bool_or,
    "and": prim_bool_and, "or": prim_bool_or,
    "Bool.toNat": prim_bool_to_bv, "decide": prim_identity,
    "Decidable.decide": prim_identity,
    # the Sail library's integer slicing
    "get_slice_int": prim_get_slice_int,
    "Sail.get_slice_int": prim_get_slice_int,
    "id": prim_identity, "pure": prim_identity, "Pure.pure": prim_identity,
    "cast": None,
    "bne": None, "beq": None, "BitVec.zero": None,
    "Sail.BitVec.updateSubrange": None, "BitVec.extractLsb": prim_extract,
    "HAppend.hAppend": None, "String.append": None,
}


def prim_bne(a, b):
    return z3.Not(values_equal(a, b))


def prim_beq(a, b):
    return values_equal(a, b)


def prim_bv_zero(n):
    n = concrete_int(n)
    if n == 0:
        return EmptyBits()
    return z3.BitVecVal(0, n)


def prim_bv_all_ones(n):
    n = concrete_int(n)
    if n == 0:
        return EmptyBits()
    return z3.BitVecVal((1 << n) - 1, n)


PRIMITIVES["BitVec.allOnes"] = prim_bv_all_ones
PRIMITIVES["sail_ones"] = prim_bv_all_ones
PRIMITIVES["sail_zeros"] = prim_bv_zero


def prim_update_subrange(v, hi, lo, x):
    v = bv_of(v)
    x = bv_of(x)
    hi = concrete_int(hi)
    lo = concrete_int(lo)
    parts = []
    if hi < v.size() - 1:
        parts.append(z3.Extract(v.size() - 1, hi + 1, v))
    parts.append(x)
    if lo > 0:
        parts.append(z3.Extract(lo - 1, 0, v))
    if len(parts) == 1:
        return parts[0]
    return z3.Concat(*parts)


def prim_happend(a, b):
    if isinstance(a, str) and isinstance(b, str):
        return a + b
    return prim_bv_append(a, b)


def prim_bv_update(v, i, bit):
    v = bv_of(v)
    i = concrete_int(i)
    return prim_update_subrange(v, i, i, bv_of(bit))


def prim_shift_bits_left(v, n):
    return prim_bv_shl(v, n)


def prim_shift_bits_right(v, n):
    return prim_bv_lshr(v, n)


PRIMITIVES["shift_bits_left"] = prim_shift_bits_left
PRIMITIVES["shift_bits_right"] = prim_shift_bits_right
PRIMITIVES["shiftl"] = prim_int_shl
PRIMITIVES["shiftr"] = prim_int_shr
PRIMITIVES["sail_shiftleft"] = prim_bv_shl
PRIMITIVES["sail_shiftright"] = prim_bv_lshr
PRIMITIVES["sail_arith_shiftright"] = prim_bv_ashr
PRIMITIVES["BitVec.update"] = prim_bv_update
FLOAT_SORTS = {16: z3.Float16(), 32: z3.Float32(), 64: z3.Float64()}
SOFTFLOAT_ARITH = re.compile(r"^riscv_f(16|32|64)(Add|Sub|Mul|Div|Sqrt|MulAdd)$")
SOFTFLOAT_COMPARE = re.compile(r"^riscv_f(16|32|64)(Lt|Le|Eq)(_quiet)?$")
SOFTFLOAT_FROM_INT = re.compile(r"^riscv_(i|ui)(32|64)ToF(16|32|64)$")
SOFTFLOAT_TO_INT = re.compile(r"^riscv_f(16|32|64)To(I|Ui)(32|64)$")
SOFTFLOAT_TO_FLOAT = re.compile(r"^riscv_f(16|32|64)ToF(16|32|64)$")
ROUNDING_BY_NAME = {"RM_RNE": z3.RNE(), "RM_RTZ": z3.RTZ(), "RM_RDN": z3.RTN(),
                    "RM_RUP": z3.RTP(), "RM_RMM": z3.RNA()}
"""the five rounding modes of the ISA by the model's own constructor names
(`encdec_rounding_mode_backwards` turns the 3-bit field into these)."""
FLAG_COUNTER = [0]


class SoftfloatEnvironment(object):
    """what the softfloat externs need from the reader: the model's own
    reading of a 3-bit rounding field."""

    def __init__(self, reader):
        self.reader = reader

    def rounding(self, bits):
        bits = z3.simplify(bv_of(bits))
        if not z3.is_bv_value(bits):
            raise ReadRefused("a symbolic rounding mode reached softfloat")
        if "encdec_rounding_mode_backwards" not in self.reader.definitions:
            raise ReadRefused("the emit has no encdec_rounding_mode_backwards")
        mode = self.reader.call("encdec_rounding_mode_backwards", [bits],
                                Machine({}))
        name = mode.name if isinstance(mode, Ctor) else "%r" % (mode,)
        if name not in ROUNDING_BY_NAME:
            raise ReadRefused("rounding mode %s has no z3 meaning" % name)
        return ROUNDING_BY_NAME[name]


SOFTFLOAT_ENV = [None]


def fresh_flags():
    FLAG_COUNTER[0] = FLAG_COUNTER[0] + 1
    return z3.BitVec("softfloat_flags_%d" % FLAG_COUNTER[0], 5)


def to_float(bits, width):
    return z3.fpBVToFP(bv_of(bits), FLOAT_SORTS[width])


def softfloat(name):
    """the z3 meaning of one softfloat extern, or None."""
    hit = SOFTFLOAT_ARITH.match(name)
    if hit is not None:
        width = int(hit.group(1))
        kind = hit.group(2)

        def arith(rm, *args):
            mode = SOFTFLOAT_ENV[0].rounding(rm)
            values = [to_float(a, width) for a in args]
            if kind == "Add":
                result = z3.fpAdd(mode, values[0], values[1])
            elif kind == "Sub":
                result = z3.fpSub(mode, values[0], values[1])
            elif kind == "Mul":
                result = z3.fpMul(mode, values[0], values[1])
            elif kind == "Div":
                result = z3.fpDiv(mode, values[0], values[1])
            elif kind == "Sqrt":
                result = z3.fpSqrt(mode, values[0])
            else:
                result = z3.fpFMA(mode, values[0], values[1], values[2])
            return (fresh_flags(), z3.fpToIEEEBV(result))
        return arith
    hit = SOFTFLOAT_COMPARE.match(name)
    if hit is not None:
        width = int(hit.group(1))
        kind = hit.group(2)

        def compare(a, b):
            left = to_float(a, width)
            right = to_float(b, width)
            if kind == "Lt":
                result = z3.fpLT(left, right)
            elif kind == "Le":
                result = z3.fpLEQ(left, right)
            else:
                result = z3.fpEQ(left, right)
            return (fresh_flags(), result)
        return compare
    hit = SOFTFLOAT_FROM_INT.match(name)
    if hit is not None:
        signed = hit.group(1) == "i"
        width = int(hit.group(3))

        def from_int(rm, x):
            mode = SOFTFLOAT_ENV[0].rounding(rm)
            if signed:
                result = z3.fpSignedToFP(mode, bv_of(x), FLOAT_SORTS[width])
            else:
                result = z3.fpUnsignedToFP(mode, bv_of(x), FLOAT_SORTS[width])
            return (fresh_flags(), z3.fpToIEEEBV(result))
        return from_int
    hit = SOFTFLOAT_TO_INT.match(name)
    if hit is not None:
        width = int(hit.group(1))
        signed = hit.group(2) == "I"
        bits = int(hit.group(3))

        def to_int(rm, x):
            mode = SOFTFLOAT_ENV[0].rounding(rm)
            value = to_float(x, width)
            if signed:
                result = z3.fpToSBV(mode, value, z3.BitVecSort(bits))
            else:
                result = z3.fpToUBV(mode, value, z3.BitVecSort(bits))
            return (fresh_flags(), result)
        return to_int
    hit = re.match(r"^riscv_f(16|32|64)roundToInt$", name)
    if hit is not None:
        width = int(hit.group(1))

        def round_to_int(rm, x, _exact):
            mode = SOFTFLOAT_ENV[0].rounding(rm)
            result = z3.fpRoundToIntegral(mode, to_float(x, width))
            return (fresh_flags(), z3.fpToIEEEBV(result))
        return round_to_int
    hit = SOFTFLOAT_TO_FLOAT.match(name)
    if hit is not None:
        source = int(hit.group(1))
        target = int(hit.group(2))

        def widen(rm, x):
            mode = SOFTFLOAT_ENV[0].rounding(rm)
            result = z3.fpFPToFP(mode, to_float(x, source), FLOAT_SORTS[target])
            return (fresh_flags(), z3.fpToIEEEBV(result))
        return widen
    return None


PRIMITIVES["bne"] = prim_bne
PRIMITIVES["beq"] = prim_beq
PRIMITIVES["BitVec.zero"] = prim_bv_zero
PRIMITIVES["Sail.BitVec.updateSubrange"] = prim_update_subrange
PRIMITIVES["HAppend.hAppend"] = prim_happend
PRIMITIVES["String.append"] = prim_happend

INFIX = {
    "+": ("add",), "-": ("sub",), "*": ("mul",),
    "+i": ("iadd",), "-i": ("isub",), "*i": ("imul",),
    "/i": ("itdiv",), "%i": ("itmod",), "^i": ("ipow",), "^": ("ipow",),
    "/": ("itdiv",), "%": ("itmod",),
    "&&&": ("bvand",), "|||": ("bvor",), "^^^": ("bvxor",),
    "<<<": ("shl",), ">>>": ("lshr",), "++": ("append",),
    "==": ("eq",), "!=": ("ne",), "≠": ("ne",), "=": ("eq",), "+++": ("append",),
    "<": ("lt",), ">": ("gt",), "<=": ("le",), ">=": ("ge",),
    "≤": ("le",), "≥": ("ge",),
    "<b": ("lt",), ">b": ("gt",), "≤b": ("le",), "≥b": ("ge",),
    "&&": ("and",), "||": ("or",),
}


def values_equal(left, right):
    if isinstance(left, Ctor) and isinstance(right, Ctor):
        if left.name != right.name:
            return z3.BoolVal(False)
        parts = [values_equal(a, b) for a, b in zip(left.args, right.args)]
        if not parts:
            return z3.BoolVal(True)
        return z3.And(*parts)
    if isinstance(left, Ctor) or isinstance(right, Ctor):
        return z3.BoolVal(False)
    if isinstance(left, LInt) or isinstance(right, LInt):
        return int_of(left) == int_of(right)
    if isinstance(left, bool) or z3.is_bool(left):
        return bool_of(left) == bool_of(right)
    if isinstance(left, str) or isinstance(right, str):
        return z3.BoolVal(left == right)
    if isinstance(left, tuple) and isinstance(right, tuple):
        parts = [values_equal(a, b) for a, b in zip(left, right)]
        return z3.And(*parts) if parts else z3.BoolVal(True)
    if left is None and right is None:
        return z3.BoolVal(True)
    left, right = same_width(left, right)
    return left == right


def apply_infix(op, left, right):
    kind = INFIX[op][0]
    if kind == "add":
        if isinstance(left, LInt) or isinstance(right, LInt):
            return prim_int_add(left, right)
        return prim_bv_add(left, right)
    if kind == "sub":
        if isinstance(left, LInt) or isinstance(right, LInt):
            return prim_int_sub(left, right)
        return prim_bv_sub(left, right)
    if kind == "mul":
        if isinstance(left, LInt) or isinstance(right, LInt):
            return prim_int_mul(left, right)
        return prim_bv_mul(left, right)
    if kind == "iadd":
        return prim_int_add(left, right)
    if kind == "isub":
        return prim_int_sub(left, right)
    if kind == "imul":
        return prim_int_mul(left, right)
    if kind == "itdiv":
        return prim_int_tdiv(left, right)
    if kind == "itmod":
        return prim_int_tmod(left, right)
    if kind == "ipow":
        return prim_int_pow(left, right)
    if kind == "bvand":
        return prim_bv_and(left, right)
    if kind == "bvor":
        return prim_bv_or(left, right)
    if kind == "bvxor":
        return prim_bv_xor(left, right)
    if kind == "shl":
        if isinstance(left, LInt):
            return prim_int_shl(left, right)
        return prim_bv_shl(left, right)
    if kind == "lshr":
        if isinstance(left, LInt):
            return prim_int_shr(left, right)
        return prim_bv_lshr(left, right)
    if kind == "append":
        return prim_bv_append(left, right)
    if kind == "eq":
        return values_equal(left, right)
    if kind == "ne":
        return z3.Not(values_equal(left, right))
    if kind in ("lt", "le", "gt", "ge"):
        if isinstance(left, LInt) or isinstance(right, LInt):
            table = {"lt": prim_int_lt, "le": prim_int_le,
                     "gt": prim_int_gt, "ge": prim_int_ge}
            return table[kind](left, right)
        left, right = same_width(left, right)
        table = {"lt": z3.ULT, "le": z3.ULE, "gt": z3.UGT, "ge": z3.UGE}
        return table[kind](left, right)
    if kind == "and":
        return prim_bool_and(left, right)
    if kind == "or":
        return prim_bool_or(left, right)
    raise ReadRefused("infix %r is not known" % op)


# ==================================================================
# section 5: the evaluator
# ==================================================================

class Reader(object):
    """evaluates parsed definitions against a Machine."""

    def __init__(self, definitions, widths=None):
        self.definitions = definitions
        self.widths = widths or {}
        self.depth = 0
        self.trace = []
        self.stack = []

    # -- entry points --------------------------------------------------

    def call(self, name, args, machine):
        """apply the emitted definition `name` to values."""
        if name not in self.definitions:
            raise ReadRefused("no definition named %s in the emit" % name)
        params, body = self.definitions[name]
        env = {}
        positional = [p for p in params]
        if len(args) > len(positional):
            raise ReadRefused("%s takes %d arguments, %d given"
                              % (name, len(positional), len(args)))
        for (param, _kind), value in zip(positional, args):
            env[param] = value
        if len(args) < len(positional):
            rest = positional[len(args):]
            return Closure([p for p, _k in rest], body, env)
        self.depth = self.depth + 1
        self.stack.append(name)
        if self.depth > MAX_DEPTH:
            trail = " > ".join(self.stack[-24:])
            self.stack = []
            self.depth = 0
            raise ReadRefused("the reader went %d calls deep at %s; the "
                              "last calls: %s" % (MAX_DEPTH, name, trail))
        try:
            return self.eval(body, env, machine)
        except EarlyReturn as early:
            return early.value
        except ReadRefused as problem:
            raise self.trailed(problem)
        finally:
            self.depth = self.depth - 1
            if self.stack:
                self.stack.pop()

    def trailed(self, problem):
        if getattr(problem, "trailed", False):
            return problem
        message = "%s [in %s]" % (problem, " > ".join(self.stack[-10:]))
        out = ReadRefused(message)
        out.trailed = True
        return out

    # -- the walk --------------------------------------------------------

    def eval(self, node, env, machine):
        kind = node[0]
        if kind == "var":
            return self.variable(node[1], env, machine)
        if kind == "num":
            return lint(parse_number(node[1]))
        if kind == "bv":
            width = int(node[2])
            return z3.BitVecVal(parse_number(node[1]), width)
        if kind == "str":
            return node[1]
        if kind == "unit":
            return None
        if kind == "tuple":
            return tuple(self.eval(item, env, machine) for item in node[1])
        if kind == "list":
            return [self.eval(item, env, machine) for item in node[1]]
        if kind == "ascribe":
            return self.ascribed(node, env, machine)
        if kind == "named":
            return ("named", node[1], self.eval(node[2], env, machine))
        if kind == "bindexpr":
            return self.eval(node[1], env, machine)
        if kind == "binop":
            left = self.eval(node[2], env, machine)
            right = self.eval(node[3], env, machine)
            return apply_infix(node[1], left, right)
        if kind == "if":
            return self.conditional(node, env, machine)
        if kind == "let" or kind == "bind":
            value = self.eval(node[2], env, machine)
            inner = dict(env)
            self.bind_pattern(node[1], value, inner)
            return self.eval(node[3], inner, machine)
        if kind == "seq":
            self.eval(node[1], env, machine)
            return self.eval(node[2], env, machine)
        if kind == "mut":
            value = self.eval(node[2], env, machine)
            inner = dict(env)
            name = node[1]
            if isinstance(name, tuple):
                name = name[1]
            inner[name] = Cell(value)
            return self.eval(node[3], inner, machine)
        if kind == "assign":
            value = self.eval(node[2], env, machine)
            if node[1] not in env or not isinstance(env[node[1]], Cell):
                raise ReadRefused("assignment to %s, which is not a "
                                  "mutable variable here" % node[1])
            env[node[1]].value = value
            return self.eval(node[3], env, machine)
        if kind == "for":
            return self.loop(node, env, machine)
        if kind == "match":
            return self.match(node, env, machine)
        if kind == "fun":
            return Closure(node[1], node[2], env)
        if kind == "app":
            return self.application(node, env, machine)
        if kind == "struct":
            out = {}
            for name, item in node[1]:
                out[name] = self.eval(item, env, machine)
            return out
        if kind == "proj":
            value = self.eval(node[1], env, machine)
            field = node[2]
            if isinstance(value, dict):
                if field in value:
                    return value[field]
                raise ReadRefused("no field %s in %r" % (field, sorted(value)))
            if isinstance(value, tuple) and field.isdigit():
                return value[int(field) - 1]
            if isinstance(value, Ctor) and field.isdigit():
                return value.args[int(field) - 1]
            raise ReadRefused("projection .%s of %r" % (field, value))
        raise ReadRefused("the reader has no case for a %s node" % kind)

    def loop(self, node, env, machine):
        """a foreach with concrete bounds, unrolled; anything else refused."""
        _kind, variable, lower, upper, step, block, body = node
        low = concrete_int(self.eval(lower, env, machine))
        high = concrete_int(self.eval(upper, env, machine))
        by = concrete_int(self.eval(step, env, machine))
        if by == 0:
            raise ReadRefused("a loop with step 0")
        count = 0
        index = low
        while (by > 0 and index <= high) or (by < 0 and index >= high):
            inner = dict(env)
            inner[variable] = lint(index)
            self.eval(block, inner, machine)
            index = index + by
            count = count + 1
            if count > 100000:
                raise ReadRefused("a loop of more than 100000 iterations")
        return self.eval(body, env, machine)

    def call_tolerant(self, name, args, machine, skipped):
        """the definition's statements one by one; a statement the reader
        refuses is skipped and recorded in `skipped`, the rest still run."""
        params, body = self.definitions[name]
        env = {}
        for (param, _kind), value in zip(params, args):
            env[param] = value
        node = body
        while True:
            kind = node[0]
            try:
                if kind == "seq":
                    self.eval(node[1], env, machine)
                    node = node[2]
                    continue
                if kind in ("let", "bind"):
                    value = self.eval(node[2], env, machine)
                    env = dict(env)
                    self.bind_pattern(node[1], value, env)
                    node = node[3]
                    continue
                if kind == "mut":
                    value = self.eval(node[2], env, machine)
                    env = dict(env)
                    env[node[1] if not isinstance(node[1], tuple) else node[1][1]] = Cell(value)
                    node = node[3]
                    continue
                return self.eval(node, env, machine)
            except ReadRefused as problem:
                skipped.append("%s" % problem)
                if kind == "seq":
                    node = node[2]
                    continue
                if kind in ("let", "bind", "mut"):
                    node = node[3]
                    continue
                return None

    def ascribed(self, node, env, machine):
        value = self.eval(node[1], env, machine)
        typetext = node[2].replace(" ", "")
        hit = re.match(r"^\(?BitVec\(?(\d+)\)?$", typetext)
        if hit is not None and isinstance(value, LInt):
            return int_to_bv(value, int(hit.group(1)))
        if typetext in ("Int", "Nat") and z3.is_bv(value) and \
                not isinstance(value, LInt):
            if value.size() == INT_WIDTH:
                return lint(value)
        if typetext == "Bool" and z3.is_bv(value) and value.size() == 1:
            return bool_of(value)
        return value

    def variable(self, name, env, machine):
        if name in env:
            value = env[name]
            if isinstance(value, Cell):
                return value.value
            return value
        if name in ("true", "True", "Bool.true"):
            return z3.BoolVal(True)
        if name in ("false", "False", "Bool.false"):
            return z3.BoolVal(False)
        if name in ("none", "Option.none", ".none"):
            return Ctor("none", [])
        if name in ("some", "Option.some"):
            return Ctor("some", [])
        if name.startswith("."):
            return Ctor(name[1:], [])
        if name in self.definitions:
            params, body = self.definitions[name]
            if not params:
                return self.call(name, [], machine)
            return Closure([p for p, _k in params], body, {}, name)
        if name in self.widths:
            return RegisterName(name)
        if name in PRIMITIVES:
            return ("prim", name)
        meaning = softfloat(name)
        if meaning is not None:
            PRIMITIVES[name] = meaning
            SOFTFLOAT_ENV[0] = SoftfloatEnvironment(self)
            return ("prim", name)
        if name[:1].isupper() or "." in name or name in LOWERCASE_CONSTRUCTORS:
            return Ctor(name.split(".")[-1], [])
        return RegisterName(name)

    def conditional(self, node, env, machine):
        condition = bool_of(self.eval(node[1], env, machine))
        simplified = z3.simplify(condition)
        if z3.is_true(simplified):
            return self.eval(node[2], env, machine)
        if z3.is_false(simplified):
            return self.eval(node[3], env, machine)
        yes_machine = machine_copy(machine)
        yes_returned = False
        try:
            yes = self.eval(node[2], env, yes_machine)
        except EarlyReturn as early:
            yes = early.value
            yes_returned = True
        no_machine = machine_copy(machine)
        no_returned = False
        try:
            no = self.eval(node[3], env, no_machine)
        except EarlyReturn as early:
            no = early.value
            no_returned = True
        except ReadRefused as err:
            if "the definition throws:" not in str(err):
                raise
            machine.registers = yes_machine.registers
            machine.writes = yes_machine.writes
            machine.reads = yes_machine.reads
            if yes_returned:
                raise EarlyReturn(yes)
            return yes
        merge_machines(machine, condition, yes_machine, no_machine)
        if yes_returned and no_returned:
            raise EarlyReturn(merge_values(condition, yes, no))
        if yes_returned or no_returned:
            raise ReadRefused("a return on one side of a symbolic "
                              "conditional and not the other")
        return merge_values(condition, yes, no)

    def match(self, node, env, machine):
        value = self.eval(node[1], env, machine)
        arms = node[2]
        return self.match_arms(value, arms, env, machine)

    def match_arms(self, value, arms, env, machine):
        while True:
            if not arms:
                raise ReadRefused("no match arm fits %r" % (value,))
            pattern, body = arms[0]
            rest = arms[1:]
            inner = dict(env)
            condition = self.pattern_condition(pattern, value, inner)
            simplified = z3.simplify(condition)
            if z3.is_true(simplified) or not rest:
                # the last arm of an exhaustive match is taken whatever
                # its condition simplifies to
                return self.eval(body, inner, machine)
            if z3.is_false(simplified):
                arms = rest
                continue
            break
        yes_machine = machine_copy(machine)
        yes_returned = False
        try:
            yes = self.eval(body, inner, yes_machine)
        except EarlyReturn as early:
            yes = early.value
            yes_returned = True
        no_machine = machine_copy(machine)
        no_returned = False
        try:
            no = self.match_arms(value, rest, env, no_machine)
        except EarlyReturn as early:
            no = early.value
            no_returned = True
        merge_machines(machine, condition, yes_machine, no_machine)
        if yes_returned and no_returned:
            raise EarlyReturn(merge_values(condition, yes, no))
        if yes_returned or no_returned:
            raise ReadRefused("a return in one arm of a symbolic match "
                              "and not in another")
        return merge_values(condition, yes, no)

    def pattern_condition(self, pattern, value, env):
        kind = pattern[0]
        if kind == "pwild":
            return z3.BoolVal(True)
        if kind == "pvar":
            env[pattern[1]] = value
            return z3.BoolVal(True)
        if kind == "pnum":
            number = parse_number(pattern[1])
            if z3.is_bv(value) and not isinstance(value, LInt):
                return value == z3.BitVecVal(number, value.size())
            if isinstance(value, bool) or z3.is_bool(value):
                return bool_of(value) == z3.BoolVal(number != 0)
            return values_equal(value, lint(number))
        if kind == "pstr":
            return z3.BoolVal(value == pattern[1])
        if kind == "ptuple":
            if not isinstance(value, tuple):
                raise ReadRefused("a tuple pattern against %r" % (value,))
            parts = []
            for sub, item in zip(pattern[1], value):
                parts.append(self.pattern_condition(sub, item, env))
            return z3.And(*parts) if parts else z3.BoolVal(True)
        if kind == "pctor":
            name = pattern[1].split(".")[-1]
            args = pattern[2]
            if name in ("true", "false") and not args:
                wanted = z3.BoolVal(name == "true")
                return bool_of(value) == wanted
            if isinstance(value, Ctor):
                if value.name == "ite" and len(value.args) == 3:
                    return z3.If(
                        value.args[0],
                        self.pattern_condition(pattern, value.args[1], env),
                        self.pattern_condition(pattern, value.args[2], env),
                    )
                if value.name != name:
                    return z3.BoolVal(False)
                parts = []
                for sub, item in zip(args, value.args):
                    parts.append(self.pattern_condition(sub, item, env))
                return z3.And(*parts) if parts else z3.BoolVal(True)
            if name == "some" and len(args) == 1:
                env_cond = self.pattern_condition(args[0], value, env)
                return env_cond
            raise ReadRefused("constructor pattern %s against %r"
                              % (name, value))
        raise ReadRefused("pattern kind %s" % kind)

    def bind_pattern(self, pattern, value, env):
        if isinstance(pattern, tuple) and pattern and \
                pattern[0] in ("pvar", "pwild", "ptuple", "pctor",
                               "pnum", "pstr"):
            condition = self.pattern_condition(pattern, value, env)
            del condition
            return
        env[pattern] = value

    def application(self, node, env, machine):
        head_node = node[1]
        arg_nodes = node[2]
        if head_node[0] == "var":
            special = self.special_form(head_node[1], arg_nodes, env,
                                        machine)
            if special is not NOT_SPECIAL:
                return special
        head = self.eval(head_node, env, machine)
        args = []
        named = {}
        for item in arg_nodes:
            value = self.eval(item, env, machine)
            if isinstance(value, tuple) and value and \
                    isinstance(value[0], str) and value[0] == "named":
                named[value[1]] = value[2]
                continue
            args.append(value)
        return self.apply(head, args, named, machine)

    def special_form(self, name, arg_nodes, env, machine):
        if name in ("readReg", "read_reg", "readRegRef"):
            register = self.register_name(arg_nodes[0], env, machine)
            return machine.read(register)
        if name in ("writeReg", "write_reg", "writeRegRef"):
            register = self.register_name(arg_nodes[0], env, machine)
            value = self.eval(arg_nodes[1], env, machine)
            machine.write(register, value)
            return None
        if name in ("throw", "Sail.throw", "sail_throw", "panic",
                    "sail_assert_false"):
            raise ReadRefused("the definition throws: %s" % name)
        if name in ("assert", "sail_assert", "Sail.assert"):
            return None
        if name in ("pure", "Pure.pure"):
            return self.eval(arg_nodes[0], env, machine)
        if name in ("SailME.run", "SailM.run", "Id.run", "ExceptT.run",
                    "StateT.run"):
            # the monad runner: the block's value, an early throw included
            try:
                return self.eval(arg_nodes[0], env, machine)
            except EarlyReturn as early:
                return early.value
        if name == "return":
            raise EarlyReturn(self.eval(arg_nodes[0], env, machine))
        if name in ("SailME.throw", "throwError"):
            # the exception monad's throw: the definition's value is the
            # thrown one (`SailME.run do ...` at the definition boundary)
            raise EarlyReturn(self.eval(arg_nodes[0], env, machine))
        if name == "to_bits_truncate":
            return NOT_SPECIAL
        return NOT_SPECIAL

    def register_name(self, node, env, machine):
        if node[0] == "var":
            if node[1] in env:
                value = env[node[1]]
                if isinstance(value, RegisterName):
                    return value.name
                if isinstance(value, str):
                    return value
            return node[1]
        value = self.eval(node, env, machine)
        if isinstance(value, RegisterName):
            return value.name
        if isinstance(value, str):
            return value
        raise ReadRefused("a register name was expected, found %r"
                          % (value,))

    def apply(self, head, args, named, machine):
        if isinstance(head, Closure):
            env = dict(head.env)
            params = list(head.params)
            if named:
                kept = []
                for param in params:
                    if param in named:
                        env[param] = named[param]
                        continue
                    kept.append(param)
                params = kept
            if len(args) < len(params):
                for param, value in zip(params, args):
                    env[param] = value
                return Closure(params[len(args):], head.body, env, head.name)
            for param, value in zip(params, args):
                env[param] = value
            self.depth = self.depth + 1
            self.stack.append(getattr(head, "name", "(closure)"))
            if self.depth > MAX_DEPTH:
                trail = " > ".join(self.stack[-24:])
                self.stack = []
                self.depth = 0
                raise ReadRefused("the reader went %d calls deep; the last "
                                  "calls: %s" % (MAX_DEPTH, trail))
            try:
                result = self.eval(head.body, env, machine)
            except EarlyReturn as early:
                result = early.value
            except ReadRefused as problem:
                raise self.trailed(problem)
            finally:
                self.depth = self.depth - 1
                if self.stack:
                    self.stack.pop()
            extra = args[len(params):]
            if extra:
                return self.apply(result, extra, named, machine)
            return result
        if isinstance(head, tuple) and head and isinstance(head[0], str) \
                and head[0] == "prim":
            return self.primitive(head[1], args, named)
        if isinstance(head, Ctor):
            return Ctor(head.name, head.args + list(args))
        if isinstance(head, RegisterName):
            raise ReadRefused("%s is applied but is not defined in the "
                              "emit nor in the primitive table" % head.name)
        raise ReadRefused("cannot apply %r" % (head,))

    def primitive(self, name, args, named):
        function = PRIMITIVES.get(name)
        if function is None:
            raise ReadRefused("primitive %s has no z3 meaning in the table"
                              % name)
        if name in ("to_bits_truncate",):
            return function(*args)
        try:
            return function(*args)
        except TypeError as problem:
            raise ReadRefused("primitive %s applied to %d arguments: %s"
                              % (name, len(args), problem))


NOT_SPECIAL = object()


def parse_number(text):
    if text.startswith("0x"):
        return int(text, 16)
    if text.startswith("0b"):
        return int(text, 2)
    return int(text, 10)


def machine_copy(machine):
    return machine.copy()


def merge_values(condition, yes, no):
    if yes is None and no is None:
        return None
    if isinstance(yes, LInt) or isinstance(no, LInt):
        return lint(z3.If(condition, int_of(yes), int_of(no)))
    if isinstance(yes, Ctor) and isinstance(no, Ctor):
        if yes.name == no.name and not yes.args and not no.args:
            return yes
        return Ctor("ite", [condition, yes, no])
    if isinstance(yes, tuple) and isinstance(no, tuple):
        return tuple(merge_values(condition, a, b) for a, b in zip(yes, no))
    if isinstance(yes, bool) or z3.is_bool(yes):
        return z3.If(condition, bool_of(yes), bool_of(no))
    if isinstance(yes, str) and isinstance(no, str):
        if yes == no:
            return yes
        raise ReadRefused("two strings joined under a symbolic condition")
    yes, no = same_width(yes, no)
    return z3.If(condition, yes, no)


def merge_machines(machine, condition, yes_machine, no_machine):
    names = set(yes_machine.registers) | set(no_machine.registers)
    for name in names:
        yes = yes_machine.registers.get(name)
        no = no_machine.registers.get(name)
        if yes is no and yes is not None:
            machine.registers[name] = yes
            continue
        if yes is None or no is None:
            width = None
            present = yes if yes is not None else no
            if z3.is_bv(present):
                width = present.size()
            seeded = machine.read(name, width)
            if yes is None:
                yes = seeded
            if no is None:
                no = seeded
        machine.registers[name] = merge_values(condition, yes, no)
    machine.writes = list(yes_machine.writes) + \
        [w for w in no_machine.writes if w not in yes_machine.writes]
    machine.reads = list(yes_machine.reads) + \
        [r for r in no_machine.reads if r not in yes_machine.reads]
