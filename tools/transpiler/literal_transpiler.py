import os
import sys
import ast
import keyword

# Attempt to load tree_sitter_kotlin
try:
    from tree_sitter import Language, Parser
    import tree_sitter_kotlin as tsk
except ImportError:
    print("Error: tree_sitter or tree_sitter_kotlin not found. Please ensure they are installed.")
    sys.exit(1)

# ---------------------------------------------------------------------------
# Collaboration note (Claude, log_36): this file is Gemini's literal transpiler.
# The architecture (LiteralVisitor / parse_expression / visit) is unchanged.
# What changed, to take the fleet from "18/27 compile, 0 run" toward runnable:
#   1. ALL contexts route through parse_expression (if/when/while/for conditions
#      + iterables) instead of raw get_text  -> fixes `||`, `!`, `==` leaks.
#   2. unary_expression `!x` -> `(not x)`.
#   3. string_literal -> f-string (handles `${expr}` interpolation, incl. nested
#      if-expressions as ternaries).
#   4. if_expression in value position -> Python ternary.
#   5. elvis-with-control-flow (`x ?: return`) lowered at statement level to a
#      guard, since Python has no statement-expression.
#   6. implicit `this`: identifiers that name a class member -> `self.<name>`.
#   7. function-local `val/var` -> real local assignment (not `self.x = None`).
#   8. lambdas: unique names, `it=None` param, implicit return of the last expr.
#   9. `null`->None, numeric suffixes (1_000L -> 1000) normalized everywhere.
#  10. the emit gate is now blocking (run() exits non-zero on invalid Python).
# ---------------------------------------------------------------------------

def build_parser():
    lang = Language(tsk.language())
    try:
        return Parser(lang)
    except TypeError:
        p = Parser()
        p.language = lang
        return p


BINOPS = {
    "&&": "and", "||": "or",
    "===": "is", "!==": "is not",
}
JUMP_TYPES = ("return_expression", "throw_expression", "jump_expression",
              "break_expression", "continue_expression")


class LiteralVisitor:
    def __init__(self):
        self.indent_level = 0
        self.output = []
        self.class_members = set()   # field + method + ctor-param names of current class
        self.scopes = []             # stack of local variable sets
        self.func_depth = 0          # >0 means we are inside a function body (locals, not fields)
        self.lambda_counter = 0

    def _indent(self):
        return "    " * self.indent_level

    def emit(self, text):
        self.output.append(f"{self._indent()}{text}")

    def get_text(self, node, source_bytes):
        return source_bytes[node.start_byte:node.end_byte].decode('utf-8')

    def _safe_attr(self, name):
        # Kotlin method names like `.with(...)` / `.is(...)` collide with Python
        # keywords; mangle so the emitted Python parses.
        return name + "_" if keyword.iskeyword(name) else name

    def _is_jump(self, node, source_bytes):
        # The grammar gives `return`/`throw` their own *_expression nodes, but bare
        # `continue`/`break` parse as plain identifiers -- detect both.
        if node is None:
            return False
        if node.type in JUMP_TYPES:
            return True
        if node.type in ("identifier", "simple_identifier"):
            return self.get_text(node, source_bytes).strip() in ("continue", "break", "return")
        return False

    def _real(self, node):
        if not node: return []
        return [c for c in node.named_children if c.type not in ("line_comment", "block_comment")]

    # -- expression translation ------------------------------------------- #

    def parse_expression(self, node, source_bytes) -> str:
        if not node:
            return ""

        t = node.type

        if t in ("identifier", "simple_identifier"):
            text = self.get_text(node, source_bytes)
            if text == "null":
                return "None"
            if text == "true":
                return "True"
            if text == "false":
                return "False"
            if text == "this":
                return "self"
            if text in self.class_members:
                shadowed = any(text in s for s in self.scopes)
                if not shadowed:
                    return f"self.{text}"
            return text

        if t == "type_identifier":
            return self.get_text(node, source_bytes)

        if t in ("integer_literal", "number_literal", "hex_literal", "bin_literal",
                 "real_literal", "long_literal", "unsigned_literal", "float_literal"):
            text = self.get_text(node, source_bytes).replace("_", "")
            return text.rstrip("LFfuU") or "0"

        if t == "boolean_literal":
            return "True" if self.get_text(node, source_bytes) == "true" else "False"

        if t == "null_literal":
            return "None"

        if t in ("string_literal", "line_string_literal", "multiline_string_literal"):
            return self._string_to_fstring(node, source_bytes)

        if t in ("character_literal",):
            return self.get_text(node, source_bytes).replace("'", '"', 2)

        if t in ("unary_expression", "prefix_expression"):
            op_node = next((c for c in node.children if c.type in ("!", "-", "+", "++", "--")), None)
            real_kids = self._real(node)
            operand = real_kids[-1] if real_kids else None
            operand_str = self.parse_expression(operand, source_bytes)
            if op_node and op_node.type == "!":
                return f"(not {operand_str})"
            if op_node and op_node.type in ("-", "+"):
                return f"{op_node.type}{operand_str}"
            return operand_str

        if t == "postfix_expression":
            # e.g. `x!!` -> just `x`
            real_kids = self._real(node)
            inner = real_kids[0] if real_kids else None
            return self.parse_expression(inner, source_bytes)

        if t == "navigation_expression":
            real_kids = self._real(node)
            left = self.parse_expression(real_kids[0], source_bytes) if real_kids else ""
            # the selector (right) is a bare member name -> keep literal, do NOT member-resolve
            right = ""
            if len(real_kids) > 1:
                right = self._safe_attr(self.get_text(real_kids[-1], source_bytes))
            op_node = next((c for c in node.children if c.type in (".", "?.")), None)
            if op_node and op_node.type == "?.":
                return f"({left}.{right} if {left} is not None else None)"
            return f"{left}.{right}"

        if t == "call_expression":
            return self._parse_call(node, source_bytes)

        if t == "index_expression":
            real_kids = self._real(node)
            base = self.parse_expression(real_kids[0], source_bytes) if real_kids else ""
            idxs = [self.parse_expression(c, source_bytes) for c in real_kids[1:]]
            return f"{base}[{', '.join(idxs)}]" if idxs else f"{base}[0]"

        if t in ("binary_expression", "comparison_expression", "equality_expression",
                 "additive_expression", "multiplicative_expression",
                 "conjunction_expression", "disjunction_expression",
                 "elvis_expression", "in_expression", "is_expression"):
            real_kids = self._real(node)
            left = self.parse_expression(real_kids[0], source_bytes) if real_kids else ""
            right_node = real_kids[1] if len(real_kids) > 1 else None
            right = self.parse_expression(right_node, source_bytes)
            op = next((c for c in node.children
                       if c.type in ("+", "-", "*", "/", "%", "==", "!=", ">", "<", ">=", "<=",
                                     "?:", "&&", "||", "===", "!==", "in", "!in", "is", "!is")), None)
            op_text = op.type if op else ""
            if op_text == "?:":
                # `x ?: <jump>` nested inside an expression can't carry the jump in
                # Python (jumps are statements); the statement-level lowering in
                # _elvis_cf handles the common `val a = x ?: return` case.
                if self._is_jump(right_node, source_bytes):
                    return f"({left} if {left} is not None else None)"
                return f"({left} if {left} is not None else {right})"
            if op_text == "is":
                return f"isinstance({left}, {right})"
            if op_text == "!is":
                return f"(not isinstance({left}, {right}))"
            if op_text == "in":
                return f"({left} in {right})"
            if op_text == "!in":
                return f"({left} not in {right})"
            if op_text in BINOPS:
                return f"{left} {BINOPS[op_text]} {right}"
            return f"{left} {op_text} {right}"

        if t == "parenthesized_expression":
            real_kids = self._real(node)
            inner = self.parse_expression(real_kids[0], source_bytes) if real_kids else ""
            return f"({inner})"

        if t == "if_expression":
            if self._if_has_block(node):
                return self._emit_block_wrapper(node, source_bytes, self._visit_if_statement)
            return self._if_as_ternary(node, source_bytes)

        if t in ("lambda_literal", "annotated_lambda"):
            return self._lambda_as_pyexpr(node, source_bytes)

        if t in ("as_expression", "cast_expression"):
            # Python is dynamically typed: `x as T` / `x as? T` -> just `x`.
            return self.parse_expression(node.named_children[0], source_bytes) if node.named_children else "None"

        if t == "when_expression":
            has_blocks = any(c.type in ("block", "control_structure_body") and len(c.named_children) > 1 
                             for e in self._when_entries(node) for c in e.children)
            if has_blocks:
                return self._emit_block_wrapper(node, source_bytes, self._visit_when)
            return self._when_as_ternary(node, source_bytes)

        if t in ("collection_literal",):
            return "[" + ", ".join(self.parse_expression(c, source_bytes) for c in node.named_children) + "]"

        # fallback: NEVER emit raw Kotlin as code -- it breaks the parse and leaks
        # unicode from comments. Emit a loud, valid-Python placeholder instead.
        return '"__TODO_EXPR__"'

    def _emit_block_wrapper(self, node, source_bytes, visit_func):
        name = f"_block_{self.lambda_counter}"
        self.lambda_counter += 1
        self.emit(f"def {name}():")
        self.indent_level += 1
        self.scopes.append(set())
        visit_func(node, source_bytes, is_value=True)
        self.scopes.pop()
        self.indent_level -= 1
        return f"{name}()"

    def _parse_call(self, node, source_bytes):
        real_kids = self._real(node)
        func_node = real_kids[0] if real_kids else None

        is_safe_call = False
        safe_left = safe_right = ""
        if func_node and func_node.type == "navigation_expression":
            op_node = next((c for c in func_node.children if c.type == "?."), None)
            if op_node:
                is_safe_call = True
                func_real = self._real(func_node)
                safe_left = self.parse_expression(func_real[0], source_bytes) if func_real else ""
                safe_right = self._safe_attr(self.get_text(func_real[-1], source_bytes)) \
                    if len(func_real) > 1 else ""

        func_name = self.parse_expression(func_node, source_bytes)
        args_node = next((c for c in node.children if c.type == "value_arguments"), None)
        args_str = self._parse_args(args_node, source_bytes)

        lambda_node = self._trailing_lambda(node)
        if lambda_node:
            lambda_name = self._emit_lambda_block(lambda_node, source_bytes)
            if func_node and func_node.type == "call_expression" and args_node is None:
                if func_name.endswith(")"):
                    if func_name.endswith("()"):
                        func_name = func_name[:-1] + f"{lambda_name})"
                    else:
                        func_name = func_name[:-1] + f", {lambda_name})"
                    return func_name
            else:
                if args_str:
                    args_str = f"{args_str}, {lambda_name}"
                else:
                    args_str = lambda_name

        if is_safe_call:
            return f"({safe_left}.{safe_right}({args_str}) if {safe_left} is not None else None)"
        return f"{func_name}({args_str})"

    def _parse_args(self, args_node, source_bytes):
        if not args_node:
            return ""
        parts = []
        for arg in args_node.named_children:
            if arg.type != "value_argument":
                continue
            has_eq = next((c for c in arg.children if c.type == "="), None)
            if has_eq:
                name = self.get_text(arg.named_children[0], source_bytes)
                expr = self.parse_expression(arg.named_children[-1], source_bytes) \
                    if len(arg.named_children) > 1 else ""
                parts.append(f"{name}={expr}")
            else:
                parts.append(self.parse_expression(arg.named_children[-1], source_bytes)
                             if arg.named_children else "")
        return ", ".join(parts)

    def _if_as_ternary(self, node, source_bytes):
        # named children: [condition, then] or [condition, then, else]
        named = self._real(node)
        cond_node = named[0] if named else None
        rest = named[1:]
        cond_str = self.parse_expression(cond_node, source_bytes) if cond_node else "True"
        then_e = self.parse_expression(rest[0], source_bytes) if len(rest) > 0 else "None"
        has_else = any(c.type == "else" for c in node.children)
        else_e = self.parse_expression(rest[1], source_bytes) if (has_else and len(rest) > 1) else "None"
        return f"({then_e} if {cond_str} else {else_e})"

    def _if_has_block(self, node):
        named = list(node.named_children)
        rest = named[1:]
        if len(rest) > 0 and rest[0].type in ("block", "control_structure_body"):
            return True
        if len(rest) > 1 and rest[1].type in ("block", "control_structure_body"):
            return True
        return False

    def _condition_of(self, node, source_bytes):
        cond_node = next((c for c in node.children if c.type == "parenthesized_expression"), None)
        if cond_node is not None:
            c_real = self._real(cond_node)
            inner = c_real[0] if c_real else None
            return self.parse_expression(inner, source_bytes) if inner else "True"
        # no parens -> first named child is the condition
        n_real = self._real(node)
        return self.parse_expression(n_real[0], source_bytes) if n_real else "True"

    def _string_to_fstring(self, node, source_bytes):
        segs = []
        has_interp = False
        for c in node.children:
            ct = c.type
            if ct in ('"', '"""', "'"):
                continue
            if ct == "interpolation":
                has_interp = True
                expr_node = next((k for k in c.named_children), None)
                inner = self.parse_expression(expr_node, source_bytes) if expr_node else ""
                segs.append("{" + inner + "}")
            elif ct in ("interpolated_identifier",):
                has_interp = True
                segs.append("{" + self.parse_expression(c, source_bytes) + "}")
            else:
                # literal content (string_content, line_str_text, escape, '$', etc.)
                txt = self.get_text(c, source_bytes)
                segs.append(txt.replace("{", "{{").replace("}", "}}"))
        body = "".join(segs)
        if not has_interp:
            return '"' + body.replace("\\", "\\\\").replace('"', '\\"') + '"'
        if '"' not in body:
            return 'f"' + body + '"'
        if "'" not in body:
            return "f'" + body + "'"
        return 'f"""' + body + '"""'

    def _lambda_as_pyexpr(self, node, source_bytes):
        lam = node
        if node.type == "annotated_lambda":
            lam = next((c for c in node.children if c.type == "lambda_literal"), node)
        stmts = self._lambda_statements(lam)
        if len(stmts) == 1:
            return f"(lambda it=None: {self.parse_expression(stmts[0], source_bytes)})"
        return "(lambda it=None: None)"

    # -- statement / structure visiting ----------------------------------- #

    def _collect_members(self, body_node, source_bytes):
        for child in body_node.named_children:
            if child.type == "property_declaration":
                vd = next((c for c in child.children if c.type == "variable_declaration"), None)
                if vd:
                    pid = next((c for c in vd.children if c.type in ("identifier", "simple_identifier")), None)
                    if pid:
                        self.class_members.add(self.get_text(pid, source_bytes))
            elif child.type == "function_declaration":
                nid = next((c for c in child.children if c.type in ("identifier", "simple_identifier")), None)
                if nid:
                    self.class_members.add(self.get_text(nid, source_bytes))

    def visit(self, node, source_bytes):
        if node.type == "source_file":
            for child in node.named_children:
                self.visit(child, source_bytes)

        elif node.type == "class_declaration":
            # skip annotations for class
            name_node = next((c for c in node.children if c.type in ("identifier", "simple_identifier")), None)
            name = self.get_text(name_node, source_bytes) if name_node else "UnknownClass"
            body_node = next((c for c in node.children if c.type in ("class_body", "enum_class_body")), None)

            if node.parent is None or node.parent.type == "source_file":
                self.emit("")
                self.emit("")
            self.emit(f"class {name}:")
            self.indent_level += 1

            has_enum_entries = False
            if body_node and body_node.type == "enum_class_body":
                entries = [c for c in body_node.named_children if c.type == "enum_entry"]
                for e in entries:
                    e_name = next((c for c in e.named_children if c.type in ("identifier", "simple_identifier")), None)
                    if e_name:
                        ename_str = self.get_text(e_name, source_bytes)
                        self.emit(f"{ename_str} = '{ename_str}'")
                        has_enum_entries = True

            prev_members = self.class_members
            self.class_members = set()
            ctor_params = []
            
            for cp in node.children:
                if cp.type == "primary_constructor":
                    for pn in cp.named_children:
                        if pn.type == "class_parameter":
                            pid = next((c for c in pn.children if c.type in ("identifier", "simple_identifier")), None)
                            if pid:
                                name = self.get_text(pid, source_bytes)
                                self.class_members.add(name)
                                ctor_params.append(name)
            
            properties = []
            inits = []
            methods = []
            
            if body_node:
                self._collect_members(body_node, source_bytes)
                for child in body_node.named_children:
                    if child.type == "property_declaration":
                        properties.append(child)
                    elif child.type == "anonymous_initializer":
                        inits.append(child)
                    elif child.type != "enum_entry":
                        methods.append(child)
                        
            init_args = ["self"] + ctor_params
            self.emit(f"def __init__({', '.join(init_args)}):")
            self.indent_level += 1
            has_init_body = False
            for cp in ctor_params:
                self.emit(f"self.{cp} = {cp}")
                has_init_body = True
                
            self.func_depth += 1
            for p in properties:
                self.visit(p, source_bytes)
                has_init_body = True
            for i in inits:
                # init_block has a block child
                block = next((c for c in i.children if c.type == "block"), None)
                if block:
                    self.visit(block, source_bytes)
                has_init_body = True
            self.func_depth -= 1
            
            if not has_init_body:
                self.emit("pass")
            self.indent_level -= 1
            
            if not methods and not properties and not inits and not ctor_params:
                self.emit("pass")
            else:
                for m in methods:
                    self.visit(m, source_bytes)

            self.indent_level -= 1
            self.class_members = prev_members
            self.emit("")

        elif node.type == "function_declaration":
            for child in node.children:
                if child.type == "modifiers":
                    for c in child.children:
                        if c.type == "annotation":
                            self.emit(self.get_text(c, source_bytes))

            name_node = next((c for c in node.children if c.type in ("identifier", "simple_identifier")), None)
            func_name = self.get_text(name_node, source_bytes) if name_node else "unknown_func"

            params = ["self"]
            param_node = next((c for c in node.children if c.type == "function_value_parameters"), None)
            if param_node:
                for p in param_node.named_children:
                    if p.type == "parameter":
                        pid = next((c for c in p.children if c.type in ("identifier", "simple_identifier")), None)
                        if pid:
                            params.append(self.get_text(pid, source_bytes))

            self.emit(f"def {func_name}({', '.join(params)}):")
            self.indent_level += 1
            self.func_depth += 1
            self.scopes.append(set(params[1:]))

            body_node = next((c for c in node.children if c.type in ("function_body", "block")), None)
            if body_node:
                self.visit(body_node, source_bytes)
            else:
                self.emit("pass")

            self.scopes.pop()
            self.func_depth -= 1
            self.indent_level -= 1
            self.emit("")

        elif node.type in ("block", "function_body"):
            if node.type == "function_body" and any(c.type == "=" for c in node.children):
                real_kids = self._real(node)
                if real_kids:
                    self.emit(f"return {self.parse_expression(real_kids[0], source_bytes)}")
                else:
                    self.emit("pass")
                return

            real = [c for c in node.named_children]
            if len(real) == 0:
                self.emit("pass")
            else:
                for child in real:
                    self.visit(child, source_bytes)

        elif node.type == "property_declaration":
            self._visit_property(node, source_bytes)

        elif node.type == "expression_statement":
            for child in node.named_children:
                self.visit(child, source_bytes)

        elif node.type == "if_expression":
            self._visit_if_statement(node, source_bytes)

        elif node.type == "when_expression":
            self._visit_when(node, source_bytes)

        elif node.type == "assignment":
            self._visit_assignment(node, source_bytes)

        elif node.type == "for_statement":
            loop_var = None
            for c in node.children:
                if c.type in ("variable_declaration", "identifier", "simple_identifier"):
                    loop_var = c
                    break
            var_text = self.get_text(loop_var, source_bytes) if loop_var else "item"
            iterable = next((c for c in node.children if c.type in
                             ("identifier", "simple_identifier", "navigation_expression",
                              "call_expression", "binary_expression", "range_expression",
                              "parenthesized_expression")), None)
            iter_text = self._iterable_text(iterable, source_bytes)
            self.emit(f"for {var_text} in {iter_text}:")
            self.indent_level += 1
            if self.scopes:
                self.scopes[-1].add(var_text)
            body = node.named_children[-1] if node.named_children else None
            if body is not None and body != iterable and body.type in ("block", "control_structure_body"):
                self.visit(body, source_bytes)
            elif body is not None and body != iterable:
                self.visit(body, source_bytes)
            else:
                self.emit("pass")
            self.indent_level -= 1

        elif node.type == "while_statement":
            cond = next((c for c in node.children if c.type == "parenthesized_expression"), None)
            cond_str = "True"
            if cond and cond.named_children:
                cond_str = self.parse_expression(cond.named_children[0], source_bytes)
            self.emit(f"while {cond_str}:")
            self.indent_level += 1
            body = node.named_children[-1] if node.named_children else None
            if body is not None and body != cond:
                self.visit(body, source_bytes)
            else:
                self.emit("pass")
            self.indent_level -= 1

        elif node.type in ("control_structure_body",):
            if node.named_children:
                for c in node.named_children:
                    self.visit(c, source_bytes)
            else:
                self.emit("pass")

        elif node.type in ("return_statement", "return_expression", "jump_expression"):
            self._visit_jump(node, source_bytes)

        elif node.type == "throw_expression":
            inner = node.named_children[0] if node.named_children else None
            self.emit(f"raise {self.parse_expression(inner, source_bytes)}" if inner else "raise")

        elif node.type in ("call_expression", "navigation_expression"):
            self.emit(self.parse_expression(node, source_bytes))

        elif node.type == "import_list":
            for child in node.named_children:
                self.visit(child, source_bytes)

        elif node.type in ("import", "import_header"):
            raw_import = self.get_text(node, source_bytes)
            if "kotlinx.coroutines.flow." in raw_import:
                symbol = raw_import.split("kotlinx.coroutines.flow.")[-1].strip()
                self.emit(f"from core.flow import {symbol}")
            elif "kotlinx.coroutines." in raw_import:
                symbol = raw_import.split("kotlinx.coroutines.")[-1].strip()
                self.emit(f"from core.coroutines import {symbol}")
            else:
                self.emit(f"# TODO_RAW_IMPORT: {raw_import}")

        elif node.type in ("package_header", "line_comment", "block_comment", "shebang_line"):
            pass

        else:
            raw_text = self.get_text(node, source_bytes).replace('\n', '\\n')
            self.emit(f"# TODO_UNHANDLED_KOTLIN_NODE: [{node.type}] {raw_text}")
            self.emit("pass")

    # -- statement helpers ------------------------------------------------ #

    def _visit_property(self, node, source_bytes):
        vd = next((c for c in node.children if c.type == "variable_declaration"), None)
        name = None
        if vd:
            pid = next((c for c in vd.children if c.type in ("identifier", "simple_identifier")), None)
            if pid:
                name = self.get_text(pid, source_bytes)
        # the initializer is the expression after `=`
        eq = next((c for c in node.children if c.type == "="), None)
        value_node = None
        if eq:
            idx = node.children.index(eq)
            for c in node.children[idx + 1:]:
                if c.is_named:
                    value_node = c
                    break

        target = name if name else "_unknown"
        is_class_field = (node.parent is not None and node.parent.type == "class_body")
        if is_class_field and name:
            target = f"self.{name}"
        elif self.scopes and name and self.func_depth > 0:
            self.scopes[-1].add(name)

        if value_node is None:
            self.emit(f"{target} = None")
            return

        # elvis-with-control-flow:  val a = x ?: return
        cf = self._elvis_cf(value_node, source_bytes)
        if cf:
            left_node, jump_node = cf
            self.emit(f"{target} = {self.parse_expression(left_node, source_bytes)}")
            self.emit(f"if {target} is None:")
            self.indent_level += 1
            self._visit_jump(jump_node, source_bytes)
            self.indent_level -= 1
            return

        lam = self._trailing_lambda(value_node)
        if lam:
            self._emit_lambda_assign(target, value_node, lam, source_bytes)
        else:
            self.emit(f"{target} = {self.parse_expression(value_node, source_bytes)}")

    def _visit_assignment(self, node, source_bytes):
        left = self.parse_expression(node.named_children[0], source_bytes) if node.named_children else ""
        right_node = node.named_children[1] if len(node.named_children) > 1 else None

        if not left or "__TODO_EXPR__" in left or left[0] in "\"'" or left[0].isdigit():
            raw = self.get_text(node, source_bytes).replace("\n", " ")[:80]
            self.emit(f"# TODO_UNRESOLVED_ASSIGN_TARGET: {raw}")
            return

        cf = self._elvis_cf(right_node, source_bytes)
        if cf:
            left_node, jump_node = cf
            self.emit(f"{left} = {self.parse_expression(left_node, source_bytes)}")
            self.emit(f"if {left} is None:")
            self.indent_level += 1
            self._visit_jump(jump_node, source_bytes)
            self.indent_level -= 1
            return

        lam = self._trailing_lambda(right_node)
        if lam:
            self._emit_lambda_assign(left, right_node, lam, source_bytes)
        else:
            self.emit(f"{left} = {self.parse_expression(right_node, source_bytes)}")

    def _visit_jump(self, node, source_bytes):
        # return / throw / break / continue
        txt = self.get_text(node, source_bytes).strip()
        if txt.startswith("throw"):
            inner = next((c for c in node.named_children), None)
            self.emit(f"raise {self.parse_expression(inner, source_bytes)}" if inner else "raise")
        elif txt.startswith("break"):
            self.emit("break")
        elif txt.startswith("continue"):
            self.emit("continue")
        else:
            val = next((c for c in node.named_children if c.is_named), None)
            if val is not None:
                self.emit(f"return {self.parse_expression(val, source_bytes)}")
            else:
                self.emit("return")

    def _elvis_cf(self, node, source_bytes):
        """If node is `left ?: <jump>`, return (left_node, jump_node), else None."""
        if node is None:
            return None
        if node.type not in ("binary_expression", "elvis_expression"):
            return None
        has_elvis = any(c.type == "?:" for c in node.children)
        if not has_elvis or len(node.named_children) < 2:
            return None
        right = node.named_children[1]
        if self._is_jump(right, source_bytes):
            return node.named_children[0], right
        return None

    def _visit_if_statement(self, node, source_bytes, is_value=False):
        cond_str = self._condition_of(node, source_bytes)
        self.emit(f"if {cond_str}:")
        self.indent_level += 1
        cond_node = next((c for c in node.children if c.type == "parenthesized_expression"), None)
        # consequence = first named child after the condition that is a body/expr
        named = list(node.named_children)
        consequence = None
        else_node = None
        seen_else_kw = False
        for c in node.children:
            if c.type == "else":
                seen_else_kw = True
                continue
            if not c.is_named:
                continue
            if c == cond_node:
                continue
            if c.type == "parenthesized_expression":
                continue
            if not seen_else_kw and consequence is None and c != cond_node:
                # skip the bare condition expression if it's a named child (no parens form)
                if cond_node is None and c == named[0]:
                    continue
                consequence = c
            elif seen_else_kw and else_node is None:
                else_node = c
        if consequence is not None:
            if is_value:
                self._emit_block_as_value(consequence, source_bytes)
            else:
                self.visit(consequence, source_bytes)
        else:
            self.emit("pass" if not is_value else "return None")
        self.indent_level -= 1
        if else_node is not None:
            self.emit("else:")
            self.indent_level += 1
            if is_value:
                self._emit_block_as_value(else_node, source_bytes)
            else:
                self.visit(else_node, source_bytes)
            self.indent_level -= 1
        elif is_value:
            self.emit("else:")
            self.indent_level += 1
            self.emit("return None")
            self.indent_level -= 1

    def _emit_block_as_value(self, block_node, source_bytes):
        if block_node.type in ("block", "control_structure_body"):
            stmts = list(block_node.named_children)
            if not stmts:
                self.emit("return None")
            else:
                for i, stmt in enumerate(stmts):
                    if i == len(stmts) - 1:
                        inner = stmt.named_children[0] if stmt.type == "expression_statement" and stmt.named_children else stmt
                        self.emit(f"return {self.parse_expression(inner, source_bytes)}")
                    else:
                        self.visit(stmt, source_bytes)
        else:
            self.emit(f"return {self.parse_expression(block_node, source_bytes)}")

    def _when_subject(self, node, source_bytes):
        subject_node = next((c for c in node.children if c.type == "when_subject"), None)
        if subject_node is None:
            return None
        inner = None
        for c in subject_node.named_children:
            inner = c
        return self.parse_expression(inner, source_bytes) if inner is not None else None

    def _when_entries(self, node):
        body = next((c for c in node.children if c.type in ("when_body", "block")), None)
        src = body.named_children if body else node.named_children
        return [c for c in src if c.type == "when_entry"]

    def _visit_when(self, node, source_bytes, is_value=False):
        subject = self._when_subject(node, source_bytes)
        entries = self._when_entries(node)
        if not entries:
            self.emit("pass")
            return
        is_first = True
        for entry in entries:
            cond_node = next((c for c in entry.children if c.type == "when_condition"), None)
            is_else = any(c.type == "else" for c in entry.children)
            if is_else:
                self.emit("else:")
            else:
                test = self._when_test(subject, cond_node, source_bytes)
                self.emit(f"{'if' if is_first else 'elif'} {test}:")
            self.indent_level += 1
            entry_body = self._when_entry_body(entry)
            if entry_body is not None:
                if is_value:
                    self._emit_block_as_value(entry_body, source_bytes)
                else:
                    self.visit(entry_body, source_bytes)
            else:
                self.emit("pass" if not is_value else "return None")
            self.indent_level -= 1
            is_first = False

    def _when_as_ternary(self, node, source_bytes):
        subject = self._when_subject(node, source_bytes)
        entries = self._when_entries(node)
        else_entry = next((e for e in entries if any(c.type == "else" for c in e.children)), None)
        result = self._when_entry_value(else_entry, source_bytes) if else_entry is not None else "None"
        for e in reversed([e for e in entries if e is not else_entry]):
            cond_node = next((c for c in e.children if c.type == "when_condition"), None)
            test = self._when_test(subject, cond_node, source_bytes)
            val = self._when_entry_value(e, source_bytes)
            result = f"({val} if {test} else {result})"
        return result

    def _when_test(self, subject, cond_node, source_bytes):
        if cond_node is None:
            return "True"
        if subject is None:
            inner = next((c for c in cond_node.named_children), None)
            return self.parse_expression(inner, source_bytes)
        if any(c.type == "is" for c in cond_node.children):
            tnode = next((c for c in cond_node.named_children), None)
            neg = any(c.type == "!is" for c in cond_node.children)
            inner = f"isinstance({subject}, {self.parse_expression(tnode, source_bytes)})"
            return f"(not {inner})" if neg else inner
        if any(c.type == "in" for c in cond_node.children):
            rnode = next((c for c in cond_node.named_children), None)
            return f"{subject} in {self.parse_expression(rnode, source_bytes)}"
        expr_node = next((c for c in cond_node.named_children), None)
        return f"{subject} == {self.parse_expression(expr_node, source_bytes)}"

    def _when_entry_value(self, entry, source_bytes):
        if entry is None:
            return "None"
        body = self._when_entry_body(entry)
        if body is None:
            return "None"
        if body.type in ("block", "control_structure_body"):
            stmts = list(body.named_children)
            if not stmts:
                return "None"
            last = stmts[-1]
            inner = last.named_children[0] if last.type == "expression_statement" and last.named_children else last
            return self.parse_expression(inner, source_bytes)
        return self.parse_expression(body, source_bytes)

    def _when_entry_body(self, entry):
        seen = False
        for c in entry.children:
            if c.type in ("when_condition", "else"):
                seen = True
                continue
            if seen and c.type not in ("->", "line_comment", "block_comment") and c.is_named:
                return c
        return None

    def _iterable_text(self, iterable, source_bytes):
        if iterable is None:
            return "[]"
        if iterable.type in ("identifier", "simple_identifier", "navigation_expression", "call_expression"):
            return self.parse_expression(iterable, source_bytes)
        # range `a..b`, `a downTo b`, `a until b step c` etc.
        txt = self.get_text(iterable, source_bytes)
        rng = self._range_to_python(iterable, txt, source_bytes)
        if rng is not None:
            return rng
        return f"[_RAW_ITERABLE_TODO_]  # {txt}".split("#")[0].strip() or "[]"

    def _range_to_python(self, node, txt, source_bytes):
        # best-effort: a..b -> range(a, b+1); a until b -> range(a, b); a downTo b -> range(a, b-1, -1)
        for kw, repl in (("downTo", "down"), ("until", "until"), ("..", "to")):
            if kw in txt:
                parts = txt.split(kw)
                if len(parts) == 2:
                    lo = parts[0].strip().rstrip("L")
                    hi = parts[1]
                    step = "1"
                    if "step" in hi:
                        hi, step = hi.split("step")
                        step = step.strip().rstrip("L")
                    hi = hi.strip().rstrip("L")
                    if repl == "down":
                        return f"range({lo}, ({hi}) - 1, -{step})"
                    if repl == "until":
                        return f"range({lo}, {hi}, {step})"
                    return f"range({lo}, ({hi}) + 1, {step})"
        return None

    # -- lambda handling -------------------------------------------------- #

    def _trailing_lambda(self, node):
        if node is None or node.type not in ("call_expression", "navigation_expression"):
            return None
        lam = next((c for c in node.children if c.type == "lambda_literal"), None)
        if lam:
            return lam
        ann = next((c for c in node.children if c.type == "annotated_lambda"), None)
        if ann:
            return next((c for c in ann.children if c.type == "lambda_literal"), None)
        rhs = next((c for c in node.children if c.type == "call_expression"), None)
        if rhs:
            return self._trailing_lambda(rhs)
        return None

    def _lambda_statements(self, lambda_node):
        if lambda_node is None:
            return []
        stmts = next((c for c in lambda_node.named_children if c.type == "statements"), None)
        if stmts:
            return list(stmts.named_children)
        return [c for c in lambda_node.named_children if c.type != "lambda_parameters"]

    def _emit_lambda_block(self, lambda_node, source_bytes):
        """Emit a uniquely-named def for a Kotlin lambda; returns the def name.
        Binds implicit `it` (default None so zero-arg call sites also work) and
        returns the value of the final expression (Kotlin's implicit return)."""
        name = f"_lambda_{self.lambda_counter}"
        self.lambda_counter += 1
        self.emit(f"def {name}(it=None):")
        self.indent_level += 1
        self.scopes.append({"it"})
        stmts = self._lambda_statements(lambda_node)
        if not stmts:
            self.emit("pass")
        else:
            for i, stmt in enumerate(stmts):
                last = (i == len(stmts) - 1)
                inner = stmt
                if stmt.type == "expression_statement" and stmt.named_children:
                    inner = stmt.named_children[0]
                if last and inner.type in (
                        "call_expression", "navigation_expression", "identifier",
                        "simple_identifier", "binary_expression", "if_expression",
                        "string_literal", "parenthesized_expression") and not self._trailing_lambda(inner):
                    self.emit(f"return {self.parse_expression(inner, source_bytes)}")
                else:
                    self.visit(stmt, source_bytes)
        self.scopes.pop()
        self.indent_level -= 1
        return name

    def _emit_trailing_lambda_call(self, node, lambda_node, source_bytes):
        func_name = self.parse_expression(node.named_children[0], source_bytes) if node.named_children else ""
        # gather any non-lambda args
        args_node = next((c for c in node.children if c.type == "value_arguments"), None)
        pre_args = self._parse_args(args_node, source_bytes)
        name = self._emit_lambda_block(lambda_node, source_bytes)
        all_args = (pre_args + ", " + name) if pre_args else name
        self.emit(f"{func_name}({all_args})")

    def _emit_lambda_assign(self, target, value_node, lambda_node, source_bytes):
        func_name = self.parse_expression(value_node.named_children[0], source_bytes) \
            if value_node.named_children else ""
        args_node = next((c for c in value_node.children if c.type == "value_arguments"), None)
        pre_args = self._parse_args(args_node, source_bytes)
        name = self._emit_lambda_block(lambda_node, source_bytes)
        all_args = (pre_args + ", " + name) if pre_args else name
        self.emit(f"{target} = {func_name}({all_args})")

    def transpile(self, source_code: bytes) -> str:
        parser = build_parser()
        tree = parser.parse(source_code)
        self.visit(tree.root_node, source_code)
        return "\n".join(self.output)


def run():
    if len(sys.argv) < 2:
        print("Usage: python literal_transpiler.py <path_to_kotlin_file>")
        sys.exit(1)

    kt_file = sys.argv[1]
    if not os.path.exists(kt_file):
        print(f"File not found: {kt_file}")
        sys.exit(1)

    with open(kt_file, "rb") as f:
        source_code = f.read()

    visitor = LiteralVisitor()
    python_code = visitor.transpile(source_code)

    out_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "build", "literal")
    os.makedirs(out_dir, exist_ok=True)
    out_file = os.path.join(out_dir, os.path.basename(kt_file).replace(".kt", ".py"))

    with open(out_file, "w") as f:
        f.write(python_code)

    print(f"Transpiled {kt_file} -> {out_file}")
    # Blocking gate: emitted Python MUST parse.
    try:
        ast.parse(python_code)
    except SyntaxError as e:
        print(f"ERROR: Emitted Python is invalid! (line {e.lineno}: {e.msg})")
        sys.exit(2)


if __name__ == "__main__":
    run()
