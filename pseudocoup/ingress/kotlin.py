from tree_sitter import Parser, Language
import tree_sitter_kotlin as tskotlin
from pseudocoup.core.ledger import Ledger
from pseudocoup.core.ur_ast import (
    URNode, ModuleNode, FunctionDefNode, ClassDefNode, MethodDefNode,
    AssignmentNode, ReturnNode, BinaryOpNode, CallNode,
    IdentifierNode, LiteralNode,
    IfNode, WhileNode, ForNode, TryCatchNode,
    ListNode, DictNode, SubscriptNode, AttributeNode
)

class KotlinIngestor:
    def __init__(self, ledger: Ledger):
        self.ledger = ledger
        self.parser = Parser()
        
        # Determine tree-sitter version compat
        try:
            # For tree-sitter < 0.22
            self.language = Language(tskotlin.language(), "kotlin")
            self.parser.set_language(self.language)
        except Exception:
            # For tree-sitter >= 0.22
            self.language = Language(tskotlin.language())
            try:
                self.parser.set_language(self.language)
            except AttributeError:
                self.parser.language = self.language

    def parse(self, source_bytes: bytes) -> ModuleNode:
        tree = self.parser.parse(source_bytes)
        root_node = tree.root_node
        return self._map_node(root_node, source_bytes, "main")

    def ingest(self, source_bytes: bytes) -> ModuleNode:
        return self.parse(source_bytes)

    def _get_text(self, node, source_bytes: bytes) -> str:
        if node is None:
            return ""
        return source_bytes[node.start_byte:node.end_byte].decode('utf-8')

    def _map_node(self, node, source_bytes: bytes, scope: str = "main") -> URNode:
        if node is None:
            return None

        if node.type == 'source_file':
            body = []
            for child in node.named_children:
                mapped = self._map_node(child, source_bytes, scope)
                if mapped:
                    body.append(mapped)
            return ModuleNode(body)

        elif node.type == 'function_declaration':
            # name is usually an identifier child
            ident_node = next((c for c in node.named_children if c.type == 'identifier'), None)
            name = self._get_text(ident_node, source_bytes) if ident_node else ""
            
            new_scope = name if scope == "main" else f"{scope}.{name}"

            # return type
            type_node = next((c for c in node.named_children if c.type in ('user_type', 'nullable_type')), None)
            return_type = self._get_text(type_node, source_bytes) if type_node else None

            args = []
            params_node = next((c for c in node.named_children if c.type == 'function_value_parameters'), None)
            if params_node:
                for p in params_node.named_children:
                    if p.type == 'parameter':
                        p_ident = next((c for c in p.named_children if c.type == 'identifier'), None)
                        p_type = next((c for c in p.named_children if c.type in ('user_type', 'nullable_type')), None)
                        if p_ident and p_type:
                            ident_name = self._get_text(p_ident, source_bytes)
                            type_str = self._get_text(p_type, source_bytes)
                            self.ledger.register_type(new_scope, ident_name, type_str)
                        if p_ident:
                            args.append(self._map_node(p_ident, source_bytes, new_scope))

            body = []
            body_node = next((c for c in node.named_children if c.type == 'function_body'), None)
            if body_node:
                # it's usually a block
                block_node = next((c for c in body_node.named_children if c.type == 'block'), None)
                if block_node:
                    for child in block_node.named_children:
                        mapped = self._map_node(child, source_bytes, new_scope)
                        if mapped:
                            body.append(mapped)

            func_node = FunctionDefNode(name, args, body, return_type)
            if return_type:
                func_node.metadata['type'] = return_type
            return func_node

        elif node.type == 'class_declaration':
            ident_node = next((c for c in node.named_children if c.type == 'identifier'), None)
            name = self._get_text(ident_node, source_bytes) if ident_node else ""
            
            new_scope = name if scope == "main" else f"{scope}.{name}"

            bases = [] # TODO if needed

            methods = []
            fields = []
            body_node = next((c for c in node.named_children if c.type == 'class_body'), None)
            if body_node:
                for child in body_node.named_children:
                    mapped = self._map_node(child, source_bytes, new_scope)
                    if isinstance(mapped, FunctionDefNode):
                        method = MethodDefNode(mapped.name, mapped.args, mapped.body, mapped.return_type)
                        method.metadata = mapped.metadata
                        methods.append(method)
                    elif isinstance(mapped, MethodDefNode):
                        methods.append(mapped)
                    elif isinstance(mapped, AssignmentNode):
                        fields.append(mapped)
                    elif isinstance(mapped, list): # For multiple fields if mapped returned a list
                        for m in mapped:
                            if isinstance(m, AssignmentNode):
                                fields.append(m)

            return ClassDefNode(name, bases, methods, fields)

        elif node.type == 'secondary_constructor':
            args = []
            params_node = next((c for c in node.named_children if c.type == 'function_value_parameters'), None)
            if params_node:
                for p in params_node.named_children:
                    if p.type == 'parameter':
                        p_ident = next((c for c in p.named_children if c.type == 'identifier'), None)
                        p_type = next((c for c in p.named_children if c.type in ('user_type', 'nullable_type')), None)
                        if p_ident and p_type:
                            ident_name = self._get_text(p_ident, source_bytes)
                            type_str = self._get_text(p_type, source_bytes)
                            self.ledger.register_type(scope, ident_name, type_str)
                        if p_ident:
                            args.append(self._map_node(p_ident, source_bytes, scope))

            body = []
            block_node = next((c for c in node.named_children if c.type == 'block'), None)
            if block_node:
                for child in block_node.named_children:
                    mapped = self._map_node(child, source_bytes, scope)
                    if mapped:
                        body.append(mapped)
            return MethodDefNode("__init__", args, body, None)

        elif node.type == 'property_declaration':
            var_decl = next((c for c in node.named_children if c.type == 'variable_declaration'), None)
            ident_node = next((c for c in var_decl.named_children if c.type == 'identifier'), None) if var_decl else None
            type_node = next((c for c in var_decl.named_children if c.type in ('user_type', 'nullable_type')), None) if var_decl else None
            
            left = None
            if ident_node:
                ident_name = self._get_text(ident_node, source_bytes)
                if type_node:
                    type_str = self._get_text(type_node, source_bytes)
                    self.ledger.register_type(scope, ident_name, type_str)
                left = self._map_node(ident_node, source_bytes, scope)

            # right side is the last named child of property_declaration if it is an expression
            right = None
            if len(node.named_children) > 1:
                # Usually it's the last child like number_literal, string_literal, etc.
                right_node = node.named_children[-1]
                if right_node.type != 'variable_declaration':
                    right = self._map_node(right_node, source_bytes, scope)
            
            if left and right:
                return AssignmentNode(left, right)
            return None

        elif node.type == 'assignment':
            if len(node.named_children) >= 2:
                left = self._map_node(node.named_children[0], source_bytes, scope)
                right = self._map_node(node.named_children[1], source_bytes, scope)
                return AssignmentNode(left, right)
            return None

        elif node.type == 'return_expression':
            if node.named_children:
                value = self._map_node(node.named_children[0], source_bytes, scope)
                return ReturnNode(value)
            return ReturnNode(None)

        elif node.type == 'binary_expression':
            if len(node.named_children) == 2:
                left_node = node.named_children[0]
                right_node = node.named_children[1]
                # Find the operator text from source bytes since unnamed child is the operator
                op_node = None
                for child in node.children:
                    if not child.is_named:
                        op_node = child
                        break
                operator = self._get_text(op_node, source_bytes).strip() if op_node else ""
                
                left = self._map_node(left_node, source_bytes, scope)
                right = self._map_node(right_node, source_bytes, scope)
                return BinaryOpNode(left, right, operator)
            return None
            
        elif node.type == 'prefix_expression' or node.type == 'unary_expression':
            op_node = next((c for c in node.children if not c.is_named), None)
            operator = self._get_text(op_node, source_bytes).strip() if op_node else ""
            if operator == '!':
                arg_node = node.named_children[0] if node.named_children else None
                arg = self._map_node(arg_node, source_bytes, scope) if arg_node else None
                return BinaryOpNode(IdentifierNode(""), arg, "!")
            elif operator == '-':
                arg_node = node.named_children[0] if node.named_children else None
                arg = self._map_node(arg_node, source_bytes, scope) if arg_node else None
                return BinaryOpNode(IdentifierNode(""), arg, "-")
            return None

        elif node.type == 'call_expression':
            # func name
            ident_node = next((c for c in node.named_children if c.type in ('identifier', 'navigation_expression')), None)
            func_name = self._map_node(ident_node, source_bytes, scope) if ident_node else IdentifierNode("")

            args = []
            val_args_node = next((c for c in node.named_children if c.type == 'value_arguments'), None)
            if val_args_node:
                for child in val_args_node.named_children:
                    if child.type == 'value_argument':
                        mapped = self._map_node(child.named_children[0] if child.named_children else child, source_bytes, scope)
                        if mapped:
                            args.append(mapped)

            # Unpack print(x) -> call PrintNode if needed, but Python uses call('print', args)
            return CallNode(func_name, args)

        elif node.type == 'identifier':
            name = self._get_text(node, source_bytes)
            ident_node = IdentifierNode(name)
            ledger_type = self.ledger.get_type(scope, name)
            if ledger_type:
                ident_node.metadata['type'] = ledger_type
            return ident_node

        elif node.type == 'null_literal' or self._get_text(node, source_bytes) == 'null':
            return IdentifierNode("null")
            
        elif node.type == 'this_expression':
            return IdentifierNode("self")

        elif node.type in ('integer_literal', 'number_literal'):
            value_str = self._get_text(node, source_bytes)
            try:
                value = int(value_str)
            except ValueError:
                value = float(value_str) if '.' in value_str else value_str
            return LiteralNode(value)

        elif node.type in ('float_literal', 'double_literal'):
            value_str = self._get_text(node, source_bytes).rstrip('fF')
            return LiteralNode(float(value_str))

        elif node.type == 'string_literal':
            # handle string_content
            content_node = next((c for c in node.named_children if c.type == 'string_content'), None)
            if content_node:
                value = self._get_text(content_node, source_bytes)
            else:
                value = self._get_text(node, source_bytes).strip('\'"')
            return LiteralNode(value)

        elif node.type == 'boolean_literal':
            value_str = self._get_text(node, source_bytes)
            return LiteralNode(value_str == 'true')

        elif node.type == 'if_expression':
            condition_node = next((c for c in node.children if c.type == 'parenthesized_expression'), None)
            if not condition_node and node.named_children:
                condition_node = node.named_children[0]
                
            condition = self._map_node(condition_node, source_bytes, scope) if condition_node else None

            blocks = [c for c in node.children if c.type == 'block']
            body = []
            orelse_body = []
            
            if len(blocks) > 0:
                for child in blocks[0].named_children:
                    mapped = self._map_node(child, source_bytes, scope)
                    if mapped:
                        body.append(mapped)
                        
            orelse = None
            if len(blocks) > 1:
                for child in blocks[1].named_children:
                    mapped = self._map_node(child, source_bytes, scope)
                    if mapped:
                        orelse_body.append(mapped)
                orelse = IfNode(LiteralNode(True), orelse_body, None)
            else:
                elif_node = next((c for c in node.named_children if c.type == 'if_expression'), None)
                if elif_node:
                    orelse = self._map_node(elif_node, source_bytes, scope)

            return IfNode(condition, body, orelse)

        elif node.type == 'while_statement':
            condition_node = next((c for c in node.named_children if c.type == 'parenthesized_expression'), None)
            condition = self._map_node(condition_node, source_bytes, scope) if condition_node else None
            
            body = []
            block_node = next((c for c in node.named_children if c.type == 'block'), None)
            if block_node:
                for child in block_node.named_children:
                    mapped = self._map_node(child, source_bytes, scope)
                    if mapped:
                        body.append(mapped)
            return WhileNode(condition, body)

        elif node.type == 'for_statement':
            target_node = next((c for c in node.named_children if c.type in ('variable_declaration', 'identifier')), None)
            target = None
            if target_node:
                if target_node.type == 'variable_declaration':
                    ident = next((c for c in target_node.named_children if c.type == 'identifier'), None)
                    target = self._map_node(ident, source_bytes, scope) if ident else None
                else:
                    target = self._map_node(target_node, source_bytes, scope)
            
            # Kotlin "for (x in iter)" has 'in_expression' or something?
            # Actually, the children of for_statement are usually parameter/variable_declaration and the iterable expression
            # Wait, `for (k in (1 until 6))`
            # The second named child is usually the iterable.
            iter_mapped = None
            if len(node.named_children) > 1:
                # The 2nd child is the iterable
                iter_mapped = self._map_node(node.named_children[1], source_bytes, scope)
            
            body = []
            block_node = next((c for c in node.named_children if c.type == 'block'), None)
            if block_node:
                for child in block_node.named_children:
                    mapped = self._map_node(child, source_bytes, scope)
                    if mapped:
                        body.append(mapped)
            return ForNode(target, iter_mapped, body)

        elif node.type == 'try_expression':
            body = []
            blocks = [c for c in node.named_children if c.type == 'block']
            if len(blocks) > 0:
                for child in blocks[0].named_children:
                    mapped = self._map_node(child, source_bytes, scope)
                    if mapped:
                        body.append(mapped)
            
            handlers = []
            catch_node = next((c for c in node.named_children if c.type == 'catch_block'), None)
            if catch_node:
                catch_block = next((c for c in catch_node.named_children if c.type == 'block'), None)
                if catch_block:
                    for child in catch_block.named_children:
                        mapped = self._map_node(child, source_bytes, scope)
                        if mapped:
                            handlers.append(mapped)

            return TryCatchNode(body, handlers)

        elif node.type == 'throw_expression':
            exc = None
            if node.named_children:
                exc = self._map_node(node.named_children[0], source_bytes, scope)
            return CallNode("throw", [exc]) if exc else CallNode("throw", [])

        elif node.type == 'navigation_expression': # e.g. a.b
            obj_node = node.named_children[0] if len(node.named_children) > 0 else None
            prop_node = node.named_children[1] if len(node.named_children) > 1 else None
            
            obj = self._map_node(obj_node, source_bytes, scope) if obj_node else None
            attr = self._get_text(prop_node, source_bytes) if prop_node else ""
            return AttributeNode(obj, attr)

        elif node.type == 'index_expression': # e.g. a[b]
            value_node = node.named_children[0] if len(node.named_children) > 0 else None
            slice_node = node.named_children[1] if len(node.named_children) > 1 else None
            
            value = self._map_node(value_node, source_bytes, scope) if value_node else None
            slice_mapped = self._map_node(slice_node, source_bytes, scope) if slice_node else None
            return SubscriptNode(value, slice_mapped)

        elif node.type == 'infix_expression':
            left = self._map_node(node.named_children[0], source_bytes, scope) if len(node.named_children) > 0 else None
            right = self._map_node(node.named_children[1], source_bytes, scope) if len(node.named_children) > 1 else None
            
            # find operator
            op_node = None
            for child in node.children:
                if not child.is_named:
                    op_node = child
                    break
            operator = self._get_text(op_node, source_bytes).strip() if op_node else ""
            
            if operator == "until":
                return CallNode(IdentifierNode("range"), [left, right])
            return BinaryOpNode(left, right, operator)

        elif node.type == 'parenthesized_expression':
            if node.named_children:
                return self._map_node(node.named_children[0], source_bytes, scope)
            return None
            
        elif node.type == 'as_expression': # e.g. pair[0] as String
            if node.named_children:
                return self._map_node(node.named_children[0], source_bytes, scope)
            return None
            
        elif node.type == 'in_expression': # e.g. "quickfox" in words
            # Treat as BinaryOpNode with operator 'in'
            if len(node.named_children) == 2:
                left = self._map_node(node.named_children[0], source_bytes, scope)
                right = self._map_node(node.named_children[1], source_bytes, scope)
                return BinaryOpNode(left, right, "in")
            return None

        # Ignore imports for UR-AST as per typical transpiler mapping
        elif node.type == 'import_list' or node.type == 'import':
            return None

        else:
            return None
