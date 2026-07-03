"""navigation.py -- a headless stand-in for Jetpack Navigation-Compose, on top of the reactive scheduler.

    rememberNavController()                 -> a NavController (current route + back stack, remembered)
    NavHost(navController, startDestination, content={ composable(route){ Screen() } ... })
                                            -> registers route PATTERNS, renders the current route
    navController.navigate("gym_editor?gymId=abc")
                                            -> a State write -> one recompose -> NavHost matches the
                                               concrete route against the registered patterns, extracts
                                               the arguments ({"gymId": "abc"}), and renders that screen
                                               with the arguments available (the COURIER: what the
                                               androidx.navigation library does at runtime on the phone)
    navController.popBackStack()            -> back

Patterns are the app's own transpiled route strings: path arguments ("path_detail/{pathId}") and query
arguments ("gym_editor?gymId={gymId}"). While a destination renders, its extracted arguments are on
_ARGS_STACK -- current_args() -- where the ViewModel factory picks them up for the SavedStateHandle.
Edits nothing in the transpiled code.
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import runtime.reactive as reactive           # noqa: E402
from runtime.compose import _call, remember, push_slot_scope, pop_slot_scope   # noqa: E402

_NAV_STACK = []     # active NavHost route-registration collectors (composable() fills the top one)
_ARGS_STACK = []    # the arguments of the destination currently rendering (for hiltViewModel/di)
last_controller = None    # the most recent NavHost's controller -- the harness/kit drives taps through it


def current_args():
    """The route arguments of the destination currently being rendered, or None."""
    return _ARGS_STACK[-1] if _ARGS_STACK else None


def _norm(p):
    return (p or "").replace("{{", "{").replace("}}", "}")


def _match(pattern, route):
    """Match a concrete route against a pattern; the extracted arguments or None.
    'gym_editor?gymId={gymId}' matches 'gym_editor?gymId=abc' -> {'gymId': 'abc'} and plain
    'gym_editor' -> {} (query args are optional); 'path_detail/{pathId}' matches 'path_detail/x'."""
    pattern, route = _norm(pattern), _norm(route)
    p_path, _, p_query = pattern.partition("?")
    r_path, _, r_query = route.partition("?")
    ps, rs = p_path.split("/"), r_path.split("/")
    if len(ps) != len(rs):
        return None
    args = {}
    for pseg, rseg in zip(ps, rs):
        if pseg.startswith("{") and pseg.endswith("}"):
            args[pseg[1:-1]] = rseg
        elif pseg != rseg:
            return None
    given = dict(kv.split("=", 1) for kv in r_query.split("&") if "=" in kv) if r_query else {}
    for kv in (p_query.split("&") if p_query else []):
        if "=" not in kv:
            continue
        k, v = kv.split("=", 1)
        if v.startswith("{") and v.endswith("}"):
            if k in given:
                args[v[1:-1]] = given[k]
        elif given.get(k) != v:
            return None
    return args


class _Arguments(dict):
    """The back-stack entry's argument bag (androidx Bundle-ish reads; missing -> None)."""
    def getString(self, k, d=None):
        return self.get(k, d)

    get_ = getString


class _Destination:
    def __init__(self, route):
        self.route = route                   # the PATTERN (androidx semantics -- bottom-bar compares on it)


class _BackEntry:
    def __init__(self, pattern, args=None):
        self.destination = _Destination(pattern)
        self.arguments = _Arguments(args or {})


class _EntryState:
    def __init__(self, controller):
        self._c = controller

    @property
    def value(self):
        return self._c._entry()


class NavController:
    def __init__(self, start=None):
        self._route = reactive.State(start)   # the CONCRETE route (a State write -> one recompose)
        self._stack = [start] if start is not None else []
        self._patterns = {}                   # pattern -> destination fn (registered by NavHost)

    def navigate(self, route, *a, **k):
        self._stack.append(route)
        self._route.set(route)

    def popBackStack(self, *a, **k):
        if len(self._stack) > 1:
            self._stack.pop()
            self._route.set(self._stack[-1])
            return True
        return False

    def currentRoute(self):
        return self._route.value

    def _resolve(self, route):
        """(pattern, args, fn) for a concrete route, or (route, {}, None) when nothing matches."""
        if route is not None:
            for pattern, fn in self._patterns.items():
                args = _match(pattern, route)
                if args is not None:
                    return pattern, args, fn
        return route, {}, None

    def _entry(self, route=None):
        r = route if route is not None else self.currentRoute()
        if r is None:
            return None
        pattern, args, _fn = self._resolve(r)
        return _BackEntry(pattern, args)

    def currentBackStackEntryAsState(self, *a, **k):
        return _EntryState(self)

    @property
    def currentBackStackEntry(self):
        return self._entry()

    @property
    def previousBackStackEntry(self):
        return self._entry(self._stack[-2]) if len(self._stack) >= 2 else None


def rememberNavController(*a, **k):
    return remember(lambda: NavController())          # persist the controller across recompositions


def NavHost(navController=None, startDestination=None, content=None, **k):
    routes = {}
    _NAV_STACK.append(routes)
    try:
        if callable(content):
            content()                                 # runs the composable(route){…} registrations
    finally:
        _NAV_STACK.pop()
    if navController is not None:
        global last_controller
        last_controller = navController
        navController._patterns = routes
        if navController.currentRoute() is None and startDestination is not None:
            navController._route._value = startDestination   # seed without a spurious recompose
            navController._stack = [startDestination]
    current = (navController.currentRoute() if navController is not None else None) or startDestination
    if navController is not None:
        _pattern, args, fn = navController._resolve(current)
    else:
        args, fn = {}, routes.get(current)
    if fn is None:
        fn = next(iter(routes.values()), None) if routes else None
    if callable(fn):
        _ARGS_STACK.append(args)                      # the courier's delivery: current_args() while
        push_slot_scope(_pattern if navController is not None else current)   # per-destination remember
        try:                                          # this destination (and its ViewModel) builds
            _call(fn)
        finally:
            pop_slot_scope()
            _ARGS_STACK.pop()


def composable(route=None, *a, **k):
    fn = k.get("content") or next((x for x in a if callable(x)), None)
    if _NAV_STACK and callable(fn):
        _NAV_STACK[-1][_norm(route)] = fn


def navigation(*a, **k):                              # nested nav graph builder -> just run its content
    fn = k.get("content") or next((x for x in a if callable(x)), None)
    if callable(fn):
        fn()


def navArgument(*a, **k):
    return None


def BackHandler(*a, **k):                             # back is driven by the controller here -> no-op
    return None


class NavType:                                        # NavType.StringType etc. -- only referenced, never run
    StringType = "string"
    IntType = "int"
    LongType = "long"
    BoolType = "bool"


if __name__ == "__main__":
    assert _match("gym_editor?gymId={gymId}", "gym_editor?gymId=abc") == {"gymId": "abc"}
    assert _match("gym_editor?gymId={gymId}", "gym_editor") == {}
    assert _match("path_detail/{pathId}", "path_detail/x1") == {"pathId": "x1"}
    assert _match("path_detail/{pathId}", "today") is None
    assert _match("gym_editor?gymId={{gymId}}", "gym_editor?gymId=z") == {"gymId": "z"}  # brace-doubled ok
    print("navigation self-test: OK")