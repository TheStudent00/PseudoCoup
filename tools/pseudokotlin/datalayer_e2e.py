"""
datalayer_e2e.py — the data-layer 'oracle': load the REAL transpiled foundation (entities, DAOs, enums),
wire a room.Database, and run an actual @Query end-to-end. Proves the foundation's OWN data layer RUNS --
not just the generators. The instrumented ExerciseDaoMuscleGroupTest can't run headless; this is its
headless equivalent over the same query.

  python3 datalayer_e2e.py
"""
import os
import sys
import glob

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import registry              # noqa: E402

ROOT = os.path.expanduser("~/Programming/WFL_MixingCenter")


def load_foundation():
    """exec the non-UI foundation into one runtime-seeded namespace (multipass for ordering)."""
    ns = dict(registry.namespace())
    files = [f for f in glob.glob(ROOT + "/**/*.py", recursive=True)
             if "/WFL/" not in f and "/__pycache__/" not in f and "/ui/" not in f and "/navigation/" not in f]
    pending = {f: open(f).read() for f in files}
    while pending:
        progressed = False
        for f, src in list(pending.items()):
            try:
                exec(compile(src, f, "exec"), ns)
                del pending[f]
                progressed = True
            except Exception:               # noqa: BLE001 -- a dep not loaded yet; retry next pass
                pass
        if not progressed:
            break
    return ns


def main():
    ns = load_foundation()
    ExerciseEntity, ExerciseDao = ns["ExerciseEntity"], ns["ExerciseDao"]
    MuscleGroup, MovementPattern, EquipmentType = ns["MuscleGroup"], ns["MovementPattern"], ns["EquipmentType"]

    # the real instrumented-test path: Room.inMemoryDatabaseBuilder(...).build().exerciseDao()
    Room, WorkoutDatabase = ns["Room"], ns["WorkoutDatabase"]
    db = Room.inMemoryDatabaseBuilder(None, WorkoutDatabase).build()
    dao = db.exerciseDao()
    mp = next(getattr(MovementPattern, n) for n in dir(MovementPattern) if n.isupper())
    eq = next(getattr(EquipmentType, n) for n in dir(EquipmentType) if n.isupper())
    CHEST, BACK = MuscleGroup.CHEST, MuscleGroup.UPPER_BACK

    def ex(eid, primary, secondary=None):
        return ExerciseEntity(eid, eid, primary, secondary or [], mp, eq, False, False, False,
                              instructions=None, createdAt=0, updatedAt=0)

    dao.insertAll([
        ex("bench", [CHEST]),
        ex("row", [BACK]),                  # no CHEST anywhere -> must NOT match
        ex("incline", [CHEST, BACK]),
        ex("pulldown", [BACK], [CHEST]),    # CHEST in secondary -> must match
    ])

    hits = sorted(e.id for e in dao.getByMuscleGroup("CHEST").first())
    assert hits == ["bench", "incline", "pulldown"], hits     # 'row' correctly excluded
    one = dao.getById("incline").first()                      # Flow<ExerciseEntity?> round-trip
    assert [m.name for m in one.primaryMuscleGroups] == ["CHEST", "UPPER_BACK"]

    # @Update: give 'bench' a BACK secondary -> it now matches a BACK query
    bench = dao.getById("bench").first()
    bench.secondaryMuscleGroups = [BACK]
    dao.update(bench)
    assert "bench" in [e.id for e in dao.getByMuscleGroup("UPPER_BACK").first()]
    # @Delete: remove it -> gone
    dao.delete(bench)
    assert dao.getById("bench").first() is None

    print(f"data-layer e2e: OK -- the REAL transpiled ExerciseDao ran getByMuscleGroup('CHEST') -> {hits} "
          f"on sqlite3; enum_list round-tripped; @Update + @Delete verified.")


if __name__ == "__main__":
    main()
