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

def test_v2_python_to_rust_roundtrip():
    with open("temp_src.py", "w") as f:
        f.write(TEST_CODE)

    # Python -> Rust
    rs_code = subprocess.check_output([
        "python3", "-m", "pseudocoup.cli", "--source", "temp_src.py", "--source-lang", "python", "--target-lang", "rust"
    ], text=True)

    with open("temp_rs.rs", "w") as f:
        f.write(rs_code)

    # Rust -> Python
    python_code = subprocess.check_output([
        "python3", "-m", "pseudocoup.cli", "--source", "temp_rs.rs", "--source-lang", "rust", "--target-lang", "python"
    ], text=True)

    os.remove("temp_src.py")
    os.remove("temp_rs.rs")

    assert "print(\"Bigger\")" in python_code
    assert "while" in python_code
    assert "x = 10" in python_code

if __name__ == "__main__":
    test_v2_python_to_rust_roundtrip()
    print("Rust Parity Test Passed!")
