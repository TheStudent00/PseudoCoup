from tree_sitter import Node
from .builder import IRBuilder
from .models import Instruction, OpCode

class RustFlattener:
    """
    Flattens Rust Tree-Sitter AST nodes into the Universal Linear IR.
    """
    def __init__(self, builder: IRBuilder):
        self.builder = builder

    def flatten(self, root_node: Node):
        """Walks the Rust AST and emits linear IR instructions."""
        self._visit(root_node)

    def _visit(self, node: Node) -> str:
        """Visits a Rust node, emits instructions, and returns the temp variable holding its value."""
        if not node:
            return ""
            
        if node.type in ("let_declaration", "assignment_expression"):
            left = None
            right = None
            
            if node.type == "let_declaration":
                left = node.child_by_field_name("pattern")
                right = node.child_by_field_name("value")
                if not left:
                    # Fallback for older tree-sitter-rust
                    for child in node.named_children:
                        if child.type == "identifier":
                            left = child
                        elif child.type != "mutable_specifier":
                            right = child
            elif node.type == "assignment_expression":
                left = node.child_by_field_name("left") or node.named_children[0]
                right = node.child_by_field_name("right") or node.named_children[1]
                
            if left and right:
                dest = left.text.decode('utf8')
                val = self._visit(right)
                self.builder.emit_assign(dest, [val])
                return dest
                
        elif node.type == "call_expression":
            func_node = node.child_by_field_name("function") or node.named_children[0]
            args_node = node.child_by_field_name("arguments") or node.named_children[1]
            
            func_name = self._visit(func_node) if func_node else ""
            args = []
            
            if args_node:
                for arg in args_node.named_children:
                    args.append(self._visit(arg))
            
            return self.builder.emit_temp_call(func_name, args)
            
        elif node.type == "macro_invocation":
            # identifier! ( token_tree )
            macro_name_node = node.child_by_field_name("macro")
            if not macro_name_node and len(node.named_children) > 0:
                macro_name_node = node.named_children[0]
                
            token_tree = node.child_by_field_name("tokens")
            if not token_tree and len(node.named_children) > 1:
                token_tree = node.named_children[1]
                
            func_name = macro_name_node.text.decode('utf8') if macro_name_node else ""
            
            # Map common macros to universal built-ins
            if func_name in ("println", "print", "format"):
                func_name = "print"
                
            args = []
            if token_tree and token_tree.type == "token_tree":
                # token_tree contains all the arguments
                for child in token_tree.named_children:
                    args.append(self._visit(child))
                    
            return self.builder.emit_temp_call(func_name, args)
            
        elif node.type == "field_expression":
            # object.property
            obj = node.child_by_field_name("value") or node.named_children[0]
            attr = node.child_by_field_name("field") or node.named_children[1]
            
            obj_val = self._visit(obj) if obj else ""
            attr_name = attr.text.decode('utf8') if attr else ""
            
            dest = self.builder._next_temp()
            self.builder.emit(Instruction(OpCode.ATTR, dest=dest, args=[obj_val, attr_name]))
            return dest
            
        elif node.type == "identifier":
            return node.text.decode('utf8')
            
        elif node.type in ("integer_literal", "float_literal", "string_literal", "boolean_literal"):
            val = node.text.decode('utf8')
            if node.type == "boolean_literal":
                val = val.capitalize() # true -> True
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
            
        elif node.type in ("while_expression", "loop_expression"):
            loop_header_idx = len(self.builder.instructions)
            
            cond_var = ""
            if node.type == "while_expression":
                cond_node = node.child_by_field_name("condition")
                if not cond_node and len(node.named_children) > 0:
                    cond_node = node.named_children[0]
                cond_var = self._visit(cond_node) if cond_node else ""
            else:
                # infinite loop
                cond_var = self.builder.emit_temp_assign(["True"])
                
            branch_instr = Instruction(OpCode.BRANCH, args=[cond_var, -1, -1])
            self.builder.emit(branch_instr)
            
            body_idx = len(self.builder.instructions)
            body = node.child_by_field_name("body")
            if not body and node.type == "while_expression" and len(node.named_children) > 1:
                body = node.named_children[1]
            elif not body and node.type == "loop_expression" and len(node.named_children) > 0:
                body = node.named_children[0]
                
            if body:
                self._visit(body)
                
            self.builder.emit(Instruction(OpCode.JUMP, args=[loop_header_idx]))
            
            exit_idx = len(self.builder.instructions)
            branch_instr.args[1] = body_idx
            branch_instr.args[2] = exit_idx
            return ""
            
        elif node.type == "expression_statement":
            return self._visit(node.named_children[0]) if node.named_children else ""
            
        else:
            for child in node.named_children:
                self._visit(child)
            return ""
