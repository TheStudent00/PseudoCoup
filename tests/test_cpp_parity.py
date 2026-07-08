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

def test_v2_python_to_cpp_roundtrip():
    with open("temp_src.py", "w") as f:
        f.write(TEST_CODE)

    # Python -> C++
    cpp_code = subprocess.check_output([
        "python3", "-m", "pseudocoup.cli", "--source", "temp_src.py", "--source-lang", "python", "--target-lang", "cpp"
    ], text=True)

    with open("temp_cpp.cpp", "w") as f:
        f.write(cpp_code)

    # C++ -> Python
    python_code = subprocess.check_output([
        "python3", "-m", "pseudocoup.cli", "--source", "temp_cpp.cpp", "--source-lang", "cpp", "--target-lang", "python"
    ], text=True)

    os.remove("temp_src.py")
    os.remove("temp_cpp.cpp")

    assert "print(\"Bigger\")" in python_code
    assert "while" in python_code
    assert "x_0 = 10" in python_code

if __name__ == "__main__":
    test_v2_python_to_cpp_roundtrip()
    print("C++ Parity Test Passed!")
