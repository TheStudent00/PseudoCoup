from typing import List, Optional, Any
from .models import Instruction, OpCode

class IRBuilder:
    def __init__(self):
        self.instructions: List[Instruction] = []
        self._temp_counter = 0

    def _next_temp(self) -> str:
        """Generates a monotonically incrementing temporary variable string (e.g., t1, t2)."""
        self._temp_counter += 1
        return f"t{self._temp_counter}"

    def emit(self, instruction: Instruction):
        """Appends an instruction to the sequential stream."""
        self.instructions.append(instruction)

    def emit_assign(self, dest: str, args: List[Any]) -> str:
        """Helper to emit an assignment and return the destination."""
        self.emit(Instruction(OpCode.ASSIGN, dest=dest, args=args))
        return dest

    def emit_temp_assign(self, args: List[Any]) -> str:
        """Helper to assign arguments to a new temp variable and return it."""
        dest = self._next_temp()
        return self.emit_assign(dest, args)

    def emit_call(self, dest: str, func: str, args: List[str]) -> str:
        self.emit(Instruction(OpCode.CALL, dest=dest, args=[func] + args))
        return dest

    def emit_temp_call(self, func: str, args: List[str]) -> str:
        dest = self._next_temp()
        return self.emit_call(dest, func, args)
