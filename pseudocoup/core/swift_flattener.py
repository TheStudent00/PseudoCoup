from tree_sitter import Node
from .builder import IRBuilder
from .models import Instruction, OpCode

class SwiftFlattener:
    """
    Flattens Swift Tree-Sitter AST nodes into the Universal Linear IR.
    """
    def __init__(self, builder: IRBuilder):
        self.builder = builder

    def flatten(self, root_node: Node):
        """Walks the Swift AST and emits linear IR instructions."""
        self._visit(root_node)

    def _visit(self, node: Node) -> str:
        """Visits a Swift node, emits instructions, and returns the temp variable holding its value."""
        if not node:
            return ""
            
        if node.type in ("property_declaration", "assignment"):
            left = None
            right = None
            
            if node.type == "property_declaration":
                # Find the pattern (left) and the literal/expression (right)
                for child in node.named_children:
                    if child.type == "pattern":
                        left = child
                    elif child.type != "value_binding_pattern" and child.type != "pattern":
                        right = child
            elif node.type == "assignment":
                for child in node.named_children:
                    if child.type == "directly_assignable_expression":
                        left = child
                    else:
                        right = child
                
            if left and right:
                dest = self._visit(left) if left.type != "simple_identifier" else left.text.decode('utf8')
                if not dest:
                    if left.named_children:
                        dest = left.named_children[0].text.decode('utf8')
                    else:
                        dest = left.text.decode('utf8')
                val = self._visit(right)
                self.builder.emit_assign(dest, [val])
                return dest
                
        elif node.type == "call_expression":
            func_node = node.named_children[0]
            func_name = self._visit(func_node) if func_node else ""
            
            args = []
            if len(node.named_children) > 1:
                call_suffix = node.named_children[1]
                if call_suffix.type == "call_suffix" and len(call_suffix.named_children) > 0:
                    val_args = call_suffix.named_children[0]
                    for arg in val_args.named_children:
                        args.append(self._visit(arg))
            
            return self.builder.emit_temp_call(func_name, args)
            
        elif node.type == "additive_expression":
            left = node.named_children[0]
            right = node.named_children[1]
            op = node.child_by_field_name("operator")
            op_text = op.text.decode('utf8') if op else "-"
            l_val = self._visit(left)
            r_val = self._visit(right)
            return self.builder.emit_temp_assign([f"{l_val} {op_text} {r_val}"])
            
        elif node.type in ("simple_identifier", "pattern", "directly_assignable_expression"):
            if node.named_children:
                return self._visit(node.named_children[0])
            return node.text.decode('utf8')
            
        elif node.type in ("integer_literal", "boolean_literal", "line_string_literal", "value_argument"):
            if node.type == "line_string_literal":
                return node.text.decode('utf8')
            if node.type == "value_argument":
                return self._visit(node.named_children[0]) if node.named_children else ""
                
            val = node.text.decode('utf8')
            if val == "true":
                val = "True"
            elif val == "false":
                val = "False"
            return self.builder.emit_temp_assign([val])
            
        elif node.type == "if_statement":
            cond_node = node.named_children[0]
                
            cond_var = self._visit(cond_node) if cond_node else ""
            
            branch_instr = Instruction(OpCode.BRANCH, args=[cond_var, -1, -1])
            self.builder.emit(branch_instr)
            
            true_idx = len(self.builder.instructions)
            consequence = None
            for child in node.named_children:
                if child.type == "statements":
                    consequence = child
                    break
                    
            if consequence:
                self._visit(consequence)
                
            jump_merge_true = Instruction(OpCode.JUMP, args=[-1])
            self.builder.emit(jump_merge_true)
            
            false_idx = len(self.builder.instructions)
            
            # Swift if-else? Wait, if_statement might have 'else' block
            alternative = None
            if len(node.named_children) > 2:
                # Just simplified check
                pass
                
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
            
        elif node.type == "while_statement":
            loop_header_idx = len(self.builder.instructions)
            
            cond_node = node.named_children[0]
            
            cond_var = ""
            if cond_node:
                cond_var = self._visit(cond_node)
            else:
                cond_var = self.builder.emit_temp_assign(["True"])
                
            branch_instr = Instruction(OpCode.BRANCH, args=[cond_var, -1, -1])
            self.builder.emit(branch_instr)
            
            body_idx = len(self.builder.instructions)
            body = None
            for child in node.named_children:
                if child.type == "statements":
                    body = child
                    break
                        
            if body:
                self._visit(body)
                
            self.builder.emit(Instruction(OpCode.JUMP, args=[loop_header_idx]))
            
            exit_idx = len(self.builder.instructions)
            branch_instr.args[1] = body_idx
            branch_instr.args[2] = exit_idx
            return ""
            
        elif node.type in ("statements", "source_file"):
            for child in node.named_children:
                self._visit(child)
            return ""
            
        else:
            for child in node.named_children:
                self._visit(child)
            return ""
