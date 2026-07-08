import tree_sitter_typescript as tsts
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

class TsToPyTranspiler:
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
        if ts_type == "number": return "int"
        if ts_type == "string": return "str"
        if ts_type == "void": return "None"
        if ts_type == "boolean": return "bool"
        if ts_type == "any": return "Any"
        if ts_type == "null": return "None"
        if " | null" in ts_type: return f"Optional[{self.map_type(ts_type.replace(' | null', ''))}]"
        if ts_type.endswith("[]"): return f"List[{self.map_type(ts_type[:-2])}]"
        if ts_type.startswith("Record<"):
            inner = ts_type[7:-1].split(",")
            return f"Dict[{self.map_type(inner[0].strip())}, {self.map_type(inner[1].strip())}]"
        return ts_type

    def transpile(self, root_node):
        for node in root_node.children:
            if node.type == "class_declaration":
                self.visit_class(node)
            elif node.type == "function_declaration":
                self.visit_function(node)
        return "\n".join(self.lines)

    def visit_class(self, node):
        name_node = self.get_child(node, "type_identifier")
        class_name = self.get_text(name_node)
        self.add_line(f"class {class_name}:")
        self.indent_level += 1
        
        body = self.get_child(node, "class_body")
        
        for c in body.children:
            if c.type == "public_field_definition":
                ident_node = self.get_child(c, "property_identifier")
                type_node = self.get_child(c, "type_annotation")
                ident = self.get_text(ident_node)
                t_str = self.get_text(type_node) if type_node else ""
                if t_str.startswith(": "): t_str = t_str[2:]
                self.add_line(f"{ident}: {self.map_type(t_str)}")
                
        self.add_line("")
        
        for c in body.children:
            if c.type == "method_definition":
                ident_node = self.get_child(c, "property_identifier")
                name = self.get_text(ident_node)
                
                params_node = self.get_child(c, "formal_parameters")
                params = ["self"]
                if params_node:
                    for p in self.get_children(params_node, "required_parameter"):
                        p_ident = self.get_text(self.get_child(p, "identifier"))
                        p_type_node = self.get_child(p, "type_annotation")
                        p_t = self.get_text(p_type_node) if p_type_node else "any"
                        if p_t.startswith(": "): p_t = p_t[2:]
                        params.append(f"{p_ident}: {self.map_type(p_t)}")
                        
                t_node = self.get_child(c, "type_annotation")
                ret_t = self.map_type(self.get_text(t_node)[2:]) if t_node else "Any"
                
                if name == "constructor":
                    self.add_line(f"def __init__({', '.join(params)}) -> None:")
                else:
                    self.add_line(f"def {name}({', '.join(params)}) -> {ret_t}:")
                    
                self.indent_level += 1
                
                block = self.get_child(c, "statement_block")
                if block:
                    for stmt in block.children:
                        if stmt.is_named:
                            self.visit_statement(stmt)
                else:
                    self.add_line("pass")
                    
                self.indent_level -= 1
                self.add_line("")
                
        self.indent_level -= 1

    def visit_function(self, node):
        ident_node = self.get_child(node, "identifier")
        name = self.get_text(ident_node)
        
        params_node = self.get_child(node, "formal_parameters")
        params = []
        if params_node:
            for p in self.get_children(params_node, "required_parameter"):
                p_ident = self.get_text(self.get_child(p, "identifier"))
                p_type_node = self.get_child(p, "type_annotation")
                p_t = self.get_text(p_type_node) if p_type_node else "any"
                if p_t.startswith(": "): p_t = p_t[2:]
                params.append(f"{p_ident}: {self.map_type(p_t)}")
                
        t_node = self.get_child(node, "type_annotation")
        ret_t = self.map_type(self.get_text(t_node)[2:]) if t_node else "Any"
        
        self.add_line(f"def {name}({', '.join(params)}) -> {ret_t}:")
        self.indent_level += 1
        
        block = self.get_child(node, "statement_block")
        if block:
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
                self.add_line(s)
        elif node.type == "lexical_declaration":
            # let x: type = y;
            for decl in self.get_children(node, "variable_declarator"):
                ident = self.get_text(self.get_child(decl, "identifier"))
                type_node = self.get_child(decl, "type_annotation")
                val_node = [c for c in decl.children if c.type not in ("identifier", "type_annotation", "=", ":")]
                val_str = self.visit_expression(val_node[0]) if val_node else "None"
                t_str = self.map_type(self.get_text(type_node)[2:]) if type_node else "Any"
                self.add_line(f"{ident}: {t_str} = {val_str}")
        elif node.type == "if_statement":
            cond = self.visit_expression(self.get_child(node, "parenthesized_expression").children[1])
            self.add_line(f"if {cond}:")
            self.indent_level += 1
            body = self.get_child(node, "statement_block")
            if body:
                for c in body.children:
                    if c.is_named: self.visit_statement(c)
            else: self.add_line("pass")
            self.indent_level -= 1
            
            else_node = self.get_child(node, "else_clause")
            if else_node:
                self.add_line("else:")
                self.indent_level += 1
                else_body = [c for c in else_node.children if c.is_named][-1]
                if else_body.type == "statement_block":
                    for c in else_body.children:
                        if c.is_named: self.visit_statement(c)
                else: self.visit_statement(else_body)
                self.indent_level -= 1
                
        elif node.type == "while_statement":
            cond = self.visit_expression(self.get_child(node, "parenthesized_expression").children[1])
            self.add_line(f"while {cond}:")
            self.indent_level += 1
            body = self.get_child(node, "statement_block")
            if body:
                for c in body.children:
                    if c.is_named: self.visit_statement(c)
            else: self.add_line("pass")
            self.indent_level -= 1
            
        elif node.type == "try_statement":
            self.add_line("try:")
            self.indent_level += 1
            body = self.get_child(node, "statement_block")
            for c in body.children:
                if c.is_named: self.visit_statement(c)
            self.indent_level -= 1
            
            catch_node = self.get_child(node, "catch_clause")
            if catch_node:
                self.add_line("except Exception as e:")
                self.indent_level += 1
                cbody = self.get_child(catch_node, "statement_block")
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
        # for (let i = 0; i < maxVal; i++)
        decl = self.get_child(node, "lexical_declaration")
        decl_var = self.get_child(decl, "variable_declarator")
        var_name = self.get_text(self.get_child(decl_var, "identifier"))
        start_val = self.get_text(self.get_child(decl_var, "number"))
        
        rel = self.get_child(node, "binary_expression")
        end_val = self.get_text(rel.children[2])
        
        self.ledger.log("for(C-style)", "range()", "control-flow-unroll")
        
        self.add_line(f"for {var_name} in range({start_val}, {end_val}):")
        
        self.indent_level += 1
        block = self.get_child(node, "statement_block")
        for stmt in block.children:
            if stmt.is_named:
                self.visit_statement(stmt)
        self.indent_level -= 1

    def visit_expression(self, expr):
        if expr.type == "identifier":
            return self.get_text(expr)
        elif expr.type == "number":
            return self.get_text(expr)
        elif expr.type == "string":
            # the AST node has string_fragment inside it
            frag = self.get_child(expr, "string_fragment")
            return f"'{self.get_text(frag)}'" if frag else "''"
        elif expr.type == "null": return "None"
        elif expr.type == "true": return "True"
        elif expr.type == "false": return "False"
        elif expr.type == "this":
            self.ledger.log("this", "self", "instance-access-mapping")
            return "self"
        elif expr.type == "array":
            elts = [self.visit_expression(c) for c in expr.children if c.is_named]
            return f"[{', '.join(elts)}]"
        elif expr.type == "object":
            pairs = []
            for c in expr.children:
                if c.type == "pair":
                    k = self.visit_expression(c.children[0])
                    v = self.visit_expression(c.children[2])
                    pairs.append(f"{k}: {v}")
            return f"{{{', '.join(pairs)}}}"
        elif expr.type == "subscript_expression":
            left = self.visit_expression(expr.children[0])
            idx = self.visit_expression(expr.children[2])
            return f"{left}[{idx}]"
        elif expr.type == "member_expression":
            left = self.visit_expression(expr.children[0])
            right = self.get_text(expr.children[2])
            if right == "length": return f"len({left})"
            return f"{left}.{right}"
        elif expr.type == "binary_expression":
            left = self.visit_expression(expr.children[0])
            op = self.get_text(expr.children[1])
            right = self.visit_expression(expr.children[2])
            
            if op == "===": return f"{left} == {right}" if right != "None" else f"{left} is None"
            if op == "!==": return f"{left} != {right}" if right != "None" else f"{left} is not None"
            
            # Type coercion for string concatenation in TS
            if expr.children[0].type == "string" and expr.children[2].type == "member_expression":
                right = f"str({right})"
                
            return f"{left} {op} {right}"
        elif expr.type == "unary_expression":
            op = self.get_text(expr.children[0])
            val = self.visit_expression(expr.children[1])
            if op == "!": return f"not {val}"
            return f"{op}{val}"
        elif expr.type == "new_expression":
            # new Fox(...)
            func_name = self.get_text(expr.children[1])
            if func_name == "Error": func_name = "Exception"
            arg_list = self.get_child(expr, "arguments")
            args = []
            if arg_list:
                for a in arg_list.children:
                    if a.is_named: args.append(self.visit_expression(a))
            return f"{func_name}({', '.join(args)})"
        elif expr.type == "parenthesized_expression":
            return self.visit_expression(expr.children[1])
        elif expr.type == "call_expression":
            func_name = self.visit_expression(expr.children[0])
            
            arg_list = self.get_child(expr, "arguments")
            args = []
            for a in arg_list.children:
                if a.is_named:
                    args.append(self.visit_expression(a))
            
            if func_name == "console.log":
                if not args: return "print()"
                return f"print({', '.join(args)})"
            if func_name.endswith(".toString"):
                return f"str({func_name[:-9]})"
                
            return f"{func_name}({', '.join(args)})"
            
        return f"/* unhandled expr {expr.type} */"



def transpile(code: str) -> str:
    import tree_sitter_typescript
    from tree_sitter import Language, Parser
    parser = Parser(Language(tree_sitter_typescript.language_typescript()))
    src_bytes = code.encode('utf8')
    tree = parser.parse(src_bytes)
    transpiler = TsToPyTranspiler(src_bytes)
    python_code = transpiler.transpile(tree.root_node)
    python_code += "\nif __name__ == '__main__':\n    main()\n"
    return python_code
