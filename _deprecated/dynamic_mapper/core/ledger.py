import json
import os
from core.state import SemanticState

class GraphLedger:
    """
    A persistent record of all explored app states and transitions.
    """
    def __init__(self, storage_path: str = "ledger_graph.json"):
        self.storage_path = storage_path
        self.nodes = {} # Hash -> SemanticState as dict
        self.edges = [] # List of (from_hash, action, to_hash)
        self.load()

    def record_transition(self, state_a: SemanticState, action: str, state_b: SemanticState):
        """
        Records a transition from State A to State B via an Action.
        """
        hash_a = state_a.get_identity_hash()
        hash_b = state_b.get_identity_hash()

        if hash_a not in self.nodes:
            self.nodes[hash_a] = self._state_to_dict(state_a)
        
        if hash_b not in self.nodes:
            self.nodes[hash_b] = self._state_to_dict(state_b)

        # Record edge if it doesn't exist
        edge = (hash_a, action, hash_b)
        if edge not in self.edges:
            self.edges.append(edge)
            print(f"Ledger: New transition recorded: {action}")
            self.save()

    def get_identity_hash_count(self, identity_hash: str) -> int:
        return 1 if identity_hash in self.nodes else 0

    def get_coverage_gaps(self) -> list[str]:
        explored_sources = {e[0] for e in self.edges}
        return [h for h in self.nodes.keys() if h not in explored_sources]

    def _state_to_dict(self, state: SemanticState) -> dict:
        from dataclasses import asdict
        return asdict(state)

    def save(self):
        data = {
            "nodes": self.nodes,
            "edges": self.edges
        }
        with open(self.storage_path, "w") as f:
            json.dump(data, f, indent=2)

    def load(self):
        if os.path.exists(self.storage_path):
            try:
                with open(self.storage_path, "r") as f:
                    data = json.load(f)
                    self.nodes = data.get("nodes", {})
                    self.edges = [tuple(e) for e in data.get("edges", [])]
            except Exception as e:
                print(f"Error loading ledger: {e}")
