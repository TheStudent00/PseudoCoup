import os
import sys
import ast

# Attempt to load tree_sitter_kotlin
try:
    from tree_sitter import Language, Parser
    import tree_sitter_kotlin as tsk
except ImportError:
    print("Error: tree_sitter or tree_sitter_kotlin not found. Please ensure they are installed.")
    sys.exit(1)

def build_parser():
    lang = Language(tsk.language())
    try:
        return Parser(lang)
    except TypeError:
        p = Parser()
        p.language = lang
        return p

class LiteralVisitor:
    def __init__(self):
        self.indent_level = 0
        self.output = []
        
    def _indent(self):
        return "    " * self.indent_level
        
    def emit(self, text):
        self.output.append(f"{self._indent()}{text}")

    def get_text(self, node, source_bytes):
        return source_bytes[node.start_byte:node.end_byte].decode('utf-8')

    def parse_expression(self, node, source_bytes) -> str:
        if not node:
            return ""
            
        if node.type in ("identifier", "type_identifier", "number_literal", "boolean_literal", "null_literal"):
            text = self.get_text(node, source_bytes)
            if node.type == "boolean_literal":
                return "True" if text == "true" else "False"
            if node.type == "null_literal":
                return "None"
            if node.type == "number_literal" and text.endswith("L"):
                return text[:-1]
            return text
            
        elif node.type == "string_literal":
            return self.get_text(node, source_bytes)
            
        elif node.type == "navigation_expression":
            left = self.parse_expression(node.named_children[0], source_bytes) if len(node.named_children) > 0 else ""
            right = self.parse_expression(node.named_children[1], source_bytes) if len(node.named_children) > 1 else ""
            
            op_node = next((c for c in node.children if c.type in (".", "?.")), None)
            if op_node and op_node.type == "?.":
                # For safe navigation, we just construct the python equivalent but note that if it's called
                # e.g., (a.b if a is not None else None)(), it will crash in Python.
                # A fully robust transpile would extract this, but for 1:1 structure this is okay, or we can use a wrapper.
                # Actually, let's just emit `a.b if a is not None else None`.
                # If it's part of a call `a?.b()`, tree-sitter parses `call_expression(navigation_expression)`.
                return f"({left}.{right} if {left} is not None else None)"
            return f"{left}.{right}"
            
        elif node.type == "call_expression":
            func_node = node.named_children[0] if len(node.named_children) > 0 else None
            
            # Check if func_node is a safe navigation `x?.y`. If so, we must wrap the WHOLE call.
            is_safe_call = False
            safe_left = ""
            safe_right = ""
            if func_node and func_node.type == "navigation_expression":
                op_node = next((c for c in func_node.children if c.type == "?."), None)
                if op_node:
                    is_safe_call = True
                    safe_left = self.parse_expression(func_node.named_children[0], source_bytes)
                    safe_right = self.parse_expression(func_node.named_children[1], source_bytes)
            
            func_name = self.parse_expression(func_node, source_bytes)
            
            args_node = next((c for c in node.children if c.type == "value_arguments"), None)
            args_str = ""
            if args_node:
                args_list = []
                for arg in args_node.named_children:
                    if arg.type == "value_argument":
                        # Check for `x = y` (identifier followed by =)
                        has_eq = next((c for c in arg.children if c.type == "="), None)
                        if has_eq:
                            name_node = arg.named_children[0]
                            expr_nodes = arg.named_children[1:]
                            name = self.get_text(name_node, source_bytes)
                            expr = self.parse_expression(expr_nodes[-1] if expr_nodes else None, source_bytes)
                            args_list.append(f"{name}={expr}")
                        else:
                            expr = self.parse_expression(arg.named_children[-1] if len(arg.named_children) > 0 else None, source_bytes)
                            args_list.append(expr)
                args_str = ", ".join(args_list)
                
            if is_safe_call:
                return f"({safe_left}.{safe_right}({args_str}) if {safe_left} is not None else None)"
            return f"{func_name}({args_str})"
            
        elif node.type == "binary_expression":
            left = self.parse_expression(node.named_children[0], source_bytes) if len(node.named_children) > 0 else ""
            right = self.parse_expression(node.named_children[1], source_bytes) if len(node.named_children) > 1 else ""
            op = next((c for c in node.children if c.type in ("+", "-", "*", "/", "==", "!=", ">", "<", ">=", "<=", "?:", "&&", "||")), None)
            op_text = self.get_text(op, source_bytes) if op else ""
            
            if op_text == "?:":
                return f"({left} if {left} is not None else {right})"
            elif op_text == "&&":
                return f"{left} and {right}"
            elif op_text == "||":
                return f"{left} or {right}"
            else:
                return f"{left} {op_text} {right}"
                
        elif node.type == "parenthesized_expression":
            inner = self.parse_expression(node.named_children[0], source_bytes) if len(node.named_children) > 0 else ""
            return f"({inner})"
            
        else:
            return self.get_text(node, source_bytes)

    def visit(self, node, source_bytes):
        if node.type == "source_file":
            for child in node.named_children:
                self.visit(child, source_bytes)
                
        elif node.type == "class_declaration":
            # Extract class name
            name_node = next((c for c in node.children if c.type == "identifier"), None)
            class_name = self.get_text(name_node, source_bytes) if name_node else "UnknownClass"
            self.emit(f"class {class_name}:")
            self.indent_level += 1
            
            # Find class body
            body_node = next((c for c in node.children if c.type == "class_body"), None)
            if body_node:
                for child in body_node.named_children:
                    self.visit(child, source_bytes)
            else:
                self.emit("pass")
            self.indent_level -= 1
            self.emit("")
            
        elif node.type == "function_declaration":
            # Check for annotations (like @Composable)
            for child in node.children:
                if child.type == "modifiers":
                    annotations = [self.get_text(c, source_bytes) for c in child.children if c.type == "annotation"]
                    for ann in annotations:
                        self.emit(ann)
                        
            name_node = next((c for c in node.children if c.type == "identifier"), None)
            func_name = self.get_text(name_node, source_bytes) if name_node else "unknown_func"
            
            # Parameters
            params = ["self"]
            param_node = next((c for c in node.children if c.type == "function_value_parameters"), None)
            if param_node:
                for p in param_node.named_children:
                    if p.type == "parameter":
                        pid = next((c for c in p.children if c.type == "identifier"), None)
                        if pid:
                            params.append(self.get_text(pid, source_bytes))
            
            self.emit(f"def {func_name}({', '.join(params)}):")
            self.indent_level += 1
            
            body_node = next((c for c in node.children if c.type == "function_body" or c.type == "block"), None)
            if body_node:
                self.visit(body_node, source_bytes)
            else:
                self.emit("pass")
                
            self.indent_level -= 1
            self.emit("")
            
        elif node.type == "block" or node.type == "function_body":
            if len(node.named_children) == 0:
                self.emit("pass")
            else:
                for child in node.named_children:
                    self.visit(child, source_bytes)
                    
        elif node.type == "property_declaration":
            # For simplicity, we just output the raw text as a comment or try to parse it
            raw_text = self.get_text(node, source_bytes).replace('\n', ' ')
            name_node = next((c for c in node.children if c.type == "variable_declaration"), None)
            if name_node:
                pid = next((c for c in name_node.children if c.type == "identifier"), None)
                if pid:
                    prop_name = self.get_text(pid, source_bytes)
                    self.emit(f"self.{prop_name} = None  # {raw_text}")
                    return
            self.emit(f"# TODO_UNHANDLED_PROPERTY: {raw_text}")

        elif node.type == "expression_statement":
            for child in node.named_children:
                self.visit(child, source_bytes)
                
        elif node.type == "if_expression":
            condition_node = next((c for c in node.children if c.type == "value_arguments" or c.type == "parenthesized_expression"), None)
            if not condition_node:
                condition_node = node.named_children[0] if len(node.named_children) > 0 else None
            
            cond_text = self.get_text(condition_node, source_bytes) if condition_node else "True"
            self.emit(f"if {cond_text}:")
            self.indent_level += 1
            
            # Find the consequence. It should be the first named child after the condition
            consequence = None
            found_cond = False
            for child in node.named_children:
                if child == condition_node:
                    found_cond = True
                    continue
                if found_cond:
                    consequence = child
                    break
            
            if consequence:
                self.visit(consequence, source_bytes)
            else:
                self.emit("pass")
            self.indent_level -= 1
            
            # Check for else
            else_idx = next((i for i, c in enumerate(node.children) if c.type == "else"), -1)
            if else_idx != -1 and else_idx + 1 < len(node.children):
                self.emit("else:")
                self.indent_level += 1
                self.visit(node.children[else_idx + 1], source_bytes)
                self.indent_level -= 1

        elif node.type == "when_expression":
            subject = next((c for c in node.children if c.type == "when_subject"), None)
            subject_text = self.get_text(subject, source_bytes) if subject else "True"
            if subject_text.startswith("(") and subject_text.endswith(")"):
                subject_text = subject_text[1:-1]
                
            body = next((c for c in node.children if c.type == "block"), None)
            if body:
                is_first = True
                for child in body.named_children:
                    if child.type == "when_entry":
                        conditions = next((c for c in child.children if c.type == "when_condition"), None)
                        cond_text = self.get_text(conditions, source_bytes) if conditions else "else"
                        
                        prefix = "if" if is_first else "elif"
                        
                        if cond_text == "else":
                            self.emit("else:")
                        else:
                            # A literal transpilation of when(x) { y -> ... } is `if x == y:`
                            self.emit(f"{prefix} {subject_text} == {cond_text}:")
                        self.indent_level += 1
                        
                        # Get the entry body which is the child after the condition
                        entry_body = None
                        found_cond = False
                        for c in child.children:
                            if c.type == "when_condition" or c.type == "else":
                                found_cond = True
                                continue
                            if found_cond and c.type not in ("->", "line_comment", "block_comment"):
                                entry_body = c
                                break
                        
                        if entry_body:
                            self.visit(entry_body, source_bytes)
                        else:
                            self.emit("pass")
                        self.indent_level -= 1
                        is_first = False
            else:
                self.emit("pass")

        elif node.type == "assignment":
            left = self.parse_expression(node.named_children[0], source_bytes) if len(node.named_children) > 0 else ""
            right_node = node.named_children[1] if len(node.named_children) > 1 else None
            
            # Check if right-hand side is a call with a lambda
            has_lambda = False
            if right_node and right_node.type in ("call_expression", "navigation_expression"):
                has_lambda = any(c.type == "lambda_literal" or c.type == "annotated_lambda" for c in right_node.children)
                
            if has_lambda:
                func_name = self.parse_expression(right_node.named_children[0] if right_node and len(right_node.named_children) > 0 else None, source_bytes)
                
                self.emit("def _lambda():")
                self.indent_level += 1
                
                # Dig down to the lambda
                lambda_node = next((c for c in right_node.children if c.type == "lambda_literal"), None)
                if not lambda_node:
                    ann_lambda = next((c for c in right_node.children if c.type == "annotated_lambda"), None)
                    if ann_lambda:
                        lambda_node = next((c for c in ann_lambda.children if c.type == "lambda_literal"), None)
                
                if not lambda_node:
                    rhs_call = next((c for c in right_node.children if c.type == "call_expression"), None)
                    if rhs_call:
                        lambda_node = next((c for c in rhs_call.children if c.type == "lambda_literal"), None)
                        if not lambda_node:
                            ann_lambda = next((c for c in rhs_call.children if c.type == "annotated_lambda"), None)
                            if ann_lambda:
                                lambda_node = next((c for c in ann_lambda.children if c.type == "lambda_literal"), None)
                
                statements_node = next((c for c in lambda_node.named_children if c.type == "statements"), None) if lambda_node else None
                children = statements_node.named_children if statements_node else (lambda_node.named_children if lambda_node else [])
                
                if children:
                    for stmt in children:
                        self.visit(stmt, source_bytes)
                else:
                    self.emit("pass")
                self.indent_level -= 1
                
                self.emit(f"{left} = {func_name}(_lambda)")
            else:
                right = self.parse_expression(right_node, source_bytes)
                self.emit(f"{left} = {right}")

        elif node.type == "for_statement":
            # Extract loop variable and iterable
            loop_var = next((c for c in node.children if c.type == "identifier" or c.type == "variable_declaration"), None)
            iterable = next((c for c in node.children if c.type == "value_arguments" or c.type == "parenthesized_expression" or c.type == "navigation_expression" or c.type == "identifier" or c.type == "call_expression"), None)
            
            # tree-sitter Kotlin sometimes puts the loop var and iterable inside parentheses
            if not loop_var and len(node.named_children) > 0:
                loop_var = node.named_children[0]
            if not iterable and len(node.named_children) > 1:
                iterable = node.named_children[1]
                
            var_text = self.get_text(loop_var, source_bytes) if loop_var else "item"
            iter_text = self.get_text(iterable, source_bytes) if iterable else "collection"
            
            if iterable and iterable.type not in ("identifier", "navigation_expression", "call_expression"):
                self.emit(f"for {var_text} in [_RAW_ITERABLE_TODO_]:  # {iter_text}")
            else:
                self.emit(f"for {var_text} in {iter_text}:")

            self.indent_level += 1
            
            # The body is the last child that is not a parenthesis or identifier
            body = node.named_children[-1] if len(node.named_children) > 0 else None
            if body and body != iterable:
                self.visit(body, source_bytes)
            else:
                self.emit("pass")
            self.indent_level -= 1

        elif node.type == "while_statement":
            condition = next((c for c in node.children if c.type == "parenthesized_expression"), None)
            cond_text = self.get_text(condition, source_bytes) if condition else "True"
            self.emit(f"while {cond_text}:")
            self.indent_level += 1
            
            body = node.named_children[-1] if len(node.named_children) > 0 else None
            if body and body != condition:
                self.visit(body, source_bytes)
            else:
                self.emit("pass")
            self.indent_level -= 1

        elif node.type == "return_statement":
            if len(node.named_children) > 0:
                expr = self.parse_expression(node.named_children[0], source_bytes)
                self.emit(f"return {expr}")
            else:
                self.emit("return")

        elif node.type in ("call_expression", "navigation_expression"):
            # Check for trailing lambda (e.g. `_uiState.update { ... }`)
            lambda_node = next((c for c in node.children if c.type == "lambda_literal"), None)
            if not lambda_node:
                rhs = next((c for c in node.children if c.type == "call_expression"), None)
                if rhs:
                    lambda_node = next((c for c in rhs.children if c.type == "lambda_literal"), None)
                
                ann_lambda = next((c for c in node.children if c.type == "annotated_lambda"), None)
                if ann_lambda:
                    lambda_node = next((c for c in ann_lambda.children if c.type == "lambda_literal"), None)

            if lambda_node:
                func_name = self.parse_expression(node.named_children[0] if len(node.named_children) > 0 else None, source_bytes)
                
                self.emit("def _lambda():")
                self.indent_level += 1
                
                statements_node = next((c for c in lambda_node.named_children if c.type == "statements"), None)
                if statements_node:
                    children = statements_node.named_children
                else:
                    children = lambda_node.named_children
                
                if children:
                    for stmt in children:
                        self.visit(stmt, source_bytes)
                else:
                    self.emit("pass")
                self.indent_level -= 1
                
                self.emit(f"{func_name}(_lambda)")
            else:
                expr = self.parse_expression(node, source_bytes)
                self.emit(expr)
            
        elif node.type == "import_list":
            for child in node.named_children:
                self.visit(child, source_bytes)
                
        elif node.type in ("import", "import_header"):
            raw_import = self.get_text(node, source_bytes)
            # Example: import kotlinx.coroutines.flow.MutableStateFlow
            if "kotlinx.coroutines.flow." in raw_import:
                symbol = raw_import.split("kotlinx.coroutines.flow.")[-1].strip()
                self.emit(f"from core.flow import {symbol}")
            elif "kotlinx.coroutines." in raw_import:
                symbol = raw_import.split("kotlinx.coroutines.")[-1].strip()
                self.emit(f"from core.coroutines import {symbol}")
            else:
                self.emit(f"# TODO_RAW_IMPORT: {raw_import}")

        elif node.type in ("package_header", "line_comment", "block_comment"):
            # skip or emit as comment
            pass
            
        else:
            # STRICT RULE: Emit TODO for unhandled node types
            raw_text = self.get_text(node, source_bytes).replace('\n', '\\n')
            self.emit(f"# TODO_UNHANDLED_KOTLIN_NODE: [{node.type}] {raw_text}")
            self.emit("pass")

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
        
    try:
        ast.parse(python_code)
    except SyntaxError as e:
        print(f"ERROR: Emitted Python is invalid! ({e})")
        
    print(f"Transpiled {kt_file} -> {out_file}")

if __name__ == "__main__":
    run()
