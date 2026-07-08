import argparse
import sys
import os
from pseudocoup.egress import kotlin as eg_kt, go as eg_go, typescript as eg_ts, dart as eg_dart
from pseudocoup.ingress import kotlin as in_kt, go as in_go, typescript as in_ts, dart as in_dart

def main():
    parser = argparse.ArgumentParser(description="PseudoCoup Universal Intentful Transpiler")
    parser.add_argument("direction", choices=["egress", "ingress"], help="Transpilation direction (egress=Py->Lang, ingress=Lang->Py)")
    parser.add_argument("source", help="Source file path")
    parser.add_argument("--lang", required=True, choices=["kotlin", "go", "typescript", "dart"], help="Target language")
    
    args = parser.parse_args()
    
    if not os.path.exists(args.source):
        print(f"Error: {args.source} not found.")
        sys.exit(1)
        
    with open(args.source, "r") as f:
        code = f.read()
        
    if args.direction == "egress":
        if args.lang == "kotlin": result = eg_kt.transpile(code)
        elif args.lang == "go": result = eg_go.transpile(code)
        elif args.lang == "typescript": result = eg_ts.transpile(code)
        elif args.lang == "dart": result = eg_dart.transpile(code)
    else:
        if args.lang == "kotlin": result = in_kt.transpile(code)
        elif args.lang == "go": result = in_go.transpile(code)
        elif args.lang == "typescript": result = in_ts.transpile(code)
        elif args.lang == "dart": result = in_dart.transpile(code)
        
    print(result)

if __name__ == "__main__":
    main()
