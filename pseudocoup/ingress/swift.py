import json

class SwiftToPyTranspiler:
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
            elif node.type == "function_declaration":
                name = self.get_text(self.get_child(node, "simple_identifier"))
                if name == "main":
                    self.add_line("def main() -> None:")
                    self.indent_level += 1
                    body = self.get_child(node, "function_body")
                    stmts = self.get_child(body, "statements") if body else None
                    if stmts and any(c.is_named for c in stmts.children):
                        for c in stmts.children:
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

    def visit_class(self, node):
        name_node = self.get_child(node, "type_identifier")
        class_name = self.get_text(name_node)
        
        self.add_line(f"class {class_name}:")
        self.indent_level += 1
        
        body = self.get_child(node, "class_body")
        if body:
            fields = self.get_children(body, "property_declaration")
            if fields:
                for f in fields:
                    ident = self.get_child(f, "pattern")
                    if ident:
                        name = self.get_text(ident)
                        self.add_line(f"{name}: Any")
                self.add_line("")
                
            has_methods = False
            for m in body.children:
                if m.type == "init_declaration":
                    self.visit_method(m, is_init=True)
                    has_methods = True
                elif m.type == "function_declaration":
                    self.visit_method(m)
                    has_methods = True
            if not has_methods and not fields:
                self.add_line("pass")
        else:
            self.add_line("pass")
        self.indent_level -= 1
        self.add_line("")

    def visit_method(self, node, is_init=False):
        name = "__init__" if is_init else self.get_text(self.get_child(node, "simple_identifier"))
        
        params = ["self"]
        for p in self.get_children(node, "parameter"):
            # in swift `parameter` has two simple_identifiers: external and internal, e.g. `_ arg`
            idents = self.get_children(p, "simple_identifier")
            ident = self.get_text(idents[-1]) if idents else "unknown"
            params.append(f"{ident}: Any")
                
        if is_init:
            self.add_line(f"def {name}({', '.join(params)}) -> None:")
        else:
            self.add_line(f"def {name}({', '.join(params)}) -> Any:")
            
        self.indent_level += 1
        body = self.get_child(node, "function_body")
        stmts = self.get_child(body, "statements") if body else None
        if stmts and any(c.is_named for c in stmts.children):
            for c in stmts.children:
                if c.is_named:
                    self.visit_statement(c)
        else:
            self.add_line("pass")
        self.indent_level -= 1
        self.add_line("")

    def visit_statement(self, node):
        if node.type == "property_declaration":
            ident = self.get_child(node, "pattern")
            # swift parses `var x = val` as a child node pattern having the var name, and an equal sign with value... wait!
            # in Swift AST: property_declaration > value_binding_pattern, pattern, type_annotation OR expression?
            # actually it's easier to just take the first assignable part.
            var_name = self.get_text(self.get_child(node, "pattern")) if self.get_child(node, "pattern") else "unknown"
            
            # extract value
            val = "None"
            for i, c in enumerate(node.children):
                if c.type == "=" and i+1 < len(node.children):
                    val = self.visit_expression(node.children[i+1])
                    break
            # if we didn't find = direct child, maybe it's inside pattern? We just fall back
            if val == "None":
                # Look for call_expression or literals
                expr = [c for c in node.children if c.type in ("call_expression", "array_literal", "dictionary_literal", "integer_literal", "string_literal", "try_expression")]
                if expr: val = self.visit_expression(expr[0])
            self.add_line(f"{var_name} = {val}")
        elif node.type == "assignment":
            left = self.visit_expression(node.children[0])
            op = self.get_text(node.children[1])
            right = self.visit_expression(node.children[2])
            self.add_line(f"{left} {op} {right}")
        elif node.type == "if_statement":
            cond_node = None
            for c in node.children:
                if c.is_named and c.type != "statements":
                    cond_node = c
                    break
            cond = self.visit_expression(cond_node) if cond_node else "True"
            
            self.add_line(f"if {cond}:")
            self.indent_level += 1
            stmts = self.get_child(node, "statements")
            if stmts:
                for c in stmts.children:
                    if c.is_named: self.visit_statement(c)
            else: self.add_line("pass")
            self.indent_level -= 1
            
            else_node = None
            found_else = False
            for c in node.children:
                if c.type == "else":
                    found_else = True
                elif found_else and c.is_named:
                    else_node = c
                    break
            
            if else_node:
                self.add_line("else:")
                self.indent_level += 1
                if else_node.type == "if_statement":
                    self.visit_statement(else_node)
                else: # statements block
                    for c in else_node.children:
                        if c.is_named: self.visit_statement(c)
                self.indent_level -= 1
        elif node.type == "while_statement":
            cond_node = None
            for c in node.children:
                if c.is_named and c.type != "statements":
                    cond_node = c
                    break
            cond = self.visit_expression(cond_node) if cond_node else "True"
            
            self.add_line(f"while {cond}:")
            self.indent_level += 1
            stmts = self.get_child(node, "statements")
            if stmts:
                for c in stmts.children:
                    if c.is_named: self.visit_statement(c)
            else: self.add_line("pass")
            self.indent_level -= 1
        elif node.type == "control_transfer_statement":
            kw = self.get_text(node.children[0])
            if kw == "return":
                exprs = [c for c in node.children if c.is_named]
                if exprs:
                    self.add_line(f"return {self.visit_expression(exprs[0])}")
                else:
                    self.add_line("return")
            elif kw == "throw":
                exprs = [c for c in node.children if c.is_named and c.type != "throw_keyword"]
                if exprs:
                    self.add_line(f"raise {self.visit_expression(exprs[-1])}")
            else:
                self.add_line(kw)
        elif node.type == "do_statement":
            self.add_line("try:")
            self.indent_level += 1
            stmts = self.get_child(node, "statements")
            if stmts:
                for c in stmts.children:
                    if c.is_named: self.visit_statement(c)
            self.indent_level -= 1
            # catches are outside do_statement? wait, Swift AST: do_statement has catch_clause child!
            for catch_clause in self.get_children(node, "catch_block"):
                n = "e"
                pattern = self.get_child(catch_clause, "pattern")
                if pattern: n = self.get_text(self.get_child(pattern, "simple_identifier"))
                if not n: n = "e"
                self.add_line(f"except Exception as {n}:")
                self.indent_level += 1
                cbody = self.get_child(catch_clause, "statements")
                if cbody:
                    for c in cbody.children:
                        if c.is_named: self.visit_statement(c)
                else:
                    self.add_line("pass")
                self.indent_level -= 1
        else:
            # Maybe an expression
            val = self.visit_expression(node)
            if val: self.add_line(val)

    def visit_expression(self, node):
        if not node: return "None"
        if node.type == "simple_identifier":
            t = self.get_text(node)
            if t == "nil": return "None"
            if t == "true": return "True"
            if t == "false": return "False"
            return t
        elif node.type == "type_identifier":
            return self.get_text(node)
        elif node.type in ("integer_literal", "float_literal"):
            return self.get_text(node)
        elif node.type == "line_string_literal":
            contents = self.get_children(node, "line_str_text")
            if contents:
                return '"' + "".join([self.get_text(c) for c in contents]) + '"'
            return '""'
        elif node.type == "true": return "True"
        elif node.type == "false": return "False"
        elif node.type == "nil": return "None"
        elif node.type == "self_expression": return "self"
        elif node.type == "navigation_expression":
            named = [c for c in node.children if c.is_named]
            if len(named) >= 2:
                left = self.visit_expression(named[0])
                right = self.visit_expression(named[-1])
                if right == "count": return f"len({left})"
                return f"{left}.{right}"
            return self.get_text(node)
        elif node.type == "navigation_suffix":
            named = [c for c in node.children if c.is_named]
            if named:
                return self.visit_expression(named[-1])
            return self.get_text(node)
        elif node.type == "additive_expression" or node.type == "multiplicative_expression" or node.type == "equality_expression" or node.type == "comparison_expression" or node.type == "infix_expression":
            left = self.visit_expression(node.children[0])
            op = self.get_text(node.children[1])
            right = self.visit_expression(node.children[2])
            return f"{left} {op} {right}"
        elif node.type == "prefix_expression":
            op = self.get_text(node.children[0])
            right = self.visit_expression(node.children[1])
            if op == "!": return f"not {right}"
            return f"{op}{right}"
        elif node.type == "call_expression":
            func = self.visit_expression(node.children[0])
            args_node = self.get_child(node, "call_suffix")
            args = []
            is_subscript = False
            if args_node:
                # call_suffix has value_arguments
                val_args = self.get_child(args_node, "value_arguments")
                if val_args:
                    if any(c.type == "[" for c in val_args.children):
                        is_subscript = True
                    for c in val_args.children:
                        if c.type == "value_argument":
                            named = [child for child in c.children if child.is_named]
                            if named:
                                args.append(self.visit_expression(named[-1]))
                            else:
                                txt = self.get_text(c)
                                if txt == "nil": args.append("None")
                                elif txt == "true": args.append("True")
                                elif txt == "false": args.append("False")
                                else: args.append(txt)
            
            if func == "print":
                return f"print({args[0]})"
            if func == "String":
                return f"str({args[0]})"
            
            # Check if func is a method like X.count
            if func.endswith(".count"):
                obj = func[:-6]
                return f"len({obj})"
            if func.endswith(".keys.contains"):
                obj = func[:-14]
                return f"{args[0]} in {obj}"
                
            if is_subscript:
                return f"{func}[{args[0]}]"
            return f"{func}({', '.join(args)})"
        elif node.type == "directly_assignable_expression":
            return self.visit_expression(node.children[0])
        elif node.type == "array_literal":
            items = []
            for c in node.children:
                if c.is_named: items.append(self.visit_expression(c))
            return f"[{', '.join(items)}]"
        elif node.type == "dictionary_literal":
            pairs = []
            named = [c for c in node.children if c.is_named]
            for i in range(0, len(named), 2):
                if i+1 < len(named):
                    k = self.visit_expression(named[i])
                    v = self.visit_expression(named[i+1])
                    pairs.append(f"{k}: {v}")
            return f"{{{', '.join(pairs)}}}"
        elif node.type == "subscript_expression":
            left = self.visit_expression(node.children[0])
            right = self.visit_expression(node.children[2])
            return f"{left}[{right}]"
        elif node.type == "tuple_expression":
            return f"({self.visit_expression(node.children[1])})"
        elif node.type == "try_expression":
            # try fn() -> fn()
            return self.visit_expression(node.children[1])
        return self.get_text(node)

def transpile(code: str) -> str:
    import tree_sitter_swift
    from tree_sitter import Language, Parser
    
    parser = Parser(Language(tree_sitter_swift.language()))
    tree = parser.parse(code.encode('utf8'))
    
    transpiler = SwiftToPyTranspiler()
    res = transpiler.transpile(tree.root_node)
    
    return res
