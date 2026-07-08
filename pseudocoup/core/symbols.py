from typing import Dict, Optional, List

class MethodSignature:
    def __init__(self, name: str, params: List[str], return_type: Optional[str] = None):
        self.name = name
        self.params = params
        self.return_type = return_type

class ClassDefinition:
    def __init__(self, name: str, parent_classes: List[str]):
        self.name = name
        self.parent_classes = parent_classes
        self.methods: Dict[str, MethodSignature] = {}

class GlobalSymbolTable:
    """Stores all globally available references extracted from the file before compilation."""
    def __init__(self):
        self.imports: Dict[str, str] = {}              # alias -> FQN
        self.classes: Dict[str, ClassDefinition] = {}  # class_name -> Definition
        self.functions: Dict[str, MethodSignature] = {} # func_name -> Signature

    def register_import(self, alias: str, fqn: str):
        self.imports[alias] = fqn

    def register_class(self, class_name: str, parent_classes: List[str]) -> ClassDefinition:
        cls_def = ClassDefinition(class_name, parent_classes)
        self.classes[class_name] = cls_def
        return cls_def

    def register_function(self, name: str, params: List[str], return_type: Optional[str] = None):
        self.functions[name] = MethodSignature(name, params, return_type)
