import tree_sitter_python
from tree_sitter import Language, Parser

def build_parser() -> Parser:
    """Instantiate and return a Tree-Sitter parser configured for Python."""
    p = Parser()
    p.language = Language(tree_sitter_python.language())
    return p
