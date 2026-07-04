"""compose_ui.py -- the Compose styling / layout / icon / animation surface, as REAL wrappers.

These are the names that decorate the UI tree (Modifier, Color, shapes, Icons, theming, animation specs) plus
the layout modifier functions (padding/fillMaxWidth/...). For the headless tree + Kivy kit they carry no
behaviour yet, so each is a chainable structural value (`_UI`): attr, call, index all yield it, and it is
arithmetic/compare-safe so no chain ever crashes. The few with real behaviour are set below: dp/sp/em are
real numbers (sizes), rememberCoroutineScope is a real scope. This completes the compose binding -- these are
provided wrappers now, not autostub stubs. When the kit starts reading style, _UI grows real fields.
"""


class _UIChain:
    def __getattr__(self, n):
        return self

    def __call__(self, *a, **k):
        return self

    def __getitem__(self, _k):
        return self

    def __iter__(self):
        return iter(())

    def __len__(self):
        return 0

    def __bool__(self):
        return True

    def __contains__(self, _x):
        return False

    def _id(self, *a):
        return self

    __add__ = __radd__ = __sub__ = __rsub__ = __mul__ = __rmul__ = _id
    __truediv__ = __rtruediv__ = __floordiv__ = __mod__ = __neg__ = __pos__ = __abs__ = _id

    def __int__(self):
        return 0

    def __float__(self):
        return 0.0

    def __index__(self):
        return 0

    def __eq__(self, _o):
        return self is _o

    def __hash__(self):
        return id(self)

    def __lt__(self, _o):
        return False

    __gt__ = __le__ = __ge__ = __lt__

    def __repr__(self):
        return "<ui>"


_UI = _UIChain()

_NAMES = """Add Alignment Arrangement ArrowBack ArrowDownward ArrowDropDown ArrowUpward AssistChipDefaults
BarChart Bedtime BorderStroke Brush ButtonDefaults Canvas CardDefaults Check CheckCircle CircleShape Close Color
LaunchedEffect
ColumnScope DatePicker DatePickerDialog DateRange Dp Edit EmojiEvents ExpandLess ExpandMore ExperimentalLayoutApi
ExperimentalMaterial3Api ExperimentalTextApi FastOutSlowInEasing Favorite FavoriteBorder FilterChipDefaults
FitnessCenter FocusRequester Font FontFamily FontStyle FontVariation FontWeight HelpOutline Home
Icons ImageVector ImeAction Immutable Info IntrinsicSize KeyboardActions KeyboardArrowDown KeyboardArrowRight
KeyboardArrowUp KeyboardOptions KeyboardType Link ListItemDefaults LocalConfiguration LocalFocusManager Modifier
MoreHoriz MoreVert MutableInteractionSource NavigationBarItemDefaults Offset Path PathEffect Person
PlayArrow ReadOnlyComposable Remove RepeatMode RoundedCornerShape Route Search
SearchBarDefaults SegmentedButtonDefaults SelectableDates SelfImprovement Size SolidColor Spring Star
Stroke StrokeCap StrokeJoin SwapVert SwipeToDismissBoxValue TextAlign TextDecoration TextFieldValue TextOverflow
TextRange TooltipDefaults TopAppBarDefaults Typography WindowInsets alpha animateFloat animateFloatAsState
background border buildAnnotatedString clickable clip clipToBounds darkColorScheme detectHorizontalDragGestures
drawBehind fadeIn fadeOut fillMaxHeight fillMaxSize fillMaxWidth focusRequester getValue graphicsLayer height
heightIn horizontalScroll infiniteRepeatable isSystemInDarkTheme key lerp lightColorScheme navigationBarsPadding
offset onFocusChanged onGloballyPositioned padding pointerInput positionInParent rememberDatePickerState
rememberInfiniteTransition rememberLazyListState rememberModalBottomSheetState rememberPagerState rememberScrollState
rememberSwipeToDismissBoxState rememberTooltipState rotate scale setValue size slideInHorizontally slideInVertically
slideOutHorizontally slideOutVertically spring togetherWith tween verticalScroll width
withFrameMillis wrapContentSize zIndex rememberLauncherForActivityResult LocalContext
LocalDensity LocalLifecycleOwner LocalSoftwareKeyboardController""".split()

for _n in _NAMES:
    globals()[_n] = _UI


# ---- CompositionLocal: the theme's delivery path (was inert, so tokens/colors dropped) ----------- #
class _Provided:
    """The result of `LocalX provides value` (transpiled `LocalX.provides(value)`): a (local, value) pair
    handed to CompositionLocalProvider, which pushes it for the duration of its content."""
    __slots__ = ("local", "value")

    def __init__(self, local, value):
        self.local, self.value = local, value


class CompositionLocal:
    """A value provided high in the UI tree and read anywhere below via `.current`, without threading it
    through every function. The theme is exactly this: `WflTheme.tokens` reads `LocalWflTokens.current`.
    `.current` returns the innermost provided value, or the default the local was created with. Was an inert
    `<ui>` before, which is why every `WflTheme.tokens.*` / `WflTheme.colors.*` read collapsed to nothing."""
    __slots__ = ("_default_factory", "_stack")

    def __init__(self, default_factory):
        self._default_factory = default_factory
        self._stack = []                         # provided values, innermost last

    @property
    def current(self):
        if self._stack:
            return self._stack[-1]
        f = self._default_factory
        if callable(f):
            try:
                return f()
            except TypeError:
                return f(None)                   # the default lambda is emitted as `lambda it=None: ...`
        return f

    def provides(self, value):
        return _Provided(self, value)

    def providesDefault(self, value):            # Compose's providesDefault -- same pairing here
        return _Provided(self, value)

    def push(self, value):                       # the provider brackets its content with push/pop
        self._stack.append(value)

    def pop(self):
        if self._stack:
            self._stack.pop()


def staticCompositionLocalOf(default_factory=None, *a, **k):
    return CompositionLocal(default_factory)


compositionLocalOf = staticCompositionLocalOf   # (change-tracking distinction is moot in this model)


# ---- the few with real behaviour ----------------------------------------------------------------- #
def dp(x=0, *a, **k):        # a dimension IS its number here (so sizes/arithmetic are real)
    return x


sp = em = dp


def rememberCoroutineScope(*a, **k):
    import runtime.coroutines as _c
    return _c.CoroutineScope()


# ---- MaterialTheme: the M3 DEFAULT TYPE SCALE as real values (the Material spec, app-agnostic) ---- #
class _M3Typography:
    """material3's default type scale (fontSize in sp; sp == px here). Text(style = MaterialTheme.
    typography.titleLarge) was reading an inert <ui>, so every styled text fell back to one size."""
    def __init__(self):
        from runtime.java_rt import TextStyle
        for name, size in (("displayLarge", 57), ("displayMedium", 45), ("displaySmall", 36),
                           ("headlineLarge", 32), ("headlineMedium", 28), ("headlineSmall", 24),
                           ("titleLarge", 22), ("titleMedium", 16), ("titleSmall", 14),
                           ("bodyLarge", 16), ("bodyMedium", 14), ("bodySmall", 12),
                           ("labelLarge", 14), ("labelMedium", 12), ("labelSmall", 11)):
            setattr(self, name, TextStyle(fontSize=size))


class _MaterialTheme:
    """MaterialTheme is BOTH the theme object (`MaterialTheme.typography.bodyMedium`) and a composable
    (`MaterialTheme(colorScheme=..., typography=..., content=...)`). The object side carries the real M3
    type scale; the composable side runs its content so children emit. colorScheme stays inert until the
    kit paints colors."""
    def __init__(self):
        self.typography = _M3Typography()
        self.colorScheme = _UI
        self.shapes = _UI

    def __call__(self, *args, **kwargs):
        content = kwargs.get("content") or next((a for a in args if callable(a)), None)
        if callable(content):
            try:
                return content()
            except TypeError:
                return content(None)
        return None


MaterialTheme = _MaterialTheme()


class PaddingValues:
    """A REAL padding record (was inert, so LazyColumn(contentPadding=...) silently dropped its inset).
    Forms: PaddingValues(all) / (horizontal=, vertical=) / (start=, top=, end=, bottom=). The kit reads
    .l/.t/.r/.b."""
    __slots__ = ("l", "t", "r", "b")

    def __init__(self, *a, **k):
        def num(v):
            try:
                return float(v)
            except (TypeError, ValueError):
                return 0.0
        if len(a) == 1 and not k:
            self.l = self.t = self.r = self.b = num(a[0])
            return
        h, v = num(k.get("horizontal")), num(k.get("vertical"))
        self.l = num(k.get("start", k.get("left"))) or h
        self.r = num(k.get("end", k.get("right"))) or h
        self.t = num(k.get("top")) or v
        self.b = num(k.get("bottom")) or v

    def calculateTopPadding(self):
        return self.t

    def calculateBottomPadding(self):
        return self.b

    def calculateStartPadding(self, *_):
        return self.l

    def calculateEndPadding(self, *_):
        return self.r


# ---- the RECORDED style surface (the wrapper records, the kit applies) --------------------------- #
class _Mod:
    """A Modifier chain that RECORDS its calls: Modifier.fillMaxWidth().padding(16) -> a value carrying
    (('fillMaxWidth', (), {}), ('padding', (16,), {})). Immutable -- every call yields a new chain, like
    Kotlin's Modifier. The kit reads ._ops and applies what it understands."""
    __slots__ = ("_ops",)

    def __init__(self, ops=()):
        object.__setattr__(self, "_ops", tuple(ops))

    def __getattr__(self, name):
        def add(*a, **k):
            return _Mod(self._ops + ((name, a, k),))
        return add

    def __repr__(self):
        return f"<Modifier {'.'.join(o[0] for o in self._ops) or '-'}>"


Modifier = _Mod()


class FontWeight:            # DISTINCT values (an inert shared object can't tell Bold from Normal)
    Thin = Light = ExtraLight = "light"
    Normal = W400 = "normal"
    Medium = W500 = "medium"
    SemiBold = W600 = "semibold"
    Bold = W700 = ExtraBold = Black = "bold"


class TextAlign:
    Start = Left = "left"
    Center = "center"
    End = Right = "right"
    Justify = "justify"


class _Spaced(float):        # Arrangement.spacedBy(n): the spacing value, marked by type
    pass


class Arrangement:
    Start = Top = "start"
    Center = "center"
    End = Bottom = "end"
    SpaceBetween = "space_between"
    SpaceAround = "space_around"
    SpaceEvenly = "space_evenly"

    @staticmethod
    def spacedBy(v=0, *a, **k):
        try:
            return _Spaced(v)
        except (TypeError, ValueError):
            return _Spaced(0)


class Alignment:                        # DISTINCT 9-point values (an inert shared "top" can't tell a
    TopStart = "top_start"              # bottom-END FAB from a top-START one), so the kit can place each
    TopCenter = "top_center"
    TopEnd = "top_end"
    CenterStart = "center_start"
    Center = "center"
    CenterEnd = "center_end"
    BottomStart = "bottom_start"
    BottomCenter = "bottom_center"
    BottomEnd = "bottom_end"
    # 1-D alignments (used as cross-axis alignment in Row/Column) mapped onto the grid as best they can
    Top = "top_center"
    Bottom = "bottom_center"
    Start = "center_start"
    End = "center_end"
    CenterHorizontally = "center"
    CenterVertically = "center"
