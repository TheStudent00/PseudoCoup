"""navigation.py -- a headless stand-in for Jetpack Navigation-Compose, on top of the reactive scheduler.

    rememberNavController()                 -> a NavController (current route + back stack, remembered)
    NavHost(navController, startDestination, content={ composable(route){ Screen() } ... })
                                            -> registers routes, renders the CURRENT one
    navController.navigate(route)           -> switch route (a State write -> one recompose -> NavHost
                                               renders the new screen)
    navController.popBackStack()            -> back

Route strings and the screen lambdas come straight from the transpiled graph; this just picks which screen
to render and repaints on navigate. Edits nothing in the transpiled code.
"""
import runtime.reactive as reactive
from runtime.compose import _call, remember

_NAV_STACK = []     # active NavHost route-registration collectors (composable() fills the top one)


class _Destination:
    def __init__(self, route):
        self.route = route


class _BackEntry:
    def __init__(self, route):
        self.destination = _Destination(route)
        self.arguments = None


class _EntryState:
    def __init__(self, controller):
        self._c = controller

    @property
    def value(self):
        r = self._c.currentRoute()
        return _BackEntry(r) if r is not None else None


class NavController:
    def __init__(self, start=None):
        self._route = reactive.State(start)
        self._stack = [start] if start is not None else []

    def navigate(self, route, *a, **k):
        self._stack.append(route)
        self._route.set(route)                       # -> recompose -> NavHost renders `route`

    def popBackStack(self, *a, **k):
        if len(self._stack) > 1:
            self._stack.pop()
            self._route.set(self._stack[-1])
            return True
        return False

    def currentRoute(self):
        return self._route.value

    def currentBackStackEntryAsState(self, *a, **k):
        return _EntryState(self)

    @property
    def currentBackStackEntry(self):
        r = self.currentRoute()
        return _BackEntry(r) if r is not None else None

    @property
    def previousBackStackEntry(self):
        return _BackEntry(self._stack[-2]) if len(self._stack) >= 2 else None


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
    if navController is not None and navController.currentRoute() is None and startDestination is not None:
        navController._route._value = startDestination     # seed start route without a spurious recompose
        navController._stack = [startDestination]
    current = (navController.currentRoute() if navController is not None else None) or startDestination
    fn = routes.get(current) or (next(iter(routes.values()), None) if routes else None)
    if callable(fn):
        _call(fn)                                     # render the current screen into the tree


def composable(route=None, *a, **k):
    fn = k.get("content") or next((x for x in a if callable(x)), None)
    if _NAV_STACK and callable(fn):
        _NAV_STACK[-1][route] = fn


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
