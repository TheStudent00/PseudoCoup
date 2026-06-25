# PseudoCoup -- navigation map (static)

Screens are nodes; edges are `router.navigate()` calls found statically in
handler bodies. Red = NOT reachable from the entry screen by any nav path.

```mermaid
flowchart LR
    calibrate["calibrate"]
    debug_panel["debug_panel"]
    exercise_create["exercise_create"]
    exercise_detail["exercise_detail"]
    exercise_picker["exercise_picker"]
    exercises["exercises"]
    gym_create_wizard["gym_create_wizard"]
    gym_editor["gym_editor"]
    gym_list["gym_list"]
    logcardio["logcardio"]
    onboarding["onboarding"]
    path_detail["path_detail"]
    paths["paths"]
    program["program"]
    program_day_editor["program_day_editor"]
    program_editor["program_editor"]
    programs["programs"]
    progress["progress"]
    report_bug["report_bug"]
    session_detail["session_detail"]
    settings_notifications["settings_notifications"]
    stretch_suggestions["stretch_suggestions"]
    today["today"]
    update_program["update_program"]
    wins["wins"]
    workout_cooldown["workout_cooldown"]
    workout_execution["workout_execution"]
    workout_summary["workout_summary"]
    workout_warmup["workout_warmup"]
    you["you"]
    today -.nav bar.-> paths
    today -.nav bar.-> program
    today -.nav bar.-> progress
    today -.nav bar.-> you
    debug_panel --> you
    exercise_create --> exercises
    exercise_detail --> exercises
    exercise_picker --> program_day_editor
    exercises --> exercise_create
    exercises --> exercise_detail
    exercises --> you
    gym_create_wizard --> gym_editor
    gym_create_wizard --> gym_list
    gym_editor --> gym_list
    gym_list --> gym_create_wizard
    gym_list --> gym_editor
    gym_list --> you
    logcardio --> you
    onboarding --> today
    path_detail --> paths
    paths --> path_detail
    program --> programs
    program --> update_program
    program_day_editor --> exercise_picker
    program_day_editor --> program_editor
    program_editor --> program_day_editor
    program_editor --> programs
    programs --> program
    programs --> program_editor
    progress --> session_detail
    progress --> wins
    report_bug --> you
    session_detail --> progress
    settings_notifications --> you
    stretch_suggestions --> exercise_detail
    stretch_suggestions --> workout_cooldown
    today --> workout_warmup
    update_program --> program
    wins --> progress
    workout_cooldown --> stretch_suggestions
    workout_cooldown --> workout_execution
    workout_cooldown --> workout_summary
    workout_execution --> today
    workout_execution --> workout_cooldown
    workout_summary --> today
    workout_warmup --> today
    workout_warmup --> workout_execution
    you --> calibrate
    you --> debug_panel
    you --> exercises
    you --> gym_list
    you --> logcardio
    you --> onboarding
    you --> report_bug
    you --> settings_notifications
    you --> wins
    classDef tab fill:#dff,stroke:#06c,color:#036;
    classDef dead fill:#fdd,stroke:#c00,color:#900;
    class today,program,paths,progress,you tab;
```

_The 5 blue tabs share a persistent bottom nav bar (dotted edges = that hub, which lives in the router, not in a screen)._

**All screens reachable from `today`.**
