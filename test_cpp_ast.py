from pseudocoup.core.parser import build_parser
parser = build_parser("cpp")
tree = parser.parse(b"""
#include <iostream>

int main() {
    auto x = 10;
    bool cond = true;
    std::cout << "Bigger" << std::endl;
    if (cond) {
        x = 5;
    }
    while (cond) {
        x = x - 1;
    }
    return 0;
}
""")

def print_tree(node, field_name=None, indent=0):
    field_prefix = f"{field_name}: " if field_name else ""
    print(" " * indent + field_prefix + node.type)
    for child in node.named_children:
        print_tree(child, None, indent + 2)

print_tree(tree.root_node)
