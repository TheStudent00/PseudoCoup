import argparse
import sys
import os

from .core.parser import build_parser
from .core.builder import IRBuilder
from .core.extractor import ContextExtractor
from .core.flattener import ASTFlattener
from .graph.cfg_builder import CFGBuilder
from .graph.ssa import SSABuilder
from .semantic.type_prop import TypePropagator
from .semantic.registry import WrapperRegistry
from .egress.emitter import GraphEmitter
from .egress.python import PythonGenerator
from .egress.dart import DartGenerator
from .core.diagnostics import GraphVizExporter

class Compiler:
    def __init__(self):
        self.registry = WrapperRegistry()

    def compile(self, file_path: str, source_lang: str, target_lang: str, emit_dot: bool = False):
        if not os.path.exists(file_path):
            print(f"Error: Source file '{file_path}' not found.")
            sys.exit(1)
            
        self.registry.load_defaults(source_lang, target_lang)
            
        with open(file_path, "rb") as f:
            src_bytes = f.read()

        # 1. Parse AST
        parser = build_parser(source_lang)
        tree = parser.parse(src_bytes)
        root_node = tree.root_node

        # 2. Extract Global Context
        extractor = ContextExtractor()
        sym_table = extractor.extract(root_node)

        # 3. Flatten AST to Linear IR
        builder = IRBuilder()
        if source_lang == "python":
            flattener = ASTFlattener(builder)
        elif source_lang == "dart":
            from .core.dart_flattener import DartFlattener
            flattener = DartFlattener(builder)
        elif source_lang == "kotlin":
            from .core.kotlin_flattener import KotlinFlattener
            flattener = KotlinFlattener(builder)
        elif source_lang == "rust":
            from .core.rust_flattener import RustFlattener
            flattener = RustFlattener(builder)
        elif source_lang == "go":
            from .core.go_flattener import GoFlattener
            flattener = GoFlattener(builder)
        elif source_lang == "typescript":
            from .core.typescript_flattener import TypeScriptFlattener
            flattener = TypeScriptFlattener(builder)
        elif source_lang == "c_sharp":
            from .core.c_sharp_flattener import CSharpFlattener
            flattener = CSharpFlattener(builder)
        elif source_lang == "cpp":
            from .core.cpp_flattener import CppFlattener
            flattener = CppFlattener(builder)
        else:
            print(f"Error: Ingress lang '{source_lang}' not supported in V2.")
            sys.exit(1)
            
        flattener.flatten(root_node)

        # 4. Construct CFG
        cfg_builder = CFGBuilder(builder.instructions)
        cfg = cfg_builder.build()

        # 5. Transform to SSA
        ssa_builder = SSABuilder(cfg)
        ssa_builder.transform()

        # 6. Type Propagation and Registry Intercept
        type_prop = TypePropagator(cfg, sym_table, registry=self.registry)
        type_prop.propagate()

        # Output diagnostics if requested
        if emit_dot:
            diag = GraphVizExporter(cfg)
            dot_path = file_path + ".dot"
            png_path = file_path + ".png"
            diag.export_dot(dot_path)
            diag.render_png(dot_path, png_path)
            print(f"Diagnostic CFG exported to: {png_path}")

        # 7. Egress Emission (Deconstruct SSA and reconstruct AST)
        emitter = GraphEmitter(cfg)
        emitter.emit()
        ast_output = emitter.export_decorated_ast()
        
        if target_lang == "python":
            gen = PythonGenerator()
            output_code = gen.generate(ast_output)
        elif target_lang == "dart":
            gen = DartGenerator()
            output_code = gen.generate(ast_output)
        elif target_lang == "kotlin":
            from .egress.kotlin import KotlinGenerator
            gen = KotlinGenerator()
            output_code = gen.generate(ast_output)
        elif target_lang == "rust":
            from .egress.rust import RustGenerator
            gen = RustGenerator()
            output_code = gen.generate(ast_output)
        elif target_lang == "go":
            from .egress.go import GoGenerator
            gen = GoGenerator()
            output_code = gen.generate(ast_output)
        elif target_lang == "typescript":
            from .egress.typescript import TypeScriptGenerator
            gen = TypeScriptGenerator()
            output_code = gen.generate(ast_output)
        elif target_lang == "c_sharp":
            from .egress.c_sharp import CSharpGenerator
            gen = CSharpGenerator()
            output_code = gen.generate(ast_output)
        elif target_lang == "cpp":
            from .egress.cpp import CppGenerator
            gen = CppGenerator()
            output_code = gen.generate(ast_output)
        else:
            print(f"Error: Target language '{target_lang}' is not yet supported in V2.")
            sys.exit(1)
            
        print(output_code)

def main():
    parser = argparse.ArgumentParser(description="PseudoCoup V2 True Compiler")
    parser.add_argument("--source", required=True, help="Path to the source file")
    parser.add_argument("--source-lang", default="python", help="Source language (default: python)")
    parser.add_argument("--target-lang", required=True, help="Target language (e.g. kotlin, go, rust)")
    parser.add_argument("--emit-dot", action="store_true", help="Generate a GraphViz .dot file and PNG of the CFG")

    args = parser.parse_args()

    compiler = Compiler()
    compiler.compile(args.source, args.source_lang, args.target_lang, args.emit_dot)

if __name__ == "__main__":
    main()
