import ast
import json

class PythonToCTranspiler(ast.NodeVisitor):
    def __init__(self, ledger):
        self.ledger = ledger
        self.lines = [
            "#include <stdio.h>",
            "#include <stdlib.h>",
            "#include <string.h>",
            "#include <stdbool.h>",
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
            if py_type == "str": return "char*"
            if py_type == "bool": return "bool"
            if py_type == "float": return "float"
            if py_type == "None": return "void"
            return f"{py_type}*" # Assume pointer for classes
        elif isinstance(py_type_node, ast.Subscript):
            base_type = py_type_node.value.id
            if base_type == "List":
                return "List*"
            elif base_type == "Dict":
                return "Dict*"
            elif base_type == "Optional":
                return self.map_type(py_type_node.slice)
        return "void*"

    def visit_ClassDef(self, node):
        self.current_class = node.name
        self.add_line(f"typedef struct {node.name} {{")
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
                                p_type = "void*"
                                if isinstance(stmt.value, ast.List): p_type = "List*"
                                elif isinstance(stmt.value, ast.Dict): p_type = "Dict*"
                                else:
                                    for arg in body_node.args.args:
                                        if arg.arg == target.attr and arg.annotation:
                                            p_type = self.map_type(arg.annotation)
                                            break
                                    if p_type == "void*":
                                        if isinstance(stmt.value, ast.Constant):
                                            if isinstance(stmt.value.value, int): p_type = "int"
                                            elif isinstance(stmt.value.value, str): p_type = "char*"
                                            elif isinstance(stmt.value.value, bool): p_type = "bool"
                                self.properties.append((target.attr, p_type))
        
        for name, p_type in self.properties:
            self.add_line(f"{p_type} {name};")
            
        self.indent_level -= 1
        self.add_line(f"}} {node.name};")
        self.add_line("")

        for body_node in node.body:
            if isinstance(body_node, ast.AnnAssign): continue
            self.visit(body_node)
            
        self.current_class = None

    def visit_FunctionDef(self, node):
        if node.name == "main":
            return # skip top-level main, handled separately

        is_init = node.name == "__init__"
        if self.current_class:
            method_name = f"{self.current_class}_{node.name}"
            # C functions must have explicit `self` parameter
            # Add self to args if not there (which it usually is in python methods)
            params = []
            for arg in node.args.args:
                ptype = f"{self.current_class}*" if arg.arg == "self" else (self.map_type(arg.annotation) if arg.annotation else "void*")
                params.append(f"{ptype} {arg.arg}")
        else:
            method_name = node.name
            params = []
            for arg in node.args.args:
                ptype = self.map_type(arg.annotation) if arg.annotation else "void*"
                params.append(f"{ptype} {arg.arg}")
                
        ret_type = "void" if is_init else (self.map_type(node.returns) if node.returns else "void")
        
        decl = f"{ret_type} {method_name}({', '.join(params)})"
        
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
            # Try to infer if it's declaration (since C needs declarations)
            # In C, variables must be declared. We'll emit `int target = val;` loosely.
            # Tree-sitter parses `target = val;` as an expression_statement if not declared, which is valid C (though compiler would error, tree-sitter doesn't care).
            pass
            
        self.add_line(f"{target} = {val};")

    def visit_AnnAssign(self, node):
        target = self.expr_to_str(node.target)
        val = self.expr_to_str(node.value) if node.value else "NULL"
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
        exc = self.expr_to_str(node.exc) if node.exc else "Exception()"
        if exc == "[]": exc = "Exception()" # Fallback
        self.add_line(f"raise_error({exc});")

    def visit_Try(self, node):
        self.add_line("if (Pseudo_TRY())")
        self.add_line("{")
        self.indent_level += 1
        for stmt in node.body:
            self.visit(stmt)
        self.indent_level -= 1
        self.add_line("}")
        for handler in node.handlers:
            n = handler.name if handler.name else "e"
            self.add_line(f"else if (Pseudo_CATCH(&{n}))")
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
            if node.id == "None": return "NULL"
            if node.id == "True": return "true"
            if node.id == "False": return "false"
            if node.id == "Exception": return "Exception"
            return node.id
        elif isinstance(node, ast.Constant):
            if isinstance(node.value, str): return f'"{node.value}"'
            if node.value is None: return "NULL"
            if isinstance(node.value, bool): return "true" if node.value else "false"
            return str(node.value)
        elif isinstance(node, ast.Attribute):
            val = self.expr_to_str(node.value)
            # C uses -> for struct pointers. Since user-defined objects are pointers:
            return f"{val}->{node.attr}"
        elif isinstance(node, ast.Call):
            func = self.expr_to_str(node.func)
            args = [self.expr_to_str(a) for a in node.args]
            
            if func == "print":
                return "printf(" + " + ".join(args) + ")"
            if func == "str":
                # Preserve str() call so it parses back in Ingress
                return f"str({args[0]})"
            if func == "len":
                return f"List_length({args[0]})"
                
            # Class instantiation in procedural C:
            # `SpaceStation(...)` -> `SpaceStation_new(...)`
            if isinstance(node.func, ast.Name) and node.func.id[0].isupper() and node.func.id != "Exception" and node.func.id != "RuntimeError":
                return f"{func}_new({', '.join(args)})"
            if func == "Exception" or func == "RuntimeError":
                return f"Exception_new({args[0] if args else '\"\"'})"
                
            # Method call via OOP attribute: e.g. `self.assigned_station.printStatus()`
            # wait, `node.func` is `ast.Attribute` for methods!
            if isinstance(node.func, ast.Attribute):
                # We need to map `obj.method(...)` to `Class_method(obj, ...)`
                # But we don't strictly know `Class` here!
                # Wait, if we use a pseudo C syntax `obj->method(obj, ...)` tree-sitter parses it as `call_expression` with `field_expression`.
                # Or we can just emit `obj->method(...)`! C function pointers in structs work exactly like this!
                # If we emit `obj->method(...)`, tree-sitter-c parses it as a call_expression with a field_expression.
                return f"{self.expr_to_str(node.func)}({', '.join(args)})"
                
            return f"{func}({', '.join(args)})"
        elif isinstance(node, ast.BinOp):
            return f"{self.expr_to_str(node.left)} {self.op_to_str(node.op)} {self.expr_to_str(node.right)}"
        elif isinstance(node, ast.UnaryOp):
            if isinstance(node.op, ast.USub): return f"-{self.expr_to_str(node.operand)}"
            if isinstance(node.op, ast.Not): return f"!{self.expr_to_str(node.operand)}"
            return f"{self.expr_to_str(node.operand)}"
        elif isinstance(node, ast.Compare):
            if isinstance(node.ops[0], ast.In):
                return f"Dict_contains({self.expr_to_str(node.comparators[0])}, {self.expr_to_str(node.left)})"
            return f"{self.expr_to_str(node.left)} {self.op_to_str(node.ops[0])} {self.expr_to_str(node.comparators[0])}"
        elif isinstance(node, ast.List):
            elts = [self.expr_to_str(e) for e in node.elts]
            return f"(List){{{', '.join(elts)}}}"
        elif isinstance(node, ast.Dict):
            pairs = []
            for k, v in zip(node.keys, node.values):
                pairs.append(f"{{{self.expr_to_str(k)}, {self.expr_to_str(v)}}}")
            return f"(Dict){{{', '.join(pairs)}}}"
        elif isinstance(node, ast.Subscript):
            return f"{self.expr_to_str(node.value)}[{self.expr_to_str(node.slice)}]"
        return "/* unhandled expr */"

def transpile(code: str) -> str:
    tree = ast.parse(code)
    class DummyLedger:
        def log(self, *args): pass
    transpiler = PythonToCTranspiler(DummyLedger())
    
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
    
    # In C we don't have 'self', but we mapped parameter 'self' -> 'self'.
    # `self->attr` is perfectly valid C.
    return "\n".join(transpiler.lines)
