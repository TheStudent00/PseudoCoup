"""
runtime/android_rt.py — STUBS for the Android-framework names the foundation touches (android.*,
androidx.* framework, WorkManager, Firebase/Play, the Room builder). These are honest STUBS, not
wrappers: there is no Python Android, so they exist to resolve the names and accept the calls without
crashing at load. The code that uses them is platform glue (an Activity, notification scheduling, crash
reporting, background workers) that inherently cannot run off-device -- so it is not exercised by the
foundation's tests. Wrapping these makes the names RESOLVE; it does not make the platform RUN.

When a piece of this genuinely needs to run in Python (e.g. notification CONTENT built from domain data),
the right move is to lift that logic out of the platform glue into the domain layer, where it is testable.

Exception to "stubs only": app-private STORAGE (Context.filesDir, SharedPreferences) is real -- a local
folder and JSON files -- because file/preference reads and writes are not phone hardware; they run fine
in Python and the CrashReporter / debug-clock code paths need them for real.
"""
import os as _os


class _StubMeta(type):
    """Class-level permissiveness: reading an undefined class attribute yields a stub, so a platform object
    (ActivityResultContracts.CreateDocument) doesn't need every nested contract/constant listed by hand."""
    def __getattr__(cls, name):
        if name.startswith("__"):
            raise AttributeError(name)          # leave dunders to Python's normal machinery
        return _Stub()


class _Stub(metaclass=_StubMeta):
    """A permissive stub: any attribute is another stub (on the instance AND the class), any call returns a
    stub, truthy-but-inert."""
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
# The phone's app-private storage, mapped to a REAL local folder: files under .appdata/files (the
# CrashReporter's crash file lives there), preferences as JSON under .appdata/prefs (the debug clock's
# offset lives there). Real inputs -- code that reads/writes them behaves as on the device.
_APPDATA = _os.path.expanduser("~/Programming/WFL_MixingCenter/.appdata")


class _SharedPreferences:
    """android SharedPreferences: a named key->value store that survives restarts. JSON-file-backed."""
    def __init__(self, name):
        self._path = _os.path.join(_APPDATA, "prefs", str(name) + ".json")
        try:
            import json
            with open(self._path) as fh:
                self._d = json.load(fh)
        except (OSError, ValueError):
            self._d = {}

    def _get(self, k, d):
        return self._d.get(str(k), d)

    def getLong(self, k, d=0):
        return int(self._get(k, d))

    getInt = getLong

    def getFloat(self, k, d=0.0):
        return float(self._get(k, d))

    def getBoolean(self, k, d=False):
        return bool(self._get(k, d))

    def getString(self, k, d=None):
        return self._get(k, d)

    def edit(self):
        return _PrefsEditor(self)


class _PrefsEditor:
    def __init__(self, prefs):
        self._p = prefs

    def _put(self, k, v):
        self._p._d[str(k)] = v
        return self

    putLong = putInt = putFloat = putBoolean = putString = _put

    def remove(self, k):
        self._p._d.pop(str(k), None)
        return self

    def apply(self):
        import json
        _os.makedirs(_os.path.dirname(self._p._path), exist_ok=True)
        with open(self._p._path, "w") as fh:
            json.dump(self._p._d, fh)

    commit = apply


class Context(_Stub):
    @property
    def filesDir(self):
        d = _os.path.join(_APPDATA, "files")
        _os.makedirs(d, exist_ok=True)
        return d

    def getSharedPreferences(self, name, mode=0):
        return _SharedPreferences(name)


class Application(Context):
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


class _RBucket:
    def __init__(self, t):
        self._t = t

    def __getattr__(self, name):
        return name                              # R.font.figtree_variable -> "figtree_variable"


class _RNames:
    """R.<type>.<name> -> the resource NAME (a string). Real enough for the kit to resolve actual files
    (R.font.* -> res/font/<name>.ttf) and for ids to be stable comparable values."""
    def __getattr__(self, t):
        b = _RBucket(t)
        setattr(self, t, b)
        return b


R = _RNames()   # com.sara.workoutforlife.R -- Gradle-generated resources (R.string.x / R.font.y / …)

# Dagger/Hilt DI markers + a couple Wearable platform names. DI is hand-wired in the constructed objects
# (there is no runtime DI container), so these are INTENTIONAL no-ops -- defined here as real, inert names
# (annotations are dropped; `SingletonComponent::class` etc. survive as values) so they don't auto-stub.
for _n in ("Inject", "Provides", "Provider", "Module", "Binds", "Singleton", "InstallIn", "HiltAndroidApp",
           "SingletonComponent", "EntryPoint", "EntryPointAccessors", "MessageEvent", "WearableListenerService",
           "ComponentActivity", "ApplicationContext", "AndroidEntryPoint", "CoroutineWorker",
           "WorkerParameters", "SupportSQLiteDatabase"):
    globals()[_n] = type(_n, (_Stub,), {})


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
class ActivityResultContracts(_Stub):   # any contract (RequestPermission/CreateDocument/OpenDocument/…) -> stub
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
class FirebaseApp(_Stub):                # _Stub base: any other class-level read (getApps) yields a stub
    @staticmethod
    def initializeApp(*a, **k):
        return _Stub()

    @staticmethod
    def getApps(*a, **k):
        return []                        # no Firebase off-device -> "not configured", the code's real branch


class FirebaseCrashlytics(_Stub):
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
