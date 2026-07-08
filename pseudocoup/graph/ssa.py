from typing import List, Dict, Set, DefaultDict
from collections import defaultdict
from ..core.models import ControlFlowGraph, BasicBlock, Instruction, OpCode

class SSABuilder:
    def __init__(self, cfg: ControlFlowGraph):
        self.cfg = cfg
        self.idom: Dict[int, int] = {}
        self.dom_tree: DefaultDict[int, List[int]] = defaultdict(list)
        self.df: DefaultDict[int, Set[int]] = defaultdict(set)
        
        self.defs: DefaultDict[str, Set[int]] = defaultdict(set)
        self.uses: DefaultDict[str, Set[int]] = defaultdict(set)
        
        self.var_counts: DefaultDict[str, int] = defaultdict(int)
        self.var_stacks: DefaultDict[str, List[str]] = defaultdict(list)
        
    def transform(self):
        """Transforms the given CFG into Static Single Assignment form."""
        if not self.cfg.entry:
            return
            
        self._compute_dominators()
        self._compute_dominance_frontiers()
        self._map_def_uses()
        self._insert_phi_nodes()
        self._rename_variables()

    def _compute_dominators(self):
        """Computes Immediate Dominators using a simple iterative approach."""
        blocks = list(self.cfg.blocks.values())
        entry_id = self.cfg.entry.id
        
        doms: Dict[int, Set[int]] = {}
        all_nodes = {b.id for b in blocks}
        
        for b in blocks:
            if b.id == entry_id:
                doms[b.id] = {entry_id}
            else:
                doms[b.id] = set(all_nodes)
                
        changed = True
        while changed:
            changed = False
            for b in blocks:
                if b.id == entry_id:
                    continue
                    
                new_dom = set(all_nodes)
                for p in b.preds:
                    if p.id in doms:
                        new_dom = new_dom.intersection(doms[p.id])
                new_dom.add(b.id)
                
                if doms[b.id] != new_dom:
                    doms[b.id] = new_dom
                    changed = True
                    
        # Compute idom from doms
        for b in blocks:
            if b.id == entry_id:
                continue
            strict_doms = doms[b.id] - {b.id}
            for d in strict_doms:
                # d is idom if there is no other node in strict_doms that is dominated by d
                # Wait, idom of b is the unique node d in strict_doms that is dominated by all other nodes in strict_doms.
                is_idom = True
                for other in strict_doms:
                    if d != other and d in doms[other]:
                        is_idom = False
                        break
                if is_idom:
                    self.idom[b.id] = d
                    self.dom_tree[d].append(b.id)
                    break

    def _compute_dominance_frontiers(self):
        """Computes Dominance Frontier for each block."""
        for b in self.cfg.blocks.values():
            if len(b.preds) >= 2:
                for p in b.preds:
                    runner = p.id
                    while runner != self.idom.get(b.id, -1):
                        self.df[runner].add(b.id)
                        runner = self.idom.get(runner, -1)
                        if runner == -1:
                            break

    def _map_def_uses(self):
        """Records definitions and uses to find multi-assigned variables."""
        for b in self.cfg.blocks.values():
            for instr in b.instructions:
                if instr.dest:
                    self.defs[instr.dest].add(b.id)
                for arg in instr.args:
                    if isinstance(arg, str) and not arg.startswith('t'): 
                        # Only track true variables, assuming temps are already SSA
                        self.uses[arg].add(b.id)

    def _insert_phi_nodes(self):
        """Inserts PHI nodes at dominance frontiers for variables assigned in multiple blocks."""
        for v, defining_blocks in self.defs.items():
            if len(defining_blocks) <= 1:
                continue # Already single assignment across blocks
                
            worklist = list(defining_blocks)
            has_already = set()
            
            while worklist:
                n = worklist.pop(0)
                for d in self.df[n]:
                    if d not in has_already:
                        has_already.add(d)
                        block = self.cfg.blocks[d]
                        # Create empty PHI node (args filled in later during rename)
                        phi_instr = Instruction(OpCode.PHI, dest=v, args=[])
                        block.instructions.insert(0, phi_instr)
                        
                        if d not in defining_blocks:
                            worklist.append(d)

    def _rename_variables(self):
        """Walks the dominator tree to version variables and resolve PHI arguments."""
        self.var_counts.clear()
        self.var_stacks.clear()
        
        self._rename(self.cfg.entry)
        
    def _rename(self, block: BasicBlock):
        # Dictionary to track how many pushes happened in this block, to pop later
        pushed_vars = defaultdict(int)
        
        for instr in block.instructions:
            # Rewrite Uses (skip PHI arguments, they are populated by predecessors)
            if instr.op != OpCode.PHI:
                for i, arg in enumerate(instr.args):
                    if isinstance(arg, str) and arg in self.var_stacks and self.var_stacks[arg]:
                        instr.args[i] = self.var_stacks[arg][-1]
                        
            # Version Definitions
            if instr.dest:
                v = instr.dest
                # Only rename original variables, if dest already has a version, it might be an issue.
                # Here we assume dest is the original string name.
                orig_v = v.split('_')[0] if '_' in v else v
                count = self.var_counts[orig_v]
                self.var_counts[orig_v] += 1
                
                new_v = f"{orig_v}_{count}"
                instr.dest = new_v
                self.var_stacks[orig_v].append(new_v)
                pushed_vars[orig_v] += 1

        # Populate PHI nodes in successor blocks
        for succ in block.succs:
            for instr in succ.instructions:
                if instr.op == OpCode.PHI:
                    # Look up the original variable name by stripping the version if it was renamed
                    orig_v = instr.dest.split('_')[0] if '_' in instr.dest else instr.dest
                    if self.var_stacks[orig_v]:
                        current_v = self.var_stacks[orig_v][-1]
                        instr.args.append((block.id, current_v))
                    else:
                        instr.args.append((block.id, "undef"))

        # Recurse down dominator tree
        for child_id in self.dom_tree[block.id]:
            self._rename(self.cfg.blocks[child_id])
            
        # Pop variables pushed in this block
        for orig_v, num_pushed in pushed_vars.items():
            for _ in range(num_pushed):
                self.var_stacks[orig_v].pop()
