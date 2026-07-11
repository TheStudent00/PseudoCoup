from pseudocoup.core.ur_ast import (
    URNode, ModuleNode, FunctionDefNode, MethodDefNode, ClassDefNode, AssignmentNode,
    BinaryOpNode, CallNode, IdentifierNode, LiteralNode,
    ReturnNode, IfNode, WhileNode, ForNode, TryCatchNode, ListNode,
    DictNode, SubscriptNode, AttributeNode
)
from pseudocoup.core.ledger import Ledger

class CppEmitter:
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
            return 'std::any'
        mapping = {
            'int': 'int',
            'float': 'double',
            'bool': 'bool',
            'str': 'std::string',
            'List[str]': 'std::vector<std::string>',
            'List[int]': 'std::vector<int>',
            'List[Any]': 'std::vector<std::any>',
            'Dict[str, int]': 'std::unordered_map<std::string, int>',
            'Optional[int]': 'std::optional<int>',
            'Optional[Any]': 'std::optional<std::any>',
            'Any': 'std::any',
            'None': 'void',
            'Void': 'void',
            'Tuple[str, int]': 'std::any'
        }
        return mapping.get(py_type, py_type)

    def generate(self, node: URNode) -> str:
        if node is None:
            return "/* Unmapped */"
        method_name = f"visit_{node.__class__.__name__}"
        visitor = getattr(self, method_name, self.generic_visit)
        return visitor(node)

    def generic_visit(self, node: URNode) -> str:
        raise NotImplementedError(f"No visit_{node.__class__.__name__} method in CppEmitter")

    def visit_ModuleNode(self, node: ModuleNode) -> str:
        self.push_scope()
        
        body_lines = [
            "#include <iostream>",
            "#include <string>",
            "#include <vector>",
            "#include <unordered_map>",
            "#include <any>",
            "#include <stdexcept>",
            ""
        ]
        
        for stmt in node.body:
            if isinstance(stmt, LiteralNode) and isinstance(stmt.value, str):
                continue
            
            stmt_str = self.generate(stmt)
            if isinstance(stmt, (AssignmentNode, ReturnNode, IfNode, WhileNode, ForNode, TryCatchNode)):
                # Note: floating statements in C++ ModuleNode will just be emitted as is. 
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
        
        ret_type = node.metadata.get('type', 'std::any')
        ret_type = self.map_type(ret_type)
        if ret_type == 'std::any' and not getattr(self, 'current_class_name', None):
            ret_type = 'void'
            
        args_list = []
        body_statements = node.body[:]
        
        for arg in node.args:
            if isinstance(node, MethodDefNode) and arg.name in ("self", "this"):
                continue
            arg_type = self.ledger.get_type(scope, arg.name)
            if not arg_type: arg_type = arg.metadata.get('type', 'std::any')
            arg_type = self.map_type(arg_type)
            args_list.append(f"{arg_type} {arg.name}")
            
        args_str = ", ".join(args_list)
        
        lines = []
        if isinstance(node, MethodDefNode):
            if node.name == "__init__":
                lines.append(f"{self._indent()}{self.current_class_name}({args_str}) {{")
            else:
                lines.append(f"{self._indent()}{ret_type} {node.name}({args_str}) {{")
        else:
            if node.name == "main":
                ret_type = "int"
                if not args_str:
                    lines.append(f"{self._indent()}int main() {{")
                else:
                    lines.append(f"{self._indent()}int main({args_str}) {{")
            else:
                lines.append(f"{self._indent()}{ret_type} {node.name}({args_str}) {{")
            
        self.push_scope()
        for arg in node.args:
            if isinstance(node, MethodDefNode) and arg.name in ("self", "this"): continue
            self.declare_var(arg.name)
            
        self.indent_level += 1
        
        for i, stmt in enumerate(body_statements):
            stmt_str = self.generate(stmt)
            
            if isinstance(stmt, (AssignmentNode, ReturnNode)):
                lines.append(f"{stmt_str};")
            elif isinstance(stmt, (IfNode, WhileNode, ForNode, TryCatchNode)):
                lines.append(stmt_str)
            else:
                if not stmt_str.endswith(";") and not stmt_str.endswith("}"):
                    stmt_str += ";"
                lines.append(f"{self._indent()}{stmt_str}")
                
        if node.name == "main":
            lines.append(f"{self._indent()}return 0;")
                
        self.indent_level -= 1
        self.pop_scope()
        lines.append(f"{self._indent()}}}")
        return "\n".join(lines)

    def visit_MethodDefNode(self, node: MethodDefNode) -> str:
        return self.visit_FunctionDefNode(node)

    def visit_ClassDefNode(self, node: ClassDefNode) -> str:
        lines = []
        
        lines.append(f"{self._indent()}class {node.name} {{")
        lines.append(f"{self._indent()}public:")
        self.push_scope()
        self.indent_level += 1
        
        prev_class_name = getattr(self, 'current_class_name', None)
        self.current_class_name = node.name
        
        for field in node.fields:
            if isinstance(field, AssignmentNode) and getattr(field.left, 'name', None):
                var_type = field.left.metadata.get('type', 'var')
                var_type = self.map_type(var_type)
                lines.append(f"{self._indent()}{var_type} {field.left.name};")
                self.declare_var(field.left.name)
                
        for method in node.methods:
            lines.append(self.generate(method))
            
        self.current_class_name = prev_class_name
        self.indent_level -= 1
        self.pop_scope()
        lines.append(f"{self._indent()}}};")
        return "\n".join(lines)

    def visit_AssignmentNode(self, node: AssignmentNode) -> str:
        right_str = self.generate(node.right) if node.right else "nullptr"
        
        if isinstance(node.left, IdentifierNode) and not getattr(self, 'current_class_name', None) and not self.is_declared(node.left.name):
            var_type = node.left.metadata.get('type', 'std::any')
            var_type = self.map_type(var_type)
            left_str = f"{var_type} {node.left.name}"
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
                args_str = " << ".join(self.generate(arg) for arg in node.args)
                return f"std::cout << {args_str} << \"\\n\""
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
                
        if func_str == "throw":
            args_str = ", ".join(self.generate(arg) for arg in node.args)
            return f"throw std::runtime_error({args_str})"
            
        if func_str == "format":
            # Very basic string concat emulation for format
            args_str = ", ".join(self.generate(arg) for arg in node.args)
            return f"builtins_py::format({args_str})"

        args_str = ", ".join(self.generate(arg) for arg in node.args)
        return f"{func_str}({args_str})"

    def visit_IdentifierNode(self, node: IdentifierNode) -> str:
        if node.name == "self": return "this"
        if node.name == "Exception": return "std::exception"
        return node.name

    def visit_LiteralNode(self, node: LiteralNode) -> str:
        if isinstance(node.value, bool):
            return "true" if node.value else "false"
        elif isinstance(node.value, str):
            return f'"{node.value}"'
        elif node.value is None:
            return "nullptr"
        else:
            if isinstance(node.value, float):
                s = str(node.value)
                if "." not in s: s += ".0"
                return s
            return str(node.value)

    def visit_IfNode(self, node: IfNode) -> str:
        condition_str = self.generate(node.condition)
        lines = [f"{self._indent()}if ({condition_str}) {{"]
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
        lines = [f"{self._indent()}while ({condition_str}) {{"]
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
        
        # If it's a builtins_py::range(start, end)
        if iter_str.startswith("builtins_py::range("):
            args = iter_str[19:-1].split(", ")
            start = args[0]
            end = args[1]
            lines = [f"{self._indent()}for (int {target_str} = {start}; {target_str} < {end}; {target_str}++) {{"]
        else:
            lines = [f"{self._indent()}for (auto {target_str} : {iter_str}) {{"]
            
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
        lines = [f"{self._indent()}try {{"]
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
        
        lines.append(f"{self._indent()}}} catch (const std::exception& e) {{")
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
        lines.append(f"{self._indent()}}}")
        return "\n".join(lines)

    def visit_ListNode(self, node: ListNode) -> str:
        elements_str = ", ".join(self.generate(e) for e in node.elements)
        return f"{{{elements_str}}}"

    def visit_DictNode(self, node: DictNode) -> str:
        if not node.keys:
            return "builtins_py::hashmap()"
        pairs = []
        for k, v in zip(node.keys, node.values):
            pairs.append(f"{{{self.generate(k)}, {self.generate(v)}}}")
        pairs_str = ", ".join(pairs)
        return f"builtins_py::hashmap({{{pairs_str}}})"

    def visit_SubscriptNode(self, node: SubscriptNode) -> str:
        value_str = self.generate(node.value)
        slice_str = self.generate(node.slice)
        return f"{value_str}[{slice_str}]"

    def visit_AttributeNode(self, node: AttributeNode) -> str:
        value_str = self.generate(node.value)
        if value_str == '""' and node.attr == "format":
            return "format"
            
        if value_str == "this":
            return f"{value_str}->{node.attr}"
            
        return f"{value_str}.{node.attr}"
