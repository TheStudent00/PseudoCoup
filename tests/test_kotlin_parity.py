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

def test_v2_python_to_kotlin_roundtrip():
    with open("temp_src.py", "w") as f:
        f.write(TEST_CODE)

    # Python -> Kotlin
    kt_code = subprocess.check_output([
        "python3", "-m", "pseudocoup.cli", "--source", "temp_src.py", "--source-lang", "python", "--target-lang", "kotlin"
    ], text=True)

    with open("temp_kt.kt", "w") as f:
        f.write(kt_code)

    # Kotlin -> Python
    python_code = subprocess.check_output([
        "python3", "-m", "pseudocoup.cli", "--source", "temp_kt.kt", "--source-lang", "kotlin", "--target-lang", "python"
    ], text=True)

    os.remove("temp_src.py")
    os.remove("temp_kt.kt")

    assert "print(\"Bigger\")" in python_code
    assert "while" in python_code
    assert "x_0 = 10" in python_code

if __name__ == "__main__":
    test_v2_python_to_kotlin_roundtrip()
    print("Kotlin Parity Test Passed!")
