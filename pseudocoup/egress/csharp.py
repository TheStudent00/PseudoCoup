import ast
import json

class PythonToCSharpTranspiler(ast.NodeVisitor):
    def __init__(self, ledger):
        self.ledger = ledger
        self.lines = [
            "using System;",
            "using System.Collections.Generic;",
            ""
        ]
        self.indent_level = 0
        self.current_class = None
        self.properties = []

    def add_line(self, text):
        if text.strip() == "":
            self.lines.append("")
        else:
            self.lines.append("    " * self.indent_level + text)

    def map_type(self, py_type_node):
        if isinstance(py_type_node, ast.Name):
            py_type = py_type_node.id
            if py_type == "int": return "int"
            if py_type == "str": return "string"
            if py_type == "bool": return "bool"
            if py_type == "float": return "float"
            if py_type == "None": return "void"
            return py_type
        elif isinstance(py_type_node, ast.Subscript):
            base = py_type_node.value.id
            if base == "List":
                inner = self.map_type(py_type_node.slice)
                return f"List<{inner}>"
            elif base == "Dict":
                if isinstance(py_type_node.slice, ast.Tuple):
                    k = self.map_type(py_type_node.slice.elts[0])
                    v = self.map_type(py_type_node.slice.elts[1])
                    return f"Dictionary<{k}, {v}>"
            elif base == "Optional":
                inner = self.map_type(py_type_node.slice)
                # Quick hack for reference types vs value types nullable
                if inner in ("int", "float", "bool"):
                    return f"{inner}?"
                return inner
        return "object"

    def visit_ClassDef(self, node):
        self.current_class = node.name
        self.properties = []
        
        init_method = None
        for child in node.body:
            if isinstance(child, ast.FunctionDef) and child.name == "__init__":
                init_method = child
                for stmt in child.body:
                    if isinstance(stmt, ast.AnnAssign) and isinstance(stmt.target, ast.Attribute) and isinstance(stmt.target.value, ast.Name) and stmt.target.value.id == "self":
                        target = stmt.target.attr
                        cs_type = self.map_type(stmt.annotation)
                        self.properties.append({"name": target, "type": cs_type})

        self.add_line(f"public class {self.current_class}")
        self.add_line("{")
        self.indent_level += 1
        
        for p in self.properties:
            self.add_line(f"public {p['type']} {p['name']};")
            
        self.add_line("")
        
        if init_method:
            params = []
            for arg in init_method.args.args:
                if arg.arg == "self": continue
                cs_type = self.map_type(arg.annotation)
                params.append(f"{cs_type} {arg.arg}")
                
            self.add_line(f"public {self.current_class}({', '.join(params)})")
            self.add_line("{")
            self.indent_level += 1
            for stmt in init_method.body:
                self.visit(stmt)
            self.indent_level -= 1
            self.add_line("}")
            self.add_line("")
            
        for body_node in node.body:
            if isinstance(body_node, ast.FunctionDef) and body_node.name != "__init__":
                self.visit(body_node)
            
        self.indent_level -= 1
        self.add_line("}")
        self.add_line("")
        self.current_class = None

    def visit_FunctionDef(self, node):
        params = []
        for arg in node.args.args:
            if arg.arg == "self": continue
            cs_type = self.map_type(arg.annotation)
            params.append(f"{cs_type} {arg.arg}")
            
        ret_type = "void"
        if node.returns:
            if isinstance(node.returns, (ast.Name, ast.Subscript)):
                ret_type = self.map_type(node.returns)
            elif isinstance(node.returns, ast.Constant) and node.returns.value is None:
                ret_type = "void"
                
        prefix = "public " if self.current_class else "public static "
        self.add_line(f"{prefix}{ret_type} {node.name}({', '.join(params)})")
        self.add_line("{")
        self.indent_level += 1
        for body_node in node.body:
            self.visit(body_node)
        self.indent_level -= 1
        self.add_line("}")
        self.add_line("")

    def visit_AnnAssign(self, node):
        target = self.get_expr_str(node.target)
        if target.startswith("this."):
            value = self.get_expr_str(node.value) if node.value else "null"
            self.add_line(f"{target} = {value};")
            return
        
        prop_names = [p["name"] for p in self.properties] if self.properties else []
        if hasattr(node.target, "id") and node.target.id in prop_names:
            value = self.get_expr_str(node.value) if node.value else "null"
            self.add_line(f"{target} = {value};")
            return
            
        value = self.get_expr_str(node.value) if node.value else "null"
        cs_type = self.map_type(node.annotation)
        self.add_line(f"{cs_type} {target} = {value};")

    def visit_Assign(self, node):
        target = self.get_expr_str(node.targets[0])
        value = self.get_expr_str(node.value)
        self.add_line(f"{target} = {value};")

    def visit_If(self, node):
        cond = self.get_expr_str(node.test)
        self.add_line(f"if ({cond})")
        self.add_line("{")
        self.indent_level += 1
        for stmt in node.body:
            self.visit(stmt)
        self.indent_level -= 1
        if node.orelse:
            self.add_line("}")
            self.add_line("else")
            self.add_line("{")
            self.indent_level += 1
            for stmt in node.orelse:
                self.visit(stmt)
            self.indent_level -= 1
        self.add_line("}")
        
    def visit_While(self, node):
        cond = self.get_expr_str(node.test)
        self.add_line(f"while ({cond})")
        self.add_line("{")
        self.indent_level += 1
        for stmt in node.body:
            self.visit(stmt)
        self.indent_level -= 1
        self.add_line("}")

    def visit_Try(self, node):
        self.add_line("try")
        self.add_line("{")
        self.indent_level += 1
        for stmt in node.body:
            self.visit(stmt)
        self.indent_level -= 1
        for handler in node.handlers:
            self.add_line("}")
            self.add_line("catch (Exception e)")
            self.add_line("{")
            self.indent_level += 1
            for stmt in handler.body:
                self.visit(stmt)
            self.indent_level -= 1
        self.add_line("}")
        
    def visit_Raise(self, node):
        exc = self.get_expr_str(node.exc)
        self.add_line(f"throw {exc};")
        
    def visit_Break(self, node):
        self.add_line("break;")
        
    def visit_Continue(self, node):
        self.add_line("continue;")

    def visit_For(self, node):
        var_name = node.target.id
        start_val = self.get_expr_str(node.iter.args[0])
        end_val = self.get_expr_str(node.iter.args[1])
        
        self.add_line(f"for (int {var_name} = {start_val}; {var_name} < {end_val}; {var_name}++)")
        self.add_line("{")
        self.indent_level += 1
        for body_node in node.body:
            self.visit(body_node)
        self.indent_level -= 1
        self.add_line("}")

    def visit_Return(self, node):
        val = self.get_expr_str(node.value) if node.value else ""
        if val:
            self.add_line(f"return {val};")
        else:
            self.add_line("return;")

    def visit_Expr(self, node):
        if getattr(node, "value", None) and isinstance(node.value, ast.Constant) and isinstance(node.value.value, str):
            return
        expr = self.get_expr_str(node.value)
        self.add_line(f"{expr};")

    def get_expr_str(self, expr_node):
        if isinstance(expr_node, ast.Attribute):
            val = self.get_expr_str(expr_node.value)
            attr = expr_node.attr
            if val == "self":
                return f"this.{attr}"
            return f"{val}.{attr}"
        elif isinstance(expr_node, ast.Name):
            if expr_node.id == "None": return "null"
            if expr_node.id == "True": return "true"
            if expr_node.id == "False": return "false"
            return expr_node.id
        elif isinstance(expr_node, ast.Constant):
            if expr_node.value is None: return "null"
            if isinstance(expr_node.value, bool): return "true" if expr_node.value else "false"
            if isinstance(expr_node.value, str):
                return f'"{expr_node.value}"'
            return str(expr_node.value)
        elif isinstance(expr_node, ast.UnaryOp):
            op_map = {ast.USub: "-", ast.UAdd: "+", ast.Not: "!"}
            op = op_map.get(type(expr_node.op), type(expr_node.op).__name__)
            operand = self.get_expr_str(expr_node.operand)
            return f"{op}{operand}"
        elif isinstance(expr_node, ast.BinOp):
            left = self.get_expr_str(expr_node.left)
            right = self.get_expr_str(expr_node.right)
            if isinstance(expr_node.op, ast.Add): op = "+"
            elif isinstance(expr_node.op, ast.Sub): op = "-"
            elif isinstance(expr_node.op, ast.Mult): op = "*"
            elif isinstance(expr_node.op, ast.Div): op = "/"
            elif isinstance(expr_node.op, ast.Mod): op = "%"
            else: op = type(expr_node.op).__name__
            return f"{left} {op} {right}"
        elif isinstance(expr_node, ast.Compare):
            left = self.get_expr_str(expr_node.left)
            op_node = expr_node.ops[0]
            right = self.get_expr_str(expr_node.comparators[0])
            if isinstance(op_node, ast.Lt): op = "<"
            elif isinstance(op_node, ast.Gt): op = ">"
            elif isinstance(op_node, ast.Eq): op = "=="
            elif isinstance(op_node, ast.NotEq): op = "!="
            elif isinstance(op_node, ast.Is):
                return f"{left} == {right}"
            elif isinstance(op_node, ast.IsNot):
                return f"{left} != {right}"
            elif isinstance(op_node, ast.In):
                # "Red" in dict -> dict.ContainsKey("Red")
                return f"{right}.ContainsKey({left})"
            else: op = type(op_node).__name__
            return f"{left} {op} {right}"
        elif isinstance(expr_node, ast.Dict):
            pairs = []
            for k, v in zip(expr_node.keys, expr_node.values):
                pairs.append(f"{{{self.get_expr_str(k)}, {self.get_expr_str(v)}}}")
            
            # Type inferring is hard without context, but C# 9.0 target-typed new() makes it easy!
            # Example: Dictionary<string, int> x = new() { {"a", 1} };
            if len(pairs) == 0:
                return "new()"
            return f"new() {{{', '.join(pairs)}}}"
        elif isinstance(expr_node, ast.List):
            elts = [self.get_expr_str(e) for e in expr_node.elts]
            if len(elts) == 0:
                return "new()"
            return f"new() {{ {', '.join(elts)} }}"
        elif isinstance(expr_node, ast.Subscript):
            val = self.get_expr_str(expr_node.value)
            slc = self.get_expr_str(expr_node.slice)
            return f"{val}[{slc}]"
        elif isinstance(expr_node, ast.Call):
            func_name = self.get_expr_str(expr_node.func)
            args = [self.get_expr_str(a) for a in expr_node.args]
            
            if func_name == "print":
                if not args: return "Console.WriteLine()"
                return f"Console.WriteLine({', '.join(args)})"
            if func_name == "str":
                return f"{args[0]}.ToString()"
            if func_name == "len":
                return f"{args[0]}.Count"
            if func_name in ("IllegalArgumentException", "Exception", "ValueError"):
                return f"new Exception({', '.join(args)})"
                
            if func_name[0].isupper():
                return f"new {func_name}({', '.join(args)})"
            return f"{func_name}({', '.join(args)})"
            
        return f"/* unhandled expr {type(expr_node).__name__} */"


def transpile(code: str) -> str:
    import ast
    tree = ast.parse(code)
    transpiler = PythonToCSharpTranspiler(ledger={})
    
    global_stmts = []
    
    for node in tree.body:
        if isinstance(node, ast.If) and isinstance(node.test, ast.Compare):
            if getattr(node.test.left, "id", None) == "__name__":
                continue
                
        if isinstance(node, (ast.ClassDef, ast.FunctionDef, ast.Import, ast.ImportFrom)):
            transpiler.visit(node)
        else:
            global_stmts.append(node)
            
    transpiler.add_line("public class Program")
    transpiler.add_line("{")
    transpiler.indent_level += 1
    transpiler.add_line("public static void Main()")
    transpiler.add_line("{")
    transpiler.indent_level += 1
    for stmt in global_stmts:
        transpiler.visit(stmt)
    transpiler.indent_level -= 1
    transpiler.add_line("}")
    transpiler.indent_level -= 1
    transpiler.add_line("}")
    
    return "\n".join(transpiler.lines)
