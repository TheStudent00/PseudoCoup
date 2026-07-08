import tree_sitter_c
from tree_sitter import Language, Parser
parser = Parser(Language(tree_sitter_c.language()))
tree = parser.parse(b"void* A() {}")
def p(n, d=0):
  print("  "*d + n.type)
  for c in n.children: p(c, d+1)
p(tree.root_node)
