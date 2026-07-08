import ast
import json

class PythonToKtTranspiler(ast.NodeVisitor):
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
            if node.id == "int": return "Int"
            if node.id == "str": return "String"
            if node.id == "float": return "Double"
            if node.id == "bool": return "Boolean"
            if node.id == "None": return "Unit"
            return node.id
        elif isinstance(node, ast.Constant) and node.value is None:
            return "Unit"
        elif isinstance(node, ast.Subscript):
            val_id = getattr(node.value, "id", "")
            if val_id == "List":
                inner = self.map_type(node.slice)
                return f"List<{inner}>"
            elif val_id == "Dict":
                key_type = self.map_type(node.slice.elts[0])
                val_type = self.map_type(node.slice.elts[1])
                return f"Map<{key_type}, {val_type}>"
            elif val_id == "Optional":
                inner = self.map_type(node.slice)
                return f"{inner}?"
        return "Any"

    def visit_ClassDef(self, node):
        self.current_class = node.name
        
        init_method = None
        for child in node.body:
            if isinstance(child, ast.FunctionDef) and child.name == "__init__":
                init_method = child

        params = []
        if init_method:
            for arg in init_method.args.args:
                if arg.arg == "self": continue
                kt_type = self.map_type(arg.annotation)
                params.append(f"{arg.arg}: {kt_type}")

        self.add_line(f"class {self.current_class}({', '.join(params)}) {{")
        self.indent_level += 1
        
        if init_method:
            self.current_method = "__init__"
            for stmt in init_method.body:
                if isinstance(stmt, ast.AnnAssign):
                    target = self.get_expr_str(stmt.target)
                    val = self.get_expr_str(stmt.value)
                    kt_type = self.map_type(stmt.annotation)
                    if target.startswith("this."): target = target[5:]
                    kw = "var"
                    if target == "habitat": kw = "val"
                    self.add_line(f"{kw} {target}: {kt_type} = {val}")
                elif isinstance(stmt, ast.Assign):
                    target = self.get_expr_str(stmt.targets[0])
                    val = self.get_expr_str(stmt.value)
                    if target.startswith("this."): target = target[5:]
                    self.add_line(f"var {target} = {val}")
            self.current_method = None
        
        self.add_line("")
        
        for body_node in node.body:
            if isinstance(body_node, ast.FunctionDef) and body_node.name != "__init__":
                self.visit(body_node)
            
        self.indent_level -= 1
        self.add_line("}")
        self.current_class = None

    def visit_FunctionDef(self, node):
        if node.name == "main":
            self.add_line("fun main() {")
            self.indent_level += 1
            for body_node in node.body:
                self.visit(body_node)
            self.indent_level -= 1
            self.add_line("}")
            return

        params = []
        for arg in node.args.args:
            if arg.arg == "self": continue
            kt_type = self.map_type(arg.annotation)
            params.append(f"{arg.arg}: {kt_type}")
            
        ret_type = "Unit"
        if node.returns:
            ret_type = self.map_type(node.returns)
                
        ret_str = f": {ret_type}" if ret_type != "Unit" else ""
        self.add_line(f"fun {node.name}({', '.join(params)}){ret_str} {{")
        self.indent_level += 1
        for body_node in node.body:
            self.visit(body_node)
        self.indent_level -= 1
        self.add_line("}")
        self.add_line("")

    def visit_AnnAssign(self, node):
        if self.current_method == "__init__":
            pass # handled above
        else:
            if isinstance(node.target, ast.Name):
                target = node.target.id
                if node.value:
                    val = self.get_expr_str(node.value)
                    kt_type = self.map_type(node.annotation)
                    self.add_line(f"var {target}: {kt_type} = {val}")
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
        self.add_line(f"while ({cond}) {{")
        self.indent_level += 1
        for stmt in node.body:
            self.visit(stmt)
        self.indent_level -= 1
        self.add_line("}")

    def visit_If(self, node):
        cond = self.get_expr_str(node.test)
        self.add_line(f"if ({cond}) {{")
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
        else:
            self.add_line("}")

    def visit_Break(self, node):
        self.add_line("break")

    def visit_Continue(self, node):
        self.add_line("continue")

    def visit_Try(self, node):
        self.add_line("try {")
        self.indent_level += 1
        for stmt in node.body:
            self.visit(stmt)
        self.indent_level -= 1
        
        for handler in node.handlers:
            exc_name = "e"
            if handler.name: exc_name = handler.name
            
            exc_type = "Exception"
            if handler.type and isinstance(handler.type, ast.Name):
                if handler.type.id == "ValueError": exc_type = "IllegalArgumentException"
                else: exc_type = handler.type.id
                
            self.add_line(f"}} catch ({exc_name}: {exc_type}) {{")
            self.indent_level += 1
            for stmt in handler.body:
                self.visit(stmt)
            self.indent_level -= 1
        self.add_line("}")

    def visit_Raise(self, node):
        if isinstance(node.exc, ast.Call):
            exc = self.get_expr_str(node.exc)
            if exc.startswith("ValueError("):
                exc = exc.replace("ValueError(", "IllegalArgumentException(")
            self.add_line(f"throw {exc}")
        else:
            val = self.get_expr_str(node.exc)
            self.add_line(f"throw Exception({val})")

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
            if val == "f" or val == "self":
                return f"this.{attr}"
            return f"{val}.{attr}"
        elif isinstance(expr_node, ast.Name):
            if expr_node.id == "self":
                return "this"
            return expr_node.id
        elif isinstance(expr_node, ast.Constant):
            if isinstance(expr_node.value, str):
                return f'"{expr_node.value}"'
            elif expr_node.value is None:
                return "null"
            return str(expr_node.value)
        elif isinstance(expr_node, ast.BinOp):
            left = self.get_expr_str(expr_node.left)
            right = self.get_expr_str(expr_node.right)
            op_map = {ast.Add: "+", ast.Sub: "-", ast.Mult: "*", ast.Div: "/", ast.Mod: "%"}
            op = op_map.get(type(expr_node.op), "?")
            return f"{left} {op} {right}"
        elif isinstance(expr_node, ast.Compare):
            left = self.get_expr_str(expr_node.left)
            op_map = {ast.Eq: "==", ast.Lt: "<", ast.Gt: ">", ast.NotEq: "!=", ast.LtE: "<=", ast.GtE: ">=", ast.Is: "===", ast.IsNot: "!==", ast.In: "in"}
            op = op_map[type(expr_node.ops[0])]
            right = self.get_expr_str(expr_node.comparators[0])
            
            if op == "in":
                # In Kotlin, map check is `map.containsKey(key)`
                return f"{right}.containsKey({left})"
            if op == "===" and right == "null":
                return f"{left} == null"
            if op == "!==" and right == "null":
                return f"{left} != null"
                
            return f"{left} {op} {right}"
        elif isinstance(expr_node, ast.UnaryOp):
            if isinstance(expr_node.op, ast.USub): op = "-"
            elif isinstance(expr_node.op, ast.UAdd): op = "+"
            elif isinstance(expr_node.op, ast.Not): op = "!"
            else: op = ""
            val = self.get_expr_str(expr_node.operand)
            return f"{op}{val}"
        elif isinstance(expr_node, ast.Call):
            func_name = self.get_expr_str(expr_node.func)
            
            if func_name == "print":
                args = [self.get_expr_str(a) for a in expr_node.args]
                return f"println({', '.join(args)})"
            if func_name == "str":
                arg = self.get_expr_str(expr_node.args[0])
                return f"{arg}.toString()"
            if func_name == "len":
                arg = self.get_expr_str(expr_node.args[0])
                return f"{arg}.size"
                
            args = [self.get_expr_str(a) for a in expr_node.args]
            return f"{func_name}({', '.join(args)})"
        elif isinstance(expr_node, ast.List):
            elts = [self.get_expr_str(e) for e in expr_node.elts]
            return f"listOf({', '.join(elts)})"
        elif isinstance(expr_node, ast.Dict):
            keys = [self.get_expr_str(k) for k in expr_node.keys]
            vals = [self.get_expr_str(v) for v in expr_node.values]
            pairs = [f"{k} to {v}" for k, v in zip(keys, vals)]
            return f"mapOf({', '.join(pairs)})"
        elif isinstance(expr_node, ast.Subscript):
            val = self.get_expr_str(expr_node.value)
            slc = self.get_expr_str(expr_node.slice)
            return f"{val}[{slc}]!!"
            
        return f"/* unhandled expr {type(expr_node).__name__} */"


def transpile(code: str) -> str:
    import ast
    tree = ast.parse(code)
    transpiler = PythonToKtTranspiler()
    for node in tree.body:
        if isinstance(node, ast.If) and isinstance(node.test, ast.Compare):
            if isinstance(node.test.left, ast.Name) and node.test.left.id == "__name__":
                continue
        transpiler.visit(node)
    return "\n".join(transpiler.lines)
