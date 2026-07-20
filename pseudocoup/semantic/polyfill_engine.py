from pseudocoup.core.ur_ast import (
    ModuleNode, FunctionDefNode, MethodDefNode, ClassDefNode, AssignmentNode,
    BinaryOpNode, CallNode, IdentifierNode, LiteralNode, AttributeNode
)
from pseudocoup.core.ledger import Ledger

class PolyfillEngine:
    """
    Semantic Rewriter that intercepts the UR-AST before Egress.
    It replaces fundamentally incompatible primitives (e.g. Unsigned Ints, Pointers)
    with mathematically robust target-language simulators.
    """
    def __init__(self, ledger: Ledger, target_lang: str):
        self.ledger = ledger
        self.target_lang = target_lang

    def apply_polyfills(self, module: ModuleNode) -> ModuleNode:
        # Traverse and rewrite the entire UR-AST
        module.body = [self._walk(child) for child in module.body]
        return module

    def _walk(self, node):
        if not node:
            return None

        # Recursively walk children
        if isinstance(node, (FunctionDefNode, MethodDefNode)):
            node.body = [self._walk(c) for c in node.body]
        elif isinstance(node, ClassDefNode):
            node.methods = [self._walk(c) for c in node.methods]
            node.fields = [self._walk(c) for c in node.fields]
        elif isinstance(node, AssignmentNode):
            node.left = self._walk(node.left)
            node.right = self._walk(node.right)
        elif isinstance(node, BinaryOpNode):
            node.left = self._walk(node.left)
            node.right = self._walk(node.right)
            
            # PHASE 1: PRIMITIVE MATH ENFORCERS (Unsigned Ints)
            # If we detect a bitwise shift (>>) on a uint64_t, we must rewrite the AST
            # to use a polyfill method that enforces logical shifts in languages like Dart.
            if node.operator in ('>', '>>', '&', '|', '^', '~'):
                var_name = self._extract_identifier_name(node.left)
                if var_name:
                    # Check metadata or Ledger for original C++ type
                    original_type = getattr(node.left, 'metadata', {}).get('type', '')
                    if not original_type:
                        original_type = self.ledger.get_type("", var_name) or self.ledger.get_type("calculateCalleeSaves", var_name) or ''
                    
                    if original_type in ('uint32_t', 'uint64_t', 'unsigned int', 'regMaskTP'):
                        return self._rewrite_to_unsigned_polyfill(node, original_type)

        elif isinstance(node, CallNode):
            func_name = self._extract_identifier_name(node.func_name)
            node.args = [self._walk(arg) for arg in node.args]
            
            # PHASE 2: MEMORY SANDBOX (Pointers & Malloc)
            if func_name == 'malloc' or func_name == 'new':
                return self._rewrite_to_virtual_ram_alloc(node)
                
            # PHASE 3: HARDWARE INTRINSICS
            if func_name and func_name.startswith('__builtin_'):
                return self._rewrite_intrinsic(node, func_name)

        return node

    def _extract_identifier_name(self, node) -> str:
        if isinstance(node, IdentifierNode):
            return node.name
        if isinstance(node, AttributeNode):
            return node.attr
        return None

    def _rewrite_to_unsigned_polyfill(self, node: BinaryOpNode, cpp_type: str):
        """
        Rewrites: `mask >> 1`  =>  `PseudoUint64.shiftRight(mask, 1)`
        """
        polyfill_class = "PseudoUint64" if "64" in cpp_type else "PseudoUint32"
        
        op_map = {
            '>>': 'shiftRightLogical',
            '<<': 'shiftLeft',
            '&': 'bitwiseAnd',
            '|': 'bitwiseOr',
            '~': 'bitwiseNot'
        }
        method_name = op_map.get(node.operator, "unknownOp")
        
        # Build new AST CallNode to replace the BinaryOpNode
        func_ast = AttributeNode(
            value=IdentifierNode(name=polyfill_class), 
            attr=method_name
        )
        return CallNode(func_name=func_ast, args=[node.left, node.right])

    def _rewrite_to_virtual_ram_alloc(self, node: CallNode):
        """
        Rewrites: `malloc(24)` => `VirtualRAM.allocate(24)`
        """
        func_ast = AttributeNode(
            value=IdentifierNode(name="VirtualRAM"), 
            attr="allocate"
        )
        return CallNode(func_name=func_ast, args=node.args)

    def _rewrite_intrinsic(self, node: CallNode, intrinsic: str):
        """
        Rewrites: `__builtin_popcount(x)` => `HardwarePolyfill.popcount(x)`
        """
        clean_name = intrinsic.replace('__builtin_', '')
        func_ast = AttributeNode(
            value=IdentifierNode(name="HardwarePolyfill"), 
            attr=clean_name
        )
        return CallNode(func_name=func_ast, args=node.args)
