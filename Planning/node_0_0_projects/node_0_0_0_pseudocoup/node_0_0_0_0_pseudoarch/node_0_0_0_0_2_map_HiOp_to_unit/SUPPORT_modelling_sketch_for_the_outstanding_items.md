---
id: hq.projects.pseudocoup.pseudoarch.map_HiOp_to_unit.support.modelling_sketch_for_the_outstanding_items
status: draft
---

# SUPPORT — modelling_sketch_for_the_outstanding_items

A page of sketches: the modelling that would close the open items of
`node_0_0_0_0_2_4_extract_lang_vocab/SUPPORT_gnu_c_vocab_what_is_missing.md`
(items 1 to 38). Written 2026-10-12 by Claude (Opus 5.5) at Dee's request:

> id also like a sketch of the modelling we would have to do to solve the
> outstanding items.

The goal is Dee's, the same day:

> faithful AutoPoly — meaning that coding components of any GNU-C program has
> polyfill that is computationally equivalent. i would settle for just RISCV if
> it makes a difference

My reading of "computationally equivalent": a polyfill gives what the
machine's own Unit gives, on every input, machine by machine. The sketches are
mine. Each is a few lines of pseudo-code, with the items it would close and
what is already known. 

## Read this first: the plan's design already covers most of the eight (2026-10-13, 

Dee, 2026-10-13: "we are going as far to emulate the very RISC-V arch-opcodes
by slicing GMP and modeling by-hand the handful of basic operations GMP uses to
model arch-opcodes. omg. you arent familiar with the entire project."

The sketches below were written as if each machine's behaviour needed its own
model. The plan already holds it. `pseudoarch` has one model, RISC-V's, and
every LoOp's Lean is either Sail's body or SoftFloat sliced over the 24 GMP
primitives (built in research, Step 1.2, 2026-09-17). AutoPoly emulates each
LoOp from a language's Units proven equal to those primitives (its CORE). So
a polyfill gives what riscv64 gives, edge cases included.

| model | under the design |
|---|---|
| 1. places | the ledger's: where a holder lives in the target language; values never depend on it (run elv2_l152) |
| 2. what a Unit means | settled (logs 437, 440) |
| 3. holders per machine | riscv64's facts are in its Units; the other machines only serve the all-three-architectures rule |
| 4. calls | mapping: the routines' riscv64 code, lowered; system calls are where the emulation meets the environment |
| 5. traps | in the LoOps (Sail): riscv64's divide gives -1 and never traps; a holder read before its first write is the ledger's (Dee's definition) |
| 6. data | the ledger's |
| 7. control | Dee's design (logs 395 to 399) |
| 8. threads | one thread: in the LoOps; what other harts see (RVWMO): the one thing left |

## Read this first: most of these models are mapping (2026-10-12, 

Dee, later the same day:

> if we made a mapping from high_level --to--> low_level for every high level
> building block, the intermediate stage wouldnt require a model.

> the function wrapper was only meant to contain the arch-opcodes associated
> with the HiOp ... its just for the sake of isolating the associated
> arch-opcodes.

The argument holds. Running the lowerer gives each block's words, so nothing
between the two levels needs a model. Where a block's words are a call, the
called routine's words are part of the block's low level, and each routine is
mapped once. The wrapper only marks where a HiOp's words start and end, so the
Unit is the HiOp's own words (my reading, asked in log 437: its fetches and
store are in, the wrapper's frame is out). Under both, the models below sort
into what each item really needs.

Dee answered the question of log 437 the same day : "if the
answer being yes reduces work, i dont see why we wouldnt." It does, so the
fetches and the store are the HiOp's own words, and items 16 and 27 to 30 are
closed in the list. Log 440 also shows that this is September's canon form
(log 141), with the compiler writing the loads and the store.

Table 0. The list's 39 items, by what each needs (log 437, Table 1).

| needs | items | count |
|---|---|---|
| mapping: lower each block in the contexts and flags a program uses, follow its calls, read declarations' bytes from the object file | 3, 5, 10, 11, 12, 13, 14, 15, 17, 18, 19, 20, 21, 32, 36, 37, 39 | 17 |
| nothing more: the words carry it | 16, 27, 28, 29, 30, 31 | 6 |
| a model of the machine level itself: traps, the rounding mode, linker symbols, threads | 1, 2, 22, 33, 34, 38 | 6 |
| a fix to our own tools | 6, 7, 9, 23, 24, 25 | 6 |
| nothing: the all-three-architectures rule | 4, 8, 35 | 3 |
| done | 26 | 1 |

So Model 2 is settled by Dee's word, Model 3 is carried by the words, and
Models 4 and 6 are mapping. Models 5 and 8 are the machine level. Model 1 is a
shortcut for mapping, and Model 7 is Dee's design. The sketches below stay as
the record of what each part involves.

Figure 1. Where the eight models meet. It shows which model feeds which step;
it does not show order or cost.

```
a GNU C program
 ├─ HiOp variant: operator + holders
 │   + where each operand lives      model 1
 │   + what each holder is, per
 │     machine and build flags       model 3
 │   lowered per machine to words    (done, log 405)
 │   read as a meaning               model 2
 │     + the routines it calls       model 4
 │     + the traps it can raise      model 5
 │     + what other threads see      model 8
 │   → a Lean term per machine
 ├─ declarations → data              model 6
 └─ statements → nested calls        model 7
a polyfill in language B ≡ that Lean term
```

Every open item of the list (38 of its 39; item 26 is done) needs one of three
things. 29 need a model: they sit in the eight models below. 6 need a fix to our
own tools, with no model of C. 3 need nothing: the all-three-architectures rule
sets them aside. They are listed at the end, under "Not a model".

Run elv2_l151  tested the models by running compiled code on the
three machines. Each "Tested" line below gives what it checked. 51 of 51
results agreed with the predictions written before the run.

## Model 1. Where each operand lives (items 12, 13, 22)

Block A.

```python
def unit_words(hiop, places, machine):
	words = frame_start(machine)
	for operand in hiop.operands:
		words.extend(fetch(places[operand], machine))
	words.extend(operation(hiop, machine))
	words.extend(store(places["result"], machine))
	words.extend(frame_end(machine))
	return words
```

- A place is one of the six kinds of place, or a constant written into the
  operation's own word (item 14).
- A symbol's address is filled in by the linker (item 22): in the Lean term
  it is a named unknown.
- Known: this rule predicts 11,994 of 13,026 functions word for word (log 433).
- Tested (run elv2_l151): a global plus a local gives 5 on all three; a place
  changes a Unit's words, not its value.
- Tested by value (run elv2_l152, : all 13,026 functions of log
  433, 4,342 per machine, on 4 pairs of inputs each, give the predicted value:
  52,104 of 52,104 checks. That includes the 1,032 whose words this model did
  not predict (bit-fields 760, x86-64's division and shifts 200, aarch64's
  thread-local functions 72): its misses are in the words only.
- A limit of that run (log 443): its inputs fit the 13-bit bit-fields, so it
  never stored a value that does not fit. Such a value is cut to the width:
  the width belongs to the holder's type, not its place (item 40).

## Model 2. What a Unit means: its words, or its whole function (items 16, 27 to 30)

Block B.

```python
def meaning(held_function, machine):
	before = machine_state()
	after = run(held_function, before, machine)
	change = visible_change(before, after, convention(machine))
	return change
```

- `run` is the machine's own model. For riscv64 that is Sail's.
- `visible_change` keeps only what the calling convention lets the caller
  see: the memory the function was handed, and its result.
- Frame words, register choice, x86-64's folded fetch, the bit-field merges
  and aarch64's choice of selector all happen inside the function, so this
  reading needs no model of them. The other reading cuts each HiOp's own
  words out, and then needs every machine's word rules.
- Which reading a Unit takes is Dee's (log 434 §3.2, queued).
- Settled 2026-10-12 at Dee's word : the wrapper only
  isolates a HiOp's words, and a Unit is the HiOp's operand fetches, its
  operation and its result's store; the frame and the copy of `p` are cut
  (`op_1970` on riscv64: 4 of its 15 words). So neither reading above is
  needed, and items 16 and 27 to 30 are closed.

## Model 3. What each holder is, per machine and build flags (items 15, 31, 37)

Block C.

```python
def value_of(holder, stored_bytes, machine, flags):
	facts = description(machine, flags)
	form = facts.form_of(holder)
	value = decode(form, stored_bytes)
	return value
```

- `description` reads clang's own answer: its predefined macros for the
  machine and flags (run elv2_l149). `__CHAR_UNSIGNED__` gives `char`'s sign;
  `__LDBL_MANT_DIG__` gives `long double`'s form; `__WCHAR_TYPE__` gives
  `wchar_t`.
- A program's own flags change the facts (`-funsigned-char`, `-fshort-enums`),
  so the flags are an input (item 37).
- Item 15: where clang fuses `a * b + c`, that is one HiOp variant of its own,
  with its own Unit; it is not `*` then `+`.
- Tested (run elv2_l151): `char` 0xC8 + 1 gave 201, -55, 201; `1 + 2^-70` on
  `long double` kept the small part on riscv64 and aarch64 only; `L'\xffffffff'`
  was negative on riscv64 and x86-64 only; `a * b + c` was fused on riscv64 and
  aarch64 only. All as predicted.

## Model 4. The routines a Unit calls (items 3, 10, 21, 32)

Block D.

```python
def meaning_of_call(callee, arguments, machine):
	rules = convention(machine)
	place_arguments(arguments, rules)
	body = body_of(callee, machine)
	output = run(body)
	result = take_result(output, rules)
	return result


def body_of(callee, machine):
	body = environment(callee)
	if callee in program_functions:
		body = units_of(callee, machine)
	if callee in compiler_rt:
		source = source_of(callee)
		lowered = lower(source)
		body = units_of(lowered, machine)
	return body
```

- `convention`: each machine's calling convention. Run elv2_l149 found 24 of
  the 52 holder types passed or returned differently on the three machines.
- compiler-rt's routines (`__addtf3`, `__divti3`) are C, so the same pipeline
  lowers them (item 32; log 434 §3.4).
- `environment`: the C library and the kernel (items 3 and 10). The C library
  is mostly C too; the kernel's calls are the edge of the model.
- Tested (run elv2_l151): compiler-rt's `__addtf3`, `__eqtf2`, `__divti3`, built
  from source by the same clang, gave the predicted values on all three, and
  `__addtf3` reads the machine's rounding mode itself (`riscv/fp_mode.c`).

## Model 5. Traps and machine state, where C gives no result (items 33, 38)

Block E.

```python
def outcome(unit, inputs, machine):
	result = run(unit, inputs, machine)
	if result.is_trap:
		stop = signal_of(result.trap)
		return stop
	value = result.value
	return value
```

- Where C gives no result, a machine does one of three things:
  - **a value of its own:** riscv64's `a / 0` is -1, and float-to-int gives
    each machine's own value. The Unit is the meaning; nothing more is needed.
  - **a trap:** x86-64's `a / 0`, or any machine reading a bad address. The
    operating system stops the program with a signal (`SIGFPE`, `SIGSEGV`), and
    a polyfill must stop the program with the same signal.
  - **whatever was already there:** `int n; ... n ...` reads a stack slot that
    nothing wrote. What "equivalent" means there is Dee's to say.
- Where to look: the 19 checks of clang's group "undefined" (`Sanitizers.def`)
  name the operations.
- Tested (run elv2_l151): `(int)` of a NaN gave 0x7FFFFFFF, -0x80000000, 0;
  `7 / 0` gave -1 on riscv64, 0 on aarch64, and stopped x86-64 with SIGFPE
  (exit 136); rounding up and to nearest changed one `double` add on all three.
- Item 38 is the same kind of thing: a float Unit reads the rounding mode from
  a machine register and sets flags there (riscv64's `dyn` reads `fcsr`). So
  `run` takes that register as an input and gives it back as an output.

## Model 6. Data: declarations, layouts and attributes (items 5, 14, 17 to 20, 36, 39)

Block F.

```python
def place_of(declaration, machine):
	layout = lay_out(declaration, machine)
	place = symbol_or_stack_place(layout)
	return place
```

- `lay_out` is log 385's 22 rules, with a column per machine. Run elv2_l149
  found the machines' layouts differ: aarch64 aligns a struct to its unnamed
  bit-fields, and x86-64 aligns global arrays of 16 bytes or more to 16
  (item 36).
- Attributes (item 39) belong here: one of a declaration's contexts. Of the
  attributes a C program can write, 122 are read by clang's lowering code.
- Tested (run elv2_l151): `sizeof` of `struct { char a; int : 0; char b; }` was
  5, 5, 8, as predicted.

## Model 7. Control: statements as nested calls (item 11)

Block G.

```python
def StmtExpr(body):
	for part in body[0:-1]:
		run(part)
	value = run(body[-1])
	return value
```

- Dee's design of logs 395 to 399: a rich HiOp is a function of its bodies.
  A statement expression `({ a; b; })` is one more of them.
- Tested (run elv2_l151): `({ a; b; })` gave `b` on all three.

## Model 8. Threads: what an atomic HiOp promises (items 1, 2, 34)

Block H.

```python
def meaning_of_atomic(unit, machine):
	effect = meaning(unit, machine)
	order = ordering(unit, memory_model(machine))
	promise = (effect, order)
	return promise
```

- `effect` is Model 2's, in one thread. A fence's effect is nothing.
- `order` is what the words promise other threads under the machine's memory
  model: `fence r, rw` on riscv64, `dmb ishld` on aarch64, no word at all on
  x86-64 (log 434 §2.4).
- A polyfill must give the same effect, and an order at least as strong in its
  own language.
- Tested (run elv2_l151): a fence between a store and a load left the value
  as it was, on all three. The order between threads was not tested: that
  needs two threads and a memory model.

## Just riscv64, or all three

Table 1. What each model needs per machine, and what riscv64 alone saves.

| model | per machine, from what clang gives | needs a model of the machine itself |
|---|---|---|
| 1. places | yes | no |
| 2. meaning | the words, lowered per machine (done) | yes: a Lean model per machine; the project has riscv64's (Sail) only |
| 3. holders and flags | yes: clang's macros (run elv2_l149) | no |
| 4. calls | yes: clang's calling conventions (run elv2_l149) | no |
| 5. traps | | yes: which words trap, per machine |
| 6. data | yes: clang's layouts (run elv2_l149) | no |
| 7. control | the same on every machine | no |
| 8. threads | | yes: a memory model per machine |

- So riscv64 alone saves two machine models in Lean (x86-64 and aarch64), their
  trap rules, and their memory models. The rest is per-machine data that clang
  already gives, and the automation reads it three times, once per machine.
- My reading, not checked: Sail models of Arm and x86 exist upstream. Whether
  Sail's Lean output works for them is not known. `~/Programming/SOURCES/`
  holds an x86-64 semantics in K (`X86-64-semantics`), which is not Lean.

## Not a model

- A fix to our own tools, needed, with no model of C: items 6, 7, 9, 23, 24
  and 25 (re-run the trace over more holders, print its messages in full, write
  `extract()`, fix the riscv64 reader, settle the trace's read record, sort 31
  builtins).
- Nothing, unless the rule changes: items 4, 8 and 35, which the
  all-three-architectures rule sets aside.
- Done: item 26, the comparison with clang's and LLVM's lists (log 436).
