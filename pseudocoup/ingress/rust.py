import tree_sitter_rust as ts
from tree_sitter import Parser, Language, Node
from pseudocoup.core.ur_ast import (
    URNode, ModuleNode, FunctionDefNode, MethodDefNode, ClassDefNode, AssignmentNode,
    BinaryOpNode, CallNode, IdentifierNode, LiteralNode,
    ReturnNode, IfNode, WhileNode, ForNode, TryCatchNode, ListNode,
    DictNode, SubscriptNode, AttributeNode
)
from pseudocoup.core.ledger import Ledger
from collections import defaultdict

class RustIngestor:
    def __init__(self, ledger: Ledger):
        self.ledger = ledger
        self.parser = Parser()
        try:
            lang = Language(ts.language(), "rust")
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
        if not type_node:
            type_node = next((c for c in node.named_children if 'type' in c.type), None)
        if type_node:
            return self._get_text(type_node, source_bytes).strip()
        return "Any"

    def _get_pattern_name(self, node: Node, source_bytes: bytes) -> str:
        if not node: return "unknown"
        if node.type == 'identifier':
            return self._get_text(node, source_bytes)
        # Check if it's a mut_pattern or similar
        id_node = next((c for c in node.named_children if c.type == 'identifier'), None)
        if id_node:
            return self._get_text(id_node, source_bytes)
        return self._get_text(node, source_bytes)

    def _map_root(self, root: Node, source_bytes: bytes) -> ModuleNode:
        classes = defaultdict(lambda: {"fields": [], "methods": []})
        
        body = []
        # Pass 1: Extract structs and impls
        for child in root.named_children:
            if child.type == 'struct_item':
                name_node = child.child_by_field_name('name')
                name = self._get_text(name_node, source_bytes) if name_node else "Unknown"
                
                body_node = child.child_by_field_name('body')
                if body_node:
                    for field in body_node.named_children:
                        if field.type == 'field_declaration':
                            f_name_node = field.child_by_field_name('name')
                            f_name = self._get_text(f_name_node, source_bytes) if f_name_node else "unknown"
                            f_type = self._extract_type(field, source_bytes)
                            
                            self.ledger.register_type(name, f_name, f_type)
                            left = self._create_node(IdentifierNode, name=f_name, metadata={"type": f_type})
                            classes[name]['fields'].append(self._create_node(AssignmentNode, left=left, right=None))
            
            elif child.type == 'impl_item':
                name_node = child.child_by_field_name('type')
                name = self._get_text(name_node, source_bytes) if name_node else "Unknown"
                
                body_node = child.child_by_field_name('body')
                if body_node:
                    for method in body_node.named_children:
                        m_ast = self._map_node(method, source_bytes, name)
                        if m_ast:
                            classes[name]['methods'].append(m_ast)

        # Pass 2: generate ClassDefNodes and other top-level statements
        for class_name, content in classes.items():
            class_node = self._create_node(ClassDefNode, name=class_name, bases=[], fields=content['fields'], methods=content['methods'])
            body.append(class_node)
            
        for child in root.named_children:
            if child.type not in ('struct_item', 'impl_item'):
                mapped = self._map_node(child, source_bytes, "")
                if isinstance(mapped, list): body.extend(mapped)
                elif mapped: body.append(mapped)

        return self._create_node(ModuleNode, body=body)

    def _map_node(self, node: Node, source_bytes: bytes, scope: str):
        if not node or not node.is_named:
            return None

        if node.type == 'function_item':
            name_node = node.child_by_field_name('name')
            raw_name = self._get_text(name_node, source_bytes) if name_node else "unknown"
            
            # Map new to __init__
            meth_name = "__init__" if raw_name == "new" else raw_name
            
            ret_node = node.child_by_field_name('return_type')
            ret_type = self._get_text(ret_node, source_bytes) if ret_node else "Void"
            
            self.ledger.register_type(scope, meth_name, ret_type)
            fqdn = f"{scope}.{meth_name}" if scope else meth_name
            
            args = []
            param_node = node.child_by_field_name('parameters')
            if param_node:
                for param in param_node.named_children:
                    if param.type == 'self_parameter':
                        args.append(self._create_node(IdentifierNode, name="self"))
                    elif param.type == 'parameter':
                        p_name_node = param.child_by_field_name('pattern')
                        if not p_name_node:
                            p_name_node = next((c for c in param.named_children if c.type in ('identifier', 'mut_pattern')), None)
                        p_name = self._get_pattern_name(p_name_node, source_bytes)
                        p_type = self._extract_type(param, source_bytes)
                        self.ledger.register_type(fqdn, p_name, p_type)
                        args.append(self._create_node(IdentifierNode, name=p_name, metadata={"type": p_type}))
            
            body_node = node.child_by_field_name('body')
            body = []
            if body_node:
                # The body is a block
                for child in body_node.named_children:
                    mapped = self._map_node(child, source_bytes, fqdn)
                    if mapped:
                        if isinstance(mapped, list): body.extend(mapped)
                        else: body.append(mapped)
                        
                # Rust implicit return: last statement lacking semicolon is a return expression if not already statement
                # We can check if the last node in body is just an expression statement, but in UR-AST we can just let it be.
                # However, if the last child is an expression (not a statement), we should wrap it in ReturnNode.
                if len(body_node.named_children) > 0:
                    last_c = body_node.named_children[-1]
                    if not last_c.type.endswith('statement') and not last_c.type.endswith('declaration'):
                        # Wrap last element in ReturnNode if it's not already
                        if len(body) > 0 and not isinstance(body[-1], (ReturnNode, IfNode, WhileNode, ForNode, TryCatchNode)):
                            body[-1] = self._create_node(ReturnNode, value=body[-1])
                            
            if not scope:
                return self._create_node(FunctionDefNode, name=meth_name, args=args, body=body, metadata={"type": ret_type})
            return self._create_node(MethodDefNode, name=meth_name, args=args, body=body, metadata={"type": ret_type})

        elif node.type == 'let_declaration':
            pat_node = node.child_by_field_name('pattern')
            name = self._get_pattern_name(pat_node, source_bytes)
            var_type = self._extract_type(node, source_bytes)
            
            self.ledger.register_type(scope, name, var_type)
            
            val_node = node.child_by_field_name('value')
            left = self._create_node(IdentifierNode, name=name, metadata={"type": var_type})
            right = self._map_node(val_node, source_bytes, scope) if val_node else None
            
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
            
            return self._create_node(BinaryOpNode, 
                left=self._map_node(left_node, source_bytes, scope),
                operator=op_text,
                right=self._map_node(right_node, source_bytes, scope)
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

        elif node.type == 'macro_invocation':
            # e.g., println!("True") -> builtins_py.print
            mac_node = node.child_by_field_name('macro')
            if not mac_node: mac_node = node.named_children[0]
            mac_name = self._get_text(mac_node, source_bytes)
            
            if mac_name == 'println' or mac_name == 'print':
                func_ast = self._create_node(IdentifierNode, name="print")
            elif mac_name == 'format':
                func_ast = self._create_node(AttributeNode, value=self._create_node(LiteralNode, value=""), attr="format")
            elif mac_name == 'panic':
                func_ast = self._create_node(IdentifierNode, name="throw")
            else:
                func_ast = self._create_node(IdentifierNode, name=mac_name)
                
            tt_node = node.child_by_field_name('token_tree')
            args = []
            if tt_node:
                for arg in tt_node.named_children:
                    mapped = self._map_node(arg, source_bytes, scope)
                    if mapped: args.append(mapped)
                    
            # For format!("...", a, b), we might need to map it properly, but here we just pass them as CallNode arguments
            return self._create_node(CallNode, func_name=func_ast, args=args)

        elif node.type == 'if_expression':
            cond_node = node.child_by_field_name('condition')
            cond_ast = self._map_node(cond_node, source_bytes, scope) if cond_node else self._create_node(LiteralNode, value=True)
                
            conseq_node = node.child_by_field_name('consequence')
            body = []
            if conseq_node:
                for c in conseq_node.named_children:
                    m = self._map_node(c, source_bytes, scope)
                    if isinstance(m, list): body.extend(m)
                    elif m: body.append(m)
                    
            alt_node = node.child_by_field_name('alternative')
            orelse = None
            if alt_node:
                # alternative could be else_clause -> block or if_expression
                obody = []
                for c in alt_node.named_children:
                    m = self._map_node(c, source_bytes, scope)
                    if m:
                        if isinstance(m, IfNode):
                            orelse = m
                            obody = None
                            break
                        if isinstance(m, list): obody.extend(m)
                        else: obody.append(m)
                if obody is not None:
                    orelse = self._create_node(IfNode, condition=self._create_node(LiteralNode, value=True), body=obody, orelse=None)
            
            return self._create_node(IfNode, condition=cond_ast, body=body, orelse=orelse)

        elif node.type == 'for_expression':
            pattern_node = node.child_by_field_name('pattern')
            target_name = self._get_pattern_name(pattern_node, source_bytes)
            target_ast = self._create_node(IdentifierNode, name=target_name)
            
            range_node = node.child_by_field_name('value')
            iter_ast = self._map_node(range_node, source_bytes, scope)
            
            body_node = node.child_by_field_name('body')
            body = []
            if body_node:
                for c in body_node.named_children:
                    m = self._map_node(c, source_bytes, scope)
                    if isinstance(m, list): body.extend(m)
                    elif m: body.append(m)
                    
            return self._create_node(ForNode, target=target_ast, iter=iter_ast, body=body)

        elif node.type == 'while_expression':
            cond_node = node.child_by_field_name('condition')
            cond_ast = self._map_node(cond_node, source_bytes, scope) if cond_node else self._create_node(LiteralNode, value=True)
            
            body_node = node.child_by_field_name('body')
            body = []
            if body_node:
                for c in body_node.named_children:
                    m = self._map_node(c, source_bytes, scope)
                    if isinstance(m, list): body.extend(m)
                    elif m: body.append(m)
                    
            return self._create_node(WhileNode, condition=cond_ast, body=body)

        elif node.type == 'range_expression':
            # e.g., 0..5
            args = []
            for c in node.named_children:
                args.append(self._map_node(c, source_bytes, scope))
            return self._create_node(CallNode, func_name=self._create_node(IdentifierNode, name="range"), args=args)
            
        elif node.type == 'struct_expression':
            # Box { value: 5 }
            name_node = node.child_by_field_name('name')
            if not name_node: name_node = node.named_children[0]
            name = self._get_text(name_node, source_bytes)
            
            # Since Python uses __init__(value), we'll try to extract values in order, though Rust is named fields
            # For simplicity in ingress -> UR-AST structural mapping, we'll map this to a CallNode
            # with the values as arguments.
            args = []
            fil_node = node.child_by_field_name('body')
            if not fil_node:
                fil_node = next((c for c in node.named_children if c.type == 'field_initializer_list'), None)
            if fil_node:
                for c in fil_node.named_children:
                    if c.type == 'field_initializer':
                        val = c.child_by_field_name('value')
                        if val:
                            args.append(self._map_node(val, source_bytes, scope))
                        else:
                            # Shorthand like `Box { value }` -> value is just the identifier
                            args.append(self._map_node(c.named_children[0], source_bytes, scope))
                            
            return self._create_node(CallNode, func_name=self._create_node(IdentifierNode, name=name), args=args)

        elif node.type == 'expression_statement' or node.type == 'block':
            res = []
            for c in node.named_children:
                m = self._map_node(c, source_bytes, scope)
                if isinstance(m, list): res.extend(m)
                elif m: res.append(m)
            if node.type == 'expression_statement':
                return res[0] if res else None
            return res

        elif node.type == 'field_expression':
            obj_ast = self._map_node(node.child_by_field_name('value'), source_bytes, scope)
            field_name = self._get_text(node.child_by_field_name('field'), source_bytes)
            return self._create_node(AttributeNode, value=obj_ast, attr=field_name)

        elif node.type == 'identifier':
            return self._create_node(IdentifierNode, name=self._get_text(node, source_bytes))

        elif node.type == 'self':
            return self._create_node(IdentifierNode, name="self")

        elif node.type == 'integer_literal' or node.type == 'float_literal':
            text = self._get_text(node, source_bytes)
            if '.' in text or 'e' in text.lower():
                return self._create_node(LiteralNode, value=float(text), metadata={"type": "f64"})
            return self._create_node(LiteralNode, value=int(text), metadata={"type": "i32"})

        elif node.type == 'boolean_literal':
            text = self._get_text(node, source_bytes)
            return self._create_node(LiteralNode, value=(text == 'true'), metadata={"type": "bool"})

        elif node.type == 'string_literal':
            text_node = next((c for c in node.named_children if c.type == 'string_content'), None)
            text = self._get_text(text_node, source_bytes) if text_node else ""
            return self._create_node(LiteralNode, value=text, metadata={"type": "String"})

        return None
