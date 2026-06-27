class Visualizer:
    """
    Utility for generating visual representations of the GraphLedger.
    """
    @staticmethod
    def export_mermaid(ledger, output_path: str):
        """
        Generates a Mermaid.js flow diagram of the ledger.
        """
        mmd_lines = ["graph TD"]
        
        # Add nodes with short labels
        for node_hash, state_dict in ledger.nodes.items():
            screen = state_dict.get("current_screen", "unknown")
            label = f"{screen}\\n{node_hash[:6]}"
            mmd_lines.append(f'    {node_hash}["{label}"]')
            
        # Add edges
        for from_hash, action, to_hash in ledger.edges:
            mmd_lines.append(f'    {from_hash} -->|"{action}"| {to_hash}')
            
        with open(output_path, "w") as f:
            f.write("\n".join(mmd_lines))

    @staticmethod
    def export_markdown_mermaid(ledger, output_path: str):
        """
        Generates a Markdown file with an embedded Mermaid.js flow diagram of the ledger.
        """
        mmd_lines = ["```mermaid", "graph TD"]
        
        # Add nodes with short labels
        for node_hash, state_dict in ledger.nodes.items():
            screen = state_dict.get("current_screen", "unknown")
            label = f"{screen}\\n{node_hash[:6]}"
            mmd_lines.append(f'    {node_hash}["{label}"]')
            
        # Add edges
        for from_hash, action, to_hash in ledger.edges:
            mmd_lines.append(f'    {from_hash} -->|"{action}"| {to_hash}')
            
        mmd_lines.append("```")
        
        with open(output_path, "w") as f:
            f.write("\n".join(mmd_lines))

    @staticmethod
    def export_graphviz(ledger, output_path: str):
        """
        Generates a Graphviz DOT file for high-quality visualization.
        """
        dot_lines = ["digraph G {", '    node [shape=box, style=filled, fillcolor=lightblue];']
        
        for node_hash, state_dict in ledger.nodes.items():
            screen = state_dict.get("current_screen", "unknown")
            label = f"Screen: {screen}\\nID: {node_hash[:8]}"
            dot_lines.append(f'    "{node_hash}" [label="{label}"];')
            
        for from_hash, action, to_hash in ledger.edges:
            dot_lines.append(f'    "{from_hash}" -> "{to_hash}" [label="{action}"];')
            
        dot_lines.append("}")
        
        with open(output_path, "w") as f:
            f.write("\n".join(dot_lines))
