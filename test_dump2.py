import sys
from pseudocoup.cli import Compiler
from pseudocoup.graph.cfg_builder import CFGBuilder
from pseudocoup.core.parser import build_parser
from pseudocoup.core.extractor import ContextExtractor
from pseudocoup.core.builder import IRBuilder
from pseudocoup.core.dart_flattener import DartFlattener
from pseudocoup.graph.ssa import SSABuilder
from pseudocoup.egress.emitter import GraphEmitter

with open("temp_dart.dart", "rb") as f:
    src_bytes = f.read()

parser = build_parser()
tree = parser.parse(src_bytes)
builder = IRBuilder()
flattener = DartFlattener(builder)
flattener.flatten(tree.root_node)

print("\n--- DART FLATTENED STREAM ---")
for i, instr in enumerate(builder.instructions):
    print(f"[{i}] {instr.op.name} {instr.dest} = {instr.args}")
