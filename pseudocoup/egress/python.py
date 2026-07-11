from pseudocoup.core.ur_ast import (
    URNode, ModuleNode, FunctionDefNode, MethodDefNode, ClassDefNode, AssignmentNode,
    BinaryOpNode, CallNode, IdentifierNode, LiteralNode,
    ReturnNode, IfNode, WhileNode, ForNode, TryCatchNode, ListNode,
    DictNode, SubscriptNode, AttributeNode
)

class PythonEmitter:
    def __init__(self, ledger):
        self.ledger = ledger
        self.indent_level = 0
        self.scopes = [{}]  # List of sets for tracking variable declarations
        self.class_contexts = []
        self.in_method = False
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
            return 'Any'
        # The ledger stores the Python type exactly, so we mostly return it directly.
        # But we ensure it maps cleanly.
        mapping = {
            'None': 'None',
        }
        return mapping.get(py_type, py_type)

    def generate(self, node: URNode) -> str:
        if node is None:
            return "pass"
        method_name = f"visit_{node.__class__.__name__}"
        visitor = getattr(self, method_name, self.generic_visit)
        return visitor(node)

    def generic_visit(self, node: URNode) -> str:
        raise NotImplementedError(f"No visit_{node.__class__.__name__} method")

    def visit_ModuleNode(self, node: ModuleNode) -> str:
        self.push_scope()
        lines = []
        
        # We need standard typing imports
        lines.append("from typing import List, Dict, Optional, Tuple, Any\n")
        
        for wrapper in sorted(list(self.injected_wrappers)):
            lines.append(f"import {wrapper}")
        if self.injected_wrappers:
            lines.append("")
        
        for stmt in node.body:
            stmt_str = self.generate(stmt)
            if isinstance(stmt, (AssignmentNode, ReturnNode, FunctionDefNode, MethodDefNode, ClassDefNode, IfNode, WhileNode, ForNode, TryCatchNode, CallNode)):
                # If these are top-level statements, they are already indented by their own visit logic
                if isinstance(stmt, (AssignmentNode, ReturnNode, CallNode)):
                    lines.append(f"{self._indent()}{stmt_str}")
                else:
                    lines.append(stmt_str)
            else:
                lines.append(f"{self._indent()}{stmt_str}")
        self.pop_scope()
        return "\n".join(lines)

    def visit_FunctionDefNode(self, node: FunctionDefNode) -> str:
        # compute scope
        if getattr(self, 'current_class_name', None):
            scope = f"{self.current_class_name}.{node.name}"
        else:
            scope = node.name
            
        ret_type = node.metadata.get('type', 'Any')
        ret_type = self.map_type(ret_type)
        
        args_list = []
        is_method = getattr(self, 'current_class_name', None) is not None
        has_self = False
        
        for arg in node.args:
            name = arg.name
            if name in ("this", "self"):
                name = "self"
                has_self = True
                
            if name in ("self", "cls"):
                args_list.append(name)
            else:
                arg_type = self.ledger.get_type(scope, name)
                if not arg_type:
                    arg_type = arg.metadata.get('type', 'Any')
                arg_type = self.map_type(arg_type)
                args_list.append(f"{name}: {arg_type}")
                
        if is_method and not has_self:
            args_list.insert(0, "self")
        
        args_str = ", ".join(args_list)
        
        lines = []
        lines.append(f"{self._indent()}def {node.name}({args_str}) -> {ret_type}:")
        
        self.push_scope()
        for arg in node.args:
            self.declare_var(arg.name)
            
        self.indent_level += 1
        if not node.body:
            lines.append(f"{self._indent()}pass")
        else:
            for stmt in node.body:
                stmt_str = self.generate(stmt)
                if isinstance(stmt, (AssignmentNode, ReturnNode, CallNode)):
                    lines.append(f"{self._indent()}{stmt_str}")
                elif isinstance(stmt, (FunctionDefNode, MethodDefNode, ClassDefNode, IfNode, WhileNode, ForNode, TryCatchNode)):
                    lines.append(stmt_str)
                else:
                    lines.append(f"{self._indent()}{stmt_str}")
            
        self.indent_level -= 1
        self.pop_scope()
        
        # Add a blank line after functions if they are at the top level
        if self.indent_level == 0:
            lines.append("")
        elif self.indent_level == 1 and getattr(self, 'current_class_name', None):
            lines.append("")
            
        return "\n".join(lines)

    def visit_MethodDefNode(self, node: MethodDefNode) -> str:
        prev_in_method = getattr(self, 'in_method', False)
        self.in_method = True
        res = self.visit_FunctionDefNode(node)
        self.in_method = prev_in_method
        return res

    def visit_ClassDefNode(self, node: ClassDefNode) -> str:
        lines = []
        bases_str = f"({', '.join(node.bases)})" if getattr(node, 'bases', None) else ""
        lines.append(f"{self._indent()}class {node.name}{bases_str}:")
        
        self.push_scope()
        self.indent_level += 1
        
        prev_class_name = getattr(self, 'current_class_name', None)
        self.current_class_name = node.name
        
        class_fields = set()
        for field in node.fields:
            if isinstance(field, AssignmentNode) and isinstance(field.left, IdentifierNode):
                class_fields.add(field.left.name)
        for method in node.methods:
            class_fields.add(method.name)
        self.class_contexts.append(class_fields)
        
        has_body = False
        
        # Fields
        for field in node.fields:
            if isinstance(field, AssignmentNode):
                # Fields don't have right sides usually in the AST here, they are just left assignments with types
                var_type = field.left.metadata.get('type', 'Any')
                var_type = self.map_type(var_type)
                lines.append(f"{self._indent()}{field.left.name}: {var_type}")
                has_body = True
            else:
                lines.append(f"{self._indent()}{self.generate(field)}")
                has_body = True
                
        # Methods
        for method in node.methods:
            lines.append(self.generate(method))
            has_body = True
            
        if not has_body:
            lines.append(f"{self._indent()}pass")
            
        self.current_class_name = prev_class_name
        self.class_contexts.pop()
        self.indent_level -= 1
        self.pop_scope()
        
        if self.indent_level == 0:
            lines.append("")
            
        return "\n".join(lines)

    def visit_AssignmentNode(self, node: AssignmentNode) -> str:
        if node.right is None:
            if isinstance(node.left, IdentifierNode) and not self.is_declared(node.left.name):
                var_type = node.left.metadata.get('type', 'Any')
                var_type = self.map_type(var_type)
                self.declare_var(node.left.name)
                return f"{node.left.name}: {var_type}"
            else:
                left_str = self.generate(node.left)
                return f"{left_str}"

        right_str = self.generate(node.right)
        
        if isinstance(node.left, IdentifierNode) and not self.is_declared(node.left.name):
            var_type = node.left.metadata.get('type', 'Any')
            var_type = self.map_type(var_type)
            left_str = f"{node.left.name}: {var_type}"
            self.declare_var(node.left.name)
        else:
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
        if op == "&&":
            op = "and"
        elif op == "||":
            op = "or"
            
        if op == "!":
            return f"not {right_str}"
            
        return f"{left_str} {op} {right_str}"

    def visit_CallNode(self, node: CallNode) -> str:
        if node.func_name == "throw":
            arg_str = self.generate(node.args[0]) if node.args else ""
            return f"raise {arg_str}"
            
        func = node.func_name
        if isinstance(func, IdentifierNode):
            func_str = func.name
        elif isinstance(func, str):
            func_str = func
        else:
            func_str = self.generate(func)

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
            
        args_str = ", ".join(self.generate(arg) for arg in node.args)
        return f"{func_str}({args_str})"

    def visit_IdentifierNode(self, node: IdentifierNode) -> str:
        name = node.name
        if name == "null":
            return "None"
        if name == "this":
            return "self"
            
        if getattr(self, 'in_method', False) and getattr(self, 'class_contexts', None):
            if name in self.class_contexts[-1] and not self.is_declared(name):
                return f"self.{name}"
                
        return name

    def visit_LiteralNode(self, node: LiteralNode) -> str:
        if isinstance(node.value, bool):
            return "True" if node.value else "False"
        elif isinstance(node.value, str):
            if "\n" in node.value:
                return f'"""{node.value}"""'
            return repr(node.value)
        else:
            return str(node.value)

    def visit_IfNode(self, node: IfNode) -> str:
        condition_str = self.generate(node.condition)
        lines = [f"{self._indent()}if {condition_str}:"]
        
        self.push_scope()
        self.indent_level += 1
        if not node.body:
            lines.append(f"{self._indent()}pass")
        else:
            for stmt in node.body:
                stmt_str = self.generate(stmt)
                if isinstance(stmt, (AssignmentNode, ReturnNode, CallNode)):
                    lines.append(f"{self._indent()}{stmt_str}")
                elif isinstance(stmt, (FunctionDefNode, MethodDefNode, ClassDefNode, IfNode, WhileNode, ForNode, TryCatchNode)):
                    lines.append(stmt_str)
                else:
                    lines.append(f"{self._indent()}{stmt_str}")
        self.indent_level -= 1
        self.pop_scope()
        
        if node.orelse:
            if isinstance(node.orelse, IfNode):
                # elif case
                # Actually in UR-AST orelse might just be an IfNode
                # To emit elif nicely:
                orelse_str = self.generate(node.orelse).lstrip()
                # IfNode starts with "if ", replace with "elif "
                if orelse_str.startswith("if "):
                    lines.append(f"{self._indent()}el{orelse_str}")
                else:
                    lines.append(f"{self._indent()}else:")
                    self.push_scope()
                    self.indent_level += 1
                    # indent the orelse_str since it's an if node? wait, if it doesn't start with "if " it shouldn't be an IfNode
                    lines.append(f"{self._indent()}{orelse_str}")
                    self.indent_level -= 1
                    self.pop_scope()
            else:
                lines.append(f"{self._indent()}else:")
                self.push_scope()
                self.indent_level += 1
                stmt_str = self.generate(node.orelse)
                if isinstance(node.orelse, (AssignmentNode, ReturnNode, CallNode)):
                    lines.append(f"{self._indent()}{stmt_str}")
                else:
                    lines.append(f"{self._indent()}{stmt_str}") # wait, normally orelse in Python AST is a list of stmts, but in UR-AST it's a single Node or List? In UR-AST, orelse is Optional['URNode']. Usually it's either an IfNode or a list of statements (but wait, UR-AST says Optional['URNode']). Oh, the python ingestor wraps else body in some node? Actually wait, we should check `pseudocoup/ingress/python.py`. Let's assume it's just a block/list? If it's a list, `generate` will fail if it expects a single node. Let's see python.py ingestor... wait, `URNode` `orelse` is `Optional['URNode']`. If it's a list, the ingestor might have packed it into something, or maybe it's just a List. Let me double check `pseudocoup/core/ur_ast.py`. It says `orelse: Optional['URNode'] = None`. So it's a single node, probably an IfNode or something. Wait, in DartEmitter, `orelse_str = self.generate(node.orelse).lstrip()`. Okay.
                self.indent_level -= 1
                self.pop_scope()
            
        return "\n".join(lines)

    def visit_WhileNode(self, node: WhileNode) -> str:
        condition_str = self.generate(node.condition)
        lines = [f"{self._indent()}while {condition_str}:"]
        
        self.push_scope()
        self.indent_level += 1
        if not node.body:
            lines.append(f"{self._indent()}pass")
        else:
            for stmt in node.body:
                stmt_str = self.generate(stmt)
                if isinstance(stmt, (AssignmentNode, ReturnNode, CallNode)):
                    lines.append(f"{self._indent()}{stmt_str}")
                elif isinstance(stmt, (FunctionDefNode, MethodDefNode, ClassDefNode, IfNode, WhileNode, ForNode, TryCatchNode)):
                    lines.append(stmt_str)
                else:
                    lines.append(f"{self._indent()}{stmt_str}")
        self.indent_level -= 1
        self.pop_scope()
        return "\n".join(lines)

    def visit_ForNode(self, node: ForNode) -> str:
        target_str = self.generate(node.target)
        iter_str = self.generate(node.iter)
        
        self.push_scope()
        if isinstance(node.target, IdentifierNode):
            self.declare_var(node.target.name)
            
        lines = [f"{self._indent()}for {target_str} in {iter_str}:"]
        self.indent_level += 1
        if not node.body:
            lines.append(f"{self._indent()}pass")
        else:
            for stmt in node.body:
                stmt_str = self.generate(stmt)
                if isinstance(stmt, (AssignmentNode, ReturnNode, CallNode)):
                    lines.append(f"{self._indent()}{stmt_str}")
                elif isinstance(stmt, (FunctionDefNode, MethodDefNode, ClassDefNode, IfNode, WhileNode, ForNode, TryCatchNode)):
                    lines.append(stmt_str)
                else:
                    lines.append(f"{self._indent()}{stmt_str}")
        self.indent_level -= 1
        self.pop_scope()
        return "\n".join(lines)

    def visit_TryCatchNode(self, node: TryCatchNode) -> str:
        lines = [f"{self._indent()}try:"]
        self.push_scope()
        self.indent_level += 1
        if not node.body:
            lines.append(f"{self._indent()}pass")
        else:
            for stmt in node.body:
                stmt_str = self.generate(stmt)
                if isinstance(stmt, (AssignmentNode, ReturnNode, CallNode)):
                    lines.append(f"{self._indent()}{stmt_str}")
                elif isinstance(stmt, (FunctionDefNode, MethodDefNode, ClassDefNode, IfNode, WhileNode, ForNode, TryCatchNode)):
                    lines.append(stmt_str)
                else:
                    lines.append(f"{self._indent()}{stmt_str}")
        self.indent_level -= 1
        self.pop_scope()
        
        lines.append(f"{self._indent()}except Exception:")
        self.push_scope()
        self.indent_level += 1
        
        if not node.handlers:
            lines.append(f"{self._indent()}pass")
        else:
            for stmt in node.handlers:
                stmt_str = self.generate(stmt)
                if isinstance(stmt, (AssignmentNode, ReturnNode, CallNode)):
                    lines.append(f"{self._indent()}{stmt_str}")
                elif isinstance(stmt, (FunctionDefNode, MethodDefNode, ClassDefNode, IfNode, WhileNode, ForNode, TryCatchNode)):
                    lines.append(stmt_str)
                else:
                    lines.append(f"{self._indent()}{stmt_str}")
                    
        self.indent_level -= 1
        self.pop_scope()
            
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


