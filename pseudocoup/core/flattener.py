from tree_sitter import Node
from .builder import IRBuilder
from .models import Instruction, OpCode
from .constants import (
    NODE_EXPRESSION_STATEMENT, NODE_ASSIGNMENT, NODE_CALL, 
    NODE_ATTRIBUTE, NODE_IDENTIFIER, NODE_INTEGER, NODE_STRING,
    NODE_IF_STATEMENT, NODE_WHILE_STATEMENT, NODE_FOR_STATEMENT,
    NODE_TRY_STATEMENT
)

class ASTFlattener:
    def __init__(self, builder: IRBuilder):
        self.builder = builder

    def flatten(self, root_node: Node):
        """Walks the AST and emits linear IR instructions."""
        self._visit(root_node)

    def _visit(self, node: Node) -> str:
        """Visits a node, emits instructions, and returns the temp variable holding its value."""
        if node.type == NODE_ASSIGNMENT:
            left = node.child_by_field_name('left')
            right = node.child_by_field_name('right')
            if left and right:
                dest = left.text.decode('utf8') # Assuming simple identifier for now
                val = self._visit(right)
                self.builder.emit_assign(dest, [val])
                return dest
                
        elif node.type == NODE_CALL:
            func_node = node.child_by_field_name('function')
            args_node = node.child_by_field_name('arguments')
            
            func_name = self._visit(func_node) if func_node else ""
            args = []
            if args_node:
                # Naive argument extraction
                for arg in args_node.named_children:
                    args.append(self._visit(arg))
            
            return self.builder.emit_temp_call(func_name, args)
            
        elif node.type == NODE_ATTRIBUTE:
            obj = node.child_by_field_name('object')
            attr = node.child_by_field_name('attribute')
            
            obj_val = self._visit(obj) if obj else ""
            attr_name = attr.text.decode('utf8') if attr else ""
            
            dest = self.builder._next_temp()
            self.builder.emit(Instruction(OpCode.ATTR, dest=dest, args=[obj_val, attr_name]))
            return dest
            
        elif node.type == NODE_IDENTIFIER:
            return node.text.decode('utf8')
            
        elif node.type in (NODE_INTEGER, NODE_STRING, 'true', 'false'):
            # For literals, emit an assignment to a temp
            return self.builder.emit_temp_assign([node.text.decode('utf8')])
            
        elif node.type == NODE_IF_STATEMENT:
            cond_node = node.child_by_field_name('condition')
            cond_var = self._visit(cond_node) if cond_node else ""
            
            # Emit BRANCH with dummy targets
            branch_instr = Instruction(OpCode.BRANCH, args=[cond_var, -1, -1])
            self.builder.emit(branch_instr)
            
            # Visit true block
            true_idx = len(self.builder.instructions)
            consequence = node.child_by_field_name('consequence')
            if consequence:
                self._visit(consequence)
                
            # Emit JUMP to merge point
            jump_merge_true = Instruction(OpCode.JUMP, args=[-1])
            self.builder.emit(jump_merge_true)
            
            # Visit false block (elif/else)
            false_idx = len(self.builder.instructions)
            alternative = node.child_by_field_name('alternative')
            if alternative:
                self._visit(alternative)
                
            # Emit JUMP to merge point
            jump_merge_false = Instruction(OpCode.JUMP, args=[-1])
            self.builder.emit(jump_merge_false)
            
            merge_idx = len(self.builder.instructions)
            
            # Backpatch target indices
            branch_instr.args[1] = true_idx
            branch_instr.args[2] = false_idx
            jump_merge_true.args[0] = merge_idx
            jump_merge_false.args[0] = merge_idx
            
            return ""
            
        elif node.type in (NODE_WHILE_STATEMENT, NODE_FOR_STATEMENT):
            # Emit LOOP_HEADER JUMP target (this instruction itself doesn't execute, it's just the index)
            loop_header_idx = len(self.builder.instructions)
            
            # Condition
            cond_var = ""
            if node.type == NODE_WHILE_STATEMENT:
                cond_node = node.child_by_field_name('condition')
                cond_var = self._visit(cond_node) if cond_node else ""
            else:
                # Naive for-loop handling: assuming condition is just true for now in flat IR
                cond_var = self.builder.emit_temp_assign(["True"])
                
            # Branch to body or exit
            branch_instr = Instruction(OpCode.BRANCH, args=[cond_var, -1, -1])
            self.builder.emit(branch_instr)
            
            body_idx = len(self.builder.instructions)
            body = node.child_by_field_name('body')
            if body:
                self._visit(body)
                
            # Jump back to header
            self.builder.emit(Instruction(OpCode.JUMP, args=[loop_header_idx]))
            
            exit_idx = len(self.builder.instructions)
            
            # Backpatch
            branch_instr.args[1] = body_idx
            branch_instr.args[2] = exit_idx
            return ""
            
        elif node.type == NODE_TRY_STATEMENT:
            # For SSA, try block executes sequentially. Complex exception CFG is out of scope for MVP.
            body = node.child_by_field_name('body')
            if body:
                self._visit(body)
                
            # Assume implicit JUMP to merge after try
            jump_merge = Instruction(OpCode.JUMP, args=[-1])
            self.builder.emit(jump_merge)
            
            # except/finally blocks treated linearly for now
            # In a true compiler, every instruction in the try could jump here.
            # We omit full exception edges to keep the SSA graph simple in Part 2.
            for child in node.named_children:
                if child.type == "except_clause":
                    self._visit(child.child_by_field_name('body') if child.child_by_field_name('body') else child)
                    
            merge_idx = len(self.builder.instructions)
            jump_merge.args[0] = merge_idx
            return ""
            
        else:
            # Recursively visit children for block statements
            for child in node.named_children:
                self._visit(child)
            return ""
