"""
registry.py — the wrapper registry: maps an external origin to the Python runtime module that stands in
for it. RESOLVE says where a name comes from (its fully-qualified name + origin); the registry says which
wrapper provides it. A name with no provider is a build-time gap (listed by externals.py), never a
runtime NameError.

Today kotlin_rt is the catch-all for the stdlib plus the few platform names already wrapped. As the UI
phase lands, compose / dagger_hilt / androidx_* get their own runtime modules and ORIGIN_MODULE points
this map at them -- one registry edit per new wrapper module.
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import runtime.kotlin_rt as kotlin_rt      # noqa: E402
import runtime.coroutines as coroutines    # noqa: E402
import runtime.java_rt as java_rt          # noqa: E402
import runtime.json_rt as json_rt          # noqa: E402
import runtime.android_rt as android_rt    # noqa: E402
import runtime.room as room                # noqa: E402  (the sqlite3 data-layer engine: Dao/Entity/Col)
import runtime.numbers as numbers          # noqa: E402  (fixed-width numeric wrappers, emitted at literals)
import runtime.compose as compose          # noqa: E402  (headless Compose: a @Composable emits a UI tree)

# origin label (from resolve.origin) -> the runtime module that currently provides its stand-ins.
# (provided() indexes by NAME across all of these, so a name already in kotlin_rt -- e.g. java Date or
# room Migration -- stays found there; the per-origin modules add the rest.)
ORIGIN_MODULE = {
    "compose": compose,                    # androidx.compose.* -> headless Compose (Column/Text/… emit a tree)
    "kotlin": kotlin_rt,
    "java": java_rt,                       # java.time chain, UUID, TimeUnit, File, ... (+ Date in kotlin_rt)
    "javax": kotlin_rt,
    "kotlinx_coroutines": coroutines,      # synchronous Flow/StateFlow reactive stand-in
    "org": json_rt,                        # org.json -> Python json (real)
    "android": android_rt,                 # Android-framework STUBS (no Python Android)
    "androidx": android_rt,
    "androidx_work": android_rt,
    "androidx_room": room,                 # @Dao/@Entity -> the sqlite3 engine (Room builder stub in
                                           #   android_rt, Migration in kotlin_rt -- both still in scope)
    "dagger_hilt": android_rt,             # EntryPointAccessors stub
    "google": android_rt,                  # Firebase / Play / Wearable stubs
}


def _modules():
    seen, mods = set(), []
    for m in [numbers, *ORIGIN_MODULE.values()]:    # numbers isn't an import origin -- always available
        if m.__name__ not in seen:
            seen.add(m.__name__)
            mods.append(m)
    return mods


def provided():
    """{ external simple name -> runtime module label } for everything the runtime supplies."""
    out = {}
    for m in _modules():
        label = m.__name__.split(".")[-1]
        for n in dir(m):
            if not n.startswith("_"):
                out[n] = label
    return out


def module_for(origin):
    """The runtime module label that owns an origin's wrappers, or None if not yet wrapped."""
    m = ORIGIN_MODULE.get(origin)
    return m.__name__.split(".")[-1] if m is not None else None


def covers(name):
    """Is there a runtime wrapper for this external simple name?"""
    return name in provided()


def namespace():
    """The merged runtime namespace -- every public name across all wrapper modules -> its value.
    Seeds the oracle and the load gate, so a wrapper lands wherever its origin module puts it and the
    harnesses pick up a new origin module the moment ORIGIN_MODULE points at it."""
    ns = {}
    for m in _modules():
        for n in dir(m):
            if not n.startswith("_"):
                ns[n] = getattr(m, n)
    return ns
