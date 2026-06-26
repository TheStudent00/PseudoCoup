# log_45 — the actual code: one transpiled line, fully decomposed (no counts, real snippets)

Date: 2026-06-25
Type: evidence. Request was "show the snippets of code, not vague references to thousands." Fair.
This decomposes ONE real line of transpiled output into the exact, file-by-file work it needs. Every
path is verifiable.

## The line (real, from `build/literal/TodayViewModel.py:163`)

```python
self._outerState = combine(userRepository.getUser(), programDao.getEnrolled(),
                           sessionDao.getActiveSession(), pathRepository.activePaths)(_lambda_6)
```

Every identifier in it is undefined in Python. Below is each one, the real Kotlin it maps to, and the
Python state.

## 1. `combine` — exists, but is a no-op stub

Entire current implementation (`core/flow.py:78`):
```python
def combine(*flows: Flow, transform: Callable[..., Any]) -> Flow:
    return Flow()        # empty object; carries no data; runs no transform
```
Needs: a real implementation that subscribes to N flows, re-emits on any change, runs the transform.
(Also the `(_lambda_6)` trailing call is the keyword-only `transform` bug from log_42.)

## 2. `userRepository` — does not exist (`data/repository/UserRepository.kt:18,28`)

```kotlin
class UserRepository @Inject constructor(
    private val userDao: UserDao,
    private val timeProvider: TimeProvider,
) {
    fun getUser(): Flow<UserEntity> = userDao.getUser().map { it ?: defaultUser() }
```
Porting this pulls in `userDao` (another DAO), `UserEntity` (another entity), and `defaultUser()`.
Python equivalent: none. There are **18 repository classes**.

## 3. `programDao` / `sessionDao` — do not exist; they are SQL (`data/db/dao/SetLogDao.kt:92`)

```kotlin
@Query("""
    SELECT COUNT(DISTINCT ws.id) FROM set_logs sl
    INNER JOIN exercise_logs el ON sl.exerciseLogId = el.id
    INNER JOIN workout_sessions ws ON el.sessionId = ws.id
    WHERE ...
""")
fun ...(...): Flow<Int>
```
Needs: a class that executes that SQL against a real DB (sqlite) and returns a reactive stream.
Python equivalent: none. **26 DAO files, 149 `@Query` statements.**

## 4. The entities those return — do not exist (`data/db/entity/WorkoutSessionEntity.kt:26`)

```kotlin
data class WorkoutSessionEntity(
    @PrimaryKey val id: String,
    val programDayId: String?,
    val startedAt: Long,
    val completedAt: Long?,
    val durationSeconds: Int?,
    val isCompleted: Boolean,
    val checkInSleep: Int?,
    // ... 15 fields
)
```
Python equivalent: none. **27 entity classes.**

## 5. `AutoregulationEngine` — does not exist (`engine/AutoregulationEngine.kt:42`)

Referenced at `TodayViewModel.py:297` (`AutoregulationEngine.DeloadRecommendation.NONE`), imported as
a bare `# TODO_RAW_IMPORT` at `TodayViewModel.py:32`.
```kotlin
fun suggestRawWeight(e1rm: Double, targetRir: Int, targetRepsCenter: Int): Double {
    val repsToFailure = targetRepsCenter + targetRir
    return e1rm / (1.0 + repsToFailure / 30.0)
}
```
Pure logic — transpiles like a VM. Python equivalent: none. **9 engine files.**

## The whole Python domain side, today

`ls core/` -> `__init__.py  coroutines.py  flow.py`. No entity, no dao, no repository, no engine.
**Zero domain code exists.**

## So "make this ONE line run" =

- replace the fake `combine` (and the other ~20 inert operators) with real ones,
- write the 4 entity dataclasses it touches (`UserEntity`, `WorkoutSessionEntity`, `ProgramEntity`,
  `PathEntity`),
- write the 4 DAO classes that run real SQL (`userDao`, `programDao`, `sessionDao`, `pathDao`),
- write the 4 repositories that wrap them (`UserRepository`, `PathRepository`, …),
- port `AutoregulationEngine`.

That is the "domain layer" from log_44, made concrete. It is not hand-waving — it is these specific
files, none of which exist in Python. One line of one VM touches ~13 of them; the 27 VMs' union is the
whole `data/`+`engine/` tree.

Pointers (all verifiable): `build/literal/TodayViewModel.py:163,297,32`, `core/flow.py:78`,
`~/Programming/WFL/.../data/repository/UserRepository.kt:28`,
`.../data/db/dao/SetLogDao.kt:92`, `.../data/db/entity/WorkoutSessionEntity.kt:26`,
`.../engine/AutoregulationEngine.kt:42`.
