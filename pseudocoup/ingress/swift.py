import tree_sitter_swift as ts
from tree_sitter import Parser, Language, Node
from pseudocoup.core.ur_ast import (
    URNode, ModuleNode, FunctionDefNode, MethodDefNode, ClassDefNode, AssignmentNode,
    BinaryOpNode, CallNode, IdentifierNode, LiteralNode,
    ReturnNode, IfNode, WhileNode, ForNode, TryCatchNode, ListNode,
    DictNode, SubscriptNode, AttributeNode
)
from pseudocoup.core.ledger import Ledger

class SwiftIngestor:
    def __init__(self, ledger: Ledger):
        self.ledger = ledger
        self.parser = Parser()
        try:
            lang = Language(ts.language(), "swift")
            self.parser.set_language(lang)
        except Exception:
            lang = Language(ts.language())
            try:
                self.parser.set_language(lang)
            except AttributeError:
                self.parser.language = lang

    def _create_node(self, node_cls, metadata=None, **kwargs):
        node = node_cls(**kwargs)
        if metadata:
            node.metadata = metadata
        return node

    def parse(self, source_bytes: bytes) -> ModuleNode:
        tree = self.parser.parse(source_bytes)
        module_node = self._map_node(tree.root_node, source_bytes, "")
        if isinstance(module_node, list):
            return self._create_node(ModuleNode, body=module_node)
        return module_node if isinstance(module_node, ModuleNode) else self._create_node(ModuleNode, body=[module_node])

    def _get_text(self, node: Node, source_bytes: bytes) -> str:
        if not node: return ""
        return source_bytes[node.start_byte:node.end_byte].decode("utf-8")
        
    def _extract_type_annotation(self, node: Node, source_bytes: bytes) -> str:
        if not node: return "Any"
        type_ann = node.child_by_field_name('type') or next((c for c in node.named_children if c.type == 'type_annotation' or c.type == 'user_type'), None)
        if type_ann:
            if type_ann.type == 'type_annotation':
                ut = next((c for c in type_ann.named_children if c.type == 'user_type'), None)
                if ut: type_ann = ut
            return self._get_text(type_ann, source_bytes).strip()
        return "Any"

    def _get_pattern_name(self, node: Node, source_bytes: bytes) -> str:
        if not node: return "unknown"
        if node.type == 'value_binding_pattern' or node.type == 'pattern':
            pat = next((c for c in node.named_children if c.type == 'pattern'), None) or node
            id_node = next((c for c in pat.named_children if c.type == 'simple_identifier'), None)
            if id_node:
                return self._get_text(id_node, source_bytes)
        return self._get_text(node, source_bytes)

    def _map_node(self, node: Node, source_bytes: bytes, scope: str):
        if not node or not node.is_named:
            return None

        if node.type == 'source_file':
            body = []
            for child in node.named_children:
                mapped = self._map_node(child, source_bytes, scope)
                if mapped:
                    if isinstance(mapped, list): body.extend(mapped)
                    else: body.append(mapped)
            return self._create_node(ModuleNode, body=body, metadata={"type": "source_file"})

        elif node.type == 'class_declaration':
            name_node = next((c for c in node.named_children if c.type == 'type_identifier'), None)
            name = self._get_text(name_node, source_bytes) if name_node else "UnknownClass"
            new_scope = f"{scope}.{name}" if scope else name
            
            fields = []
            methods = []
            
            body_node = next((c for c in node.named_children if c.type == 'class_body'), None)
            if body_node:
                for child in body_node.named_children:
                    mapped = self._map_node(child, source_bytes, new_scope)
                    if not mapped: continue
                    
                    if isinstance(mapped, list):
                        for m in mapped:
                            if isinstance(m, AssignmentNode): fields.append(m)
                            else: methods.append(m)
                    else:
                        if isinstance(mapped, AssignmentNode): fields.append(mapped)
                        else: methods.append(mapped)
                        
            return self._create_node(ClassDefNode, name=name, bases=[], fields=fields, methods=methods)

        elif node.type == 'property_declaration':
            assignments = []
            
            pattern_nodes = [c for c in node.named_children if c.type == 'pattern']
            if not pattern_nodes:
                # might be simple
                pass
                
            for pat in pattern_nodes:
                name = self._get_pattern_name(pat, source_bytes)
                var_type = self._extract_type_annotation(node, source_bytes)
                
                # Check if var_type is empty or we need to extract from vbp directly
                if var_type == "Any":
                    ta = next((c for c in node.named_children if c.type == 'type_annotation'), None)
                    if ta:
                        ut = next((c for c in ta.named_children if c.type == 'user_type'), None)
                        if ut: var_type = self._get_text(ut, source_bytes)
                        
                self.ledger.register_type(scope, name, var_type)
                
                # value is typically a sibling or child. In Swift tree-sitter:
                # integer_literal is a sibling of type_annotation and value_binding_pattern
                val_node = None
                for c in node.named_children:
                    if c.type not in ('value_binding_pattern', 'type_annotation', 'pattern', 'simple_identifier'):
                        val_node = c
                        break
                        
                left = self._create_node(IdentifierNode, name=name, metadata={"type": var_type})
                right = self._map_node(val_node, source_bytes, scope) if val_node else None
                
                assignments.append(self._create_node(AssignmentNode, left=left, right=right))
                
            if len(assignments) == 1:
                return assignments[0]
            if len(assignments) > 1:
                return assignments
                
            return None

        elif node.type == 'init_declaration':
            meth_name = "__init__"
            ret_type = "Void"
            
            self.ledger.register_type(scope, meth_name, ret_type)
            fqdn = f"{scope}.{meth_name}" if scope else meth_name
            
            args = []
            for param in node.named_children:
                if param.type == 'parameter':
                    p_name_node = next((c for c in param.named_children if c.type == 'simple_identifier'), None)
                    if p_name_node:
                        p_name = self._get_text(p_name_node, source_bytes)
                        p_type = self._extract_type_annotation(param, source_bytes)
                        self.ledger.register_type(fqdn, p_name, p_type)
                        args.append(self._create_node(IdentifierNode, name=p_name, metadata={"type": p_type}))
            
            body_node = next((c for c in node.named_children if c.type == 'function_body'), None)
            body = []
            if body_node:
                for child in body_node.named_children:
                    mapped = self._map_node(child, source_bytes, fqdn)
                    if mapped:
                        if isinstance(mapped, list): body.extend(mapped)
                        else: body.append(mapped)
                        
            return self._create_node(MethodDefNode, name=meth_name, args=args, body=body, metadata={"type": ret_type})

        elif node.type == 'function_declaration':
            name_node = next((c for c in node.named_children if c.type == 'simple_identifier'), None)
            name = self._get_text(name_node, source_bytes) if name_node else "unknown"
            
            ret_type = "Void"
            ut_node = next((c for c in node.named_children if c.type == 'user_type'), None)
            if ut_node: ret_type = self._get_text(ut_node, source_bytes)
            
            self.ledger.register_type(scope, name, ret_type)
            fqdn = f"{scope}.{name}" if scope else name
            
            args = []
            for param in node.named_children:
                if param.type == 'parameter':
                    p_name_node = next((c for c in param.named_children if c.type == 'simple_identifier'), None)
                    if p_name_node:
                        p_name = self._get_text(p_name_node, source_bytes)
                        # Could be array_type or user_type
                        p_type = self._get_text(param.named_children[-1], source_bytes) if len(param.named_children) > 1 else "Any"
                        self.ledger.register_type(fqdn, p_name, p_type)
                        args.append(self._create_node(IdentifierNode, name=p_name, metadata={"type": p_type}))
            
            body_node = next((c for c in node.named_children if c.type == 'function_body'), None)
            body = []
            if body_node:
                for child in body_node.named_children:
                    mapped = self._map_node(child, source_bytes, fqdn)
                    if mapped:
                        if isinstance(mapped, list): body.extend(mapped)
                        else: body.append(mapped)
                        
            # If we are at the root (scope is empty), it's a FunctionDefNode. If we are in a class, MethodDefNode.
            if not scope:
                return self._create_node(FunctionDefNode, name=name, args=args, body=body, metadata={"type": ret_type})
            return self._create_node(MethodDefNode, name=name, args=args, body=body, metadata={"type": ret_type})

        elif node.type == 'statements' or node.type == 'function_body':
            res = []
            for c in node.named_children:
                m = self._map_node(c, source_bytes, scope)
                if isinstance(m, list): res.extend(m)
                elif m: res.append(m)
            return res

        elif node.type == 'assignment':
            left_node = node.named_children[0]
            right_node = node.named_children[-1]
            return self._create_node(AssignmentNode, 
                left=self._map_node(left_node, source_bytes, scope),
                right=self._map_node(right_node, source_bytes, scope)
            )

        elif node.type in ('additive_expression', 'multiplicative_expression', 'equality_expression'):
            left_node = node.named_children[0]
            right_node = node.named_children[-1]
            
            op_text = source_bytes[left_node.end_byte:right_node.start_byte].decode("utf-8").strip()
            
            return self._create_node(BinaryOpNode, 
                left=self._map_node(left_node, source_bytes, scope),
                operator=op_text,
                right=self._map_node(right_node, source_bytes, scope)
            )

        elif node.type == 'call_expression':
            func_node = node.named_children[0]
            func_ast = self._map_node(func_node, source_bytes, scope)
            
            call_suffix = next((c for c in node.named_children if c.type == 'call_suffix'), None)
            args = []
            if call_suffix:
                val_args = next((c for c in call_suffix.named_children if c.type == 'value_arguments'), None)
                if val_args:
                    for arg in val_args.named_children:
                        if arg.type == 'value_argument':
                            arg_val = arg.named_children[-1] if arg.named_children else arg
                            args.append(self._map_node(arg_val, source_bytes, scope))
                        else:
                            args.append(self._map_node(arg, source_bytes, scope))
                            
            return self._create_node(CallNode, func_name=func_ast, args=args)

        elif node.type == 'if_statement':
            cond_node = next((c for c in node.named_children if 'expression' in c.type or c.type == 'simple_identifier'), None)
            
            cond_ast = self._map_node(cond_node, source_bytes, scope) if cond_node else self._create_node(LiteralNode, value=True)
                
            statements_nodes = [c for c in node.named_children if c.type == 'statements']
            body = []
            if len(statements_nodes) > 0:
                conseq_node = statements_nodes[0]
                for c in conseq_node.named_children:
                    m = self._map_node(c, source_bytes, scope)
                    if isinstance(m, list): body.extend(m)
                    elif m: body.append(m)
                    
            orelse = None
            if len(statements_nodes) > 1:
                alt_node = statements_nodes[1]
                obody = []
                for c in alt_node.named_children:
                    m = self._map_node(c, source_bytes, scope)
                    if isinstance(m, list): obody.extend(m)
                    elif m: obody.append(m)
                orelse = self._create_node(IfNode, condition=self._create_node(LiteralNode, value=True), body=obody, orelse=None)
            
            return self._create_node(IfNode, condition=cond_ast, body=body, orelse=orelse)

        elif node.type == 'for_statement':
            pattern_node = next((c for c in node.named_children if c.type == 'pattern'), None)
            target_name = self._get_pattern_name(pattern_node, source_bytes)
            target_ast = self._create_node(IdentifierNode, name=target_name)
            
            range_node = next((c for c in node.named_children if c.type == 'range_expression' or c.type == 'simple_identifier'), None)
            iter_ast = self._map_node(range_node, source_bytes, scope)
            
            body_node = next((c for c in node.named_children if c.type == 'statements'), None)
            body = []
            if body_node:
                for c in body_node.named_children:
                    m = self._map_node(c, source_bytes, scope)
                    if isinstance(m, list): body.extend(m)
                    elif m: body.append(m)
                    
            return self._create_node(ForNode, target=target_ast, iter=iter_ast, body=body)

        elif node.type == 'while_statement':
            cond_node = next((c for c in node.named_children if 'expression' in c.type or c.type == 'simple_identifier'), None)
            cond_ast = self._map_node(cond_node, source_bytes, scope) if cond_node else self._create_node(LiteralNode, value=True)
            
            body_node = next((c for c in node.named_children if c.type == 'statements'), None)
            body = []
            if body_node:
                for c in body_node.named_children:
                    m = self._map_node(c, source_bytes, scope)
                    if isinstance(m, list): body.extend(m)
                    elif m: body.append(m)
                    
            return self._create_node(WhileNode, condition=cond_ast, body=body)

        elif node.type == 'do_statement':
            body_node = next((c for c in node.named_children if c.type == 'statements'), None)
            body = []
            if body_node:
                for c in body_node.named_children:
                    m = self._map_node(c, source_bytes, scope)
                    if isinstance(m, list): body.extend(m)
                    elif m: body.append(m)
                    
            handlers = []
            catch_node = next((c for c in node.named_children if c.type == 'catch_block'), None)
            if catch_node:
                cb_statements = next((c for c in catch_node.named_children if c.type == 'statements'), None)
                if cb_statements:
                    for c in cb_statements.named_children:
                        m = self._map_node(c, source_bytes, scope)
                        if isinstance(m, list): handlers.extend(m)
                        elif m: handlers.append(m)
                            
            return self._create_node(TryCatchNode, body=body, handlers=handlers)

        elif node.type == 'control_transfer_statement':
            # Swift's return or throw usually inside control_transfer_statement
            text = self._get_text(node, source_bytes)
            if text.startswith('return'):
                val_node = next((c for c in node.named_children), None)
                val_ast = self._map_node(val_node, source_bytes, scope) if val_node else None
                return self._create_node(ReturnNode, value=val_ast)
            elif text.startswith('throw'):
                val_node = next((c for c in node.named_children), None)
                args = []
                if val_node:
                    args.append(self._map_node(val_node, source_bytes, scope))
                return self._create_node(CallNode, func_name=self._create_node(IdentifierNode, name="throw"), args=args)
                
            return None

        elif node.type == 'directly_assignable_expression' or node.type == 'navigation_expression':
            if len(node.named_children) == 1:
                return self._map_node(node.named_children[0], source_bytes, scope)
            if len(node.named_children) == 2:
                obj_ast = self._map_node(node.named_children[0], source_bytes, scope)
                suffix_node = node.named_children[1] # navigation_suffix
                field_node = next((c for c in suffix_node.named_children if c.type == 'simple_identifier'), None)
                field_name = self._get_text(field_node, source_bytes) if field_node else ""
                return self._create_node(AttributeNode, value=obj_ast, attr=field_name)

        elif node.type == 'simple_identifier':
            return self._create_node(IdentifierNode, name=self._get_text(node, source_bytes))

        elif node.type == 'self_expression':
            return self._create_node(IdentifierNode, name="self")

        elif node.type == 'integer_literal' or node.type == 'real_literal':
            text = self._get_text(node, source_bytes)
            if '.' in text or 'e' in text.lower():
                return self._create_node(LiteralNode, value=float(text), metadata={"type": "Double"})
            return self._create_node(LiteralNode, value=int(text), metadata={"type": "Int"})

        elif node.type == 'boolean_literal':
            text = self._get_text(node, source_bytes)
            return self._create_node(LiteralNode, value=(text == 'true'), metadata={"type": "Bool"})

        elif node.type == 'line_string_literal':
            text_node = next((c for c in node.named_children if c.type == 'line_str_text'), None)
            text = self._get_text(text_node, source_bytes) if text_node else ""
            return self._create_node(LiteralNode, value=text, metadata={"type": "String"})

        elif node.type == 'nil_literal':
            return self._create_node(LiteralNode, value=None)
            
        elif node.type == 'range_expression':
            args = []
            for c in node.named_children:
                args.append(self._map_node(c, source_bytes, scope))
            return self._create_node(CallNode, func_name=self._create_node(IdentifierNode, name="range"), args=args)

        return None
