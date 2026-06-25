import yaml
import os

class FlowGenerator:
    """
    Generates Maestro .yaml test flows for the Tracer Dye cross-validation loop.
    """
    def __init__(self, output_dir: str = "runtime_uimap/flows"):
        self.output_dir = output_dir
        os.makedirs(self.output_dir, exist_ok=True)

    def generate_flow(self, test_name: str, app_id: str, taps: list[str], launch: bool = True) -> str:
        """
        Generates a Maestro yaml flow that performs a series of taps.
        """
        flow = {
            "appId": app_id,
            "---": None # YAML separator
        }
        
        commands = []
        if launch:
            commands.append({"launchApp": {"appId": app_id}})
            commands.append({"extendedWaitUntil": {"visible": {"id": ".*"}, "timeout": 5000}})
            
        for tap in taps:
            commands.append({"tapOn": tap})
            # Add a small wait to allow for transitions
            commands.append({"extendedWaitUntil": {"visible": {"id": ".*"}, "timeout": 3000}})
            
        file_path = os.path.join(self.output_dir, f"{test_name}.yaml")
        
        with open(file_path, 'w') as f:
            f.write(f"appId: {app_id}\n")
            f.write("---\n")
            for cmd in commands:
                if "launchApp" in cmd:
                    f.write(f"- launchApp:\n    appId: \"{cmd['launchApp']['appId']}\"\n")
                elif "tapOn" in cmd:
                    f.write(f"- tapOn: \"{cmd['tapOn']}\"\n")
                elif "extendedWaitUntil" in cmd:
                    f.write(f"- extendedWaitUntil:\n    visible:\n      id: \".*\"\n    timeout: 3000\n")
                    
        return file_path

if __name__ == "__main__":
    generator = FlowGenerator()
    # Generate a test flow to go from Today -> Warmup -> Execution
    taps = ["Start Workout", "Start Warmup"]
    wfl_flow = generator.generate_flow("test_wfl_start_workout", "com.sara.workoutforlife", taps)
    pc_flow = generator.generate_flow("test_pc_start_workout", "com.example.wfl_pseudocoup_flutter", taps)
    print(f"Generated flows: \n{wfl_flow}\n{pc_flow}")
