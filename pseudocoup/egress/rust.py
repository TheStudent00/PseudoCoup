from pseudocoup.core.ur_ast import (
    URNode, ModuleNode, FunctionDefNode, MethodDefNode, ClassDefNode, AssignmentNode,
    BinaryOpNode, CallNode, IdentifierNode, LiteralNode,
    ReturnNode, IfNode, WhileNode, ForNode, TryCatchNode, ListNode,
    DictNode, SubscriptNode, AttributeNode
)
from pseudocoup.core.ledger import Ledger

class RustEmitter:
    def __init__(self, ledger: Ledger):
        self.ledger = ledger
        self.indent_level = 0
        self.scopes = [{}]
        self.current_class_name = None
        self.current_func_name = None

    def _indent(self) -> str:
        return "    " * self.indent_level

    def push_scope(self):
        self.scopes.append(set())

    def pop_scope(self):
        self.scopes.pop()

    def declare_var(self, name: str):
        self.scopes[-1].add(name)

    def is_declared(self, name: str) -> bool:
        for scope in reversed(self.scopes):
            if name in scope:
                return True
        return False

    def map_type(self, py_type: str) -> str:
        if not py_type or py_type == 'var' or py_type == 'dynamic' or py_type == 'Any':
            return 'Any'
        mapping = {
            'int': 'i32',
            'float': 'f64',
            'bool': 'bool',
            'str': 'String',
            'List[str]': 'Vec<String>',
            'List[int]': 'Vec<i32>',
            'List[Any]': 'Vec<Any>',
            'Dict[str, int]': 'HashMap<String, i32>',
            'Optional[int]': 'Option<i32>',
            'Optional[Any]': 'Option<Any>',
            'Any': 'Any',
            'None': '()',
            'Void': '()',
            'Tuple[str, int]': 'Any'
        }
        return mapping.get(py_type, py_type)

    def generate(self, node: URNode) -> str:
        if node is None:
            return "/* Unmapped */"
        method_name = f"visit_{node.__class__.__name__}"
        visitor = getattr(self, method_name, self.generic_visit)
        return visitor(node)

    def generic_visit(self, node: URNode) -> str:
        raise NotImplementedError(f"No visit_{node.__class__.__name__} method in RustEmitter")

    def visit_ModuleNode(self, node: ModuleNode) -> str:
        self.push_scope()
        
        body_lines = []
        for stmt in node.body:
            if isinstance(stmt, LiteralNode) and isinstance(stmt.value, str):
                continue
            
            stmt_str = self.generate(stmt)
            if isinstance(stmt, (AssignmentNode, ReturnNode, IfNode, WhileNode, ForNode, TryCatchNode)):
                # Note: floating statements in Rust ModuleNode will just be emitted as is. 
                # If they are top level, it might not compile, but we trust the AST or assume testing structure accommodates.
                body_lines.append(stmt_str)
            elif isinstance(stmt, (ClassDefNode, FunctionDefNode)):
                body_lines.append(stmt_str)
            else:
                body_lines.append(f"{self._indent()}{stmt_str}")
                
        self.pop_scope()
        return "\n".join(body_lines)

    def visit_FunctionDefNode(self, node: FunctionDefNode) -> str:
        scope = f"{self.current_class_name}.{node.name}" if getattr(self, 'current_class_name', None) else node.name
        
        ret_type = node.metadata.get('type', 'Any')
        ret_type = self.map_type(ret_type)
        if ret_type == 'Any' and not getattr(self, 'current_class_name', None):
            ret_type = '()'
            
        args_list = []
        sugared_args = set()
        body_statements = node.body[:]
        
        if node.name == "__init__" and getattr(self, 'current_class_name', None):
            ret_type = "Self"
            
        for arg in node.args:
            if isinstance(node, MethodDefNode) and arg.name in ("self", "this"):
                # Handled later via &mut self
                continue
            arg_type = self.ledger.get_type(scope, arg.name)
            if not arg_type: arg_type = arg.metadata.get('type', 'Any')
            arg_type = self.map_type(arg_type)
            args_list.append(f"{arg.name}: {arg_type}")
            
        args_str = ", ".join(args_list)
        
        lines = []
        if isinstance(node, MethodDefNode):
            if node.name == "__init__":
                lines.append(f"{self._indent()}fn new({args_str}) -> {ret_type} {{")
            else:
                receiver = "&mut self"
                # Some heuristics might use &self, but for simplicity we'll use &mut self
                prefix = f"{receiver}, " if args_str else receiver
                lines.append(f"{self._indent()}fn {node.name}({prefix}{args_str}) -> {ret_type} {{")
        else:
            lines.append(f"{self._indent()}fn {node.name}({args_str}) -> {ret_type} {{")
            
        self.push_scope()
        for arg in node.args:
            if isinstance(node, MethodDefNode) and arg.name in ("self", "this"): continue
            self.declare_var(arg.name)
            
        self.indent_level += 1
        
        if node.name == "__init__" and getattr(self, 'current_class_name', None):
            # Try to build struct initialization from simple self.x = val statements
            init_fields = []
            other_statements = []
            for stmt in body_statements:
                if isinstance(stmt, AssignmentNode):
                    left = stmt.left
                    right = stmt.right
                    if isinstance(left, AttributeNode) and isinstance(left.value, IdentifierNode) and left.value.name in ("self", "this"):
                        field_name = left.attr
                        val_str = self.generate(right)
                        init_fields.append(f"{field_name}: {val_str}")
                    else:
                        other_statements.append(stmt)
                else:
                    other_statements.append(stmt)
                    
            for stmt in other_statements:
                stmt_str = self.generate(stmt)
                if not stmt_str.endswith(";") and not stmt_str.endswith("}"):
                    stmt_str += ";"
                lines.append(f"{self._indent()}{stmt_str}")
                
            init_str = ", ".join(init_fields)
            lines.append(f"{self._indent()}Self {{ {init_str} }}")
        else:
            for i, stmt in enumerate(body_statements):
                stmt_str = self.generate(stmt)
                
                if isinstance(stmt, (AssignmentNode, ReturnNode)):
                    lines.append(f"{stmt_str};")
                elif isinstance(stmt, (IfNode, WhileNode, ForNode, TryCatchNode)):
                    lines.append(stmt_str)
                else:
                    # In Rust, statements need a semicolon, but the last one can be the return value if missing it.
                    # For simplicity, we just add semicolons to expressions unless they are explicitly returns in UR-AST?
                    if not stmt_str.endswith(";") and not stmt_str.endswith("}"):
                        stmt_str += ";"
                    lines.append(f"{self._indent()}{stmt_str}")
                
        self.indent_level -= 1
        self.pop_scope()
        lines.append(f"{self._indent()}}}")
        return "\n".join(lines)

    def visit_MethodDefNode(self, node: MethodDefNode) -> str:
        return self.visit_FunctionDefNode(node)

    def visit_ClassDefNode(self, node: ClassDefNode) -> str:
        lines = []
        
        lines.append(f"{self._indent()}struct {node.name} {{")
        self.push_scope()
        self.indent_level += 1
        
        prev_class_name = getattr(self, 'current_class_name', None)
        self.current_class_name = node.name
        
        fields = []
        for field in node.fields:
            if isinstance(field, AssignmentNode) and getattr(field.left, 'name', None):
                var_type = field.left.metadata.get('type', 'var')
                var_type = self.map_type(var_type)
                lines.append(f"{self._indent()}{field.left.name}: {var_type},")
                self.declare_var(field.left.name)
                
        self.indent_level -= 1
        lines.append(f"{self._indent()}}}")
        lines.append("")
        
        lines.append(f"{self._indent()}impl {node.name} {{")
        self.indent_level += 1
        
        for method in node.methods:
            lines.append(self.generate(method))
            
        self.current_class_name = prev_class_name
        self.indent_level -= 1
        self.pop_scope()
        lines.append(f"{self._indent()}}}")
        return "\n".join(lines)

    def visit_AssignmentNode(self, node: AssignmentNode) -> str:
        right_str = self.generate(node.right) if node.right else "None"
        
        if isinstance(node.left, IdentifierNode) and not getattr(self, 'current_class_name', None) and not self.is_declared(node.left.name):
            var_type = node.left.metadata.get('type', 'Any')
            var_type = self.map_type(var_type)
            left_str = f"let mut {node.left.name}: {var_type}"
            self.declare_var(node.left.name)
        elif isinstance(node.left, IdentifierNode) and getattr(self, 'current_class_name', None) and not self.is_declared(node.left.name):
            left_str = self.generate(node.left)
        else:
            left_str = self.generate(node.left)
            
        return f"{self._indent()}{left_str} = {right_str}"

    def visit_ReturnNode(self, node: ReturnNode) -> str:
        if node.value is None:
            return f"{self._indent()}return"
        val_str = self.generate(node.value)
        return f"{self._indent()}return {val_str}"

    def visit_BinaryOpNode(self, node: BinaryOpNode) -> str:
        left_str = self.generate(node.left)
        right_str = self.generate(node.right)
        op = node.operator
        
        if op == "//": return f"({left_str} / {right_str})"
        if op == "is": return f"({left_str} == {right_str})"
        if op == "is not": return f"({left_str} != {right_str})"
            
        if op == "and": op = "&&"
        if op == "or": op = "||"
            
        if getattr(node.left, 'name', None) == "":
            if op == "not": op = "!"
            return f"{op}({right_str})"
            
        return f"({left_str} {op} {right_str})"

    def visit_CallNode(self, node: CallNode) -> str:
        func_val = node.func_name
        if isinstance(func_val, IdentifierNode):
            func_str = func_val.name
        elif isinstance(func_val, str):
            func_str = func_val
        else:
            func_str = self.generate(func_val)
            
        if isinstance(func_str, str):
            if func_str == "print":
                func_str = "println!"
            elif func_str == "len":
                func_str = "builtins_py::len"
            elif func_str == "str":
                func_str = "builtins_py::str"
            elif func_str == "range":
                func_str = "builtins_py::range"
            elif func_str.startswith("math."):
                func_str = func_str.replace("math.", "math_py::", 1)
            elif func_str.startswith("os."):
                func_str = func_str.replace("os.", "io_py::", 1)
            elif func_str.startswith("requests."):
                func_str = func_str.replace("requests.", "network_py::", 1)
            elif "." in func_str and "::" not in func_str and "builtins_py" not in func_str and func_str != "format":
                pass
                
        if func_str == "throw":
            args_str = ", ".join(self.generate(arg) for arg in node.args)
            return f"panic!({args_str})"
            
        if func_str == "format":
            args_str = ", ".join(self.generate(arg) for arg in node.args)
            return f"format!({args_str})"
            
        if "::new" not in func_str and func_str[0].isupper() and "." not in func_str and func_str != "Option" and func_str != "Any":
            func_str = f"{func_str}::new"

        args_str = ", ".join(self.generate(arg) for arg in node.args)
        return f"{func_str}({args_str})"

    def visit_IdentifierNode(self, node: IdentifierNode) -> str:
        if node.name == "self": return "self"
        if node.name == "Exception": return "Exception"
        return node.name

    def visit_LiteralNode(self, node: LiteralNode) -> str:
        if isinstance(node.value, bool):
            return "true" if node.value else "false"
        elif isinstance(node.value, str):
            return f'"{node.value}"'
        elif node.value is None:
            return "None"
        else:
            if isinstance(node.value, float):
                # Ensure float literal has a decimal
                s = str(node.value)
                if "." not in s: s += ".0"
                return s
            return str(node.value)

    def visit_IfNode(self, node: IfNode) -> str:
        condition_str = self.generate(node.condition)
        lines = [f"{self._indent()}if {condition_str} {{"]
        self.push_scope()
        self.indent_level += 1
        for stmt in node.body:
            stmt_str = self.generate(stmt)
            if isinstance(stmt, (AssignmentNode, ReturnNode)):
                lines.append(f"{stmt_str};")
            elif isinstance(stmt, (IfNode, WhileNode, ForNode, TryCatchNode)):
                lines.append(stmt_str)
            else:
                if not stmt_str.endswith(";") and not stmt_str.endswith("}"):
                    stmt_str += ";"
                lines.append(f"{self._indent()}{stmt_str}")
        self.indent_level -= 1
        self.pop_scope()
        
        if node.orelse:
            if isinstance(node.orelse, IfNode):
                if isinstance(node.orelse.condition, LiteralNode) and node.orelse.condition.value is True:
                    lines.append(f"{self._indent()}}} else {{")
                    self.push_scope()
                    self.indent_level += 1
                    for stmt in node.orelse.body:
                        stmt_str = self.generate(stmt)
                        if isinstance(stmt, (AssignmentNode, ReturnNode)):
                            lines.append(f"{stmt_str};")
                        elif isinstance(stmt, (IfNode, WhileNode, ForNode, TryCatchNode)):
                            lines.append(stmt_str)
                        else:
                            if not stmt_str.endswith(";") and not stmt_str.endswith("}"):
                                stmt_str += ";"
                            lines.append(f"{self._indent()}{stmt_str}")
                    self.indent_level -= 1
                    self.pop_scope()
                    lines.append(f"{self._indent()}}}")
                else:
                    orelse_str = self.generate(node.orelse).lstrip()
                    lines.append(f"{self._indent()}}} else {orelse_str}")
            else:
                lines.append(f"{self._indent()}}} else {{")
        else:
            lines.append(f"{self._indent()}}}")
        return "\n".join(lines)

    def visit_WhileNode(self, node: WhileNode) -> str:
        condition_str = self.generate(node.condition)
        lines = [f"{self._indent()}while {condition_str} {{"]
        self.push_scope()
        self.indent_level += 1
        for stmt in node.body:
            stmt_str = self.generate(stmt)
            if isinstance(stmt, (AssignmentNode, ReturnNode)):
                lines.append(f"{stmt_str};")
            elif isinstance(stmt, (IfNode, WhileNode, ForNode, TryCatchNode)):
                lines.append(stmt_str)
            else:
                if not stmt_str.endswith(";") and not stmt_str.endswith("}"):
                    stmt_str += ";"
                lines.append(f"{self._indent()}{stmt_str}")
        self.indent_level -= 1
        self.pop_scope()
        lines.append(f"{self._indent()}}}")
        return "\n".join(lines)

    def visit_ForNode(self, node: ForNode) -> str:
        target_str = self.generate(node.target)
        iter_str = self.generate(node.iter)
        self.push_scope()
        
        lines = [f"{self._indent()}for {target_str} in {iter_str} {{"]
        self.indent_level += 1
        for stmt in node.body:
            stmt_str = self.generate(stmt)
            if isinstance(stmt, (AssignmentNode, ReturnNode)):
                lines.append(f"{stmt_str};")
            elif isinstance(stmt, (IfNode, WhileNode, ForNode, TryCatchNode)):
                lines.append(stmt_str)
            else:
                if not stmt_str.endswith(";") and not stmt_str.endswith("}"):
                    stmt_str += ";"
                lines.append(f"{self._indent()}{stmt_str}")
        self.indent_level -= 1
        self.pop_scope()
        lines.append(f"{self._indent()}}}")
        return "\n".join(lines)

    def visit_TryCatchNode(self, node: TryCatchNode) -> str:
        # Rust does not have standard try catch. Just emitting it as is via a comment and the body.
        # Alternatively, we map to `catch_unwind`, but let's just do a comment.
        lines = [f"{self._indent()}// try {{"]
        self.push_scope()
        self.indent_level += 1
        for stmt in node.body:
            stmt_str = self.generate(stmt)
            if isinstance(stmt, (AssignmentNode, ReturnNode)):
                lines.append(f"{stmt_str};")
            elif isinstance(stmt, (IfNode, WhileNode, ForNode, TryCatchNode)):
                lines.append(stmt_str)
            else:
                if not stmt_str.endswith(";") and not stmt_str.endswith("}"):
                    stmt_str += ";"
                lines.append(f"{self._indent()}{stmt_str}")
        self.indent_level -= 1
        self.pop_scope()
        
        lines.append(f"{self._indent()}// }} catch {{")
        self.push_scope()
        self.declare_var("e")
        self.indent_level += 1
        for stmt in node.handlers:
            stmt_str = self.generate(stmt)
            if isinstance(stmt, (AssignmentNode, ReturnNode)):
                lines.append(f"{stmt_str};")
            elif isinstance(stmt, (IfNode, WhileNode, ForNode, TryCatchNode)):
                lines.append(stmt_str)
            else:
                if not stmt_str.endswith(";") and not stmt_str.endswith("}"):
                    stmt_str += ";"
                lines.append(f"{self._indent()}{stmt_str}")
        self.indent_level -= 1
        self.pop_scope()
        lines.append(f"{self._indent()}// }}")
        return "\n".join(lines)

    def visit_ListNode(self, node: ListNode) -> str:
        elements_str = ", ".join(self.generate(e) for e in node.elements)
        return f"vec![{elements_str}]"

    def visit_DictNode(self, node: DictNode) -> str:
        if not node.keys:
            return "builtins_py::hashmap!()"
        pairs = []
        for k, v in zip(node.keys, node.values):
            pairs.append(f"{self.generate(k)} => {self.generate(v)}")
        pairs_str = ", ".join(pairs)
        return f"builtins_py::hashmap!({pairs_str})"

    def visit_SubscriptNode(self, node: SubscriptNode) -> str:
        value_str = self.generate(node.value)
        slice_str = self.generate(node.slice)
        return f"{value_str}[{slice_str}]"

    def visit_AttributeNode(self, node: AttributeNode) -> str:
        value_str = self.generate(node.value)
        # Check if the left hand is format string syntax `"".format(args)`
        if value_str == '""' and node.attr == "format":
            return "format"
        return f"{value_str}.{node.attr}"
