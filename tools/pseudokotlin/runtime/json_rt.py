"""
runtime/json_rt.py — org.json (JSONObject / JSONArray) backed by Python's json. Real wrappers: the
foundation uses these to serialise bug-report / diagnostics payloads, which Python does natively.
"""
import json as _json

import os as _os
import sys as _sys
_sys.path.insert(0, _os.path.dirname(_os.path.dirname(_os.path.abspath(__file__))))
from runtime.kotlin_rt import KtList   # noqa: E402  -- keys() returns a KtList so .filter/.toList chain


class _Null:
    """org.json's JSONObject.NULL sentinel: a stand-in for JSON null that equals Python None (so a parsed
    null and an explicit NULL both compare equal), serialises as null, and is falsy."""
    def __eq__(self, other):
        return other is None or isinstance(other, _Null)

    def __ne__(self, other):
        return not self.__eq__(other)

    def __hash__(self):
        return 0

    def __bool__(self):
        return False

    def __repr__(self):
        return "null"


class JSONObject:
    NULL = _Null()

    def __init__(self, source=None):
        if isinstance(source, str):
            self._d = _json.loads(source)
        elif isinstance(source, dict):
            self._d = dict(source)
        else:
            self._d = {}

    def put(self, key, value):
        self._d[key] = _unwrap(value)
        return self

    def get(self, key):
        return self._d[key]

    def getString(self, key):
        return str(self._d[key])

    def getInt(self, key):
        return int(self._d[key])

    def getLong(self, key):
        return int(self._d[key])

    def getBoolean(self, key):
        return bool(self._d[key])

    def optString(self, key, default=""):
        v = self._d.get(key, default)
        return default if v is None else str(v)

    def optInt(self, key, default=0):
        v = self._d.get(key, default)
        return default if v is None else int(v)

    def optJSONArray(self, key):
        v = self._d.get(key)
        return JSONArray(v) if isinstance(v, list) else None

    def optJSONObject(self, key):
        v = self._d.get(key)
        return JSONObject(v) if isinstance(v, dict) else None

    def has(self, key):
        return key in self._d

    def keys(self):
        return KtList(self._d.keys())          # KtList so `keys().filter { … }.toList()` chains

    def toString(self, indent=None):
        return _json.dumps(self._d, indent=indent) if indent else _json.dumps(self._d)

    def __str__(self):
        return _json.dumps(self._d)


class JSONArray:
    def __init__(self, source=None):
        if isinstance(source, str):
            self._a = _json.loads(source)
        elif isinstance(source, (list, tuple)):
            self._a = [_unwrap(x) for x in source]
        else:
            self._a = []

    def put(self, value):
        self._a.append(_unwrap(value))
        return self

    def length(self):
        return len(self._a)

    def get(self, i):
        return self._a[i]

    def getJSONObject(self, i):
        return JSONObject(self._a[i])

    def getString(self, i):
        return str(self._a[i])

    def toString(self, *a):
        return _json.dumps(self._a)

    def __str__(self):
        return _json.dumps(self._a)


def _unwrap(v):
    if isinstance(v, JSONObject):
        return v._d
    if isinstance(v, JSONArray):
        return v._a
    if isinstance(v, _Null):                   # JSONObject.NULL -> a real JSON null
        return None
    return v


if __name__ == "__main__":
    o = JSONObject().put("name", "WFL").put("count", 3)
    o.put("tags", JSONArray().put("a").put("b"))
    s = o.toString()
    back = JSONObject(s)
    assert back.getString("name") == "WFL"
    assert back.getInt("count") == 3
    assert JSONArray(back.get("tags") if isinstance(back.get("tags"), list) else "[]").length() == 2
    print("json_rt self-test: OK")
