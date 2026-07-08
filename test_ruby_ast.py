from pseudocoup.core.parser import build_parser
parser = build_parser("ruby")
tree = parser.parse(b"""
x = 10
cond = true
puts("Bigger")
if cond
    x = 5
end
while cond
    x = x - 1
end
""")

def print_tree(node, field_name=None, indent=0):
    field_prefix = f"{field_name}: " if field_name else ""
    print(" " * indent + field_prefix + node.type)
    for child in node.named_children:
        print_tree(child, None, indent + 2)

print_tree(tree.root_node)
