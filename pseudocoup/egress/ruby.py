from ..core.models import PseudoNode
from ..core.constants import NODE_ASSIGNMENT, NODE_CALL, NODE_IDENTIFIER, NODE_STRING, NODE_INTEGER

class RubyGenerator:
    def __init__(self):
        self.lines = []
        self.indent_level = 0
        self.declared_vars = set()
        
    def _add_line(self, text: str):
        if text.strip() == "":
            self.lines.append("")
        else:
            self.lines.append("    " * self.indent_level + text)
            
    def generate(self, root: PseudoNode) -> str:
        self.lines = []
        self.indent_level = 0
        self.declared_vars = set()
        
        for child in root.named_children:
            self._visit(child)
            
        return "\n".join(self.lines)

    def _visit(self, node: PseudoNode):
        if node.type == NODE_ASSIGNMENT:
            left = node.child_by_field_name('left')
            right = node.child_by_field_name('right')
            left_str = self._expr(left)
            right_str = self._expr(right)
            
            # Ruby is dynamically typed, no let/var
            self._add_line(f"{left_str} = {right_str}")
            self.declared_vars.add(left_str)
            
        elif node.type == NODE_CALL:
            func = node.child_by_field_name('function')
            args = node.child_by_field_name('arguments')
            
            func_str = self._expr(func)
            args_str = ""
            if args:
                args_list = [self._expr(arg) for arg in args.named_children]
                args_str = ", ".join(args_list)
                
            self._add_line(f"{func_str}({args_str})")

        elif node.type == "block":
            for child in node.named_children:
                self._visit(child)
                
        elif node.type == "if_statement":
            cond = node.child_by_field_name('condition')
            cond_str = self._expr(cond) if cond else ""
            self._add_line(f"if {cond_str}")
            self.indent_level += 1
            
            consequence = node.child_by_field_name('consequence')
            if consequence and consequence.named_children:
                self._visit(consequence)
            self.indent_level -= 1
            
            alternative = node.child_by_field_name('alternative')
            if alternative:
                self._add_line("else")
                self.indent_level += 1
                if alternative.named_children:
                    self._visit(alternative)
                self.indent_level -= 1
            self._add_line("end")
                
        elif node.type == "while_statement":
            cond = node.child_by_field_name('condition')
            cond_str = self._expr(cond) if cond else ""
            self._add_line(f"while {cond_str}")
            self.indent_level += 1
            
            body = node.child_by_field_name('body')
            if body and body.named_children:
                self._visit(body)
            self.indent_level -= 1
            self._add_line("end")

    def _expr(self, node: PseudoNode) -> str:
        if node.type == NODE_INTEGER:
            return node.text.decode('utf8')
        elif node.type == NODE_STRING:
            val = node.text.decode('utf8')
            if not val.startswith('"') and not val.startswith("'"):
                return f'"{val}"'
            return val
        elif node.type == NODE_IDENTIFIER:
            name = node.text.decode('utf8')
            if name == "print":
                return "puts" 
            if name == "True":
                return "true"
            if name == "False":
                return "false"
            return name
        
        return f"/* unhandled {node.type} */"
