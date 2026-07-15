from pseudocoup.core.ur_ast import (
    URNode, ModuleNode, FunctionDefNode, MethodDefNode, ClassDefNode, AssignmentNode,
    BinaryOpNode, CallNode, IdentifierNode, LiteralNode,
    ReturnNode, IfNode, WhileNode, ForNode, TryCatchNode, ListNode,
    DictNode, SubscriptNode, AttributeNode
)
from pseudocoup.egress.hoisting import HoistingMixin

class GoEmitter(HoistingMixin):
    # visit_* methods for these node types return already-indented text; every
    # other statement gets the block loop's indent prefix (including the
    # historical double-indent on compound-statement first lines, preserved
    # byte-for-byte from the pre-mixin loops).
    SELF_INDENTING_NODES = (AssignmentNode, ReturnNode, FunctionDefNode, MethodDefNode, ClassDefNode)

    def __init__(self, ledger):
        self.ledger = ledger
        self.indent_level = 0
        self.scopes = [{}]  # List of sets for tracking variable declarations
        self.injected_wrappers = set()

    def _indent(self) -> str:
        return "\t" * self.indent_level

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
            return 'interface{}'
        mapping = {
            'int': 'int',
            'float': 'float64',
            'str': 'builtins_py.String',
            'bool': 'bool',
            'List[str]': 'builtins_py.List_str',
            'List[int]': 'builtins_py.List_int',
            'List[Any]': '[]interface{}',
            'Dict[str, int]': 'builtins_py.Map_str_int',
            'Optional[int]': '*int',
            'Optional[Any]': 'interface{}',
            'None': 'void',
            'Tuple[str, int]': '[]interface{}'
        }
        if py_type in mapping:
            return mapping[py_type]
        if py_type and py_type[0].isupper() and not py_type.startswith(("List", "Dict", "Tuple", "Optional", "Any")):
            return f"*{py_type}"
        return py_type

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
        
        import_lines = [
            "\t\"fmt\""
        ]
        self.injected_wrappers.add("roundtrip/builtins_py")
        for wrapper in sorted(list(self.injected_wrappers)):
            import_lines.append(f"\t\"{wrapper}\"")
            
        imports_str = "import (\n" + "\n".join(import_lines) + "\n)"
        
        lines = [
            "package main",
            "",
            imports_str,
            "",
            "func Contains[T comparable](slice []T, item T) bool {",
            "\tfor _, s := range slice {",
            "\t\tif s == item {",
            "\t\t\treturn true",
            "\t\t}",
            "\t}",
            "\treturn false",
            "}",
            "",
            "func Range(start, end int) []int {",
            "\tvar r []int",
            "\tfor i := start; i < end; i++ {",
            "\t\tr = append(r, i)",
            "\t}",
            "\treturn r",
            "}",
            "",
            "func Ptr[T any](v T) *T {",
            "\treturn &v",
            "}",
            ""
        ]
        
        for stmt in node.body:
            if isinstance(stmt, (FunctionDefNode, MethodDefNode, ClassDefNode, AssignmentNode)):
                lines.append(self.emit_stmt(stmt))
        self.pop_scope()
        return "\n".join(lines)

    def visit_FunctionDefNode(self, node: FunctionDefNode) -> str:
        ret_type = node.metadata.get('type', 'interface{}')
        ret_type = self.map_type(ret_type)
        if ret_type == 'void':
            ret_type = ''
            
        args_list = []
        is_method = getattr(self, 'current_class_name', None) is not None
        
        for arg in node.args:
            if node.name == "__init__" and arg.name in ("self", "this"):
                continue
            if is_method and arg.name in ("self", "this"):
                continue
            arg_type = arg.metadata.get('type', 'interface{}')
            arg_type = self.map_type(arg_type)
            args_list.append(f"{arg.name} {arg_type}")
        
        args_str = ", ".join(args_list)
        
        lines = []
        
        if is_method:
            if node.name == "__init__":
                lines.append(f"{self._indent()}func New{self.current_class_name}({args_str}) *{self.current_class_name} {{")
                self.push_scope()
                lines.append(f"{self._indent()}\tthis := &{self.current_class_name}{{}}")
                self.declare_var("this")
            else:
                ret_str = f" {ret_type}" if ret_type else ""
                method_name = node.name
                if method_name and method_name[0].islower():
                    method_name = method_name.capitalize()
                lines.append(f"{self._indent()}func (this *{self.current_class_name}) {method_name}({args_str}){ret_str} {{")
                self.push_scope()
                self.declare_var("this")
        else:
            ret_str = f" {ret_type}" if ret_type else ""
            lines.append(f"{self._indent()}func {node.name}({args_str}){ret_str} {{")
            self.push_scope()
            
        for arg in node.args:
            if arg.name not in ("self", "this"):
                self.declare_var(arg.name)
                
        self.indent_level += 1
        for stmt in node.body:
            lines.append(self.emit_stmt(stmt))

        if is_method and node.name == "__init__":
            lines.append(f"{self._indent()}return this")
        elif ret_type:
            if ret_type == "int": lines.append(f"{self._indent()}return 0")
            elif ret_type == "float64": lines.append(f"{self._indent()}return 0.0")
            elif ret_type == "string": lines.append(f"{self._indent()}return \"\"")
            elif ret_type == "bool": lines.append(f"{self._indent()}return false")
            elif ret_type == "interface{}": lines.append(f"{self._indent()}return nil")
            elif ret_type.startswith("*"): lines.append(f"{self._indent()}return nil")
            elif ret_type.startswith("[]") or ret_type.startswith("map"): lines.append(f"{self._indent()}return nil")
            
        self.indent_level -= 1
        self.pop_scope()
        
        lines.append(f"{self._indent()}}}")
        return "\n".join(lines)

    def visit_MethodDefNode(self, node: MethodDefNode) -> str:
        return self.visit_FunctionDefNode(node)

    def visit_ClassDefNode(self, node: ClassDefNode) -> str:
        lines = []
        lines.append(f"{self._indent()}type {node.name} struct {{")
        
        self.push_scope()
        self.indent_level += 1
        
        prev_class_name = getattr(self, 'current_class_name', None)
        self.current_class_name = node.name
        
        # Ensure all fields are emitted first
        for field in node.fields:
            if isinstance(field.left, IdentifierNode):
                field_type = self.map_type(field.left.metadata.get('type', 'interface{}'))
                lines.append(f"{self._indent()}{field.left.name} {field_type}")
                
        self.indent_level -= 1
        lines.append(f"{self._indent()}}}")
        
        # Then emit methods
        for method in node.methods:
            lines.append(self.generate(method))
            
        self.current_class_name = prev_class_name
        self.pop_scope()
        
        return "\n\n".join(lines)

    def visit_AssignmentNode(self, node: AssignmentNode) -> str:
        if node.right is None:
            if isinstance(node.left, IdentifierNode) and not self.is_declared(node.left.name):
                var_type = node.left.metadata.get('type', 'interface{}')
                var_type = self.map_type(var_type)
                self.declare_var(node.left.name)
                return f"{self._indent()}var {node.left.name} {var_type}"
            else:
                left_str = self.generate(node.left)
                return f"{self._indent()}{left_str}"

        right_str = self.generate(node.right)
        
        if isinstance(node.left, IdentifierNode):
            left_type = self.map_type(node.left.metadata.get('type', 'interface{}'))
            if left_type == "builtins_py.Map_str_int" and right_str == "map[interface{}]interface{}{}":
                right_str = f"{left_type}{{}}"
            elif left_type == "builtins_py.List_int" and right_str == "[]interface{}{}":
                right_str = f"{left_type}{{}}"
            
            if left_type != "interface{}" and isinstance(node.right, SubscriptNode) and isinstance(node.right.value, IdentifierNode):
                val_type = self.map_type(node.right.value.metadata.get('type', 'interface{}'))
                if val_type == "[]interface{}" or val_type == "interface{}":
                    right_str = f"{right_str}.({left_type})"
                    
            if left_type.startswith("*") and right_str != "nil" and not right_str.startswith("&") and not right_str.startswith("New"):
                right_str = f"Ptr({right_str})"

            if not self.is_declared(node.left.name):
                self.declare_var(node.left.name)
                if left_type != "interface{}":
                    return f"{self._indent()}var {node.left.name} {left_type} = {right_str}"
                return f"{self._indent()}{node.left.name} := {right_str}"
            else:
                return f"{self._indent()}{node.left.name} = {right_str}"
                
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
        if node.operator == "in":
            right_type = node.right.metadata.get('type', '')
            if right_type.startswith('Dict'):
                # Dict membership has no legal Go expression form that binds the
                # comma-ok result inline; hoist the comma-ok statement into the
                # enclosing statement's prelude (was: a one-off IIFE).
                tmp, _ = self.hoister.hoist_stmt(
                    [f"_, @TMP@ := {right_str}[{left_str}]"], "@TMP@"
                )
                return tmp
            return f"Contains({right_str}, {left_str})"
        elif node.operator == "and":
            return f"{left_str} && {right_str}"
        elif node.operator == "or":
            return f"{left_str} || {right_str}"
        elif node.operator == "//":
            return f"({left_str} / {right_str})"
        elif node.operator == "/":
            # Cast to float64 if they are likely integers or just to be safe
            return f"(float64({left_str}) / float64({right_str}))"
        elif node.operator == "is":
            return f"{left_str} == {right_str}"
        elif node.operator == "is not":
            return f"{left_str} != {right_str}"
        elif node.operator == "!":
            return f"!({right_str})"
        return f"{left_str} {node.operator} {right_str}"

    def visit_CallNode(self, node: CallNode) -> str:
        func_val = node.func_name
        if isinstance(func_val, IdentifierNode):
            func_str = func_val.name
        elif isinstance(func_val, str):
            func_str = func_val
        elif isinstance(func_val, AttributeNode):
            obj_str = self.generate(func_val.value)
            attr_name = func_val.attr
            if attr_name and attr_name[0].islower():
                attr_name = attr_name.capitalize()
            func_str = f"{obj_str}.{attr_name}"
        else:
            func_str = self.generate(func_val)

        if isinstance(func_str, str):
            if func_str.startswith("math."):
                self.injected_wrappers.add("math_py")
                method = func_str.split(".")[1]
                func_str = f"math_py.{method.capitalize()}"
            elif func_str.startswith("os."):
                self.injected_wrappers.add("io_py")
                method = func_str.split(".")[1]
                func_str = f"io_py.{method.capitalize()}"
            elif func_str.startswith("requests."):
                self.injected_wrappers.add("network_py")
                method = func_str.split(".")[1]
                func_str = f"network_py.{method.capitalize()}"
        if func_str == "print":
            args_str = ", ".join(self.generate(arg) for arg in node.args)
            return f"fmt.Println({args_str})"
        if func_str == "len" and node.args:
            arg_str = self.generate(node.args[0])
            return f"len({arg_str})"
        if func_str == "str" and node.args:
            arg_str = self.generate(node.args[0])
            return f"builtins_py.String(fmt.Sprintf(\"%v\", {arg_str}))"
        if func_str == "throw":
            if node.args:
                arg_str = self.generate(node.args[0])
                if arg_str == "ValueError":
                    return "panic(\"ValueError\")"
                return f"panic({arg_str})"
            return "panic(\"error\")"
        if func_str == "ValueError":
            if node.args:
                arg_str = self.generate(node.args[0])
                return arg_str
            return "\"ValueError\""
        if func_str == "range":
            args_str = ", ".join(self.generate(arg) for arg in node.args)
            return f"Range({args_str})"
        if func_str and func_str[0].isupper() and "." not in func_str:
            args_str = ", ".join(self.generate(arg) for arg in node.args)
            return f"New{func_str}({args_str})"
            
        args_strs = []
        for i, arg in enumerate(node.args):
            arg_str = self.generate(arg)
            
            # Heuristic to check if this parameter expects a pointer
            # We attempt to match FQDN if the argument is a known variable
            if isinstance(func_str, str) and "." in func_str:
                obj, method = func_str.split(".", 1)
                obj_type = self.ledger.get_type(getattr(self, "current_class_name", "main"), obj)
                if obj_type:
                    func_str = f"{obj_type}.{method}"
            
            # Assuming memory_erasure might be registered as Func.param
            # We don't have the param name, but if the arg is an identifier, maybe they match?
            is_pointer = False
            if isinstance(arg, IdentifierNode):
                if self.ledger.memory_erasure.get(f"{func_str}.{arg.name}") == "pointer":
                    is_pointer = True
                    
            if is_pointer:
                arg_str = f"&{arg_str}"
                
            args_strs.append(arg_str)
            
        args_str = ", ".join(args_strs)
        return f"{func_str}({args_str})"

    def visit_IdentifierNode(self, node: IdentifierNode) -> str:
        if node.name == "self":
            return "this"
        if node.name in ("None", "null"):
            return "nil"
        return node.name

    def visit_LiteralNode(self, node: LiteralNode) -> str:
        if isinstance(node.value, bool):
            return "true" if node.value else "false"
        elif isinstance(node.value, str):
            import json
            return f"builtins_py.String({json.dumps(node.value)})"
        else:
            return str(node.value)

    def visit_IfNode(self, node: IfNode) -> str:
        condition_str = self.generate(node.condition)
        lines = self.prelude_block()  # anything hoisted out of the condition
        lines.append(f"{self._indent()}if {condition_str} {{")

        self.push_scope()
        self.indent_level += 1
        for stmt in node.body:
            lines.append(self.emit_stmt(stmt))
        self.indent_level -= 1
        self.pop_scope()
        
        if node.orelse:
            if isinstance(node.orelse, IfNode):
                if isinstance(node.orelse.condition, LiteralNode) and node.orelse.condition.value is True:
                    lines.append(f"{self._indent()}}} else {{")
                    self.push_scope()
                    self.indent_level += 1
                    for stmt in node.orelse.body:
                        lines.append(self.emit_stmt(stmt))
                    self.indent_level -= 1
                    self.pop_scope()
                    lines.append(f"{self._indent()}}}")
                else:
                    orelse_str = self.generate(node.orelse).lstrip()
                    lines.append(f"{self._indent()}}} else {orelse_str}")
            else:
                # Should not reach here typically since orelse in IfNode is usually a list if it's an else block, wait.
                # In PythonIngestor, orelse is an IfNode.
                pass
        else:
            lines.append(f"{self._indent()}}}")
            
        return "\n".join(lines)

    def visit_WhileNode(self, node: WhileNode) -> str:
        condition_str = self.generate(node.condition)
        # NOTE: a hoist out of a while condition is evaluated ONCE, before the
        # loop -- see the known-limitations note in egress/hoisting.py.
        lines = self.prelude_block()
        lines.append(f"{self._indent()}for {condition_str} {{")

        self.push_scope()
        self.indent_level += 1
        for stmt in node.body:
            lines.append(self.emit_stmt(stmt))
        self.indent_level -= 1
        self.pop_scope()
        lines.append(f"{self._indent()}}}")
        return "\n".join(lines)

    def visit_ForNode(self, node: ForNode) -> str:
        target_str = self.generate(node.target)
        iter_str = self.generate(node.iter)
        
        self.push_scope()
        op = ":="
        if isinstance(node.target, IdentifierNode):
            if self.is_declared(node.target.name):
                op = "="
            else:
                self.declare_var(node.target.name)
            
        lines = self.prelude_block()  # anything hoisted out of the iterable
        lines.append(f"{self._indent()}for _, {target_str} {op} range ({iter_str}) {{")
        self.indent_level += 1
        for stmt in node.body:
            lines.append(self.emit_stmt(stmt))
        self.indent_level -= 1
        self.pop_scope()
        lines.append(f"{self._indent()}}}")
        return "\n".join(lines)

    def visit_TryCatchNode(self, node: TryCatchNode) -> str:
        lines = [f"{self._indent()}func() {{"]
        self.push_scope()
        self.indent_level += 1
        
        lines.append(f"{self._indent()}defer func() {{")
        self.indent_level += 1
        lines.append(f"{self._indent()}if e := recover(); e != nil {{")
        self.indent_level += 1
        
        for stmt in node.handlers:
            lines.append(self.emit_stmt(stmt))

        self.indent_level -= 1
        lines.append(f"{self._indent()}}}")
        self.indent_level -= 1
        lines.append(f"{self._indent()}}}()")

        for stmt in node.body:
            lines.append(self.emit_stmt(stmt))

        self.indent_level -= 1
        self.pop_scope()
        
        lines.append(f"{self._indent()}}}()")
        return "\n".join(lines)

    def visit_ListNode(self, node: ListNode) -> str:
        elements_str = ", ".join(self.generate(e) for e in node.elements)
        list_type = node.metadata.get('type', 'interface{}')
        list_type = self.map_type(list_type)
        if list_type == 'interface{}':
            if not node.elements:
                list_type = '[]interface{}'
            else:
                list_type = '[]interface{}'
                for el in node.elements:
                    if isinstance(el, LiteralNode):
                        if isinstance(el.value, str): list_type = "builtins_py.List_str"; break
                        elif isinstance(el.value, int) and not isinstance(el.value, bool): list_type = "builtins_py.List_int"; break
                        elif isinstance(el.value, float): list_type = "[]float64"; break
                    elif isinstance(el, BinaryOpNode) and isinstance(el.right, LiteralNode):
                        if isinstance(el.right.value, int) and not isinstance(el.right.value, bool): list_type = "builtins_py.List_int"; break
                        elif isinstance(el.right.value, float): list_type = "[]float64"; break
        return f"{list_type}{{{elements_str}}}"

    def visit_DictNode(self, node: DictNode) -> str:
        pairs = []
        for k, v in zip(node.keys, node.values):
            pairs.append(f"{self.generate(k)}: {self.generate(v)}")
        pairs_str = ", ".join(pairs)
        
        dict_type = node.metadata.get('type', 'interface{}')
        dict_type = self.map_type(dict_type)
        if dict_type == 'interface{}':
            if not node.keys:
                dict_type = 'map[interface{}]interface{}'
            else:
                first_key = node.keys[0]
                first_val = node.values[0]
                k_type = "interface{}"
                v_type = "interface{}"
                if isinstance(first_key, LiteralNode) and isinstance(first_key.value, str): k_type = "builtins_py.String"
                if isinstance(first_val, LiteralNode) and isinstance(first_val.value, int) and not isinstance(first_val.value, bool): v_type = "int"
                
                if k_type == "builtins_py.String" and v_type == "int":
                    dict_type = "builtins_py.Map_str_int"
                else:
                    dict_type = f"map[{k_type}]{v_type}"
        return f"{dict_type}{{{pairs_str}}}"

    def visit_SubscriptNode(self, node: SubscriptNode) -> str:
        value_str = self.generate(node.value)
        slice_str = self.generate(node.slice)
        return f"{value_str}[{slice_str}]"

    def visit_AttributeNode(self, node: AttributeNode) -> str:
        value_str = self.generate(node.value)
        if value_str == "self":
            value_str = "this"
        return f"{value_str}.{node.attr}"


