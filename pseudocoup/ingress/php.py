import tree_sitter_php as ts
from tree_sitter import Parser, Language, Node
from pseudocoup.core.ur_ast import (
    URNode, ModuleNode, FunctionDefNode, MethodDefNode, ClassDefNode, AssignmentNode,
    BinaryOpNode, CallNode, IdentifierNode, LiteralNode,
    ReturnNode, IfNode, WhileNode, ForNode, TryCatchNode, ListNode,
    DictNode, SubscriptNode, AttributeNode
)
from pseudocoup.core.ledger import Ledger

class PhpIngestor:
    def __init__(self, ledger: Ledger):
        self.ledger = ledger
        self.parser = Parser()
        try:
            lang = Language(ts.language_php(), "php")
            self.parser.set_language(lang)
        except Exception:
            lang = Language(ts.language_php())
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

    def _strip_dollar(self, var_name: str) -> str:
        if var_name.startswith('$'):
            return var_name[1:]
        return var_name

    def _map_php_type(self, type_str: str) -> str:
        if not type_str: return "dynamic"
        if type_str == "int": return "int"
        if type_str == "string": return "str"
        if type_str == "float": return "float"
        if type_str == "bool": return "bool"
        return "dynamic"

    def _map_root(self, root: Node, source_bytes: bytes) -> ModuleNode:
        body = []
        for child in root.named_children:
            if child.type == 'php_tag':
                continue
            mapped = self._map_node(child, source_bytes, "")
            if mapped:
                if isinstance(mapped, list): body.extend(mapped)
                else: body.append(mapped)
        return self._create_node(ModuleNode, body=body)

    def _map_node(self, node: Node, source_bytes: bytes, scope: str):
        if not node or not node.is_named:
            return None

        if node.type == 'class_declaration':
            name_node = node.child_by_field_name('name')
            class_name = self._get_text(name_node, source_bytes) if name_node else "Unknown"
            
            fields = []
            methods = []
            
            body_node = node.child_by_field_name('body')
            if body_node:
                for c in body_node.named_children:
                    if c.type == 'method_declaration':
                        m = self._map_node(c, source_bytes, class_name)
                        if m: methods.append(m)
                    elif c.type == 'property_declaration':
                        # Can optionally parse property declarations but for now we ignore field static emission as per earlier decisions
                        pass
                        
            return self._create_node(ClassDefNode, name=class_name, bases=[], fields=fields, methods=methods)

        elif node.type in ('method_declaration', 'function_definition'):
            raw_name = self._get_text(node.child_by_field_name('name'), source_bytes)
            is_constructor = (raw_name == "__construct" and scope != "")
            meth_name = "__init__" if is_constructor else raw_name
            
            # Map return type
            type_node = node.child_by_field_name('type')
            if not type_node and node.child_by_field_name('return_type'):
                type_node = node.child_by_field_name('return_type')
                
            ret_type = self._map_php_type(self._get_text(type_node, source_bytes)) if type_node else "dynamic"
            if is_constructor:
                ret_type = scope

            self.ledger.register_type(scope, meth_name, ret_type)
            fqdn = f"{scope}.{meth_name}" if scope else meth_name
            
            args = []
            if scope:
                args.append(self._create_node(IdentifierNode, name="self"))
                
            param_node = node.child_by_field_name('parameters')
            if param_node:
                for param in param_node.named_children:
                    if param.type == 'simple_parameter':
                        p_name_node = param.child_by_field_name('name')
                        p_type_node = param.child_by_field_name('type')
                        
                        raw_p_name = self._get_text(p_name_node, source_bytes) if p_name_node else ""
                        p_name = self._strip_dollar(raw_p_name)
                        p_type = self._map_php_type(self._get_text(p_type_node, source_bytes) if p_type_node else "")
                        
                        self.ledger.register_type(fqdn, p_name, p_type)
                        args.append(self._create_node(IdentifierNode, name=p_name, metadata={"type": p_type}))
                    
            body_node = node.child_by_field_name('body')
            body = []
            if body_node:
                for c in body_node.named_children:
                    m = self._map_node(c, source_bytes, fqdn)
                    if isinstance(m, list): body.extend(m)
                    elif m: body.append(m)
                    
            if node.type == 'method_declaration':
                return self._create_node(MethodDefNode, name=meth_name, args=args, body=body, metadata={"type": ret_type})
            return self._create_node(FunctionDefNode, name=meth_name, args=args, body=body, metadata={"type": ret_type})

        elif node.type == 'expression_statement':
            if len(node.named_children) > 0:
                return self._map_node(node.named_children[0], source_bytes, scope)
            return None

        elif node.type == 'assignment_expression':
            left_node = node.child_by_field_name('left')
            right_node = node.child_by_field_name('right')
            
            right_ast = self._map_node(right_node, source_bytes, scope)
            left_ast = self._map_node(left_node, source_bytes, scope)
            
            if isinstance(left_ast, IdentifierNode):
                # Infer type logic fallback (if not defined by hints, we can still fall back to inferring literals)
                if right_ast and isinstance(right_ast, LiteralNode):
                    if isinstance(right_ast.value, int) and not isinstance(right_ast.value, bool):
                        self.ledger.register_type(scope, left_ast.name, "int")
                    elif isinstance(right_ast.value, str):
                        self.ledger.register_type(scope, left_ast.name, "str")
                        
            return self._create_node(AssignmentNode, left=left_ast, right=right_ast)

        elif node.type == 'variable_name' or node.type == 'name':
            var_name = self._strip_dollar(self._get_text(node, source_bytes))
            if var_name == "this": var_name = "self"
            return self._create_node(IdentifierNode, name=var_name)

        elif node.type == 'member_access_expression':
            obj_node = node.child_by_field_name('object')
            name_node = node.child_by_field_name('name')
            
            obj_ast = self._map_node(obj_node, source_bytes, scope)
            attr_name = self._strip_dollar(self._get_text(name_node, source_bytes)) if name_node else ""
            
            return self._create_node(AttributeNode, value=obj_ast, attr=attr_name)

        elif node.type == 'binary_expression':
            left_node = node.child_by_field_name('left')
            right_node = node.child_by_field_name('right')
            op_text = source_bytes[left_node.end_byte:right_node.start_byte].decode("utf-8").strip()
            
            return self._create_node(BinaryOpNode, 
                left=self._map_node(left_node, source_bytes, scope),
                operator=op_text,
                right=self._map_node(right_node, source_bytes, scope)
            )

        elif node.type in ('function_call_expression', 'method_call_expression', 'print_intrinsic'):
            func_node = node.child_by_field_name('function') if node.type != 'print_intrinsic' else None
            
            if node.type == 'print_intrinsic':
                func_ast = self._create_node(IdentifierNode, name="print")
                args_node = node.named_children[0] if len(node.named_children) > 0 else None
                # print in PHP can take a parenthesized_expression
                args = []
                if args_node:
                    # In print(x), tree-sitter might see parenthesized_expression containing the argument
                    if args_node.type == 'parenthesized_expression':
                        args_node = args_node.named_children[0] if len(args_node.named_children) > 0 else None
                    if args_node:
                        args.append(self._map_node(args_node, source_bytes, scope))
                return self._create_node(CallNode, func_name=func_ast, args=args)
                
            func_ast = None
            if node.type == 'method_call_expression':
                obj_node = node.child_by_field_name('object')
                name_node = node.child_by_field_name('name')
                obj_ast = self._map_node(obj_node, source_bytes, scope)
                attr_name = self._get_text(name_node, source_bytes)
                func_ast = self._create_node(AttributeNode, value=obj_ast, attr=attr_name)
            else:
                func_name = self._get_text(func_node, source_bytes)
                if func_name == "strval": func_name = "str"
                func_ast = self._create_node(IdentifierNode, name=func_name)
                
            args = []
            args_node = node.child_by_field_name('arguments')
            if args_node:
                for arg in args_node.named_children:
                    args.append(self._map_node(arg, source_bytes, scope))
                    
            return self._create_node(CallNode, func_name=func_ast, args=args)

        elif node.type == 'if_statement':
            cond_node = node.child_by_field_name('condition')
            body_node = node.child_by_field_name('body')
            alt_node = node.child_by_field_name('alternative')
            
            # PHP condition is often wrapped in parenthesized_expression
            if cond_node and cond_node.type == 'parenthesized_expression':
                cond_node = cond_node.named_children[0] if len(cond_node.named_children) > 0 else cond_node
                
            cond_ast = self._map_node(cond_node, source_bytes, scope)
            body = []
            if body_node:
                for c in body_node.named_children:
                    m = self._map_node(c, source_bytes, scope)
                    if isinstance(m, list): body.extend(m)
                    elif m: body.append(m)
                    
            orelse = None
            if alt_node:
                obody = []
                # else_clause or elseif_clause
                if alt_node.type == 'else_clause':
                    alt_body_node = alt_node.named_children[0] if len(alt_node.named_children) > 0 else None
                    if alt_body_node:
                        for c in alt_body_node.named_children:
                            m = self._map_node(c, source_bytes, scope)
                            if isinstance(m, list): obody.extend(m)
                            elif m: obody.append(m)
                    orelse = self._create_node(IfNode, condition=self._create_node(LiteralNode, value=True), body=obody, orelse=None)
                elif alt_node.type == 'elseif_clause':
                    orelse = self._map_node(alt_node, source_bytes, scope) # Not exactly right if multiple elseifs, but UR-AST handles chains with orelse
                
            return self._create_node(IfNode, condition=cond_ast, body=body, orelse=orelse)

        elif node.type == 'for_statement':
            # for ($i = 0; $i < 5; $i++)
            init_node = None
            cond_node = None
            update_node = None
            body_node = node.child_by_field_name('body')
            
            for c in node.named_children:
                if c.type == 'assignment_expression': init_node = c
                elif c.type == 'binary_expression': cond_node = c
                elif c.type == 'update_expression': update_node = c
            
            # Since UR-AST uses ForNode(target, iter) mapping closely to python `for target in iter`,
            # we try to synthesize a range() if it matches standard $i=0; $i<X; $i++
            # Otherwise we'll have to fallback to WhileNode equivalent or try our best.
            target_ast = None
            iter_ast = None
            if init_node and init_node.type == 'assignment_expression':
                target_ast = self._map_node(init_node.child_by_field_name('left'), source_bytes, scope)
                start_ast = self._map_node(init_node.child_by_field_name('right'), source_bytes, scope)
                
                end_ast = None
                if cond_node and cond_node.type == 'binary_expression':
                    end_ast = self._map_node(cond_node.child_by_field_name('right'), source_bytes, scope)
                    
                if target_ast and start_ast and end_ast:
                    iter_ast = self._create_node(CallNode, 
                        func_name=self._create_node(IdentifierNode, name="range"), 
                        args=[start_ast, end_ast]
                    )
                    
            body = []
            if body_node:
                for c in body_node.named_children:
                    m = self._map_node(c, source_bytes, scope)
                    if isinstance(m, list): body.extend(m)
                    elif m: body.append(m)
                    
            if target_ast and iter_ast:
                return self._create_node(ForNode, target=target_ast, iter=iter_ast, body=body)
                
            # Fallback (not implemented fully for generic for-loops here, UR-AST usually needs ForNode target/iter)
            return self._create_node(ForNode, target=self._create_node(IdentifierNode, name="i"), iter=self._create_node(IdentifierNode, name="[]"), body=body)

        elif node.type == 'while_statement':
            cond_node = node.child_by_field_name('condition')
            body_node = node.child_by_field_name('body')
            
            if cond_node and cond_node.type == 'parenthesized_expression':
                cond_node = cond_node.named_children[0] if len(cond_node.named_children) > 0 else cond_node
                
            cond_ast = self._map_node(cond_node, source_bytes, scope)
            body = []
            if body_node:
                for c in body_node.named_children:
                    m = self._map_node(c, source_bytes, scope)
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

        elif node.type == 'return_statement':
            if len(node.named_children) > 0:
                return self._create_node(ReturnNode, value=self._map_node(node.named_children[0], source_bytes, scope))
            return self._create_node(ReturnNode, value=None)

        elif node.type == 'integer':
            return self._create_node(LiteralNode, value=int(self._get_text(node, source_bytes)))
            
        elif node.type == 'float':
            return self._create_node(LiteralNode, value=float(self._get_text(node, source_bytes)))

        elif node.type == 'boolean':
            val = self._get_text(node, source_bytes).lower()
            return self._create_node(LiteralNode, value=(val == "true"))

        elif node.type == 'null':
            return self._create_node(LiteralNode, value=None)

        elif node.type == 'string' or node.type == 'encapsed_string':
            # Simplified string extraction
            text_node = next((c for c in node.named_children if c.type == 'string_content'), None)
            text = self._get_text(text_node, source_bytes) if text_node else ""
            if not text_node and len(node.named_children) == 0:
                text = self._get_text(node, source_bytes)
                if text.startswith("'") or text.startswith('"'):
                    text = text[1:-1]
            return self._create_node(LiteralNode, value=text)
            
        elif node.type == 'parenthesized_expression':
            if len(node.named_children) > 0:
                return self._map_node(node.named_children[0], source_bytes, scope)
            return None

        elif node.type == 'argument':
            if len(node.named_children) > 0:
                return self._map_node(node.named_children[0], source_bytes, scope)
            return None

        return None
