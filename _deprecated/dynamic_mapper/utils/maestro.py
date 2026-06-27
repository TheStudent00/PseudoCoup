import subprocess
import json
import os

class MaestroUtils:
    @staticmethod
    def get_maestro_path() -> str:
        local_path = os.path.expanduser("~/.maestro/bin/maestro")
        if os.path.exists(local_path):
            return local_path
        return "maestro" 

    @staticmethod
    def get_hierarchy() -> dict:
        try:
            result = subprocess.run([MaestroUtils.get_maestro_path(), "hierarchy"], capture_output=True, text=True, check=True)
            return json.loads(result.stdout)
        except (subprocess.CalledProcessError, json.JSONDecodeError) as e:
            return {}

    @staticmethod
    def tap(app_id: str, element_id: str) -> bool:
        yaml_content = f"""
appId: {app_id}
---
- tapOn: "{element_id}"
"""
        with open("/tmp/temp_flow.yaml", "w") as f:
            f.write(yaml_content)
        try:
            subprocess.run([MaestroUtils.get_maestro_path(), "test", "/tmp/temp_flow.yaml"], check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            return True
        except subprocess.CalledProcessError:
            return False

    @staticmethod
    def back(app_id: str) -> bool:
        yaml_content = f"""
appId: {app_id}
---
- pressKey: back
"""
        with open("/tmp/temp_flow.yaml", "w") as f:
            f.write(yaml_content)
        try:
            subprocess.run([MaestroUtils.get_maestro_path(), "test", "/tmp/temp_flow.yaml"], check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            return True
        except subprocess.CalledProcessError:
            return False
