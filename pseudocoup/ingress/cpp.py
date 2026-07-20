import tree_sitter_cpp as ts
from tree_sitter import Parser, Language, Node
from pseudocoup.core.ur_ast import (
    URNode, ModuleNode, FunctionDefNode, MethodDefNode, ClassDefNode, AssignmentNode,
    BinaryOpNode, UnaryOpNode, CallNode, IdentifierNode, LiteralNode,
    ReturnNode, IfNode, WhileNode, ForNode, TryCatchNode, ListNode,
    DictNode, SubscriptNode, AttributeNode, CastNode
)
from pseudocoup.core.ledger import Ledger

class CppIngestor:
    def __init__(self, ledger: Ledger):
        self.ledger = ledger
        self.parser = Parser()
        try:
            lang = Language(ts.language(), "cpp")
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
        module_node = self._map_root(tree.root_node, source_bytes)
        if isinstance(module_node, list):
            return self._create_node(ModuleNode, body=module_node)
        return module_node if isinstance(module_node, ModuleNode) else self._create_node(ModuleNode, body=[module_node])

    def _get_text(self, node: Node, source_bytes: bytes) -> str:
        if not node: return ""
        return source_bytes[node.start_byte:node.end_byte].decode("utf-8")

    def _extract_type(self, node: Node, source_bytes: bytes) -> str:
        if not node: return "Any"
        type_node = node.child_by_field_name('type')
        if type_node:
            return self._get_text(type_node, source_bytes).strip()
        # Fallback to primitive_type, type_identifier, qualified_identifier, auto
        for c in node.named_children:
            if 'type' in c.type or c.type in ('auto', 'qualified_identifier'):
                return self._get_text(c, source_bytes).strip()
        return "Any"
        
    def _extract_name(self, node: Node, source_bytes: bytes) -> str:
        if not node: return "unknown"
        if node.type == 'identifier' or node.type == 'field_identifier':
            return self._get_text(node, source_bytes)
            
        decl = node.child_by_field_name('declarator')
        if decl:
            if decl.type == 'identifier' or decl.type == 'field_identifier':
                return self._get_text(decl, source_bytes)
            # e.g., init_declarator
            id_node = next((c for c in decl.named_children if c.type in ('identifier', 'field_identifier')), None)
            if id_node:
                return self._get_text(id_node, source_bytes)
        
        id_node = next((c for c in node.named_children if c.type in ('identifier', 'field_identifier')), None)
        if id_node:
            return self._get_text(id_node, source_bytes)
        return self._get_text(node, source_bytes)

    def _map_root(self, root: Node, source_bytes: bytes) -> ModuleNode:
        body = []
        for child in root.named_children:
            mapped = self._map_node(child, source_bytes, "")
            if mapped:
                if isinstance(mapped, list): body.extend(mapped)
                else: body.append(mapped)
        return self._create_node(ModuleNode, body=body)

    def _map_node(self, node: Node, source_bytes: bytes, scope: str):
        if not node or not node.is_named:
            return None

        if node.type == 'class_specifier':
            name_node = node.child_by_field_name('name')
            class_name = self._get_text(name_node, source_bytes) if name_node else "Unknown"
            
            fields = []
            methods = []
            
            body_node = node.child_by_field_name('body')
            if body_node:
                for c in body_node.named_children:
                    if c.type == 'field_declaration':
                        f_name = self._extract_name(c, source_bytes)
                        f_type = self._extract_type(c, source_bytes)
                        self.ledger.register_type(class_name, f_name, f_type)
                        left = self._create_node(IdentifierNode, name=f_name, metadata={"type": f_type})
                        fields.append(self._create_node(AssignmentNode, left=left, right=None))
                    elif c.type == 'function_definition':
                        mapped = self._map_node(c, source_bytes, class_name)
                        if mapped: methods.append(mapped)
                        
            return self._create_node(ClassDefNode, name=class_name, bases=[], fields=fields, methods=methods)

        elif node.type == 'function_definition':
            # Check for constructor
            type_node = node.child_by_field_name('type')
            decl_node = node.child_by_field_name('declarator')
            
            raw_name = "unknown"
            if decl_node:
                id_node = next((c for c in decl_node.named_children if c.type in ('identifier', 'field_identifier')), None)
                if id_node: raw_name = self._get_text(id_node, source_bytes)
                
            is_constructor = (not type_node and raw_name == scope and scope != "")
            meth_name = "__init__" if is_constructor else raw_name
            
            ret_type = self._get_text(type_node, source_bytes) if type_node else "Any"
            if is_constructor: ret_type = scope
            
            self.ledger.register_type(scope, meth_name, ret_type)
            fqdn = f"{scope}.{meth_name}" if scope else meth_name
            
            args = []
            if scope:
                # Inject self
                args.append(self._create_node(IdentifierNode, name="self"))
                
            param_list = None
            if decl_node:
                param_list = decl_node.child_by_field_name('parameters')
                if not param_list:
                    param_list = next((c for c in decl_node.named_children if c.type == 'parameter_list'), None)
                    
            if param_list:
                for param in param_list.named_children:
                    if param.type == 'parameter_declaration':
                        p_name = self._extract_name(param, source_bytes)
                        p_type = self._extract_type(param, source_bytes)
                        self.ledger.register_type(fqdn, p_name, p_type)
                        args.append(self._create_node(IdentifierNode, name=p_name, metadata={"type": p_type}))
                        
            body_node = node.child_by_field_name('body')
            body = []
            if body_node:
                for c in body_node.named_children:
                    m = self._map_node(c, source_bytes, fqdn)
                    if isinstance(m, list): body.extend(m)
                    elif m: body.append(m)
                        
            if scope:
                return self._create_node(MethodDefNode, name=meth_name, args=args, body=body, metadata={"type": ret_type})
            return self._create_node(FunctionDefNode, name=meth_name, args=args, body=body, metadata={"type": ret_type})

        elif node.type == 'declaration':
            # e.g., int a = 5;
            var_type = self._extract_type(node, source_bytes)
            decl_node = node.child_by_field_name('declarator')
            
            if not decl_node:
                # possibly multiple declarators or simple decl
                decl_node = next((c for c in node.named_children if c.type == 'init_declarator' or c.type == 'identifier'), None)
                
            if not decl_node: return None
            
            name = self._extract_name(decl_node, source_bytes)
            self.ledger.register_type(scope, name, var_type)
            
            left = self._create_node(IdentifierNode, name=name, metadata={"type": var_type})
            
            right_node = decl_node.child_by_field_name('value')
            if not right_node:
                # sometimes it's just the 2nd child in init_declarator
                if decl_node.type == 'init_declarator' and len(decl_node.named_children) > 1:
                    right_node = decl_node.named_children[1]
                    
            right = self._map_node(right_node, source_bytes, scope) if right_node else None
            return self._create_node(AssignmentNode, left=left, right=right)

        elif node.type == 'assignment_expression':
            left_node = node.child_by_field_name('left')
            right_node = node.child_by_field_name('right')
            return self._create_node(AssignmentNode, 
                left=self._map_node(left_node, source_bytes, scope),
                right=self._map_node(right_node, source_bytes, scope)
            )

        elif node.type == 'binary_expression':
            left_node = node.child_by_field_name('left')
            right_node = node.child_by_field_name('right')
            op_text = source_bytes[left_node.end_byte:right_node.start_byte].decode("utf-8").strip()
            
            # std::cout << "True\n";
            left_text = self._get_text(left_node, source_bytes)
            if op_text == '<<' and ("cout" in left_text or "cerr" in left_text):
                func_ast = self._create_node(IdentifierNode, name="print")
                arg_ast = self._map_node(right_node, source_bytes, scope)
                return self._create_node(CallNode, func_name=func_ast, args=[arg_ast])
            
            return self._create_node(BinaryOpNode, 
                left=self._map_node(left_node, source_bytes, scope),
                operator=op_text,
                right=self._map_node(right_node, source_bytes, scope)
            )

        elif node.type == 'unary_expression' or node.type == 'pointer_expression':
            arg_node = node.child_by_field_name('argument')
            if not arg_node and len(node.named_children) > 0:
                arg_node = node.named_children[0]
            op_text = source_bytes[node.start_byte:arg_node.start_byte].decode("utf-8").strip() if arg_node else ""
            if not op_text:
                op_text = source_bytes[node.start_byte:node.end_byte].decode("utf-8").strip()[0]
            return self._create_node(UnaryOpNode,
                operator=op_text,
                operand=self._map_node(arg_node, source_bytes, scope)
            )

        elif node.type == 'cast_expression':
            type_node = node.child_by_field_name('type')
            val_node = node.child_by_field_name('value')
            return self._create_node(CastNode,
                target_type=self._get_text(type_node, source_bytes),
                value=self._map_node(val_node, source_bytes, scope)
            )

        elif node.type == 'call_expression':
            func_node = node.child_by_field_name('function')
            func_ast = self._map_node(func_node, source_bytes, scope)
            
            args_node = node.child_by_field_name('arguments')
            args = []
            if args_node:
                for arg in args_node.named_children:
                    args.append(self._map_node(arg, source_bytes, scope))
                    
            return self._create_node(CallNode, func_name=func_ast, args=args)

        elif node.type == 'if_statement':
            cond_clause = node.child_by_field_name('condition')
            cond_node = None
            if cond_clause:
                cond_node = cond_clause.child_by_field_name('value')
                if not cond_node and len(cond_clause.named_children) > 0:
                    cond_node = cond_clause.named_children[0]
            
            cond_ast = self._map_node(cond_node, source_bytes, scope) if cond_node else self._create_node(LiteralNode, value=True)
                
            conseq_node = node.child_by_field_name('consequence')
            body = []
            if conseq_node:
                if conseq_node.type == 'compound_statement':
                    for c in conseq_node.named_children:
                        m = self._map_node(c, source_bytes, scope)
                        if isinstance(m, list): body.extend(m)
                        elif m: body.append(m)
                else:
                    m = self._map_node(conseq_node, source_bytes, scope)
                    if isinstance(m, list): body.extend(m)
                    elif m: body.append(m)
                    
            alt_node = node.child_by_field_name('alternative')
            orelse = None
            if alt_node:
                obody = []
                if alt_node.type == 'else_clause':
                    alt_body = alt_node.named_children[0] if len(alt_node.named_children) > 0 else None
                    if alt_body and alt_body.type == 'if_statement':
                        orelse = self._map_node(alt_body, source_bytes, scope)
                    elif alt_body and alt_body.type == 'compound_statement':
                        for c in alt_body.named_children:
                            m = self._map_node(c, source_bytes, scope)
                            if isinstance(m, list): obody.extend(m)
                            elif m: obody.append(m)
                        orelse = self._create_node(IfNode, condition=self._create_node(LiteralNode, value=True), body=obody, orelse=None)
                    elif alt_body:
                        m = self._map_node(alt_body, source_bytes, scope)
                        if isinstance(m, list): obody.extend(m)
                        elif m: obody.append(m)
                        orelse = self._create_node(IfNode, condition=self._create_node(LiteralNode, value=True), body=obody, orelse=None)
            
            return self._create_node(IfNode, condition=cond_ast, body=body, orelse=orelse)

        elif node.type == 'for_statement':
            # for (int i = 0; i < 5; i++)
            decl_node = node.child_by_field_name('initializer')
            if not decl_node:
                decl_node = next((c for c in node.named_children if c.type in ('declaration', 'expression_statement')), None)
            
            target_name = "i"
            start_ast = self._create_node(LiteralNode, value=0)
            if decl_node and decl_node.type == 'declaration':
                init_decl = decl_node.child_by_field_name('declarator')
                if init_decl:
                    target_name = self._extract_name(init_decl, source_bytes)
                    val_node = init_decl.child_by_field_name('value')
                    if val_node: start_ast = self._map_node(val_node, source_bytes, scope)
                
            cond_node = node.child_by_field_name('condition')
            end_ast = self._create_node(LiteralNode, value=0)
            if cond_node and cond_node.type == 'binary_expression':
                # i < 5
                end_ast = self._map_node(cond_node.child_by_field_name('right'), source_bytes, scope)
                
            target_ast = self._create_node(IdentifierNode, name=target_name)
            iter_ast = self._create_node(CallNode, func_name=self._create_node(IdentifierNode, name="range"), args=[start_ast, end_ast])
            
            body_node = node.child_by_field_name('body')
            body = []
            if body_node:
                if body_node.type == 'compound_statement':
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
            cond_clause = node.child_by_field_name('condition')
            cond_node = None
            if cond_clause:
                cond_node = cond_clause.child_by_field_name('value')
                if not cond_node and len(cond_clause.named_children) > 0:
                    cond_node = cond_clause.named_children[0]
            
            cond_ast = self._map_node(cond_node, source_bytes, scope) if cond_node else self._create_node(LiteralNode, value=True)
            
            body_node = node.child_by_field_name('body')
            body = []
            if body_node:
                if body_node.type == 'compound_statement':
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
            body_node = node.child_by_field_name('body')
            body = []
            if body_node:
                for c in body_node.named_children:
                    m = self._map_node(c, source_bytes, scope)
                    if isinstance(m, list): body.extend(m)
                    elif m: body.append(m)
                    
            handlers = []
            for c in node.named_children:
                if c.type == 'catch_clause':
                    cb_node = c.child_by_field_name('body')
                    if cb_node:
                        for sc in cb_node.named_children:
                            m = self._map_node(sc, source_bytes, scope)
                            if isinstance(m, list): handlers.extend(m)
                            elif m: handlers.append(m)
                            
            return self._create_node(TryCatchNode, body=body, handlers=handlers)
            
        elif node.type == 'throw_statement':
            args = []
            if len(node.named_children) > 0:
                args.append(self._map_node(node.named_children[0], source_bytes, scope))
            return self._create_node(CallNode, func_name=self._create_node(IdentifierNode, name="throw"), args=args)

        elif node.type == 'expression_statement' or node.type == 'compound_statement':
            res = []
            for c in node.named_children:
                m = self._map_node(c, source_bytes, scope)
                if isinstance(m, list): res.extend(m)
                elif m: res.append(m)
            if node.type == 'expression_statement':
                return res[0] if res else None
            return res

        elif node.type == 'return_statement':
            if len(node.named_children) > 0:
                return self._create_node(ReturnNode, value=self._map_node(node.named_children[0], source_bytes, scope))
            return self._create_node(ReturnNode, value=None)

        elif node.type == 'field_expression':
            obj_ast = self._map_node(node.child_by_field_name('value'), source_bytes, scope)
            if not obj_ast and len(node.named_children) > 0:
                obj_ast = self._map_node(node.named_children[0], source_bytes, scope)
                
            field_name = self._get_text(node.child_by_field_name('field'), source_bytes)
            if not field_name and len(node.named_children) > 1:
                field_name = self._get_text(node.named_children[1], source_bytes)
                
            return self._create_node(AttributeNode, value=obj_ast, attr=field_name)

        elif node.type == 'qualified_identifier':
            # std::cout
            return self._create_node(IdentifierNode, name=self._get_text(node, source_bytes))

        elif node.type == 'identifier' or node.type == 'type_identifier' or node.type == 'field_identifier':
            return self._create_node(IdentifierNode, name=self._get_text(node, source_bytes))

        elif node.type == 'this':
            return self._create_node(IdentifierNode, name="self")

        elif node.type == 'number_literal':
            text = self._get_text(node, source_bytes)
            clean_text = text.lower().replace('u', '').replace('l', '')
            if '.' in text or 'e' in text.lower():
                return self._create_node(LiteralNode, value=float(clean_text), metadata={"type": "double"})
            return self._create_node(LiteralNode, value=int(clean_text, 0), metadata={"type": "int"})

        elif node.type == 'boolean_literal':
            text = self._get_text(node, source_bytes)
            return self._create_node(LiteralNode, value=(text == 'true'), metadata={"type": "bool"})

        elif node.type == 'string_literal':
            # In C++ a string_literal can contain string_content
            text_node = next((c for c in node.named_children if c.type == 'string_content'), None)
            text = self._get_text(text_node, source_bytes) if text_node else ""
            return self._create_node(LiteralNode, value=text, metadata={"type": "std::string"})
            
        elif node.type == 'update_expression':
            # i++ 
            arg = node.named_children[0]
            if not arg: return None
            op_text = source_bytes[arg.end_byte:node.end_byte].decode("utf-8").strip()
            if op_text == '++':
                return self._create_node(AssignmentNode, 
                    left=self._map_node(arg, source_bytes, scope), 
                    right=self._create_node(BinaryOpNode, 
                        left=self._map_node(arg, source_bytes, scope), 
                        operator='+', 
                        right=self._create_node(LiteralNode, value=1)
                    )
                )
            if op_text == '--':
                return self._create_node(AssignmentNode, 
                    left=self._map_node(arg, source_bytes, scope), 
                    right=self._create_node(BinaryOpNode, 
                        left=self._map_node(arg, source_bytes, scope), 
                        operator='-', 
                        right=self._create_node(LiteralNode, value=1)
                    )
                )

        return None
