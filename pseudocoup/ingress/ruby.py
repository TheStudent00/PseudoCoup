from tree_sitter import Node
from ..core.builder import IRBuilder
from ..core.models import Instruction, OpCode

class RubyFlattener:
    """
    Flattens Ruby Tree-Sitter AST nodes into the Universal Linear IR.
    """
    def __init__(self, builder: IRBuilder):
        self.builder = builder

    def flatten(self, root_node: Node):
        """Walks the Ruby AST and emits linear IR instructions."""
        self._visit(root_node)

    def _visit(self, node: Node) -> str:
        """Visits a Ruby node, emits instructions, and returns the temp variable holding its value."""
        if not node:
            return ""
            
        if node.type == "assignment":
            left = node.child_by_field_name("left") or node.named_children[0]
            right = node.child_by_field_name("right") or node.named_children[1]
            
            dest = left.text.decode('utf8')
            val = self._visit(right)
            self.builder.emit_assign(dest, [val])
            return dest
            
        elif node.type == "call":
            func_node = node.child_by_field_name("method") or node.named_children[0]
            args_node = node.child_by_field_name("arguments") or (node.named_children[1] if len(node.named_children) > 1 else None)
            
            func_name = self._visit(func_node) if func_node else ""
            
            if func_name in ("puts", "print"):
                func_name = "print"
                
            args = []
            if args_node and args_node.type == "argument_list":
                for arg in args_node.named_children:
                    args.append(self._visit(arg))
            
            return self.builder.emit_temp_call(func_name, args)
            
        elif node.type == "binary":
            left = node.child_by_field_name("left") or node.named_children[0]
            right = node.child_by_field_name("right") or node.named_children[1]
            op = node.child_by_field_name("operator")
            op_text = op.text.decode('utf8') if op else "-"
            l_val = self._visit(left)
            r_val = self._visit(right)
            return self.builder.emit_temp_assign([f"{l_val} {op_text} {r_val}"])
            
        elif node.type == "identifier":
            return node.text.decode('utf8')
            
        elif node.type in ("integer", "float", "string", "true", "false", "string_content"):
            if node.type == "string":
                val = node.named_children[0].text.decode('utf8') if node.named_children else node.text.decode('utf8')
                return self.builder.emit_temp_assign([f'"{val}"'])
            
            val = node.text.decode('utf8')
            if node.type == "true":
                val = "True"
            elif node.type == "false":
                val = "False"
            return self.builder.emit_temp_assign([val])
            
        elif node.type == "if":
            cond_node = node.child_by_field_name("condition")
            if not cond_node and len(node.named_children) > 0:
                cond_node = node.named_children[0]
                
            cond_var = self._visit(cond_node) if cond_node else ""
            
            branch_instr = Instruction(OpCode.BRANCH, args=[cond_var, -1, -1])
            self.builder.emit(branch_instr)
            
            true_idx = len(self.builder.instructions)
            consequence = node.child_by_field_name("consequence")
            if not consequence:
                for child in node.named_children:
                    if child.type == "then":
                        consequence = child
                        break
                        
            if consequence:
                self._visit(consequence)
                
            jump_merge_true = Instruction(OpCode.JUMP, args=[-1])
            self.builder.emit(jump_merge_true)
            
            false_idx = len(self.builder.instructions)
            alternative = node.child_by_field_name("alternative")
            if not alternative:
                for child in node.named_children:
                    if child.type == "else" or child.type == "elsif":
                        alternative = child
                        break
                        
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
            
        elif node.type == "while":
            loop_header_idx = len(self.builder.instructions)
            
            cond_node = node.child_by_field_name("condition")
            if not cond_node and len(node.named_children) > 0:
                cond_node = node.named_children[0]
                
            cond_var = ""
            if cond_node:
                cond_var = self._visit(cond_node)
            else:
                cond_var = self.builder.emit_temp_assign(["True"])
                
            branch_instr = Instruction(OpCode.BRANCH, args=[cond_var, -1, -1])
            self.builder.emit(branch_instr)
            
            body_idx = len(self.builder.instructions)
            body = node.child_by_field_name("body")
            if not body:
                for child in node.named_children:
                    if child.type == "do":
                        body = child
                        break
                        
            if body:
                self._visit(body)
                
            self.builder.emit(Instruction(OpCode.JUMP, args=[loop_header_idx]))
            
            exit_idx = len(self.builder.instructions)
            branch_instr.args[1] = body_idx
            branch_instr.args[2] = exit_idx
            return ""
            
        elif node.type in ("program", "then", "do", "else", "elsif"):
            for child in node.named_children:
                self._visit(child)
            return ""
            
        else:
            for child in node.named_children:
                self._visit(child)
            return ""
