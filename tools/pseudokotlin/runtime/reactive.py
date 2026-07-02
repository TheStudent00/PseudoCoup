"""reactive.py -- the transpiler world's copy of PseudoCoup's observable-state + recompose model.

This is a faithful port of WFL_PseudoCoup/src/reactive.py (the log_17 reactivity spike), kept here so
WFL_MixingCenter stands on its own rather than importing across repos. Same model, not a re-design:

    Kotlin (Compose)            here
    MutableStateFlow(x)    ->   State(x)
    flow.value             ->   state.value          (read)
    _flow.value = x        ->   state.set(x) / .value = x   (write -- auto-notifies)
    recompose per event    ->   the scheduler: N writes in one handler => ONE repaint after it

The kit (render side) drives the scheduler: begin() before an event handler, flush() after; State writes
call invalidate() in between. It never edits transpiled code -- it's the behaviour behind the compose state
names the transpiled screens import.
"""


class _Recompose:
    """One scheduler per app. The render side wires host (the repaint) and drives begin()/flush() around each
    event; a State write in between marks it dirty; flush() repaints once if anything changed."""
    def __init__(self):
        self._host = None
        self._dirty = False

    def set_host(self, host):
        self._host = host

    def begin(self):
        self._dirty = False

    def invalidate(self):
        self._dirty = True

    def flush(self):
        if self._dirty and self._host is not None:
            self._dirty = False
            self._host()


recompose = _Recompose()


def invalidate():
    """Request a repaint WITHOUT a State write -- for a ViewModel action that mutates the (non-reactive) data
    layer, where Compose would rely on a Room Flow re-emitting. Call it after a repo mutation."""
    recompose.invalidate()


class State:
    """An observable value. Read `state.value`; write `state.value = v` (or `state.set(v)`). A write that
    changes the value schedules one recompose -- mirroring a Compose MutableStateFlow."""
    def __init__(self, value):
        self._value = value

    @property
    def value(self):
        return self._value

    @value.setter
    def value(self, v):
        self.set(v)

    def set(self, v):
        if self._value != v:
            self._value = v
            recompose.invalidate()

    # component1/component2: Kotlin `val (v, setV) = remember { mutableStateOf(x) }` destructuring
    def component1(self):
        return self._value

    def component2(self):
        return self.set

    def __repr__(self):
        return f"State({self._value!r})"


class ObservableMap(dict):
    """Compose SnapshotStateMap: a mutable map whose writes repaint. Missing-key read returns None (Kotlin
    map[key] is nullable), NOT KeyError -- matches how the transpiled screens index it."""
    def __getitem__(self, k):
        return self.get(k)

    def __setitem__(self, k, v):
        if self.get(k) != v:
            super().__setitem__(k, v)
            recompose.invalidate()

    def put(self, k, v):
        self[k] = v

    def remove(self, k):
        if k in self:
            super().__delitem__(k)
            recompose.invalidate()


class ObservableList(list):
    """Compose SnapshotStateList: a mutable list whose structural writes repaint."""
    def add(self, x):
        self.append(x)
        recompose.invalidate()
        return True

    def remove(self, x):
        if x in self:
            super().remove(x)
            recompose.invalidate()
            return True
        return False

    def clear(self):
        if self:
            super().clear()
            recompose.invalidate()


def mutableStateOf(value=None, *a, **k):
    return State(value)


def mutableStateMapOf(*pairs):
    m = ObservableMap()
    for p in pairs:
        m[p[0]] = p[1]
    return m


def mutableStateListOf(*xs):
    return ObservableList(xs)
