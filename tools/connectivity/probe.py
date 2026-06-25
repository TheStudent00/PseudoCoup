#!/usr/bin/env python3
"""
probe.py -- Phase-1 connectivity probe (STATIC, no runtime).

A grounded prototype of log_18/log_19's idea: treat the Kotlin ViewModel as the
fully-connected REFERENCE (every state field + action + the screen's wiring to them
is a static reference in the source), then VERIFY the PseudoCoup side preserves each
edge. This is "Level 1" -- check, not regenerate. It demonstrates that the
connectivity the ingest tool merely FLAGS is in fact statically RESOLVABLE, and that
PC can be diffed against it edge-by-edge.

Reuses ingest's tree-sitter Kotlin parser (answering Gemini's open question: yes, the
existing bindings carry this).

Run:  python3 tools/connectivity/probe.py [screen_slug]   (default: report_bug)
"""

import ast
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(os.path.dirname(HERE))
WFL_PC_REPO = os.path.expanduser("~/Programming/WFL_PseudoCoup")
sys.path.insert(0, os.path.join(WFL_PC_REPO, "tools", "ingest"))
from ingest import _build_parser   # noqa: E402  (tree-sitter Kotlin parser)

WFL = os.path.expanduser("~/Programming/WFL/app/src/main/java/com/sara/workoutforlife")

WFL_UI = os.path.expanduser("~/Programming/WFL/app/src/main/java/com/sara/workoutforlife/ui")
PC_UI = os.path.expanduser("~/Programming/WFL_PseudoCoup/src/ui")
PC_VM = os.path.expanduser("~/Programming/WFL_PseudoCoup/src/viewmodel")

def _to_snake_case(name):
    s1 = re.sub('(.)([A-Z][a-z]+)', r'\1_\2', name)
    return re.sub('([a-z0-9])([A-Z])', r'\1_\2', s1).lower()

def discover_screens():
    screens = {}
    for root, _, files in os.walk(WFL_UI):
        for f in files:
            if f.endswith("Screen.kt"):
                slug = f.replace("Screen.kt", "")
                snake_slug = _to_snake_case(slug)
                
                k_scr = os.path.join(root, f)
                k_vm = os.path.join(root, f"{slug}ViewModel.kt")
                if not os.path.exists(k_vm):
                    continue
                    
                pc_scr = os.path.join(PC_UI, f"{snake_slug}_screen.py")
                pc_vm = os.path.join(PC_VM, f"{snake_slug}_view_model.py")
                
                if os.path.exists(pc_scr) and os.path.exists(pc_vm):
                    screens[snake_slug] = (k_vm, f"{slug}ViewModel", k_scr, pc_vm, pc_scr)
    return screens

SCREENS = discover_screens()


# ---- tiny tree-sitter helpers ---------------------------------------------- #

def txt(n):
    return n.text.decode("utf-8", "replace")


def walk(n):
    yield n
    for c in n.children:
        yield from walk(c)


def name_of(node):
    """The declared name: a direct `identifier` child (class/fun/param), else the
    identifier inside a variable_declaration (property), else first identifier seen."""
    for c in node.children:
        if c.type == "identifier":
            return txt(c)
    for c in node.children:
        if c.type in ("variable_declaration", "parameter"):
            for cc in c.children:
                if cc.type == "identifier":
                    return txt(cc)
    for d in walk(node):
        if d.type == "identifier":
            return txt(d)
    return None


def enclosing_class(node):
    p = node.parent
    while p is not None:
        if p.type == "class_declaration":
            return name_of(p)
        p = p.parent
    return None


def snake(s):
    """camelCase -> snake_case (to compare Kotlin names with PC's snake_case)."""
    return re.sub(r"(?<!^)(?=[A-Z])", "_", s).lower()


# ---- Kotlin side: the fully-connected REFERENCE ---------------------------- #

def kotlin_vm(path, vm_class):
    """State fields (data-class UiState params + derived val-getters) and actions
    (fun at the VM class level) -- the VM's logical nodes."""
    root = _build_parser().parse(open(path, "rb").read()).root_node
    state, derived, actions = [], [], []
    for n in walk(root):
        if n.type == "class_declaration":
            cname = name_of(n) or ""
            is_data = txt(n).lstrip().startswith("data class") or " data class" in txt(n)[:30]
            if is_data and cname.endswith("UiState"):
                for p in walk(n):
                    if p.type == "class_parameter":
                        nm = name_of(p)
                        if nm:
                            state.append(nm)
                # derived val with a getter (e.g. canSubmit)
                for p in walk(n):
                    if p.type == "property_declaration" and "get()" in txt(p):
                        nm = name_of(p)
                        if nm and nm not in state:
                            derived.append(nm)
        if n.type == "function_declaration" and enclosing_class(n) == vm_class:
            nm = name_of(n)
            if nm:
                actions.append(nm)
    return state, derived, actions


def kotlin_screen_wiring(path):
    """The screen->vm edges, statically: every `<recv>.<member>` where recv is the
    state/uiState/viewModel handle. Plus navigate() destinations."""
    src = open(path).read()
    # field reads = state.X, minus state.X(...) which are method calls (e.g.
    # state.collectAsStateWithLifecycle()), not UiState field reads.
    all_state = set(re.findall(r"\b(?:state|uiState)\.([a-zA-Z]\w*)", src))
    state_calls = set(re.findall(r"\b(?:state|uiState)\.([a-zA-Z]\w*)\s*\(", src))
    reads = sorted(all_state - state_calls)
    calls = sorted(set(re.findall(r"\b(?:viewModel|vm)\.([a-zA-Z]\w*)\s*\(", src)))
    refs = sorted(set(re.findall(r"\b(?:viewModel|vm)::([a-zA-Z]\w*)", src)))  # method refs
    navs = sorted(set(re.findall(r'navigate\(\s*"([^"]+)"', src)))
    return reads, sorted(set(calls + refs)), navs


# ---- PC side: what we VERIFY ----------------------------------------------- #

def pc_vm(path):
    """PC State fields (self.X: State = State(...) in __init__) + public methods."""
    tree = ast.parse(open(path).read())
    cls = next((n for n in tree.body if isinstance(n, ast.ClassDef)), None)
    fields, methods = [], []
    if cls:
        for m in cls.body:
            if isinstance(m, ast.FunctionDef):
                if not m.name.startswith("__"):
                    methods.append(m.name)
                if m.name == "__init__":
                    for s in ast.walk(m):
                        if isinstance(s, ast.AnnAssign) and isinstance(s.target, ast.Attribute):
                            ann = getattr(s.annotation, "id", None)
                            if ann == "State":
                                fields.append(s.target.attr)
    return fields, methods


def pc_screen_wiring(path):
    src = open(path).read()
    reads = sorted(set(re.findall(r"self\.vm\.(\w+)\.value", src)))
    calls = sorted(set(re.findall(r"self\.vm\.(\w+)\s*\(", src)))
    navs = sorted(set(re.findall(r'navigate\(\s*"([^"]+)"', src)))
    return reads, calls, navs


# ---- verify + report -------------------------------------------------------- #

def check(kotlin_names, pc_names, label, out_file=None):
    """For each Kotlin connectivity node, is there a PC counterpart (snake-mapped)?"""
    pcset = set(pc_names)
    msg = "\n%s" % label
    print(msg)
    if out_file: out_file.write(msg + "\n")
    
    ok = 0
    for k in kotlin_names:
        cand = snake(k)
        # accept exact snake match, or a method that starts with it (on_x_change etc.)
        hit = next((p for p in pc_names if p == cand or p.replace("_", "") == cand.replace("_", "")), None)
        mark = "OK " if hit else "GAP"
        if hit:
            ok += 1
        msg = "   [%s] %-24s -> %s" % (mark, k, hit or "(* no PC counterpart *)")
        print(msg)
        if out_file: out_file.write(msg + "\n")
        
    extra = [p for p in pc_names if p not in {None}]  # informational
    msg = "   %d/%d Kotlin %s have a PC counterpart" % (ok, len(kotlin_names), label.split()[0].lower())
    print(msg)
    if out_file: out_file.write(msg + "\n")
    return ok, len(kotlin_names)

def run_probe_for_screen(slug, out_file=None):
    kvm_path, vm_class, kscr_path, pcvm_path, pcscr_path = SCREENS[slug]

    k_state, k_derived, k_actions = kotlin_vm(kvm_path, vm_class)
    k_reads, k_calls, k_navs = kotlin_screen_wiring(kscr_path)
    p_fields, p_methods = pc_vm(pcvm_path)
    p_reads, p_calls, p_navs = pc_screen_wiring(pcscr_path)

    msg = "=" * 70 + "\n"
    msg += "CONNECTIVITY PROBE (static) -- %s\n" % slug
    msg += "Kotlin VM is the reference; PC is verified against it.\n"
    msg += "=" * 70 + "\n"
    print(msg, end="")
    if out_file: out_file.write(msg)
    
    msg = "\nKotlin reference graph (%s):\n" % vm_class
    msg += "  state fields : %s\n" % ", ".join(k_state)
    msg += "  derived      : %s\n" % ", ".join(k_derived)
    msg += "  actions      : %s\n" % ", ".join(k_actions)
    msg += "  screen reads : %s\n" % ", ".join(k_reads)
    msg += "  screen calls : %s\n" % ", ".join(k_calls)
    msg += "  screen navs  : %s\n" % ", ".join(k_navs)
    print(msg, end="")
    if out_file: out_file.write(msg)
    
    msg = "\nPseudoCoup side:\n"
    msg += "  State fields : %s\n" % ", ".join(p_fields)
    msg += "  methods      : %s\n" % ", ".join(p_methods)
    msg += "  screen reads : %s\n" % ", ".join(p_reads)
    msg += "  screen calls : %s\n" % ", ".join(p_calls)
    msg += "  screen navs  : %s\n" % ", ".join(p_navs)
    print(msg, end="")
    if out_file: out_file.write(msg)

    msg = "\n" + "-" * 70 + "\n"
    msg += "VERIFY: every Kotlin connectivity node has a PC counterpart?\n"
    print(msg, end="")
    if out_file: out_file.write(msg)
    
    a1 = check(k_state, p_fields, "STATE fields (vm.state -> PC State)", out_file)
    a2 = check(k_derived + k_actions, p_methods, "ACTIONS/derived (vm methods -> PC methods)", out_file)
    a3 = check(k_calls, p_calls, "SCREEN->vm action edges (screen calls the action)", out_file)
    tot_ok = a1[0] + a2[0] + a3[0]
    tot = a1[1] + a2[1] + a3[1]
    
    msg = "\n%s  CONNECTIVITY: %d/%d Kotlin edges preserved in PC%s\n" % ("=" * 8, tot_ok, tot, "  (FULLY CONNECTED)" if tot_ok == tot else "  <-- GAPS ABOVE")
    print(msg, end="")
    if out_file: out_file.write(msg)
    
    return tot_ok, tot


def main():
    if len(sys.argv) > 1 and sys.argv[1] != "all":
        slug = sys.argv[1]
        if slug in SCREENS:
            run_probe_for_screen(slug)
        else:
            print(f"Screen {slug} not found.")
    else:
        out_path = os.path.expanduser("~/Programming/PseudoCoup/connectivity_audit_results.md")
        with open(out_path, "w") as f:
            f.write("# Connectivity Audit Results\n\n")
            total_ok = 0
            total_edges = 0
            
            for slug in sorted(SCREENS.keys()):
                ok, edges = run_probe_for_screen(slug, f)
                total_ok += ok
                total_edges += edges
                f.write("\n\n")
                
            summary = f"\n# SUMMARY\nTotal Edges Preserved: {total_ok}/{total_edges} ({(total_ok/total_edges)*100:.2f}%)\n"
            print(summary)
            f.write(summary)
        print(f"Full audit written to {out_path}")


if __name__ == "__main__":
    main()
