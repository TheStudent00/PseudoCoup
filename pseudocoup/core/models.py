from enum import Enum, auto
from typing import List, Any, Optional, Dict

class OpCode(Enum):
    ASSIGN = auto()
    CALL = auto()
    ATTR = auto()
    BRANCH = auto()
    JUMP = auto()
    PHI = auto()
    RETURN = auto()

class TypeTag:
    """Base class for propagated semantic types."""
    def __init__(self, name: str):
        self.name = name
    
    def __repr__(self):
        return self.name
    
    def __eq__(self, other):
        return isinstance(other, TypeTag) and self.name == other.name

class Instruction:
    def __init__(self, op: OpCode, dest: Optional[str] = None, args: List[Any] = None):
        self.op = op
        self.dest = dest
        self.args = args or []
        self.type_tag: Optional[TypeTag] = None
        
    def __str__(self):
        args_str = ", ".join(str(a) for a in self.args)
        if self.dest:
            return f"{self.dest} = {self.op.name} {args_str}"
        return f"{self.op.name} {args_str}"

class BasicBlock:
    def __init__(self, block_id: int):
        self.id = block_id
        self.instructions: List[Instruction] = []
        self.preds: List['BasicBlock'] = []
        self.succs: List['BasicBlock'] = []
        
    def __repr__(self):
        return f"BasicBlock({self.id})"

class ControlFlowGraph:
    def __init__(self):
        self.entry: Optional[BasicBlock] = None
        self.blocks: Dict[int, BasicBlock] = {}
        self._next_id = 0
        
    def get_next_id(self) -> int:
        idx = self._next_id
        self._next_id += 1
        return idx

class TypeMismatchError(Exception):
    """Raised when Phi node branches have conflicting types, or type propagation fails."""
    pass

class WrapperPolicyError(Exception):
    """Raised when an external ecosystem dependency is imported but not wrapped."""
    pass

class PseudoNode:
    """Synthetic AST Node for Egress generators."""
    def __init__(self, node_type: str, text: str = ""):
        self.type = node_type
        self.text_val = text
        self.children: List['PseudoNode'] = []
        self.named_children: List['PseudoNode'] = []
        self.fields: Dict[str, 'PseudoNode'] = {}
        self._semantic_type: Optional[TypeTag] = None

    @property
    def text(self) -> bytes:
        return self.text_val.encode('utf8')

    def child_by_field_name(self, name: str) -> Optional['PseudoNode']:
        return self.fields.get(name)
