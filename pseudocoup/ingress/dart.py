import tree_sitter_dart as tsdart
from tree_sitter import Language, Parser
import json

class Ledger:
    def __init__(self):
        self.entries = []
    
    def log(self, dart_node, py_target, reason):
        entry = {"dart_node": dart_node, "py_target": py_target, "reason": reason}
        if entry not in self.entries:
            self.entries.append(entry)
    
    def save(self, path):
        with open(path, 'w') as f:
            json.dump(self.entries, f, indent=2)

class DartToPyTranspiler:
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

    def map_type(self, dart_type):
        dart_type = dart_type.strip()
        if dart_type == "int": return "int"
        if dart_type == "String": return "str"
        if dart_type == "void": return "None"
        if dart_type == "bool": return "bool"
        if dart_type.endswith("?"): return f"Optional[{self.map_type(dart_type[:-1])}]"
        if dart_type.startswith("List<"): return f"List[{self.map_type(dart_type[5:-1])}]"
        if dart_type.startswith("Map<"):
            inner = dart_type[4:-1].split(",")
            return f"Dict[{self.map_type(inner[0].strip())}, {self.map_type(inner[1].strip())}]"
        return dart_type

    def transpile(self, root_node):
        for node in root_node.children:
            if node.type == "class_definition":
                self.visit_class(node)
        
        # main function is a program child in Dart
        for node in root_node.children:
            if node.type == "function_signature":
                # Need the next sibling which is function_body
                idx = root_node.children.index(node)
                if idx + 1 < len(root_node.children) and root_node.children[idx+1].type == "function_body":
                    self.visit_function(node, root_node.children[idx+1])
                    
        return "\n".join(self.lines)

    def visit_class(self, node):
        name_node = self.get_child(node, "identifier")
        class_name = self.get_text(name_node)
        self.add_line(f"class {class_name}:")
        self.indent_level += 1
        
        body = self.get_child(node, "class_body")
        
        decls = self.get_children(body, "declaration")
        constructor_node = None
        method_sig = None
        properties = []
        
        for decl in decls:
            if self.get_child(decl, "type_identifier"):
                t_node = self.get_child(decl, "type_identifier")
                t_name = self.get_text(t_node)
                
                if self.get_child(decl, "nullable_type"): t_name += "?"
                t_args = self.get_child(decl, "type_arguments")
                if t_args: t_name += self.get_text(t_args)
                    
                ilist = self.get_child(decl, "initialized_identifier_list")
                ident_node = self.get_child(self.get_child(ilist, "initialized_identifier"), "identifier")
                ident = self.get_text(ident_node)
                properties.append({"name": ident, "type": t_name})
                self.add_line(f"{ident}: {self.map_type(t_name)}")
                
        for child in body.children:
            if child.type == "method_signature" and self.get_child(child, "constructor_signature"):
                constructor_node = self.get_child(child, "constructor_signature")
                method_sig = child
                break

        self.add_line("")
        
        if constructor_node:
            sig = constructor_node
            params_node = self.get_child(sig, "formal_parameter_list")
            
            params = ["self"]
            init_assigns = []
            if params_node:
                for p in self.get_children(params_node, "formal_parameter"):
                    cp = self.get_child(p, "constructor_param")
                    if cp:
                        ident = self.get_text(self.get_child(cp, "identifier"))
                        p_type = "Any"
                        for prop in properties:
                            if prop["name"] == ident:
                                p_type = prop["type"]
                        params.append(f"{ident}: {self.map_type(p_type)}")
                        init_assigns.append(ident)
                    else:
                        t_node = self.get_child(p, "type_identifier")
                        t_name = self.get_text(t_node) if t_node else "Any"
                        if self.get_child(p, "nullable_type"): t_name += "?"
                        ident = self.get_text(self.get_child(p, "identifier"))
                        params.append(f"{ident}: {self.map_type(t_name)}")
            
            self.add_line(f"def __init__({', '.join(params)}) -> None:")
            self.indent_level += 1
            if init_assigns:
                for a in init_assigns:
                    self.add_line(f"self.{a} = {a}")
            
            if method_sig:
                idx = body.children.index(method_sig)
                if idx + 1 < len(body.children) and body.children[idx+1].type == "function_body":
                    fbody = body.children[idx+1]
                    block = self.get_child(fbody, "block")
                    if block:
                        for stmt in block.children:
                            if stmt.is_named:
                                self.visit_statement(stmt)
                    elif not init_assigns:
                        self.add_line("pass")
                elif not init_assigns:
                    self.add_line("pass")
            else:
                if not init_assigns:
                    self.add_line("pass")
                    
            self.indent_level -= 1
            self.add_line("")
        
        children = [c for c in body.children if c.is_named]
        for i, c in enumerate(children):
            if c.type == "method_signature" and not self.get_child(c, "constructor_signature"):
                func_body = None
                if i + 1 < len(children) and children[i+1].type == "function_body":
                    func_body = children[i+1]
                self.visit_function(c, func_body)
                
        self.indent_level -= 1

    def visit_function(self, sig_node, body_node):
        if sig_node.type == "method_signature":
            func_sig = self.get_child(sig_node, "function_signature")
        else:
            func_sig = sig_node
            
        ident_node = self.get_child(func_sig, "identifier")
        name = self.get_text(ident_node)
        
        t_node = self.get_child(func_sig, "type_identifier")
        if not t_node: t_node = self.get_child(func_sig, "void_type")
        ret_type = self.map_type(self.get_text(t_node)) if t_node else "Any"
        
        params_node = self.get_child(func_sig, "formal_parameter_list")
        params = ["self"] if sig_node.type == "method_signature" else []
        if params_node:
            for p in self.get_children(params_node, "formal_parameter"):
                p_t = self.get_text(self.get_child(p, "type_identifier"))
                if self.get_child(p, "nullable_type"): p_t += "?"
                p_ident = self.get_text(self.get_child(p, "identifier"))
                params.append(f"{p_ident}: {self.map_type(p_t)}")
                
        self.add_line(f"def {name}({', '.join(params)}) -> {ret_type}:")
        self.indent_level += 1
        
        if body_node:
            block = self.get_child(body_node, "block")
            if block:
                for stmt in block.children:
                    if stmt.is_named:
                        self.visit_statement(stmt)
        else:
            self.add_line("pass")
            
        self.indent_level -= 1
        self.add_line("")

    def visit_expression_chain(self, children):
        # [identifier, selector, selector, ...]
        if not children: return ""
        res = self.visit_expression(children[0])
        for sel in children[1:]:
            s = self.visit_selector(sel)
            # handle print coercion
            if res == "print" and s.startswith("("):
                res = f"print{s}"
            elif res == "Exception" and s.startswith("("):
                res = f"Exception{s}"
            else:
                res += s
        return res

    def visit_selector(self, expr):
        if expr.type == "selector" or expr.type == "unconditional_assignable_selector":
            inner = self.get_child(expr, "unconditional_assignable_selector") or expr
            if inner and inner.type == "unconditional_assignable_selector":
                ident_node = self.get_child(inner, "identifier")
                if ident_node:
                    ident = self.get_text(ident_node)
                    if ident == "toString": return ".toString"
                    if ident == "length": return ".length"
                    return f".{ident}"
                if self.get_child(inner, "index_selector"):
                    idx_node = self.get_child(inner, "index_selector")
                    idx = self.visit_expression([c for c in idx_node.children if c.is_named][0])
                    return f"[{idx}]"
            
            if self.get_child(expr, "argument_part"):
                args = self.get_child(self.get_child(expr, "argument_part"), "arguments")
                arg_list = []
                if args:
                    for a in self.get_children(args, "argument"):
                        arg_list.append(self.visit_expression(a.children[0]))
                return f"({', '.join(arg_list)})"
            # null assertion operator '!' is an empty selector in tree-sitter-dart
            return ""
        return ""

    def process_expression_string(self, expr_str):
        # Convert JS/Dart syntax generated by chain to Python syntax
        if ".length" in expr_str:
            expr_str = expr_str.replace(".length", "")
            return f"len({expr_str})"
        if ".toString()" in expr_str:
            expr_str = expr_str.replace(".toString()", "")
            return f"str({expr_str})"
        if ".containsKey(" in expr_str:
            # a.containsKey(b) -> b in a
            parts = expr_str.split(".containsKey(")
            left = parts[0]
            right = parts[1][:-1] # remove ')'
            return f"{right} in {left}"
        return expr_str

    def visit_statement(self, node):
        if node.type == "for_statement":
            self.visit_for(node)
        elif node.type == "expression_statement":
            expr = [c for c in node.children if c.is_named][0]
            if expr.type == "assignment_expression":
                children = [c for c in expr.children if c.is_named]
                left = self.visit_expression(children[0])
                right = self.visit_expression(children[1])
                self.add_line(f"{left} = {right}")
            elif expr.type == "throw_expression":
                children = [c for c in expr.children if c.is_named]
                val = self.visit_expression_chain(children)
                self.add_line(f"raise {val}")
            else:
                children = [c for c in node.children if c.is_named]
                s = self.visit_expression_chain(children)
                s = self.process_expression_string(s)
                self.add_line(s)
        elif node.type == "local_variable_declaration":
            init = self.get_child(node, "initialized_variable_definition")
            t_node = self.get_child(init, "type_identifier")
            named_children = [c for c in init.children if c.is_named]
            
            if t_node:
                t_name = self.get_text(t_node)
                if self.get_child(init, "type_arguments"): t_name += self.get_text(self.get_child(init, "type_arguments"))
                name_idx = 1
            else:
                t_name = "Any"
                name_idx = 0
                
            ident = self.get_text(named_children[name_idx])
            val_nodes = named_children[name_idx+1:]
            
            if val_nodes:
                val = self.visit_expression_chain(val_nodes)
                val = self.process_expression_string(val)
                self.add_line(f"{ident}: {self.map_type(t_name)} = {val}")
            else:
                self.add_line(f"{ident}: {self.map_type(t_name)} = None")
        elif node.type == "if_statement":
            named_children = [c for c in node.children if c.is_named]
            block_idx = -1
            for i, c in enumerate(named_children):
                if c.type in ("block", "expression_statement", "return_statement", "if_statement", "break_statement", "continue_statement"):
                    block_idx = i
                    break
            if block_idx == -1: block_idx = len(named_children) - 1
            
            cond = self.visit_expression_chain(named_children[:block_idx])
            cond = self.process_expression_string(cond)
            self.add_line(f"if {cond}:")
            self.indent_level += 1
            true_body = named_children[block_idx]
            if true_body.type == "block":
                for c in true_body.children:
                    if c.is_named: self.visit_statement(c)
            else:
                self.visit_statement(true_body)
            self.indent_level -= 1
            
            if block_idx + 1 < len(named_children):
                self.add_line("else:")
                self.indent_level += 1
                else_body = named_children[block_idx + 1]
                if else_body.type == "block":
                    for c in else_body.children:
                        if c.is_named: self.visit_statement(c)
                else:
                    self.visit_statement(else_body)
                self.indent_level -= 1
        elif node.type == "while_statement":
            named_children = [c for c in node.children if c.is_named]
            block_idx = -1
            for i, c in enumerate(named_children):
                if c.type == "block":
                    block_idx = i
                    break
            cond = self.visit_expression_chain(named_children[:block_idx])
            cond = self.process_expression_string(cond)
            self.add_line(f"while {cond}:")
            self.indent_level += 1
            block = self.get_child(node, "block")
            for c in block.children:
                if c.is_named: self.visit_statement(c)
            self.indent_level -= 1
        elif node.type == "try_statement":
            self.add_line("try:")
            self.indent_level += 1
            block = self.get_child(node, "block")
            for c in block.children:
                if c.is_named: self.visit_statement(c)
            self.indent_level -= 1
            
            catch_clause = self.get_child(node, "catch_clause")
            if catch_clause:
                self.add_line("except Exception as e:")
                self.indent_level += 1
                idx = node.children.index(catch_clause)
                cblock = None
                if idx + 1 < len(node.children) and node.children[idx+1].type == "block":
                    cblock = node.children[idx+1]
                if cblock:
                    for c in cblock.children:
                        if c.is_named: self.visit_statement(c)
                else:
                    self.add_line("pass")
                self.indent_level -= 1
        elif node.type == "break_statement":
            self.add_line("break")
        elif node.type == "continue_statement":
            self.add_line("continue")
        elif node.type == "return_statement":
            children = [c for c in node.children if c.is_named]
            if len(children) > 0:
                parts = [self.visit_expression_chain([c]) for c in children]
                expr = "".join(parts)
                expr = self.process_expression_string(expr)
                self.add_line(f"return {expr}")
            else:
                self.add_line("return")

    def visit_for(self, node):
        # Dart: for (int i = 0; i < maxVal; i++)
        parts = self.get_child(node, "for_loop_parts")
        decl = self.get_child(parts, "local_variable_declaration")
        init = self.get_child(decl, "initialized_variable_definition")
        var_name = self.get_text(self.get_child(init, "identifier"))
        start_val = self.get_text(self.get_child(init, "decimal_integer_literal"))
        
        rel = self.get_child(parts, "relational_expression")
        end_val = self.get_text(rel.children[2])
        
        self.add_line(f"for {var_name} in range({start_val}, {end_val}):")
        
        self.indent_level += 1
        block = self.get_child(node, "block")
        for stmt in block.children:
            if stmt.is_named:
                self.visit_statement(stmt)
        self.indent_level -= 1

    def visit_expression(self, expr):
        if expr.type == "identifier":
            return self.get_text(expr)
        elif expr.type == "decimal_integer_literal":
            return self.get_text(expr)
        elif expr.type == "string_literal":
            return self.get_text(expr)
        elif expr.type == "this":
            return "self"
        elif expr.type == "null_literal":
            return "None"
        elif expr.type == "boolean_literal":
            return "True" if self.get_text(expr) == "true" else "False"
        elif expr.type == "list_literal":
            elts = [self.visit_expression(c) for c in expr.children if c.type == "string_literal" or c.type == "decimal_integer_literal"]
            return f"[{', '.join(elts)}]"
        elif expr.type == "set_or_map_literal":
            pairs = []
            for pair in self.get_children(expr, "pair"):
                k = self.visit_expression(pair.children[0])
                v = self.visit_expression(pair.children[2])
                pairs.append(f"{k}: {v}")
            return f"{{{', '.join(pairs)}}}"
        elif expr.type == "assignable_expression":
            named = [c for c in expr.children if c.is_named]
            return self.visit_expression_chain(named)
        elif expr.type == "unconditional_assignable_selector":
            if self.get_child(expr, "identifier"):
                ident = self.get_text(self.get_child(expr, "identifier"))
                return f".{ident}"
            if self.get_child(expr, "index_selector"):
                idx_node = self.get_child(expr, "index_selector")
                idx = self.visit_expression([c for c in idx_node.children if c.is_named][0])
                return f"[{idx}]"
            return ""
        elif expr.type == "additive_expression" or expr.type == "multiplicative_expression":
            named = [c for c in expr.children if c.is_named]
            op_idx = -1
            for i, c in enumerate(named):
                if c.type in ("additive_operator", "multiplicative_operator"):
                    op_idx = i
                    break
            left = self.visit_expression_chain(named[:op_idx])
            op = self.get_text(named[op_idx])
            right = self.visit_expression_chain(named[op_idx+1:])
            left = self.process_expression_string(left)
            right = self.process_expression_string(right)
            if left.startswith("str(") or right.startswith("str("):
                if not left.startswith("str("): left = f"str({left})"
                if not right.startswith("str("): right = f"str({right})"
            return f"{left} {op} {right}"
        elif expr.type == "relational_expression" or expr.type == "equality_expression":
            named = [c for c in expr.children if c.is_named]
            op_idx = -1
            for i, c in enumerate(named):
                if c.type in ("relational_operator", "equality_operator"):
                    op_idx = i
                    break
            left = self.visit_expression_chain(named[:op_idx])
            op = self.get_text(named[op_idx])
            right = self.visit_expression_chain(named[op_idx+1:])
            left = self.process_expression_string(left)
            right = self.process_expression_string(right)
            if op == "==" and right == "None": return f"{left} is None"
            if op == "!=" and right == "None": return f"{left} is not None"
            return f"{left} {op} {right}"
        elif expr.type == "unary_expression":
            op = self.get_text(expr.children[0])
            val = self.visit_expression(expr.children[1])
            if op == "!": return f"not {val}"
            return f"{op}{val}"
        elif expr.type == "parenthesized_expression":
            return self.visit_expression(expr.children[1])
        elif expr.type == "argument":
            return self.visit_expression_chain([c for c in expr.children if c.is_named])
            
        return f"/* {expr.type} */"



def transpile(code: str) -> str:
    import tree_sitter_dart
    from tree_sitter import Language, Parser
    parser = Parser(Language(tree_sitter_dart.language()))
    src_bytes = code.encode('utf8')
    tree = parser.parse(src_bytes)
    transpiler = DartToPyTranspiler(src_bytes)
    python_code = transpiler.transpile(tree.root_node)
    python_code += "\nif __name__ == '__main__':\n    main()\n"
    return python_code
