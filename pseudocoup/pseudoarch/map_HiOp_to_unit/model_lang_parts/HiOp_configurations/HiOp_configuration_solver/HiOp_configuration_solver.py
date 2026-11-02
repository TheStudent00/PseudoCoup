"""HiOp_configuration_solver -- the owner's method for finding each listing's
configuration by trying arrangements of its components on the lowerer, not
by reading the lowerer's code. Steps 1 to 4, the upgrades of 
Table 4 (rules 63 to 74), the fixes after the first small run (rules 75 to
80), and what the wide run adds (rules 81 to 85). Built as configuration_brute_force ; named
dependent_HiOp_solver by the owner and moved into extract_lang_vocab on 2026-10-11
; renamed HiOp_configuration_solver the same day, at the owner's
choice of the name Claude proposed in .

Plan node: Planning/node_0_0_projects/node_0_0_0_pseudocoup/node_0_0_0_0_pseudoarch/
node_0_0_0_0_2_map_HiOp_to_unit/node_0_0_0_0_2_4_extract_lang_vocab/
node_0_0_0_0_2_4_3_HiOp_configuration_solver (Block A in section 2, the steps in
section 3, what steps 2 to 4 add in section 3.1, the checks in section 4).
The method in full: 
elv2_l122. Its runs and records: Research/extract_lang_vocabulary/
HiOp_configuration_solver/ (lanes_elv2/, and out/, where every record is written).

    python3 HiOp_configuration_solver.py <work folder> <part>     inside a run, with clang 21.1.8 on PATH

The words.

    listing       one written form of a HiOp, as kinds_forms.json holds it in
                  its `template` key: `if (a) b; else c;`
    component     one written piece of a listing, with what it takes: `if(a)`
                  and `else`
    inert call    a call to a function declared and never defined: `inert_0()`
    arrangement   a group's components and inert calls, one per line, in some
                  order, each line at a level; a line one level deeper than
                  the line above is held in that line's body
    kept          an arrangement the lowerer accepts: what works
    prefix        the first lines of an arrangement, built one line at a time
    part          the groups one run arranges (rule 36)
    fill          how a listing's values are written: `int` inert calls, typed
                  inert calls, or constants (rule 32)
    run           (signal 2) one program run once, in a process of its own,
                  with a chosen schedule for each inert call (rule 49)
    body          (signal 2) a part that runs behind the branch or again, and
                  is not tested (rule 52)
    context       the function around a listing alone, with what it declares
                  and the names it offers (rule 64): `void f(void)` until now
    stand-in      a definition written for a function the linker does not
                  find, so the program links and runs (rule 65)
    label table   the table of two label addresses a run of `goto *a;` jumps
                  through (rule 67)
    X set         the values probed for one form, as the probe design of
                  2026-08-21 settled them, clipped to an inert call's type
                  (rule 71)
    sort          what a refusal is about: where a component stands, the test
                  program, the listing as written, or unsorted (rules 72 and
                  77)

Step 1 ran Block A's lines 1, 2, 3, 4 and 6 on four groups chosen by hand,
with signal 1 only. Steps 2 to 4 (the plan's section 3.1, built together) add
signal 2 (line 5), typed inert calls, the listings that are expressions,
trimming (step 3), and every listing in groups chosen by rule (step 4). Rules 1
to 27 are step 1's; where steps 2 to 4 change one, it says so and names the
rule that does. Rules 28 to 62 are steps 2 to 4's. Rules 63 to 74 are the
upgrades of , each naming the
row it carries; where one changes an earlier rule, that rule names it. Rules 75
to 80 are the fixes after the first small run (elv2_l132, , each
naming the rule it changes, and that rule names it. Rules 81 to 85 come with
the wide run , in the same way. Rule 86 comes with part (b), when
the standard-form began to take its routing from this record .

read_components: each listing's components, read from its text
 1. Which listings: in step 1, the 7 that the four groups name (GROUPS), each
    found in kinds_forms.json by its `template` text. Steps 2 to 4: rule 28.
 2. Placeholders: a letter standing as a word of its own. `a` to `h` hold
    values, `m` and `n` are names, `T` to `W` are types: the placeholder
    letters of Projects/PseudoArch/map_HiOp_to_unit/extract_lang_vocab
    (PLACEHOLDER), typed here.
 3. The text is cut into pieces, kept as written: words, spaces, `...`, and
    single marks (any other character).
 4. Held: a value placeholder outside parentheses whose next piece, past
    spaces, is `;` is a statement. It is what the component before it holds,
    and the `;` is its own. Steps 2 to 4: the lowerer has the last word on
    each (rule 29).
 5. Component: the text from the listing's start, or from the end of a held
    statement, up to the next held statement or the listing's end, is one
    component, when it holds more than spaces. A `;` that ends a component
    holding nothing is that statement's end, kept apart from what is written.
    Steps 2 to 4: a block is one component (rule 30).
 6. Taken: every placeholder left in a component is what it takes: inside its
    parentheses (`if (a)`), between `case` and its `:`, or a name (`goto m`,
    `m:`).
 7. Named: a component's keyword is its first word that is not a
    placeholder. The component is named by its keyword followed by what it
    takes, written from its first placeholder to its last, in parentheses:
    `if(a)`, `for(a; b; c)`, `goto(m)`. It is named by its keyword alone when
    it takes nothing: `else`, `break`. A component with no keyword is a
    label, named as written: `m:`. Steps 2 to 4: rule 31.
 8. The check: the 7 listings give exactly the components of the plan's
    section 3 (EXPECTED_COMPONENTS, typed from it): the same names, in the
    same order, the same ones holding a body. A difference stops the run.

arrange: every arrangement of each group
 9. A group's lines: its listings' components, as read, and its inert calls:
    one before, one after, and one for each component that holds a body.
10. Every distinct order. Inert calls are alike, so orders that only swap
    them count once; the components are each different. Steps 2 to 4: two
    copies of one component are alike too (rule 37).
11. Every indentation. The first line is at level 0. A line may go one level
    deeper than the line above only when the line above is a component that
    holds a body. It may come back out to any lower level.
12. Made in a fixed order: at each place an inert call first, then the
    components as read; at each line the lowest level first. Numbered from 1
    in each group.
13. the owner's order: the `if` group's arrangements with the lines in the owner's order
    (DEES_ORDER) are marked, and the owner's three examples among them by their
    levels (DEES_EXAMPLES).
14. The check: 280, 60, 420 and 60 arrangements (EXPECTED_ARRANGEMENTS, from
    the plan's section 3), 820 in all; 12 in the owner's order; the owner's 3 examples
    found. Any other count stops the run. Steps 2 to 4: made again untrimmed
    in the part step_1_again, where the same count is checked.

write_programs: each arrangement written in GNU C
15. Only GNU C is written. Another language stops the run.
16. Inert calls are numbered so no two share a name: the lines that are inert
    calls first, in line order, as the owner numbers them (`inert_0()` to
    `inert_3()` in the `if` group); then each value a component takes, in
    line order, since a component's value becomes an inert call too. Each is
    declared `int inert_<k>(void);`. Steps 2 to 4: a value written as a
    constant takes no number (rule 35), a typed one is declared as its fill
    says (rule 34), and every number the group uses is declared (rule 44).
17. A component is written as its listing writes it, each value it takes
    replaced by its inert call: `if (a)` becomes `if (inert_4())`. A name
    stays as written: `goto m`. A component that holds a body is followed by
    its held lines inside `{ }`, and by `{ }` when it holds nothing. A
    component that holds nothing ends with its listing's own `;`: `break;`,
    `goto m;`. Steps 2 to 4: each value as the listing's fill writes it
    (rules 32 to 35); a type as its holder (rule 34).
18. The program: the declarations, then `void f(void) {`, the lines, each
    indented four spaces more for each level, then `}`.
19. Typed here, not read from a listing: `{ }` for a held body (how C writes
    a held body, one of the handful each language needs by hand, 
    section 2); the inert call and its declaration, returning `int` so it can
    stand as a test; and the function `void f(void)` around the lines.

ask_the_lowerer: signal 1
20. Each program is written to a file of its own in the work folder and given
    to clang alone, run in that folder:
    `clang -std=gnu17 --target=riscv64-unknown-linux-gnu -fsyntax-only <file>`.
    Steps 2 to 4: in batches (rule 46), each program still its own
    translation unit, and every 200th asked alone as here.
21. Accepted when clang exits 0; refused otherwise. For each refusal the
    first line of clang's output that holds `: error: ` is kept as its first
    error, with clang's exit code. Steps 2 to 4: rule 46.

run_with_chosen_returns: signal 2
22. Step 1: not built. Steps 2 to 4: rules 47 to 53.

classify: what the kept arrangements show, in each group
23. The kept arrangements of a group are those clang accepted; every count
    below is out of them.
24. Holds a body: for each component read as holding a body (rule 4), the
    kept arrangements where it holds at least one line (the line after it is
    one level deeper), and those where it holds nothing. A component read as
    holding nothing is never given a held line (rule 11), so the kept set
    cannot show a body in it.
25. Right after: for each ordered pair of the group's components, X then Y,
    the kept arrangements where Y is the first line after X's held lines and
    stands at X's level. Y must come right after X when that is so in every
    kept arrangement.
26. Where each stands: for each component that holds nothing (in step 1
    `break`, `continue` and `goto(m)`), the components whose held lines it
    stands in, outermost first, with its level, tallied over the kept
    arrangements; "only inside" names the components it stands in in every
    kept arrangement. And, for each other component of its group, the kept
    arrangements where that one comes before it and those where it comes
    after (`m:` before or after `goto(m)`). Steps 2 to 4: rule 54.
27. Step 1's check, against what was already known: the reader of
    dependent_HiOp_reader and C's grammar as each listing writes it, each
    arrangement's answer predicted from them. Steps 2 to 4: rule 57.

Steps 2 to 4.

read_components
28. Which listings: every listing clang parsed as written (`parsed_as_written`)
    in kinds_forms.json, label_address.json (`&&m`) and kinds_builtins.json;
    the others are counted, with that reason, and not used. Rule 63 replaces
    this filter: every listing clang accepted is used. A listing is a
    statement listing when its kind (its `name` up to the first `.`) ends in
    `Stmt`, as DRY_mask_maker's is_statement reads it; the rest are
    expressions. A part reads every listing's components; it asks the
    lowerer about the listings it uses (rule 36).
29. Held or taken, asked of the lowerer: for each value placeholder rule 4
    reads as held, the listing alone (rule 33) is written twice, with that
    placeholder once as `inert_k();` and once as `{ inert_k(); }`. The same
    answer both times (both accepted, or both refused with the same first
    error message) reads it held; any other answer reads it taken, and the
    listing is read again with it taken: `a` of `goto *a;` and of
    `return a;`. Rule 68: asked only where tree-sitter cannot answer, and for
    every 10th listing it can, as a check.
30. A block: a first component written only `{`, and a last one written only
    `}` holding nothing, are how C writes a held body: the two make one
    component, written as nothing, named `{ }`, holding a body; a held
    statement with only spaces before it, back to the held statement before,
    is held by the same component (`{ a; b; }` holds `a` and `b`).
31. Named (rule 7, extended): what a component takes is written as inside its
    parentheses, all of it, when it has parentheses (`for(; a; b)`), and from
    its first placeholder to its last when it has none (`goto(m)`); the marks
    between its keyword and what it takes, other than spaces and `(`, stay in
    its name (`goto*(a)`). A component of an expression listing standing as
    a line ends with `;` (`&&m;`).
32. The fill, asked of the lowerer, tried in this order: `int` (each value an
    `int` inert call, as in step 1), typed (rule 34), by address (each value an
    inert call of its holder, `int` when it has none, returned by address and
    read through it, so it can be assigned: `(*inert_k())++`), constant (rule
    35). A listing's fill is the first the lowerer accepts for it alone (rule 33);
    for a listing refused alone under every fill, the first the lowerer
    accepts with the listing held in a holder listing (rule 39), its own text
    held by the holder's first component that holds a body, the holders tried
    in their order in kinds_forms.json; a listing refused everywhere keeps
    `int` and is counted as refused under every fill. Rules 66 (one
    placeholder as a constant), 64 (the other contexts) and 72 (refusals for
    the test program) come between the two.
33. Alone: an inert call, the listing's own text with every slot filled, what
    the listing needs (rule 40) each as its own text, and an inert call, each
    a line of `void f(void)`. In a listing's own text a held statement is an
    inert call statement, `inert_k();`; its slots are numbered after the two
    inert call lines, in the order written; an expression ends with `;`.
34. Typed: each value or type placeholder takes its holder from the listing's
    `holders` (kinds_forms.json), one per placeholder that is not a name, in
    the order written; `bool` is written `_Bool`. holders.json names each
    holder's class: an integer class (INTEGER_CLASSES) is written `int`, as
    in step 1; a pointer or floating class (VALUE_CLASSES) is returned by
    value, its type taken through a comma so qualifiers come off
    (`__typeof__(((void)0, (*(char * *)0)))`); any other class (arrays,
    records, vectors, `_Atomic`, `_Complex`, `__builtin_va_list`, `__fp16`,
    `__bf16`) is returned by address and read through it, `(*inert_k())`. A
    type placeholder is written as its holder under every fill. The composite
    holders (`struct S`, `fnptr`, `arr4`, ...) are declared at the top of
    every program that uses a typed fill, a fill by address or a type
    placeholder, as DRY_mask_maker's C_HELD_TYPES declares them, read from its
    source, not imported. A builtin that is a library function is declared
    before its listing's own text as library_declarations.json (beside
    kinds_forms.json) declares it, found by the listing's `kept_as` name:
    clang accepts a library builtin only after its declaration.
35. Constant: each value of the k-th component, in line order, whose fill is
    constant, is written k, from 0 (`case 1 ... 1:`); in the groups marked
    "the same value", every constant is 0. A constant takes no inert number.

arrange
36. A part names the groups one run arranges:
      step_1_again     step 1's four groups, untrimmed, every program also
                       asked alone (rule 46), and checked against step 1's
                       record: the same programs and answers;
      step_1_trimmed   the same four groups, trimmed (rule 38): it must keep
                       step 1's 185 of 820, by levels and lines;
      listings         every listing alone (rule 33), each its own group of
                       one arrangement;
      switch_untrimmed and switch_trimmed: `switch (a) b;`, `case a: b;`,
                       `default: a;` and `break;` (the plan's step 3), with 5
                       inert calls; the two must keep the same;
      do_untrimmed and do_trimmed: `break;`, `do a; while (b);` and
                       `while (a) b;`, where a `do` is held by another body
                       (rule 38's clause on a prefix's own lines); the two
                       must keep the same;
      pairs            rule 41;
      two_of_the_same  rule 42;
      triples          rule 43, all or a slice, `triples:k/n` (the k-th of n
                       slices, the groups dealt in turn) or `triples:j-k/n`
                       (the j-th to the k-th of them);
      record           no arranging: every part's record read and set
                       together (rules 56 to 62);
      declarations     rule 70's groups;
      small_run_upgrades  rule 74;
      label_table_pairs   rule 83: the pairs of `goto *a;`, all or a slice, as
                       the triples.
37. Copies: two components of one listing in a group (`while(a)` twice) are
    alike, as inert calls are: orders that only swap them count once; in each
    arrangement the first in line order is the first copy, named as read,
    the second named with `, second`.
38. Trimmed (step 3; the plan's section 3.1): the arrangements of all groups
    of a part are built together, one line at a time, depth by depth, in
    rule 12's order. A prefix whose last line is a component, short of a
    whole arrangement, is asked about; a prefix ending in an inert call is
    not, since the next component's prefix is. A prefix is trimmed, with
    every arrangement that starts with it, when both hold:
      a. clang refuses it closed off (each open body closed; each component
         that holds a body and holds nothing given `{ }`), and its first
         error stands on one of the prefix's own lines, at or before its last
         line;
      b. clang still refuses it, with the same first error at the same line,
         when the group's remaining components are added after it at the
         outermost level, each holding nothing, in the group's order.
    The clause "on one of the prefix's own lines" is beyond the plan's
    wording. Without it a `do` ending a prefix inside another body
    (`while (x) { do { } }`) is refused at the brace that closes it off, and
    the first remaining component added at the outermost level stands on
    that same line number, so b holds though `while (b);` right after the
    `do` makes it work. Rule 72: a prefix is trimmed only when that first
    error is sorted "where it stands". Whole arrangements reached are not
    asked here; lines
    3 and 4 of Block A write and ask them. An untrimmed part makes every
    arrangement and asks only whole ones.
39. Holders, by rule: the statement listings whose components hold a body
    (rules 4, 29 and 30) and that the lowerer accepts alone (rule 33).
40. Dependents, by rule: the statement listings the lowerer refuses alone
    under every fill and accepts held in a holder; and the listings that need
    something in the same function, refused alone without it and accepted
    with it. What each needs is typed from the plan (the owner's table of the 16,
    : `goto m;` needs `m: a;`, `goto *a;` needs `&&m`
    and `m: a;`, `&&m` needs `m: a;` (NEEDS). A listing refused alone and
    held in every holder is neither, and is counted so (`return a;`, whose
    function must return a value).
41. Pairs: each dependent, with what it needs, beside each holder listing,
    one group each; a component already in the group (the `m:` of `m: a;`)
    is not added twice. Groups whose components are written the same
    (`{ a; }` and `{ a; b; }` both give one `{ }`) are arranged once and
    counted for each. (Rule 83: the pairs of `goto *a;` are the part
    label_table_pairs.)
42. Two of the same: the dependents whose kept pairs stand inside one holder
    listing only (read from the pairs' record), two at a time with
    repetition, with that holder (`case` twice, `default` twice, `case` with
    `default`, with `switch`); and the two-at-a-time groups of
    constant-taking dependents again with every constant 0, "the same value"
    (rule 35), for clang's rule against a value twice in one switch.
43. Triples (configuration 4): each dependent, a holder listing between (any
    of rule 39's), and each holder the dependent depends on, one whose every
    kept pair has the dependent inside it (read from the pairs' record). The
    holder between and the holder depended on may be the same listing (two
    copies, rule 37).

write_programs
44. Every program of a group declares every inert number the group uses (its
    inert call lines and the values its components take), a number not yet
    used by a prefix as `int`, so a prefix's lines stand on the same line
    numbers closed off and with the remaining components added. A group with
    a typed fill declares the composite holders first (rule 34).
45. A listing alone (rule 33), held in a holder (rule 32), or written for
    rule 29, is one line of its own text, written with the same rules.

ask_the_lowerer
46. Batches: clang's front end, `clang -cc1` with the arguments the driver
    gives it for rule 20's command (read once from `clang -###`; the input
    file and its `-main-file-name` left out; `-ferror-limit 0`, so no error
    is held back), given up to 200 programs per call, each its own
    translation unit; 8 calls at once. A program is accepted when clang
    writes no error line for its file; its first error is the first line
    naming its file that holds `: error: ` or `: fatal error: `, kept as its
    line number and message. A call clang does not finish (a crash, a time
    out, an exit code other than 0 and 1, or exit 1 with no file named) is
    asked again one program at a time. Every 200th program, and every program of
    the part step_1_again, is also given to clang alone as rule 20 asks; a
    different answer stops the run.

run_with_chosen_returns
47. Which programs run: every kept arrangement of the part's groups, and
    every listing the lowerer accepts alone. Not run, each with its reason,
    counted: a listing refused alone (its runs are in the groups); an
    arrangement with `goto *a;` in it (its target must be a label's address,
    which no inert call returns); and a program clang refuses when it is
    built for the VM's own processor. Rule 67 runs the arrangements with
    `goto *a;` through a label table; rules 65 and 66 build again a program
    that fails to link, or asks for a constant.
48. Built for the VM's own processor (which parts run does not depend on the
    processor): `clang -std=gnu17 -O0 -g` with no `--target` (the owner's standing
    rule: no optimizer); up to 500 programs of one group with the same
    declarations in one file, each program's function renamed `f_<n>`,
    linked with a harness file that gives each inert call a body. A file
    clang refuses is built again one program at a time. Linked with the C
    library's math library (`-lm`), which the math builtins call when the
    optimizer is off.
49. The harness: each inert call records its number in a trace the harness
    shares with the run, and returns the n-th entry of its schedule on its
    n-th call, 0 after the schedule ends. An inert call of a pointer holder
    returns the address of a static buffer of 4,096 zero bytes (of a function
    pointer holder, a function that returns 0); one returned by address
    returns the address of a static object of its holder, all zero. A run
    ends when the program returns ("returned"), when the calls reach 64
    ("cap", so a loop nothing tests ends), when the program ends its process
    itself ("exit"), on a signal ("signal", a crash), or after 0.02 seconds
    ("timeout"; a run that returns takes under a millisecond). Each run is a process of its own (fork), its input, output
    and error streams on /dev/null.
50. The values tried: two base runs, every schedule all 0 and all 1 (64
    ones); then, from each base, each inert call's schedule alone flipped
    (all 1 from the all-0 base, all 0 from the all-1 base), for each inert
    call that ran in that base and returns a number; an inert call whose flip
    changes the trace is tested. Then every schedule of length 3 over {0, 1}
    for each tested inert call, 8 per call, combined across the tested ones;
    when that is more than 512 runs, each tested call's 8 are tried with the
    others' schedules empty, and the program is marked so. Rule 71 adds, for a
    listing alone, the runs with the X sets' values.
51. A trace compared: the inert calls' numbers in order and how the run
    ended (returned, cap, exit, signal or timeout, without the exit code or
    the signal's number, so `exit(a)`'s value is not read as a test);
    counted: each inert call's calls in each run, capped at 9.
52. Each inert call's reading, over all runs of its program:
      tested             its flip changed the trace (rule 50);
      never              it ran in no run;
      behind the branch  it ran in some run, and in some run that ended
                         returned or exit it did not run;
      again              it ran more than once in some run;
      once               none of these: it ran exactly once in every run
                         that ended returned or exit;
    behind the branch and again when both hold. A run ended by cap, signal or
    timeout was cut short: it shows what ran, not what did not. A part is a
    body when it reads behind the branch or again, and is not tested.
53. A listing alone: each placeholder that is an inert call (a value taken,
    or a held statement) is a part, with its reading, and whether it is a
    body; N is the number of its bodies; and the traces of the two base runs.
    (Rule 78: no N for a listing not run alone; a dependent's N by signal 1.
    Rule 81: the listing's configuration counts a part a component holds too.)

classify
54. Each group: rules 23 to 25 over its kept arrangements, and rule 26 for
    every component of its dependents and of what they need, whether or not
    it holds a body; the first errors of the refused, counted; and the asks
    the search made.
55. Signal 2 in each group: each inert call of each kept arrangement, by
    where it stands (inside which components, outermost first, at the top
    when none; and after the nearest component that holds nothing earlier in
    the same body, when there is one) or which component takes it, its
    reading counted.
56. The record per listing (out/configurations.json, from every part's
    record): its components as read, held or taken, its fill and the answer
    under each fill; as holder or dependent (rules 39 and 40); from signal 1,
    in the groups that hold its components: which hold a body and whether
    each was kept holding nothing, which must come right after which, and for
    a dependent where it was kept: inside which components, at which depths,
    before or after what it needs, and in the triples how often it was kept
    inside the holder between, inside the holder it depends on
    (configuration 4); from signal 2, its parts alone, its bodies and N, and
    how the lines its components hold, and the lines after them, read in the
    groups. Each group's arrangements untrimmed are counted, not made (rules
    10 to 12 and 37, from its components, copies and inert calls), beside the
    whole arrangements the trimmed search asked. (Rule 78: each listing's
    `configuration`; rule 80: the small run read too; rule 81: every N by the
    second reading; rule 82: never a kept record; rule 84: against the
    earlier record.)
57. The check, every difference listed and none decided here:
    a. against the reader (dependent_HiOp_reader): bodies.json (matched by
       file, position and text), each part's `body` and each listing's N
       against signal 2 alone, or, for a dependent not run alone, against how
       the lines its components hold read in the groups; places.json, each
       dependent's `places` against the holders it was kept inside in the
       pairs, its `needs_in_the_same_function` against the pairs, and its
       `one_switch` refusals against the groups of two of the same;
    b. against the hand tables of
       Projects/PseudoArch/map_HiOp_to_unit/DRY_mask_maker.py, read from its
       source, not changed: INERT_PART_ROLES, each part's role against its
       reading alone (`body` against a body; `value` against a part that is
       not a body; `constant` against a value the fill writes as a number;
       `name` against a name placeholder); C_STATEMENT_CONTEXT, each
       dependent's context there against whether the record keeps the
       dependent in it;
    c. against C's grammar as each listing is written: each later component
       of a listing right after what the one before it holds, at its level,
       in every kept arrangement of every group that holds both.
    (Rule 78 adds d., each dependent's N; rule 81 adds e., every listing's N
    by both readings, and INERT_PART_ROLES against the configuration's
    bodies beside b. Rule 86: b. reads the two hand tables under their
    _BY_HAND names.)
58. The `for` start: the reading of `a` in the four `for` listings with a
    start, alone, and of the start in every kept arrangement of the groups.

The record
59. (Rule 79: a list filled as runs finish is sorted first; rule 82: the
    record reads a part's record only under its own name.)
    Each part writes out/part_<part>.json.gz: its groups (rules 54 and 55),
    each group's kept arrangements in short form (rule 60), its refusals
    counted by first error, the asks it made and its times. No refused
    program is kept.
60. An arrangement in short form: its lines, `.` for an inert call and a
    capital letter for each component of the group in the order read (a copy
    takes its component's letter); `|`; its levels as digits; and, when it
    ran, `|`, each inert number's reading (t tested, n never, b behind the
    branch, a again, x behind the branch and again, o once), `|`, and its
    runs counted by how they ended (R returned, C cap, E exit, S signal, T
    timeout).
61. The part record writes out/configurations.json (rule 56 and the check of
    rule 57) and out/steps_2_to_4_summary.txt, every count with its whole.
62. A file this run reads is named with its sha256 in every record written.

The upgrades of 

read_components
63. (log 421 Table 4, row 1) Which listings, from now: every listing of
    kinds_forms.json, label_address.json and kinds_builtins.json that has a
    `parsed_as` kind, the entry clang read it as in the operator reader's run
    (clang accepted a program for it there); rule 28's `parsed_as_written`
    filter is left out. Each listing is recorded with what clang read it as
    (`parsed_as`, `detail`). Listings written the same are one listing to the
    method, arranged and asked once, each recorded beside it (`listed_as`);
    their holders must be the same, or nothing is run. Listings read as the
    same entry (`parsed_as` and `detail` alike) are named together, and rule
    73 compares their configurations.
64. (row 2) Contexts as components: CONTEXTS, typed here (one of the handful
    each language needs by hand), names each context: the lines before the
    function, the function's header, the lines it declares first in the
    function, the names it offers, each with the holders it fits, and how a
    run calls it. Today's `void f(void)` is the first. A listing refused alone
    under every fill (rules 32 and 66) is asked in each other context in
    turn: first with the context's names as fills, each where it fits a
    placeholder's holder (the other placeholders as the `int` fill), then
    under each fill; the first context the lowerer accepts it in is the
    context it needs, kept per listing. In signal 2 the run's `f_<n>(void)`
    calls the context's function with the arguments CONTEXTS names.
65. (row 3; rule 75 names each stand-in by an assembler label)
    The linker's whole output is kept with every program that fails
    to build. When it fails to link, each `undefined reference to X` in that
    output gets a stand-in definition, `void X(void) { }`, in a file of its
    own built with `-fno-builtin`; the program is linked again with it and
    run. A stand-in's value does not matter: the run records which inert calls
    ran, and clang has decided which arguments run before the call is made.
    The stand-ins are kept per listing.
66. (row 3) A constant where the lowerer asks for one: a listing still refused
    alone whose refusal asks for a constant (CONSTANT_ASKED), or a listing
    whose build fails with "cannot compile this builtin function yet", is
    written again with one value placeholder at a time as a constant (rule
    35's number) and the others as before, in the order written; the first
    the lowerer accepts (and, at the build, builds) is kept, with the
    placeholder that is constant.
67. (row 4) `goto *a;` runs: a program that holds `goto *a;` is run (signal 2)
    as its label table variant: `a` written `goto_targets[inert_k() & 1]`
    (inert_k declared `int`), `static void *const goto_targets[] = {
    &&goto_target_0, &&goto_target_1 };` first in the function, and
    `goto_target_0:` and `goto_target_1:` at the outermost level after the
    lines, each followed by an inert call numbered after the others. The
    variant is asked of the lowerer before it is built; signal 1 answers for
    the program as written, as before. Alone or in a group alike.
68. (row 5) tree-sitter's C grammar first: each listing is parsed inside
    `void f(void) { ... }` (an expression as a statement, with `;`); each
    value placeholder is read as held when it is a statement of its own (an
    expression statement holding only it: a `consequence`, `alternative` or
    `body`, or a statement of a block, a label or a case), and as taken
    otherwise (a `condition`, `initializer`, `update`, `value`, an argument),
    with the field it sits in. Where tree-sitter parses a listing without an
    error, its answer is the first answer, and rule 29's question is asked of
    clang only for every 10th listing with a placeholder rule 4 reads as held,
    as a check; where tree-sitter reports an error, clang is asked, as
    before. If any checked listing disagrees, clang is asked for every
    listing, its answers are used, and the disagreements are listed. Kept per
    listing: tree-sitter's answer, clang's where asked, and whether they
    agree.
69. (row 5) The reader's places as the expected places: for each group with a
    dependent, places.json's places for the dependent against the kinds of
    the group's holders; the reader expects the dependent kept when a
    holder's kind is one of its places, or always for a dependent it places
    by a rule over the whole function. Each group's record says whether its
    kept arrangements match. Every arrangement is still made; trimming (rule
    38) is the only thing that drops one.
70. (row 6) Declarations as components: DECLARATIONS, typed here (C's
    per-language piece): `int vla_n[a];` (a variable-length array, its length
    an inert call), `int cleanup_n __attribute__((cleanup(drop_int))) = 0;`
    (with `static void drop_int(int *p) { (void)p; }` before the function) and
    `int plain_n = 0;`, each a component that holds nothing. The part
    declarations arranges each with `goto m;` and `m: a;`, and the
    variable-length array with `switch (a) b;` and `case a: b;`, trimmed like
    any group. Classify counts, in each, the kept arrangements where a jump
    enters the declaration's scope: a `goto(m)` outside it to an `m:` in it,
    or the `switch` to a `case` in it (C forbids both for the
    variable-length array and the cleanup variable, and allows them for the
    plain one).

run_with_chosen_returns
71. (row 7) Return values from the X sets: a listing run alone is also run,
    for each inert call that returns a number, once for each value of its
    holder's X set, that inert call returning the value on every call and
    every other inert call returning 1 (rule 50's all-1 schedule). The X sets
    are the probe design's (kind_fuzz_clustering's SUPPORT_conversion_spec.md,
    "the sets actually used": whole 17, fractional 16), clipped to each inert
    call's own type: an `int` inert call takes the whole set's values that fit
    in `int` (0 and 1 when the placeholder's holder is `_Bool`); a floating
    one the fractional set in its own type (`float`, `double`, `long double`,
    `_Float16`; a value the type cannot hold is left out), with NaN and both
    infinities. The harness holds each inert call's values in a table and
    returns the one its schedule names (`x<index>`). Each part keeps, for
    each inert call varied, the values under which it ran; and its reading
    over every run, these with rule 50's, beside rule 52's.

ask_the_lowerer, arrange and classify
72. (row 8; rules 76 and 77 add messages and a fourth sort)
    Refusals sorted by clang's message: REFUSAL_SORTS, typed here
    (C's per-language piece), sorts each first error into "where it stands"
    (clang forbids a component where it stands), "the test program" (a fault
    of the program the method wrote: a name, a type, a constant, a library,
    the linker) or "unsorted" (anything else: listed for the owner, never put in
    either by guess). Trimming (rule 38) trims only on a "where it stands"
    refusal. A listing refused alone only for the test program, under every
    fill and in every context, is recorded as not accepted because of the
    test program, with the message, and is not asked held in a holder: it is
    never a fact about where it may stand. The record keeps the sort with
    every refusal, and each part's summary tallies refusals by sort.
73. (row 1) Classify: listings read as the same entry (rule 63) are checked to
    get the same configuration (accepted alone or not, its context, N, its
    bodies, its role); those that differ are listed. Listings written the
    same share one configuration, so the check counts them apart.
74. The small run (part small_run_upgrades, : the listings
    SMALL_RUN names, each listing read as the same entry as one of its row 1
    listings, and every 100th of the listings in rule 63's order, each alone;
    the pairs of `case a ... b: c;`; and the part declarations' groups,
    through every stage. It writes out/small_run_upgrades.json and
    out/small_run_upgrades_summary.txt, whose table has one row per listing or
    group, and never a part record or out/configurations.json.

The fixes after the first small run (elv2_l132, 

75. (row 3; changes rule 65) Every stand-in is written under a name of its
    own, its symbol set by an assembler label:
    `void stand_in_<k>(void) __asm__("<the name>");` and then
    `void stand_in_<k>(void) { }`. clang never sees the name the linker asked
    for declared, so a name clang keeps as its own builtin even under
    `-fno-builtin` (`__atomic_is_lock_free`) is stood in for like any other.
76. (row 8; changes rule 72) Six messages the first small run left unsorted
    are the test program's, each about what the test program supplied: an
    argument with a side effect, a reference bound to a temporary or to
    another type, a value of no floating type, a value that is not a vector,
    and a stand-in's conflicting types. Each is in REFUSAL_SORTS, so the
    listing goes on to the next fill or context, as on any refusal of the test
    program.
77. (row 8; changes rule 72: a fourth sort) "the listing as written": a
    refusal of the listing's own argument count, too many or too few arguments
    to a function-like macro or to a call. In a program the method asks, the
    listing's own call is the only one written with arguments (an inert call
    takes none), so the count refused is the listing's. A listing refused
    alone under every fill and in every context, each refusal the test
    program's or the listing as written's and at least one the listing as
    written's, is not accepted as written: it is recorded with the messages
    and with the evidence, clang asked once more for that program, the note
    clang gives with the refusal, and the lines of the file the note names,
    from the nearest `#if` above the note's line down to it. It is never
    counted as the test program's fault, and it is not asked held in a holder.
78. (changes rules 53 and 56) A listing not run alone has no N and no bodies:
    written "not run alone". A dependent's N by signal 1: each part a
    component of it holds is a body (the second reading of 
    2: a part is a body when a component holds it, or when it runs behind the
    branch or again), each shown with how the lines that component holds read
    in the groups (rule 55), and set against the reader's. Each listing's
    record carries its `configuration`: N, the bodies, and what they come from
    (signal 2 alone; signal 1 and the groups, for a dependent; or not run
    alone); the record's check counts every dependent's N given so against
    the reader's. (Rule 81: every listing run alone the same way.)
79. (changes rule 59) A list filled as runs finish (the not-run list, and its
    count by why) is sorted before it is written, so two records of the same
    work compare byte for byte.
80. (changes rule 56) The record reads out/small_run_upgrades.json too, when
    it is there, as the part small_run_upgrades. A listing the small run ran
    alone is taken, its reading and its run alone together, from whichever of
    it and the part listings was written later, and its record names that part
    (`from_part`); a listing only the small run read (rule 63) is added; a
    group of the same name in two parts is taken from the part written later;
    `upgrades` takes each of its fields from the latest part that holds it.
    (Rule 85: but one, the check of the listings read as the same entry.)

The wide run 

81. (changes rules 53, 56 and 78) Every listing run alone has its N by the
    second reading of 
    part is a body when a component of the listing holds it, or when it runs
    behind the branch or again alone (rule 52; a tested part is not one). Each
    body is kept with why (`why`): the component that holds it, how it runs
    alone, or both; with the component that holds each part (`held_by`) and how
    the lines it holds read in the groups. The first reading (a part is a body
    when it runs behind the branch or again, signal 2 alone) is kept beside it
    in the configuration (`by_signal_2_alone`), and the run alone keeps its own
    N and bodies as before. A listing neither run alone nor a dependent still
    has no N. The record's check counts every N so given against the reader's,
    by both readings, for the listings run alone and for the dependents
    (`the_reader_n`), and INERT_PART_ROLES against the configuration's bodies
    beside rule 57b's count; the summary says, per listing, which parts are
    bodies and why.
82. (changes rule 59) The record reads each part's record only under its own
    name, out/part_<part>.json.gz. A record kept beside the one that replaced
    it, named with the run it came from (out/part_pairs_l130.json.gz), is left
    out, and named in the record (`kept_records_left_out`).
83. (changes rules 36 and 41) The pairs in two parts: the part pairs takes
    every dependent's pairs but those of a dependent run through the label
    table (`goto *a;`, rule 67), which the part label_table_pairs takes, all or
    a slice (`label_table_pairs:k/n`, `label_table_pairs:j-k/n`, as rule 36's
    triples). The groups of two of the same and the triples read the part pairs,
    as before: no kept pair has `goto *a;` only inside a holder 
    section 5), so it makes none of their groups; the part label_table_pairs
    checks this in its own record (`depends_on_no_holder`) and stops if not. A
    part's slices are added up in the record, and left out of it when the
    whole part is there.
84. The record against the record it replaces: the newest
    out/configurations_l<run>.json beside it (the record of 
    as out/configurations_l130.json), listing by listing: the listings in both
    and in one only; for each listing in both, whether it ran alone, its role,
    fill and context, whether clang accepted it alone, N (the earlier record's,
    which has no configuration, by signal 2 alone), N by signal 2 alone, each
    part's reading alone, and how many groups hold its components; each listing
    that differs named with what differs, before and after. Written into
    out/configurations.json (`against_the_earlier_record`) and the summary.
85. (changes rule 80) The record's `upgrades` takes the check of the listings
    read as the same entry (rule 73) from the latest part that compared at
    least one, a part that ran listings alone (the part listings, or the small
    run), and names that part (`read_as_the_same_entry_from_part`); only when
    none did, from the latest part, as rule 80. Every other part of the wide
    run runs no listing alone, so it compares none: found by the record part
    over the wide run's first parts, on the laptop, before the record's run
    (0 of 69 compared, from the part label_table_pairs:1/3, where the part
    listings compared 39 of 69).

Part (b): the standard-form takes its routing from this record 

86. (changes rule 57b) The hand tables b. checks against are read under the
    names DRY_mask_maker.py keeps them by since the standard-form began to take its
    routing from this record: INERT_PART_ROLES_BY_HAND and
    C_STATEMENT_CONTEXT_BY_HAND (the tables written by hand, the oracle the
    record is checked against). The names INERT_PART_ROLES and
    C_STATEMENT_CONTEXT are no longer in that file; its routing from this
    record is DRY_mask_maker.ROUTING, which b. does not read.
"""

import ast
import gzip
import hashlib
import json
import multiprocessing
import os
import re
import shlex
import subprocess
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
# Projects/PseudoArch/map_HiOp_to_unit/extract_lang_vocab/HiOp_configuration_solver: four folders down from Projects.
PROJECTS = os.path.normpath(os.path.join(HERE, "..", "..", "..", "..", ".."))
PCHQ = os.path.dirname(PROJECTS)
# The vocabulary's research folder: the listings read, the reader's records, and this module's runs and records.
VOCABULARY = os.path.join(PCHQ, "Research", "extract_lang_vocabulary")
GNU17_FOLDER = os.path.join(VOCABULARY, "mask", "gnu17")
LISTINGS = os.path.join(GNU17_FOLDER, "kinds_forms.json")
LABEL_ADDRESS = os.path.join(GNU17_FOLDER, "label_address.json")
BUILTINS = os.path.join(GNU17_FOLDER, "kinds_builtins.json")
HOLDER_CLASSES = os.path.join(GNU17_FOLDER, "holders.json")
LIBRARY_DECLARATIONS = os.path.join(GNU17_FOLDER, "library_declarations.json")
READER_PLACES = os.path.join(VOCABULARY, "dependent_HiOp_reader", "out", "places.json")
READER_BODIES = os.path.join(VOCABULARY, "dependent_HiOp_reader", "out", "bodies.json")
HAND_TABLES = os.path.join(PCHQ, "Projects", "PseudoArch", "map_HiOp_to_unit", "lower_HiOp", "standard_HiOp_wrapper.py")
OUT = os.path.join(VOCABULARY, "HiOp_configuration_solver", "out")
STEP_1_RECORD = os.path.join(OUT, "step_1_arrangements.json")
PART_FILE = os.path.join(OUT, "part_{0}.json.gz")
CONFIGURATIONS_FILE = os.path.join(OUT, "configurations.json")
SUMMARY_FILE = os.path.join(OUT, "steps_2_to_4_summary.txt")

# The four groups of step 1, chosen by hand (the plan's section 3). Each names
# the listings whose components it uses, by their `template` text.
GROUPS = {
    "if": ["if (a) b; else c;"],
    "while": ["while (a) b;", "break;"],
    "for": ["for (a; b; c) d;", "break;", "continue;"],
    "goto": ["goto m;", "m: a;"],
}

# Rule 8: the components the plan's section 3 gives for the 7 listings,
# typed by hand from it. The check, not the source.
EXPECTED_COMPONENTS = {
    "if (a) b; else c;": ["if(a) holds a body", "else holds a body"],
    "while (a) b;": ["while(a) holds a body"],
    "break;": ["break"],
    "for (a; b; c) d;": ["for(a; b; c) holds a body"],
    "continue;": ["continue"],
    "goto m;": ["goto(m)"],
    "m: a;": ["m: holds a body"],
}

# Rule 14: the plan's section 3 and 
EXPECTED_ARRANGEMENTS = {"if": 280, "while": 60, "for": 420, "goto": 60}
EXPECTED_IN_DEES_ORDER = 12
# Rule 36: step 1's record, as run elv2_l122 kept it .
EXPECTED_STEP_1_KEPT = 185

# Rule 13: the owner's `if` example (the owner's chat of 2026-10-10, quoted in PCHQ log
# 416): the lines in the owner's order, and the owner's three arrangements, by their
# levels, with the owner's words.
DEES_ORDER = ["inert call", "if(a)", "inert call", "else", "inert call", "inert call"]
DEES_EXAMPLES = [
    {"example": 1, "levels": [0, 0, 0, 0, 0, 0], "dees_words": "doesnt work"},
    {"example": 2, "levels": [0, 0, 1, 0, 0, 0],
     "dees_words": "doesnt work. but might identify where it works and doesnt so we can keep what works"},
    {"example": 3, "levels": [0, 0, 1, 0, 1, 0], "dees_words": "like that kind of brute force"},
]

# Rule 36: the plan's step 3 groups, by their listings.
SWITCH_GROUP = ["switch (a) b;", "case a: b;", "default: a;", "break;"]
DO_GROUP = ["break;", "do a; while (b);", "while (a) b;"]
EXPECTED_SWITCH_ARRANGEMENTS = 166320

# Rule 40: what each listing needs in the same function, typed from the owner's
# table of the 16 .
NEEDS = {
    "goto m;": ["m: a;"],
    "goto *a;": ["&&m", "m: a;"],
    "&&m": ["m: a;"],
}

# Rule 2.
VALUE_LETTERS = ("a", "b", "c", "d", "e", "f", "g", "h")
NAME_LETTERS = ("m", "n")
TYPE_LETTERS = ("T", "U", "V", "W")
# Rule 3: a word, spaces, `...`, or any one other character.
PIECE = re.compile(r"\w+|\s+|\.\.\.|.")
WORD = re.compile(r"\w+")

# An inert call, as a line of an arrangement; and as the owner writes one.
INERT_CALL = {"is": "inert call"}
INERT_CALL_WRITTEN = "inert_{0}()"

# Rule 19: typed for C.
C_DECLARATION = "int inert_{0}(void);"
C_INERT_CALL_LINE = "inert_{0}();"
C_FUNCTION_START = "void f(void) {"
C_FUNCTION_NAMED = "void {0}(void) {{"
C_FUNCTION_END = "}"
C_BODY_OPENS = " {"
C_EMPTY_BODY = " { }"
C_BODY_CLOSES = "}"
C_INDENT = "    "
C_HELD_BODY = "{{ {0}; }}"

# Rule 34: typed inert calls.
C_VALUE_TYPE = "__typeof__(((void)0, (*({0} *)0)))"
C_VALUE_DECLARATION = C_VALUE_TYPE + " inert_{1}(void);"
C_ADDRESS_DECLARATION = "__typeof__({0}) *inert_{1}(void);"
C_BY_ADDRESS = "(*inert_{0}())"
C_TYPE_SPELLING = {"bool": "_Bool"}
INTEGER_CLASSES = ("Bool", "Char_U", "Char_S", "UChar", "SChar", "WChar_U", "WChar_S", "Char8", "Char16",
                   "Char32", "UShort", "Short", "UInt", "Int", "ULong", "Long", "ULongLong", "LongLong",
                   "UInt128", "Int128", "EnumType", "BitIntType", "qualified")
VALUE_CLASSES = ("PointerType", "Float", "Double", "LongDouble", "Float16")
FLOATING_CLASSES = ("Float", "Double", "LongDouble", "Float16")
FUNCTION_POINTER_TYPEDEF = re.compile(r"typedef\s+[^;]*\(\s*\*\s*(\w+)\s*\)\s*\(")
FILLS = ("int", "typed", "address", "constant")

# Rules 20, 21 and 46: GNU C's lowerer, as signal 1 asks it.
GNU_C = "GNU C"
GNU_C_COMMAND = ["clang", "-std=gnu17", "--target=riscv64-unknown-linux-gnu", "-fsyntax-only"]
FIRST_ERROR_MARK = ": error: "
FATAL_ERROR_MARK = ": fatal error: "
DIAGNOSTIC = re.compile(r"^(?P<file>[^:\s]+\.c):(?P<line>\d+):(?P<column>\d+): (?P<what>error|fatal error): (?P<message>.*)$")
CRASH_MARKS = ("PLEASE submit a bug report", "Stack dump:")
AT_ONCE = 8
PROGRAMS_PER_CALL = 200
ALONE_EVERY = 200
CALL_SECONDS = 900

# Rules 48 to 51: GNU C's lowerer, as signal 2 builds for the VM's processor.
GNU_C_BUILD = ["clang", "-std=gnu17", "-O0", "-g"]
GNU_C_LIBRARIES = ["-lm"]
PROGRAMS_PER_BUILD = 500
BUILD_SECONDS = 900
CAP = 64
SCHEDULE_LENGTH = 3
MOST_COMBINED_RUNS = 512
RUNS_SECONDS = 3600
READING_LETTERS = {
    "tested": "t",
    "never": "n",
    "behind the branch": "b",
    "again": "a",
    "behind the branch and again": "x",
    "once": "o",
}
BODY_READINGS = ("behind the branch", "again", "behind the branch and again")
# Rule 81: the two readings of N of 
SECOND_READING = ("a part is a body when a component of the listing holds it, or when it runs behind the "
                  "branch or again ")
FIRST_READING = ("a part is a body when it runs behind the branch or again, alone (signal 2 alone; 
                 "419 Table 2, the first reading)")
FINISHED_OUTCOMES = ("R", "E")

# Rule 60: the short form of an arrangement.
SHORT_INERT_CALL = "."
SHORT_COMPONENT_LETTERS = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"

PARTS = ("step_1_again", "step_1_trimmed", "listings", "switch_untrimmed", "switch_trimmed", "do_untrimmed",
         "do_trimmed", "pairs", "two_of_the_same", "triples", "record", "declarations", "small_run_upgrades",
         "label_table_pairs")
TRIMMED_PARTS = ("step_1_trimmed", "switch_trimmed", "do_trimmed", "pairs", "two_of_the_same", "triples",
                 "declarations", "small_run_upgrades", "label_table_pairs")
# Rule 83: the parts that may run in slices (`triples:k/n`, `label_table_pairs:j-k/n`).
SLICED_PARTS = ("triples", "label_table_pairs")
ALL_ALONE_PARTS = ("step_1_again",)

# Rule 64 : GNU C's contexts, typed here, one of the handful each language needs by
# hand. Each: the lines before the function, its header, the lines it declares first in it, the names it offers
# (each with the holder spellings or holder classes it fits), and how a run's f_<n>(void) calls it.
TODAYS_CONTEXT = "void f(void)"
CONTEXTS = [
    {"context": "void f(void)", "prelude": [], "header": "void f(void) {", "declares": [], "names": [],
     "returns": "void", "parameters": "void", "arguments": ""},
    {"context": "int f(void)", "prelude": [], "header": "int f(void) {", "declares": [], "names": [],
     "returns": "int", "parameters": "void", "arguments": ""},
    {"context": "void f(int n, ...)", "prelude": ["#include <stdarg.h>"], "header": "void f(int n, ...) {",
     "declares": ["va_list ap;"],
     "names": [{"name": "ap", "fits": ("__builtin_va_list",)}, {"name": "n", "fits": INTEGER_CLASSES}],
     "returns": "void", "parameters": "int n, ...", "arguments": "0"},
    {"context": "void f(struct counted *s)",
     "prelude": ["struct counted { int n; int a[] __attribute__((counted_by(n))); };",
                 "static struct counted counted_object;"],
     "header": "void f(struct counted *s) {", "declares": [],
     "names": [{"name": "s->a", "fits": ("arr4", "ConstantArrayType")}],
     "returns": "void", "parameters": "struct counted *s", "arguments": "&counted_object"},
]
C_CONTEXT_FUNCTION = "static {0} g_{1}({2}) {{"
C_CONTEXT_CALLER = "void f_{0}(void) {{ g_{0}({1}); }}"

# Rule 66 (row 3): a refusal that asks for a constant, by a piece of clang's message; and the build failure.
CONSTANT_ASKED = ("must be a constant", "integer constant expression", "not a compile-time constant",
                  "must be a compile-time constant")
NOT_COMPILED_YET = "cannot compile this builtin function yet"

# Rule 65 (row 3): the linker's word for a function no library defines, and the stand-ins' build; rule 75: each
# stand-in under a name of its own, the symbol the linker asked for set by an assembler label.
UNDEFINED_REFERENCE = re.compile(r"undefined reference to [`']([^'`]+)'")
C_STAND_IN_DECLARED = "void stand_in_{0}(void) __asm__(\"{1}\");"
C_STAND_IN = "void stand_in_{0}(void) {{ }}"
GNU_C_STAND_INS = ["clang", "-std=gnu17", "-O0", "-g", "-fno-builtin", "-c"]

# Rule 67 (row 4): the label table of `goto *a;`'s runs.
LABEL_TABLE = "label table"
C_LABEL_TABLE = "static void *const goto_targets[] = { &&goto_target_0, &&goto_target_1 };"
C_LABEL_TABLE_ENTRY = "goto_targets[{0} & 1]"
C_LABEL_TABLE_TARGET = "goto_target_{0}: inert_{1}();"

# Rule 68 (row 5): tree-sitter's C grammar; and every how many listings it reads are asked of clang too.
TREE_SITTER_CHECK_EVERY = 10
TREE_SITTER_FUNCTION = "void f(void) {{ {0} }}"

# Rule 70 (row 6): GNU C's declarations, typed here, each with its name, what it needs before the function, and
# what C's rule says of a jump into its scope; and the groups each goes in.
DECLARATIONS = [
    {"declaration": "int vla_n[a];", "name": "int vla_n[a]", "prelude": [],
     "a_jump_into_its_scope": "refused (a variable-length array)"},
    {"declaration": "int cleanup_n __attribute__((cleanup(drop_int))) = 0;", "name": "int cleanup_n",
     "prelude": ["static void drop_int(int *p) { (void)p; }"],
     "a_jump_into_its_scope": "refused (a variable with a cleanup)"},
    {"declaration": "int plain_n = 0;", "name": "int plain_n", "prelude": [],
     "a_jump_into_its_scope": "accepted (a plain variable)"},
]
DECLARATION_GROUPS = [
    {"declaration": "int vla_n[a];", "dependent": "goto m;", "holder": "m: a;"},
    {"declaration": "int cleanup_n __attribute__((cleanup(drop_int))) = 0;", "dependent": "goto m;", "holder": "m: a;"},
    {"declaration": "int plain_n = 0;", "dependent": "goto m;", "holder": "m: a;"},
    {"declaration": "int vla_n[a];", "dependent": "case a: b;", "holder": "switch (a) b;"},
]
DECLARATION_FILE = "DECLARATIONS (typed here, rule 70)"

# Rule 71 (row 7): the X sets of the probe design (kind_fuzz_clustering's SUPPORT_conversion_spec.md, "the sets
# actually used"), clipped to each inert call's own type. An `int` inert call: the whole set's values that fit in
# `int`, each with its label and its C text; `_Bool`'s holder: 0 and 1. A floating one: the fractional set, written
# for each floating type from clang's own macros, with NaN and both infinities; a value the type cannot hold is
# left out (2^53 in `_Float16`).
WHOLE_IN_INT = [("-2^31", "(-2147483647 - 1)"), ("-42", "-42"), ("-1", "-1"), ("0", "0"), ("1", "1"), ("7", "7"),
                ("42", "42"), ("1000", "1000"), ("2^31-1", "2147483647")]
WHOLE_LEFT_OUT_OF_INT = ("-2^63", "-2^63+1", "-2^53-1", "2^31", "2^53-1", "2^53+1", "2^63-1", "2^64-1")
TRUTH_IN_BOOL = [("0", "0"), ("1", "1")]
FRACTIONAL = [("-max_finite", "-{MAX}"), ("-1.5", "-1.5{S}"), ("-1.0", "-1.0{S}"),
              ("-(1.0-1ulp)", "-(1.0{S} - {EPSILON} / 2)"), ("-0.0", "-0.0{S}"), ("+0.0", "0.0{S}"),
              ("+min_subnormal", "{DENORM_MIN}"), ("+min_normal", "{MIN}"), ("1.0-1ulp", "(1.0{S} - {EPSILON} / 2)"),
              ("1.0", "1.0{S}"), ("1.0+1ulp", "(1.0{S} + {EPSILON})"), ("1.5", "1.5{S}"),
              ("pi", "3.14159265358979323846264338327950288{S}"), ("2^53", "9007199254740992.0{S}"),
              ("max_finite", "{MAX}"), ("0.1", "0.1{S}"), ("nan", "{NAN}"), ("+inf", "{INF}"), ("-inf", "-{INF}")]
FLOATING_TYPES = {
    "Float": {"S": "f", "MAX": "__FLT_MAX__", "EPSILON": "__FLT_EPSILON__", "DENORM_MIN": "__FLT_DENORM_MIN__",
              "MIN": "__FLT_MIN__", "NAN": "__builtin_nanf(\"\")", "INF": "__builtin_inff()", "left_out": (),
              "cast": None},
    "Double": {"S": "", "MAX": "__DBL_MAX__", "EPSILON": "__DBL_EPSILON__", "DENORM_MIN": "__DBL_DENORM_MIN__",
               "MIN": "__DBL_MIN__", "NAN": "__builtin_nan(\"\")", "INF": "__builtin_inf()", "left_out": (),
               "cast": None},
    "LongDouble": {"S": "L", "MAX": "__LDBL_MAX__", "EPSILON": "__LDBL_EPSILON__", "DENORM_MIN": "__LDBL_DENORM_MIN__",
                   "MIN": "__LDBL_MIN__", "NAN": "__builtin_nanl(\"\")", "INF": "__builtin_infl()", "left_out": (),
                   "cast": None},
    "Float16": {"S": "", "MAX": "__FLT16_MAX__", "EPSILON": "__FLT16_EPSILON__", "DENORM_MIN": "__FLT16_DENORM_MIN__",
                "MIN": "__FLT16_MIN__", "NAN": "__builtin_nanf(\"\")", "INF": "__builtin_inff()", "left_out": ("2^53",),
                "cast": "_Float16"},
}

# Rule 72 (row 8): what a first error is about, typed here for GNU C from clang's messages: the first entry whose
# piece is in the message decides; a message no entry names is unsorted.
WHERE_IT_STANDS = "where it stands"
TEST_PROGRAM = "the test program"
LISTING_AS_WRITTEN = "the listing as written"
UNSORTED = "unsorted"
REFUSAL_SORTS = [
    ("'break' statement not in loop or switch statement", WHERE_IT_STANDS),
    ("'continue' statement not in loop statement", WHERE_IT_STANDS),
    ("'case' statement not in switch statement", WHERE_IT_STANDS),
    ("'default' statement not in switch statement", WHERE_IT_STANDS),
    ("use of undeclared label", WHERE_IT_STANDS),
    ("cannot jump from this goto statement to its label", WHERE_IT_STANDS),
    ("cannot jump from this indirect goto statement", WHERE_IT_STANDS),
    ("cannot jump from switch statement to this case label", WHERE_IT_STANDS),
    ("duplicate case value", WHERE_IT_STANDS),
    ("multiple default labels in one switch", WHERE_IT_STANDS),
    ("indirect goto in function with no address-of-label expressions", WHERE_IT_STANDS),
    ("redefinition of label", WHERE_IT_STANDS),
    ("expected expression", WHERE_IT_STANDS),
    ("expected statement", WHERE_IT_STANDS),
    ("expected ';'", WHERE_IT_STANDS),
    ("expected '('", WHERE_IT_STANDS),
    ("expected ')'", WHERE_IT_STANDS),
    ("expected '}'", WHERE_IT_STANDS),
    ("expected 'while' in do/while loop", WHERE_IT_STANDS),
    ("label at end of compound statement", WHERE_IT_STANDS),
    ("use of undeclared identifier", TEST_PROGRAM),
    ("incompatible", TEST_PROGRAM),
    ("call to undeclared function", TEST_PROGRAM),
    ("call to undeclared library function", TEST_PROGRAM),
    ("implicit declaration of function", TEST_PROGRAM),
    ("must be a pointer", TEST_PROGRAM),
    ("should not return a value", TEST_PROGRAM),
    ("should return a value", TEST_PROGRAM),
    ("must be a constant", TEST_PROGRAM),
    ("integer constant expression", TEST_PROGRAM),
    ("not a compile-time constant", TEST_PROGRAM),
    ("cannot compile this builtin function yet", TEST_PROGRAM),
    ("flexible array member", TEST_PROGRAM),
    ("linker command failed", TEST_PROGRAM),
    ("undefined reference", TEST_PROGRAM),
    # rule 77: the listing's own argument count
    ("too many arguments provided to function-like macro invocation", LISTING_AS_WRITTEN),
    ("too few arguments provided to function-like macro invocation", LISTING_AS_WRITTEN),
    ("too many arguments to function call", LISTING_AS_WRITTEN),
    ("too few arguments to function call", LISTING_AS_WRITTEN),
    ("too many arguments", TEST_PROGRAM),
    ("too few arguments", TEST_PROGRAM),
    ("is not a function or function pointer", TEST_PROGRAM),
    ("requires pointer operand", TEST_PROGRAM),
    ("invalid operands to binary expression", TEST_PROGRAM),
    ("is not a structure or union", TEST_PROGRAM),
    ("subscripted value is not", TEST_PROGRAM),
    ("is not assignable", TEST_PROGRAM),
    ("cannot take the address of an rvalue", TEST_PROGRAM),
    ("where arithmetic or pointer type is required", TEST_PROGRAM),
    ("statement requires expression of", TEST_PROGRAM),
    ("requires argument of", TEST_PROGRAM),
    ("invalid application of", TEST_PROGRAM),
    ("unknown type name", TEST_PROGRAM),
    ("has incomplete type", TEST_PROGRAM),
    ("used type", TEST_PROGRAM),
    # rule 76: the six the first small run left unsorted, each about what the test program supplied
    ("cannot have side-effects", TEST_PROGRAM),
    ("non-const lvalue reference to type", TEST_PROGRAM),
    ("must be a scalar or vector of floating-point types", TEST_PROGRAM),
    ("must be vectors", TEST_PROGRAM),
    ("requires two args of floating point type", TEST_PROGRAM),
    ("conflicting types for", TEST_PROGRAM),
]
# Rule 77: a note clang writes after a refusal, naming the file and line it is about.
NOTE = re.compile(r"^(?P<file>[^:\s]+):(?P<line>\d+):(?P<column>\d+): note: (?P<message>.*)$")
NOTE_LINES_ABOVE = 20

# Rule 74: the small run of 
# its entry's name), with the rows of log 421 Table 4 it is chosen for. Every listing also shows row 8.
SMALL_RUN = [
    {"listing": "__sync_lock_test_and_set_1(a, b, c)", "name": None, "rows": [1]},
    {"listing": "a * b", "name": "CXXRewrittenBinaryOperator.Mul", "rows": [1]},
    {"listing": "(T)a", "name": "CompoundLiteralExpr", "rows": [1]},
    {"listing": "__builtin_invoke(a, b)", "name": None, "rows": [1]},
    {"listing": "return a;", "name": None, "rows": [2]},
    {"listing": "va_start(a, b)", "name": None, "rows": [2]},
    {"listing": "va_start(a, b, c)", "name": None, "rows": [2]},
    {"listing": "__builtin_counted_by_ref(a)", "name": None, "rows": [2]},
    {"listing": "__builtin_acosf16(a)", "name": None, "rows": [3]},
    {"listing": "__sinpi(a)", "name": None, "rows": [3]},
    {"listing": "__builtin___get_unsafe_stack_ptr()", "name": None, "rows": [3]},
    {"listing": "_Block_object_assign(a, b, c)", "name": None, "rows": [3]},
    {"listing": "__atomic_is_lock_free(a, b)", "name": None, "rows": [3]},
    {"listing": "__atomic_always_lock_free(a, b)", "name": None, "rows": [3]},
    {"listing": "goto *a;", "name": None, "rows": [4]},
    {"listing": "if (a) b; else c;", "name": None, "rows": [5]},
    {"listing": "for (a; b; c) d;", "name": None, "rows": [5]},
    {"listing": "case a ... b: c;", "name": None, "rows": [5]},
    {"listing": "__builtin_fpclassify(a, b, c, d, e, f)", "name": None, "rows": [7]},
    {"listing": "a && b", "name": None, "rows": [7]},
    {"listing": "a ? b : c", "name": None, "rows": [7]},
]
SMALL_RUN_PAIRS = ("case a ... b: c;",)
SMALL_RUN_STRIDE = 100
SMALL_RUN_RECORD = "small_run_upgrades.json"
SMALL_RUN_SUMMARY = "small_run_upgrades_summary.txt"


def main() -> None:
    work_folder, part = arguments_from_the_command_line()
    lowerer = gnu_c_lowerer(work_folder, part)
    if part == "record":
        write_the_whole_record(lowerer)
    else:
        configurations = configurations_by_brute_force(lowerer, LISTINGS, part)
        write_the_part(configurations, lowerer, part)
    close_the_pool(lowerer)


def configurations_by_brute_force(lowerer, listings_path, part):
    """Block A (the plan's section 2), for the groups of one part (rule 36)."""
    listings = read_components(listings_path, lowerer, part)   # 1  each listing's written pieces, each with what it takes; held or taken and the fill asked of the lowerer
    arrangements = arrange(listings, lowerer, part)            # 2  every order and indentation, inert calls alike; trimmed: each prefix asked
    programs = write_programs(arrangements, lowerer)           # 3  each arrangement written in the language; in C a held line goes in { }
    accepted = ask_the_lowerer(programs, lowerer)              # 4  signal 1: accepted or refused
    runs = run_with_chosen_returns(accepted, lowerer)          # 5  signal 2: which inert calls run, for each value they return
    configurations = classify(accepted, runs)                  # 6  what the record shows: which parts are bodies, where each may stand
    return configurations


# The lowerer


def arguments_from_the_command_line() -> tuple:
    if len(sys.argv) != 3:
        stop("usage: python3 HiOp_configuration_solver.py <work folder> <part>")
    folder = sys.argv[1]
    part = sys.argv[2]
    check_the_part(part)
    arguments = (folder, part)
    return arguments


def check_the_part(part: str) -> None:
    name = part_name(part)
    if name not in PARTS:
        stop(f"no part {part!r}; the parts: {', '.join(PARTS)}")


def part_name(part: str) -> str:
    name = part.split(":")[0]
    return name


def gnu_c_lowerer(work_folder: str, part: str) -> dict:
    """GNU C's lowerer as this part asks it (rules 20, 46 and 48), and the
    folder its programs are written into."""
    os.makedirs(work_folder, exist_ok=True)
    lowerer = {}
    lowerer["language"] = GNU_C
    lowerer["command"] = GNU_C_COMMAND
    lowerer["build"] = GNU_C_BUILD
    lowerer["work_folder"] = work_folder
    lowerer["part"] = part
    lowerer["version"] = version_of(GNU_C_COMMAND)
    lowerer["front_end"] = front_end_command(work_folder)
    lowerer["alone_every"] = alone_every_of(part)
    lowerer["asks"] = new_ask_tally()
    lowerer["pool"] = new_pool()
    return lowerer


def new_pool():
    """Rules 46 and 48: 8 workers, made before anything large is held, so each starts small."""
    context = multiprocessing.get_context("fork")
    pool = context.Pool(AT_ONCE)
    return pool


def close_the_pool(lowerer: dict) -> None:
    lowerer["pool"].close()
    lowerer["pool"].join()


def version_of(command: list) -> str:
    finished = subprocess.run([command[0], "--version"], capture_output=True, text=True)
    lines = finished.stdout.splitlines()
    version = lines[0]
    return version


def alone_every_of(part: str) -> int:
    every = ALONE_EVERY
    if part_name(part) in ALL_ALONE_PARTS:
        every = 1
    return every


def front_end_command(work_folder: str) -> list:
    """Rule 46: the front end's arguments as the driver gives them for rule 20's command."""
    probe = os.path.join(work_folder, "front_end_probe.c")
    write_text(probe, "void f(void) { }\n")
    finished = subprocess.run(GNU_C_COMMAND + ["-###", "front_end_probe.c"], cwd=work_folder,
                              capture_output=True, text=True)
    arguments = front_end_arguments_of(finished.stderr)
    os.remove(probe)
    return arguments


def front_end_arguments_of(output: str) -> list:
    line = front_end_line_of(output)
    if line is None:
        stop("ask_the_lowerer: `clang -###` gave no front end command; nothing is run")
    arguments = shlex.split(line)
    kept = front_end_arguments_kept(arguments)
    return kept


def front_end_line_of(output: str):
    found = None
    for line in output.splitlines():
        if '"-cc1"' in line:
            found = line
    return found


def front_end_arguments_kept(arguments: list) -> list:
    """Without the input file and `-main-file-name`, with no error limit."""
    kept = []
    skip = 0
    for index in range(len(arguments)):
        argument = arguments[index]
        if skip > 0:
            skip -= 1
        elif argument == "-main-file-name" or argument == "-ferror-limit":
            skip = 1
        elif argument == "front_end_probe.c":
            pass
        else:
            kept.append(argument)
    kept.append("-ferror-limit")
    kept.append("0")
    return kept


def new_ask_tally() -> dict:
    tally = {}
    tally["programs"] = 0
    tally["calls"] = 0
    tally["asked_alone"] = 0
    tally["alone_differs"] = 0
    tally["calls_asked_again_alone"] = 0
    tally["seconds"] = 0.0
    return tally


# 1. read_components


def read_components(listings_path: str, lowerer: dict, part: str) -> dict:
    """Each listing's components, read from its text and asked of the lowerer
    (rules 1 to 8, 28 to 35, 39 and 40; 63, 64, 66, 68, 70 and 72)."""
    records = records_of_every_listing(listings_path)
    listings = components_of_every_listing(records)
    check_the_components(listings)
    add_the_declarations(listings, part)
    read_held_or_taken_with_tree_sitter(listings)
    ask_held_or_taken(listings, lowerer)
    ask_the_fills(listings, lowerer, part)
    return listings


def records_of_every_listing(listings_path: str) -> dict:
    """Rule 28: every listing of the three files, each with its file."""
    records = {}
    records["kinds_forms.json"] = read_json(listings_path)["operators"]
    records["label_address.json"] = [label_address_record()]
    records["kinds_builtins.json"] = read_json(BUILTINS)["operators"]
    return records


def label_address_record() -> dict:
    record = dict(read_json(LABEL_ADDRESS)["operator"])
    record["position"] = None
    record["holders"] = []
    return record


def components_of_every_listing(records: dict) -> dict:
    """Every listing clang accepted, one entry per text, keyed by its text (rules 28 and 63)."""
    listings = {}
    listings["by_text"] = {}
    listings["not_parsed_as_written"] = []
    listings["every_listing"] = []
    listings["not_taken"] = []
    for file_name in records:
        add_listings_of_a_file(listings, file_name, records[file_name])
    check_the_texts_listed_twice(listings)
    listings["read_as_the_same_entry"] = read_as_the_same_entry(listings["every_listing"])
    listings["holder_classes"] = holder_classes()
    listings["holder_types"] = held_type_declarations()
    listings["function_pointers"] = function_pointer_holders()
    listings["library"] = library_declarations()
    return listings


def library_declarations() -> dict:
    """Rule 34: the declaration clang asks for before a library builtin, by the function's name."""
    declarations = {}
    for declaration in read_json(LIBRARY_DECLARATIONS)["declarations"]:
        declarations[declared_name(declaration)] = declaration
    return declarations


def declared_name(declaration: str) -> str:
    before = declaration.split("(")[0]
    words = WORD.findall(before)
    name = words[-1]
    return name


def add_listings_of_a_file(listings: dict, file_name: str, records: list) -> None:
    for record in records:
        add_one_listing(listings, file_name, record)


def add_one_listing(listings: dict, file_name: str, record: dict) -> None:
    """Rule 63: every listing with a `parsed_as` kind is taken; the ones clang read as another entry are named too."""
    described = listed_described(file_name, record)
    if record.get("parsed_as") is None:
        listings["not_taken"].append(described)
    else:
        listings["every_listing"].append(described)
        add_a_listing(listings["by_text"], file_name, record, described)
    if not record["parsed_as_written"]:
        listings["not_parsed_as_written"].append(f"{file_name}: {record['position']}: {record['template']} "
                                                 f"({record['name']})")


def listed_described(file_name: str, record: dict) -> dict:
    """Rule 63: one listing as its file lists it, with what clang read it as."""
    described = {}
    described["file"] = file_name
    described["position"] = record.get("position")
    described["name"] = record["name"]
    described["listing"] = record["template"]
    described["parsed_as"] = record.get("parsed_as")
    described["detail"] = record.get("detail")
    described["parsed_as_written"] = record["parsed_as_written"]
    described["holders"] = record.get("holders", [])
    return described


def add_a_listing(by_text: dict, file_name: str, record: dict, described: dict) -> None:
    """Rule 63: one entry per text, from its first listing clang parsed as written, or else its first; every
    listing written so is kept beside it."""
    text = record["template"]
    listed_as = []
    if text in by_text:
        listed_as = by_text[text]["listed_as"]
    if text not in by_text or (record["parsed_as_written"] and not by_text[text]["parsed_as_written"]):
        by_text[text] = listing_entry(text, record, file_name, [])
        by_text[text]["listed_as"] = listed_as
    by_text[text]["listed_as"].append(described)


def check_the_texts_listed_twice(listings: dict) -> None:
    """Rule 63: listings written the same are one program, so they must take the same holders."""
    for text in listings["by_text"]:
        for described in listings["by_text"][text]["listed_as"]:
            if described["holders"] != listings["by_text"][text]["holders"]:
                stop(f"read_components: {text!r} is listed twice with different holders; nothing is run")


def read_as_the_same_entry(every_listing: list) -> list:
    """Rule 63: the listings clang read as the same entry, `parsed_as` and `detail` alike, two or more, at least
    one of them read as an entry other than the one listed (forms of one kind clang parsed as written, as
    `if (a) b;` and `if (a) b; else c;`, are each their own entry)."""
    by_entry = {}
    for described in every_listing:
        add_to_a_list(by_entry, f"{described['parsed_as']} {described['detail']}", described)
    entries = []
    for key in by_entry:
        if len(by_entry[key]) >= 2 and not all_listed_as_written(by_entry[key]):
            entries.append({"entry": key, "listings": by_entry[key]})
    return entries


def all_listed_as_written(listed: list) -> bool:
    every = True
    for described in listed:
        if not described["parsed_as_written"]:
            every = False
    return every


def listing_entry(text: str, record: dict, file_name: str, taken: list) -> dict:
    entry = {}
    entry["listing"] = text
    entry["kind"] = record["name"]
    entry["position"] = record["position"]
    entry["file"] = file_name
    entry["holders"] = record.get("holders", [])
    entry["kept_as"] = record.get("kept_as")
    entry["is_statement"] = is_statement_kind(record["name"])
    entry["taken_by_the_lowerer"] = taken
    entry["components"] = components_of(text, record, taken)
    entry["fill"] = "int"
    entry["fill_answers"] = {}
    entry["alone"] = None
    entry["role"] = "neither"
    entry["parsed_as"] = record.get("parsed_as")
    entry["detail"] = record.get("detail")
    entry["parsed_as_written"] = record.get("parsed_as_written", True)
    entry["listed_as"] = []
    entry["prelude"] = record.get("prelude", [])
    entry["context"] = TODAYS_CONTEXT
    entry["fill_overrides"] = {}
    entry["fill_answer_sorts"] = {}
    return entry


# Rule 70 : declarations as components


def add_the_declarations(listings: dict, part: str) -> None:
    """Rule 70: each declaration a listing of one component that holds nothing, in the parts that arrange them."""
    if part_name(part) in ("declarations", "small_run_upgrades"):
        for declaration in DECLARATIONS:
            listings["by_text"][declaration["declaration"]] = declaration_entry(declaration)


def declaration_entry(declaration: dict) -> dict:
    record = {}
    record["template"] = declaration["declaration"]
    record["name"] = "DeclStmt"
    record["position"] = None
    record["holders"] = []
    record["parsed_as"] = "DeclStmt"
    record["detail"] = declaration["name"]
    record["parsed_as_written"] = True
    record["prelude"] = declaration["prelude"]
    entry = listing_entry(declaration["declaration"], record, DECLARATION_FILE, [])
    entry["components"][0]["component"] = declaration["name"]
    entry["role"] = "declaration"
    entry["declaration"] = declaration
    return entry


def declaration_named(text: str):
    found = None
    for declaration in DECLARATIONS:
        if declaration["declaration"] == text:
            found = declaration
    return found


# Rule 74: the small run's listings


def small_run_selection(listings: dict) -> dict:
    """Rule 74: SMALL_RUN's listings, each listing read as the same entry as one of its row 1 listings, and every
    100th of the listings in rule 63's order; each text once, with why it was chosen."""
    chosen = {"entries": [], "texts": []}
    for entry in SMALL_RUN:
        add_a_chosen_text(chosen, listings, entry["listing"], entry["name"], entry["rows"], "named in the small run")
    for entry in SMALL_RUN:
        if 1 in entry["rows"]:
            add_the_same_entry_partners(chosen, listings, entry)
    every = listings["every_listing"]
    for index in range(0, len(every), SMALL_RUN_STRIDE):
        add_a_chosen_text(chosen, listings, every[index]["listing"], every[index]["name"], [],
                          f"every {SMALL_RUN_STRIDE}th listing: number {index} of {len(every)}, counted from 0")
    return chosen


def add_a_chosen_text(chosen: dict, listings: dict, text: str, name, rows: list, why: str) -> None:
    if text not in listings["by_text"]:
        stop(f"the small run: no listing {text!r}; nothing is run")
    if name is not None and name not in names_listed_as(listings["by_text"][text]):
        stop(f"the small run: {text!r} is not listed under {name}; nothing is run")
    if text not in chosen["texts"]:
        chosen["texts"].append(text)
        chosen["entries"].append({"listing": text, "names": [], "rows": [], "why": []})
    entry = chosen["entries"][chosen["texts"].index(text)]
    if name is not None:
        add_new(entry["names"], name)
    add_new(entry["why"], why)
    for row in rows:
        add_new(entry["rows"], row)


def names_listed_as(listing: dict) -> list:
    names = []
    for described in listing["listed_as"]:
        names.append(described["name"])
    return names


def add_the_same_entry_partners(chosen: dict, listings: dict, entry: dict) -> None:
    """Rule 74: every listing clang read as the same entry as the named one."""
    described = described_by_name(listings["by_text"][entry["listing"]], entry["name"])
    key = f"{described['parsed_as']} {described['detail']}"
    for same in listings["read_as_the_same_entry"]:
        if same["entry"] == key:
            add_partners(chosen, listings, same, entry)


def add_partners(chosen: dict, listings: dict, same: dict, entry: dict) -> None:
    for partner in same["listings"]:
        add_a_chosen_text(chosen, listings, partner["listing"], partner["name"], [1],
                          f"read as the same entry as {entry['listing']} ({same['entry']})")


def described_by_name(listing: dict, name) -> dict:
    found = listing["listed_as"][0]
    for described in listing["listed_as"]:
        if described["name"] == name:
            found = described
    return found


def is_statement_kind(name: str) -> bool:
    """Rule 28: DRY_mask_maker's is_statement, as it reads a kind."""
    kind = name.split(".")[0]
    statement = kind.endswith("Stmt")
    return statement


def components_of(text: str, record: dict, taken: list) -> list:
    """The components of one listing, in the order written (rules 3 to 7, 29 to 31)."""
    pieces = pieces_of(text)
    held = held_statements(pieces, taken)
    components = []
    start = 0
    for statement in held:
        before = pieces[start:statement["at"]]
        add_component(components, before, statement["letter"], record)
        start = statement["ends"] + 1
    rest = pieces[start:]
    add_component(components, rest, None, record)
    blocks = as_a_block(components, record)
    return blocks


def pieces_of(text: str) -> list:
    """The text cut into pieces, each with what it is (rules 2 and 3)."""
    pieces = []
    for found in PIECE.finditer(text):
        piece = {}
        piece["text"] = found.group(0)
        piece["is"] = what_a_piece_is(found.group(0))
        pieces.append(piece)
    return pieces


def what_a_piece_is(text: str) -> str:
    what = "mark"
    if text in VALUE_LETTERS:
        what = "value"
    elif text in NAME_LETTERS:
        what = "name"
    elif text in TYPE_LETTERS:
        what = "type"
    elif text.isspace():
        what = "space"
    elif WORD.fullmatch(text):
        what = "word"
    return what


def held_statements(pieces: list, taken: list) -> list:
    """Each value placeholder outside parentheses whose next piece, past
    spaces, is `;`, and that the lowerer did not read as taken: its letter,
    where it is, and where its `;` is (rules 4 and 29)."""
    held = []
    depth = 0
    for index in range(len(pieces)):
        depth = depth_after(pieces[index]["text"], depth)
        if pieces[index]["is"] == "value" and depth == 0 and pieces[index]["text"] not in taken:
            add_if_a_statement(held, pieces, index)
    return held


def depth_after(text: str, depth: int) -> int:
    after = depth
    if text == "(":
        after = depth + 1
    if text == ")":
        after = depth - 1
    return after


def add_if_a_statement(held: list, pieces: list, index: int) -> None:
    ends = next_piece_past_spaces(pieces, index)
    if ends is not None and pieces[ends]["text"] == ";":
        statement = {}
        statement["letter"] = pieces[index]["text"]
        statement["at"] = index
        statement["ends"] = ends
        held.append(statement)


def next_piece_past_spaces(pieces: list, index: int):
    found = None
    for later in range(index + 1, len(pieces)):
        if pieces[later]["is"] != "space":
            found = later
            break
    return found


def add_component(components: list, pieces: list, holds, record: dict) -> None:
    """One component from its pieces, when they hold more than spaces (rules 5
    to 7); a held statement with only spaces before it is held by the
    component before (rule 30)."""
    trimmed = without_spaces_at_the_ends(pieces)
    ends_with = statement_end_of(trimmed, holds)
    written = without_the_end(trimmed, ends_with)
    if len(written) > 0:
        component = component_entry(written, holds, ends_with, record, len(components))
        components.append(component)
    elif holds is not None and len(components) > 0:
        components[-1]["holds_all"].append(holds)


def without_spaces_at_the_ends(pieces: list) -> list:
    first = first_piece_not_space(pieces)
    last = last_piece_not_space(pieces)
    trimmed = []
    if first is not None:
        trimmed = pieces[first:last + 1]
    return trimmed


def first_piece_not_space(pieces: list):
    found = None
    for index in range(len(pieces)):
        if pieces[index]["is"] != "space":
            found = index
            break
    return found


def last_piece_not_space(pieces: list):
    found = None
    for index in range(len(pieces) - 1, -1, -1):
        if pieces[index]["is"] != "space":
            found = index
            break
    return found


def statement_end_of(pieces: list, holds) -> str:
    """`;` when the component holds nothing and its last piece is `;` (rule 5)."""
    end = ""
    if holds is None and len(pieces) > 0 and pieces[-1]["text"] == ";":
        end = ";"
    return end


def without_the_end(pieces: list, ends_with: str) -> list:
    written = pieces
    if ends_with != "":
        written = without_spaces_at_the_ends(pieces[:-1])
    return written


def component_entry(pieces: list, holds, ends_with: str, record: dict, number: int) -> dict:
    component = {}
    component["is"] = "component"
    component["component"] = name_of(pieces)
    component["listing"] = record["template"]
    component["kind"] = record["name"]
    component["position"] = record["position"]
    component["number_in_listing"] = number
    component["written"] = joined(pieces)
    component["takes"] = placeholders_in(pieces)
    component["values"] = values_in(pieces)
    component["holds"] = holds
    component["holds_all"] = holds_all_of(holds)
    component["holds_a_body"] = holds is not None
    component["ends_with"] = ends_with
    component["copy"] = 1
    return component


def holds_all_of(holds) -> list:
    held = []
    if holds is not None:
        held.append(holds)
    return held


def as_a_block(components: list, record: dict) -> list:
    """Rule 30: `{` and `}` around held statements are one component, `{ }`."""
    blocks = components
    if is_a_block(components):
        block = dict(components[0])
        block["component"] = "{ }"
        block["written"] = ""
        block["holds_all"] = list(components[0]["holds_all"])
        blocks = [block]
    return blocks


def is_a_block(components: list) -> bool:
    block = False
    if len(components) == 2 and components[0]["written"] == "{" and components[1]["written"] == "}":
        block = components[0]["holds_a_body"] and not components[1]["holds_a_body"]
    return block


def name_of(pieces: list) -> str:
    """Rules 7 and 31: the keyword, its marks, and what it takes; or the label, as written."""
    keyword = keyword_of(pieces)
    taken = taken_as_written(pieces)
    name = joined(pieces)
    if keyword is not None and taken == "":
        name = keyword
    if keyword is not None and taken != "":
        name = f"{keyword}{marks_after_the_keyword(pieces)}({taken})"
    return name


def keyword_of(pieces: list):
    keyword = None
    for piece in pieces:
        if piece["is"] == "word":
            keyword = piece["text"]
            break
    return keyword


def marks_after_the_keyword(pieces: list) -> str:
    """Rule 31: the marks between the keyword and what it takes, other than spaces and `(`."""
    marks = []
    after_the_keyword = False
    for piece in pieces:
        if after_the_keyword and (is_placeholder(piece) or piece["text"] == "("):
            break
        if after_the_keyword and piece["is"] == "mark":
            marks.append(piece["text"])
        if piece["is"] == "word":
            after_the_keyword = True
    written = "".join(marks)
    return written


def taken_as_written(pieces: list) -> str:
    """Rule 31: inside the parentheses, all of it, when there are any; else
    from the first placeholder to the last, as written (rule 7)."""
    inside = inside_the_parentheses(pieces)
    taken = inside
    if inside is None:
        taken = first_to_last_placeholder(pieces)
    return taken


def inside_the_parentheses(pieces: list):
    """The text inside the component's first parentheses, when a placeholder is in them."""
    opened = None
    closed = None
    for index in range(len(pieces)):
        if pieces[index]["text"] == "(" and opened is None:
            opened = index
        if pieces[index]["text"] == ")" and opened is not None and closed is None:
            closed = index
    inside = None
    if opened is not None and closed is not None and has_a_placeholder(pieces[opened + 1:closed]):
        inside = joined(pieces[opened + 1:closed])
    return inside


def has_a_placeholder(pieces: list) -> bool:
    found = False
    for piece in pieces:
        if is_placeholder(piece):
            found = True
    return found


def first_to_last_placeholder(pieces: list) -> str:
    first = first_placeholder(pieces)
    last = last_placeholder(pieces)
    taken = ""
    if first is not None:
        taken = joined(pieces[first:last + 1])
    return taken


def first_placeholder(pieces: list):
    found = None
    for index in range(len(pieces)):
        if is_placeholder(pieces[index]):
            found = index
            break
    return found


def last_placeholder(pieces: list):
    found = None
    for index in range(len(pieces) - 1, -1, -1):
        if is_placeholder(pieces[index]):
            found = index
            break
    return found


def is_placeholder(piece: dict) -> bool:
    placeholder = piece["is"] in ("value", "name", "type")
    return placeholder


def placeholders_in(pieces: list) -> list:
    placeholders = []
    for piece in pieces:
        if is_placeholder(piece):
            placeholders.append(piece["text"])
    return placeholders


def values_in(pieces: list) -> list:
    values = []
    for piece in pieces:
        if piece["is"] == "value":
            values.append(piece["text"])
    return values


def joined(pieces: list) -> str:
    texts = []
    for piece in pieces:
        texts.append(piece["text"])
    text = "".join(texts)
    return text


def check_the_components(listings: dict) -> None:
    """Rule 8."""
    differences = component_differences(listings)
    if len(differences) > 0:
        stop("read_components: the components differ from the plan's section 3: " + "; ".join(differences))


def component_differences(listings: dict) -> list:
    differences = []
    for text in EXPECTED_COMPONENTS:
        described = described_components(listings["by_text"][text]["components"])
        if described != EXPECTED_COMPONENTS[text]:
            differences.append(f"{text!r} gives {described}, the plan {EXPECTED_COMPONENTS[text]}")
    return differences


def described_components(components: list) -> list:
    described = []
    for component in components:
        described.append(described_component(component))
    return described


def described_component(component: dict) -> str:
    described = component["component"]
    if component["holds_a_body"]:
        described = described + " holds a body"
    return described


# Rule 29: held or taken


def ask_held_or_taken(listings: dict, lowerer: dict) -> None:
    """Rules 29 and 68: for each placeholder read as held, the lowerer answers whether it is, where tree-sitter
    cannot, and for every 10th listing tree-sitter can, as a check; for every listing when a check disagrees."""
    asked = texts_to_ask(listings)
    questions = held_or_taken_questions(listings, asked)
    answers = answers_of_listing_programs(questions, lowerer)
    disagreements = tree_sitter_disagreements(listings, questions, answers)
    if len(disagreements) > 0:
        asked = texts_with_held_letters(listings)
        questions = held_or_taken_questions(listings, asked)
        answers = answers_of_listing_programs(questions, lowerer)
    taken = taken_by_the_lowerer(questions, answers)
    add_what_tree_sitter_reads_as_taken(taken, listings, asked)
    listings["held_or_taken"] = held_or_taken_record(questions, answers)
    listings["tree_sitter_check"] = tree_sitter_check(listings, asked, disagreements, clang_reads(questions, answers))
    read_again_with_what_is_taken(listings, taken)


def held_or_taken_questions(listings: dict, texts: list) -> list:
    questions = []
    for text in texts:
        add_held_or_taken_questions(questions, listings["by_text"][text], listings)
    return questions


def add_held_or_taken_questions(questions: list, listing: dict, listings: dict) -> None:
    for component in listing["components"]:
        for letter in component["holds_all"]:
            questions.append(alone_question(listing, letter, "statement", listings))
            questions.append(alone_question(listing, letter, "body", listings))


def alone_question(listing: dict, letter, held_as: str, listings: dict) -> dict:
    question = {}
    question["listing"] = listing
    question["letter"] = letter
    question["held_as"] = held_as
    question["fill"] = "int"
    question["held_in"] = None
    question["with_needs"] = True
    question["program"] = program_alone(listing, listings, "int", True, letter, held_as)["text"]
    return question


def taken_by_the_lowerer(questions: list, answers: list) -> dict:
    """Each listing's letters the lowerer reads as taken: the two answers differ."""
    taken = {}
    for index in range(0, len(questions), 2):
        if not the_same_answer(answers[index], answers[index + 1]):
            add_to_a_list(taken, questions[index]["listing"]["listing"], questions[index]["letter"])
    return taken


def the_same_answer(first: dict, second: dict) -> bool:
    same = first["accepted"] == second["accepted"] and first["message"] == second["message"]
    return same


def add_to_a_list(lists: dict, key, item) -> None:
    if key not in lists:
        lists[key] = []
    lists[key].append(item)


def read_again_with_what_is_taken(listings: dict, taken: dict) -> None:
    for text in taken:
        listing = listings["by_text"][text]
        record = listing_as_a_record(listing)
        listings["by_text"][text] = listing_entry(text, record, listing["file"], taken[text])
        carry_over(listing, listings["by_text"][text])


def carry_over(old: dict, new: dict) -> None:
    """What a listing read again keeps from its first reading (rules 63 and 68)."""
    for key in ("listed_as", "tree_sitter", "held_or_taken_by"):
        if key in old:
            new[key] = old[key]


def listing_as_a_record(listing: dict) -> dict:
    record = {}
    record["template"] = listing["listing"]
    record["name"] = listing["kind"]
    record["position"] = listing["position"]
    record["holders"] = listing["holders"]
    record["kept_as"] = listing["kept_as"]
    record["parsed_as"] = listing["parsed_as"]
    record["detail"] = listing["detail"]
    record["parsed_as_written"] = listing["parsed_as_written"]
    record["prelude"] = listing["prelude"]
    return record


# Rule 68 : held or taken, read first with tree-sitter's C grammar


def tree_sitter_parser():
    """tree-sitter's C grammar; the run stops by name when it is not installed."""
    try:
        import tree_sitter
        import tree_sitter_c
    except ImportError:
        stop("read_components: tree_sitter and tree_sitter_c are needed (rule 68); nothing is run")
    language = tree_sitter.Language(tree_sitter_c.language())
    parser = tree_sitter.Parser(language)
    return parser


def read_held_or_taken_with_tree_sitter(listings: dict) -> None:
    """Rule 68: each listing's value placeholders, held or taken, as tree-sitter reads them."""
    parser = tree_sitter_parser()
    for text in listings["by_text"]:
        listings["by_text"][text]["tree_sitter"] = tree_sitter_reading(parser, listings["by_text"][text])


def tree_sitter_reading(parser, listing: dict) -> dict:
    source = tree_sitter_source(listing)
    tree = parser.parse(source.encode("utf-8"))
    body = function_body_of(tree.root_node)
    reading = {}
    reading["source"] = source
    reading["parsed"] = not tree.root_node.has_error
    reading["parts"] = {}
    for letter in own_values_of(listing["listing"]):
        reading["parts"][letter] = part_read_by_tree_sitter(placeholder_node(body, letter, source), body, source)
    return reading


def tree_sitter_source(listing: dict) -> str:
    """The listing inside a function; an expression as a statement."""
    text = listing["listing"]
    if not listing["is_statement"]:
        text = text + ";"
    source = TREE_SITTER_FUNCTION.format(text)
    return source


def function_body_of(root):
    """The function's body. tree-sitter's own names (`parent`, `children`, ...) are its API's, used as they are."""
    body = root
    for node in root.children:
        if node.type == "function_definition" and node.child_by_field_name("body") is not None:
            body = node.child_by_field_name("body")
    return body


def placeholder_node(body, letter: str, source: str):
    """The first node in the function's body named by the placeholder's letter."""
    found = None
    waiting = [body]
    while len(waiting) > 0 and found is None:
        node = waiting.pop(0)
        if node.type.endswith("identifier") and node_text(node, source) == letter:
            found = node
        add_all(waiting, node.children)
    return found


def node_text(node, source: str) -> str:
    text = source.encode("utf-8")[node.start_byte:node.end_byte].decode("utf-8")
    return text


def part_read_by_tree_sitter(node, body, source: str) -> dict:
    """Held: the placeholder is a statement of its own (an expression statement holding only it); taken otherwise."""
    part = {"read": "not found", "field": None, "path": []}
    if node is not None:
        part["read"] = held_or_taken_of_a_node(node, source)
        part["path"] = path_above(node, body)
        part["field"] = nearest_field(part["path"])
    return part


def held_or_taken_of_a_node(node, source: str) -> str:
    read = "taken"
    above = node.parent
    if above is not None and above.type == "expression_statement" and \
            node_text(above, source).replace(" ", "") == node_text(node, source) + ";":
        read = "held"
    return read


def path_above(node, body) -> list:
    """From the listing's own node down to the placeholder: each node's type, with the field it holds the next in."""
    steps = []
    below = node
    while below.parent is not None and below.parent.id != body.id and below.id != body.id:
        above = below.parent
        steps.insert(0, {"node": above.type, "field": field_holding(above, below)})
        below = above
    return steps


def field_holding(above, below):
    """The field of the node above that holds the node below, or None."""
    field = None
    for index in range(above.child_count):
        if above.children[index].id == below.id:
            field = above.field_name_for_child(index)
    return field


def nearest_field(path: list):
    """The field nearest the placeholder: `consequence`, `condition`, `body`, ..."""
    field = None
    for step in path:
        if step["field"] is not None:
            field = step["field"]
    return field


def texts_with_held_letters(listings: dict) -> list:
    texts = []
    for text in listings["by_text"]:
        if len(held_letters_of(listings["by_text"][text])) > 0:
            texts.append(text)
    return texts


def texts_to_ask(listings: dict) -> list:
    """Rule 68: of the listings with a placeholder rule 4 reads as held, every one tree-sitter did not parse, and
    every 10th one it did, in their order."""
    asked = []
    parsed = 0
    for text in texts_with_held_letters(listings):
        if not listings["by_text"][text]["tree_sitter"]["parsed"]:
            asked.append(text)
        else:
            add_every_tenth(asked, text, parsed)
            parsed += 1
    return asked


def add_every_tenth(asked: list, text: str, parsed: int) -> None:
    if parsed % TREE_SITTER_CHECK_EVERY == 0:
        asked.append(text)


def clang_reads(questions: list, answers: list) -> dict:
    """Rule 29's answers, held or taken, by listing and letter."""
    reads = {}
    for index in range(0, len(questions), 2):
        key = (questions[index]["listing"]["listing"], questions[index]["letter"])
        reads[key] = held_or_taken_word(answers[index], answers[index + 1])
    return reads


def tree_sitter_disagreements(listings: dict, questions: list, answers: list) -> list:
    """Rule 68: a listing tree-sitter parsed and clang was asked about, read differently."""
    reads = clang_reads(questions, answers)
    disagreements = []
    for key in reads:
        reading = listings["by_text"][key[0]]["tree_sitter"]
        if reading["parsed"] and reading["parts"][key[1]]["read"] != reads[key]:
            disagreements.append({"listing": key[0], "letter": key[1], "tree_sitter": reading["parts"][key[1]],
                                  "clang": reads[key]})
    return disagreements


def add_what_tree_sitter_reads_as_taken(taken: dict, listings: dict, asked: list) -> None:
    """Rule 68: a listing clang was not asked about takes tree-sitter's answer."""
    for text in texts_with_held_letters(listings):
        if text not in asked:
            add_letters_tree_sitter_takes(taken, listings["by_text"][text])


def add_letters_tree_sitter_takes(taken: dict, listing: dict) -> None:
    for letter in held_letters_of(listing):
        if listing["tree_sitter"]["parts"][letter]["read"] == "taken":
            add_to_a_list(taken, listing["listing"], letter)


def tree_sitter_check(listings: dict, asked: list, disagreements: list, reads: dict) -> dict:
    """Rule 68's record: what tree-sitter read, what clang was asked, and where the two agree."""
    check = {"listings_with_a_held_placeholder": 0, "tree_sitter_parsed": 0, "tree_sitter_erred": 0,
             "asked_of_clang": len(asked), "checked": 0, "agree": 0, "disagreements": disagreements,
             "asked_every_listing": len(disagreements) > 0}
    for text in texts_with_held_letters(listings):
        listing = listings["by_text"][text]
        listing["held_or_taken_by"] = held_or_taken_by(listing, text in asked, reads)
        check["listings_with_a_held_placeholder"] += 1
        add_one_tree_sitter_count(check, listing, text in asked)
    return check


def add_one_tree_sitter_count(check: dict, listing: dict, was_asked: bool) -> None:
    if listing["tree_sitter"]["parsed"]:
        check["tree_sitter_parsed"] += 1
    else:
        check["tree_sitter_erred"] += 1
    if listing["tree_sitter"]["parsed"] and was_asked:
        check["checked"] += 1
    if listing["tree_sitter"]["parsed"] and was_asked and agrees_with_clang(listing) is not False:
        check["agree"] += 1


def held_or_taken_by(listing: dict, was_asked: bool, reads: dict) -> dict:
    """Per listing: tree-sitter's answer, clang's where asked, whether they agree, and which was used."""
    by = {}
    for letter in held_letters_of(listing):
        entry = {}
        entry["tree_sitter"] = listing["tree_sitter"]["parts"][letter]["read"]
        entry["field"] = listing["tree_sitter"]["parts"][letter]["field"]
        entry["clang"] = reads.get((listing["listing"], letter))
        entry["agree"] = None
        if entry["clang"] is not None and listing["tree_sitter"]["parsed"]:
            entry["agree"] = entry["clang"] == entry["tree_sitter"]
        entry["used"] = "tree-sitter"
        if was_asked:
            entry["used"] = "clang"
        by[letter] = entry
    return by


def agrees_with_clang(listing: dict):
    """True when every letter clang was asked about reads the same as tree-sitter's; False when one does not;
    None when clang was not asked, or tree-sitter could not parse the listing."""
    agrees = None
    for letter in listing.get("held_or_taken_by", {}):
        agrees = agreement_of_a_letter(agrees, listing["held_or_taken_by"][letter]["agree"])
    return agrees


def agreement_of_a_letter(agrees, letter_agrees):
    result = agrees
    if letter_agrees is False:
        result = False
    if letter_agrees is True and agrees is None:
        result = True
    return result


def held_or_taken_record(questions: list, answers: list) -> list:
    record = []
    for index in range(0, len(questions), 2):
        entry = {}
        entry["listing"] = questions[index]["listing"]["listing"]
        entry["letter"] = questions[index]["letter"]
        entry["as_a_statement"] = answer_described(answers[index])
        entry["as_a_body"] = answer_described(answers[index + 1])
        entry["read"] = held_or_taken_word(answers[index], answers[index + 1])
        record.append(entry)
    return record


def held_or_taken_word(first: dict, second: dict) -> str:
    word = "taken"
    if the_same_answer(first, second):
        word = "held"
    return word


def answer_described(answer: dict) -> str:
    described = "accepted"
    if not answer["accepted"]:
        described = f"refused at line {answer['line']}: {answer['message']}"
    return described


# Rules 32 to 35, 39 and 40: the fills, the holders and the dependents


def ask_the_fills(listings: dict, lowerer: dict, part: str) -> None:
    """Rules 32, 33, 39 and 40, for the listings the part uses; rules 66, 64 and 72 between them."""
    used = listings_the_part_uses(listings, part)
    ask_each_alone(listings, used, lowerer)
    ask_each_with_one_constant(listings, used, lowerer)
    ask_each_in_the_other_contexts(listings, used, lowerer)
    mark_the_test_program_refusals(listings, used, lowerer)
    mark_the_holders(listings, used)
    ask_each_held_in_the_holders(listings, used, lowerer)
    ask_each_without_what_it_needs(listings, used, lowerer)
    mark_the_dependents(listings, used)
    listings["used"] = used


def listings_the_part_uses(listings: dict, part: str) -> list:
    """Rule 28: every listing for the part listings; the statement listings and what they need for the rest;
    rule 74: and the small run's listings."""
    chosen = []
    if part_name(part) == "small_run_upgrades":
        listings["small_run"] = small_run_selection(listings)
        chosen = listings["small_run"]["texts"]
    used = []
    for text in listings["by_text"]:
        if part_name(part) == "listings" or uses_in_groups(listings["by_text"][text]) or text in chosen:
            used.append(text)
    return used


def uses_in_groups(listing: dict) -> bool:
    used = listing["is_statement"] or listing["listing"] in NEEDS
    return used


def ask_each_alone(listings: dict, used: list, lowerer: dict) -> None:
    """Rule 32: alone, under each fill in turn, until the lowerer accepts one."""
    waiting = list(used)
    for fill in FILLS:
        questions = fill_questions(listings, waiting, fill, None)
        answers = answers_of_listing_programs(questions, lowerer)
        record_the_fill_answers(listings, questions, answers, "alone")
        waiting = refused_alone(listings, waiting)


def fill_questions(listings: dict, texts: list, fill: str, holder) -> list:
    questions = []
    for text in texts:
        if fill_applies(listings["by_text"][text], fill):
            questions.append(fill_question(listings, text, fill, holder))
    return questions


def fill_applies(listing: dict, fill: str) -> bool:
    """A typed fill needs a holder for each placeholder; a fill other than `int` needs a value to fill."""
    applies = True
    if fill != "int" and len(own_values_of(listing["listing"])) == 0:
        applies = False
    if fill == "typed" and holder_of_each(listing) is None:
        applies = False
    return applies


def fill_question(listings: dict, text: str, fill: str, holder, overrides=None, context=TODAYS_CONTEXT) -> dict:
    """Rule 32's question; rules 64 and 66: in a context, and with placeholders written as names or constants."""
    listing = listings["by_text"][text]
    question = {}
    question["listing"] = listing
    question["letter"] = None
    question["held_as"] = None
    question["fill"] = fill
    question["held_in"] = holder
    question["with_needs"] = True
    question["overrides"] = {}
    if overrides is not None:
        question["overrides"] = overrides
    question["context"] = context
    if holder is None:
        question["program"] = program_alone(listing, listings, fill, True, None, None, question["overrides"],
                                            context)["text"]
    else:
        question["program"] = program_held_in(listing, listings["by_text"][holder], listings, fill)["text"]
    return question


def record_the_fill_answers(listings: dict, questions: list, answers: list, where: str) -> None:
    """Each answer kept with its listing, and its sort (rule 72); the first accepted sets the listing's fill;
    rule 77: the program of a refusal of the listing as written, kept for its evidence."""
    for index in range(len(questions)):
        listing = questions[index]["listing"]
        key = fill_answer_key(questions[index], where)
        listing["fill_answers"][key] = answer_described(answers[index])
        listing["fill_answer_sorts"][key] = sort_of_an_answer(answers[index])
        if listing["fill_answer_sorts"][key] == LISTING_AS_WRITTEN:
            keep_the_program_as_written(listing, key, questions[index]["program"])
        if answers[index]["accepted"] and listing["alone"] is None:
            set_the_fill(listing, questions[index], where)


def keep_the_program_as_written(listing: dict, key: str, program: str) -> None:
    if "as_written_programs" not in listing:
        listing["as_written_programs"] = {}
    listing["as_written_programs"][key] = program


def fill_answer_key(question: dict, where: str) -> str:
    """`alone, typed`; rules 64 and 66: `alone in int f(void), int`, `alone, typed, a as a constant`."""
    key = f"{where}, {question['fill']}"
    if question.get("context", TODAYS_CONTEXT) != TODAYS_CONTEXT:
        key = f"{where} in {question['context']}, {question['fill']}"
    if len(question.get("overrides", {})) > 0:
        key = key + ", " + overrides_written(question["overrides"])
    if question["held_in"] is not None:
        key = f"held in {question['held_in']}, {question['fill']}"
    return key


def overrides_written(overrides: dict) -> str:
    texts = []
    for letter in overrides:
        texts.append(f"{letter} as {override_written(overrides[letter])}")
    written = ", ".join(texts)
    return written


def override_written(form: dict) -> str:
    written = form["form"]
    if form["form"] == "name":
        written = form["text"]
    if form["form"] == "constant":
        written = "a constant"
    if form["form"] == LABEL_TABLE:
        written = "the label table"
    return written


def set_the_fill(listing: dict, question: dict, where: str) -> None:
    listing["fill"] = question["fill"]
    listing["alone"] = where
    listing["fill_overrides"] = question.get("overrides", {})
    listing["context"] = question.get("context", TODAYS_CONTEXT)
    if question["held_in"] is not None:
        listing["alone"] = "refused alone; accepted held in a holder"
        listing["accepted_held_in"] = question["held_in"]


# Rule 66 : one placeholder at a time as a constant, where a refusal asks for one


def ask_each_with_one_constant(listings: dict, used: list, lowerer: dict) -> None:
    """Rule 66: a listing still refused alone, a refusal of it asking for a constant: one value at a time written
    as a constant, the others typed (or `int`), in the order written."""
    questions = []
    for text in refused_alone(listings, used):
        if asks_for_a_constant(listings["by_text"][text]):
            add_all(questions, one_constant_questions(listings, text))
    answers = answers_of_listing_programs(questions, lowerer)
    record_the_fill_answers(listings, questions, answers, "alone")


def asks_for_a_constant(listing: dict) -> bool:
    asks = False
    for key in listing["fill_answers"]:
        if mentions_a_constant(listing["fill_answers"][key]):
            asks = True
    return asks


def mentions_a_constant(answer: str) -> bool:
    found = False
    for piece in CONSTANT_ASKED:
        if piece in answer:
            found = True
    return found


def one_constant_questions(listings: dict, text: str) -> list:
    listing = listings["by_text"][text]
    fill = "typed"
    if not fill_applies(listing, "typed"):
        fill = "int"
    questions = []
    for letter in own_values_of(text):
        if letter not in held_letters_of(listing):
            questions.append(fill_question(listings, text, fill, None, constant_override(listing, letter)))
    return questions


def constant_override(listing: dict, letter: str) -> dict:
    overrides = {}
    overrides[letter] = {"form": "constant", "holder": holder_spelled(listing, letter)}
    return overrides


# Rule 64 : the other contexts


def context_named(name: str) -> dict:
    found = CONTEXTS[0]
    for context in CONTEXTS:
        if context["context"] == name:
            found = context
    return found


def ask_each_in_the_other_contexts(listings: dict, used: list, lowerer: dict) -> None:
    """Rule 64: a listing still refused alone, asked in each other context in turn, with the context's names where
    they fit, then under each fill; the first the lowerer accepts, in that order, is kept."""
    refused = refused_alone(listings, used)
    questions = []
    for context in CONTEXTS[1:]:
        for text in refused:
            add_all(questions, context_questions(listings, text, context))
    answers = answers_of_listing_programs(questions, lowerer)
    record_the_fill_answers(listings, questions, answers, "alone")


def context_questions(listings: dict, text: str, context: dict) -> list:
    listing = listings["by_text"][text]
    questions = []
    names = names_that_fit(listing, context, listings)
    if len(names) > 0:
        questions.append(fill_question(listings, text, "int", None, names, context["context"]))
    for fill in FILLS:
        if fill_applies(listing, fill):
            questions.append(fill_question(listings, text, fill, None, {}, context["context"]))
    return questions


def names_that_fit(listing: dict, context: dict, listings: dict) -> dict:
    """Rule 64: each value placeholder a name of the context fits, by its holder's spelling or class."""
    overrides = {}
    paired = holder_of_each(listing)
    if paired is not None:
        for letter in own_values_of(listing["listing"]):
            add_a_name_that_fits(overrides, letter, paired.get(letter), context, listings)
    return overrides


def add_a_name_that_fits(overrides: dict, letter: str, holder, context: dict, listings: dict) -> None:
    holder_class = listings["holder_classes"].get(holder)
    for name in context["names"]:
        if letter not in overrides and (holder in name["fits"] or holder_class in name["fits"]):
            overrides[letter] = {"form": "name", "holder": holder, "text": name["name"]}


# Rule 72 : refusals sorted by clang's message


def sort_of(message) -> str:
    """What a first error is about, by REFUSAL_SORTS; unsorted when no entry names it."""
    sort = UNSORTED
    if message is not None:
        sort = sort_by_the_table(message)
    return sort


def sort_by_the_table(message: str) -> str:
    found = UNSORTED
    for piece, sort in REFUSAL_SORTS:
        if piece in message and found == UNSORTED:
            found = sort
    return found


def sort_of_an_answer(answer: dict) -> str:
    sort = "accepted"
    if not answer["accepted"]:
        sort = sort_of(answer["message"])
    return sort


def mark_the_test_program_refusals(listings: dict, used: list, lowerer: dict) -> None:
    """Rule 72: a listing refused alone only for the test program, under every fill and in every context, is not
    accepted because of the test program, never a fact about where it may stand. Rule 77: one refused for the
    test program and for the listing as written, at least once for the listing as written, is not accepted as
    written, with clang's evidence."""
    for text in refused_alone(listings, used):
        listing = listings["by_text"][text]
        sorts = sorts_alone(listing)
        if only_the_test_program(sorts):
            listing["not_accepted"] = {"because": TEST_PROGRAM, "messages": messages_alone(listing)}
        elif refused_as_written(sorts):
            listing["not_accepted"] = {"because": LISTING_AS_WRITTEN, "messages": messages_alone(listing),
                                       "evidence": evidence_as_written(listing, lowerer)}


def refused_as_written(sorts: list) -> bool:
    """Rule 77: every refusal the test program's or the listing as written's, and one at least the listing as
    written's."""
    found = False
    others = False
    for sort in sorts:
        if sort == LISTING_AS_WRITTEN:
            found = True
        elif sort != TEST_PROGRAM:
            others = True
    as_written = found and not others
    return as_written


def evidence_as_written(listing: dict, lowerer: dict) -> dict:
    """Rule 77: clang asked once more, alone, for the first program refused as written; the note it gives with
    the refusal, and the lines of the file the note names, from the nearest `#if` above the note's line down to
    it."""
    key = first_key(listing["as_written_programs"])
    folder = os.path.join(lowerer["work_folder"], "as_written")
    os.makedirs(folder, exist_ok=True)
    write_text(os.path.join(folder, "as_written.c"), listing["as_written_programs"][key])
    finished = subprocess.run(lowerer["command"] + ["as_written.c"], cwd=folder, capture_output=True, text=True,
                              timeout=CALL_SECONDS)
    evidence = {}
    evidence["asked"] = key
    evidence["command"] = " ".join(lowerer["command"]) + " as_written.c"
    evidence["exit"] = finished.returncode
    evidence["refusal"] = first_build_error(finished.stderr)
    evidence["note"] = None
    evidence["file"] = None
    evidence["lines"] = None
    evidence["text"] = []
    add_the_note(evidence, finished.stderr)
    return evidence


def first_key(keyed: dict) -> str:
    found = None
    for key in keyed:
        if found is None:
            found = key
    return found


def add_the_note(evidence: dict, output: str) -> None:
    """The first note after the refusal, and the lines of the file it names."""
    seen_the_refusal = False
    for line in output.splitlines():
        if FIRST_ERROR_MARK in line:
            seen_the_refusal = True
        found = NOTE.match(line)
        if seen_the_refusal and found is not None and evidence["note"] is None:
            evidence["note"] = line
            evidence["file"] = found.group("file")
            add_the_lines_of_the_note(evidence, found.group("file"), int(found.group("line")))


def add_the_lines_of_the_note(evidence: dict, path: str, line: int) -> None:
    if os.path.exists(path):
        with open(path, encoding="utf-8", errors="replace") as handle:
            lines = handle.read().splitlines()
        first = first_line_of_the_condition(lines, line)
        evidence["lines"] = f"{first} to {line}"
        for number in range(first, line + 1):
            evidence["text"].append(f"{number}: {lines[number - 1]}")


def first_line_of_the_condition(lines: list, line: int) -> int:
    """The nearest line above `line` (counted from 1) that opens a condition (`#if`, `#ifdef`, `#ifndef`), at most
    NOTE_LINES_ABOVE lines above; the note's own line when there is none."""
    first = line
    number = line - 1
    while number >= 1 and number >= line - NOTE_LINES_ABOVE and first == line:
        if lines[number - 1].strip().startswith("#if"):
            first = number
        number -= 1
    return first


def sorts_alone(listing: dict) -> list:
    sorts = []
    for key in listing["fill_answer_sorts"]:
        if not key.startswith("held in "):
            sorts.append(listing["fill_answer_sorts"][key])
    return sorts


def only_the_test_program(sorts: list) -> bool:
    only = len(sorts) > 0
    for sort in sorts:
        if sort != TEST_PROGRAM:
            only = False
    return only


def messages_alone(listing: dict) -> list:
    messages = []
    for key in listing["fill_answers"]:
        if not key.startswith("held in ") and listing["fill_answers"][key] != "accepted":
            add_new(messages, answer_without_line(listing["fill_answers"][key]))
    return messages


def mark_the_holders(listings: dict, used: list) -> None:
    """Rule 39."""
    holders = []
    for text in used:
        if is_a_holder(listings["by_text"][text]):
            holders.append(text)
            listings["by_text"][text]["role"] = "holder"
    listings["holders"] = holders


def is_a_holder(listing: dict) -> bool:
    holder = listing["is_statement"] and listing["alone"] == "alone" and holds_a_body_in(listing["components"])
    return holder


def holds_a_body_in(components: list) -> bool:
    holds = False
    for component in components:
        if component["holds_a_body"]:
            holds = True
    return holds


def ask_each_held_in_the_holders(listings: dict, used: list, lowerer: dict) -> None:
    """Rule 32: a statement listing refused alone under every fill, held in each holder, under each fill in turn;
    rule 72: not one refused only for the test program."""
    listings["refused_alone"] = refused_alone(listings, used)
    refused = statements_among(listings, not_for_the_test_program(listings, listings["refused_alone"]))
    for fill in FILLS:
        refused = held_in_the_holders_under(listings, refused, fill, lowerer)


def refused_alone(listings: dict, used: list) -> list:
    refused = []
    for text in used:
        if listings["by_text"][text]["alone"] is None:
            refused.append(text)
    return refused


def not_for_the_test_program(listings: dict, texts: list) -> list:
    kept = []
    for text in texts:
        if listings["by_text"][text].get("not_accepted") is None:
            kept.append(text)
    return kept


def statements_among(listings: dict, texts: list) -> list:
    statements = []
    for text in texts:
        if listings["by_text"][text]["is_statement"]:
            statements.append(text)
    return statements


def held_in_the_holders_under(listings: dict, refused: list, fill: str, lowerer: dict) -> list:
    questions = []
    for holder in listings["holders"]:
        add_all(questions, fill_questions(listings, refused, fill, holder))
    answers = answers_of_listing_programs(questions, lowerer)
    record_the_fill_answers(listings, questions, answers, "held")
    still = refused_alone(listings, refused)
    return still


def add_all(items: list, more: list) -> None:
    for item in more:
        items.append(item)


def ask_each_without_what_it_needs(listings: dict, used: list, lowerer: dict) -> None:
    """Rule 40: a listing that needs something, asked alone without it, under its fill."""
    questions = []
    for text in used:
        if text in NEEDS:
            questions.append(without_needs_question(listings, text))
    answers = answers_of_listing_programs(questions, lowerer)
    for index in range(len(questions)):
        questions[index]["listing"]["without_what_it_needs"] = answer_described(answers[index])


def without_needs_question(listings: dict, text: str) -> dict:
    listing = listings["by_text"][text]
    question = {}
    question["listing"] = listing
    question["letter"] = None
    question["held_as"] = None
    question["fill"] = listing["fill"]
    question["held_in"] = None
    question["with_needs"] = False
    question["program"] = program_alone(listing, listings, listing["fill"], False, None, None,
                                        listing["fill_overrides"], listing["context"])["text"]
    return question


def mark_the_dependents(listings: dict, used: list) -> None:
    """Rule 40."""
    dependents = []
    neither = []
    for text in used:
        add_by_role(dependents, neither, listings["by_text"][text])
    listings["dependents"] = dependents
    listings["neither"] = neither


def add_by_role(dependents: list, neither: list, listing: dict) -> None:
    text = listing["listing"]
    if listing.get("accepted_held_in") is not None:
        dependents.append(text)
        listing["role"] = "dependent"
    elif text in NEEDS and listing["alone"] == "alone" and refused_without_needs(listing):
        dependents.append(text)
        listing["role"] = "dependent"
    elif listing.get("not_accepted") is not None:
        listing["role"] = role_not_accepted(listing["not_accepted"])
    elif listing["alone"] is None and listing["is_statement"]:
        neither.append(text)
        listing["role"] = "refused alone and in every holder"


def role_not_accepted(not_accepted: dict) -> str:
    """Rules 72 and 77."""
    role = "not accepted because of the test program"
    if not_accepted["because"] == LISTING_AS_WRITTEN:
        role = "not accepted as written"
    return role


def refused_without_needs(listing: dict) -> bool:
    refused = listing.get("without_what_it_needs", "accepted") != "accepted"
    return refused


# Rule 34: holders and their classes


def holder_classes() -> dict:
    """holders.json: each holder's spelling, with its class."""
    classes = {}
    for holder in read_json(HOLDER_CLASSES)["holders"]:
        classes[holder["spelling"]] = holder["name"]
    return classes


def hand_table(name: str):
    """A table of DRY_mask_maker.py, read from its source, not imported (rules 34 and 57)."""
    tree = ast.parse(read_text(HAND_TABLES))
    found = None
    for node in tree.body:
        if is_the_assignment_of(node, name):
            found = ast.literal_eval(node.value)
    if found is None:
        stop(f"the hand table {name} is not in {relative_to_pchq(HAND_TABLES)}; nothing is run")
    return found


def is_the_assignment_of(node, name: str) -> bool:
    assignment = False
    if isinstance(node, ast.Assign) and len(node.targets) == 1 and isinstance(node.targets[0], ast.Name):
        assignment = node.targets[0].id == name
    return assignment


def held_type_declarations() -> list:
    declarations = hand_table("C_HELD_TYPES")
    return declarations


def function_pointer_holders() -> list:
    """The holders C_HELD_TYPES declares as pointers to functions (`fnptr`)."""
    names = []
    for declaration in held_type_declarations():
        found = FUNCTION_POINTER_TYPEDEF.match(declaration)
        if found is not None:
            names.append(found.group(1))
    return names


def holder_of_each(listing: dict):
    """Rule 34: each value or type placeholder's holder, in the order written; None when they do not pair."""
    letters = value_and_type_letters(listing["listing"])
    holders = listing["holders"]
    paired = None
    if len(letters) == len(holders) and len(holders) > 0:
        paired = {}
        for index in range(len(letters)):
            paired[letters[index]] = holders[index]
    return paired


def value_and_type_letters(text: str) -> list:
    letters = []
    for piece in pieces_of(text):
        if piece["is"] in ("value", "type"):
            letters.append(piece["text"])
    return letters


def own_values_of(text: str) -> list:
    letters = []
    for piece in pieces_of(text):
        if piece["is"] == "value":
            letters.append(piece["text"])
    return letters


def form_of(listing: dict, letter: str, fill: str, listings: dict) -> dict:
    """Rules 32 to 35: how one value or type placeholder is written under a fill."""
    holder = holder_spelled(listing, letter)
    form = {}
    form["holder"] = holder
    form["form"] = "int"
    if letter in TYPE_LETTERS:
        form["form"] = "type"
    elif fill == "constant":
        form["form"] = "constant"
    elif fill == "typed":
        form["form"] = typed_form(holder, listings)
    elif fill == "address":
        form["form"] = "address"
        form["holder"] = holder or "int"
    return form


def holder_spelled(listing: dict, letter: str):
    paired = holder_of_each(listing)
    holder = None
    if paired is not None and letter in paired:
        holder = C_TYPE_SPELLING.get(paired[letter], paired[letter])
    if holder is None and letter in TYPE_LETTERS:
        holder = "int"
    return holder


def typed_form(holder, listings: dict) -> str:
    """Rule 34: `int`, by value, or by address, by the holder's class."""
    holder_class = listings["holder_classes"].get(holder_unspelled(holder))
    form = "address"
    if holder_class in INTEGER_CLASSES:
        form = "int"
    elif holder_class in VALUE_CLASSES:
        form = "value"
    return form


def holder_unspelled(holder) -> str:
    unspelled = holder
    for spelling in C_TYPE_SPELLING:
        if C_TYPE_SPELLING[spelling] == holder:
            unspelled = spelling
    return unspelled


def component_forms(component: dict, listing: dict, fill: str, listings: dict) -> dict:
    """Rules 32 to 35: how each value or type a component takes is written, under its listing's fill; rule 66: a
    value the listing writes as a constant. In a group a context's names are not in reach (rule 64)."""
    forms = {}
    for letter in component["takes"]:
        if letter in VALUE_LETTERS or letter in TYPE_LETTERS:
            forms[letter] = form_of(listing, letter, fill, listings)
    apply_the_overrides(forms, listing.get("fill_overrides", {}), ("constant", LABEL_TABLE))
    return forms


def apply_the_overrides(forms: dict, overrides: dict, which: tuple) -> None:
    """Rules 64, 66 and 67: a placeholder written as a context's name, a constant, or the label table."""
    for letter in overrides:
        if letter in forms and overrides[letter]["form"] in which:
            forms[letter] = overrides[letter]


# 2. arrange


def arrange(listings: dict, lowerer: dict, part: str) -> dict:
    """Every arrangement of each group of the part (rules 9 to 14, 36 to 43);
    trimmed in the parts that trim (rule 38)."""
    groups = groups_of_the_part(listings, part)
    searched = searched_groups(groups, lowerer, part)
    arrangements = arrangements_record(listings, groups, searched, part)
    check_the_counts(arrangements, part)
    return arrangements


def groups_of_the_part(listings: dict, part: str) -> list:
    """Rule 36."""
    name = part_name(part)
    groups = []
    if name in ("step_1_again", "step_1_trimmed"):
        groups = step_1_groups(listings)
    elif name == "listings":
        groups = groups_of_one_listing(listings)
    elif name in ("switch_untrimmed", "switch_trimmed"):
        groups = [group_of("switch", "step 3", SWITCH_GROUP, listings, "numbered")]
    elif name in ("do_untrimmed", "do_trimmed"):
        groups = [group_of("do", "step 3", DO_GROUP, listings, "numbered")]
    elif name == "pairs":
        groups = pair_groups(listings, False)
    elif name == "label_table_pairs":
        groups = the_slice(pair_groups(listings, True), part)
    elif name == "two_of_the_same":
        groups = groups_of_two_of_the_same(listings)
    elif name == "triples":
        groups = triple_groups(listings, part)
    elif name == "declarations":
        groups = declaration_groups(listings)
    elif name == "small_run_upgrades":
        groups = small_run_groups(listings)
    return groups


def declaration_groups(listings: dict) -> list:
    """Rule 70: each declaration with `goto m;` and `m: a;`; the variable-length array with `case a: b;` and
    `switch (a) b;`."""
    groups = []
    for entry in DECLARATION_GROUPS:
        groups.append(declaration_group(entry, listings))
    return groups


def declaration_group(entry: dict, listings: dict) -> dict:
    texts = [entry["declaration"], entry["dependent"], entry["holder"]]
    name = " | ".join([declaration_named(entry["declaration"])["name"], entry["dependent"], entry["holder"]])
    group = group_of(name, "declaration", texts, listings, "numbered")
    group["dependent"] = entry["dependent"]
    group["holders"] = [entry["holder"]]
    group["declaration"] = entry["declaration"]
    return group


def small_run_groups(listings: dict) -> list:
    """Rule 74: each listing of the small run alone; the pairs of `case a ... b: c;`; the declarations' groups."""
    groups = []
    for text in listings["small_run"]["texts"]:
        groups.append(group_alone(text))
    for dependent in SMALL_RUN_PAIRS:
        add_all(groups, merged_when_written_the_same(pairs_of_one(dependent, listings)))
    add_all(groups, declaration_groups(listings))
    return groups


def pairs_of_one(dependent: str, listings: dict) -> list:
    groups = []
    if dependent in listings["dependents"]:
        add_pairs_of(groups, dependent, listings)
    return groups


def step_1_groups(listings: dict) -> list:
    groups = []
    for name in GROUPS:
        groups.append(group_of(name, "step 1", GROUPS[name], listings, "numbered"))
    return groups


def groups_of_one_listing(listings: dict) -> list:
    """Rule 36, the part listings: each listing alone is a group of one arrangement."""
    groups = []
    for text in listings["used"]:
        groups.append(group_alone(text))
    return groups


def group_alone(text: str) -> dict:
    group = {}
    group["group"] = text
    group["family"] = "alone"
    group["listings"] = [text]
    group["dependents"] = []
    group["components"] = []
    group["also_for"] = []
    return group


def group_of(name: str, family: str, texts: list, listings: dict, constants: str) -> dict:
    """A group of components (rules 9 and 37): each listing's components in turn, a listing named twice giving copies."""
    components = group_components(texts, listings)
    group = {}
    group["group"] = name
    group["family"] = family
    group["listings"] = texts
    group["dependents"] = dependents_among(texts, listings)
    group["constants"] = constants
    group["components"] = components
    group["types"] = type_of_each(components)
    group["type_copies"] = copies_by_type(components, group["types"])
    group["copies"] = count_of_each_type(group["type_copies"])
    group["inert_calls"] = 2 + count_holding_a_body(components)
    group["values"] = count_inert_values(components)
    group["lines"] = group["inert_calls"] + len(components)
    group["typed"] = uses_a_typed_fill(components)
    group["held_types"] = listings["holder_types"]
    group["also_for"] = []
    group["context"] = TODAYS_CONTEXT
    group["label_table"] = False
    group["prelude"] = preludes_of_the_texts(texts, listings)
    return group


def preludes_of_the_texts(texts: list, listings: dict) -> list:
    """Rule 70: the lines the group's declarations need before the function."""
    preludes = []
    for text in texts:
        for line in listings["by_text"][text]["prelude"]:
            add_new(preludes, line)
    return preludes


def group_components(texts: list, listings: dict) -> list:
    components = []
    seen = {}
    for text in texts:
        seen[text] = seen.get(text, 0) + 1
        add_components_of(components, listings["by_text"][text], seen[text], listings)
    return components


def add_components_of(components: list, listing: dict, copy: int, listings: dict) -> None:
    for component in listing["components"]:
        components.append(component_in_a_group(component, listing, copy, listings))


def component_in_a_group(component: dict, listing: dict, copy: int, listings: dict) -> dict:
    """Rule 37: a copy is named with `, second`; every component carries its forms."""
    in_a_group = dict(component)
    in_a_group["copy"] = copy
    in_a_group["forms"] = component_forms(component, listing, listing["fill"], listings)
    in_a_group["of_a_statement"] = listing["is_statement"]
    if copy == 2:
        in_a_group["component"] = component["component"] + ", second"
    return in_a_group


def dependents_among(texts: list, listings: dict) -> list:
    dependents = []
    for text in texts:
        if text in listings.get("dependents", []) and text not in dependents:
            dependents.append(text)
    return dependents


def type_of_each(components: list) -> list:
    """Rule 37: each component's type, the first component of its listing and place in it."""
    types = []
    firsts = []
    for component in components:
        key = (component["listing"], component["number_in_listing"])
        if key not in firsts:
            firsts.append(key)
        types.append(firsts.index(key))
    return types


def copies_by_type(components: list, types: list) -> list:
    copies = []
    for index in range(len(components)):
        if types[index] == len(copies):
            copies.append([])
        copies[types[index]].append(components[index])
    return copies


def count_of_each_type(type_copies: list) -> list:
    counts = []
    for copies in type_copies:
        counts.append(len(copies))
    return counts


def count_holding_a_body(lines: list) -> int:
    count = 0
    for line in lines:
        if holds_a_body(line):
            count += 1
    return count


def count_inert_values(components: list) -> int:
    count = 0
    for component in components:
        count += len(inert_values_of(component))
    return count


def inert_values_of(component: dict) -> list:
    """The values a component takes that are inert calls, not constants (rules 16 and 35) nor names (rule 64)."""
    values = []
    for letter in component["values"]:
        if component["forms"][letter]["form"] not in ("constant", "name"):
            values.append(letter)
    return values


def uses_a_typed_fill(components: list) -> bool:
    typed = False
    for component in components:
        if has_a_typed_form(component["forms"]):
            typed = True
    return typed


def has_a_typed_form(forms: dict) -> bool:
    """Rule 34: a typed value, or a type placeholder, needs the composite holders declared."""
    typed = False
    for letter in forms:
        if forms[letter]["form"] in ("value", "address", "type"):
            typed = True
    return typed


def pair_groups(listings: dict, through_the_label_table: bool) -> list:
    """Rule 41; rule 83: the pairs of a dependent run through the label table (rule 67) in a part of their own,
    the others in the part pairs."""
    groups = []
    for dependent in listings["dependents"]:
        if runs_through_the_label_table(listings["by_text"][dependent]) == through_the_label_table:
            add_pairs_of(groups, dependent, listings)
    merged = merged_when_written_the_same(groups)
    return merged


def runs_through_the_label_table(listing: dict) -> bool:
    """Rule 67's listings, as has_an_indirect_goto finds them: of the kind clang reads `goto *a;` as."""
    through = listing["kind"] == "IndirectGotoStmt"
    return through


def add_pairs_of(groups: list, dependent: str, listings: dict) -> None:
    for holder in listings["holders"]:
        texts = without_repeats([dependent] + NEEDS.get(dependent, []) + [holder])
        group = group_of(f"{dependent} | {holder}", "pair", texts, listings, "numbered")
        group["dependent"] = dependent
        group["holders"] = [holder]
        groups.append(group)


def without_repeats(texts: list) -> list:
    kept = []
    for text in texts:
        if text not in kept:
            kept.append(text)
    return kept


def merged_when_written_the_same(groups: list) -> list:
    """Rule 41: groups whose components are written the same are arranged once, counted for each."""
    merged = []
    by_signature = {}
    for group in groups:
        signature = signature_of(group)
        if signature in by_signature:
            add_as_also_for(by_signature[signature], group)
        else:
            by_signature[signature] = group
            merged.append(group)
    return merged


def signature_of(group: dict) -> str:
    parts = [group["constants"]]
    for component in group["components"]:
        parts.append(json.dumps([component["written"], component["holds_a_body"], component["ends_with"],
                                 component["forms"], component["of_a_statement"], component["copy"]],
                                sort_keys=True))
    signature = "\n".join(parts)
    return signature


def add_as_also_for(kept: dict, group: dict) -> None:
    entry = {}
    entry["group"] = group["group"]
    entry["listings"] = group["listings"]
    entry["holders"] = group.get("holders", [])
    kept["also_for"].append(entry)


def the_pairs_record() -> dict:
    """The record of the part pairs (rules 42 and 43)."""
    path = PART_FILE.format("pairs")
    if not os.path.exists(path):
        stop("arrange: the pairs' record is not there; run the part pairs first; nothing is run")
    record = read_json_gz(path)
    return record


def depended_holders(pairs: dict, listings: dict) -> dict:
    """Rules 42 and 43: each dependent's holders, those every kept pair has it inside."""
    depended = {}
    for group in pairs["groups"]:
        add_depended_holders(depended, group, listings)
    return depended


def add_depended_holders(depended: dict, group: dict, listings: dict) -> None:
    dependent = group["dependent"]
    if dependent not in depended:
        depended[dependent] = []
    for holder in holders_of_a_pair(group):
        if group["kept"] > 0 and stands_only_inside(group, dependent, holder, listings):
            depended[dependent].append(holder)


def holders_of_a_pair(group: dict) -> list:
    holders = list(group["holders"])
    for entry in group["also_for"]:
        add_all(holders, entry["holders"])
    return holders


def stands_only_inside(group: dict, dependent: str, holder: str, listings: dict) -> bool:
    """The dependent's first component stands inside one of the holder's components in every kept pair."""
    first = listings["by_text"][dependent]["components"][0]["component"]
    holders_names = names_of(listings["by_text"][holder]["components"])
    inside = False
    for entry in group["where_each_stands"]:
        if entry["component"] == first and shares_one(entry["only_inside"], holders_names):
            inside = True
    return inside


def groups_of_two_of_the_same(listings: dict) -> list:
    """Rule 42."""
    depended = depended_holders(the_pairs_record(), listings)
    in_one = dependents_in_one_holder(depended)
    groups = two_at_a_time(in_one, listings)
    return groups


def dependents_in_one_holder(depended: dict) -> list:
    in_one = []
    for dependent in depended:
        if len(depended[dependent]) == 1:
            in_one.append((dependent, depended[dependent][0]))
    return in_one


def two_at_a_time(in_one: list, listings: dict) -> list:
    groups = []
    for first in range(len(in_one)):
        for second in range(first, len(in_one)):
            add_two_of_the_same(groups, in_one[first], in_one[second], listings)
    return groups


def add_two_of_the_same(groups: list, first: tuple, second: tuple, listings: dict) -> None:
    if first[1] == second[1]:
        texts = [first[0], second[0], first[1]]
        name = f"{first[0]} + {second[0]} | {first[1]}"
        groups.append(two_of_the_same_group(name, texts, listings, "numbered"))
        if takes_constants(first[0], listings) and takes_constants(second[0], listings):
            groups.append(two_of_the_same_group(name + " | the same value", texts, listings, "the same value"))


def two_of_the_same_group(name: str, texts: list, listings: dict, constants: str) -> dict:
    group = group_of(name, "two of the same", texts, listings, constants)
    group["dependent"] = texts[0]
    group["holders"] = [texts[2]]
    return group


def takes_constants(text: str, listings: dict) -> bool:
    constants = listings["by_text"][text]["fill"] == "constant"
    return constants


def triple_groups(listings: dict, part: str) -> list:
    """Rule 43."""
    depended = depended_holders(the_pairs_record(), listings)
    every = every_triple(depended, listings)
    merged = merged_when_written_the_same(every)
    groups = the_slice(merged, part)
    return groups


def every_triple(depended: dict, listings: dict) -> list:
    groups = []
    for dependent in depended:
        add_triples_of(groups, dependent, depended[dependent], listings)
    return groups


def add_triples_of(groups: list, dependent: str, holders: list, listings: dict) -> None:
    for between in listings["holders"]:
        for holder in holders:
            texts = [dependent] + NEEDS.get(dependent, []) + [between, holder]
            group = group_of(f"{dependent} | {between} | {holder}", "triple", texts, listings, "numbered")
            group["dependent"] = dependent
            group["holders"] = [between, holder]
            groups.append(group)


def the_slice(groups: list, part: str) -> list:
    """Rule 36: `triples:k/n`, the k-th of n slices, the groups dealt in turn; `triples:j-k/n`, the j-th to
    the k-th; rule 83: `label_table_pairs` the same way."""
    sliced = groups
    if ":" in part:
        first, last, count = slice_of(part)
        sliced = []
        for index in range(len(groups)):
            if first - 1 <= index % count <= last - 1:
                sliced.append(groups[index])
    return sliced


def slice_of(part: str) -> tuple:
    written = part.split(":")[1]
    which = written.split("/")[0]
    count = int(written.split("/")[1])
    first = int(which.split("-")[0])
    last = int(which.split("-")[-1])
    the_slice_numbers = (first, last, count)
    return the_slice_numbers


# Rules 10 to 12, 37 and 38: the search


def searched_groups(groups: list, lowerer: dict, part: str) -> dict:
    """Rule 36: a listing alone is one arrangement; the other groups are searched trimmed or untrimmed, as the part
    says (rule 74: the small run has both)."""
    name = part_name(part)
    others = groups_alone(groups, False)
    searched = one_arrangement_each(groups_alone(groups, True))
    if len(others) > 0 and name in TRIMMED_PARTS:
        add_the_search(searched, trimmed_search(others, lowerer))
    elif len(others) > 0:
        add_the_search(searched, untrimmed_search(others))
    return searched


def groups_alone(groups: list, alone: bool) -> list:
    chosen = []
    for group in groups:
        if (group["family"] == "alone") == alone:
            chosen.append(group)
    return chosen


def add_the_search(searched: dict, more: dict) -> None:
    for name in more["leaves"]:
        searched["leaves"][name] = more["leaves"][name]
        searched["tallies"][name] = more["tallies"][name]
    if "seconds" in more:
        searched["seconds"] = more["seconds"]


def new_searched() -> dict:
    searched = {}
    searched["leaves"] = {}
    searched["tallies"] = {}
    return searched


def one_arrangement_each(groups: list) -> dict:
    searched = new_searched()
    for group in groups:
        searched["leaves"][group["group"]] = [((), ())]
        searched["tallies"][group["group"]] = {"trimmed": False, "whole_arrangements": 1}
    return searched


def untrimmed_search(groups: list) -> dict:
    """Rules 10 to 12: every arrangement of each group."""
    searched = new_searched()
    for group in groups:
        started = time.time()
        leaves = every_arrangement_of(group)
        searched["leaves"][group["group"]] = leaves
        searched["tallies"][group["group"]] = untrimmed_tally(leaves, started)
    return searched


def every_arrangement_of(group: dict) -> list:
    prefixes = [((), ())]
    for _line in range(group["lines"]):
        prefixes = one_line_longer(prefixes, group)
    prefixes.sort()
    return prefixes


def untrimmed_tally(leaves: list, started: float) -> dict:
    tally = {}
    tally["trimmed"] = False
    tally["whole_arrangements"] = len(leaves)
    tally["seconds_making_them"] = round(time.time() - started, 1)
    return tally


def one_line_longer(prefixes: list, group: dict) -> list:
    longer = []
    for prefix in prefixes:
        add_one_line_longer(longer, prefix, group)
    return longer


def add_one_line_longer(longer: list, prefix: tuple, group: dict) -> None:
    """Rules 10 to 12 and 37: an inert call first, then each type with a copy left; the lowest level first."""
    tokens = prefix[0]
    levels = prefix[1]
    for token in next_tokens(tokens, group):
        for level in next_levels(tokens, levels, group):
            longer.append((tokens + (token,), levels + (level,)))


def next_tokens(tokens: tuple, group: dict) -> list:
    following = []
    if tokens.count(-1) < group["inert_calls"]:
        following.append(-1)
    for token in range(len(group["copies"])):
        if tokens.count(token) < group["copies"][token]:
            following.append(token)
    return following


def next_levels(tokens: tuple, levels: tuple, group: dict) -> range:
    deepest = 0
    if len(tokens) > 0:
        deepest = levels[-1]
    if len(tokens) > 0 and token_holds_a_body(tokens[-1], group):
        deepest = deepest + 1
    allowed = range(deepest + 1)
    return allowed


def token_holds_a_body(token: int, group: dict) -> bool:
    holds = False
    if token >= 0:
        holds = group["type_copies"][token][0]["holds_a_body"]
    return holds


def trimmed_search(groups: list, lowerer: dict) -> dict:
    """Rule 38: all groups of the part together, depth by depth."""
    state = new_trimmed_state(groups)
    every_depth_trimmed(state, groups, lowerer)
    searched = searched_of_the_state(state, groups)
    return searched


def new_trimmed_state(groups: list) -> dict:
    state = {}
    state["prefixes"] = {}
    state["leaves"] = {}
    state["tallies"] = {}
    state["started"] = time.time()
    for group in groups:
        state["prefixes"][group["group"]] = [((), ())]
        state["leaves"][group["group"]] = []
        state["tallies"][group["group"]] = new_trim_tally()
    return state


def new_trim_tally() -> dict:
    tally = {}
    tally["trimmed"] = True
    tally["prefixes_made"] = 0
    tally["prefixes_asked"] = 0
    tally["refused_closed_off"] = 0
    tally["refused_on_their_own_lines"] = 0
    tally["asked_with_the_rest"] = 0
    tally["prefixes_trimmed"] = 0
    tally["kept_going_for_the_sort"] = 0
    tally["whole_arrangements"] = 0
    return tally


def every_depth_trimmed(state: dict, groups: list, lowerer: dict) -> None:
    by_name = groups_by_name(groups)
    for depth in range(1, most_lines(groups) + 1):
        one_depth_trimmed(state, by_name, lowerer, depth)
        progress(f"depth {depth} of {most_lines(groups)}: {count_prefixes(state)} prefixes go on, "
                 f"{count_leaves(state)} whole arrangements, {round(time.time() - state['started'])} s")


def groups_by_name(groups: list) -> dict:
    by_name = {}
    for group in groups:
        by_name[group["group"]] = group
    return by_name


def most_lines(groups: list) -> int:
    most = 0
    for group in groups:
        most = max(most, group["lines"])
    return most


def one_depth_trimmed(state: dict, by_name: dict, lowerer: dict, depth: int) -> None:
    extended = extended_by_one_line(state, by_name)
    move_the_whole_ones(state, extended, by_name)
    asked = prefixes_to_ask(extended, by_name)
    closed = answers_closed_off(asked, by_name, lowerer)
    on_own_lines = refused_on_their_own_lines(asked, closed)
    with_the_rest = answers_with_the_rest(on_own_lines, by_name, lowerer)
    trimmed = trimmed_of(on_own_lines, with_the_rest)
    keep_what_is_not_trimmed(state, extended, trimmed, by_name)
    tally_the_depth(state, extended, asked, closed, on_own_lines, trimmed)
    tally_what_the_sort_kept_going(state, held_back_by_the_sort(on_own_lines, with_the_rest))


def extended_by_one_line(state: dict, by_name: dict) -> dict:
    extended = {}
    for name in state["prefixes"]:
        extended[name] = one_line_longer(state["prefixes"][name], by_name[name])
    return extended


def move_the_whole_ones(state: dict, extended: dict, by_name: dict) -> None:
    for name in extended:
        for prefix in extended[name]:
            if len(prefix[0]) == by_name[name]["lines"]:
                state["leaves"][name].append(prefix)


def prefixes_to_ask(extended: dict, by_name: dict) -> list:
    """Rule 38: a prefix whose last line is a component, short of a whole arrangement."""
    asked = []
    for name in extended:
        for prefix in extended[name]:
            if prefix[0][-1] >= 0 and len(prefix[0]) < by_name[name]["lines"]:
                asked.append((name, prefix))
    return asked


def answers_closed_off(asked: list, by_name: dict, lowerer: dict) -> list:
    """Rule 38a: each prefix closed off; its answer, with the line of its last line."""
    texts = []
    last_lines = []
    for name, prefix in asked:
        written = program_of_prefix(by_name[name], prefix[0], prefix[1], None)
        texts.append(written["text"])
        last_lines.append(written["last_line"])
    answers = answers_of_programs(texts, lowerer)
    for index in range(len(answers)):
        answers[index]["last_line"] = last_lines[index]
    return answers


def refused_on_their_own_lines(asked: list, closed: list) -> list:
    """Rule 38a: refused, the first error on one of the prefix's own lines."""
    refused = []
    for index in range(len(asked)):
        if is_refused_on_its_own_lines(closed[index]):
            refused.append((asked[index][0], asked[index][1], closed[index]))
    return refused


def is_refused_on_its_own_lines(answer: dict) -> bool:
    on_own_lines = False
    if not answer["accepted"] and answer["line"] is not None:
        on_own_lines = answer["line"] <= answer["last_line"]
    return on_own_lines


def answers_with_the_rest(refused: list, by_name: dict, lowerer: dict) -> list:
    """Rule 38b: each refused prefix with the group's remaining components at the outermost level."""
    texts = []
    for name, prefix, _answer in refused:
        written = program_of_prefix(by_name[name], prefix[0], prefix[1], 0)
        texts.append(written["text"])
    answers = answers_of_programs(texts, lowerer)
    return answers


def trimmed_of(refused: list, with_the_rest: list) -> set:
    """Rule 38b: still refused, with the same first error at the same line; rule 72: an error sorted where it
    stands."""
    trimmed = set()
    for index in range(len(refused)):
        closed = refused[index][2]
        if refused_the_same(closed, with_the_rest[index]) and sort_of(closed["message"]) == WHERE_IT_STANDS:
            trimmed.add((refused[index][0], refused[index][1]))
    return trimmed


def refused_the_same(closed: dict, rest: dict) -> bool:
    same = not rest["accepted"] and rest["line"] == closed["line"] and rest["message"] == closed["message"]
    return same


def held_back_by_the_sort(refused: list, with_the_rest: list) -> list:
    """Rule 72: the prefixes rule 38's a and b would trim, kept going because their error is not sorted where it
    stands."""
    held_back = []
    for index in range(len(refused)):
        closed = refused[index][2]
        if refused_the_same(closed, with_the_rest[index]) and sort_of(closed["message"]) != WHERE_IT_STANDS:
            held_back.append(refused[index][0])
    return held_back


def tally_what_the_sort_kept_going(state: dict, held_back: list) -> None:
    for name in held_back:
        state["tallies"][name]["kept_going_for_the_sort"] += 1


def keep_what_is_not_trimmed(state: dict, extended: dict, trimmed: set, by_name: dict) -> None:
    for name in extended:
        state["prefixes"][name] = prefixes_going_on(name, extended[name], trimmed, by_name[name]["lines"])


def prefixes_going_on(name: str, prefixes: list, trimmed: set, lines: int) -> list:
    going_on = []
    for prefix in prefixes:
        if len(prefix[0]) < lines and (name, prefix) not in trimmed:
            going_on.append(prefix)
    return going_on


def tally_the_depth(state: dict, extended: dict, asked: list, closed: list, on_own_lines: list,
                    trimmed: set) -> None:
    for name in extended:
        state["tallies"][name]["prefixes_made"] += len(extended[name])
    for index in range(len(asked)):
        tally = state["tallies"][asked[index][0]]
        tally["prefixes_asked"] += 1
        if not closed[index]["accepted"]:
            tally["refused_closed_off"] += 1
    for entry in on_own_lines:
        state["tallies"][entry[0]]["refused_on_their_own_lines"] += 1
        state["tallies"][entry[0]]["asked_with_the_rest"] += 1
    for name, _prefix in trimmed:
        state["tallies"][name]["prefixes_trimmed"] += 1


def count_prefixes(state: dict) -> int:
    count = 0
    for name in state["prefixes"]:
        count += len(state["prefixes"][name])
    return count


def count_leaves(state: dict) -> int:
    count = 0
    for name in state["leaves"]:
        count += len(state["leaves"][name])
    return count


def searched_of_the_state(state: dict, groups: list) -> dict:
    searched = new_searched()
    for group in groups:
        name = group["group"]
        leaves = sorted(state["leaves"][name])
        searched["leaves"][name] = leaves
        state["tallies"][name]["whole_arrangements"] = len(leaves)
        searched["tallies"][name] = state["tallies"][name]
    searched["seconds"] = round(time.time() - state["started"], 1)
    return searched


def arrangements_record(listings: dict, groups: list, searched: dict, part: str) -> dict:
    record = {}
    record["part"] = part
    record["listings"] = listings
    record["groups"] = groups
    record["arrangements"] = numbered_arrangements(groups, searched, listings)
    record["search"] = searched["tallies"]
    record["search_seconds"] = searched.get("seconds")
    return record


def numbered_arrangements(groups: list, searched: dict, listings: dict) -> list:
    arrangements = []
    for group in groups:
        add_numbered(arrangements, group, searched["leaves"][group["group"]], listings)
    return arrangements


def add_numbered(arrangements: list, group: dict, leaves: list, listings: dict) -> None:
    for number in range(1, len(leaves) + 1):
        arrangements.append(arrangement_entry(group, number, leaves[number - 1], listings))


def arrangement_entry(group: dict, number: int, leaf: tuple, listings: dict) -> dict:
    arrangement = {}
    arrangement["group"] = group["group"]
    arrangement["number"] = number
    arrangement["tokens"] = leaf[0]
    arrangement["levels"] = list(leaf[1])
    arrangement["alone"] = group["family"] == "alone"
    arrangement["lines"] = []
    if not arrangement["alone"]:
        arrangement["lines"] = lines_of(group, leaf[0])
    arrangement["in_dees_order"] = False
    arrangement["dees_example"] = None
    if group["family"] == "step 1" and group["group"] == "if":
        mark_dees_order(arrangement)
    return arrangement


def mark_dees_order(arrangement: dict) -> None:
    """Rule 13."""
    if line_names(arrangement["lines"]) == DEES_ORDER:
        arrangement["in_dees_order"] = True
        arrangement["dees_example"] = dees_example_of(arrangement["levels"])


def dees_example_of(levels: list):
    found = None
    for example in DEES_EXAMPLES:
        if example["levels"] == levels:
            found = example
            break
    return found


def check_the_counts(arrangements: dict, part: str) -> None:
    """Rule 14 for step_1_again; rule 36's 166,320 for switch_untrimmed. Any other count stops the run."""
    name = part_name(part)
    counts = counts_by_group(arrangements)
    if name == "step_1_again" and counts != EXPECTED_ARRANGEMENTS:
        stop(f"arrange: the counts are {counts}, not {EXPECTED_ARRANGEMENTS}; nothing is run")
    if name == "step_1_again" and count_in_dees_order(arrangements["arrangements"]) != EXPECTED_IN_DEES_ORDER:
        stop(f"arrange: not {EXPECTED_IN_DEES_ORDER} arrangements in the owner's order; nothing is run")
    if name == "step_1_again" and count_dees_examples(arrangements["arrangements"]) != len(DEES_EXAMPLES):
        stop(f"arrange: not the owner's {len(DEES_EXAMPLES)} examples; nothing is run")
    if name == "switch_untrimmed" and counts.get("switch") != EXPECTED_SWITCH_ARRANGEMENTS:
        stop(f"arrange: the switch group has {counts.get('switch')} arrangements, not "
             f"{EXPECTED_SWITCH_ARRANGEMENTS}; nothing is run")


def counts_by_group(arrangements: dict) -> dict:
    counts = {}
    for arrangement in arrangements["arrangements"]:
        counts[arrangement["group"]] = counts.get(arrangement["group"], 0) + 1
    return counts


def count_in_dees_order(arrangements: list) -> int:
    count = 0
    for arrangement in arrangements:
        if arrangement["in_dees_order"]:
            count += 1
    return count


def count_dees_examples(arrangements: list) -> int:
    count = 0
    for arrangement in arrangements:
        if arrangement["dees_example"] is not None:
            count += 1
    return count


# 3. write_programs


def write_programs(arrangements: dict, lowerer: dict) -> dict:
    """Each arrangement written as a program in the lowerer's language (rules 15 to 19, 44 and 45)."""
    check_the_language(lowerer)
    programs = dict(arrangements)
    add_the_programs(programs["arrangements"], arrangements)
    return programs


def check_the_language(lowerer: dict) -> None:
    if lowerer["language"] != GNU_C:
        stop(f"write_programs: only {GNU_C} is written, not {lowerer['language']}; nothing is run")


def add_the_programs(arrangement_list: list, arrangements: dict) -> None:
    """Each program's text, kept whole only in the part step_1_again, where it is checked against step 1's."""
    by_name = groups_by_name(arrangements["groups"])
    listings = arrangements["listings"]
    whole = part_name(arrangements["part"]) == "step_1_again"
    for arrangement in arrangement_list:
        written = program_of_an_arrangement(arrangement, by_name, listings)
        if whole:
            arrangement["program_text"] = written["text"]
        arrangement["header"] = written["header"]
        arrangement["function"] = written["function"]
        arrangement["forms_by_number"] = written["forms_by_number"]
        arrangement["numbers"] = written["numbers"]
        arrangement["number_count"] = written["number_count"]
        arrangement["own_slots"] = written.get("own_slots", [])
        arrangement["context"] = written["context"]


def program_of_an_arrangement(arrangement: dict, by_name: dict, listings: dict) -> dict:
    if arrangement["alone"]:
        listing = listings["by_text"][arrangement["group"]]
        written = program_alone(listing, listings, listing["fill"], True, None, None, listing["fill_overrides"],
                                listing["context"])
    else:
        group = by_name[arrangement["group"]]
        written = program_of_prefix(group, arrangement["tokens"], tuple(arrangement["levels"]), None)
    return written


def program_text_of(arrangement: dict) -> str:
    text = arrangement["header"] + "\n" + arrangement["function"] + "\n"
    return text


def program_of_prefix(group: dict, tokens: tuple, levels: tuple, rest_level) -> dict:
    """A prefix, or a whole arrangement, as a program; with the group's remaining
    components at `rest_level` when it is not None (rules 16 to 18, 38 and 44)."""
    lines = lines_of(group, tokens)
    all_levels = list(levels)
    if rest_level is not None:
        add_the_rest(lines, all_levels, group, tokens, rest_level)
    written = written_program(group, lines, all_levels, len(tokens))
    return written


def lines_of(group: dict, tokens: tuple) -> list:
    """Rule 37: the k-th line of a type is its k-th copy."""
    lines = []
    seen = {}
    for token in tokens:
        if token < 0:
            lines.append(INERT_CALL)
        else:
            copy = seen.get(token, 0)
            lines.append(group["type_copies"][token][copy])
            seen[token] = copy + 1
    return lines


def add_the_rest(lines: list, levels: list, group: dict, tokens: tuple, rest_level: int) -> None:
    """Rule 38b: the group's remaining components, in its order, each holding nothing."""
    for token in range(len(group["type_copies"])):
        used = tokens.count(token)
        for copy in range(used, group["copies"][token]):
            lines.append(group["type_copies"][token][copy])
            levels.append(rest_level)


def written_program(group: dict, lines: list, levels: list, own_count: int) -> dict:
    """Rule 18: the declarations, then `void f(void) {`, the lines, then `}`; rule 64: a context's lines before the
    function, its header and what it declares; rule 67: the label table and its two targets."""
    numbers = numbers_of_the_lines(lines, group["inert_calls"])
    constants = constants_of_the_lines(lines, group["constants"])
    count = number_count_of(group)
    header = header_of(group, lines, numbers, count)
    function = function_of(lines, levels, numbers, constants, frame_of(group))
    written = {}
    written["header"] = "\n".join(header["lines"])
    written["function"] = "\n".join(function["lines"])
    written["text"] = written["header"] + "\n" + written["function"] + "\n"
    written["last_line"] = len(header["lines"]) + function["line_of"][own_count - 1]
    written["forms_by_number"] = header["forms"]
    written["numbers"] = numbers
    written["number_count"] = count
    written["context"] = group.get("context", TODAYS_CONTEXT)
    return written


def number_count_of(group: dict) -> int:
    """Rule 16's numbers; rule 67: and the label table's two inert calls, after every other."""
    count = group["inert_calls"] + group["values"]
    if group.get("label_table", False):
        count = count + 2
    return count


def frame_of(group: dict) -> dict:
    """Rules 18, 64 and 67: the function's first line, what it declares first, and the label table."""
    context = context_named(group.get("context", TODAYS_CONTEXT))
    count = number_count_of(group)
    frame = {}
    frame["start"] = context["header"]
    frame["declares"] = context["declares"]
    frame["label_table"] = group.get("label_table", False)
    frame["targets"] = [count - 2, count - 1]
    return frame


def preludes_of(group: dict) -> list:
    """Rules 64 and 70: the context's lines before the function, then those of the declarations the group holds."""
    lines = list(context_named(group.get("context", TODAYS_CONTEXT))["prelude"])
    for line in group.get("prelude", []):
        add_new(lines, line)
    return lines


def numbers_of_the_lines(lines: list, inert_calls: int) -> list:
    """Rule 16: inert call lines first, in line order; then each slot, from the group's count of inert call lines."""
    numbers = empty_lists(len(lines))
    next_number = 0
    for index in range(len(lines)):
        if is_inert_call(lines[index]):
            numbers[index].append(next_number)
            next_number += 1
    next_number = inert_calls
    for index in range(len(lines)):
        for _slot in slots_of_a_line(lines[index]):
            numbers[index].append(next_number)
            next_number += 1
    return numbers


def empty_lists(count: int) -> list:
    lists = []
    for _count in range(count):
        lists.append([])
    return lists


def slots_of_a_line(line: dict) -> list:
    slots = []
    if is_own_text(line):
        slots = line["slots"]
    elif not is_inert_call(line):
        slots = inert_values_of(line)
    return slots


def constants_of_the_lines(lines: list, constants: str) -> list:
    """Rule 35: the k-th line, in line order, that takes constants, writes k; 0 in "the same value"."""
    written = []
    count = 0
    for line in lines:
        if takes_a_constant(line) and constants == "the same value":
            written.append(0)
        elif takes_a_constant(line):
            written.append(count)
            count += 1
        else:
            written.append(None)
    return written


def takes_a_constant(line: dict) -> bool:
    constant = False
    if not is_inert_call(line):
        constant = has_a_constant_form(line["forms"])
    return constant


def has_a_constant_form(forms: dict) -> bool:
    constant = False
    for letter in forms:
        if forms[letter]["form"] == "constant":
            constant = True
    return constant


def header_of(group: dict, lines: list, numbers: list, count: int) -> dict:
    """Rules 34 and 44: the composite holders when typed, then a declaration for every number the group uses;
    rules 64 and 70: the lines a context or a declaration needs before the function, first."""
    forms = forms_by_number_of(lines, numbers)
    header = {}
    header["lines"] = []
    add_all(header["lines"], preludes_of(group))
    if group["typed"]:
        add_all(header["lines"], group["held_types"])
    add_all(header["lines"], group.get("library", []))
    for number in range(count):
        header["lines"].append(declaration_of(number, forms.get(number)))
    header["forms"] = forms
    return header


def forms_by_number_of(lines: list, numbers: list) -> dict:
    forms = {}
    for index in range(len(lines)):
        add_forms_of_a_line(forms, lines[index], numbers[index])
    return forms


def add_forms_of_a_line(forms: dict, line: dict, line_numbers: list) -> None:
    slots = slots_of_a_line(line)
    for index in range(len(slots)):
        forms[line_numbers[index]] = form_of_a_slot(line, slots[index])


def form_of_a_slot(line: dict, letter: str) -> dict:
    """A held statement of a listing's own text is an `int` inert call statement (rule 33)."""
    form = {"form": "int", "holder": None}
    if letter in line["forms"]:
        form = line["forms"][letter]
    return form


def declaration_of(number: int, form) -> str:
    declaration = C_DECLARATION.format(number)
    if form is not None and form["form"] == "value":
        declaration = C_VALUE_DECLARATION.format(form["holder"], number)
    if form is not None and form["form"] == "address":
        declaration = C_ADDRESS_DECLARATION.format(form["holder"], number)
    return declaration


def function_of(lines: list, levels: list, numbers: list, constants: list, frame: dict) -> dict:
    """Rules 17 and 18: each line at its level, each held body in { }; the line each stands on; rules 64 and 67:
    the context's header and what it declares, the label table first and its two targets last."""
    text_lines = [frame["start"]]
    add_what_the_frame_declares(text_lines, frame)
    line_of = []
    open_bodies = 0
    for index in range(len(lines)):
        close_bodies(text_lines, open_bodies, levels[index])
        statement = statement_of(lines[index], numbers[index], constants[index])
        opening = body_opening(lines[index], levels, index)
        text_lines.append(indented(with_the_opening(statement, opening), levels[index]))
        line_of.append(len(text_lines))
        open_bodies = bodies_open_after(levels, index)
    close_bodies(text_lines, open_bodies, 0)
    add_the_label_table_targets(text_lines, frame)
    text_lines.append(C_FUNCTION_END)
    function = {}
    function["lines"] = text_lines
    function["line_of"] = line_of
    return function


def add_what_the_frame_declares(text_lines: list, frame: dict) -> None:
    for line in frame["declares"]:
        text_lines.append(indented(line, 0))
    if frame["label_table"]:
        text_lines.append(indented(C_LABEL_TABLE, 0))


def add_the_label_table_targets(text_lines: list, frame: dict) -> None:
    """Rule 67: `goto_target_0:` and `goto_target_1:` at the outermost level, each followed by an inert call."""
    if frame["label_table"]:
        for which in range(2):
            text_lines.append(indented(C_LABEL_TABLE_TARGET.format(which, frame["targets"][which]), 0))


def close_bodies(text_lines: list, open_bodies: int, level: int) -> None:
    """Close each body deeper than `level`; a body's `}` stands at its component's level."""
    for depth in range(open_bodies - 1, level - 1, -1):
        text_lines.append(indented(C_BODY_CLOSES, depth))


def statement_of(line: dict, line_numbers: list, constant) -> str:
    statement = ""
    if is_inert_call(line):
        statement = C_INERT_CALL_LINE.format(line_numbers[0])
    elif is_own_text(line):
        statement = own_text_in_c(line, line_numbers, constant)
    else:
        statement = component_in_c(line, line_numbers, constant) + line["ends_with"] + expression_end(line)
    return statement


def expression_end(line: dict) -> str:
    """Rule 31: a component of an expression listing standing as a line ends with `;`."""
    end = ""
    if not line.get("of_a_statement", True):
        end = ";"
    return end


def component_in_c(component: dict, line_numbers: list, constant) -> str:
    """Rules 17 and 32 to 35: the component as its listing writes it, each value as its fill writes it."""
    written = []
    taken = 0
    for piece in pieces_of(component["written"]):
        text = piece["text"]
        if piece["is"] == "value" and component["forms"][text]["form"] == "constant":
            text = str(constant)
        elif piece["is"] == "value" and component["forms"][text]["form"] == "name":
            text = component["forms"][text]["text"]
        elif piece["is"] == "value":
            text = inert_written(line_numbers[taken], component["forms"][text])
            taken += 1
        elif piece["is"] == "type":
            text = component["forms"][text]["holder"]
        written.append(text)
    in_c = "".join(written)
    return in_c


def inert_written(number: int, form: dict) -> str:
    """An inert call; read through its address (rule 34); an entry of the label table (rule 67)."""
    written = INERT_CALL_WRITTEN.format(number)
    if form["form"] == "address":
        written = C_BY_ADDRESS.format(number)
    if form["form"] == LABEL_TABLE:
        written = C_LABEL_TABLE_ENTRY.format(INERT_CALL_WRITTEN.format(number))
    return written


def with_the_opening(statement: str, opening: str) -> str:
    """A block's component is written as nothing (rule 30): its line is the brace alone."""
    written = statement + opening
    if statement == "":
        written = opening.lstrip()
    return written


def body_opening(line: dict, levels: list, index: int) -> str:
    opening = ""
    if holds_lines(levels, index):
        opening = C_BODY_OPENS
    elif holds_a_body(line):
        opening = C_EMPTY_BODY
    return opening


def bodies_open_after(levels: list, index: int) -> int:
    open_bodies = levels[index]
    if holds_lines(levels, index):
        open_bodies = levels[index] + 1
    return open_bodies


def indented(text: str, level: int) -> str:
    written = C_INDENT * (level + 1) + text
    return written


# Rules 33 and 45: a listing's own text


def program_alone(listing: dict, listings: dict, fill: str, with_needs: bool, body_letter, held_as, overrides=None,
                  context=TODAYS_CONTEXT, label_table=False) -> dict:
    """Rule 33: an inert call, the listing's own text, what it needs, an inert call; rules 64, 66 and 67: in a
    context, with placeholders written as names, constants or the label table."""
    as_body = None
    if held_as == "body":
        as_body = body_letter
    lines = [INERT_CALL, own_line(listing, fill, listings, as_body, overrides)]
    if with_needs:
        add_the_needs(lines, listing, listings)
    lines.append(INERT_CALL)
    levels = zeros(len(lines))
    group = group_of_one_program(lines, listings, context, label_table)
    written = written_program(group, lines, levels, len(lines))
    written["own_slots"] = slots_with_numbers(lines[1]["slots"], written["numbers"][1])
    return written


def slots_with_numbers(slots: list, numbers: list) -> list:
    paired = []
    for index in range(len(slots)):
        paired.append([slots[index], numbers[index]])
    return paired


def program_held_in(listing: dict, holder: dict, listings: dict, fill: str) -> dict:
    """Rule 32: the listing's own text held by the holder's first component that holds a body."""
    lines = [INERT_CALL]
    levels = [0]
    add_the_holder_holding(lines, levels, holder, own_line(listing, fill, listings, None), listings)
    lines.append(INERT_CALL)
    levels.append(0)
    written = written_program(group_of_one_program(lines, listings), lines, levels, len(lines))
    return written


def add_the_holder_holding(lines: list, levels: list, holder: dict, held: dict, listings: dict) -> None:
    holding = False
    for component in holder["components"]:
        lines.append(component_in_a_group(component, holder, 1, listings))
        levels.append(0)
        if component["holds_a_body"] and not holding:
            lines.append(held)
            levels.append(1)
            holding = True


def add_the_needs(lines: list, listing: dict, listings: dict) -> None:
    for need in NEEDS.get(listing["listing"], []):
        needed = listings["by_text"][need]
        lines.append(own_line(needed, needed["fill"], listings, None, needed["fill_overrides"]))


def zeros(count: int) -> list:
    levels = []
    for _count in range(count):
        levels.append(0)
    return levels


def group_of_one_program(lines: list, listings: dict, context=TODAYS_CONTEXT, label_table=False) -> dict:
    group = {}
    group["inert_calls"] = count_inert_call_lines(lines)
    group["values"] = count_slots(lines)
    group["typed"] = lines_use_a_typed_fill(lines)
    group["held_types"] = listings["holder_types"]
    group["constants"] = "numbered"
    group["library"] = library_declarations_of(lines, listings)
    group["context"] = context
    group["label_table"] = label_table
    group["prelude"] = preludes_of_the_lines(lines, listings)
    return group


def preludes_of_the_lines(lines: list, listings: dict) -> list:
    """Rule 70: the lines a declaration needs before the function, for each own text that is one."""
    preludes = []
    for line in lines:
        if is_own_text(line) and line["listing"] in listings["by_text"]:
            add_all(preludes, listings["by_text"][line["listing"]]["prelude"])
    return preludes


def library_declarations_of(lines: list, listings: dict) -> list:
    """Rule 34: the library declarations a listing's own text calls for."""
    declarations = []
    for line in lines:
        if is_own_text(line) and line["kept_as"] in listings["library"]:
            add_new(declarations, listings["library"][line["kept_as"]])
    return declarations


def count_inert_call_lines(lines: list) -> int:
    count = 0
    for line in lines:
        if is_inert_call(line):
            count += 1
    return count


def count_slots(lines: list) -> int:
    count = 0
    for line in lines:
        count += len(slots_of_a_line(line))
    return count


def lines_use_a_typed_fill(lines: list) -> bool:
    typed = False
    for line in lines:
        if not is_inert_call(line) and has_a_typed_form(line["forms"]):
            typed = True
    return typed


def own_line(listing: dict, fill: str, listings: dict, body_letter, overrides=None) -> dict:
    """A listing's own text as one line (rules 33 and 45); rules 64, 66 and 67: placeholders written as names,
    constants or the label table."""
    line = {}
    line["is"] = "own text"
    line["listing"] = listing["listing"]
    line["kept_as"] = listing["kept_as"]
    line["of_a_statement"] = listing["is_statement"]
    line["held"] = held_letters_of(listing)
    line["forms"] = own_forms(listing, fill, line["held"], listings, overrides)
    line["body_letter"] = body_letter
    line["slots"] = own_slots(listing["listing"], line["held"], line["forms"])
    line["holds_a_body"] = False
    return line


def held_letters_of(listing: dict) -> list:
    held = []
    for component in listing["components"]:
        add_all(held, component["holds_all"])
    return held


def own_forms(listing: dict, fill: str, held: list, listings: dict, overrides=None) -> dict:
    forms = {}
    for letter in value_and_type_letters(listing["listing"]):
        if letter not in held:
            forms[letter] = form_of(listing, letter, fill, listings)
    if overrides is not None:
        apply_the_overrides(forms, overrides, ("name", "constant", LABEL_TABLE))
    return forms


def own_slots(text: str, held: list, forms: dict) -> list:
    """Rule 33: each value and held statement that is an inert call, in the order written."""
    slots = []
    for piece in pieces_of(text):
        if piece["is"] == "value" and is_an_inert_slot(piece["text"], held, forms):
            slots.append(piece["text"])
    return slots


def is_an_inert_slot(letter: str, held: list, forms: dict) -> bool:
    inert = letter in held
    if letter in forms and forms[letter]["form"] not in ("constant", "name"):
        inert = True
    return inert


def own_text_in_c(line: dict, line_numbers: list, constant) -> str:
    """Rule 33: the listing's own text, each slot filled; a held statement as `inert_k()`,
    or as `{ inert_k(); }` with its `;` when rule 29 asks for it as a body."""
    pieces = pieces_of(line["listing"])
    skipped = None
    if line["body_letter"] in line["held"]:
        skipped = semicolon_after_the_body(pieces, line["body_letter"])
    written = []
    slot = 0
    for index in range(len(pieces)):
        text = pieces[index]["text"]
        what = pieces[index]["is"]
        if index == skipped:
            text = ""
        elif what == "value" and text in line["held"]:
            text = held_call_written(line_numbers[slot], text == line["body_letter"])
            slot += 1
        elif what == "value" and line["forms"][text]["form"] == "constant":
            text = str(constant)
        elif what == "value" and line["forms"][text]["form"] == "name":
            text = line["forms"][text]["text"]
        elif what == "value":
            text = inert_written(line_numbers[slot], line["forms"][text])
            slot += 1
        elif what == "type":
            text = line["forms"][text]["holder"]
        written.append(text)
    in_c = "".join(written) + expression_end(line)
    return in_c


def semicolon_after_the_body(pieces: list, body_letter):
    skipped = None
    for index in range(len(pieces)):
        if pieces[index]["text"] == body_letter and pieces[index]["is"] == "value":
            skipped = next_piece_past_spaces(pieces, index)
    return skipped


def held_call_written(number: int, as_a_body: bool) -> str:
    written = INERT_CALL_WRITTEN.format(number)
    if as_a_body:
        written = C_HELD_BODY.format(written)
    return written


# 4. ask_the_lowerer


def ask_the_lowerer(programs: dict, lowerer: dict) -> dict:
    """Signal 1 (rules 20, 21 and 46). Block A names what it hands back
    `accepted`: every program with the lowerer's answer; the kept ones are
    those accepted."""
    texts = program_texts(programs["arrangements"])
    answers = answers_of_programs(texts, lowerer)
    accepted = dict(programs)
    add_the_answers(accepted["arrangements"], answers)
    accepted["asks"] = dict(lowerer["asks"])
    return accepted


def program_texts(arrangements: list) -> list:
    texts = []
    for arrangement in arrangements:
        texts.append(program_text_of(arrangement))
    return texts


def add_the_answers(arrangements: list, answers: list) -> None:
    """A refused arrangement of a group keeps no program text (rule 59)."""
    for index in range(len(arrangements)):
        arrangements[index]["accepted"] = answers[index]["accepted"]
        arrangements[index]["first_error_line"] = answers[index]["line"]
        arrangements[index]["first_error"] = answers[index]["message"]
        if not answers[index]["accepted"] and not arrangements[index]["alone"]:
            arrangements[index]["header"] = None
            arrangements[index]["function"] = None


def answers_of_listing_programs(questions: list, lowerer: dict) -> list:
    texts = []
    for question in questions:
        texts.append(question["program"])
    answers = answers_of_programs(texts, lowerer)
    return answers


def answers_of_programs(texts: list, lowerer: dict) -> list:
    """Rule 46: the programs in batches, 8 calls at once; the answers in the programs' order."""
    started = time.time()
    tasks = batches_of(texts, lowerer)
    answers = answers_from_the_pool(tasks, len(texts), lowerer["pool"])
    tally_the_asks(lowerer["asks"], tasks, answers, started)
    stop_on_a_different_answer(answers, texts)
    return answers


def batches_of(texts: list, lowerer: dict) -> list:
    tasks = []
    for first in range(0, len(texts), PROGRAMS_PER_CALL):
        tasks.append(batch_task(texts, first, lowerer))
    return tasks


def batch_task(texts: list, first: int, lowerer: dict) -> dict:
    task = {}
    task["first"] = first
    task["texts"] = texts[first:first + PROGRAMS_PER_CALL]
    task["front_end"] = lowerer["front_end"]
    task["command"] = lowerer["command"]
    task["folder"] = lowerer["work_folder"]
    task["alone_every"] = lowerer["alone_every"]
    task["serial"] = lowerer["asks"]["programs"] + first
    return task


def answers_from_the_pool(tasks: list, count: int, pool) -> list:
    answers = nones(count)
    if len(tasks) > 0:
        place_the_answers(answers, tasks, pool)
    return answers


def nones(count: int) -> list:
    items = []
    for _count in range(count):
        items.append(None)
    return items


def place_the_answers(answers: list, tasks: list, pool) -> None:
    for batch in pool.imap_unordered(answers_of_a_batch, tasks):
        place_a_batch(answers, batch)


def place_a_batch(answers: list, batch: list) -> None:
    for answer in batch:
        answers[answer["index"]] = answer


def answers_of_a_batch(task: dict) -> list:
    """One call of clang's front end on a batch, each program its own
    translation unit; the sampled ones also asked alone (rule 46)."""
    folder = folder_of_this_worker(task["folder"], "ask")
    names = write_the_batch(folder, task)
    finished = front_end_on(task, names, folder)
    answers = answers_of_the_call(finished, task, names, folder)
    add_answers_alone(answers, task, names, folder)
    remove_files(folder, names)
    return answers


def folder_of_this_worker(work_folder: str, what: str) -> str:
    folder = os.path.join(work_folder, f"{what}_{os.getpid()}")
    os.makedirs(folder, exist_ok=True)
    return folder


def write_the_batch(folder: str, task: dict) -> list:
    names = []
    for index in range(len(task["texts"])):
        name = f"p_{task['first'] + index}.c"
        write_text(os.path.join(folder, name), task["texts"][index])
        names.append(name)
    return names


def front_end_on(task: dict, names: list, folder: str):
    finished = None
    try:
        finished = subprocess.run(task["front_end"] + names, cwd=folder, capture_output=True, text=True,
                                  timeout=CALL_SECONDS)
    except subprocess.TimeoutExpired:
        finished = None
    return finished


def answers_of_the_call(finished, task: dict, names: list, folder: str) -> list:
    if call_did_not_finish(finished):
        answers = answers_one_at_a_time(task, names, folder)
    else:
        answers = answers_from_the_output(finished.stderr, task, names)
    return answers


def call_did_not_finish(finished) -> bool:
    """Rule 46: a crash, a timeout, an exit code clang does not give for errors, or a failed call that
    names no program's file."""
    unfinished = finished is None
    if finished is not None and finished.returncode not in (0, 1):
        unfinished = True
    if finished is not None and has_a_crash_mark(finished.stderr):
        unfinished = True
    if finished is not None and finished.returncode == 1 and len(first_errors_by_file(finished.stderr)) == 0:
        unfinished = True
    return unfinished


def has_a_crash_mark(output: str) -> bool:
    found = False
    for mark in CRASH_MARKS:
        if mark in output:
            found = True
    return found


def answers_from_the_output(output: str, task: dict, names: list) -> list:
    errors = first_errors_by_file(output)
    answers = []
    for index in range(len(names)):
        answers.append(answer_entry(task["first"] + index, errors.get(names[index])))
    return answers


def first_errors_by_file(output: str) -> dict:
    errors = {}
    for line in output.splitlines():
        found = DIAGNOSTIC.match(line)
        if found is not None and found.group("file") not in errors:
            errors[found.group("file")] = found
    return errors


def answer_entry(index: int, found) -> dict:
    answer = {}
    answer["index"] = index
    answer["accepted"] = found is None
    answer["line"] = None
    answer["message"] = None
    answer["alone"] = None
    answer["asked_again_alone"] = False
    if found is not None:
        answer["line"] = int(found.group("line"))
        answer["message"] = found.group("message")
    return answer


def answers_one_at_a_time(task: dict, names: list, folder: str) -> list:
    answers = []
    for index in range(len(names)):
        answer = answer_alone(task, names[index], folder, task["first"] + index)
        answer["asked_again_alone"] = True
        answers.append(answer)
    return answers


def answer_alone(task: dict, name: str, folder: str, index: int) -> dict:
    """Rule 20: one program, the driver's command, alone."""
    finished = subprocess.run(task["command"] + [name], cwd=folder, capture_output=True, text=True,
                              timeout=CALL_SECONDS)
    errors = first_errors_by_file(finished.stderr)
    answer = answer_entry(index, errors.get(name))
    answer["accepted"] = finished.returncode == 0
    return answer


def add_answers_alone(answers: list, task: dict, names: list, folder: str) -> None:
    for index in range(len(names)):
        if (task["serial"] + index) % task["alone_every"] == 0:
            alone = answer_alone(task, names[index], folder, task["first"] + index)
            answers[index]["alone"] = alone_compared(answers[index], alone)


def alone_compared(answer: dict, alone: dict) -> str:
    compared = "same"
    if answer["accepted"] != alone["accepted"] or answer["line"] != alone["line"] or \
            answer["message"] != alone["message"]:
        compared = f"differs: alone {answer_described(alone)}; in the batch {answer_described(answer)}"
    return compared


def remove_files(folder: str, names: list) -> None:
    for name in names:
        os.remove(os.path.join(folder, name))


def tally_the_asks(tally: dict, tasks: list, answers: list, started: float) -> None:
    tally["programs"] += len(answers)
    tally["calls"] += len(tasks)
    tally["seconds"] += time.time() - started
    for answer in answers:
        tally_one_answer(tally, answer)


def tally_one_answer(tally: dict, answer: dict) -> None:
    if answer["alone"] is not None:
        tally["asked_alone"] += 1
    if answer["alone"] is not None and answer["alone"] != "same":
        tally["alone_differs"] += 1
    if answer["asked_again_alone"]:
        tally["calls_asked_again_alone"] += 1


def stop_on_a_different_answer(answers: list, texts: list) -> None:
    """Rule 46: a program the batch and the driver alone answer differently stops the run."""
    for index in range(len(answers)):
        if answers[index]["alone"] is not None and answers[index]["alone"] != "same":
            stop(f"ask_the_lowerer: {answers[index]['alone']}; the program:\n{texts[index]}")


# 5. run_with_chosen_returns


def run_with_chosen_returns(accepted: dict, lowerer: dict) -> dict:
    """Signal 2 (rules 47 to 53): each kept program built and run, every inert
    call given a body that records that it ran and returns a chosen value;
    rule 67: a program holding `goto *a;` run through the label table; rules 65
    and 66: built again with stand-ins, or with a constant; rule 71: the X sets."""
    chosen = programs_that_run(accepted)
    run_with_the_label_table(chosen, accepted, lowerer)
    chunks = chunks_of_the_programs(chosen["run"], accepted, lowerer)
    results = results_from_the_pool(chunks, lowerer["pool"])
    build_again_with_a_constant(results, chosen, accepted, lowerer)
    runs = runs_record(chosen, results)
    return runs


def programs_that_run(accepted: dict) -> dict:
    """Rule 47; rule 67: the programs holding `goto *a;` set apart for the label table."""
    chosen = {}
    chosen["run"] = []
    chosen["not_run"] = []
    chosen["label_table"] = []
    chosen["started"] = time.time()
    for arrangement in accepted["arrangements"]:
        add_to_run_or_not(chosen, arrangement, accepted["listings"])
    return chosen


def add_to_run_or_not(chosen: dict, arrangement: dict, listings: dict) -> None:
    if arrangement["accepted"] or arrangement["alone"]:
        reason = why_not_run(arrangement, listings)
        if reason is None and has_an_indirect_goto(arrangement, listings):
            chosen["label_table"].append(arrangement)
        elif reason is None:
            chosen["run"].append(arrangement)
        else:
            chosen["not_run"].append({"program": identity_of(arrangement), "why": reason})


def why_not_run(arrangement: dict, listings: dict):
    reason = None
    if arrangement["alone"] and not arrangement["accepted"]:
        reason = why_refused_alone(listings["by_text"][arrangement["group"]])
    return reason


def why_refused_alone(listing: dict) -> str:
    reason = "refused alone, under every fill"
    if listing["role"] == "dependent":
        reason = "refused alone (a dependent: its runs are in the groups)"
    if listing["role"] == "refused alone and in every holder":
        reason = "refused alone and held in every holder"
    if listing.get("not_accepted") is not None:
        reason = role_not_accepted(listing["not_accepted"]) + ": " + "; ".join(listing["not_accepted"]["messages"])
    return reason


# Rule 67 : `goto *a;` run through the label table


def run_with_the_label_table(chosen: dict, accepted: dict, lowerer: dict) -> None:
    """Rule 67: each program holding `goto *a;` written again as its label table variant and asked of the
    lowerer; each the lowerer accepts is run as the variant."""
    variants = []
    texts = []
    for arrangement in chosen["label_table"]:
        written = label_table_variant(arrangement, accepted)
        variants.append(written)
        texts.append(written["text"])
    answers = answers_of_programs(texts, lowerer)
    for index in range(len(variants)):
        take_the_variant(chosen, chosen["label_table"][index], variants[index], answers[index])


def label_table_variant(arrangement: dict, accepted: dict) -> dict:
    listings = accepted["listings"]
    if arrangement["alone"]:
        listing = listings["by_text"][arrangement["group"]]
        written = program_alone(listing, listings, listing["fill"], True, None, None, label_table_overrides(listing),
                                listing["context"], True)
    else:
        group = label_table_group(groups_by_name(accepted["groups"])[arrangement["group"]])
        written = program_of_prefix(group, arrangement["tokens"], tuple(arrangement["levels"]), None)
    return written


def label_table_overrides(listing: dict) -> dict:
    overrides = dict(listing["fill_overrides"])
    for letter in own_values_of(listing["listing"]):
        overrides[letter] = {"form": LABEL_TABLE, "holder": None}
    return overrides


def label_table_group(group: dict) -> dict:
    """Rule 67: the group with each `goto *a;` component's value written as the label table's entry."""
    variant = dict(group)
    variant["label_table"] = True
    variant["type_copies"] = []
    for copies in group["type_copies"]:
        variant["type_copies"].append(copies_with_the_label_table(copies))
    return variant


def copies_with_the_label_table(copies: list) -> list:
    changed = []
    for component in copies:
        changed.append(component_with_the_label_table(component))
    return changed


def component_with_the_label_table(component: dict) -> dict:
    changed = component
    if component["kind"] == "IndirectGotoStmt":
        changed = dict(component)
        changed["forms"] = dict(component["forms"])
        for letter in component["values"]:
            changed["forms"][letter] = {"form": LABEL_TABLE, "holder": None}
    return changed


def take_the_variant(chosen: dict, arrangement: dict, written: dict, answer: dict) -> None:
    if answer["accepted"]:
        written_into(arrangement, written, "the label table variant (rule 67)")
        chosen["run"].append(arrangement)
    else:
        chosen["not_run"].append({"program": identity_of(arrangement),
                                  "why": f"its label table variant was refused: {answer_described(answer)}",
                                  "sort": sort_of(answer["message"])})


def written_into(arrangement: dict, written: dict, run_as: str) -> None:
    """The program a run builds, in place of the one signal 1 asked, which is kept."""
    if "asked_program" not in arrangement:
        arrangement["asked_program"] = program_text_of(arrangement)
    arrangement["header"] = written["header"]
    arrangement["function"] = written["function"]
    arrangement["forms_by_number"] = written["forms_by_number"]
    arrangement["numbers"] = written["numbers"]
    arrangement["number_count"] = written["number_count"]
    arrangement["own_slots"] = written.get("own_slots", arrangement.get("own_slots", []))
    arrangement["context"] = written["context"]
    arrangement["run_as"] = run_as


# Rule 66 : built again with a constant


def build_again_with_a_constant(results: dict, chosen: dict, accepted: dict, lowerer: dict) -> None:
    """Rule 66: a listing alone whose build clang cannot compile yet, written again with one value at a time as a
    constant; the first the lowerer accepts and that builds and runs is kept."""
    for arrangement in chosen["run"]:
        result = results.get(identity_of(arrangement))
        if arrangement["alone"] and result is not None and NOT_COMPILED_YET in result.get("build_output", ""):
            build_one_again_with_a_constant(arrangement, results, accepted, lowerer)


def build_one_again_with_a_constant(arrangement: dict, results: dict, accepted: dict, lowerer: dict) -> None:
    listing = accepted["listings"]["by_text"][arrangement["group"]]
    identity = identity_of(arrangement)
    tried = []
    for letter in letters_a_constant_may_take(listing):
        if results[identity].get("constant_in") is None:
            tried.append(a_constant_tried(arrangement, listing, letter, results, accepted, lowerer))
    results[identity]["constants_tried"] = tried


def letters_a_constant_may_take(listing: dict) -> list:
    letters = []
    for letter in own_values_of(listing["listing"]):
        if letter not in held_letters_of(listing) and letter not in listing["fill_overrides"]:
            letters.append(letter)
    return letters


def a_constant_tried(arrangement: dict, listing: dict, letter: str, results: dict, accepted: dict,
                     lowerer: dict) -> dict:
    """One value as a constant: asked, then built and run; kept when it runs."""
    overrides = dict(listing["fill_overrides"])
    overrides[letter] = {"form": "constant", "holder": holder_spelled(listing, letter)}
    written = program_alone(listing, accepted["listings"], listing["fill"], True, None, None, overrides,
                            listing["context"])
    answer = answers_of_programs([written["text"]], lowerer)[0]
    tried = {"constant_in": letter, "asked": answer_described(answer), "built_and_run": False}
    if answer["accepted"]:
        tried["built_and_run"] = built_and_run_with_a_constant(arrangement, listing, written, overrides, letter,
                                                               results, accepted, lowerer)
    return tried


def built_and_run_with_a_constant(arrangement: dict, listing: dict, written: dict, overrides: dict, letter: str,
                                  results: dict, accepted: dict, lowerer: dict) -> bool:
    variant = dict(arrangement)
    written_into(variant, written, f"with {letter} as a constant (rule 66)")
    chunk = chunk_task([variant], accepted["listings"], lowerer)
    result = results_from_the_pool([chunk], lowerer["pool"]).get(identity_of(arrangement))
    ran = result is not None and result["not_run"] is None
    if ran:
        written_into(arrangement, written, f"with {letter} as a constant (rule 66)")
        result["constant_in"] = letter
        results[identity_of(arrangement)] = result
        listing["fill_overrides"] = overrides
    return ran


def has_an_indirect_goto(arrangement: dict, listings: dict) -> bool:
    found = False
    if arrangement["alone"]:
        found = listings["by_text"][arrangement["group"]]["kind"] == "IndirectGotoStmt"
    for line in arrangement["lines"]:
        if not is_inert_call(line) and line["kind"] == "IndirectGotoStmt":
            found = True
    return found


def identity_of(arrangement: dict) -> str:
    identity = f"{arrangement['group']}#{arrangement['number']}"
    if arrangement["alone"]:
        identity = arrangement["group"]
    return identity


def chunks_of_the_programs(run: list, accepted: dict, lowerer: dict) -> list:
    """Rule 48: up to 500 programs of one group with the same declarations to a file."""
    by_header = programs_by_group_and_header(run)
    chunks = []
    for key in by_header:
        add_chunks(chunks, by_header[key], accepted["listings"], lowerer)
    return chunks


def programs_by_group_and_header(run: list) -> dict:
    by_header = {}
    for arrangement in run:
        key = (arrangement["group"], arrangement["header"])
        add_to_a_list(by_header, key, arrangement)
    return by_header


def add_chunks(chunks: list, arrangements: list, listings: dict, lowerer: dict) -> None:
    for first in range(0, len(arrangements), PROGRAMS_PER_BUILD):
        chunks.append(chunk_task(arrangements[first:first + PROGRAMS_PER_BUILD], listings, lowerer))


def chunk_task(arrangements: list, listings: dict, lowerer: dict) -> dict:
    task = {}
    task["header"] = arrangements[0]["header"]
    task["stand_ins_build"] = GNU_C_STAND_INS
    task["functions"] = functions_renamed(arrangements)
    task["kinds"] = harness_kinds(arrangements[0], listings)
    task["typed"] = has_typed_kinds(task["kinds"])
    task["held_types"] = listings["holder_types"]
    task["traces"] = arrangements[0]["alone"]
    task["folder"] = lowerer["work_folder"]
    task["build"] = lowerer["build"]
    return task


def functions_renamed(arrangements: list) -> list:
    functions = []
    for index in range(len(arrangements)):
        functions.append(function_renamed(arrangements[index], index))
    return functions


def function_renamed(arrangement: dict, index: int) -> dict:
    function = {}
    function["identity"] = identity_of(arrangement)
    function["source"] = arrangement["function"]
    function["context"] = arrangement.get("context", TODAYS_CONTEXT)
    function["text"] = function_text(function, index)
    function["count"] = arrangement["number_count"]
    return function


def function_text(function: dict, index: int) -> str:
    """Rule 48: the program's function named f_<index>; rule 64: a context's function named g_<index>, which
    f_<index> calls with the context's arguments."""
    lines = function["source"].split("\n")
    context = context_named(function["context"])
    if context["context"] == TODAYS_CONTEXT:
        lines[0] = C_FUNCTION_NAMED.format(f"f_{index}")
    else:
        lines[0] = C_CONTEXT_FUNCTION.format(context["returns"], index, context["parameters"])
        lines.append(C_CONTEXT_CALLER.format(index, context["arguments"]))
    text = "\n".join(lines)
    return text


def harness_kinds(arrangement: dict, listings: dict) -> list:
    """Rule 49: for each inert number, how its body returns."""
    kinds = []
    for number in range(arrangement["number_count"]):
        kinds.append(harness_kind(arrangement["forms_by_number"].get(number), listings))
    return kinds


def harness_kind(form, listings: dict) -> dict:
    """Rule 49: how an inert call's body returns; rule 71: the values of its X set, when it returns a number."""
    kind = {"kind": "int", "holder": None}
    if form is not None and form["form"] == "address":
        kind = {"kind": "address", "holder": form["holder"]}
    if form is not None and form["form"] == "value":
        kind = {"kind": value_kind(form["holder"], listings), "holder": form["holder"]}
    kind["values"] = x_set_of(kind, form, listings)
    return kind


def x_set_of(kind: dict, form, listings: dict) -> list:
    """Rule 71: the X set of an inert call, clipped to its own type, each value with its label and its C text;
    none for one that returns no number."""
    values = []
    if kind["kind"] == "int" and form is not None and form.get("holder") == "_Bool":
        values = TRUTH_IN_BOOL
    elif kind["kind"] == "int":
        values = WHOLE_IN_INT
    elif kind["kind"] == "arithmetic":
        values = fractional_in(listings["holder_classes"].get(holder_unspelled(kind["holder"])))
    return values


def fractional_in(class_name) -> list:
    """Rule 71: the fractional set, with NaN and both infinities, written in one floating type."""
    values = []
    written = FLOATING_TYPES.get(class_name)
    if written is not None:
        for label, text in FRACTIONAL:
            add_a_value_it_holds(values, label, text, written)
    return values


def add_a_value_it_holds(values: list, label: str, text: str, written: dict) -> None:
    """A value the type holds, in its C text; a type with no literal suffix of its own (`_Float16`) by a cast."""
    if label not in written["left_out"]:
        value = text.format(**written)
        if written["cast"] is not None:
            value = f"(({written['cast']}) ({value}))"
        values.append((label, value))


def value_kind(holder: str, listings: dict) -> str:
    kind = "pointer"
    if listings["holder_classes"].get(holder_unspelled(holder)) in FLOATING_CLASSES:
        kind = "arithmetic"
    if holder in listings["function_pointers"]:
        kind = "function pointer"
    return kind


def has_typed_kinds(kinds: list) -> bool:
    typed = False
    for kind in kinds:
        if kind["kind"] != "int":
            typed = True
    return typed


def results_from_the_pool(chunks: list, pool) -> dict:
    results = {}
    if len(chunks) > 0:
        place_the_results(results, chunks, pool)
    return results


def place_the_results(results: dict, chunks: list, pool) -> None:
    done = 0
    started = time.time()
    for chunk_results in pool.imap_unordered(runs_of_a_chunk, chunks):
        place_chunk_results(results, chunk_results)
        done += 1
        if done % 50 == 0 or done == len(chunks):
            progress(f"signal 2: {done} of {len(chunks)} builds run, {round(time.time() - started)} s")


def place_chunk_results(results: dict, chunk_results: list) -> None:
    for result in chunk_results:
        results[result["identity"]] = result


def runs_of_a_chunk(task: dict) -> list:
    """Rules 48 to 52: one file of programs built, linked with the harness, and run."""
    folder = folder_of_this_worker(task["folder"], "run")
    binary = built(task, task["functions"], folder, "chunk")
    if binary is None:
        results = runs_one_program_at_a_time(task, folder)
    else:
        results = runs_of_a_build(binary, task, task["functions"])
    remove_the_build(folder)
    return results


def built(task: dict, functions: list, folder: str, name: str, objects=None):
    """Rule 48: the programs and the harness, built for the VM's own processor; None when clang refuses. Rule 65:
    the whole output of a build that fails is kept; objects (the stand-ins) are linked in when named."""
    write_text(os.path.join(folder, name + ".c"), chunk_text(task, functions))
    write_text(os.path.join(folder, "harness.c"), harness_text(task))
    linked = []
    if objects is not None:
        linked = objects
    finished = subprocess.run(task["build"] + [name + ".c", "harness.c"] + linked + ["-o", name] + GNU_C_LIBRARIES,
                              cwd=folder, capture_output=True, text=True, timeout=BUILD_SECONDS)
    binary = None
    if finished.returncode == 0:
        binary = os.path.join(folder, name)
    else:
        task["last_build_error"] = first_build_error(finished.stderr)
        task["last_build_output"] = finished.stderr
    return binary


def first_build_error(output: str) -> str:
    found = "(no error line)"
    for line in output.splitlines():
        if FIRST_ERROR_MARK in line or FATAL_ERROR_MARK in line:
            found = line
            break
    return found


def chunk_text(task: dict, functions: list) -> str:
    lines = [task["header"]]
    names = []
    for index in range(len(functions)):
        lines.append(functions[index]["text"])
        names.append(f"f_{index}")
    lines.append("typedef void (*program_function)(void);")
    lines.append("program_function programs[] = {" + ", ".join(names) + "};")
    lines.append(f"int program_count = {len(functions)};")
    lines.append("")
    text = "\n".join(lines)
    return text


def runs_one_program_at_a_time(task: dict, folder: str) -> list:
    results = []
    for function in task["functions"]:
        add_all(results, runs_of_one_program(task, function, folder))
    return results


def runs_of_one_program(task: dict, function: dict, folder: str) -> list:
    """Rule 48: one program built alone; rule 65: when it does not link, linked again with a stand-in for each
    function the linker names."""
    binary = built(task, [function_as_the_first(function)], folder, "one")
    stand_ins = []
    if binary is None:
        stand_ins = undefined_references(task.get("last_build_output", ""))
    if binary is None and len(stand_ins) > 0:
        binary = built_with_stand_ins(task, [function_as_the_first(function)], folder, stand_ins)
    results = []
    if binary is None:
        results.append(not_run_result(function, f"refused when built for the VM's processor: "
                                                f"{task.get('last_build_error')}", task, stand_ins))
    else:
        results = runs_of_a_build(binary, task, [function])
        add_the_stand_ins(results, stand_ins)
    return results


def function_as_the_first(function: dict) -> dict:
    first = dict(function)
    first["text"] = function_text(function, 0)
    return first


def not_run_result(function: dict, reason: str, task=None, stand_ins=None) -> dict:
    """Rule 65: with the build's whole output, and the stand-ins tried."""
    result = {}
    result["identity"] = function["identity"]
    result["not_run"] = reason
    result["sort"] = sort_of(reason)
    if task is not None:
        result["build_output"] = task.get("last_build_output", "")
    if stand_ins is not None and len(stand_ins) > 0:
        result["stand_ins_tried"] = stand_ins
    return result


# Rule 65 : stand-ins for what the linker does not find


def undefined_references(output: str) -> list:
    """Each name the linker says it has no definition of, once, in the order named."""
    names = []
    for found in UNDEFINED_REFERENCE.finditer(output):
        add_new(names, found.group(1))
    return names


def stand_ins_text(names: list) -> str:
    """Rule 75: each stand-in under a name of its own, `stand_in_<k>`, the symbol the linker asked for set by an
    assembler label, so clang never sees that name declared (a name clang keeps as its own builtin is refused as a
    declaration of conflicting type)."""
    lines = []
    for index in range(len(names)):
        lines.append(C_STAND_IN_DECLARED.format(index, names[index]))
        lines.append(C_STAND_IN.format(index))
    lines.append("")
    text = "\n".join(lines)
    return text


def built_with_stand_ins(task: dict, functions: list, folder: str, names: list):
    """Rule 65: a stand-in for each name, in a file of its own built with -fno-builtin, linked with the program;
    rule 75: each under a name of its own."""
    write_text(os.path.join(folder, "stand_ins.c"), stand_ins_text(names))
    compiled = subprocess.run(task["stand_ins_build"] + ["stand_ins.c", "-o", "stand_ins.o"], cwd=folder,
                              capture_output=True, text=True, timeout=BUILD_SECONDS)
    binary = None
    if compiled.returncode == 0:
        binary = built(task, functions, folder, "one", ["stand_ins.o"])
    else:
        task["last_build_error"] = first_build_error(compiled.stderr)
        task["last_build_output"] = compiled.stderr
    return binary


def add_the_stand_ins(results: list, stand_ins: list) -> None:
    for result in results:
        if len(stand_ins) > 0:
            result["stand_ins"] = stand_ins


def remove_the_build(folder: str) -> None:
    for name in os.listdir(folder):
        os.remove(os.path.join(folder, name))


# Rule 49: the harness


HARNESS_START = [
    "#include <fcntl.h>",
    "#include <signal.h>",
    "#include <stdint.h>",
    "#include <stdio.h>",
    "#include <stdlib.h>",
    "#include <string.h>",
    "#include <sys/mman.h>",
    "#include <sys/time.h>",
    "#include <sys/wait.h>",
    "#include <unistd.h>",
]

HARNESS_RECORD = [
    "#define CAP " + str(CAP),
    "#define MOST 256",
    "typedef void (*program_function)(void);",
    "extern program_function programs[];",
    "extern int program_count;",
    "static int *shared;",
    "static unsigned char schedule[MOST][CAP];",
    "static int schedule_length[MOST];",
    "static int calls_of[MOST];",
    "static int value_index[MOST];",
    "static _Alignas(64) unsigned char harness_buffer[4096];",
    "static int harness_called() { return 0; }",
    "static int record(int number) {",
    "    int at = shared[0];",
    "    if (at >= CAP) {",
    "        shared[1] = 1;",
    "        _exit(0);",
    "    }",
    "    shared[3 + at] = number;",
    "    shared[0] = at + 1;",
    "    int value = 0;",
    "    if (calls_of[number] < schedule_length[number]) {",
    "        value = schedule[number][calls_of[number]];",
    "    }",
    "    calls_of[number] += 1;",
    "    return value;",
    "}",
]

HARNESS_MAIN = [
    "static void read_schedule(char **cursor, int number) {",
    "    while (**cursor == ' ') {",
    "        (*cursor)++;",
    "    }",
    "    int length = 0;",
    "    value_index[number] = -1;",
    "    if (**cursor == 'x') {",
    "        (*cursor)++;",
    "        value_index[number] = (int) strtol(*cursor, cursor, 10);",
    "    }",
    "    if (**cursor == '-') {",
    "        (*cursor)++;",
    "    }",
    "    while (**cursor == '0' || **cursor == '1') {",
    "        if (length < CAP) {",
    "            schedule[number][length] = (unsigned char)(**cursor - '0');",
    "            length++;",
    "        }",
    "        (*cursor)++;",
    "    }",
    "    schedule_length[number] = length;",
    "}",
    "static void outcome_of(int status, char *outcome) {",
    "    if (shared[1]) {",
    "        snprintf(outcome, 32, \"C\");",
    "    } else if (shared[2] && WIFEXITED(status) && WEXITSTATUS(status) == 0) {",
    "        snprintf(outcome, 32, \"R\");",
    "    } else if (WIFEXITED(status)) {",
    "        snprintf(outcome, 32, \"E%d\", WEXITSTATUS(status));",
    "    } else if (WIFSIGNALED(status) && WTERMSIG(status) == SIGALRM) {",
    "        snprintf(outcome, 32, \"T\");",
    "    } else if (WIFSIGNALED(status)) {",
    "        snprintf(outcome, 32, \"S%d\", WTERMSIG(status));",
    "    } else {",
    "        snprintf(outcome, 32, \"U\");",
    "    }",
    "}",
    "static unsigned long long trace_hash(int calls, const char *outcome) {",
    "    unsigned long long hash = 1469598103934665603ULL;",
    "    for (int at = 0; at < calls; at++) {",
    "        hash = (hash ^ (unsigned long long)(shared[3 + at] + 1)) * 1099511628211ULL;",
    "    }",
    "    hash = (hash ^ (unsigned long long)(unsigned char)outcome[0]) * 1099511628211ULL;",
    "    return hash;",
    "}",
    "int main(void) {",
    "    shared = mmap(NULL, sizeof(int) * (3 + CAP), PROT_READ | PROT_WRITE, MAP_SHARED | MAP_ANONYMOUS, -1, 0);",
    "    int nothing = open(\"/dev/null\", O_RDWR);",
    "    static char line[1 << 20];",
    "    while (fgets(line, sizeof line, stdin) != NULL) {",
    "        char *cursor = line;",
    "        long job = strtol(cursor, &cursor, 10);",
    "        int which = (int) strtol(cursor, &cursor, 10);",
    "        int traces = (int) strtol(cursor, &cursor, 10);",
    "        int count = (int) strtol(cursor, &cursor, 10);",
    "        for (int number = 0; number < count && number < MOST; number++) {",
    "            read_schedule(&cursor, number);",
    "            calls_of[number] = 0;",
    "        }",
    "        memset(shared, 0, sizeof(int) * (3 + CAP));",
    "        fflush(stdout);",
    "        pid_t forked = fork();",
    "        if (forked == 0) {",
    "            dup2(nothing, 0);",
    "            dup2(nothing, 1);",
    "            dup2(nothing, 2);",
    "            struct itimerval timer;",
    "            memset(&timer, 0, sizeof timer);",
    "            timer.it_value.tv_usec = 20000;",
    "            setitimer(ITIMER_REAL, &timer, NULL);",
    "            if (which >= 0 && which < program_count) {",
    "                programs[which]();",
    "            }",
    "            shared[2] = 1;",
    "            _exit(0);",
    "        }",
    "        int status = 0;",
    "        waitpid(forked, &status, 0);",
    "        char outcome[32];",
    "        outcome_of(status, outcome);",
    "        int calls = shared[0];",
    "        if (calls > CAP) {",
    "            calls = CAP;",
    "        }",
    "        printf(\"%ld %s %d %016llx \", job, outcome, calls, trace_hash(calls, outcome));",
    "        for (int number = 0; number < count; number++) {",
    "            int seen = 0;",
    "            for (int at = 0; at < calls; at++) {",
    "                if (shared[3 + at] == number) {",
    "                    seen++;",
    "                }",
    "            }",
    "            if (seen > 9) {",
    "                seen = 9;",
    "            }",
    "            putchar('0' + seen);",
    "        }",
    "        if (traces) {",
    "            putchar(' ');",
    "            for (int at = 0; at < calls; at++) {",
    "                printf(at ? \",%d\" : \"%d\", shared[3 + at]);",
    "            }",
    "        }",
    "        putchar('\\n');",
    "    }",
    "    return 0;",
    "}",
]


def harness_text(task: dict) -> str:
    """Rule 49: a body for each inert call, and the runs."""
    lines = list(HARNESS_START)
    if task["typed"]:
        add_all(lines, task["held_types"])
    add_all(lines, HARNESS_RECORD)
    for number in range(len(task["kinds"])):
        add_all(lines, values_table(number, task["kinds"][number]))
        lines.append(inert_body(number, task["kinds"][number]))
    add_all(lines, HARNESS_MAIN)
    lines.append("")
    text = "\n".join(lines)
    return text


def values_table(number: int, kind: dict) -> list:
    """Rule 71: the inert call's X set as a table of its own type, which the harness returns from by index."""
    lines = []
    if len(kind.get("values", [])) > 0:
        texts = []
        for label, value in kind["values"]:
            texts.append(value)
        lines.append(f"static const {value_type_of(kind)} values_{number}[] = {{ {', '.join(texts)} }};")
    return lines


def value_type_of(kind: dict) -> str:
    written = "int"
    if kind["kind"] == "arithmetic":
        written = C_VALUE_TYPE.format(kind["holder"])
    return written


def inert_body(number: int, kind: dict) -> str:
    """Rule 49; rule 71: an inert call with an X set returns the value its schedule names (`x<index>`)."""
    body = f"int inert_{number}(void) {{ return record({number}); }}"
    holder = kind["holder"]
    if kind["kind"] == "int" and len(kind.get("values", [])) > 0:
        body = (f"int inert_{number}(void) {{ int value = record({number}); if (value_index[{number}] >= 0) "
                f"{{ return values_{number}[value_index[{number}]]; }} return value; }}")
    if kind["kind"] == "arithmetic":
        value_type = C_VALUE_TYPE.format(holder)
        body = f"{value_type} inert_{number}(void) {{ return ({value_type}) record({number}); }}"
    if kind["kind"] == "arithmetic" and len(kind.get("values", [])) > 0:
        value_type = C_VALUE_TYPE.format(holder)
        body = (f"{value_type} inert_{number}(void) {{ int value = record({number}); if (value_index[{number}] >= 0) "
                f"{{ return values_{number}[value_index[{number}]]; }} return ({value_type}) value; }}")
    if kind["kind"] == "pointer":
        value_type = C_VALUE_TYPE.format(holder)
        body = (f"{value_type} inert_{number}(void) {{ record({number}); "
                f"return ({value_type}) (void *) harness_buffer; }}")
    if kind["kind"] == "function pointer":
        value_type = C_VALUE_TYPE.format(holder)
        body = f"{value_type} inert_{number}(void) {{ record({number}); return ({value_type}) harness_called; }}"
    if kind["kind"] == "address":
        body = (f"__typeof__({holder}) *inert_{number}(void) {{ static __typeof__({holder}) object; "
                f"record({number}); return &object; }}")
    return body


# Rules 50 to 52: the values tried, and the readings


def runs_of_a_build(binary: str, task: dict, functions: list) -> list:
    base = base_runs(binary, task, functions)
    flips = flip_runs(binary, task, functions, base)
    tested = tested_by_function(functions, base, flips)
    schedules = schedule_runs(binary, functions, tested)
    x_sets = x_set_runs(binary, task, functions)
    results = results_of_the_runs(functions, base, flips, schedules, tested, task, x_sets)
    return results


def x_set_runs(binary: str, task: dict, functions: list) -> dict:
    """Rule 71: for a listing alone, each inert call that returns a number, each value of its X set, on every
    call, the others returning 1."""
    jobs = []
    if task["traces"]:
        for index in range(len(functions)):
            add_x_set_jobs(jobs, index, functions[index]["count"], task["kinds"])
    outcomes = run_the_jobs_or_none(binary, jobs)
    runs = runs_by_function(jobs, outcomes)
    return runs


def add_x_set_jobs(jobs: list, index: int, count: int, kinds: list) -> None:
    for number in range(count):
        for value in range(len(kinds[number].get("values", []))):
            jobs.append(new_job(len(jobs), index, False, x_set_schedules(count, number, value),
                                ("x set", number, value)))


def x_set_schedules(count: int, number: int, value: int) -> list:
    schedules = every_schedule(count, all_ones())
    schedules[number] = f"x{value}"
    return schedules


def x_set_record(runs: list, kinds: list) -> list:
    """Rule 71: each run with an X set's value: the inert call varied, the value's label, how it ended, the
    calls of each inert call."""
    record = []
    for run in runs:
        number = run["what"][1]
        entry = {}
        entry["number"] = number
        entry["value"] = kinds[number]["values"][run["what"][2]][0]
        entry["outcome"] = run["outcome"]
        entry["counts"] = run["counts"]
        record.append(entry)
    return record


def tested_by_function(functions: list, base: dict, flips: dict) -> dict:
    tested = {}
    for index in range(len(functions)):
        tested[index] = tested_of(base.get(index, []), flips.get(index, []))
    return tested


def every_schedule(count: int, schedule: str) -> list:
    schedules = []
    for _number in range(count):
        schedules.append(schedule)
    return schedules


def all_ones() -> str:
    ones = "1" * CAP
    return ones


def base_runs(binary: str, task: dict, functions: list) -> dict:
    """Rule 50: every schedule all 0, and all 1."""
    jobs = []
    for index in range(len(functions)):
        count = functions[index]["count"]
        jobs.append(new_job(len(jobs), index, task["traces"], every_schedule(count, ""), ("all 0", None)))
        jobs.append(new_job(len(jobs), index, task["traces"], every_schedule(count, all_ones()), ("all 1", None)))
    outcomes = run_the_jobs(binary, jobs)
    base = runs_by_function(jobs, outcomes)
    return base


def new_job(identity: int, which: int, traces: bool, schedules: list, what: tuple) -> dict:
    job = {}
    job["id"] = identity
    job["which"] = which
    job["traces"] = traces
    job["schedules"] = schedules
    job["what"] = what
    return job


def run_the_jobs(binary: str, jobs: list) -> dict:
    lines = []
    for job in jobs:
        lines.append(job_line(job))
    finished = subprocess.run([binary], input="\n".join(lines) + "\n", capture_output=True, text=True,
                              timeout=RUNS_SECONDS)
    outcomes = outcomes_of(finished.stdout)
    return outcomes


def job_line(job: dict) -> str:
    parts = [str(job["id"]), str(job["which"]), str(int(job["traces"])), str(len(job["schedules"]))]
    for schedule in job["schedules"]:
        parts.append(schedule_written(schedule))
    line = " ".join(parts)
    return line


def schedule_written(schedule: str) -> str:
    written = schedule
    if schedule == "":
        written = "-"
    return written


def outcomes_of(output: str) -> dict:
    outcomes = {}
    for line in output.splitlines():
        parts = line.split(" ")
        if len(parts) >= 5:
            outcomes[int(parts[0])] = outcome_entry(parts)
    return outcomes


def outcome_entry(parts: list) -> dict:
    entry = {}
    entry["outcome"] = parts[1]
    entry["calls"] = int(parts[2])
    entry["hash"] = parts[3]
    entry["counts"] = parts[4]
    entry["trace"] = None
    if len(parts) >= 6:
        entry["trace"] = trace_of(parts[5])
    return entry


def trace_of(written: str) -> list:
    trace = []
    for number in written.split(","):
        if number != "":
            trace.append(int(number))
    return trace


def runs_by_function(jobs: list, outcomes: dict) -> dict:
    """Each function's runs, each with what was tried; a run with no answer is counted lost."""
    by_function = {}
    for job in jobs:
        add_to_a_list(by_function, job["which"], run_of_a_job(job, outcomes))
    return by_function


def run_of_a_job(job: dict, outcomes: dict) -> dict:
    run = dict(outcomes.get(job["id"], lost_run(len(job["schedules"]))))
    run["what"] = job["what"]
    run["schedules"] = job["schedules"]
    return run


def lost_run(count: int) -> dict:
    run = {}
    run["outcome"] = "L"
    run["calls"] = 0
    run["hash"] = "lost"
    run["counts"] = "0" * count
    run["trace"] = None
    return run


def flip_runs(binary: str, task: dict, functions: list, base: dict) -> dict:
    """Rule 50: from each base, each inert call's schedule alone flipped, when it ran there and returns a number."""
    jobs = []
    for index in range(len(functions)):
        add_flip_jobs(jobs, index, base.get(index, []), task)
    outcomes = run_the_jobs_or_none(binary, jobs)
    flips = runs_by_function(jobs, outcomes)
    return flips


def run_the_jobs_or_none(binary: str, jobs: list) -> dict:
    outcomes = {}
    if len(jobs) > 0:
        outcomes = run_the_jobs(binary, jobs)
    return outcomes


def add_flip_jobs(jobs: list, index: int, base: list, task: dict) -> None:
    for run in base:
        for number in range(len(run["schedules"])):
            if returns_a_number(task["kinds"][number]) and run["counts"][number] != "0":
                jobs.append(new_job(len(jobs), index, False, flipped(run, number), (run["what"][0], number)))


def returns_a_number(kind: dict) -> bool:
    number = kind["kind"] in ("int", "arithmetic")
    return number


def flipped(run: dict, number: int) -> list:
    schedules = list(run["schedules"])
    if run["what"][0] == "all 0":
        schedules[number] = all_ones()
    else:
        schedules[number] = ""
    return schedules


def tested_of(base: list, flips: list) -> list:
    """Rule 50: an inert call whose flip changes the trace."""
    hashes = base_hashes(base)
    tested = []
    for run in flips:
        number = run["what"][1]
        if run["hash"] != hashes.get(run["what"][0]) and number not in tested:
            tested.append(number)
    tested.sort()
    return tested


def base_hashes(base: list) -> dict:
    hashes = {}
    for run in base:
        hashes[run["what"][0]] = run["hash"]
    return hashes


def schedule_runs(binary: str, functions: list, tested: dict) -> dict:
    """Rule 50: every schedule of length 3 for each tested inert call, combined."""
    jobs = []
    combined = {}
    for index in range(len(functions)):
        combined[index] = add_schedule_jobs(jobs, index, functions[index]["count"], tested[index])
    outcomes = run_the_jobs_or_none(binary, jobs)
    schedules = runs_by_function(jobs, outcomes)
    schedules["combined"] = combined
    return schedules


def add_schedule_jobs(jobs: list, index: int, count: int, tested: list) -> bool:
    combinations = schedule_combinations(tested)
    for combination in combinations["each"]:
        jobs.append(new_job(len(jobs), index, False, schedules_of_a_combination(count, combination),
                            ("schedules", None)))
    combined = combinations["combined"]
    return combined


def schedule_combinations(tested: list) -> dict:
    combinations = {}
    combinations["combined"] = 8 ** len(tested) <= MOST_COMBINED_RUNS
    if combinations["combined"]:
        combinations["each"] = combined_schedules(tested)
    else:
        combinations["each"] = each_tested_alone(tested)
    return combinations


def schedules_of_length_3() -> list:
    schedules = []
    for value in range(2 ** SCHEDULE_LENGTH):
        schedules.append(format(value, "03b"))
    return schedules


def combined_schedules(tested: list) -> list:
    combinations = [[]]
    for number in tested:
        combinations = each_with_one_more(combinations, number)
    if len(tested) == 0:
        combinations = []
    return combinations


def each_with_one_more(combinations: list, number: int) -> list:
    longer = []
    for combination in combinations:
        for schedule in schedules_of_length_3():
            longer.append(combination + [(number, schedule)])
    return longer


def each_tested_alone(tested: list) -> list:
    combinations = []
    for number in tested:
        for schedule in schedules_of_length_3():
            combinations.append([(number, schedule)])
    return combinations


def schedules_of_a_combination(count: int, combination: list) -> list:
    schedules = every_schedule(count, "")
    for number, schedule in combination:
        schedules[number] = schedule
    return schedules


def results_of_the_runs(functions: list, base: dict, flips: dict, schedules: dict, tested: dict,
                        task: dict, x_sets: dict) -> list:
    results = []
    for index in range(len(functions)):
        result = result_of_a_program(functions[index], base.get(index, []), flips.get(index, []),
                                     schedules.get(index, []), schedules["combined"][index], tested[index], task)
        add_the_x_sets(result, functions[index], base.get(index, []) + flips.get(index, []) +
                       schedules.get(index, []), x_sets.get(index, []), tested[index], task)
        results.append(result)
    return results


def result_of_a_program(function: dict, base: list, flips: list, schedules: list, combined: bool,
                        tested: list, task: dict) -> dict:
    """Rules 51 to 53."""
    every_run = base + flips + schedules
    result = {}
    result["identity"] = function["identity"]
    result["not_run"] = None
    result["readings"] = readings_of(function["count"], every_run, tested)
    result["tested"] = tested
    result["runs"] = len(every_run)
    result["outcomes"] = outcomes_tallied(every_run)
    result["combined"] = combined
    if task["traces"]:
        result["traces"] = base_traces(base)
    return result


def add_the_x_sets(result: dict, function: dict, every_run: list, x_runs: list, tested: list, task: dict) -> None:
    """Rule 71: the runs with the X sets' values, and the readings over every run, these with rule 50's."""
    if task["traces"]:
        result["x_set"] = x_set_record(x_runs, task["kinds"])
        result["x_set_runs"] = len(x_runs)
        result["x_set_outcomes"] = outcomes_tallied(x_runs)
        result["readings_with_the_x_sets"] = readings_of(function["count"], every_run + x_runs, tested)


def readings_of(count: int, runs: list, tested: list) -> str:
    letters = []
    for number in range(count):
        letters.append(READING_LETTERS[reading_of(number, runs, tested)])
    readings = "".join(letters)
    return readings


def reading_of(number: int, runs: list, tested: list) -> str:
    """Rule 52."""
    seen = what_the_runs_show(number, runs)
    reading = "once"
    if number in tested:
        reading = "tested"
    elif not seen["ran"]:
        reading = "never"
    elif seen["missing"] and seen["again"]:
        reading = "behind the branch and again"
    elif seen["missing"]:
        reading = "behind the branch"
    elif seen["again"]:
        reading = "again"
    return reading


def what_the_runs_show(number: int, runs: list) -> dict:
    seen = {"ran": False, "again": False, "missing": False}
    for run in runs:
        calls = int(run["counts"][number])
        if calls >= 1:
            seen["ran"] = True
        if calls >= 2:
            seen["again"] = True
        if calls == 0 and run["outcome"][0] in FINISHED_OUTCOMES:
            seen["missing"] = True
    return seen


def outcomes_tallied(runs: list) -> dict:
    tallied = {}
    for run in runs:
        add_one(tallied, run["outcome"])
    return tallied


def base_traces(base: list) -> dict:
    traces = {}
    for run in base:
        traces[run["what"][0]] = {"trace": run["trace"], "outcome": run["outcome"]}
    return traces


def runs_record(chosen: dict, results: dict) -> dict:
    """Rule 79: the not-run list, filled as runs finish, sorted before it is written."""
    runs = {}
    runs["results"] = results
    not_run = list(chosen["not_run"])
    add_not_run_results(not_run, results)
    runs["not_run"] = sorted(not_run, key=not_run_key)
    runs["tallies"] = runs_tallied(chosen, results, runs["not_run"])
    return runs


def not_run_key(entry: dict) -> tuple:
    key = (entry["program"], entry["why"])
    return key


def add_not_run_results(not_run: list, results: dict) -> None:
    for identity in results:
        if results[identity]["not_run"] is not None:
            not_run.append({"program": identity, "why": results[identity]["not_run"],
                            "sort": results[identity].get("sort")})


def runs_tallied(chosen: dict, results: dict, not_run: list) -> dict:
    tallied = {}
    tallied["programs_to_run"] = len(chosen["run"])
    tallied["programs_run"] = 0
    tallied["runs"] = 0
    tallied["outcomes"] = {}
    tallied["programs_tried_each_tested_alone"] = 0
    tallied["x_set_runs"] = 0
    tallied["not_run"] = len(not_run)
    tallied["not_run_by_why"] = not_run_by_why(not_run)
    tallied["seconds"] = round(time.time() - chosen["started"], 1)
    for identity in results:
        add_a_result_to_the_tally(tallied, results[identity])
    return tallied


def not_run_by_why(not_run: list) -> dict:
    """Rule 79: by why, the whys in order."""
    counted = {}
    for entry in not_run:
        add_one(counted, why_in_short(entry["why"]))
    by_why = {}
    for why in sorted(counted):
        by_why[why] = counted[why]
    return by_why


def why_in_short(why: str) -> str:
    short = why
    if why.startswith("refused when built"):
        short = "refused when built for the VM's processor"
    return short


def add_a_result_to_the_tally(tallied: dict, result: dict) -> None:
    if result["not_run"] is None:
        tallied["programs_run"] += 1
        tallied["runs"] += result["runs"]
        add_counts(tallied["outcomes"], outcomes_in_short(result["outcomes"]))
        tallied["x_set_runs"] += result.get("x_set_runs", 0)
        if not result["combined"]:
            tallied["programs_tried_each_tested_alone"] += 1


def outcomes_in_short(outcomes: dict) -> dict:
    short = {}
    for outcome in outcomes:
        short[outcome[0]] = short.get(outcome[0], 0) + outcomes[outcome]
    return short


def add_counts(counts: dict, more: dict) -> None:
    for key in more:
        counts[key] = counts.get(key, 0) + more[key]


def add_one(counts: dict, key) -> None:
    if key not in counts:
        counts[key] = 0
    counts[key] += 1


# 6. classify


def classify(accepted: dict, runs: dict) -> dict:
    """What the record shows (rules 23 to 26, 53 to 55), and the part's own check (rule 36); rules 69, 70, 72 and
    73: the reader's places, the declarations' scopes, refusals by sort, and listings read as the same entry."""
    groups = classifications_of_the_groups(accepted, runs)
    alone = listings_alone(accepted, runs)
    add_the_configurations(alone, groups, accepted["listings"])
    checks = checks_of_the_part(accepted, groups)
    configurations = {}
    configurations["part"] = accepted["part"]
    configurations["reading"] = reading_of_the_listings(accepted["listings"])
    configurations["groups"] = groups
    configurations["alone"] = alone
    configurations["asks"] = accepted["asks"]
    configurations["search_seconds"] = accepted["search_seconds"]
    configurations["signal_2"] = runs["tallies"]
    configurations["not_run"] = runs["not_run"]
    configurations["checks"] = checks
    configurations["refusals_by_sort"] = refusals_by_sort(accepted, groups, runs)
    configurations["read_as_the_same_entry"] = same_entry_check(alone, accepted["listings"])
    if "small_run" in accepted["listings"]:
        configurations["small_run"] = accepted["listings"]["small_run"]
    return configurations


# Rule 72 : every refusal of a part by its sort


def refusals_by_sort(accepted: dict, groups: list, runs: dict) -> dict:
    """Rule 72: the part's refusals by sort: the whole arrangements of its groups, the listings' asks (alone, in a
    context, held in a holder), and the builds of signal 2; and every unsorted message, for the owner."""
    tally = {"whole arrangements": {}, "listings' asks": {}, "builds": {}, "unsorted messages": {}}
    for group in groups:
        for entry in group["first_errors"]:
            add_to_the_sort(tally, "whole arrangements", entry["sort"], entry["refused"], entry["error"])
    for text in accepted["listings"].get("used", []):
        add_the_asks_of_a_listing(tally, accepted["listings"]["by_text"][text])
    for entry in runs["not_run"]:
        if entry.get("sort") is not None:
            add_to_the_sort(tally, "builds", entry["sort"], 1, entry["why"])
    return tally


def add_the_asks_of_a_listing(tally: dict, listing: dict) -> None:
    for key in listing["fill_answer_sorts"]:
        if listing["fill_answer_sorts"][key] != "accepted":
            add_to_the_sort(tally, "listings' asks", listing["fill_answer_sorts"][key], 1,
                            answer_without_line(listing["fill_answers"][key]))


def add_to_the_sort(tally: dict, where: str, sort: str, count: int, message: str) -> None:
    tally[where][sort] = tally[where].get(sort, 0) + count
    if sort == UNSORTED:
        tally["unsorted messages"][message] = tally["unsorted messages"].get(message, 0) + count


# Rule 73 : listings read as the same entry get the same configuration


def same_entry_check(alone: list, listings: dict) -> dict:
    """Rule 73: for each entry two or more listings were read as, whether the listings of it this part ran alone
    got the same configuration; those that differ listed; listings written the same counted apart."""
    configurations = configurations_alone(alone)
    check = {"entries": 0, "written_the_same_only": 0, "compared": 0, "the_same": 0, "differ": [],
             "not_all_in_this_part": 0}
    for same in listings["read_as_the_same_entry"]:
        check["entries"] += 1
        add_an_entry_checked(check, same, configurations)
    return check


def configurations_alone(alone: list) -> dict:
    configurations = {}
    for entry in alone:
        configurations[entry["listing"]] = configuration_of(entry)
    return configurations


def configuration_of(entry: dict) -> dict:
    """Rule 73: what is compared: accepted alone or not, the context, N, the bodies, the role."""
    configuration = {}
    configuration["accepted_alone"] = entry["accepted_alone"]
    configuration["context"] = entry.get("context")
    configuration["N"] = entry["N"]
    configuration["bodies"] = None
    if entry["bodies"] is not None:
        configuration["bodies"] = sorted(entry["bodies"])
    configuration["role"] = entry.get("role")
    return configuration


def add_an_entry_checked(check: dict, same: dict, configurations: dict) -> None:
    texts = []
    for described in same["listings"]:
        add_new(texts, described["listing"])
    present = []
    for text in texts:
        if text in configurations:
            present.append(text)
    if len(texts) == 1:
        check["written_the_same_only"] += 1
    elif len(present) < len(texts):
        check["not_all_in_this_part"] += 1
    if len(present) >= 2:
        add_a_comparison(check, same, present, configurations)


def add_a_comparison(check: dict, same: dict, present: list, configurations: dict) -> None:
    check["compared"] += 1
    first = configurations[present[0]]
    differing = []
    for text in present[1:]:
        if configurations[text] != first:
            differing.append(text)
    if len(differing) == 0:
        check["the_same"] += 1
    else:
        entry = {"entry": same["entry"], "configurations": {}}
        for text in present:
            entry["configurations"][text] = configurations[text]
        check["differ"].append(entry)


def classifications_of_the_groups(accepted: dict, runs: dict) -> list:
    by_group = arrangements_by_group(accepted["arrangements"])
    places = read_json(READER_PLACES)["by_listing"]
    classifications = []
    for group in accepted["groups"]:
        if group["family"] != "alone":
            classifications.append(classification_of_a_group(group, by_group.get(group["group"], []),
                                                              accepted["search"].get(group["group"], {}),
                                                              runs["results"], places))
    return classifications


def arrangements_by_group(arrangements: list) -> dict:
    by_group = {}
    for arrangement in arrangements:
        add_to_a_list(by_group, arrangement["group"], arrangement)
    return by_group


def classification_of_a_group(group: dict, arrangements: list, search: dict, results: dict, places: dict) -> dict:
    """Rules 23 to 26, 54 and 55, for one group; rule 69: the reader's places; rule 70: a declaration's scope."""
    kept = kept_of(arrangements)
    components = group["components"]
    classification = {}
    classification["group"] = group["group"]
    classification["family"] = group["family"]
    classification["listings"] = group["listings"]
    classification["dependent"] = group.get("dependent")
    classification["holders"] = group.get("holders", [])
    classification["also_for"] = group["also_for"]
    classification["constants"] = group["constants"]
    classification["components"] = names_of(components)
    classification["letters"] = letters_of_the_group(group)
    classification["inert_calls"] = group["inert_calls"]
    classification["search"] = search
    classification["whole_arrangements_asked"] = len(arrangements)
    classification["kept"] = len(kept)
    classification["refused"] = len(arrangements) - len(kept)
    classification["first_errors"] = first_errors_tallied(arrangements)
    classification["holds_a_body"] = holding_of_each(components, kept)
    classification["right_after"] = right_after_each(components, kept)
    classification["where_each_stands"] = where_each_stands(stand_components(group), components, kept)
    classification["signal_2"] = signal_2_by_place(kept, results)
    classification["kept_arrangements"] = short_forms(kept, results)
    classification["the_readers_places"] = readers_places_of_a_group(group, len(kept), places)
    classification["declaration"] = declaration_scope_of_a_group(group, kept, classification["first_errors"])
    classification["run_as"] = runs_as_counted(kept)
    return classification


def runs_as_counted(kept: list) -> dict:
    """Rule 67: the kept arrangements run as their label table variant."""
    counted = {}
    for arrangement in kept:
        if "run_as" in arrangement:
            add_one(counted, arrangement["run_as"])
    return counted


# Rule 69 : the reader's places, as the places each group's dependent is expected in


def readers_places_of_a_group(group: dict, kept: int, places: dict) -> dict:
    """Rule 69: the reader's places for the group's dependent against the kinds of its holders; the reader expects
    the dependent kept when a holder's kind is one of its places, or always for one placed by a rule over the
    whole function; whether the kept arrangements match."""
    dependent = group.get("dependent")
    entry = {"dependent": dependent, "places": None, "holder_kinds": [], "expected": "no dependent in the group",
             "kept": kept, "matches": None}
    if dependent is not None and dependent in places:
        entry["places"] = places[dependent]["places"]
        entry["holder_kinds"] = holder_kinds_of(group)
        entry["expected"] = expected_by_the_reader(entry["places"], entry["holder_kinds"])
        entry["matches"] = (entry["expected"] == "kept") == (kept > 0)
    return entry


def holder_kinds_of(group: dict) -> list:
    kinds = []
    for text in group.get("holders", []):
        kinds.append(kind_of_a_holder(text))
    return kinds


def expected_by_the_reader(places, kinds: list) -> str:
    expected = "refused"
    if places is None or shares_one(kinds, places):
        expected = "kept"
    return expected


# Rule 70 : a jump into a declaration's scope


def declaration_scope_of_a_group(group: dict, kept: list, first_errors: list):
    """Rule 70: in a group with a declaration, the kept arrangements where a jump enters its scope, beside what
    C's rule says, and the refusals that name a jump."""
    entry = None
    if group.get("declaration") is not None:
        declaration = declaration_named(group["declaration"])
        entry = {}
        entry["declaration"] = group["declaration"]
        entry["C_says_a_jump_into_its_scope_is"] = declaration["a_jump_into_its_scope"]
        entry["kept"] = len(kept)
        entry["kept_with_a_jump_into_its_scope"] = kept_jumping_in(kept, declaration["name"])
        entry["refused_naming_a_jump"] = refused_naming_a_jump(first_errors)
    return entry


def kept_jumping_in(kept: list, name: str) -> int:
    count = 0
    for arrangement in kept:
        if a_jump_enters(arrangement, name):
            count += 1
    return count


def a_jump_enters(arrangement: dict, name: str) -> bool:
    """A `goto(m)` outside the declaration's scope to an `m:` in it, or a `switch(a)` to a `case(a)` in it."""
    lines = arrangement["lines"]
    levels = arrangement["levels"]
    at = index_of(lines, name)
    end = end_of_its_scope(levels, at)
    enters = False
    for source, target in jumps_of(lines):
        if at < target < end and not at < source < end:
            enters = True
    return enters


def end_of_its_scope(levels: list, at: int) -> int:
    """The first line after a declaration that stands outside the body it is declared in."""
    end = len(levels)
    for later in range(len(levels) - 1, at, -1):
        if levels[later] < levels[at]:
            end = later
    return end


def jumps_of(lines: list) -> list:
    jumps = []
    for source_name, target_name in (("goto(m)", "m:"), ("switch(a)", "case(a)")):
        source = index_of(lines, source_name)
        target = index_of(lines, target_name)
        if source >= 0 and target >= 0:
            jumps.append((source, target))
    return jumps


def refused_naming_a_jump(first_errors: list) -> dict:
    named = {}
    for entry in first_errors:
        if entry["error"].startswith("cannot jump"):
            named[entry["error"]] = entry["refused"]
    return named


def letters_of_the_group(group: dict) -> dict:
    """Rule 60: each component's letter in the short form."""
    letters = {}
    for token in range(len(group["type_copies"])):
        letters[SHORT_COMPONENT_LETTERS[token]] = names_of(group["type_copies"][token])
    return letters


def kept_of(arrangements: list) -> list:
    kept = []
    for arrangement in arrangements:
        if arrangement["accepted"]:
            kept.append(arrangement)
    return kept


def first_errors_tallied(arrangements: list) -> list:
    """Each first error of the refused arrangements, by clang's message, the most common first."""
    counts = {}
    refused = 0
    for arrangement in arrangements:
        if not arrangement["accepted"]:
            refused += 1
            add_one(counts, arrangement["first_error"] or "(no error line)")
    tallied = first_error_entries(counts, refused)
    return tallied


def first_error_entries(counts: dict, refused: int) -> list:
    """Each message with its count; rule 72: and its sort."""
    entries = []
    for message in counts:
        entry = {}
        entry["error"] = message
        entry["refused"] = counts[message]
        entry["out_of"] = refused
        entry["sort"] = sort_of(message)
        entries.append(entry)
    entries.sort(key=most_refused_first)
    return entries


def most_refused_first(entry: dict) -> tuple:
    order = (-entry["refused"], entry["error"])
    return order


def holding_of_each(components: list, kept: list) -> list:
    """Rule 24."""
    holding = []
    for component in components:
        if component["holds_a_body"]:
            holding.append(holding_of(component, kept))
    return holding


def holding_of(component: dict, kept: list) -> dict:
    holding_lines = 0
    for arrangement in kept:
        index = index_of(arrangement["lines"], component["component"])
        if holds_lines(arrangement["levels"], index):
            holding_lines += 1
    entry = {}
    entry["component"] = component["component"]
    entry["listing"] = component["listing"]
    entry["kept_holding_lines"] = holding_lines
    entry["kept_holding_nothing"] = len(kept) - holding_lines
    entry["out_of_kept"] = len(kept)
    return entry


def right_after_each(components: list, kept: list) -> list:
    """Rule 25."""
    pairs = []
    for first in components:
        add_pairs_starting_with(pairs, first, components, kept)
    return pairs


def add_pairs_starting_with(pairs: list, first: dict, components: list, kept: list) -> None:
    for then in components:
        if then is not first:
            pairs.append(right_after_pair(first, then, kept))


def right_after_pair(first: dict, then: dict, kept: list) -> dict:
    count = 0
    for arrangement in kept:
        if comes_right_after(arrangement, first, then):
            count += 1
    pair = {}
    pair["first"] = first["component"]
    pair["then"] = then["component"]
    pair["first_listing"] = first["listing"]
    pair["then_listing"] = then["listing"]
    pair["kept"] = count
    pair["out_of_kept"] = len(kept)
    pair["must"] = in_every(count, len(kept))
    return pair


def comes_right_after(arrangement: dict, first: dict, then: dict) -> bool:
    lines = arrangement["lines"]
    index = index_of(lines, first["component"])
    after = line_right_after(lines, arrangement["levels"], index)
    right_after = line_name(after) == then["component"]
    return right_after


def in_every(count: int, whole: int) -> bool:
    every = False
    if whole > 0 and count == whole:
        every = True
    return every


def stand_components(group: dict) -> list:
    """Rule 54: the components of the group's dependents and of what they need; else, as rule 26, those that hold nothing."""
    texts = dependents_and_needs(group["dependents"])
    stand = []
    for component in group["components"]:
        if component["listing"] in texts or component.get("kind") == "DeclStmt" or \
                (len(texts) == 0 and not component["holds_a_body"]):
            stand.append(component)
    return stand


def dependents_and_needs(dependents: list) -> list:
    texts = list(dependents)
    for dependent in dependents:
        add_all(texts, NEEDS.get(dependent, []))
    return texts


def where_each_stands(stand: list, components: list, kept: list) -> list:
    """Rules 26 and 54."""
    places = []
    for component in stand:
        places.append(where_it_stands(component, components, kept))
    return places


def where_it_stands(component: dict, components: list, kept: list) -> dict:
    entry = {}
    entry["component"] = component["component"]
    entry["listing"] = component["listing"]
    entry["out_of_kept"] = len(kept)
    entry["inside_and_level"] = inside_and_level_tallied(component, kept)
    entry["only_inside"] = inside_in_every(component, kept)
    entry["before_and_after"] = before_and_after_each(component, components, kept)
    return entry


def inside_and_level_tallied(component: dict, kept: list) -> list:
    counts = {}
    for arrangement in kept:
        index = index_of(arrangement["lines"], component["component"])
        around = names_around(arrangement, index)
        key = (tuple(around), arrangement["levels"][index])
        add_one(counts, key)
    tallied = inside_and_level_entries(counts, len(kept))
    return tallied


def inside_and_level_entries(counts: dict, whole: int) -> list:
    entries = []
    for key in counts:
        entry = {}
        entry["inside"] = list(key[0])
        entry["level"] = key[1]
        entry["kept"] = counts[key]
        entry["out_of_kept"] = whole
        entries.append(entry)
    entries.sort(key=most_kept_first)
    return entries


def most_kept_first(entry: dict) -> tuple:
    order = (-entry["kept"], entry["level"], " ".join(entry["inside"]))
    return order


def inside_in_every(component: dict, kept: list) -> list:
    """The components it stands inside in every kept arrangement."""
    every = None
    for arrangement in kept:
        index = index_of(arrangement["lines"], component["component"])
        around = names_around(arrangement, index)
        every = in_both(every, around)
    if every is None:
        every = []
    return every


def in_both(every, around: list) -> list:
    both = []
    if every is None:
        add_all(both, around)
    else:
        add_those_in(both, every, around)
    return both


def add_those_in(both: list, every: list, around: list) -> None:
    for name in every:
        if name in around:
            both.append(name)


def before_and_after_each(component: dict, components: list, kept: list) -> list:
    entries = []
    for other in components:
        if other is not component:
            entries.append(before_and_after(component, other, kept))
    return entries


def before_and_after(component: dict, other: dict, kept: list) -> dict:
    before = 0
    after = 0
    for arrangement in kept:
        here = index_of(arrangement["lines"], component["component"])
        there = index_of(arrangement["lines"], other["component"])
        if there < here:
            before += 1
        if there > here:
            after += 1
    entry = {}
    entry["other"] = other["component"]
    entry["kept_with_it_before"] = before
    entry["kept_with_it_after"] = after
    entry["out_of_kept"] = len(kept)
    return entry


# Rule 55: signal 2 in the groups


READING_WORDS = {
    "t": "tested",
    "n": "never",
    "b": "behind the branch",
    "a": "again",
    "x": "behind the branch and again",
    "o": "once",
}


def signal_2_by_place(kept: list, results: dict) -> list:
    tally = {}
    for arrangement in kept:
        result = results.get(identity_of(arrangement))
        if result is not None and result["not_run"] is None:
            add_places_of(tally, arrangement, result["readings"])
    entries = place_entries(tally)
    return entries


def add_places_of(tally: dict, arrangement: dict, readings: str) -> None:
    for index in range(len(arrangement["lines"])):
        line = arrangement["lines"][index]
        numbers = arrangement["numbers"][index]
        if is_inert_call(line):
            add_reading(tally, place_of_a_line(arrangement, index), readings[numbers[0]])
        else:
            add_value_readings(tally, line, numbers, readings)


def add_value_readings(tally: dict, line: dict, numbers: list, readings: str) -> None:
    values = inert_values_of(line)
    for position in range(len(values)):
        add_reading(tally, f"taken by {line['component']} ({values[position]})", readings[numbers[position]])


def add_reading(tally: dict, place: str, letter: str) -> None:
    if place not in tally:
        tally[place] = {}
    add_one(tally[place], READING_WORDS[letter])


def place_of_a_line(arrangement: dict, index: int) -> str:
    """Rule 55: inside which components, and after which component that holds nothing in the same body."""
    around = names_around(arrangement, index)
    place = "at the top"
    if len(around) > 0:
        place = "inside " + " > ".join(around)
    after = holding_nothing_before_it(arrangement, index)
    if after is not None:
        place = place + ", after " + after
    return place


def holding_nothing_before_it(arrangement: dict, index: int):
    lines = arrangement["lines"]
    levels = arrangement["levels"]
    found = None
    for earlier in range(index - 1, -1, -1):
        if levels[earlier] < levels[index]:
            break
        if found is None and levels[earlier] == levels[index] and is_a_component_holding_nothing(lines[earlier]):
            found = lines[earlier]["component"]
    return found


def is_a_component_holding_nothing(line: dict) -> bool:
    holding_nothing = not is_inert_call(line) and not line["holds_a_body"]
    return holding_nothing


def place_entries(tally: dict) -> list:
    entries = []
    for place in sorted(tally):
        entry = {}
        entry["place"] = place
        entry["readings"] = tally[place]
        entry["out_of"] = sum_of(tally[place])
        entries.append(entry)
    return entries


def sum_of(counts: dict) -> int:
    total = 0
    for key in counts:
        total += counts[key]
    return total


# Rule 60: the short form


def short_forms(kept: list, results: dict) -> list:
    forms = []
    for arrangement in kept:
        forms.append(short_form(arrangement, results.get(identity_of(arrangement))))
    return forms


def short_form(arrangement: dict, result) -> str:
    parts = [short_lines(arrangement["tokens"]), short_levels(arrangement["levels"])]
    if result is not None and result["not_run"] is None:
        parts.append(result["readings"])
        parts.append(outcomes_written(result["outcomes"]))
    short = "|".join(parts)
    return short


def short_lines(tokens: tuple) -> str:
    letters = []
    for token in tokens:
        letters.append(short_letter(token))
    written = "".join(letters)
    return written


def short_letter(token: int) -> str:
    letter = SHORT_INERT_CALL
    if token >= 0:
        letter = SHORT_COMPONENT_LETTERS[token]
    return letter


def short_levels(levels: list) -> str:
    digits = []
    for level in levels:
        digits.append(str(level))
    written = "".join(digits)
    return written


def outcomes_written(outcomes: dict) -> str:
    short = outcomes_in_short(outcomes)
    texts = []
    for letter in "RCESTUL":
        if letter in short:
            texts.append(f"{letter}{short[letter]}")
    written = "".join(texts)
    return written


# Rule 53: each listing alone


def listings_alone(accepted: dict, runs: dict) -> list:
    alone = []
    for arrangement in accepted["arrangements"]:
        if arrangement["alone"]:
            alone.append(alone_entry(arrangement, accepted["listings"], runs["results"]))
    return alone


def alone_entry(arrangement: dict, listings: dict, results: dict) -> dict:
    listing = listings["by_text"][arrangement["group"]]
    result = results.get(arrangement["group"])
    entry = {}
    entry["listing"] = listing["listing"]
    entry["accepted_alone"] = arrangement["accepted"]
    entry["first_error"] = answer_described(answer_of_an_arrangement(arrangement))
    entry["program"] = arrangement.get("asked_program", program_text_of(arrangement))
    entry["parts"] = parts_alone(arrangement, listing, result)
    entry["bodies"] = bodies_of(entry["parts"])
    entry["N"] = len(entry["bodies"])
    entry["traces"] = traces_named(arrangement, result)
    entry["tested_each_alone"] = result is not None and result.get("combined") is False
    entry["not_run"] = why_alone_not_run(arrangement, result, listings)
    if entry["not_run"] is not None:
        entry["bodies"] = None
        entry["N"] = None
    add_the_upgrades_alone(entry, arrangement, listing, result)
    return entry


# Rule 78: each listing's configuration: N, its bodies, and what they come from


def add_the_configurations(alone: list, groups: list, listings: dict) -> None:
    for entry in alone:
        entry["configuration"] = configuration_of_a_listing(entry, listings["by_text"][entry["listing"]], groups)


def configuration_of_a_listing(entry: dict, listing: dict, groups: list) -> dict:
    """Rule 78: a dependent, by signal 1 and the groups; a listing neither run alone nor a dependent has no N.
    Rule 81: a listing run alone by the second reading of 
    component holds it, or when it runs behind the branch or again), the first (signal 2 alone) kept beside it."""
    ran = entry["not_run"] is None
    configuration = configuration_not_run_alone()
    if ran or entry["role"] == "dependent":
        configuration = configuration_held_or_run(entry["parts"], listing["components"], "holds_all")
        add_held_lines_of_the_part(configuration, entry["listing"], groups)
    configuration["from"] = configuration_from(ran, entry["role"])
    configuration["by_signal_2_alone"] = first_reading_of(ran, entry["N"], entry["bodies"])
    configuration["written"] = configuration_in_words(configuration)
    return configuration


def configuration_not_run_alone() -> dict:
    """Rule 78: a listing neither run alone nor a dependent: no N, no bodies."""
    configuration = {}
    configuration["N"] = None
    configuration["bodies"] = None
    configuration["why"] = {}
    configuration["held_by"] = {}
    configuration["held_lines_in_the_groups"] = {}
    configuration["reading"] = SECOND_READING
    return configuration


def configuration_held_or_run(parts: list, components: list, holds_key: str) -> dict:
    """Rules 78 and 81: each part a component of the listing holds is a body, and each part that ran behind the
    branch or again alone (a tested part is not one); each body with why, in the order of the listing's parts."""
    held = held_by_component(components, holds_key)
    configuration = {}
    configuration["N"] = None
    configuration["bodies"] = []
    configuration["why"] = {}
    configuration["held_by"] = held
    configuration["held_lines_in_the_groups"] = {}
    configuration["reading"] = SECOND_READING
    for part in parts:
        add_a_part_held_or_run(configuration, part, held)
    for letter in held:
        add_a_body(configuration, letter, f"held by {held[letter]}; not a part of its run alone")
    configuration["N"] = len(configuration["bodies"])
    return configuration


def held_by_component(components: list, holds_key: str) -> dict:
    """Each letter a component holds, with that component's name (rules 4, 29 and 30)."""
    held = {}
    for component in components:
        for letter in component[holds_key]:
            held[letter] = component["component"]
    return held


def add_a_part_held_or_run(configuration: dict, part: dict, held: dict) -> None:
    reasons = reasons_of_a_part(part, held)
    if len(reasons) > 0:
        add_a_body(configuration, part["letter"], "; ".join(reasons))


def reasons_of_a_part(part: dict, held: dict) -> list:
    """Rule 81: why a part is a body: the component that holds it, how it runs alone, or both; a held part that
    runs otherwise alone says how."""
    reasons = []
    if part["letter"] in held:
        reasons.append(f"held by {held[part['letter']]}")
    if part["reading"] in BODY_READINGS:
        reasons.append(f"runs {part['reading']}")
    elif part["letter"] in held and part["reading"] is not None:
        reasons.append(f"alone it reads {part['reading']}")
    return reasons


def add_a_body(configuration: dict, letter: str, why: str) -> None:
    if letter not in configuration["bodies"]:
        configuration["bodies"].append(letter)
        configuration["why"][letter] = why


def add_held_lines_of_the_part(configuration: dict, text: str, groups: list) -> None:
    """Rule 78: how the lines each holding component holds read in this part's groups."""
    for letter in configuration["held_by"]:
        configuration["held_lines_in_the_groups"][letter] = held_lines_read(configuration["held_by"][letter], text,
                                                                            groups)


def configuration_from(ran: bool, role: str) -> str:
    """Rules 78 and 81: what a listing's N comes from."""
    source = "not run alone"
    if ran:
        source = "signal 1 and signal 2 alone"
    if role == "dependent":
        source = "signal 1 and the groups (a dependent)"
    if role == "dependent" and ran:
        source = "signal 1, the groups and signal 2 alone (a dependent)"
    return source


def first_reading_of(ran: bool, n, bodies) -> dict:
    """Rule 81: the first reading of , kept beside the configuration."""
    first = {}
    first["reading"] = FIRST_READING
    first["N"] = None
    first["bodies"] = None
    if ran:
        first["N"] = n
        first["bodies"] = bodies
    return first


def held_lines_read(name: str, text: str, groups: list) -> dict:
    """The readings, over the groups that hold `text`, of the lines the component `name` holds directly."""
    readings = {}
    for group in groups:
        if text in group["listings"]:
            add_held_readings(readings, group["signal_2"], name)
    return readings


def add_held_readings(readings: dict, places: list, name: str) -> None:
    for entry in places:
        if entry["place"].endswith(f"> {name}") or entry["place"] == f"inside {name}":
            add_counts(readings, entry["readings"])


def configuration_in_words(configuration: dict) -> str:
    """`N = 1 (c)`; `not run alone`."""
    written = "not run alone"
    if configuration["N"] is not None:
        written = f"N = {configuration['N']}"
    if configuration["N"] is not None and len(configuration["bodies"]) > 0:
        written = written + f" ({', '.join(configuration['bodies'])})"
    return written


def add_the_upgrades_alone(entry: dict, arrangement: dict, listing: dict, result) -> None:
    """Rules 63 to 72, for a listing alone: what clang read it as, its context and fill, how it ran."""
    entry["parsed_as"] = listing["parsed_as"]
    entry["detail"] = listing["detail"]
    entry["listed_as"] = listing["listed_as"]
    entry["role"] = listing["role"]
    entry["context"] = listing["context"]
    entry["fill"] = listing["fill"]
    entry["fill_overrides"] = overrides_written(listing["fill_overrides"])
    entry["first_error_sort"] = sort_of_an_answer(answer_of_an_arrangement(arrangement))
    entry["not_accepted"] = listing.get("not_accepted")
    entry["held_or_taken_by"] = listing.get("held_or_taken_by", {})
    entry["tree_sitter_parsed"] = listing["tree_sitter"]["parsed"]
    entry["run_as"] = arrangement.get("run_as")
    if "asked_program" in arrangement:
        entry["run_program"] = program_text_of(arrangement)
    add_how_it_was_built(entry, result)


def add_how_it_was_built(entry: dict, result) -> None:
    """Rules 65, 66 and 71: the stand-ins, the constant, the whole output of a build that failed, the X sets."""
    if result is not None:
        for key in ("stand_ins", "stand_ins_tried", "build_output", "constant_in", "constants_tried", "x_set_runs",
                    "x_set_outcomes"):
            if key in result:
                entry[key] = result[key]


def answer_of_an_arrangement(arrangement: dict) -> dict:
    answer = {}
    answer["accepted"] = arrangement["accepted"]
    answer["line"] = arrangement["first_error_line"]
    answer["message"] = arrangement["first_error"]
    return answer


def parts_alone(arrangement: dict, listing: dict, result) -> list:
    held = held_letters_of(listing)
    names = names_of_the_numbers(arrangement)
    parts = []
    for letter, number in arrangement["own_slots"]:
        parts.append(part_alone(letter, number, letter in held, result, names))
    return parts


def part_alone(letter: str, number: int, is_held: bool, result, names: dict) -> dict:
    part = {}
    part["letter"] = letter
    part["inert_call"] = f"inert_{number}()"
    part["is"] = "a value it takes"
    if is_held:
        part["is"] = "a held statement"
    part["reading"] = None
    part["body"] = None
    if result is not None and result["not_run"] is None:
        part["reading"] = READING_WORDS[result["readings"][number]]
        part["body"] = part["reading"] in BODY_READINGS
    if result is not None and result["not_run"] is None and "readings_with_the_x_sets" in result:
        part["reading_with_the_x_sets"] = READING_WORDS[result["readings_with_the_x_sets"][number]]
        part["ran_under"] = ran_under_of(number, result, names)
    return part


def ran_under_of(number: int, result: dict, names: dict) -> dict:
    """Rule 71: for each inert call varied, the values under which this part ran, those it did not, and those
    whose runs were cut short."""
    by_varied = {}
    for run in result.get("x_set", []):
        varied = names.get(run["number"], f"inert_{run['number']}")
        if varied not in by_varied:
            by_varied[varied] = {"ran": [], "did_not_run": [], "cut_short": []}
        add_a_value_ran_under(by_varied[varied], run, number)
    return by_varied


def add_a_value_ran_under(entry: dict, run: dict, number: int) -> None:
    calls = int(run["counts"][number])
    if calls >= 1:
        entry["ran"].append(run["value"])
    elif run["outcome"][0] in FINISHED_OUTCOMES:
        entry["did_not_run"].append(run["value"])
    else:
        entry["cut_short"].append(f"{run['value']} ({outcome_word(run['outcome'])})")


def bodies_of(parts: list) -> list:
    bodies = []
    for part in parts:
        if part["body"]:
            bodies.append(part["letter"])
    return bodies


def traces_named(arrangement: dict, result) -> dict:
    """Rule 53: the two base runs, each inert call named by its part."""
    names = names_of_the_numbers(arrangement)
    traces = {}
    if result is not None and result["not_run"] is None and "traces" in result:
        for what in result["traces"]:
            traces[what] = trace_named(result["traces"][what], names)
    return traces


def names_of_the_numbers(arrangement: dict) -> dict:
    names = {0: "inert_0 (before)", 1: "inert_1 (after)"}
    for letter, number in arrangement["own_slots"]:
        names[number] = letter
    return names


def trace_named(trace: dict, names: dict) -> str:
    named = []
    for number in trace["trace"] or []:
        named.append(names.get(number, f"inert_{number}"))
    written = " ".join(named) + f" ({outcome_word(trace['outcome'])})"
    return written


def outcome_word(outcome: str) -> str:
    words = {"R": "returned", "C": "cap", "E": "exit", "S": "signal", "T": "timeout", "U": "unknown", "L": "lost"}
    word = words.get(outcome[0], outcome) + outcome[1:]
    return word


def why_alone_not_run(arrangement: dict, result, listings: dict):
    why = why_not_run(arrangement, listings)
    if why is None and result is not None:
        why = result["not_run"]
    return why


# The part's own checks (rule 36)


def checks_of_the_part(accepted: dict, groups: list) -> dict:
    name = part_name(accepted["part"])
    checks = {}
    if name == "step_1_again":
        checks["against_step_1"] = against_step_1_again(accepted)
    if name == "step_1_trimmed":
        checks["against_step_1"] = kept_against_step_1(accepted)
    if name in ("switch_trimmed", "do_trimmed"):
        checks["against_the_untrimmed"] = kept_against_the_untrimmed(groups, name.replace("_trimmed", "_untrimmed"))
    if name == "label_table_pairs":
        checks["depends_on_no_holder"] = depends_on_no_holder(groups, accepted["listings"])
    return checks


def depends_on_no_holder(groups: list, listings: dict) -> dict:
    """Rule 83: in this part's kept pairs no dependent stands only inside a holder, so the groups of two of the
    same and the triples, read from the part pairs alone, miss none of its groups."""
    depended = {}
    for group in groups:
        add_depended_holders(depended, group, listings)
    check = {"depended_holders": depended, "the_same": True}
    for dependent in depended:
        if len(depended[dependent]) > 0:
            check["the_same"] = False
    return check


def step_1_by_arrangement() -> dict:
    by_arrangement = {}
    for entry in read_json(STEP_1_RECORD)["by_arrangement"]:
        by_arrangement[(entry["group"], entry["number"])] = entry
    return by_arrangement


def against_step_1_again(accepted: dict) -> dict:
    """Rule 36: the same programs and the same answers as step 1's record."""
    step_1 = step_1_by_arrangement()
    check = {"arrangements": 0, "programs_the_same": 0, "answers_the_same": 0, "differences": []}
    for arrangement in accepted["arrangements"]:
        compare_with_step_1(check, arrangement, step_1.get((arrangement["group"], arrangement["number"])))
    check["the_same"] = check["programs_the_same"] == check["arrangements"] == check["answers_the_same"] and \
        check["arrangements"] == len(step_1)
    check["step_1_arrangements"] = len(step_1)
    return check


def compare_with_step_1(check: dict, arrangement: dict, entry) -> None:
    check["arrangements"] += 1
    if entry is not None and entry["program"] == arrangement["program_text"]:
        check["programs_the_same"] += 1
    elif len(check["differences"]) < 20:
        check["differences"].append(f"{arrangement['group']} {arrangement['number']}: the program differs")
    if entry is not None and step_1_answer(entry) == (arrangement["accepted"], arrangement["first_error_line"],
                                                       arrangement["first_error"]):
        check["answers_the_same"] += 1
    elif len(check["differences"]) < 20:
        check["differences"].append(f"{arrangement['group']} {arrangement['number']}: the answer differs")


def step_1_answer(entry: dict) -> tuple:
    accepted = entry["clang"] == "accepted"
    line = None
    message = None
    found = None
    if entry["first_error"] is not None:
        found = DIAGNOSTIC.match(entry["first_error"])
    if found is not None:
        line = int(found.group("line"))
        message = found.group("message")
    answer = (accepted, line, message)
    return answer


def kept_against_step_1(accepted: dict) -> dict:
    """Rule 36: the trimmed search keeps step 1's 185 of 820, by levels and lines."""
    step_1 = step_1_kept_keys()
    kept = kept_keys(accepted["arrangements"])
    check = set_comparison(kept, step_1)
    check["the_same"] = check["the_same"] and len(step_1) == EXPECTED_STEP_1_KEPT
    return check


def step_1_kept_keys() -> set:
    keys = set()
    for entry in read_json(STEP_1_RECORD)["by_arrangement"]:
        if entry["clang"] == "accepted":
            keys.add((entry["group"], " ".join(entry["lines"]), tuple(entry["levels"])))
    return keys


def kept_keys(arrangements: list) -> set:
    keys = set()
    for arrangement in arrangements:
        if arrangement["accepted"]:
            keys.add((arrangement["group"], " ".join(notation_of(arrangement["lines"])),
                      tuple(arrangement["levels"])))
    return keys


def set_comparison(these: set, those: set) -> dict:
    check = {}
    check["kept_here"] = len(these)
    check["kept_there"] = len(those)
    check["in_both"] = len(these & those)
    check["only_here"] = len(these - those)
    check["only_there"] = len(those - these)
    check["the_same"] = these == those
    return check


def kept_against_the_untrimmed(groups: list, untrimmed_part: str) -> dict:
    """Rule 36: the trimmed part keeps exactly what the untrimmed one kept."""
    path = PART_FILE.format(untrimmed_part)
    check = {"untrimmed_part": untrimmed_part, "the_same": False, "why": "its record is not there"}
    if os.path.exists(path):
        check = set_comparison(kept_lines_and_levels(groups), kept_lines_and_levels(read_json_gz(path)["groups"]))
        check["untrimmed_part"] = untrimmed_part
    return check


def kept_lines_and_levels(groups: list) -> set:
    keys = set()
    for group in groups:
        for short in group["kept_arrangements"]:
            parts = short.split("|")
            keys.add((group["group"], parts[0], parts[1]))
    return keys


def notation_of(lines: list) -> list:
    """The lines as the owner writes them: inert calls numbered in line order; a
    component that holds a body followed by `:` (`if(a):`), unless its name
    ends in one (`m:`)."""
    notation = []
    next_number = 0
    for line in lines:
        if is_inert_call(line):
            notation.append(INERT_CALL_WRITTEN.format(next_number))
            next_number += 1
        else:
            notation.append(component_notation(line))
    return notation


def component_notation(component: dict) -> str:
    written = component["component"]
    if component["holds_a_body"] and not written.endswith(":"):
        written = written + ":"
    return written


# What was read (rules 28 to 35, 39 and 40)


def reading_of_the_listings(listings: dict) -> dict:
    """Rules 28 to 35, 39 and 40; rule 63: every listing taken, the texts arranged, the listings read as the same
    entry; rule 68: tree-sitter against clang."""
    reading = {}
    reading["listings_parsed_as_written"] = count_parsed_as_written(listings["every_listing"])
    reading["not_parsed_as_written"] = listings["not_parsed_as_written"]
    reading["listings_taken"] = len(listings["every_listing"])
    reading["texts"] = len(listings["by_text"])
    reading["not_taken"] = listings["not_taken"]
    reading["every_listing"] = listings["every_listing"]
    reading["read_as_the_same_entry"] = listings["read_as_the_same_entry"]
    reading["tree_sitter_check"] = listings.get("tree_sitter_check")
    reading["held_or_taken"] = listings["held_or_taken"]
    reading["used"] = len(listings.get("used", []))
    reading["holders"] = listings.get("holders", [])
    reading["dependents"] = listings.get("dependents", [])
    reading["neither"] = listings.get("neither", [])
    reading["refused_alone"] = listings.get("refused_alone", [])
    reading["by_listing"] = listings_described(listings)
    return reading


def count_parsed_as_written(every_listing: list) -> int:
    count = 0
    for described in every_listing:
        if described["parsed_as_written"]:
            count += 1
    return count


def listings_described(listings: dict) -> list:
    described = []
    for text in listings.get("used", []):
        described.append(listing_described(listings["by_text"][text]))
    return described


def listing_described(listing: dict) -> dict:
    entry = {}
    entry["listing"] = listing["listing"]
    entry["kind"] = listing["kind"]
    entry["file"] = listing["file"]
    entry["position"] = listing["position"]
    entry["is_statement"] = listing["is_statement"]
    entry["holders"] = listing["holders"]
    entry["components"] = components_described(listing["components"])
    entry["taken_by_the_lowerer"] = listing["taken_by_the_lowerer"]
    entry["fill"] = listing["fill"]
    entry["fill_answers"] = listing["fill_answers"]
    entry["alone"] = listing["alone"]
    entry["accepted_held_in"] = listing.get("accepted_held_in")
    entry["without_what_it_needs"] = listing.get("without_what_it_needs")
    entry["role"] = listing["role"]
    entry["parsed_as"] = listing["parsed_as"]
    entry["detail"] = listing["detail"]
    entry["parsed_as_written"] = listing["parsed_as_written"]
    entry["listed_as"] = listing["listed_as"]
    entry["context"] = listing["context"]
    entry["fill_overrides"] = listing["fill_overrides"]
    entry["fill_answer_sorts"] = listing["fill_answer_sorts"]
    entry["not_accepted"] = listing.get("not_accepted")
    entry["tree_sitter"] = listing.get("tree_sitter")
    entry["held_or_taken_by"] = listing.get("held_or_taken_by", {})
    return entry


def components_described(components: list) -> list:
    described = []
    for component in components:
        entry = {}
        entry["component"] = component["component"]
        entry["written"] = component["written"]
        entry["takes"] = component["takes"]
        entry["holds"] = component["holds_all"]
        entry["ends_with"] = component["ends_with"]
        described.append(entry)
    return described


# Lines, levels and what holds what


def is_inert_call(line: dict) -> bool:
    inert = line["is"] == "inert call"
    return inert


def is_own_text(line: dict) -> bool:
    own = line["is"] == "own text"
    return own


def holds_a_body(line: dict) -> bool:
    holds = False
    if not is_inert_call(line):
        holds = line["holds_a_body"]
    return holds


def line_name(line) -> str:
    name = ""
    if line is not None and is_inert_call(line):
        name = "inert call"
    if line is not None and not is_inert_call(line):
        name = line["component"]
    return name


def line_names(lines: list) -> list:
    names = []
    for line in lines:
        names.append(line_name(line))
    return names


def names_of(components: list) -> list:
    names = []
    for component in components:
        names.append(component["component"])
    return names


def index_of(lines: list, name: str) -> int:
    found = -1
    for index in range(len(lines)):
        if line_name(lines[index]) == name:
            found = index
            break
    return found


def holds_lines(levels: list, index: int) -> bool:
    """The line after it is one level deeper: it holds at least that line."""
    holds = False
    if index + 1 < len(levels) and levels[index + 1] == levels[index] + 1:
        holds = True
    return holds


def end_of_held_lines(levels: list, index: int) -> int:
    """The first line after line `index` that is not held in it."""
    end = len(levels)
    for later in range(index + 1, len(levels)):
        if levels[later] <= levels[index]:
            end = later
            break
    return end


def line_right_after(lines: list, levels: list, index: int):
    """The line right after line `index`'s held lines, at its level; None when there is none."""
    after = None
    end = end_of_held_lines(levels, index)
    if end < len(lines) and levels[end] == levels[index]:
        after = lines[end]
    return after


def components_around(lines: list, levels: list, index: int) -> list:
    """The components whose held lines line `index` stands in, outermost first."""
    around = []
    level = levels[index]
    for earlier in range(index - 1, -1, -1):
        if levels[earlier] < level:
            around.insert(0, lines[earlier])
            level = levels[earlier]
    return around


def names_around(arrangement: dict, index: int) -> list:
    around = components_around(arrangement["lines"], arrangement["levels"], index)
    names = names_of(around)
    return names


def shares_one(these: list, those: list) -> bool:
    shared = False
    for item in these:
        if item in those:
            shared = True
    return shared


def progress(message: str) -> None:
    print(message, flush=True)


# The record of a part (rules 59, 60 and 62)


def write_the_part(configurations: dict, lowerer: dict, part: str) -> None:
    """Rule 59; rule 74: the small run writes its own record and summary, never a part record."""
    os.makedirs(OUT, exist_ok=True)
    record = part_record(configurations, lowerer, part)
    if part_name(part) == "small_run_upgrades":
        write_the_small_run(record)
    else:
        write_json_gz(PART_FILE.format(file_name_of_the_part(part)), record)
    print_the_part(record)
    stop_when_a_check_fails(record)


# Rule 74: the small run's record, and its table, one row per listing or group


def write_the_small_run(record: dict) -> None:
    """Rule 74: out/small_run_upgrades.json and its summary; log 419's record is read for the table (rule 62)."""
    if os.path.exists(CONFIGURATIONS_FILE):
        record["files_read"].append({"file": relative_to_pchq(CONFIGURATIONS_FILE),
                                     "sha256": sha256_of(CONFIGURATIONS_FILE)})
    record["eye_table"] = eye_table(record, log_419_record())
    write_json(os.path.join(OUT, SMALL_RUN_RECORD), record)
    summary = small_run_summary(record)
    write_text(os.path.join(OUT, SMALL_RUN_SUMMARY), summary)
    progress(summary)


EYE_COLUMNS = [("listing", "listing"), ("rows", "rows of Table 4 it tests"), ("context_and_fill", "context and fill used"),
               ("answer", "clang's answer"), ("parts", "which parts run, for which values"),
               ("configuration", "the configuration it gives"), ("tree_sitter", "tree-sitter agrees?"),
               ("reader", "the reader agrees?"), ("log_419_then_now", "log 419's record -> now")]


def small_run_summary(record: dict) -> str:
    """Rule 74: the small run's summary; every count with its whole."""
    text = []
    add_small_run_heading(text, record)
    add_what_was_chosen(text, record)
    add_the_eye_table(text, record["eye_table"])
    add_the_refusals_by_sort(text, record["refusals_by_sort"])
    add_the_tree_sitter_check(text, record["reading"]["tree_sitter_check"])
    add_the_same_entry_check(text, record["read_as_the_same_entry"])
    add_the_declarations_section(text, record["groups"])
    add_the_places_matched(text, record["groups"])
    add_the_x_sets_of_the_run(text, record["alone"])
    add_the_listings_as_written(text, record["alone"])
    add_the_configurations_section(text, record["alone"])
    text.append("")
    summary = "\n".join(text)
    return summary


def add_small_run_heading(text: list, record: dict) -> None:
    text.append("HiOp_configuration_solver, the small run of : the upgrades of 
                "rows 1 to 8, through every stage, with the fixes after the first small run (rules 75 to 80)")
    text.append(f"lowerer: {record['lowerer']}")
    text.append(f"asked alone: {record['asked_alone']}")
    text.append(f"built: {record['built']}")
    text.append(f"written: {record['written']}")
    text.append("files read:")
    for entry in record["files_read"]:
        text.append(f"   {entry['file']}  sha256 {entry['sha256']}")


def add_what_was_chosen(text: list, record: dict) -> None:
    entries = record["small_run"]["entries"]
    alone = record["alone"]
    accepted = 0
    run = 0
    for entry in alone:
        if entry["accepted_alone"]:
            accepted += 1
        if entry["not_run"] is None:
            run += 1
    text.append("")
    text.append("1. What was chosen, and how it went")
    text.append(f"   listings chosen: {len(entries)} (why each: in the record's small_run)")
    text.append(f"   listings taken by rule 63: {record['reading']['listings_taken']} (parsed as written "
                f"{record['reading']['listings_parsed_as_written']} of {record['reading']['listings_taken']}), "
                f"in {record['reading']['texts']} texts")
    text.append(f"   asked alone: {len(alone)}; accepted alone {accepted} of {len(alone)}; refused alone "
                f"{len(alone) - accepted} of {len(alone)}")
    text.append(f"   run (signal 2): {run} of {len(alone)}; not run {len(alone) - run} of {len(alone)}:")
    for entry in alone:
        if entry["not_run"] is not None:
            text.append(f"      {entry['listing']}: {entry['not_run']}")
    text.append(f"   groups: {len(record['groups'])}; whole arrangements asked "
                f"{count_in_groups(record['groups'], 'whole_arrangements_asked')}, kept "
                f"{count_in_groups(record['groups'], 'kept')} of {count_in_groups(record['groups'], 'whole_arrangements_asked')}")
    text.append(f"   signal 2: {json.dumps(record['signal_2'], sort_keys=True)}")


def add_the_listings_as_written(text: list, alone: list) -> None:
    """Rule 77: each listing not accepted as written, with clang's evidence."""
    found = []
    for entry in alone:
        if entry.get("not_accepted") is not None and entry["not_accepted"]["because"] == LISTING_AS_WRITTEN:
            found.append(entry)
    text.append("")
    text.append(f"9. Listings not accepted as written (rule 77): {len(found)} of {len(alone)} asked alone")
    for entry in found:
        add_one_listing_as_written(text, entry)


def add_one_listing_as_written(text: list, entry: dict) -> None:
    evidence = entry["not_accepted"]["evidence"]
    text.append(f"   {entry['listing']}")
    for message in entry["not_accepted"]["messages"]:
        text.append(f"      {message}")
    text.append(f"      asked again, {evidence['asked']}: {evidence['command']} (exit {evidence['exit']})")
    text.append(f"      clang: {evidence['refusal']}")
    text.append(f"      the note: {evidence['note']}")
    text.append(f"      {evidence['file']}, lines {evidence['lines']}:")
    for line in evidence["text"]:
        text.append(f"         {line}")


def add_the_configurations_section(text: list, alone: list) -> None:
    """Rule 78: each listing's N by what it comes from; each dependent's held parts."""
    by_from = {}
    for entry in alone:
        add_one(by_from, entry["configuration"]["from"])
    text.append("")
    text.append(f"10. Each listing's configuration (rule 78), by what it comes from, of {len(alone)}: "
                f"{json.dumps(by_from, sort_keys=True)}")
    for entry in alone:
        if entry["configuration"]["N"] is None:
            text.append(f"   {entry['listing']}: not run alone ({entry['not_run']})")
        elif entry["role"] == "dependent":
            text.append(f"   {entry['listing']}: {entry['configuration']['written']}, "
                        f"from {entry['configuration']['from']}")


def count_in_groups(groups: list, key: str) -> int:
    count = 0
    for group in groups:
        count += group[key]
    return count


def add_the_eye_table(text: list, rows: list) -> None:
    text.append("")
    text.append(f"2. The table: one row per listing or group ({len(rows)} rows)")
    text.append("")
    headings = []
    rules = []
    for key, heading in EYE_COLUMNS:
        headings.append(heading)
        rules.append("---")
    text.append("| " + " | ".join(headings) + " |")
    text.append("|" + "|".join(rules) + "|")
    for row in rows:
        entries = []
        for key, heading in EYE_COLUMNS:
            entries.append(table_entry_written(row[key]))
        text.append("| " + " | ".join(entries) + " |")


def table_entry_written(value) -> str:
    written = str(value).replace("\n", " ").replace("|", "\\|")
    return written


def add_the_refusals_by_sort(text: list, tally: dict) -> None:
    text.append("")
    text.append("3. Refusals sorted by clang's message (rules 72, 76 and 77)")
    for where in ("whole arrangements", "listings' asks", "builds"):
        whole = sum_of(tally[where])
        parts = []
        for sort in (WHERE_IT_STANDS, TEST_PROGRAM, LISTING_AS_WRITTEN, UNSORTED):
            parts.append(f"{sort} {tally[where].get(sort, 0)} of {whole}")
        text.append(f"   {where}: {'; '.join(parts)}")
    unsorted = tally["unsorted messages"]
    text.append(f"   unsorted messages, for the owner ({len(unsorted)}):")
    for message in most_common_first(unsorted):
        text.append(f"      {unsorted[message]}: {message}")


def add_the_tree_sitter_check(text: list, check) -> None:
    text.append("")
    text.append("4. tree-sitter's C grammar against clang (rule 68)")
    if check is not None:
        whole = check["listings_with_a_held_placeholder"]
        text.append(f"   listings with a placeholder rule 4 reads as held: {whole}; tree-sitter parsed "
                    f"{check['tree_sitter_parsed']} of {whole}, erred on {check['tree_sitter_erred']} of {whole}")
        text.append(f"   asked of clang: {check['asked_of_clang']} of {whole}; checked (tree-sitter parsed, clang asked): "
                    f"{check['checked']}; agree {check['agree']} of {check['checked']}; every listing asked again: "
                    f"{check['asked_every_listing']}")
        for disagreement in check["disagreements"]:
            text.append(f"      differs: {disagreement['letter']} of {disagreement['listing']}: tree-sitter "
                        f"{disagreement['tree_sitter']['read']}, clang {disagreement['clang']}")


def add_the_same_entry_check(text: list, check: dict) -> None:
    text.append("")
    text.append("5. Listings read as the same entry (rules 63 and 73)")
    text.append(f"   entries two or more listings were read as: {check['entries']}; written the same only (one "
                f"configuration by construction): {check['written_the_same_only']} of {check['entries']}; compared in "
                f"this run: {check['compared']} of {check['entries']}; the same configuration {check['the_same']} of "
                f"{check['compared']}; differ {len(check['differ'])} of {check['compared']}")
    for entry in check["differ"]:
        text.append(f"      {entry['entry']}: {json.dumps(entry['configurations'], sort_keys=True)}")


def add_the_declarations_section(text: list, groups: list) -> None:
    text.append("")
    text.append("6. Declarations as components (rule 70)")
    for group in groups:
        if group.get("declaration") is not None:
            entry = group["declaration"]
            text.append(f"   {group['group']}: kept {group['kept']} of {group['whole_arrangements_asked']}; kept with a "
                        f"jump into its scope {entry['kept_with_a_jump_into_its_scope']} of {entry['kept']}; C says such "
                        f"a jump is {entry['C_says_a_jump_into_its_scope_is']}; refused naming a jump: "
                        f"{json.dumps(entry['refused_naming_a_jump'], sort_keys=True)}")


def add_the_places_matched(text: list, groups: list) -> None:
    matched = 0
    compared = 0
    for group in groups:
        if group["the_readers_places"]["matches"] is not None:
            compared += 1
            if group["the_readers_places"]["matches"]:
                matched += 1
    text.append("")
    text.append("7. The reader's places as the expected places (rule 69)")
    text.append(f"   groups with a dependent the reader places: {compared} of {len(groups)}; kept arrangements match "
                f"the reader in {matched} of {compared}")
    for group in groups:
        places = group["the_readers_places"]
        if places["matches"] is False:
            text.append(f"      differs: {group['group']}: the reader expects it {places['expected']}; kept {places['kept']}")


def add_the_x_sets_of_the_run(text: list, alone: list) -> None:
    text.append("")
    text.append("8. The X sets (rule 71): for each listing run alone, each part's values of a varied inert call under "
                "which it did not run")
    for entry in alone:
        if entry.get("x_set_runs", 0) > 0:
            text.append(f"   {entry['listing']}: {entry['x_set_runs']} runs with X set values; "
                        f"{json.dumps(entry.get('x_set_outcomes', {}), sort_keys=True)}")
            add_x_set_lines(text, entry)


def add_x_set_lines(text: list, entry: dict) -> None:
    for part in entry["parts"]:
        for varied in part.get("ran_under", {}):
            values = part["ran_under"][varied]
            tried = len(values["ran"]) + len(values["did_not_run"]) + len(values["cut_short"])
            if len(values["did_not_run"]) > 0 or len(values["cut_short"]) > 0:
                text.append(f"      {part['letter']}, {varied} varied: ran {len(values['ran'])} of {tried}; not run "
                            f"{len(values['did_not_run'])} of {tried}: {', '.join(values['did_not_run'])}; cut short "
                            f"{len(values['cut_short'])} of {tried}: {', '.join(values['cut_short'])}")


def log_419_record() -> dict:
    """The record of , by listing; read, never written here."""
    by_listing = {}
    if os.path.exists(CONFIGURATIONS_FILE):
        for listing in read_json(CONFIGURATIONS_FILE)["listings"]:
            by_listing[listing["listing"]] = listing
    return by_listing


def by_listing_text(entries: list) -> dict:
    found = {}
    for entry in entries:
        found[entry["listing"]] = entry
    return found


def eye_table(record: dict, log_419: dict) -> list:
    """Rule 74: one row per listing chosen, then one per group."""
    alone = by_listing_text(record["alone"])
    described = by_listing_text(record["reading"]["by_listing"])
    bodies = readers_bodies()
    rows = []
    for chosen in record["small_run"]["entries"]:
        rows.append(eye_row_of_a_listing(chosen, alone.get(chosen["listing"]), described.get(chosen["listing"]),
                                         record, bodies, log_419))
    for group in record["groups"]:
        rows.append(eye_row_of_a_group(group, log_419))
    return rows


def eye_row_of_a_listing(chosen: dict, entry, described, record: dict, bodies: dict, log_419: dict) -> dict:
    row = {}
    row["listing"] = listing_written(chosen, described)
    row["rows"] = rows_tested(chosen, entry, described, record)
    row["context_and_fill"] = "not asked alone"
    row["answer"] = "not asked alone"
    row["parts"] = ""
    row["configuration"] = ""
    row["tree_sitter"] = ""
    row["reader"] = ""
    row["log_419_then_now"] = ""
    if entry is not None:
        row["context_and_fill"] = context_and_fill_of(entry)
        row["answer"] = answer_of_a_listing(entry, described)
        row["parts"] = parts_written(entry)
        row["configuration"] = configuration_written(entry, record)
        row["tree_sitter"] = tree_sitter_written(entry)
        row["reader"] = reader_written(entry, described, bodies, record)
        row["log_419_then_now"] = then_and_now(entry, log_419.get(chosen["listing"]))
    return row


def listing_written(chosen: dict, described) -> str:
    written = f"`{chosen['listing']}`"
    if len(chosen["names"]) > 0:
        written = written + " as " + ", ".join(chosen["names"])
    if described is not None and len(described["listed_as"]) > 1:
        written = written + f" (written the same by {len(described['listed_as'])} listings)"
    return written


def rows_tested(chosen: dict, entry, described, record: dict) -> str:
    """The rows of log 421 Table 4 a listing was chosen for, and those its run shows; row 8 shows on every one."""
    rows = list(chosen["rows"])
    if described is not None and (not all_parsed_as_written(described) or in_a_same_entry(chosen["listing"], record)):
        add_new(rows, 1)
    if entry is not None:
        add_rows_its_run_shows(rows, entry)
    add_new(rows, 8)
    rows.sort()
    written = rows_joined(rows)
    return written


def rows_joined(rows: list) -> str:
    texts = []
    for row in rows:
        texts.append(str(row))
    joined = ", ".join(texts)
    return joined


def all_parsed_as_written(described: dict) -> bool:
    every = True
    for listed in described["listed_as"]:
        if not listed["parsed_as_written"]:
            every = False
    return every


def in_a_same_entry(text: str, record: dict) -> bool:
    found = False
    for same in record["reading"]["read_as_the_same_entry"]:
        if text in texts_of_an_entry(same) and len(texts_of_an_entry(same)) > 1:
            found = True
    return found


def texts_of_an_entry(same: dict) -> list:
    texts = []
    for described in same["listings"]:
        add_new(texts, described["listing"])
    return texts


def add_rows_its_run_shows(rows: list, entry: dict) -> None:
    if entry.get("context") not in (None, TODAYS_CONTEXT):
        add_new(rows, 2)
    if "stand_ins" in entry or "stand_ins_tried" in entry or "constant_in" in entry or "constants_tried" in entry:
        add_new(rows, 3)
    if entry.get("run_as") is not None and "label table" in entry["run_as"]:
        add_new(rows, 4)
    if len(entry.get("held_or_taken_by", {})) > 0:
        add_new(rows, 5)
    if entry.get("x_set_runs", 0) > 0:
        add_new(rows, 7)


def context_and_fill_of(entry: dict) -> str:
    written = f"{entry.get('context')}; {entry.get('fill')}"
    if entry.get("fill_overrides"):
        written = written + ", " + entry["fill_overrides"]
    return written


def answer_of_a_listing(entry: dict, described) -> str:
    """clang's answer alone, sorted when refused (rule 72), and how it was built and run."""
    written = "accepted alone"
    if not entry["accepted_alone"]:
        written = f"refused alone ({entry.get('first_error_sort')}): {answer_without_line(entry['first_error'])}"
    if described is not None and described.get("accepted_held_in") is not None:
        written = written + f"; accepted held in `{described['accepted_held_in']}`"
    if entry.get("not_accepted") is not None:
        written = written + "; " + role_not_accepted(entry["not_accepted"])
    if entry.get("not_accepted") is not None and entry["not_accepted"].get("evidence") is not None:
        written = written + " (" + evidence_in_short(entry["not_accepted"]["evidence"]) + ")"
    written = written + "; " + how_it_ran(entry)
    return written


def evidence_in_short(evidence: dict) -> str:
    """Rule 77: the note clang gives, and the lines of the file it names."""
    written = f"clang: {evidence['refusal']}"
    if evidence["note"] is not None:
        written = written + f"; {evidence['note']}"
    if evidence["lines"] is not None:
        written = written + f"; lines {evidence['lines']}: " + " / ".join(evidence["text"])
    return written


def how_it_ran(entry: dict) -> str:
    written = "run"
    if entry["not_run"] is not None:
        written = f"not run: {entry['not_run']}"
    if entry["not_run"] is None and "stand_ins" in entry:
        written = "run, linked with stand-ins for " + ", ".join(entry["stand_ins"])
    if entry["not_run"] is None and "constant_in" in entry:
        written = f"run with {entry['constant_in']} as a constant"
    if entry["not_run"] is None and entry.get("run_as") is not None and "label table" in entry["run_as"]:
        written = "run through the label table"
    return written


def parts_written(entry: dict) -> str:
    """Each part's reading over every run (rule 71), and the values of a varied inert call under which it did not
    run."""
    texts = []
    for part in entry["parts"]:
        texts.append(f"{part['letter']} {part.get('reading_with_the_x_sets', part['reading'])}")
    for part in entry["parts"]:
        add_values_it_did_not_run_under(texts, part)
    written = joined_or(texts, "; ", "no part")
    return written


def joined_or(texts: list, between: str, nothing: str) -> str:
    written = nothing
    if len(texts) > 0:
        written = between.join(texts)
    return written


def add_values_it_did_not_run_under(texts: list, part: dict) -> None:
    for varied in part.get("ran_under", {}):
        values = part["ran_under"][varied]
        tried = len(values["ran"]) + len(values["did_not_run"]) + len(values["cut_short"])
        if len(values["did_not_run"]) > 0:
            texts.append(f"{part['letter']} not run when {varied} = {', '.join(values['did_not_run'])} "
                         f"({len(values['did_not_run'])} of {tried} values)")


def configuration_written(entry: dict, record: dict) -> str:
    """Rule 78: N and the bodies, with what they come from; for a dependent, its held parts as its lines read in
    the groups, and where it was kept."""
    configuration = entry["configuration"]
    written = configuration["written"]
    if configuration["N"] is not None:
        written = written + f", from {configuration['from']}"
    for letter in configuration.get("held_by", {}):
        written = written + (f"; {letter} held by {configuration['held_by'][letter]}, its lines in the groups: "
                             f"{readings_or_none(configuration['held_lines_in_the_groups'][letter])}")
    if entry.get("role") == "dependent":
        written = written + "; " + where_a_dependent_stands(entry["listing"], record)
    return written


def readings_or_none(readings: dict) -> str:
    written = "none"
    if len(readings) > 0:
        written = readings_written(readings)
    return written


def where_a_dependent_stands(dependent: str, record: dict) -> str:
    """For a dependent: the holder kinds of its pair groups that kept it, of its pair groups."""
    kinds = []
    pairs = 0
    for group in record["groups"]:
        if group["family"] == "pair" and group["dependent"] == dependent:
            pairs += 1
            add_kinds_that_kept(kinds, group)
    written = f"kept inside {joined_or(kinds, ', ', 'no holder')} ({len(kinds)} holder kinds kept it, of {pairs} pair groups)"
    return written


def add_kinds_that_kept(kinds: list, group: dict) -> None:
    if group["kept"] > 0:
        for kind in group["the_readers_places"]["holder_kinds"]:
            add_new(kinds, kind)


def tree_sitter_written(entry: dict) -> str:
    """Rule 68: what tree-sitter read for the held placeholders, beside clang where asked."""
    by = entry.get("held_or_taken_by", {})
    written = "no placeholder rule 4 reads as held"
    texts = []
    for letter in by:
        texts.append(f"{letter}: {letter_compared(by[letter], entry.get('tree_sitter_parsed'))}")
    if len(texts) > 0:
        written = "; ".join(texts)
    return written


def letter_compared(by: dict, parsed) -> str:
    written = f"tree-sitter {by['tree_sitter']} ({by['field']}), not checked; used"
    if not parsed:
        written = f"tree-sitter erred; clang {by['clang']}; clang's used"
    if parsed and by["clang"] is not None:
        written = f"tree-sitter {by['tree_sitter']} ({by['field']}), clang {by['clang']}: agree {by['agree']}"
    return written


def reader_written(entry: dict, described, bodies: dict, record: dict) -> str:
    """The reader's N (bodies.json) beside now's; for a dependent, its places against the pair groups (rule 69)."""
    written = "not read by the reader"
    configuration = entry["configuration"]
    if described is not None:
        reader = bodies.get((described["file"], described["position"], described["listing"]))
        if reader is not None and reader.get("read") and configuration["N"] is None:
            written = f"the reader's N {reader['N']}; now not run alone"
        if reader is not None and reader.get("read") and configuration["N"] is not None:
            written = (f"the reader's N {reader['N']}, now {configuration['N']} ({configuration['from']}): "
                       f"agree {reader['N'] == configuration['N']}")
    if entry.get("role") == "dependent":
        written = written + "; " + places_matched(entry["listing"], record)
    return written


def places_matched(dependent: str, record: dict) -> str:
    matched = 0
    groups = 0
    for group in record["groups"]:
        if group["dependent"] == dependent and group["the_readers_places"]["matches"] is not None:
            groups += 1
            if group["the_readers_places"]["matches"]:
                matched += 1
    written = f"its places match the kept arrangements in {matched} of {groups} groups"
    return written


def then_and_now(entry: dict, then) -> str:
    """Log 419's record of the listing beside now's."""
    now = f"N {entry['N']}"
    if entry["not_run"] is not None:
        now = "not run"
    written = f"not in log 419's record (not parsed as written) -> {now}"
    if then is not None:
        written = f"{then_written(then)} -> {now}"
    return written


def then_written(then: dict) -> str:
    alone = then["signal_2"]["alone"]
    written = f"N {alone.get('N')}"
    if alone.get("not_run") is not None:
        written = f"not run ({why_in_short(alone['not_run'])})"
    return written


def eye_row_of_a_group(group: dict, log_419: dict) -> dict:
    row = {}
    row["listing"] = f"group `{group['group']}`"
    row["rows"] = rows_joined(rows_of_a_group(group))
    row["context_and_fill"] = f"{TODAYS_CONTEXT}; each listing's fill"
    row["answer"] = f"kept {group['kept']} of {group['whole_arrangements_asked']} whole arrangements asked; " \
                    f"refused by sort: {json.dumps(sorts_of_the_refused(group), sort_keys=True)}"
    row["parts"] = group_runs_written(group)
    row["configuration"] = group_configuration_written(group)
    row["tree_sitter"] = "-"
    row["reader"] = group_reader_written(group)
    row["log_419_then_now"] = group_then_and_now(group, log_419)
    return row


def rows_of_a_group(group: dict) -> list:
    rows = []
    if group["family"] == "declaration":
        rows.append(6)
    if group["the_readers_places"]["matches"] is not None:
        rows.append(5)
    if len(group.get("run_as", {})) > 0:
        rows.append(4)
    rows.append(8)
    return rows


def sorts_of_the_refused(group: dict) -> dict:
    sorts = {}
    for entry in group["first_errors"]:
        sorts[entry["sort"]] = sorts.get(entry["sort"], 0) + entry["refused"]
    return sorts


def group_runs_written(group: dict) -> str:
    runs = 0
    for place in group["signal_2"]:
        runs += place["out_of"]
    written = f"readings at {len(group['signal_2'])} places, {runs} in all"
    if group.get("declaration") is not None:
        written = written + f"; kept with a jump into the declaration's scope: " \
                            f"{group['declaration']['kept_with_a_jump_into_its_scope']} of {group['kept']}"
    return written


def group_configuration_written(group: dict) -> str:
    written = ""
    for entry in group["where_each_stands"]:
        written = written + f"{entry['component']} only inside: {joined_or(entry['only_inside'], ', ', 'nothing')}; "
    if group.get("declaration") is not None:
        written = written + f"C says a jump into its scope is {group['declaration']['C_says_a_jump_into_its_scope_is']}"
    return written


def group_reader_written(group: dict) -> str:
    places = group["the_readers_places"]
    written = "no dependent the reader places"
    if places["matches"] is not None:
        written = f"the reader expects it {places['expected']} (places {places['places']}, holders " \
                  f"{places['holder_kinds']}); kept {places['kept']}: match {places['matches']}"
    return written


def group_then_and_now(group: dict, log_419: dict) -> str:
    """Log 419's kept count for the same group, from its record of the dependent; not tried for a declaration."""
    written = f"not tried in log 419 (no arrangement held a declaration) -> kept {group['kept']}"
    if group["family"] != "declaration":
        written = f"{kept_in_log_419(group, log_419)} -> kept {group['kept']}"
    return written


def kept_in_log_419(group: dict, log_419: dict) -> str:
    written = "not in log 419's record"
    then = log_419.get(group.get("dependent"))
    if then is not None:
        for where in then["signal_1"]["where_it_stands"]:
            if where["group"] == group["group"]:
                written = f"kept {where['kept']} of {where['of_whole_arrangements_asked']}"
    return written


def file_name_of_the_part(part: str) -> str:
    name = part.replace(":", "_").replace("/", "_of_")
    return name


def part_record(configurations: dict, lowerer: dict, part: str) -> dict:
    record = heading_of(f"HiOp_configuration_solver, part {part}: its groups, kept arrangements and runs", lowerer)
    record["part"] = part
    for key in configurations:
        record[key] = configurations[key]
    return record


def heading_of(what: str, lowerer: dict) -> dict:
    heading = {}
    heading["what"] = what
    heading["plan"] = ("Planning/node_0_0_projects/node_0_0_0_pseudocoup/node_0_0_0_0_pseudoarch/node_0_0_0_0_2_map_HiOp_to_unit/"
                       "node_0_0_0_0_2_4_extract_lang_vocab/node_0_0_0_0_2_4_3_HiOp_configuration_solver (Block A; section 3.1)")
    heading["rules"] = "HiOp_configuration_solver.py, its docstring"
    heading["lowerer"] = lowerer["version"]
    heading["asked_alone"] = " ".join(lowerer["command"]) + " <program>.c (rule 20)"
    heading["asked_in_batches"] = " ".join(lowerer["front_end"]) + " <programs> (rule 46)"
    heading["built"] = " ".join(lowerer["build"]) + " <programs>.c harness.c " + " ".join(GNU_C_LIBRARIES) + " (rule 48)"
    heading["files_read"] = files_read()
    heading["written"] = time.strftime("%Y-%m-%d %H:%M:%S %Z")
    return heading


def files_read() -> list:
    files = []
    for path in (LISTINGS, LABEL_ADDRESS, BUILTINS, HOLDER_CLASSES, READER_PLACES, READER_BODIES, HAND_TABLES,
                 STEP_1_RECORD, os.path.abspath(__file__)):
        files.append({"file": relative_to_pchq(path), "sha256": sha256_of(path)})
    return files


def print_the_part(record: dict) -> None:
    progress(f"part {record['part']}: {len(record['groups'])} groups, {len(record['alone'])} listings alone")
    progress(f"asked: {record['asks']['programs']} programs in {record['asks']['calls']} calls, "
             f"{round(record['asks']['seconds'])} s; asked alone too: {record['asks']['asked_alone']}, "
             f"different: {record['asks']['alone_differs']}; calls asked again one at a time: "
             f"{record['asks']['calls_asked_again_alone']}")
    for group in record["groups"]:
        progress(group_line(group))
    progress(f"signal 2: {json.dumps(record['signal_2'], sort_keys=True)}")
    for name in record["checks"]:
        progress(f"check {name}: {json.dumps(record['checks'][name], sort_keys=True)}")


def group_line(group: dict) -> str:
    search = group["search"]
    line = (f"  {group['group']}: kept {group['kept']} of {group['whole_arrangements_asked']} whole arrangements "
            f"asked")
    if search.get("trimmed"):
        line = line + (f"; prefixes made {search['prefixes_made']}, asked {search['prefixes_asked']}, refused on "
                       f"their own lines {search['refused_on_their_own_lines']}, trimmed {search['prefixes_trimmed']}")
    return line


def stop_when_a_check_fails(record: dict) -> None:
    for name in record["checks"]:
        if not record["checks"][name]["the_same"]:
            stop(f"the check {name} fails: {json.dumps(record['checks'][name], sort_keys=True)}")


# The record (rules 56 to 58, 61 and 62)


RECORD_PARTS = ("listings", "step_1_again", "step_1_trimmed", "switch_untrimmed", "switch_trimmed", "do_untrimmed",
                "do_trimmed", "pairs", "two_of_the_same", "triples", "declarations", "label_table_pairs")
# Rule 82: a record kept beside the one that replaced it, named with the run it came from.
KEPT_RECORD = re.compile(r"_l\d+\.json(\.gz)?$")
# Rule 84: the record this one replaces, kept beside it.
EARLIER_RECORD = re.compile(r"^configurations_l(\d+)\.json$")
COMPARED_FIELDS = ("run alone", "role", "fill", "context", "accepted alone", "N", "N by signal 2 alone", "parts",
                   "groups")
FOR_LISTINGS_WITH_A_START = ("for (a; b; c) d;", "for (a; b;) c;", "for (a; ; b) c;", "for (a; ;) b;")
THE_FOUR_EXPRESSIONS = ("a && b", "a || b", "a ? b : c", "a ?: b")


def write_the_whole_record(lowerer: dict) -> None:
    """Rules 56 to 58, 61 and 62: every part's record read and set together; rule 80: the small run's too."""
    parts = every_part_record()
    configurations = the_record_per_listing(parts, lowerer)
    if "small_run_upgrades" in parts:
        path = os.path.join(OUT, SMALL_RUN_RECORD)
        configurations["files_read"].append({"file": relative_to_pchq(path), "sha256": sha256_of(path)})
    write_json(CONFIGURATIONS_FILE, configurations)
    summary = summary_of(configurations)
    write_text(SUMMARY_FILE, summary)
    progress(summary)


def every_part_record() -> dict:
    """Each out/part_<part>.json.gz; rule 80: and out/small_run_upgrades.json, when it is there; rule 82: never a
    record kept beside the one that replaced it."""
    parts = {}
    for name in sorted(os.listdir(OUT)):
        add_a_part_record(parts, name)
    path = os.path.join(OUT, SMALL_RUN_RECORD)
    if os.path.exists(path):
        record = read_json(path)
        parts[record["part"]] = record
    return parts


def add_a_part_record(parts: dict, file_name: str) -> None:
    if is_a_part_record(file_name):
        record = read_json_gz(os.path.join(OUT, file_name))
        check_the_name_of_a_part_record(record, file_name)
        parts[record["part"]] = record


def is_a_part_record(file_name: str) -> bool:
    """Rule 59; rule 82: a record kept beside the one that replaced it (`part_pairs_l130.json.gz`) is not one."""
    found = file_name.startswith("part_") and file_name.endswith(".json.gz")
    if KEPT_RECORD.search(file_name) is not None:
        found = False
    return found


def check_the_name_of_a_part_record(record: dict, file_name: str) -> None:
    """Rule 82: a part's record is read only under its own name, out/part_<part>.json.gz."""
    own_name = os.path.basename(PART_FILE.format(file_name_of_the_part(record["part"])))
    if own_name != file_name:
        stop(f"the record: {file_name} holds the part {record['part']}, whose record is named {own_name}; "
             f"nothing is written")


def kept_records_left_out() -> list:
    """Rule 82: each part record kept beside the one that replaced it, left out of the record and named in it."""
    left_out = []
    for name in sorted(os.listdir(OUT)):
        if name.startswith("part_") and KEPT_RECORD.search(name) is not None:
            left_out.append(name)
    return left_out


def the_record_per_listing(parts: dict, lowerer: dict) -> dict:
    """Rule 56."""
    groups = every_group(parts)
    record = heading_of("HiOp_configuration_solver: the record per listing (rule 56) and the check (rule 57)",
                        lowerer)
    record["parts"] = parts_described(parts)
    record["reading"] = reading_summarized(parts)
    record["trimming"] = trimming_checked(parts)
    record["step_4"] = step_4_counted(parts)
    record["listings"] = every_listing_record(parts, groups)
    record["configuration_4"] = configuration_4_counted(record["listings"], groups)
    record["check"] = the_check(record["listings"], parts, groups)
    record["for_start"] = the_for_start(record["listings"])
    record["upgrades"] = upgrades_of_the_record(parts, groups)
    record["kept_records_left_out"] = kept_records_left_out()
    record["against_the_earlier_record"] = against_the_earlier_record(record)
    return record


# Rule 84: the record against the record it replaces, listing by listing


def against_the_earlier_record(record: dict) -> dict:
    """Rule 84: the newest out/configurations_l<run>.json beside this record, listing by listing."""
    name = the_earlier_record()
    comparison = {"earlier_record": name, "compared": False}
    if name is not None:
        earlier = read_json(os.path.join(OUT, name))
        comparison = listings_compared(earlier, record)
        comparison["earlier_record"] = name
        comparison["earlier_sha256"] = sha256_of(os.path.join(OUT, name))
        comparison["earlier_written"] = earlier.get("written")
    return comparison


def the_earlier_record():
    """Rule 84: the file name of the newest earlier record kept beside this one; None when there is none."""
    newest = None
    run = -1
    for name in sorted(os.listdir(OUT)):
        found = EARLIER_RECORD.match(name)
        if found is not None and int(found.group(1)) > run:
            newest = name
            run = int(found.group(1))
    return newest


def listings_compared(earlier: dict, record: dict) -> dict:
    before = by_listing_text(earlier["listings"])
    now = by_listing_text(record["listings"])
    comparison = {"compared": True, "listings_before": len(before), "listings_now": len(now), "in_both": 0,
                  "the_same": 0, "differ": {}, "by_listing": [], "only_now": [], "only_before": []}
    for text in now:
        if text not in before:
            comparison["only_now"].append(text)
    for text in before:
        if text in now:
            add_a_listing_compared(comparison, before[text], now[text])
        else:
            comparison["only_before"].append(text)
    return comparison


def add_a_listing_compared(comparison: dict, before: dict, now: dict) -> None:
    comparison["in_both"] += 1
    then = listing_facts(before)
    found = listing_facts(now)
    differing = {}
    for field in COMPARED_FIELDS:
        if then[field] != found[field]:
            differing[field] = {"before": then[field], "now": found[field]}
            add_to_a_list(comparison["differ"], field, now["listing"])
    if len(differing) == 0:
        comparison["the_same"] += 1
    else:
        comparison["by_listing"].append({"listing": now["listing"], "differs": differing})


def listing_facts(listing: dict) -> dict:
    """Rule 84: what is compared of a listing, from a record's own fields: whether it ran alone, its role, fill
    and context, whether clang accepted it alone, N, N by signal 2 alone, each part's reading alone, and how many
    groups hold its components."""
    alone = listing["signal_2"]["alone"]
    ran = alone.get("not_run") is None and alone.get("parts") is not None
    facts = {}
    facts["run alone"] = ran
    facts["role"] = listing.get("role")
    facts["fill"] = listing.get("fill")
    facts["context"] = listing.get("context", TODAYS_CONTEXT)
    facts["accepted alone"] = alone.get("accepted_alone")
    facts["N"] = n_of_a_listing(listing, ran)
    facts["N by signal 2 alone"] = None
    if ran:
        facts["N by signal 2 alone"] = alone.get("N")
    facts["parts"] = readings_by_letter(alone.get("parts") or [])
    facts["groups"] = listing.get("groups")
    return facts


def n_of_a_listing(listing: dict, ran: bool):
    """A record's N for a listing: its configuration's (rules 78 and 81); in a record written before them, signal
    2 alone's, when it ran alone."""
    n = None
    if "configuration" in listing:
        n = listing["configuration"]["N"]
    elif ran:
        n = listing["signal_2"]["alone"].get("N")
    return n


def readings_by_letter(parts: list) -> dict:
    readings = {}
    for part in parts:
        readings[part["letter"]] = part.get("reading")
    return readings


def upgrades_of_the_record(parts: dict, groups: list) -> dict:
    """Rules 63 to 73, from every part's record: every listing taken and what clang read it as, the listings read
    as the same entry, tree-sitter against clang, refusals by sort, the reader's places by group, declarations."""
    upgrades = {}
    upgrades["every_listing"] = latest_of(parts, "reading", "every_listing", [])
    upgrades["read_as_the_same_entry"] = latest_compared(parts)
    upgrades["read_as_the_same_entry_from_part"] = part_of_the_latest_compared(parts)
    upgrades["tree_sitter_check"] = latest_of(parts, "reading", "tree_sitter_check", None)
    upgrades["refusals_by_sort"] = refusals_by_sort_of_the_parts(parts)
    upgrades["the_readers_places"] = places_by_group(groups)
    upgrades["declarations"] = declarations_by_group(groups)
    return upgrades


def latest_of(parts: dict, section, key: str, nothing):
    """Rule 80: the field from the latest part that holds it."""
    found = nothing
    written = ""
    for part in parts:
        holder = parts[part]
        if section is not None:
            holder = parts[part].get(section, {})
        if holder.get(key) is not None and parts[part]["written"] > written:
            found = holder[key]
            written = parts[part]["written"]
    return found


def latest_compared(parts: dict):
    """Rule 85: the check of the listings read as the same entry, from the latest part that compared one (a part
    that ran listings alone: the part listings, or the small run); when none did, the latest part's (rule 80)."""
    found = latest_of(parts, None, "read_as_the_same_entry", None)
    name = part_of_the_latest_compared(parts)
    if name is not None:
        found = parts[name]["read_as_the_same_entry"]
    return found


def part_of_the_latest_compared(parts: dict):
    """Rule 85: the latest part whose check of the listings read as the same entry compared at least one."""
    found = None
    written = ""
    for part in parts:
        check = parts[part].get("read_as_the_same_entry")
        if check is not None and check.get("compared", 0) > 0 and parts[part]["written"] > written:
            found = part
            written = parts[part]["written"]
    return found


def refusals_by_sort_of_the_parts(parts: dict) -> dict:
    tally = {}
    for part in parts:
        tally[part] = parts[part].get("refusals_by_sort")
    return tally


def places_by_group(groups: list) -> dict:
    counted = {"groups": 0, "matched": 0, "differ": []}
    for group in groups:
        places = group.get("the_readers_places")
        if places is not None and places["matches"] is not None:
            counted["groups"] += 1
            add_a_place_matched(counted, group, places)
    return counted


def add_a_place_matched(counted: dict, group: dict, places: dict) -> None:
    if places["matches"]:
        counted["matched"] += 1
    else:
        counted["differ"].append({"group": group["group"], "expected": places["expected"], "kept": places["kept"]})


def declarations_by_group(groups: list) -> list:
    found = []
    for group in groups:
        if group.get("declaration") is not None:
            found.append(group["declaration"])
    return found


def every_group(parts: dict) -> list:
    """Every group of every part but the untrimmed ones, which the trimmed ones repeat (rule 36); the part
    triples whole, when it is there, in place of its slices; rule 80: a group of the same name in two parts, from
    the part written later."""
    by_name = {}
    for part in parts:
        if is_a_part_of_the_record(part, parts):
            add_groups_by_name(by_name, parts[part])
    groups = []
    for name in by_name:
        groups.append(by_name[name])
    return groups


def add_groups_by_name(by_name: dict, record: dict) -> None:
    for group in record["groups"]:
        entry = dict(group)
        entry["part"] = record["part"]
        entry["part_written"] = record["written"]
        if group["group"] not in by_name or by_name[group["group"]]["part_written"] < record["written"]:
            by_name[group["group"]] = entry


def is_a_part_of_the_record(part: str, parts: dict) -> bool:
    """Rule 36; rule 83: a slice of a part is left out when the whole part is there."""
    used = part_name(part) not in ("step_1_again", "switch_untrimmed", "do_untrimmed")
    if ":" in part and part_name(part) in parts:
        used = False
    return used


def parts_described(parts: dict) -> list:
    described = []
    for part in parts:
        described.append(part_described(parts[part]))
    return described


def part_described(record: dict) -> dict:
    entry = {}
    entry["part"] = record["part"]
    entry["written"] = record["written"]
    entry["groups"] = len(record["groups"])
    entry["listings_alone"] = len(record["alone"])
    entry["asks"] = record["asks"]
    entry["search_seconds"] = record["search_seconds"]
    entry["signal_2"] = record["signal_2"]
    entry["checks"] = record["checks"]
    entry["whole_arrangements_asked"] = 0
    entry["kept"] = 0
    for group in record["groups"]:
        entry["whole_arrangements_asked"] += group["whole_arrangements_asked"]
        entry["kept"] += group["kept"]
    return entry


def reading_summarized(parts: dict) -> dict:
    """Rules 28 to 35, 39 and 40, from the part listings."""
    summarized = {}
    if "listings" in parts:
        reading = parts["listings"]["reading"]
        summarized["listings_parsed_as_written"] = reading["listings_parsed_as_written"]
        summarized["not_parsed_as_written"] = len(reading["not_parsed_as_written"])
        summarized["texts"] = reading.get("texts", reading["listings_parsed_as_written"])
        summarized["held_or_taken"] = reading["held_or_taken"]
        summarized["holders"] = reading["holders"]
        summarized["dependents"] = reading["dependents"]
        summarized["neither"] = reading["neither"]
        summarized["fills"] = fills_counted(reading["by_listing"])
        summarized["refused_under_every_int_fill_in_log_416"] = the_twelve(reading["by_listing"])
    return summarized


LOG_416_REFUSED = ("goto *a;", "case a ... b: c;", "case a: b;", "default: a;", "*a", "_Countof a",
                   "__builtin_vectorelements a", "a[b]", "a(b)", "a->m", "a.m", "__builtin_va_arg(a, T)")


def fills_counted(by_listing: list) -> dict:
    counted = {}
    for listing in by_listing:
        add_one(counted, f"{listing['fill']}, {listing['alone'] or 'refused alone under every fill'}")
    return counted


def the_twelve(by_listing: list) -> list:
    """Section 3 of the task: the 12 listings log 416 found refused under every `int` fill."""
    twelve = []
    for listing in by_listing:
        if listing["listing"] in LOG_416_REFUSED:
            twelve.append(twelve_entry(listing))
    return twelve


def twelve_entry(listing: dict) -> dict:
    entry = {}
    entry["listing"] = listing["listing"]
    entry["holders"] = listing["holders"]
    entry["fill"] = listing["fill"]
    entry["alone"] = listing["alone"]
    entry["accepted_held_in"] = listing["accepted_held_in"]
    entry["answers"] = answers_alone_and_held(listing["fill_answers"])
    return entry


def answers_alone_and_held(fill_answers: dict) -> dict:
    """Each answer alone; the answers held in the holders counted, by fill and answer, each of the
    holders asked under that fill."""
    answers = {}
    asked = {}
    for key in fill_answers:
        if key.startswith("held in "):
            fill = key.split(", ")[-1]
            add_one(asked, fill)
            add_one(answers, f"held in a holder, {fill}: {answer_without_line(fill_answers[key])}")
        else:
            answers[key] = fill_answers[key]
    with_wholes = counts_of_holders(answers, asked)
    return with_wholes


def counts_of_holders(answers: dict, asked: dict) -> dict:
    written = {}
    for key in answers:
        if key.startswith("held in a holder, "):
            fill = key[len("held in a holder, "):].split(":")[0]
            written[key] = f"{answers[key]} of {asked[fill]} holders"
        else:
            written[key] = answers[key]
    return written


def answer_without_line(answer: str) -> str:
    plain = re.sub(r"^refused at line \d+: ", "refused: ", answer)
    return plain


def trimming_checked(parts: dict) -> dict:
    """Section 4 of the task: the trimmed search against step 1 and against the untrimmed searches."""
    checked = {}
    for name in ("step_1_again", "step_1_trimmed", "switch_untrimmed", "switch_trimmed", "do_untrimmed", "do_trimmed"):
        if name in parts:
            checked[name] = trimming_entry(parts[name])
    return checked


def trimming_entry(record: dict) -> dict:
    entry = part_described(record)
    entry["searches"] = searches_of(record)
    entry["untrimmed_arrangements"] = 0
    for group in record["groups"]:
        entry["untrimmed_arrangements"] += untrimmed_count_of(group)
    return entry


def untrimmed_count_of(group: dict) -> int:
    """Rules 10 to 12 and 37, counted, not made: each distinct order of the group's components and inert
    calls, copies alike, times each indentation it may take."""
    shape = shape_of_a_group(group)
    memo = {}
    count = completions(tuple(shape["copies"]), group["inert_calls"], -1, False, shape["holds"], memo)
    return count


def shape_of_a_group(group: dict) -> dict:
    holding = holding_names(group)
    shape = {"copies": [], "holds": []}
    for letter in sorted(group["letters"]):
        names = group["letters"][letter]
        shape["copies"].append(len(names))
        shape["holds"].append(plain_name(names[0]) in holding)
    return shape


def holding_names(group: dict) -> list:
    names = []
    for entry in group["holds_a_body"]:
        names.append(plain_name(entry["component"]))
    return names


def completions(left: tuple, inert_left: int, level: int, holds: bool, type_holds: list, memo: dict) -> int:
    """The arrangements that finish a prefix whose last line stands at `level` (-1 before the first line)."""
    key = (left, inert_left, level, holds)
    if key not in memo:
        memo[key] = completions_counted(left, inert_left, level, holds, type_holds, memo)
    count = memo[key]
    return count


def completions_counted(left: tuple, inert_left: int, level: int, holds: bool, type_holds: list,
                        memo: dict) -> int:
    count = 0
    if sum(left) == 0 and inert_left == 0:
        count = 1
    for next_level in levels_after(level, holds):
        count += completions_at_a_level(left, inert_left, next_level, type_holds, memo)
    return count


def levels_after(level: int, holds: bool) -> range:
    deepest = 0
    if level >= 0:
        deepest = level
    if level >= 0 and holds:
        deepest = level + 1
    allowed = range(deepest + 1)
    return allowed


def completions_at_a_level(left: tuple, inert_left: int, level: int, type_holds: list, memo: dict) -> int:
    count = 0
    if inert_left > 0:
        count += completions(left, inert_left - 1, level, False, type_holds, memo)
    for token in range(len(left)):
        if left[token] > 0:
            fewer = left[:token] + (left[token] - 1,) + left[token + 1:]
            count += completions(fewer, inert_left, level, type_holds[token], type_holds, memo)
    return count


def searches_of(record: dict) -> dict:
    searches = {}
    for group in record["groups"]:
        searches[group["group"]] = group["search"]
    return searches


def step_4_counted(parts: dict) -> dict:
    """Rules 41 to 43; rule 83: and the pairs through the label table."""
    counted = {}
    for part in parts:
        if part_name(part) in ("pairs", "two_of_the_same", "triples", "label_table_pairs"):
            counted[part] = step_4_entry(parts[part])
    add_the_slices_together(counted)
    return counted


def add_the_slices_together(counted: dict) -> None:
    """The slices of each part run in slices (the triples; rule 83: the pairs through the label table) added up,
    as one more entry, when there are two or more."""
    for name in SLICED_PARTS:
        add_the_slices_of(counted, name)


def add_the_slices_of(counted: dict, name: str) -> None:
    slices = []
    for part in counted:
        if part.startswith(name + ":"):
            slices.append(counted[part])
    if len(slices) >= 2:
        counted[f"{name}, its slices added up"] = slices_added_up(slices)


def slices_added_up(slices: list) -> dict:
    added = {}
    for name in ("groups", "groups_counted_for", "untrimmed_arrangements", "untrimmed_arrangements_counted_for_each",
                 "whole_arrangements_asked", "kept", "prefixes_asked", "asked_with_the_rest", "prefixes_trimmed"):
        added[name] = 0
        for entry in slices:
            added[name] += entry[name]
    added["asks"] = {"programs": 0, "seconds": 0.0}
    added["first_errors"] = {}
    added["signal_2"] = {"programs_run": 0, "runs": 0, "not_run": 0, "outcomes": {}, "seconds": 0.0}
    for entry in slices:
        add_a_slice(added, entry)
    return added


def add_a_slice(added: dict, entry: dict) -> None:
    added["asks"]["programs"] += entry["asks"]["programs"]
    added["asks"]["seconds"] += entry["asks"]["seconds"]
    add_counts(added["first_errors"], entry["first_errors"])
    for name in ("programs_run", "runs", "not_run", "seconds"):
        added["signal_2"][name] += entry["signal_2"].get(name, 0)
    add_counts(added["signal_2"]["outcomes"], entry["signal_2"].get("outcomes", {}))


def step_4_entry(record: dict) -> dict:
    entry = part_described(record)
    entry["groups_counted_for"] = 0
    entry["untrimmed_arrangements"] = 0
    entry["untrimmed_arrangements_counted_for_each"] = 0
    entry["prefixes_asked"] = 0
    entry["asked_with_the_rest"] = 0
    entry["prefixes_trimmed"] = 0
    entry["first_errors"] = {}
    for group in record["groups"]:
        add_a_step_4_group(entry, group)
    return entry


def add_a_step_4_group(entry: dict, group: dict) -> None:
    entry["groups_counted_for"] += 1 + len(group["also_for"])
    entry["untrimmed_arrangements"] += untrimmed_count_of(group)
    entry["untrimmed_arrangements_counted_for_each"] += untrimmed_count_of(group) * (1 + len(group["also_for"]))
    entry["prefixes_asked"] += group["search"].get("prefixes_asked", 0)
    entry["asked_with_the_rest"] += group["search"].get("asked_with_the_rest", 0)
    entry["prefixes_trimmed"] += group["search"].get("prefixes_trimmed", 0)
    for error in group["first_errors"]:
        entry["first_errors"][error["error"]] = entry["first_errors"].get(error["error"], 0) + error["refused"]


# Configuration 4 (rule 43): a dependent inside a holder, inside the holder it depends on


def configuration_4_counted(listings: list, groups: list) -> list:
    names = component_names_by_listing(listings)
    counted = {}
    for group in groups:
        if group["family"] == "triple":
            add_configuration_4_of_a_group(counted, group, names)
    entries = configuration_4_entries(counted)
    return entries


def component_names_by_listing(listings: list) -> dict:
    names = {}
    for listing in listings:
        names[listing["listing"]] = names_of(listing["components"])
    return names


def add_configuration_4_of_a_group(counted: dict, group: dict, names: dict) -> None:
    dependent = group["dependent"]
    if dependent not in counted:
        counted[dependent] = {"dependent": dependent, "groups": 0, "groups_with_it": 0, "kept": 0, "kept_so": 0}
    entry = counted[dependent]
    kept_so = kept_in_configuration_4(group, names)
    entry["groups"] += 1
    entry["kept"] += group["kept"]
    entry["kept_so"] += kept_so
    if kept_so > 0:
        entry["groups_with_it"] += 1


def kept_in_configuration_4(group: dict, names: dict) -> int:
    """The kept arrangements whose dependent stands inside a component of the holder between, which stands
    inside a component of the holder depended on (read from rule 26's chains)."""
    between = names.get(group["holders"][0], [])
    depended = names.get(group["holders"][1], [])
    first = names.get(group["dependent"], [""])[0]
    count = 0
    for entry in group["where_each_stands"]:
        if entry["component"] == first:
            count += kept_with_the_chain(entry["inside_and_level"], between, depended)
    return count


def kept_with_the_chain(tallied: list, between: list, depended: list) -> int:
    count = 0
    for entry in tallied:
        if between_inside_depended(entry["inside"], between, depended):
            count += entry["kept"]
    return count


def between_inside_depended(chain: list, between: list, depended: list) -> bool:
    found = False
    for outer in range(len(chain)):
        for inner in range(outer + 1, len(chain)):
            if plain_name(chain[outer]) in depended and plain_name(chain[inner]) in between:
                found = True
    return found


def configuration_4_entries(counted: dict) -> list:
    entries = []
    for dependent in counted:
        entries.append(counted[dependent])
    return entries


# Rule 56: each listing


def every_listing_record(parts: dict, groups: list) -> list:
    """Rule 56; rule 80: a listing the small run ran alone, from whichever of it and the part listings was written
    later, its reading and its run alone together; a listing only the small run read, added."""
    records = []
    sources = []
    for name in ("listings", "small_run_upgrades"):
        if name in parts:
            sources.append(parts[name])
    taken = listings_taken_from(sources)
    for text in taken:
        source = taken[text]
        record = listing_record(source["described"], source["alone"], groups)
        record["from_part"] = source["part"]
        records.append(record)
    return records


def listings_taken_from(sources: list) -> dict:
    """Each listing's reading and run alone, from the latest source that ran it alone (the first source, the part
    listings, reads and runs every listing it takes)."""
    taken = {}
    for source in sources:
        alone = alone_by_listing(source["alone"])
        for described in source["reading"]["by_listing"]:
            add_a_listing_taken(taken, described, alone.get(described["listing"]), source)
    return taken


def add_a_listing_taken(taken: dict, described: dict, alone, source: dict) -> None:
    text = described["listing"]
    newer = text in taken and alone is not None and taken[text]["written"] < source["written"]
    if text not in taken or newer:
        taken[text] = {"described": described, "alone": alone, "part": source["part"], "written": source["written"]}


def alone_by_listing(alone: list) -> dict:
    by_listing = {}
    for entry in alone:
        by_listing[entry["listing"]] = entry
    return by_listing


def listing_record(described: dict, alone, groups: list) -> dict:
    record = dict(described)
    holding = groups_holding(described["listing"], groups)
    record["groups"] = len(holding)
    record["signal_1"] = signal_1_of_a_listing(described, holding)
    record["signal_2"] = signal_2_of_a_listing(described, alone, holding)
    record["configuration"] = configuration_of_the_record(record)
    return record


# Rule 78: each listing's configuration, from the record's own fields


def configuration_of_the_record(record: dict) -> dict:
    """Rule 78, from the record's own fields: a dependent, by signal 1 (the parts its components hold) and how
    the lines they hold read in the groups; a listing neither run alone nor a dependent has no N. Rule 81: a
    listing run alone by the second reading too, the first (signal 2 alone) kept beside it."""
    alone = record["signal_2"]["alone"]
    ran = alone.get("not_run") is None and alone.get("parts") is not None
    configuration = configuration_not_run_alone()
    if ran or record["role"] == "dependent":
        configuration = configuration_held_or_run(alone.get("parts") or [], record["components"], "holds")
        add_held_lines_of_the_record(configuration, record)
    configuration["from"] = configuration_from(ran, record["role"])
    configuration["by_signal_2_alone"] = first_reading_of(ran, alone.get("N"), alone.get("bodies"))
    configuration["written"] = configuration_in_words(configuration)
    return configuration


def add_held_lines_of_the_record(configuration: dict, record: dict) -> None:
    """Rule 78: how the lines each holding component holds read in the groups, from the record's own fields."""
    for letter in configuration["held_by"]:
        configuration["held_lines_in_the_groups"][letter] = held_lines_of_the_record(configuration["held_by"][letter],
                                                                                     record)


def held_lines_of_the_record(name: str, record: dict) -> dict:
    readings = {}
    add_held_readings(readings, record["signal_2"]["in_the_groups"], name)
    return readings


def groups_holding(text: str, groups: list) -> list:
    """The groups that hold the listing's components: [group, the listing their components name for it]."""
    holding = []
    for group in groups:
        named = name_in_the_group(group, text)
        if named is not None:
            holding.append([group, named])
    return holding


def name_in_the_group(group: dict, text: str):
    """The listing the group's components name for `text`: itself, or, in a group counted for it
    too (rule 41), the holder written the same."""
    named = None
    if text in group["listings"]:
        named = text
    for entry in group["also_for"]:
        if text in entry["holders"]:
            named = group["holders"][entry["holders"].index(text)]
    return named


def signal_1_of_a_listing(described: dict, holding: list) -> dict:
    signal_1 = {}
    signal_1["holds_a_body"] = holding_summed(described, holding)
    signal_1["right_after"] = right_after_summed(described, holding)
    signal_1["where_it_stands"] = where_it_stands_by_group(described, holding)
    return signal_1


def plain_name(name: str) -> str:
    plain = name
    if name.endswith(", second"):
        plain = name[:-len(", second")]
    return plain


def holding_summed(described: dict, holding: list) -> list:
    summed = []
    for component in described["components"]:
        if len(component["holds"]) > 0:
            summed.append(holding_of_a_component(component["component"], holding))
    return summed


def holding_of_a_component(name: str, holding: list) -> dict:
    entry = {"component": name, "kept_holding_lines": 0, "kept_holding_nothing": 0, "out_of_kept": 0, "groups": 0}
    for group, named in holding:
        for counted in group["holds_a_body"]:
            if counted["listing"] == named and plain_name(counted["component"]) == name:
                entry["kept_holding_lines"] += counted["kept_holding_lines"]
                entry["kept_holding_nothing"] += counted["kept_holding_nothing"]
                entry["out_of_kept"] += counted["out_of_kept"]
                entry["groups"] += 1
    entry["may_hold_nothing"] = may_hold_nothing(entry)
    return entry


def may_hold_nothing(entry: dict) -> str:
    word = "not tried"
    if entry["kept_holding_nothing"] > 0:
        word = "yes"
    elif entry["out_of_kept"] > 0:
        word = "not kept holding nothing in any group"
    return word


def right_after_summed(described: dict, holding: list) -> list:
    """Rule 57c: each pair of the listing's own components, counted over every group that holds both."""
    names = names_of(described["components"])
    summed = []
    for first in names:
        for then in names:
            if first != then:
                summed.append(right_after_of_a_pair(first, then, holding))
    return summed


def right_after_of_a_pair(first: str, then: str, holding: list) -> dict:
    """Counted over copies (rule 37): each copy of `first` in each kept arrangement, with any copy of `then`
    right after it."""
    entry = {"first": first, "then": then, "kept": 0, "out_of_kept": 0, "groups": 0}
    for group, named in holding:
        copies = copies_in_the_group(group, first)
        if copies > 0 and copies_in_the_group(group, then) > 0:
            entry["kept"] += right_after_over_copies(group, first, then, named)
            entry["out_of_kept"] += group["kept"] * copies
            entry["groups"] += 1
    entry["must"] = in_every(entry["kept"], entry["out_of_kept"])
    return entry


def copies_in_the_group(group: dict, name: str) -> int:
    count = 0
    for component in group["components"]:
        if plain_name(component) == name:
            count += 1
    return count


def right_after_over_copies(group: dict, first: str, then: str, named: str) -> int:
    count = 0
    for pair in group["right_after"]:
        if plain_name(pair["first"]) == first and plain_name(pair["then"]) == then and \
                pair["first_listing"] == named and pair["then_listing"] == named:
            count += pair["kept"]
    return count


def where_it_stands_by_group(described: dict, holding: list) -> list:
    """Rule 56: for a dependent, or what one needs, where it was kept in each group."""
    names = names_of(described["components"])
    by_group = []
    for group, named in holding:
        for entry in group["where_each_stands"]:
            if entry["listing"] == named and plain_name(entry["component"]) in names:
                by_group.append(where_entry(group, entry))
    return by_group


def where_entry(group: dict, entry: dict) -> dict:
    where = {}
    where["group"] = group["group"]
    where["family"] = group["family"]
    where["component"] = entry["component"]
    where["kept"] = group["kept"]
    where["of_whole_arrangements_asked"] = group["whole_arrangements_asked"]
    where["only_inside"] = entry["only_inside"]
    where["inside_and_level"] = entry["inside_and_level"]
    where["before_and_after"] = entry["before_and_after"]
    return where


def signal_2_of_a_listing(described: dict, alone, holding: list) -> dict:
    signal_2 = {}
    signal_2["alone"] = alone_described(alone)
    signal_2["in_the_groups"] = places_of_its_components(described, holding)
    return signal_2


def alone_described(alone) -> dict:
    described = {"not_in_the_part_listings": True}
    if alone is not None:
        described = {}
        described["accepted_alone"] = alone["accepted_alone"]
        described["first_error"] = alone["first_error"]
        described["program"] = alone["program"]
        described["parts"] = alone["parts"]
        described["bodies"] = alone["bodies"]
        described["N"] = alone["N"]
        described["traces"] = alone["traces"]
        described["not_run"] = alone["not_run"]
        if alone["not_run"] is not None:
            described["bodies"] = None
            described["N"] = None
        described["tested_each_alone"] = alone["tested_each_alone"]
        add_the_upgrades_described(described, alone)
    return described


def add_the_upgrades_described(described: dict, alone: dict) -> None:
    """Rules 63 to 72, as the part listings kept them for a listing alone."""
    for key in ("context", "fill_overrides", "first_error_sort", "not_accepted", "run_as", "run_program", "stand_ins",
                "stand_ins_tried", "constant_in", "constants_tried", "x_set_runs", "x_set_outcomes", "build_output"):
        if key in alone:
            described[key] = alone[key]


def places_of_its_components(described: dict, holding: list) -> list:
    """Rule 55, for the listing: the values its components take, the lines they hold, and what follows them."""
    names = names_of(described["components"])
    tally = {}
    for group, _named in holding:
        add_places_of_names(tally, group["signal_2"], names)
    places = place_entries(tally)
    return places


def add_places_of_names(tally: dict, places: list, names: list) -> None:
    for entry in places:
        if is_a_place_of(entry["place"], names):
            add_readings(tally, place_without_seconds(entry["place"]), entry["readings"])


def is_a_place_of(place: str, names: list) -> bool:
    found = False
    plain = place_without_seconds(place)
    for name in names:
        if plain.startswith(f"taken by {name} (") or plain.endswith(f"> {name}") or \
                plain == f"inside {name}" or f", after {name}" in plain:
            found = True
    return found


def place_without_seconds(place: str) -> str:
    plain = place.replace(", second", "")
    return plain


def add_readings(tally: dict, place: str, readings: dict) -> None:
    if place not in tally:
        tally[place] = {}
    add_counts(tally[place], readings)


# Rule 57: the check


def the_check(listings: list, parts: dict, groups: list) -> dict:
    check = {}
    check["the_reader_bodies"] = against_the_readers_bodies(listings)
    check["the_reader_places"] = against_the_readers_places(listings, groups)
    check["inert_part_roles"] = against_inert_part_roles(listings)
    check["c_statement_context"] = against_c_statement_context(groups)
    check["c_grammar"] = against_c_grammar(listings)
    check["the_dependents_n"] = the_dependents_n(listings)
    check["the_reader_n"] = the_reader_n(listings)
    check["differences"] = every_difference_of(check)
    return check


# Rule 81: every listing's N, by both readings, against the reader's


def the_reader_n(listings: list) -> dict:
    """Rule 81: every listing's N as its configuration gives it (the second reading of , and
    by signal 2 alone (the first), against the reader's N (bodies.json); counted for the listings run alone and
    for the dependents; each difference named."""
    reader = readers_bodies()
    check = {}
    check["reading"] = SECOND_READING
    check["run_alone"] = new_n_tally()
    check["dependents"] = new_n_tally()
    check["differences"] = []
    check["first_reading_differences"] = []
    for listing in listings:
        found = reader.get((listing["file"], listing["position"], listing["listing"]))
        if found is not None and found.get("read"):
            add_a_listing_n(check, listing, found)
    return check


def new_n_tally() -> dict:
    tally = {"compared": 0, "agree": 0, "first_reading_compared": 0, "first_reading_agree": 0}
    return tally


def add_a_listing_n(check: dict, listing: dict, reader: dict) -> None:
    configuration = listing["configuration"]
    first = configuration["by_signal_2_alone"]
    if first["N"] is not None:
        add_an_n(check["run_alone"], configuration["N"], first["N"], reader["N"])
    if listing["role"] == "dependent":
        add_an_n(check["dependents"], configuration["N"], first["N"], reader["N"])
    if configuration["N"] is not None and configuration["N"] != reader["N"]:
        check["differences"].append(a_difference("N differs, the second reading", listing["listing"],
                                                 readers_n_written(reader), bodies_with_why(configuration)))
    if first["N"] is not None and first["N"] != reader["N"]:
        check["first_reading_differences"].append(a_difference("N differs, the first reading", listing["listing"],
                                                               readers_n_written(reader),
                                                               f"signal 2 alone: N {first['N']} "
                                                               f"({', '.join(first['bodies'])})"))


def add_an_n(tally: dict, n, first_n, readers_n: int) -> None:
    tally["compared"] += 1
    if n == readers_n:
        tally["agree"] += 1
    if first_n is not None:
        tally["first_reading_compared"] += 1
    if first_n is not None and first_n == readers_n:
        tally["first_reading_agree"] += 1


def readers_n_written(reader: dict) -> str:
    written = f"the reader: N {reader['N']} ({', '.join(reader['bodies'])})"
    return written


def bodies_with_why(configuration: dict) -> str:
    """Rule 81: `N 2: b (held by if(a); runs behind the branch), c (...)`."""
    written = f"N {configuration['N']}"
    if len(configuration["bodies"] or []) > 0:
        written = written + ": " + each_body_with_why(configuration)
    return written


def each_body_with_why(configuration: dict) -> str:
    texts = []
    for letter in configuration["bodies"]:
        texts.append(f"{letter} ({configuration['why'].get(letter, '')})")
    written = ", ".join(texts)
    return written


def the_dependents_n(listings: list) -> dict:
    """Rule 78: every dependent's N, as the record's own fields give it (`configuration`), against the
    reader's."""
    reader = readers_bodies()
    check = {"dependents": 0, "given": 0, "agree": 0, "differences": [], "by_dependent": []}
    for listing in listings:
        if listing["role"] == "dependent":
            add_a_dependent_n(check, listing, reader.get((listing["file"], listing["position"], listing["listing"])))
    return check


def add_a_dependent_n(check: dict, listing: dict, reader) -> None:
    configuration = listing["configuration"]
    check["dependents"] += 1
    entry = {"listing": listing["listing"], "N": configuration["N"], "bodies": configuration["bodies"],
             "from": configuration["from"], "the_reader": None}
    if configuration["N"] is not None:
        check["given"] += 1
    if reader is not None and reader.get("read"):
        entry["the_reader"] = f"N {reader['N']} ({', '.join(reader['bodies'])})"
    if reader is not None and reader.get("read") and reader["N"] == configuration["N"]:
        check["agree"] += 1
    elif reader is not None and reader.get("read"):
        check["differences"].append(a_difference("a dependent's N differs", listing["listing"],
                                                 f"the reader: N {reader['N']} ({', '.join(reader['bodies'])})",
                                                 f"the record: {configuration['written']}, from "
                                                 f"{configuration['from']}"))
    check["by_dependent"].append(entry)


def readers_bodies() -> dict:
    """bodies.json, by file, position and listing text (a text comes again for kinds clang did not parse as
    written)."""
    record = read_json(READER_BODIES)
    by_listing = {}
    for file_name in record["by_file"]:
        for entry in record["by_file"][file_name]["listings"]:
            by_listing[(file_name, entry["position"], entry["template"])] = entry
    return by_listing


def a_difference(difference: str, about: str, known: str, found: str) -> dict:
    entry = {}
    entry["difference"] = difference
    entry["about"] = about
    entry["what_is_known"] = known
    entry["the_record"] = found
    return entry


def against_the_readers_bodies(listings: list) -> dict:
    """Rule 57a: each part's `body` and each listing's N, against signal 2 alone."""
    reader = readers_bodies()
    check = {"listings_compared": 0, "parts_compared": 0, "parts_agree": 0, "n_agree": 0, "differences": []}
    for listing in listings:
        compare_bodies(check, listing, reader.get((listing["file"], listing["position"], listing["listing"])))
    return check


def compare_bodies(check: dict, listing: dict, reader) -> None:
    alone = listing["signal_2"]["alone"]
    if reader is None or not reader.get("read"):
        check["differences"].append(a_difference("not read by the reader", listing["listing"],
                                                 "no reading in bodies.json", n_or_not_run_alone(alone)))
    elif alone.get("not_run") is None and alone.get("parts") is not None:
        compare_parts(check, listing, alone, reader)
    elif has_held_lines_read_in_the_groups(listing):
        compare_held_in_the_groups(check, listing, reader)
    else:
        check["differences"].append(a_difference("not run alone", listing["listing"],
                                                 f"the reader: N {reader['N']}, bodies {reader['bodies']}",
                                                 f"not run: {alone.get('not_run')}"))


def n_or_not_run_alone(alone: dict) -> str:
    """Rule 78: `N 2`, or `not run alone`."""
    written = "not run alone"
    if alone.get("N") is not None:
        written = f"N {alone['N']}"
    return written


def has_held_lines_read_in_the_groups(listing: dict) -> bool:
    found = False
    for letter in held_letters_described(listing):
        if held_reading_in_the_groups(letter, listing).startswith("in the groups"):
            found = True
    return found


def held_letters_described(listing: dict) -> list:
    held = []
    for component in listing["components"]:
        add_all(held, component["holds"])
    return held


def compare_held_in_the_groups(check: dict, listing: dict, reader: dict) -> None:
    """A dependent not run alone: each held statement as the lines its component holds read in the groups;
    each other part of the reader's, a value the listing writes as a constant or a name, is no body."""
    check["listings_compared"] += 1
    check["listings_compared_through_the_groups"] = check.get("listings_compared_through_the_groups", 0) + 1
    held = held_letters_described(listing)
    bodies = []
    for part in reader["parts"]:
        found = "a constant or a name, not an inert call"
        if part["letter"] in held:
            found = held_reading_in_the_groups(part["letter"], listing)
        is_a_body = part["letter"] in held and held_lines_read_as_bodies(found)
        if is_a_body:
            bodies.append(part["letter"])
        add_a_part_through_the_groups(check, listing["listing"], part, is_a_body, found)
    add_n_through_the_groups(check, listing["listing"], reader, bodies)


def add_a_part_through_the_groups(check: dict, text: str, part: dict, is_a_body: bool, found: str) -> None:
    check["parts_compared"] += 1
    if part["body"] == is_a_body:
        check["parts_agree"] += 1
    else:
        check["differences"].append(a_difference("a part differs", f"{part['letter']} of {text}",
                                                 f"the reader: {part['place']}, body {part['body']}", found))


def add_n_through_the_groups(check: dict, text: str, reader: dict, bodies: list) -> None:
    if reader["N"] == len(bodies):
        check["n_agree"] += 1
    else:
        check["differences"].append(a_difference("N differs", text,
                                                 f"the reader: N {reader['N']} ({', '.join(reader['bodies'])})",
                                                 f"in the groups: N {len(bodies)} ({', '.join(bodies)})"))


def compare_parts(check: dict, listing: dict, alone: dict, reader: dict) -> None:
    check["listings_compared"] += 1
    readers_parts = parts_by_letter(reader["parts"])
    for part in alone["parts"]:
        check["parts_compared"] += 1
        compare_a_part(check, listing, part, readers_parts.get(part["letter"]))
    if reader["N"] == alone["N"]:
        check["n_agree"] += 1
    else:
        check["differences"].append(a_difference("N differs", listing["listing"],
                                                 f"the reader: N {reader['N']} ({', '.join(reader['bodies'])})",
                                                 f"signal 2 alone: N {alone['N']} ({', '.join(alone['bodies'])})"))


def parts_by_letter(parts: list) -> dict:
    by_letter = {}
    for part in parts:
        by_letter[part["letter"]] = part
    return by_letter


def compare_a_part(check: dict, listing: dict, part: dict, readers) -> None:
    if readers is not None and readers["body"] == part["body"]:
        check["parts_agree"] += 1
    else:
        check["differences"].append(a_difference("a part differs", f"{part['letter']} of {listing['listing']}",
                                                 readers_part_described(readers),
                                                 alone_and_in_the_groups(listing, part)))


def alone_and_in_the_groups(listing: dict, part: dict) -> str:
    """A held statement's reading alone, beside how the lines its component holds read in the groups."""
    found = f"signal 2 alone: {part['reading']}"
    if part["is"] == "a held statement":
        found = found + "; " + held_reading_in_the_groups(part["letter"], listing)
    return found


def readers_part_described(readers) -> str:
    described = "the reader has no such part"
    if readers is not None:
        described = f"the reader: {readers['place']}, body {readers['body']}"
    return described


def against_the_readers_places(listings: list, groups: list) -> dict:
    """Rule 57a: places.json against the pairs and the groups of two of the same."""
    places = read_json(READER_PLACES)["by_listing"]
    check = {"dependents_compared": 0, "differences": [], "by_dependent": []}
    for listing in listings:
        if listing["listing"] in places:
            check["by_dependent"].append(dependent_checked(check, listing, places[listing["listing"]], groups))
    return check


def dependent_checked(check: dict, listing: dict, reader: dict, groups: list) -> dict:
    check["dependents_compared"] += 1
    kinds = kinds_kept_inside_in_the_pairs(listing, groups)
    entry = {}
    entry["listing"] = listing["listing"]
    entry["the_readers_places"] = reader["places"]
    entry["the_readers_needs"] = reader.get("needs_in_the_same_function")
    entry["kinds_it_was_kept_inside_in_every_kept_pair"] = kinds["only_inside"]
    entry["kinds_of_pairs_that_kept_it"] = kinds["kept"]
    entry["without_what_it_needs"] = listing.get("without_what_it_needs")
    entry["one_switch"] = one_switch_rules(listing["listing"], reader, groups)
    add_place_differences(check, listing["listing"], reader, kinds)
    add_one_switch_differences(check, listing["listing"], entry["one_switch"])
    add_may_not_enter_differences(check, listing["listing"], reader)
    return entry


def kinds_kept_inside_in_the_pairs(listing: dict, groups: list) -> dict:
    kinds = {"only_inside": [], "kept": []}
    first = listing["components"][0]["component"]
    for group in groups:
        if group["family"] == "pair" and group["dependent"] == listing["listing"] and group["kept"] > 0:
            add_kinds_of_a_pair(kinds, group, first)
    return kinds


def add_kinds_of_a_pair(kinds: dict, group: dict, first: str) -> None:
    holder_kind = holder_kind_of(group)
    add_new(kinds["kept"], holder_kind)
    for entry in group["where_each_stands"]:
        if entry["component"] == first and len(entry["only_inside"]) > 0:
            add_new(kinds["only_inside"], holder_kind)


def holder_kind_of(group: dict) -> str:
    kind = kind_of_a_holder(group["holders"][0])
    return kind


KIND_OF_A_HOLDER = {}


def kind_of_a_holder(text: str) -> str:
    """The kind of a holder listing, by its text, from kinds_forms.json."""
    if len(KIND_OF_A_HOLDER) == 0:
        for operator in read_json(LISTINGS)["operators"]:
            KIND_OF_A_HOLDER[operator["template"]] = operator["name"]
    kind = KIND_OF_A_HOLDER.get(text, text)
    return kind


def add_new(items: list, item) -> None:
    if item not in items:
        items.append(item)


def add_place_differences(check: dict, text: str, reader: dict, kinds: dict) -> None:
    places = reader["places"] or []
    for kind in places:
        if kind not in kinds["only_inside"]:
            check["differences"].append(a_difference("differs", text, f"the reader lets it stand inside {kind}",
                                                     f"no kept pair with {kind} has it inside in every kept arrangement"))
    for kind in kinds["only_inside"]:
        if kind not in places:
            check["differences"].append(a_difference("differs", text, f"the reader does not place it inside {kind}",
                                                     f"the pairs with {kind} keep it only inside"))


def one_switch_rules(text: str, reader: dict, groups: list) -> list:
    """Rule 57a: each `one_switch` refusal, against the groups of two of the same."""
    rules = []
    for rule in reader.get("one_switch", []):
        rules.append(one_switch_rule_checked(text, rule, groups))
    return rules


def one_switch_rule_checked(text: str, rule: dict, groups: list) -> dict:
    entry = {"refusal": rule["refusal"], "says": rule["says"], "groups": []}
    for group in groups:
        if group["family"] == "two of the same" and group["listings"][0] == text and group["listings"][1] == text:
            entry["groups"].append(two_of_the_same_described(group, rule["says"]))
    return entry


def two_of_the_same_described(group: dict, says: str) -> dict:
    described = {}
    described["group"] = group["group"]
    described["kept"] = group["kept"]
    described["whole_arrangements_asked"] = group["whole_arrangements_asked"]
    described["refused_with_it"] = refused_saying(group, says)
    return described


def refused_saying(group: dict, says: str) -> int:
    start = says.split("%")[0].split("'")[0].strip()
    count = 0
    for error in group["first_errors"]:
        if error["error"].startswith(start):
            count += error["refused"]
    return count


def add_one_switch_differences(check: dict, text: str, rules: list) -> None:
    for rule in rules:
        refused = 0
        for group in rule["groups"]:
            refused += group["refused_with_it"]
        if len(rule["groups"]) == 0 or refused == 0:
            check["differences"].append(a_difference("not shown", text, f"the reader: {rule['refusal']} ({rule['says']})",
                                                     "no group of two of the same was refused with it"))


def add_may_not_enter_differences(check: dict, text: str, reader: dict) -> None:
    for rule in reader.get("may_not_enter", []):
        check["differences"].append(a_difference("not tried", text,
                                                 f"the reader: it may not enter a protected scope ({rule['refusal']})",
                                                 "no arrangement holds a declaration, so none holds a protected scope"))


def against_inert_part_roles(listings: list) -> dict:
    """Rule 57b: INERT_PART_ROLES against each part's reading. Rule 81: and against the configuration's bodies
    (the second reading), counted beside it."""
    roles = hand_table("INERT_PART_ROLES_BY_HAND")
    by_text = {}
    for listing in listings:
        by_text[listing["listing"]] = listing
    check = {"parts_compared": 0, "agree": 0, "differences": [], "agree_by_the_configuration": 0,
             "differences_by_the_configuration": []}
    for text in roles:
        for letter in roles[text]:
            compare_a_role(check, text, letter, roles[text][letter], by_text.get(text))
    return check


def compare_a_role(check: dict, text: str, letter: str, role: str, listing) -> None:
    check["parts_compared"] += 1
    found = what_the_record_says_of(letter, listing)
    if role_agrees(role, found):
        check["agree"] += 1
    else:
        check["differences"].append(a_difference("differs", f"{letter} of {text}",
                                                 f"INERT_PART_ROLES: {role}", found))
    compare_a_role_by_the_configuration(check, text, letter, role, listing, found)


def compare_a_role_by_the_configuration(check: dict, text: str, letter: str, role: str, listing, found: str) -> None:
    """Rule 81: a `body` or `value` part against whether the configuration counts it a body; any other role, or a
    listing with no N, as rule 57b reads it."""
    agrees = role_agrees(role, found)
    says = found
    if listing is not None and role in ("body", "value") and listing["configuration"]["N"] is not None:
        is_a_body = letter in listing["configuration"]["bodies"]
        agrees = is_a_body == (role == "body")
        says = configuration_says_of(letter, listing["configuration"], found)
    if agrees:
        check["agree_by_the_configuration"] += 1
    else:
        check["differences_by_the_configuration"].append(a_difference("differs, by the configuration",
                                                                      f"{letter} of {text}",
                                                                      f"INERT_PART_ROLES: {role}", says))


def configuration_says_of(letter: str, configuration: dict, found: str) -> str:
    says = f"not a body ({found})"
    if letter in configuration["bodies"]:
        says = f"a body ({configuration['why'][letter]})"
    return says


def what_the_record_says_of(letter: str, listing) -> str:
    """A part's reading alone; for a listing not run alone, how the lines its components hold read in the groups."""
    found = "not in the record"
    if listing is not None and letter in NAME_LETTERS:
        found = "a name"
    elif listing is not None and listing["fill"] == "constant" and letter in own_values_of(listing["listing"]) and \
            not is_held_in_the_listing(letter, listing):
        found = "a constant"
    elif listing is not None:
        found = reading_for_a_role(letter, listing)
    return found


def is_held_in_the_listing(letter: str, listing: dict) -> bool:
    held = False
    for component in listing["components"]:
        if letter in component["holds"]:
            held = True
    return held


def reading_for_a_role(letter: str, listing: dict) -> str:
    found = "not run"
    for part in listing["signal_2"]["alone"].get("parts") or []:
        if part["letter"] == letter and part["reading"] is not None:
            found = part["reading"]
    if found == "not run" and is_held_in_the_listing(letter, listing):
        found = held_reading_in_the_groups(letter, listing)
    return found


def held_reading_in_the_groups(letter: str, listing: dict) -> str:
    """The lines the component holding `letter` holds directly, as they read in the groups."""
    holder = None
    for component in listing["components"]:
        if letter in component["holds"]:
            holder = component["component"]
    readings = {}
    for entry in listing["signal_2"]["in_the_groups"]:
        if entry["place"].endswith(f"> {holder}") or entry["place"] == f"inside {holder}":
            add_counts(readings, entry["readings"])
    found = "not run, alone or in a group"
    if len(readings) > 0:
        found = "in the groups, its held lines: " + readings_written(readings)
    return found


def readings_written(readings: dict) -> str:
    texts = []
    for reading in sorted(readings):
        texts.append(f"{reading} {readings[reading]}")
    written = ", ".join(texts)
    return written


def role_agrees(role: str, found: str) -> bool:
    agrees = False
    if role == "name":
        agrees = found == "a name"
    if role == "constant":
        agrees = found == "a constant"
    if role == "body":
        agrees = found in BODY_READINGS or held_lines_read_as_bodies(found)
    if role == "value":
        agrees = found in ("tested", "once", "never")
    return agrees


def held_lines_read_as_bodies(found: str) -> bool:
    bodies = found.startswith("in the groups, its held lines:")
    if bodies:
        bodies = "behind the branch" in found or "again" in found
    return bodies


# Rule 57b: C_STATEMENT_CONTEXT, each context written as the arrangement it is


CONTEXT_TESTS = {
    "BreakStmt": ("break;", "for (;;) a;", "break inside for"),
    "ContinueStmt": ("continue;", "for (;;) a;", "continue inside for"),
    "GotoStmt": ("goto m;", None, "goto(m) before m:, at its level"),
    "IndirectGotoStmt": ("goto *a;", None, "goto*(a) before m:, &&m inside m:"),
    "CaseStmt": ("case a: b;", "switch (a) b;", "case(a) inside switch(a)"),
    "DefaultStmt": ("default: a;", "switch (a) b;", "default inside switch(a), after case(a), which holds break"),
}


def against_c_statement_context(groups: list) -> dict:
    """Rule 57b: each dependent's context in C_STATEMENT_CONTEXT, against the kept arrangements of the groups
    that could hold it. How each context is read as an arrangement is typed here (CONTEXT_TESTS)."""
    contexts = hand_table("C_STATEMENT_CONTEXT_BY_HAND")
    check = {"contexts": [], "differences": []}
    for kind in contexts:
        check["contexts"].append(context_checked(check, kind, contexts[kind], groups))
    return check


def context_checked(check: dict, kind: str, context: str, groups: list) -> dict:
    test = CONTEXT_TESTS.get(kind)
    entry = {"kind": kind, "context": context, "read_as": None, "kept_in_it": 0, "groups_looked_at": 0}
    if test is not None:
        entry["read_as"] = test[2]
        count_kept_in_the_context(entry, kind, test, groups)
    if entry["kept_in_it"] == 0:
        check["differences"].append(a_difference("not kept", kind, f"C_STATEMENT_CONTEXT: {context}",
                                                 f"no kept arrangement reads as {entry['read_as']}"))
    return entry


def count_kept_in_the_context(entry: dict, kind: str, test: tuple, groups: list) -> None:
    for group in groups:
        if group_could_hold(group, test):
            entry["groups_looked_at"] += 1
            entry["kept_in_it"] += kept_in_a_context(kind, group)


def group_could_hold(group: dict, test: tuple) -> bool:
    could = test[0] in group["listings"]
    if test[1] is not None:
        could = could and test[1] in all_holders_of(group)
    if test[0] == "default: a;":
        could = could and "case a: b;" in group["listings"]
    return could


def all_holders_of(group: dict) -> list:
    holders = list(group["listings"])
    for entry in group["also_for"]:
        add_all(holders, entry["holders"])
    return holders


def kept_in_a_context(kind: str, group: dict) -> int:
    count = 0
    for short in group["kept_arrangements"]:
        decoded = decoded_short_form(short, group)
        if in_the_context(kind, decoded):
            count += 1
    return count


def decoded_short_form(short: str, group: dict) -> dict:
    """Rule 60, read back: each line's component name (the k-th copy for the k-th time a letter comes), and levels."""
    parts = short.split("|")
    names = []
    seen = {}
    for letter in parts[0]:
        names.append(decoded_name(letter, group, seen))
    decoded = {"names": names, "levels": digits_of(parts[1])}
    return decoded


def decoded_name(letter: str, group: dict, seen: dict) -> str:
    name = "inert call"
    if letter != SHORT_INERT_CALL:
        copy = seen.get(letter, 0)
        name = group["letters"][letter][copy]
        seen[letter] = copy + 1
    return name


def digits_of(written: str) -> list:
    digits = []
    for digit in written:
        digits.append(int(digit))
    return digits


def in_the_context(kind: str, decoded: dict) -> bool:
    names = decoded["names"]
    levels = decoded["levels"]
    found = False
    if kind in ("BreakStmt", "ContinueStmt"):
        found = directly_inside(names, levels, kind_word(kind), "for")
    if kind == "GotoStmt":
        found = before_at_its_level(names, levels, "goto(m)", "m:")
    if kind == "IndirectGotoStmt":
        found = before_at_its_level(names, levels, "goto*(a)", "m:") and directly_inside(names, levels, "&&m", "m:")
    if kind == "CaseStmt":
        found = directly_inside(names, levels, "case(a)", "switch(a)")
    if kind == "DefaultStmt":
        found = directly_inside(names, levels, "default", "switch(a)") and \
            directly_inside(names, levels, "case(a)", "switch(a)") and \
            directly_inside(names, levels, "break", "case(a)") and \
            names.index("case(a)") < names.index("default")
    return found


def kind_word(kind: str) -> str:
    word = "break"
    if kind == "ContinueStmt":
        word = "continue"
    return word


def directly_inside(names: list, levels: list, inner: str, outer: str) -> bool:
    inside = False
    if inner in names and outer in names:
        index = names.index(inner)
        holder = holder_line(levels, index)
        inside = holder is not None and names[holder] == outer
    return inside


def holder_line(levels: list, index: int):
    found = None
    for earlier in range(index - 1, -1, -1):
        if levels[earlier] < levels[index]:
            found = earlier
            break
    return found


def before_at_its_level(names: list, levels: list, first: str, then: str) -> bool:
    before = False
    if first in names and then in names:
        here = names.index(first)
        there = names.index(then)
        before = here < there and levels[here] == levels[there]
    return before


def against_c_grammar(listings: list) -> dict:
    """Rule 57c: each later component right after what the one before it holds, at its level."""
    check = {"pairs_compared": 0, "must": 0, "differences": []}
    for listing in listings:
        add_grammar_of_a_listing(check, listing)
    return check


def add_grammar_of_a_listing(check: dict, listing: dict) -> None:
    components = listing["components"]
    for number in range(1, len(components)):
        add_grammar_pair(check, listing, components[number - 1]["component"], components[number]["component"])


def add_grammar_pair(check: dict, listing: dict, first: str, then: str) -> None:
    for pair in listing["signal_1"]["right_after"]:
        if pair["first"] == first and pair["then"] == then:
            check["pairs_compared"] += 1
            add_grammar_result(check, listing["listing"], pair)


def add_grammar_result(check: dict, text: str, pair: dict) -> None:
    if pair["must"]:
        check["must"] += 1
    else:
        check["differences"].append(a_difference("differs", f"{pair['first']}, {pair['then']} of {text}",
                                                 f"C's grammar as {text} writes it: {pair['then']} right after what "
                                                 f"{pair['first']} holds, at its level",
                                                 f"right after in {pair['kept']} of {pair['out_of_kept']} kept, "
                                                 f"in {pair['groups']} groups"))


def every_difference_of(check: dict) -> list:
    differences = []
    for name in ("the_reader_bodies", "the_reader_places", "inert_part_roles", "c_statement_context", "c_grammar",
                 "the_dependents_n", "the_reader_n"):
        for difference in check[name]["differences"]:
            entry = dict(difference)
            entry["check"] = name
            differences.append(entry)
    return differences


def the_for_start(listings: list) -> list:
    """Rule 58."""
    starts = []
    for listing in listings:
        if listing["listing"] in FOR_LISTINGS_WITH_A_START:
            starts.append(for_start_entry(listing))
    return starts


def for_start_entry(listing: dict) -> dict:
    entry = {}
    entry["listing"] = listing["listing"]
    entry["alone"] = reading_for_a_role("a", listing)
    entry["in_the_groups"] = {}
    name = listing["components"][0]["component"]
    for place in listing["signal_2"]["in_the_groups"]:
        if place["place"] == f"taken by {name} (a)":
            entry["in_the_groups"] = place["readings"]
    return entry


# The summary (rule 61)


def summary_of(configurations: dict) -> str:
    text = []
    add_summary_heading(text, configurations)
    add_parts_section(text, configurations)
    add_reading_section(text, configurations)
    add_trimming_section(text, configurations)
    add_alone_section(text, configurations)
    add_twelve_section(text, configurations)
    add_step_4_section(text, configurations)
    add_dependents_section(text, configurations)
    add_check_section(text, configurations)
    add_upgrades_section(text, configurations)
    add_bodies_section(text, configurations)
    add_against_the_earlier_record_section(text, configurations)
    text.append("")
    summary = "\n".join(text)
    return summary


def add_upgrades_section(text: list, configurations: dict) -> None:
    """Rules 63 to 73, counted from the record (`upgrades`)."""
    upgrades = configurations.get("upgrades", {})
    text.append("")
    text.append("9. The upgrades of ")
    every = upgrades.get("every_listing", [])
    text.append(f"   listings taken (rule 63): {len(every)}")
    same = upgrades.get("read_as_the_same_entry")
    if same is not None:
        text.append(f"   read as the same entry (rule 73): compared {same['compared']} of {same['entries']}; the same "
                    f"{same['the_same']} of {same['compared']}; differ {len(same['differ'])} of {same['compared']}")
    places = upgrades.get("the_readers_places", {"groups": 0, "matched": 0})
    text.append(f"   the reader's places (rule 69): groups matching {places['matched']} of {places['groups']}")
    for part in upgrades.get("refusals_by_sort", {}):
        text.append(f"   refusals by sort (rule 72), part {part}: "
                    f"{json.dumps(upgrades['refusals_by_sort'][part], sort_keys=True)}")


def add_summary_heading(text: list, configurations: dict) -> None:
    text.append("HiOp_configuration_solver, steps 2 to 4: the owner's method (plan node 0_0_0_0_2_4_4, section 3.1; ")
    text.append(f"lowerer: {configurations['lowerer']}")
    text.append(f"asked alone: {configurations['asked_alone']}")
    text.append(f"asked in batches: {configurations['asked_in_batches']}")
    text.append(f"built: {configurations['built']}")
    text.append("files read:")
    for entry in configurations["files_read"]:
        text.append(f"   {entry['file']}  sha256 {entry['sha256']}")


def add_parts_section(text: list, configurations: dict) -> None:
    text.append("")
    text.append("1. The parts recorded (rule 36), each its own run")
    text.append(f"   {'part':<18} {'groups':>7} {'alone':>6} {'asked':>10} {'s asking':>9} {'whole':>9} "
                f"{'kept':>9} {'programs run':>13} {'runs':>11} {'s running':>10}")
    for part in configurations["parts"]:
        text.append(f"   {part['part']:<18} {part['groups']:>7} {part['listings_alone']:>6} "
                    f"{part['asks']['programs']:>10} {round(part['asks']['seconds']):>9} "
                    f"{part['whole_arrangements_asked']:>9} {part['kept']:>9} "
                    f"{part['signal_2'].get('programs_run', 0):>13} {part['signal_2'].get('runs', 0):>11} "
                    f"{round(part['signal_2'].get('seconds', 0)):>10}")
    text.append("   asked: every program clang was given (prefixes, prefixes with the rest, whole arrangements, "
                "and the reading's questions); whole: the whole arrangements asked; kept: those accepted")


def add_reading_section(text: list, configurations: dict) -> None:
    reading = configurations["reading"]
    text.append("")
    text.append("2. What was read (rules 28 to 35, 39 and 40), from the part listings")
    if len(reading) == 0:
        text.append("   the part listings is not recorded")
    else:
        add_reading_lines(text, reading)


def add_reading_lines(text: list, reading: dict) -> None:
    whole = reading["listings_parsed_as_written"] + reading["not_parsed_as_written"]
    text.append(f"   listings parsed as written: {reading['listings_parsed_as_written']} of {whole}; not: "
                f"{reading['not_parsed_as_written']} of {whole}")
    held = count_read_as(reading["held_or_taken"], "held")
    asked = len(reading["held_or_taken"])
    text.append(f"   held or taken (rule 29): {asked} placeholders asked; held {held} of {asked}; taken "
                f"{asked - held} of {asked}: {taken_written(reading['held_or_taken'])}")
    text.append("   fills (rule 32), each listing by its fill and where the lowerer accepted it:")
    for key in sorted(reading["fills"]):
        text.append(f"      {reading['fills'][key]:>5} of {reading.get('texts', reading['listings_parsed_as_written'])}: {key}")
    text.append(f"   holders (rule 39): {len(reading['holders'])}: {'; '.join(reading['holders'])}")
    text.append(f"   dependents (rule 40): {len(reading['dependents'])}: {'; '.join(reading['dependents'])}")
    text.append(f"   neither, refused alone and held in every holder: {len(reading['neither'])}: "
                f"{'; '.join(reading['neither'])}")


def count_read_as(entries: list, word: str) -> int:
    count = 0
    for entry in entries:
        if entry["read"] == word:
            count += 1
    return count


def taken_written(entries: list) -> str:
    texts = []
    for entry in entries:
        if entry["read"] == "taken":
            texts.append(f"{entry['letter']} of {entry['listing']}")
    written = ", ".join(texts) or "none"
    return written


def add_trimming_section(text: list, configurations: dict) -> None:
    text.append("")
    text.append("3. Trimming's check (rule 38; the plan's section 3.1)")
    for name in configurations["trimming"]:
        entry = configurations["trimming"][name]
        text.append(f"   {name}: whole arrangements asked {entry['whole_arrangements_asked']}, kept {entry['kept']}; "
                    f"programs asked in all {entry['asks']['programs']}, {round(entry['asks']['seconds'])} s asking, "
                    f"{entry['search_seconds']} s in the search")
        for check in entry["checks"]:
            text.append(f"      check {check}: {json.dumps(entry['checks'][check], sort_keys=True)}")
        for group in entry["searches"]:
            text.append(f"      {group}: {json.dumps(entry['searches'][group], sort_keys=True)}")


def add_alone_section(text: list, configurations: dict) -> None:
    text.append("")
    text.append("4. Signal 2, each listing alone (rules 47 to 53)")
    if len(configurations["listings"]) == 0:
        text.append("   the part listings is not recorded")
    else:
        add_alone_lines_of_every_listing(text, configurations)


def add_alone_lines_of_every_listing(text: list, configurations: dict) -> None:
    listings = configurations["listings"]
    run = count_run_alone(listings)
    text.append(f"   listings: {len(listings)}; run {run} of {len(listings)}; not run {len(listings) - run} of "
                f"{len(listings)}, by why:")
    reasons = not_run_reasons(listings)
    for reason in sorted(reasons):
        text.append(f"      {reasons[reason]} of {len(listings) - run}: {reason}")
    outcomes = outcomes_alone(listings)
    text.append(f"   how the runs of the {run} ended, each count of its listings: {json.dumps(outcomes, sort_keys=True)}")
    text.append("   the 8 `for` listings and the 4 expressions, each part's reading alone, its bodies and N:")
    for listing in listings:
        if listing["listing"].startswith("for (") or listing["listing"] in THE_FOUR_EXPRESSIONS:
            add_alone_lines(text, listing)
    text.append("   the `for` start (rule 58):")
    for entry in configurations["for_start"]:
        text.append(f"      {entry['listing']:<18} a alone: {entry['alone']}; in the groups: "
                    f"{readings_written(entry['in_the_groups']) or 'not in a kept arrangement'}")


def count_run_alone(listings: list) -> int:
    count = 0
    for listing in listings:
        if listing["signal_2"]["alone"].get("not_run") is None and \
                listing["signal_2"]["alone"].get("parts") is not None:
            count += 1
    return count


def not_run_reasons(listings: list) -> dict:
    reasons = {}
    for listing in listings:
        why = listing["signal_2"]["alone"].get("not_run")
        if why is not None:
            add_one(reasons, why_in_short(why))
    return reasons


def outcomes_alone(listings: list) -> dict:
    """For each outcome of a base run, the listings with a base run that ended so."""
    outcomes = {}
    for listing in listings:
        for outcome in outcome_letters_of(listing):
            add_one(outcomes, outcome)
    return outcomes


def outcome_letters_of(listing: dict) -> list:
    letters = []
    traces = listing["signal_2"]["alone"].get("traces") or {}
    for what in traces:
        word = traces[what].split("(")[-1].rstrip(")")
        add_new(letters, word)
    return letters


def add_alone_lines(text: list, listing: dict) -> None:
    alone = listing["signal_2"]["alone"]
    parts = []
    for part in alone.get("parts") or []:
        parts.append(f"{part['letter']} ({part['is']}) {part['reading']}")
    text.append(f"      {listing['listing']:<18} {'; '.join(parts)}; bodies {', '.join(alone.get('bodies') or []) or 'none'}; "
                f"{listing['configuration']['written']}")
    for what in alone.get("traces") or {}:
        text.append(f"         {what}: {alone['traces'][what]}")


def add_twelve_section(text: list, configurations: dict) -> None:
    twelve = configurations["reading"].get("refused_under_every_int_fill_in_log_416", [])
    text.append("")
    text.append(f"5. Typed fills: the 12 listings log 416 found refused under every `int` fill ({len(twelve)} of 12 "
                f"read here)")
    for entry in twelve:
        text.append(f"   {entry['listing']:<24} holders {entry['holders']}; fill {entry['fill']}; "
                    f"{entry['alone'] or 'refused alone under every fill'}"
                    f"{held_in_written(entry['accepted_held_in'])}")
        for key in entry["answers"]:
            text.append(f"      {key}: {entry['answers'][key]}")


def held_in_written(holder) -> str:
    written = ""
    if holder is not None:
        written = f" (first accepted held in {holder})"
    return written


def add_step_4_section(text: list, configurations: dict) -> None:
    text.append("")
    text.append("6. Step 4: pairs, two of the same, triples (rules 41 to 43)")
    for part in configurations["step_4"]:
        entry = configurations["step_4"][part]
        text.append(f"   {part}: {entry['groups']} groups arranged, counted for {entry['groups_counted_for']}")
        text.append(f"      arrangements untrimmed {entry['untrimmed_arrangements']} (counted for each group: "
                    f"{entry['untrimmed_arrangements_counted_for_each']}); whole arrangements the trimmed search "
                    f"asked {entry['whole_arrangements_asked']} of {entry['untrimmed_arrangements']}; kept "
                    f"{entry['kept']} of {entry['whole_arrangements_asked']}")
        text.append(f"      prefixes asked {entry['prefixes_asked']}, with the rest {entry['asked_with_the_rest']}, "
                    f"trimmed {entry['prefixes_trimmed']}; programs asked in all {entry['asks']['programs']} in "
                    f"{round(entry['asks']['seconds'])} s")
        refused = entry["whole_arrangements_asked"] - entry["kept"]
        text.append(f"      first errors of the {refused} refused whole arrangements:")
        for error in most_common_first(entry["first_errors"])[:12]:
            text.append(f"         {entry['first_errors'][error]} of {refused}: {error}")
        text.append(f"      signal 2: {json.dumps(entry['signal_2'], sort_keys=True)}")


def most_common_first(counts: dict) -> list:
    pairs = []
    for key in counts:
        pairs.append((-counts[key], key))
    pairs.sort()
    keys = []
    for pair in pairs:
        keys.append(pair[1])
    return keys


def add_dependents_section(text: list, configurations: dict) -> None:
    text.append("")
    text.append("7. Where each dependent was kept (rule 56), against the reader's places (rule 57a)")
    for entry in configurations["check"]["the_reader_places"]["by_dependent"]:
        text.append(f"   {entry['listing']}: the reader: places {entry['the_readers_places']}, needs "
                    f"{json.dumps(entry['the_readers_needs'])}")
        text.append(f"      kept inside in every kept pair, by holder kind: "
                    f"{', '.join(entry['kinds_it_was_kept_inside_in_every_kept_pair']) or 'none'}; pairs that kept it, "
                    f"by holder kind: {', '.join(entry['kinds_of_pairs_that_kept_it']) or 'none'}")
        if entry["without_what_it_needs"] is not None:
            text.append(f"      alone without what it needs: {entry['without_what_it_needs']}")
        for rule in entry["one_switch"]:
            text.append(f"      {rule['refusal']} ({rule['says']}): {json.dumps(rule['groups'])}")
        add_configuration_4_line(text, entry["listing"], configurations)
        add_signal_2_of_a_dependent(text, entry["listing"], configurations)
    text.append("   C_STATEMENT_CONTEXT (rule 57b), each context read as an arrangement:")
    for entry in configurations["check"]["c_statement_context"]["contexts"]:
        text.append(f"      {entry['kind']}: {entry['context']!r}, read as {entry['read_as']}: kept so in "
                    f"{entry['kept_in_it']} arrangements of {entry['groups_looked_at']} groups looked at")


def add_configuration_4_line(text: list, dependent: str, configurations: dict) -> None:
    for entry in configurations["configuration_4"]:
        if entry["dependent"] == dependent:
            text.append(f"      configuration 4, in the triples: kept inside the holder between, inside the holder it "
                        f"depends on, in {entry['kept_so']} of {entry['kept']} kept arrangements; in "
                        f"{entry['groups_with_it']} of {entry['groups']} triple groups")


def add_signal_2_of_a_dependent(text: list, dependent: str, configurations: dict) -> None:
    """The lines after each of the dependent's components in its body, and the lines each holds, as they
    read in the groups, added up over every place (each place apart in out/configurations.json)."""
    for listing in configurations["listings"]:
        if listing["listing"] == dependent:
            add_signal_2_lines_of_a_listing(text, listing)


def add_signal_2_lines_of_a_listing(text: list, listing: dict) -> None:
    for component in listing["components"]:
        name = component["component"]
        after = readings_of_places(listing, name, "after")
        held = readings_of_places(listing, name, "held")
        if len(after) > 0:
            text.append(f"      signal 2, the lines after {name} in its body: {readings_written(after)} "
                        f"(of {sum_of(after)})")
        if len(held) > 0:
            text.append(f"      signal 2, the lines {name} holds: {readings_written(held)} (of {sum_of(held)})")


def readings_of_places(listing: dict, name: str, which: str) -> dict:
    readings = {}
    for place in listing["signal_2"]["in_the_groups"]:
        if which == "after" and place["place"].endswith(f", after {name}"):
            add_counts(readings, place["readings"])
        if which == "held" and (place["place"].endswith(f"> {name}") or place["place"] == f"inside {name}"):
            add_counts(readings, place["readings"])
    return readings


def add_check_section(text: list, configurations: dict) -> None:
    check = configurations["check"]
    bodies = check["the_reader_bodies"]
    roles = check["inert_part_roles"]
    grammar = check["c_grammar"]
    text.append("")
    text.append("8. The check (rule 57), every difference listed, none decided here")
    text.append(f"   a. bodies.json: listings compared {bodies['listings_compared']}; parts agree "
                f"{bodies['parts_agree']} of {bodies['parts_compared']}; N agrees {bodies['n_agree']} of "
                f"{bodies['listings_compared']}")
    text.append(f"   b. INERT_PART_ROLES: agree {roles['agree']} of {roles['parts_compared']} parts")
    add_roles_by_the_configuration(text, roles)
    text.append(f"   c. C's grammar: right after in every kept arrangement {grammar['must']} of "
                f"{grammar['pairs_compared']} pairs")
    dependents = check["the_dependents_n"]
    text.append(f"   d. each dependent's N from the record's own fields (rule 78): given {dependents['given']} of "
                f"{dependents['dependents']}; agree with the reader {dependents['agree']} of {dependents['dependents']}")
    for entry in dependents["by_dependent"]:
        text.append(f"      {entry['listing']}: N {entry['N']} ({', '.join(entry['bodies'] or [])}), from {entry['from']}; "
                    f"the reader: {entry['the_reader']}")
    add_the_reader_n_lines(text, check.get("the_reader_n"))
    differences = check["differences"]
    by_kind = {}
    for difference in differences:
        add_one(by_kind, f"{difference['check']}: {difference['difference']}")
    text.append(f"   differences: {len(differences)}, by check and kind: {json.dumps(by_kind, sort_keys=True)}")
    for number in range(1, len(differences) + 1):
        entry = differences[number - 1]
        text.append(f"   {number}. {entry['difference']}, {entry['check']}, {entry['about']}")
        text.append(f"      known: {entry['what_is_known']}")
        text.append(f"      the record: {entry['the_record']}")


def add_roles_by_the_configuration(text: list, roles: dict) -> None:
    """Rule 81: INERT_PART_ROLES against the configuration's bodies, each difference named."""
    if "agree_by_the_configuration" in roles:
        text.append(f"      by the configuration's bodies (rule 81): agree {roles['agree_by_the_configuration']} of "
                    f"{roles['parts_compared']} parts; the other "
                    f"{roles['parts_compared'] - roles['agree_by_the_configuration']}:")
        for entry in roles["differences_by_the_configuration"]:
            text.append(f"         {entry['about']}: {entry['what_is_known']}; the record: {entry['the_record']}")


def add_the_reader_n_lines(text: list, check) -> None:
    """Rule 81: N against the reader by both readings, each difference named."""
    if check is not None:
        run_alone = check["run_alone"]
        dependents = check["dependents"]
        text.append(f"   e. N against the reader (rule 81), the second reading (a part is a body when a component "
                    f"holds it, or when it runs behind the branch or again): listings run alone, agree "
                    f"{run_alone['agree']} of {run_alone['compared']}; dependents, agree {dependents['agree']} of "
                    f"{dependents['compared']}")
        text.append(f"      the first reading (signal 2 alone): listings run alone, agree "
                    f"{run_alone['first_reading_agree']} of {run_alone['first_reading_compared']}")
        for entry in check["differences"]:
            text.append(f"      the second reading differs: {entry['about']}: {entry['what_is_known']}; the record: "
                        f"{entry['the_record']}")
        for entry in check["first_reading_differences"]:
            text.append(f"      the first reading differs: {entry['about']}: {entry['what_is_known']}; the record: "
                        f"{entry['the_record']}")


def add_bodies_section(text: list, configurations: dict) -> None:
    """Rule 81: per listing, which parts are bodies and why (held by which component, or how it runs alone), and N
    by signal 2 alone beside it."""
    listings = configurations["listings"]
    counted = n_counted(listings)
    given = len(listings) - counted.get("not run alone", 0)
    text.append("")
    text.append("10. Each listing's bodies (rule 81): a part is a body when a component of the listing holds it, or "
                "when it runs behind the branch or again ; beside it, N by "
                "signal 2 alone (the first reading)")
    text.append(f"   listings: {len(listings)}; N given {given} of {len(listings)}; no N (not run alone, not a "
                f"dependent) {counted.get('not run alone', 0)} of {len(listings)}")
    text.append(f"   listings by N, each count of {given}: {n_counts_written(counted)}")
    for listing in listings:
        text.append("   " + bodies_line(listing))


def n_counted(listings: list) -> dict:
    counted = {}
    for listing in listings:
        n = listing["configuration"]["N"]
        if n is None:
            add_one(counted, "not run alone")
        else:
            add_one(counted, f"N = {n}")
    return counted


def n_counts_written(counted: dict) -> str:
    texts = []
    for key in sorted(counted):
        if key != "not run alone":
            texts.append(f"{key}: {counted[key]}")
    written = "; ".join(texts)
    return written


def bodies_line(listing: dict) -> str:
    """`if (a) b; else c;`: N = 2: b (held by if(a); runs behind the branch), c (...); the others: a tested; by signal
    2 alone N = 2."""
    configuration = listing["configuration"]
    alone = listing["signal_2"]["alone"]
    why = alone.get("not_run") or "not in the part listings"
    line = f"{listing['listing']}: not run alone ({why_in_short(why)})"
    if configuration["N"] is not None:
        line = f"{listing['listing']}: N = {configuration['N']}"
    if configuration["N"] is not None and configuration["N"] > 0:
        line = line + ": " + each_body_with_why(configuration)
    if configuration["N"] is not None:
        line = line + others_written(alone.get("parts") or [], configuration["bodies"])
        line = line + f"; by signal 2 alone {first_reading_written(configuration['by_signal_2_alone'])}"
    return line


def others_written(parts: list, bodies: list) -> str:
    """The parts that are not bodies, each with how it ran alone."""
    texts = []
    for part in parts:
        if part["letter"] not in bodies:
            texts.append(f"{part['letter']} {part['reading'] or 'not run alone'}")
    written = ""
    if len(texts) > 0:
        written = "; the others: " + ", ".join(texts)
    return written


def first_reading_written(first: dict) -> str:
    written = "not run alone"
    if first["N"] is not None:
        written = f"N = {first['N']}"
    return written


def add_against_the_earlier_record_section(text: list, configurations: dict) -> None:
    """Rule 84: the record against the earlier one, listing by listing; rule 82: the kept part records left out."""
    comparison = configurations.get("against_the_earlier_record", {})
    text.append("")
    text.append("11. The record against the earlier record, listing by listing (rule 84)")
    text.append(f"   part records kept beside the ones that replaced them, left out (rule 82): "
                f"{', '.join(configurations.get('kept_records_left_out', [])) or 'none'}")
    if comparison.get("compared"):
        add_comparison_lines(text, comparison)
    else:
        text.append("   no earlier record beside it")


def add_comparison_lines(text: list, comparison: dict) -> None:
    both = comparison["in_both"]
    text.append(f"   the earlier record: out/{comparison['earlier_record']} (written {comparison['earlier_written']}, "
                f"sha256 {comparison['earlier_sha256']})")
    text.append(f"   listings: before {comparison['listings_before']}, now {comparison['listings_now']}; in both {both}; "
                f"only now {len(comparison['only_now'])}; only before {len(comparison['only_before'])}")
    text.append(f"   in both, the same in every field compared: {comparison['the_same']} of {both}; differ "
                f"{both - comparison['the_same']} of {both}; by field:")
    for field in COMPARED_FIELDS:
        text.append(f"      {field}: differs for {len(comparison['differ'].get(field, []))} of {both}")
    text.append(f"   each listing that differs ({len(comparison['by_listing'])} of {both}), each field before -> now:")
    for entry in comparison["by_listing"]:
        text.append("      " + a_listing_compared_written(entry))
    text.append(f"   only now ({len(comparison['only_now'])} of {comparison['listings_now']}): "
                f"{'; '.join(comparison['only_now']) or 'none'}")
    text.append(f"   only before ({len(comparison['only_before'])} of {comparison['listings_before']}): "
                f"{'; '.join(comparison['only_before']) or 'none'}")


def a_listing_compared_written(entry: dict) -> str:
    texts = []
    for field in entry["differs"]:
        before = json.dumps(entry["differs"][field]["before"], sort_keys=True)
        now = json.dumps(entry["differs"][field]["now"], sort_keys=True)
        texts.append(f"{field} {before} -> {now}")
    written = f"{entry['listing']}: " + "; ".join(texts)
    return written


# Files


def read_json(path: str):
    with open(path, encoding="utf-8") as json_file:
        contents = json.load(json_file)
    return contents


def read_json_gz(path: str):
    with gzip.open(path, "rt", encoding="utf-8") as json_file:
        contents = json.load(json_file)
    return contents


def write_json(path: str, contents) -> None:
    with open(path, "w", encoding="utf-8") as json_file:
        json.dump(contents, json_file, indent=1)
        json_file.write("\n")


def write_json_gz(path: str, contents) -> None:
    with gzip.open(path, "wt", encoding="utf-8") as json_file:
        json.dump(contents, json_file, separators=(",", ":"))
        json_file.write("\n")


def read_text(path: str) -> str:
    with open(path, encoding="utf-8") as text_file:
        text = text_file.read()
    return text


def write_text(path: str, text: str) -> None:
    with open(path, "w", encoding="utf-8") as text_file:
        text_file.write(text)


def sha256_of(path: str) -> str:
    with open(path, "rb") as read_file:
        digest = hashlib.sha256(read_file.read()).hexdigest()
    return digest


def relative_to_pchq(path: str) -> str:
    relative = os.path.relpath(path, PCHQ)
    return relative


def stop(message: str) -> None:
    print(message, flush=True)
    sys.exit(1)


if __name__ == "__main__":
    main()
