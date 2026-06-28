# ≡KT module  java/com/sara/workoutforlife/engine/NotificationTriggers.kt  ->  NotificationTriggers.py
# connects(1deg): --

class NotificationTriggers:
    """≡KT  object NotificationTriggers  -> object->instance
    attrs (3/3): ABSENCE_NUDGE_MIN_DAYS, MICROCYCLE_REMINDER_AT, VICTORY_PROMPT_AFTER_SESSIONS
    """
    def __init__(self):
        self.ABSENCE_NUDGE_MIN_DAYS = 7
        self.MICROCYCLE_REMINDER_AT = 1
        self.VICTORY_PROMPT_AFTER_SESSIONS = 3
    def shouldNudgeAbsence(self, gapDays):
        """≡KT  fun shouldNudgeAbsence  -> exact"""
        return gapDays >= self.ABSENCE_NUDGE_MIN_DAYS
    def shouldRemindWorkout(self, hasUpNextWorkout, completedSessionToday):
        """≡KT  fun shouldRemindWorkout  -> exact"""
        return hasUpNextWorkout and (not completedSessionToday)
    def shouldRemindMicrocycle(self, workoutsRemaining):
        """≡KT  fun shouldRemindMicrocycle  -> exact"""
        return workoutsRemaining == self.MICROCYCLE_REMINDER_AT
    def shouldRemindMesocycle(self, isPeakWeek, deloadStartsNext):
        """≡KT  fun shouldRemindMesocycle  -> exact"""
        return isPeakWeek or deloadStartsNext
    def shouldPromptVictory(self, completedSessionsSinceLastWin):
        """≡KT  fun shouldPromptVictory  -> exact"""
        return completedSessionsSinceLastWin >= self.VICTORY_PROMPT_AFTER_SESSIONS


NotificationTriggers = NotificationTriggers()
