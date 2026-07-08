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

def test_v2_python_to_ruby_roundtrip():
    with open("temp_src.py", "w") as f:
        f.write(TEST_CODE)

    # Python -> Ruby
    ruby_code = subprocess.check_output([
        "python3", "-m", "pseudocoup.cli", "--source", "temp_src.py", "--source-lang", "python", "--target-lang", "ruby"
    ], text=True)

    with open("temp_ruby.rb", "w") as f:
        f.write(ruby_code)

    # Ruby -> Python
    python_code = subprocess.check_output([
        "python3", "-m", "pseudocoup.cli", "--source", "temp_ruby.rb", "--source-lang", "ruby", "--target-lang", "python"
    ], text=True)

    os.remove("temp_src.py")
    os.remove("temp_ruby.rb")

    assert "print(\"Bigger\")" in python_code
    assert "while" in python_code
    assert "x_0 = 10" in python_code

if __name__ == "__main__":
    test_v2_python_to_ruby_roundtrip()
    print("Ruby Parity Test Passed!")
