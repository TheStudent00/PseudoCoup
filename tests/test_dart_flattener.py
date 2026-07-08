import pytest
from pseudocoup.core.parser import build_parser
from pseudocoup.core.builder import IRBuilder
from pseudocoup.core.dart_flattener import DartFlattener
from pseudocoup.core.models import OpCode

def test_dart_flattener_assignment():
    parser = build_parser(lang="dart")
    code = """
    void main() {
        int x = 42;
        String msg = "Hello";
    }
    """
    tree = parser.parse(bytes(code, "utf8"))
    
    builder = IRBuilder()
    flattener = DartFlattener(builder)
    flattener.flatten(tree.root_node)
    
    opcodes = [instr.op for instr in builder.instructions]
    assert OpCode.ASSIGN in opcodes
    
    # Check that variables 'x' and 'msg' were processed
    destinations = [instr.dest for instr in builder.instructions if instr.dest]
    assert 'x' in destinations
    assert 'msg' in destinations

def test_dart_flattener_control_flow():
    parser = build_parser(lang="dart")
    code = """
    void main() {
        if (x > 10) {
            y = 5;
        } else {
            y = 2;
        }
    }
    """
    tree = parser.parse(bytes(code, "utf8"))
    
    builder = IRBuilder()
    flattener = DartFlattener(builder)
    flattener.flatten(tree.root_node)
    
    opcodes = [instr.op for instr in builder.instructions]
    assert OpCode.BRANCH in opcodes
    assert OpCode.JUMP in opcodes

def test_dart_flattener_loop():
    parser = build_parser(lang="dart")
    code = """
    void main() {
        while (true) {
            print("Looping");
        }
    }
    """
    tree = parser.parse(bytes(code, "utf8"))
    
    builder = IRBuilder()
    flattener = DartFlattener(builder)
    flattener.flatten(tree.root_node)
    
    opcodes = [instr.op for instr in builder.instructions]
    assert OpCode.BRANCH in opcodes
    assert OpCode.CALL in opcodes
    assert OpCode.JUMP in opcodes
