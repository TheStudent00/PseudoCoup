---
id: hq.projects.pseudocoup.hub.autopoly.support.riscv64_ordering_per_target_language
status: draft
---

# SUPPORT — riscv64_ordering_per_target_language

What a riscv64 LoOp promises other threads, and how each of this line's
twelve languages keeps that promise when AutoPoly runs the LoOp in it. Written
by hand, 2026-10-13, by Claude (Opus 5.5), 

> same with this. if you can do them by hand. do them please.

the owner placed this outside the Lean proofs (log 447 §5): "its more of an
infrastructure thing no?" Sail's definitions follow one hart, and in one
thread an ordering word changes nothing, so its whole meaning is what other
threads may see.

**What breaks in transpilation, and for whom.** Only a program with two or
more threads sharing memory: for instance, two threads bumping one counter
with `atomic_fetch_add(&hits, 1)`. If the target language lets its threads
reorder memory more than riscv64 allows (RVWMO, riscv64's memory model), one
thread can see a value it could never see on riscv64. A program with one
thread loses nothing.

**The rule (the owner, log 447):** each target keeps every order riscv64 keeps, or
a stronger one. Stronger is always correct; it only costs speed.

## 1. What each riscv64 word promises

Table 1. riscv64's words that order memory, what each promises other
threads, and the C11 order clang writes it for. The orders and words are read
from run elv2_l158 (`Research/lower_HiOp/out/samples_l157/atomics_riscv64.txt`:
20 builtins held by hand, 37 standard functions, all lowered and cut).

| riscv64 word | what other threads may count on | clang writes it for |
|---|---|---|
| a plain load or store (`lw`, `sw`) | one address is seen in one order; a load that a later access depends on stays before it | a relaxed load or store |
| `fence r, rw` | earlier loads come before every later access | acquire: after an acquire load |
| `fence rw, w` | every earlier access comes before later stores | release: before a release or seq_cst store |
| `fence.tso` | both of the above; a store may still pass a later load | an acq_rel fence |
| `fence rw, rw` | every earlier access comes before every later one | a seq_cst fence; before a seq_cst load; after a seq_cst store |
| `amoadd.w` and the other AMOs, plain or with `.aq`, `.rl` or `.aqrl` | one read-change-write no other thread can split; `.aq`: nothing later moves before it; `.rl`: nothing earlier moves after it; `.aqrl`: both | relaxed, acquire, release, acq_rel and seq_cst |
| `lr.w` … `sc.w`, a pair in a loop | a read that reserves its address, then a write that succeeds only if no other thread wrote there since | compare-and-exchange, `nand`, and a byte-sized exchange (riscv64 has no AMO for these) |
| `fence.i` | this thread's later instruction fetches see its own earlier stores (code written while running) | not written by clang for C11; reached through the C library's `__riscv_flush_icache` |

- The seq_cst store: clang 21 writes `fence rw, w`, the store, then
  `fence rw, rw` (seen in elv2_l158; I had predicted no trailing fence).
- A byte-sized exchange (`__atomic_test_and_set`): an `lr.w`/`sc.w` loop on
  the 4-byte word holding the byte (seen in elv2_l158; I had predicted
  `amoor.w`).

## 2. How each target language keeps it

Table 2. For each of the twelve languages (log 287 §0): how threads share
memory, and what keeps each row of Table 1. "One thread at a time" means
AutoPoly runs all of the program's threads inside one target thread, taking
turns, so every access happens in one order and every fence is already kept.

| language | shared memory, plain loads and stores | a fence | an AMO | an LR/SC pair |
|---|---|---|---|---|
| c | `atomic_load_explicit(acquire)`, `atomic_store_explicit(release)` | `atomic_thread_fence` with Table 1's order | `atomic_fetch_add_explicit` and its family, same order | `atomic_compare_exchange_strong_explicit` |
| cpp | `std::atomic_ref` (C++20), `load(acquire)`, `store(release)` | `std::atomic_thread_fence` | `fetch_add` and its family | `compare_exchange_strong` |
| csharp | `Volatile.Read`, `Volatile.Write` | `Interlocked.MemoryBarrier()` for every fence (a full fence, so at least as strong) | `Interlocked.Add`, `Exchange`, `And`, `Or`; `xor`, `max`, `min`, `nand` by a `CompareExchange` loop | `Interlocked.CompareExchange` |
| dart | isolates share no memory: one thread at a time | kept | kept | kept |
| go | `sync/atomic` for every shared access (sequentially consistent) | nothing more is needed | `atomic.AddInt32`, `SwapInt32`, `AndInt32`, `OrInt32`; the rest by a `CompareAndSwapInt32` loop | `CompareAndSwapInt32` |
| java | a `VarHandle` on an `int[]`: `getAcquire`, `setRelease` | `VarHandle.acquireFence()`, `releaseFence()`, `fullFence()` | `getAndAdd`, `getAndSet`, `getAndBitwiseAnd`/`Or`/`Xor`; `max`, `min`, `nand` by a `compareAndExchange` loop | `compareAndSet` |
| javascript | a `SharedArrayBuffer`, every access by `Atomics.load` and `Atomics.store` (sequentially consistent) | nothing more is needed | `Atomics.add`, `sub`, `and`, `or`, `xor`, `exchange`; `max`, `min`, `nand` by an `Atomics.compareExchange` loop | `Atomics.compareExchange` |
| php | no threads sharing memory: one thread at a time | kept | kept | kept |
| python | one thread at a time (simplest, and right under the global lock and without it) | kept | kept | kept |
| ruby | one thread at a time (threads take turns under the global lock; Ractors share no memory) | kept | kept | kept |
| rust | `AtomicU32` and `AtomicU64` over the shared memory, `Ordering::Acquire` and `Release` | `std::sync::atomic::fence` | `fetch_add` and its family, `fetch_max`, `fetch_min`, `fetch_nand`, `swap` | `compare_exchange` |
| swift | `Atomic` (the Synchronization module, Swift 6), `load(ordering: .acquiring)`, `store(ordering: .releasing)` | `atomicMemoryFence(ordering:)` | `wrappingAdd`, `bitwiseAnd`/`Or`/`Xor`, `exchange`; the rest by a `compareExchange` loop | `compareExchange` |

- Why plain loads and stores of shared memory become acquire and release
  where threads really run together: in c, cpp, rust and swift an unordered
  race between threads has no meaning at all, and in java and csharp it may
  reorder more than RVWMO does. Acquire and release are stronger than RVWMO's
  plain order, so they are always correct; they cost speed, which a run per
  language would measure.
- Why a compare-and-exchange can stand for an LR/SC pair: clang writes the
  pair only as a loop that computes a compare-and-exchange or a
  read-change-write, and for those loops the result is the same. A bare pair
  could fail where a compare-and-exchange succeeds (another thread writing the
  same value back), but a bare pair comes only from `asm`, which is out by
  the all-three-architectures rule.
- `fence.i`: when AutoPoly reads each instruction from the program's memory
  as it runs it, nothing is needed; when it keeps decoded instructions, it
  drops them at a `fence.i` (my reading).

**Status of each row.** The c row is clang's own mapping, read backwards from
run elv2_l158 (Table 1). The other eleven rows are my reading of each
language's documentation; no run has checked them.
