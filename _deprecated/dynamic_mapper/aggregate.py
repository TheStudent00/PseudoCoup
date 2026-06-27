import os
import sys
import glob

# Ensure local modules can be imported
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from core.ledger import GraphLedger

def generate_combined_markdown(output_dir="/home/lucas/Programming/PseudoCoup/runtime_uimap"):
    combined_path = os.path.join(output_dir, "combined_map.md")
    
    with open(combined_path, "w") as out_f:
        out_f.write("# Dynamic UI Maps\n\n")
        
        for app_key in ["wfl", "pc"]:
            ledger_path = os.path.join(output_dir, f"{app_key}_ledger.json")
            if not os.path.exists(ledger_path):
                continue
                
            out_f.write(f"## {app_key.upper()} Map\n\n")
            out_f.write("```mermaid\n")
            out_f.write("graph TD\n")
            
            ledger = GraphLedger(storage_path=ledger_path)
            
            for node_hash, state_dict in ledger.nodes.items():
                screen = state_dict.get("current_screen", "unknown")
                label = f"{screen}\\n{node_hash[:6]}"
                out_f.write(f'    {node_hash}["{label}"]\n')
                
            for from_hash, action, to_hash in ledger.edges:
                out_f.write(f'    {from_hash} -->|"{action}"| {to_hash}\n')
                
            out_f.write("```\n\n")
            
    print(f"Generated combined map at {combined_path}")

if __name__ == "__main__":
    generate_combined_markdown()
