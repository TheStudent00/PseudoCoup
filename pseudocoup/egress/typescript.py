from pseudocoup.core.ur_ast import (
    URNode, ModuleNode, FunctionDefNode, MethodDefNode, ClassDefNode, AssignmentNode,
    BinaryOpNode, CallNode, IdentifierNode, LiteralNode,
    ReturnNode, IfNode, WhileNode, ForNode, TryCatchNode, ListNode,
    DictNode, SubscriptNode, AttributeNode
)
from pseudocoup.core.ledger import Ledger

class TypeScriptEmitter:
    def __init__(self, ledger: Ledger):
        self.ledger = ledger
        self.indent_level = 0
        self.scopes = [{}]
        self.injected_wrappers = set()
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
            return 'any'
        mapping = {
            'int': 'number',
            'float': 'number',
            'bool': 'boolean',
            'str': 'string',
            'List[str]': 'string[]',
            'List[int]': 'number[]',
            'List[Any]': 'any[]',
            'Dict[str, int]': 'Record<string, number>',
            'Optional[int]': 'number | null',
            'Optional[Any]': 'any',
            'Any': 'any',
            'None': 'void',
            'Tuple[str, int]': 'any[]'
        }
        return mapping.get(py_type, py_type)

    def generate(self, node: URNode) -> str:
        if node is None:
            return "/* Unmapped */"
        method_name = f"visit_{node.__class__.__name__}"
        visitor = getattr(self, method_name, self.generic_visit)
        return visitor(node)

    def generic_visit(self, node: URNode) -> str:
        raise NotImplementedError(f"No visit_{node.__class__.__name__} method in TypeScriptEmitter")

    def visit_ModuleNode(self, node: ModuleNode) -> str:
        self.push_scope()
        self.injected_wrappers.add("builtins_py")
        
        # We need to collect wrapper dependencies from the AST first if possible,
        # but for simplicity, we append imports at the top at the end, 
        # or we generate body, see wrappers, and prepend.
        
        body_lines = []
        for stmt in node.body:
            if isinstance(stmt, LiteralNode) and isinstance(stmt.value, str):
                continue
            if isinstance(stmt, IfNode) and isinstance(stmt.condition, BinaryOpNode):
                if getattr(stmt.condition.left, 'name', '') == '__name__':
                    # Emit main() if it's typical python __name__ == '__main__'
                    body_lines.append(f"{self._indent()}main([]);")
                    continue
                    
            stmt_str = self.generate(stmt)
            if isinstance(stmt, (AssignmentNode, ReturnNode, IfNode, WhileNode, ForNode, TryCatchNode)):
                body_lines.append(stmt_str)
            elif isinstance(stmt, (ClassDefNode, FunctionDefNode)):
                body_lines.append(stmt_str)
            else:
                body_lines.append(f"{self._indent()}{stmt_str};")
                
        lines = []
        for wrapper in sorted(list(self.injected_wrappers)):
            lines.append(f"import * as {wrapper} from \"./{wrapper}\";")
        if self.injected_wrappers:
            lines.append("")
            
        lines.extend(body_lines)
            
        self.pop_scope()
        return "\n".join(lines)

    def visit_FunctionDefNode(self, node: FunctionDefNode) -> str:
        scope = f"{self.current_class_name}.{node.name}" if getattr(self, 'current_class_name', None) else node.name
        
        ret_type = node.metadata.get('type', 'any')
        ret_type = self.map_type(ret_type)
        if ret_type == 'any' and not getattr(self, 'current_class_name', None):
            ret_type = 'void'
            
        args_list = []
        sugared_args = set()
        body_statements = node.body[:]
        
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
            
        for arg in node.args:
            if isinstance(node, MethodDefNode) and arg.name in ("self", "this"):
                continue
            arg_type = self.ledger.get_type(scope, arg.name)
            if not arg_type: arg_type = arg.metadata.get('type', 'any')
            arg_type = self.map_type(arg_type)
            args_list.append(f"{arg.name}: {arg_type}")
            
        args_str = ", ".join(args_list)
        
        lines = []
        if node.name == "__init__" and getattr(self, 'current_class_name', None):
            lines.append(f"{self._indent()}constructor({args_str}) {{")
        elif isinstance(node, MethodDefNode):
            lines.append(f"{self._indent()}{node.name}({args_str}): {ret_type} {{")
        else:
            lines.append(f"{self._indent()}function {node.name}({args_str}): {ret_type} {{")
            
        self.push_scope()
        for arg in node.args:
            if isinstance(node, MethodDefNode) and arg.name in ("self", "this"): continue
            self.declare_var(arg.name)
            
        self.indent_level += 1
        for stmt in body_statements:
            stmt_str = self.generate(stmt)
            if isinstance(stmt, (AssignmentNode, ReturnNode, FunctionDefNode, MethodDefNode, ClassDefNode, IfNode, WhileNode, ForNode, TryCatchNode)):
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
        
        for field in node.fields:
            if isinstance(field, AssignmentNode) and getattr(field.left, 'name', None):
                var_type = field.left.metadata.get('type', 'var')
                var_type = self.map_type(var_type)
                lines.append(f"{self._indent()}{field.left.name}: {var_type};")
                self.declare_var(field.left.name)

        for method in node.methods:
            lines.append(self.generate(method))
            
        self.current_class_name = prev_class_name
        self.indent_level -= 1
        self.pop_scope()
        lines.append(f"{self._indent()}}}")
        return "\n".join(lines)

    def visit_AssignmentNode(self, node: AssignmentNode) -> str:
        right_str = self.generate(node.right) if node.right else "null"
        
        if isinstance(node.left, IdentifierNode) and not getattr(self, 'current_class_name', None) and not self.is_declared(node.left.name):
            var_type = node.left.metadata.get('type', 'any')
            var_type = self.map_type(var_type)
            left_str = f"let {node.left.name}: {var_type}"
            self.declare_var(node.left.name)
        elif isinstance(node.left, IdentifierNode) and getattr(self, 'current_class_name', None) and not self.is_declared(node.left.name):
            # If we are parsing class properties in python, they come as assignments in class body. 
            # In typescript we don't emit 'let' inside a class. This is handled by visit_ClassDefNode iterating over fields though.
            left_str = self.generate(node.left)
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
            return f"({left_str} in {right_str})"
        if op == "//":
            return f"Math.floor({left_str} / {right_str})"
        if op == "is":
            if right_str == "null": op = "==="
            else: return f"({left_str} instanceof {right_str})"
        elif op == "is not":
            if right_str == "null": op = "!=="
            else: return f"!({left_str} instanceof {right_str})"
            
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
            if func_str in ("len", "str", "print", "range"):
                self.injected_wrappers.add("builtins_py")
                func_str = f"builtins_py.{func_str}"
            elif func_str.startswith("math."):
                self.injected_wrappers.add("math_py")
                func_str = func_str.replace("math.", "math_py.", 1)
            elif func_str.startswith("os."):
                self.injected_wrappers.add("io_py")
                func_str = func_str.replace("os.", "io_py.", 1)
            elif func_str.startswith("requests."):
                self.injected_wrappers.add("network_py")
                func_str = func_str.replace("requests.", "network_py.", 1)
                
        args_str = ", ".join(self.generate(arg) for arg in node.args)
        
        if func_str == "throw":
            return f"throw {args_str}"
        elif func_str == "ValueError":
            return f"new Error({args_str})"
            
        # Capitalized function name implies a class instantiation, TS requires 'new'
        if isinstance(func_val, IdentifierNode) and func_val.name[0].isupper() and func_val.name not in ("Exception", "Error"):
            return f"new {func_str}({args_str})"
            
        return f"{func_str}({args_str})"

    def visit_IdentifierNode(self, node: IdentifierNode) -> str:
        if node.name == "self": return "this"
        if node.name == "Exception": return "Error"
        return node.name

    def visit_LiteralNode(self, node: LiteralNode) -> str:
        if isinstance(node.value, bool):
            return "true" if node.value else "false"
        elif isinstance(node.value, str):
            return f'"{node.value}"'
        elif node.value is None:
            return "null"
        else:
            return str(node.value)

    def visit_IfNode(self, node: IfNode) -> str:
        condition_str = self.generate(node.condition)
        lines = [f"{self._indent()}if ({condition_str}) {{"]
        self.push_scope()
        self.indent_level += 1
        for stmt in node.body:
            stmt_str = self.generate(stmt)
            if isinstance(stmt, (AssignmentNode, ReturnNode, FunctionDefNode, MethodDefNode, ClassDefNode, IfNode, WhileNode, ForNode, TryCatchNode)):
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
                        if isinstance(stmt, (AssignmentNode, ReturnNode, FunctionDefNode, MethodDefNode, ClassDefNode, IfNode, WhileNode, ForNode, TryCatchNode)):
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
                lines.append(f"{self._indent()}}} else {{")
                pass
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
            if isinstance(stmt, (AssignmentNode, ReturnNode, FunctionDefNode, MethodDefNode, ClassDefNode, IfNode, WhileNode, ForNode, TryCatchNode)):
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
            if not self.is_declared(node.target.name):
                target_str = f"let {node.target.name}"
                self.declare_var(node.target.name)
                
        lines = [f"{self._indent()}for ({target_str} of {iter_str}) {{"]
        self.indent_level += 1
        for stmt in node.body:
            stmt_str = self.generate(stmt)
            if isinstance(stmt, (AssignmentNode, ReturnNode, FunctionDefNode, MethodDefNode, ClassDefNode, IfNode, WhileNode, ForNode, TryCatchNode)):
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
            if isinstance(stmt, (AssignmentNode, ReturnNode, FunctionDefNode, MethodDefNode, ClassDefNode, IfNode, WhileNode, ForNode, TryCatchNode)):
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
            if isinstance(stmt, (AssignmentNode, ReturnNode, FunctionDefNode, MethodDefNode, ClassDefNode, IfNode, WhileNode, ForNode, TryCatchNode)):
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
        if not node.keys:
            return "{}"
        pairs = []
        for k, v in zip(node.keys, node.values):
            pairs.append(f"{self.generate(k)}: {self.generate(v)}")
        pairs_str = ", ".join(pairs)
        return f"{{ {pairs_str} }}"

    def visit_SubscriptNode(self, node: SubscriptNode) -> str:
        value_str = self.generate(node.value)
        slice_str = self.generate(node.slice)
        return f"{value_str}[{slice_str}]"

    def visit_AttributeNode(self, node: AttributeNode) -> str:
        value_str = self.generate(node.value)
        return f"{value_str}.{node.attr}"
