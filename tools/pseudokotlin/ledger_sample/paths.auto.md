# PseudoUI AUTO verify -- paths: bindings emitted by the TRANSPILER (no hand spec)

Every binding expression in the IR was transpiled Kt->Py and eval'd against kotlin_rt +
the transpiled viewModel. There is NO per-screen binding spec -- the transpiler IS the spec.

## leaf agreement vs hand-built (same seeded data)
- shared (type+content):  3
- interpreted-only:       0   (Compose representation: icon descs etc.)
- hand-built-only:        0   (kit glyphs/helpers)

## dynamic values resolved (0/0 match hand-built)
- unresolved IR exprs: 0

## sample of the transpiler-emitted bindings (Kotlin -> Python, mechanical)
    'activePaths.isEmpty()'
      -> __r = (len(activePaths) == 0)
    'activePaths.isNotEmpty()'
      -> __r = (len(activePaths) != 0)
    'pickerState'
      -> __r = pickerState
    'viewModel.activePaths.collectAsStateWithLifecycle()'
      -> __r = viewModel.activePaths.collectAsStateWithLifecycle()
    'viewModel.pickerState.collectAsStateWithLifecycle()'
      -> __r = viewModel.pickerState.collectAsStateWithLifecycle()
