/* path_recorder.c -- traced_clang's recorder (PCHQ plan:
   research/trace_logical_paths/traced_clang, entry path_recorder).

   clang's Sema, AST, Basic and CodeGen libraries are compiled with
   -finstrument-functions, which calls __cyg_profile_func_enter and
   __cyg_profile_func_exit at every function's entry and return, and with
   -fsanitize-coverage=trace-pc-guard, which calls
   __sanitizer_cov_trace_pc_guard on every branch taken. This file answers
   those calls. While recording, it writes one event per call to the file
   LP_TRACE_FILE names: one byte for the kind (1 enter, 2 return, 3 branch)
   and eight for the offset in the binary (the function's start for enter
   and return, the branch's place for a branch).

   Three lists of offsets in the binary steer it:
     LP_START   recording starts at the first entry into one of these
                (hexadecimal, comma-separated; up to 16): trace.py hands it
                Sema::ActOnStartOfFunctionDef, the start of the standard
                form's function.
     LP_STOP    recording stops for good at the first entry into one of
                these, after writing that entry: trace.py hands it
                CodeGenFunction::FinishFunction, which clang calls when the
                standard form's function body is lowered.
     LP_OPAQUE  a file of sorted 8-byte offsets: a function on it, with
                everything it calls, writes nothing. trace.py lists the hash
                tables, allocators and sorts of LLVM and the C++ library,
                whose steps depend on where things sit in memory, not on the
                program.
   With LP_TRACE_FILE unset nothing is written. The file is opened when
   recording starts, never before: after a crash, clang's driver starts
   itself again to write its crash report, and that second process, which
   never reaches the start, would otherwise open the file anew and empty it
   (run elv2_l198).

   Compiled without either instrumentation, so it records nothing of
   itself. */

#define _GNU_SOURCE
#include <dlfcn.h>
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#define NO_RECORD __attribute__((no_instrument_function))
#define LIST_MAX 16
#define BUFFER_BYTES (1 << 24)

enum { EVENT_ENTER = 1, EVENT_RETURN = 2, EVENT_BRANCH = 3 };

static FILE *out = 0;
static const char *trace_path = 0;
static int ready = 0;
static int armed = 0;
static int recording = 0;
static int stopped = 0;
static uintptr_t base = 0;
static uint64_t starts[LIST_MAX];
static int start_count = 0;
static uint64_t stops[LIST_MAX];
static int stop_count = 0;
static uint64_t *opaque = 0;
static size_t opaque_count = 0;
static unsigned long opaque_depth = 0;
static char buffer[BUFFER_BYTES];

NO_RECORD static void finish(void) {
  recording = 0;
  stopped = 1;
  if (out) {
    fflush(out);
    fclose(out);
    out = 0;
  }
}

NO_RECORD static int read_list(const char *list, uint64_t *into) {
  int count = 0;
  const char *place = list;
  while (place && *place && count < LIST_MAX) {
    char *end = 0;
    unsigned long long value = strtoull(place, &end, 16);
    if (end == place) {
      break;
    }
    into[count] = (uint64_t)value;
    count += 1;
    place = end;
    if (*place == ',') {
      place += 1;
    }
  }
  return count;
}

NO_RECORD static void read_opaque(const char *path) {
  if (!path) {
    return;
  }
  FILE *file = fopen(path, "rb");
  if (!file) {
    return;
  }
  fseek(file, 0, SEEK_END);
  long size = ftell(file);
  fseek(file, 0, SEEK_SET);
  if (size > 0) {
    opaque = malloc((size_t)size);
    if (opaque) {
      opaque_count = fread(opaque, 8, (size_t)size / 8, file);
    }
  }
  fclose(file);
}

NO_RECORD static int open_out(void) {
  out = fopen(trace_path, "wb");
  if (!out) {
    stopped = 1;
    return 0;
  }
  setvbuf(out, buffer, _IOFBF, BUFFER_BYTES);
  atexit(finish);
  return 1;
}

NO_RECORD static void set_up(void) {
  ready = 1;
  trace_path = getenv("LP_TRACE_FILE");
  if (!trace_path) {
    return;
  }
  Dl_info info;
  if (!dladdr((void *)&set_up, &info)) {
    return;
  }
  base = (uintptr_t)info.dli_fbase;
  start_count = read_list(getenv("LP_START"), starts);
  stop_count = read_list(getenv("LP_STOP"), stops);
  read_opaque(getenv("LP_OPAQUE"));
  armed = 1;
  if (start_count == 0 && open_out()) {
    recording = 1;
  }
}

NO_RECORD static void write_event(unsigned char kind, uint64_t offset) {
  unsigned char record[9];
  record[0] = kind;
  memcpy(record + 1, &offset, 8);
  fwrite(record, 9, 1, out);
}

NO_RECORD static int is_listed(const uint64_t *list, int count, uint64_t offset) {
  for (int i = 0; i < count; i++) {
    if (list[i] == offset) {
      return 1;
    }
  }
  return 0;
}

NO_RECORD static int is_opaque(uint64_t offset) {
  size_t low = 0;
  size_t high = opaque_count;
  while (low < high) {
    size_t middle = low + (high - low) / 2;
    if (opaque[middle] < offset) {
      low = middle + 1;
    } else {
      high = middle;
    }
  }
  int found = low < opaque_count && opaque[low] == offset;
  return found;
}

NO_RECORD void __cyg_profile_func_enter(void *function, void *call_site) {
  (void)call_site;
  if (!ready) {
    set_up();
  }
  if (!armed || stopped) {
    return;
  }
  uint64_t offset = (uint64_t)((uintptr_t)function - base);
  if (!recording) {
    if (!is_listed(starts, start_count, offset)) {
      return;
    }
    if (!open_out()) {
      return;
    }
    recording = 1;
  }
  if (opaque_depth > 0) {
    opaque_depth += 1;
    return;
  }
  if (is_opaque(offset)) {
    opaque_depth = 1;
    return;
  }
  write_event(EVENT_ENTER, offset);
  if (is_listed(stops, stop_count, offset)) {
    recording = 0;
    stopped = 1;
    fflush(out);
  }
}

NO_RECORD void __cyg_profile_func_exit(void *function, void *call_site) {
  (void)call_site;
  if (!recording) {
    return;
  }
  if (opaque_depth > 0) {
    opaque_depth -= 1;
    return;
  }
  write_event(EVENT_RETURN, (uint64_t)((uintptr_t)function - base));
}

NO_RECORD void __sanitizer_cov_trace_pc_guard_init(uint32_t *start, uint32_t *stop) {
  static uint32_t count = 0;
  if (start == stop || *start) {
    return;
  }
  for (uint32_t *guard = start; guard < stop; guard++) {
    count += 1;
    *guard = count;
  }
}

NO_RECORD void __sanitizer_cov_trace_pc_guard(uint32_t *guard) {
  (void)guard;
  if (!recording || opaque_depth > 0) {
    return;
  }
  write_event(EVENT_BRANCH, (uint64_t)((uintptr_t)__builtin_return_address(0) - base));
}
