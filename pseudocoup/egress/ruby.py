from pseudocoup.core.ur_ast import (
    URNode, ModuleNode, FunctionDefNode, MethodDefNode, ClassDefNode, AssignmentNode,
    BinaryOpNode, CallNode, IdentifierNode, LiteralNode,
    ReturnNode, IfNode, WhileNode, ForNode, TryCatchNode, ListNode,
    DictNode, SubscriptNode, AttributeNode
)
from pseudocoup.core.ledger import Ledger

class RubyEmitter:
    def __init__(self, ledger: Ledger):
        self.ledger = ledger
        self.indent_level = 0

    def _indent(self) -> str:
        return "  " * self.indent_level

    def generate(self, node: URNode) -> str:
        if node is None:
            return "nil"
        method_name = f"visit_{node.__class__.__name__}"
        visitor = getattr(self, method_name, self.generic_visit)
        return visitor(node)

    def generic_visit(self, node: URNode) -> str:
        raise NotImplementedError(f"No visit_{node.__class__.__name__} method in RubyEmitter")

    def visit_ModuleNode(self, node: ModuleNode) -> str:
        body_lines = [
            "require_relative 'builtins_py'",
            ""
        ]
        
        for stmt in node.body:
            if isinstance(stmt, LiteralNode) and isinstance(stmt.value, str):
                continue
            
            stmt_str = self.generate(stmt)
            if isinstance(stmt, (ClassDefNode, FunctionDefNode, MethodDefNode, IfNode, WhileNode, ForNode, TryCatchNode)):
                body_lines.append(stmt_str)
            else:
                body_lines.append(f"{self._indent()}{stmt_str}")
                
        return "\n".join(body_lines)

    def visit_FunctionDefNode(self, node: FunctionDefNode) -> str:
        args_list = []
        for arg in node.args:
            if isinstance(node, MethodDefNode) and arg.name in ("self", "this"):
                continue
            args_list.append(arg.name)
            
        args_str = f"({', '.join(args_list)})" if args_list else ""
        
        lines = []
        name = node.name
        if isinstance(node, MethodDefNode) and name == "__init__":
            name = "initialize"
            
        lines.append(f"{self._indent()}def {name}{args_str}")
        self.indent_level += 1
        
        for stmt in node.body:
            stmt_str = self.generate(stmt)
            if isinstance(stmt, (IfNode, WhileNode, ForNode, TryCatchNode)):
                lines.append(stmt_str)
            else:
                lines.append(f"{self._indent()}{stmt_str}")
                
        self.indent_level -= 1
        lines.append(f"{self._indent()}end")
        return "\n".join(lines)

    def visit_MethodDefNode(self, node: MethodDefNode) -> str:
        return self.visit_FunctionDefNode(node)

    def visit_ClassDefNode(self, node: ClassDefNode) -> str:
        lines = []
        lines.append(f"{self._indent()}class {node.name}")
        self.indent_level += 1
        
        # We ignore fields because Ruby defines instance variables in methods
        for method in node.methods:
            lines.append(self.generate(method))
            
        self.indent_level -= 1
        lines.append(f"{self._indent()}end")
        return "\n".join(lines)

    def visit_AssignmentNode(self, node: AssignmentNode) -> str:
        right_str = self.generate(node.right) if node.right else "nil"
        left_str = self.generate(node.left)
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
                func_str = "puts"
            elif func_str == "len":
                func_str = "builtins_py.len"
            elif func_str == "str":
                func_str = "builtins_py.str"
            elif func_str == "range":
                func_str = "builtins_py.range"
            elif func_str.startswith("math."):
                func_str = func_str.replace("math.", "math_py.", 1)
            elif func_str.startswith("os."):
                func_str = func_str.replace("os.", "io_py.", 1)
            elif func_str.startswith("requests."):
                func_str = func_str.replace("requests.", "network_py.", 1)
                
        if func_str == "throw":
            args_str = ", ".join(self.generate(arg) for arg in node.args)
            return f"raise StandardError.new({args_str})"
            
        if func_str == "format":
            args_str = ", ".join(self.generate(arg) for arg in node.args)
            return f"builtins_py.format({args_str})"

        args_str = ", ".join(self.generate(arg) for arg in node.args)
        if not args_str:
            return f"{func_str}()"
        return f"{func_str}({args_str})"

    def visit_IdentifierNode(self, node: IdentifierNode) -> str:
        if node.name == "self": return "self"
        if node.name == "Exception": return "StandardError"
        return node.name

    def visit_LiteralNode(self, node: LiteralNode) -> str:
        if isinstance(node.value, bool):
            return "true" if node.value else "false"
        elif isinstance(node.value, str):
            return f'"{node.value}"'
        elif node.value is None:
            return "nil"
        else:
            if isinstance(node.value, float):
                s = str(node.value)
                if "." not in s: s += ".0"
                return s
            return str(node.value)

    def visit_IfNode(self, node: IfNode) -> str:
        condition_str = self.generate(node.condition)
        lines = [f"{self._indent()}if {condition_str}"]
        self.indent_level += 1
        for stmt in node.body:
            stmt_str = self.generate(stmt)
            if isinstance(stmt, (IfNode, WhileNode, ForNode, TryCatchNode)):
                lines.append(stmt_str)
            else:
                lines.append(f"{self._indent()}{stmt_str}")
        self.indent_level -= 1
        
        if node.orelse:
            if isinstance(node.orelse, IfNode):
                if isinstance(node.orelse.condition, LiteralNode) and node.orelse.condition.value is True:
                    lines.append(f"{self._indent()}else")
                    self.indent_level += 1
                    for stmt in node.orelse.body:
                        stmt_str = self.generate(stmt)
                        if isinstance(stmt, (IfNode, WhileNode, ForNode, TryCatchNode)):
                            lines.append(stmt_str)
                        else:
                            lines.append(f"{self._indent()}{stmt_str}")
                    self.indent_level -= 1
                    lines.append(f"{self._indent()}end")
                else:
                    orelse_str = self.generate(node.orelse).lstrip()
                    lines.append(f"{self._indent()}els{orelse_str}")
            else:
                lines.append(f"{self._indent()}else")
        else:
            lines.append(f"{self._indent()}end")
        return "\n".join(lines)

    def visit_WhileNode(self, node: WhileNode) -> str:
        condition_str = self.generate(node.condition)
        lines = [f"{self._indent()}while {condition_str}"]
        self.indent_level += 1
        for stmt in node.body:
            stmt_str = self.generate(stmt)
            if isinstance(stmt, (IfNode, WhileNode, ForNode, TryCatchNode)):
                lines.append(stmt_str)
            else:
                lines.append(f"{self._indent()}{stmt_str}")
        self.indent_level -= 1
        lines.append(f"{self._indent()}end")
        return "\n".join(lines)

    def visit_ForNode(self, node: ForNode) -> str:
        target_str = self.generate(node.target)
        iter_str = self.generate(node.iter)
        
        lines = [f"{self._indent()}for {target_str} in {iter_str}"]
        self.indent_level += 1
        for stmt in node.body:
            stmt_str = self.generate(stmt)
            if isinstance(stmt, (IfNode, WhileNode, ForNode, TryCatchNode)):
                lines.append(stmt_str)
            else:
                lines.append(f"{self._indent()}{stmt_str}")
        self.indent_level -= 1
        lines.append(f"{self._indent()}end")
        return "\n".join(lines)

    def visit_TryCatchNode(self, node: TryCatchNode) -> str:
        lines = [f"{self._indent()}begin"]
        self.indent_level += 1
        for stmt in node.body:
            stmt_str = self.generate(stmt)
            if isinstance(stmt, (IfNode, WhileNode, ForNode, TryCatchNode)):
                lines.append(stmt_str)
            else:
                lines.append(f"{self._indent()}{stmt_str}")
        self.indent_level -= 1
        
        lines.append(f"{self._indent()}rescue StandardError => e")
        self.indent_level += 1
        for stmt in node.handlers:
            stmt_str = self.generate(stmt)
            if isinstance(stmt, (IfNode, WhileNode, ForNode, TryCatchNode)):
                lines.append(stmt_str)
            else:
                lines.append(f"{self._indent()}{stmt_str}")
        self.indent_level -= 1
        lines.append(f"{self._indent()}end")
        return "\n".join(lines)

    def visit_ListNode(self, node: ListNode) -> str:
        elements_str = ", ".join(self.generate(e) for e in node.elements)
        return f"[{elements_str}]"

    def visit_DictNode(self, node: DictNode) -> str:
        if not node.keys:
            return "builtins_py.hashmap()"
        pairs = []
        for k, v in zip(node.keys, node.values):
            pairs.append(f"{self.generate(k)} => {self.generate(v)}")
        pairs_str = ", ".join(pairs)
        return f"{{{pairs_str}}}"

    def visit_SubscriptNode(self, node: SubscriptNode) -> str:
        value_str = self.generate(node.value)
        slice_str = self.generate(node.slice)
        return f"{value_str}[{slice_str}]"

    def visit_AttributeNode(self, node: AttributeNode) -> str:
        value_str = self.generate(node.value)
        if value_str == '""' and node.attr == "format":
            return "format"
            
        if value_str == "self":
            return f"@{node.attr}"
            
        return f"{value_str}.{node.attr}"
