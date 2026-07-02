"""
runtime/compose.py — a headless, faithful stand-in for Jetpack Compose, the way room.py is for Room.

A @Composable, when CALLED, emits a tree of UI nodes: a container (Scaffold / Column / LazyColumn / …)
runs its content + slot lambdas to build its children; a leaf (Text / Icon / Spacer) emits a node. Styling
(Modifier / MaterialTheme / dp / colors) is structural noise here, so it stays an autostub stub. The result
is the UI STRUCTURE the transpiled screen produces -- provable headless, without a device. Point the tree at
a real kit (Flutter/Kivy) later; this proves the transpiler PATH renders, end to end from Kotlin.
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

_STACK = []     # the current composition parent -- children emit into _STACK[-1]


class Node:
    def __init__(self, kind):
        self.kind, self.text, self.children = kind, None, []
        self.handlers = {}      # on*-event name -> the transpiled handler (wired to the kit, fired on action)

    def tree(self, depth=0):
        line = "  " * depth + self.kind + (f": {self.text!r}" if isinstance(self.text, str) else "")
        return "\n".join([line] + [c.tree(depth + 1) for c in self.children])

    def count(self):
        return 1 + sum(c.count() for c in self.children)

    def find(self, kind):
        out = [self] if self.kind == kind else []
        for c in self.children:
            out += c.find(kind)
        return out


def _emit(node):
    if _STACK:
        _STACK[-1].children.append(node)
    return node


def _call(fn):
    """Run a slot lambda. It may take no arg (the `it=None` form) or one (a PaddingValues / a *Scope).
    Only ARITY TypeErrors (raised at the call frame itself, no deeper traceback) trigger the retry --
    a TypeError from INSIDE the body is a real failure and must surface, never be swallowed (a swallowed
    one silently drops the body's children and renders a lying, thinner tree)."""
    try:
        return fn()
    except TypeError as e:
        if e.__traceback__.tb_next is not None:
            raise
        from runtime.autostub import Stub
        try:
            return fn(Stub())
        except TypeError as e2:
            if e2.__traceback__.tb_next is not None:
                raise
            return None


def _composable(kind):
    def make(*args, **kwargs):
        node = Node(kind)
        _emit(node)
        _STACK.append(node)
        try:
            for a in args:                       # `Text("hi")`, `Column(content_lambda)`
                if callable(a):
                    _call(a)
                elif node.text is None and isinstance(a, str):
                    node.text = a
            for k, v in kwargs.items():          # `content=`, `topBar=`, `title=`, `label=`, `icon=`, …
                if k.startswith("on"):           # an EVENT handler (onClick/onValueChange/onDone): STORE it
                    if callable(v):              # for the kit to fire on user action -- never call at render
                        node.handlers[k] = v     # (calling it here would run app logic mid-build).
                    continue
                if callable(v):
                    _call(v)
                elif k == "text" and isinstance(v, str):
                    node.text = v
        finally:
            _STACK.pop()
        return node
    return make


# the Compose surface the foundation uses -- containers and leaves both go through the one emitter.
_NAMES = """Scaffold Column Row Box BoxWithConstraints LazyColumn LazyRow LazyVerticalGrid FlowRow FlowColumn
Card ElevatedCard OutlinedCard Surface TopAppBar CenterAlignedTopAppBar MediumTopAppBar BottomAppBar
IconButton FilledIconButton FilledTonalIconButton OutlinedIconButton Button TextButton OutlinedButton
ElevatedButton FilledTonalButton FloatingActionButton ExtendedFloatingActionButton Text BasicText Spacer Icon
Image HorizontalDivider VerticalDivider SuggestionChip FilterChip AssistChip InputChip ElevatedFilterChip
SegmentedButton SingleChoiceSegmentedButtonRow MultiChoiceSegmentedButtonRow CircularProgressIndicator
LinearProgressIndicator OutlinedTextField TextField BasicTextField Checkbox Switch Slider RangeSlider
RadioButton TriStateCheckbox NavigationBar NavigationBarItem NavigationRail NavigationRailItem ModalBottomSheet
AlertDialog BasicAlertDialog Dialog Badge BadgedBox Tab LeadingIconTab TabRow ScrollableTabRow PrimaryTabRow
Snackbar SnackbarHost ModalNavigationDrawer DismissibleNavigationDrawer PermanentNavigationDrawer
SwipeToDismissBox PullToRefreshBox AnimatedVisibility AnimatedContent Crossfade SelectionContainer
ProvideTextStyle CompositionLocalProvider DropdownMenu DropdownMenuItem ExposedDropdownMenuBox ListItem""".split()
for _n in _NAMES:
    globals()[_n] = _composable(_n)


def Composable(fn=None, *a, **k):       # the @Composable annotation if it ever survives -> identity
    return fn if fn is not None else (lambda g: g)


# ---- LazyColumn / LazyRow DSL: item { } / items(list) { } / itemsIndexed emit into the lazy container ----
def item(*args, **kwargs):
    fn = next((a for a in args if callable(a)), None) or kwargs.get("content")
    if callable(fn):
        _call(fn)


def items(data=None, *args, **kwargs):
    fn = kwargs.get("itemContent") or kwargs.get("content") or next((a for a in args if callable(a)), None)
    seq = data if hasattr(data, "__iter__") and not isinstance(data, str) else []
    if callable(fn):
        for d in seq:
            try:
                fn(d)
            except TypeError:
                _call(fn)


def itemsIndexed(data=None, *args, **kwargs):
    fn = kwargs.get("itemContent") or kwargs.get("content") or next((a for a in args if callable(a)), None)
    seq = data if hasattr(data, "__iter__") and not isinstance(data, str) else []
    if callable(fn):
        for i, d in enumerate(seq):
            try:
                fn(i, d)
            except TypeError:
                pass


def stickyHeader(*args, **kwargs):
    item(*args, **kwargs)


_COMPOSITION = None     # the composition currently running -- remember() reads its slot table


class Composition:
    """One screen's live composition: the composable + args, plus a positional slot table so `remember`
    keeps the same value across recompositions (Compose's slot table). recompose() re-runs the composable
    with the slots preserved and produces a fresh Node tree."""
    def __init__(self, fn, args=(), kwargs=None):
        self.fn, self.args, self.kwargs = fn, args, (kwargs or {})
        self.slots = []                      # [(keys, value)] by call position
        self._i = 0
        self.root = None

    def compose(self):
        global _COMPOSITION
        prev = _COMPOSITION
        _COMPOSITION = self
        self._i = 0
        root = Node("root")
        _STACK.append(root)
        try:
            self.fn(*self.args, **self.kwargs)
        finally:
            _STACK.pop()
            _COMPOSITION = prev
        self.root = root.children[0] if len(root.children) == 1 else root
        return self.root

    def slot(self, calc, keys):
        if self._i < len(self.slots):
            okeys, val = self.slots[self._i]
            if okeys != keys:                # a key changed -> recompute this slot
                val = calc()
                self.slots[self._i] = (keys, val)
        else:
            val = calc()
            self.slots.append((keys, val))
        self._i += 1
        return val


def remember(*args):
    """Compose remember: the LAST arg is the calculation, any earlier args are keys. Memoized by call
    position so `remember { mutableStateOf(x) }` returns the SAME State across recompositions (else state
    would reset every repaint). Outside a composition (e.g. one-shot render), just computes."""
    calc = args[-1] if args else (lambda: None)
    keys = tuple(args[:-1])
    calc_fn = calc if callable(calc) else (lambda: calc)
    if _COMPOSITION is None:
        return calc_fn()
    return _COMPOSITION.slot(calc_fn, keys)


rememberSaveable = remember      # same behaviour here (no process-death to restore across)


def render(composable, *args, **kwargs):
    """Call a top-level @Composable in a fresh composition and return the root Node (`.tree()` prints it)."""
    return Composition(composable, args, kwargs).compose()


if __name__ == "__main__":
    def Screen():                            # a hand-written composable, to prove the emitter
        Scaffold(topBar=lambda: Text("Title"),
                 content=lambda pad: Column(content=lambda: (Text("hello"), Spacer(), Button(
                     onClick=lambda: None, content=lambda: Text("Save")))))
    tree = render(Screen)
    print(tree.tree())
    assert tree.kind == "Scaffold"
    assert tree.find("Text")[0].text == "Title"
    assert [t.text for t in tree.find("Text")] == ["Title", "hello", "Save"]
    print("\ncompose self-test: OK")
