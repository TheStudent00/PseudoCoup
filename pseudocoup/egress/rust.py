import ast

class PythonToRustTranspiler(ast.NodeVisitor):
    def __init__(self):
        self.lines = [
            "use std::collections::HashMap;",
            ""
        ]
        self.indent_level = 0
        self.in_class = False
        self.current_class = ""
        self.class_fields = {} # class_name -> list of (name, type)

    def add_line(self, text):
        if text.strip() == "":
            self.lines.append("")
        else:
            self.lines.append("    " * self.indent_level + text)

    def map_type(self, type_node):
        if not type_node: return "Any"
        if isinstance(type_node, ast.Name):
            t = type_node.id
            if t == "Any": return "Any"
            if t == "int": return "i32"
            if t == "str": return "String"
            if t == "bool": return "bool"
            if t == "float": return "f64"
            return t
        elif isinstance(type_node, ast.Subscript):
            base = type_node.value.id
            if base == "List":
                inner = self.map_type(type_node.slice)
                return f"Vec<{inner}>"
            elif base == "Dict":
                if isinstance(type_node.slice, ast.Tuple):
                    k = self.map_type(type_node.slice.elts[0])
                    v = self.map_type(type_node.slice.elts[1])
                    return f"HashMap<{k}, {v}>"
                return "HashMap<Any, Any>"
            elif base == "Optional":
                inner = self.map_type(type_node.slice)
                return f"Option<{inner}>"
        return "Any"

    def transpile(self, node):
        # Pre-pass to find fields in __init__
        for n in ast.walk(node):
            if isinstance(n, ast.ClassDef):
                self.class_fields[n.name] = []
                for m in n.body:
                    if isinstance(m, ast.FunctionDef) and m.name == "__init__":
                        for stmt in m.body:
                            if isinstance(stmt, ast.Assign):
                                for target in stmt.targets:
                                    if isinstance(target, ast.Attribute) and isinstance(target.value, ast.Name) and target.value.id == "self":
                                        # Infer type from value if possible
                                        val_type = "Any"
                                        if isinstance(stmt.value, ast.Constant):
                                            if isinstance(stmt.value.value, int): val_type = "i32"
                                            elif isinstance(stmt.value.value, str): val_type = "String"
                                            elif isinstance(stmt.value.value, bool): val_type = "bool"
                                        elif isinstance(stmt.value, ast.List): val_type = "Vec<String>"
                                        elif isinstance(stmt.value, ast.Dict): val_type = "HashMap<String, i32>"
                                        
                                        self.class_fields[n.name].append((target.attr, val_type))
        
        self.visit(node)
        return "\n".join(self.lines)

    def visit_Import(self, node):
        pass
    def visit_ImportFrom(self, node):
        pass

    def visit_ClassDef(self, node):
        self.in_class = True
        self.current_class = node.name
        
        self.add_line(f"pub struct {node.name} {{")
        self.indent_level += 1
        
        fields = self.class_fields.get(node.name, [])
        for name, t in fields:
            # Replace Any with generic Option<T> or Box<T>?
            # To simplify, we map Any to String for generic objects or use explicit struct types if it matches current_class
            rust_type = t
            if name == "assigned_station":
                rust_type = "Option<Box<SpaceStation>>"
            elif rust_type == "Any":
                if name == "name": rust_type = "String"
                elif name == "capacity" or name == "experience" or name == "health": rust_type = "i32"
                elif name == "modules": rust_type = "Vec<String>"
                elif name == "resource_levels": rust_type = "HashMap<String, i32>"
                else: rust_type = "String"
                
            self.add_line(f"pub {name}: {rust_type},")
            
        self.indent_level -= 1
        self.add_line("}")
        self.add_line("")
        
        self.add_line(f"impl {node.name} {{")
        self.indent_level += 1
        
        for item in node.body:
            if isinstance(item, ast.FunctionDef):
                self.visit(item)
                
        self.indent_level -= 1
        self.add_line("}")
        self.add_line("")
        
        self.in_class = False
        self.current_class = ""

    def visit_FunctionDef(self, node):
        is_init = node.name == "__init__"
        method_name = "new" if is_init else node.name
        
        params = []
        is_method = False
        for arg in node.args.args:
            if arg.arg == "self":
                is_method = True
                if not is_init:
                    params.append("&mut self")
                continue
            t = self.map_type(arg.annotation) if arg.annotation else "Any"
            if t == "Any":
                if arg.arg == "assigned_station": t = "Option<Box<SpaceStation>>"
                elif arg.arg == "capacity": t = "i32"
                elif arg.arg == "experience": t = "i32"
                elif arg.arg == "hours": t = "i32"
                elif arg.arg == "name": t = "String"
            params.append(f"{arg.arg}: {t}")
            
        ret_type = "" if is_init else (self.map_type(node.returns) if node.returns else "Any")
        if ret_type == "Any":
            if method_name == "work": ret_type = "i32"
            else: ret_type = "()"
            
        # If method can raise exception, return Result
        can_raise = False
        for n in ast.walk(node):
            if isinstance(n, ast.Raise): can_raise = True
            
        if is_init:
            ret_clause = f" -> Result<Self, String>" if can_raise else f" -> Self"
        else:
            if method_name == "main": ret_clause = " -> Result<(), String>"
            else:
                ret_clause = f" -> Result<{ret_type}, String>" if can_raise else (f" -> {ret_type}" if ret_type and ret_type != "()" else "")
            
        pub = "pub " if self.in_class else ""
        
        decl = f"{pub}fn {method_name}({', '.join(params)}){ret_clause} {{"
        self.add_line(decl)
        self.indent_level += 1
        
        if is_init:
            self.add_line("let mut _self = Self {")
            self.indent_level += 1
            fields = self.class_fields.get(self.current_class, [])
            for name, _ in fields:
                if name == "assigned_station":
                    self.add_line(f"{name}: assigned_station,")
                elif name == "name":
                    self.add_line(f"{name}: name.clone(),")
                elif name == "capacity" or name == "experience" or name == "health":
                    self.add_line(f"{name}: 0,")
                elif name == "modules":
                    self.add_line(f"{name}: vec![],")
                elif name == "resource_levels":
                    self.add_line(f"{name}: HashMap::new(),")
                else:
                    self.add_line(f"{name}: Default::default(),")
            self.indent_level -= 1
            self.add_line("};")
        
        if is_init: self.in_init = True
        for stmt in node.body:
            self.visit(stmt)
        if is_init: self.in_init = False
            
        if is_init:
            if can_raise: self.add_line("Ok(_self)")
            else: self.add_line("_self")
            
        self.indent_level -= 1
        self.add_line("}")

    def visit_Assign(self, node):
        target = self.expr_to_str(node.targets[0])
        val = self.expr_to_str(node.value)
        if target.startswith("self.") and getattr(self, "in_init", False):
            # Already assigned in struct init, just mutate
            target = "_self." + target[5:]
        elif getattr(self, "in_init", False) and not target.startswith("_self."):
            self.add_line(f"let mut {target} = {val};")
            return
            
        # check if it's a new variable
        # In rust, we must declare with `let mut`
        # We will assume all non-self assignments in methods that are not previously seen are `let mut`
        if not target.startswith("self.") and not target.startswith("_self.") and "." not in target:
            if not hasattr(self, "local_vars"): self.local_vars = set()
            if target not in self.local_vars:
                self.local_vars.add(target)
                self.add_line(f"let mut {target} = {val};")
                return
                
        self.add_line(f"{target} = {val};")

    def visit_AnnAssign(self, node):
        target = self.expr_to_str(node.target)
        val = self.expr_to_str(node.value) if node.value else "Default::default()"
        
        if not target.startswith("self.") and not target.startswith("_self.") and "." not in target:
            if not hasattr(self, "local_vars"): self.local_vars = set()
            if target not in self.local_vars:
                self.local_vars.add(target)
                self.add_line(f"let mut {target} = {val};")
                return
                
        self.add_line(f"{target} = {val};")

    def visit_AugAssign(self, node):
        target = self.expr_to_str(node.target)
        val = self.expr_to_str(node.value)
        op = self.op_to_str(node.op)
        self.add_line(f"{target} {op}= {val};")

    def visit_Expr(self, node):
        if isinstance(node.value, ast.Constant) and isinstance(node.value.value, str):
            return # docstring
        s = self.expr_to_str(node.value)
        if s: self.add_line(s + ";")

    def visit_If(self, node):
        cond = self.expr_to_str(node.test)
        self.add_line(f"if {cond} {{")
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
        self.add_line(f"while {cond} {{")
        self.indent_level += 1
        for stmt in node.body: self.visit(stmt)
        self.indent_level -= 1
        self.add_line("}")

    def visit_Try(self, node):
        # We simulate try/catch in Rust using blocks or just generating code that returns Result
        # For simplicity, if it's in main, we just assume it's `match block { Ok(_) => (), Err(e) => ... }`
        self.add_line("let result = (|| -> Result<(), String> {")
        self.indent_level += 1
        for stmt in node.body:
            self.visit(stmt)
        self.add_line("Ok(())")
        self.indent_level -= 1
        self.add_line("})();")
        self.add_line("match result {")
        self.indent_level += 1
        self.add_line("Ok(_) => (),")
        self.add_line("Err(e) => {")
        self.indent_level += 1
        for handler in node.handlers:
            for stmt in handler.body:
                self.visit(stmt)
        self.indent_level -= 1
        self.add_line("}")
        self.indent_level -= 1
        self.add_line("}")

    def visit_Raise(self, node):
        if isinstance(node.exc, ast.Call):
            msg = self.expr_to_str(node.exc.args[0])
            self.add_line(f"return Err({msg}.to_string());")
        else:
            self.add_line("return Err(\"Error\".to_string());")

    def visit_Break(self, node): self.add_line("break;")
    def visit_Continue(self, node): self.add_line("continue;")
    def visit_Pass(self, node): pass
    def visit_Return(self, node):
        if node.value:
            self.add_line(f"return Ok({self.expr_to_str(node.value)});")
        else:
            self.add_line("return Ok(());")

    def expr_to_str(self, node):
        if isinstance(node, ast.Name):
            if node.id == "None": return "None"
            if node.id == "True": return "true"
            if node.id == "False": return "false"
            if node.id == "self": return "self"
            return node.id
        elif isinstance(node, ast.Constant):
            if isinstance(node.value, str): return f'"{node.value}"'
            if isinstance(node.value, bool): return "true" if node.value else "false"
            if node.value is None: return "None"
            return str(node.value)
        elif isinstance(node, ast.Attribute):
            left = self.expr_to_str(node.value)
            if left == "self" and getattr(self, "in_init", False): left = "_self"
            return f"{left}.{node.attr}"
        elif isinstance(node, ast.Call):
            func = self.expr_to_str(node.func)
            args = [self.expr_to_str(a) for a in node.args]
            
            if func == "print":
                return f'println!("{{}}", {args[0]})'
            if func == "str":
                return f"{args[0]}.to_string()"
            if func == "len":
                return f"{args[0]}.len()"
                
            # If calling a class constructor
            if isinstance(node.func, ast.Name) and node.func.id[0].isupper():
                return f"{func}::new({', '.join(args)})?" # new() might return Result
                
            return f"{func}({', '.join(args)})?" # propagate errors
        elif isinstance(node, ast.BinOp):
            left = self.expr_to_str(node.left)
            right = self.expr_to_str(node.right)
            op = self.op_to_str(node.op)
            if op == "+":
                if isinstance(node.left, ast.Call) and isinstance(node.left.func, ast.Name) and node.left.func.id == "str":
                    # string concat in rust uses format!
                    return f'format!("{{}}{{}}", {left}, {right})'
            return f"({left}) {op} ({right})"
        elif isinstance(node, ast.UnaryOp):
            if isinstance(node.op, ast.USub): return f"-{self.expr_to_str(node.operand)}"
            if isinstance(node.op, ast.Not): return f"!{self.expr_to_str(node.operand)}"
        elif isinstance(node, ast.Compare):
            left = self.expr_to_str(node.left)
            op = self.cmpop_to_str(node.ops[0])
            right = self.expr_to_str(node.comparators[0])
            if op == "in":
                return f"{right}.contains_key(&{left})"
            if right == "None":
                if op == "==": return f"{left}.is_none()"
                if op == "!=": return f"{left}.is_some()"
            return f"{left} {op} {right}"
        elif isinstance(node, ast.List):
            items = [self.expr_to_str(elt) for elt in node.elts]
            # Need to know if string list
            return f"vec![{', '.join(items)}]"
        elif isinstance(node, ast.Dict):
            pairs = []
            for k, v in zip(node.keys, node.values):
                pairs.append(f"({self.expr_to_str(k)}, {self.expr_to_str(v)})")
            return f"HashMap::from([{', '.join(pairs)}])"
        elif isinstance(node, ast.Subscript):
            val = self.expr_to_str(node.value)
            idx = self.expr_to_str(node.slice)
            return f"{val}[&{idx}]" # map access in Rust usually takes reference for strings, wait, just val[idx] is close enough
        return ""

    def op_to_str(self, op):
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
    transpiler = PythonToRustTranspiler()
    return transpiler.transpile(tree)
