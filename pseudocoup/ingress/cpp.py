import json

class CppToPyTranspiler:
    def __init__(self):
        self.lines = [
            "from typing import List, Dict, Optional, Any",
            ""
        ]
        self.indent_level = 0
        self.current_class = None

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

    def find_ident(self, n):
        if not n: return None
        if n.type == "identifier": return n
        for c in n.children:
            res = self.find_ident(c)
            if res: return res
        return None

    def map_type(self, cpp_type):
        if not cpp_type: return "Any"
        if cpp_type in ("int", "double", "float"): return "int" # Simplified
        if cpp_type == "bool": return "bool"
        if "string" in cpp_type: return "str"
        if "vector" in cpp_type: return "List[Any]"
        if "unordered_map" in cpp_type or "map" in cpp_type: return "Dict[Any, Any]"
        return cpp_type.replace("*", "").replace("&", "")

    def transpile(self, root_node):
        # translation_unit -> functions, classes
        for node in root_node.children:
            if node.type == "class_specifier":
                self.visit_class(node)
            elif node.type == "function_definition":
                self.visit_global_method(node)
        return "\n".join(self.lines)

    def visit_class(self, node):
        name_node = self.get_child(node, "type_identifier")
        class_name = self.get_text(name_node)
        self.add_line(f"class {class_name}:")
        self.indent_level += 1
        
        body = self.get_child(node, "field_declaration_list")
        if body:
            has_methods = False
            for c in body.children:
                if c.type == "function_definition":
                    has_methods = True
                    self.visit_method(c, class_name)
            if not has_methods:
                self.add_line("pass")
        else:
            self.add_line("pass")
            
        self.indent_level -= 1
        self.add_line("")

    def visit_global_method(self, node):
        decl = self.get_child(node, "function_declarator")
        ident_node = self.get_child(decl, "identifier")
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

    def visit_method(self, node, class_name):
        decl = self.get_child(node, "function_declarator")
        ident_node = self.get_child(decl, "identifier")
        if not ident_node:
            # Maybe it's a constructor where identifier is nested?
            # Actually, constructor just has identifier: ClassName? No, function_declarator -> type_identifier maybe?
            # Let's check type_identifier
            ident_node = self.get_child(decl, "type_identifier")
            if not ident_node:
                # Fallback to get_text of first child
                name = self.get_text(decl.children[0]) if decl.children else "unknown"
            else:
                name = self.get_text(ident_node)
        else:
            name = self.get_text(ident_node)
            
        is_init = (name == class_name)
        params_node = self.get_child(decl, "parameter_list")
        
        params = ["self"]
        if params_node:
            for p in self.get_children(params_node, "parameter_declaration"):
                ident = self.get_text(self.find_ident(p))
                params.append(f"{ident}: Any")
                
        if is_init:
            self.add_line(f"def __init__({', '.join(params)}) -> None:")
        else:
            self.add_line(f"def {name}({', '.join(params)}) -> Any:")
            
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
            # local variables
            # e.g. int x = 0; SpaceStation* station = new SpaceStation(...);
            ident_node = self.get_child(node, "init_declarator")
            if not ident_node:
                # sometimes just identifier
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
            cond_node = self.get_child(node, "condition_clause")
            if cond_node:
                cond_expr = [c for c in cond_node.children if c.is_named][-1]
                cond = self.visit_expression(cond_expr)
            else:
                # Maybe just parentheses?
                cond_node = self.get_child(node, "parenthesized_expression")
                if cond_node:
                    cond = self.visit_expression(cond_node)
                else:
                    cond_list = [c for c in node.children if c.is_named and c.type != "compound_statement" and c.type != "if_statement"]
                    cond = self.visit_expression(cond_list[0]) if cond_list else "True"
            
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
            cond_node = self.get_child(node, "condition_clause")
            if cond_node:
                cond_expr = [c for c in cond_node.children if c.is_named][-1]
                cond = self.visit_expression(cond_expr)
            else:
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
        elif node.type == "try_statement":
            self.add_line("try:")
            self.indent_level += 1
            body = self.get_child(node, "compound_statement")
            if body:
                for c in body.children:
                    if c.is_named: self.visit_statement(c)
            self.indent_level -= 1
            catch_node = self.get_child(node, "catch_clause")
            if catch_node:
                catch_params = self.get_child(catch_node, "parameter_list")
                err_name = "e"
                if catch_params:
                    # parameter_list -> parameter_declaration
                    for p in self.get_children(catch_params, "parameter_declaration"):
                        idents = self.get_children(p, "identifier")
                        if idents: err_name = self.get_text(idents[-1])
                self.add_line(f"except Exception as {err_name}:")
                self.indent_level += 1
                cbody = self.get_child(catch_node, "compound_statement")
                if cbody:
                    for c in cbody.children:
                        if c.is_named: self.visit_statement(c)
                self.indent_level -= 1
        elif node.type in ("break_statement", "continue_statement"):
            self.add_line(node.type.split("_")[0])
        elif node.type == "throw_statement":
            expr = [c for c in node.children if c.is_named]
            if expr:
                self.add_line(f"raise {self.visit_expression(expr[0])}")
            else:
                self.add_line("raise")

    def visit_expression(self, node):
        if not node: return "None"
        if node.type == "identifier":
            return self.get_text(node)
        elif node.type == "type_identifier":
            return self.get_text(node)
        elif node.type == "primitive_type":
            return self.get_text(node)
        elif node.type == "number_literal":
            return self.get_text(node)
        elif node.type == "string_literal":
            # C++ string literal includes quotes, but might have multiple string_content children
            contents = self.get_children(node, "string_content")
            if contents:
                return '"' + "".join([self.get_text(c) for c in contents]) + '"'
            return self.get_text(node)
        elif node.type == "true": return "True"
        elif node.type == "false": return "False"
        elif node.type == "null": return "None"
        elif node.type == "nullptr": return "None"
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
            
            if func == "std::to_string":
                return f"str({args[0]})"
            
            # std::cout << handling
            # wait, std::cout is a binary_expression usually (e.g. std::cout << "foo")
            # so call_expression won't catch it unless we have it inside something else
            return f"{func}({', '.join(args)})"
        elif node.type == "new_expression":
            type_node = self.get_child(node, "type_identifier")
            args_node = self.get_child(node, "argument_list")
            args = []
            if args_node:
                for c in args_node.children:
                    if c.is_named: args.append(self.visit_expression(c))
            return f"{self.get_text(type_node)}({', '.join(args)})"
        elif node.type == "subscript_expression":
            left = self.visit_expression(node.children[0])
            arg_list = self.get_child(node, "subscript_argument_list")
            right = self.visit_expression([c for c in arg_list.children if c.is_named][-1]) if arg_list else "0"
            return f"{left}[{right}]"
        elif node.type == "parenthesized_expression":
            return f"({self.visit_expression(node.children[1])})"
        elif node.type == "compound_literal_expression":
            # For lists and dicts like std::vector<std::string>{"Command", "Life Support"}
            # The children are the type and initializer_list
            init_list = self.get_child(node, "initializer_list")
            if init_list:
                # Is it a dict? dicts have nested initializer_lists like {{"Oxygen", 95}}
                elements = [c for c in init_list.children if c.is_named]
                if elements and elements[0].type == "initializer_list":
                    # Dict!
                    pairs = []
                    for e in elements:
                        subs = [c for c in e.children if c.is_named]
                        if len(subs) >= 2:
                            pairs.append(f"{self.visit_expression(subs[0])}: {self.visit_expression(subs[1])}")
                    return f"{{{', '.join(pairs)}}}"
                else:
                    # List!
                    items = [self.visit_expression(e) for e in elements]
                    return f"[{', '.join(items)}]"
            
        return self.get_text(node)

def transpile(code: str) -> str:
    import tree_sitter_cpp
    from tree_sitter import Language, Parser
    
    parser = Parser(Language(tree_sitter_cpp.language()))
    tree = parser.parse(code.encode('utf8'))
    
    transpiler = CppToPyTranspiler()
    res = transpiler.transpile(tree.root_node)
    
    # Custom post-processing for std::cout since it's parsed as nested binary_expressions
    final_lines = []
    for line in res.split("\n"):
        if "std::cout" in line:
            # Simple heuristic since std::cout << "foo" << "bar" << std::endl
            # becomes std::cout << "foo" << "bar" << std::endl
            # we just string split
            parts = line.split(" << ")
            args = []
            for p in parts[1:]:
                p = p.strip().strip(";")
                if p == "std::endl": continue
                args.append(p)
            final_lines.append(line[:line.find("std::cout")] + "print(" + " + ".join(args) + ")")
        elif "std::runtime_error" in line:
            final_lines.append(line.replace("std::runtime_error", "Exception"))
        else:
            final_lines.append(line)
            
    # Fix .size() properly
    import re
    res = "\n".join(final_lines)
    res = re.sub(r'([a-zA-Z0-9_\.\[\]]+)\.size\(\)', r'len(\1)', res)
    # Fix dict count logic `.count(X) > 0` -> `X in dict`
    res = re.sub(r'\(([a-zA-Z0-9_\.\[\]]+)\.count\((.*?)\) > 0\)', r'\2 in \1', res)
    
    return res
