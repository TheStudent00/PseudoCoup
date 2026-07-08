from typing import List, Set
from ..core.models import ControlFlowGraph, BasicBlock, Instruction, OpCode

class CFGBuilder:
    def __init__(self, instructions: List[Instruction]):
        self.instructions = instructions
        self.cfg = ControlFlowGraph()
        
    def build(self) -> ControlFlowGraph:
        """Slices instructions into basic blocks and wires the directed edges."""
        if not self.instructions:
            return self.cfg
            
        blocks = self._slice_basic_blocks()
        self._wire_edges(blocks)
        self._prune_unreachable()
        
        return self.cfg
        
    def _slice_basic_blocks(self) -> List[BasicBlock]:
        """Identifies leaders and partitions instructions into BasicBlocks."""
        leaders = set()
        leaders.add(0) # First instruction is always a leader
        
        for i, instr in enumerate(self.instructions):
            if instr.op in (OpCode.BRANCH, OpCode.JUMP, OpCode.RETURN):
                if i + 1 < len(self.instructions):
                    leaders.add(i + 1)
            
            # Note: in a true linear IR, jump targets would be explicit labels.
            # Since our flattener currently only outputs AST-level ops without explicit jump targets,
            # we rely on the higher level structural knowledge. We'll simplify the AST to CFG mapping
            # by directly generating structural blocks from the flattener if explicit jump targets aren't used.
            # Assuming here the flattener inserted JUMP instructions pointing to target indices.
            if instr.op in (OpCode.BRANCH, OpCode.JUMP):
                for target_idx in instr.args:
                    if isinstance(target_idx, int):
                        leaders.add(target_idx)
                        
        sorted_leaders = sorted(list(leaders))
        blocks = []
        
        for idx, leader_start in enumerate(sorted_leaders):
            end_idx = sorted_leaders[idx+1] if idx + 1 < len(sorted_leaders) else len(self.instructions)
            
            block = BasicBlock(self.cfg.get_next_id())
            block.instructions = self.instructions[leader_start:end_idx]
            blocks.append(block)
            self.cfg.blocks[block.id] = block
            self.cfg.leader_to_block_id[leader_start] = block.id
            
            if idx == 0:
                self.cfg.entry = block
                
        return blocks
        
    def _wire_edges(self, blocks: List[BasicBlock]):
        """Wires predecessor and successor arrays based on jumps."""
        # A mapping of starting instruction index to the block
        idx_to_block = {}
        curr_idx = 0
        for block in blocks:
            idx_to_block[curr_idx] = block
            curr_idx += len(block.instructions)
            
        for idx, block in enumerate(blocks):
            if not block.instructions:
                continue
                
            last_instr = block.instructions[-1]
            if last_instr.op == OpCode.JUMP:
                target_idx = last_instr.args[0]
                target_block = idx_to_block.get(target_idx)
                if target_block:
                    self._link(block, target_block)
            elif last_instr.op == OpCode.BRANCH:
                true_idx = last_instr.args[1]
                false_idx = last_instr.args[2]
                
                true_block = idx_to_block.get(true_idx)
                false_block = idx_to_block.get(false_idx)
                
                if true_block: self._link(block, true_block)
                if false_block: self._link(block, false_block)
            elif last_instr.op != OpCode.RETURN:
                # Fall-through to next block
                if idx + 1 < len(blocks):
                    self._link(block, blocks[idx + 1])
                    
    def _link(self, source: BasicBlock, target: BasicBlock):
        if target not in source.succs:
            source.succs.append(target)
        if source not in target.preds:
            target.preds.append(source)
            
    def _prune_unreachable(self):
        """Runs DFS from entry block to mark and delete dead code blocks."""
        if not self.cfg.entry:
            return
            
        visited: Set[int] = set()
        
        def dfs(block: BasicBlock):
            if block.id in visited:
                return
            visited.add(block.id)
            for succ in block.succs:
                dfs(succ)
                
        dfs(self.cfg.entry)
        
        # Prune dead blocks
        dead_blocks = [b_id for b_id in self.cfg.blocks if b_id not in visited]
        for b_id in dead_blocks:
            # Note: actual pruning would require removing edges from predecessors
            del self.cfg.blocks[b_id]
            
        assert self.cfg.entry is not None, "CFG entry block cannot be pruned!"
