import subprocess
import os
import pytest

EXAMPLES_DIR = os.path.join(os.path.dirname(__file__), "../examples")
STATION_PY = os.path.join(EXAMPLES_DIR, "space_station.py")

@pytest.fixture(scope="module")
def canonical_output():
    return subprocess.check_output(["python3", STATION_PY], text=True)

@pytest.mark.parametrize("lang", ["kotlin", "go", "typescript", "dart", "csharp", "cpp"])
def test_roundtrip_oracle(lang, canonical_output):
    # Egress
    egress_code = subprocess.check_output([
        "python3", "-m", "pseudocoup.cli", "egress", STATION_PY, "--lang", lang
    ], text=True)
    
    # Save temp egress file
    temp_egress = f"temp_{lang}_src.txt"
    with open(temp_egress, "w") as f:
        f.write(egress_code)
        
    # Ingress
    ingress_code = subprocess.check_output([
        "python3", "-m", "pseudocoup.cli", "ingress", temp_egress, "--lang", lang
    ], text=True)
    
    # Save temp ingress file
    temp_ingress = f"temp_inverted_{lang}.py"
    with open(temp_ingress, "w") as f:
        f.write(ingress_code)
        
    # Test dynamic oracle
    actual_output = subprocess.check_output(["python3", temp_ingress], text=True)
    
    # Cleanup
    os.remove(temp_egress)
    os.remove(temp_ingress)
    
    assert actual_output == canonical_output
