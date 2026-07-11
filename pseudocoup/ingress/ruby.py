import tree_sitter_ruby as ts
from tree_sitter import Parser, Language, Node
from pseudocoup.core.ur_ast import (
    URNode, ModuleNode, FunctionDefNode, MethodDefNode, ClassDefNode, AssignmentNode,
    BinaryOpNode, CallNode, IdentifierNode, LiteralNode,
    ReturnNode, IfNode, WhileNode, ForNode, TryCatchNode, ListNode,
    DictNode, SubscriptNode, AttributeNode
)
from pseudocoup.core.ledger import Ledger

class RubyIngestor:
    def __init__(self, ledger: Ledger):
        self.ledger = ledger
        self.parser = Parser()
        try:
            lang = Language(ts.language(), "ruby")
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

    def _infer_type_from_value(self, right_ast: URNode) -> str:
        if right_ast is None: return "dynamic"
        if isinstance(right_ast, LiteralNode):
            if isinstance(right_ast.value, int) and not isinstance(right_ast.value, bool):
                return "int"
            if isinstance(right_ast.value, float):
                return "float"
            if isinstance(right_ast.value, str):
                return "str"
            if isinstance(right_ast.value, bool):
                return "bool"
        return "dynamic"

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

        if node.type == 'class':
            name_node = node.child_by_field_name('name')
            class_name = self._get_text(name_node, source_bytes) if name_node else "Unknown"
            
            fields = []
            methods = []
            
            # Since ruby fields aren't explicitly declared, we can dynamically scrape them from the AST if needed.
            # But the requirement doesn't strictly ask to statically synthesize them if not declared, though UR-AST ClassDefNode takes fields.
            # We will populate fields as empty, as Python doesn't require static fields, but we will register to Ledger when assigned.
            
            body_node = node.child_by_field_name('body')
            if body_node:
                for c in body_node.named_children:
                    if c.type == 'method':
                        m = self._map_node(c, source_bytes, class_name)
                        if m: methods.append(m)
                    else:
                        pass # Ignore non-methods at class level for now, or map dynamically
                        
            return self._create_node(ClassDefNode, name=class_name, bases=[], fields=fields, methods=methods)

        elif node.type == 'method':
            raw_name = self._get_text(node.child_by_field_name('name'), source_bytes)
            is_constructor = (raw_name == "initialize" and scope != "")
            meth_name = "__init__" if is_constructor else raw_name
            
            ret_type = scope if is_constructor else "dynamic"
            self.ledger.register_type(scope, meth_name, ret_type)
            fqdn = f"{scope}.{meth_name}" if scope else meth_name
            
            args = []
            if scope:
                args.append(self._create_node(IdentifierNode, name="self"))
                
            param_node = node.child_by_field_name('parameters')
            if param_node:
                for param in param_node.named_children:
                    p_name = self._get_text(param, source_bytes)
                    self.ledger.register_type(fqdn, p_name, "dynamic")
                    args.append(self._create_node(IdentifierNode, name=p_name, metadata={"type": "dynamic"}))
                    
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

        elif node.type == 'assignment':
            left_node = node.child_by_field_name('left')
            right_node = node.child_by_field_name('right')
            
            right_ast = self._map_node(right_node, source_bytes, scope)
            inferred_type = self._infer_type_from_value(right_ast)
            
            if left_node.type == 'instance_variable':
                # @name
                var_name = self._get_text(left_node, source_bytes)[1:] # strip @
                self.ledger.register_type(scope, var_name, inferred_type)
                left_ast = self._create_node(AttributeNode, value=self._create_node(IdentifierNode, name="self"), attr=var_name)
            else:
                var_name = self._get_text(left_node, source_bytes)
                self.ledger.register_type(scope, var_name, inferred_type)
                left_ast = self._create_node(IdentifierNode, name=var_name, metadata={"type": inferred_type})
                
            return self._create_node(AssignmentNode, left=left_ast, right=right_ast)

        elif node.type == 'instance_variable':
            var_name = self._get_text(node, source_bytes)[1:] # strip @
            return self._create_node(AttributeNode, value=self._create_node(IdentifierNode, name="self"), attr=var_name)

        elif node.type == 'binary':
            left_node = node.child_by_field_name('left')
            right_node = node.child_by_field_name('right')
            op_text = source_bytes[left_node.end_byte:right_node.start_byte].decode("utf-8").strip()
            
            return self._create_node(BinaryOpNode, 
                left=self._map_node(left_node, source_bytes, scope),
                operator=op_text,
                right=self._map_node(right_node, source_bytes, scope)
            )

        elif node.type == 'call':
            method_node = node.child_by_field_name('method')
            receiver_node = node.child_by_field_name('receiver')
            
            if receiver_node:
                # e.g. @value.to_s -> obj = self.value, func = to_s
                obj_ast = self._map_node(receiver_node, source_bytes, scope)
                func_name = self._get_text(method_node, source_bytes)
                func_ast = self._create_node(AttributeNode, value=obj_ast, attr=func_name)
            else:
                func_name = self._get_text(method_node, source_bytes)
                if func_name == "puts": func_name = "print"
                func_ast = self._create_node(IdentifierNode, name=func_name)
                
            args = []
            args_node = node.child_by_field_name('arguments')
            if args_node:
                for arg in args_node.named_children:
                    args.append(self._map_node(arg, source_bytes, scope))
                    
            return self._create_node(CallNode, func_name=func_ast, args=args)

        elif node.type == 'if':
            cond_node = node.child_by_field_name('condition')
            conseq_node = node.child_by_field_name('consequence')
            alt_node = node.child_by_field_name('alternative')
            
            cond_ast = self._map_node(cond_node, source_bytes, scope)
            body = []
            if conseq_node:
                if conseq_node.type == 'then':
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
                obody = []
                for c in alt_node.named_children:
                    m = self._map_node(c, source_bytes, scope)
                    if isinstance(m, list): obody.extend(m)
                    elif m: obody.append(m)
                orelse = self._create_node(IfNode, condition=self._create_node(LiteralNode, value=True), body=obody, orelse=None)
                
            return self._create_node(IfNode, condition=cond_ast, body=body, orelse=orelse)

        elif node.type == 'for':
            # for i in 0...5
            var_node = node.named_children[0]
            in_node = node.child_by_field_name('in')
            # The 'in' node in tree-sitter ruby actually holds the iter, e.g. a 'range' node
            # The structure is: for -> identifier, in -> (range)
            # wait, 'in' is a keyword. the tree-sitter names it 'in' field? No, field is not 'in'.
            # Looking at dump:
            # for
            #   identifier
            #   in
            #     range -> integer, integer
            iter_node = next((c for c in node.named_children if c.type in ('in', 'range', 'array')), None)
            if iter_node and iter_node.type == 'in':
                iter_node = iter_node.named_children[0] if len(iter_node.named_children) > 0 else None
                
            target_ast = self._map_node(var_node, source_bytes, scope)
            
            if iter_node and iter_node.type == 'range':
                start_node = iter_node.named_children[0]
                end_node = iter_node.named_children[1] if len(iter_node.named_children) > 1 else None
                iter_ast = self._create_node(CallNode, 
                    func_name=self._create_node(IdentifierNode, name="range"), 
                    args=[self._map_node(start_node, source_bytes, scope), self._map_node(end_node, source_bytes, scope)]
                )
            else:
                iter_ast = self._map_node(iter_node, source_bytes, scope)
                
            body_node = node.child_by_field_name('body')
            body = []
            if body_node:
                for c in body_node.named_children:
                    m = self._map_node(c, source_bytes, scope)
                    if isinstance(m, list): body.extend(m)
                    elif m: body.append(m)
                    
            return self._create_node(ForNode, target=target_ast, iter=iter_ast, body=body)

        elif node.type == 'while':
            cond_node = node.child_by_field_name('condition')
            body_node = node.child_by_field_name('body')
            
            cond_ast = self._map_node(cond_node, source_bytes, scope)
            body = []
            if body_node:
                for c in body_node.named_children:
                    m = self._map_node(c, source_bytes, scope)
                    if isinstance(m, list): body.extend(m)
                    elif m: body.append(m)
            return self._create_node(WhileNode, condition=cond_ast, body=body)

        elif node.type == 'begin':
            body = []
            handlers = []
            
            for c in node.named_children:
                if c.type == 'rescue':
                    hbody = []
                    cb_node = c.child_by_field_name('body')
                    if cb_node:
                        for sc in cb_node.named_children:
                            m = self._map_node(sc, source_bytes, scope)
                            if isinstance(m, list): hbody.extend(m)
                            elif m: hbody.append(m)
                    handlers.extend(hbody)
                else:
                    m = self._map_node(c, source_bytes, scope)
                    if isinstance(m, list): body.extend(m)
                    elif m: body.append(m)
                    
            return self._create_node(TryCatchNode, body=body, handlers=handlers)

        elif node.type == 'return':
            if len(node.named_children) > 0:
                return self._create_node(ReturnNode, value=self._map_node(node.named_children[0], source_bytes, scope))
            return self._create_node(ReturnNode, value=None)

        elif node.type == 'identifier' or node.type == 'constant':
            return self._create_node(IdentifierNode, name=self._get_text(node, source_bytes))

        elif node.type == 'integer':
            return self._create_node(LiteralNode, value=int(self._get_text(node, source_bytes)))
            
        elif node.type == 'float':
            return self._create_node(LiteralNode, value=float(self._get_text(node, source_bytes)))

        elif node.type == 'true':
            return self._create_node(LiteralNode, value=True)

        elif node.type == 'false':
            return self._create_node(LiteralNode, value=False)

        elif node.type == 'string':
            text_node = next((c for c in node.named_children if c.type == 'string_content'), None)
            text = self._get_text(text_node, source_bytes) if text_node else ""
            return self._create_node(LiteralNode, value=text)

        elif node.type == 'body_statement' or node.type == 'then' or node.type == 'else' or node.type == 'do':
            res = []
            for c in node.named_children:
                m = self._map_node(c, source_bytes, scope)
                if isinstance(m, list): res.extend(m)
                elif m: res.append(m)
            return res

        return None
