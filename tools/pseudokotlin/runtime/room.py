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
    """The sqlite3-backed database. register() each entity, then DAOs run query/insert/update/delete."""
    def __init__(self):
        self._conn = sqlite3.connect(":memory:")
        self._conn.row_factory = sqlite3.Row
        self._entities = {}

    def register(self, entity):
        self._entities[entity.table] = entity
        cols = ", ".join(
            f"{c.name} {c.sql_type()}" + (" PRIMARY KEY" if c.pk else "")
            for c in entity.columns)
        self._conn.execute(f"CREATE TABLE IF NOT EXISTS {entity.table} ({cols})")
        return self

    def close(self):
        self._conn.close()

    def query(self, table, sql, params=None, single=False):
        """Run a @Query -> entity objects (or one, or None). Returns a plain list; the DAO wraps it."""
        ent = self._entities[table]
        rows = self._conn.execute(sql, params or {}).fetchall()
        out = [ent.factory({c.name: c.from_db(row[c.name]) for c in ent.columns}) for row in rows]
        if single:
            return out[0] if out else None
        return out

    def insert(self, table, obj, replace=True):
        ent = self._entities[table]
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
    """Base for a generated DAO: holds the database + its entity's table name."""
    def __init__(self, db, table):
        self._db = db
        self._table = table

    def _flow(self, sql, params=None):
        return Flow(self._db.query(self._table, sql, params))

    def _one(self, sql, params=None):
        return self._db.query(self._table, sql, params, single=True)


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
    db = Database().register(Entity("exercises", COLS, ExerciseEntity))

    def ex(id, primary, secondary=()):
        e = ExerciseEntity({"id": id, "name": id,
                            "primaryMuscleGroups": list(primary), "secondaryMuscleGroups": list(secondary)})
        db.insert("exercises", e)
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
    chest = [e.id for e in db.query("exercises", SQL, {"mg": "CHEST"})]
    assert chest == ["first", "last", "only", "secondary"], chest
    abs_hits = [e.id for e in db.query("exercises", SQL, {"mg": "ABS"})]
    assert abs_hits == [], abs_hits                 # token boundary: ABS != ABS_OBLIQUES

    # round-trip an enum_list through the converter
    back = db.query("exercises", "SELECT * FROM exercises WHERE id = :id", {"id": "first"}, single=True)
    assert [m.name for m in back.primaryMuscleGroups] == ["CHEST", "SHOULDERS"]
    print("room self-test: OK (sqlite3 runs the real @Query; whole-token matching holds)")
