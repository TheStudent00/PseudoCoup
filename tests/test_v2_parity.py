import subprocess
import os
import pytest

# A simple valid Python file to test
TEST_CODE = """
def main():
    x = 10
    cond = True
    if cond:
        print("Bigger")
    else:
        print("Smaller")
        
    while cond:
        x = 5
"""

def test_v2_python_to_dart():
    with open("temp_src.py", "w") as f:
        f.write(TEST_CODE)
        
    # Python -> Dart
    dart_code = subprocess.check_output([
        "python3", "-m", "pseudocoup.cli", "--source", "temp_src.py", "--source-lang", "python", "--target-lang", "dart"
    ], text=True)
    
    with open("temp_dart.dart", "w") as f:
        f.write(dart_code)
        
    # Dart -> Python
    python_code = subprocess.check_output([
        "python3", "-m", "pseudocoup.cli", "--source", "temp_dart.dart", "--source-lang", "dart", "--target-lang", "python"
    ], text=True)
    
    os.remove("temp_src.py")
    os.remove("temp_dart.dart")
    
    assert "print(\"Bigger\")" in python_code
    assert "while" in python_code
    assert "x = 10" in python_code
