import os
import sys

# Attempt to load tree_sitter_kotlin
try:
    from tree_sitter import Language, Parser
    import tree_sitter_kotlin as tsk
except ImportError:
    print("Error: tree_sitter or tree_sitter_kotlin not found. Please ensure they are installed.")
    sys.exit(1)

def build_parser():
    lang = Language(tsk.language())
    try:
        return Parser(lang)
    except TypeError:
        p = Parser()
        p.language = lang
        return p

class LiteralVisitor:
    def __init__(self):
        self.indent_level = 0
        self.output = []
        
    def _indent(self):
        return "    " * self.indent_level
        
    def emit(self, text):
        self.output.append(f"{self._indent()}{text}")

    def get_text(self, node, source_bytes):
        return source_bytes[node.start_byte:node.end_byte].decode('utf-8')

    def visit(self, node, source_bytes):
        if node.type == "source_file":
            for child in node.named_children:
                self.visit(child, source_bytes)
                
        elif node.type == "class_declaration":
            # Extract class name
            name_node = next((c for c in node.children if c.type == "identifier"), None)
            class_name = self.get_text(name_node, source_bytes) if name_node else "UnknownClass"
            self.emit(f"class {class_name}:")
            self.indent_level += 1
            
            # Find class body
            body_node = next((c for c in node.children if c.type == "class_body"), None)
            if body_node:
                for child in body_node.named_children:
                    self.visit(child, source_bytes)
            else:
                self.emit("pass")
            self.indent_level -= 1
            self.emit("")
            
        elif node.type == "function_declaration":
            # Check for annotations (like @Composable)
            for child in node.children:
                if child.type == "modifiers":
                    annotations = [self.get_text(c, source_bytes) for c in child.children if c.type == "annotation"]
                    for ann in annotations:
                        self.emit(ann)
                        
            name_node = next((c for c in node.children if c.type == "identifier"), None)
            func_name = self.get_text(name_node, source_bytes) if name_node else "unknown_func"
            
            # Parameters
            params = ["self"]
            param_node = next((c for c in node.children if c.type == "function_value_parameters"), None)
            if param_node:
                for p in param_node.named_children:
                    if p.type == "parameter":
                        pid = next((c for c in p.children if c.type == "identifier"), None)
                        if pid:
                            params.append(self.get_text(pid, source_bytes))
            
            self.emit(f"def {func_name}({', '.join(params)}):")
            self.indent_level += 1
            
            body_node = next((c for c in node.children if c.type == "function_body" or c.type == "block"), None)
            if body_node:
                self.visit(body_node, source_bytes)
            else:
                self.emit("pass")
                
            self.indent_level -= 1
            self.emit("")
            
        elif node.type == "block" or node.type == "function_body":
            if len(node.named_children) == 0:
                self.emit("pass")
            else:
                for child in node.named_children:
                    self.visit(child, source_bytes)
                    
        elif node.type == "property_declaration":
            # For simplicity, we just output the raw text as a comment or try to parse it
            raw_text = self.get_text(node, source_bytes).replace('\n', ' ')
            name_node = next((c for c in node.children if c.type == "variable_declaration"), None)
            if name_node:
                pid = next((c for c in name_node.children if c.type == "identifier"), None)
                if pid:
                    prop_name = self.get_text(pid, source_bytes)
                    self.emit(f"self.{prop_name} = None  # {raw_text}")
                    return
            self.emit(f"# TODO_UNHANDLED_PROPERTY: {raw_text}")

        elif node.type == "expression_statement":
            for child in node.named_children:
                self.visit(child, source_bytes)
                
        elif node.type in ("call_expression", "navigation_expression"):
            raw_text = self.get_text(node, source_bytes)
            # We emit the raw call for now as a placeholder for full AST mapping
            self.emit(raw_text)
            
        elif node.type in ("import_list", "package_header", "line_comment", "block_comment"):
            # skip or emit as comment
            pass
            
        else:
            # STRICT RULE: Emit TODO for unhandled node types
            raw_text = self.get_text(node, source_bytes).replace('\n', '\\n')
            self.emit(f"# TODO_UNHANDLED_KOTLIN_NODE: [{node.type}] {raw_text}")

    def transpile(self, source_code: bytes) -> str:
        parser = build_parser()
        tree = parser.parse(source_code)
        self.visit(tree.root_node, source_code)
        return "\n".join(self.output)

def run():
    if len(sys.argv) < 2:
        print("Usage: python literal_transpiler.py <path_to_kotlin_file>")
        sys.exit(1)
        
    kt_file = sys.argv[1]
    if not os.path.exists(kt_file):
        print(f"File not found: {kt_file}")
        sys.exit(1)
        
    with open(kt_file, "rb") as f:
        source_code = f.read()
        
    visitor = LiteralVisitor()
    python_code = visitor.transpile(source_code)
    
    out_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "build", "literal")
    os.makedirs(out_dir, exist_ok=True)
    out_file = os.path.join(out_dir, os.path.basename(kt_file).replace(".kt", ".py"))
    
    with open(out_file, "w") as f:
        f.write(python_code)
        
    print(f"Transpiled {kt_file} -> {out_file}")

if __name__ == "__main__":
    run()
