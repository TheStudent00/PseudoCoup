import tree_sitter_cpp
from tree_sitter import Language, Parser
parser = Parser(Language(tree_sitter_cpp.language()))
tree = parser.parse(b"class A { void B() { x[0]; } };")
def p(n, d=0):
  print("  "*d + n.type + (f": {n.text.decode('utf8')}" if not n.children else ""))
  for c in n.children:
      if c.is_named: p(c, d+1)
p(tree.root_node)
