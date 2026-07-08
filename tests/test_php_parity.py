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

def test_v2_python_to_php_roundtrip():
    with open("temp_src.py", "w") as f:
        f.write(TEST_CODE)

    # Python -> PHP
    php_code = subprocess.check_output([
        "python3", "-m", "pseudocoup.cli", "--source", "temp_src.py", "--source-lang", "python", "--target-lang", "php"
    ], text=True)

    with open("temp_php.php", "w") as f:
        f.write(php_code)

    # PHP -> Python
    python_code = subprocess.check_output([
        "python3", "-m", "pseudocoup.cli", "--source", "temp_php.php", "--source-lang", "php", "--target-lang", "python"
    ], text=True)

    os.remove("temp_src.py")
    os.remove("temp_php.php")

    assert "print(\"Bigger\")" in python_code
    assert "while" in python_code
    assert "x = 10" in python_code

if __name__ == "__main__":
    test_v2_python_to_php_roundtrip()
    print("PHP Parity Test Passed!")
