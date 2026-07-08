import tree_sitter_c_sharp
from tree_sitter import Language, Parser
parser = Parser(Language(tree_sitter_c_sharp.language()))
with open("fox.cs", "rb") as f:
    tree = parser.parse(f.read())
def print_tree(node, depth=0):
    print("  "*depth + node.type + (f": {node.text.decode('utf8')}" if not node.children else ""))
    for c in node.children:
        if c.is_named:
            print_tree(c, depth+1)
print_tree(tree.root_node)
