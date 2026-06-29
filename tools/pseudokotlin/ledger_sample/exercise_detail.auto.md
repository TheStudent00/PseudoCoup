# PseudoUI AUTO verify -- exercise_detail: bindings emitted by the TRANSPILER (no hand spec)

Every binding expression in the IR was transpiled Kt->Py and eval'd against kotlin_rt +
the transpiled viewModel. There is NO per-screen binding spec -- the transpiler IS the spec.

## leaf agreement vs hand-built (same seeded data)
- shared (type+content):  8
- interpreted-only:       4   (Compose representation: icon descs etc.)
    INT I: 'More'
    INT I: 'Toggle favorite'
    INT T: 'Duplicate & Edit'
    INT T: 'Never program this'
- hand-built-only:        2   (kit glyphs/helpers)
    HB  T: '⋮'
    HB  T: '♡'

## dynamic values resolved (4/5 match hand-built)
    OK   T: 'Compound'
    OK   T: 'Bilateral'
    OK   T: 'Squat · Barbell'
    OK   T: 'Back Squat'
    MISS  T: 'Never program this'
- unresolved IR exprs: 1
    cond: 'showDeleteDialog'

## sample of the transpiler-emitted bindings (Kotlin -> Python, mechanical)
    '!exercise.cues.isNullOrBlank()'
      -> __r = (not (exercise.cues is None or len(exercise.cues.strip()) == 0))
    '!exercise.instructions.isNullOrBlank()'
      -> __r = (not (exercise.instructions is None or len(exercise.instructions.strip()) == 0))
    '!exercise.videoLink.isNullOrBlank()'
      -> __r = (not (exercise.videoLink is None or len(exercise.videoLink.strip()) == 0))
    'ex != null'
      -> __r = ex != None
    'ex?.isCustom == true'
      -> __r = (ex.isCustom if ex is not None else None) == True
    'ex?.name ?: ""'
      -> __r = ((ex.name if ex is not None else None) if (ex.name if ex is not None else None) is not None else "")
    'excludePrompt'
      -> __r = excludePrompt
    'exercise'
      -> __r = exercise
