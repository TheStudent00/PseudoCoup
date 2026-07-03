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


def _call_site():
    """The (file, line) in the TRANSPILED APP code that is creating the current node: walk up the call
    stack past the runtime's own frames to the first frame executing app code. The loader compiles each
    app file under its real path, so the frame carries ui/settings/SettingsScreen.py:123 exactly."""
    rt = os.path.dirname(os.path.abspath(__file__))          # .../tools/pseudokotlin/runtime
    f = sys._getframe(1)
    while f is not None:
        fn = f.f_code.co_filename
        if not fn.startswith(rt) and "WFL_MixingCenter" in fn and os.sep + "render" + os.sep not in fn:
            return fn, f.f_lineno
        f = f.f_back
    return None


class Node:
    def __init__(self, kind):
        self.kind, self.text, self.children = kind, None, []
        self.handlers = {}      # on*-event name -> the transpiled handler (wired to the kit, fired on action)
        self.props = {}         # the widget's VALUE kwargs (modifier chain, fontSize, arrangement, ...) --
                                # recorded here so the kit can APPLY them (the wrapper records, the kit draws)
        self.src = _call_site()  # (file, line) in the TRANSPILED app code that emitted this node -- the
                                 # inspector's link from a live component back to the code that declared it

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
                elif hasattr(a, "_ops"):         # a positional Modifier chain: `Spacer(Modifier.height(8))`
                    node.props.setdefault("modifier", a)
            for k, v in kwargs.items():          # `content=`, `topBar=`, `title=`, `label=`, `icon=`, …
                if k.startswith("on"):           # an EVENT handler (onClick/onValueChange/onDone): STORE it
                    if callable(v):              # for the kit to fire on user action -- never call at render
                        node.handlers[k] = v     # (calling it here would run app logic mid-build).
                    continue
                if k == "style":                 # a TextStyle VALUE -- it happens to be callable (permissive
                    node.props[k] = v            # object), so the slot-lambda branch would swallow it
                    continue
                if callable(v):
                    _call(v)
                elif k in ("text", "value") and isinstance(v, str):
                    node.text = v                # an input widget DISPLAYS its value -- record it
                else:
                    node.props[k] = v            # a VALUE kwarg (modifier/fontSize/arrangement/...) --
                                                 # recorded for the kit to apply
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


def CompositionLocalProvider(*args, **kwargs):
    """Provide CompositionLocal values for the duration of the content. The transpiled call is
    `CompositionLocalProvider(LocalX.provides(v), LocalY.provides(w), content=...)` (or the content lambda
    positional). Push each (local, value) pair, run content so every `.current` read below sees it, then
    pop. This is the theme's on-ramp: without the push, WflTheme.colors read only the local's default."""
    from runtime.compose_ui import _Provided
    provided = [a for a in args if isinstance(a, _Provided)]
    content = kwargs.get("content")
    if content is None:
        content = next((a for a in args if callable(a) and not isinstance(a, _Provided)), None)
    for p in provided:
        p.local.push(p.value)
    try:
        node = Node("CompositionLocalProvider")
        _emit(node)
        _STACK.append(node)
        try:
            if callable(content):
                _call(content)
        finally:
            _STACK.pop()
        return node
    finally:
        for p in reversed(provided):
            p.local.pop()


def Scaffold(*args, **kwargs):
    """Scaffold has SLOTS -- topBar / content / bottomBar / floatingActionButton -- and Compose FRAMES them
    (bar pinned top, content filling with inset, FAB floating bottom-end). The plain emitter dropped which
    child came from which slot, so the kit stacked them in emission order and the FAB landed on the title.
    Tag each child with its slot name so the kit can place it. content also receives the inner PaddingValues
    (a Stub here); the block runs so its subtree emits."""
    node = Node("Scaffold")
    _emit(node)
    _STACK.append(node)
    try:
        content_fn = kwargs.get("content") or next((a for a in args if callable(a)), None)
        for slot in ("topBar", "content", "floatingActionButton", "bottomBar", "snackbarHost"):
            fn = content_fn if slot == "content" else kwargs.get(slot)
            if callable(fn):
                before = len(node.children)
                _call(fn)
                for ch in node.children[before:]:
                    ch.props.setdefault("slot", slot)
    finally:
        _STACK.pop()
    return node


def _topbar(kind):
    """TopAppBar has SLOTS with a spec-defined visual ORDER: navigationIcon (left), title, then actions
    (right). The plain emitter ran kwargs in call order (title first), so the title rendered at the left
    edge and the nav icon after it -- backwards."""
    def make(*args, **kwargs):
        node = Node(kind)
        _emit(node)
        _STACK.append(node)
        try:
            for slot in ("navigationIcon", "title", "actions"):
                fn = kwargs.get(slot)
                if callable(fn):
                    _call(fn)
            for k, v in kwargs.items():              # non-slot kwargs keep the normal recording rules
                if k in ("navigationIcon", "title", "actions"):
                    continue
                if k.startswith("on") and callable(v):
                    node.handlers[k] = v
                elif not callable(v):
                    node.props[k] = v
        finally:
            _STACK.pop()
        return node
    return make


TopAppBar = _topbar("TopAppBar")
CenterAlignedTopAppBar = _topbar("CenterAlignedTopAppBar")
MediumTopAppBar = _topbar("MediumTopAppBar")


def Composable(fn=None, *a, **k):       # the @Composable annotation if it ever survives -> identity
    return fn if fn is not None else (lambda g: g)


def LaunchedEffect(*args, **kwargs):
    """Compose's enter-composition side effect: run the block on first composition and again whenever a
    key changes (synchronous model -- the block runs inline). The onboarding-complete navigation, scroll
    effects, etc. live in these blocks; inert would mean the app never leaves such screens."""
    block = kwargs.get("block")
    keys = args
    if block is None and args and callable(args[-1]):
        block, keys = args[-1], args[:-1]
    if not callable(block):
        return None

    def run_block():
        try:
            block()
        except TypeError as e:
            if e.__traceback__.tb_next is not None:
                raise
            block(None)
        return _EFFECT_RAN

    if _COMPOSITION is None:
        run_block()
        return None
    _COMPOSITION.slot(run_block, tuple(repr(k) for k in keys))
    return None


_EFFECT_RAN = object()


def _state_content(kind, state_key):
    """AnimatedContent/Crossfade: the content lambda receives the REAL target state (the current page/
    tab/step), not a placeholder -- otherwise the whole subtree renders around nothing."""
    def make(*args, **kwargs):
        node = Node(kind)
        _emit(node)
        _STACK.append(node)
        try:
            target = args[0] if args else kwargs.get(state_key)
            fn = kwargs.get("content") or next((x for x in args[1:] if callable(x)), None)
            if callable(fn):
                try:
                    fn(target)
                except TypeError as e:
                    if e.__traceback__.tb_next is not None:
                        raise
                    _call(fn)
        finally:
            _STACK.pop()
        return node
    return make


AnimatedContent = _state_content("AnimatedContent", "targetState")
Crossfade = _state_content("Crossfade", "targetState")


def AnimatedVisibility(*args, **kwargs):     # content renders only when actually visible
    node = Node("AnimatedVisibility")
    _emit(node)
    _STACK.append(node)
    try:
        visible = args[0] if args else kwargs.get("visible", True)
        fn = kwargs.get("content") or next((x for x in args[1:] if callable(x)), None)
        if visible and callable(fn):
            _call(fn)
    finally:
        _STACK.pop()
    return node


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
    """One live composition: the composable + args, plus a positional slot table so `remember` keeps the
    same value across recompositions (Compose's slot table). Slots are SCOPED -- the navigation host pushes
    each destination's route as a scope, so screen A's remembered values can never bleed into screen B's
    positions when the rendered destination changes."""
    def __init__(self, fn, args=(), kwargs=None):
        self.fn, self.args, self.kwargs = fn, args, (kwargs or {})
        self.slots = {}                      # scope -> [(keys, value)] by call position within the scope
        self._i = {}                         # scope -> next position (reset each compose)
        self._scopes = [None]
        self.root = None

    def compose(self):
        global _COMPOSITION
        prev = _COMPOSITION
        _COMPOSITION = self
        self._i = {}
        self._scopes = [None]
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
        sc = self._scopes[-1]
        lst = self.slots.setdefault(sc, [])
        i = self._i.get(sc, 0)
        self._i[sc] = i + 1
        if i < len(lst):
            okeys, val = lst[i]
            if okeys != keys:                # a key changed -> recompute this slot
                val = calc()
                lst[i] = (keys, val)
        else:
            val = calc()
            lst.append((keys, val))
        return val


def push_slot_scope(scope):
    """The navigation host brackets each destination's render with its route, so remember/effect slots are
    per-destination (never misaligned across screens)."""
    if _COMPOSITION is not None:
        _COMPOSITION._scopes.append(scope)


def pop_slot_scope():
    if _COMPOSITION is not None and len(_COMPOSITION._scopes) > 1:
        _COMPOSITION._scopes.pop()


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
