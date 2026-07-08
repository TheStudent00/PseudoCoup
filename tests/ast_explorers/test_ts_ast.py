from pseudocoup.core.parser import build_parser
parser = build_parser("typescript")
tree = parser.parse(b"""
function main() {
    let x = 10;
    let cond = true;
    console.log("Bigger");
    if (cond) {
        x = 5;
    }
    while (cond) {
        x = x - 1;
    }
}
""")

def print_tree(node, field_name=None, indent=0):
    field_prefix = f"{field_name}: " if field_name else ""
    print(" " * indent + field_prefix + node.type)
    
    # Just print children without fields since field_name on older tree-sitter bindings is annoying
    for child in node.named_children:
        print_tree(child, None, indent + 2)

print_tree(tree.root_node)
