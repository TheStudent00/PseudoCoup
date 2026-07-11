import tree_sitter_typescript as ts
from tree_sitter import Parser, Language, Node
from pseudocoup.core.ur_ast import (
    URNode, ModuleNode, FunctionDefNode, MethodDefNode, ClassDefNode, AssignmentNode,
    BinaryOpNode, CallNode, IdentifierNode, LiteralNode,
    ReturnNode, IfNode, WhileNode, ForNode, TryCatchNode, ListNode,
    DictNode, SubscriptNode, AttributeNode
)
from pseudocoup.core.ledger import Ledger

class TypeScriptIngestor:
    def __init__(self, ledger: Ledger):
        self.ledger = ledger
        self.parser = Parser()
        try:
            lang = Language(ts.language_typescript(), "typescript")
            self.parser.set_language(lang)
        except Exception:
            lang = Language(ts.language_typescript())
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
        type_ann = next((c for c in node.named_children if c.type == 'type_annotation'), None)
        if not type_ann: return "Any"
        # The child of type_annotation is the actual type string
        if type_ann.named_children:
            return self._get_text(type_ann.named_children[0], source_bytes)
        return "Any"

    def _map_node(self, node: Node, source_bytes: bytes, scope: str):
        if not node or not node.is_named:
            return None

        if node.type == 'program':
            body = []
            for child in node.named_children:
                mapped = self._map_node(child, source_bytes, scope)
                if mapped:
                    if isinstance(mapped, list): body.extend(mapped)
                    else: body.append(mapped)
            return self._create_node(ModuleNode, body=body, metadata={"type": "program"})

        elif node.type == 'class_declaration':
            name_node = node.child_by_field_name('name') or next((c for c in node.named_children if c.type == 'type_identifier' or c.type == 'identifier'), None)
            name = self._get_text(name_node, source_bytes) if name_node else "UnknownClass"
            new_scope = f"{scope}.{name}" if scope else name
            
            fields = []
            methods = []
            
            body_node = node.child_by_field_name('body') or next((c for c in node.named_children if c.type == 'class_body'), None)
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

        elif node.type == 'public_field_definition':
            name_node = node.child_by_field_name('name') or next((c for c in node.named_children if c.type == 'property_identifier'), None)
            name = self._get_text(name_node, source_bytes) if name_node else "unknown"
            
            var_type = self._extract_type_annotation(node, source_bytes)
            self.ledger.register_type(scope, name, var_type)
            
            val_node = node.child_by_field_name('value')
            
            left = self._create_node(IdentifierNode, name=name, metadata={"type": var_type})
            right = self._map_node(val_node, source_bytes, scope) if val_node else None
            
            return self._create_node(AssignmentNode, left=left, right=right)

        elif node.type in ('lexical_declaration', 'variable_declaration'):
            assignments = []
            for declarator in node.named_children:
                if declarator.type != 'variable_declarator': continue
                
                name_node = declarator.child_by_field_name('name') or next((c for c in declarator.named_children if c.type == 'identifier'), None)
                name = self._get_text(name_node, source_bytes) if name_node else "unknown"
                
                var_type = self._extract_type_annotation(declarator, source_bytes)
                self.ledger.register_type(scope, name, var_type)
                
                val_node = declarator.child_by_field_name('value')
                if not val_node and declarator.named_children:
                    # value might just be the last child if it's an assignment
                    last = declarator.named_children[-1]
                    if last != name_node and last.type != 'type_annotation':
                        val_node = last
                
                left = self._create_node(IdentifierNode, name=name, metadata={"type": var_type})
                right = self._map_node(val_node, source_bytes, scope) if val_node else None
                
                assignments.append(self._create_node(AssignmentNode, left=left, right=right))
                
            if len(assignments) == 1:
                return assignments[0]
            return assignments

        elif node.type == 'method_definition':
            name_node = node.child_by_field_name('name') or next((c for c in node.named_children if c.type == 'property_identifier'), None)
            name = self._get_text(name_node, source_bytes) if name_node else "unknown"
            
            is_constructor = (name == 'constructor')
            meth_name = "__init__" if is_constructor else name
            
            ret_type = self._extract_type_annotation(node, source_bytes)
            if is_constructor: ret_type = "void"
            
            self.ledger.register_type(scope, meth_name, ret_type)
            fqdn = f"{scope}.{meth_name}" if scope else meth_name
            
            params = node.child_by_field_name('parameters') or next((c for c in node.named_children if c.type == 'formal_parameters'), None)
            args = []
            if params:
                for param in params.named_children:
                    if param.type in ('required_parameter', 'optional_parameter'):
                        p_name_node = next((c for c in param.named_children if c.type == 'identifier'), None)
                        if p_name_node:
                            p_name = self._get_text(p_name_node, source_bytes)
                            p_type = self._extract_type_annotation(param, source_bytes)
                            self.ledger.register_type(fqdn, p_name, p_type)
                            args.append(self._create_node(IdentifierNode, name=p_name, metadata={"type": p_type}))
            
            body_node = node.child_by_field_name('body') or next((c for c in node.named_children if c.type == 'statement_block'), None)
            body = []
            if body_node:
                for child in body_node.named_children:
                    mapped = self._map_node(child, source_bytes, fqdn)
                    if mapped:
                        if isinstance(mapped, list): body.extend(mapped)
                        else: body.append(mapped)
                        
            return self._create_node(MethodDefNode, name=meth_name, args=args, body=body, metadata={"type": ret_type})

        elif node.type == 'function_declaration':
            name_node = node.child_by_field_name('name') or next((c for c in node.named_children if c.type == 'identifier'), None)
            name = self._get_text(name_node, source_bytes) if name_node else "unknown"
            
            ret_type = self._extract_type_annotation(node, source_bytes)
            
            self.ledger.register_type(scope, name, ret_type)
            fqdn = f"{scope}.{name}" if scope else name
            
            params = node.child_by_field_name('parameters') or next((c for c in node.named_children if c.type == 'formal_parameters'), None)
            args = []
            if params:
                for param in params.named_children:
                    if param.type in ('required_parameter', 'optional_parameter'):
                        p_name_node = next((c for c in param.named_children if c.type == 'identifier'), None)
                        if p_name_node:
                            p_name = self._get_text(p_name_node, source_bytes)
                            p_type = self._extract_type_annotation(param, source_bytes)
                            self.ledger.register_type(fqdn, p_name, p_type)
                            args.append(self._create_node(IdentifierNode, name=p_name, metadata={"type": p_type}))
            
            body_node = node.child_by_field_name('body') or next((c for c in node.named_children if c.type == 'statement_block'), None)
            body = []
            if body_node:
                for child in body_node.named_children:
                    mapped = self._map_node(child, source_bytes, fqdn)
                    if mapped:
                        if isinstance(mapped, list): body.extend(mapped)
                        else: body.append(mapped)
                        
            return self._create_node(FunctionDefNode, name=name, args=args, body=body, metadata={"type": ret_type})

        elif node.type == 'expression_statement':
            if node.named_children:
                return self._map_node(node.named_children[0], source_bytes, scope)
            return None

        elif node.type == 'assignment_expression':
            left_node = node.named_children[0]
            right_node = node.named_children[-1]
            return self._create_node(AssignmentNode, 
                left=self._map_node(left_node, source_bytes, scope),
                right=self._map_node(right_node, source_bytes, scope)
            )

        elif node.type == 'binary_expression':
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
            
            args_node = node.child_by_field_name('arguments') or next((c for c in node.named_children if c.type == 'arguments'), None)
            args = []
            if args_node:
                for arg in args_node.named_children:
                    args.append(self._map_node(arg, source_bytes, scope))
                    
            return self._create_node(CallNode, func_name=func_ast, args=args)

        elif node.type == 'if_statement':
            cond_node = node.child_by_field_name('condition') or next((c for c in node.named_children if c.type == 'parenthesized_expression'), None)
            
            if cond_node and cond_node.named_children:
                cond_ast = self._map_node(cond_node.named_children[0], source_bytes, scope)
            else:
                cond_ast = self._map_node(cond_node, source_bytes, scope) if cond_node else self._create_node(LiteralNode, value=True)
                
            conseq_node = node.child_by_field_name('consequence') 
            alt_node = node.child_by_field_name('alternative')
            
            if not conseq_node:
                blocks = [c for c in node.named_children if c.type == 'statement_block']
                if blocks:
                    conseq_node = blocks[0]
                
            body = []
            if conseq_node:
                if conseq_node.type == 'statement_block':
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
                    
                if alt_node.type == 'statement_block':
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
            body_node = node.child_by_field_name('body')
            update_node = None
            
            children = node.named_children
            if not init_node and len(children) > 0: init_node = children[0]
            if not cond_node and len(children) > 1: cond_node = children[1]
            if not update_node and len(children) > 2:
                # the 3rd might be the update expression, or the body if there is no update
                if children[2].type != 'statement_block':
                    update_node = children[2]
            if not body_node: body_node = next((c for c in children if c.type == 'statement_block'), None)
            
            init_ast = self._map_node(init_node, source_bytes, scope) if init_node else None
            cond_ast = self._map_node(cond_node, source_bytes, scope) if cond_node else self._create_node(LiteralNode, value=True)
            update_ast = self._map_node(update_node, source_bytes, scope) if update_node else None
            
            body = []
            if body_node:
                if body_node.type == 'statement_block':
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

        elif node.type in ('for_in_statement', 'for_of_statement'):
            name_node = node.child_by_field_name('left') or next((c for c in node.named_children if c.type in ('identifier', 'lexical_declaration', 'variable_declaration')), None)
            value_node = node.child_by_field_name('right') or next((c for c in node.named_children if c != name_node and c.type != 'statement_block'), None)
            body_node = node.child_by_field_name('body') or next((c for c in node.named_children if c.type == 'statement_block'), None)
            
            target_name = "unknown"
            if name_node:
                if name_node.type in ('lexical_declaration', 'variable_declaration'):
                    decl = next((c for c in name_node.named_children if c.type == 'variable_declarator'), None)
                    if decl:
                        id_node = decl.child_by_field_name('name') or next((c for c in decl.named_children if c.type == 'identifier'), None)
                        if id_node: target_name = self._get_text(id_node, source_bytes)
                else:
                    target_name = self._get_text(name_node, source_bytes)
            
            target_ast = self._create_node(IdentifierNode, name=target_name)
            iter_ast = self._map_node(value_node, source_bytes, scope) if value_node else None
            
            body = []
            if body_node:
                if body_node.type == 'statement_block':
                    for c in body_node.named_children:
                        m = self._map_node(c, source_bytes, scope)
                        if isinstance(m, list): body.extend(m)
                        elif m: body.append(m)
                else:
                    m = self._map_node(body_node, source_bytes, scope)
                    if isinstance(m, list): body.extend(m)
                    elif m: body.append(m)
                    
            return self._create_node(ForNode, target=target_ast, iter=iter_ast, body=body)

        elif node.type == 'while_statement':
            cond_node = node.child_by_field_name('condition') or next((c for c in node.named_children if c.type == 'parenthesized_expression'), None)
            body_node = node.child_by_field_name('body') or next((c for c in node.named_children if c.type == 'statement_block'), None)
            
            if cond_node and cond_node.named_children:
                cond_ast = self._map_node(cond_node.named_children[0], source_bytes, scope)
            else:
                cond_ast = self._map_node(cond_node, source_bytes, scope) if cond_node else self._create_node(LiteralNode, value=True)
                
            body = []
            if body_node:
                if body_node.type == 'statement_block':
                    for c in body_node.named_children:
                        m = self._map_node(c, source_bytes, scope)
                        if isinstance(m, list): body.extend(m)
                        elif m: body.append(m)
                else:
                    m = self._map_node(body_node, source_bytes, scope)
                    if isinstance(m, list): body.extend(m)
                    elif m: body.append(m)
                    
            return self._create_node(WhileNode, condition=cond_ast, body=body)

        elif node.type == 'try_statement':
            body_node = node.child_by_field_name('body') or next((c for c in node.named_children if c.type == 'statement_block'), None)
            
            body = []
            if body_node:
                for c in body_node.named_children:
                    m = self._map_node(c, source_bytes, scope)
                    if isinstance(m, list): body.extend(m)
                    elif m: body.append(m)
                    
            handlers = []
            for child in node.named_children:
                if child.type == 'catch_clause':
                    cb_node = child.child_by_field_name('body') or next((c for c in child.named_children if c.type == 'statement_block'), None)
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

        elif node.type == 'identifier' or node.type == 'property_identifier':
            return self._create_node(IdentifierNode, name=self._get_text(node, source_bytes))

        elif node.type == 'this':
            return self._create_node(IdentifierNode, name="this")

        elif node.type == 'number':
            text = self._get_text(node, source_bytes)
            if '.' in text or 'e' in text.lower():
                return self._create_node(LiteralNode, value=float(text), metadata={"type": "float"})
            return self._create_node(LiteralNode, value=int(text), metadata={"type": "int"})

        elif node.type in ('true', 'false'):
            text = self._get_text(node, source_bytes)
            return self._create_node(LiteralNode, value=(text == 'true'), metadata={"type": "bool"})

        elif node.type == 'string':
            text = self._get_text(node, source_bytes)
            if (text.startswith('"') and text.endswith('"')) or (text.startswith("'") and text.endswith("'")):
                text = text[1:-1]
            return self._create_node(LiteralNode, value=text, metadata={"type": "str"})
            
        elif node.type == 'null':
            return self._create_node(LiteralNode, value=None)

        elif node.type == 'member_expression':
            obj_node = node.named_children[0]
            field_node = node.named_children[-1]
            
            obj_ast = self._map_node(obj_node, source_bytes, scope)
            field_name = self._get_text(field_node, source_bytes)
            
            return self._create_node(AttributeNode, value=obj_ast, attr=field_name)

        elif node.type == 'parenthesized_expression':
            if node.named_children:
                return self._map_node(node.named_children[0], source_bytes, scope)
            return None
            
        elif node.type == 'arguments':
            # This is handled mostly in call_expression, but if traversed
            pass

        elif node.type == 'new_expression':
            type_node = node.named_children[0]
            args_node = node.child_by_field_name('arguments') or next((c for c in node.named_children if c.type == 'arguments'), None)
            
            func_name = self._get_text(type_node, source_bytes) if type_node else "unknown"
            
            args = []
            if args_node:
                for arg in args_node.named_children:
                    args.append(self._map_node(arg, source_bytes, scope))
                    
            return self._create_node(CallNode, func_name=self._create_node(IdentifierNode, name=func_name), args=args)

        if node.type == 'statement_block' or node.type == 'class_body':
            res = []
            for c in node.named_children:
                m = self._map_node(c, source_bytes, scope)
                if isinstance(m, list): res.extend(m)
                elif m: res.append(m)
            return res

        return None
