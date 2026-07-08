import json

class JavaToPyTranspiler:
    def __init__(self):
        self.lines = [
            "from typing import List, Dict, Optional, Any",
            ""
        ]
        self.indent_level = 0
        self.properties = {}

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

    def transpile(self, root_node):
        for node in root_node.children:
            if node.type == "class_declaration":
                self.visit_class(node)
                
        return "\n".join(self.lines)

    def visit_class(self, node):
        name_node = self.get_child(node, "identifier")
        class_name = self.get_text(name_node)
        
        if class_name == "Main":
            self.add_line("def main() -> None:")
            self.indent_level += 1
            body = self.get_child(node, "class_body")
            has_stmts = False
            if body:
                for method in self.get_children(body, "method_declaration"):
                    name = self.get_text(self.get_child(method, "identifier"))
                    if name == "main":
                        mbody = self.get_child(method, "block")
                        if mbody:
                            for c in mbody.children:
                                if c.is_named:
                                    self.visit_statement(c)
                                    has_stmts = True
            if not has_stmts:
                self.add_line("pass")
            self.indent_level -= 1
            self.add_line("")
            self.add_line("if __name__ == '__main__':")
            self.indent_level += 1
            self.add_line("main()")
            self.indent_level -= 1
            return
            
        self.add_line(f"class {class_name}:")
        self.indent_level += 1
        
        body = self.get_child(node, "class_body")
        if body:
            fields = self.get_children(body, "field_declaration")
            if fields:
                for f in fields:
                    t_str = self.visit_expression(self.get_child(f, "type_identifier"))
                    if not t_str: t_str = self.visit_expression(self.get_child(f, "generic_type"))
                    if not t_str: t_str = "Any"
                    
                    decls = self.get_children(f, "variable_declarator")
                    for d in decls:
                        ident = self.get_text(self.get_child(d, "identifier"))
                        self.add_line(f"{ident}: Any")
                self.add_line("")
                
            has_methods = False
            for m in body.children:
                if m.type == "constructor_declaration":
                    self.visit_method(m, is_init=True)
                    has_methods = True
                elif m.type == "method_declaration":
                    self.visit_method(m)
                    has_methods = True
            if not has_methods and not fields:
                self.add_line("pass")
        else:
            self.add_line("pass")
        self.indent_level -= 1
        self.add_line("")

    def visit_method(self, node, is_init=False):
        name = "__init__" if is_init else self.get_text(self.get_child(node, "identifier"))
        
        params_node = self.get_child(node, "formal_parameters")
        params = ["self"]
        if params_node:
            for p in self.get_children(params_node, "formal_parameter"):
                ident = self.get_text(self.get_child(p, "identifier"))
                params.append(f"{ident}: Any")
                
        if is_init:
            self.add_line(f"def {name}({', '.join(params)}) -> None:")
        else:
            self.add_line(f"def {name}({', '.join(params)}) -> Any:")
            
        self.indent_level += 1
        body = self.get_child(node, "block")
        if not body:
            body = self.get_child(node, "constructor_body")
            
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
        if node.type == "local_variable_declaration":
            var_decls = self.get_children(node, "variable_declarator")
            for var_decl in var_decls:
                ident = self.get_child(var_decl, "identifier")
                val_node = None
                for i, c in enumerate(var_decl.children):
                    if c.type == "=" and i+1 < len(var_decl.children):
                        val_node = var_decl.children[i+1]
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
            cond_node = self.get_child(node, "parenthesized_expression")
            cond = self.visit_expression(cond_node) if cond_node else "True"
            
            self.add_line(f"while {cond}:")
            self.indent_level += 1
            body = node.child_by_field_name("body")
            if body:
                if body.type == "block":
                    for c in body.children:
                        if c.is_named: self.visit_statement(c)
                else: self.visit_statement(body)
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
        elif node.type == "try_statement":
            self.add_line("try:")
            self.indent_level += 1
            body = self.get_child(node, "block")
            if body:
                for c in body.children:
                    if c.is_named: self.visit_statement(c)
            self.indent_level -= 1
            for catch_clause in self.get_children(node, "catch_clause"):
                param = self.get_child(catch_clause, "catch_formal_parameter")
                n = "e"
                if param: n = self.get_text(self.get_child(param, "identifier"))
                self.add_line(f"except Exception as {n}:")
                self.indent_level += 1
                cbody = self.get_child(catch_clause, "block")
                if cbody:
                    for c in cbody.children:
                        if c.is_named: self.visit_statement(c)
                self.indent_level -= 1
        elif node.type == "throw_statement":
            expr = [c for c in node.children if c.is_named]
            if expr:
                self.add_line(f"raise {self.visit_expression(expr[0])}")

    def visit_expression(self, node):
        if not node: return "None"
        if node.type == "identifier":
            return self.get_text(node)
        elif node.type == "type_identifier":
            return self.get_text(node)
        elif node.type in ("decimal_integer_literal", "decimal_floating_point_literal", "hex_integer_literal"):
            return self.get_text(node)
        elif node.type == "string_literal":
            return self.get_text(node)
        elif node.type == "true": return "True"
        elif node.type == "false": return "False"
        elif node.type == "null_literal": return "None"
        elif node.type == "this": return "self"
        elif node.type == "assignment_expression":
            left = self.visit_expression(node.children[0])
            op = self.get_text(node.children[1])
            right = self.visit_expression(node.children[2])
            return f"{left} {op} {right}"
        elif node.type == "field_access":
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
        elif node.type == "method_invocation":
            obj = node.child_by_field_name("object")
            name = node.child_by_field_name("name")
            
            if not name:
                name = self.get_child(node, "identifier")
            
            func_name = self.get_text(name) if name else ""
            obj_name = self.visit_expression(obj) if obj else None
            
            full_func = f"{obj_name}.{func_name}" if obj_name else func_name

            args_node = node.child_by_field_name("arguments")
            args = []
            if args_node:
                for c in args_node.children:
                    if c.is_named: args.append(self.visit_expression(c))
            
            if "System.out.println" in full_func or func_name == "println":
                return f"print({args[0]})"
            if full_func == "String.valueOf":
                return f"str({args[0]})"
            if func_name == "size":
                return f"len({obj_name})"
            if func_name == "containsKey":
                return f"{args[0]} in {obj_name}"
            if func_name == "get":
                return f"{obj_name}[{args[0]}]"
            if full_func == "List.of":
                return f"[{', '.join(args)}]"
            if full_func == "Map.of":
                pairs = []
                for i in range(0, len(args), 2):
                    if i+1 < len(args):
                        pairs.append(f"{args[i]}: {args[i+1]}")
                return f"{{{', '.join(pairs)}}}"
                
            if obj_name:
                return f"{obj_name}.{func_name}({', '.join(args)})"
            return f"{func_name}({', '.join(args)})"
        elif node.type == "object_creation_expression":
            t_node = node.child_by_field_name("type")
            if not t_node: t_node = self.get_child(node, "type_identifier")
            if not t_node: t_node = self.get_child(node, "generic_type")
            t_name = self.get_text(t_node)
            
            args_node = node.child_by_field_name("arguments")
            args = []
            if args_node:
                for c in args_node.children:
                    if c.is_named: args.append(self.visit_expression(c))
                    
            if "ArrayList" in t_name or "HashMap" in t_name:
                if args:
                    return args[0]
                if "ArrayList" in t_name: return "[]"
                return "{}"
                
            return f"{t_name}({', '.join(args)})"
        elif node.type == "parenthesized_expression":
            return f"({self.visit_expression(node.children[1])})"
        return self.get_text(node)

def transpile(code: str) -> str:
    import tree_sitter_java
    from tree_sitter import Language, Parser
    
    parser = Parser(Language(tree_sitter_java.language()))
    tree = parser.parse(code.encode('utf8'))
    
    transpiler = JavaToPyTranspiler()
    res = transpiler.transpile(tree.root_node)
    
    return res
