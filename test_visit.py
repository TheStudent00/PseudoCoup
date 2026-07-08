from pseudocoup.ingress.cpp import CppToPyTranspiler
import tree_sitter_cpp
from tree_sitter import Language, Parser
parser = Parser(Language(tree_sitter_cpp.language()))
tree = parser.parse(b"class A { void B() { std::cout << \"No station assigned.\" << std::endl; } };")
t = CppToPyTranspiler()
stmt = [c for c in tree.root_node.children[0].children[2].children[0].children[3].children if c.is_named][0]
print(stmt.type)
print(t.visit_expression([c for c in stmt.children if c.is_named][0]))
