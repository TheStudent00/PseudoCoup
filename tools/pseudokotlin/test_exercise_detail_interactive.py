"""exercise_detail interaction proof (sandbox): render + SharedFlow edit-nav + the reactive
exclude-prompt dialog. Run from PseudoCoup/tools/pseudokotlin. Companion to test_gym_list_gen."""
import pseudoui_run as R

O, KL = R.O, R.KL
cname, ir = R.build_ir(O.find_one(O.MAIN, "ExerciseDetailScreen.kt"))
src = R.emit_app_screen(ir, "exercise_detail", "ExerciseDetailScreenGen")
KL._setup_modules()
db = KL._seeded_db()
g = {"build_transpiled_vm": R.build_transpiled_vm}
exec(compile(src, "gen.py", "exec"), g)                # noqa: S102 -- generated, trusted


class RecRouter:
    def __init__(self, sel): self.selected_id = sel; self.navs = []
    def navigate(self, t): self.navs.append(t)
    def __getattr__(self, n): return lambda *a, **k: None


def leaves(gen, router):
    rec = KL._RecUI()
    gen.build(rec, "content", router)
    return [a for k, z, s, a in rec.recs if k in ("text", "button") and a]


gen = g["ExerciseDetailScreenGen"](db)
router = RecRouter("eSquat")
checks = []

# 1. render: shared leaves vs the hand-built screen (same seeded squat)
b1 = leaves(gen, router)
shared = len({(KL._ntype("text"), a) for a in b1})
checks.append(("renders the seeded exercise (>=8 leaves)", len(b1) >= 8))

# 2. SharedFlow edit-nav: vm.editCurrent() emits navigateToEdit -> collector -> _nav_edit -> navigate
before = len(router.navs)
gen.vm.editCurrent()
checks.append(("editCurrent() -> SharedFlow nav to 'exercise_create'",
               router.navs[before:] == ["exercise_create"]))

# 3. reactive dialog: onToggleExcluded sets excludePrompt -> rebuild renders the AlertDialog
DIALOG = {("Already in your program",), ("Got it",), ("Cancel",)}
gen.vm.onToggleExcluded()
b2 = set(leaves(gen, router))
checks.append(("onToggleExcluded() -> exclude-prompt dialog renders", bool(DIALOG & b2)))

# 4. dismiss clears excludePrompt -> rebuild, dialog gone (MutableStateFlow->State repaint)
gen.vm.confirmSwapLater()
b3 = set(leaves(gen, router))
checks.append(("confirmSwapLater() -> dialog dismissed (no stale dialog)", not (DIALOG & b3)))

print("exercise_detail interaction proof (transpiled VM + generator):")
ok = True
for label, passed in checks:
    print(f"  {'OK  ' if passed else 'FAIL'} {label}")
    ok = ok and passed
print("RESULT:", "ALL PASS" if ok else "FAILURES")
