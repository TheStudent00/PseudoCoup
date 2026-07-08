from tree_sitter import Node
from ..core.builder import IRBuilder
from ..core.models import Instruction, OpCode

class JavaFlattener:
    """
    Flattens Java Tree-Sitter AST nodes into the Universal Linear IR.
    """
    def __init__(self, builder: IRBuilder):
        self.builder = builder

    def flatten(self, root_node: Node):
        """Walks the Java AST and emits linear IR instructions."""
        self._visit(root_node)

    def _visit(self, node: Node) -> str:
        """Visits a Java node, emits instructions, and returns the temp variable holding its value."""
        if not node:
            return ""
            
        if node.type in ("local_variable_declaration", "assignment_expression"):
            left = None
            right = None
            
            if node.type == "local_variable_declaration":
                declarator = None
                for child in node.named_children:
                    if child.type == "variable_declarator":
                        declarator = child
                        break
                
                if declarator:
                    left = declarator.child_by_field_name("name") or declarator.named_children[0]
                    right = declarator.child_by_field_name("value") or declarator.named_children[1]
            elif node.type == "assignment_expression":
                left = node.child_by_field_name("left") or node.named_children[0]
                right = node.child_by_field_name("right") or node.named_children[1]
                
            if left and right:
                dest = left.text.decode('utf8')
                val = self._visit(right)
                self.builder.emit_assign(dest, [val])
                return dest
                
        elif node.type == "method_invocation":
            obj_node = node.child_by_field_name("object")
            name_node = node.child_by_field_name("name")
            args_node = node.child_by_field_name("arguments")
            
            if not name_node and len(node.named_children) >= 2:
                if node.named_children[0].type == "field_access":
                    obj_node = node.named_children[0]
                    name_node = node.named_children[1]
                    if len(node.named_children) > 2:
                        args_node = node.named_children[2]
                else:
                    name_node = node.named_children[0]
                    args_node = node.named_children[1]
            
            obj_str = self._visit(obj_node) if obj_node else ""
            name_str = name_node.text.decode('utf8') if name_node else ""
            
            func_name = name_str
            if obj_str == "System.out" and func_name in ("println", "print"):
                func_name = "print"
            elif obj_str:
                # We could emit an ATTR here, but for simplicity
                func_name = f"{obj_str}.{name_str}"
                
            args = []
            if args_node and args_node.type == "argument_list":
                for arg in args_node.named_children:
                    args.append(self._visit(arg))
            
            return self.builder.emit_temp_call(func_name, args)
            
        elif node.type == "field_access":
            obj = node.child_by_field_name("object") or node.named_children[0]
            field = node.child_by_field_name("field") or node.named_children[1]
            
            obj_str = self._visit(obj)
            field_str = field.text.decode('utf8')
            
            if obj_str == "System" and field_str == "out":
                return "System.out"
                
            dest = self.builder._next_temp()
            self.builder.emit(Instruction(OpCode.ATTR, dest=dest, args=[obj_str, field_str]))
            return dest
            
        elif node.type == "identifier":
            return node.text.decode('utf8')
            
        elif node.type in ("decimal_integer_literal", "decimal_floating_point_literal", "string_literal", "true", "false", "character_literal"):
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
                
            if cond_node and cond_node.type == "parenthesized_expression":
                cond_node = cond_node.named_children[0]
                
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
            
            cond_node = node.child_by_field_name("condition")
            if not cond_node and len(node.named_children) > 0 and node.named_children[0].type != "block":
                cond_node = node.named_children[0]
                
            if cond_node and cond_node.type == "parenthesized_expression":
                cond_node = cond_node.named_children[0]
                
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
            
        elif node.type in ("expression_statement", "block", "function_definition", "method_declaration", "class_body", "class_declaration", "program", "parenthesized_expression"):
            for child in node.named_children:
                self._visit(child)
            return ""
            
        else:
            for child in node.named_children:
                self._visit(child)
            return ""
