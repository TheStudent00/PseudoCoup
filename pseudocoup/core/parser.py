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
    elif lang == "go":
        import tree_sitter_go
        p.language = Language(tree_sitter_go.language())
    elif lang == "typescript":
        import tree_sitter_typescript
        p.language = Language(tree_sitter_typescript.language_typescript())
    elif lang == "c_sharp":
        import tree_sitter_c_sharp
        p.language = Language(tree_sitter_c_sharp.language())
    elif lang == "cpp":
        import tree_sitter_cpp
        p.language = Language(tree_sitter_cpp.language())
    else:
        raise ValueError(f"Unsupported Ingress language: {lang}")
        
    return p
