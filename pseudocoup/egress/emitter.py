from typing import List, Dict, Any
from ..core.models import ControlFlowGraph, BasicBlock, Instruction, OpCode, PseudoNode
from ..core.constants import NODE_ASSIGNMENT, NODE_CALL, NODE_IDENTIFIER, NODE_STRING, NODE_INTEGER

class GraphEmitter:
    def __init__(self, cfg: ControlFlowGraph):
        self.cfg = cfg
        self.sorted_blocks: List[BasicBlock] = []
        self.linearized_stream: List[Instruction] = []

    def emit(self) -> List[Instruction]:
        """Deconstructs the SSA CFG and linearizes it for target code generation."""
        if not self.cfg.entry:
            return []

        self._deconstruct_ssa()
        self._topological_sort()
        self._linearize()
        
        return self.linearized_stream

    def _deconstruct_ssa(self):
        """Eliminates PHI nodes by injecting explicit assignments into predecessor blocks."""
        for block in self.cfg.blocks.values():
            # Collect all PHI nodes in this block
            phi_nodes = [instr for instr in block.instructions if instr.op == OpCode.PHI]
            
            for phi in phi_nodes:
                dest = phi.dest
                for pred_id, src_var in phi.args:
                    if src_var == "undef":
                        continue
                    
                    # Find the predecessor block
                    pred_block = self.cfg.blocks.get(pred_id)
                    if not pred_block:
                        continue
                        
                    # Inject explicit assignment: dest = src_var
                    # Must be inserted before the final JUMP/BRANCH instruction of the predecessor
                    assign_instr = Instruction(OpCode.ASSIGN, dest=dest, args=[src_var])
                    # Assuming type tags were fully populated, copy it over
                    assign_instr.type_tag = phi.type_tag
                    
                    if pred_block.instructions and pred_block.instructions[-1].op in (OpCode.BRANCH, OpCode.JUMP):
                        pred_block.instructions.insert(-1, assign_instr)
                    else:
                        pred_block.instructions.append(assign_instr)
                        
            # Remove the PHI nodes from the current block
            block.instructions = [instr for instr in block.instructions if instr.op != OpCode.PHI]

    def _topological_sort(self):
        """Sorts basic blocks such that dominators precede their dominated blocks (Reverse Post-Order)."""
        visited = set()
        post_order = []
        
        def dfs(block: BasicBlock):
            if block.id in visited:
                return
            visited.add(block.id)
            for succ in reversed(block.succs):
                dfs(succ)
            post_order.append(block)
            
        dfs(self.cfg.entry)
        self.sorted_blocks = list(reversed(post_order))

    def _linearize(self):
        """Concatenates the instructions from the sorted blocks into a single stream and rewrites JUMP/BRANCH targets."""
        block_starts = {}
        curr_idx = 0
        for block in self.sorted_blocks:
            block_starts[block.id] = curr_idx
            curr_idx += len(block.instructions)
            
        for block in self.sorted_blocks:
            for instr in block.instructions:
                if instr.op == OpCode.JUMP:
                    old_target = instr.args[0]
                    target_block_id = self.cfg.leader_to_block_id.get(old_target)
                    if target_block_id is not None:
                        instr.args[0] = block_starts[target_block_id]
                elif instr.op == OpCode.BRANCH:
                    old_true = instr.args[1]
                    old_false = instr.args[2]
                    
                    true_block_id = self.cfg.leader_to_block_id.get(old_true)
                    if true_block_id is not None:
                        instr.args[1] = block_starts[true_block_id]
                        
                    false_block_id = self.cfg.leader_to_block_id.get(old_false)
                    if false_block_id is not None:
                        instr.args[2] = block_starts[false_block_id]
                        
                self.linearized_stream.append(instr)
                
        self._compute_use_counts()
        
    def _compute_use_counts(self):
        self.use_counts = {}
        for instr in self.linearized_stream:
            if instr.op in (OpCode.ASSIGN, OpCode.ATTR, OpCode.CALL):
                for arg in instr.args:
                    if isinstance(arg, str) and arg.startswith("t"):
                        self.use_counts[arg] = self.use_counts.get(arg, 0) + 1
            elif instr.op == OpCode.BRANCH:
                arg = instr.args[0]
                if isinstance(arg, str) and arg.startswith("t"):
                    self.use_counts[arg] = self.use_counts.get(arg, 0) + 1
                
    def export_decorated_ast(self) -> PseudoNode:
        """
        Takes the linearized stream and reconstructs structured AST nodes.
        Attaches `instr.type_tag` to the generated nodes.
        """
        root = PseudoNode("module")
        temp_map: Dict[str, PseudoNode] = {}
        
        self._parse_stream(0, len(self.linearized_stream), root, temp_map)
        return root

    def _parse_stream(self, start_idx: int, end_idx: int, parent: PseudoNode, temp_map: Dict[str, PseudoNode]):
        i = start_idx
        while i < end_idx:
            instr = self.linearized_stream[i]
            
            if instr.op == OpCode.BRANCH:
                cond_val = instr.args[0]
                true_idx = instr.args[1]
                false_idx = instr.args[2]
                
                # Check if it's a loop by looking at the instruction right before false_idx
                jump_body = self.linearized_stream[false_idx - 1] if false_idx - 1 < len(self.linearized_stream) else None
                if jump_body and jump_body.op == OpCode.JUMP and jump_body.args[0] <= i:
                    # It's a while loop
                    loop_node = PseudoNode("while_statement")
                    cond_node = self._literal_to_node(cond_val) if isinstance(cond_val, str) and cond_val not in temp_map else temp_map.get(cond_val, self._literal_to_node(cond_val))
                    loop_node.fields['condition'] = cond_node
                    
                    body_node = PseudoNode("block")
                    self._parse_stream(true_idx, false_idx - 1, body_node, temp_map)
                    loop_node.fields['body'] = body_node
                    
                    parent.named_children.append(loop_node)
                    i = false_idx
                    continue
                else:
                    # It's an IF statement
                    if_node = PseudoNode("if_statement")
                    cond_node = self._literal_to_node(cond_val) if isinstance(cond_val, str) and cond_val not in temp_map else temp_map.get(cond_val, self._literal_to_node(cond_val))
                    if_node.fields['condition'] = cond_node
                    
                    jump_true = self.linearized_stream[false_idx - 1] if false_idx - 1 < len(self.linearized_stream) else None
                    merge_idx = jump_true.args[0] if jump_true and jump_true.op == OpCode.JUMP else false_idx
                    
                    consequence = PseudoNode("block")
                    self._parse_stream(true_idx, false_idx - 1, consequence, temp_map)
                    if_node.fields['consequence'] = consequence
                    
                    if merge_idx > false_idx:
                        alternative = PseudoNode("block")
                        self._parse_stream(false_idx, merge_idx - 1, alternative, temp_map)
                        if_node.fields['alternative'] = alternative
                    
                    parent.named_children.append(if_node)
                    i = merge_idx
                    continue

            elif instr.op == OpCode.JUMP:
                # Should be consumed by the BRANCH parsing, but just in case
                i += 1
                continue
                
            else:
                node = self._instr_to_node(instr, temp_map)
                if node:
                    if instr.dest and instr.dest.startswith("t") and instr.op in (OpCode.ASSIGN, OpCode.CALL, OpCode.ATTR):
                        temp_map[instr.dest] = node
                        if self.use_counts.get(instr.dest, 0) == 0:
                            if parent:
                                parent.named_children.append(node)
                    else:
                        if parent:
                            parent.named_children.append(node)
            i += 1

    def _instr_to_node(self, instr: Instruction, temp_map: Dict[str, PseudoNode]) -> PseudoNode:
        """Converts a single instruction to a PseudoNode, inlining temps."""
        if instr.op == OpCode.ASSIGN:
            # Inline RHS if it's a temp, else it's a literal/identifier
            rhs_val = instr.args[0]
            if isinstance(rhs_val, str) and rhs_val in temp_map:
                rhs_node = temp_map[rhs_val]
            else:
                rhs_node = self._literal_to_node(rhs_val)
                
            if instr.dest and not instr.dest.startswith("t"):
                # Real assignment statement
                assign_node = PseudoNode(NODE_ASSIGNMENT)
                lhs_node = PseudoNode(NODE_IDENTIFIER, text=instr.dest)
                assign_node.fields['left'] = lhs_node
                assign_node.fields['right'] = rhs_node
                assign_node._semantic_type = instr.type_tag
                return assign_node
            else:
                # Temp assignment, return RHS to be stored in temp_map
                rhs_node._semantic_type = instr.type_tag
                return rhs_node
                
        elif instr.op == OpCode.CALL:
            call_node = PseudoNode(NODE_CALL)
            func_name = instr.args[0]
            call_node.fields['function'] = PseudoNode(NODE_IDENTIFIER, text=func_name)
            
            args_node = PseudoNode("argument_list")
            for arg in instr.args[1:]:
                if isinstance(arg, str) and arg in temp_map:
                    args_node.named_children.append(temp_map[arg])
                else:
                    args_node.named_children.append(self._literal_to_node(arg))
                    
            call_node.fields['arguments'] = args_node
            call_node._semantic_type = instr.type_tag
            return call_node
            
        # Add BRANCH/JUMP reconstruction logic here if needed for structural recovery
        return None
        
    def _literal_to_node(self, val: Any) -> PseudoNode:
        if isinstance(val, str):
            if val.startswith(('"', "'")):
                return PseudoNode(NODE_STRING, text=val)
            elif val.isdigit():
                return PseudoNode(NODE_INTEGER, text=val)
            else:
                return PseudoNode(NODE_IDENTIFIER, text=val)
        return PseudoNode(NODE_IDENTIFIER, text=str(val))
