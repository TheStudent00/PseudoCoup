from tree_sitter import Node
from .builder import IRBuilder
from .models import Instruction, OpCode

class CSharpFlattener:
    """
    Flattens C# Tree-Sitter AST nodes into the Universal Linear IR.
    """
    def __init__(self, builder: IRBuilder):
        self.builder = builder

    def flatten(self, root_node: Node):
        """Walks the C# AST and emits linear IR instructions."""
        self._visit(root_node)

    def _visit(self, node: Node) -> str:
        """Visits a C# node, emits instructions, and returns the temp variable holding its value."""
        if not node:
            return ""
            
        if node.type in ("local_declaration_statement", "assignment_expression"):
            left = None
            right = None
            
            if node.type == "local_declaration_statement":
                decl = None
                for child in node.named_children:
                    if child.type == "variable_declaration":
                        decl = child
                        break
                
                if decl:
                    declarator = None
                    for child in decl.named_children:
                        if child.type == "variable_declarator":
                            declarator = child
                            break
                            
                    if declarator and len(declarator.named_children) >= 2:
                        left = declarator.named_children[0]
                        right = declarator.named_children[1]
            elif node.type == "assignment_expression":
                left = node.child_by_field_name("left") or node.named_children[0]
                right = node.child_by_field_name("right") or node.named_children[1]
                
            if left and right:
                dest = left.text.decode('utf8')
                val = self._visit(right)
                self.builder.emit_assign(dest, [val])
                return dest
                
        elif node.type == "invocation_expression":
            func_node = node.child_by_field_name("function") or node.named_children[0]
            args_node = node.child_by_field_name("arguments") or node.named_children[1]
            
            func_name = self._visit(func_node) if func_node else ""
            
            if func_name == "Console.WriteLine" or func_name == "Console.Write":
                func_name = "print"
                
            args = []
            if args_node and args_node.type == "argument_list":
                for arg in args_node.named_children:
                    # In C#, an argument is usually wrapped in an 'argument' node
                    val_node = arg.named_children[0] if arg.type == "argument" and arg.named_children else arg
                    args.append(self._visit(val_node))
            
            return self.builder.emit_temp_call(func_name, args)
            
        elif node.type == "member_access_expression":
            # object.property
            obj = node.child_by_field_name("expression") or node.named_children[0]
            attr = node.child_by_field_name("name") or node.named_children[1]
            
            obj_val = self._visit(obj) if obj else ""
            attr_name = attr.text.decode('utf8') if attr else ""
            
            if obj_val == "Console" and attr_name in ("WriteLine", "Write"):
                return f"{obj_val}.{attr_name}"
            
            dest = self.builder._next_temp()
            self.builder.emit(Instruction(OpCode.ATTR, dest=dest, args=[obj_val, attr_name]))
            return dest
            
        elif node.type == "identifier":
            return node.text.decode('utf8')
            
        elif node.type in ("integer_literal", "real_literal", "string_literal", "boolean_literal"):
            val = node.text.decode('utf8')
            if node.type == "boolean_literal":
                val = val.capitalize() # true -> True
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
            
        elif node.type in ("while_statement", "for_statement"):
            loop_header_idx = len(self.builder.instructions)
            
            cond_node = node.child_by_field_name("condition")
            if not cond_node and len(node.named_children) > 0 and node.named_children[0].type != "block":
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
            
        elif node.type in ("expression_statement", "block", "method_declaration", "class_declaration", "declaration_list", "compilation_unit"):
            for child in node.named_children:
                self._visit(child)
            return ""
            
        else:
            for child in node.named_children:
                self._visit(child)
            return ""
