import ast
import json

class PythonToSwiftTranspiler(ast.NodeVisitor):
    def __init__(self, ledger):
        self.ledger = ledger
        self.lines = [
            "import Foundation",
            ""
        ]
        self.indent_level = 0
        self.current_class = None

    def add_line(self, text):
        if text.strip() == "":
            self.lines.append("")
        else:
            self.lines.append("    " * self.indent_level + text)

    def map_type(self, py_type_node):
        if isinstance(py_type_node, ast.Name):
            py_type = py_type_node.id
            if py_type == "int": return "Int"
            if py_type == "str": return "String"
            if py_type == "bool": return "Bool"
            if py_type == "float": return "Double"
            if py_type == "None": return "Void"
            return py_type
        elif isinstance(py_type_node, ast.Subscript):
            base_type = py_type_node.value.id
            if base_type == "List":
                inner = self.map_type(py_type_node.slice)
                return f"[{inner}]"
            elif base_type == "Dict":
                inner1 = self.map_type(py_type_node.slice.elts[0])
                inner2 = self.map_type(py_type_node.slice.elts[1])
                return f"[{inner1}: {inner2}]"
            elif base_type == "Optional":
                return f"{self.map_type(py_type_node.slice)}?"
        return "Any"

    def visit_ClassDef(self, node):
        self.current_class = node.name
        self.add_line(f"class {node.name} {{")
        self.indent_level += 1
        
        # Collect properties from __init__
        self.properties = []
        for body_node in node.body:
            if isinstance(body_node, ast.FunctionDef) and body_node.name == "__init__":
                for stmt in body_node.body:
                    if isinstance(stmt, ast.Assign):
                        for target in stmt.targets:
                            if isinstance(target, ast.Attribute) and isinstance(target.value, ast.Name) and target.value.id == "self":
                                # Try to infer type
                                p_type = "Any"
                                if isinstance(stmt.value, ast.List): p_type = "[Any]"
                                elif isinstance(stmt.value, ast.Dict): p_type = "[Any: Any]"
                                else:
                                    for arg in body_node.args.args:
                                        if arg.arg == target.attr and arg.annotation:
                                            p_type = self.map_type(arg.annotation)
                                            break
                                    if p_type == "Any":
                                        if isinstance(stmt.value, ast.Constant):
                                            if isinstance(stmt.value.value, int): p_type = "Int"
                                            elif isinstance(stmt.value.value, str): p_type = "String"
                                            elif isinstance(stmt.value.value, bool): p_type = "Bool"
                                self.properties.append((target.attr, p_type))
        
        for name, p_type in self.properties:
            # Note: in Swift, properties must be initialized. We'll use implicit unwrapped optional if not explicitly handled, but for our transpiler, we can just say `var name: Type!`
            self.add_line(f"var {name}: {p_type}!")
        if self.properties:
            self.add_line("")

        for body_node in node.body:
            if isinstance(body_node, ast.AnnAssign): continue
            self.visit(body_node)
            
        self.indent_level -= 1
        self.add_line("}")
        self.add_line("")
        self.current_class = None

    def visit_FunctionDef(self, node):
        if node.name == "main":
            return

        is_init = node.name == "__init__"
        method_name = "init" if is_init else node.name
        
        params = []
        for arg in node.args.args:
            if arg.arg == "self": continue
            ptype = self.map_type(arg.annotation) if arg.annotation else "Any"
            # In Swift, parameter names are required by default. We use `_` to allow calling without parameter names like Python, though Python requires names for kwargs. We'll just emit normal parameters.
            params.append(f"_ {arg.arg}: {ptype}")
            
        ret_type = "" if is_init else (self.map_type(node.returns) if node.returns else "Void")
        
        if is_init:
            decl = f"{method_name}({', '.join(params)}) throws"
        else:
            ret_clause = f" -> {ret_type}" if ret_type and ret_type != "Void" else ""
            decl = f"func {method_name}({', '.join(params)}) throws{ret_clause}"
            
        self.add_line(decl)
        self.add_line("{")
        self.indent_level += 1
        for stmt in node.body:
            self.visit(stmt)
        self.indent_level -= 1
        self.add_line("}")
        self.add_line("")

    def visit_Assign(self, node):
        target = self.expr_to_str(node.targets[0])
        val = self.expr_to_str(node.value)
        
        if isinstance(node.targets[0], ast.Name):
            # In Swift, we need `var` or `let`. We'll just emit `var`.
            self.add_line(f"var {target} = {val}")
        else:
            self.add_line(f"{target} = {val}")

    def visit_AnnAssign(self, node):
        target = self.expr_to_str(node.target)
        val = self.expr_to_str(node.value) if node.value else "nil"
        t_str = self.map_type(node.annotation)
        self.add_line(f"var {target}: {t_str} = {val}")

    def visit_AugAssign(self, node):
        target = self.expr_to_str(node.target)
        val = self.expr_to_str(node.value)
        op = self.op_to_str(node.op)
        self.add_line(f"{target} {op}= {val}")

    def visit_Expr(self, node):
        s = self.expr_to_str(node.value)
        self.add_line(s)

    def visit_If(self, node):
        cond = self.expr_to_str(node.test)
        self.add_line(f"if {cond} {{")
        self.indent_level += 1
        for stmt in node.body:
            self.visit(stmt)
        self.indent_level -= 1
        self.add_line("}")
        if node.orelse:
            self.add_line("else {")
            self.indent_level += 1
            for stmt in node.orelse:
                self.visit(stmt)
            self.indent_level -= 1
            self.add_line("}")

    def visit_While(self, node):
        cond = self.expr_to_str(node.test)
        self.add_line(f"while {cond} {{")
        self.indent_level += 1
        for stmt in node.body:
            self.visit(stmt)
        self.indent_level -= 1
        self.add_line("}")

    def visit_Break(self, node):
        self.add_line("break")
        
    def visit_Continue(self, node):
        self.add_line("continue")

    def visit_Return(self, node):
        if node.value:
            self.add_line(f"return {self.expr_to_str(node.value)}")
        else:
            self.add_line("return")

    def visit_Raise(self, node):
        exc = self.expr_to_str(node.exc) if node.exc else "RuntimeError()"
        self.add_line(f"throw {exc}")

    def visit_Try(self, node):
        self.add_line("do {")
        self.indent_level += 1
        for stmt in node.body:
            self.visit(stmt)
        self.indent_level -= 1
        self.add_line("}")
        for handler in node.handlers:
            n = handler.name if handler.name else "e"
            self.add_line(f"catch let {n} {{")
            self.indent_level += 1
            for stmt in handler.body:
                self.visit(stmt)
            self.indent_level -= 1
            self.add_line("}")

    def op_to_str(self, op):
        if isinstance(op, ast.Add): return "+"
        if isinstance(op, ast.Sub): return "-"
        if isinstance(op, ast.Mult): return "*"
        if isinstance(op, ast.Div): return "/"
        if isinstance(op, ast.Mod): return "%"
        if isinstance(op, ast.Eq): return "=="
        if isinstance(op, ast.NotEq): return "!="
        if isinstance(op, ast.Lt): return "<"
        if isinstance(op, ast.LtE): return "<="
        if isinstance(op, ast.Gt): return ">"
        if isinstance(op, ast.GtE): return ">="
        if isinstance(op, ast.Is): return "=="
        if isinstance(op, ast.IsNot): return "!="
        return "?"

    def expr_to_str(self, node):
        if isinstance(node, ast.Name):
            if node.id == "self": return "self"
            if node.id == "None": return "nil"
            if node.id == "True": return "true"
            if node.id == "False": return "false"
            return node.id
        elif isinstance(node, ast.Constant):
            if isinstance(node.value, str): return f'"{node.value}"'
            if node.value is None: return "nil"
            if isinstance(node.value, bool): return "true" if node.value else "false"
            return str(node.value)
        elif isinstance(node, ast.Attribute):
            val = self.expr_to_str(node.value)
            return f"{val}.{node.attr}"
        elif isinstance(node, ast.Call):
            func = self.expr_to_str(node.func)
            args = [self.expr_to_str(a) for a in node.args]
            
            if func == "print":
                return "print(" + ", ".join(args) + ")"
            if func == "str":
                return f"String({args[0]})"
            if func == "len":
                return f"{args[0]}.count"
                
            if isinstance(node.func, ast.Name) and node.func.id[0].isupper():
                return f"{func}({', '.join(args)})" # no `new` in Swift
                
            return f"try {func}({', '.join(args)})"
        elif isinstance(node, ast.BinOp):
            return f"({self.expr_to_str(node.left)}) {self.op_to_str(node.op)} ({self.expr_to_str(node.right)})"
        elif isinstance(node, ast.UnaryOp):
            if isinstance(node.op, ast.USub): return f"-{self.expr_to_str(node.operand)}"
            if isinstance(node.op, ast.Not): return f"!{self.expr_to_str(node.operand)}"
            return f"{self.expr_to_str(node.operand)}"
        elif isinstance(node, ast.Compare):
            if isinstance(node.ops[0], ast.In):
                return f"{self.expr_to_str(node.comparators[0])}.keys.contains({self.expr_to_str(node.left)})"
            return f"{self.expr_to_str(node.left)} {self.op_to_str(node.ops[0])} {self.expr_to_str(node.comparators[0])}"
        elif isinstance(node, ast.List):
            elts = [self.expr_to_str(e) for e in node.elts]
            return f"[{', '.join(elts)}]"
        elif isinstance(node, ast.Dict):
            pairs = []
            for k, v in zip(node.keys, node.values):
                pairs.append(f"{self.expr_to_str(k)}: {self.expr_to_str(v)}")
            return f"[{', '.join(pairs)}]"
        elif isinstance(node, ast.Subscript):
            return f"{self.expr_to_str(node.value)}[{self.expr_to_str(node.slice)}]"
        return "/* unhandled expr */"

def transpile(code: str) -> str:
    tree = ast.parse(code)
    class DummyLedger:
        def log(self, *args): pass
    transpiler = PythonToSwiftTranspiler(DummyLedger())
    
    global_stmts = []
    
    for node in tree.body:
        if isinstance(node, ast.If) and isinstance(node.test, ast.Compare):
            if getattr(node.test.left, "id", None) == "__name__":
                continue
                
        if isinstance(node, (ast.ClassDef, ast.FunctionDef, ast.Import, ast.ImportFrom)):
            if isinstance(node, ast.FunctionDef) and node.name == "main":
                global_stmts.append(node)
            else:
                transpiler.visit(node)
        else:
            global_stmts.append(node)
            
    # Wrap global statements
    transpiler.add_line("func main() throws {")
    transpiler.indent_level += 1
    for stmt in global_stmts:
        if isinstance(stmt, ast.FunctionDef) and stmt.name == "main":
            for sub_stmt in stmt.body:
                transpiler.visit(sub_stmt)
        else:
            transpiler.visit(stmt)
    transpiler.indent_level -= 1
    transpiler.add_line("}")
    transpiler.add_line("")
    transpiler.add_line("do {")
    transpiler.indent_level += 1
    transpiler.add_line("try main()")
    transpiler.indent_level -= 1
    transpiler.add_line("} catch {}")
    
    return "\n".join(transpiler.lines)
