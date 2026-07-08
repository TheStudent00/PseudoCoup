from typing import Dict, List, Set
from ..core.models import ControlFlowGraph, Instruction, OpCode, TypeTag, TypeMismatchError
from ..core.symbols import GlobalSymbolTable

# Predefined Primitive Type Tags
IntType = TypeTag("Int")
StringType = TypeTag("String")
BoolType = TypeTag("Bool")
FloatType = TypeTag("Float")
VoidType = TypeTag("Void")
UnknownType = TypeTag("Unknown")

class TypePropagator:
    def __init__(self, cfg: ControlFlowGraph, symbol_table: GlobalSymbolTable):
        self.cfg = cfg
        self.symbol_table = symbol_table
        self.type_env: Dict[str, TypeTag] = {}
        
    def propagate(self):
        """Propagates types forward through the CFG in topological order."""
        if not self.cfg.entry:
            return
            
        # First, seed parameter types (if available) and initial constants
        self._seed_initial_types()
        
        # Then, propagate through basic blocks in topological order
        # Since we have back-edges (loops), a worklist algorithm is more robust
        # than strict topological sort to handle reaching definitions.
        self._worklist_propagate()

    def _seed_initial_types(self):
        """Seeds initial type assumptions from the GlobalSymbolTable."""
        # E.g., function parameters. In a real impl, we'd iterate over function signatures
        pass

    def _worklist_propagate(self):
        """Iterates blocks until type environments reach a fixed point."""
        worklist = [self.cfg.entry.id]
        in_worklist = {self.cfg.entry.id}
        
        # Ensure we visit blocks at least once
        for b_id in self.cfg.blocks:
            if b_id not in in_worklist:
                worklist.append(b_id)
                in_worklist.add(b_id)
                
        while worklist:
            b_id = worklist.pop(0)
            in_worklist.remove(b_id)
            block = self.cfg.blocks[b_id]
            
            changed = False
            for instr in block.instructions:
                if self._process_instruction(instr):
                    changed = True
                    
            if changed:
                for succ in block.succs:
                    if succ.id not in in_worklist:
                        worklist.append(succ.id)
                        in_worklist.add(succ.id)

    def _process_instruction(self, instr: Instruction) -> bool:
        """Determines the type of an instruction. Returns True if the dest type changed."""
        if not instr.dest:
            return False
            
        old_type = self.type_env.get(instr.dest)
        new_type = UnknownType
        
        if instr.op == OpCode.ASSIGN:
            # Type of LHS is type of RHS
            arg = instr.args[0]
            if isinstance(arg, str) and arg.startswith(('"', "'")):
                new_type = StringType
            elif isinstance(arg, str) and arg.isdigit():
                new_type = IntType
            elif isinstance(arg, str) and arg in ["True", "False"]:
                new_type = BoolType
            elif isinstance(arg, str) and arg in self.type_env:
                new_type = self.type_env[arg]
                
        elif instr.op == OpCode.CALL:
            func_name = instr.args[0]
            # 1. Check GlobalSymbolTable for imports (external types)
            if func_name in self.symbol_table.imports:
                fqn = self.symbol_table.imports[func_name]
                new_type = TypeTag(fqn)
            # 2. Check local functions
            elif func_name in self.symbol_table.functions:
                ret = self.symbol_table.functions[func_name].return_type
                new_type = TypeTag(ret) if ret else UnknownType
            else:
                # Placeholder for Wrapper Registry intercept logic 
                # (to be expanded in Part 6)
                new_type = UnknownType
                
        elif instr.op == OpCode.ATTR:
            obj_name = instr.args[0]
            attr_name = instr.args[1]
            obj_type = self.type_env.get(obj_name, UnknownType)
            # Placeholder for Wrapper Registry attribute resolution
            new_type = UnknownType
            
        elif instr.op == OpCode.PHI:
            new_type = self._validate_and_merge_phi(instr)
            
        if old_type != new_type:
            self.type_env[instr.dest] = new_type
            instr.type_tag = new_type
            return True
            
        return False

    def _validate_and_merge_phi(self, instr: Instruction) -> TypeTag:
        """Ensures all branches converging at a PHI node provide identical types."""
        resolved_types: Set[TypeTag] = set()
        
        for pred_id, arg_var in instr.args:
            if arg_var == "undef":
                continue
            arg_type = self.type_env.get(arg_var, UnknownType)
            if arg_type != UnknownType:
                resolved_types.add(arg_type)
                
        if not resolved_types:
            return UnknownType
            
        if len(resolved_types) > 1:
            types_str = ", ".join(t.name for t in resolved_types)
            raise TypeMismatchError(
                f"PHI node '{instr.dest}' merges conflicting types: [{types_str}]. "
                "Type mutated dynamically across branches."
            )
            
        return next(iter(resolved_types))
