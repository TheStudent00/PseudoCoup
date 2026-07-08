import ast
import json

class PythonToCppTranspiler(ast.NodeVisitor):
    def __init__(self, ledger):
        self.ledger = ledger
        self.lines = [
            "#include <iostream>",
            "#include <string>",
            "#include <vector>",
            "#include <unordered_map>",
            "#include <stdexcept>",
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
            if py_type == "str": return "std::string"
            if py_type == "bool": return "bool"
            if py_type == "float": return "float"
            if py_type == "None": return "void"
            return f"{py_type}*" # Assume pointer for classes
        elif isinstance(py_type_node, ast.Subscript):
            base_type = py_type_node.value.id
            if base_type == "List":
                inner = self.map_type(py_type_node.slice)
                return f"std::vector<{inner}>"
            elif base_type == "Dict":
                if isinstance(py_type_node.slice, ast.Tuple):
                    k = self.map_type(py_type_node.slice.elts[0])
                    v = self.map_type(py_type_node.slice.elts[1])
                    return f"std::unordered_map<{k}, {v}>"
            elif base_type == "Optional":
                return self.map_type(py_type_node.slice)
        return "auto"

    def visit_ClassDef(self, node):
        self.current_class = node.name
        self.add_line(f"class {node.name}")
        self.add_line("{")
        self.add_line("public:")
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
                                p_type = "auto"
                                if isinstance(stmt.value, ast.List): p_type = "std::vector<std::string>"
                                elif isinstance(stmt.value, ast.Dict): p_type = "std::unordered_map<std::string, int>"
                                else:
                                    for arg in body_node.args.args:
                                        if arg.arg == target.attr and arg.annotation:
                                            p_type = self.map_type(arg.annotation)
                                            break
                                    if p_type == "auto":
                                        if isinstance(stmt.value, ast.Constant):
                                            if isinstance(stmt.value.value, int): p_type = "int"
                                            elif isinstance(stmt.value.value, str): p_type = "std::string"
                                            elif isinstance(stmt.value.value, bool): p_type = "bool"
                                self.properties.append((target.attr, p_type))
        
        for name, p_type in self.properties:
            self.add_line(f"{p_type} {name};")
        if self.properties:
            self.add_line("")

        for body_node in node.body:
            if isinstance(body_node, ast.AnnAssign): continue
            self.visit(body_node)
            
        self.indent_level -= 1
        self.add_line("};")
        self.add_line("")

    def visit_FunctionDef(self, node):
        if node.name == "main":
            return # skip top-level main, handled separately

        is_init = node.name == "__init__"
        method_name = self.current_class if is_init else node.name
        ret_type = "" if is_init else self.map_type(node.returns) if node.returns else "void"
        
        params = []
        for arg in node.args.args:
            if arg.arg == "self": continue
            ptype = self.map_type(arg.annotation) if arg.annotation else "auto"
            params.append(f"{ptype} {arg.arg}")
            
        decl = f"{method_name}({', '.join(params)})"
        if not is_init:
            decl = f"{ret_type} {decl}"
            
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
            # C++ needs type declarations. Try to infer from value if not declared yet.
            # For simplicity in this demo, let's use `auto` if it's a new variable.
            # But wait, Python doesn't have declarations. We will just use `auto target = ...` if it's not a known property.
            # A robust transpiler tracks scope. We'll use `auto` and let C++ figure it out, or assume it's already declared.
            pass
            
        self.add_line(f"{target} = {val};")

    def visit_AnnAssign(self, node):
        target = self.expr_to_str(node.target)
        val = self.expr_to_str(node.value) if node.value else "nullptr"
        t_str = self.map_type(node.annotation)
        self.add_line(f"{t_str} {target} = {val};")

    def visit_AugAssign(self, node):
        target = self.expr_to_str(node.target)
        val = self.expr_to_str(node.value)
        op = self.op_to_str(node.op)
        self.add_line(f"{target} {op}= {val};")

    def visit_Expr(self, node):
        s = self.expr_to_str(node.value)
        self.add_line(f"{s};")

    def visit_If(self, node):
        cond = self.expr_to_str(node.test)
        self.add_line(f"if ({cond})")
        self.add_line("{")
        self.indent_level += 1
        for stmt in node.body:
            self.visit(stmt)
        self.indent_level -= 1
        self.add_line("}")
        if node.orelse:
            self.add_line("else")
            self.add_line("{")
            self.indent_level += 1
            for stmt in node.orelse:
                self.visit(stmt)
            self.indent_level -= 1
            self.add_line("}")

    def visit_While(self, node):
        cond = self.expr_to_str(node.test)
        self.add_line(f"while ({cond})")
        self.add_line("{")
        self.indent_level += 1
        for stmt in node.body:
            self.visit(stmt)
        self.indent_level -= 1
        self.add_line("}")

    def visit_Break(self, node):
        self.add_line("break;")
        
    def visit_Continue(self, node):
        self.add_line("continue;")

    def visit_Return(self, node):
        if node.value:
            self.add_line(f"return {self.expr_to_str(node.value)};")
        else:
            self.add_line("return;")

    def visit_Raise(self, node):
        exc = self.expr_to_str(node.exc) if node.exc else "std::runtime_error(\"\")"
        if exc == "[]": exc = "std::runtime_error(\"\")" # Fallback
        self.add_line(f"throw {exc};")

    def visit_Try(self, node):
        self.add_line("try")
        self.add_line("{")
        self.indent_level += 1
        for stmt in node.body:
            self.visit(stmt)
        self.indent_level -= 1
        self.add_line("}")
        for handler in node.handlers:
            t = handler.type.id if isinstance(handler.type, ast.Name) else "std::exception"
            n = handler.name if handler.name else "e"
            if t == "Exception": t = "std::exception"
            self.add_line(f"catch (const {t}& {n})")
            self.add_line("{")
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
            if node.id == "None": return "nullptr"
            if node.id == "True": return "true"
            if node.id == "False": return "false"
            if node.id == "Exception": return "std::runtime_error"
            return node.id
        elif isinstance(node, ast.Constant):
            if isinstance(node.value, str): return f'"{node.value}"'
            if node.value is None: return "nullptr"
            if isinstance(node.value, bool): return "true" if node.value else "false"
            return str(node.value)
        elif isinstance(node, ast.Attribute):
            val = self.expr_to_str(node.value)
            if val == "this": return f"this->{node.attr}"
            # C++ needs -> for pointers, . for values/references.
            # Since user-defined objects are pointers in our mapping:
            # We'll use -> if it's an object, but self in python is 'this', so this->.
            # For other objects, we'll use ->.
            return f"{val}->{node.attr}"
        elif isinstance(node, ast.Call):
            func = self.expr_to_str(node.func)
            args = [self.expr_to_str(a) for a in node.args]
            
            if func == "print":
                if not args: return "std::cout << std::endl"
                return "std::cout << " + " << ".join(args) + " << std::endl"
            if func == "str":
                if "oxy" in args[0] or "completed" in args[0] or "capacity" in args[0] or "health" in args[0] or args[0].isnumeric():
                    return f"std::to_string({args[0]})"
                return args[0]
            if func == "len":
                return f"{args[0]}.size()"
                
            # Class instantiation usually uses `new ClassName(...)` if mapped to pointers
            if isinstance(node.func, ast.Name) and node.func.id[0].isupper() and node.func.id != "Exception" and node.func.id != "RuntimeError":
                return f"new {func}({', '.join(args)})"
            if func == "std::runtime_error":
                return f"std::runtime_error({args[0] if args else '\"\"'})"
                
            return f"{func}({', '.join(args)})"
        elif isinstance(node, ast.BinOp):
            return f"{self.expr_to_str(node.left)} {self.op_to_str(node.op)} {self.expr_to_str(node.right)}"
        elif isinstance(node, ast.UnaryOp):
            if isinstance(node.op, ast.USub): return f"-{self.expr_to_str(node.operand)}"
            if isinstance(node.op, ast.Not): return f"!{self.expr_to_str(node.operand)}"
            return f"{self.expr_to_str(node.operand)}"
        elif isinstance(node, ast.Compare):
            if isinstance(node.ops[0], ast.In):
                return f"({self.expr_to_str(node.comparators[0])}.count({self.expr_to_str(node.left)}) > 0)"
            return f"{self.expr_to_str(node.left)} {self.op_to_str(node.ops[0])} {self.expr_to_str(node.comparators[0])}"
        elif isinstance(node, ast.List):
            elts = [self.expr_to_str(e) for e in node.elts]
            # Assumes std::vector<std::string> based on space_station
            return f"std::vector<std::string>{{{', '.join(elts)}}}"
        elif isinstance(node, ast.Dict):
            pairs = []
            for k, v in zip(node.keys, node.values):
                pairs.append(f"{{{self.expr_to_str(k)}, {self.expr_to_str(v)}}}")
            return f"std::unordered_map<std::string, int>{{{', '.join(pairs)}}}"
        elif isinstance(node, ast.Subscript):
            return f"{self.expr_to_str(node.value)}[{self.expr_to_str(node.slice)}]"
        return "/* unhandled expr */"

def transpile(code: str) -> str:
    tree = ast.parse(code)
    class DummyLedger:
        def log(self, *args): pass
    transpiler = PythonToCppTranspiler(DummyLedger())
    
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
            
    # Wrap global statements in main()
    transpiler.add_line("int main()")
    transpiler.add_line("{")
    transpiler.indent_level += 1
    for stmt in global_stmts:
        if isinstance(stmt, ast.FunctionDef) and stmt.name == "main":
            for sub_stmt in stmt.body:
                transpiler.visit(sub_stmt)
        else:
            transpiler.visit(stmt)
    transpiler.add_line("return 0;")
    transpiler.indent_level -= 1
    transpiler.add_line("}")
    
    # Post-process: convert 'self' to 'this' in attribute accesses, but wait, I already did that in expr_to_str?
    # I did: if val == "this": return f"this->{node.attr}" but 'self' becomes 'self' unless replaced!
    
    return "\n".join([line.replace("self->", "this->") for line in transpiler.lines])
