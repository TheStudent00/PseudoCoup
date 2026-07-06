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

_NAMES = """Add Alignment Arrangement ArrowBack ArrowDownward ArrowDropDown ArrowUpward
BarChart Bedtime Brush Canvas Check CheckCircle Close
LaunchedEffect
ColumnScope DatePicker DatePickerDialog DateRange Dp Edit EmojiEvents ExpandLess ExpandMore ExperimentalLayoutApi
ExperimentalMaterial3Api ExperimentalTextApi FastOutSlowInEasing Favorite FavoriteBorder
FitnessCenter FocusRequester FontStyle FontVariation FontWeight HelpOutline Home
Icons ImageVector ImeAction Immutable Info IntrinsicSize KeyboardActions KeyboardArrowDown KeyboardArrowRight
KeyboardArrowUp KeyboardOptions KeyboardType Link ListItemDefaults LocalConfiguration LocalFocusManager Modifier
MoreHoriz MoreVert MutableInteractionSource NavigationBarItemDefaults Offset Path PathEffect Person
PlayArrow ReadOnlyComposable Remove RepeatMode RoundedCornerShape Route Search
SegmentedButtonDefaults SelectableDates SelfImprovement Size SolidColor Spring Star
Stroke StrokeCap StrokeJoin SwapVert SwipeToDismissBoxValue TextAlign TextDecoration TextOverflow
TextRange TooltipDefaults WindowInsets alpha animateFloat animateFloatAsState
background border clickable clip clipToBounds detectHorizontalDragGestures
drawBehind fadeIn fadeOut fillMaxHeight fillMaxSize fillMaxWidth focusRequester getValue graphicsLayer height
heightIn horizontalScroll infiniteRepeatable isSystemInDarkTheme key lerp navigationBarsPadding
offset onFocusChanged onGloballyPositioned padding pointerInput positionInParent rememberDatePickerState
rememberInfiniteTransition rememberLazyListState rememberModalBottomSheetState rememberPagerState rememberScrollState
rememberSwipeToDismissBoxState rememberTooltipState rotate scale setValue size slideInHorizontally slideInVertically
slideOutHorizontally slideOutVertically spring togetherWith tween verticalScroll width
withFrameMillis wrapContentSize zIndex rememberLauncherForActivityResult LocalContext
LocalDensity LocalLifecycleOwner LocalSoftwareKeyboardController""".split()

for _n in _NAMES:
    globals()[_n] = _UI


# ---- the COLOR TABLE: real colors + shapes + schemes (was inert, so the paint layer stayed dark) ---- #
class Color:
    """A real Compose Color. The transpiled theme builds these as Color(Int32(0xFF6650A4)) (a packed
    0xAARRGGBB long -- Int32 wraps it to a SIGNED 32-bit int, so mask back to unsigned before unpacking)
    or Color(red, green, blue[, alpha]) with 0..1 floats. Exposes .red/.green/.blue/.alpha as 0..1 floats
    for the kit's _channels resolver; .copy(...) returns a new Color for chains the kit doesn't model."""
    __slots__ = ("red", "green", "blue", "alpha", "value")

    def __init__(self, *a, **k):
        def f(x, d=0.0):
            try:
                return float(x)
            except (TypeError, ValueError):
                return d
        if "red" in k or "green" in k or "blue" in k:      # channel kwargs
            self.red, self.green, self.blue = f(k.get("red")), f(k.get("green")), f(k.get("blue"))
            self.alpha = f(k.get("alpha", 1.0), 1.0)
            self.value = None
            return
        if len(a) == 1 and isinstance(a[0], int) and not isinstance(a[0], bool):
            v = int(a[0]) & 0xFFFFFFFF                      # Int32 delivers this signed; mask to unsigned
            self.value = v
            alpha = ((v >> 24) & 0xFF) / 255.0
            self.alpha = 1.0 if (alpha == 0.0 and v <= 0xFFFFFF) else alpha
            self.red = ((v >> 16) & 0xFF) / 255.0
            self.green = ((v >> 8) & 0xFF) / 255.0
            self.blue = (v & 0xFF) / 255.0
            return
        if len(a) >= 3:                                    # Color(r, g, b[, a]) floats
            self.red, self.green, self.blue = f(a[0]), f(a[1]), f(a[2])
            self.alpha = f(a[3], 1.0) if len(a) > 3 else 1.0
            self.value = None
            return
        # unknown form: an opaque black, still a real Color so paint resolves rather than crashing
        self.red = self.green = self.blue = 0.0
        self.alpha = 1.0
        self.value = None

    def copy(self, **k):
        c = Color(red=k.get("red", self.red), green=k.get("green", self.green),
                  blue=k.get("blue", self.blue), alpha=k.get("alpha", self.alpha))
        return c

    def toArgb(self):
        if self.value is not None:
            return self.value
        def b(x):
            return max(0, min(255, int(round(x * 255))))
        return (b(self.alpha) << 24) | (b(self.red) << 16) | (b(self.green) << 8) | b(self.blue)

    def __getattr__(self, _n):                             # permissive tail for chains the kit ignores
        return _UI

    def __repr__(self):
        return f"Color({self.red:.3f}, {self.green:.3f}, {self.blue:.3f}, {self.alpha:.3f})"


# companions the app reads. Unspecified is DELIBERATELY the inert sentinel (type _UIChain), which the kit's
# _channels rejects by name -- so a WflColors default of Color.Unspecified paints nothing (correct) rather
# than resolving to a stray black.
Color.Transparent = Color(red=0.0, green=0.0, blue=0.0, alpha=0.0)
Color.White = Color(0xFFFFFFFF)
Color.Black = Color(0xFF000000)
Color.Red = Color(0xFFFF0000)
Color.Green = Color(0xFF00FF00)
Color.Blue = Color(0xFF0000FF)
Color.Gray = Color(0xFF888888)
Color.LightGray = Color(0xFFCCCCCC)
Color.DarkGray = Color(0xFF444444)
Color.Yellow = Color(0xFFFFFF00)
Color.Cyan = Color(0xFF00FFFF)
Color.Magenta = Color(0xFFFF00FF)
Color.Unspecified = _UI


class RoundedCornerShape:
    """A real corner shape exposing a numeric .radius for the kit's _radius resolver. Forms:
    RoundedCornerShape(8) (uniform dp) and RoundedCornerShape(topStart=, topEnd=, bottomEnd=, bottomStart=)
    (per-corner -- .topStart is what the kit reads for the rounded rect it draws)."""
    __slots__ = ("radius", "topStart", "topEnd", "bottomEnd", "bottomStart")

    def __init__(self, *a, **k):
        def num(v, d=0.0):
            try:
                return float(v)
            except (TypeError, ValueError):
                return d
        if a:
            r = num(a[0])
            self.radius = self.topStart = self.topEnd = self.bottomEnd = self.bottomStart = r
        else:
            self.topStart = num(k.get("topStart", k.get("topStartPercent")))
            self.topEnd = num(k.get("topEnd", k.get("topEndPercent")))
            self.bottomEnd = num(k.get("bottomEnd", k.get("bottomEndPercent")))
            self.bottomStart = num(k.get("bottomStart", k.get("bottomStartPercent")))
            self.radius = self.topStart


class _CircleShape:
    """CircleShape: a fully-rounded shape. Exposes a very large radius; the kit clamps it to half the
    widget's size, giving a pill / circle."""
    radius = 9999.0


CircleShape = _CircleShape()


class _ColorScheme:
    """An M3 color scheme: the role kwargs (primary/surface/background/onSurface/outline/...) become
    attributes, each a real Color. Roles the app omits are simply absent (getattr -> None), so the kit
    falls back rather than the runtime inventing a palette."""
    def __init__(self, **roles):
        for name, col in roles.items():
            setattr(self, name, col)

    def copy(self, **changes):
        d = dict(self.__dict__)
        d.update(changes)
        return _ColorScheme(**d)


def lightColorScheme(**roles):
    return _ColorScheme(**roles)


def darkColorScheme(**roles):
    return _ColorScheme(**roles)


def _scheme_role(role):
    """The current MaterialTheme.colorScheme's role Color, or None while the scheme is unresolved (the
    theme composable hasn't run yet) or the role is absent. Looked up lazily (MaterialTheme is defined
    further down this module) so *Defaults factories below can resolve an omitted color argument to the
    same theme the kit's _theme_color() reads later -- one shared source of truth, never a second table."""
    cs = getattr(MaterialTheme, "colorScheme", None)
    if cs is None or type(cs).__name__ == "_UIChain":
        return None
    v = getattr(cs, role, None)
    return v if isinstance(v, Color) else None


class ColorsSpec:
    """A REAL, value-retaining result for every M3 `*Defaults.xColors(...)` factory (CardDefaults.cardColors,
    ButtonDefaults.buttonColors/textButtonColors, TopAppBarDefaults.topAppBarColors, FilterChipDefaults.
    filterChipColors, AssistChipDefaults.assistChipColors, ...). Was previously the inert `_UIChain` autostub,
    which silently discarded every containerColor/contentColor/... argument -- this is the fix.

    Each named role kwarg passed explicitly is kept AS-IS (including `Color.Unspecified`, which must stay the
    inert marker -- never resolved to a default, per the "unresolved color = no paint" law). Any role kwarg
    OMITTED entirely resolves to the matching MaterialTheme.colorScheme role via `_scheme_role`, the exact
    mechanism `_ColorScheme`/`MaterialTheme` already provide elsewhere in this file -- no second table, no
    invented palette. Roles that have no natural colorScheme counterpart (e.g. disabled* variants) are left
    `None` when omitted, which the paint layer treats as "unresolved" (skip), exactly like every other gap."""
    __slots__ = ("roles",)

    # factory kwarg name -> (default colorScheme role name to resolve when omitted, else None -> stays None)
    _DEFAULTS = {
        "containerColor": "surface", "contentColor": "onSurface",
        "selectedContainerColor": "secondaryContainer", "selectedContentColor": "onSecondaryContainer",
        "selectedLabelColor": "onSecondaryContainer", "labelColor": "onSurfaceVariant",
        "leadingIconContentColor": "onSurfaceVariant", "trailingIconContentColor": "onSurfaceVariant",
        "disabledContainerColor": None, "disabledContentColor": None, "disabledLabelColor": None,
        "disabledLeadingIconContentColor": None, "disabledTrailingIconContentColor": None,
        "scrolledContainerColor": None, "titleContentColor": "onSurface",
        "navigationIconContentColor": "onSurfaceVariant", "actionIconContentColor": "onSurfaceVariant",
        "disabledContentColor_button": None,
    }

    def __init__(self, **kwargs):
        roles = {}
        for k, v in kwargs.items():
            if v is not None:
                roles[k] = v                       # explicit value (incl. Color.Unspecified): kept as-is
            else:
                roles[k] = None
        for k in kwargs:
            if kwargs[k] is None:
                default_role = self._DEFAULTS.get(k)
                roles[k] = _scheme_role(default_role) if default_role else None
        object.__setattr__(self, "roles", roles)

    def __getattr__(self, name):
        roles = object.__getattribute__(self, "roles")
        if name in roles:
            return roles[name]
        return _UI                                  # an unasked-for role: permissive tail, never invented

    def containerColorFor(self, selected=False, disabled=False):
        """The role a kit paint routine should use for a container fill, honoring selected/disabled state
        the same way M3's ColorScheme-derived defaults do -- selected wins over the plain containerColor,
        disabled wins over both (Kotlin's own precedence for these factories)."""
        r = self.roles
        if disabled and r.get("disabledContainerColor") is not None:
            return r["disabledContainerColor"]
        if selected and r.get("selectedContainerColor") is not None:
            return r["selectedContainerColor"]
        return r.get("containerColor")

    def contentColorFor(self, selected=False, disabled=False):
        r = self.roles
        if disabled and r.get("disabledContentColor") is not None:
            return r["disabledContentColor"]
        if selected:
            for k in ("selectedContentColor", "selectedLabelColor"):
                if r.get(k) is not None:
                    return r[k]
        for k in ("contentColor", "labelColor"):
            if r.get(k) is not None:
                return r[k]
        return None


class _CardDefaults:
    """CardDefaults.cardColors/elevatedCardColors/outlinedCardColors: all three build the same ColorsSpec
    shape (containerColor/contentColor[/disabledContainerColor/disabledContentColor]); M3 differs them only
    by which theme role backs an OMITTED containerColor (filled/elevated = surface[Variant]; outlined =
    surface) -- irrelevant here since every real call site in this app (WflCard.kt:47) passes containerColor
    explicitly. cardElevation is left as the harmless inert stub (elevation is drawn from _ELEVATION_LEVEL,
    a spec table, not from this factory's dp argument)."""
    @staticmethod
    def cardColors(containerColor=None, contentColor=None, disabledContainerColor=None,
                    disabledContentColor=None, *a, **k):
        return ColorsSpec(containerColor=containerColor, contentColor=contentColor,
                           disabledContainerColor=disabledContainerColor,
                           disabledContentColor=disabledContentColor)

    elevatedCardColors = cardColors
    outlinedCardColors = cardColors

    def __getattr__(self, name):                    # cardElevation / any other factory: permissive tail
        return _UI


CardDefaults = _CardDefaults()


class _ButtonDefaults:
    """ButtonDefaults.buttonColors/textButtonColors/... : real ColorsSpec, replacing the inert autostub that
    discarded Button(colors = ButtonDefaults.buttonColors(containerColor = ..., contentColor = ...))."""
    @staticmethod
    def buttonColors(containerColor=None, contentColor=None, disabledContainerColor=None,
                      disabledContentColor=None, *a, **k):
        return ColorsSpec(containerColor=containerColor, contentColor=contentColor,
                           disabledContainerColor=disabledContainerColor,
                           disabledContentColor=disabledContentColor)

    @staticmethod
    def textButtonColors(containerColor=None, contentColor=None, disabledContainerColor=None,
                          disabledContentColor=None, *a, **k):
        return ColorsSpec(containerColor=containerColor, contentColor=contentColor,
                           disabledContainerColor=disabledContainerColor,
                           disabledContentColor=disabledContentColor)

    outlinedButtonColors = elevatedButtonColors = filledTonalButtonColors = buttonColors

    def __getattr__(self, name):
        return _UI


ButtonDefaults = _ButtonDefaults()


class _FilterChipDefaults:
    """FilterChipDefaults.filterChipColors: real ColorsSpec carrying selected/disabled variants (the
    selected-state kwargs a FilterChip actually uses to differ its look when checked)."""
    @staticmethod
    def filterChipColors(containerColor=None, labelColor=None, selectedContainerColor=None,
                          selectedLabelColor=None, disabledContainerColor=None, disabledLabelColor=None,
                          leadingIconContentColor=None, trailingIconContentColor=None, *a, **k):
        return ColorsSpec(containerColor=containerColor, labelColor=labelColor,
                           selectedContainerColor=selectedContainerColor,
                           selectedLabelColor=selectedLabelColor,
                           disabledContainerColor=disabledContainerColor,
                           disabledLabelColor=disabledLabelColor,
                           leadingIconContentColor=leadingIconContentColor,
                           trailingIconContentColor=trailingIconContentColor)

    def __getattr__(self, name):
        return _UI


FilterChipDefaults = _FilterChipDefaults()


class _AssistChipDefaults:
    """AssistChipDefaults.assistChipColors: real ColorsSpec (GymListScreen.kt:152 passes containerColor/
    labelColor/leadingIconContentColor explicitly)."""
    @staticmethod
    def assistChipColors(containerColor=None, labelColor=None, leadingIconContentColor=None,
                          trailingIconContentColor=None, disabledContainerColor=None,
                          disabledLabelColor=None, *a, **k):
        return ColorsSpec(containerColor=containerColor, labelColor=labelColor,
                           leadingIconContentColor=leadingIconContentColor,
                           trailingIconContentColor=trailingIconContentColor,
                           disabledContainerColor=disabledContainerColor,
                           disabledLabelColor=disabledLabelColor)

    def __getattr__(self, name):
        return _UI


AssistChipDefaults = _AssistChipDefaults()


class _TopAppBarDefaults:
    """TopAppBarDefaults.topAppBarColors: real ColorsSpec (WorkoutExecutionScreen.kt:211 passes
    containerColor explicitly)."""
    @staticmethod
    def topAppBarColors(containerColor=None, scrolledContainerColor=None, navigationIconContentColor=None,
                         titleContentColor=None, actionIconContentColor=None, *a, **k):
        return ColorsSpec(containerColor=containerColor, scrolledContainerColor=scrolledContainerColor,
                           navigationIconContentColor=navigationIconContentColor,
                           titleContentColor=titleContentColor,
                           actionIconContentColor=actionIconContentColor)

    def __getattr__(self, name):
        return _UI


TopAppBarDefaults = _TopAppBarDefaults()


class BorderStroke:
    """A REAL BorderStroke(width, color): retains .width/.color so the kit's _paint_spec can read a Card's
    (or any component's) `border=` constructor kwarg. Was previously the inert autostub, which discarded
    both arguments -- WflCard.kt:46's BorderStroke(borderWidth, borderColor) built nothing usable.
    `color` may be `Color.Unspecified` (kept as-is, unresolved -- never invented) or omitted (resolves to
    MaterialTheme.colorScheme.outline, M3's own BorderStroke default when a caller doesn't specify one)."""
    __slots__ = ("width", "color")

    def __init__(self, width=1.0, color=None, *a, **k):
        try:
            self.width = float(width)
        except (TypeError, ValueError):
            self.width = 1.0
        self.color = color if color is not None else _scheme_role("outline")


class TextFieldValue:
    """A text-input's value object. Was an inert _UI stub, which DESTROYED the string at construction --
    every BasicTextField(value = TextFieldValue(...)) rendered empty (the WorkoutExecution ValueAdjusters).
    Keeps the text; the recorder unwraps it into node.text like a plain string."""
    def __init__(self, text="", selection=None, *a, **k):
        self.text = "" if text is None else str(text)
        self.selection = selection

    def copy(self, text=None, **k):
        return TextFieldValue(self.text if text is None else text, self.selection)

    def __str__(self):
        return self.text

    def __eq__(self, other):
        return isinstance(other, TextFieldValue) and other.text == self.text

    def __hash__(self):
        return hash(self.text)


class AnnotatedStringBuilder:
    """buildAnnotatedString { append… withStyle(...) { append… } }: collects the PLAIN text (the spans are
    style, which the kit does not paint yet); toString() yields it, and Text() renders that directly. The
    transpiler's builder scope makes one of these the implicit receiver, exactly like buildString."""
    def __init__(self):
        self._parts = []

    def append(self, x=""):
        self._parts.append("" if x is None else str(x))
        return self

    def appendLine(self, x=""):
        self._parts.append(("" if x is None else str(x)) + "\n")
        return self

    def withStyle(self, _style=None, block=None):
        if block is None and callable(_style):
            _style, block = None, _style
        if callable(block):
            block()                       # bare append inside still binds to this builder (receiver scope)
        return self

    def pushStyle(self, _style=None):
        return 0

    def popStyle(self, *_a):
        return self

    pushStringAnnotation = withStyle
    pop = popStyle

    def toAnnotatedString(self):
        return self.toString()

    def toString(self):
        return "".join(self._parts)

    def __str__(self):
        return self.toString()


def buildAnnotatedString(block):        # kept real for a first-class reference; usually inlined by the
    b = AnnotatedStringBuilder()        # transpiler's builder scope
    block(b)
    return b.toString()


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
        for name, size, line in (("displayLarge", 57, 64), ("displayMedium", 45, 52),
                                 ("displaySmall", 36, 44), ("headlineLarge", 32, 40),
                                 ("headlineMedium", 28, 36), ("headlineSmall", 24, 32),
                                 ("titleLarge", 22, 28), ("titleMedium", 16, 24), ("titleSmall", 14, 20),
                                 ("bodyLarge", 16, 24), ("bodyMedium", 14, 20), ("bodySmall", 12, 16),
                                 ("labelLarge", 14, 20), ("labelMedium", 12, 16), ("labelSmall", 11, 16)):
            setattr(self, name, TextStyle(fontSize=size, lineHeight=line))


class Font:
    """A font resource reference: Font(R.font.x, weight=...) -- R.font.x resolves to the resource NAME,
    so the kit can find the actual file under the app's res/font/."""
    def __init__(self, resource=None, *a, **k):
        self.resource = resource if isinstance(resource, str) else None
        self.weight = k.get("weight")


class FontFamily:
    """A set of Font()s (was inert, so the app's real typeface -- and therefore every measured text
    width -- silently fell back to Kivy's default font)."""
    Default = Monospace = SansSerif = Serif = Cursive = None

    def __init__(self, *fonts, **k):
        self.fonts = [f for f in fonts if isinstance(f, Font)]

    @property
    def resource(self):
        return next((f.resource for f in self.fonts if f.resource), None)


def Typography(*a, **roles):
    """The app's type scale as REAL role -> TextStyle mappings (was inert, so the theme's custom sizes and
    line heights -- e.g. this app's titleMedium 18/24 vs M3's 16/24 -- silently fell back to M3 defaults).
    Unspecified roles keep the M3 default."""
    t = _M3Typography()
    for name, style in roles.items():
        if getattr(style, "fontSize", None) is not None:
            setattr(t, name, style)
    return t


class _MaterialTheme:
    """MaterialTheme is BOTH the theme object (`MaterialTheme.typography.bodyMedium`) and a composable
    (`MaterialTheme(colorScheme=..., typography=..., content=...)`). The object side carries the real M3
    type scale; the composable side INSTALLS a provided typography (the app theme's custom type scale)
    and runs its content so children emit. colorScheme stays inert until the kit paints colors."""
    def __init__(self):
        self.typography = _M3Typography()
        self.colorScheme = _UI
        self.shapes = _UI

    def __call__(self, *args, **kwargs):
        t = kwargs.get("typography")
        if isinstance(t, _M3Typography):
            self.typography = t                  # the app theme's scale: every later style read sees it
        cs = kwargs.get("colorScheme")
        if isinstance(cs, _ColorScheme):
            self.colorScheme = cs                # the app theme's scheme: every _theme_color read sees it
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


class IntrinsicSize:                    # height(IntrinsicSize.Min) = size to the content's intrinsic
    Min = "intrinsic_min"               # measure -- for the kit that IS wrap-to-content. The values are
    Max = "intrinsic_max"               # non-numeric ON PURPOSE: the autostub float-coerces to 0.0, which
                                        # collapsed every IntrinsicSize row to zero height (roadmap overlap).


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
