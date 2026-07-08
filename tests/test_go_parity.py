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

def test_v2_python_to_go_roundtrip():
    with open("temp_src.py", "w") as f:
        f.write(TEST_CODE)

    # Python -> Go
    go_code = subprocess.check_output([
        "python3", "-m", "pseudocoup.cli", "--source", "temp_src.py", "--source-lang", "python", "--target-lang", "go"
    ], text=True)

    with open("temp_go.go", "w") as f:
        f.write(go_code)

    # Go -> Python
    python_code = subprocess.check_output([
        "python3", "-m", "pseudocoup.cli", "--source", "temp_go.go", "--source-lang", "go", "--target-lang", "python"
    ], text=True)

    os.remove("temp_src.py")
    os.remove("temp_go.go")

    assert "print(\"Bigger\")" in python_code
    assert "while" in python_code
    assert "x = 10" in python_code

if __name__ == "__main__":
    test_v2_python_to_go_roundtrip()
    print("Go Parity Test Passed!")
