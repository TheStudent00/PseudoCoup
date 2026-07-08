from pseudocoup.core.parser import build_parser
parser = build_parser("dart")
tree = parser.parse(b'void main() { if (cond_0) {} }')

def print_tree(node, indent=0):
    print(" " * indent + node.type)
    for child in node.named_children:
        print_tree(child, indent + 2)

print_tree(tree.root_node)
