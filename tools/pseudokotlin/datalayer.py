"""
datalayer.py — the Room "map" stage: turn @Entity / @Dao Kotlin into code that drives the room.py engine.

entity_schema(class_node, name, enums) -> a `Name._room = Entity(table, [Col(...)], factory)` line, the
column kinds inferred from field types (String->text, Boolean->bool, an enum type->enum, List<enum>->
enum_list, the same shape Room's @TypeConverter produces). dao_body(...) (next) turns a @Query method into
a body that runs its SQL.
"""
import os
import re

_SCALAR = {"String": "text", "CharSequence": "text", "Int": "int", "Long": "long",
           "Boolean": "bool", "Double": "real", "Float": "real"}

# The global enum set is computed once, lazily, from the WFL copy (entities are only seen when
# transpiling it). Cached so the transpiler can call enums() per-@Entity without rescanning.
_KT_ROOT = os.path.expanduser("~/Programming/WFL_MixingCenter/WFL/app/src/main/java/com/sara/workoutforlife")
_ENUMS = None


def enums():
    global _ENUMS
    if _ENUMS is None:
        import sys
        sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
        import resolve
        _ENUMS = resolve.app_enums(_KT_ROOT)
    return _ENUMS


def _find(node, kind):
    if node.type == kind:
        return node
    for c in node.children:
        r = _find(c, kind)
        if r is not None:
            return r
    return None


def entity_table(class_node, class_name):
    """@Entity(tableName = "exercises") -> "exercises"; Room defaults to the class name."""
    m = re.search(r'tableName\s*=\s*"([^"]+)"', class_node.text.decode())
    return m.group(1) if m else class_name


def _col_kind(type_text, enums):
    t = type_text.strip().rstrip("?")
    if t in _SCALAR:
        return _SCALAR[t], None
    m = re.match(r"(?:List|MutableList|Set)<(\w+)>", t)
    if m and m.group(1) in enums:
        return "enum_list", m.group(1)
    if t in enums:
        return "enum", t
    return "text", None                     # best-effort: anything else stored as text


def field_specs(class_node, enums):
    """[(name, kind, enum_name|None, is_pk)] for each constructor column (skipping @Ignore)."""
    cps = _find(class_node, "class_parameters")
    specs = []
    if cps is None:
        return specs
    for cp in cps.named_children:
        if cp.type != "class_parameter":
            continue
        mods = next((k for k in cp.children if k.type == "modifiers"), None)
        mtext = mods.text.decode() if mods is not None else ""
        if "@Ignore" in mtext:
            continue
        name = next((k.text.decode() for k in cp.children if k.type == "identifier"), None)
        tnode = next((k for k in cp.children if k.type.endswith("type")), None)
        if name is None or tnode is None:
            continue
        kind, enum = _col_kind(tnode.text.decode(), enums)
        specs.append((name, kind, enum, "@PrimaryKey" in mtext))
    return specs


def _col_expr(name, kind, enum, pk):
    args = [repr(name)]
    if kind != "text" or enum:
        args.append(repr(kind))
    if enum:
        args.append(enum)               # the enum CLASS by name (entity module imports it)
    if pk:
        args.append("pk=True")
    return f"Col({', '.join(args)})"


def entity_schema(class_node, class_name, enums):
    """The room.Entity registration line for an @Entity class."""
    table = entity_table(class_node, class_name)
    specs = field_specs(class_node, enums)
    cols = ", ".join(_col_expr(*s) for s in specs)
    return f"{class_name}._room = Entity({table!r}, [{cols}], lambda kw: {class_name}(**kw))"


# ---- @Dao methods -> bodies that run against the engine ----------------------------------------- #
def _method_params(method_node):
    vp = _find(method_node, "function_value_parameters") or _find(method_node, "value_parameters")
    if vp is None:
        return []
    return [n for n in (next((k.text.decode() for k in p.children if k.type == "identifier"), None)
                        for p in vp.named_children if p.type in ("parameter", "function_value_parameter"))
            if n]


def dao_body(method_node):
    """A DAO method's body. @Query -> run its SQL (Flow<List> -> _flow, Flow<one> -> _flowOne, suspend one
    -> _one); @Insert -> _insert. @Update/@Delete need generated SQL -> left as a TODO pass for now."""
    text = method_node.text.decode()
    params = _method_params(method_node)
    pdict = "{" + ", ".join(f"{p!r}: {p}" for p in params) + "}"
    qm = (re.search(r'@Query\(\s*"""(.*?)"""', text, re.DOTALL)
          or re.search(r'@Query\(\s*"((?:[^"\\]|\\.)*)"', text))
    if qm:
        sql = " ".join((qm.group(1) or qm.group(2)).split())
        ret = re.search(r"\)\s*:\s*([A-Za-z][\w<>?., ]*)", text)
        ret = ret.group(1) if ret else ""
        if "Flow" in ret and "List" in ret:
            helper = "_flow"
        elif "Flow" in ret:
            helper = "_flowOne"
        else:
            helper = "_one"
        return f"return self.{helper}({sql!r}, {pdict})"
    arg = params[0] if params else "entity"
    if "@Insert" in text:
        return f"return self._insert({arg})"
    if "@Update" in text:
        return f"return self._update({arg})"
    if "@Delete" in text:
        return f"return self._delete({arg})"
    if "@Transaction" in text:
        return "pass  # @Transaction default method (next data-layer step)"
    return "pass"


def dao_class(dao_node, class_name):
    """The whole @Dao interface -> a Python class extending room.Dao, each method's body generated."""
    body = _find(dao_node, "class_body")
    methods = [c for c in (body.named_children if body is not None else []) if c.type == "function_declaration"]
    lines = [f"class {class_name}(Dao):"]
    for m in methods:
        name = next((k.text.decode() for k in m.children if k.type == "identifier"), None)
        sig = ", ".join(["self"] + _method_params(m))
        lines.append(f"    def {name}({sig}):")
        lines += [f"        {bl}" for bl in dao_body(m).split("\n")]
    if len(lines) == 1:                             # an interface with no methods -> a valid empty class
        lines.append("    pass")
    return "\n".join(lines)


def database_patches(class_node, name):
    """@Database -> module-level wiring patched onto the rendered DB class: an __init__ that creates a
    room.Database and registers every listed entity, and a body for each abstract DAO accessor."""
    text = class_node.text.decode()
    m = re.search(r"entities\s*=\s*\[(.*?)\]", text, re.DOTALL)
    ents = re.findall(r"(\w+)::class", m.group(1)) if m else []
    body = _find(class_node, "class_body")
    accessors = []
    for fn in (body.named_children if body is not None else []):
        if fn.type != "function_declaration":
            continue
        nm = next((k.text.decode() for k in fn.children if k.type == "identifier"), None)
        rt = re.search(r"\)\s*:\s*(\w+)", fn.text.decode())
        if nm and rt and rt.group(1).endswith("Dao"):
            accessors.append((nm, rt.group(1)))
    init = [f"def _{name}_init(self):", "    self._db = Database()"]
    init += [f"    self._db.register({e})" for e in ents]
    patches = ["\n".join(init), f"{name}.__init__ = _{name}_init"]
    patches += [f"{name}.{nm} = lambda self: {dao}(self._db)" for nm, dao in accessors]
    patches += [f"{name}.openHelper = property(lambda self: self._db.openHelper)",
                f"{name}.close = lambda self: self._db.close()",
                f"{name}.withTransaction = lambda self, block: self._db.withTransaction(block)"]
    return patches


# ---- test: generate ExerciseEntity's schema and check the inferred column kinds ----------------- #
if __name__ == "__main__":
    import os
    import sys
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    from parse import parse
    import resolve

    KT = os.path.expanduser("~/Programming/WFL_MixingCenter/WFL/app/src/main/java/com/sara/workoutforlife")
    enums = resolve.app_enums(KT)
    src = open(os.path.join(KT, "data/db/entity/ExerciseEntity.kt"), "rb").read()
    cls = _find(parse(src).root_node, "class_declaration")
    line = entity_schema(cls, "ExerciseEntity", enums)
    print(line)
    assert "Col('id', pk=True)" in line
    assert "Col('primaryMuscleGroups', 'enum_list', MuscleGroup)" in line
    assert "Col('movementPattern', 'enum', MovementPattern)" in line
    assert "Col('isUnilateral', 'bool')" in line
    assert "Col('name')" in line
    assert "Entity('exercises'" in line
    print("\ndatalayer entity_schema test: OK")

    # --- DAO body generation ---
    dao_root = parse(open(os.path.join(KT, "data/db/dao/ExerciseDao.kt"), "rb").read()).root_node
    dao_cls = _find(dao_root, "class_declaration")
    methods = {next((k.text.decode() for k in m.children if k.type == "identifier"), None): m
               for m in _find(dao_cls, "class_body").named_children if m.type == "function_declaration"}
    gbmg = dao_body(methods["getByMuscleGroup"])
    print("getByMuscleGroup ->", gbmg)
    assert gbmg.startswith("return self._flow(") and "'muscleGroup': muscleGroup" in gbmg
    assert "self._flowOne(" in dao_body(methods["getById"])          # Flow<ExerciseEntity?>
    assert "self._insert(" in dao_body(methods["insertAll"])
    print("datalayer dao_body test: OK")

    # --- end-to-end: GENERATED schema + GENERATED DAO bodies run the real query on the engine ---
    from runtime.room import Database, Entity, Col, Dao  # noqa: E402

    class MuscleGroup2:
        _by = {}

        def __init__(self, name):
            self.name = name

        @staticmethod
        def valueOf(s):
            return MuscleGroup2._by[s]
    for _n in ("CHEST", "SHOULDERS", "ABS", "ABS_OBLIQUES"):
        MuscleGroup2._by[_n] = MuscleGroup2(_n)

    class Ex:
        def __init__(self, **kw):
            self.__dict__.update(kw)
    Ex._room = Entity("exercises", [Col("id", pk=True), Col("name"),
                                    Col("primaryMuscleGroups", "enum_list", MuscleGroup2),
                                    Col("secondaryMuscleGroups", "enum_list", MuscleGroup2)],
                      lambda kw: Ex(**kw))
    db = Database().register(Ex)
    ns = {"Dao": Dao}
    exec(dao_class(dao_cls, "ExerciseDao"), ns)         # the GENERATED DAO class
    dao = ns["ExerciseDao"](db)
    g = lambda s: MuscleGroup2._by[s]
    dao.insertAll([
        Ex(id="only", name="only", primaryMuscleGroups=[g("CHEST")], secondaryMuscleGroups=[]),
        Ex(id="mid", name="mid", primaryMuscleGroups=[g("SHOULDERS"), g("CHEST")], secondaryMuscleGroups=[]),
        Ex(id="absob", name="absob", primaryMuscleGroups=[g("ABS_OBLIQUES")], secondaryMuscleGroups=[]),
    ])
    chest = [e.id for e in dao.getByMuscleGroup("CHEST").first()]
    assert chest == ["mid", "only"], chest               # ORDER BY name
    abs_hits = [e.id for e in dao.getByMuscleGroup("ABS").first()]
    assert abs_hits == [], abs_hits                       # token boundary holds through GENERATED code
    print("datalayer end-to-end (generated schema + generated DAO + engine): OK")
