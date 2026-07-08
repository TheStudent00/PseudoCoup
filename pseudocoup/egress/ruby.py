import ast

class PyToRubyTranspiler(ast.NodeVisitor):
    def __init__(self):
        self.lines = []
        self.indent_level = 0
        self.in_class = False
        self.current_class = None

    def add_line(self, text):
        if text.strip() == "":
            self.lines.append("")
        else:
            self.lines.append("    " * self.indent_level + text)

    def visit_Module(self, node):
        for stmt in node.body:
            self.visit(stmt)

    def visit_Import(self, node):
        pass

    def visit_ImportFrom(self, node):
        pass

    def visit_ClassDef(self, node):
        self.in_class = True
        self.current_class = node.name
        self.add_line(f"class {node.name}")
        self.indent_level += 1
        
        # Collect fields for attr_accessor
        fields = []
        for stmt in node.body:
            if isinstance(stmt, ast.AnnAssign) and isinstance(stmt.target, ast.Name):
                fields.append(stmt.target.id)
                
        if fields:
            self.add_line(f"attr_accessor :{', :'.join(fields)}")
            self.add_line("")
            
        for stmt in node.body:
            if not isinstance(stmt, ast.AnnAssign):
                self.visit(stmt)
                
        self.indent_level -= 1
        self.add_line("end")
        self.add_line("")
        self.in_class = False
        self.current_class = None

    def visit_FunctionDef(self, node):
        method_name = node.name
        if method_name == "__init__": method_name = "initialize"
        
        params = []
        for arg in node.args.args:
            if arg.arg == "self": continue
            params.append(arg.arg)
            
        param_str = f"({', '.join(params)})" if params else ""
        
        if method_name == "main" and not self.in_class:
            self.add_line(f"def {method_name}{param_str}")
        else:
            self.add_line(f"def {method_name}{param_str}")
            
        self.indent_level += 1
        old_in_class = self.in_class
        self.in_class = False
        for stmt in node.body:
            self.visit(stmt)
        self.in_class = old_in_class
        self.indent_level -= 1
        self.add_line("end")
        self.add_line("")

    def visit_Assign(self, node):
        targets = [self.expr_to_str(t) for t in node.targets]
        val = self.expr_to_str(node.value)
        for t in targets:
            self.add_line(f"{t} = {val}")

    def visit_AnnAssign(self, node):
        if not self.in_class:
            t = self.expr_to_str(node.target)
            if node.value:
                val = self.expr_to_str(node.value)
                self.add_line(f"{t} = {val}")

    def visit_Expr(self, node):
        val = self.expr_to_str(node.value)
        if val: self.add_line(val)

    def visit_Return(self, node):
        if node.value:
            self.add_line(f"return {self.expr_to_str(node.value)}")
        else:
            self.add_line("return")

    def visit_If(self, node):
        cond = self.expr_to_str(node.test)
        if cond == '__name__ == "__main__"': return
        
        self.add_line(f"if {cond}")
        self.indent_level += 1
        for stmt in node.body: self.visit(stmt)
        self.indent_level -= 1
        
        if node.orelse:
            self.add_line("else")
            self.indent_level += 1
            for stmt in node.orelse: self.visit(stmt)
            self.indent_level -= 1
            
        self.add_line("end")

    def visit_While(self, node):
        cond = self.expr_to_str(node.test)
        self.add_line(f"while {cond}")
        self.indent_level += 1
        for stmt in node.body: self.visit(stmt)
        self.indent_level -= 1
        self.add_line("end")

    def visit_Break(self, node):
        self.add_line("break")

    def visit_Continue(self, node):
        self.add_line("next")

    def visit_Try(self, node):
        self.add_line("begin")
        self.indent_level += 1
        for stmt in node.body: self.visit(stmt)
        self.indent_level -= 1
        
        for handler in node.handlers:
            err = handler.name or "e"
            self.add_line(f"rescue StandardError => {err}")
            self.indent_level += 1
            for stmt in handler.body: self.visit(stmt)
            self.indent_level -= 1
            
        self.add_line("end")

    def visit_Raise(self, node):
        if isinstance(node.exc, ast.Call):
            if isinstance(node.exc.func, ast.Name) and node.exc.func.id == "Exception":
                if node.exc.args:
                    msg = self.expr_to_str(node.exc.args[0])
                    self.add_line(f"raise StandardError, {msg}")
                    return
        self.add_line(f"raise {self.expr_to_str(node.exc)}")

    def expr_to_str(self, node):
        if isinstance(node, ast.Name):
            if node.id == "True": return "true"
            if node.id == "False": return "false"
            if node.id == "None": return "nil"
            return node.id
        elif isinstance(node, ast.Constant):
            if isinstance(node.value, str):
                return f'"{node.value}"'
            if node.value is None: return "nil"
            if node.value is True: return "true"
            if node.value is False: return "false"
            return str(node.value)
        elif isinstance(node, ast.Attribute):
            left = self.expr_to_str(node.value)
            # if left == "self", we need to emit self.field
            return f"{left}.{node.attr}"
        elif isinstance(node, ast.Call):
            func = self.expr_to_str(node.func)
            args = [self.expr_to_str(arg) for arg in node.args]
            if func == "print":
                return f"puts {args[0]}"
            if func == "len":
                return f"{args[0]}.length"
            if func == "str":
                return f"{args[0]}.to_s"
            if func == "dict":
                if isinstance(node.args[0], ast.List):
                    items = []
                    for elt in node.args[0].elts:
                        if isinstance(elt, ast.Tuple) and len(elt.elts) == 2:
                            k = self.expr_to_str(elt.elts[0])
                            v = self.expr_to_str(elt.elts[1])
                            items.append(f"{k} => {v}")
                    return f"{{{', '.join(items)}}}"
                return "{}"
            if func[0].isupper():
                return f"{func}.new({', '.join(args)})"
            return f"{func}({', '.join(args)})"
        elif isinstance(node, ast.UnaryOp):
            op = "-" if isinstance(node.op, ast.USub) else ("not " if isinstance(node.op, ast.Not) else "+")
            val = self.expr_to_str(node.operand)
            return f"{op}{val}"
        elif isinstance(node, ast.BinOp):
            left = self.expr_to_str(node.left)
            right = self.expr_to_str(node.right)
            op = self.binop_to_str(node.op)
            return f"({left}) {op} ({right})"
        elif isinstance(node, ast.Compare):
            left = self.expr_to_str(node.left)
            op = self.cmpop_to_str(node.ops[0])
            right = self.expr_to_str(node.comparators[0])
            if op == "in":
                return f"{right}.has_key?({left})"
            if op == "not in":
                return f"!{right}.has_key?({left})"
            if right == "nil":
                if op == "==": return f"{left}.nil?"
                if op == "!=": return f"!{left}.nil?"
            return f"{left} {op} {right}"
        elif isinstance(node, ast.List):
            items = [self.expr_to_str(elt) for elt in node.elts]
            return f"[{', '.join(items)}]"
        elif isinstance(node, ast.Dict):
            items = []
            for k, v in zip(node.keys, node.values):
                items.append(f"{self.expr_to_str(k)} => {self.expr_to_str(v)}")
            return f"{{{', '.join(items)}}}"
        elif isinstance(node, ast.Subscript):
            val = self.expr_to_str(node.value)
            slice_ = self.expr_to_str(node.slice)
            return f"{val}[{slice_}]"
        elif isinstance(node, ast.Tuple):
            return f"[{', '.join([self.expr_to_str(e) for e in node.elts])}]"
        return ""

    def binop_to_str(self, op):
        if isinstance(op, ast.Add): return "+"
        if isinstance(op, ast.Sub): return "-"
        if isinstance(op, ast.Mult): return "*"
        if isinstance(op, ast.Div): return "/"
        if isinstance(op, ast.Mod): return "%"
        return "+"

    def cmpop_to_str(self, op):
        if isinstance(op, ast.Eq): return "=="
        if isinstance(op, ast.NotEq): return "!="
        if isinstance(op, ast.Lt): return "<"
        if isinstance(op, ast.LtE): return "<="
        if isinstance(op, ast.Gt): return ">"
        if isinstance(op, ast.GtE): return ">="
        if isinstance(op, ast.In): return "in"
        if isinstance(op, ast.Is): return "=="
        if isinstance(op, ast.IsNot): return "!="
        return "=="

def transpile(code: str) -> str:
    tree = ast.parse(code)
    transpiler = PyToRubyTranspiler()
    transpiler.visit(tree)
    
    # Add ruby run block
    transpiler.lines.append("if __FILE__ == $0")
    transpiler.lines.append("    main()")
    transpiler.lines.append("end")
    
    return "\n".join(transpiler.lines)
