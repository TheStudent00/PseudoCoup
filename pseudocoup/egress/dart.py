from pseudocoup.core.ur_ast import (
    URNode, ModuleNode, FunctionDefNode, MethodDefNode, ClassDefNode, AssignmentNode,
    BinaryOpNode, CallNode, IdentifierNode, LiteralNode,
    ReturnNode, IfNode, WhileNode, ForNode, TryCatchNode, ListNode,
    DictNode, SubscriptNode, AttributeNode
)

class DartEmitter:
    def __init__(self, ledger):
        self.ledger = ledger
        self.indent_level = 0
        self.scopes = [{}]  # List of sets for tracking variable declarations
        self.injected_wrappers = set()

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
        if not py_type or py_type == 'var' or py_type == 'dynamic':
            return 'var'
        mapping = {
            'int': 'int',
            'str': 'String',
            'float': 'double',
            'bool': 'bool',
            'List[str]': 'List<String>',
            'List[int]': 'List<int>',
            'Dict[str, int]': 'Map<String, int>',
            'Optional[int]': 'int?',
            'Optional[Any]': 'dynamic',
            'Any': 'dynamic',
            'None': 'void',
            'Tuple[str, int]': 'List<dynamic>'
        }
        return mapping.get(py_type, py_type)

    def generate(self, node: URNode) -> str:
        if node is None:
            return "/* Unmapped */"
        method_name = f"visit_{node.__class__.__name__}"
        visitor = getattr(self, method_name, self.generic_visit)
        return visitor(node)

    def generic_visit(self, node: URNode) -> str:
        raise NotImplementedError(f"No visit_{node.__class__.__name__} method")

    def visit_ModuleNode(self, node: ModuleNode) -> str:
        self.push_scope()
        self.injected_wrappers.add("builtins_py")
        lines = []
        for wrapper in sorted(list(self.injected_wrappers)):
            lines.append(f"import '{wrapper}.dart';")
        if self.injected_wrappers:
            lines.append("")
            
        for stmt in node.body:
            # Filter out top-level strings (docstrings)
            if isinstance(stmt, LiteralNode) and isinstance(stmt.value, str):
                continue
            # Filter out Python execution hook if __name__ == "__main__"
            if isinstance(stmt, IfNode) and isinstance(stmt.condition, BinaryOpNode):
                if getattr(stmt.condition.left, 'name', '') == '__name__':
                    continue
                    
            stmt_str = self.generate(stmt)
            if isinstance(stmt, (AssignmentNode, ReturnNode, FunctionDefNode, MethodDefNode, ClassDefNode)):
                lines.append(stmt_str)
            else:
                lines.append(f"{self._indent()}{stmt_str};")
        self.pop_scope()
        return "\n\n".join(lines)

    def visit_FunctionDefNode(self, node: FunctionDefNode) -> str:
        if getattr(self, 'current_class_name', None):
            scope = f"{self.current_class_name}.{node.name}"
        else:
            scope = node.name
            
        ret_type = node.metadata.get('type', 'dynamic')
        ret_type = self.map_type(ret_type)
        
        body_statements = node.body[:]
        sugared_args = set()
        
        # Unroll constructor assignments (self.x = x) into this.x params
        if node.name == "__init__" and getattr(self, 'current_class_name', None):
            idx = 0
            while idx < len(body_statements):
                stmt = body_statements[idx]
                if isinstance(stmt, AssignmentNode):
                    left = stmt.left
                    right = stmt.right
                    if isinstance(left, AttributeNode) and isinstance(left.value, IdentifierNode) and left.value.name in ("self", "this"):
                        if isinstance(right, IdentifierNode) and right.name == left.attr:
                            sugared_args.add(right.name)
                            idx += 1
                            continue
                break
            body_statements = body_statements[idx:]
        
        args_list = []
        for arg in node.args:
            if isinstance(node, MethodDefNode) and arg.name in ("self", "this"):
                continue
                
            if arg.name in sugared_args:
                args_list.append(f"this.{arg.name}")
            else:
                arg_type = self.ledger.get_type(scope, arg.name)
                if not arg_type:
                    arg_type = arg.metadata.get('type', 'dynamic')
                arg_type = self.map_type(arg_type)
                args_list.append(f"{arg_type} {arg.name}")
        
        args_str = ", ".join(args_list)
        
        lines = []
        if node.name == "__init__" and getattr(self, 'current_class_name', None):
            if not body_statements:
                lines.append(f"{self._indent()}{self.current_class_name}({args_str});")
                return "\n".join(lines)
            else:
                lines.append(f"{self._indent()}{self.current_class_name}({args_str}) {{")
        else:
            lines.append(f"{self._indent()}{ret_type} {node.name}({args_str}) {{")
        
        self.push_scope()
        for arg in node.args:
            if isinstance(node, MethodDefNode) and arg.name in ("self", "this"):
                continue
            self.declare_var(arg.name)
            
        self.indent_level += 1
        for stmt in body_statements:
            stmt_str = self.generate(stmt)
            if isinstance(stmt, (AssignmentNode, ReturnNode, FunctionDefNode, MethodDefNode, ClassDefNode)):
                lines.append(stmt_str)
            else:
                lines.append(f"{self._indent()}{stmt_str};")
            
        self.indent_level -= 1
        self.pop_scope()
        
        lines.append(f"{self._indent()}}}")
        return "\n".join(lines)

    def visit_MethodDefNode(self, node: MethodDefNode) -> str:
        return self.visit_FunctionDefNode(node)

    def visit_ClassDefNode(self, node: ClassDefNode) -> str:
        lines = []
        bases_str = f" extends {node.bases[0]}" if getattr(node, 'bases', None) else ""
        lines.append(f"{self._indent()}class {node.name}{bases_str} {{")
        
        self.push_scope()
        self.indent_level += 1
        
        prev_class_name = getattr(self, 'current_class_name', None)
        self.current_class_name = node.name
        
        # Ensure all fields are emitted before methods.
        for field in node.fields:
            lines.append(self.generate(field))
            
        for method in node.methods:
            lines.append(self.generate(method))
            
        self.current_class_name = prev_class_name
        self.indent_level -= 1
        self.pop_scope()
        
        lines.append(f"{self._indent()}}}")
        return "\n".join(lines)

    def visit_AssignmentNode(self, node: AssignmentNode) -> str:
        if node.right is None:
            if isinstance(node.left, IdentifierNode) and not self.is_declared(node.left.name):
                var_type = node.left.metadata.get('type', 'var')
                var_type = self.map_type(var_type)
                self.declare_var(node.left.name)
                default = ""
                if var_type == "int": default = " = 0"
                elif var_type == "double": default = " = 0.0"
                elif var_type == "bool": default = " = false"
                elif var_type == "String": default = " = \"\""
                return f"{self._indent()}{var_type} {node.left.name}{default};"
            else:
                left_str = self.generate(node.left)
                return f"{self._indent()}{left_str};"

        right_str = self.generate(node.right)
        
        if isinstance(node.left, IdentifierNode) and not self.is_declared(node.left.name):
            var_type = node.left.metadata.get('type', 'var')
            var_type = self.map_type(var_type)
            left_str = f"{var_type} {node.left.name}"
            self.declare_var(node.left.name)
        else:
            left_str = self.generate(node.left)
            
        return f"{self._indent()}{left_str} = {right_str};"

    def visit_ReturnNode(self, node: ReturnNode) -> str:
        if node.value is None:
            return f"{self._indent()}return;"
        val_str = self.generate(node.value)
        return f"{self._indent()}return {val_str};"

    def visit_BinaryOpNode(self, node: BinaryOpNode) -> str:
        left_str = self.generate(node.left)
        right_str = self.generate(node.right)
        op = node.operator
        if op == "in":
            return f"{right_str}.contains({left_str})"
        if op == "//":
            op = "~/"
        if op == "is" and right_str == "null":
            op = "=="
        
        if getattr(node.left, 'name', None) == "":
            return f"{op}({right_str})"
            
        return f"{left_str} {op} {right_str}"

    def visit_CallNode(self, node: CallNode) -> str:
        func_val = node.func_name
        if isinstance(func_val, IdentifierNode):
            func_str = func_val.name
        elif isinstance(func_val, str):
            func_str = func_val
        else:
            func_str = self.generate(func_val)

        if func_str == "len" and node.args:
            arg_str = self.generate(node.args[0])
            return f"{arg_str}.length"
        if func_str == "str" and node.args:
            arg_str = self.generate(node.args[0])
            return f"({arg_str}).toString()"
            
        if isinstance(func_str, str):
            if func_str.startswith("math."):
                self.injected_wrappers.add("math_py")
                func_str = func_str.replace("math.", "math_py.", 1)
            elif func_str.startswith("os."):
                self.injected_wrappers.add("io_py")
                func_str = func_str.replace("os.", "io_py.", 1)
            elif func_str.startswith("requests."):
                self.injected_wrappers.add("network_py")
                func_str = func_str.replace("requests.", "network_py.", 1)
        else:
            func_str = str(func_str)
            
        args_str = ", ".join(self.generate(arg) for arg in node.args)
        return f"{func_str}({args_str})"

    def visit_IdentifierNode(self, node: IdentifierNode) -> str:
        if node.name == "self":
            return "this"
        return node.name

    def visit_LiteralNode(self, node: LiteralNode) -> str:
        if isinstance(node.value, bool):
            return "true" if node.value else "false"
        elif isinstance(node.value, str):
            return f'"{node.value}"'
        else:
            return str(node.value)

    def visit_IfNode(self, node: IfNode) -> str:
        condition_str = self.generate(node.condition)
        lines = [f"{self._indent()}if ({condition_str}) {{"]
        
        self.push_scope()
        self.indent_level += 1
        for stmt in node.body:
            stmt_str = self.generate(stmt)
            if isinstance(stmt, (AssignmentNode, ReturnNode, FunctionDefNode, MethodDefNode, ClassDefNode)):
                lines.append(stmt_str)
            else:
                lines.append(f"{self._indent()}{stmt_str};")
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
                        if isinstance(stmt, (AssignmentNode, ReturnNode, FunctionDefNode, MethodDefNode, ClassDefNode)):
                            lines.append(stmt_str)
                        else:
                            lines.append(f"{self._indent()}{stmt_str};")
                    self.indent_level -= 1
                    self.pop_scope()
                    lines.append(f"{self._indent()}}}")
                else:
                    orelse_str = self.generate(node.orelse).lstrip()
                    lines.append(f"{self._indent()}}} else {orelse_str}")
        else:
            lines.append(f"{self._indent()}}}")
            
        return "\n".join(lines)

    def visit_WhileNode(self, node: WhileNode) -> str:
        condition_str = self.generate(node.condition)
        lines = [f"{self._indent()}while ({condition_str}) {{"]
        
        self.push_scope()
        self.indent_level += 1
        for stmt in node.body:
            stmt_str = self.generate(stmt)
            if isinstance(stmt, (AssignmentNode, ReturnNode, FunctionDefNode, MethodDefNode, ClassDefNode)):
                lines.append(stmt_str)
            else:
                lines.append(f"{self._indent()}{stmt_str};")
        self.indent_level -= 1
        self.pop_scope()
        lines.append(f"{self._indent()}}}")
        return "\n".join(lines)

    def visit_ForNode(self, node: ForNode) -> str:
        target_str = self.generate(node.target)
        iter_str = self.generate(node.iter)
        
        self.push_scope()
        if isinstance(node.target, IdentifierNode):
            self.declare_var(node.target.name)
            
        lines = [f"{self._indent()}for (var {target_str} in {iter_str}) {{"]
        self.indent_level += 1
        for stmt in node.body:
            stmt_str = self.generate(stmt)
            if isinstance(stmt, (AssignmentNode, ReturnNode, FunctionDefNode, MethodDefNode, ClassDefNode)):
                lines.append(stmt_str)
            else:
                lines.append(f"{self._indent()}{stmt_str};")
        self.indent_level -= 1
        self.pop_scope()
        lines.append(f"{self._indent()}}}")
        return "\n".join(lines)

    def visit_TryCatchNode(self, node: TryCatchNode) -> str:
        lines = [f"{self._indent()}try {{"]
        self.push_scope()
        self.indent_level += 1
        for stmt in node.body:
            stmt_str = self.generate(stmt)
            if isinstance(stmt, (AssignmentNode, ReturnNode, FunctionDefNode, MethodDefNode, ClassDefNode)):
                lines.append(stmt_str)
            else:
                lines.append(f"{self._indent()}{stmt_str};")
        self.indent_level -= 1
        self.pop_scope()
        
        lines.append(f"{self._indent()}}} catch (e) {{")
        self.push_scope()
        self.declare_var("e")
        self.indent_level += 1
        
        for stmt in node.handlers:
            stmt_str = self.generate(stmt)
            if isinstance(stmt, (AssignmentNode, ReturnNode, FunctionDefNode, MethodDefNode, ClassDefNode)):
                lines.append(stmt_str)
            else:
                lines.append(f"{self._indent()}{stmt_str};")
                    
        self.indent_level -= 1
        self.pop_scope()
        lines.append(f"{self._indent()}}}")
        return "\n".join(lines)

    def visit_ListNode(self, node: ListNode) -> str:
        elements_str = ", ".join(self.generate(e) for e in node.elements)
        return f"[{elements_str}]"

    def visit_DictNode(self, node: DictNode) -> str:
        pairs = []
        for k, v in zip(node.keys, node.values):
            pairs.append(f"{self.generate(k)}: {self.generate(v)}")
        pairs_str = ", ".join(pairs)
        return f"{{{pairs_str}}}"

    def visit_SubscriptNode(self, node: SubscriptNode) -> str:
        value_str = self.generate(node.value)
        slice_str = self.generate(node.slice)
        return f"{value_str}[{slice_str}]"

    def visit_AttributeNode(self, node: AttributeNode) -> str:
        value_str = self.generate(node.value)
        return f"{value_str}.{node.attr}"


