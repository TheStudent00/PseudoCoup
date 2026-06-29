"""
runtime/room.py — an in-memory, sqlite3-backed stand-in for Room. This is a FAITHFUL data layer, not a
stub: Room's @Query strings are real SQLite SQL with :named params, and Python's sqlite3 IS SQLite, so the
queries run verbatim. An @Entity becomes a table; a DAO method runs its @Query and maps rows back to
entity objects (wrapped in a synchronous Flow); converters bridge entity fields and columns
(List<Enum> <-> comma string, Boolean <-> 0/1, Enum <-> name) -- the same job Room's @TypeConverter does.

What the transpiler feeds this (the wiring step): each @Entity's table + column specs, each DAO method's
SQL. Until then, the self-test at the bottom hand-builds the ExerciseDao muscle-group query to prove the
engine runs the real query logic (whole-token matching, so ABS does not match ABS_OBLIQUES).
"""
import sqlite3
import re as _re

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from runtime.coroutines import Flow  # noqa: E402  -- DAO query methods return a Flow


class Col:
    """One entity field <-> one column, with the conversion Room's TypeConverters would do."""
    def __init__(self, name, kind="text", enum=None, pk=False):
        self.name, self.kind, self.enum, self.pk = name, kind, enum, pk

    def to_db(self, v):
        if v is None:
            return None
        if self.kind == "bool":
            return 1 if v else 0
        if self.kind == "enum":
            return v.name if hasattr(v, "name") else str(v)
        if self.kind == "enum_list":
            return ",".join(e.name for e in v)
        return v

    def from_db(self, v):
        if v is None:
            return None
        if self.kind == "bool":
            return bool(v)
        if self.kind == "enum":
            return self.enum.valueOf(v) if self.enum is not None else v
        if self.kind == "enum_list":
            return [] if not v else [self.enum.valueOf(t.strip()) for t in v.split(",")]
        return v

    def sql_type(self):
        return {"int": "INTEGER", "long": "INTEGER", "real": "REAL", "bool": "INTEGER"}.get(self.kind, "TEXT")


class Entity:
    """Binds an entity class to a table: its columns + a factory(dict)->instance for reads."""
    def __init__(self, table, columns, factory):
        self.table, self.columns, self.factory = table, columns, factory


class Database:
    """The sqlite3-backed database. register(EntityClass) each entity (it carries cls._room), then DAOs
    run SQL -- the table is derived from the SQL's FROM (reads) or the entity class (writes)."""
    def __init__(self):
        self._conn = sqlite3.connect(":memory:")
        self._conn.row_factory = sqlite3.Row
        self._entities = {}                 # table name -> Entity

    def register(self, cls):
        ent = cls._room                     # entity_schema sets `Cls._room = Entity(...)`
        self._entities[ent.table] = ent
        cols = ", ".join(
            f"{c.name} {c.sql_type()}" + (" PRIMARY KEY" if c.pk else "")
            for c in ent.columns)
        self._conn.execute(f"CREATE TABLE IF NOT EXISTS {ent.table} ({cols})")
        return self

    def close(self):
        self._conn.close()

    def query(self, sql, params=None, single=False):
        """Run a @Query. If its FROM table is a known entity, map rows -> entity objects (one/None when
        single); otherwise (a scalar/aggregate query) return raw row tuples."""
        rows = self._conn.execute(sql, params or {}).fetchall()
        m = _re.search(r"\bFROM\s+(\w+)", sql, _re.IGNORECASE)
        ent = self._entities.get(m.group(1)) if m else None
        if ent is None:
            out = [tuple(r) for r in rows]
        else:
            out = [ent.factory({c.name: c.from_db(row[c.name]) for c in ent.columns}) for row in rows]
        if single:
            return out[0] if out else None
        return out

    def insert(self, obj, replace=True):
        ent = obj.__class__._room
        names = ", ".join(c.name for c in ent.columns)
        holes = ", ".join(f":{c.name}" for c in ent.columns)
        verb = "INSERT OR REPLACE" if replace else "INSERT OR IGNORE"
        vals = {c.name: c.to_db(getattr(obj, c.name)) for c in ent.columns}
        self._conn.execute(f"{verb} INTO {ent.table} ({names}) VALUES ({holes})", vals)

    def execute(self, sql, params=None):
        """A raw @Query that isn't a row->entity SELECT (UPDATE/DELETE, or a scalar)."""
        cur = self._conn.execute(sql, params or {})
        self._conn.commit()
        return cur


class Dao:
    """Base for a generated DAO -- holds the database; query helpers wrap results the way Room's return
    types do (Flow<List> / Flow<one> / suspend one)."""
    def __init__(self, db):
        self._db = db

    def _flow(self, sql, params=None):          # Flow<List<X>> -- emits the whole list as ONE value
        return Flow([self._db.query(sql, params)])

    def _flowOne(self, sql, params=None):       # Flow<X?> -- emits the single entity (or None) as one value
        return Flow([self._db.query(sql, params, single=True)])

    def _one(self, sql, params=None):           # suspend X?
        return self._db.query(sql, params, single=True)

    def _insert(self, obj, replace=True):       # @Insert one or a list
        for e in (obj if isinstance(obj, list) else [obj]):
            self._db.insert(e, replace)


# ---- self-test: run the real ExerciseDao muscle-group query against sqlite3 --------------------- #
if __name__ == "__main__":
    class MuscleGroup:                       # a stand-in enum (the foundation's transpiled enums look like this)
        def __init__(self, name):
            self.name = name
        _by = {}

        @staticmethod
        def valueOf(s):
            return MuscleGroup._by[s]

    for _n in ("CHEST", "SHOULDERS", "ABS", "ABS_OBLIQUES"):
        MuscleGroup._by[_n] = MuscleGroup(_n)
    CHEST, SHOULDERS, ABS, ABS_OBLIQUES = (MuscleGroup._by[n] for n in ("CHEST", "SHOULDERS", "ABS", "ABS_OBLIQUES"))

    class ExerciseEntity:
        def __init__(self, kw):
            self.id = kw["id"]; self.name = kw["name"]
            self.primaryMuscleGroups = kw["primaryMuscleGroups"]
            self.secondaryMuscleGroups = kw["secondaryMuscleGroups"]

    COLS = [Col("id", pk=True), Col("name"),
            Col("primaryMuscleGroups", "enum_list", MuscleGroup),
            Col("secondaryMuscleGroups", "enum_list", MuscleGroup)]
    ExerciseEntity._room = Entity("exercises", COLS, lambda kw: ExerciseEntity(kw))
    db = Database().register(ExerciseEntity)

    def ex(id, primary, secondary=()):
        e = ExerciseEntity({"id": id, "name": id,
                            "primaryMuscleGroups": list(primary), "secondaryMuscleGroups": list(secondary)})
        db.insert(e)
        return e

    ex("only", [CHEST])
    ex("first", [CHEST, SHOULDERS])
    ex("last", [SHOULDERS, CHEST])
    ex("abs_obliques_only", [ABS_OBLIQUES])     # must NOT match a query for ABS
    ex("secondary", [SHOULDERS], [CHEST])

    SQL = ("SELECT * FROM exercises "
           "WHERE (',' || primaryMuscleGroups || ',') LIKE '%,' || :mg || ',%' "
           "   OR (',' || secondaryMuscleGroups || ',') LIKE '%,' || :mg || ',%' "
           "ORDER BY name ASC")
    chest = [e.id for e in db.query(SQL, {"mg": "CHEST"})]
    assert chest == ["first", "last", "only", "secondary"], chest
    abs_hits = [e.id for e in db.query(SQL, {"mg": "ABS"})]
    assert abs_hits == [], abs_hits                 # token boundary: ABS != ABS_OBLIQUES

    # round-trip an enum_list through the converter
    back = db.query("SELECT * FROM exercises WHERE id = :id", {"id": "first"}, single=True)
    assert [m.name for m in back.primaryMuscleGroups] == ["CHEST", "SHOULDERS"]
    print("room self-test: OK (sqlite3 runs the real @Query; whole-token matching holds)")
