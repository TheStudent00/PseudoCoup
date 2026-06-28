# PseudoUI IR -- gym_list (from GymListScreen)

box V (Scaffold)
  IF gyms.isEmpty():
    box V (Box)
      Text<static> '"No gyms yet. Tap + to add one."'
  ELSE:
    box V (LazyColumn)
      FOREACH gymWithEquipment in gyms:
        box V (GymListItem)
          box V (WflCard)
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