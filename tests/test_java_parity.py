import subprocess
import os

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

def test_v2_python_to_java_roundtrip():
    with open("temp_src.py", "w") as f:
        f.write(TEST_CODE)

    # Python -> Java
    java_code = subprocess.check_output([
        "python3", "-m", "pseudocoup.cli", "--source", "temp_src.py", "--source-lang", "python", "--target-lang", "java"
    ], text=True)

    with open("temp_java.java", "w") as f:
        f.write(java_code)

    # Java -> Python
    python_code = subprocess.check_output([
        "python3", "-m", "pseudocoup.cli", "--source", "temp_java.java", "--source-lang", "java", "--target-lang", "python"
    ], text=True)

    os.remove("temp_src.py")
    os.remove("temp_java.java")

    assert "print(\"Bigger\")" in python_code
    assert "while" in python_code
    assert "x = 10" in python_code

if __name__ == "__main__":
    test_v2_python_to_java_roundtrip()
    print("Java Parity Test Passed!")
