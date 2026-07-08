import json

class CToPyTranspiler:
    def __init__(self):
        self.lines = [
            "from typing import List, Dict, Optional, Any",
            ""
        ]
        self.indent_level = 0
        self.structs = []

    def add_line(self, text):
        if text.strip() == "":
            self.lines.append("")
        else:
            self.lines.append("    " * self.indent_level + text)

    def get_text(self, node):
        return node.text.decode('utf8') if node else ""

    def get_child(self, node, type_name):
        for c in node.children:
            if c.type == type_name: return c
        return None

    def get_children(self, node, type_name):
        return [c for c in node.children if c.type == type_name]

    def find_node(self, n, type_name):
        if not n: return None
        if n.type == type_name: return n
        for c in n.children:
            res = self.find_node(c, type_name)
            if res: return res
        return None

    def find_ident(self, n):
        if not n: return None
        if n.type == "identifier" or n.type == "field_identifier": return n
        for c in n.children:
            res = self.find_ident(c)
            if res: return res
        return None

    def map_type(self, c_type):
        if not c_type: return "Any"
        if c_type in ("int", "double", "float"): return "int"
        if c_type == "bool": return "bool"
        if "char" in c_type: return "str"
        if "List" in c_type: return "List[Any]"
        if "Dict" in c_type: return "Dict[Any, Any]"
        return c_type.replace("*", "")

    def transpile(self, root_node):
        # translation_unit -> type_definition (structs), function_definition
        # 1st Pass: Collect structs
        for node in root_node.children:
            if node.type == "type_definition":
                struct_spec = self.get_child(node, "struct_specifier")
                if struct_spec:
                    ident = self.get_child(struct_spec, "type_identifier")
                    if ident:
                        self.structs.append(self.get_text(ident))
        
        # 2nd Pass: Emit classes
        for s_name in self.structs:
            self.add_line(f"class {s_name}:")
            self.indent_level += 1
            has_methods = False
            for node in root_node.children:
                if node.type == "function_definition":
                    decl = self.find_node(node, "function_declarator")
                    if not decl: continue
                    ident_node = self.find_ident(decl)
                    func_name = self.get_text(ident_node)
                    if func_name.startswith(s_name + "_"):
                        has_methods = True
                        self.visit_method(node, s_name, func_name[len(s_name)+1:])
            if not has_methods:
                self.add_line("pass")
                self.add_line("")
            self.indent_level -= 1
        
        # 3rd Pass: Emit global functions
        for node in root_node.children:
            if node.type == "function_definition":
                decl = self.find_node(node, "function_declarator")
                if not decl: continue
                ident_node = self.find_ident(decl)
                func_name = self.get_text(ident_node)
                is_method = False
                for s in self.structs:
                    if func_name.startswith(s + "_"):
                        is_method = True
                        break
                if not is_method:
                    self.visit_global_method(node)
                    
        return "\n".join(self.lines)

    def visit_global_method(self, node):
        decl = self.find_node(node, "function_declarator")
        ident_node = self.find_ident(decl)
        name = self.get_text(ident_node)
        
        is_main = (name == "main")
        params_node = self.get_child(decl, "parameter_list")
        
        params = []
        if params_node:
            for p in self.get_children(params_node, "parameter_declaration"):
                ident = self.get_text(self.find_ident(p))
                params.append(f"{ident}: Any")
                
        if is_main:
            self.add_line("def main() -> None:")
        else:
            self.add_line(f"def {name}({', '.join(params)}) -> Any:")
            
        self.indent_level += 1
        body = self.get_child(node, "compound_statement")
        if body:
            for c in body.children:
                if c.is_named: self.visit_statement(c)
        else:
            self.add_line("pass")
        self.indent_level -= 1
        self.add_line("")
        
        if is_main:
            self.add_line("if __name__ == '__main__':")
            self.indent_level += 1
            self.add_line("main()")
            self.indent_level -= 1

    def visit_method(self, node, class_name, short_name):
        decl = self.find_node(node, "function_declarator")
        params_node = self.find_node(decl, "parameter_list")
        
        params = []
        if params_node:
            for p in self.get_children(params_node, "parameter_declaration"):
                ident = self.get_text(self.find_ident(p))
                if ident != "self":
                    params.append(f"{ident}: Any")
                
        if short_name == "__init__":
            self.add_line(f"def __init__(self, {', '.join(params)}) -> None:")
            # Fix case where params is empty except self, no trailing comma needed
            if not params:
                self.lines[-1] = "    " * self.indent_level + "def __init__(self) -> None:"
        else:
            if not params:
                self.add_line(f"def {short_name}(self) -> Any:")
            else:
                self.add_line(f"def {short_name}(self, {', '.join(params)}) -> Any:")
            
        self.indent_level += 1
        body = self.get_child(node, "compound_statement")
        if body:
            has_stmts = False
            for c in body.children:
                if c.is_named:
                    self.visit_statement(c)
                    has_stmts = True
            if not has_stmts:
                self.add_line("pass")
        else:
            self.add_line("pass")
        self.indent_level -= 1
        self.add_line("")

    def visit_statement(self, node):
        if node.type == "declaration":
            ident_node = self.get_child(node, "init_declarator")
            if not ident_node:
                ident_node = self.get_child(node, "identifier")
            
            if ident_node and ident_node.type == "init_declarator":
                ident = self.find_ident(ident_node)
                val_node = None
                for i, c in enumerate(ident_node.children):
                    if c.type == "=" and i+1 < len(ident_node.children):
                        val_node = ident_node.children[i+1]
                        break
                
                name = self.get_text(ident) if ident else "unknown"
                val = self.visit_expression(val_node) if val_node else "None"
                self.add_line(f"{name} = {val}")
        elif node.type == "expression_statement":
            expr = [c for c in node.children if c.is_named]
            if expr:
                val = self.visit_expression(expr[0])
                if val: self.add_line(val)
        elif node.type == "if_statement":
            cond_node = self.get_child(node, "parenthesized_expression")
            cond = self.visit_expression(cond_node) if cond_node else "True"
            
            # Check for Pseudo_TRY
            if cond == "(Pseudo_TRY())":
                self.add_line("try:")
                self.indent_level += 1
                body = node.child_by_field_name("consequence")
                if body:
                    if body.type == "compound_statement":
                        for c in body.children:
                            if c.is_named: self.visit_statement(c)
                    else: self.visit_statement(body)
                else: self.add_line("pass")
                self.indent_level -= 1
                
                else_node = node.child_by_field_name("alternative")
                if else_node:
                    else_body = [c for c in else_node.children if c.is_named][-1]
                    if else_body.type == "if_statement":
                        e_cond = self.visit_expression(self.get_child(else_body, "parenthesized_expression"))
                        if e_cond and "Pseudo_CATCH" in e_cond:
                            # extract err var e.g. (Pseudo_CATCH(&e)) -> e
                            err_var = "e"
                            if "&" in e_cond:
                                err_var = e_cond[e_cond.find("&")+1 : e_cond.find(")")]
                            self.add_line(f"except Exception as {err_var}:")
                            self.indent_level += 1
                            cbody = else_body.child_by_field_name("consequence")
                            if cbody:
                                if cbody.type == "compound_statement":
                                    for c in cbody.children:
                                        if c.is_named: self.visit_statement(c)
                                else: self.visit_statement(cbody)
                            self.indent_level -= 1
                return

            self.add_line(f"if {cond}:")
            self.indent_level += 1
            body = node.child_by_field_name("consequence")
            if body:
                if body.type == "compound_statement":
                    for c in body.children:
                        if c.is_named: self.visit_statement(c)
                else: self.visit_statement(body)
            else: self.add_line("pass")
            self.indent_level -= 1
            
            else_node = node.child_by_field_name("alternative")
            if else_node:
                self.add_line("else:")
                self.indent_level += 1
                else_body = [c for c in else_node.children if c.is_named][-1]
                if else_body.type == "compound_statement":
                    for c in else_body.children:
                        if c.is_named: self.visit_statement(c)
                else: self.visit_statement(else_body)
                self.indent_level -= 1
        elif node.type == "while_statement":
            cond_node = self.get_child(node, "parenthesized_expression")
            cond = self.visit_expression(cond_node) if cond_node else "True"
                
            self.add_line(f"while {cond}:")
            self.indent_level += 1
            body = self.get_child(node, "compound_statement")
            if body:
                for c in body.children:
                    if c.is_named: self.visit_statement(c)
            else: self.add_line("pass")
            self.indent_level -= 1
        elif node.type == "return_statement":
            exprs = [c for c in node.children if c.is_named]
            if exprs:
                self.add_line(f"return {self.visit_expression(exprs[0])}")
            else:
                self.add_line("return")
        elif node.type in ("break_statement", "continue_statement"):
            self.add_line(node.type.split("_")[0])

    def visit_expression(self, node):
        if not node: return "None"
        if node.type == "identifier" or node.type == "field_identifier":
            return self.get_text(node)
        elif node.type == "type_identifier":
            return self.get_text(node)
        elif node.type == "primitive_type":
            return self.get_text(node)
        elif node.type == "number_literal":
            return self.get_text(node)
        elif node.type == "string_literal":
            contents = self.get_children(node, "string_content")
            if contents:
                return '"' + "".join([self.get_text(c) for c in contents]) + '"'
            return self.get_text(node)
        elif node.type == "true": return "True"
        elif node.type == "false": return "False"
        elif node.type == "null": return "None"
        elif node.type == "NULL": return "None"
        elif node.type == "this": return "self"
        elif node.type == "assignment_expression":
            left = self.visit_expression(node.children[0])
            op = self.get_text(node.children[1])
            right = self.visit_expression(node.children[2])
            return f"{left} {op} {right}"
        elif node.type == "field_expression":
            left = self.visit_expression(node.children[0])
            right = self.get_text(node.children[2])
            return f"{left}.{right}"
        elif node.type == "binary_expression":
            left = self.visit_expression(node.children[0])
            op = self.get_text(node.children[1])
            right = self.visit_expression(node.children[2])
            return f"{left} {op} {right}"
        elif node.type == "unary_expression":
            op = self.get_text(node.children[0])
            right = self.visit_expression(node.children[1])
            if op == "!": return f"not {right}"
            return f"{op}{right}"
        elif node.type == "call_expression":
            func = self.visit_expression(node.children[0])
            args_node = self.get_child(node, "argument_list")
            args = []
            if args_node:
                for c in args_node.children:
                    if c.is_named: args.append(self.visit_expression(c))
            
            if func == "printf":
                return f"print({args[0]})"
            if func == "raise_error":
                return f"raise {args[0]}"
            if func == "Exception_new":
                return f"Exception({args[0]})"
            if func == "List_length":
                return f"len({args[0]})"
            if func == "Dict_contains":
                return f"{args[1]} in {args[0]}"
            if func.endswith("_new"):
                # Astronaut_new("foo") -> Astronaut("foo")
                return f"{func[:-4]}({', '.join(args)})"
                
            return f"{func}({', '.join(args)})"
        elif node.type == "subscript_expression":
            left = self.visit_expression(node.children[0])
            right = self.visit_expression([c for c in node.children if c.is_named][-1])
            return f"{left}[{right}]"
        elif node.type == "parenthesized_expression":
            return f"({self.visit_expression(node.children[1])})"
        elif node.type == "compound_literal_expression":
            init_list = self.get_child(node, "initializer_list")
            if init_list:
                elements = [c for c in init_list.children if c.is_named]
                if elements and elements[0].type == "initializer_list":
                    pairs = []
                    for e in elements:
                        subs = [c for c in e.children if c.is_named]
                        if len(subs) >= 2:
                            pairs.append(f"{self.visit_expression(subs[0])}: {self.visit_expression(subs[1])}")
                    return f"{{{', '.join(pairs)}}}"
                else:
                    items = [self.visit_expression(e) for e in elements]
                    return f"[{', '.join(items)}]"
        elif node.type == "pointer_expression":
            return self.visit_expression(node.children[1])
            
        return self.get_text(node)

def transpile(code: str) -> str:
    import tree_sitter_c
    from tree_sitter import Language, Parser
    
    parser = Parser(Language(tree_sitter_c.language()))
    tree = parser.parse(code.encode('utf8'))
    
    transpiler = CToPyTranspiler()
    res = transpiler.transpile(tree.root_node)
    
    return res
