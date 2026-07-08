import ast
from tree_sitter import Language, Parser
import tree_sitter_php

class PhpToPyTranspiler:
    def __init__(self):
        self.parser = Parser(Language(tree_sitter_php.language_php()))

    def transpile(self, code: str) -> str:
        tree = self.parser.parse(code.encode('utf8'))
        py_ast = self.visit_node(tree.root_node)
        
        ast.fix_missing_locations(py_ast)
        return ast.unparse(py_ast)

    def ensure_stmt(self, node):
        if isinstance(node, ast.expr):
            return ast.Expr(value=node)
        return node

    def visit_node(self, node):
        if node.type == "program":
            body = []
            
            import_typing = ast.ImportFrom(
                module="typing",
                names=[ast.alias(name="Any", asname=None), ast.alias(name="List", asname=None), ast.alias(name="Dict", asname=None)],
                level=0
            )
            body.append(import_typing)
            
            for child in node.children:
                if child.is_named:
                    res = self.visit_node(child)
                    if res: body.append(self.ensure_stmt(res))
            return ast.Module(body=body, type_ignores=[])
            
        elif node.type == "class_declaration":
            name = self.get_text(self.get_child(node, "name"))
            decl_list = self.get_child(node, "declaration_list")
            body = []
            if decl_list:
                for c in decl_list.children:
                    if c.is_named and c.type != "property_declaration":
                        res = self.visit_node(c)
                        if res: body.append(self.ensure_stmt(res))
                        
            if not body: body.append(ast.Pass())
            return ast.ClassDef(
                name=name,
                bases=[],
                keywords=[],
                body=body,
                decorator_list=[]
            )
            
        elif node.type in ("function_definition", "method_declaration"):
            name = self.get_text(self.get_child(node, "name"))
            if name == "__construct": name = "__init__"
            
            args = []
            if node.type == "method_declaration":
                args.append(ast.arg(arg="self", annotation=None))
                
            params = self.get_child(node, "formal_parameters")
            if params:
                for c in params.children:
                    if c.type == "simple_parameter":
                        var_name = self.get_child(c, "variable_name")
                        if var_name:
                            args.append(ast.arg(arg=self.get_text(self.get_child(var_name, "name")), annotation=ast.Name(id="Any", ctx=ast.Load())))
                            
            body_stmt = self.get_child(node, "compound_statement")
            body = []
            if body_stmt:
                for c in body_stmt.children:
                    if c.is_named:
                        res = self.visit_node(c)
                        if res:
                            if isinstance(res, list): body.extend([self.ensure_stmt(x) for x in res])
                            else: body.append(self.ensure_stmt(res))
            if not body: body.append(ast.Pass())
            
            return ast.FunctionDef(
                name=name,
                args=ast.arguments(
                    posonlyargs=[], args=args, kwonlyargs=[], kw_defaults=[], defaults=[]
                ),
                body=body,
                decorator_list=[],
                returns=ast.Name(id="Any", ctx=ast.Load())
            )
            
        elif node.type == "assignment_expression":
            left = self.visit_node(node.children[0])
            if isinstance(left, ast.Attribute): left.ctx = ast.Store()
            if isinstance(left, ast.Name): left.ctx = ast.Store()
            if isinstance(left, ast.Subscript): left.ctx = ast.Store()
            right = self.visit_node(node.children[2])
            return ast.Assign(targets=[left], value=right)
            
        elif node.type == "member_access_expression" or node.type == "member_call_expression":
            receiver = self.visit_node(node.children[0])
            attr = self.get_text(self.get_child(node, "name"))
            
            if node.type == "member_call_expression":
                args_node = self.get_child(node, "arguments")
                args = self.parse_args(args_node) if args_node else []
                return ast.Call(func=ast.Attribute(value=receiver, attr=attr, ctx=ast.Load()), args=args, keywords=[])
            
            return ast.Attribute(value=receiver, attr=attr, ctx=ast.Load())
            
        elif node.type == "function_call_expression":
            func_node = node.children[0]
            args_node = self.get_child(node, "arguments")
            args = self.parse_args(args_node) if args_node else []
            
            if func_node.type == "name":
                func_name = self.get_text(func_node)
                if func_name == "array_key_exists":
                    return ast.Compare(left=args[0], ops=[ast.In()], comparators=[args[1]])
                if func_name == "count":
                    return ast.Call(func=ast.Name(id="len", ctx=ast.Load()), args=[args[0]], keywords=[])
                    
                return ast.Call(func=ast.Name(id=func_name, ctx=ast.Load()), args=args, keywords=[])
                
        elif node.type == "object_creation_expression":
            cls_name = self.get_text(self.get_child(node, "name"))
            args_node = self.get_child(node, "arguments")
            args = self.parse_args(args_node) if args_node else []
            return ast.Call(func=ast.Name(id=cls_name, ctx=ast.Load()), args=args, keywords=[])

        elif node.type == "binary_expression":
            left = self.visit_node(node.children[0])
            op = self.get_text(node.children[1])
            right = self.visit_node(node.children[2])
            
            if op in ["==", "===", "!=", "!==", "<", "<=", ">", ">="]:
                op_map = {
                    "==": ast.Eq(), "===": ast.Eq(), "!=": ast.NotEq(), "!==": ast.NotEq(),
                    "<": ast.Lt(), "<=": ast.LtE(),
                    ">": ast.Gt(), ">=": ast.GtE()
                }
                return ast.Compare(left=left, ops=[op_map[op]], comparators=[right])
            else:
                op_map = {
                    "+": ast.Add(), "-": ast.Sub(),
                    "*": ast.Mult(), "/": ast.Div(), "%": ast.Mod(),
                    ".": ast.Add() # string concat
                }
                
                # Check if we are doing string concat, wrap with str()
                if op == ".":
                    if not (isinstance(left, ast.Constant) and isinstance(left.value, str)):
                        left = ast.Call(func=ast.Name(id="str", ctx=ast.Load()), args=[left], keywords=[])
                    if not (isinstance(right, ast.Constant) and isinstance(right.value, str)):
                        right = ast.Call(func=ast.Name(id="str", ctx=ast.Load()), args=[right], keywords=[])
                        
                return ast.BinOp(left=left, op=op_map.get(op, ast.Add()), right=right)

        elif node.type == "unary_op_expression":
            op_text = self.get_text(node.children[0])
            operand = self.visit_node(node.children[1])
            if op_text == "-":
                return ast.UnaryOp(op=ast.USub(), operand=operand)
            elif op_text == "!":
                if isinstance(operand, ast.Compare) and isinstance(operand.ops[0], ast.Eq) and isinstance(operand.comparators[0], ast.Constant) and operand.comparators[0].value is None:
                    return ast.Compare(left=operand.left, ops=[ast.NotEq()], comparators=[ast.Constant(value=None)])
                return ast.UnaryOp(op=ast.Not(), operand=operand)
            return operand
            
        elif node.type == "parenthesized_expression":
            for c in node.children:
                if c.is_named: return self.visit_node(c)
                
        elif node.type == "array_creation_expression":
            elts = []
            keys = []
            is_dict = False
            for c in node.children:
                if c.type == "array_element_initializer":
                    val = self.visit_node(c.children[-1])
                    if len(c.children) >= 3 and c.children[1].type == "=>":
                        is_dict = True
                        key = self.visit_node(c.children[0])
                        keys.append(key)
                        elts.append(val)
                    else:
                        elts.append(val)
            
            if is_dict:
                return ast.Call(
                    func=ast.Name(id="dict", ctx=ast.Load()),
                    args=[ast.List(elts=[ast.Tuple(elts=[k, v], ctx=ast.Load()) for k, v in zip(keys, elts)], ctx=ast.Load())],
                    keywords=[]
                )
            return ast.List(elts=elts, ctx=ast.Load())
            
        elif node.type == "subscript_expression":
            obj = self.visit_node(node.children[0])
            slice_ = self.visit_node(node.children[2])
            return ast.Subscript(value=obj, slice=slice_, ctx=ast.Load())
            
        elif node.type == "if_statement":
            cond = self.visit_node(self.get_child(node, "parenthesized_expression"))
            
            if isinstance(cond, ast.Compare) and isinstance(cond.left, ast.Call) and getattr(cond.left.func, "id", "") == "basename":
                # basename(__FILE__) == basename($_SERVER['PHP_SELF'])
                cond = ast.Compare(left=ast.Name(id="__name__", ctx=ast.Load()), ops=[ast.Eq()], comparators=[ast.Constant(value="__main__")])
            
            body_stmt = self.get_child(node, "compound_statement")
            body = []
            if body_stmt:
                for c in body_stmt.children:
                    if c.is_named: body.append(self.ensure_stmt(self.visit_node(c)))
            if not body: body.append(ast.Pass())
            
            orelse = []
            else_node = self.get_child(node, "else_clause")
            if else_node:
                else_body = self.get_child(else_node, "compound_statement")
                if else_body:
                    for c in else_body.children:
                        if c.is_named: orelse.append(self.ensure_stmt(self.visit_node(c)))
                    
            return ast.If(test=cond, body=body, orelse=orelse)
            
        elif node.type == "while_statement":
            cond = self.visit_node(self.get_child(node, "parenthesized_expression"))
            body_stmt = self.get_child(node, "compound_statement")
            body = []
            if body_stmt:
                for c in body_stmt.children:
                    if c.is_named: body.append(self.ensure_stmt(self.visit_node(c)))
            if not body: body.append(ast.Pass())
            return ast.While(test=cond, body=body, orelse=[])
            
        elif node.type == "try_statement":
            body_stmt = self.get_child(node, "compound_statement")
            body = []
            if body_stmt:
                for c in body_stmt.children:
                    if c.is_named: body.append(self.ensure_stmt(self.visit_node(c)))
            if not body: body.append(ast.Pass())
            
            handlers = []
            catch_node = self.get_child(node, "catch_clause")
            if catch_node:
                ex_type = ast.Name(id="Exception", ctx=ast.Load())
                name = "e"
                var_name = self.get_child(catch_node, "variable_name")
                if var_name: name = self.get_text(self.get_child(var_name, "name"))
                
                catch_body = self.get_child(catch_node, "compound_statement")
                h_body = []
                if catch_body:
                    for tc in catch_body.children:
                        if tc.is_named: h_body.append(self.ensure_stmt(self.visit_node(tc)))
                if not h_body: h_body.append(ast.Pass())
                
                handlers.append(ast.ExceptHandler(type=ex_type, name=name, body=h_body))
                    
            return ast.Try(body=body, handlers=handlers, orelse=[], finalbody=[])

        elif node.type == "return_statement":
            val = None
            for c in node.children:
                if c.is_named:
                    val = self.visit_node(c)
                    break
            return ast.Return(value=val)
            
        elif node.type == "throw_expression":
            for c in node.children:
                if c.type == "object_creation_expression":
                    exc = self.visit_node(c)
                    if isinstance(exc, ast.Call) and getattr(exc.func, "id", "") == "Exception":
                        return ast.Raise(exc=exc, cause=None)
            
        elif node.type == "break_statement": return ast.Break()
        elif node.type == "continue_statement": return ast.Continue()
        
        elif node.type == "echo_statement":
            val = None
            for c in node.children:
                if c.is_named:
                    val = self.visit_node(c)
                    break
            # Remove the appended "\n" if it's there
            if isinstance(val, ast.BinOp) and isinstance(val.op, ast.Add) and isinstance(val.right, ast.Constant) and val.right.value == "\\n":
                val = val.left
            return ast.Call(func=ast.Name(id="print", ctx=ast.Load()), args=[val], keywords=[])
            
        elif node.type == "variable_name":
            name = self.get_text(self.get_child(node, "name"))
            if name == "this": name = "self"
            return ast.Name(id=name, ctx=ast.Load())
            
        elif node.type == "name":
            return ast.Name(id=self.get_text(node), ctx=ast.Load())
            
        elif node.type == "integer":
            return ast.Constant(value=int(self.get_text(node)))
            
        elif node.type in ("string", "encapsed_string"):
            # simplify string content
            content = self.get_text(node)
            if content.startswith('"') and content.endswith('"'):
                content = content[1:-1]
            elif content.startswith("'") and content.endswith("'"):
                content = content[1:-1]
            return ast.Constant(value=content)
            
        elif node.type == "true": return ast.Constant(value=True)
        elif node.type == "false": return ast.Constant(value=False)
        elif node.type == "null": return ast.Constant(value=None)
        
        # cast expression like (string)$completed
        elif node.type == "cast_expression":
            # skip cast_type, get the actual expression
            val = None
            for c in node.children:
                if c.is_named and c.type != "cast_type":
                    val = self.visit_node(c)
                    break
            
            cast_t = self.get_child(node, "cast_type")
            if cast_t and self.get_text(cast_t) in ["string", "(string)"]:
                return ast.Call(func=ast.Name(id="str", ctx=ast.Load()), args=[val], keywords=[])
            return val
                
        # fallback to expression statement
        elif node.is_named:
            res = None
            for c in node.children:
                if c.is_named:
                    res = self.visit_node(c)
                    if res: break
            return res

        return None

    def parse_args(self, args_node):
        args = []
        for c in args_node.children:
            if c.is_named and c.type == "argument":
                res = self.visit_node(c.children[0])
                if res is not None: args.append(res)
        return args

    def get_child(self, node, type_name):
        for c in node.children:
            if c.type == type_name: return c
        return None

    def get_text(self, node):
        return node.text.decode('utf8')

def transpile(code: str) -> str:
    transpiler = PhpToPyTranspiler()
    return transpiler.transpile(code)
