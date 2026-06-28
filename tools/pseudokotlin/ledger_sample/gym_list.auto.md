# PseudoUI AUTO verify -- gym_list: bindings emitted by the TRANSPILER (no hand spec)

Every binding expression in the IR was transpiled Kt->Py and eval'd against kotlin_rt +
the transpiled viewModel. There is NO per-screen binding spec -- the transpiler IS the spec.

## leaf agreement vs hand-built (same seeded data)
- shared (type+content):  10
- interpreted-only:       0   (Compose representation: icon descs etc.)
- hand-built-only:        0   (kit glyphs/helpers)

## dynamic values resolved (4/4 match hand-built)
    OK   T: 'Home Gym'
    OK   T: '🏠 Home Gym'
    OK   T: '2 items'
    OK   T: 'Olympic Bar, Adjustable Dumbbe…'
- unresolved IR exprs: 1
    cond: 'onClick != null'

## sample of the transpiler-emitted bindings (Kotlin -> Python, mechanical)
    'BorderStroke(borderWidth, borderColor)'
      -> __r = BorderStroke(borderWidth, borderColor)
    'CardDefaults.cardColors(containerColor = containerColor)'
      -> __r = CardDefaults.cardColors(containerColor=containerColor)
    'CardDefaults.cardElevation(defaultElevation = 0.dp)'
      -> __r = CardDefaults.cardElevation(defaultElevation=dp(0))
    'RoundedCornerShape(WflTheme.tokens.cardRadius)'
      -> __r = RoundedCornerShape(WflTheme.tokens.cardRadius)
    'activeGym?.id == gymWithEquipment.profile.id'
      -> __r = (activeGym.id if activeGym is not None else None) == gymWithEquipment.profile.id
    'equipmentList.isNotEmpty()'
      -> __r = (len(equipmentList) != 0)
    'equipmentList.joinToString(", ") { it.name }'
      -> __r = equipmentList.joinToString(", ", (lambda it=None: it.name))
    'equipmentNames'
      -> __r = equipmentNames
