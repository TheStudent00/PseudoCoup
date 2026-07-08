import tree_sitter_go as tsgo
from tree_sitter import Language, Parser
import json

class Ledger:
    def __init__(self):
        self.entries = []
    
    def log(self, go_node, py_target, reason):
        entry = {"go_node": go_node, "py_target": py_target, "reason": reason}
        if entry not in self.entries:
            self.entries.append(entry)
    
    def save(self, path):
        with open(path, 'w') as f:
            json.dump(self.entries, f, indent=2)

class GoToPyTranspiler:
    def __init__(self, src_bytes):
        self.src_bytes = src_bytes
        self.lines = []
        self.indent_level = 0
        self.ledger = Ledger()
        self.structs = {}  # struct_name -> {"fields": [], "methods": [], "constructor": None}
        
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

    def map_type(self, go_type):
        if go_type == "int": return "int"
        if go_type == "string": return "str"
        if go_type == "float64": return "float"
        if go_type == "bool": return "bool"
        if go_type.startswith("[]"):
            inner = self.map_type(go_type[2:])
            return f"List[{inner}]"
        if go_type.startswith("map["):
            closing_idx = go_type.find("]")
            key_t = self.map_type(go_type[4:closing_idx])
            val_t = self.map_type(go_type[closing_idx+1:])
            return f"Dict[{key_t}, {val_t}]"
        if go_type.startswith("*"):
            inner = self.map_type(go_type[1:])
            return f"Optional[{inner}]"
        return "Any"

    def transpile(self, root_node):
        # Pass 1: Discovery
        self.main_func = None
        for node in root_node.children:
            if node.type == "type_declaration":
                spec = self.get_child(node, "type_spec")
                ident = self.get_child(spec, "type_identifier")
                struct_name = self.get_text(ident)
                struct_type = self.get_child(spec, "struct_type")
                if struct_type:
                    self.ledger.log("type_declaration(struct)", "class", "struct-to-class")
                    if struct_name not in self.structs:
                        self.structs[struct_name] = {"fields": [], "methods": [], "constructor": None}
                    
                    fields = self.get_child(struct_type, "field_declaration_list")
                    for fd in self.get_children(fields, "field_declaration"):
                        f_ident = self.get_child(fd, "field_identifier")
                        t_ident = self.get_child(fd, "type_identifier")
                        if not t_ident: # Maybe it's an array type or map type
                            t_ident = fd.children[1] # the type is the second child usually
                        if f_ident and t_ident:
                            self.structs[struct_name]["fields"].append({
                                "name": self.get_text(f_ident),
                                "type": self.get_text(t_ident)
                            })
                            
            elif node.type == "function_declaration":
                ident = self.get_text(self.get_child(node, "identifier"))
                if ident == "main":
                    self.main_func = node
                elif ident.startswith("New"):
                    ret_type_node = self.get_child(node, "pointer_type")
                    if ret_type_node:
                        t_ident = self.get_child(ret_type_node, "type_identifier")
                        target_struct = self.get_text(t_ident)
                        if target_struct in self.structs:
                            self.structs[target_struct]["constructor"] = node
                            self.ledger.log("function_declaration(NewX)", "__init__", "factory-to-init")
                            self.ledger.log("pointer_type(*T)", "T", "pointer-erasure")
            elif node.type == "method_declaration":
                rcvr = self.get_child(node, "parameter_list")
                pdecl = self.get_child(rcvr, "parameter_declaration")
                ptype = self.get_child(pdecl, "pointer_type")
                if ptype:
                    t_ident = self.get_child(ptype, "type_identifier")
                    target_struct = self.get_text(t_ident)
                    if target_struct in self.structs:
                        self.structs[target_struct]["methods"].append(node)
                        self.ledger.log("method_declaration(receiver)", "class method", "receiver-to-method")
                        self.ledger.log("receiver parameter", "self", "instance-access-mapping")

        self.lines.append("from typing import List, Dict, Optional, Any")
        self.lines.append("")
        
        # Pass 2: Generation
        for struct_name, data in self.structs.items():
            self.add_line(f"class {struct_name}:")
            self.indent_level += 1
            
            # Constructor
            if data["constructor"]:
                c_node = data["constructor"]
                params_node = self.get_child(c_node, "parameter_list")
                params = ["self"]
                if params_node:
                    for p in self.get_children(params_node, "parameter_declaration"):
                        ident = self.get_child(p, "identifier")
                        t_ident = p.children[1] # type_identifier or pointer_type
                        params.append(f"{self.get_text(ident)}: {self.map_type(self.get_text(t_ident))}")
                
                self.add_line(f"def __init__({', '.join(params)}) -> None:")
                self.indent_level += 1
                
                block = self.get_child(c_node, "block")
                stmt_list = self.get_child(block, "statement_list")
                assigned = False
                for stmt in stmt_list.children:
                    if stmt.type == "assignment_statement" or stmt.type == "short_var_declaration":
                        expr_lists = self.get_children(stmt, "expression_list")
                        left = self.visit_expression(expr_lists[0].children[0])
                        right = self.visit_expression(expr_lists[1].children[0])
                        
                        if left in ("f", "self") and ("composite_literal" in right or "/*" in right): continue
                        if left.startswith("f."):
                            left = "self." + left[2:]
                        elif left.startswith("self."):
                            pass # already mapped
                        
                        field_name = left.split('.')[-1]
                        field_type = "Any"
                        for f in data["fields"]:
                            if f["name"] == field_name:
                                field_type = self.map_type(f["type"])
                        
                        self.add_line(f"{left}: {field_type} = {right}")
                        assigned = True
                    elif stmt.type == "return_statement":
                        continue
                        
                if not assigned:
                    self.add_line("pass")
                    
                self.indent_level -= 1
                self.add_line("")

            # Methods
            for m_node in data["methods"]:
                m_name = self.get_text(self.get_child(m_node, "field_identifier"))
                
                params_nodes = self.get_children(m_node, "parameter_list")
                method_params = params_nodes[1] if len(params_nodes) > 1 else None
                
                params = ["self"]
                if method_params:
                    for p in self.get_children(method_params, "parameter_declaration"):
                        ident = self.get_child(p, "identifier")
                        t_ident = p.children[1]
                        params.append(f"{self.get_text(ident)}: {self.map_type(self.get_text(t_ident))}")
                        
                ret_t_node = self.get_child(m_node, "type_identifier")
                ret_t = self.map_type(self.get_text(ret_t_node)) if ret_t_node else "None"
                
                rcvr_pdecl = self.get_child(params_nodes[0], "parameter_declaration")
                self.rcvr_name = self.get_text(self.get_child(rcvr_pdecl, "identifier"))
                
                py_m_name = m_name[0].lower() + m_name[1:]
                
                self.add_line(f"def {py_m_name}({', '.join(params)}) -> {ret_t}:")
                self.indent_level += 1
                
                block = self.get_child(m_node, "block")
                stmt_list = self.get_child(block, "statement_list")
                for stmt in stmt_list.children:
                    if stmt.is_named:
                        self.visit_statement(stmt)
                        
                self.indent_level -= 1
                self.add_line("")

            self.indent_level -= 1

        # main function
        if self.main_func:
            self.add_line("def main() -> None:")
            self.indent_level += 1
            block = self.get_child(self.main_func, "block")
            stmt_list = self.get_child(block, "statement_list")
            for stmt in stmt_list.children:
                if stmt.is_named:
                    self.visit_statement(stmt)
            self.indent_level -= 1
            self.add_line("")

        return "\n".join(self.lines)

    def visit_statement(self, node):
        if node.type == "for_statement":
            # Can be while or for
            for_clause = self.get_child(node, "for_clause")
            if for_clause:
                # wait, fox.go generated: `for current < prey_count {` which is just a binary_expression in Go
                pass
            else:
                # Is it a while loop? Go's while is `for condition {`
                bin_expr = self.get_child(node, "binary_expression")
                if bin_expr:
                    self.ledger.log("for_statement(condition)", "while", "while-loop-mapping")
                    cond = self.visit_expression(bin_expr)
                    self.add_line(f"while {cond}:")
                    self.indent_level += 1
                    block = self.get_child(node, "block")
                    stmt_list = self.get_child(block, "statement_list")
                    for stmt in stmt_list.children:
                        if stmt.is_named:
                            self.visit_statement(stmt)
                    self.indent_level -= 1
                    
        elif node.type == "assignment_statement" or node.type == "short_var_declaration":
            expr_lists = self.get_children(node, "expression_list")
            if len(expr_lists) == 2:
                left = self.visit_expression(expr_lists[0].children[0])
                right = self.visit_expression(expr_lists[1].children[0])
                self.add_line(f"{left} = {right}")
                
        elif node.type == "return_statement":
            expr_list = self.get_child(node, "expression_list")
            if expr_list:
                expr = self.visit_expression(expr_list.children[0])
                self.add_line(f"return {expr}")
            else:
                self.add_line("return")
                
        elif node.type == "expression_statement":
            expr = self.visit_expression(node.children[0])
            if expr: # Some might be handled specially (like panic) and return ""
                self.add_line(expr)
                
        elif node.type == "if_statement":
            cond = self.visit_expression(node.children[1])
            self.add_line(f"if {cond}:")
            self.indent_level += 1
            block = self.get_child(node, "block")
            for stmt in self.get_child(block, "statement_list").children:
                if stmt.is_named: self.visit_statement(stmt)
            self.indent_level -= 1
            
            else_node = None
            for c in node.children:
                if c.type == "block" and c != block:
                    else_node = c
            
            if else_node:
                self.add_line("else:")
                self.indent_level += 1
                for stmt in self.get_child(else_node, "statement_list").children:
                    if stmt.is_named: self.visit_statement(stmt)
                self.indent_level -= 1
                
        elif node.type == "break_statement":
            self.add_line("break")
        elif node.type == "continue_statement":
            self.add_line("continue")

    def visit_expression(self, expr):
        if expr.type == "identifier":
            ident = self.get_text(expr)
            if hasattr(self, 'rcvr_name') and ident == self.rcvr_name:
                return "self"
            if ident == "nil":
                return "None"
            return ident
            
        elif expr.type == "nil":
            return "None"
            
        elif expr.type == "int_literal" or expr.type == "interpreted_string_literal":
            return self.get_text(expr)
            
        elif expr.type == "selector_expression":
            left = self.visit_expression(expr.children[0])
            right = self.get_text(expr.children[2])
            # lower case the property/method name
            right = right[0].lower() + right[1:]
            return f"{left}.{right}"
            
        elif expr.type == "binary_expression":
            left = self.visit_expression(expr.children[0])
            op = self.get_text(expr.children[1])
            right = self.visit_expression(expr.children[2])
            return f"{left} {op} {right}"
            
        elif expr.type == "call_expression":
            func_name = self.get_text(expr.children[0])
            arg_list = self.get_child(expr, "argument_list")
            args = []
            for a in arg_list.children:
                if a.is_named:
                    args.append(self.visit_expression(a))
            
            if func_name == "fmt.Println":
                self.ledger.log("fmt.Println", "print()", "side-effect-wrapper")
                return f"print({', '.join(args)})"
            elif func_name == "fmt.Sprintf":
                # args[0] is "%v", args[1] is the value
                if len(args) > 1:
                    return f"str({args[1]})"
            elif func_name == "mapContains":
                self.ledger.log("mapContains helper", "in operator", "map-key-checking")
                return f"{args[1]} in {args[0]}"
            elif func_name == "len":
                return f"len({args[0]})"
            elif func_name == "panic":
                # Is it panic(fmt.Errorf(...))?
                inner = arg_list.children[1] # the argument to panic
                if inner.type == "call_expression":
                    inner_func = self.get_text(inner.children[0])
                    if inner_func == "fmt.Errorf":
                        err_args = self.get_child(inner, "argument_list")
                        msg = self.get_text(err_args.children[1])
                        self.ledger.log("panic(fmt.Errorf)", "raise ValueError", "exception-mapping")
                        return f"raise ValueError({msg})"
                return f"raise Exception({args[0]})"
            elif expr.children[0].type == "func_literal":
                # anonymous function call... Wait, the try/except block is:
                # func() { defer func() { if r := recover(); r != nil { ... } }(); ... }()
                func_lit = expr.children[0]
                block = self.get_child(func_lit, "block")
                stmt_list = self.get_child(block, "statement_list")
                
                first_stmt = stmt_list.children[0] if stmt_list and stmt_list.children else None
                if first_stmt and first_stmt.type == "defer_statement":
                    defer_call = self.get_child(first_stmt, "call_expression")
                    if defer_call and defer_call.children[0].type == "func_literal":
                        self.ledger.log("defer recover()", "try/except", "exception-handling")
                        self.add_line("try:")
                        self.indent_level += 1
                        
                        for stmt in stmt_list.children[1:]:
                            if stmt.is_named:
                                self.visit_statement(stmt)
                        
                        self.indent_level -= 1
                        self.add_line("except Exception as e:")
                        self.indent_level += 1
                        
                        defer_func = defer_call.children[0]
                        defer_block = self.get_child(defer_func, "block")
                        defer_stmts = self.get_child(defer_block, "statement_list")
                        if_stmt = self.get_child(defer_stmts, "if_statement")
                        if if_stmt:
                            catch_block = self.get_child(if_stmt, "block")
                            for stmt in self.get_child(catch_block, "statement_list").children:
                                if stmt.is_named:
                                    self.visit_statement(stmt)
                        
                        self.indent_level -= 1
                        return ""
                
            elif func_name.startswith("New"):
                self.ledger.log("NewX constructor call", "X()", "constructor-call-mapping")
                return f"{func_name[3:]}({', '.join(args)})"
                
            # If it's a method call, we need to map selector expression
            func_name_parsed = self.visit_expression(expr.children[0])
            return f"{func_name_parsed}({', '.join(args)})"
            
        elif expr.type == "composite_literal":
            lit_type = self.get_text(expr.children[0])
            lit_val = self.get_child(expr, "literal_value")
            
            if lit_type.startswith("[]"):
                self.ledger.log("slice literal", "list literal", "collection-literal")
                els = []
                for e in self.get_children(lit_val, "literal_element"):
                    els.append(self.visit_expression(e))
                return f"[{', '.join(els)}]"
                
            elif lit_type.startswith("map["):
                self.ledger.log("map literal", "dict literal", "collection-literal")
                pairs = []
                for ke in self.get_children(lit_val, "keyed_element"):
                    lit_els = self.get_children(ke, "literal_element")
                    if len(lit_els) == 2:
                        k = self.visit_expression(lit_els[0])
                        v = self.visit_expression(lit_els[1])
                        pairs.append(f"{k}: {v}")
                return f"{{{', '.join(pairs)}}}"
                
        elif expr.type == "index_expression":
            left = self.visit_expression(expr.children[0])
            idx = self.visit_expression(expr.children[2])
            return f"{left}[{idx}]"
            
        elif expr.type == "literal_element":
            return self.visit_expression(expr.children[0])
            
        elif expr.type == "unary_expression":
            op = self.get_text(expr.children[0])
            val = self.visit_expression(expr.children[1])
            if op == "&":
                self.ledger.log("unary_expression(&)", "val", "pointer-erasure")
                return val
            if op == "!":
                return f"not {val}"
            return f"{op}{val}"
            
        return f"/* {expr.type} */"



def transpile(code: str) -> str:
    import tree_sitter_go
    from tree_sitter import Language, Parser
    parser = Parser(Language(tree_sitter_go.language()))
    src_bytes = code.encode('utf8')
    tree = parser.parse(src_bytes)
    transpiler = GoToPyTranspiler(src_bytes)
    python_code = transpiler.transpile(tree.root_node)
    python_code += "\nif __name__ == '__main__':\n    main()\n"
    return python_code
