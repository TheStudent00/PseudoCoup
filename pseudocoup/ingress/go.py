from tree_sitter import Node
from ..core.builder import IRBuilder
from ..core.models import Instruction, OpCode

class GoFlattener:
    """
    Flattens Go Tree-Sitter AST nodes into the Universal Linear IR.
    """
    def __init__(self, builder: IRBuilder):
        self.builder = builder

    def flatten(self, root_node: Node):
        """Walks the Go AST and emits linear IR instructions."""
        self._visit(root_node)

    def _visit(self, node: Node) -> str:
        """Visits a Go node, emits instructions, and returns the temp variable holding its value."""
        if not node:
            return ""
            
        if node.type in ("short_var_declaration", "assignment_statement"):
            left = node.child_by_field_name("left")
            right = node.child_by_field_name("right")
            
            # fallback to expression_list position
            if not left and len(node.named_children) >= 2:
                left = node.named_children[0]
                right = node.named_children[1]
                
            if left and right:
                # Go usually wraps left/right in an expression_list, so we must unwrap it
                if left.type == "expression_list" and len(left.named_children) > 0:
                    left = left.named_children[0]
                if right.type == "expression_list" and len(right.named_children) > 0:
                    right = right.named_children[0]
                    
                dest = left.text.decode('utf8')
                val = self._visit(right)
                self.builder.emit_assign(dest, [val])
                return dest
                
        elif node.type == "call_expression":
            func_node = node.child_by_field_name("function") or node.named_children[0]
            args_node = node.child_by_field_name("arguments") or node.named_children[1]
            
            func_name = self._visit(func_node) if func_node else ""
            
            if func_name == "fmt.Println" or func_name == "fmt.Print" or func_name == "fmt.Printf":
                func_name = "print"
                
            args = []
            if args_node:
                for arg in args_node.named_children:
                    args.append(self._visit(arg))
            
            return self.builder.emit_temp_call(func_name, args)
            
        elif node.type == "selector_expression":
            # object.property
            obj = node.child_by_field_name("operand") or node.named_children[0]
            attr = node.child_by_field_name("field") or node.named_children[1]
            
            obj_val = self._visit(obj) if obj else ""
            attr_name = attr.text.decode('utf8') if attr else ""
            
            # For fmt.Println, it's easier to just return the full name since Go doesn't usually treat packages as dynamic objects in IR
            if obj_val == "fmt" and attr_name in ("Println", "Print", "Printf"):
                return f"{obj_val}.{attr_name}"
            
            dest = self.builder._next_temp()
            self.builder.emit(Instruction(OpCode.ATTR, dest=dest, args=[obj_val, attr_name]))
            return dest
            
        elif node.type in ("identifier", "package_identifier", "field_identifier"):
            return node.text.decode('utf8')
            
        elif node.type in ("int_literal", "float_literal", "interpreted_string_literal", "raw_string_literal", "rune_literal", "true", "false"):
            val = node.text.decode('utf8')
            if node.type == "true":
                val = "True"
            elif node.type == "false":
                val = "False"
            return self.builder.emit_temp_assign([val])
            
        elif node.type == "if_statement":
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
            
        elif node.type == "for_statement":
            loop_header_idx = len(self.builder.instructions)
            
            cond_node = node.child_by_field_name("condition")
            if not cond_node and len(node.named_children) > 0 and node.named_children[0].type != "block":
                cond_node = node.named_children[0]
                
            cond_var = ""
            if cond_node:
                cond_var = self._visit(cond_node)
            else:
                # infinite loop `for {`
                cond_var = self.builder.emit_temp_assign(["True"])
                
            branch_instr = Instruction(OpCode.BRANCH, args=[cond_var, -1, -1])
            self.builder.emit(branch_instr)
            
            body_idx = len(self.builder.instructions)
            body = node.child_by_field_name("body")
            if not body:
                for child in node.named_children:
                    if child.type == "block":
                        body = child
                        break
                        
            if body:
                self._visit(body)
                
            self.builder.emit(Instruction(OpCode.JUMP, args=[loop_header_idx]))
            
            exit_idx = len(self.builder.instructions)
            branch_instr.args[1] = body_idx
            branch_instr.args[2] = exit_idx
            return ""
            
        elif node.type in ("expression_statement", "statement_list", "block", "function_declaration", "source_file"):
            for child in node.named_children:
                self._visit(child)
            return ""
            
        else:
            for child in node.named_children:
                self._visit(child)
            return ""
