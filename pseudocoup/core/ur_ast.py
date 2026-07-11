from typing import Any, List, Optional

class URNode:
    """Base class for all Universal Rich AST nodes."""
    def __init__(self):
        self.metadata: dict[str, Any] = {}
        # metadata will hold properties hydrated from the Ledger
        
class ModuleNode(URNode):
    def __init__(self, body: List['URNode']):
        super().__init__()
        self.body = body

class FunctionDefNode(URNode):
    def __init__(self, name: str, args: List['IdentifierNode'], body: List['URNode'], return_type: Optional[str] = None):
        super().__init__()
        self.name = name
        self.args = args
        self.body = body
        self.return_type = return_type

class MethodDefNode(URNode):
    def __init__(self, name: str, args: List['IdentifierNode'], body: List['URNode'], return_type: Optional[str] = None):
        super().__init__()
        self.name = name
        self.args = args
        self.body = body
        self.return_type = return_type

class ClassDefNode(URNode):
    def __init__(self, name: str, bases: List[str], methods: List['MethodDefNode'], fields: List['AssignmentNode']):
        super().__init__()
        self.name = name
        self.bases = bases
        self.methods = methods
        self.fields = fields

class AssignmentNode(URNode):
    def __init__(self, left: 'URNode', right: 'URNode'):
        super().__init__()
        self.left = left
        self.right = right

class BinaryOpNode(URNode):
    def __init__(self, left: 'URNode', right: 'URNode', operator: str):
        super().__init__()
        self.left = left
        self.right = right
        self.operator = operator

class CallNode(URNode):
    def __init__(self, func_name: str, args: List['URNode']):
        super().__init__()
        self.func_name = func_name
        self.args = args

class IdentifierNode(URNode):
    def __init__(self, name: str):
        super().__init__()
        self.name = name

class LiteralNode(URNode):
    def __init__(self, value: Any):
        super().__init__()
        self.value = value

class ReturnNode(URNode):
    def __init__(self, value: 'URNode'):
        super().__init__()
        self.value = value

class IfNode(URNode):
    def __init__(self, condition: 'URNode', body: List['URNode'], orelse: Optional['URNode'] = None):
        super().__init__()
        self.condition = condition
        self.body = body
        self.orelse = orelse

class WhileNode(URNode):
    def __init__(self, condition: 'URNode', body: List['URNode']):
        super().__init__()
        self.condition = condition
        self.body = body

class ForNode(URNode):
    def __init__(self, target: 'URNode', iter: 'URNode', body: List['URNode']):
        super().__init__()
        self.target = target
        self.iter = iter
        self.body = body

class TryCatchNode(URNode):
    """
    Due to Go's constraints, TryCatchNode acts as a broad protected boundary block.
    """
    def __init__(self, body: List['URNode'], handlers: List['URNode']):
        super().__init__()
        self.body = body
        self.handlers = handlers

class ListNode(URNode):
    def __init__(self, elements: List['URNode']):
        super().__init__()
        self.elements = elements

class DictNode(URNode):
    def __init__(self, keys: List['URNode'], values: List['URNode']):
        super().__init__()
        self.keys = keys
        self.values = values

class SubscriptNode(URNode):
    def __init__(self, value: 'URNode', slice: 'URNode'):
        super().__init__()
        self.value = value
        self.slice = slice

class AttributeNode(URNode):
    def __init__(self, value: 'URNode', attr: str):
        super().__init__()
        self.value = value
        self.attr = attr


