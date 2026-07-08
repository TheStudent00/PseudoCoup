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
from .core.diagnostics import GraphVizExporter

class Compiler:
    def __init__(self):
        self.registry = WrapperRegistry()

    def compile(self, file_path: str, target_lang: str, emit_dot: bool = False):
        if not os.path.exists(file_path):
            print(f"Error: Source file '{file_path}' not found.")
            sys.exit(1)
            
        with open(file_path, "rb") as f:
            src_bytes = f.read()

        # 1. Parse AST
        parser = build_parser()
        tree = parser.parse(src_bytes)
        root_node = tree.root_node

        # 2. Extract Global Context
        extractor = ContextExtractor()
        sym_table = extractor.extract(root_node)

        # 3. Flatten AST to Linear IR
        builder = IRBuilder()
        flattener = ASTFlattener(builder)
        flattener.flatten(root_node)

        # 4. Construct CFG
        cfg_builder = CFGBuilder(builder.instructions)
        cfg = cfg_builder.build()

        # 5. Transform to SSA
        ssa_builder = SSABuilder(cfg)
        ssa_builder.transform()

        # 6. Type Propagation and Registry Intercept
        type_prop = TypePropagator(cfg, sym_table) # We'll wire the registry in properly soon
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
        linear_stream = emitter.emit()
        
        # Placeholder for final egress code generation
        # ast_output = emitter.export_decorated_ast()
        # output_code = dispatch(ast_output, target_lang)
        
        print(f"Successfully compiled {file_path} to IR.")
        # print(output_code)

def main():
    parser = argparse.ArgumentParser(description="PseudoCoup V2 True Compiler")
    parser.add_argument("--source", required=True, help="Path to the source python file")
    parser.add_argument("--target-lang", required=True, help="Target language (e.g. kotlin, go, rust)")
    parser.add_argument("--emit-dot", action="store_true", help="Generate a GraphViz .dot file and PNG of the CFG")

    args = parser.parse_args()

    compiler = Compiler()
    compiler.compile(args.source, args.target_lang, args.emit_dot)

if __name__ == "__main__":
    main()
