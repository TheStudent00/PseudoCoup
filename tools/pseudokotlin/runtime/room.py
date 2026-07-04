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
import json as _json

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from runtime.coroutines import Flow      # noqa: E402  -- DAO query methods return a Flow
from runtime.kotlin_rt import KtList      # noqa: E402  -- query results carry Kotlin collection methods

# Room's exported schema JSON (one file per version), used by MigrationTestHelper to recreate an old
# schema and validate the result after replaying migrations.
_SCHEMA_DIR = os.path.normpath(os.path.join(
    os.path.dirname(__file__), "..", "..", "..", "..", "WFL_MixingCenter", "WFL", "app", "schemas",
    "com.sara.workoutforlife.data.db.WorkoutDatabase"))
_NAMED_DBS = {}                 # name -> sqlite3 conn, shared between MigrationTestHelper and the builder


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
            return KtList() if not v else KtList(self.enum.valueOf(t.strip()) for t in v.split(","))
        return v                              # KtList: List-extension methods dispatch on it

    def sql_type(self):
        return {"int": "INTEGER", "long": "INTEGER", "real": "REAL", "bool": "INTEGER"}.get(self.kind, "TEXT")


def _bind(params):
    """Adapt @Query PARAMETERS the way Col.to_db adapts entity fields -- Room runs its TypeConverters
    on query args too (an enum arg binds as its name, a Boolean as 0/1). sqlite3 would otherwise
    reject the object outright."""
    out = {}
    for k, v in (params or {}).items():
        if isinstance(v, bool):
            v = int(v)
        elif not isinstance(v, (int, float, str, bytes, type(None))):
            n = getattr(v, "name", None)         # enum constant -> its name (Room's converter)
            v = n if isinstance(n, str) else str(v)
        out[k] = v
    return out


class Entity:
    """Binds an entity class to a table: its columns + a factory(dict)->instance for reads."""
    def __init__(self, table, columns, factory):
        self.table, self.columns, self.factory = table, columns, factory


class Database:
    """The sqlite3-backed database. register(EntityClass) each entity (it carries cls._room), then DAOs
    run SQL -- the table is derived from the SQL's FROM (reads) or the entity class (writes)."""
    def __init__(self, version=1, conn=None):
        self._version = int(version)
        if conn is not None:                # bind to an existing conn (MigrationTestHelper's named DB)
            self._conn = conn
        else:
            self._conn = sqlite3.connect(":memory:", isolation_level=None)   # autocommit; BEGIN/ROLLBACK explicit
            self._conn.row_factory = sqlite3.Row
            self._conn.execute(f"PRAGMA user_version = {int(version)}")      # @Database(version=N) -> db.version
        self._entities = {}                 # table name -> Entity

    def withTransaction(self, block):
        """Room's db.withTransaction { } -> run block in a transaction; roll back on any exception."""
        self._conn.execute("BEGIN")
        try:
            result = block()
            self._conn.execute("COMMIT")
            return result
        except BaseException:               # noqa: BLE001 -- rollback then re-raise
            self._conn.execute("ROLLBACK")
            raise

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

    def clearAllTables(self):
        """Room's RoomDatabase.clearAllTables() -- wipe every registered table (the reinstall/reset path)."""
        for table in self._entities:
            self._conn.execute(f"DELETE FROM {table}")

    def query(self, sql, params=None, single=False, pojo=None):
        """Run a @Query. `SELECT *` from a known entity table maps rows -> entity objects (one/None when
        single). A column selection with a declared result CLASS (pojo) maps each row to it by column
        name -- Room's row-object mapping (the SQL aliases match the class's fields). Otherwise
        (COUNT(*)/aggregates) return the plain value(s), a single column unwrapped to the bare value."""
        rows = self._conn.execute(sql, _bind(params)).fetchall()
        m = _re.search(r"\bFROM\s+(\w+)", sql, _re.IGNORECASE)
        ent = self._entities.get(m.group(1)) if m else None
        star = _re.match(r"\s*SELECT\s+\*", sql, _re.IGNORECASE) is not None
        if not star:
            # aliased whole-row select from a JOIN (`SELECT ms.* FROM mesocycles ms INNER JOIN ...`):
            # still an entity read -- resolve the alias to its table so enum/bool columns CONVERT
            # (the pojo fallback maps raw values, which handed the VM a bare string for an enum).
            am = _re.match(r"\s*SELECT\s+(\w+)\.\*", sql, _re.IGNORECASE)
            if am:
                tm = _re.search(r"\b(?:FROM|JOIN)\s+(\w+)\s+(?:AS\s+)?" + am.group(1) + r"\b",
                                sql, _re.IGNORECASE)
                if tm and tm.group(1) in self._entities:
                    ent, star = self._entities[tm.group(1)], True
        if ent is not None and star:
            out = KtList(ent.factory({c.name: c.from_db(row[c.name]) for c in ent.columns}) for row in rows)
        elif pojo is not None:
            # Room cursor semantics: SQL NULL read into a primitive number column -> 0 (aggregates like
            # SUM/AVG are NULL on an empty table). The pojo's preserved type hints say which fields those are.
            import inspect as _inspect
            try:
                anns = {p.name: (p.annotation if isinstance(p.annotation, str) else "")
                        for p in list(_inspect.signature(pojo.__init__).parameters.values())[1:]}
            except (ValueError, TypeError):
                anns = {}
            zero = {"Int": 0, "Long": 0, "Double": 0.0, "Float": 0.0}

            def _cv(k, v):
                return zero[anns[k]] if v is None and anns.get(k) in zero else v
            out = KtList(pojo(**{k: _cv(k, row[k]) for k in row.keys()}) for row in rows)
        else:
            out = KtList((tuple(r)[0] if len(r) == 1 else tuple(r)) for r in rows)
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

    def update(self, obj):
        """@Update -> UPDATE every non-pk column WHERE pk = the object's pk (built from its schema)."""
        ent = obj.__class__._room
        pk = next((c for c in ent.columns if c.pk), None)
        if pk is None:
            return
        sets = ", ".join(f"{c.name} = :{c.name}" for c in ent.columns if not c.pk)
        vals = {c.name: c.to_db(getattr(obj, c.name)) for c in ent.columns}
        self._conn.execute(f"UPDATE {ent.table} SET {sets} WHERE {pk.name} = :{pk.name}", vals)

    def delete(self, obj):
        """@Delete -> DELETE the row WHERE pk = the object's pk."""
        ent = obj.__class__._room
        pk = next((c for c in ent.columns if c.pk), None)
        if pk is None:
            return
        self._conn.execute(f"DELETE FROM {ent.table} WHERE {pk.name} = :_pk",
                           {"_pk": pk.to_db(getattr(obj, pk.name))})

    def execute(self, sql, params=None):
        """A raw @Query that isn't a row->entity SELECT (UPDATE/DELETE, or a scalar)."""
        cur = self._conn.execute(sql, _bind(params))
        self._conn.commit()
        return cur

    @property
    def openHelper(self):
        """Room's `db.openHelper.writableDatabase.execSQL(...)` raw-SQL escape hatch."""
        return _OpenHelper(self._conn)


class RoomDatabase:
    """The base the @Database class now inherits (inheritance is kept in translation). The class is a
    schema carrier -- the RUNNING database is the engine `Database` the builder returns -- so the base
    only needs to exist."""
    def __init__(self, *a, **k):
        pass


class Dao:
    """Base for a generated DAO -- holds the database; query helpers wrap results the way Room's return
    types do (Flow<List> / Flow<one> / suspend one)."""
    def __init__(self, db):
        self._db = db

    def _flow(self, sql, params=None, pojo=None):    # Flow<List<X>> -- emits the whole list as ONE value
        return Flow([self._db.query(sql, params, pojo=pojo)])

    def _flowOne(self, sql, params=None, pojo=None):  # Flow<X?> -- the single row (or None) as one value
        return Flow([self._db.query(sql, params, single=True, pojo=pojo)])

    def _one(self, sql, params=None, pojo=None):      # suspend X?
        return self._db.query(sql, params, single=True, pojo=pojo)

    def _list(self, sql, params=None, pojo=None):     # suspend List<X> -- ALL rows
        return self._db.query(sql, params, pojo=pojo)

    def _relation(self, sql, params, pojo, emb_field, rel_field, rel_entity,
                  parent_col, entity_col, rel_is_list, as_list=True):
        """A @Transaction @Query returning a @Relation POJO. Run the base query for the @Embedded rows, then
        for each stitch its related rows (SELECT * FROM <rel table> WHERE <entityColumn> = row.<parentColumn>)
        -- exactly Room's relation assembly. Returns Flow<List<POJO>> / Flow<POJO?>."""
        table = rel_entity._room.table
        parents = self._db.query(sql, params)

        def stitch(p):
            kids = self._db.query(f"SELECT * FROM {table} WHERE {entity_col} = :_pk",
                                  {"_pk": getattr(p, parent_col)})
            return pojo(**{emb_field: p, rel_field: (kids if rel_is_list else (kids[0] if kids else None))})

        out = [stitch(p) for p in parents]
        return Flow([out if as_list else (out[0] if out else None)])

    def _insert(self, obj, replace=True):       # @Insert one or a list
        for e in (obj if isinstance(obj, list) else [obj]):
            self._db.insert(e, replace)

    def _update(self, obj):                     # @Update one or a list
        for e in (obj if isinstance(obj, list) else [obj]):
            self._db.update(e)

    def _delete(self, obj):                     # @Delete one or a list
        for e in (obj if isinstance(obj, list) else [obj]):
            self._db.delete(e)


class _Cursor:
    """android.database.Cursor over a fetched result set: a row pointer + typed column access + .use { }.
    getType(i) returns android.database.Cursor.FIELD_TYPE_* (NULL 0 / INTEGER 1 / FLOAT 2 / STRING 3)."""
    def __init__(self, rows, columns):
        self._rows, self._cols, self._i = rows, columns, -1

    @property
    def columnNames(self):
        return KtList(self._cols)

    def getColumnCount(self):
        return len(self._cols)

    def getColumnName(self, i):
        return self._cols[i]

    def getColumnIndex(self, name):
        return self._cols.index(name) if name in self._cols else -1

    def getCount(self):
        return len(self._rows)

    def moveToFirst(self):
        self._i = 0
        return bool(self._rows)

    def moveToNext(self):
        self._i += 1
        return self._i < len(self._rows)

    def _cell(self, i):
        return self._rows[self._i][i]

    def isNull(self, i):
        return self._cell(i) is None

    def getType(self, i):
        v = self._cell(i)
        if v is None:
            return 0
        if isinstance(v, (bool, int)):
            return 1
        if isinstance(v, float):
            return 2
        if isinstance(v, (bytes, bytearray)):
            return 4
        return 3

    def getString(self, i):
        v = self._cell(i)
        return None if v is None else str(v)

    def getInt(self, i):
        v = self._cell(i)
        return 0 if v is None else int(v)

    def getLong(self, i):
        v = self._cell(i)
        return 0 if v is None else int(v)

    def getDouble(self, i):
        v = self._cell(i)
        return 0.0 if v is None else float(v)

    def use(self, block):                       # Kotlin Closeable.use { } -- run then close
        try:
            return block(self)
        finally:
            self.close()

    def close(self):
        pass

    def __enter__(self):
        return self

    def __exit__(self, *a):
        self.close()
        return False


class _SupportSQLiteDatabase:
    """androidx.sqlite SupportSQLiteDatabase -- the raw-SQL surface under db.openHelper: execSQL (with bind
    args), query -> a Cursor, the schema .version, and the begin/setSuccessful/end transaction protocol."""
    def __init__(self, conn):
        self._conn = conn
        self._depth = 0          # nested-transaction ref count; commit only when the outermost closes
        self._began = 0          #   and every frame called setTransactionSuccessful (marks == begins)
        self._marks = 0

    def execSQL(self, sql, *bind_args):
        # No commit here: autocommit (isolation_level=None) commits a bare statement itself, and one inside
        # beginTransaction()/endTransaction() must NOT commit early.
        self._conn.execute(sql, bind_args[0] if bind_args else [])

    def query(self, sql, *a):
        cur = self._conn.execute(sql, a[0] if a else [])
        cols = [d[0] for d in cur.description] if cur.description else []
        return _Cursor(cur.fetchall(), cols)

    @property
    def version(self):
        return self._conn.execute("PRAGMA user_version").fetchone()[0]

    def beginTransaction(self):
        if self._depth == 0:
            self._conn.execute("BEGIN")
            self._began = self._marks = 0
        self._depth += 1
        self._began += 1

    def setTransactionSuccessful(self):
        self._marks += 1

    def endTransaction(self):
        if self._depth == 0:
            return
        self._depth -= 1
        if self._depth == 0:
            self._conn.execute("COMMIT" if self._marks == self._began else "ROLLBACK")

    def close(self):
        pass                                # the conn is owned by the Database / named-DB registry


class _OpenHelper:
    def __init__(self, conn):
        self.writableDatabase = _SupportSQLiteDatabase(conn)
        self.readableDatabase = self.writableDatabase


class _Builder:
    """Room's database builder. The chained options are inert; build() constructs the @Database class
    (whose generated __init__ creates a Database and registers every entity). For a NAMED database that
    MigrationTestHelper already created, build() instead binds to that connection, replays the registered
    migrations up to the @Database version, and validates the schema (the migration-test path)."""
    def __init__(self, klass, name=None):
        self._klass = klass
        self._name = name
        self._migrations = []

    def build(self):
        inst = self._klass()
        if self._name is not None and self._name in _NAMED_DBS:
            target = inst._db._version                  # the @Database(version=N) target
            conn = _NAMED_DBS[self._name]
            inst._db = Database(version=target, conn=conn)   # rebind onto the named (old-schema) conn
            _run_migrations(conn, self._migrations, target)
            _validate_schema(conn, target)
        return inst

    def addMigrations(self, *migrations):
        for m in migrations:                            # accept varargs OR a spread array
            self._migrations.extend(m if isinstance(m, (list, tuple)) else [m])
        return self

    def fallbackToDestructiveMigration(self, *a):
        return self

    def fallbackToDestructiveMigrationOnDowngrade(self, *a):
        return self

    def addTypeConverter(self, *a):
        return self

    def addCallback(self, *a):
        return self

    def setQueryExecutor(self, *a):
        return self

    def allowMainThreadQueries(self):
        return self


class Room:
    @staticmethod
    def inMemoryDatabaseBuilder(context, klass, *a):
        return _Builder(klass.java if hasattr(klass, "java") else klass)

    @staticmethod
    def databaseBuilder(context, klass, name=None, *a):
        return _Builder(klass.java if hasattr(klass, "java") else klass, name)


# ---- migration testing: recreate an old schema, replay migrations, validate the result -------------- #
def _load_schema(version):
    with open(os.path.join(_SCHEMA_DIR, f"{int(version)}.json")) as f:
        return _json.load(f)["database"]


def _run_migrations(conn, migrations, target):
    """Replay registered migrations from the conn's current user_version up to `target`, in order. A gap
    (no migration starting at the current version) is exactly the failure the test exists to catch."""
    support = _SupportSQLiteDatabase(conn)
    by_start = {}
    for m in migrations:
        by_start.setdefault(int(m.startVersion), m)
    cur = conn.execute("PRAGMA user_version").fetchone()[0]
    while cur < target:
        m = by_start.get(cur)
        if m is None:
            raise RuntimeError(f"Missing migration starting at version {cur}")
        m.migrate(support)
        cur = int(m.endVersion)
        conn.execute(f"PRAGMA user_version = {cur}")


def _validate_schema(conn, version):
    """Room validates the migrated schema against the @Database entities. Faithful stand-in: every table
    in the target schema JSON must exist with all its expected columns -- a missing/broken migration shows
    up as a missing table or column."""
    for ent in _load_schema(version)["entities"]:
        table = ent["tableName"]
        expected = {f["columnName"] for f in ent["fields"]}
        actual = {r[1] for r in conn.execute(f"PRAGMA table_info(`{table}`)").fetchall()}
        if not actual:
            raise RuntimeError(f"Schema validation failed: table `{table}` missing after migration")
        missing = expected - actual
        if missing:
            raise RuntimeError(f"Schema validation failed: `{table}` missing columns {sorted(missing)}")


class MigrationTestHelper:
    """androidx.room.testing.MigrationTestHelper -- createDatabase(name, v) builds the v-schema (from the
    exported schema JSON) on a fresh connection kept in _NAMED_DBS, which the builder later reopens."""
    def __init__(self, instrumentation=None, klass=None, *a, **k):
        self._klass = klass

    def createDatabase(self, name, version):
        conn = sqlite3.connect(":memory:", isolation_level=None)
        conn.row_factory = sqlite3.Row
        schema = _load_schema(version)
        for ent in schema["entities"]:
            conn.execute(ent["createSql"].replace("${TABLE_NAME}", ent["tableName"]))
        for q in schema.get("setupQueries", []):
            conn.execute(q)
        conn.execute(f"PRAGMA user_version = {int(version)}")
        _NAMED_DBS[str(name)] = conn
        return _SupportSQLiteDatabase(conn)

    def runMigrationsAndValidate(self, name, version, validateDroppedTables=True, *migrations):
        conn = _NAMED_DBS[str(name)]
        migs = [x for m in migrations for x in (m if isinstance(m, (list, tuple)) else [m])]
        _run_migrations(conn, migs, int(version))
        _validate_schema(conn, int(version))
        return _SupportSQLiteDatabase(conn)

    def closeWhenFinished(self, *a):
        pass


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
