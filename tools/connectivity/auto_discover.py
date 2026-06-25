import os
import re

WFL_UI = os.path.expanduser("~/Programming/WFL/app/src/main/java/com/sara/workoutforlife/ui")
PC_UI = os.path.expanduser("~/Programming/WFL_PseudoCoup/src/ui")
PC_VM = os.path.expanduser("~/Programming/WFL_PseudoCoup/src/viewmodel")

def to_snake_case(name):
    s1 = re.sub('(.)([A-Z][a-z]+)', r'\1_\2', name)
    return re.sub('([a-z0-9])([A-Z])', r'\1_\2', s1).lower()

def discover_screens():
    screens = {}
    for root, _, files in os.walk(WFL_UI):
        for f in files:
            if f.endswith("Screen.kt"):
                slug = f.replace("Screen.kt", "")
                snake_slug = to_snake_case(slug)
                
                k_scr = os.path.join(root, f)
                k_vm = os.path.join(root, f"{slug}ViewModel.kt")
                if not os.path.exists(k_vm):
                    continue
                    
                pc_scr = os.path.join(PC_UI, f"{snake_slug}_screen.py")
                pc_vm = os.path.join(PC_VM, f"{snake_slug}_view_model.py")
                
                if os.path.exists(pc_scr) and os.path.exists(pc_vm):
                    screens[snake_slug] = (k_vm, f"{slug}ViewModel", k_scr, pc_vm, pc_scr)
    return screens

if __name__ == "__main__":
    import pprint
    pprint.pprint(discover_screens())
