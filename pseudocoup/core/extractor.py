from typing import List, Optional
from tree_sitter import Node
from .symbols import GlobalSymbolTable
from .constants import (
    NODE_IMPORT, NODE_IMPORT_FROM, NODE_CLASS_DEFINITION, 
    NODE_FUNCTION_DEFINITION, NODE_IDENTIFIER
)

class ContextExtractor:
    def __init__(self):
        self.table = GlobalSymbolTable()

    def extract(self, root_node: Node) -> GlobalSymbolTable:
        """Walks the AST to populate the GlobalSymbolTable."""
        self._visit(root_node)
        return self.table

    def _visit(self, node: Node):
        if node.type == NODE_IMPORT:
            self._handle_import(node)
        elif node.type == NODE_IMPORT_FROM:
            self._handle_import_from(node)
        elif node.type == NODE_CLASS_DEFINITION:
            self._handle_class(node)
        elif node.type == NODE_FUNCTION_DEFINITION:
            self._handle_function(node)
        
        for child in node.children:
            self._visit(child)

    def _handle_import(self, node: Node):
        # Simplistic extraction: handles `import foo.bar as baz`
        # A real implementation would parse the module_name and alias aliases correctly
        pass

    def _handle_import_from(self, node: Node):
        # Handles `from java.util import List`
        pass

    def _handle_class(self, node: Node):
        name_node = node.child_by_field_name('name')
        if name_node:
            name = name_node.text.decode('utf8')
            # Extract parent classes from 'superclasses' field if needed
            self.table.register_class(name, [])

    def _handle_function(self, node: Node):
        name_node = node.child_by_field_name('name')
        if name_node:
            name = name_node.text.decode('utf8')
            # Extract parameters and return type
            self.table.register_function(name, [])
