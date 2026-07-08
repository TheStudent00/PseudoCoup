import argparse
import sys
import os
from pseudocoup.egress import kotlin as eg_kt, go as eg_go, typescript as eg_ts, dart as eg_dart, csharp as eg_cs, cpp as eg_cpp, c as eg_c, java as eg_java, swift as eg_swift, rust as eg_rust, ruby as eg_ruby, php as eg_php
from pseudocoup.ingress import kotlin as in_kt, go as in_go, typescript as in_ts, dart as in_dart, csharp as in_cs, cpp as in_cpp, c as in_c, java as in_java, swift as in_swift, rust as in_rust, ruby as in_ruby, php as in_php

def main():
    parser = argparse.ArgumentParser(description="PseudoCoup Universal Intentful Transpiler")
    parser.add_argument("direction", choices=["egress", "ingress"], help="Transpilation direction (egress=Py->Lang, ingress=Lang->Py)")
    parser.add_argument("source", help="Source file path")
    parser.add_argument("--lang", required=True, choices=["kotlin", "go", "typescript", "dart", "csharp", "cpp", "c", "java", "swift", "rust", "ruby", "php"], help="Target language")
    
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
        elif args.lang == "csharp": result = eg_cs.transpile(code)
        elif args.lang == "cpp": result = eg_cpp.transpile(code)
        elif args.lang == "c": result = eg_c.transpile(code)
        elif args.lang == "java": result = eg_java.transpile(code)
        elif args.lang == "swift": result = eg_swift.transpile(code)
        elif args.lang == "rust": result = eg_rust.transpile(code)
        elif args.lang == "ruby": result = eg_ruby.transpile(code)
        elif args.lang == "php": result = eg_php.transpile(code)
    else:
        if args.lang == "kotlin": result = in_kt.transpile(code)
        elif args.lang == "go": result = in_go.transpile(code)
        elif args.lang == "typescript": result = in_ts.transpile(code)
        elif args.lang == "dart": result = in_dart.transpile(code)
        elif args.lang == "csharp": result = in_cs.transpile(code)
        elif args.lang == "cpp": result = in_cpp.transpile(code)
        elif args.lang == "c": result = in_c.transpile(code)
        elif args.lang == "java": result = in_java.transpile(code)
        elif args.lang == "swift": result = in_swift.transpile(code)
        elif args.lang == "rust": result = in_rust.transpile(code)
        elif args.lang == "ruby": result = in_ruby.transpile(code)
        elif args.lang == "php": result = in_php.transpile(code)
        
    print(result)

if __name__ == "__main__":
    main()
