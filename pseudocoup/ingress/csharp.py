import tree_sitter_c_sharp
from tree_sitter import Language, Parser
import json

class Ledger:
    def __init__(self):
        self.entries = []
    
    def log(self, ts_node, py_target, reason):
        entry = {"ts_node": ts_node, "py_target": py_target, "reason": reason}
        if entry not in self.entries:
            self.entries.append(entry)
    
    def save(self, path):
        with open(path, 'w') as f:
            json.dump(self.entries, f, indent=2)

class CSharpToPyTranspiler:
    def __init__(self, src_bytes):
        self.src_bytes = src_bytes
        self.lines = []
        self.indent_level = 0
        self.ledger = Ledger()
        self.lines.append("from typing import List, Dict, Optional, Any")
        self.lines.append("")
        
    def add_line(self, text):
        if text.strip() == "":
            self.lines.append("")
        else:
            self.lines.append("    " * self.indent_level + text)

    def get_text(self, node):
        if node is None: return ""
        return self.src_bytes[node.start_byte:node.end_byte].decode('utf8')
        
    def get_child(self, node, type_name):
        for child in node.children:
            if child.type == type_name:
                return child
        return None

    def get_children(self, node, type_name):
        return [c for c in node.children if c.type == type_name]

    def map_type(self, ts_type):
        ts_type = ts_type.strip()
        if ts_type == "int": return "int"
        if ts_type == "float": return "float"
        if ts_type == "string": return "str"
        if ts_type == "void": return "None"
        if ts_type == "bool": return "bool"
        if ts_type == "object": return "Any"
        if ts_type.endswith("?"): return f"Optional[{self.map_type(ts_type[:-1])}]"
        if ts_type.startswith("List<"): return f"List[{self.map_type(ts_type[5:-1])}]"
        if ts_type.startswith("Dictionary<"):
            inner = ts_type[11:-1].split(",")
            return f"Dict[{self.map_type(inner[0].strip())}, {self.map_type(inner[1].strip())}]"
        return ts_type

    def transpile(self, root_node):
        for node in root_node.children:
            if node.type == "class_declaration":
                # Is it the main program wrapper?
                name = self.get_text(self.get_child(node, "identifier"))
                if name != "Program":
                    self.visit_class(node)
            elif node.type in ("method_declaration", "local_function_statement"):
                self.visit_global_method(node)
            elif node.type == "global_statement":
                for child in node.children:
                    if child.type in ("method_declaration", "local_function_statement"):
                        self.visit_global_method(child)
        return "\n".join(self.lines)

    def visit_class(self, node):
        name_node = self.get_child(node, "identifier")
        class_name = self.get_text(name_node)
        self.add_line(f"class {class_name}:")
        self.indent_level += 1
        
        body = self.get_child(node, "declaration_list")
        
        for c in body.children:
            if c.type == "field_declaration":
                # public int x;
                decl_list = self.get_child(c, "variable_declaration")
                if decl_list:
                    type_node = self.get_child(decl_list, "predefined_type") or self.get_child(decl_list, "generic_name") or self.get_child(decl_list, "identifier")
                    var_decl = self.get_child(decl_list, "variable_declarator")
                    ident = self.get_text(self.get_child(var_decl, "identifier")) if var_decl else ""
                    t_str = self.get_text(type_node) if type_node else ""
                    self.add_line(f"{ident}: {self.map_type(t_str)}")
                
        self.add_line("")
        
        for c in body.children:
            if c.type == "constructor_declaration":
                params_node = self.get_child(c, "parameter_list")
                params = ["self"]
                if params_node:
                    for p in self.get_children(params_node, "parameter"):
                        idents = self.get_children(p, "identifier")
                        p_ident = self.get_text(idents[-1]) if idents else ""
                        p_type_node = self.get_child(p, "predefined_type") or self.get_child(p, "generic_name") or (idents[0] if len(idents) > 1 else None)
                        p_t = self.get_text(p_type_node) if p_type_node else "object"
                        params.append(f"{p_ident}: {self.map_type(p_t)}")
                        
                self.add_line(f"def __init__({', '.join(params)}) -> None:")
                self.indent_level += 1
                
                block = self.get_child(c, "block")
                if block and any(stmt.is_named for stmt in block.children):
                    for stmt in block.children:
                        if stmt.is_named:
                            self.visit_statement(stmt)
                else:
                    self.add_line("pass")
                    
                self.indent_level -= 1
                self.add_line("")
                
            elif c.type == "method_declaration":
                name = self.get_text(self.get_child(c, "identifier"))
                
                # Check for static
                modifiers = self.get_children(c, "modifier")
                is_static = any(self.get_text(m) == "static" for m in modifiers)
                
                params_node = self.get_child(c, "parameter_list")
                params = [] if is_static else ["self"]
                if params_node:
                    for p in self.get_children(params_node, "parameter"):
                        idents = self.get_children(p, "identifier")
                        p_ident = self.get_text(idents[-1]) if idents else ""
                        p_type_node = self.get_child(p, "predefined_type") or self.get_child(p, "generic_name") or (idents[0] if len(idents) > 1 else None)
                        p_t = self.get_text(p_type_node) if p_type_node else "object"
                        params.append(f"{p_ident}: {self.map_type(p_t)}")
                        
                t_node = self.get_child(c, "predefined_type") or self.get_child(c, "generic_name") or self.get_child(c, "identifier")
                ret_t = self.map_type(self.get_text(t_node)) if t_node else "Any"
                
                self.add_line(f"def {name}({', '.join(params)}) -> {ret_t}:")
                self.indent_level += 1
                
                block = self.get_child(c, "block")
                if block and any(stmt.is_named for stmt in block.children):
                    for stmt in block.children:
                        if stmt.is_named:
                            self.visit_statement(stmt)
                else:
                    self.add_line("pass")
                    
                self.indent_level -= 1
                self.add_line("")
                
        self.indent_level -= 1

    def visit_global_method(self, c):
        name = self.get_text(self.get_child(c, "identifier"))
        params_node = self.get_child(c, "parameter_list")
        params = []
        if params_node:
            for p in self.get_children(params_node, "parameter"):
                idents = self.get_children(p, "identifier")
                p_ident = self.get_text(idents[-1]) if idents else ""
                p_type_node = self.get_child(p, "predefined_type") or self.get_child(p, "generic_name") or (idents[0] if len(idents) > 1 else None)
                p_t = self.get_text(p_type_node) if p_type_node else "object"
                params.append(f"{p_ident}: {self.map_type(p_t)}")
                
        t_node = self.get_child(c, "predefined_type") or self.get_child(c, "generic_name") or self.get_child(c, "identifier")
        ret_t = self.map_type(self.get_text(t_node)) if t_node else "Any"
        
        self.add_line(f"def {name}({', '.join(params)}) -> {ret_t}:")
        self.indent_level += 1
        
        block = self.get_child(c, "block")
        if block and any(stmt.is_named for stmt in block.children):
            for stmt in block.children:
                if stmt.is_named:
                    self.visit_statement(stmt)
        else:
            self.add_line("pass")
            
        self.indent_level -= 1
        self.add_line("")

    def visit_statement(self, node):
        if node.type == "for_statement":
            self.visit_for(node)
        elif node.type == "expression_statement":
            expr = [c for c in node.children if c.is_named][0]
            if expr.type == "assignment_expression":
                left = self.visit_expression(expr.children[0])
                right = self.visit_expression(expr.children[2])
                self.add_line(f"{left} = {right}")
            else:
                s = self.visit_expression(expr)
                if s: self.add_line(s)
        elif node.type == "local_declaration_statement":
            decl = self.get_child(node, "variable_declaration")
            type_node = self.get_child(decl, "predefined_type") or self.get_child(decl, "generic_name") or self.get_child(decl, "identifier") or self.get_child(decl, "implicit_type")
            for var_decl in self.get_children(decl, "variable_declarator"):
                ident = self.get_text(self.get_child(var_decl, "identifier"))
                named_children = [c for c in var_decl.children if c.is_named]
                val_str = self.visit_expression(named_children[1]) if len(named_children) > 1 else "None"
                t_str = self.map_type(self.get_text(type_node)) if type_node else "Any"
                self.add_line(f"{ident}: {t_str} = {val_str}")
        elif node.type == "if_statement":
            cond = self.visit_expression([c for c in node.children if c.is_named and c.type != "block"][0])
            self.add_line(f"if {cond}:")
            self.indent_level += 1
            body = node.child_by_field_name("consequence")
            if body:
                if body.type == "block":
                    for c in body.children:
                        if c.is_named: self.visit_statement(c)
                else: self.visit_statement(body)
            else: self.add_line("pass")
            self.indent_level -= 1
            
            else_node = node.child_by_field_name("alternative")
            if else_node:
                self.add_line("else:")
                self.indent_level += 1
                if else_node.type == "block":
                    for c in else_node.children:
                        if c.is_named: self.visit_statement(c)
                else: self.visit_statement(else_node)
                self.indent_level -= 1
                
        elif node.type == "while_statement":
            cond = self.visit_expression([c for c in node.children if c.is_named and c.type != "block"][0])
            self.add_line(f"while {cond}:")
            self.indent_level += 1
            body = self.get_child(node, "block")
            if body:
                for c in body.children:
                    if c.is_named: self.visit_statement(c)
            else: self.add_line("pass")
            self.indent_level -= 1
            
        elif node.type == "try_statement":
            self.add_line("try:")
            self.indent_level += 1
            body = self.get_child(node, "block")
            for c in body.children:
                if c.is_named: self.visit_statement(c)
            self.indent_level -= 1
            
            for catch_node in self.get_children(node, "catch_clause"):
                catch_decl = self.get_child(catch_node, "catch_declaration")
                err_name = "e"
                if catch_decl:
                    idents = self.get_children(catch_decl, "identifier")
                    err_name = self.get_text(idents[-1]) if idents else "e"
                self.add_line(f"except Exception as {err_name}:")
                self.indent_level += 1
                cbody = self.get_child(catch_node, "block")
                for c in cbody.children:
                    if c.is_named: self.visit_statement(c)
                self.indent_level -= 1
                
        elif node.type == "throw_statement":
            val = self.visit_expression([c for c in node.children if c.is_named][0])
            self.add_line(f"raise {val}")
        elif node.type == "break_statement": self.add_line("break")
        elif node.type == "continue_statement": self.add_line("continue")
        elif node.type == "return_statement":
            children = [c for c in node.children if c.is_named]
            if len(children) > 0:
                parts = [self.visit_expression(c) for c in children]
                expr = "".join(parts)
                self.add_line(f"return {expr}")
            else:
                self.add_line("return")

    def visit_for(self, node):
        decl = self.get_child(node, "local_declaration_statement") or self.get_child(node, "variable_declaration")
        if decl:
            if decl.type == "local_declaration_statement":
                decl = self.get_child(decl, "variable_declaration")
            decl_var = self.get_child(decl, "variable_declarator")
            var_name = self.get_text(self.get_child(decl_var, "identifier"))
            val_clause = self.get_child(decl_var, "equals_value_clause")
            start_val = self.get_text(val_clause.children[1]) if val_clause else "0"
        else:
            var_name = "i"
            start_val = "0"
            
        rel = self.get_child(node, "binary_expression")
        end_val = self.get_text(rel.children[2]) if rel else "0"
        
        self.add_line(f"for {var_name} in range({start_val}, {end_val}):")
        
        self.indent_level += 1
        block = self.get_child(node, "block")
        if block:
            for stmt in block.children:
                if stmt.is_named:
                    self.visit_statement(stmt)
        self.indent_level -= 1

    def visit_expression(self, expr):
        if expr.type == "identifier":
            return self.get_text(expr)
        elif expr.type == "integer_literal":
            return self.get_text(expr)
        elif expr.type == "real_literal":
            return self.get_text(expr)
        elif expr.type == "string_literal":
            frag = self.get_child(expr, "string_literal_content")
            return f"'{self.get_text(frag)}'" if frag else "''"
        elif expr.type == "null_literal": return "None"
        elif expr.type == "true": return "True"
        elif expr.type == "false": return "False"
        elif expr.type == "this_expression" or expr.type == "this": return "self"
        elif expr.type in ("implicit_object_creation_expression", "object_creation_expression"):
            init = self.get_child(expr, "initializer_expression")
            if init:
                # Dictionary has initializer_expression > initializer_expression
                if any(c.type == "initializer_expression" for c in init.children):
                    pairs = []
                    for c in init.children:
                        if c.type == "initializer_expression":
                            named = [x for x in c.children if x.is_named]
                            k = self.visit_expression(named[0])
                            v = self.visit_expression(named[1])
                            pairs.append(f"{k}: {v}")
                    return f"{{{', '.join(pairs)}}}"
                else:
                    elts = []
                    for c in init.children:
                        if c.is_named:
                            elts.append(self.visit_expression(c))
                    return f"[{', '.join(elts)}]"
            else:
                type_node = self.get_child(expr, "identifier") or self.get_child(expr, "generic_name") or self.get_child(expr, "predefined_type")
                if not type_node: return "[]"
                class_name = self.get_text(type_node)
                if class_name == "Exception": class_name = "Exception"
                arg_list = self.get_child(expr, "argument_list")
                args = []
                if arg_list:
                    for a in arg_list.children:
                        if a.is_named:
                            args.append(self.visit_expression(a))
                return f"{class_name}({', '.join(args)})"
        elif expr.type == "element_access_expression":
            left = self.visit_expression(expr.children[0])
            bracket = self.get_child(expr, "bracketed_argument_list")
            idx = self.visit_expression([c for c in bracket.children if c.is_named][0])
            return f"{left}[{idx}]"
        elif expr.type == "member_access_expression":
            left = self.visit_expression(expr.children[0])
            right = self.get_text(expr.children[2])
            if right == "Count" or right == "Length": return f"len({left})"
            return f"{left}.{right}"
        elif expr.type == "binary_expression":
            left = self.visit_expression(expr.children[0])
            op = self.get_text(expr.children[1])
            right = self.visit_expression(expr.children[2])
            
            if op == "==": return f"{left} == {right}" if right != "None" else f"{left} is None"
            if op == "!=": return f"{left} != {right}" if right != "None" else f"{left} is not None"
                
            return f"{left} {op} {right}"
        elif expr.type == "prefix_unary_expression":
            op = self.get_text(expr.children[0])
            val = self.visit_expression(expr.children[1])
            if op == "!": return f"not {val}"
            return f"{op}{val}"
        elif expr.type == "parenthesized_expression":
            return self.visit_expression([c for c in expr.children if c.is_named][0])
        elif expr.type == "argument":
            return self.visit_expression([c for c in expr.children if c.is_named][0])
        elif expr.type == "invocation_expression":
            func_name = self.visit_expression(expr.children[0])
            
            arg_list = self.get_child(expr, "argument_list")
            args = []
            if arg_list:
                for a in arg_list.children:
                    if a.is_named:
                        args.append(self.visit_expression(a))
            
            if func_name == "Console.WriteLine":
                if not args: return "print()"
                return f"print({', '.join(args)})"
            if func_name.endswith(".ToString"):
                return f"str({func_name[:-9]})"
            if func_name.endswith(".ContainsKey"):
                # dict.ContainsKey(key) -> key in dict
                return f"{args[0]} in {func_name[:-12]}"
                
            return f"{func_name}({', '.join(args)})"
            
        return f"/* unhandled expr {expr.type} */"

def transpile(code: str) -> str:
    import tree_sitter_c_sharp
    from tree_sitter import Language, Parser
    parser = Parser(Language(tree_sitter_c_sharp.language()))
    src_bytes = code.encode('utf8')
    tree = parser.parse(src_bytes)
    transpiler = CSharpToPyTranspiler(src_bytes)
    python_code = transpiler.transpile(tree.root_node)
    python_code += "\nif __name__ == '__main__':\n    main()\n"
    return python_code
