from tree_sitter import Parser, Language
import tree_sitter_python as tspython
from pseudocoup.core.ledger import Ledger
from pseudocoup.core.ur_ast import (
    URNode, ModuleNode, FunctionDefNode, ClassDefNode, MethodDefNode,
    AssignmentNode, ReturnNode, BinaryOpNode, CallNode,
    IdentifierNode, LiteralNode,
    IfNode, WhileNode, ForNode, TryCatchNode,
    ListNode, DictNode, SubscriptNode, AttributeNode
)

class PythonIngestor:
    def __init__(self, ledger: Ledger):
        self.ledger = ledger
        self.parser = Parser()
        
        # Determine tree-sitter version compat
        try:
            # For tree-sitter < 0.22
            self.language = Language(tspython.language(), "python")
            self.parser.set_language(self.language)
        except Exception:
            # For tree-sitter >= 0.22
            self.language = Language(tspython.language())
            try:
                self.parser.set_language(self.language)
            except AttributeError:
                self.parser.language = self.language

    def parse(self, source_bytes: bytes) -> ModuleNode:
        tree = self.parser.parse(source_bytes)
        root_node = tree.root_node
        return self._map_node(root_node, source_bytes, "main")

    def _map_node(self, node, source_bytes: bytes, scope: str = "main") -> URNode:
        if node is None:
            return None

        if node.type == 'module':
            body = []
            for child in node.named_children:
                mapped = self._map_node(child, source_bytes, scope)
                if mapped:
                    body.append(mapped)
            return ModuleNode(body)

        elif node.type == 'function_definition':
            name_node = node.child_by_field_name('name')
            name = name_node.text.decode('utf-8') if name_node else ""
            
            new_scope = name if scope == "main" else f"{scope}.{name}"

            return_type_node = node.child_by_field_name('return_type')
            return_type = return_type_node.text.decode('utf-8') if return_type_node else None

            args = []
            parameters_node = node.child_by_field_name('parameters')
            if parameters_node:
                for child in parameters_node.named_children:
                    if child.type == 'identifier':
                        args.append(self._map_node(child, source_bytes, scope))
                    elif child.type == 'typed_parameter':
                        ident_node = child.child(0)
                        type_node = child.child_by_field_name('type')
                        if type_node and ident_node:
                            ident_name = ident_node.text.decode('utf-8')
                            type_str = type_node.text.decode('utf-8')
                            self.ledger.register_type(new_scope, ident_name, type_str)
                        if ident_node:
                            args.append(self._map_node(ident_node, source_bytes, new_scope))

            body = []
            body_node = node.child_by_field_name('body')
            if body_node:
                for child in body_node.named_children:
                    mapped = self._map_node(child, source_bytes, new_scope)
                    if mapped:
                        body.append(mapped)

            func_node = FunctionDefNode(name, args, body, return_type)
            if return_type:
                func_node.metadata['type'] = return_type
            return func_node

        elif node.type == 'class_definition':
            name_node = node.child_by_field_name('name')
            name = name_node.text.decode('utf-8') if name_node else ""
            
            new_scope = name if scope == "main" else f"{scope}.{name}"

            superclasses_node = node.child_by_field_name('superclasses')
            bases = []
            if superclasses_node:
                for child in superclasses_node.named_children:
                    bases.append(child.text.decode('utf-8'))

            methods = []
            fields = []
            body_node = node.child_by_field_name('body')
            if body_node:
                for child in body_node.named_children:
                    mapped = self._map_node(child, source_bytes, new_scope)
                    if isinstance(mapped, FunctionDefNode):
                        method = MethodDefNode(mapped.name, mapped.args, mapped.body, mapped.return_type)
                        method.metadata = mapped.metadata
                        methods.append(method)
                    elif isinstance(mapped, AssignmentNode):
                        fields.append(mapped)

            return ClassDefNode(name, bases, methods, fields)

        elif node.type in ('expression_statement', 'parenthesized_expression', 'pattern_list'):
            if node.named_children:
                return self._map_node(node.named_children[0], source_bytes, scope)
            return None

        elif node.type == 'assignment':
            left_node = node.child_by_field_name('left')
            right_node = node.child_by_field_name('right')
            type_node = node.child_by_field_name('type')

            if type_node and left_node:
                left_name = left_node.text.decode('utf-8')
                type_str = type_node.text.decode('utf-8')
                self.ledger.register_type(scope, left_name, type_str)

            left = self._map_node(left_node, source_bytes, scope) if left_node else None
            right = self._map_node(right_node, source_bytes, scope) if right_node else None
            return AssignmentNode(left, right)

        elif node.type == 'return_statement':
            if node.named_children:
                value = self._map_node(node.named_children[0], source_bytes, scope)
                return ReturnNode(value)
            return ReturnNode(None)

        elif node.type in ('binary_operator', 'comparison_operator', 'boolean_operator'):
            left_node = node.child_by_field_name('left') or (node.named_children[0] if len(node.named_children) > 0 else None)
            right_node = node.child_by_field_name('right') or (node.named_children[1] if len(node.named_children) > 1 else None)
            operator_node = node.child_by_field_name('operator')
            if operator_node:
                operator = operator_node.text.decode('utf-8')
            else:
                # Find the first unnamed child, which is usually the operator
                operator = ""
                for child in node.children:
                    if not child.is_named:
                        operator = child.text.decode('utf-8')
                        break
                        
            if operator == 'and': operator = '&&'
            if operator == 'or': operator = '||'
            left = self._map_node(left_node, source_bytes, scope) if left_node else None
            right = self._map_node(right_node, source_bytes, scope) if right_node else None
            return BinaryOpNode(left, right, operator)

        elif node.type in ('unary_operator', 'not_operator'):
            operator_node = node.child_by_field_name('operator')
            if operator_node:
                operator = operator_node.text.decode('utf-8')
            else:
                operator = ""
                for child in node.children:
                    if not child.is_named:
                        operator = child.text.decode('utf-8')
                        break
                        
            if operator == 'not': operator = '!'
            arg_node = node.child_by_field_name('argument') or (node.named_children[0] if len(node.named_children) > 0 else None)
            arg = self._map_node(arg_node, source_bytes, scope) if arg_node else None
            # map unary as binary with empty left side to trick dart emitter
            return BinaryOpNode(IdentifierNode(""), arg, operator)

        elif node.type == 'call':
            function_node = node.child_by_field_name('function')
            func_name = self._map_node(function_node, source_bytes, scope) if function_node else ""

            args = []
            arguments_node = node.child_by_field_name('arguments')
            if arguments_node:
                for child in arguments_node.named_children:
                    mapped = self._map_node(child, source_bytes, scope)
                    if mapped:
                        args.append(mapped)

            return CallNode(func_name, args)

        elif node.type == 'identifier':
            name = node.text.decode('utf-8')
            ident_node = IdentifierNode(name)
            
            # Fetch from ledger using FQDN
            ledger_type = self.ledger.get_type(scope, name)
            if ledger_type:
                ident_node.metadata['type'] = ledger_type
            return ident_node
            
        elif node.type == 'none':
            return IdentifierNode("null")

        elif node.type == 'integer':
            value = int(node.text.decode('utf-8'))
            return LiteralNode(value)

        elif node.type == 'float':
            value = float(node.text.decode('utf-8'))
            return LiteralNode(value)

        elif node.type in ('string', 'string_content'):
            value = node.text.decode('utf-8')
            value = value.strip('\'"')
            return LiteralNode(value)

        elif node.type in ('true', 'false'):
            return LiteralNode(node.type == 'true')

        elif node.type == 'if_statement':
            condition_node = node.child_by_field_name('condition')
            condition = self._map_node(condition_node, source_bytes, scope) if condition_node else None

            body = []
            consequence_node = node.child_by_field_name('consequence')
            if consequence_node:
                for child in consequence_node.named_children:
                    mapped = self._map_node(child, source_bytes, scope)
                    if mapped:
                        body.append(mapped)

            alternatives = [c for c in node.named_children if c.type in ('elif_clause', 'else_clause')]
            
            # Build nested IfNodes from right to left
            orelse = None
            for alt in reversed(alternatives):
                if alt.type == 'else_clause':
                    orelse_body = []
                    else_body_node = alt.child_by_field_name('body')
                    if else_body_node:
                        for child in else_body_node.named_children:
                            mapped = self._map_node(child, source_bytes, scope)
                            if mapped:
                                orelse_body.append(mapped)
                    orelse = IfNode(LiteralNode(True), orelse_body, None)
                elif alt.type == 'elif_clause':
                    elif_cond_node = alt.child_by_field_name('condition')
                    elif_cond = self._map_node(elif_cond_node, source_bytes, scope) if elif_cond_node else None
                    
                    elif_body = []
                    elif_cons_node = alt.child_by_field_name('consequence')
                    if elif_cons_node:
                        for child in elif_cons_node.named_children:
                            mapped = self._map_node(child, source_bytes, scope)
                            if mapped:
                                elif_body.append(mapped)
                    orelse = IfNode(elif_cond, elif_body, orelse)

            return IfNode(condition, body, orelse)

        elif node.type == 'while_statement':
            condition_node = node.child_by_field_name('condition')
            condition = self._map_node(condition_node, source_bytes, scope) if condition_node else None
            
            body = []
            body_node = node.child_by_field_name('body')
            if body_node:
                for child in body_node.named_children:
                    mapped = self._map_node(child, source_bytes, scope)
                    if mapped:
                        body.append(mapped)
            return WhileNode(condition, body)

        elif node.type == 'for_statement':
            target_node = node.child_by_field_name('left')
            target = self._map_node(target_node, source_bytes, scope) if target_node else None
            
            iter_node = node.child_by_field_name('right')
            iter_mapped = self._map_node(iter_node, source_bytes, scope) if iter_node else None
            
            body = []
            body_node = node.child_by_field_name('body')
            if body_node:
                for child in body_node.named_children:
                    mapped = self._map_node(child, source_bytes, scope)
                    if mapped:
                        body.append(mapped)
            return ForNode(target, iter_mapped, body)

        elif node.type == 'try_statement':
            body = []
            body_node = node.child_by_field_name('body')
            if body_node:
                for child in body_node.named_children:
                    mapped = self._map_node(child, source_bytes, scope)
                    if mapped:
                        body.append(mapped)
            
            handlers = []
            for child in node.named_children:
                if child.type == 'except_clause':
                    exc_body_node = child.child_by_field_name('body')
                    if exc_body_node:
                        for exc_child in exc_body_node.named_children:
                            mapped = self._map_node(exc_child, source_bytes, scope)
                            if mapped:
                                handlers.append(mapped)
                    break

            return TryCatchNode(body, handlers)

        elif node.type in ('list', 'tuple'):
            elements = []
            for child in node.named_children:
                mapped = self._map_node(child, source_bytes, scope)
                if mapped:
                    elements.append(mapped)
            return ListNode(elements)

        elif node.type == 'dictionary':
            keys = []
            values = []
            for child in node.named_children:
                if child.type == 'pair':
                    k_node = child.child_by_field_name('key')
                    v_node = child.child_by_field_name('value')
                    if k_node and v_node:
                        keys.append(self._map_node(k_node, source_bytes, scope))
                        values.append(self._map_node(v_node, source_bytes, scope))
            return DictNode(keys, values)

        elif node.type == 'subscript':
            value_node = node.child_by_field_name('value')
            slice_node = node.child_by_field_name('subscript')
            value = self._map_node(value_node, source_bytes, scope) if value_node else None
            slice_mapped = self._map_node(slice_node, source_bytes, scope) if slice_node else None
            return SubscriptNode(value, slice_mapped)

        elif node.type == 'attribute':
            value_node = node.child_by_field_name('object')
            attr_node = node.child_by_field_name('attribute')
            value = self._map_node(value_node, source_bytes, scope) if value_node else None
            attr = attr_node.text.decode('utf-8') if attr_node else ""
            return AttributeNode(value, attr)
            
        elif node.type == 'raise_statement':
            # Map raise to a CallNode for 'throw'
            exc = None
            if node.named_children:
                exc = self._map_node(node.named_children[0], source_bytes, scope)
            return CallNode("throw", [exc]) if exc else CallNode("throw", [])

        else:
            return None
