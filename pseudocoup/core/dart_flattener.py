from tree_sitter import Node
from .builder import IRBuilder
from .models import Instruction, OpCode

class DartFlattener:
    """
    Flattens Dart Tree-Sitter AST nodes into the Universal Linear IR.
    """
    def __init__(self, builder: IRBuilder):
        self.builder = builder

    def flatten(self, root_node: Node):
        """Walks the Dart AST and emits linear IR instructions."""
        self._visit(root_node)

    def _visit(self, node: Node) -> str:
        """Visits a Dart node, emits instructions, and returns the temp variable holding its value."""
        if not node:
            return ""
            
        # Dart assigns using 'assignment_expression' or 'initialized_variable_definition'
        if node.type in ("assignment_expression", "initialized_variable_definition"):
            left = node.child_by_field_name('left') or node.child_by_field_name('name')
            right = node.child_by_field_name('right') or node.child_by_field_name('value')
            
            # If named fields aren't present (e.g. some dart tree-sitter versions)
            if not left and node.type == "initialized_variable_definition":
                # Find identifier and value manually
                for child in node.named_children:
                    if child.type == "identifier":
                        left = child
                    elif child.type != "type_identifier":
                        right = child
            
            if not left and node.type == "assignment_expression":
                left = node.named_children[0]
                right = node.named_children[1]
            
            if left and right:
                dest = left.text.decode('utf8')
                val = self._visit(right)
                self.builder.emit_assign(dest, [val])
                return dest
                
        # Function call in Dart could just be identifier + selector
        elif node.type == "expression_statement":
            # Sometimes method calls are just expressions
            return self._visit(node.named_children[0])
            
        elif node.type == "parenthesized_expression":
            return self._visit(node.named_children[0]) if node.named_children else ""
            
        elif node.type == "identifier":
            # Check if this identifier is actually part of a method call (followed by a selector)
            if node.next_named_sibling and node.next_named_sibling.type == "selector":
                selector = node.next_named_sibling
                arg_part = selector.named_children[0] if selector.named_children else None
                
                args_node = None
                if arg_part and arg_part.type == "argument_part":
                    args_node = arg_part.named_children[0] if arg_part.named_children else None
                elif arg_part and arg_part.type == "arguments":
                    args_node = arg_part
                    
                func_name = node.text.decode('utf8')
                args = []
                if args_node and args_node.type == "arguments":
                    for arg in args_node.named_children:
                        val_node = arg.named_children[0] if arg.named_children else arg
                        args.append(self._visit(val_node))
                return self.builder.emit_temp_call(func_name, args)
            return node.text.decode('utf8')
            
        # Property access (e.g. foo.bar)
        elif node.type == "property_access":
            obj = node.child_by_field_name('target')
            attr = node.child_by_field_name('propertyName')
            
            obj_val = self._visit(obj) if obj else ""
            attr_name = attr.text.decode('utf8') if attr else ""
            
            dest = self.builder._next_temp()
            self.builder.emit(Instruction(OpCode.ATTR, dest=dest, args=[obj_val, attr_name]))
            return dest
            
        elif node.type == "identifier":
            return node.text.decode('utf8')
            
        elif node.type in ("number_literal", "string_literal", "boolean_literal", "decimal_integer_literal"):
            # Emit assignment to temp for literals
            return self.builder.emit_temp_assign([node.text.decode('utf8')])
            
        elif node.type == "if_statement":
            cond_node = node.child_by_field_name('condition')
            if not cond_node and len(node.named_children) > 0:
                cond_node = node.named_children[0]
            cond_var = self._visit(cond_node) if cond_node else ""
            
            branch_instr = Instruction(OpCode.BRANCH, args=[cond_var, -1, -1])
            self.builder.emit(branch_instr)
            
            true_idx = len(self.builder.instructions)
            consequence = node.child_by_field_name('consequence')
            if not consequence and len(node.named_children) > 1:
                consequence = node.named_children[1]
            if consequence:
                self._visit(consequence)
                
            jump_merge_true = Instruction(OpCode.JUMP, args=[-1])
            self.builder.emit(jump_merge_true)
            
            false_idx = len(self.builder.instructions)
            alternative = node.child_by_field_name('alternative')
            if not alternative and len(node.named_children) > 2:
                alternative = node.named_children[2]
            if alternative:
                self._visit(alternative)
                
            jump_merge_false = Instruction(OpCode.JUMP, args=[-1])
            self.builder.emit(jump_merge_false)
            
            merge_idx = len(self.builder.instructions)
            
            branch_instr.args[1] = true_idx
            branch_instr.args[2] = false_idx
            jump_merge_true.args[0] = merge_idx
            jump_merge_false.args[0] = merge_idx
            
            return ""

        elif node.type in ("while_statement", "for_statement"):
            loop_header_idx = len(self.builder.instructions)
            
            cond_var = ""
            body = None
            
            if node.type == "while_statement":
                cond_node = node.child_by_field_name('condition')
                if not cond_node and len(node.named_children) > 0:
                    cond_node = node.named_children[0]
                cond_var = self._visit(cond_node) if cond_node else ""
            else:
                # Basic for-loop assumption for MVP flat IR
                cond_var = self.builder.emit_temp_assign(["True"])
                
            branch_instr = Instruction(OpCode.BRANCH, args=[cond_var, -1, -1])
            self.builder.emit(branch_instr)
            
            body_idx = len(self.builder.instructions)
            if not body:
                body = node.child_by_field_name('body')
            if not body and node.type == "while_statement" and len(node.named_children) > 1:
                body = node.named_children[1]
            if body:
                self._visit(body)
                
            self.builder.emit(Instruction(OpCode.JUMP, args=[loop_header_idx]))
            
            exit_idx = len(self.builder.instructions)
            branch_instr.args[1] = body_idx
            branch_instr.args[2] = exit_idx
            return ""

        elif node.type == "try_statement":
            body = node.child_by_field_name('body')
            if body:
                self._visit(body)
                
            jump_merge = Instruction(OpCode.JUMP, args=[-1])
            self.builder.emit(jump_merge)
            
            for child in node.named_children:
                if child.type == "catch_clause":
                    catch_body = child.child_by_field_name('body')
                    self._visit(catch_body if catch_body else child)
                    
            merge_idx = len(self.builder.instructions)
            jump_merge.args[0] = merge_idx
            return ""

        else:
            # Recursively descend for blocks / expression_statements
            for child in node.named_children:
                self._visit(child)
            return ""
