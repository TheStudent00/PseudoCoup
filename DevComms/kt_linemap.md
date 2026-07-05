# py-line → kt-line sidecar for the layout inspector

## Goal
The layout inspector linked each component to its Kotlin **file** only. This adds an exact
**line** deep-link: pyline→ktline per generated module, produced by the same build, consumed by
the inspector.

## Mechanism chosen and why
Handlers in the transpiler return plain strings, so tree-sitter node positions are lost by the
time a module is assembled. Threading provenance through every handler + every string join would
be invasive. Instead:

- **Marker side-channel.** `KtToPy._kt_tag(text, node)` appends a trailing comment
  `  #@@KTSRC <ktline>` to the **first physical line** of each rendered statement/decl, carrying
  `node.start_point[0]+1` (the Kotlin source line). Tagging happens at the statement funnel
  (`transpiler.stmt_lines`), the expression-body return line (`declarations._render_function_body`),
  and each top-level decl (`declarations.v_source_file`).
- **Why the first line / why it survives.** Indentation (`util.indent`) prepends spaces and joins
  are always `"\n"`, so no assembly step merges or splits lines — each tagged line stays its own
  physical line. Line numbers are therefore exact **in the final module text**, which is where the
  map is read.
- **Extraction + strip.** `build_mixingcenter.extract_linemap(code)` scans the final text, records
  `{py_line: kt_line}`, and strips the markers. Stripping a trailing comment never removes a line,
  so the recorded py line numbers stay valid against the written `.py` (which is what the runtime
  execs and what `node.src` captures via the stack frame).
- **Opt-in.** `self._srcmap` defaults `False`; only `build_mixingcenter` sets it `True`. So
  `transpile()` output stays **byte-identical** for the oracle / kotlin-test / fidelity paths that
  transpile fresh — the gates are structurally protected.
- **Safety.** `_kt_tag` refuses to tag a line containing `"""`/`'''` (a marker there would land
  inside string data); such statements simply fall back to file-level linking.

## Granularity
Statement-level (no sub-expression), which for this codebase is **per-component**: every transpiled
Compose component (`Text(...)`, `Column(...)`, `Scaffold(...)`, …) is emitted as its own single
Python statement line, so each maps to its own Kotlin line. Unmapped lines (helper `def _lamN`
headers, triple-quote statements) degrade gracefully to the existing file-level link.

## Sidecar format
One `<module>.py.linemap.json` next to each generated `.py`:
`{"kt": "<app-root-relative .kt path>", "map": {"<py_line>": <kt_line>, ...}}`
254 modules → 254 sidecars.

## Consumer wiring
`WFL_MixingCenter/render/inspect_layout.py::source_of` now reads the sidecar
(`_linemap`) for the component's py line; on a hit it deep-links `kt:<file>:<line>` and adds the
Kotlin source line text (`kt_code`) rendered under the link in the HTML. On a miss it keeps the
old file-level link. (This file lives under `render/` but is the inspector/HTML generator the task
named as the consumer — not the kivy kit / interact / walk / diff the fence protects; only the
kt-linking code was touched.)

## Verification gates (verbatim)

### 5 spot-checks (py line ↔ kt line)
```
[ui/gym/GymListScreen.py]  py 25 -> kt 134
  py: Text(gym.name, style=MaterialTheme.typography.titleMedium, fontWeight=FontWeight.SemiB
  kt: Text(   // gym.name,
[ui/gym/GymListScreen.py]  py 30 -> kt 129
  py: Row(modifier=Modifier.fillMaxWidth(), horizontalArrangement=Arrangement.SpaceBetween,
  kt: Row(
[ui/gym/GymListScreen.py]  py 58 -> kt 270
  py: Text(label, style=MaterialTheme.typography.labelSmall, color=MaterialTheme.colorScheme
  kt: Text(
[ui/settings/SettingsScreen.py]  py 32 -> kt 85
  py: AlertDialog(onDismissRequest=_lam1, title=(lambda it=None: Text("Restore from backup?"
  kt: AlertDialog(
[ui/history/HistoryScreen.py]  py 16 -> kt 70
  py: Text(text="No workouts yet", style=MaterialTheme.typography.titleMedium, color=Mat
  kt: Text(   // text = "No workouts yet",
```

### Build
```
254 .kt files (advanced transpiler = KtToPy)
  written .py        : 254
  py-compile OK      : 254/254
  transpiler errored : 0
  emitted-but-invalid: 0
```
No `@@KTSRC` markers remain in any written `.py`. HTML deep-links confirmed rendering
(18 exact-line `GymListScreen.kt:<n>` links in the regenerated HTML, file-level fallback otherwise).

### run_kotlin_tests.py
```
RESULT: 160/160 pass
```

### interact.py
```
INTERACT: 513 fired, 513 ok, 0 failures across 27 screens
```

### fidelity.py
```
FIDELITY ALL: 377/377 components within tolerance (28 screens)
```

## Files changed
- `tools/pseudokotlin/transpiler.py` — `_srcmap` flag, `_kt_tag`, tag in `stmt_lines`
- `tools/pseudokotlin/nodes/declarations.py` — tag expression-body return line + top-level decls
- `tools/pseudokotlin/build_mixingcenter.py` — enable markers, `extract_linemap`, write sidecar
- `WFL_MixingCenter/render/inspect_layout.py` — read sidecar, deep-link exact kt line + kt code

Not committed / pushed (per task).
