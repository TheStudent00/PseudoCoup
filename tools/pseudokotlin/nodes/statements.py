"""
statements.py — control flow. Statement-shaped nodes return a (multi-line) Python
string.

Kotlin's `if`/`when` are expressions; Python's are statements. We resolve this by
SHAPE + VALUE-DISTRIBUTION: a block-form `if`/`when` renders to an if/elif/else
statement, and when it sits in value position (`return when …`, `val x = if …`),
the consumer passes a `lead` ("return " / "x = ") that is distributed onto each
branch's value. Simple expression branches stay ternaries.
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from dispatch import kind  # noqa: E402
from util import block as _block  # noqa: E402


class Statements:
    # ---- if / when (shape + value-distribution) -------------------------- #
    @kind("if_expression")
    def v_if(self, node):
        # value position. simple branches -> a ternary. a statement-shaped branch can't be a ternary
        # arm, so hoist `if c: _t = …; else: _t = …` above and use the temp. (Statement-position ifs
        # are rendered straight by stmt_lines, so they never reach here.)
        if self._if_is_block(node):
            self._lam += 1
            tmp = f"_if{self._lam}"
            self._hoist.append(self._if(node, f"{tmp} = "))
            return tmp
        return self._if(node, "")

    def _if(self, node, lead):
        kids = self.named(node)
        pc = next((c for c in node.children if c.type == "parenthesized_expression"), None)
        if pc is not None:
            inner = self.named(pc)
            cond = self.visit(inner[0]) if inner else "True"
            branches = [k for k in kids if k is not pc]
        else:
            cond = self.visit(kids[0]) if kids else "True"
            branches = kids[1:]
        then_n = branches[0] if branches else None
        else_n = branches[1] if len(branches) > 1 else None

        if self._renders_stmt(then_n) or self._renders_stmt(else_n):
            out = [f"if {cond}:", self._branch(then_n, lead)]
            if else_n is not None and else_n.type == "if_expression":
                out.append("el" + self._if(else_n, lead))      # elif chain
            elif else_n is not None:
                out += ["else:", self._branch(else_n, lead)]
            return "\n".join(out)
        then_e = self.visit(then_n) if then_n is not None else "None"
        else_e = self.visit(else_n) if else_n is not None else "None"
        tern = f"({then_e} if {cond} else {else_e})"
        return f"{lead}{tern}" if lead else tern

    def _if_is_block(self, node):
        kids = self.named(node)
        pc = next((c for c in node.children if c.type == "parenthesized_expression"), None)
        branches = [k for k in kids if k is not pc] if pc else kids[1:]
        return any(self._renders_stmt(b) for b in branches)

    @kind("when_expression")
    def v_when(self, node):
        # value position: a `when` always lowers to an if/elif chain (a statement), so it can't be an
        # inline expression -- hoist `if …: _t = …` above and use the temp. (Statement-position whens
        # are rendered straight by stmt_lines.)
        self._lam += 1
        tmp = f"_when{self._lam}"
        self._hoist.append(self._when(node, f"{tmp} = "))
        return tmp

    def _when(self, node, lead):
        subj_node = next((c for c in node.named_children if c.type == "when_subject"), None)
        subj = None
        if subj_node is not None:
            inner = self.named(subj_node)
            subj = self.visit(inner[-1]) if inner else None
        out, first = [], True
        for e in [c for c in node.named_children if c.type == "when_entry"]:
            named = self.named(e)
            body = named[-1]
            is_else = any(c.type == "else" for c in e.children) or len(named) == 1
            if is_else:
                out += ["else:", self._branch(body, lead)]
            else:
                conds = named[:-1]
                cs = [self._when_cond(c, subj) for c in conds]
                out += [f"{'if' if first else 'elif'} {' or '.join(cs)}:",
                        self._branch(body, lead)]
                first = False
        return "\n".join(out)

    def _when_cond(self, c, subj):
        # a `when (subj)` branch condition. `is Type`/`!is Type` -> isinstance(subj, Type); a plain
        # value `v` -> `subj == v` (or just `v` for a subject-less boolean `when`).
        if c.type == "type_test":
            neg = any(k.type == "!is" for k in c.children)
            tn = next((k for k in c.named_children if k.type == "user_type"), None)
            chk = f"isinstance({subj}, {self._py_type_name(tn)})"
            return f"not {chk}" if neg else chk
        return f"{subj} == {self.visit(c)}" if subj else self.visit(c)

    def _distribute(self, node, lead):
        """Render `node` in value position with `lead` ('return ' / 'x = ') pushed
        onto its value. A block-form when/if becomes a statement with `lead` on each
        branch (Kotlin expression -> Python statement); a statement-shaped node
        (return/throw/++) carries its own flow and takes no lead; anything else is
        `lead+expr`. The plain case leaves hoists in self._hoist for the caller."""
        if node.type == "when_expression":
            return self._when(node, lead)
        if node.type == "try_expression":
            return self._try(node, lead)
        if node.type == "if_expression" and self._if_is_block(node):
            return self._if(node, lead)
        if self._stmt_shaped(node):
            inc = self._maybe_increment(node)   # `if (c) n++` branch -> clean `n += 1`
            return inc if inc is not None else self.visit(node)
        return f"{lead}{self.visit(node)}"

    def _stmt_shaped(self, node):
        """True for nodes rendering to a Python STATEMENT, not a value-expression:
        return/throw/assignment/loops (is_value False), and ++/-- (an augmented-assign
        statement though typed as a unary). Such a node never takes a value-lead and
        cannot be a lambda body or ternary branch."""
        if not self.is_value(node):
            return True
        if node.type == "identifier" and self.text(node) in ("continue", "break"):
            return True                  # loop jumps parse as identifiers in this grammar
        return (node.type == "unary_expression"
                and any(c.type in ("++", "--") for c in node.children))

    def _renders_stmt(self, n):
        """True when `n` compiles to a Python STATEMENT rather than a value-expression:
        a block, a when/try (always statement form here), a block-form if, or a
        statement-shaped node (return/throw/assign/loop/++). Forces if/when into
        statement form and keeps such a node out of a lambda body / ternary branch."""
        if n is None:
            return False
        if n.type in ("block", "when_expression", "try_expression"):
            return True
        if n.type == "if_expression":
            return self._if_is_block(n)
        return self._stmt_shaped(n)

    def _branch(self, body, lead):
        """Render a branch body (block or single node), distributing `lead` onto the
        branch's value (its last statement) via `_distribute` -- so a last statement
        that is itself a when/if/return/throw/++ is handled correctly, not blindly
        prefixed. Hoist-aware."""
        stmts = self.named(body) if body.type == "block" else [body]
        if not (lead and stmts):
            return _block(self.render_statements(stmts))
        lines = self.render_statements(stmts[:-1])
        before = len(self._hoist)
        last_line = self._distribute(stmts[-1], lead)
        lines += self._hoist[before:]
        del self._hoist[before:]
        lines.append(last_line)
        return _block(lines)

    # ---- loops ----------------------------------------------------------- #
    @kind("for_statement")
    def v_for(self, node):
        var = next((c for c in node.children if c.type in
                    ("variable_declaration", "identifier")), None)
        var_txt = self.text(var) if var is not None else "item"
        body = next((c for c in node.children if c.type == "block"), None)
        it = self._loop_iterable(node, exclude=var)
        return f"for {var_txt} in {it}:\n{self._suite(body)}"

    @kind("while_statement")
    def v_while(self, node):
        cond = self._condition(node)
        body = next((c for c in node.children if c.type == "block"), None)
        return f"while {cond}:\n{self._suite(body)}"

    @kind("do_while_statement")
    def v_do_while(self, node):
        cond = self._condition(node)
        body = next((c for c in node.children if c.type == "block"), None)
        lines = [self.visit(c) for c in self.named(body)] if body else []
        lines.append(f"if not ({cond}):")
        lines.append("    break")
        return "while True:\n" + _block(lines)

    # ---- try / jumps / assignment ---------------------------------------- #
    @kind("try_expression")
    def v_try(self, node):
        return self._try(node, "")

    def _try(self, node, lead):
        # Kotlin try is an expression: its value is the try block's (or the matching
        # catch block's) last expression. `lead` distributes into try/catch via
        # _branch; `finally` never carries the value, so it stays a plain suite.
        kids = self.named(node)
        out = ["try:", self._branch(kids[0], lead)]
        for c in node.named_children:
            if c.type == "catch_block":
                ck = c.named_children
                ename = next((self._safe(self.text(k))
                              for k in ck if k.type == "identifier"), "e")
                ut = next((k for k in ck if k.type == "user_type"), None)
                etype = self.text(ut) if ut is not None else "Exception"
                cblock = next((k for k in ck if k.type == "block"), None)
                cbody = self._branch(cblock, lead) if cblock is not None else _block([])
                out += [f"except {etype} as {ename}:", cbody]
            elif c.type == "finally_block":
                fblock = next((k for k in c.named_children if k.type == "block"), None)
                out += ["finally:", self._suite(fblock)]
        return "\n".join(out)

    @kind("assignment")
    def v_assignment(self, node):
        kids = self.named(node)
        op = next((c.type for c in node.children
                   if c.type in ("=", "+=", "-=", "*=", "/=", "%=")), "=")
        tgt = kids[0]
        # `a?.b = v` -> guarded assignment (Kotlin no-ops when a is null). The safe-call would
        # otherwise render as a ternary on the left, which can't be assigned to.
        if tgt.type == "navigation_expression" and any(c.type == "?." for c in tgt.children):
            nk = self.named(tgt)
            recv, attr = self.visit(nk[0]), self._safe(self.text(nk[-1]))
            return f"if {recv} is not None:\n{_block([f'{recv}.{attr} {op} {self.visit(kids[-1])}'])}"
        return f"{self.visit(tgt)} {op} {self.visit(kids[-1])}"

    @kind("return_expression")
    def v_return(self, node):
        # `return@label [value]`: the `return@` token makes the FIRST named child the label (an
        # identifier) -- drop it. `return` from the lambda-as-def is correct for `launch`/`let` blocks
        # AND for forEach (returning from the per-item function = skip to the next item).
        kids = self.named(node)
        if any(c.type == "return@" for c in node.children):
            kids = kids[1:]
        if not kids:
            return "return"
        return self._distribute(kids[0], "return ")

    @kind("throw_expression")
    def v_throw(self, node):
        kids = self.named(node)
        return f"raise {self.visit(kids[0])}" if kids else "raise"

    # ---- helpers --------------------------------------------------------- #
    def _condition(self, node):
        pc = next((c for c in node.children if c.type == "parenthesized_expression"), None)
        if pc is not None:
            inner = self.named(pc)
            return self.visit(inner[0]) if inner else "True"
        kids = self.named(node)
        return self.visit(kids[0]) if kids else "True"

    def _suite(self, n):
        if n is None:
            return _block([])
        nodes = self.named(n) if n.type == "block" else [n]
        return _block(self.render_statements(nodes))

    def _loop_iterable(self, node, exclude):
        kinds = ("call_expression", "navigation_expression", "identifier",
                 "binary_expression", "range_expression", "parenthesized_expression",
                 "index_expression", "infix_expression")
        cand = next((c for c in node.children
                     if c.type in kinds and c is not exclude), None)
        return self.visit(cand) if cand is not None else "[]"
