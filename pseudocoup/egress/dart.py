from ..core.models import PseudoNode
from ..core.constants import NODE_ASSIGNMENT, NODE_CALL, NODE_IDENTIFIER, NODE_STRING, NODE_INTEGER

class DartGenerator:
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
        
        # In Dart, we might want to wrap top-level statements in a main() if not already
        has_main = any(child.type == "function_definition" and child.child_by_field_name('name').text.decode('utf8') == "main" for child in root.named_children)
        
        if not has_main:
            self._add_line("void main() {")
            self.indent_level += 1
            
        for child in root.named_children:
            self._visit(child)
            
        if not has_main:
            self.indent_level -= 1
            self._add_line("}")
            
        return "\n".join(self.lines)

    def _visit(self, node: PseudoNode):
        if node.type == NODE_ASSIGNMENT:
            left = node.child_by_field_name('left')
            right = node.child_by_field_name('right')
            left_str = self._expr(left)
            right_str = self._expr(right)
            
            if left_str not in self.declared_vars:
                # Use dynamic or var if type is Unknown
                type_str = "var"
                if node._semantic_type and node._semantic_type.name != "Unknown":
                    # Convert Python/Universal types to Dart
                    if node._semantic_type.name == "Int": type_str = "int"
                    elif node._semantic_type.name == "String": type_str = "String"
                    elif node._semantic_type.name == "Bool": type_str = "bool"
                    elif node._semantic_type.name == "Float": type_str = "double"
                
                self._add_line(f"{type_str} {left_str} = {right_str};")
                self.declared_vars.add(left_str)
            else:
                self._add_line(f"{left_str} = {right_str};")
            
        elif node.type == NODE_CALL:
            func = node.child_by_field_name('function')
            args = node.child_by_field_name('arguments')
            
            func_str = self._expr(func)
            args_str = ""
            if args:
                args_list = [self._expr(arg) for arg in args.named_children]
                args_str = ", ".join(args_list)
                
            self._add_line(f"{func_str}({args_str});")

        elif node.type == "block":
            for child in node.named_children:
                self._visit(child)
                
        elif node.type == "if_statement":
            cond = node.child_by_field_name('condition')
            cond_str = self._expr(cond) if cond else ""
            self._add_line(f"if ({cond_str}) {{")
            self.indent_level += 1
            
            consequence = node.child_by_field_name('consequence')
            if consequence and consequence.named_children:
                self._visit(consequence)
            self.indent_level -= 1
            
            alternative = node.child_by_field_name('alternative')
            if alternative:
                self._add_line("} else {")
                self.indent_level += 1
                if alternative.named_children:
                    self._visit(alternative)
                self.indent_level -= 1
            self._add_line("}")
                
        elif node.type == "while_statement":
            cond = node.child_by_field_name('condition')
            cond_str = self._expr(cond) if cond else ""
            self._add_line(f"while ({cond_str}) {{")
            self.indent_level += 1
            
            body = node.child_by_field_name('body')
            if body and body.named_children:
                self._visit(body)
            self.indent_level -= 1
            self._add_line("}")

    def _expr(self, node: PseudoNode) -> str:
        if node.type == NODE_INTEGER:
            return node.text.decode('utf8')
        elif node.type == NODE_STRING:
            val = node.text.decode('utf8')
            if not val.startswith('"') and not val.startswith("'"):
                return f'"{val}"'
            return val
        elif node.type == NODE_IDENTIFIER:
            # Mapped method intercepts can be directly handled here or in Emitter
            name = node.text.decode('utf8')
            if name == "print":
                return "print"
            return name
        
        return f"/* unhandled {node.type} */"
