from pseudocoup.core.parser import build_parser
parser = build_parser("go")
tree = parser.parse(b"""
package main

import "fmt"

func main() {
    x := 10
    cond := true
    fmt.Println("Bigger")
    if cond {
        x = 5
    }
    for cond {
        x = x - 1
    }
}
""")

def print_tree(node, indent=0):
    print(" " * indent + node.type)
    for child in node.named_children:
        print_tree(child, indent + 2)

print_tree(tree.root_node)
