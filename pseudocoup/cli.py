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

# ---------------------------------------------------------------------------
# Egress gate (U4): pseudoir.gate pre-transpile discipline check.
#
# Scope decision (recorded per the plan's natural-answer norm): the gate only
# understands Hub notation (Python source importing the U null-safety
# namespace, e.g. `from hub import U`). PseudoCoup's plain-Python examples
# (fox.py, space_station.py) MAP-fail the gate because baseline-Python idioms
# outside Hub discipline (lambdas, comprehensions, un-annotated defs) are not
# Hub notation -- so running the gate on all python source would break every
# existing transpile. Therefore: the gate runs automatically when
# --source-lang is python AND the source verifiably imports U (detected with
# pseudoir.binder.u_import_present, the gate's own definition -- no drift).
# Non-python ingress languages are never Hub notation; the gate never runs
# for them. A --no-gate escape hatch is provided (rationale: matches
# pseudoir.transpile's spirit of gate-by-default while letting a developer
# emit anyway to inspect partial output while iterating on a Hub file; the
# default stays ON for Hub source so discipline is opt-out, not opt-in).
#
# D3 (binding): registry cells with status 'pending' for targets swift and
# csharp are PASS-WITH-WARNING -- recorded on stderr, non-blocking -- for
# those two targets only. A strategy of 'fail', or a pending cell in any
# other target, still blocks. pseudoir.gate itself treats pending as not-ok
# (LookupResult.ok requires confirmed status); the downgrade is implemented
# here on the PseudoCoup side, leaving pseudoir semantics untouched.
# ---------------------------------------------------------------------------

GATE_WARN_PENDING_TARGETS = {"swift", "csharp"}  # D3

_TARGET_ALIASES = {
    "kt": "kotlin", "cs": "csharp", "c#": "csharp",
    "ts": "typescript", "c++": "cpp", "rb": "ruby",
}


def _canon_target(name):
    n = name.lower()
    return _TARGET_ALIASES.get(n, n)


def _is_hub_source(source_bytes):
    """Hub notation = the U namespace is genuinely imported. Uses the exact
    detector the gate itself uses (pseudoir.binder.u_import_present)."""
    from pseudoir import binder as _binder
    tree = _binder.parse(source_bytes)
    return _binder.u_import_present(tree.root_node, source_bytes)


def _run_egress_gate(source_bytes, target, source_path):
    """Run pseudoir.gate.check pre-transpile. On FAIL print the gate report
    and exit nonzero (matching pseudoir.transpile's own refuse-to-emit
    contract). Pending swift/csharp cells downgrade to warnings per D3."""
    from pseudoir import gate as _gate
    res = _gate.check(source_bytes, [target], hub_file=source_path)
    if res.passed:
        return
    downgradable = [
        wf for wf in res.wrap_failures
        if wf[1] in GATE_WARN_PENDING_TARGETS
        and wf[3] == "pending" and wf[2] != "fail"
    ]
    if not res.map_failures and len(downgradable) == len(res.wrap_failures):
        print(f"[gate] PASS-WITH-WARNING for target '{target}': "
              f"{len(downgradable)} registry cell(s) pending "
              f"(unconfirmed; non-blocking per D3):", file=sys.stderr)
        for (op_id, tgt, strategy, status) in downgradable:
            print(f"[gate]   {op_id} @ {tgt}: strategy={strategy}, "
                  f"status={status}", file=sys.stderr)
        return
    print(_gate.format_report(res), file=sys.stderr)
    print(f"Error: egress gate FAILED for target '{target}'; "
          f"refusing to emit.", file=sys.stderr)
    sys.exit(1)


def main():
    parser = argparse.ArgumentParser(description="PseudoCoup V3 CLI")
    parser.add_argument("--source", required=True, help="The path to the source file")
    parser.add_argument("--source-lang", default="python", help="The input language")
    parser.add_argument("--target-lang", default="dart", help="The output language")
    parser.add_argument("--no-gate", action="store_true",
                        help="Skip the pseudoir egress gate (runs by default "
                             "on Hub-notation python source)")

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

    # U4: pre-transpile egress gate -- python-Hub ingress path only.
    if (not args.no_gate and args.source_lang.lower() == "python"
            and _is_hub_source(source_bytes)):
        _run_egress_gate(source_bytes, _canon_target(args.target_lang),
                         source_path)

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
