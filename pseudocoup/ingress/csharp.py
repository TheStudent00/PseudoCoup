import tree_sitter_c_sharp as tscsharp
from tree_sitter import Parser, Language, Node
from pseudocoup.core.ur_ast import (
    URNode, ModuleNode, FunctionDefNode, MethodDefNode, ClassDefNode, AssignmentNode,
    BinaryOpNode, CallNode, IdentifierNode, LiteralNode,
    ReturnNode, IfNode, WhileNode, ForNode, TryCatchNode, ListNode,
    DictNode, SubscriptNode, AttributeNode
)
from pseudocoup.core.ledger import Ledger

class CSharpIngestor:
    def __init__(self, ledger: Ledger):
        self.ledger = ledger
        self.parser = Parser()
        try:
            lang = Language(tscsharp.language(), "c_sharp")
            self.parser.set_language(lang)
        except Exception:
            lang = Language(tscsharp.language())
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
        
    def _get_type_text(self, node: Node, source_bytes: bytes) -> str:
        return self._get_text(node, source_bytes)

    def _map_node(self, node: Node, source_bytes: bytes, scope: str):
        if not node or not node.is_named:
            return None

        if node.type == 'compilation_unit':
            body = []
            for child in node.named_children:
                mapped = self._map_node(child, source_bytes, scope)
                if mapped:
                    if isinstance(mapped, list): body.extend(mapped)
                    else: body.append(mapped)
            return self._create_node(ModuleNode, body=body, metadata={"type": "compilation_unit"})

        elif node.type == 'class_declaration':
            name_node = node.child_by_field_name('name')
            if not name_node:
                for c in node.named_children:
                    if c.type == 'identifier':
                        name_node = c
                        break
            
            name = self._get_text(name_node, source_bytes) if name_node else "UnknownClass"
            new_scope = f"{scope}.{name}" if scope else name
            
            fields = []
            methods = []
            
            body_node = node.child_by_field_name('body') or next((c for c in node.named_children if c.type == 'declaration_list'), None)
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

        elif node.type == 'field_declaration':
            var_decl = next((c for c in node.named_children if c.type == 'variable_declaration'), None)
            if not var_decl: return None
            return self._map_node(var_decl, source_bytes, scope)

        elif node.type == 'local_declaration_statement':
            var_decl = next((c for c in node.named_children if c.type == 'variable_declaration'), None)
            if not var_decl: return None
            return self._map_node(var_decl, source_bytes, scope)

        elif node.type == 'variable_declaration':
            type_node = node.child_by_field_name('type') if hasattr(node, 'child_by_field_name') else next((c for c in node.named_children if c.type in ('predefined_type', 'identifier', 'array_type')), None)
            var_type = self._get_type_text(type_node, source_bytes) if type_node else "Any"
            
            declarators = [c for c in node.named_children if c.type == 'variable_declarator']
            assignments = []
            
            for declarator in declarators:
                name_node = declarator.child_by_field_name('name') or next((c for c in declarator.named_children if c.type == 'identifier'), None)
                name = self._get_text(name_node, source_bytes) if name_node else "unknown"
                
                self.ledger.register_type(scope, name, var_type)
                
                val_node = declarator.child_by_field_name('value') 
                if not val_node:
                    # In C#, equals_value_clause or directly child
                    equals = next((c for c in declarator.named_children if c.type == 'equals_value_clause'), None)
                    if equals:
                        val_node = equals.named_children[-1] if equals.named_children else None
                    else:
                        val_node = declarator.named_children[-1] if len(declarator.named_children) > 1 else None
                
                left = self._create_node(IdentifierNode, name=name, metadata={"type": var_type})
                right = self._map_node(val_node, source_bytes, scope) if val_node else None
                
                assignments.append(self._create_node(AssignmentNode, left=left, right=right))
                
            if len(assignments) == 1:
                return assignments[0]
            return assignments

        elif node.type == 'method_declaration':
            name_node = node.child_by_field_name('name') or next((c for c in node.named_children if c.type == 'identifier'), None)
            name = self._get_text(name_node, source_bytes) if name_node else "unknown"
            
            type_node = node.child_by_field_name('type') or next((c for c in node.named_children if c.type in ('predefined_type', 'identifier', 'array_type') and c != name_node), None)
            ret_type = self._get_type_text(type_node, source_bytes) if type_node else "void"
            
            self.ledger.register_type(scope, name, ret_type)
            fqdn = f"{scope}.{name}" if scope else name
            
            params = node.child_by_field_name('parameters') or next((c for c in node.named_children if c.type == 'parameter_list'), None)
            args = []
            if params:
                for param in params.named_children:
                    if param.type == 'parameter':
                        p_type_node = param.child_by_field_name('type') or next((c for c in param.named_children if c.type in ('predefined_type', 'identifier', 'array_type')), None)
                        p_name_node = param.child_by_field_name('name') or next((c for c in param.named_children if c.type == 'identifier'), None)
                        if p_name_node:
                            p_name = self._get_text(p_name_node, source_bytes)
                            p_type = self._get_type_text(p_type_node, source_bytes) if p_type_node else "Any"
                            self.ledger.register_type(fqdn, p_name, p_type)
                            args.append(self._create_node(IdentifierNode, name=p_name, metadata={"type": p_type}))
            
            body_node = node.child_by_field_name('body') or next((c for c in node.named_children if c.type == 'block'), None)
            body = []
            if body_node:
                for child in body_node.named_children:
                    mapped = self._map_node(child, source_bytes, fqdn)
                    if mapped:
                        if isinstance(mapped, list): body.extend(mapped)
                        else: body.append(mapped)
                        
            return self._create_node(MethodDefNode, name=name, args=args, body=body, metadata={"type": ret_type})

        elif node.type == 'constructor_declaration':
            name = "__init__"
            
            self.ledger.register_type(scope, name, "void")
            fqdn = f"{scope}.{name}" if scope else name
            
            params = node.child_by_field_name('parameters') or next((c for c in node.named_children if c.type == 'parameter_list'), None)
            args = []
            if params:
                for param in params.named_children:
                    if param.type == 'parameter':
                        p_type_node = param.child_by_field_name('type') or next((c for c in param.named_children if c.type in ('predefined_type', 'identifier', 'array_type')), None)
                        p_name_node = param.child_by_field_name('name') or next((c for c in param.named_children if c.type == 'identifier'), None)
                        if p_name_node:
                            p_name = self._get_text(p_name_node, source_bytes)
                            p_type = self._get_type_text(p_type_node, source_bytes) if p_type_node else "Any"
                            self.ledger.register_type(fqdn, p_name, p_type)
                            args.append(self._create_node(IdentifierNode, name=p_name, metadata={"type": p_type}))
                            
            body_node = node.child_by_field_name('body') or next((c for c in node.named_children if c.type == 'block'), None)
            body = []
            if body_node:
                for child in body_node.named_children:
                    mapped = self._map_node(child, source_bytes, fqdn)
                    if mapped:
                        if isinstance(mapped, list): body.extend(mapped)
                        else: body.append(mapped)
                        
            return self._create_node(MethodDefNode, name=name, args=args, body=body, metadata={"type": "void"})

        elif node.type == 'expression_statement':
            if node.named_children:
                return self._map_node(node.named_children[0], source_bytes, scope)
            return None

        elif node.type == 'assignment_expression':
            left_node = node.child_by_field_name('left') or node.named_children[0]
            right_node = node.child_by_field_name('right') or node.named_children[-1]
            return self._create_node(AssignmentNode, 
                left=self._map_node(left_node, source_bytes, scope),
                right=self._map_node(right_node, source_bytes, scope)
            )

        elif node.type == 'binary_expression':
            left_node = node.child_by_field_name('left') or node.named_children[0]
            right_node = node.child_by_field_name('right') or node.named_children[-1]
            
            # Extract operator by text between left and right nodes
            op_text = source_bytes[left_node.end_byte:right_node.start_byte].decode("utf-8").strip()
            
            return self._create_node(BinaryOpNode, 
                left=self._map_node(left_node, source_bytes, scope),
                operator=op_text,
                right=self._map_node(right_node, source_bytes, scope)
            )

        elif node.type == 'invocation_expression':
            func_node = node.child_by_field_name('function') or node.named_children[0]
            
            func_ast = self._map_node(func_node, source_bytes, scope)
            
            args_node = node.child_by_field_name('arguments') or next((c for c in node.named_children if c.type == 'argument_list'), None)
            args = []
            if args_node:
                for arg in args_node.named_children:
                    args.append(self._map_node(arg, source_bytes, scope))
                    
            return self._create_node(CallNode, func_name=func_ast, args=args)

        elif node.type == 'if_statement':
            cond_node = node.child_by_field_name('condition') or next((c for c in node.named_children if c.type != 'block'), None)
            
            # in C#, condition could be parenthesized. The C# parser typically drops parens or keeps them as condition.
            if cond_node and cond_node.type == 'parenthesized_expression' and cond_node.named_children:
                cond_ast = self._map_node(cond_node.named_children[0], source_bytes, scope)
            else:
                cond_ast = self._map_node(cond_node, source_bytes, scope)
                
            conseq_node = node.child_by_field_name('consequence') 
            alt_node = node.child_by_field_name('alternative')
            
            # Fallback if names not present (e.g. older tree-sitter)
            if not conseq_node:
                blocks = [c for c in node.named_children if c.type == 'block']
                if blocks:
                    conseq_node = blocks[0]
                if len(blocks) > 1:
                    alt_node = blocks[1]
                
            body = []
            if conseq_node:
                if conseq_node.type == 'block':
                    for c in conseq_node.named_children:
                        m = self._map_node(c, source_bytes, scope)
                        if isinstance(m, list): body.extend(m)
                        elif m: body.append(m)
                else:
                    m = self._map_node(conseq_node, source_bytes, scope)
                    if isinstance(m, list): body.extend(m)
                    elif m: body.append(m)
                    
            orelse = None
            if alt_node:
                if alt_node.type == 'else_clause':
                    alt_block = next((c for c in alt_node.named_children), None)
                    if alt_block: alt_node = alt_block
                    
                if alt_node.type == 'block':
                    obody = []
                    for c in alt_node.named_children:
                        m = self._map_node(c, source_bytes, scope)
                        if isinstance(m, list): obody.extend(m)
                        elif m: obody.append(m)
                    orelse = self._create_node(IfNode, condition=self._create_node(LiteralNode, value=True), body=obody, orelse=None)
                else:
                    orelse = self._map_node(alt_node, source_bytes, scope)
                    
            return self._create_node(IfNode, condition=cond_ast, body=body, orelse=orelse)

        elif node.type == 'for_statement':
            init_node = node.child_by_field_name('initializer')
            cond_node = node.child_by_field_name('condition')
            update_node = node.child_by_field_name('update')
            body_node = node.child_by_field_name('body')
            
            if not init_node: init_node = next((c for c in node.named_children if c.type == 'variable_declaration'), None)
            if not cond_node: cond_node = next((c for c in node.named_children if c.type == 'binary_expression'), None)
            if not update_node: update_node = next((c for c in node.named_children if c.type == 'assignment_expression'), None)
            if not body_node: body_node = next((c for c in node.named_children if c.type == 'block'), None)
            
            init_ast = self._map_node(init_node, source_bytes, scope) if init_node else None
            cond_ast = self._map_node(cond_node, source_bytes, scope) if cond_node else self._create_node(LiteralNode, value=True)
            update_ast = self._map_node(update_node, source_bytes, scope) if update_node else None
            
            body = []
            if body_node:
                if body_node.type == 'block':
                    for c in body_node.named_children:
                        m = self._map_node(c, source_bytes, scope)
                        if isinstance(m, list): body.extend(m)
                        elif m: body.append(m)
                else:
                    m = self._map_node(body_node, source_bytes, scope)
                    if isinstance(m, list): body.extend(m)
                    elif m: body.append(m)
                    
            if update_ast:
                body.append(update_ast)
                
            while_ast = self._create_node(WhileNode, condition=cond_ast, body=body)
            
            if init_ast:
                if isinstance(init_ast, list):
                    return init_ast + [while_ast]
                else:
                    return [init_ast, while_ast]
            return while_ast

        elif node.type == 'foreach_statement':
            type_node = node.child_by_field_name('type')
            name_node = node.child_by_field_name('left') or next((c for c in node.named_children if c.type == 'identifier'), None) 
            
            value_node = node.child_by_field_name('right') or next((c for c in node.named_children if c != name_node and c != type_node and c.type != 'block'), None)
            body_node = node.child_by_field_name('body') or next((c for c in node.named_children if c.type == 'block'), None)
            
            target_name = self._get_text(name_node, source_bytes) if name_node else "unknown"
            
            target_ast = self._create_node(IdentifierNode, name=target_name)
            iter_ast = self._map_node(value_node, source_bytes, scope) if value_node else None
            
            body = []
            if body_node:
                if body_node.type == 'block':
                    for c in body_node.named_children:
                        m = self._map_node(c, source_bytes, scope)
                        if isinstance(m, list): body.extend(m)
                        elif m: body.append(m)
                else:
                    m = self._map_node(body_node, source_bytes, scope)
                    if isinstance(m, list): body.extend(m)
                    elif m: body.append(m)
                    
            return self._create_node(ForNode, target=target_ast, iter=iter_ast, body=body)

        elif node.type == 'try_statement':
            body_node = node.child_by_field_name('body') or next((c for c in node.named_children if c.type == 'block'), None)
            
            body = []
            if body_node:
                for c in body_node.named_children:
                    m = self._map_node(c, source_bytes, scope)
                    if isinstance(m, list): body.extend(m)
                    elif m: body.append(m)
                    
            handlers = []
            for child in node.named_children:
                if child.type == 'catch_clause':
                    cb_node = child.child_by_field_name('body') or next((c for c in child.named_children if c.type == 'block'), None)
                    if cb_node:
                        for c in cb_node.named_children:
                            m = self._map_node(c, source_bytes, scope)
                            if isinstance(m, list): handlers.extend(m)
                            elif m: handlers.append(m)
                            
            return self._create_node(TryCatchNode, body=body, handlers=handlers)

        elif node.type == 'throw_statement':
            val_node = next((c for c in node.named_children), None)
            args = []
            if val_node:
                args.append(self._map_node(val_node, source_bytes, scope))
            return self._create_node(CallNode, func_name=self._create_node(IdentifierNode, name="throw"), args=args)

        elif node.type == 'return_statement':
            val_node = next((c for c in node.named_children), None)
            val_ast = self._map_node(val_node, source_bytes, scope) if val_node else None
            return self._create_node(ReturnNode, value=val_ast)

        elif node.type == 'identifier':
            return self._create_node(IdentifierNode, name=self._get_text(node, source_bytes))

        elif node.type == 'this_expression':
            return self._create_node(IdentifierNode, name="this")

        elif node.type in ('integer_literal'):
            text = self._get_text(node, source_bytes)
            return self._create_node(LiteralNode, value=int(text), metadata={"type": "int"})

        elif node.type in ('real_literal'):
            text = self._get_text(node, source_bytes).rstrip('fFdDmM')
            return self._create_node(LiteralNode, value=float(text), metadata={"type": "float"})

        elif node.type == 'boolean_literal':
            text = self._get_text(node, source_bytes)
            return self._create_node(LiteralNode, value=(text == 'true'), metadata={"type": "bool"})

        elif node.type == 'string_literal':
            text = self._get_text(node, source_bytes)
            if text.startswith('"') and text.endswith('"'):
                text = text[1:-1]
            return self._create_node(LiteralNode, value=text, metadata={"type": "str"})
            
        elif node.type == 'null_literal':
            return self._create_node(LiteralNode, value=None)

        elif node.type == 'member_access_expression':
            obj_node = node.child_by_field_name('expression') or node.named_children[0]
            field_node = node.child_by_field_name('name') or node.named_children[-1]
            
            obj_ast = self._map_node(obj_node, source_bytes, scope)
            field_name = self._get_text(field_node, source_bytes)
            
            return self._create_node(AttributeNode, value=obj_ast, attr=field_name)

        elif node.type == 'parenthesized_expression':
            if node.named_children:
                return self._map_node(node.named_children[0], source_bytes, scope)
            return None
            
        elif node.type == 'argument':
            if node.named_children:
                return self._map_node(node.named_children[-1], source_bytes, scope)
            return None

        elif node.type == 'object_creation_expression':
            type_node = node.child_by_field_name('type') or node.named_children[0]
            args_node = node.child_by_field_name('arguments') or next((c for c in node.named_children if c.type == 'argument_list'), None)
            
            func_name = self._get_text(type_node, source_bytes) if type_node else "unknown"
            
            args = []
            if args_node:
                for arg in args_node.named_children:
                    args.append(self._map_node(arg, source_bytes, scope))
                    
            return self._create_node(CallNode, func_name=self._create_node(IdentifierNode, name=func_name), args=args)

        if node.type == 'block':
            res = []
            for c in node.named_children:
                m = self._map_node(c, source_bytes, scope)
                if isinstance(m, list): res.extend(m)
                elif m: res.append(m)
            return res

        return None
