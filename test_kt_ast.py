from pseudocoup.core.parser import build_parser
parser = build_parser("kotlin")
tree = parser.parse(b"""
fun main() {
    var x = 10
    val y = "hello"
    println("Bigger")
    if (x > 5) {
        x = 5
    }
    while (true) {
        x = x - 1
    }
}
""")

def print_tree(node, field_name=None, indent=0):
    field_prefix = f"{field_name}: " if field_name else ""
    print(" " * indent + field_prefix + node.type)
    
    cursor = node.walk()
    if cursor.goto_first_child():
        while True:
            if cursor.node.is_named:
                print_tree(cursor.node, cursor.current_field_name, indent + 2)
            if not cursor.goto_next_sibling():
                break
        cursor.goto_parent()

print_tree(tree.root_node)
