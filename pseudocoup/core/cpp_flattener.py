from tree_sitter import Node
from .builder import IRBuilder
from .models import Instruction, OpCode

class CppFlattener:
    """
    Flattens C++ Tree-Sitter AST nodes into the Universal Linear IR.
    """
    def __init__(self, builder: IRBuilder):
        self.builder = builder

    def flatten(self, root_node: Node):
        """Walks the C++ AST and emits linear IR instructions."""
        self._visit(root_node)

    def _visit(self, node: Node) -> str:
        """Visits a C++ node, emits instructions, and returns the temp variable holding its value."""
        if not node:
            return ""
            
        if node.type in ("declaration", "assignment_expression"):
            left = None
            right = None
            
            if node.type == "declaration":
                declarator = None
                for child in node.named_children:
                    if child.type == "init_declarator":
                        declarator = child
                        break
                
                if declarator:
                    left = declarator.child_by_field_name("declarator") or declarator.named_children[0]
                    right = declarator.child_by_field_name("value") or declarator.named_children[1]
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
            if args_node and args_node.type == "argument_list":
                for arg in args_node.named_children:
                    args.append(self._visit(arg))
            
            return self.builder.emit_temp_call(func_name, args)
            
        elif node.type == "binary_expression":
            # Check if this is a std::cout << operation
            is_cout = False
            curr = node
            operands = []
            
            # C++ shift operators are left-associative, so std::cout << "a" << "b" is nested (cout << "a") << "b"
            # We will flatten this sequence to see if the leftmost is std::cout
            def extract_cout(n):
                if n.type == "binary_expression" and n.child_by_field_name("operator") and n.child_by_field_name("operator").text.decode('utf8') == "<<":
                    left = n.child_by_field_name("left") or n.named_children[0]
                    right = n.child_by_field_name("right") or n.named_children[1]
                    res, is_cout_chain = extract_cout(left)
                    if is_cout_chain:
                        res.append(right)
                        return res, True
                else:
                    val = self._visit(n)
                    if val == "std::cout":
                        return [], True
                return [], False
                
            operator_node = node.child_by_field_name("operator")
            op_text = operator_node.text.decode('utf8') if operator_node else ""
            
            if op_text == "<<":
                extracted_args, is_cout = extract_cout(node)
                if is_cout:
                    # It is a std::cout chain!
                    # Filter out std::endl
                    args = []
                    for arg_node in extracted_args:
                        val = self._visit(arg_node)
                        if val != "std::endl":
                            args.append(val)
                    return self.builder.emit_temp_call("print", args)
                    
            # If not cout, standard binary expression
            left = node.child_by_field_name("left") or node.named_children[0]
            right = node.child_by_field_name("right") or node.named_children[1]
            l_val = self._visit(left)
            r_val = self._visit(right)
            # Dummy generic handling for now
            return self.builder.emit_temp_assign([f"{l_val} {op_text} {r_val}"])
            
        elif node.type in ("qualified_identifier", "scoped_identifier"):
            return node.text.decode('utf8')
            
        elif node.type == "identifier":
            return node.text.decode('utf8')
            
        elif node.type in ("number_literal", "string_literal", "true", "false"):
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
                
            if cond_node and cond_node.type == "condition_clause":
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
            if not cond_node and len(node.named_children) > 0 and node.named_children[0].type != "compound_statement":
                cond_node = node.named_children[0]
                
            if cond_node and cond_node.type == "condition_clause":
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
                    if child.type == "compound_statement":
                        body = child
                        break
                        
            if body:
                self._visit(body)
                
            self.builder.emit(Instruction(OpCode.JUMP, args=[loop_header_idx]))
            
            exit_idx = len(self.builder.instructions)
            branch_instr.args[1] = body_idx
            branch_instr.args[2] = exit_idx
            return ""
            
        elif node.type in ("expression_statement", "compound_statement", "function_definition", "translation_unit"):
            for child in node.named_children:
                self._visit(child)
            return ""
            
        else:
            for child in node.named_children:
                self._visit(child)
            return ""
