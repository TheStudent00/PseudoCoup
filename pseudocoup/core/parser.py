import tree_sitter_python
import tree_sitter_dart
from tree_sitter import Language, Parser

def build_parser(lang: str = "python") -> Parser:
    """Instantiate and return a Tree-Sitter parser configured for the target language."""
    p = Parser()
    
    if lang == "python":
        p.language = Language(tree_sitter_python.language())
    elif lang == "dart":
        p.language = Language(tree_sitter_dart.language())
    elif lang == "kotlin":
        import tree_sitter_kotlin
        p.language = Language(tree_sitter_kotlin.language())
    elif lang == "rust":
        import tree_sitter_rust
        p.language = Language(tree_sitter_rust.language())
    else:
        raise ValueError(f"Unsupported Ingress language: {lang}")
        
    return p
