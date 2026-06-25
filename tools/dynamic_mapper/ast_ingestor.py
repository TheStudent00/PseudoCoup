import json
import os
import re

class ASTIngestor:
    def __init__(self, html_path: str):
        self.html_path = html_path
        self.data = self._extract_data()

    def _extract_data(self) -> dict:
        with open(self.html_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        match = re.search(r'const DATA = (\{.*\});', content)
        if not match:
            raise ValueError("Could not find DATA in " + self.html_path)
        
        return json.loads(match.group(1))

    def get_screens(self) -> dict:
        return self.data.get("screens", {})

    def get_navigation_edges(self) -> dict:
        """Returns a mapping of screen_id to a list of outbound screen_ids"""
        edges = {}
        for slug, screen_data in self.get_screens().items():
            screen_id = screen_data.get("id")
            if not screen_id:
                continue
            edges[screen_id] = screen_data.get("nav_out", [])
        return edges
    
    def find_all_paths(self, start_id: str, max_depth: int = 5) -> list[list[str]]:
        # returns list of paths (lists of screen_ids)
        edges = self.get_navigation_edges()
        paths = []
        
        def dfs(current_id, current_path):
            if len(current_path) > max_depth:
                return
            paths.append(current_path)
            
            for next_id in edges.get(current_id, []):
                if next_id not in current_path: # avoid cycles
                    dfs(next_id, current_path + [next_id])
                    
        dfs(start_id, [start_id])
        return paths

    def get_screen_by_id(self, target_id: str) -> dict:
        for slug, data in self.get_screens().items():
            if data.get("id") == target_id:
                return data
        return {}

    def get_nav_trigger_label(self, source_id: str, target_id: str) -> str:
        """
        Attempts to find the text label of the button/element that triggers navigation 
        from source_id to target_id.
        Looks through the kt_tree of the source_id screen.
        """
        screen = self.get_screen_by_id(source_id)
        if not screen:
            return None
        
        # We search the kt_tree for nodes where nav == target_id or handler == some known transition
        # But wait, looking at uimap/index.html data, navigation targets might not be fully explicit in the kt_tree 
        # or they might be in the 'tree' (the PseudoCoup side). We should check both.
        def walk_tree(nodes, target):
            for node in nodes:
                if node.get("nav") == target:
                    return node.get("label", node.get("kind"))
                # Recurse
                res = walk_tree(node.get("children", []), target)
                if res:
                    return res
            return None

        # Prefer checking kt_tree (ground truth), then tree (PseudoCoup)
        label = walk_tree(screen.get("kt_tree", []), target_id)
        if not label:
            label = walk_tree(screen.get("tree", []), target_id)
        
        return label


if __name__ == "__main__":
    html_file = os.path.join(os.path.dirname(__file__), '..', '..', 'uimap', 'index.html')
    ingestor = ASTIngestor(html_file)
    print(f"Loaded {len(ingestor.get_screens())} screens.")
    paths = ingestor.find_all_paths("today")
    print(f"Found {len(paths)} paths from 'today'.")
    for path in paths[:5]:
        print(path)
