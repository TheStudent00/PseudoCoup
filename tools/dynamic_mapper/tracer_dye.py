import os
import subprocess
import json
from flow_generator import FlowGenerator
from core.parser import StateParser

class TracerDye:
    def __init__(self):
        self.generator = FlowGenerator()
        
    def _run_maestro(self, flow_path: str):
        # We need absolute path because maestro can be picky
        maestro_path = os.path.expanduser("~/.maestro/bin/maestro")
        if not os.path.exists(maestro_path):
            maestro_path = "maestro"
        
        print(f"Running flow: {flow_path}")
        subprocess.run([maestro_path, "test", flow_path], check=False, stdout=subprocess.DEVNULL)
        
    def _dump_hierarchy(self) -> dict:
        maestro_path = os.path.expanduser("~/.maestro/bin/maestro")
        if not os.path.exists(maestro_path):
            maestro_path = "maestro"
        
        result = subprocess.run([maestro_path, "hierarchy"], capture_output=True, text=True)
        if result.returncode == 0:
            try:
                return json.loads(result.stdout)
            except Exception:
                return {}
        return {}
        
    def run_trace(self, test_name: str, taps: list[str]):
        print(f"\n=== Running Tracer Dye Test: {test_name} ===")
        print(f"Path: {' -> '.join(taps)}")
        
        # 1. Generate flows
        wfl_path = self.generator.generate_flow(f"wfl_{test_name}", "com.sara.workoutforlife", taps)
        pc_path = self.generator.generate_flow(f"pc_{test_name}", "com.example.wfl_pseudocoup_flutter", taps)
        
        # 2. Run WFL
        print("\n--- Executing Kotlin (WFL) ---")
        adb_path = os.path.expanduser("~/Android/Sdk/platform-tools/adb")
        subprocess.run([adb_path, "shell", "am", "force-stop", "com.sara.workoutforlife"])
        self._run_maestro(wfl_path)
        wfl_hierarchy = self._dump_hierarchy()
        wfl_state = StateParser.parse_ui_hierarchy(wfl_hierarchy)
        
        # 3. Run PC
        print("\n--- Executing Flutter (PseudoCoup) ---")
        subprocess.run([adb_path, "shell", "am", "force-stop", "com.example.wfl_pseudocoup_flutter"])
        self._run_maestro(pc_path)
        pc_hierarchy = self._dump_hierarchy()
        pc_state = StateParser.parse_ui_hierarchy(pc_hierarchy)
        
        # 4. Diff and Report
        self._generate_report(test_name, taps, wfl_state, pc_state)
        
    def _generate_report(self, test_name: str, taps: list[str], wfl_state: dict, pc_state: dict):
        report_path = f"runtime_uimap/tracer_{test_name}.md"
        wfl_buttons = set(wfl_state.get("buttons", []))
        pc_buttons = set(pc_state.get("buttons", []))
        
        missing_in_pc = wfl_buttons - pc_buttons
        extra_in_pc = pc_buttons - wfl_buttons
        matched = wfl_buttons.intersection(pc_buttons)
        
        with open(report_path, "w") as f:
            f.write(f"# Tracer Dye Report: {test_name}\n\n")
            f.write(f"**Sequence:** `App Launch -> {' -> '.join(taps)}`\n\n")
            
            f.write("## 🛑 Missing in PseudoCoup\n")
            f.write("These buttons/texts appeared in Kotlin but NOT in Flutter. This indicates the transpiler failed to route us to the correct screen, or failed to render these elements.\n")
            for b in sorted(missing_in_pc):
                f.write(f"- `{b}`\n")
                
            f.write("\n## ⚠️ Extra in PseudoCoup\n")
            f.write("These appeared in Flutter but NOT Kotlin.\n")
            for b in sorted(extra_in_pc):
                f.write(f"- `{b}`\n")
                
            f.write("\n## ✅ Matched Elements\n")
            for b in sorted(matched):
                f.write(f"- `{b}`\n")
                
        print(f"\nReport generated: {report_path}")
        print(f"Missing elements: {len(missing_in_pc)}")
        print(f"Extra elements: {len(extra_in_pc)}")
        
if __name__ == "__main__":
    tracer = TracerDye()
    
    # Let's test the navigation to workout warmup, which the ingest transpiler handled for "workout_warmup_screen.kt"
    # The Kotlin app's "Start Workout" button triggers the warmup if it's the first time today.
    # Note: If the button is not found, maestro test will fail and wait to timeout.
    tracer.run_trace("start_workout", ["Start Workout"])
