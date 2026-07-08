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
            for succ in block.succs:
                dfs(succ)
            post_order.append(block)
            
        dfs(self.cfg.entry)
        self.sorted_blocks = list(reversed(post_order))

    def _linearize(self):
        """Concatenates the instructions from the sorted blocks into a single stream."""
        for block in self.sorted_blocks:
            # Here we might inject explicit label targets if the target language supports/requires `goto`
            # For AST reconstruction (7.1.2), this linear stream can be parsed back into structured loops/ifs
            for instr in block.instructions:
                self.linearized_stream.append(instr)
                
    def export_decorated_ast(self) -> PseudoNode:
        """
        Takes the linearized stream and reconstructs structured AST nodes.
        Attaches `instr.type_tag` to the generated nodes.
        """
        root = PseudoNode("module")
        temp_map: Dict[str, PseudoNode] = {}
        
        for instr in self.linearized_stream:
            node = self._instr_to_node(instr, temp_map)
            if node:
                # If it's an assignment to a temp, just store it for inlining.
                if instr.dest and instr.dest.startswith("t") and instr.op in (OpCode.ASSIGN, OpCode.CALL, OpCode.ATTR):
                    temp_map[instr.dest] = node
                else:
                    root.named_children.append(node)
                    
        return root

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
