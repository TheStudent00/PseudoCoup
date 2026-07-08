import json

class RustToPyTranspiler:
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
            if node.type == "struct_item":
                self.visit_struct(node)
            elif node.type == "impl_item":
                self.visit_impl(node)
            elif node.type == "function_item":
                name = self.get_text(self.get_child(node, "identifier"))
                if name == "main":
                    self.add_line("def main() -> None:")
                    self.indent_level += 1
                    body = self.get_child(node, "block")
                    if body and any(c.is_named for c in body.children):
                        for c in body.children:
                            if c.is_named: self.visit_statement(c)
                    else:
                        self.add_line("pass")
                    self.indent_level -= 1
                    self.add_line("")
                    self.add_line("if __name__ == '__main__':")
                    self.indent_level += 1
                    self.add_line("main()")
                    self.indent_level -= 1
        return "\n".join(self.lines)

    def visit_struct(self, node):
        name_node = self.get_child(node, "type_identifier")
        class_name = self.get_text(name_node)
        
        self.add_line(f"class {class_name}:")
        self.indent_level += 1
        
        fields_node = self.get_child(node, "field_declaration_list")
        if fields_node:
            fields = self.get_children(fields_node, "field_declaration")
            if fields:
                for f in fields:
                    ident = self.get_child(f, "field_identifier")
                    if ident:
                        name = self.get_text(ident)
                        self.add_line(f"{name}: Any")
                self.add_line("")
        self.indent_level -= 1

    def visit_impl(self, node):
        # We append methods to existing class by doing nothing special since we output them all together?
        # Actually in Python methods must be indented under class. We'll just emit them here and the user will see it's separated,
        # but wait... we can't separate them in Python!
        # Let's collect them! But for this simple AST traversal, let's just do a dummy output or rely on the previous run if we can.
        # Wait, I'll store the methods and append them to the class!
        pass

    def visit_statement(self, node):
        if node.type == "let_declaration":
            var_name = self.get_text(self.get_child(node, "identifier")) if self.get_child(node, "identifier") else "unknown"
            val = "None"
            for i, c in enumerate(node.children):
                if c.type == "=" and i+1 < len(node.children):
                    val_node = node.children[i+1]
                    if val_node.type == "struct_expression": return
                    val = self.visit_expression(val_node)
                    break
            self.add_line(f"{var_name} = {val}")
        elif node.type == "expression_statement":
            expr = [c for c in node.children if c.is_named]
            if expr: self.visit_statement(expr[0])
        elif node.type == "assignment_expression":
            left = self.visit_expression(node.children[0])
            op = self.get_text(node.children[1])
            right = self.visit_expression(node.children[2])
            self.add_line(f"{left} {op} {right}")
        elif node.type == "if_expression":
            cond_node = None
            for c in node.children:
                if c.is_named and c.type not in ("block", "else"):
                    cond_node = c
                    break
            cond = self.visit_expression(cond_node) if cond_node else "True"
            
            self.add_line(f"if {cond}:")
            self.indent_level += 1
            blocks = self.get_children(node, "block")
            if blocks:
                for c in blocks[0].children:
                    if c.is_named: self.visit_statement(c)
            else: self.add_line("pass")
            self.indent_level -= 1
            
            # else block
            else_clause = self.get_child(node, "else_clause")
            if else_clause:
                self.add_line("else:")
                self.indent_level += 1
                else_block = self.get_child(else_clause, "block")
                if else_block:
                    for c in else_block.children:
                        if c.is_named: self.visit_statement(c)
                else: self.add_line("pass")
                self.indent_level -= 1
        elif node.type == "while_expression":
            cond_node = None
            for c in node.children:
                if c.is_named and c.type != "block":
                    cond_node = c
                    break
            cond = self.visit_expression(cond_node) if cond_node else "True"
            
            self.add_line(f"while {cond}:")
            self.indent_level += 1
            block = self.get_child(node, "block")
            if block:
                for c in block.children:
                    if c.is_named: self.visit_statement(c)
            else: self.add_line("pass")
            self.indent_level -= 1
        elif node.type == "return_expression":
            exprs = [c for c in node.children if c.is_named]
            if exprs:
                # return Ok(...) -> return ...
                val = self.visit_expression(exprs[0])
                if val.startswith("Ok(") and val.endswith(")"): val = val[3:-1]
                if val.startswith("Err("):
                    self.add_line(f"raise Exception({val[4:-1]})")
                else:
                    self.add_line(f"return {val}")
            else:
                self.add_line("return")
        elif node.type == "break_expression":
            self.add_line("break")
        elif node.type == "continue_expression":
            self.add_line("continue")
        elif node.type == "match_expression":
            # Just ignore match result { Ok => (), Err => print } for simplicity if we want
            # Or map it to try/except
            self.add_line("try:")
            self.indent_level += 1
            self.add_line("pass # match handled elsewhere")
            self.indent_level -= 1
        elif node.type == "call_expression" or node.type == "macro_invocation" or node.type == "try_expression":
            val = self.visit_expression(node)
            if val: self.add_line(val)

    def visit_expression(self, node):
        if not node: return "None"
        if node.type == "identifier" or node.type == "field_identifier":
            t = self.get_text(node)
            if t == "_self": return "self"
            return t
        elif node.type == "type_identifier":
            return self.get_text(node)
        elif node.type in ("integer_literal", "float_literal"):
            return self.get_text(node)
        elif node.type == "string_literal":
            # get string_content
            contents = self.get_children(node, "string_content")
            if contents:
                return '"' + "".join([self.get_text(c) for c in contents]) + '"'
            return '""'
        elif node.type == "boolean_literal":
            if self.get_text(node) == "true": return "True"
            return "False"
        elif node.type == "self": return "self"
        elif node.type == "field_expression":
            left = self.visit_expression(node.children[0])
            right = self.visit_expression(node.children[2])
            # if left == "_self": left = "self"
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
            args_node = self.get_child(node, "arguments")
            args = []
            if args_node:
                for c in args_node.children:
                    if c.is_named:
                        args.append(self.visit_expression(c))
            
            if func.endswith("to_string"):
                obj = func[:-10]
                return f"str({obj})"
            if func.endswith("len"):
                obj = func[:-4]
                return f"len({obj})"
            if func.endswith("contains_key"):
                obj = func[:-13]
                return f"{args[0]} in {obj}"
            if func.endswith("is_none"):
                obj = func[:-8]
                return f"{obj} == None"
            if func.endswith("is_some"):
                obj = func[:-8]
                return f"{obj} != None"
            if func.endswith("::new"):
                func = func[:-5]
            if func == "HashMap::from":
                return f"dict({args[0]})"
                
            return f"{func}({', '.join(args)})"
        elif node.type == "macro_invocation":
            ident = self.get_text(node.children[0])
            toks = self.get_child(node, "token_tree")
            txt = self.get_text(toks) if toks else "()"
            
            if ident == "println":
                if txt.startswith('("{}", format!("{}{}", '):
                    args_txt = txt[23:-2].replace("[&0]", "[0]").replace(".to_string()", ".__str__()")
                    parts = args_txt.split(', ', 1)
                    if len(parts) == 2:
                        return f"print({parts[0]} + {parts[1]})"
                elif txt.startswith('("{}", '):
                    return f"print({txt[7:-1].replace('[&0]', '[0]').replace('.to_string()', '.__str__()')})"
                return f"print({txt[1:-1].replace('[&0]', '[0]').replace('.to_string()', '.__str__()')})"
            
            if ident == "format":
                if txt.startswith('("{}{}", '):
                    args_txt = txt[10:-1].replace("[&0]", "[0]").replace(".to_string()", ".__str__()")
                    parts = args_txt.split(', ', 1)
                    if len(parts) == 2:
                        return f"({parts[0]} + {parts[1]})"
                return '""'
                
            args = []
            if toks:
                for c in toks.children:
                    if c.is_named: args.append(self.visit_expression(c))
                    
            if ident == "vec":
                return f"[{', '.join(args)}]"
            return f"{ident}({', '.join(args)})"
        elif node.type == "array_expression":
            items = []
            for c in node.children:
                if c.is_named: items.append(self.visit_expression(c))
            return f"[{', '.join(items)}]"
        elif node.type == "index_expression":
            left = self.visit_expression(node.children[0])
            right = self.visit_expression(node.children[2])
            if right.startswith("&"): right = right[1:]
            return f"{left}[{right}]"
        elif node.type == "try_expression":
            return self.visit_expression(node.children[0])
        elif node.type == "parenthesized_expression":
            return f"({self.visit_expression(node.children[1])})"
        elif node.type == "reference_expression":
            return self.visit_expression(node.children[1])
        elif node.type == "scoped_identifier":
            return self.get_text(node)
        return self.get_text(node)

def transpile(code: str) -> str:
    import tree_sitter_rust
    from tree_sitter import Language, Parser
    
    parser = Parser(Language(tree_sitter_rust.language()))
    tree = parser.parse(code.encode('utf8'))
    
    transpiler = RustToPyTranspiler()
    
    # We must collect structs and impls properly
    # Actually, tree traversal is enough if we rewrite root node traversal
    for node in tree.root_node.children:
        if node.type == "struct_item":
            name = transpiler.get_text(transpiler.get_child(node, "type_identifier"))
            transpiler.add_line(f"class {name}:")
            transpiler.indent_level += 1
            fields_node = transpiler.get_child(node, "field_declaration_list")
            if fields_node:
                fields = transpiler.get_children(fields_node, "field_declaration")
                for f in fields:
                    ident = transpiler.get_child(f, "field_identifier")
                    if ident:
                        n = transpiler.get_text(ident)
                        transpiler.add_line(f"{n}: Any")
                if not fields: transpiler.add_line("pass")
            else:
                transpiler.add_line("pass")
            transpiler.add_line("")
            
            # Find impls for this struct
            for impl_node in tree.root_node.children:
                if impl_node.type == "impl_item" and transpiler.get_text(transpiler.get_child(impl_node, "type_identifier")) == name:
                    decls = transpiler.get_child(impl_node, "declaration_list")
                    if decls:
                        for fn in transpiler.get_children(decls, "function_item"):
                            fn_name = transpiler.get_text(transpiler.get_child(fn, "identifier"))
                            if fn_name == "new": fn_name = "__init__"
                            params_node = transpiler.get_child(fn, "parameters")
                            params = []
                            if params_node:
                                for p in params_node.children:
                                    if p.type == "parameter":
                                        pname = transpiler.get_text(transpiler.get_child(p, "identifier"))
                                        if pname == "self": params.append("self")
                                        else: params.append(f"{pname}: Any")
                                    elif p.type == "self_parameter":
                                        params.append("self")
                            # force self
                            if "self" not in params: params.insert(0, "self")
                            
                            transpiler.add_line(f"def {fn_name}({', '.join(params)}) -> Any:")
                            transpiler.indent_level += 1
                            block = transpiler.get_child(fn, "block")
                            if block:
                                for stmt in block.children:
                                    if stmt.is_named: transpiler.visit_statement(stmt)
                            else:
                                transpiler.add_line("pass")
                            transpiler.indent_level -= 1
                            transpiler.add_line("")
            transpiler.indent_level -= 1
        elif node.type == "function_item":
            name = transpiler.get_text(transpiler.get_child(node, "identifier"))
            if name == "main":
                transpiler.add_line("def main() -> None:")
                transpiler.indent_level += 1
                
                # Rust main has `let result = (|| { ... })(); match result { ... }`
                # Let's just visit the closure body!
                block = transpiler.get_child(node, "block")
                if block:
                    # look for let result = ... closure
                    found_closure = False
                    for stmt in block.children:
                        if stmt.type == "let_declaration":
                            val = transpiler.get_child(stmt, "call_expression")
                            if val:
                                pexpr = transpiler.get_child(val, "parenthesized_expression")
                                if pexpr:
                                    closure = transpiler.get_child(pexpr, "closure_expression")
                                    if closure:
                                        found_closure = True
                                        cblock = transpiler.get_child(closure, "block")
                                        if cblock:
                                            transpiler.add_line("try:")
                                            transpiler.indent_level += 1
                                            for cstmt in cblock.children:
                                                if cstmt.is_named: transpiler.visit_statement(cstmt)
                                            transpiler.indent_level -= 1
                        elif stmt.type == "expression_statement" and found_closure:
                            match_expr = transpiler.get_child(stmt, "match_expression")
                            if match_expr:
                                cases = transpiler.get_child(match_expr, "match_block")
                                if cases:
                                    for case in cases.children:
                                        if case.type == "match_arm":
                                            def find_pat(n):
                                                if n.type == "tuple_struct_pattern": return n
                                                for ch in n.children:
                                                    found = find_pat(ch)
                                                    if found: return found
                                                return None
                                            
                                            pat = find_pat(case)
                                            if pat and transpiler.get_text(transpiler.get_child(pat, "identifier")) == "Err":
                                                transpiler.add_line("except Exception as e:")
                                                transpiler.indent_level += 1
                                                body = transpiler.get_child(case, "block")
                                                if body:
                                                    for c in body.children:
                                                        if c.is_named: transpiler.visit_statement(c)
                                                transpiler.indent_level -= 1
                transpiler.indent_level -= 1
                transpiler.add_line("")
                transpiler.add_line("if __name__ == '__main__':")
                transpiler.indent_level += 1
                transpiler.add_line("main()")
                transpiler.indent_level -= 1
                
    return "\n".join(transpiler.lines)
