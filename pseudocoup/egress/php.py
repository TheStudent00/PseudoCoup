import ast

class PyToPhpTranspiler(ast.NodeVisitor):
    def __init__(self):
        self.lines = []
        self.indent_level = 0
        self.in_class = False

    def add_line(self, line):
        self.lines.append("    " * self.indent_level + line)

    def expr_to_str(self, node):
        if isinstance(node, ast.Name):
            if node.id == "self":
                return "$this"
            return f"${node.id}"
        elif isinstance(node, ast.Constant):
            if isinstance(node.value, str):
                return f'"{node.value}"'
            if node.value is None:
                return "null"
            if isinstance(node.value, bool):
                return "true" if node.value else "false"
            return str(node.value)
        elif isinstance(node, ast.Attribute):
            return f"{self.expr_to_str(node.value)}->{node.attr}"
        elif isinstance(node, ast.Subscript):
            return f"{self.expr_to_str(node.value)}[{self.expr_to_str(node.slice)}]"
        elif isinstance(node, ast.Call):
            func = self.expr_to_str(node.func)
            args = [self.expr_to_str(arg) for arg in node.args]
            if func == "$print":
                return f"echo {args[0]} . \"\\n\""
            if func == "$len":
                return f"count({args[0]})"
            if func == "$str":
                return f"(string){args[0]}"
            if func == "$dict":
                if isinstance(node.args[0], ast.List):
                    items = []
                    for elt in node.args[0].elts:
                        if isinstance(elt, ast.Tuple) and len(elt.elts) == 2:
                            k = self.expr_to_str(elt.elts[0])
                            v = self.expr_to_str(elt.elts[1])
                            items.append(f"{k} => {v}")
                    return f"[{', '.join(items)}]"
                return "[]"
            
            # Constructor calls
            if func.startswith("$") and func[1].isupper():
                return f"new {func[1:]}({', '.join(args)})"
                
            if "->" in func:
                return f"{func}({', '.join(args)})"
                
            if func.startswith("$"):
                return f"{func[1:]}({', '.join(args)})"
            return f"{func}({', '.join(args)})"
        elif isinstance(node, ast.BinOp):
            left = self.expr_to_str(node.left)
            right = self.expr_to_str(node.right)
            op = self.op_to_str(node.op)
            if op == "+" and (isinstance(node.left, ast.Constant) and isinstance(node.left.value, str) or isinstance(node.right, ast.Constant) and isinstance(node.right.value, str) or "string" in left or "string" in right):
                op = "."
            return f"({left}) {op} ({right})"
        elif isinstance(node, ast.Compare):
            left = self.expr_to_str(node.left)
            op = self.cmpop_to_str(node.ops[0])
            right = self.expr_to_str(node.comparators[0])
            
            if op == "in" and isinstance(node.comparators[0], ast.Attribute):
                # array_key_exists
                return f"array_key_exists({left}, {right})"
                
            return f"{left} {op} {right}"
        elif isinstance(node, ast.UnaryOp):
            op = "-" if isinstance(node.op, ast.USub) else ("!" if isinstance(node.op, ast.Not) else "+")
            val = self.expr_to_str(node.operand)
            return f"{op}{val}"
        elif isinstance(node, ast.List):
            elts = [self.expr_to_str(elt) for elt in node.elts]
            return f"[{', '.join(elts)}]"
        elif isinstance(node, ast.Tuple):
            elts = [self.expr_to_str(elt) for elt in node.elts]
            return f"[{', '.join(elts)}]"
        elif isinstance(node, ast.Dict):
            items = []
            for k, v in zip(node.keys, node.values):
                items.append(f"{self.expr_to_str(k)} => {self.expr_to_str(v)}")
            return f"[{', '.join(items)}]"
        return ""

    def op_to_str(self, op):
        if isinstance(op, ast.Add): return "+"
        elif isinstance(op, ast.Sub): return "-"
        elif isinstance(op, ast.Mult): return "*"
        elif isinstance(op, ast.Div): return "/"
        elif isinstance(op, ast.Mod): return "%"
        return "+"

    def cmpop_to_str(self, op):
        if isinstance(op, ast.Eq): return "=="
        elif isinstance(op, ast.NotEq): return "!="
        elif isinstance(op, ast.Lt): return "<"
        elif isinstance(op, ast.LtE): return "<="
        elif isinstance(op, ast.Gt): return ">"
        elif isinstance(op, ast.GtE): return ">="
        elif isinstance(op, ast.Is): return "==="
        elif isinstance(op, ast.IsNot): return "!=="
        elif isinstance(op, ast.In): return "in"
        return "=="

    def visit_ClassDef(self, node):
        self.add_line(f"class {node.name} {{")
        self.indent_level += 1
        self.in_class = True
        
        # Gather attributes for PHP properties
        attrs = []
        for stmt in node.body:
            if isinstance(stmt, ast.FunctionDef) and stmt.name == "__init__":
                for s in stmt.body:
                    if isinstance(s, ast.Assign) and isinstance(s.targets[0], ast.Attribute):
                        attrs.append(s.targets[0].attr)
        
        for attr in attrs:
            self.add_line(f"public ${attr};")
            
        if attrs:
            self.add_line("")
            
        for stmt in node.body:
            self.visit(stmt)
            
        self.in_class = False
        self.indent_level -= 1
        self.add_line("}")
        self.add_line("")

    def visit_FunctionDef(self, node):
        method_name = node.name
        if method_name == "__init__": method_name = "__construct"
        
        params = []
        for arg in node.args.args:
            if arg.arg == "self": continue
            params.append(f"${arg.arg}")
            
        param_str = f"({', '.join(params)})"
        
        if method_name == "main" and not self.in_class:
            self.add_line(f"function {method_name}{param_str} {{")
        else:
            self.add_line(f"public function {method_name}{param_str} {{")
            
        self.indent_level += 1
        old_in_class = self.in_class
        self.in_class = False
        for stmt in node.body:
            self.visit(stmt)
        self.in_class = old_in_class
        self.indent_level -= 1
        self.add_line("}")
        self.add_line("")

    def visit_If(self, node):
        cond = self.expr_to_str(node.test)
        if cond == '$__name__ == "__main__"': return
        
        self.add_line(f"if ({cond}) {{")
        self.indent_level += 1
        for stmt in node.body: self.visit(stmt)
        self.indent_level -= 1
        
        if node.orelse:
            self.add_line("} else {")
            self.indent_level += 1
            for stmt in node.orelse: self.visit(stmt)
            self.indent_level -= 1
            
        self.add_line("}")

    def visit_While(self, node):
        cond = self.expr_to_str(node.test)
        self.add_line(f"while ({cond}) {{")
        self.indent_level += 1
        for stmt in node.body: self.visit(stmt)
        self.indent_level -= 1
        self.add_line("}")

    def visit_Assign(self, node):
        t = self.expr_to_str(node.targets[0])
        v = self.expr_to_str(node.value)
        self.add_line(f"{t} = {v};")
        
    def visit_AnnAssign(self, node):
        if not self.in_class:
            t = self.expr_to_str(node.target)
            if node.value:
                val = self.expr_to_str(node.value)
                self.add_line(f"{t} = {val};")

    def visit_Expr(self, node):
        val = self.expr_to_str(node.value)
        if val:
            self.add_line(f"{val};")

    def visit_Return(self, node):
        if node.value:
            val = self.expr_to_str(node.value)
            self.add_line(f"return {val};")
        else:
            self.add_line("return;")

    def visit_Break(self, node):
        self.add_line("break;")
        
    def visit_Continue(self, node):
        self.add_line("continue;")
        
    def visit_Pass(self, node):
        pass

    def visit_Try(self, node):
        self.add_line("try {")
        self.indent_level += 1
        for stmt in node.body: self.visit(stmt)
        self.indent_level -= 1
        
        if node.handlers:
            ex_name = node.handlers[0].name or "e"
            self.add_line(f"}} catch (Exception ${ex_name}) {{")
            self.indent_level += 1
            for stmt in node.handlers[0].body: self.visit(stmt)
            self.indent_level -= 1
            
        self.add_line("}")

    def visit_Raise(self, node):
        ex = self.expr_to_str(node.exc)
        self.add_line(f"throw {ex};")


def transpile(code: str) -> str:
    tree = ast.parse(code)
    transpiler = PyToPhpTranspiler()
    transpiler.lines.append("<?php")
    transpiler.lines.append("")
    for node in tree.body:
        transpiler.visit(node)
        
    transpiler.lines.append("if (basename(__FILE__) == basename($_SERVER['PHP_SELF'])) {")
    transpiler.lines.append("    main();")
    transpiler.lines.append("}")
    transpiler.lines.append("?>")
    return "\n".join(transpiler.lines)
