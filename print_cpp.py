import tree_sitter_cpp
from tree_sitter import Language, Parser
parser = Parser(Language(tree_sitter_cpp.language()))
tree = parser.parse(b"class A { void B() { if (x) { } else { std::cout << 1; } } };")
def p(n):
    if n.type == "if_statement":
        print("ALT", n.child_by_field_name('alternative'))
    for c in n.children: p(c)
p(tree.root_node)
