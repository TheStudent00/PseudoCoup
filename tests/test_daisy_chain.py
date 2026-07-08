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

def test_global_daisy_chain():
    languages = [
        "python", "dart", "kotlin", "rust", "go", "typescript", 
        "c_sharp", "cpp", "c", "java", "swift", "ruby", "php", "python"
    ]
    
    current_code = TEST_CODE
    ext_map = {
        "python": "py", "dart": "dart", "kotlin": "kt", "rust": "rs",
        "go": "go", "typescript": "ts", "c_sharp": "cs", "cpp": "cpp",
        "c": "c", "java": "java", "swift": "swift", "ruby": "rb", "php": "php"
    }
    
    with open("temp_chain_0.py", "w") as f:
        f.write(current_code)
        
    for i in range(len(languages) - 1):
        source_lang = languages[i]
        target_lang = languages[i+1]
        
        source_file = f"temp_chain_{i}.{ext_map[source_lang]}"
        target_file = f"temp_chain_{i+1}.{ext_map[target_lang]}"
        
        try:
            print(f"Transpiling {source_lang} -> {target_lang}...")
            target_code = subprocess.check_output([
                "python3", "-m", "pseudocoup.cli", 
                "--source", source_file, 
                "--source-lang", source_lang, 
                "--target-lang", target_lang
            ], text=True, stderr=subprocess.STDOUT)
            
            with open(target_file, "w") as f:
                f.write(target_code)
        except subprocess.CalledProcessError as e:
            print(f"FAILED on {source_lang} -> {target_lang}")
            print(e.output)
            return

    # Check final Python
    with open(f"temp_chain_{len(languages)-1}.py", "r") as f:
        final_code = f.read()
        
    print("\n--- FINAL PYTHON CODE ---")
    print(final_code)
    
    # Cleanup
    for i in range(len(languages)):
        file_path = f"temp_chain_{i}.{ext_map[languages[i]]}"
        if os.path.exists(file_path):
            os.remove(file_path)
            
    assert "print(\"Bigger\")" in final_code
    assert "while" in final_code

if __name__ == "__main__":
    test_global_daisy_chain()
