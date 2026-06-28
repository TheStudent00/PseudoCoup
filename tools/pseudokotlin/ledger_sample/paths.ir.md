# PseudoUI IR -- paths (from PathsScreen)

val activePaths = viewModel.activePaths.collectAsStateWithLifecycle()
val pickerState = viewModel.pickerState.collectAsStateWithLifecycle()
box V (Box)
  box V (LazyColumn)
    IF activePaths.isNotEmpty():
      Text<static> '"Paths are the why. Programs are the how."'
    IF activePaths.isEmpty():
      box V (EmptyPathsState)
        box V (Column)
          Text<static> '"Start with your why."'
          Text<static> '"A Path connects your training to what actually matters — evidence-backed goals for mental health, bone strength, brain function, and more."'
          Spacer<DYN> None
          Button<static> 'Find your path'
    ELSE:
      FOREACH path in activePaths:
        box V (ActivePathCard)
          val definition = PathDefinition.findById(path.id)
          box V (WflCard)
            val shape = RoundedCornerShape(WflTheme.tokens.cardRadius)
            val border = BorderStroke(borderWidth, borderColor)
            val colors = CardDefaults.cardColors(containerColor = containerColor)
            val elevation = CardDefaults.cardElevation(defaultElevation = 0.dp)
            IF onClick != null:
              box V (Card)
            ELSE:
              box V (Card)
            box V (Column)
              box H (Row)
                Text<DYN> 'path.name'
                Button<static> 'Leave path'
              LET it = definition (if non-null):
                Spacer<DYN> None
                Text<DYN> 'it.tagline'
                Spacer<DYN> None
                box H (Row)
                  box V (LabeledStat)
                    box V (Column)
                      Text<static> '"Sessions"'
                      Text<DYN> '"${it.minSessionsPerWeek}–${it.maxSessionsPerWeek}/week"'
                  box V (LabeledStat)
                    box V (Column)
                      Text<static> '"Target"'
                      Text<DYN> '"${it.targetMinutesPerSession} min"'
                Spacer<DYN> None
                Text<static> '"The evidence"'
                box V (Box)
                  Text<DYN> 'it.evidenceSummary'
                  box V (Box)
                Spacer<DYN> None
      IF activePaths.size == 1:
        box V (Box)
          Button<static> 'Add a second path'
  box V (AnimatedVisibility)
    LET state = pickerState (if non-null):
      box V (PathSelectionSheet)
        val sections = PathDefinition.grouped(
        excludeIds = if (state.isAddingSecond) state.enrolledPathIds else emptySet(),
    )
        val title = if (state.isAddingSecond) "Add a second path" else "Find your Path"
        val subtitle = if (state.isAddingSecond) {
        "Choose one more to work toward."
    } else {
        "Choose what matters to you. Select up to 2 paths."
    }
        box V (Scaffold)
          box V (LazyColumn)
            Text<DYN> 'subtitle'
          box V (TopAppBar)
            Text<DYN> 'title'
            Icon<static> 'Cancel'
          box V (Surface)
            Button<static> 'Start my Path'