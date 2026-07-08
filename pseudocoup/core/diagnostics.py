import os
import subprocess
from typing import Optional
from .models import ControlFlowGraph, OpCode

class GraphVizExporter:
    def __init__(self, cfg: ControlFlowGraph):
        self.cfg = cfg
        self.dot_content: list[str] = []

    def export_dot(self, output_path: str):
        """Generates a GraphViz .dot string from the CFG and writes to file."""
        if not self.cfg.entry:
            return
            
        self.dot_content = ["digraph CFG {", "    node [shape=box, fontname=\"Courier\"];"]
        
        # Define nodes
        for block_id, block in self.cfg.blocks.items():
            instructions_str = "\\n".join(
                str(instr).replace('"', '\\"') for instr in block.instructions
            )
            # If block is empty, put a placeholder
            if not instructions_str:
                instructions_str = "<empty>"
                
            label = f"BB{block_id}\\n{('-'*15)}\\n{instructions_str}"
            self.dot_content.append(f'    BB{block_id} [label="{label}"];')
            
        # Define edges
        for block_id, block in self.cfg.blocks.items():
            if not block.instructions:
                # Fallthrough empty block
                for succ in block.succs:
                    self.dot_content.append(f'    BB{block_id} -> BB{succ.id};')
                continue
                
            last_instr = block.instructions[-1]
            if last_instr.op == OpCode.BRANCH:
                true_idx = last_instr.args[1]
                false_idx = last_instr.args[2]
                
                # We need to map linear Instruction indices back to BB IDs for branching
                # Assuming here the links are already set in block.succs correctly
                # We'll just map the ordered succs. (true branch first, false second convention)
                if len(block.succs) >= 1:
                    self.dot_content.append(f'    BB{block_id} -> BB{block.succs[0].id} [color="green", label="T"];')
                if len(block.succs) >= 2:
                    self.dot_content.append(f'    BB{block_id} -> BB{block.succs[1].id} [color="red", label="F"];')
                    
            elif last_instr.op == OpCode.JUMP:
                if len(block.succs) >= 1:
                    self.dot_content.append(f'    BB{block_id} -> BB{block.succs[0].id} [color="blue"];')
            else:
                # Fallthrough
                for succ in block.succs:
                    self.dot_content.append(f'    BB{block_id} -> BB{succ.id};')
                    
        self.dot_content.append("}")
        
        with open(output_path, "w") as f:
            f.write("\n".join(self.dot_content))

    def render_png(self, dot_path: str, png_path: str):
        """Calls the system `dot` command to render a PNG of the CFG."""
        if os.path.exists(dot_path):
            try:
                subprocess.run(
                    ["dot", "-Tpng", dot_path, "-o", png_path], 
                    check=True,
                    capture_output=True
                )
            except subprocess.CalledProcessError as e:
                print(f"Failed to render PNG: {e.stderr.decode()}")
            except FileNotFoundError:
                print("GraphViz 'dot' executable not found on system path. Skipping PNG generation.")
