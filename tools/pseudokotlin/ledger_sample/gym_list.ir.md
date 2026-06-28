# PseudoUI IR -- gym_list (from GymListScreen)

val gyms = viewModel.gyms.collectAsStateWithLifecycle()
val activeGym = viewModel.activeGym.collectAsStateWithLifecycle()
box V (Scaffold)
  IF gyms.isEmpty():
    box V (Box)
      Text<static> '"No gyms yet. Tap + to add one."'
  ELSE:
    box V (LazyColumn)
      FOREACH gymWithEquipment in gyms:
        box V (GymListItem)
          val gym = gymWithEquipment.profile
          val equipmentList = gymWithEquipment.equipment
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
                Text<DYN> 'gym.name'
                IF activeGym?.id == gymWithEquipment.profile.id:
                  box V (AssistChip)
                    Text<static> '"Active"'
                    Icon<DYN> None
                ELSE:
                  Button<static> 'Set active'
              Spacer<DYN> None
              LET type = gym.gymType (if non-null):
                Text<DYN> '"${type.emoji} ${type.displayName}"'
              Spacer<DYN> None
              box H (Row)
                box V (LabeledStat)
                  box V (Column)
                    Text<static> '"Equipment"'
                    Text<DYN> '"${equipmentList.size} items"'
              Spacer<DYN> None
              IF equipmentList.isNotEmpty():
                Text<static> '"Equipment"'
                box V (Box)
                  val equipmentNames = equipmentList.joinToString(", ") { it.name }
                  Text<DYN> 'equipmentNames'
                  box V (Box)
              ELSE:
                Text<static> '"No equipment listed"'
              Spacer<DYN> None
              box H (Row)
                Button<static> 'Delete gym'
  box V (TopAppBar)
    Text<static> '"Gym profiles"'
    Icon<static> 'Back'
  Icon<static> 'Add gym'