import sys
import argparse
import os

from pseudocoup.core.ledger import Ledger
from pseudocoup.ingress.python import PythonIngestor
from pseudocoup.ingress.dart import DartIngestor
from pseudocoup.egress.dart import DartEmitter
from pseudocoup.egress.go import GoEmitter
from pseudocoup.egress.python import PythonEmitter
from pseudocoup.ingress.kotlin import KotlinIngestor
from pseudocoup.egress.kotlin import KotlinEmitter
from pseudocoup.ingress.java import JavaIngestor
from pseudocoup.egress.java import JavaEmitter
from pseudocoup.ingress.csharp import CSharpIngestor
from pseudocoup.egress.csharp import CSharpEmitter
from pseudocoup.ingress.typescript import TypeScriptIngestor
from pseudocoup.egress.typescript import TypeScriptEmitter
from pseudocoup.ingress.swift import SwiftIngestor
from pseudocoup.egress.swift import SwiftEmitter
from pseudocoup.ingress.rust import RustIngestor
from pseudocoup.egress.rust import RustEmitter
from pseudocoup.ingress.cpp import CppIngestor
from pseudocoup.egress.cpp import CppEmitter
from pseudocoup.ingress.ruby import RubyIngestor
from pseudocoup.egress.ruby import RubyEmitter
from pseudocoup.ingress.php import PhpIngestor
from pseudocoup.egress.php import PhpEmitter

def main():
    parser = argparse.ArgumentParser(description="PseudoCoup V3 CLI")
    parser.add_argument("--source", required=True, help="The path to the source file")
    parser.add_argument("--source-lang", default="python", help="The input language")
    parser.add_argument("--target-lang", default="dart", help="The output language")
    
    args = parser.parse_args()
    
    source_path = args.source
    if not os.path.exists(source_path):
        print(f"Error: Source file '{source_path}' does not exist.")
        sys.exit(1)
        
    # 1. Determine the path of the companion ledger.
    base_name, _ = os.path.splitext(source_path)
    ledger_path = f"{base_name}.ledger.json"
    
    # 2. Instantiate a Ledger and call load()
    ledger = Ledger()
    ledger.load(ledger_path)
    
    # 3. Instantiate the proper Ingestor, pass it the Ledger. Call parse()
    with open(source_path, 'rb') as f:
        source_bytes = f.read()
        
    if args.source_lang.lower() == "dart":
        ingestor = DartIngestor(ledger)
    elif args.source_lang.lower() == "kotlin" or args.source_lang.lower() == "kt":
        ingestor = KotlinIngestor(ledger)
    elif args.source_lang.lower() == "java":
        ingestor = JavaIngestor(ledger)
    elif args.source_lang.lower() in ("csharp", "cs", "c#"):
        ingestor = CSharpIngestor(ledger)
    elif args.source_lang.lower() in ("typescript", "ts"):
        ingestor = TypeScriptIngestor(ledger)
    elif args.source_lang.lower() == "swift":
        ingestor = SwiftIngestor(ledger)
    elif args.source_lang.lower() == "rust":
        ingestor = RustIngestor(ledger)
    elif args.source_lang.lower() in ("cpp", "c++"):
        ingestor = CppIngestor(ledger)
    elif args.source_lang.lower() in ("ruby", "rb"):
        ingestor = RubyIngestor(ledger)
    elif args.source_lang.lower() == "php":
        ingestor = PhpIngestor(ledger)
    else:
        ingestor = PythonIngestor(ledger)
        
    module_node = ingestor.parse(source_bytes)
    
    # 4. Instantiate the correct Emitter and call generate()
    if args.target_lang.lower() == "dart":
        emitter = DartEmitter(ledger)
        output_path = f"{base_name}.dart"
    elif args.target_lang.lower() == "go":
        emitter = GoEmitter(ledger)
        output_path = f"{base_name}.go"
    elif args.target_lang.lower() == "python":
        emitter = PythonEmitter(ledger)
        output_path = f"{base_name}.python"
    elif args.target_lang.lower() == "kotlin" or args.target_lang.lower() == "kt":
        emitter = KotlinEmitter(ledger)
        output_path = f"{base_name}.kt"
    elif args.target_lang.lower() == "java":
        emitter = JavaEmitter(ledger)
        output_path = f"{base_name}.java"
    elif args.target_lang.lower() in ("csharp", "cs", "c#"):
        emitter = CSharpEmitter(ledger)
        output_path = f"{base_name}.cs"
    elif args.target_lang.lower() in ("typescript", "ts"):
        emitter = TypeScriptEmitter(ledger)
        output_path = f"{base_name}.ts"
    elif args.target_lang.lower() == "swift":
        emitter = SwiftEmitter(ledger)
        output_path = f"{base_name}.swift"
    elif args.target_lang.lower() == "rust":
        emitter = RustEmitter(ledger)
        output_path = f"{base_name}.rs"
    elif args.target_lang.lower() in ("cpp", "c++"):
        emitter = CppEmitter(ledger)
        output_path = f"{base_name}.cpp"
    elif args.target_lang.lower() in ("ruby", "rb"):
        emitter = RubyEmitter(ledger)
        output_path = f"{base_name}.rb"
    elif args.target_lang.lower() == "php":
        emitter = PhpEmitter(ledger)
        output_path = f"{base_name}.php"
    else:
        print(f"Error: Unsupported target language '{args.target_lang}'")
        sys.exit(1)
        
    output_code = emitter.generate(module_node)
    
    # 5. Save the output string to a new file
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(output_code)
        
    # 6. Call dump() on the Ledger
    ledger.dump(ledger_path)
    
    print(f"Successfully transpiled '{source_path}' to '{output_path}'.")

if __name__ == "__main__":
    main()
