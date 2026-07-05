# Paint pass 3 — ICONS: real Material glyphs in the Compose→Kivy kit

## Source found (legitimate, already on the machine)
- **Font**: the OS package `fonts-material-design-icons-iconfont` —
  `/usr/share/fonts/truetype/material-design-icons-iconfont/MaterialIcons-Regular.ttf`
  (the real "Material Icons" TTF; codepoints verified present in its cmap).
- **Name→codepoint map**: the CSS that **ships with that same package** —
  `/usr/share/fonts-material-design-icons-iconfont/css/material-design-icons.css`
  (one `.material-icons.<name>:before { content:"\eXXX" }` rule per icon, 2193 entries).
- Nothing invented, nothing downloaded, no hand-drawn approximations, no per-name codepoint guesses.
  Both the glyph shapes and the name→codepoint mapping come from the one installed package.

Path (a) app resources: the app ships only `figtree_variable.ttf` (a text face) and two launcher
vector drawables — no icon font, none of the used icons as vectors. Path (c): the recorded
`imageVector` was NOT self-describing in this runtime (see mechanism) — so path (b), the installed
Material Icons font + its shipped codepoints, is the source.

## Mechanism (all in `WFL_MixingCenter/render/kivy_kit.py`, the only file touched)
1. **Restore the erased icon name.** In this runtime `Icons` is compose_ui's inert `_UIChain`, whose every
   attribute access returns the same nameless singleton — so `Icons.Default.Add` collapsed to a valueless
   object and the name was gone before the renderer. A general, name-**tracking** root (`_IconRef`) replaces
   it (patched into `compose_ui`, refreshing autostub's namespace cache): each attribute step remembers its
   segment, so the leaf (`Add`, `ArrowBack`, …) survives. Nothing per-icon.
2. **Make compose record it.** compose.py builds the tree by *calling* every arg/slot, and would otherwise
   drop an `imageVector` (a positional non-str value is ignored; a callable keyword is treated as a content
   slot). `_IconRef.__call__` therefore **self-records** onto the Icon node currently on compose's stack —
   one hook that captures the name for BOTH `Icon(Icons.Default.Add)` and `Icon(imageVector=…)`, with no
   change to compose.py.
3. **Draw the glyph.** `_load_icon_font()` registers the TTF with Kivy and parses the shipped CSS once.
   `_draw_icon()` renders the mapped glyph (a CoreLabel texture) centered in the icon's existing widget
   rect, bound to follow pos/size, in the recorded `tint` → else the M3 default `onSurfaceVariant` (via the
   existing `_theme_color`) → else, when the theme is unresolved (an unthemed run), Kivy's neutral white —
   exactly as a Text leaf falls back, so an icon stays visible/consistent instead of invented. Standalone
   Icons draw in `_leaf_atom`; icon-only buttons/FABs (which CONSUME their Icon) draw the consumed icon's
   glyph centered in the button at the M3 24dp size in `_leaf_button`.
   **Unmapped names stay empty boxes — never a wrong glyph.** Geometry is never touched (draw-only, inside
   the already-correct rect).

## Coverage
- **36/36** distinct icon names the app actually uses map to a real codepoint in the shipped file
  (Add, ArrowBack, ArrowDropDown, Check, Delete, FitnessCenter, HelpOutline, KeyboardArrowRight,
  MoreHoriz, Remove, SwapVert, Link, Info, …). Zero unmapped among the app's set.
- Icons passed as fully dynamic vectors (not a static `Icons.*.Name`) carry no name and remain empty
  boxes by design.

## Gates
- `fidelity.py`: **377/377** components within tolerance (28 screens) — unchanged; icons touch no box.
- Specimen: **24/24**.  SpecimenList: **5/5**.
- 6 screenshots regenerated into `layout_inspect/shots/` and eyeballed: back arrows, FAB `+` (Add),
  dumbbell (FitnessCenter), `⋯` (MoreHoriz), plate-calc `−`/`+`, Settings `▼` dropdown arrows and `>`
  nav chevrons all render correctly and sensibly; no wrong glyphs.

## Notes
- `Window.screenshot(name=X)` appends an incrementing `%(counter)04d` — regenerated shots land in a NEW
  numbered file, so re-check the latest number (a stale `0001` masked the working output during dev).
