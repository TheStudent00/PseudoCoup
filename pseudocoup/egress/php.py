from pseudocoup.core.ur_ast import (
    URNode, ModuleNode, FunctionDefNode, MethodDefNode, ClassDefNode, AssignmentNode,
    BinaryOpNode, CallNode, IdentifierNode, LiteralNode,
    ReturnNode, IfNode, WhileNode, ForNode, TryCatchNode, ListNode,
    DictNode, SubscriptNode, AttributeNode
)
from pseudocoup.core.ledger import Ledger

class PhpEmitter:
    def __init__(self, ledger: Ledger):
        self.ledger = ledger
        self.indent_level = 0
        self.current_scope = []
        self.in_call_target = False

    def _indent(self) -> str:
        return "    " * self.indent_level

    def generate(self, node: URNode) -> str:
        if node is None:
            return "null"
        method_name = f"visit_{node.__class__.__name__}"
        visitor = getattr(self, method_name, self.generic_visit)
        return visitor(node)

    def generic_visit(self, node: URNode) -> str:
        raise NotImplementedError(f"No visit_{node.__class__.__name__} method in PhpEmitter")

    def _map_php_type(self, t: str) -> str:
        if t == "str": return "string"
        if t in ("int", "float", "bool"): return t
        return ""

    def visit_ModuleNode(self, node: ModuleNode) -> str:
        body_lines = [
            "<?php",
            "require_once 'builtins_py.php';",
            ""
        ]
        
        self.current_scope.append("")
        for stmt in node.body:
            if isinstance(stmt, LiteralNode) and isinstance(stmt.value, str):
                continue
            
            stmt_str = self.generate(stmt)
            if isinstance(stmt, (ClassDefNode, FunctionDefNode, MethodDefNode, IfNode, WhileNode, ForNode, TryCatchNode)):
                body_lines.append(stmt_str)
            else:
                body_lines.append(f"{self._indent()}{stmt_str};")
                
        self.current_scope.pop()
        return "\n".join(body_lines)

    def visit_FunctionDefNode(self, node: FunctionDefNode) -> str:
        name = node.name
        is_method = isinstance(node, MethodDefNode)
        if is_method and name == "__init__":
            name = "__construct"
            
        fqdn = ".".join(s for s in self.current_scope if s)
        scope_key = f"{fqdn}.{node.name}" if fqdn else node.name
        
        ret_type = self.ledger.get_type(fqdn, node.name)
        if not ret_type and node.metadata and 'type' in node.metadata:
            ret_type = node.metadata['type']
            
        ret_type_str = self._map_php_type(ret_type)
        if name == "__construct":
            ret_type_str = ""
            
        ret_sig = f": {ret_type_str}" if ret_type_str else ""

        args_list = []
        for arg in node.args:
            if is_method and arg.name in ("self", "this"):
                continue
                
            arg_type = self.ledger.get_type(scope_key, arg.name)
            if not arg_type and arg.metadata and 'type' in arg.metadata:
                arg_type = arg.metadata['type']
                
            type_str = self._map_php_type(arg_type)
            if type_str:
                args_list.append(f"{type_str} ${arg.name}")
            else:
                args_list.append(f"${arg.name}")
            
        args_str = f"({', '.join(args_list)})"
        
        lines = []
        prefix = "public function" if is_method else "function"
        lines.append(f"{self._indent()}{prefix} {name}{args_str}{ret_sig} {{")
        
        self.current_scope.append(node.name)
        self.indent_level += 1
        
        for stmt in node.body:
            stmt_str = self.generate(stmt)
            if isinstance(stmt, (IfNode, WhileNode, ForNode, TryCatchNode)):
                lines.append(stmt_str)
            else:
                lines.append(f"{self._indent()}{stmt_str};")
                
        self.indent_level -= 1
        self.current_scope.pop()
        
        lines.append(f"{self._indent()}}}")
        return "\n".join(lines)

    def visit_MethodDefNode(self, node: MethodDefNode) -> str:
        return self.visit_FunctionDefNode(node)

    def visit_ClassDefNode(self, node: ClassDefNode) -> str:
        lines = []
        lines.append(f"{self._indent()}class {node.name} {{")
        
        self.current_scope.append(node.name)
        self.indent_level += 1
        
        for method in node.methods:
            lines.append(self.generate(method))
            
        self.indent_level -= 1
        self.current_scope.pop()
        
        lines.append(f"{self._indent()}}}")
        return "\n".join(lines)

    def visit_AssignmentNode(self, node: AssignmentNode) -> str:
        left_str = self.generate(node.left)
        right_str = self.generate(node.right) if node.right else "null"
        return f"{left_str} = {right_str}"

    def visit_ReturnNode(self, node: ReturnNode) -> str:
        if node.value is None:
            return "return"
        val_str = self.generate(node.value)
        return f"return {val_str}"

    def visit_BinaryOpNode(self, node: BinaryOpNode) -> str:
        left_str = self.generate(node.left)
        right_str = self.generate(node.right)
        op = node.operator
        
        if op == "//": return f"intdiv({left_str}, {right_str})"
        if op == "is": return f"({left_str} === {right_str})"
        if op == "is not": return f"({left_str} !== {right_str})"
            
        if op == "and": op = "&&"
        if op == "or": op = "||"
            
        if getattr(node.left, 'name', None) == "":
            if op == "not": op = "!"
            return f"{op}({right_str})"
            
        return f"({left_str} {op} {right_str})"

    def visit_CallNode(self, node: CallNode) -> str:
        func_val = node.func_name
        
        self.in_call_target = True
        if isinstance(func_val, str):
            func_str = func_val
        else:
            func_str = self.generate(func_val)
        self.in_call_target = False
            
        if isinstance(func_str, str):
            if func_str == "print":
                func_str = "print"
            elif func_str == "len":
                func_str = "builtins_py_len"
            elif func_str == "str":
                func_str = "builtins_py_str"
            elif func_str == "range":
                func_str = "builtins_py_range"
            elif func_str == "hashmap":
                func_str = "builtins_py_hashmap"
            elif func_str.startswith("math."):
                func_str = func_str.replace("math.", "math_py_", 1)
            elif func_str.startswith("os."):
                func_str = func_str.replace("os.", "io_py_", 1)
            elif func_str.startswith("requests."):
                func_str = func_str.replace("requests.", "network_py_", 1)
                
        if func_str == "throw":
            args_str = ", ".join(self.generate(arg) for arg in node.args)
            return f"throw new \\Exception({args_str})"
            
        if func_str == "format":
            args_str = ", ".join(self.generate(arg) for arg in node.args)
            return f"builtins_py_format({args_str})"

        args_str = ", ".join(self.generate(arg) for arg in node.args)
        return f"{func_str}({args_str})"

    def visit_IdentifierNode(self, node: IdentifierNode) -> str:
        if node.name in ("self", "Exception"):
            return "Exception" if node.name == "Exception" else "$this"
            
        if self.in_call_target:
            return node.name
            
        return f"${node.name}"

    def visit_LiteralNode(self, node: LiteralNode) -> str:
        if isinstance(node.value, bool):
            return "true" if node.value else "false"
        elif isinstance(node.value, str):
            return f'"{node.value}"'
        elif node.value is None:
            return "null"
        else:
            if isinstance(node.value, float):
                s = str(node.value)
                if "." not in s: s += ".0"
                return s
            return str(node.value)

    def visit_IfNode(self, node: IfNode) -> str:
        condition_str = self.generate(node.condition)
        lines = [f"{self._indent()}if ({condition_str}) {{"]
        self.indent_level += 1
        for stmt in node.body:
            stmt_str = self.generate(stmt)
            if isinstance(stmt, (IfNode, WhileNode, ForNode, TryCatchNode)):
                lines.append(stmt_str)
            else:
                lines.append(f"{self._indent()}{stmt_str};")
        self.indent_level -= 1
        
        if node.orelse:
            if isinstance(node.orelse, IfNode):
                if isinstance(node.orelse.condition, LiteralNode) and node.orelse.condition.value is True:
                    lines.append(f"{self._indent()}}} else {{")
                    self.indent_level += 1
                    for stmt in node.orelse.body:
                        stmt_str = self.generate(stmt)
                        if isinstance(stmt, (IfNode, WhileNode, ForNode, TryCatchNode)):
                            lines.append(stmt_str)
                        else:
                            lines.append(f"{self._indent()}{stmt_str};")
                    self.indent_level -= 1
                    lines.append(f"{self._indent()}}}")
                else:
                    orelse_str = self.generate(node.orelse).lstrip()
                    if orelse_str.startswith("if"):
                        lines.append(f"{self._indent()}}} else{orelse_str}")
            else:
                lines.append(f"{self._indent()}}} else {{")
        else:
            lines.append(f"{self._indent()}}}")
        return "\n".join(lines)

    def visit_WhileNode(self, node: WhileNode) -> str:
        condition_str = self.generate(node.condition)
        lines = [f"{self._indent()}while ({condition_str}) {{"]
        self.indent_level += 1
        for stmt in node.body:
            stmt_str = self.generate(stmt)
            if isinstance(stmt, (IfNode, WhileNode, ForNode, TryCatchNode)):
                lines.append(stmt_str)
            else:
                lines.append(f"{self._indent()}{stmt_str};")
        self.indent_level -= 1
        lines.append(f"{self._indent()}}}")
        return "\n".join(lines)

    def visit_ForNode(self, node: ForNode) -> str:
        target_str = self.generate(node.target)
        iter_str = self.generate(node.iter)
        
        lines = [f"{self._indent()}foreach ({iter_str} as {target_str}) {{"]
        self.indent_level += 1
        for stmt in node.body:
            stmt_str = self.generate(stmt)
            if isinstance(stmt, (IfNode, WhileNode, ForNode, TryCatchNode)):
                lines.append(stmt_str)
            else:
                lines.append(f"{self._indent()}{stmt_str};")
        self.indent_level -= 1
        lines.append(f"{self._indent()}}}")
        return "\n".join(lines)

    def visit_TryCatchNode(self, node: TryCatchNode) -> str:
        lines = [f"{self._indent()}try {{"]
        self.indent_level += 1
        for stmt in node.body:
            stmt_str = self.generate(stmt)
            if isinstance(stmt, (IfNode, WhileNode, ForNode, TryCatchNode)):
                lines.append(stmt_str)
            else:
                lines.append(f"{self._indent()}{stmt_str};")
        self.indent_level -= 1
        
        lines.append(f"{self._indent()}}} catch (\\Exception $e) {{")
        self.indent_level += 1
        for stmt in node.handlers:
            stmt_str = self.generate(stmt)
            if isinstance(stmt, (IfNode, WhileNode, ForNode, TryCatchNode)):
                lines.append(stmt_str)
            else:
                lines.append(f"{self._indent()}{stmt_str};")
        self.indent_level -= 1
        lines.append(f"{self._indent()}}}")
        return "\n".join(lines)

    def visit_ListNode(self, node: ListNode) -> str:
        elements_str = ", ".join(self.generate(e) for e in node.elements)
        return f"[{elements_str}]"

    def visit_DictNode(self, node: DictNode) -> str:
        if not node.keys:
            return "builtins_py_hashmap()"
        pairs = []
        for k, v in zip(node.keys, node.values):
            pairs.append(f"{self.generate(k)} => {self.generate(v)}")
        pairs_str = ", ".join(pairs)
        return f"[{pairs_str}]" # In PHP, maps are arrays

    def visit_SubscriptNode(self, node: SubscriptNode) -> str:
        value_str = self.generate(node.value)
        slice_str = self.generate(node.slice)
        return f"{value_str}[{slice_str}]"

    def visit_AttributeNode(self, node: AttributeNode) -> str:
        value_str = self.generate(node.value)
        if value_str == '""' and node.attr == "format":
            return "format"
            
        return f"{value_str}->{node.attr}"
