import ast
from tree_sitter import Language, Parser
import tree_sitter_ruby

class RubyToPyTranspiler:
    def __init__(self):
        self.parser = Parser(Language(tree_sitter_ruby.language()))

    def transpile(self, code: str) -> str:
        tree = self.parser.parse(code.encode('utf8'))
        py_ast = self.visit_node(tree.root_node)
        
        # fix missing __init__ params or similar if needed
        # but since we translate initialize, it naturally maps to __init__
        ast.fix_missing_locations(py_ast)
        return ast.unparse(py_ast)

    def ensure_stmt(self, node):
        if isinstance(node, ast.expr):
            return ast.Expr(value=node)
        return node

    def visit_node(self, node):
        if node.type == "program":
            body = []
            
            # Add typing import
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
            
        elif node.type == "class":
            name = self.get_text(self.get_child(node, "constant"))
            body_stmt = self.get_child(node, "body_statement")
            body = []
            if body_stmt:
                for c in body_stmt.children:
                    if c.is_named:
                        res = self.visit_node(c)
                        if res: body.append(self.ensure_stmt(res))
            
            # remove attr_accessor calls
            body = [b for b in body if not (isinstance(b, ast.Expr) and isinstance(b.value, ast.Call) and isinstance(b.value.func, ast.Name) and b.value.func.id == "attr_accessor")]
            
            if not body: body.append(ast.Pass())
            return ast.ClassDef(
                name=name,
                bases=[],
                keywords=[],
                body=body,
                decorator_list=[]
            )
            
        elif node.type == "method":
            name = self.get_text(self.get_child(node, "identifier"))
            if name == "initialize": name = "__init__"
            
            args = []
            if name != "main":
                args.append(ast.arg(arg="self", annotation=None))
                
            params = self.get_child(node, "method_parameters")
            if params:
                for c in params.children:
                    if c.type == "identifier":
                        args.append(ast.arg(arg=self.get_text(c), annotation=ast.Name(id="Any", ctx=ast.Load())))
                        
            body_stmt = self.get_child(node, "body_statement")
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
            
        elif node.type == "assignment":
            left = self.visit_node(node.children[0])
            if isinstance(left, ast.Attribute): left.ctx = ast.Store()
            if isinstance(left, ast.Name): left.ctx = ast.Store()
            right = self.visit_node(node.children[2])
            return ast.Assign(targets=[left], value=right)
            
        elif node.type == "call":
            receiver = None
            method = None
            args_node = None
            
            if node.children[0].type == "self":
                # self.method (children: self, ., identifier)
                receiver = ast.Name(id="self", ctx=ast.Load())
                ident_node = self.get_child(node, "identifier")
                if ident_node:
                    method = self.get_text(ident_node)
                args_node = self.get_child(node, "argument_list")
                
                if method is None:
                    # just 'self'
                    return receiver
                    
                # In Ruby, self.capacity without args is a getter!
                if args_node is None:
                    return ast.Attribute(value=receiver, attr=method, ctx=ast.Load())
            else:
                # normal call or method call on object
                is_method = False
                method_ident = None
                for i, c in enumerate(node.children):
                    if c.type == "." and i + 1 < len(node.children) and node.children[i+1].type == "identifier":
                        is_method = True
                        method_ident = node.children[i+1]
                        break
                        
                args_node = self.get_child(node, "argument_list")
                
                if is_method:
                    receiver = self.visit_node(node.children[0])
                    method = self.get_text(method_ident)
                    
                    if method == "new":
                        return ast.Call(
                            func=receiver,
                            args=self.parse_args(args_node) if args_node else [],
                            keywords=[]
                        )
                    
                    if args_node is None:
                        if method in ["length", "size"]:
                            return ast.Call(func=ast.Name(id="len", ctx=ast.Load()), args=[receiver], keywords=[])
                        if method == "to_s":
                            return ast.Call(func=ast.Name(id="str", ctx=ast.Load()), args=[receiver], keywords=[])
                        if method == "nil?":
                            return ast.Compare(left=receiver, ops=[ast.Eq()], comparators=[ast.Constant(value=None)])
                            
                        return ast.Attribute(value=receiver, attr=method, ctx=ast.Load())
                else:
                    # func(args)
                    func_name = self.get_text(node.children[0])
                        
                    if func_name == "puts":
                        func_name = "print"
                        
                    if func_name == "raise":
                        args = self.parse_args(args_node) if args_node else []
                        if len(args) == 2 and isinstance(args[0], ast.Name) and args[0].id == "StandardError":
                            exc = ast.Call(func=ast.Name(id="Exception", ctx=ast.Load()), args=[args[1]], keywords=[])
                            return ast.Raise(exc=exc, cause=None)
                    
                    return ast.Call(
                        func=ast.Name(id=func_name, ctx=ast.Load()),
                        args=self.parse_args(args_node) if args_node else [],
                        keywords=[]
                    )
                    
            # method call
            func = ast.Attribute(value=receiver, attr=method, ctx=ast.Load())
            args = self.parse_args(args_node) if args_node else []
            
            if method == "has_key?":
                return ast.Compare(left=args[0], ops=[ast.In()], comparators=[receiver])
                
            return ast.Call(func=func, args=args, keywords=[])

        elif node.type == "binary":
            left = self.visit_node(node.children[0])
            op = self.get_text(node.children[1])
            right = self.visit_node(node.children[2])
            
            if op in ["==", "!=", "<", "<=", ">", ">="]:
                op_map = {
                    "==": ast.Eq(), "!=": ast.NotEq(),
                    "<": ast.Lt(), "<=": ast.LtE(),
                    ">": ast.Gt(), ">=": ast.GtE()
                }
                return ast.Compare(left=left, ops=[op_map[op]], comparators=[right])
            else:
                op_map = {
                    "+": ast.Add(), "-": ast.Sub(),
                    "*": ast.Mult(), "/": ast.Div(), "%": ast.Mod()
                }
                return ast.BinOp(left=left, op=op_map.get(op, ast.Add()), right=right)

        elif node.type == "unary":
            op_text = self.get_text(node.children[0])
            operand = self.visit_node(node.children[1])
            if op_text == "-":
                return ast.UnaryOp(op=ast.USub(), operand=operand)
            elif op_text == "!":
                # handle !self.assigned_station.nil? 
                if isinstance(operand, ast.Compare) and isinstance(operand.ops[0], ast.Eq) and isinstance(operand.comparators[0], ast.Constant) and operand.comparators[0].value is None:
                    return ast.Compare(left=operand.left, ops=[ast.NotEq()], comparators=[ast.Constant(value=None)])
                return ast.UnaryOp(op=ast.Not(), operand=operand)
            return operand
            
        elif node.type == "parenthesized_statements":
            for c in node.children:
                if c.is_named: return self.visit_node(c)
                
        elif node.type == "array":
            elts = []
            for c in node.children:
                if c.is_named: elts.append(self.visit_node(c))
            return ast.List(elts=elts, ctx=ast.Load())
            
        elif node.type == "hash":
            keys = []
            vals = []
            for c in node.children:
                if c.type == "pair":
                    keys.append(self.visit_node(c.children[0]))
                    vals.append(self.visit_node(c.children[2]))
            return ast.Call(
                func=ast.Name(id="dict", ctx=ast.Load()),
                args=[ast.List(elts=[ast.Tuple(elts=[k, v], ctx=ast.Load()) for k, v in zip(keys, vals)], ctx=ast.Load())],
                keywords=[]
            )
            
        elif node.type == "element_reference":
            obj = self.visit_node(node.children[0])
            slice_ = self.visit_node(node.children[2])
            return ast.Subscript(value=obj, slice=slice_, ctx=ast.Load())
            
        elif node.type == "if":
            cond = self.visit_node(node.children[1])
            
            if isinstance(cond, ast.Compare) and isinstance(cond.left, ast.Name) and cond.left.id == "__FILE__":
                cond = ast.Compare(left=ast.Name(id="__name__", ctx=ast.Load()), ops=[ast.Eq()], comparators=[ast.Constant(value="__main__")])
                
            then_node = self.get_child(node, "then")
            else_node = self.get_child(node, "else")
            
            body = []
            if then_node:
                for c in then_node.children:
                    if c.is_named: 
                        res = self.visit_node(c)
                        if res: body.append(self.ensure_stmt(res))
            if not body: body.append(ast.Pass())
            
            orelse = []
            if else_node:
                for c in else_node.children:
                    if c.is_named: 
                        res = self.visit_node(c)
                        if res: orelse.append(self.ensure_stmt(res))
                    
            return ast.If(test=cond, body=body, orelse=orelse)
            
        elif node.type == "while":
            cond = self.visit_node(node.children[1])
            do_node = self.get_child(node, "do")
            body = []
            if do_node:
                for c in do_node.children:
                    if c.is_named: 
                        res = self.visit_node(c)
                        if res: body.append(self.ensure_stmt(res))
            if not body: body.append(ast.Pass())
            return ast.While(test=cond, body=body, orelse=[])
            
        elif node.type == "begin":
            body = []
            handlers = []
            for c in node.children:
                if c.type == "rescue":
                    ex_type = ast.Name(id="Exception", ctx=ast.Load())
                    name = "e"
                    ex_var = self.get_child(c, "exception_variable")
                    if ex_var: 
                        ident_node = self.get_child(ex_var, "identifier")
                        if ident_node: name = self.get_text(ident_node)
                    
                    then_node = self.get_child(c, "then")
                    h_body = []
                    if then_node:
                        for tc in then_node.children:
                            if tc.is_named: 
                                res = self.visit_node(tc)
                                if res: h_body.append(self.ensure_stmt(res))
                    if not h_body: h_body.append(ast.Pass())
                    
                    handlers.append(ast.ExceptHandler(type=ex_type, name=name, body=h_body))
                elif c.is_named:
                    res = self.visit_node(c)
                    if res: body.append(self.ensure_stmt(res))
                    
            if not body: body.append(ast.Pass())
            return ast.Try(body=body, handlers=handlers, orelse=[], finalbody=[])

        elif node.type == "return":
            val = None
            args = self.get_child(node, "argument_list")
            if args and len(args.children) > 0:
                # usually just one named child
                for c in args.children:
                    if c.is_named:
                        val = self.visit_node(c)
                        break
            return ast.Return(value=val)
            
        elif node.type == "break": return ast.Break()
        elif node.type == "next": return ast.Continue()
        
        elif node.type in ["identifier", "global_variable"]:
            return ast.Name(id=self.get_text(node), ctx=ast.Load())
            
        elif node.type == "constant":
            # For ruby constants like SpaceStation
            return ast.Name(id=self.get_text(node), ctx=ast.Load())
            
        elif node.type == "integer":
            return ast.Constant(value=int(self.get_text(node)))
            
        elif node.type == "string":
            content = self.get_child(node, "string_content")
            return ast.Constant(value=self.get_text(content) if content else "")
            
        elif node.type == "true": return ast.Constant(value=True)
        elif node.type == "false": return ast.Constant(value=False)
        elif node.type == "nil": return ast.Constant(value=None)
        
        # handle statements not returning anything
        elif node.type in ["body_statement", "then", "do", "else"]:
            return None
            
        # fallback to expression statement
        elif node.is_named:
            res = None
            for c in node.children:
                if c.is_named:
                    res = self.visit_node(c)
                    if res: break
            if isinstance(res, (ast.Call, ast.Assign)):
                return ast.Expr(value=res)
            return res

        return None

    def parse_args(self, args_node):
        args = []
        for c in args_node.children:
            if c.is_named:
                res = self.visit_node(c)
                if res is not None: args.append(res)
        return args

    def get_child(self, node, type_name):
        for c in node.children:
            if c.type == type_name: return c
        return None

    def get_text(self, node):
        return node.text.decode('utf8')

def transpile(code: str) -> str:
    transpiler = RubyToPyTranspiler()
    return transpiler.transpile(code)
