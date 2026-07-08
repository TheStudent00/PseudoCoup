import ast
import json
import os

class PythonToGoTranspiler(ast.NodeVisitor):
    def __init__(self):
        self.lines = []
        self.indent_level = 0
        self.current_class = None
        self.current_method = None
        self.properties = []

    def add_line(self, text):
        if text.strip() == "":
            self.lines.append("")
        else:
            self.lines.append("    " * self.indent_level + text)

    def map_type(self, node):
        if isinstance(node, ast.Name):
            if node.id == "int": return "int"
            if node.id == "str": return "string"
            if node.id == "float": return "float64"
            if node.id == "bool": return "bool"
            if node.id == "None": return ""
            return f"*{node.id}" # Custom classes default to pointers in Go
        elif isinstance(node, ast.Constant) and node.value is None:
            return ""
        elif isinstance(node, ast.Subscript):
            val_id = getattr(node.value, "id", "")
            if val_id == "List":
                inner = self.map_type(node.slice)
                return f"[]{inner}"
            elif val_id == "Dict":
                key_type = self.map_type(node.slice.elts[0])
                val_type = self.map_type(node.slice.elts[1])
                return f"map[{key_type}]{val_type}"
            elif val_id == "Optional":
                inner = self.map_type(node.slice)
                return inner
        return "any"

    def visit_ClassDef(self, node):
        self.current_class = node.name
        
        self.properties = []
        init_method = None
        for child in node.body:
            if isinstance(child, ast.FunctionDef) and child.name == "__init__":
                init_method = child
                # Extract properties from __init__ type hints
                for stmt in child.body:
                    if isinstance(stmt, ast.AnnAssign) and isinstance(stmt.target, ast.Attribute):
                        prop_name = stmt.target.attr
                        prop_type = self.map_type(stmt.annotation)
                        self.properties.append({"name": prop_name, "type": prop_type})
        
        # Write Go Struct
        self.add_line(f"type {self.current_class} struct {{")
        self.indent_level += 1
        for p in self.properties:
            self.add_line(f"{p['name']} {p['type']}")
        self.indent_level -= 1
        self.add_line("}")
        self.add_line("")
            
        # Write Go Constructor
        if init_method:
            self.current_method = "__init__"
            params = []
            for arg in init_method.args.args:
                if arg.arg == "self": continue
                go_type = self.map_type(arg.annotation)
                params.append(f"{arg.arg} {go_type}")
                
            self.add_line(f"func New{self.current_class}({', '.join(params)}) *{self.current_class} {{")
            self.indent_level += 1
            
            self.add_line(f"f := &{self.current_class}{{}}")
            for stmt in init_method.body:
                if isinstance(stmt, ast.AnnAssign):
                    target = self.get_expr_str(stmt.target)
                    val = self.get_expr_str(stmt.value)
                    self.add_line(f"{target} = {val}")
                elif isinstance(stmt, ast.Assign):
                    target = self.get_expr_str(stmt.targets[0])
                    val = self.get_expr_str(stmt.value)
                    self.add_line(f"{target} = {val}")
                    
            self.add_line(f"return f")
            self.indent_level -= 1
            self.add_line("}")
            self.add_line("")
            self.current_method = None
            
        # Write other methods
        for body_node in node.body:
            if isinstance(body_node, ast.FunctionDef) and body_node.name != "__init__":
                self.visit(body_node)
                
        self.current_class = None

    def visit_FunctionDef(self, node):
        self.current_method = node.name
        params = []
        for arg in node.args.args:
            if arg.arg == "self": continue
            go_type = self.map_type(arg.annotation)
            params.append(f"{arg.arg} {go_type}")
            
        ret_type = ""
        if node.returns:
            ret_type = self.map_type(node.returns)
                
        ret_str = f" {ret_type}" if ret_type else ""
        
        m_name = node.name[0].upper() + node.name[1:]
        
        # If it's main, it's a top level function
        if node.name == "main":
            self.add_line(f"func main(){ret_str} {{")
        else:
            rcvr = f"(f *{self.current_class})"
            self.add_line(f"func {rcvr} {m_name}({', '.join(params)}){ret_str} {{")
            
        self.indent_level += 1
        for body_node in node.body:
            self.visit(body_node)
        self.indent_level -= 1
        self.add_line("}")
        self.add_line("")
        self.current_method = None

    def visit_AnnAssign(self, node):
        if self.current_method == "__init__" and isinstance(node.target, ast.Attribute):
            pass # handled in constructor explicitly
        else:
            if isinstance(node.target, ast.Name):
                target = node.target.id
                if node.value:
                    val = self.get_expr_str(node.value)
                    self.add_line(f"{target} := {val}")
            elif isinstance(node.target, ast.Attribute):
                target = self.get_expr_str(node.target)
                if node.value:
                    val = self.get_expr_str(node.value)
                    self.add_line(f"{target} = {val}")

    def visit_Assign(self, node):
        target = self.get_expr_str(node.targets[0])
        value = self.get_expr_str(node.value)
        self.add_line(f"{target} = {value}")

    def visit_While(self, node):
        cond = self.get_expr_str(node.test)
        self.add_line(f"for {cond} {{")
        self.indent_level += 1
        for stmt in node.body:
            self.visit(stmt)
        self.indent_level -= 1
        self.add_line("}")

    def visit_If(self, node):
        cond = self.get_expr_str(node.test)
        self.add_line(f"if {cond} {{")
        self.indent_level += 1
        for stmt in node.body:
            self.visit(stmt)
        self.indent_level -= 1
        if node.orelse:
            self.add_line("} else {")
            self.indent_level += 1
            for stmt in node.orelse:
                self.visit(stmt)
            self.indent_level -= 1
        self.add_line("}")

    def visit_Break(self, node):
        self.add_line("break")

    def visit_Continue(self, node):
        self.add_line("continue")

    def visit_Try(self, node):
        self.add_line("func() {")
        self.indent_level += 1
        self.add_line("defer func() {")
        self.indent_level += 1
        self.add_line("if _err := recover(); _err != nil {")
        self.indent_level += 1
        for handler in node.handlers:
            for stmt in handler.body:
                self.visit(stmt)
        self.indent_level -= 1
        self.add_line("}")
        self.indent_level -= 1
        self.add_line("}()")
        
        for stmt in node.body:
            self.visit(stmt)
            
        self.indent_level -= 1
        self.add_line("}()")

    def visit_Raise(self, node):
        val = self.get_expr_str(node.exc)
        self.add_line(f"panic({val})")

    def visit_Return(self, node):
        if node.value:
            val = self.get_expr_str(node.value)
            self.add_line(f"return {val}")
        else:
            self.add_line("return")

    def visit_Expr(self, node):
        expr = self.get_expr_str(node.value)
        self.add_line(f"{expr}")

    def get_expr_str(self, expr_node):
        if isinstance(expr_node, ast.Attribute):
            val = self.get_expr_str(expr_node.value)
            attr = expr_node.attr
            if val == "f":
                return f"f.{attr}"
            return f"{val}.{attr}"
        elif isinstance(expr_node, ast.Name):
            if expr_node.id == "self":
                return "f"
            return expr_node.id
        elif isinstance(expr_node, ast.Constant):
            if isinstance(expr_node.value, str):
                return f'"{expr_node.value}"'
            elif expr_node.value is None:
                return "nil"
            return str(expr_node.value)
        elif isinstance(expr_node, ast.BinOp):
            left = self.get_expr_str(expr_node.left)
            right = self.get_expr_str(expr_node.right)
            op_map = {ast.Add: "+", ast.Sub: "-", ast.Mult: "*", ast.Div: "/", ast.Mod: "%"}
            op = op_map.get(type(expr_node.op), "?")
            return f"{left} {op} {right}"
        elif isinstance(expr_node, ast.Compare):
            left = self.get_expr_str(expr_node.left)
            op_map = {ast.Eq: "==", ast.Lt: "<", ast.Gt: ">", ast.NotEq: "!=", ast.LtE: "<=", ast.GtE: ">=", ast.Is: "==", ast.IsNot: "!=", ast.In: "in"}
            op = op_map[type(expr_node.ops[0])]
            right = self.get_expr_str(expr_node.comparators[0])
            
            if op == "in":
                return f"mapContains({right}, {left})"
            if op == "==" and right == "nil":
                return f"{left} == nil"
            if op == "!=" and right == "nil":
                return f"{left} != nil"
                
            return f"{left} {op} {right}"
        elif isinstance(expr_node, ast.UnaryOp):
            if isinstance(expr_node.op, ast.USub): op = "-"
            elif isinstance(expr_node.op, ast.UAdd): op = "+"
            elif isinstance(expr_node.op, ast.Not): op = "!"
            else: op = ""
            val = self.get_expr_str(expr_node.operand)
            return f"{op}{val}"
        elif isinstance(expr_node, ast.Call):
            if isinstance(expr_node.func, ast.Attribute):
                val = self.get_expr_str(expr_node.func.value)
                attr = expr_node.func.attr
                attr = attr[0].upper() + attr[1:]
                func_name = f"{val}.{attr}"
            else:
                func_name = self.get_expr_str(expr_node.func)
            
            if func_name == "print":
                args = [self.get_expr_str(a) for a in expr_node.args]
                return f"fmt.Println({', '.join(args)})"
            if func_name == "str":
                arg = self.get_expr_str(expr_node.args[0])
                return f'fmt.Sprintf("%v", {arg})'
            if func_name == "len":
                arg = self.get_expr_str(expr_node.args[0])
                return f'len({arg})'
            if func_name == "ValueError":
                arg = self.get_expr_str(expr_node.args[0])
                return f'fmt.Errorf({arg})'
                
            args = [self.get_expr_str(a) for a in expr_node.args]
            # Constructing new objects in Go
            if func_name in ["Forest", "Fox"]:
                return f"New{func_name}({', '.join(args)})"
            
            return f"{func_name}({', '.join(args)})"
        elif isinstance(expr_node, ast.List):
            elts = [self.get_expr_str(e) for e in expr_node.elts]
            t = "any"
            if expr_node.elts:
                if isinstance(expr_node.elts[0], ast.Constant):
                    if isinstance(expr_node.elts[0].value, str): t = "string"
                    elif isinstance(expr_node.elts[0].value, int): t = "int"
            return f"[]{t}{{{', '.join(elts)}}}"
        elif isinstance(expr_node, ast.Dict):
            keys = [self.get_expr_str(k) for k in expr_node.keys]
            vals = [self.get_expr_str(v) for v in expr_node.values]
            kt = "any"
            if expr_node.keys and isinstance(expr_node.keys[0], ast.Constant) and isinstance(expr_node.keys[0].value, str): kt = "string"
            vt = "any"
            if expr_node.values and isinstance(expr_node.values[0], ast.Constant) and isinstance(expr_node.values[0].value, int): vt = "int"
            pairs = [f"{k}: {v}" for k, v in zip(keys, vals)]
            return f"map[{kt}]{vt}{{{', '.join(pairs)}}}"
        elif isinstance(expr_node, ast.Subscript):
            val = self.get_expr_str(expr_node.value)
            slc = self.get_expr_str(expr_node.slice)
            return f"{val}[{slc}]"
            
        return f"/* unhandled expr {type(expr_node).__name__} */"


def transpile(code: str) -> str:
    import ast
    tree = ast.parse(code)
    transpiler = PythonToGoTranspiler()
    for node in tree.body:
        if isinstance(node, ast.If) and isinstance(node.test, ast.Compare):
            if isinstance(node.test.left, ast.Name) and node.test.left.id == "__name__":
                continue
        transpiler.visit(node)
    return "\n".join(transpiler.lines)
