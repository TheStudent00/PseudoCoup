from tree_sitter import Language, Parser
import tree_sitter_kotlin
import json

class Ledger:
    def __init__(self):
        self.entries = []
    def log(self, kt_node, py_target, reason):
        pass
    def save(self, path):
        pass

class KtToPyTranspiler:
    def __init__(self, src_bytes):
        self.src_bytes = src_bytes
        self.lines = []
        self.indent_level = 0
        self.ledger = Ledger()
        self.classes = {}

    def add_line(self, text):
        if text.strip() == "":
            self.lines.append("")
        else:
            self.lines.append("    " * self.indent_level + text)

    def get_text(self, node):
        if node is None: return ""
        return self.src_bytes[node.start_byte:node.end_byte].decode('utf8')

    def map_type(self, kt_type):
        if kt_type == "Int": return "int"
        if kt_type == "String": return "str"
        if kt_type == "Boolean": return "bool"
        if kt_type == "Double": return "float"
        if kt_type == "Unit": return "None"
        if kt_type.startswith("List<"):
            inner = self.map_type(kt_type[5:-1])
            return f"List[{inner}]"
        if kt_type.startswith("Map<"):
            parts = kt_type[4:-1].split(',')
            k = self.map_type(parts[0].strip())
            v = self.map_type(parts[1].strip())
            return f"Dict[{k}, {v}]"
        if kt_type.endswith("?"):
            return f"Optional[{self.map_type(kt_type[:-1])}]"
        return kt_type

    def get_child(self, node, type_name):
        for child in node.children:
            if child.type == type_name: return child
        return None
        
    def get_children(self, node, type_name):
        return [c for c in node.children if c.type == type_name]

    def transpile(self, root_node):
        self.add_line("from typing import List, Dict, Optional, Any")
        self.add_line("")
        
        for node in root_node.children:
            if node.type == "class_declaration":
                self.visit_class(node)
            elif node.type == "function_declaration":
                ident = self.get_text(self.get_child(node, "identifier"))
                if ident == "main":
                    self.add_line("def main() -> None:")
                    self.indent_level += 1
                    block = self.get_child(node, "function_body")
                    if block and block.children and block.children[0].type == "block":
                        block = block.children[0]
                    statements = block
                    if statements:
                        for stmt in statements.children:
                            if stmt.is_named:
                                self.visit_statement(stmt)
                    self.indent_level -= 1
                    
        return "\n".join(self.lines)

    def visit_class(self, node):
        cls_name = self.get_text(self.get_child(node, "identifier"))
        self.add_line(f"class {cls_name}:")
        self.indent_level += 1
        
        primary_constructor = self.get_child(node, "primary_constructor")
        params = ["self"]
        if primary_constructor:
            value_params = self.get_child(primary_constructor, "class_parameters")
            for p in self.get_children(value_params, "class_parameter"):
                p_ident = self.get_text(self.get_child(p, "identifier"))
                
                type_node = self.get_child(p, "user_type")
                if not type_node: type_node = self.get_child(p, "nullable_type")
                if not type_node: type_node = self.get_child(p, "type")
                
                p_type = self.map_type(self.get_text(type_node))
                params.append(f"{p_ident}: {p_type}")
                
        self.add_line(f"def __init__({', '.join(params)}) -> None:")
        self.indent_level += 1
        
        body = self.get_child(node, "class_body")
        assigned = False
        if body:
            for member in body.children:
                if member.type == "property_declaration":
                    var_decl = self.get_child(member, "variable_declaration")
                    ident = self.get_text(self.get_child(var_decl, "identifier"))
                    type_node = self.get_child(var_decl, "user_type")
                    if not type_node: type_node = self.get_child(var_decl, "nullable_type")
                    if not type_node: type_node = self.get_child(var_decl, "type")
                    p_type = self.map_type(self.get_text(type_node)) if type_node else "Any"
                    
                    # initializer is the expression after `=`
                    eq_idx = -1
                    for i, c in enumerate(member.children):
                        if c.type == "=":
                            eq_idx = i
                            break
                    if eq_idx != -1 and eq_idx + 1 < len(member.children):
                        init_expr = self.visit_expression(member.children[eq_idx+1])
                        self.add_line(f"self.{ident}: {p_type} = {init_expr}")
                        assigned = True
        if not assigned:
            self.add_line("pass")
            
        self.indent_level -= 1
        self.add_line("")
        
        if body:
            for member in body.children:
                if member.type == "function_declaration":
                    self.visit_method(member)
                    
        self.indent_level -= 1

    def visit_method(self, node):
        m_name = self.get_text(self.get_child(node, "identifier"))
        params = ["self"]
        
        value_params = None
        for c in node.children:
            if "parameter" in c.type:
                value_params = c
                break
                
        if value_params:
            for p in value_params.children:
                if p.type == "parameter" or p.type == "value_parameter" or p.type == "function_value_parameter":
                    p_ident = self.get_text(self.get_child(p, "identifier"))
                    
                    type_node = self.get_child(p, "user_type")
                    if not type_node: type_node = self.get_child(p, "nullable_type")
                    if not type_node: type_node = self.get_child(p, "type")
                    
                    p_type = self.map_type(self.get_text(type_node))
                    params.append(f"{p_ident}: {p_type}")
            
        ret_type = "None"
        for c in node.children:
            if c.type == "type":
                ret_type = self.map_type(self.get_text(c))
                
        self.add_line(f"def {m_name}({', '.join(params)}) -> {ret_type}:")
        self.indent_level += 1
        
        block = self.get_child(node, "function_body")
        if block and block.children and block.children[0].type == "block":
            block = block.children[0]
        statements = block
        has_stmt = False
        if statements:
            for stmt in statements.children:
                if stmt.is_named:
                    self.visit_statement(stmt)
                    has_stmt = True
        if not has_stmt:
            self.add_line("pass")
        self.indent_level -= 1
        self.add_line("")

    def visit_statement(self, node):
        if node.type == "property_declaration":
            var_decl = self.get_child(node, "variable_declaration")
            ident = self.get_text(self.get_child(var_decl, "identifier"))
            
            type_node = self.get_child(var_decl, "user_type")
            if not type_node: type_node = self.get_child(var_decl, "nullable_type")
            if not type_node: type_node = self.get_child(var_decl, "type")
            p_type = self.map_type(self.get_text(type_node)) if type_node else None
            
            eq_idx = -1
            for i, c in enumerate(node.children):
                if c.type == "=":
                    eq_idx = i
                    break
            init_expr = self.visit_expression(node.children[eq_idx+1]) if eq_idx != -1 else "None"
            if p_type:
                self.add_line(f"{ident}: {p_type} = {init_expr}")
            else:
                self.add_line(f"{ident} = {init_expr}")
                
        elif node.type == "assignment":
            left = self.visit_expression(node.children[0])
            right = self.visit_expression(node.children[2])
            self.add_line(f"{left} = {right}")
            
        elif node.type == "while_statement":
            cond_node = None
            for c in node.children:
                if c.type not in ("while", "(", ")", "block"):
                    cond_node = c
                    break
            cond = self.visit_expression(cond_node) if cond_node else "True"
            self.add_line(f"while {cond}:")
            self.indent_level += 1
            body = self.get_child(node, "block")
            if body:
                for stmt in body.children:
                    if stmt.is_named: self.visit_statement(stmt)
            else:
                self.add_line("pass")
            self.indent_level -= 1
            
        elif node.type == "if_expression":
            cond_node = None
            for c in node.children:
                if c.type not in ("if", "(", ")", "block", "else"):
                    cond_node = c
                    break
            cond = self.visit_expression(cond_node) if cond_node else "True"
            self.add_line(f"if {cond}:")
            self.indent_level += 1
            body = None
            for c in node.children:
                if c.type == "block":
                    body = c
                    break
            if body:
                for stmt in body.children:
                    if stmt.is_named: self.visit_statement(stmt)
            else:
                self.add_line("pass")
            self.indent_level -= 1
            
            # else branch?
            for i, c in enumerate(node.children):
                if c.type == "else":
                    else_body = node.children[i+1]
                    self.add_line("else:")
                    self.indent_level += 1
                    if else_body.type == "block":
                        for stmt in else_body.children:
                            if stmt.is_named: self.visit_statement(stmt)
                    else:
                        self.visit_statement(else_body)
                    self.indent_level -= 1
                    break
                    
        elif node.type == "try_expression":
            self.add_line("try:")
            self.indent_level += 1
            block = self.get_child(node, "block")
            for stmt in block.children:
                if stmt.is_named: self.visit_statement(stmt)
            self.indent_level -= 1
            
            for c in node.children:
                if c.type == "catch_block":
                    catch_block = c
                    params = self.get_child(catch_block, "catch_block_parameters") # Not a real type maybe? Let's check child types.
                    # Usually it's `(`, `simple_identifier`, `:`, `type`, `)`
                    # Let's just catch Exception as e
                    self.add_line("except Exception as e:")
                    self.indent_level += 1
                    c_block = self.get_child(catch_block, "block")
                    for stmt in c_block.children:
                        if stmt.is_named: self.visit_statement(stmt)
                    self.indent_level -= 1
                    
        elif node.type == "return_expression":
            if len(node.children) > 1:
                val = self.visit_expression(node.children[1])
                self.add_line(f"return {val}")
            else:
                self.add_line("return")
        elif node.type == "break_expression":
            self.add_line("break")
        elif node.type == "continue_expression":
            self.add_line("continue")
        elif node.type == "throw_expression":
            exc = self.visit_expression(node.children[1])
            self.add_line(f"raise {exc}")
                
        else: # Expression as statement
            expr = self.visit_expression(node)
            if expr:
                self.add_line(expr)

    def visit_expression(self, expr):
        if expr.type == "identifier":
            ident = self.get_text(expr)
            if ident == "this": return "self"
            if ident == "null": return "None"
            return ident
            
        elif expr.type == "this_expression":
            return "self"
            
        elif expr.type == "integer_literal" or expr.type == "number_literal":
            return self.get_text(expr)
            
        elif expr.type == "string_literal" or expr.type == "line_string_literal":
            # Just return the text, it includes quotes
            return self.get_text(expr)
            
        elif expr.type == "null_literal" or expr.type == "null":
            return "None"
            
        elif expr.type == "navigation_expression":
            left = self.visit_expression(expr.children[0])
            right = self.visit_expression(expr.children[2]) # navigation_suffix
            if right.startswith("."): right = right[1:]
            if right == "size" and left not in ("self", "forest", "this"):
                return f"len({left})"
            return f"{left}.{right}"
            
        elif expr.type == "navigation_suffix":
            right = self.visit_expression(expr.children[1])
            return right
            
        elif expr.type in ("postfix_expression", "prefix_expression", "unary_expression"):
            if len(expr.children) == 2:
                if expr.children[0].type in ("+", "-", "!", "not", "!!") or self.get_text(expr.children[0]) in ("+", "-", "!", "not", "!!"):
                    op = self.get_text(expr.children[0])
                    if op == "!!": return self.visit_expression(expr.children[1])
                    val = self.visit_expression(expr.children[1])
                    if op == "!": op = "not "
                    return f"{op}{val}"
                else:
                    op = self.get_text(expr.children[1])
                    if op == "!!": return self.visit_expression(expr.children[0])
                    val = self.visit_expression(expr.children[0])
                    return f"{val}{op}"
            return f"/* {expr.type} */"
            
        elif expr.type == "indexing_expression" or expr.type == "index_expression":
            left = self.visit_expression(expr.children[0])
            idx_node = self.get_child(expr, "indexing_suffix")
            if not idx_node: idx_node = self.get_child(expr, "value_arguments")
            if not idx_node:
                # wait, maybe it's `['identifier', '[', 'expression', ']']`
                for c in expr.children:
                    if c.type not in ("[", "]", "identifier") and c != expr.children[0]:
                        idx = self.visit_expression(c)
                        return f"{left}[{idx}]"
                return f"{left}[?]"
            idx = self.visit_expression(idx_node.children[1])
            return f"{left}[{idx}]"
            
        elif expr.type == "call_expression":
            left = self.visit_expression(expr.children[0])
            val_args = self.get_child(expr, "value_arguments")
            args = []
            if val_args:
                for a in val_args.children:
                    if a.type not in ("(", ")", ",", "value_argument"):
                        args.append(self.visit_expression(a))
                    elif a.type == "value_argument":
                        args.append(self.visit_expression(a.children[0]))
                    
            if left == "println" or left == "print":
                return f"print({', '.join(args)})"
            if left.endswith(".toString"):
                return f"str({left[:-9]})"
            if left.endswith(".containsKey"):
                return f"{args[0]} in {left[:-12]}"
            if left == "listOf":
                return f"[{', '.join(args)}]"
            if left == "mapOf":
                # args are like `"Red" to 5` -> in Kotlin AST this is a binary expression?
                # Actually `to` is an infix function. It parses as an infix_expression or call.
                # Let's map it manually.
                pairs = []
                for a in args:
                    if a.endswith(")"): # e.g. "Red".to(5)
                        pass
                    if " to " in a:
                        k, v = a.split(" to ")
                        pairs.append(f"{k}: {v}")
                return f"{{{', '.join(pairs)}}}"
                
            return f"{left}({', '.join(args)})"
            
        elif expr.type == "infix_expression":
            left = self.visit_expression(expr.children[0])
            op = self.get_text(expr.children[1])
            right = self.visit_expression(expr.children[2])
            
            if op == "to":
                return f"{left} to {right}"
                
            return f"{left} {op} {right}"
            
        elif expr.type == "binary_expression" or expr.type == "equality_expression" or expr.type == "multiplicative_expression" or expr.type == "additive_expression":
            left = self.visit_expression(expr.children[0])
            op = self.get_text(expr.children[1])
            right = self.visit_expression(expr.children[2])
            
            if op == "===" or op == "==":
                if right == "None": return f"{left} is None"
                return f"{left} == {right}"
            if op == "!==" or op == "!=":
                if right == "None": return f"{left} is not None"
                return f"{left} != {right}"
                
            return f"{left} {op} {right}"
            
        elif expr.type == "parenthesized_expression":
            inner = self.visit_expression(expr.children[1])
            return inner
            
        return f"/* {expr.type} */"



def transpile(code: str) -> str:
    import tree_sitter_kotlin
    from tree_sitter import Language, Parser
    parser = Parser(Language(tree_sitter_kotlin.language()))
    src_bytes = code.encode('utf8')
    tree = parser.parse(src_bytes)
    transpiler = KtToPyTranspiler(src_bytes)
    python_code = transpiler.transpile(tree.root_node)
    python_code += "\nif __name__ == '__main__':\n    main()\n"
    return python_code
