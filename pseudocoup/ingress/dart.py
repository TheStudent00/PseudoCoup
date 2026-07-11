from tree_sitter import Parser, Language
import tree_sitter_dart as tsdart
from pseudocoup.core.ledger import Ledger
from pseudocoup.core.ur_ast import (
    URNode, ModuleNode, FunctionDefNode, ClassDefNode, MethodDefNode,
    AssignmentNode, ReturnNode, BinaryOpNode, CallNode,
    IdentifierNode, LiteralNode,
    IfNode, WhileNode, ForNode, TryCatchNode,
    ListNode, DictNode, SubscriptNode, AttributeNode
)

class DartIngestor:
    def __init__(self, ledger: Ledger):
        self.ledger = ledger
        self.parser = Parser()
        
        # Determine tree-sitter version compat
        try:
            # For tree-sitter < 0.22
            self.language = Language(tsdart.language(), "dart")
            self.parser.set_language(self.language)
        except Exception:
            # For tree-sitter >= 0.22
            self.language = Language(tsdart.language())
            try:
                self.parser.set_language(self.language)
            except AttributeError:
                self.parser.language = self.language

        # Dart to Python types mapping
        self.type_map = {
            'int': 'int',
            'double': 'float',
            'String': 'str',
            'bool': 'bool',
            'dynamic': 'Any',
            'int?': 'Optional[int]',
            'double?': 'Optional[float]',
            'String?': 'Optional[str]',
            'bool?': 'Optional[bool]',
            'List<String>': 'List[str]',
            'List<int>': 'List[int]',
            'List<dynamic>': 'List[Any]',
            'Map<String, int>': 'Dict[str, int]',
            'void': 'None'
        }

    def _map_type(self, dart_type: str) -> str:
        return self.type_map.get(dart_type, dart_type)

    def parse(self, source_bytes: bytes) -> ModuleNode:
        tree = self.parser.parse(source_bytes)
        root_node = tree.root_node
        return self._map_node(root_node, source_bytes)

    def _text(self, node, source_bytes: bytes) -> str:
        if node is None:
            return ""
        return node.text.decode('utf-8')

    def _extract_expr(self, children, idx, source_bytes):
        if idx >= len(children):
            return None, idx
            
        base_node = children[idx]
        expr = self._map_node(base_node, source_bytes)
        idx += 1
        
        while idx < len(children) and children[idx].type in ('selector', 'type_arguments', 'unconditional_assignable_selector', 'argument_part', 'index_selector'):
            sel_node = children[idx]
            if sel_node.type == 'type_arguments':
                idx += 1
                continue
                
            sel_child = sel_node.named_children[0] if sel_node.type == 'selector' and sel_node.named_children else sel_node
            
            if sel_child.type == 'unconditional_assignable_selector':
                inner = sel_child.named_children[0] if sel_child.named_children else sel_child
                if inner.type == 'index_selector' or '[' in self._text(inner, source_bytes):
                    idx_expr, _ = self._extract_expr(inner.named_children, 0, source_bytes)
                    expr = SubscriptNode(expr, idx_expr)
                else:
                    attr_name = self._text(inner, source_bytes)
                    if attr_name.startswith('.'): attr_name = attr_name[1:]
                    
                    if attr_name == 'length':
                        expr = CallNode('len', [expr])
                    else:
                        expr = AttributeNode(expr, attr_name)
                        
            elif sel_child.type == 'argument_part':
                args = []
                arguments_node = None
                for c in sel_child.children:
                    if c.type == 'arguments':
                        arguments_node = c
                        break
                        
                nodes_to_parse = arguments_node.named_children if arguments_node else sel_child.named_children
                for arg_c in nodes_to_parse:
                    arg_expr = self._map_node(arg_c, source_bytes)
                    if arg_expr:
                        args.append(arg_expr)
                            
                # Reverse polyfills logic
                if isinstance(expr, AttributeNode):
                    if expr.attr == 'toString' and not args:
                        expr = CallNode('str', [expr.value])
                    elif expr.attr == 'contains' and len(args) == 1:
                        expr = BinaryOpNode(args[0], expr.value, 'in')
                    elif expr.attr == 'append' and len(args) == 1:
                        expr = CallNode(expr, args)
                    elif expr.attr == 'get' and len(args) == 1:
                        expr = CallNode(expr, args)
                    else:
                        expr = CallNode(expr, args)
                else:
                    expr = CallNode(expr, args)
                    
            elif sel_child.type == 'index_selector' or '[' in self._text(sel_child, source_bytes):
                idx_expr, _ = self._extract_expr(sel_child.named_children, 0, source_bytes)
                expr = SubscriptNode(expr, idx_expr)
            idx += 1
            
        # Fix CallNode func_name string if it's an Identifier
        if isinstance(expr, CallNode) and isinstance(expr.func_name, IdentifierNode):
            expr.func_name = expr.func_name.name
            
        return expr, idx



    def _parse_function(self, sig_node, body_node, source_bytes) -> FunctionDefNode:
        if sig_node.type == 'function_signature':
            return_type_node = sig_node.child_by_field_name('return_type') or sig_node.named_children[0]
            # wait, return_type could be missing, let's just find identifier
            name_node = None
            for c in sig_node.named_children:
                if c.type == 'identifier':
                    name_node = c
                    break
            params_node = sig_node.child_by_field_name('parameters')
            if not params_node:
                for c in sig_node.named_children:
                    if c.type == 'formal_parameter_list':
                        params_node = c
                        break
            
            name = self._text(name_node, source_bytes)
            if name == 'if':
                py_ret_type = None
            else:
                # Find return type (any type_identifier or void_type before identifier)
                dart_ret_type = None
                for c in sig_node.named_children:
                    if c == name_node: break
                    if c.type in ('type_identifier', 'void_type'):
                        dart_ret_type = self._text(c, source_bytes)
                        
                py_ret_type = self._map_type(dart_ret_type) if dart_ret_type else None
            
        elif sig_node.type == 'constructor_signature':
            name_node = None
            for c in sig_node.named_children:
                if c.type == 'identifier':
                    name_node = c
                    break
            params_node = None
            for c in sig_node.named_children:
                if c.type == 'formal_parameter_list':
                    params_node = c
                    break
            
            name = '__init__'
            py_ret_type = None
        else:
            return None

        args = []
        implicit_assignments = []
        if params_node:
            for child in params_node.named_children:
                if child.type == 'formal_parameter':
                    # Check for 'this.x' constructor params
                    constructor_param_node = None
                    for c in child.named_children:
                        if c.type == 'constructor_param':
                            constructor_param_node = c
                            break
                            
                    if constructor_param_node:
                        ident_node_c = None
                        for c in constructor_param_node.named_children:
                            if c.type == 'identifier':
                                ident_node_c = c
                                break
                        if ident_node_c:
                            name_str = self._text(ident_node_c, source_bytes)
                            args.append(IdentifierNode(name_str))
                            
                            # Synthesize: self.x = x
                            assign_node = AssignmentNode(
                                AttributeNode(IdentifierNode("self"), name_str),
                                IdentifierNode(name_str)
                            )
                            implicit_assignments.append(assign_node)
                        continue
                    # It could be type_identifier then identifier
                    type_node = None
                    name_n = None
                    for c in child.named_children:
                        if c.type in ('type_identifier', 'inferred_type'):
                            type_node = c
                        elif c.type == 'identifier':
                            name_n = c
                            
                    mapped_t_str = None
                    if type_node and name_n:
                        ident_name = self._text(name_n, source_bytes)
                        t_str = self._text(type_node, source_bytes)
                        if t_str != 'var':
                            mapped_t_str = self._map_type(t_str)
                            self.ledger.types[ident_name] = mapped_t_str
                    
                    if name_n:
                        name_str = self._text(name_n, source_bytes)
                        if name_str == 'this':
                            # handled below
                            pass
                        else:
                            ident_node = IdentifierNode(name_str)
                            if mapped_t_str:
                                ident_node.metadata['type'] = mapped_t_str
                            args.append(ident_node)
                elif child.type == 'identifier':
                    # For `this` inside error nodes maybe?
                    name_str = self._text(child, source_bytes)
                    if name_str != 'this':
                        args.append(IdentifierNode(name_str))
                elif child.type == 'ERROR':
                    # dart tree-sitter sometimes flags `var this` as ERROR
                    for c in child.children:
                        if c.type == 'identifier':
                            name_str = self._text(c, source_bytes)
                            if name_str != 'this':
                                args.append(IdentifierNode(name_str))

        body = []
        # Prepend implicit assignments from constructor params
        body.extend(implicit_assignments)
        
        if body_node and body_node.type == 'function_body':
            block_node = body_node.named_children[0] if body_node.named_children else None
            if block_node and block_node.type == 'block':
                for child in block_node.named_children:
                    mapped = self._map_node(child, source_bytes)
                    if mapped:
                        body.append(mapped)

        if name == 'if':
            cond = BinaryOpNode(IdentifierNode("__name__"), LiteralNode("__main__"), "==")
            return IfNode(cond, body, None)

        func_node = FunctionDefNode(name, args, body, py_ret_type)
        if py_ret_type:
            func_node.metadata['type'] = py_ret_type
        return func_node

    def _map_node(self, node, source_bytes: bytes) -> URNode:
        if node is None:
            return None

        if node.type == 'program':
            body = []
            idx = 0
            children = node.named_children
            while idx < len(children):
                child = children[idx]
                if child.type == 'function_signature':
                    sig_node = child
                    body_node = children[idx+1] if idx+1 < len(children) and children[idx+1].type == 'function_body' else None
                    func_node = self._parse_function(sig_node, body_node, source_bytes)
                    if func_node: body.append(func_node)
                    if body_node: idx += 1
                else:
                    mapped = self._map_node(child, source_bytes)
                    if mapped:
                        body.append(mapped)
                idx += 1
            return ModuleNode(body)

        elif node.type == 'class_definition':
            name_node = None
            for c in node.named_children:
                if c.type == 'identifier':
                    name_node = c
                    break
            name = self._text(name_node, source_bytes)

            bases = []
            superclass_node = node.child_by_field_name('superclass')
            if superclass_node:
                for c in superclass_node.named_children:
                    if c.type == 'type_identifier':
                        bases.append(self._text(c, source_bytes))

            methods = []
            fields = []
            body_node = None
            for c in node.named_children:
                if c.type == 'class_body':
                    body_node = c
                    break
                    
            if body_node:
                idx = 0
                children = body_node.named_children
                while idx < len(children):
                    child = children[idx]
                    if child.type == 'declaration':
                        # Field declaration
                        type_node = None
                        id_list = None
                        for c in child.named_children:
                            if c.type == 'type_identifier': type_node = c
                            elif c.type == 'initialized_identifier_list': id_list = c
                            
                        t_str = self._map_type(self._text(type_node, source_bytes)) if type_node else None
                        
                        if id_list:
                            for init_id in id_list.named_children:
                                name_n = None
                                for c in init_id.named_children:
                                    if c.type == 'identifier': name_n = c
                                if name_n:
                                    ident_name = self._text(name_n, source_bytes)
                                    if t_str:
                                        self.ledger.types[ident_name] = t_str
                                        
                                    ident_node = IdentifierNode(ident_name)
                                    if t_str:
                                        ident_node.metadata['type'] = t_str
                                    fields.append(AssignmentNode(ident_node, None))
                    elif child.type == 'method_signature':
                        sig_node = child.named_children[0] if child.named_children else child
                        body_node_func = children[idx+1] if idx+1 < len(children) and children[idx+1].type == 'function_body' else None
                        func_node = self._parse_function(sig_node, body_node_func, source_bytes)
                        if func_node:
                            method = MethodDefNode(func_node.name, func_node.args, func_node.body, func_node.return_type)
                            method.metadata = func_node.metadata
                            methods.append(method)
                        if body_node_func: idx += 1
                    idx += 1

            return ClassDefNode(name, bases, methods, fields)

        elif node.type == 'local_variable_declaration':
            # local_variable_declaration -> initialized_variable_definition
            for child in node.named_children:
                if child.type == 'initialized_variable_definition':
                    type_node = child.child_by_field_name('type')
                    type_str = ""
                    if not type_node:
                        for i, c in enumerate(child.named_children):
                            if c.type in ('type_identifier', 'inferred_type', 'void_type'):
                                type_node = c
                                type_str = self._text(c, source_bytes)
                                # Check if next node is type_arguments or nullable_type
                                next_idx = i + 1
                                while next_idx < len(child.named_children) and child.named_children[next_idx].type in ('type_arguments', 'nullable_type'):
                                    type_str += self._text(child.named_children[next_idx], source_bytes)
                                    next_idx += 1
                                break
                    else:
                        type_str = self._text(type_node, source_bytes)
                        # Find index of type_node to check for type_arguments or nullable_type
                        for i, c in enumerate(child.named_children):
                            if c == type_node:
                                next_idx = i + 1
                                while next_idx < len(child.named_children) and child.named_children[next_idx].type in ('type_arguments', 'nullable_type'):
                                    type_str += self._text(child.named_children[next_idx], source_bytes)
                                    next_idx += 1
                                break
                    
                    name_node = child.child_by_field_name('name')
                    if not name_node:
                        for c in child.named_children:
                            if c.type == 'identifier':
                                name_node = c
                                break
                                
                    value_node = child.child_by_field_name('value')
                    
                    t_str = None
                    if type_node and name_node:
                        ident_name = self._text(name_node, source_bytes)
                        t_str = self._map_type(type_str)
                        self.ledger.types[ident_name] = t_str
                        
                    left = IdentifierNode(self._text(name_node, source_bytes)) if name_node else None
                    if left and left.name == 'self': left.name = 'this'
                    if left and t_str:
                        left.metadata['type'] = t_str
                    
                    if name_node:
                        idx = -1
                        for i, c in enumerate(child.named_children):
                            if c == name_node:
                                idx = i
                                break
                        if idx != -1 and idx + 1 < len(child.named_children):
                            right, _ = self._extract_expr(child.named_children, idx + 1, source_bytes)
                            return AssignmentNode(left, right)
            return None

        elif node.type == 'expression_statement':
            if node.named_children:
                expr, _ = self._extract_expr(node.named_children, 0, source_bytes)
                return expr
            return None
            
        elif node.type == 'argument':
            if node.named_children:
                expr, _ = self._extract_expr(node.named_children, 0, source_bytes)
                return expr
            return None

        elif node.type == 'assignment_expression':
            if node.named_children:
                left, idx = self._extract_expr(node.named_children, 0, source_bytes)
                if idx < len(node.named_children):
                    right, _ = self._extract_expr(node.named_children, idx, source_bytes)
                    return AssignmentNode(left, right)
                return AssignmentNode(left, None)
            return None

        elif node.type == 'assignable_expression':
            expr, _ = self._extract_expr(node.named_children, 0, source_bytes)
            return expr

        elif node.type in ('identifier', 'this'):
            name = self._text(node, source_bytes)
            # Normalize this -> self to match the Hub
            if name == 'this':
                name = 'self'
            ident = IdentifierNode(name)
            if name in self.ledger.types:
                ident.metadata['type'] = self.ledger.types[name]
            return ident

        elif node.type == 'decimal_integer_literal':
            return LiteralNode(int(self._text(node, source_bytes)))

        elif node.type == 'decimal_floating_point_literal':
            return LiteralNode(float(self._text(node, source_bytes)))

        elif node.type == 'string_literal':
            # Remove quotes
            val = self._text(node, source_bytes).strip('\'"')
            return LiteralNode(val)

        elif node.type in ('true', 'false'):
            return LiteralNode(node.type == 'true')

        elif node.type == 'null_literal':
            return IdentifierNode("null")

        elif node.type == 'return_statement':
            if node.named_children:
                value, _ = self._extract_expr(node.named_children, 0, source_bytes)
                return ReturnNode(value)
            return ReturnNode(None)

        elif node.type in ('additive_expression', 'multiplicative_expression', 'relational_expression', 
                           'equality_expression', 'logical_and_expression', 'logical_or_expression'):
            left, idx = self._extract_expr(node.named_children, 0, source_bytes)
            operator_node = node.named_children[idx] if idx < len(node.named_children) else None
            operator = self._text(operator_node, source_bytes) if operator_node else ""
            if operator == '&&': operator = 'and'
            if operator == '||': operator = 'or'
            if operator == '~/': operator = '//'
            
            right, _ = self._extract_expr(node.named_children, idx + 1, source_bytes)
            return BinaryOpNode(left, right, operator)

        elif node.type == 'unary_expression':
            operator = self._text(node.named_children[0], source_bytes) if node.named_children else ""
            if operator == '!': operator = 'not'
            arg, _ = self._extract_expr(node.named_children, 1, source_bytes)
            return BinaryOpNode(IdentifierNode(""), arg, operator)

        elif node.type == 'if_statement':
            condition_node = node.named_children[0] if node.named_children else None
            condition = self._map_node(condition_node, source_bytes) if condition_node else None
            
            body = []
            cons_node = node.child_by_field_name('consequence')
            if cons_node and cons_node.type == 'block':
                for child in cons_node.named_children:
                    mapped = self._map_node(child, source_bytes)
                    if mapped:
                        body.append(mapped)
            
            alt_node = node.child_by_field_name('alternative')
            orelse = None
            if alt_node:
                # alternative could be if_statement or block
                if alt_node.type == 'block':
                    orelse_body = []
                    for child in alt_node.named_children:
                        mapped = self._map_node(child, source_bytes)
                        if mapped:
                            orelse_body.append(mapped)
                    orelse = IfNode(LiteralNode(True), orelse_body, None)
                elif alt_node.type == 'if_statement':
                    orelse = self._map_node(alt_node, source_bytes)
            
            return IfNode(condition, body, orelse)

        elif node.type == 'while_statement':
            condition_node = node.child_by_field_name('condition')
            condition = self._map_node(condition_node, source_bytes) if condition_node else None
            
            body = []
            body_node = node.child_by_field_name('body')
            if body_node and body_node.type == 'block':
                for child in body_node.named_children:
                    mapped = self._map_node(child, source_bytes)
                    if mapped:
                        body.append(mapped)
            return WhileNode(condition, body)

        elif node.type == 'for_statement':
            # Dart: for (var w in words)
            loop_parts = None
            for c in node.named_children:
                if c.type in ('for_loop_parts', 'for_in_loop_parts', 'for_in_parts'):
                    loop_parts = c
                    break
                    
            target = None
            iter_mapped = None
            if loop_parts:
                target_idx = -1
                for i, child in enumerate(loop_parts.named_children):
                    if child.type == 'identifier':
                        target = self._map_node(child, source_bytes)
                        target_idx = i
                        break
                
                if target_idx != -1 and target_idx + 1 < len(loop_parts.named_children):
                    iter_mapped, _ = self._extract_expr(loop_parts.named_children, target_idx + 1, source_bytes)

            body = []
            body_node = node.child_by_field_name('body')
            if body_node and body_node.type == 'block':
                for child in body_node.named_children:
                    mapped = self._map_node(child, source_bytes)
                    if mapped:
                        body.append(mapped)
            return ForNode(target, iter_mapped, body)

        elif node.type == 'list_literal':
            elements = []
            for child in node.named_children:
                if child.type != 'type_arguments':
                    mapped = self._map_node(child, source_bytes)
                    if mapped:
                        elements.append(mapped)
            return ListNode(elements)

        elif node.type == 'set_or_map_literal':
            keys = []
            values = []
            for child in node.named_children:
                if child.type == 'map_literal_entry':
                    k_node = child.child_by_field_name('key')
                    v_node = child.child_by_field_name('value')
                    if k_node and v_node:
                        keys.append(self._map_node(k_node, source_bytes))
                        values.append(self._map_node(v_node, source_bytes))
            return DictNode(keys, values)

        elif node.type == 'try_statement':
            body = []
            body_node = node.child_by_field_name('body')
            if body_node and body_node.type == 'block':
                for child in body_node.named_children:
                    mapped = self._map_node(child, source_bytes)
                    if mapped:
                        body.append(mapped)
            
            handlers = []
            for child in node.named_children:
                if child.type == 'catch_clause':
                    exc_body_node = child.child_by_field_name('body')
                    if exc_body_node and exc_body_node.type == 'block':
                        for exc_child in exc_body_node.named_children:
                            mapped = self._map_node(exc_child, source_bytes)
                            if mapped:
                                handlers.append(mapped)
                    break
            return TryCatchNode(body, handlers)

        elif node.type == 'throw_expression':
            exc, _ = self._extract_expr(node.named_children, 0, source_bytes)
            return CallNode("throw", [exc]) if exc else CallNode("throw", [])

        elif node.type == 'parenthesized_expression':
            return self._map_node(node.named_children[0], source_bytes) if node.named_children else None
            
        elif node.type == 'type_test_expression':
            # e.g., v is null
            left, idx = self._extract_expr(node.named_children, 0, source_bytes)
            # type_test child
            if idx < len(node.named_children):
                type_test_node = node.named_children[idx]
                if type_test_node.type == 'type_test':
                    op = 'is'
                    right_node = type_test_node.named_children[0] if type_test_node.named_children else None
                    if right_node and right_node.type == 'type_identifier':
                        if self._text(right_node, source_bytes) == 'null':
                            op = 'is'
                            return BinaryOpNode(left, IdentifierNode("null"), op)
            return BinaryOpNode(left, IdentifierNode("null"), 'is')

        return None
