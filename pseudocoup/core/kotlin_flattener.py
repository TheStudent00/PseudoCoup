from tree_sitter import Node
from .builder import IRBuilder
from .models import Instruction, OpCode

class KotlinFlattener:
    """
    Flattens Kotlin Tree-Sitter AST nodes into the Universal Linear IR.
    """
    def __init__(self, builder: IRBuilder):
        self.builder = builder

    def flatten(self, root_node: Node):
        """Walks the Kotlin AST and emits linear IR instructions."""
        self._visit(root_node)

    def _visit(self, node: Node) -> str:
        """Visits a Kotlin node, emits instructions, and returns the temp variable holding its value."""
        if not node:
            return ""
            
        if node.type in ("property_declaration", "assignment"):
            # 'var x = 10' -> property_declaration
            # 'x = 10' -> assignment
            
            left = None
            right = None
            
            if node.type == "property_declaration":
                # Find variable_declaration and the value
                var_decl = None
                for child in node.named_children:
                    if child.type == "variable_declaration":
                        var_decl = child
                    else:
                        # The RHS is usually the next named child after variable_declaration
                        # Or it could be a type_identifier. We'll just grab the last named child if it's not the var_decl itself
                        right = child
                        
                if var_decl and var_decl.named_children:
                    left = var_decl.named_children[0] # The identifier
            elif node.type == "assignment":
                left = node.child_by_field_name("left") or node.named_children[0]
                right = node.child_by_field_name("right") or node.named_children[1]
                
            if left and right:
                dest = left.text.decode('utf8')
                val = self._visit(right)
                self.builder.emit_assign(dest, [val])
                return dest
                
        elif node.type == "call_expression":
            func_node = node.child_by_field_name("function")
            if not func_node and len(node.named_children) > 0:
                func_node = node.named_children[0]
                
            args_node = node.child_by_field_name("arguments")
            if not args_node and len(node.named_children) > 1:
                args_node = node.named_children[1] # value_arguments
                
            func_name = self._visit(func_node) if func_node else ""
            
            # Map Kotlin specific built-ins back to Universal IR
            if func_name == "println":
                func_name = "print"
                
            args = []
            
            if args_node and args_node.type == "value_arguments":
                for arg in args_node.named_children:
                    # value_argument wrapper
                    val_node = arg.named_children[0] if arg.named_children else arg
                    args.append(self._visit(val_node))
            
            return self.builder.emit_temp_call(func_name, args)
            
        elif node.type == "navigation_expression":
            # object.property
            obj = node.named_children[0] if len(node.named_children) > 0 else None
            attr = node.named_children[1] if len(node.named_children) > 1 else None
            
            obj_val = self._visit(obj) if obj else ""
            attr_name = attr.text.decode('utf8') if attr else ""
            
            dest = self.builder._next_temp()
            self.builder.emit(Instruction(OpCode.ATTR, dest=dest, args=[obj_val, attr_name]))
            return dest
            
        elif node.type == "identifier":
            return node.text.decode('utf8')
            
        elif node.type in ("integer_literal", "number_literal", "string_literal", "boolean_literal"):
            val = node.text.decode('utf8')
            if node.type == "boolean_literal":
                val = val.capitalize() # True / False for IR
            return self.builder.emit_temp_assign([val])
            
        elif node.type == "if_expression":
            cond_node = node.child_by_field_name("condition")
            if not cond_node and len(node.named_children) > 0:
                cond_node = node.named_children[0]
                
            cond_var = self._visit(cond_node) if cond_node else ""
            
            branch_instr = Instruction(OpCode.BRANCH, args=[cond_var, -1, -1])
            self.builder.emit(branch_instr)
            
            true_idx = len(self.builder.instructions)
            consequence = node.child_by_field_name("consequence")
            if not consequence and len(node.named_children) > 1:
                consequence = node.named_children[1]
                
            if consequence:
                self._visit(consequence)
                
            jump_merge_true = Instruction(OpCode.JUMP, args=[-1])
            self.builder.emit(jump_merge_true)
            
            false_idx = len(self.builder.instructions)
            alternative = node.child_by_field_name("alternative")
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
            if node.type == "while_statement":
                cond_node = node.child_by_field_name("condition")
                if not cond_node and len(node.named_children) > 0:
                    cond_node = node.named_children[0]
                cond_var = self._visit(cond_node) if cond_node else ""
            else:
                cond_var = self.builder.emit_temp_assign(["True"])
                
            branch_instr = Instruction(OpCode.BRANCH, args=[cond_var, -1, -1])
            self.builder.emit(branch_instr)
            
            body_idx = len(self.builder.instructions)
            body = node.child_by_field_name("body")
            if not body and node.type == "while_statement" and len(node.named_children) > 1:
                body = node.named_children[1]
                
            if body:
                self._visit(body)
                
            self.builder.emit(Instruction(OpCode.JUMP, args=[loop_header_idx]))
            
            exit_idx = len(self.builder.instructions)
            branch_instr.args[1] = body_idx
            branch_instr.args[2] = exit_idx
            return ""
            
        else:
            for child in node.named_children:
                self._visit(child)
            return ""
