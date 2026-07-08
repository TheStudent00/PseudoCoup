from pseudocoup.core.parser import build_parser
parser = build_parser("rust")
tree = parser.parse(b"""
fn main() {
    let mut x = 10;
    let y = "hello";
    println!("Bigger");
    if x > 5 {
        x = 5;
    }
    while x > 0 {
        x = x - 1;
    }
}
""")

def print_tree(node, indent=0):
    print(" " * indent + node.type)
    for child in node.named_children:
        print_tree(child, indent + 2)

print_tree(tree.root_node)
