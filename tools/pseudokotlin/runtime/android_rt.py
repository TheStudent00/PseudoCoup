"""
runtime/android_rt.py — STUBS for the Android-framework names the foundation touches (android.*,
androidx.* framework, WorkManager, Firebase/Play, the Room builder). These are honest STUBS, not
wrappers: there is no Python Android, so they exist to resolve the names and accept the calls without
crashing at load. The code that uses them is platform glue (an Activity, notification scheduling, crash
reporting, background workers) that inherently cannot run off-device -- so it is not exercised by the
foundation's tests. Wrapping these makes the names RESOLVE; it does not make the platform RUN.

When a piece of this genuinely needs to run in Python (e.g. notification CONTENT built from domain data),
the right move is to lift that logic out of the platform glue into the domain layer, where it is testable.
"""


class _Stub:
    """A permissive stub: any attribute is another stub, any call returns a stub, truthy-but-inert."""
    def __init__(self, *a, **k):
        pass

    def __getattr__(self, name):
        return _Stub()

    def __call__(self, *a, **k):
        return _Stub()


# ---- android.util.Log -- the one that's actually all over the code; a no-op logger ------------- #
class Log:
    @staticmethod
    def d(*a):
        return 0

    e = i = w = v = wtf = d

    @staticmethod
    def getStackTraceString(*a):
        return ""


# ---- android.* framework -------------------------------------------------------------------------- #
class Context(_Stub):
    pass


class Application(_Stub):
    pass


class Build:
    VERSION = _Stub()
    MODEL = "python"
    MANUFACTURER = "python"


class Bundle(_Stub):
    pass


class Cursor(_Stub):
    # android.database.Cursor field-type tags -- the real engine cursor (runtime/room.py) returns these
    # from getType(i) so a generic dump can branch on the stored SQLite type.
    FIELD_TYPE_NULL = 0
    FIELD_TYPE_INTEGER = 1
    FIELD_TYPE_FLOAT = 2
    FIELD_TYPE_STRING = 3
    FIELD_TYPE_BLOB = 4


R = _Stub()     # com.sara.workoutforlife.R -- Gradle-generated resources (R.string.x / R.drawable.y / …)


class BuildConfig:
    # Gradle-generated at build time (no Kotlin source) -- a stand-in so version strings resolve.
    DEBUG = False
    APPLICATION_ID = "com.sara.workoutforlife"
    BUILD_TYPE = "release"
    VERSION_CODE = 1
    VERSION_NAME = "1.0"


class Intent(_Stub):
    pass


class Manifest:
    permission = _Stub()


class NotificationChannel(_Stub):
    pass


class NotificationManager(_Stub):
    IMPORTANCE_DEFAULT = 3
    IMPORTANCE_HIGH = 4


class PackageManager(_Stub):
    pass


class PendingIntent:
    FLAG_IMMUTABLE = 67108864
    FLAG_UPDATE_CURRENT = 134217728

    @staticmethod
    def getActivity(*a, **k):
        return _Stub()

    @staticmethod
    def getBroadcast(*a, **k):
        return _Stub()


# ---- androidx.* framework + activity-compose entry points --------------------------------------- #
class ActivityResultContracts:
    RequestPermission = _Stub


class ApplicationProvider:          # androidx.test -- getApplicationContext() in instrumented tests
    @staticmethod
    def getApplicationContext():
        return _Stub()


class InstrumentationRegistry:      # androidx.test -- only passed through to MigrationTestHelper here
    @staticmethod
    def getInstrumentation():
        return _Stub()


class ContextCompat:
    @staticmethod
    def getSystemService(*a, **k):
        return _Stub()

    @staticmethod
    def checkSelfPermission(*a, **k):
        return 0


class NotificationCompat:
    class Builder(_Stub):
        pass

    PRIORITY_DEFAULT = 0


class NotificationManagerCompat:
    @staticmethod
    def from_(*a, **k):           # NotificationManagerCompat.from(context) -- `from` is a py keyword
        return _Stub()


def enableEdgeToEdge(*a, **k):
    return None


def setContent(*a, **k):          # androidx.activity.compose.setContent { } -- UI entry, inert here
    return None


# ---- androidx.work (WorkManager) ---------------------------------------------------------------- #
class WorkManager:
    @staticmethod
    def getInstance(*a, **k):
        return _Stub()


class PeriodicWorkRequestBuilder(_Stub):
    pass


class ExistingPeriodicWorkPolicy:
    KEEP = "KEEP"
    UPDATE = "UPDATE"
    REPLACE = "REPLACE"


# ---- com.google (Firebase / Play / Wearable) ---------------------------------------------------- #
class FirebaseApp:
    @staticmethod
    def initializeApp(*a, **k):
        return _Stub()


class FirebaseCrashlytics:
    @staticmethod
    def getInstance(*a, **k):
        return _Stub()


class PutDataMapRequest(_Stub):
    pass


class Tasks(_Stub):
    pass


class Wearable(_Stub):
    pass


# ---- dagger.hilt entry-point accessor ----------------------------------------------------------- #
class EntryPointAccessors:
    @staticmethod
    def fromApplication(*a, **k):
        return _Stub()


# ---- androidx.room: the Room builder + @Dao/@Entity are the real sqlite3 engine (runtime/room.py);
#      Update here is just the leftover @Update annotation name if it ever survives translation. -------- #
def Update(x=None):
    return x
