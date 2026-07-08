import tree_sitter_c
from tree_sitter import Language, Parser
parser = Parser(Language(tree_sitter_c.language()))
tree = parser.parse(open("fox_c.txt", "rb").read())
def p(n, d=0):
  if n.type == "ERROR": print("ERROR!")
  for c in n.children: p(c, d+1)
p(tree.root_node)
print("Done")
