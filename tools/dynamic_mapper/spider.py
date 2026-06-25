import argparse
import os
import sys
import time
import subprocess

# Ensure local modules can be imported
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from core.ledger import GraphLedger
from utils.maestro import MaestroUtils
from utils.visualizer import Visualizer
from core.state import SemanticState
from core.parser import StateParser

MAX_DEPTH = 3
MAX_BUTTONS_PER_SCREEN = 5

APPS = {
    "wfl": "com.sara.workoutforlife",
    "pc": "com.example.wfl_pseudocoup_flutter"
}

class DynamicSpider:
    def __init__(self, app_key: str, output_dir="/home/lucas/Programming/PseudoCoup/runtime_uimap"):
        self.app_key = app_key
        self.package_name = APPS[app_key]
        self.output_dir = output_dir
        os.makedirs(self.output_dir, exist_ok=True)
        
        self.ledger_path = os.path.join(self.output_dir, f"{self.app_key}_ledger.json")
        self.ledger = GraphLedger(storage_path=self.ledger_path)
        
        self.visited_states = set()
        self.bad_buttons = {"Navigate up", "Back", "Close", "Not now", "Not yet", "Skip check-in"}

    def start_app(self):
        print(f"Starting {self.package_name} via ADB...")
        adb_path = os.path.expanduser("~/Android/Sdk/platform-tools/adb")
        try:
            subprocess.run([adb_path, "shell", "monkey", "-p", self.package_name, "-c", "android.intent.category.LAUNCHER", "1"], 
                           capture_output=True, check=True)
        except subprocess.CalledProcessError as e:
            print(f"Failed to launch app: {e}")

    def get_semantic_state(self) -> SemanticState:
        # Get UI hierarchy
        hierarchy = MaestroUtils.get_hierarchy()
        ui_context = StateParser.parse_ui_hierarchy(hierarchy)
        
        # We don't have active DB diagnostics via BroadcastReceiver right now, 
        # so we rely purely on UI context.
        base_state = SemanticState()
        return StateParser.merge_state(base_state, ui_context)

    def run(self):
        print(f"=== Starting Dynamic UI Spider ({self.app_key.upper()}) ===")
        self.start_app()
        
        print("Waiting for app to initialize...")
        for _ in range(10):
            time.sleep(2)
            test_state = self.get_semantic_state()
            if len(test_state.ui_buttons) > 0:
                print(f"App is ready with {len(test_state.ui_buttons)} UI elements.")
                break
            print("Still waiting for app...")
            
        print("Beginning DFS UI Crawl...")
        self.explore_node(0, [])
        
        print("\n=== Crawl Complete ===")
        print(f"Discovered {len(self.ledger.nodes)} states and {len(self.ledger.edges)} transitions.")
        out_file_mmd = os.path.join(self.output_dir, f"{self.app_key}_map.mmd")
        out_file_md = os.path.join(self.output_dir, f"{self.app_key}_map.md")
        
        Visualizer.export_mermaid(self.ledger, out_file_mmd)
        Visualizer.export_markdown_mermaid(self.ledger, out_file_md)
        print(f"Exported visual maps to {out_file_mmd} and {out_file_md}")

    def explore_node(self, depth: int, path: list):
        if depth >= MAX_DEPTH:
            return

        current_state = self.get_semantic_state()
        state_hash = current_state.get_identity_hash()

        if state_hash in self.visited_states:
            return
        self.visited_states.add(state_hash)

        buttons = [b for b in current_state.ui_buttons if b not in self.bad_buttons][:MAX_BUTTONS_PER_SCREEN]
        print(f"{' ' * depth}[Depth {depth}] Exploring screen: {current_state.current_screen} ({len(buttons)} buttons)")

        for btn in buttons:
            print(f"{' ' * (depth+1)}-> Tapping '{btn}'")
            success = MaestroUtils.tap(self.package_name, btn)
            if not success:
                print(f"{' ' * (depth+4)}(Failed to tap)")
                continue
            
            time.sleep(2) # Wait for transition
            new_state = self.get_semantic_state()
            new_hash = new_state.get_identity_hash()

            if state_hash != new_hash:
                self.ledger.record_transition(current_state, f"tap('{btn}')", new_state)
                self.explore_node(depth + 1, path + [btn])

                # Rewind
                print(f"{' ' * (depth+1)}<- Backing out to {current_state.current_screen}")
                MaestroUtils.back(self.package_name)
                time.sleep(2)

                recovery_state = self.get_semantic_state()
                if recovery_state.get_identity_hash() != state_hash:
                    print(f"{' ' * (depth+1)}[WARNING] Back button did not restore exact state! Desync possible.")
            else:
                print(f"{' ' * (depth+4)}(No state change detected)")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Dynamic UI Mapper using Maestro")
    parser.add_argument("--app", choices=["wfl", "pc"], required=True, help="Target application to crawl")
    args = parser.parse_args()
    
    spider = DynamicSpider(app_key=args.app)
    spider.run()
