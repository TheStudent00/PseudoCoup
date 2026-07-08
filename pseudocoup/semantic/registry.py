from typing import Dict, Any, Optional
import json
from ..core.models import TypeTag, Instruction, OpCode, WrapperPolicyError

class WrapperRegistry:
    def __init__(self):
        # fqn -> method_name -> {"returns": "ReturnType", "mapTo": "canonical_name"}
        self.registry: Dict[str, Dict[str, Dict[str, str]]] = {}
        
    def load_from_json(self, json_string: str):
        """Loads external wrapper definitions from a JSON schema."""
        data = json.loads(json_string)
        for fqn, methods in data.items():
            self.registry[fqn] = methods

    def register(self, fqn: str, method: str, return_type: str, map_to: str):
        """Manually registers a single external method mapping."""
        if fqn not in self.registry:
            self.registry[fqn] = {}
        self.registry[fqn][method] = {
            "returns": return_type,
            "mapTo": map_to
        }

    def get_return_type(self, fqn: str, method: str) -> Optional[TypeTag]:
        """Queries the expected return type of an external method."""
        if fqn in self.registry and method in self.registry[fqn]:
            ret = self.registry[fqn][method].get("returns")
            return TypeTag(ret) if ret else None
        return None

    def intercept_and_rewrite(self, instr: Instruction, target_type: TypeTag, method_name: str):
        """
        Intercepts a CALL or ATTR instruction on an external type.
        Checks if it's explicitly registered. If so, rewrites it.
        If not, throws a strict WrapperPolicyError.
        """
        fqn = target_type.name
        
        # Safe-Fail Protocol
        if fqn not in self.registry:
            raise WrapperPolicyError(
                f"Ecosystem Leakage: The external class '{fqn}' is imported but not registered "
                f"in the Wrapper Policy."
            )
            
        if method_name not in self.registry[fqn]:
            raise WrapperPolicyError(
                f"Ecosystem Leakage: Method '{method_name}' on external class '{fqn}' "
                f"is used but not mapped in the Wrapper Policy."
            )
            
        # Rewrite the instruction
        mapping = self.registry[fqn][method_name]
        canonical_name = mapping.get("mapTo")
        
        if canonical_name:
            if instr.op == OpCode.CALL:
                # E.g., Java's .size() mapped to pseudo's len()
                # Assuming args[0] was the target object reference
                instr.args[0] = canonical_name
                
            elif instr.op == OpCode.ATTR:
                instr.args[1] = canonical_name
                
        # Set the return type explicitly based on the registry
        ret_type_str = mapping.get("returns")
        if ret_type_str:
            instr.type_tag = TypeTag(ret_type_str)
