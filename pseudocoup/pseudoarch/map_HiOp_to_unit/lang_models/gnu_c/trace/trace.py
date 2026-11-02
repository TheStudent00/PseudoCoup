"""trace -- runs traced_clang on one context, with our setup, and returns
what path_recorder wrote (PCHQ plan: research/trace_logical_paths/trace).

    names = names_of(clang_binary)
    recording = recording_of(clang_binary, names, work)
    found = trace(context, clang, recording, work)

`found.events` is every function entered and returned from and every branch
taken, from the start of the standard form's function to the end of its
lowering, each as (kind, offset in the binary); `found.accepted` and
`found.messages` are clang's own answer.
"""

import os
import struct
import subprocess
from typing import NamedTuple

from ....model_lang_parts.context.entry_context import Context, command_for, standard_source

NM = os.environ.get("LLVM_NM", "llvm-nm-21")
KINDS = {1: "enter", 2: "return", 3: "branch"}
RECORD = struct.Struct("<BQ")
OFFSET = struct.Struct("<Q")
# The start of the standard form's function: the parser calls this action
# as it begins every function definition, and the standard form has one.
START_FUNCTION = "clang::Sema::ActOnStartOfFunctionDef("
# The end: clang calls this when a function's body is lowered, so the HiOp's
# lowering is whole before recording stops.
STOP_FUNCTION = "clang::CodeGen::CodeGenFunction::FinishFunction("
# A diagnostic: clang calls this only for a diagnostic it does not ignore.
REPORT_FUNCTION = "clang::DiagnosticsEngine::Report(clang::DiagnosticsEngine::Level"
# Functions whose steps depend on where things sit in memory, not on the
# program: LLVM's hash tables, allocators, hashing and sorts, and the C++
# library's hash tables, trees, sorts and searches. Each one, with everything
# it calls, is written as nothing. The rest of the C++ library is recorded:
# clang reports a diagnostic from a destructor that std::optional calls
# (clang/lib/Sema/SemaBase.cpp, SemaDiagnosticBuilder), which run elv2_l193
# found hidden while the whole library was opaque.
# LLVM's are named as the symbol table spells them (mangled), which puts a
# function's own name first: `_ZN4llvm8DenseMap` is every function of
# llvm::DenseMap.
LLVM_OPAQUE = (
    "DenseMapBase", "DenseMap", "SmallDenseMap", "DenseMapInfo", "DenseMapIterator", "DenseSet",
    "SmallDenseSet", "SmallPtrSetImplBase", "SmallPtrSetImpl", "SmallPtrSet", "SmallPtrSetIterator",
    "SmallPtrSetIteratorImpl", "StringMapImpl", "StringMap", "StringMapIterBase", "StringMapIterator",
    "StringMapConstIterator", "StringMapEntry", "StringMapEntryBase", "FoldingSetBase", "FoldingSet",
    "FoldingSetImpl", "ContextualFoldingSet", "FoldingSetNodeID", "FoldingSetNodeIDRef",
    "FoldingSetIteratorImpl", "FoldingSetIterator", "FoldingSetBucketIteratorImpl",
    "FoldingSetBucketIterator", "FoldingSetTrait", "DefaultFoldingSetTrait", "ContextualFoldingSetTrait",
    "DefaultContextualFoldingSetTrait", "FoldingSetVector", "hashing", "hash_value", "hash_combine",
    "hash_combine_range", "hash_code", "xxh3_64bits", "xxHash64", "djbHash", "BumpPtrAllocatorImpl",
    "SpecificBumpPtrAllocator", "MallocAllocator", "AllocatorBase", "allocate_buffer", "deallocate_buffer",
    "safe_malloc", "safe_calloc", "safe_realloc", "Recycler", "RecyclingAllocator", "ArrayRecycler",
    "ScopedHashTable", "ScopedHashTableScope", "ImmutableMap", "ImmutableSet", "ImutAVLTree",
    "ImutAVLFactory", "OnDiskChainedHashTable", "OnDiskIterableChainedHashTable", "sort", "array_pod_sort",
    "array_pod_sort_comparator", "stable_sort",
)
LLVM_DETAIL_OPAQUE = ("DenseSetImpl", "DenseSetPair", "DenseMapPair")
# The C++ library's, by the function's own name (demangled, without its
# return type): a class whose name begins with one of these, or a function
# of std whose name holds one of the words.
CPP_OPAQUE_CLASSES = ("std::_Hashtable", "std::__detail::", "std::unordered_", "std::_Rb_tree", "std::hash<")
CPP_OPAQUE_CONTAINERS = ("std::map", "std::set", "std::multimap", "std::multiset")
CPP_OPAQUE_WORDS = ("sort", "heap", "merge", "lower_bound", "upper_bound", "equal_range", "binary_search",
                    "partition", "nth_element", "introselect", "median")


class Trace(NamedTuple):
    """`events` from where the cut begins; `early_exits` are the diagnostics
    already read from before it (logical_path.cut_record), and `total` is
    every event the record holds."""

    events: list
    accepted: bool
    messages: str
    early_exits: tuple = ()
    total: int = 0


class Recording(NamedTuple):
    """What path_recorder is handed: where it starts, where it stops, and the
    file of opaque functions."""

    start: str
    stop: str
    opaque: str


def symbols_of(clang_binary: str, demangle: bool) -> list:
    """(offset, name) for every function the binary defines, from its symbol
    table, in the table's order."""
    command = [NM, "--defined-only", "--no-sort", clang_binary]
    if demangle:
        command.insert(1, "--demangle")
    finished = subprocess.run(command, capture_output=True, text=True, check=True)
    symbols = []
    for line in finished.stdout.splitlines():
        parts = line.split(" ", 2)
        if len(parts) != 3:
            continue
        address, kind, name = parts
        if kind not in ("t", "T", "w", "W"):
            continue
        symbols.append((int(address, 16), name))
    return symbols


def names_of(clang_binary: str) -> dict:
    """offset -> the function's name, demangled, for every function the
    binary defines; the first name where several share an offset."""
    names = {}
    for offset, name in symbols_of(clang_binary, True):
        if offset not in names:
            names[offset] = name
    return names


def opaque_prefixes() -> tuple:
    prefixes = []
    for name in LLVM_OPAQUE:
        prefixes.append(f"_ZN4llvm{len(name)}{name}")
        prefixes.append(f"_ZNK4llvm{len(name)}{name}")
    for name in LLVM_DETAIL_OPAQUE:
        prefixes.append(f"_ZN4llvm6detail{len(name)}{name}")
        prefixes.append(f"_ZNK4llvm6detail{len(name)}{name}")
    found = tuple(prefixes)
    return found


def own_name(demangled: str) -> str:
    """The function's qualified name, without its return type or its
    parameters: `std::__introsort_loop` for `void std::__introsort_loop<...>(...)`."""
    text = demangled.replace("(anonymous namespace)", "{anonymous}")
    depth = 0
    start = 0
    end = len(text)
    for position in range(len(text)):
        character = text[position]
        if character == "<":
            depth += 1
        elif character == ">":
            depth -= 1
        elif character == "(" and depth == 0:
            end = position
            break
        elif character == " " and depth == 0:
            start = position + 1
    name = text[start:end]
    return name


def is_opaque_in_cpp_library(demangled: str) -> bool:
    name = own_name(demangled)
    if not name.startswith("std::"):
        return False
    if name.startswith(CPP_OPAQUE_CLASSES):
        return True
    base = name.split("<", 1)[0]
    if base in CPP_OPAQUE_CONTAINERS:
        return True
    last = base.split("::")[-1]
    for word in CPP_OPAQUE_WORDS:
        if word in last:
            return True
    return False


def opaque_offsets(clang_binary: str) -> list:
    """The offsets of every opaque function: LLVM's by their mangled names,
    the C++ library's by their own names."""
    prefixes = opaque_prefixes()
    mangled = symbols_of(clang_binary, False)
    demangled = symbols_of(clang_binary, True)
    if len(mangled) != len(demangled):
        raise RuntimeError("the symbol table read twice gave two lengths")
    offsets = set()
    for index in range(len(mangled)):
        offset, name = mangled[index]
        if name.startswith(prefixes) or is_opaque_in_cpp_library(demangled[index][1]):
            offsets.add(offset)
    found = sorted(offsets)
    return found


def offsets_of(names: dict, prefix: str) -> list:
    """The offsets of every function, every overload, whose name begins with
    `prefix`."""
    offsets = []
    for offset, name in names.items():
        if name.startswith(prefix):
            offsets.append(offset)
    offsets.sort()
    return offsets


def hex_list(offsets: list) -> str:
    words = []
    for offset in offsets:
        words.append(f"{offset:x}")
    text = ",".join(words)
    return text


def recording_of(clang_binary: str, names: dict, work: str, from_the_start: bool = False) -> Recording:
    """The recorder's start, stop and opaque functions; the opaque list is
    written once, into `work`. With `from_the_start` the record begins with
    the file, so the struct's own line is in it: a refusal there (the
    result's __typeof__) was outside the record until run fable1_l08 showed
    18 refusals without a diagnostic (Dee, 2026-10-18: "id like it fixed")."""
    os.makedirs(work, exist_ok=True)
    path = os.path.join(work, "opaque.bin")
    with open(path, "wb") as written:
        for offset in opaque_offsets(clang_binary):
            written.write(OFFSET.pack(offset))
    start = hex_list(offsets_of(names, START_FUNCTION))
    if from_the_start:
        start = ""
    recording = Recording(start, hex_list(offsets_of(names, STOP_FUNCTION)), path)
    return recording


def read_events(path: str) -> list:
    """The events path_recorder wrote: (kind, offset), in order."""
    events = []
    if not os.path.exists(path):
        return events
    with open(path, "rb") as recorded:
        data = recorded.read()
    events = events_of(data)
    return events


def events_of(data: bytes) -> list:
    """The events in a record's bytes: (kind, offset), in order."""
    events = []
    usable = len(data) - len(data) % RECORD.size
    for kind, offset in RECORD.iter_unpack(data[:usable]):
        if kind not in KINDS:
            # a hole of zeros: after a crash, clang's driver starts itself
            # again for its crash report, and that second process opened the
            # file anew while the first still had its buffer (run fable1_l17,
            # `__builtin_fpclassify`); the record ends at the hole, and the
            # crash is read from clang's messages
            break
        events.append((KINDS[kind], offset))
    return events


# A compile of clang's that does not end is stopped after this many seconds
# (run fable1_l105, 21:15 UTC: six compiles of CXXDeleteExpr contexts ran
# for 24 minutes at full CPU and were still going), so one context cannot
# take a whole run; TLP_COMPILE_SECONDS sets it.
COMPILE_SECONDS = int(os.environ.get("TLP_COMPILE_SECONDS", "120"))
STOPPED_MARK = "clang did not finish and was stopped"


class Finished(NamedTuple):
    returncode: int
    stdout: str
    stderr: str


def run_clang(command: list, environment: dict) -> Finished:
    """clang run with the context's command, stopped at COMPILE_SECONDS: a
    compile that does not end is read as refused, with STOPPED_MARK in its
    messages."""
    try:
        done = subprocess.run(command, capture_output=True, text=True, errors="replace", env=environment,
                              timeout=COMPILE_SECONDS)
        finished = Finished(done.returncode, done.stdout, done.stderr)
    except subprocess.TimeoutExpired as stopped:
        stderr = ""
        if stopped.stderr:
            stderr = stopped.stderr.decode("utf-8", "replace")
        finished = Finished(-1, "", f"{STOPPED_MARK} after {COMPILE_SECONDS} s\n{stderr}")
    return finished


TRACE_BYTES = int(os.environ.get("TLP_TRACE_BYTES", str(1024 * 1024 * 1024)))
# 2026-10-20 (runs fable1_l171 to l179): one context's record grew to 3.5 GB
# and filled the instance's 4 GB scratch, so every lane after it failed at
# once. A record over the cap stops its clang; the context is marked stopped.


def run_clang_watched(command: list, environment: dict, record: str) -> Finished:
    """Runs clang as run_clang does, and stops it when its record grows past
    TRACE_BYTES, so one context cannot fill the scratch for every one after."""
    import time
    started = time.time()
    process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, errors="replace",
                               env=environment)
    over = False
    while process.poll() is None:
        if time.time() - started > COMPILE_SECONDS:
            break
        if os.path.exists(record) and os.path.getsize(record) > TRACE_BYTES:
            over = True
            break
        time.sleep(0.25)
    if process.poll() is None:
        process.terminate()
        try:
            process.wait(timeout=10)
        except subprocess.TimeoutExpired:
            process.kill()
            process.wait()
    stdout, stderr = process.communicate()
    if over:
        finished = Finished(-1, "", f"{STOPPED_MARK} record over {TRACE_BYTES} bytes\n{stderr}")
        if os.path.exists(record):
            os.remove(record)
        return finished
    if time.time() - started > COMPILE_SECONDS and process.returncode in (-15, -9):
        finished = Finished(-1, "", f"{STOPPED_MARK} after {COMPILE_SECONDS} s\n{stderr}")
        return finished
    finished = Finished(process.returncode, stdout, stderr)
    return finished


def run_recorded(context: Context, clang: str, recording: Recording, work: str) -> tuple:
    """Runs `clang` (traced_clang) on the context's standard source with our
    setup, recording: (the record's bytes, accepted, clang's messages)."""
    os.makedirs(work, exist_ok=True)
    source = os.path.join(work, "op.c")
    with open(source, "w", encoding="utf-8") as written:
        written.write(standard_source(context))
    record = os.path.join(work, "trace.bin")
    if os.path.exists(record):
        os.remove(record)
    environment = dict(os.environ)
    environment["LP_TRACE_FILE"] = record
    environment["LP_START"] = recording.start
    environment["LP_STOP"] = recording.stop
    environment["LP_OPAQUE"] = recording.opaque
    command = command_for(context, clang, source, os.path.join(work, "op.o"))
    # after a crash clang's driver starts itself again for a crash report;
    # that second process opened the record anew and emptied it (log 487
    # §13, §24), so the crashed contexts had empty paths; without the report
    # the record of the first process stays whole
    command.append("-fno-crash-diagnostics")
    finished = run_clang_watched(command, environment, record)
    data = b""
    if os.path.exists(record):
        with open(record, "rb") as recorded:
            data = recorded.read()
        os.remove(record)
    found = (data, finished.returncode == 0, finished.stderr)
    return found


def trace(context: Context, clang: str, recording: Recording, work: str) -> Trace:
    """Runs `clang` (traced_clang) on the context's standard source with our
    setup, recording from the start of the standard form's function to the
    end of its lowering."""
    data, accepted, messages = run_recorded(context, clang, recording, work)
    events = events_of(data)
    found = Trace(events, accepted, messages, (), len(events))
    return found
