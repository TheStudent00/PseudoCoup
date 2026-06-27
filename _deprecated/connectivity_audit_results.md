# Connectivity Audit Results

======================================================================
CONNECTIVITY PROBE (static) -- debug_panel
Kotlin VM is the reference; PC is verified against it.
======================================================================

Kotlin reference graph (DebugPanelViewModel):
  state fields : 
  derived      : 
  actions      : nowMs, shiftDays, resetTime, seedSessionDaysAgo, clearSessions, armCelebration, seedLifeEvent, resetDatabase, exportThenReset, checkAndRepairProgramData, refreshProgramCopy, refreshDbInfo, sendTestDiagnostics, simulateCrash, clearMessage, launchSeed
  screen reads : 
  screen calls : armCelebration, checkAndRepairProgramData, clearSessions, exportThenReset, nowMs, refreshDbInfo, refreshProgramCopy, resetDatabase, resetTime, seedLifeEvent, seedSessionDaysAgo, sendTestDiagnostics, shiftDays, simulateCrash
  screen navs  : 

PseudoCoup side:
  State fields : 
  methods      : load, program_count, seed
  screen reads : 
  screen calls : load, program_count, seed
  screen navs  : you

----------------------------------------------------------------------
VERIFY: every Kotlin connectivity node has a PC counterpart?

STATE fields (vm.state -> PC State)
   0/0 Kotlin state have a PC counterpart

ACTIONS/derived (vm methods -> PC methods)
   [GAP] nowMs                    -> (* no PC counterpart *)
   [GAP] shiftDays                -> (* no PC counterpart *)
   [GAP] resetTime                -> (* no PC counterpart *)
   [GAP] seedSessionDaysAgo       -> (* no PC counterpart *)
   [GAP] clearSessions            -> (* no PC counterpart *)
   [GAP] armCelebration           -> (* no PC counterpart *)
   [GAP] seedLifeEvent            -> (* no PC counterpart *)
   [GAP] resetDatabase            -> (* no PC counterpart *)
   [GAP] exportThenReset          -> (* no PC counterpart *)
   [GAP] checkAndRepairProgramData -> (* no PC counterpart *)
   [GAP] refreshProgramCopy       -> (* no PC counterpart *)
   [GAP] refreshDbInfo            -> (* no PC counterpart *)
   [GAP] sendTestDiagnostics      -> (* no PC counterpart *)
   [GAP] simulateCrash            -> (* no PC counterpart *)
   [GAP] clearMessage             -> (* no PC counterpart *)
   [GAP] launchSeed               -> (* no PC counterpart *)
   0/16 Kotlin actions/derived have a PC counterpart

SCREEN->vm action edges (screen calls the action)
   [GAP] armCelebration           -> (* no PC counterpart *)
   [GAP] checkAndRepairProgramData -> (* no PC counterpart *)
   [GAP] clearSessions            -> (* no PC counterpart *)
   [GAP] exportThenReset          -> (* no PC counterpart *)
   [GAP] nowMs                    -> (* no PC counterpart *)
   [GAP] refreshDbInfo            -> (* no PC counterpart *)
   [GAP] refreshProgramCopy       -> (* no PC counterpart *)
   [GAP] resetDatabase            -> (* no PC counterpart *)
   [GAP] resetTime                -> (* no PC counterpart *)
   [GAP] seedLifeEvent            -> (* no PC counterpart *)
   [GAP] seedSessionDaysAgo       -> (* no PC counterpart *)
   [GAP] sendTestDiagnostics      -> (* no PC counterpart *)
   [GAP] shiftDays                -> (* no PC counterpart *)
   [GAP] simulateCrash            -> (* no PC counterpart *)
   0/14 Kotlin screen->vm have a PC counterpart

========  CONNECTIVITY: 0/30 Kotlin edges preserved in PC  <-- GAPS ABOVE


======================================================================
CONNECTIVITY PROBE (static) -- exercise_create
Kotlin VM is the reference; PC is verified against it.
======================================================================

Kotlin reference graph (ExerciseCreateViewModel):
  state fields : 
  derived      : 
  actions      : onNameChange, togglePrimary, toggleSecondary, onPatternChange, onEquipmentChange, onUnilateralChange, onCompoundChange, onInstructionsChange, onVideoLinkChange, onCuesChange, onSeedSourceChange, save
  screen reads : 
  screen calls : onCompoundChange, onCuesChange, onEquipmentChange, onInstructionsChange, onNameChange, onPatternChange, onSeedSourceChange, onUnilateralChange, onVideoLinkChange, save, togglePrimary, toggleSecondary
  screen navs  : 

PseudoCoup side:
  State fields : is_unilateral, is_compound
  methods      : on_unilateral_change, on_compound_change, can_save, save
  screen reads : is_compound, is_unilateral
  screen calls : can_save, on_compound_change, on_unilateral_change, save
  screen navs  : exercises

----------------------------------------------------------------------
VERIFY: every Kotlin connectivity node has a PC counterpart?

STATE fields (vm.state -> PC State)
   0/0 Kotlin state have a PC counterpart

ACTIONS/derived (vm methods -> PC methods)
   [GAP] onNameChange             -> (* no PC counterpart *)
   [GAP] togglePrimary            -> (* no PC counterpart *)
   [GAP] toggleSecondary          -> (* no PC counterpart *)
   [GAP] onPatternChange          -> (* no PC counterpart *)
   [GAP] onEquipmentChange        -> (* no PC counterpart *)
   [OK ] onUnilateralChange       -> on_unilateral_change
   [OK ] onCompoundChange         -> on_compound_change
   [GAP] onInstructionsChange     -> (* no PC counterpart *)
   [GAP] onVideoLinkChange        -> (* no PC counterpart *)
   [GAP] onCuesChange             -> (* no PC counterpart *)
   [GAP] onSeedSourceChange       -> (* no PC counterpart *)
   [OK ] save                     -> save
   3/12 Kotlin actions/derived have a PC counterpart

SCREEN->vm action edges (screen calls the action)
   [OK ] onCompoundChange         -> on_compound_change
   [GAP] onCuesChange             -> (* no PC counterpart *)
   [GAP] onEquipmentChange        -> (* no PC counterpart *)
   [GAP] onInstructionsChange     -> (* no PC counterpart *)
   [GAP] onNameChange             -> (* no PC counterpart *)
   [GAP] onPatternChange          -> (* no PC counterpart *)
   [GAP] onSeedSourceChange       -> (* no PC counterpart *)
   [OK ] onUnilateralChange       -> on_unilateral_change
   [GAP] onVideoLinkChange        -> (* no PC counterpart *)
   [OK ] save                     -> save
   [GAP] togglePrimary            -> (* no PC counterpart *)
   [GAP] toggleSecondary          -> (* no PC counterpart *)
   3/12 Kotlin screen->vm have a PC counterpart

========  CONNECTIVITY: 6/24 Kotlin edges preserved in PC  <-- GAPS ABOVE


======================================================================
CONNECTIVITY PROBE (static) -- exercise_detail
Kotlin VM is the reference; PC is verified against it.
======================================================================

Kotlin reference graph (ExerciseDetailViewModel):
  state fields : 
  derived      : 
  actions      : toggleFavorite, duplicate, editCurrent, delete, onToggleExcluded, confirmSwapNow, confirmSwapLater, dismissExcludePrompt
  screen reads : 
  screen calls : confirmSwapLater, confirmSwapNow, delete, dismissExcludePrompt, duplicate, editCurrent, onToggleExcluded, toggleFavorite
  screen navs  : 

PseudoCoup side:
  State fields : 
  methods      : 
  screen reads : menu_open
  screen calls : close_menu, exercise, load, open_menu, toggle_favorite
  screen navs  : exercises

----------------------------------------------------------------------
VERIFY: every Kotlin connectivity node has a PC counterpart?

STATE fields (vm.state -> PC State)
   0/0 Kotlin state have a PC counterpart

ACTIONS/derived (vm methods -> PC methods)
   [GAP] toggleFavorite           -> (* no PC counterpart *)
   [GAP] duplicate                -> (* no PC counterpart *)
   [GAP] editCurrent              -> (* no PC counterpart *)
   [GAP] delete                   -> (* no PC counterpart *)
   [GAP] onToggleExcluded         -> (* no PC counterpart *)
   [GAP] confirmSwapNow           -> (* no PC counterpart *)
   [GAP] confirmSwapLater         -> (* no PC counterpart *)
   [GAP] dismissExcludePrompt     -> (* no PC counterpart *)
   0/8 Kotlin actions/derived have a PC counterpart

SCREEN->vm action edges (screen calls the action)
   [GAP] confirmSwapLater         -> (* no PC counterpart *)
   [GAP] confirmSwapNow           -> (* no PC counterpart *)
   [GAP] delete                   -> (* no PC counterpart *)
   [GAP] dismissExcludePrompt     -> (* no PC counterpart *)
   [GAP] duplicate                -> (* no PC counterpart *)
   [GAP] editCurrent              -> (* no PC counterpart *)
   [GAP] onToggleExcluded         -> (* no PC counterpart *)
   [OK ] toggleFavorite           -> toggle_favorite
   1/8 Kotlin screen->vm have a PC counterpart

========  CONNECTIVITY: 1/16 Kotlin edges preserved in PC  <-- GAPS ABOVE


======================================================================
CONNECTIVITY PROBE (static) -- exercise_picker
Kotlin VM is the reference; PC is verified against it.
======================================================================

Kotlin reference graph (ExercisePickerViewModel):
  state fields : exercises, query, muscleGroupFilter, showFavoritesOnly, isLoading
  derived      : 
  actions      : onQueryChange, setMuscleGroupFilter, toggleFavoritesOnly, toggleFavorite, pick
  screen reads : exercises, isLoading
  screen calls : onQueryChange, pick, setMuscleGroupFilter, toggleFavorite, toggleFavoritesOnly
  screen navs  : 

PseudoCoup side:
  State fields : query, muscle_group_filter, show_favorites_only
  methods      : exercises, on_query_change, set_muscle_group_filter, toggle_favorites_only, toggle_favorite, pick
  screen reads : muscle_group_filter, show_favorites_only
  screen calls : exercises, pick, set_muscle_group_filter, toggle_favorite, toggle_favorites_only
  screen navs  : program_day_editor

----------------------------------------------------------------------
VERIFY: every Kotlin connectivity node has a PC counterpart?

STATE fields (vm.state -> PC State)
   [GAP] exercises                -> (* no PC counterpart *)
   [OK ] query                    -> query
   [OK ] muscleGroupFilter        -> muscle_group_filter
   [OK ] showFavoritesOnly        -> show_favorites_only
   [GAP] isLoading                -> (* no PC counterpart *)
   3/5 Kotlin state have a PC counterpart

ACTIONS/derived (vm methods -> PC methods)
   [OK ] onQueryChange            -> on_query_change
   [OK ] setMuscleGroupFilter     -> set_muscle_group_filter
   [OK ] toggleFavoritesOnly      -> toggle_favorites_only
   [OK ] toggleFavorite           -> toggle_favorite
   [OK ] pick                     -> pick
   5/5 Kotlin actions/derived have a PC counterpart

SCREEN->vm action edges (screen calls the action)
   [GAP] onQueryChange            -> (* no PC counterpart *)
   [OK ] pick                     -> pick
   [OK ] setMuscleGroupFilter     -> set_muscle_group_filter
   [OK ] toggleFavorite           -> toggle_favorite
   [OK ] toggleFavoritesOnly      -> toggle_favorites_only
   4/5 Kotlin screen->vm have a PC counterpart

========  CONNECTIVITY: 12/15 Kotlin edges preserved in PC  <-- GAPS ABOVE


======================================================================
CONNECTIVITY PROBE (static) -- exercises
Kotlin VM is the reference; PC is verified against it.
======================================================================

Kotlin reference graph (ExercisesViewModel):
  state fields : sections, excluded, activeTab, query, isLoading
  derived      : isEmpty
  actions      : onTabChange, onQueryChange, toggleFavorite
  screen reads : excluded, isEmpty, isLoading, sections
  screen calls : onQueryChange, onTabChange, toggleFavorite
  screen navs  : 

PseudoCoup side:
  State fields : tab, query
  methods      : load, filtered, on_tab_change, on_query_change, toggle_favorite
  screen reads : tab
  screen calls : filtered, load, on_tab_change
  screen navs  : exercise_create, exercise_detail, you

----------------------------------------------------------------------
VERIFY: every Kotlin connectivity node has a PC counterpart?

STATE fields (vm.state -> PC State)
   [GAP] sections                 -> (* no PC counterpart *)
   [GAP] excluded                 -> (* no PC counterpart *)
   [GAP] activeTab                -> (* no PC counterpart *)
   [OK ] query                    -> query
   [GAP] isLoading                -> (* no PC counterpart *)
   1/5 Kotlin state have a PC counterpart

ACTIONS/derived (vm methods -> PC methods)
   [GAP] isEmpty                  -> (* no PC counterpart *)
   [OK ] onTabChange              -> on_tab_change
   [OK ] onQueryChange            -> on_query_change
   [OK ] toggleFavorite           -> toggle_favorite
   3/4 Kotlin actions/derived have a PC counterpart

SCREEN->vm action edges (screen calls the action)
   [GAP] onQueryChange            -> (* no PC counterpart *)
   [OK ] onTabChange              -> on_tab_change
   [GAP] toggleFavorite           -> (* no PC counterpart *)
   1/3 Kotlin screen->vm have a PC counterpart

========  CONNECTIVITY: 5/12 Kotlin edges preserved in PC  <-- GAPS ABOVE


======================================================================
CONNECTIVITY PROBE (static) -- gym_create_wizard
Kotlin VM is the reference; PC is verified against it.
======================================================================

Kotlin reference graph (GymCreateWizardViewModel):
  state fields : step, gymName, gymType, selectedEquipmentTypes, equipmentSearchQuery, weightUnit, isSaving, saved
  derived      : 
  actions      : setGymName, setGymType, setEquipmentSearch, toggleEquipment, filteredEquipment, next, back, saveGym
  screen reads : equipmentSearchQuery, gymName, gymType, isSaving, saved, selectedEquipmentTypes, step
  screen calls : back, filteredEquipment, next, setEquipmentSearch, setGymName, setGymType, toggleEquipment
  screen navs  : 

PseudoCoup side:
  State fields : step, gym_name, gym_type, selected_equipment, equipment_search_query
  methods      : set_gym_name, set_gym_type, set_equipment_search, toggle_equipment, is_equipment_selected, go_to_equipment, back, save_gym
  screen reads : gym_name, gym_type, selected_equipment, step
  screen calls : back, go_to_equipment, is_equipment_selected, save_gym, set_gym_name, set_gym_type, toggle_equipment
  screen navs  : gym_editor, gym_list

----------------------------------------------------------------------
VERIFY: every Kotlin connectivity node has a PC counterpart?

STATE fields (vm.state -> PC State)
   [OK ] step                     -> step
   [OK ] gymName                  -> gym_name
   [OK ] gymType                  -> gym_type
   [GAP] selectedEquipmentTypes   -> (* no PC counterpart *)
   [OK ] equipmentSearchQuery     -> equipment_search_query
   [GAP] weightUnit               -> (* no PC counterpart *)
   [GAP] isSaving                 -> (* no PC counterpart *)
   [GAP] saved                    -> (* no PC counterpart *)
   4/8 Kotlin state have a PC counterpart

ACTIONS/derived (vm methods -> PC methods)
   [OK ] setGymName               -> set_gym_name
   [OK ] setGymType               -> set_gym_type
   [OK ] setEquipmentSearch       -> set_equipment_search
   [OK ] toggleEquipment          -> toggle_equipment
   [GAP] filteredEquipment        -> (* no PC counterpart *)
   [GAP] next                     -> (* no PC counterpart *)
   [OK ] back                     -> back
   [OK ] saveGym                  -> save_gym
   6/8 Kotlin actions/derived have a PC counterpart

SCREEN->vm action edges (screen calls the action)
   [OK ] back                     -> back
   [GAP] filteredEquipment        -> (* no PC counterpart *)
   [GAP] next                     -> (* no PC counterpart *)
   [GAP] setEquipmentSearch       -> (* no PC counterpart *)
   [OK ] setGymName               -> set_gym_name
   [OK ] setGymType               -> set_gym_type
   [OK ] toggleEquipment          -> toggle_equipment
   4/7 Kotlin screen->vm have a PC counterpart

========  CONNECTIVITY: 14/23 Kotlin edges preserved in PC  <-- GAPS ABOVE


======================================================================
CONNECTIVITY PROBE (static) -- gym_editor
Kotlin VM is the reference; PC is verified against it.
======================================================================

Kotlin reference graph (GymEditorViewModel):
  state fields : isLoading, name, equipment, isSaving, saved
  derived      : 
  actions      : onNameChange, addEquipment, removeEquipment, save, toDraft
  screen reads : equipment, isLoading, isSaving, name, saved
  screen calls : addEquipment, onNameChange, removeEquipment, save
  screen navs  : 

PseudoCoup side:
  State fields : name, result
  methods      : load, is_new_gym, gym_id, equipment_for, on_name_change, save
  screen reads : name, result
  screen calls : equipment_for, gym_id, is_new_gym, load, save
  screen navs  : gym_list

----------------------------------------------------------------------
VERIFY: every Kotlin connectivity node has a PC counterpart?

STATE fields (vm.state -> PC State)
   [GAP] isLoading                -> (* no PC counterpart *)
   [OK ] name                     -> name
   [GAP] equipment                -> (* no PC counterpart *)
   [GAP] isSaving                 -> (* no PC counterpart *)
   [GAP] saved                    -> (* no PC counterpart *)
   1/5 Kotlin state have a PC counterpart

ACTIONS/derived (vm methods -> PC methods)
   [OK ] onNameChange             -> on_name_change
   [GAP] addEquipment             -> (* no PC counterpart *)
   [GAP] removeEquipment          -> (* no PC counterpart *)
   [OK ] save                     -> save
   [GAP] toDraft                  -> (* no PC counterpart *)
   2/5 Kotlin actions/derived have a PC counterpart

SCREEN->vm action edges (screen calls the action)
   [GAP] addEquipment             -> (* no PC counterpart *)
   [GAP] onNameChange             -> (* no PC counterpart *)
   [GAP] removeEquipment          -> (* no PC counterpart *)
   [OK ] save                     -> save
   1/4 Kotlin screen->vm have a PC counterpart

========  CONNECTIVITY: 4/14 Kotlin edges preserved in PC  <-- GAPS ABOVE


======================================================================
CONNECTIVITY PROBE (static) -- gym_list
Kotlin VM is the reference; PC is verified against it.
======================================================================

Kotlin reference graph (GymListViewModel):
  state fields : 
  derived      : 
  actions      : setActive, delete
  screen reads : 
  screen calls : delete, setActive
  screen navs  : 

PseudoCoup side:
  State fields : 
  methods      : gyms, equipment_for, set_active, delete
  screen reads : 
  screen calls : delete, equipment_for, gyms, set_active
  screen navs  : gym_create_wizard, gym_editor, you

----------------------------------------------------------------------
VERIFY: every Kotlin connectivity node has a PC counterpart?

STATE fields (vm.state -> PC State)
   0/0 Kotlin state have a PC counterpart

ACTIONS/derived (vm methods -> PC methods)
   [OK ] setActive                -> set_active
   [OK ] delete                   -> delete
   2/2 Kotlin actions/derived have a PC counterpart

SCREEN->vm action edges (screen calls the action)
   [OK ] delete                   -> delete
   [OK ] setActive                -> set_active
   2/2 Kotlin screen->vm have a PC counterpart

========  CONNECTIVITY: 4/4 Kotlin edges preserved in PC  (FULLY CONNECTED)


======================================================================
CONNECTIVITY PROBE (static) -- log_cardio
Kotlin VM is the reference; PC is verified against it.
======================================================================

Kotlin reference graph (LogCardioViewModel):
  state fields : type, selectedDate, today, durationText, intensity, distanceText, avgHrText, notes, saving, duplicateCandidate, done
  derived      : durationMinutes, canSave
  actions      : onTypeChange, onDateChange, onDurationChange, onIntensityChange, onDistanceChange, onAvgHrChange, onNotesChange, onSave, onConfirmSaveAnyway, onDiscardAsDuplicate, onDismissDuplicate, commit, startedAtFor
  screen reads : avgHrText, canSave, distanceText, done, duplicateCandidate, durationText, intensity, notes, saving, selectedDate, today, type
  screen calls : onAvgHrChange, onConfirmSaveAnyway, onDateChange, onDiscardAsDuplicate, onDismissDuplicate, onDistanceChange, onDurationChange, onIntensityChange, onNotesChange, onSave, onTypeChange
  screen navs  : 

PseudoCoup side:
  State fields : type, intensity, result
  methods      : on_type_change, on_intensity_change, save
  screen reads : intensity, result, type
  screen calls : on_intensity_change, on_type_change, save
  screen navs  : you

----------------------------------------------------------------------
VERIFY: every Kotlin connectivity node has a PC counterpart?

STATE fields (vm.state -> PC State)
   [OK ] type                     -> type
   [GAP] selectedDate             -> (* no PC counterpart *)
   [GAP] today                    -> (* no PC counterpart *)
   [GAP] durationText             -> (* no PC counterpart *)
   [OK ] intensity                -> intensity
   [GAP] distanceText             -> (* no PC counterpart *)
   [GAP] avgHrText                -> (* no PC counterpart *)
   [GAP] notes                    -> (* no PC counterpart *)
   [GAP] saving                   -> (* no PC counterpart *)
   [GAP] duplicateCandidate       -> (* no PC counterpart *)
   [GAP] done                     -> (* no PC counterpart *)
   2/11 Kotlin state have a PC counterpart

ACTIONS/derived (vm methods -> PC methods)
   [GAP] durationMinutes          -> (* no PC counterpart *)
   [GAP] canSave                  -> (* no PC counterpart *)
   [OK ] onTypeChange             -> on_type_change
   [GAP] onDateChange             -> (* no PC counterpart *)
   [GAP] onDurationChange         -> (* no PC counterpart *)
   [OK ] onIntensityChange        -> on_intensity_change
   [GAP] onDistanceChange         -> (* no PC counterpart *)
   [GAP] onAvgHrChange            -> (* no PC counterpart *)
   [GAP] onNotesChange            -> (* no PC counterpart *)
   [GAP] onSave                   -> (* no PC counterpart *)
   [GAP] onConfirmSaveAnyway      -> (* no PC counterpart *)
   [GAP] onDiscardAsDuplicate     -> (* no PC counterpart *)
   [GAP] onDismissDuplicate       -> (* no PC counterpart *)
   [GAP] commit                   -> (* no PC counterpart *)
   [GAP] startedAtFor             -> (* no PC counterpart *)
   2/15 Kotlin actions/derived have a PC counterpart

SCREEN->vm action edges (screen calls the action)
   [GAP] onAvgHrChange            -> (* no PC counterpart *)
   [GAP] onConfirmSaveAnyway      -> (* no PC counterpart *)
   [GAP] onDateChange             -> (* no PC counterpart *)
   [GAP] onDiscardAsDuplicate     -> (* no PC counterpart *)
   [GAP] onDismissDuplicate       -> (* no PC counterpart *)
   [GAP] onDistanceChange         -> (* no PC counterpart *)
   [GAP] onDurationChange         -> (* no PC counterpart *)
   [OK ] onIntensityChange        -> on_intensity_change
   [GAP] onNotesChange            -> (* no PC counterpart *)
   [GAP] onSave                   -> (* no PC counterpart *)
   [OK ] onTypeChange             -> on_type_change
   2/11 Kotlin screen->vm have a PC counterpart

========  CONNECTIVITY: 6/37 Kotlin edges preserved in PC  <-- GAPS ABOVE


======================================================================
CONNECTIVITY PROBE (static) -- my_program
Kotlin VM is the reference; PC is verified against it.
======================================================================

Kotlin reference graph (MyProgramViewModel):
  state fields : 
  derived      : 
  actions      : resolveLifeEvent, extendLifeEvent, shortenLifeEvent, changeLifeEventMode, resolveInjury, resolveDirective, toggleWeekExpansion, showDayExercises, dismissDayPopup, buildRoadmap, weekComplete, phaseTitle, microTypeLabel, weeksLabel
  screen reads : 
  screen calls : changeLifeEventMode, dismissDayPopup, extendLifeEvent, resolveDirective, resolveInjury, resolveLifeEvent, shortenLifeEvent, showDayExercises
  screen navs  : 

PseudoCoup side:
  State fields : selected_day_id, show_adaptations, menu_open
  methods      : load, enrolled, active_life_events, active_injuries, active_directives, show_day, dismiss_day, open_adaptations, close_adaptations, toggle_menu, close_menu
  screen reads : menu_open, selected_day_id, show_adaptations
  screen calls : active_directives, active_injuries, active_life_events, close_adaptations, close_menu, dismiss_day, enrolled, load, open_adaptations, show_day, toggle_menu
  screen navs  : programs, update_program

----------------------------------------------------------------------
VERIFY: every Kotlin connectivity node has a PC counterpart?

STATE fields (vm.state -> PC State)
   0/0 Kotlin state have a PC counterpart

ACTIONS/derived (vm methods -> PC methods)
   [GAP] resolveLifeEvent         -> (* no PC counterpart *)
   [GAP] extendLifeEvent          -> (* no PC counterpart *)
   [GAP] shortenLifeEvent         -> (* no PC counterpart *)
   [GAP] changeLifeEventMode      -> (* no PC counterpart *)
   [GAP] resolveInjury            -> (* no PC counterpart *)
   [GAP] resolveDirective         -> (* no PC counterpart *)
   [GAP] toggleWeekExpansion      -> (* no PC counterpart *)
   [GAP] showDayExercises         -> (* no PC counterpart *)
   [GAP] dismissDayPopup          -> (* no PC counterpart *)
   [GAP] buildRoadmap             -> (* no PC counterpart *)
   [GAP] weekComplete             -> (* no PC counterpart *)
   [GAP] phaseTitle               -> (* no PC counterpart *)
   [GAP] microTypeLabel           -> (* no PC counterpart *)
   [GAP] weeksLabel               -> (* no PC counterpart *)
   0/14 Kotlin actions/derived have a PC counterpart

SCREEN->vm action edges (screen calls the action)
   [GAP] changeLifeEventMode      -> (* no PC counterpart *)
   [GAP] dismissDayPopup          -> (* no PC counterpart *)
   [GAP] extendLifeEvent          -> (* no PC counterpart *)
   [GAP] resolveDirective         -> (* no PC counterpart *)
   [GAP] resolveInjury            -> (* no PC counterpart *)
   [GAP] resolveLifeEvent         -> (* no PC counterpart *)
   [GAP] shortenLifeEvent         -> (* no PC counterpart *)
   [GAP] showDayExercises         -> (* no PC counterpart *)
   0/8 Kotlin screen->vm have a PC counterpart

========  CONNECTIVITY: 0/22 Kotlin edges preserved in PC  <-- GAPS ABOVE


======================================================================
CONNECTIVITY PROBE (static) -- onboarding
Kotlin VM is the reference; PC is verified against it.
======================================================================

Kotlin reference graph (OnboardingViewModel):
  state fields : 
  derived      : 
  actions      : runResilient, next, back, skipGymSetup, setName, setExperience, skipExperience, setTrainingRecency, skipTrainingStatus, setWeightUnit, setBodyWeightInput, setStrengthGainProfile, skipStartingStrength, setCalibrationMode, setCalibrationWeight, skipCalibration, continueFromCalibration, saveCalibration, calibrationRepsRir, setGymName, setGymType, toggleEquipment, setEquipmentSearch, setPath, setProgram, completeOnboarding, persistOnboarding, filteredEquipment
  screen reads : bodyWeightInput, calibrationInputs, calibrationMode, calibrationOutcomes, displayName, equipmentSearchQuery, gymName, gymType, isSaving, selectedEquipmentTypes, selectedPathId, selectedProgramId, step, strengthGainProfile, trainingExperience, trainingRecency, weightUnit
  screen calls : back, completeOnboarding, continueFromCalibration, filteredEquipment, next, saveCalibration, setBodyWeightInput, setCalibrationMode, setCalibrationWeight, setEquipmentSearch, setExperience, setGymName, setGymType, setName, setPath, setProgram, setStrengthGainProfile, setTrainingRecency, setWeightUnit, skipCalibration, skipExperience, skipGymSetup, skipStartingStrength, skipTrainingStatus, toggleEquipment
  screen navs  : 

PseudoCoup side:
  State fields : step, display_name, selected_path_id
  methods      : load, set_name, set_path, next, back
  screen reads : display_name, selected_path_id, step
  screen calls : load, next, set_name, set_path
  screen navs  : today

----------------------------------------------------------------------
VERIFY: every Kotlin connectivity node has a PC counterpart?

STATE fields (vm.state -> PC State)
   0/0 Kotlin state have a PC counterpart

ACTIONS/derived (vm methods -> PC methods)
   [GAP] runResilient             -> (* no PC counterpart *)
   [OK ] next                     -> next
   [OK ] back                     -> back
   [GAP] skipGymSetup             -> (* no PC counterpart *)
   [OK ] setName                  -> set_name
   [GAP] setExperience            -> (* no PC counterpart *)
   [GAP] skipExperience           -> (* no PC counterpart *)
   [GAP] setTrainingRecency       -> (* no PC counterpart *)
   [GAP] skipTrainingStatus       -> (* no PC counterpart *)
   [GAP] setWeightUnit            -> (* no PC counterpart *)
   [GAP] setBodyWeightInput       -> (* no PC counterpart *)
   [GAP] setStrengthGainProfile   -> (* no PC counterpart *)
   [GAP] skipStartingStrength     -> (* no PC counterpart *)
   [GAP] setCalibrationMode       -> (* no PC counterpart *)
   [GAP] setCalibrationWeight     -> (* no PC counterpart *)
   [GAP] skipCalibration          -> (* no PC counterpart *)
   [GAP] continueFromCalibration  -> (* no PC counterpart *)
   [GAP] saveCalibration          -> (* no PC counterpart *)
   [GAP] calibrationRepsRir       -> (* no PC counterpart *)
   [GAP] setGymName               -> (* no PC counterpart *)
   [GAP] setGymType               -> (* no PC counterpart *)
   [GAP] toggleEquipment          -> (* no PC counterpart *)
   [GAP] setEquipmentSearch       -> (* no PC counterpart *)
   [OK ] setPath                  -> set_path
   [GAP] setProgram               -> (* no PC counterpart *)
   [GAP] completeOnboarding       -> (* no PC counterpart *)
   [GAP] persistOnboarding        -> (* no PC counterpart *)
   [GAP] filteredEquipment        -> (* no PC counterpart *)
   4/28 Kotlin actions/derived have a PC counterpart

SCREEN->vm action edges (screen calls the action)
   [GAP] back                     -> (* no PC counterpart *)
   [GAP] completeOnboarding       -> (* no PC counterpart *)
   [GAP] continueFromCalibration  -> (* no PC counterpart *)
   [GAP] filteredEquipment        -> (* no PC counterpart *)
   [OK ] next                     -> next
   [GAP] saveCalibration          -> (* no PC counterpart *)
   [GAP] setBodyWeightInput       -> (* no PC counterpart *)
   [GAP] setCalibrationMode       -> (* no PC counterpart *)
   [GAP] setCalibrationWeight     -> (* no PC counterpart *)
   [GAP] setEquipmentSearch       -> (* no PC counterpart *)
   [GAP] setExperience            -> (* no PC counterpart *)
   [GAP] setGymName               -> (* no PC counterpart *)
   [GAP] setGymType               -> (* no PC counterpart *)
   [OK ] setName                  -> set_name
   [OK ] setPath                  -> set_path
   [GAP] setProgram               -> (* no PC counterpart *)
   [GAP] setStrengthGainProfile   -> (* no PC counterpart *)
   [GAP] setTrainingRecency       -> (* no PC counterpart *)
   [GAP] setWeightUnit            -> (* no PC counterpart *)
   [GAP] skipCalibration          -> (* no PC counterpart *)
   [GAP] skipExperience           -> (* no PC counterpart *)
   [GAP] skipGymSetup             -> (* no PC counterpart *)
   [GAP] skipStartingStrength     -> (* no PC counterpart *)
   [GAP] skipTrainingStatus       -> (* no PC counterpart *)
   [GAP] toggleEquipment          -> (* no PC counterpart *)
   3/25 Kotlin screen->vm have a PC counterpart

========  CONNECTIVITY: 7/53 Kotlin edges preserved in PC  <-- GAPS ABOVE


======================================================================
CONNECTIVITY PROBE (static) -- paths
Kotlin VM is the reference; PC is verified against it.
======================================================================

Kotlin reference graph (PathsViewModel):
  state fields : 
  derived      : 
  actions      : startPicker, startAddSecond, dismissPicker, togglePathSelection, setCustomName, enrollAndFinish, unenroll
  screen reads : 
  screen calls : dismissPicker, enrollAndFinish, setCustomName, startAddSecond, startPicker, togglePathSelection, unenroll
  screen navs  : 

PseudoCoup side:
  State fields : picker_open
  methods      : active_paths, start_picker, dismiss_picker, unenroll
  screen reads : picker_open
  screen calls : active_paths, dismiss_picker, start_picker, unenroll
  screen navs  : path_detail, paths

----------------------------------------------------------------------
VERIFY: every Kotlin connectivity node has a PC counterpart?

STATE fields (vm.state -> PC State)
   0/0 Kotlin state have a PC counterpart

ACTIONS/derived (vm methods -> PC methods)
   [OK ] startPicker              -> start_picker
   [GAP] startAddSecond           -> (* no PC counterpart *)
   [OK ] dismissPicker            -> dismiss_picker
   [GAP] togglePathSelection      -> (* no PC counterpart *)
   [GAP] setCustomName            -> (* no PC counterpart *)
   [GAP] enrollAndFinish          -> (* no PC counterpart *)
   [OK ] unenroll                 -> unenroll
   3/7 Kotlin actions/derived have a PC counterpart

SCREEN->vm action edges (screen calls the action)
   [OK ] dismissPicker            -> dismiss_picker
   [GAP] enrollAndFinish          -> (* no PC counterpart *)
   [GAP] setCustomName            -> (* no PC counterpart *)
   [GAP] startAddSecond           -> (* no PC counterpart *)
   [OK ] startPicker              -> start_picker
   [GAP] togglePathSelection      -> (* no PC counterpart *)
   [OK ] unenroll                 -> unenroll
   3/7 Kotlin screen->vm have a PC counterpart

========  CONNECTIVITY: 6/14 Kotlin edges preserved in PC  <-- GAPS ABOVE


======================================================================
CONNECTIVITY PROBE (static) -- program_day_editor
Kotlin VM is the reference; PC is verified against it.
======================================================================

Kotlin reference graph (ProgramDayEditorViewModel):
  state fields : day, exerciseGroups, workoutMode, weightUnit, isReadOnly, isLoading
  derived      : 
  actions      : openExercisePicker, startEditPrescription, dismissPrescriptionEditor, savePrescription, moveUp, moveDown, groupWithNext, removeFromSuperset, requestDelete, dismissDelete, confirmDelete, toExerciseGroups
  screen reads : day, exerciseGroups, isLoading, isReadOnly, weightUnit, workoutMode
  screen calls : confirmDelete, dismissDelete, dismissPrescriptionEditor, groupWithNext, moveDown, moveUp, openExercisePicker, removeFromSuperset, requestDelete, savePrescription, startEditPrescription
  screen navs  : 

PseudoCoup side:
  State fields : editing_pe_id, delete_confirm_id, menu_pe_id
  methods      : load, day_id, day, exercises_for_day, start_edit, dismiss_edit, request_delete, dismiss_delete, open_menu, close_menu, save_prescription, move_exercise, group_with_next, remove_from_superset, confirm_delete
  screen reads : delete_confirm_id, editing_pe_id, menu_pe_id
  screen calls : close_menu, confirm_delete, day, dismiss_delete, dismiss_edit, exercises_for_day, group_with_next, load, move_exercise, open_menu, remove_from_superset, request_delete, save_prescription, start_edit
  screen navs  : exercise_picker, program_editor

----------------------------------------------------------------------
VERIFY: every Kotlin connectivity node has a PC counterpart?

STATE fields (vm.state -> PC State)
   [GAP] day                      -> (* no PC counterpart *)
   [GAP] exerciseGroups           -> (* no PC counterpart *)
   [GAP] workoutMode              -> (* no PC counterpart *)
   [GAP] weightUnit               -> (* no PC counterpart *)
   [GAP] isReadOnly               -> (* no PC counterpart *)
   [GAP] isLoading                -> (* no PC counterpart *)
   0/6 Kotlin state have a PC counterpart

ACTIONS/derived (vm methods -> PC methods)
   [GAP] openExercisePicker       -> (* no PC counterpart *)
   [GAP] startEditPrescription    -> (* no PC counterpart *)
   [GAP] dismissPrescriptionEditor -> (* no PC counterpart *)
   [OK ] savePrescription         -> save_prescription
   [GAP] moveUp                   -> (* no PC counterpart *)
   [GAP] moveDown                 -> (* no PC counterpart *)
   [OK ] groupWithNext            -> group_with_next
   [OK ] removeFromSuperset       -> remove_from_superset
   [OK ] requestDelete            -> request_delete
   [OK ] dismissDelete            -> dismiss_delete
   [OK ] confirmDelete            -> confirm_delete
   [GAP] toExerciseGroups         -> (* no PC counterpart *)
   6/12 Kotlin actions/derived have a PC counterpart

SCREEN->vm action edges (screen calls the action)
   [OK ] confirmDelete            -> confirm_delete
   [OK ] dismissDelete            -> dismiss_delete
   [GAP] dismissPrescriptionEditor -> (* no PC counterpart *)
   [OK ] groupWithNext            -> group_with_next
   [GAP] moveDown                 -> (* no PC counterpart *)
   [GAP] moveUp                   -> (* no PC counterpart *)
   [GAP] openExercisePicker       -> (* no PC counterpart *)
   [OK ] removeFromSuperset       -> remove_from_superset
   [OK ] requestDelete            -> request_delete
   [OK ] savePrescription         -> save_prescription
   [GAP] startEditPrescription    -> (* no PC counterpart *)
   6/11 Kotlin screen->vm have a PC counterpart

========  CONNECTIVITY: 12/29 Kotlin edges preserved in PC  <-- GAPS ABOVE


======================================================================
CONNECTIVITY PROBE (static) -- program_editor
Kotlin VM is the reference; PC is verified against it.
======================================================================

Kotlin reference graph (ProgramEditorViewModel):
  state fields : program, roadmap, contextualGuidance, isReadOnly, isOnMyOwnJourney, isLoading
  derived      : 
  actions      : onNameChange, onDescriptionChange, togglePath, joinProgram, duplicateProgram, requestSwap, confirmSwap, dismissSwap, addWeek, showAddDayDialog, dismissAddDayDialog, addDay, requestDeleteWeek, dismissDeleteWeek, confirmDeleteWeek, requestDeleteDay, dismissDeleteDay, confirmDeleteDay, navigateToDay, toggleWeekExpansion, showDayExercises, dismissDayPopup
  screen reads : contextualGuidance, isLoading, isOnMyOwnJourney, isReadOnly, program, roadmap
  screen calls : addDay, addWeek, confirmDeleteDay, confirmDeleteWeek, confirmSwap, dismissAddDayDialog, dismissDayPopup, dismissDeleteDay, dismissDeleteWeek, dismissSwap, duplicateProgram, joinProgram, navigateToDay, onDescriptionChange, onNameChange, requestSwap, showDayExercises, togglePath, toggleWeekExpansion
  screen navs  : 

PseudoCoup side:
  State fields : name, description, selected_path_ids, add_day_week_id, show_swap_confirm, selected_day_id, delete_week_confirm_id, delete_day_confirm_id
  methods      : load, program_id, program, microcycles_for_program, days_for_microcycle, day_by_id, on_name_change, on_description_change, commit_name, commit_description, toggle_path, join_program, request_swap, dismiss_swap, confirm_swap, add_week, show_add_day_dialog, dismiss_add_day_dialog, add_day, request_delete_week, dismiss_delete_week, confirm_delete_week, request_delete_day, dismiss_delete_day, confirm_delete_day, show_day_preview, dismiss_day_preview
  screen reads : add_day_week_id, description, name, selected_day_id, selected_path_ids, show_swap_confirm
  screen calls : add_day, add_week, confirm_swap, day_by_id, days_for_microcycle, dismiss_add_day_dialog, dismiss_day_preview, dismiss_swap, load, microcycles_for_program, program, request_swap
  screen navs  : program_day_editor, programs

----------------------------------------------------------------------
VERIFY: every Kotlin connectivity node has a PC counterpart?

STATE fields (vm.state -> PC State)
   [GAP] program                  -> (* no PC counterpart *)
   [GAP] roadmap                  -> (* no PC counterpart *)
   [GAP] contextualGuidance       -> (* no PC counterpart *)
   [GAP] isReadOnly               -> (* no PC counterpart *)
   [GAP] isOnMyOwnJourney         -> (* no PC counterpart *)
   [GAP] isLoading                -> (* no PC counterpart *)
   0/6 Kotlin state have a PC counterpart

ACTIONS/derived (vm methods -> PC methods)
   [OK ] onNameChange             -> on_name_change
   [OK ] onDescriptionChange      -> on_description_change
   [OK ] togglePath               -> toggle_path
   [OK ] joinProgram              -> join_program
   [GAP] duplicateProgram         -> (* no PC counterpart *)
   [OK ] requestSwap              -> request_swap
   [OK ] confirmSwap              -> confirm_swap
   [OK ] dismissSwap              -> dismiss_swap
   [OK ] addWeek                  -> add_week
   [OK ] showAddDayDialog         -> show_add_day_dialog
   [OK ] dismissAddDayDialog      -> dismiss_add_day_dialog
   [OK ] addDay                   -> add_day
   [OK ] requestDeleteWeek        -> request_delete_week
   [OK ] dismissDeleteWeek        -> dismiss_delete_week
   [OK ] confirmDeleteWeek        -> confirm_delete_week
   [OK ] requestDeleteDay         -> request_delete_day
   [OK ] dismissDeleteDay         -> dismiss_delete_day
   [OK ] confirmDeleteDay         -> confirm_delete_day
   [GAP] navigateToDay            -> (* no PC counterpart *)
   [GAP] toggleWeekExpansion      -> (* no PC counterpart *)
   [GAP] showDayExercises         -> (* no PC counterpart *)
   [GAP] dismissDayPopup          -> (* no PC counterpart *)
   17/22 Kotlin actions/derived have a PC counterpart

SCREEN->vm action edges (screen calls the action)
   [OK ] addDay                   -> add_day
   [OK ] addWeek                  -> add_week
   [GAP] confirmDeleteDay         -> (* no PC counterpart *)
   [GAP] confirmDeleteWeek        -> (* no PC counterpart *)
   [OK ] confirmSwap              -> confirm_swap
   [OK ] dismissAddDayDialog      -> dismiss_add_day_dialog
   [GAP] dismissDayPopup          -> (* no PC counterpart *)
   [GAP] dismissDeleteDay         -> (* no PC counterpart *)
   [GAP] dismissDeleteWeek        -> (* no PC counterpart *)
   [OK ] dismissSwap              -> dismiss_swap
   [GAP] duplicateProgram         -> (* no PC counterpart *)
   [GAP] joinProgram              -> (* no PC counterpart *)
   [GAP] navigateToDay            -> (* no PC counterpart *)
   [GAP] onDescriptionChange      -> (* no PC counterpart *)
   [GAP] onNameChange             -> (* no PC counterpart *)
   [OK ] requestSwap              -> request_swap
   [GAP] showDayExercises         -> (* no PC counterpart *)
   [GAP] togglePath               -> (* no PC counterpart *)
   [GAP] toggleWeekExpansion      -> (* no PC counterpart *)
   6/19 Kotlin screen->vm have a PC counterpart

========  CONNECTIVITY: 23/47 Kotlin edges preserved in PC  <-- GAPS ABOVE


======================================================================
CONNECTIVITY PROBE (static) -- programs
Kotlin VM is the reference; PC is verified against it.
======================================================================

Kotlin reference graph (ProgramsViewModel):
  state fields : recommendedPrograms, otherPrograms, enrolledProgramId, hasActivePaths, isOnMyOwnJourney, isLoading
  derived      : 
  actions      : openCreateDialog, dismissCreateDialog, createProgram, enrollProgram, requestSwap, confirmSwap, dismissSwap, duplicateProgram, archiveProgram, requestDelete, dismissDelete, confirmDelete
  screen reads : enrolledProgramId, hasActivePaths, isLoading, isOnMyOwnJourney, otherPrograms, recommendedPrograms
  screen calls : archiveProgram, confirmDelete, confirmSwap, createProgram, dismissCreateDialog, dismissDelete, dismissSwap, duplicateProgram, enrollProgram, openCreateDialog, requestDelete, requestSwap
  screen navs  : 

PseudoCoup side:
  State fields : show_create, delete_confirm_id, swap_confirm_id, menu_prog_id
  methods      : load, all_programs, enrolled, active_paths, is_recommended, open_create_dialog, dismiss_create_dialog, close_after_create, open_menu, close_menu, enroll_program, archive_program, request_delete, dismiss_delete, confirm_delete, request_swap, dismiss_swap, confirm_swap
  screen reads : delete_confirm_id, menu_prog_id, show_create, swap_confirm_id
  screen calls : active_paths, all_programs, archive_program, close_after_create, close_menu, confirm_delete, confirm_swap, dismiss_create_dialog, dismiss_delete, dismiss_swap, enroll_program, enrolled, is_recommended, load, open_create_dialog, open_menu, request_delete, request_swap
  screen navs  : program, program_editor

----------------------------------------------------------------------
VERIFY: every Kotlin connectivity node has a PC counterpart?

STATE fields (vm.state -> PC State)
   [GAP] recommendedPrograms      -> (* no PC counterpart *)
   [GAP] otherPrograms            -> (* no PC counterpart *)
   [GAP] enrolledProgramId        -> (* no PC counterpart *)
   [GAP] hasActivePaths           -> (* no PC counterpart *)
   [GAP] isOnMyOwnJourney         -> (* no PC counterpart *)
   [GAP] isLoading                -> (* no PC counterpart *)
   0/6 Kotlin state have a PC counterpart

ACTIONS/derived (vm methods -> PC methods)
   [OK ] openCreateDialog         -> open_create_dialog
   [OK ] dismissCreateDialog      -> dismiss_create_dialog
   [GAP] createProgram            -> (* no PC counterpart *)
   [OK ] enrollProgram            -> enroll_program
   [OK ] requestSwap              -> request_swap
   [OK ] confirmSwap              -> confirm_swap
   [OK ] dismissSwap              -> dismiss_swap
   [GAP] duplicateProgram         -> (* no PC counterpart *)
   [OK ] archiveProgram           -> archive_program
   [OK ] requestDelete            -> request_delete
   [OK ] dismissDelete            -> dismiss_delete
   [OK ] confirmDelete            -> confirm_delete
   10/12 Kotlin actions/derived have a PC counterpart

SCREEN->vm action edges (screen calls the action)
   [OK ] archiveProgram           -> archive_program
   [OK ] confirmDelete            -> confirm_delete
   [OK ] confirmSwap              -> confirm_swap
   [GAP] createProgram            -> (* no PC counterpart *)
   [OK ] dismissCreateDialog      -> dismiss_create_dialog
   [OK ] dismissDelete            -> dismiss_delete
   [OK ] dismissSwap              -> dismiss_swap
   [GAP] duplicateProgram         -> (* no PC counterpart *)
   [OK ] enrollProgram            -> enroll_program
   [OK ] openCreateDialog         -> open_create_dialog
   [OK ] requestDelete            -> request_delete
   [OK ] requestSwap              -> request_swap
   10/12 Kotlin screen->vm have a PC counterpart

========  CONNECTIVITY: 20/30 Kotlin edges preserved in PC  <-- GAPS ABOVE


======================================================================
CONNECTIVITY PROBE (static) -- progress
Kotlin VM is the reference; PC is verified against it.
======================================================================

Kotlin reference graph (ProgressViewModel):
  state fields : isLoading, tonnage7dKg, tonnagePrev7dKg, tonnage30dKg, muscleVolume7d, muscleVolume30d, volumeWindow, bests, strengthScore, activeMinutes7d, activeMinutes30d, displayUnit, selectedTab, checkInMoodStat
  derived      : muscleVolume
  actions      : computeStrengthScore, selectTab, selectVolumeWindow, muscleVolumeFlow
  screen reads : activeMinutes30d, activeMinutes7d, bests, checkInMoodStat, displayUnit, isLoading, muscleVolume, muscleVolume30d, muscleVolume7d, selectedTab, strengthScore, tonnage30dKg, tonnage7dKg, tonnagePrev7dKg, volumeWindow
  screen calls : selectTab, selectVolumeWindow
  screen navs  : 

PseudoCoup side:
  State fields : tab
  methods      : load, select_tab, wins_count, bests, sessions, cardio, program_day
  screen reads : tab
  screen calls : bests, cardio, load, program_day, select_tab, sessions, wins_count
  screen navs  : session_detail, wins

----------------------------------------------------------------------
VERIFY: every Kotlin connectivity node has a PC counterpart?

STATE fields (vm.state -> PC State)
   [GAP] isLoading                -> (* no PC counterpart *)
   [GAP] tonnage7dKg              -> (* no PC counterpart *)
   [GAP] tonnagePrev7dKg          -> (* no PC counterpart *)
   [GAP] tonnage30dKg             -> (* no PC counterpart *)
   [GAP] muscleVolume7d           -> (* no PC counterpart *)
   [GAP] muscleVolume30d          -> (* no PC counterpart *)
   [GAP] volumeWindow             -> (* no PC counterpart *)
   [GAP] bests                    -> (* no PC counterpart *)
   [GAP] strengthScore            -> (* no PC counterpart *)
   [GAP] activeMinutes7d          -> (* no PC counterpart *)
   [GAP] activeMinutes30d         -> (* no PC counterpart *)
   [GAP] displayUnit              -> (* no PC counterpart *)
   [GAP] selectedTab              -> (* no PC counterpart *)
   [GAP] checkInMoodStat          -> (* no PC counterpart *)
   0/14 Kotlin state have a PC counterpart

ACTIONS/derived (vm methods -> PC methods)
   [GAP] muscleVolume             -> (* no PC counterpart *)
   [GAP] computeStrengthScore     -> (* no PC counterpart *)
   [OK ] selectTab                -> select_tab
   [GAP] selectVolumeWindow       -> (* no PC counterpart *)
   [GAP] muscleVolumeFlow         -> (* no PC counterpart *)
   1/5 Kotlin actions/derived have a PC counterpart

SCREEN->vm action edges (screen calls the action)
   [OK ] selectTab                -> select_tab
   [GAP] selectVolumeWindow       -> (* no PC counterpart *)
   1/2 Kotlin screen->vm have a PC counterpart

========  CONNECTIVITY: 2/21 Kotlin edges preserved in PC  <-- GAPS ABOVE


======================================================================
CONNECTIVITY PROBE (static) -- report_bug
Kotlin VM is the reference; PC is verified against it.
======================================================================

Kotlin reference graph (ReportBugViewModel):
  state fields : description, severity, reporterName, includesCrash, submission
  derived      : canSubmit
  actions      : onDescriptionChange, onSeverityChange, onReporterNameChange, submit, resetSubmission
  screen reads : canSubmit, description, includesCrash, reporterName, severity, submission
  screen calls : onDescriptionChange, onReporterNameChange, onSeverityChange, resetSubmission, submit
  screen navs  : 

PseudoCoup side:
  State fields : description, severity, reporter_name, includes_crash, submission, submission_error
  methods      : load, can_submit, on_description_change, on_severity_change, on_reporter_name_change, submit, reset_submission
  screen reads : description, reporter_name, severity, submission
  screen calls : load, on_description_change, on_severity_change, submit
  screen navs  : you

----------------------------------------------------------------------
VERIFY: every Kotlin connectivity node has a PC counterpart?

STATE fields (vm.state -> PC State)
   [OK ] description              -> description
   [OK ] severity                 -> severity
   [OK ] reporterName             -> reporter_name
   [OK ] includesCrash            -> includes_crash
   [OK ] submission               -> submission
   5/5 Kotlin state have a PC counterpart

ACTIONS/derived (vm methods -> PC methods)
   [OK ] canSubmit                -> can_submit
   [OK ] onDescriptionChange      -> on_description_change
   [OK ] onSeverityChange         -> on_severity_change
   [OK ] onReporterNameChange     -> on_reporter_name_change
   [OK ] submit                   -> submit
   [OK ] resetSubmission          -> reset_submission
   6/6 Kotlin actions/derived have a PC counterpart

SCREEN->vm action edges (screen calls the action)
   [OK ] onDescriptionChange      -> on_description_change
   [GAP] onReporterNameChange     -> (* no PC counterpart *)
   [OK ] onSeverityChange         -> on_severity_change
   [GAP] resetSubmission          -> (* no PC counterpart *)
   [OK ] submit                   -> submit
   3/5 Kotlin screen->vm have a PC counterpart

========  CONNECTIVITY: 14/16 Kotlin edges preserved in PC  <-- GAPS ABOVE


======================================================================
CONNECTIVITY PROBE (static) -- session_detail
Kotlin VM is the reference; PC is verified against it.
======================================================================

Kotlin reference graph (SessionDetailViewModel):
  state fields : isLoading, startedAt, durationSeconds, programDayName, totalVolumeKg, exercises, prs, displayUnit, workoutMode
  derived      : 
  actions      : 
  screen reads : displayUnit, durationSeconds, exercises, isLoading, programDayName, prs, startedAt, totalVolumeKg, workoutMode
  screen calls : 
  screen navs  : 

PseudoCoup side:
  State fields : 
  methods      : load, session_id, has_session, session, program_day_name, session_exercises
  screen reads : 
  screen calls : load, program_day_name, session, session_exercises
  screen navs  : progress, session_detail

----------------------------------------------------------------------
VERIFY: every Kotlin connectivity node has a PC counterpart?

STATE fields (vm.state -> PC State)
   [GAP] isLoading                -> (* no PC counterpart *)
   [GAP] startedAt                -> (* no PC counterpart *)
   [GAP] durationSeconds          -> (* no PC counterpart *)
   [GAP] programDayName           -> (* no PC counterpart *)
   [GAP] totalVolumeKg            -> (* no PC counterpart *)
   [GAP] exercises                -> (* no PC counterpart *)
   [GAP] prs                      -> (* no PC counterpart *)
   [GAP] displayUnit              -> (* no PC counterpart *)
   [GAP] workoutMode              -> (* no PC counterpart *)
   0/9 Kotlin state have a PC counterpart

ACTIONS/derived (vm methods -> PC methods)
   0/0 Kotlin actions/derived have a PC counterpart

SCREEN->vm action edges (screen calls the action)
   0/0 Kotlin screen->vm have a PC counterpart

========  CONNECTIVITY: 0/9 Kotlin edges preserved in PC  <-- GAPS ABOVE


======================================================================
CONNECTIVITY PROBE (static) -- today
Kotlin VM is the reference; PC is verified against it.
======================================================================

Kotlin reference graph (TodayViewModel):
  state fields : isLoaded, displayName, weightUnit, weeklyRows, doneCount, totalCount, todayDayId, weekComplete, selectedDayId, selectedDayName, selectedIsRest, activeSession, activeSessionName, activePath, pathEncouragement, programFrequency, weeklyTonnageKg, monthlyTonnageKg, ytdTonnageKg, showPreCheckIn, checkInSleep, checkInEnergy, notificationPrefsEnabled, notificationItems, welcomeBackGapDays, quietStretchDays, deloadRecommendation, showGraduationPrompt
  derived      : weeklyItems
  actions      : workoutsDone, onDaySelected, showDayExercises, dismissDayPopup, onRestDaySelected, onStartTapped, onCheckInSleep, onCheckInEnergy, onCheckInDismiss, onCheckInComplete, onLogRestDay, swapWorkoutWithUpNext, resumeSession, onNewMobilitySession, onQuietStretchRest, dismissQuietStretch, dismissDeloadNudge, onAcceptDeload, onGraduateAccepted, dismissGraduationPrompt, onWelcomeBackTapped, onWelcomeBackDismissed, onWelcomeBackApply, buildEncouragement
  screen reads : activePath, activeSession, activeSessionName, checkInEnergy, checkInSleep, deloadRecommendation, doneCount, isLoaded, pathEncouragement, programFrequency, quietStretchDays, selectedDayId, selectedDayName, selectedIsRest, showGraduationPrompt, showPreCheckIn, totalCount, weekComplete, weeklyItems, weeklyRows, weightUnit, welcomeBackGapDays
  screen calls : dismissDayPopup, dismissDeloadNudge, dismissGraduationPrompt, dismissQuietStretch, onAcceptDeload, onCheckInComplete, onCheckInDismiss, onCheckInEnergy, onCheckInSleep, onDaySelected, onGraduateAccepted, onLogRestDay, onNewMobilitySession, onQuietStretchRest, onRestDaySelected, onStartTapped, onWelcomeBackApply, onWelcomeBackDismissed, onWelcomeBackTapped, resumeSession, showDayExercises
  screen navs  : 

PseudoCoup side:
  State fields : 
  methods      : load, enrolled, current_week_days, workout_total, exercise_count, week_days_done, first_active_path, path_encouragement
  screen reads : 
  screen calls : current_week_days, exercise_count, first_active_path, load, path_encouragement, week_days_done, workout_total
  screen navs  : workout_warmup

----------------------------------------------------------------------
VERIFY: every Kotlin connectivity node has a PC counterpart?

STATE fields (vm.state -> PC State)
   [GAP] isLoaded                 -> (* no PC counterpart *)
   [GAP] displayName              -> (* no PC counterpart *)
   [GAP] weightUnit               -> (* no PC counterpart *)
   [GAP] weeklyRows               -> (* no PC counterpart *)
   [GAP] doneCount                -> (* no PC counterpart *)
   [GAP] totalCount               -> (* no PC counterpart *)
   [GAP] todayDayId               -> (* no PC counterpart *)
   [GAP] weekComplete             -> (* no PC counterpart *)
   [GAP] selectedDayId            -> (* no PC counterpart *)
   [GAP] selectedDayName          -> (* no PC counterpart *)
   [GAP] selectedIsRest           -> (* no PC counterpart *)
   [GAP] activeSession            -> (* no PC counterpart *)
   [GAP] activeSessionName        -> (* no PC counterpart *)
   [GAP] activePath               -> (* no PC counterpart *)
   [GAP] pathEncouragement        -> (* no PC counterpart *)
   [GAP] programFrequency         -> (* no PC counterpart *)
   [GAP] weeklyTonnageKg          -> (* no PC counterpart *)
   [GAP] monthlyTonnageKg         -> (* no PC counterpart *)
   [GAP] ytdTonnageKg             -> (* no PC counterpart *)
   [GAP] showPreCheckIn           -> (* no PC counterpart *)
   [GAP] checkInSleep             -> (* no PC counterpart *)
   [GAP] checkInEnergy            -> (* no PC counterpart *)
   [GAP] notificationPrefsEnabled -> (* no PC counterpart *)
   [GAP] notificationItems        -> (* no PC counterpart *)
   [GAP] welcomeBackGapDays       -> (* no PC counterpart *)
   [GAP] quietStretchDays         -> (* no PC counterpart *)
   [GAP] deloadRecommendation     -> (* no PC counterpart *)
   [GAP] showGraduationPrompt     -> (* no PC counterpart *)
   0/28 Kotlin state have a PC counterpart

ACTIONS/derived (vm methods -> PC methods)
   [GAP] weeklyItems              -> (* no PC counterpart *)
   [GAP] workoutsDone             -> (* no PC counterpart *)
   [GAP] onDaySelected            -> (* no PC counterpart *)
   [GAP] showDayExercises         -> (* no PC counterpart *)
   [GAP] dismissDayPopup          -> (* no PC counterpart *)
   [GAP] onRestDaySelected        -> (* no PC counterpart *)
   [GAP] onStartTapped            -> (* no PC counterpart *)
   [GAP] onCheckInSleep           -> (* no PC counterpart *)
   [GAP] onCheckInEnergy          -> (* no PC counterpart *)
   [GAP] onCheckInDismiss         -> (* no PC counterpart *)
   [GAP] onCheckInComplete        -> (* no PC counterpart *)
   [GAP] onLogRestDay             -> (* no PC counterpart *)
   [GAP] swapWorkoutWithUpNext    -> (* no PC counterpart *)
   [GAP] resumeSession            -> (* no PC counterpart *)
   [GAP] onNewMobilitySession     -> (* no PC counterpart *)
   [GAP] onQuietStretchRest       -> (* no PC counterpart *)
   [GAP] dismissQuietStretch      -> (* no PC counterpart *)
   [GAP] dismissDeloadNudge       -> (* no PC counterpart *)
   [GAP] onAcceptDeload           -> (* no PC counterpart *)
   [GAP] onGraduateAccepted       -> (* no PC counterpart *)
   [GAP] dismissGraduationPrompt  -> (* no PC counterpart *)
   [GAP] onWelcomeBackTapped      -> (* no PC counterpart *)
   [GAP] onWelcomeBackDismissed   -> (* no PC counterpart *)
   [GAP] onWelcomeBackApply       -> (* no PC counterpart *)
   [GAP] buildEncouragement       -> (* no PC counterpart *)
   0/25 Kotlin actions/derived have a PC counterpart

SCREEN->vm action edges (screen calls the action)
   [GAP] dismissDayPopup          -> (* no PC counterpart *)
   [GAP] dismissDeloadNudge       -> (* no PC counterpart *)
   [GAP] dismissGraduationPrompt  -> (* no PC counterpart *)
   [GAP] dismissQuietStretch      -> (* no PC counterpart *)
   [GAP] onAcceptDeload           -> (* no PC counterpart *)
   [GAP] onCheckInComplete        -> (* no PC counterpart *)
   [GAP] onCheckInDismiss         -> (* no PC counterpart *)
   [GAP] onCheckInEnergy          -> (* no PC counterpart *)
   [GAP] onCheckInSleep           -> (* no PC counterpart *)
   [GAP] onDaySelected            -> (* no PC counterpart *)
   [GAP] onGraduateAccepted       -> (* no PC counterpart *)
   [GAP] onLogRestDay             -> (* no PC counterpart *)
   [GAP] onNewMobilitySession     -> (* no PC counterpart *)
   [GAP] onQuietStretchRest       -> (* no PC counterpart *)
   [GAP] onRestDaySelected        -> (* no PC counterpart *)
   [GAP] onStartTapped            -> (* no PC counterpart *)
   [GAP] onWelcomeBackApply       -> (* no PC counterpart *)
   [GAP] onWelcomeBackDismissed   -> (* no PC counterpart *)
   [GAP] onWelcomeBackTapped      -> (* no PC counterpart *)
   [GAP] resumeSession            -> (* no PC counterpart *)
   [GAP] showDayExercises         -> (* no PC counterpart *)
   0/21 Kotlin screen->vm have a PC counterpart

========  CONNECTIVITY: 0/74 Kotlin edges preserved in PC  <-- GAPS ABOVE


======================================================================
CONNECTIVITY PROBE (static) -- workout_cooldown
Kotlin VM is the reference; PC is verified against it.
======================================================================

Kotlin reference graph (WorkoutCooldownViewModel):
  state fields : stage, activity, totalSeconds, remainingSeconds, postWorkoutMood
  derived      : timer
  actions      : onPostWorkoutMoodSelected, startActivity, addMinute, finishActivity, skipToFinish, backToSelecting, runTimer
  screen reads : activity, postWorkoutMood, stage, timer
  screen calls : addMinute, backToSelecting, finishActivity, onPostWorkoutMoodSelected, skipToFinish, startActivity
  screen navs  : 

PseudoCoup side:
  State fields : stage, activity, total_seconds, remaining_seconds, post_workout_mood
  methods      : load, timer, on_post_workout_mood_selected, start_activity, add_minute, finish_activity, skip_to_finish, back_to_selecting, _run_timer
  screen reads : activity, stage
  screen calls : add_minute, back_to_selecting, finish_activity, skip_to_finish, start_activity
  screen navs  : 

----------------------------------------------------------------------
VERIFY: every Kotlin connectivity node has a PC counterpart?

STATE fields (vm.state -> PC State)
   [OK ] stage                    -> stage
   [OK ] activity                 -> activity
   [OK ] totalSeconds             -> total_seconds
   [OK ] remainingSeconds         -> remaining_seconds
   [OK ] postWorkoutMood          -> post_workout_mood
   5/5 Kotlin state have a PC counterpart

ACTIONS/derived (vm methods -> PC methods)
   [OK ] timer                    -> timer
   [OK ] onPostWorkoutMoodSelected -> on_post_workout_mood_selected
   [OK ] startActivity            -> start_activity
   [OK ] addMinute                -> add_minute
   [OK ] finishActivity           -> finish_activity
   [OK ] skipToFinish             -> skip_to_finish
   [OK ] backToSelecting          -> back_to_selecting
   [OK ] runTimer                 -> _run_timer
   8/8 Kotlin actions/derived have a PC counterpart

SCREEN->vm action edges (screen calls the action)
   [OK ] addMinute                -> add_minute
   [OK ] backToSelecting          -> back_to_selecting
   [OK ] finishActivity           -> finish_activity
   [GAP] onPostWorkoutMoodSelected -> (* no PC counterpart *)
   [OK ] skipToFinish             -> skip_to_finish
   [OK ] startActivity            -> start_activity
   5/6 Kotlin screen->vm have a PC counterpart

========  CONNECTIVITY: 18/19 Kotlin edges preserved in PC  <-- GAPS ABOVE


======================================================================
CONNECTIVITY PROBE (static) -- workout_execution
Kotlin VM is the reference; PC is verified against it.
======================================================================

Kotlin reference graph (WorkoutExecutionViewModel):
  state fields : 
  derived      : 
  actions      : loadSession, adjustWeight, setWeight, toggleExerciseUnit, adjustReps, setReps, setEffortRir, jumpToSet, jumpToExercise, updateNotes, updateExerciseNotes, toggleFavorite, toggleExerciseFavorite, addSet, deleteSet, setSetType, addExercise, removeExercise, moveExercise, linkSuperset, unlinkSuperset, cycleWorkoutMode, cycleWeightIncrement, logCurrentSet, confirmLeaveEmpty, dismissEmptyLeaveWarning, updateExistingSet, saveCurrentPendingSet, logSubEntry, finishDropSet, finishEarly, completeAndNavigate, requestDiscard, dismissDiscard, confirmDiscard, flashPr, dismissPrBanner, maybeFlagMidMicrocycle, flashMidMicrocycle, dismissMidMicrocycleBanner, openPlateCalculator, closePlateCalculator, adjustPlateCalcTarget, setPlateCalcBar, startRestTimer, skipRest, addRestTime, startRestTimerFrom, adjustHold, startHold, logHold, cancelHold, computeInitialCursor, computeNextCursor, buildSetLog, prefillWeight, prefillReps, firstIncompleteKey, landingFor, prefillEffortRir, warmupFor, requestSwap, dismissSwap, applySwap
  screen reads : availableBarWeightsKg, availableExercises, availablePlateWeightsKg, currentCardioFlag, currentExerciseIndex, currentItem, currentSetNumber, displayUnit, dropSetEntries, error, exerciseItems, exerciseNotes, extraSetTarget, holdState, isLoading, isSessionComplete, justHitPrExerciseName, midMicrocycleMessage, pendingEffortRir, pendingHoldSeconds, pendingReps, pendingSetType, pendingWeight, plateCalcBarKg, plateCalcTargetKg, restState, showDiscardConfirm, showEmptyLeaveWarning, showPlateCalculator, showSwapPicker, suggestedTargets, swapCandidates, warmupPlan, weightIncrement, workoutMode, workoutName
  screen calls : addExercise, addRestTime, addSet, adjustHold, adjustPlateCalcTarget, adjustReps, adjustWeight, applySwap, cancelHold, closePlateCalculator, confirmDiscard, confirmLeaveEmpty, deleteSet, dismissDiscard, dismissEmptyLeaveWarning, dismissMidMicrocycleBanner, dismissPrBanner, dismissSwap, finishDropSet, finishEarly, jumpToExercise, jumpToSet, linkSuperset, logCurrentSet, moveExercise, openPlateCalculator, removeExercise, requestDiscard, requestSwap, setEffortRir, setPlateCalcBar, setReps, setSetType, setWeight, skipRest, startHold, toggleExerciseFavorite, toggleExerciseUnit, toggleFavorite, unlinkSuperset, updateExerciseNotes, updateNotes
  screen navs  : 

PseudoCoup side:
  State fields : cur_ex, edit_weight, edit_reps, edit_for
  methods      : load, items, program_sets_for, workout_name, ensure_buffer_for, adjust_weight, adjust_reps, jump_to_exercise, next_set_log_id, log_set, complete_session
  screen reads : cur_ex, edit_reps, edit_weight
  screen calls : adjust_reps, adjust_weight, complete_session, ensure_buffer_for, items, jump_to_exercise, load, log_set, next_set_log_id, program_sets_for, workout_name
  screen navs  : today, workout_cooldown

----------------------------------------------------------------------
VERIFY: every Kotlin connectivity node has a PC counterpart?

STATE fields (vm.state -> PC State)
   0/0 Kotlin state have a PC counterpart

ACTIONS/derived (vm methods -> PC methods)
   [GAP] loadSession              -> (* no PC counterpart *)
   [OK ] adjustWeight             -> adjust_weight
   [GAP] setWeight                -> (* no PC counterpart *)
   [GAP] toggleExerciseUnit       -> (* no PC counterpart *)
   [OK ] adjustReps               -> adjust_reps
   [GAP] setReps                  -> (* no PC counterpart *)
   [GAP] setEffortRir             -> (* no PC counterpart *)
   [GAP] jumpToSet                -> (* no PC counterpart *)
   [OK ] jumpToExercise           -> jump_to_exercise
   [GAP] updateNotes              -> (* no PC counterpart *)
   [GAP] updateExerciseNotes      -> (* no PC counterpart *)
   [GAP] toggleFavorite           -> (* no PC counterpart *)
   [GAP] toggleExerciseFavorite   -> (* no PC counterpart *)
   [GAP] addSet                   -> (* no PC counterpart *)
   [GAP] deleteSet                -> (* no PC counterpart *)
   [GAP] setSetType               -> (* no PC counterpart *)
   [GAP] addExercise              -> (* no PC counterpart *)
   [GAP] removeExercise           -> (* no PC counterpart *)
   [GAP] moveExercise             -> (* no PC counterpart *)
   [GAP] linkSuperset             -> (* no PC counterpart *)
   [GAP] unlinkSuperset           -> (* no PC counterpart *)
   [GAP] cycleWorkoutMode         -> (* no PC counterpart *)
   [GAP] cycleWeightIncrement     -> (* no PC counterpart *)
   [GAP] logCurrentSet            -> (* no PC counterpart *)
   [GAP] confirmLeaveEmpty        -> (* no PC counterpart *)
   [GAP] dismissEmptyLeaveWarning -> (* no PC counterpart *)
   [GAP] updateExistingSet        -> (* no PC counterpart *)
   [GAP] saveCurrentPendingSet    -> (* no PC counterpart *)
   [GAP] logSubEntry              -> (* no PC counterpart *)
   [GAP] finishDropSet            -> (* no PC counterpart *)
   [GAP] finishEarly              -> (* no PC counterpart *)
   [GAP] completeAndNavigate      -> (* no PC counterpart *)
   [GAP] requestDiscard           -> (* no PC counterpart *)
   [GAP] dismissDiscard           -> (* no PC counterpart *)
   [GAP] confirmDiscard           -> (* no PC counterpart *)
   [GAP] flashPr                  -> (* no PC counterpart *)
   [GAP] dismissPrBanner          -> (* no PC counterpart *)
   [GAP] maybeFlagMidMicrocycle   -> (* no PC counterpart *)
   [GAP] flashMidMicrocycle       -> (* no PC counterpart *)
   [GAP] dismissMidMicrocycleBanner -> (* no PC counterpart *)
   [GAP] openPlateCalculator      -> (* no PC counterpart *)
   [GAP] closePlateCalculator     -> (* no PC counterpart *)
   [GAP] adjustPlateCalcTarget    -> (* no PC counterpart *)
   [GAP] setPlateCalcBar          -> (* no PC counterpart *)
   [GAP] startRestTimer           -> (* no PC counterpart *)
   [GAP] skipRest                 -> (* no PC counterpart *)
   [GAP] addRestTime              -> (* no PC counterpart *)
   [GAP] startRestTimerFrom       -> (* no PC counterpart *)
   [GAP] adjustHold               -> (* no PC counterpart *)
   [GAP] startHold                -> (* no PC counterpart *)
   [GAP] logHold                  -> (* no PC counterpart *)
   [GAP] cancelHold               -> (* no PC counterpart *)
   [GAP] computeInitialCursor     -> (* no PC counterpart *)
   [GAP] computeNextCursor        -> (* no PC counterpart *)
   [GAP] buildSetLog              -> (* no PC counterpart *)
   [GAP] prefillWeight            -> (* no PC counterpart *)
   [GAP] prefillReps              -> (* no PC counterpart *)
   [GAP] firstIncompleteKey       -> (* no PC counterpart *)
   [GAP] landingFor               -> (* no PC counterpart *)
   [GAP] prefillEffortRir         -> (* no PC counterpart *)
   [GAP] warmupFor                -> (* no PC counterpart *)
   [GAP] requestSwap              -> (* no PC counterpart *)
   [GAP] dismissSwap              -> (* no PC counterpart *)
   [GAP] applySwap                -> (* no PC counterpart *)
   3/64 Kotlin actions/derived have a PC counterpart

SCREEN->vm action edges (screen calls the action)
   [GAP] addExercise              -> (* no PC counterpart *)
   [GAP] addRestTime              -> (* no PC counterpart *)
   [GAP] addSet                   -> (* no PC counterpart *)
   [GAP] adjustHold               -> (* no PC counterpart *)
   [GAP] adjustPlateCalcTarget    -> (* no PC counterpart *)
   [OK ] adjustReps               -> adjust_reps
   [OK ] adjustWeight             -> adjust_weight
   [GAP] applySwap                -> (* no PC counterpart *)
   [GAP] cancelHold               -> (* no PC counterpart *)
   [GAP] closePlateCalculator     -> (* no PC counterpart *)
   [GAP] confirmDiscard           -> (* no PC counterpart *)
   [GAP] confirmLeaveEmpty        -> (* no PC counterpart *)
   [GAP] deleteSet                -> (* no PC counterpart *)
   [GAP] dismissDiscard           -> (* no PC counterpart *)
   [GAP] dismissEmptyLeaveWarning -> (* no PC counterpart *)
   [GAP] dismissMidMicrocycleBanner -> (* no PC counterpart *)
   [GAP] dismissPrBanner          -> (* no PC counterpart *)
   [GAP] dismissSwap              -> (* no PC counterpart *)
   [GAP] finishDropSet            -> (* no PC counterpart *)
   [GAP] finishEarly              -> (* no PC counterpart *)
   [OK ] jumpToExercise           -> jump_to_exercise
   [GAP] jumpToSet                -> (* no PC counterpart *)
   [GAP] linkSuperset             -> (* no PC counterpart *)
   [GAP] logCurrentSet            -> (* no PC counterpart *)
   [GAP] moveExercise             -> (* no PC counterpart *)
   [GAP] openPlateCalculator      -> (* no PC counterpart *)
   [GAP] removeExercise           -> (* no PC counterpart *)
   [GAP] requestDiscard           -> (* no PC counterpart *)
   [GAP] requestSwap              -> (* no PC counterpart *)
   [GAP] setEffortRir             -> (* no PC counterpart *)
   [GAP] setPlateCalcBar          -> (* no PC counterpart *)
   [GAP] setReps                  -> (* no PC counterpart *)
   [GAP] setSetType               -> (* no PC counterpart *)
   [GAP] setWeight                -> (* no PC counterpart *)
   [GAP] skipRest                 -> (* no PC counterpart *)
   [GAP] startHold                -> (* no PC counterpart *)
   [GAP] toggleExerciseFavorite   -> (* no PC counterpart *)
   [GAP] toggleExerciseUnit       -> (* no PC counterpart *)
   [GAP] toggleFavorite           -> (* no PC counterpart *)
   [GAP] unlinkSuperset           -> (* no PC counterpart *)
   [GAP] updateExerciseNotes      -> (* no PC counterpart *)
   [GAP] updateNotes              -> (* no PC counterpart *)
   3/42 Kotlin screen->vm have a PC counterpart

========  CONNECTIVITY: 6/106 Kotlin edges preserved in PC  <-- GAPS ABOVE


======================================================================
CONNECTIVITY PROBE (static) -- workout_summary
Kotlin VM is the reference; PC is verified against it.
======================================================================

Kotlin reference graph (WorkoutSummaryViewModel):
  state fields : isLoading, durationSeconds, totalVolumeKg, exerciseSummaries, sessionPrs, displayUnit
  derived      : 
  actions      : loadSummary
  screen reads : displayUnit, durationSeconds, exerciseSummaries, isLoading, sessionPrs, totalVolumeKg
  screen calls : 
  screen navs  : 

PseudoCoup side:
  State fields : 
  methods      : duration_seconds, exec_items, total_volume_kg, session_prs, exercise_for
  screen reads : 
  screen calls : duration_seconds, exec_items, exercise_for, session_prs, total_volume_kg
  screen navs  : today

----------------------------------------------------------------------
VERIFY: every Kotlin connectivity node has a PC counterpart?

STATE fields (vm.state -> PC State)
   [GAP] isLoading                -> (* no PC counterpart *)
   [GAP] durationSeconds          -> (* no PC counterpart *)
   [GAP] totalVolumeKg            -> (* no PC counterpart *)
   [GAP] exerciseSummaries        -> (* no PC counterpart *)
   [GAP] sessionPrs               -> (* no PC counterpart *)
   [GAP] displayUnit              -> (* no PC counterpart *)
   0/6 Kotlin state have a PC counterpart

ACTIONS/derived (vm methods -> PC methods)
   [GAP] loadSummary              -> (* no PC counterpart *)
   0/1 Kotlin actions/derived have a PC counterpart

SCREEN->vm action edges (screen calls the action)
   0/0 Kotlin screen->vm have a PC counterpart

========  CONNECTIVITY: 0/7 Kotlin edges preserved in PC  <-- GAPS ABOVE


======================================================================
CONNECTIVITY PROBE (static) -- workout_warmup
Kotlin VM is the reference; PC is verified against it.
======================================================================

Kotlin reference graph (WorkoutWarmupViewModel):
  state fields : stage, activity, totalSeconds, remainingSeconds
  derived      : timer
  actions      : startActivity, addMinute, finishActivity, backToSelecting, runTimer
  screen reads : activity, stage, timer
  screen calls : addMinute, backToSelecting, finishActivity, startActivity
  screen navs  : 

PseudoCoup side:
  State fields : stage, activity, total_seconds, remaining_seconds
  methods      : timer, start_activity, add_minute, finish_activity, back_to_selecting, _run_timer
  screen reads : 
  screen calls : start_activity
  screen navs  : today, workout_execution

----------------------------------------------------------------------
VERIFY: every Kotlin connectivity node has a PC counterpart?

STATE fields (vm.state -> PC State)
   [OK ] stage                    -> stage
   [OK ] activity                 -> activity
   [OK ] totalSeconds             -> total_seconds
   [OK ] remainingSeconds         -> remaining_seconds
   4/4 Kotlin state have a PC counterpart

ACTIONS/derived (vm methods -> PC methods)
   [OK ] timer                    -> timer
   [OK ] startActivity            -> start_activity
   [OK ] addMinute                -> add_minute
   [OK ] finishActivity           -> finish_activity
   [OK ] backToSelecting          -> back_to_selecting
   [OK ] runTimer                 -> _run_timer
   6/6 Kotlin actions/derived have a PC counterpart

SCREEN->vm action edges (screen calls the action)
   [GAP] addMinute                -> (* no PC counterpart *)
   [GAP] backToSelecting          -> (* no PC counterpart *)
   [GAP] finishActivity           -> (* no PC counterpart *)
   [OK ] startActivity            -> start_activity
   1/4 Kotlin screen->vm have a PC counterpart

========  CONNECTIVITY: 11/14 Kotlin edges preserved in PC  <-- GAPS ABOVE



# SUMMARY
Total Edges Preserved: 171/636 (26.89%)
