from ..core.models import PseudoNode
from ..core.constants import (
    NODE_ASSIGNMENT, NODE_CALL, NODE_IDENTIFIER, 
    NODE_STRING, NODE_INTEGER
)

class PythonGenerator:
    """
    Generates Python code from the universal PseudoNode AST.
    Since the source code was Python, this acts as an identity function for syntax,
    but reconstructing it purely from the linear SSA IR.
    """
    def __init__(self):
        self.lines = []
        self.indent_level = 0

    def generate(self, root: PseudoNode) -> str:
        self.lines = []
        self.indent_level = 0
        self._visit(root)
        return "\n".join(self.lines)

    def _add_line(self, text: str):
        if text.strip() == "":
            self.lines.append("")
        else:
            self.lines.append("    " * self.indent_level + text)

    def _visit(self, node: PseudoNode):
        if not node:
            return ""

        if node.type == "module":
            for child in node.named_children:
                self._visit(child)
                
        elif node.type == NODE_ASSIGNMENT:
            left = node.child_by_field_name('left')
            right = node.child_by_field_name('right')
            left_str = self._expr(left) if left else ""
            right_str = self._expr(right) if right else ""
            self._add_line(f"{left_str} = {right_str}")
            
        elif node.type == NODE_CALL:
            func = node.child_by_field_name('function')
            args_node = node.child_by_field_name('arguments')
            
            func_str = self._expr(func) if func else ""
            args_str = ""
            if args_node:
                args = [self._expr(arg) for arg in args_node.named_children]
                args_str = ", ".join(args)
                
            # If it's a statement level call, add it as a line.
            # (If it's inside an expression, _expr handles it)
            self._add_line(f"{func_str}({args_str})")
            
        elif node.type == "block":
            for child in node.named_children:
                self._visit(child)
                
        elif node.type == "if_statement":
            cond = node.child_by_field_name('condition')
            cond_str = self._expr(cond) if cond else ""
            self._add_line(f"if {cond_str}:")
            self.indent_level += 1
            
            consequence = node.child_by_field_name('consequence')
            if consequence and consequence.named_children:
                self._visit(consequence)
            else:
                self._add_line("pass")
            self.indent_level -= 1
            
            alternative = node.child_by_field_name('alternative')
            if alternative:
                self._add_line("else:")
                self.indent_level += 1
                if alternative.named_children:
                    self._visit(alternative)
                else:
                    self._add_line("pass")
                self.indent_level -= 1
                
        elif node.type == "while_statement":
            cond = node.child_by_field_name('condition')
            cond_str = self._expr(cond) if cond else ""
            self._add_line(f"while {cond_str}:")
            self.indent_level += 1
            
            body = node.child_by_field_name('body')
            if body and body.named_children:
                self._visit(body)
            else:
                self._add_line("pass")
            self.indent_level -= 1

    def _expr(self, node: PseudoNode) -> str:
        """Returns the string representation of an expression node."""
        if not node:
            return ""
            
        if node.type == NODE_IDENTIFIER:
            return node.text.decode('utf8')
            
        elif node.type == NODE_STRING:
            # We assume it already has quotes from TreeSitter, or we add them if not
            text = node.text.decode('utf8')
            if not (text.startswith('"') or text.startswith("'")):
                return f'"{text}"'
            return text
            
        elif node.type == NODE_INTEGER:
            return node.text.decode('utf8')
            
        elif node.type == NODE_CALL:
            func = node.child_by_field_name('function')
            args_node = node.child_by_field_name('arguments')
            func_str = self._expr(func) if func else ""
            args_str = ""
            if args_node:
                args = [self._expr(arg) for arg in args_node.named_children]
                args_str = ", ".join(args)
            return f"{func_str}({args_str})"
            
        return f"/* unknown expr {node.type} */"

def generate_python(root: PseudoNode) -> str:
    generator = PythonGenerator()
    return generator.generate(root)
