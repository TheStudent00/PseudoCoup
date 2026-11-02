"""dependent_HiOp_reader -- where each dependent-HiOp of GNU C may stand, and
which parts of each GNU C listing are bodies, read from clang 21.1.8's own
source code.

A HiOp is one of GNU C's operators or statements, as the vocabulary lists it;
a listing is one written form of it, such as `case a ... b: c;`. A
dependent-HiOp is one clang refuses unless something stands around it or with
it in the function: `break;` must stand inside a loop or a switch, and
`goto m;` needs the label `m:` in the same function. The statements a
dependent-HiOp may stand inside are its depended-HiOps; this file calls them
its places. The lowerer is the compiler that lowers GNU C: clang.

Plan: Planning/node_0_0_projects/node_0_0_0_pseudocoup/node_0_0_0_0_pseudoarch/
node_0_0_0_0_2_map_HiOp_to_unit/node_0_0_0_0_2_4_extract_lang_vocab/
node_0_0_0_0_2_4_2_dependent_HiOp_reader/ (a draft for Dee to build on; a
research node until 2026-10-11, . The functions below carry the
plan's names. Its runs and records: Research/extract_lang_vocabulary/
dependent_HiOp_reader/ (lanes_elv2/, out/).

Step 1: the 5 dependent listings clang places by the scopes around them,
`break;`, `continue;`, `case a: b;`, `case a ... b: c;` and `default: a;`.
Step 2: the 3 clang places by a rule over the whole function, `goto m;`,
`&&m` and `goto *a;` (read_function_rules); the rules clang states over one
switch, for the `case` and `default` listings (read_switch_rules, which the
plan's Block A does not name); and one result per dependent listing, all 8,
each with its evidence (combine).
Step 3 (Block B): for every listing, which of its parts are bodies
(which_parts_are_bodies). The 8 it is for are the 4 expressions whose bodies
clang writes like operands (`a && b`, `a || b`, `a ? b : c`, `a ?: b`) and
the 4 `for` listings with a step. A body, as this code counts it (the plan's
stand-in for Dee's word, CORE section 3.1): a part clang writes as a
statement; or a part clang writes as an operand that clang's control-flow
builder puts behind the HiOp's own branch, or runs again before a loop's
test. The part the branch tests is not a body, nor a part that runs once,
before the branch.

    def which_parts_are_bodies(checkout, listings_path):
        branches = read_branches(checkout)                      # CFG.cpp: each kind's function, its paths, the branch a path makes
        parts = read_where_each_part_runs(checkout, branches)   # each part: tested, behind the branch, run again before the test, before
        written = read_how_each_part_is_written(checkout)       # StmtPrinter.cpp: each part written as a statement or an operand
        bodies = combine_bodies(parts, written, listings_path)  # one result per listing: its parts, its bodies, N
        return bodies

    def where_each_dependent_stands(checkout, listings_path, label_address_path):
        asks = read_checker_asks(checkout)                     # Sema: what each dependent asks for before it refuses it
        gives = read_parser_gives(checkout)                    # the parser: what each statement gives the scopes inside it
        stands = join_asks_and_gives(checkout, asks, gives)    # the statements that give what each dependent asks
        function_wide = read_function_rules(checkout, gives)   # goto m;, &&m, goto *a;: what each needs in its function
        switch_wide = read_switch_rules(checkout)              # case, default: what clang refuses among one switch's
        places = combine(stands, function_wide, switch_wide, listings_path, label_address_path)
        return places

The answer crosses files. For `break;`, the parser sets a flag on a
statement's scope (ParseStmt.cpp); the scope code lets the flag set a member
and passes the member on to every scope inside (Scope.cpp); Sema looks the
member up through a getter before it accepts the dependent (Scope.h,
SemaStmt.cpp). For `goto m;`, the label is held by the function's scope
(SemaLookup.cpp) and checked when that scope is popped (SemaDecl.cpp,
Parser.cpp). For `goto *a;`, the jump checker walks the function's body
(JumpDiagnostics.cpp). Each step is read from the code, and every answer
carries its file and line.

What it reads, from clang 21.1.8 under $PSEUDOARCH_SOURCES/llvm-project-21.1.8:

    clang/include/clang/Basic/StmtNodes.td            clang's own list of kinds
    clang/lib/Sema/SemaStmt.cpp                       the checking functions; the Sema calls that build a statement
    clang/lib/Parse/ParseStmt.cpp                     the parsing functions
    clang/include/clang/Sema/Scope.h                  each getter, and the member it returns
    clang/lib/Sema/Scope.cpp                          the flag that sets each member, and how a new scope takes it
    clang/include/clang/Sema/Sema.h                   what holds a stack (getCurFunction())
    clang/lib/Sema/SemaDecl.cpp                       step 2: a label checked when its scope is popped; the jump checker started
    clang/lib/Sema/SemaLookup.cpp                     step 2: the scope a label is pushed onto
    clang/lib/Sema/SemaExpr.cpp                       step 2: what Sema builds for `&&m`
    clang/lib/Parse/ParseExpr.cpp                     step 2: where the parser reads `&&m`
    clang/lib/Parse/Parser.cpp                        step 2: where a scope is popped; the scope of a function's body
    clang/lib/Sema/JumpDiagnostics.cpp                step 2: the jump checker
    clang/include/clang/Sema/ScopeInfo.h              step 2: when the jump checker runs
    clang/include/clang/Basic/DiagnosticSemaKinds.td  step 2: the words of each refusal and note
    clang/include/clang/Basic/DiagnosticParseKinds.td step 2: the same, for the parser's
    clang/lib/Analysis/CFG.cpp                        step 3: the control-flow builder
    clang/lib/AST/StmtPrinter.cpp                     step 3: the write-back code, through operator_reader's walk
    clang/include/clang/AST/Stmt.h                    step 3: the slot each getter of a statement returns
    clang/include/clang/AST/Expr.h, ExprCXX.h         step 3: the same for an expression; the classes operator_reader's walk reads
    clang/lib/AST/ExprCXX.cpp                         step 3: the cast names operator_reader's walk writes
    clang/include/clang/AST/IgnoreExpr.h              step 3: what IgnoreParens hands back (IgnoreParensSingleStep)
    clang/lib/AST/Expr.cpp                            step 3: Expr::IgnoreParens
    clang/include/clang/AST/OperationKinds.h          step 3: the label prefix of each list entry (`BO_##Name`)
    clang/include/clang/Basic/TypeTraits.h, ExpressionTraits.h  step 3: the same
    clang/include/clang/Basic/Builtins.td             step 3: the builtins marked NoReturn

and GNU C's listings, Research/extract_lang_vocabulary/mask/gnu17/kinds_forms.json
(and label_address.json beside it, which holds `&&m`; step 3 also reads
kinds_builtins.json beside it, the builtins as calls, and looks a kind no
listing holds up in pass_a_forms.json beside it and in
HiOp_sorter/gnu_c_sort.json). C++ is read with tree-sitter through
operator_reader's cpp_code.

    python3 dependent_HiOp_reader.py     writes out/places.json (steps 1 and 2) and out/bodies.json (step 3),
                                         out/ being Research/extract_lang_vocabulary/dependent_HiOp_reader/out;
                                         PSEUDOARCH_SOURCES names the sources folder

The reading rules, each small and stated:

 1. A checking function is `Sema::ActOn<kind>` in SemaStmt.cpp, where
    StmtNodes.td declares `<kind>` (`Sema::ActOnBreakStmt` checks BreakStmt).
    It refuses its kind for where it stands in a statement that emits a
    diagnostic named `err_..._not_in_...`; the test is the innermost `if`
    around that statement.
 2. What a test asks for: `!S`, where `S` is declared once from a getter
    call `X->getter()` and never assigned again, asks for the scope that
    getter returns. `H->Stack.empty()` asks for the stack `Stack`, not empty.
    Any other test is kept, marked not read.
 3. A parsing function is `Parser::Parse<X>Statement` in ParseStmt.cpp. The
    kinds it builds are read from its Sema calls: each `Actions.ActOn<Name>(...)`
    whose `<Name>` ends in a kind StmtNodes.td declares (the longest such
    ending: `ActOnLabelStmt` builds LabelStmt, `ActOnFinishSwitchStmt`
    SwitchStmt) and whose value the function returns, directly or through
    the names it returns (`Res = Actions.ActOnGotoStmt(...)` ... `return
    Res;`). Its other such calls build parts of it (a label's empty statement
    is a NullStmt), kept as parts. A function that returns nothing but what
    one other function of the file returns is read through that function
    (ParseCompoundStatement, through ParseCompoundStatementBody). Each
    statement of its definitions that names `Scope::<flag>` (outside an `if`
    test) sets those flags, under the tests of the `if`s it stands in; every
    branch is kept. When the flags go into a variable, the `ParseScope` made
    from that variable is named too.
 4. A parsing function pushes or pops a stack when a Sema function it calls
    (`Actions.<F>(...)`, with `Sema::<F>` defined in SemaStmt.cpp) calls
    `push_back` or `pop_back` on a name that function does not declare.
 5. The scope link: in Scope.h, a getter returns a member (`return
    BreakParent;`); in Scope.cpp, a flag sets the member to its own scope
    (`if (flags & BreakScope) BreakParent = this;`), and a new scope takes the
    member from the scope around it (`BreakParent = parent->BreakParent;`)
    unless the flag in that test's `!(flags & ...)` is set (FnScope).
 6. A dependent's places: every kind whose parsing function sets a flag that
    sets the member its getter returns; or that pushes the stack it asks for.
    So it may stand inside a place directly, or with other statements
    between that do not set the flag that stops the member being passed on.
 7. The label rule (`goto m;`, `&&m`). The statement that refuses with
    `err_undeclared_label_use` (SemaDecl.cpp), the values its test is given,
    and where its function is called; where a scope is popped (Parser.cpp).
    The scope a new label is pushed onto (`PushOnScopeChains`, in the
    function that makes a `LabelDecl`, SemaLookup.cpp), read through rule 5's
    link (`getFnParent()` returns FnParent, which FnScope sets), and the
    statements that name that flag (ParseStmt.cpp, Parser.cpp). The listings
    it is about: each parsing function that looks a label up
    (`Actions.LookupOrCreateLabel`) and passes it to an `Actions.ActOn...`
    call, of that call's kind by rule 3's ending, or else of the kind the
    Sema function returns (`new (Context) <Kind>(...)`). A `getX` the
    refusal's values test is given by `setX`; the kind whose Sema function
    calls `setX` is what the others need, with the same label.
 8. The address rule (`goto *a;`). The statement that refuses with
    `err_indirect_goto_without_addrlabel` (JumpDiagnostics.cpp), its tests
    and the returns before it. A test `X.empty()` names a list, filled by
    `X.push_back(...)` under `case Stmt::<Kind>Class:`. The list the refusal
    finds empty holds what the dependent needs; the list a return before it
    requires not empty holds the dependents it is about. Where the lists are
    filled from (the body the checker walks) and where the checker is
    started (SemaDecl.cpp, ScopeInfo.h) are kept as evidence.
 9. The places a jump may not enter (JumpDiagnostics.cpp). In
    `GotoScope(parent, in, out, where)` the second argument is a scope's
    in-note and the third its out-note; in `ScopePair(in, out)`, the first
    and the second; a note given to a name is read where that name is
    passed. A place is a scope with an in-note. An in-note is only a warning
    in C when a function `Is...Warning` names it under
    `!S.getLangOpts().CPlusPlus`, with no test that needs C++.
10. The refusals for a jump into such a place: err_goto_into_protected_scope,
    err_switch_into_protected_scope and err_indirect_goto_in_protected_scope.
    Each statement that names one is followed one step: into the function it
    is passed to (the statements that name the parameter receiving it, and
    the `push_back` of the list their test checks), or, when it emits it,
    back to the calls of the function it stands in, two calls deep. The jumps
    it refuses: the kinds its own tests name (`dyn_cast<GotoStmt>`; a loop
    over `SwitchCase`, which stands for CaseStmt and DefaultStmt); when they
    name none, the kinds the tests on its way name, and rule 8's dependents
    where the way passes through the function of rule 8's refusal. Entering
    is refused when a test on the way names the in-note (`.InDiag`).
11. The rules over one switch (SemaStmt.cpp): the statements that refuse
    with err_multiple_default_labels_defined and err_duplicate_case, and
    their tests. The kinds each is about: the declared types of the names
    its tests use, and of the values pushed onto those names
    (`CaseVals.push_back(std::make_pair(LoVal, CS))`, with `CaseStmt *CS`).

Step 3's rules (read_branches 12 to 16, read_where_each_part_runs 17 and 18,
read_how_each_part_is_written 19, combine_bodies 20):

12. The dispatch, `CFGBuilder::Visit` (CFG.cpp). It first reads an
    expression through `IgnoreParens()` (`S = E->IgnoreParens();`):
    Expr::IgnoreParens (Expr.cpp) repeats IgnoreParensSingleStep
    (IgnoreExpr.h), each of whose returns hands back one part of a kind under
    its tests (a ParenExpr's sub-expression; `__extension__`'s; a
    GenericSelectionExpr's result when `!isResultDependent()`; a ChooseExpr's
    chosen side when `!isConditionDependent()`). Such a node is read as that
    part, visited in its place; when the tests fail it goes on to the switch.
    Each `case Stmt::<Kind>Class:` sends its kinds (a case with no statement
    of its own falls to the next) to the function its `return` calls;
    `default:` sends every other concrete kind to its own (VisitStmt). A
    `return` before the switch that a test of the node's kind lets a kind
    reach is read too (OpenMP's directives). A case that returns `Block`
    makes nothing.
13. A function's paths. The walk reads a builder function statement by
    statement, keeping what each name holds: a block, none, the node, a part
    of it (rule 18), a truth, what tryEvaluateBool knows, or unknown. A test
    the rules of 14 do not decide forks; each path keeps how it took it, and a
    test met again goes the same path. A loop whose test is not decided is
    read with no turn and with one; a loop over a part of the node (`for
    (Stmt *S : llvm::reverse(C->body()))`) once, its name holding each part;
    `do { ... } while (false);` once, a `break` leaving it. A function of
    CFG.cpp handed the node (`return VisitLogicalOperator(B);`,
    `isBuiltinAssumeWithSideEffects(..., C)`) is walked in place, its
    parameters given the arguments (overloads told apart by how many they
    take), the caller's own names put back after; a builder function named
    Visit... handed a part adds that part (rule 15d). Any other call is read
    as making no block and adding no part, and kept as a call not read. The
    names class CFGBuilder declares as fields keep their values from one
    function to the next. Paths that hold the same names, did the same, stand
    at the same status and took the tests a listing decides (14c, 14d, 14i)
    the same path are one path. A statement of any other sort stops the path,
    marked not read.
14. Tests.
    a. `badCFG` is false: the builder is read as it runs on a function clang
       accepts. A path that sets it (`badCFG = true;`, `Visit(nullptr)`) is
       dropped.
    b. A test of the node's kind (`dyn_cast<BinaryConditionalOperator>(C)`,
       and a name given such a cast) holds when that kind is the node's or one
       above it in StmtNodes.td.
    c. A test of the node's list entry: a getter of the node against a name
       the function does not declare (`B->getOpcode() == BO_LOr`); anything
       against a label of clang's builtin lists (`FD->getBuiltinID() ==
       Builtin::BI__builtin_object_size`, the builtin the call names); or a
       call the kind's class defines as a test of its entry (`static bool
       isLogicalOp(Opcode Opc) { return Opc == BO_LAnd || Opc==BO_LOr; }`).
       It forks; combine_bodies decides it for a listing's entry, whose label
       is the entry's name after a prefix the lists' `#define`s paste on
       (`BO_##Name`) or a builtin list's namespace (`Builtin::`). A
       predicate is read when it compares by `==` and `!=` only.
    d. A test that a part is there (`if (Stmt *I = F->getInc())`; `if (C)`
       with C a part; a part against none) forks. combine_bodies keeps the
       path where the part is there when the listing writes it; the path where
       it is not when some path of the kind's write-back code writes it and
       the listing does not; otherwise both. A path that adds none of a part
       the listing writes, when another path of the kind adds it, is a path for
       a node without that part, and does not fit the listing (`if
       (opaqueValue)`, for `a ?: b`).
    e. A test of a part's own kind is false: a listing's part stands for any
       code, read as of no kind but the roots (`Expr`, `Stmt`), so as no
       `&&`, `||`, case or compound statement of its own. The true path (a
       part that is itself `&&` or `||`, whose function takes this node's
       terminator) is kept in CFG.cpp's lines, not read.
    f. A name that holds a block is true, one that holds none false.
    g. A parameter given `nullptr` holds none (`!Term`).
    h. What `tryEvaluateBool` knows of a listing's parts is nothing: they are
       not constants. `KnownVal.isTrue()` and `isFalse()` are false;
       `TryResult KnownVal(true)` is known true.
    i. Any other test of the node (`I->isConsteval()`) forks; combine_bodies
       keeps the path the listing's own written path took (operator_reader's
       walk of StmtPrinter decided `Node->isConsteval()` false for `if (a)
       b;`). Every other test forks, and both paths are kept.
15. Blocks.
    a. On entry `Block` holds "after", the block of the code after the node
       (an inert call stands after every listing in Dee's examples), and
       `Succ` "after it".
    b. `createBlock()` makes a block linked to the one `Succ` holds;
       `createBlock(false)` one with no link; `createNoReturnBlock()` one
       linked to the exit.
    c. `autoCreateBlock()` makes one, as `createBlock()`, when `Block` holds
       none.
    d. `addStmt(P)` and `Visit(P, ...)` add a part P to the block `Block`
       holds, made first when it holds none; the call hands that block back,
       and `Block` holds it after. `VisitChildren(S)` adds every part of the
       node there; `appendStmt(X, S)` adds S to X.
    e. A part is named by the getter that takes it (rule 18).
    f. `addSuccessor(X, Y, ...)` links X to Y; Y may be none
       (`KnownVal.isTrue() ? nullptr : LoopSuccessor`).
    g. `X->setTerminator(T)` gives X its terminator: the node's when T is
       the node. `X->setLoopTarget(...)` marks a block linked back to a
       loop's test.
    h. `SaveAndRestore save(X)` puts X back when the path leaves the braces it
       stands in; `save.get()` is X's value then.
    i. A store keeps a block from one function for another: a field of the
       builder other than Block and Succ (`SwitchTerminatedBlock`), a list of
       them (`BackpatchBlocks`), or the CFG's indirect-goto block
       (`cfg->setIndirectGotoBlock(B)`). The links another function adds to
       what it takes out of a store (`addSuccessor(SwitchTerminatedBlock,
       CaseBlock, ...)` in VisitCaseStmt; buildCFG's, over BackpatchBlocks)
       count for the block a path put there, when the tests over them that
       cast the block's terminator name no kind, or one at or above the
       node's (`dyn_cast<GCCAsmStmt>(B->getTerminator())`). A part added
       while a store held a block, where a Visit function of another kind
       links that store (VisitCaseStmt), is linked from that block: the
       labels inside a switch's body.
16. A branch: a block whose terminator is the node, with two or more links,
    those the path adds (an `addSuccessor` to none counts) and those other
    functions add through a store (rule 15i).
17. Where a part runs, over one path's blocks and links, with a start linked
    to the block the function hands back (the node's first) and an end that
    every block not made in the path links to (after, after it, the exit, one
    made elsewhere). The join is the nearest block every chain of links from
    the branch block to the end passes; none when no chain does. A part, by its block:
      tested: its block is the branch block;
      run again before the test: its block is reached from the branch block
        and links back to it (`for`'s step, in the block given setLoopTarget);
      behind the branch: every chain of links from the start to its block
        passes the branch block, and some chain to it does not pass the join;
      before: the branch block is reached from its block, and its block is
        not reached from the branch block;
      after the join: reached from the branch block, and not behind it;
      not reached: none of these.
    In a path with no branch a part added is at "no branch". A part the path
    does not add is "not added" (`sizeof a`'s operand; a case's value).
18. Parts. A part is named by the getter that takes it (`F->getInc()`), also
    through a name given its value (`Expr *RHS = B->getRHS()->IgnoreParens();`:
    `IgnoreParens()` and casts keep the part). Parts are matched across
    CFG.cpp and StmtPrinter.cpp by the slot the getter returns: the `return`
    of its body in the kind's class, or the first class above it that
    defines it (Stmt.h, Expr.h, ExprCXX.h), read through casts and a `? ...
    : nullptr` (`return cast<Expr>(SubExprs[LHS]);` is `SubExprs[LHS]`), so
    ConditionalOperator's getLHS and getTrueExpr are one part.
19. How a part is written: operator_reader's walk of StmtPrinter.cpp
    (`clang.table_for`, `ways.ways_of`), each operand piece kept with its call:
    `PrintStmt` writes the part as a statement, `PrintExpr` and `Visit` as an
    operand. A helper handed a part (`PrintControlledStmt(Node->getBody())`,
    `PrintInitStmt(Node->getInit(), 5)`) is followed to its call, and the
    part is the one handed in; a name the function gives a value is that
    value (`Stmt *Else = If->getElse()`; a loop's `I` over `Node->body()`,
    each of it). No list entry is chosen: operator_reader reads a list only
    after asking clang-tblgen for the lists clang's build makes (clang.py,
    listed_text), so a piece written from an entry's spelling, or from a name
    given one, is read as any text. A listing's letters are the pieces of
    the paths whose writing is its `template` (operator_reader's spelling_of),
    letter for piece; a builtin call's letters are its arguments, each
    written by PrintCallArgs's `PrintExpr(Node->getArg(i))`. A kind whose
    write-back code switches over a list clang's build makes (AtomicExpr) is
    not walked; when that code calls no PrintStmt, its value letters are
    written as operands all the same.
20. A body: a part written as a statement; or written as an operand, behind
    the branch or run again before the test, in every path kept for the
    listing. Not a body: a type, a name, or an operand tested, before, after
    the join, with no branch, or not added. An operand that is a body in some
    paths and not in others, or whose place is not read in every path, is not
    read. N is the number of a listing's bodies.

Not read: when a flag is set or a stack pushed, against when the statement's
body is parsed (the lines show the order); whether a jump may leave a place
(the out-notes, and the tests that use them, are kept as evidence, but no
answer is drawn from them); what a GNU local label (`__label__`) changes; the
places of C++, Objective-C, OpenMP and OpenACC, which are kept but not
checked. Step 3: what a part's own control flow does to its place (rule 14e);
the tests `isResultDependent()` and `isConditionDependent()`, which in code
clang accepts only C++ makes true, and which decide whether
GenericSelectionExpr and ChooseExpr are read through; the order of what one
block holds (a C++17 `if (init; test)` adds its init to the branch block, so
it reads as tested); the kinds of C++, Objective-C, OpenMP and SEH, which are
read but not checked.
"""

import functools
import hashlib
import json
import os
import re
import sys
from typing import NamedTuple

HERE = os.path.dirname(os.path.abspath(__file__))
# Projects/PseudoArch/map_HiOp_to_unit/extract_lang_vocab/dependent_HiOp_reader: four folders down from Projects.
PROJECTS = os.path.normpath(os.path.join(HERE, "..", "..", "..", "..", ".."))
PCHQ = os.path.dirname(PROJECTS)
# The vocabulary's research folder: the listings it reads, and this reader's runs and records.
RESEARCH = os.path.join(PCHQ, "Research", "extract_lang_vocabulary")
OUT = os.path.join(RESEARCH, "dependent_HiOp_reader", "out")
if PROJECTS not in sys.path:
    sys.path.insert(0, PROJECTS)

from PseudoArch.map_HiOp_to_unit.model_lang_parts import declaring_file_path, placeholders_of  # noqa: E402
from PseudoArch.map_HiOp_to_unit.model_lang_parts.HiOps.operator_reader import spelling_of  # noqa: E402
from PseudoArch.map_HiOp_to_unit.model_lang_parts.HiOps.operator_reader import clang as clang_reader  # noqa: E402
from PseudoArch.map_HiOp_to_unit.model_lang_parts.HiOps.operator_reader import cpp_code  # noqa: E402
from PseudoArch.map_HiOp_to_unit.model_lang_parts.HiOps.operator_reader import ways as operator_walk  # noqa: E402

# clang's source: a folder under the one $PSEUDOARCH_SOURCES names.
CHECKOUT = "llvm-project-21.1.8"
# clang's own list of the kinds of statement and expression.
STMT_NODES = clang_reader.STMT_NODES
# Where Sema checks each statement, and pushes and pops the switch stack.
SEMA_STATEMENTS = "clang/lib/Sema/SemaStmt.cpp"
# Where the parser reads each statement, and sets the flags of its scopes.
PARSE_STATEMENTS = "clang/lib/Parse/ParseStmt.cpp"
# The scope class: its getters (Scope.h); how a flag sets a member, and how a
# new scope takes it from the scope around it (Scope.cpp).
SCOPE_HEADER = "clang/include/clang/Sema/Scope.h"
SCOPE_SOURCE = "clang/lib/Sema/Scope.cpp"
# Sema's class, whose getCurFunction() holds the switch stack.
SEMA_HEADER = "clang/include/clang/Sema/Sema.h"
# Step 2. Where a label is checked when its scope is popped, and where the
# jump checker is started.
SEMA_DECLARATIONS = "clang/lib/Sema/SemaDecl.cpp"
# The scope a new label is pushed onto.
SEMA_LOOKUP = "clang/lib/Sema/SemaLookup.cpp"
# What Sema builds for `&&m`.
SEMA_EXPRESSIONS = "clang/lib/Sema/SemaExpr.cpp"
# Where the parser reads `&&m`.
PARSE_EXPRESSIONS = "clang/lib/Parse/ParseExpr.cpp"
# Where a scope is popped, and the scope of a function's body.
PARSER = "clang/lib/Parse/Parser.cpp"
# The jump checker.
JUMPS = "clang/lib/Sema/JumpDiagnostics.cpp"
# When the jump checker runs.
SCOPE_INFO = "clang/include/clang/Sema/ScopeInfo.h"
# The words of each refusal and note.
SEMA_DIAGNOSTICS = "clang/include/clang/Basic/DiagnosticSemaKinds.td"
PARSE_DIAGNOSTICS = "clang/include/clang/Basic/DiagnosticParseKinds.td"
CLANG_FILES = (STMT_NODES, SEMA_STATEMENTS, PARSE_STATEMENTS, SCOPE_HEADER, SCOPE_SOURCE, SEMA_HEADER,
               SEMA_DECLARATIONS, SEMA_LOOKUP, SEMA_EXPRESSIONS, PARSE_EXPRESSIONS, PARSER, JUMPS, SCOPE_INFO,
               SEMA_DIAGNOSTICS, PARSE_DIAGNOSTICS)
DIAGNOSTIC_FILES = (SEMA_DIAGNOSTICS, PARSE_DIAGNOSTICS)

# GNU C's listings: each HiOp's written forms, with clang's kind of each.
LISTINGS = os.path.join(RESEARCH, "mask", "gnu17", "kinds_forms.json")
# `&&m`, kept apart from the others (it takes no operand, only a name).
LABEL_ADDRESS = os.path.join(RESEARCH, "mask", "gnu17", "label_address.json")
WRITTEN = os.path.join(OUT, "places.json")

# Rule 1.
CHECKING_FUNCTION = re.compile(r"^Sema::ActOn(\w+)$")
REFUSED_FOR_WHERE_IT_STANDS = re.compile(r"diag::(err_\w*_not_in_\w*)")
# Rule 3.
PARSING_FUNCTION = re.compile(r"^Parser::Parse(\w+)Statement$")
BUILDING_CALL = re.compile(r"^ActOn(\w+)$")
SCOPE_FLAG = re.compile(r"\bScope::(\w+)")
FLAGS_WRITTEN_TO = re.compile(r"^(?:\w+\s+)?(\w+)\s*\|?=[^=]")
SCOPE_MADE_FROM = re.compile(r"^ParseScope\s+\w+\s*\(\s*this\s*,\s*(\w+)\s*[,)]")
# Rule 4.
STACK_CHANGES = ("push_back", "pop_back")
# Rule 5.
RETURNS_A_NAME = re.compile(r"^return\s+(\w+)\s*;$")
MEMBER_SET_TO_ITS_OWN_SCOPE = re.compile(r"^(\w+)\s*=\s*this\s*;$")
MEMBER_TAKEN_FROM_THE_SCOPE_AROUND = re.compile(r"^(\w+)\s*=\s*\w+->(\w+)\s*;$")

# What a test asks for (rule 2).
ASKS_FOR_A_SCOPE = "a scope, from a getter"
ASKS_FOR_A_STACK = "a stack, not empty"

# Step 2: the refusals the plan names, where each reading starts.
# Rule 7: SemaDecl.cpp line 2192 (the plan, read_function_rules).
LABEL_REFUSAL = "err_undeclared_label_use"
# Rule 7: `&&m` outside any function (ParseExpr.cpp).
OUTSIDE_A_FUNCTION_REFUSAL = "err_address_of_label_outside_fn"
# Rule 8: JumpDiagnostics.cpp line 768 (the plan, read_function_rules).
ADDRESS_REFUSAL = "err_indirect_goto_without_addrlabel"
# Rule 10.
ENTERING_REFUSALS = ("err_goto_into_protected_scope", "err_switch_into_protected_scope",
                     "err_indirect_goto_in_protected_scope")
# Rule 11.
SWITCH_REFUSALS = ("err_multiple_default_labels_defined", "err_duplicate_case")
# Rule 7: the Sema function the parser calls to look a label up, and the
# call that pushes a declaration onto a scope.
LABEL_MADE = "LabelDecl::Create"
PUSHED_ONTO_A_SCOPE = "PushOnScopeChains"
# Rule 9.
SCOPE_RECORDS = {"GotoScope": (1, 2), "ScopePair": (0, 1), "emplace_back": (1, 2)}
NOTE = re.compile(r"^diag::(note_\w+)$")
WARNING_FUNCTION = re.compile(r"^Is\w*Warning$")
NEEDS_C = "!S.getLangOpts().CPlusPlus"
NEEDS_CPP = re.compile(r"(?<!!)S\.getLangOpts\(\)\.CPlusPlus\w*")
IN_NOTE_TESTED = re.compile(r"\.InDiag\b")
OUT_NOTE_TESTED = re.compile(r"\.OutDiag\b")
# Rule 8.
LIST_FOUND_EMPTY = re.compile(r"^(\w+)\.empty\(\)$")
LIST_TESTED = re.compile(r"\b(\w+)\.empty\(\)")
CASE_OF_A_KIND = re.compile(r"\bStmt::(\w+)Class\b")
# Rules 10 and 11.
KIND_CAST = re.compile(r"\b(?:dyn_cast|cast|isa)<(\w+)>")
KIND_DECLARED = re.compile(r"\b(\w+)\s*\*\s*\w+\s*=")
A_NAME = re.compile(r"^!?\s*(\w+)$")
A_LIST_USED = re.compile(r"\b(\w+)(?:\.empty\(\)|\[)")
WORD = re.compile(r"\b\w+\b")
# The roots of StmtNodes.td stand for every kind, and are not read as one.
ROOT_KINDS = ("Stmt", "ValueStmt", "Expr")
# A diagnostic is emitted when it is an argument of a call named `...Diag`.
EMITTING_CALL = re.compile(r"Diag$")
DIAGNOSTIC_DEFINED = re.compile(r"^def\s+(\w+)\s*:\s*(\w+)\s*<", re.M)
QUOTED = re.compile(r'\s*"((?:[^"\\]|\\.)*)"')

# The tree-sitter nodes that hold a name, and the statements a name stands in.
NAME_NODES = ("identifier", "field_identifier", "qualified_identifier", "type_identifier",
              "namespace_identifier", "statement_identifier")
STATEMENT_NODES = ("expression_statement", "return_statement", "declaration", "goto_statement",
                   "break_statement", "continue_statement", "field_declaration", "condition_clause")
LOOP_NODES = ("for_statement", "while_statement", "do_statement", "for_range_loop")
LEAVING_NODES = ("goto_statement", "break_statement", "return_statement", "continue_statement")

# How a dependent listing is placed (combine).
BY_THE_SCOPES_AROUND_IT = "by the statements around it"
BY_THE_WHOLE_FUNCTION = "by a rule over the whole function"

# Step 3 (Block B). clang's control-flow builder: its dispatch, the functions
# it sends each kind to, and the class whose fields keep their values from one
# of its functions to the next (rules 12 to 16).
BUILDER = "clang/lib/Analysis/CFG.cpp"
BUILDER_CLASS = "CFGBuilder"
DISPATCH = "CFGBuilder::Visit"
# What `IgnoreParens()` hands back before the dispatch (rule 12).
IGNORE_EXPRESSIONS = "clang/include/clang/AST/IgnoreExpr.h"
EXPRESSION_SOURCE = "clang/lib/AST/Expr.cpp"
READ_THROUGH = "IgnoreParens"
READ_THROUGH_STEP = "IgnoreParensSingleStep"
# clang's write-back code, walked through operator_reader (rule 19).
STMT_PRINTER = clang_reader.PRINTER
# The classes whose getters name a kind's parts, and the slot each returns
# (rule 18).
STATEMENT_CLASSES = "clang/include/clang/AST/Stmt.h"
CLASS_FILES = (STATEMENT_CLASSES, clang_reader.EXPR, clang_reader.EXPR_CXX)
# The lists whose `#define`s give an entry's label (`BO_##Name`), rule 14c.
ENUM_FILES = clang_reader.ENUM_HEADERS
# The builtins clang marks NoReturn, whose calls VisitCallExpr ends a block
# with (CFG.cpp line 2871).
BUILTIN_LIST = clang_reader.BUILTINS_TD
NO_RETURN_BUILTIN = re.compile(r"^def\s+\w+\s*:[^{]*\{(.*?)^\}", re.M | re.S)
BUILTIN_SPELLINGS = re.compile(r'let\s+Spellings\s*=\s*\[([^\]]*)\]')
BUILTIN_ATTRIBUTES = re.compile(r'let\s+Attributes\s*=\s*\[([^\]]*)\]')
NO_RETURN = "NoReturn"
# Every clang file step 3 reads; operator_reader's walk reads Expr.h and
# ExprCXX.h (the kinds' classes) and ExprCXX.cpp (the cast names) besides
# StmtPrinter.cpp.
BODY_FILES = (STMT_NODES, BUILDER, STMT_PRINTER, STATEMENT_CLASSES, clang_reader.EXPR, clang_reader.EXPR_CXX,
              clang_reader.CASTS, IGNORE_EXPRESSIONS, EXPRESSION_SOURCE, BUILTIN_LIST) + ENUM_FILES
# The listings step 3 reads (and LISTINGS, LABEL_ADDRESS above), and the two
# lists it looks a kind up in when no listing has it.
BUILTIN_LISTINGS = os.path.join(RESEARCH, "mask", "gnu17", "kinds_builtins.json")
LISTING_FILES = (LISTINGS, LABEL_ADDRESS, BUILTIN_LISTINGS)
PASS_A_LISTINGS = os.path.join(RESEARCH, "mask", "gnu17", "pass_a_forms.json")
SORTED_LISTINGS = os.path.join(RESEARCH, "HiOp_sorter", "gnu_c_sort.json")
BODIES_WRITTEN = os.path.join(OUT, "bodies.json")
# The 8 listings of step 3 (the plan's §3.1), named for the report.
THE_EIGHT = ("a && b", "a || b", "a ? b : c", "a ?: b", "for (a; b; c) d;", "for (a; ; b) c;", "for (; a; b) c;",
             "for (;; a) b;")

# Rule 17: where a part runs, to the HiOp's branch.
TESTED = "tested"
BEHIND = "behind the branch"
RUN_AGAIN = "run again before the test"
BEFORE = "before"
AFTER = "after the join"
NOT_REACHED = "not reached"
NO_BRANCH = "no branch"
NOT_ADDED = "not added"
DIFFERS_BY_PATH = "differs by path"
BODY_PLACES = (BEHIND, RUN_AGAIN)
# Rule 19: how a part is written.
AS_STATEMENT = "statement"
AS_OPERAND = "operand"
AS_TYPE = "a type"
AS_NAME = "a name"
WRITTEN_AS_OF_A_SORT = {"type": AS_TYPE, "name": AS_NAME}
TYPE_LETTERS = ("T", "U", "V", "W")
NAME_LETTERS = ("m", "n")

# Rule 15: the blocks a walk starts with, and the ends of its graph (rule 17).
AFTER_BLOCK = "after"
AFTER_IT = "after it"
EXIT_BLOCK = "exit"
INDIRECT_GOTO_BLOCK = "the CFG's indirect-goto block"
MADE_BLOCK = re.compile(r"^b\d+$")
START = "start"
END = "end"
NODE_VALUE = ("node",)
NONE_VALUE = ("none",)
# The members a walk keeps itself; every other member given a block is a
# store (rule 15i).
WALK_MEMBERS = ("Block", "Succ")
# Rule 13: a walk follows the node into another builder function this deep,
# and keeps at most this many paths at once.
WALK_DEPTH = 4
BUILDER_PATH_LIMIT = 4096
SAVE_AND_RESTORE = "SaveAndRestore"
TRY_RESULT = "TryResult"
# Rule 14b and 14e: the calls that test a kind, and those that keep a value.
IDENTITY_CASTS = ("const_cast", "static_cast", "reinterpret_cast")
TESTING_CASTS = ("isa", "isa_and_nonnull")
FINDING_CASTS = ("dyn_cast", "dyn_cast_or_null")
PART_KEEPING = ("IgnoreParens", "IgnoreImpCasts", "IgnoreParenImpCasts", "IgnoreParenCasts")
RANGE_GETTERS = ("body", "children", "body_rbegin", "body_begin", "body_back", "body_front", "labels", "decls")
BLOCK_MARKS = {"setTerminator": "terminator", "setLoopTarget": "loop target", "setLabel": "label"}
TESTING_OPERATORS = ("==", "!=", "&&", "||")
# Rule 14: what a test is about.
THERE = "a part is there"
ENTRY_TEST = "the node's list entry"
NODE_TEST = "the node"
OTHER_TEST = "other"
DISPATCH_TEST = "the dispatch"
CLASS_NAME_OF_A_KIND = re.compile(r"^Stmt::(\w+)Class$")
CAST_DECLARED = re.compile(r"^(?:const\s+)?\w+\s*\*\s*(\w+)\s*=\s*dyn_cast<(\w+)>\(")
ENTRY_COMPARED = re.compile(r"^\s*(\w+)\s*(==|!=)\s*(\w+)\s*$")
LOOP_OVER_A_MEMBER = r"\b{0}\s*=\s*(\w+)\.begin\(\)"
BLOCK_HELD_IN = re.compile(r"^(\w+)->block$")
TERMINATOR_TESTED = "->getTerminator()"

# Rule 18 and 19: a part's getter, read through casts and a loop's range.
GETTER_OF_THE_NODE = re.compile(r"^(?:each of )?Node->(\w+)\(")
A_CAST_AROUND = re.compile(r"^(?:cast|dyn_cast|cast_or_null|dyn_cast_or_null)<[^<>()]*>\((.*)\)$")
RANGE_LOOP_HEADER = re.compile(r"^for \((?:const\s+)?[\w:]+\s*[*&]*\s*(\w+)\s*:\s*(.+)\)$")
SLOT_CAST = re.compile(r"^(?:cast|dyn_cast|cast_or_null|dyn_cast_or_null|reinterpret_cast|static_cast|const_cast)"
                       r"<[^()]*>\((.*)\)$")
SLOT_CHOICE = re.compile(r"^[^?]*\?\s*(.*?)\s*:\s*nullptr$")
# Rule 19: operator_reader's walk, each operand piece kept with its call.
ENTRY_TEXT = "‹entry›"
ENTRY_SPELLING_CALL = re.compile(r"^(?:\w+::)*(\w+)\(")
HANDED = "<the part handed in>"
THROUGH = "<written through>"
OPERAND_EFFECT = ("piece", ("operand",))
MADE_LIST_INCLUDE = "#include"


class Definition(NamedTuple):
    """One function a file defines, as tree-sitter reads it."""

    name: str        # as written: Sema::ActOnBreakStmt
    line: int        # where it starts
    node: object     # tree-sitter's node of the whole definition


class Refusal(NamedTuple):
    """A statement of a checking function that refuses its kind for where it
    stands, with the tests it stands under."""

    diagnostic: str  # err_break_not_in_loop_or_switch
    statement: object
    tests: tuple


class Test(NamedTuple):
    """One test a statement stands under: an `if`'s condition and the branch
    it stands in ("true" or "false"), or a loop or a case it stands in."""

    code: object     # cpp_code's Code of the condition, the loop, or the case
    taken: str       # "true", "false", "each turn of the loop", "this case"


class Use(NamedTuple):
    """One place a function names a name, as tree-sitter reads it (step 2)."""

    definition: Definition
    node: object
    relative: str    # the file


class Walk(NamedTuple):
    """What every step of a walk through one builder function needs (step 3,
    rule 13)."""

    checkout: str
    kind: str        # the kind of the node the walk follows
    node_name: str   # the function's parameter that holds the node: F in VisitForStmt(ForStmt *F)
    function: str    # CFGBuilder::VisitForStmt
    members: tuple   # the names class CFGBuilder declares as fields
    depth: int       # how many builder functions deep the walk is


class BuilderPath(NamedTuple):
    """One path through a builder function, so far (step 3, rules 13 to 15)."""

    values: tuple    # (name, value) for each name given a value, sorted by name
    events: tuple    # what the path did, in order: blocks made and linked, parts added (rule 15)
    tests: tuple     # (what, text, taken, at, detail) for each test it took (rule 14)
    status: str      # "", "return", "break", "continue", "stop", "dropped"
    returned: tuple  # the value handed back, when status is "return"
    made: int        # how many blocks it has made
    frames: tuple    # for each `{ ... }` it stands in, the members a SaveAndRestore saved
    why: str         # why it stopped, when status is "stop"


class TooManyBuilderPaths(Exception):
    """A builder function has more paths at once than BUILDER_PATH_LIMIT."""


def main():
    places = where_each_dependent_stands(CHECKOUT, LISTINGS, LABEL_ADDRESS)
    recorded = with_what_was_read(places, CHECKOUT, LISTINGS, LABEL_ADDRESS)
    write_json(recorded, WRITTEN)
    print_places(places)
    bodies = bodies_of_the_files(CHECKOUT, LISTING_FILES)
    branching = kinds_that_branch(CHECKOUT, bodies)
    recorded_bodies = with_what_bodies_read(bodies, branching, CHECKOUT)
    write_json(recorded_bodies, BODIES_WRITTEN)
    print_bodies(recorded_bodies)


def where_each_dependent_stands(checkout: str, listings_path: str, label_address_path: str) -> dict:
    """The dependent listings of `listings_path` and `label_address_path`,
    each with where it may stand and what it needs, read from clang's code,
    with the evidence."""
    asks = read_checker_asks(checkout)
    gives = read_parser_gives(checkout)
    stands = join_asks_and_gives(checkout, asks, gives)
    function_wide = read_function_rules(checkout, gives)
    switch_wide = read_switch_rules(checkout)
    places = combine(stands, function_wide, switch_wide, listings_path, label_address_path)
    return places


# read_checker_asks (rules 1 and 2)


def read_checker_asks(checkout: str) -> dict:
    """kind -> [what its checking function tests before it refuses the kind
    for where it stands], for each kind whose checking function has such a
    refusal (rules 1 and 2)."""
    kinds = concrete_kinds(checkout)
    definitions = read_every_function(checkout, SEMA_STATEMENTS)
    asks = {}
    for definition in definitions:
        add_asks_of(asks, definition, kinds)
    return asks


def add_asks_of(asks: dict, definition: Definition, kinds: dict) -> None:
    kind = kind_named_by(definition.name, CHECKING_FUNCTION, "", kinds)
    if kind is None:
        return
    body = body_of(definition)
    refusals = refusals_for_where_it_stands(body)
    for refusal in refusals:
        ask = ask_of(kind, kinds, definition, body, refusal)
        add_to_list(asks, kind, ask)


def refusals_for_where_it_stands(body) -> list:
    """Each statement of a checking function that emits a diagnostic named
    `err_..._not_in_...`, with the tests it stands under."""
    refusals = []
    statements = statements_under_tests(body)
    for statement, tests in statements:
        found = REFUSED_FOR_WHERE_IT_STANDS.search(statement.text)
        if found is None:
            continue
        refusals.append(Refusal(found.group(1), statement, tests))
    return refusals


def ask_of(kind: str, kinds: dict, definition: Definition, body, refusal: Refusal) -> dict:
    """What one refusal's test asks for, with where each piece is."""
    ask = {
        "kind": kind,
        "kind_declared_at": where(STMT_NODES, kinds[kind]),
        "checking_function": definition.name,
        "function_at": where(SEMA_STATEMENTS, definition.line),
        "refusal": refusal.diagnostic,
        "refusal_at": where(SEMA_STATEMENTS, refusal.statement.line),
        "refusal_statement": refusal.statement.text,
    }
    if not refusal.tests:
        ask["asks"] = not_read("the refusal stands under no test")
        return ask
    test = refusal.tests[-1]
    ask["test"] = test.code.text
    ask["test_at"] = where(SEMA_STATEMENTS, test.code.line)
    ask["refused_when_the_test_is"] = test.taken
    ask["asks"] = what_the_test_asks(body, test)
    return ask


def what_the_test_asks(body, test: Test) -> dict:
    """Rule 2: a scope from a getter (`!S`), or a stack not empty
    (`H->Stack.empty()`); anything else is kept, marked not read."""
    asked = not_read(f"`{test.code.text}` is neither `!S` with S a scope from a getter, nor `.empty()` on a stack")
    if test.taken != "true":
        return asked
    if test.code.form == "not":
        asked = scope_asked(body, test.code.parts[0])
    if is_empty_test_on_a_member(test.code):
        asked = stack_asked(test.code)
    return asked


def scope_asked(body, tested) -> dict:
    """`!S`: what S holds, when it is a getter's call."""
    value = tested
    if tested.form == "name":
        value = value_given_to(body, tested.parts[0])
    asked = not_read(f"`{tested.text}` is assigned again or declared more than once, or not from a getter")
    if value is None or not is_getter_call(value):
        return asked
    callee = value.parts[0]
    asked = {
        "what": ASKS_FOR_A_SCOPE,
        "getter": callee.parts[1],
        "called_on": callee.parts[0].text,
        "text": value.text,
        "at": where(SEMA_STATEMENTS, value.line),
    }
    return asked


def stack_asked(test_code) -> dict:
    """`H->Stack.empty()`: the stack, and what holds it."""
    stack_member = test_code.parts[0].parts[0]
    asked = {
        "what": ASKS_FOR_A_STACK,
        "stack": stack_member.parts[1],
        "held_by": stack_member.parts[0].text,
        "text": stack_member.text,
        "at": where(SEMA_STATEMENTS, test_code.line),
    }
    return asked


def value_given_to(body, name: str):
    """The value `name` is declared with, when the function declares it once
    and never assigns it again; else None."""
    declared = []
    assigned = []
    statements = statements_under_tests(body)
    for statement, _tests in statements:
        add_declared_value(declared, statement, name)
        if assigns_to(statement, name):
            assigned.append(statement)
    value = None
    if len(declared) == 1 and not assigned:
        value = declared[0]
    return value


def add_declared_value(declared: list, statement, name: str) -> None:
    if statement.form != "declare":
        return
    for declared_name, _declared_type, value in statement.parts:
        if declared_name == name:
            declared.append(value)


def assigns_to(statement, name: str) -> bool:
    assigns = False
    if statement.form == "do":
        assigns = re.match(rf"^{re.escape(name)}\s*[^=\s]?=(?!=)", statement.text) is not None
    return assigns


def is_getter_call(code) -> bool:
    """`X->getter()`: a call of a member, with no arguments."""
    answer = False
    if code.form == "call" and not code.parts[1]:
        answer = code.parts[0].form == "member"
    return answer


def is_empty_test_on_a_member(code) -> bool:
    """`H->Stack.empty()`."""
    answer = False
    if code.form != "call" or code.parts[1]:
        return answer
    callee = code.parts[0]
    if callee.form == "member" and callee.parts[1] == "empty":
        answer = callee.parts[0].form == "member"
    return answer


# read_parser_gives (rules 3 and 4)


def read_parser_gives(checkout: str) -> dict:
    """kind -> what its parsing function gives the scopes inside a statement
    of that kind: the scope flags it sets (rule 3), and the stacks it pushes
    or pops through Sema (rule 4). A parsing function that builds no kind is
    kept in "left_out", with the reason."""
    kinds = concrete_kinds(checkout)
    definitions = read_every_function(checkout, PARSE_STATEMENTS)
    sema_definitions = read_every_function(checkout, SEMA_STATEMENTS)
    gives = {"by_kind": {}, "left_out": []}
    for definition in definitions:
        add_what_it_gives(gives, definition, kinds, definitions, sema_definitions)
    return gives


def add_what_it_gives(gives: dict, definition: Definition, kinds: dict, definitions: tuple,
                      sema_definitions: tuple) -> None:
    if PARSING_FUNCTION.match(definition.name) is None:
        return
    built = statements_built_by(definition, kinds, definitions)
    if not built["kinds"]:
        gives["left_out"].append(left_out(definition.name, where(PARSE_STATEMENTS, definition.line), built["why"]))
        return
    flags = flags_set_by(definition)
    for kind in built["kinds"]:
        given = given_for(gives, kind, kinds)
        given["parsing_functions"].append(parsing_function_read(definition, kind, built))
        given["flags_set"].extend(flags)
        add_stacks_changed(given, definition, sema_definitions)


def given_for(gives: dict, kind: str, kinds: dict) -> dict:
    if kind not in gives["by_kind"]:
        gives["by_kind"][kind] = new_given(kind, kinds)
    given = gives["by_kind"][kind]
    return given


def new_given(kind: str, kinds: dict) -> dict:
    given = {
        "kind_declared_at": where(STMT_NODES, kinds[kind]),
        "parsing_functions": [],
        "flags_set": [],
        "stacks_changed": [],
        "sema_calls_read": [],
        "sema_calls_not_in_SemaStmt": [],
    }
    return given


def parsing_function_read(definition: Definition, kind: str, built: dict) -> dict:
    """Where a parsing function builds `kind` (rule 3), and its other Sema
    calls that build a part of it."""
    read = {
        "function": definition.name,
        "at": where(PARSE_STATEMENTS, definition.line),
        "builds_it_with": built["calls"][kind],
        "read_through": built["through"],
        "builds_parts_with": built["parts"],
    }
    return read


def statements_built_by(definition: Definition, kinds: dict, definitions: tuple) -> dict:
    """Rule 3: the kinds a parsing function builds, from the `Actions.ActOn...`
    calls whose value it returns; its other such calls build parts of it."""
    built = {"kinds": [], "calls": {}, "parts": [], "through": [], "why": ""}
    add_kinds_built(built, definition, kinds, definitions, [])
    return built


def add_kinds_built(built: dict, definition: Definition, kinds: dict, definitions: tuple, visited: list) -> None:
    visited.append(definition.line)
    returned = returned_values(definition.node)
    calls = building_calls_in(definition.node, kinds)
    for call, kind in calls:
        add_building_call(built, call, kind, returned)
    if built["kinds"]:
        return
    followed = the_one_function_returned(definition, returned, definitions)
    if not followed:
        built["why"] = why_no_kind(returned)
        return
    for other in followed:
        if other.line in visited:
            continue
        built["through"].append({"function": other.name, "at": where(PARSE_STATEMENTS, other.line)})
        add_kinds_built(built, other, kinds, definitions, visited)


def add_building_call(built: dict, call, kind: str, returned: list) -> None:
    read = {"call": callee_text(call), "kind": kind, "at": where(PARSE_STATEMENTS, line_of(call))}
    if not is_one_of(call, returned):
        built["parts"].append(read)
        return
    add_once(built["kinds"], kind)
    add_to_list(built["calls"], kind, read)


def building_calls_in(node, kinds: dict) -> list:
    """(call, kind) for each `Actions.ActOn<Name>(...)` whose `<Name>` ends
    in a kind (rule 3)."""
    found = []
    calls = calls_in(node)
    for call in calls:
        kind = kind_built_by_call(call, kinds)
        if kind is not None:
            found.append((call, kind))
    return found


def kind_built_by_call(call, kinds: dict):
    kind = None
    name = sema_function_called(call)
    if name is None:
        return kind
    named = BUILDING_CALL.match(name)
    if named is not None:
        kind = kind_ending(named.group(1), kinds)
    return kind


def kind_ending(name: str, kinds: dict):
    """The longest ending of `name` that starts at a capital letter and is a
    kind StmtNodes.td declares: `StartOfSwitchStmt` -> SwitchStmt; else None."""
    kind = None
    for index in range(len(name)):
        ending = name[index:]
        if name[index].isupper() and ending in kinds:
            kind = ending
            break
    return kind


def sema_function_called(call):
    """`Actions.F(...)` -> F; anything else -> None."""
    name = None
    callee = call.child_by_field_name("function")
    if callee is None or callee.type != "field_expression":
        return name
    holder = callee.child_by_field_name("argument")
    field = callee.child_by_field_name("field")
    if holder is not None and field is not None and holder.text.decode() == "Actions":
        name = field.text.decode()
    return name


def the_one_function_returned(definition: Definition, returned: list, definitions: tuple) -> list:
    """The definitions of the one other function of the file whose value is
    every value this function returns (ParseCompoundStatement returns what
    ParseCompoundStatementBody returns); else []."""
    followed = []
    names = functions_of_the_file_returned(definition, returned, definitions)
    if len(names) == 1:
        followed = definitions_named(definitions, names[0])
    return followed


def functions_of_the_file_returned(definition: Definition, returned: list, definitions: tuple) -> list:
    """The file's functions whose calls this function returns; [] when it
    returns anything else as well."""
    names = []
    owner = definition.name.split("::")[0]
    for value in returned:
        name = function_of_the_file_called(value, owner, definitions)
        if name is None:
            names = []
            break
        add_once(names, name)
    return names


def function_of_the_file_called(value, owner: str, definitions: tuple):
    """`G(...)` -> `owner::G`, when the file defines it; else None."""
    name = None
    if value.type != "call_expression":
        return name
    callee = value.child_by_field_name("function")
    if callee is None or callee.type != "identifier":
        return name
    full = owner + "::" + callee.text.decode()
    if definitions_named(definitions, full):
        name = full
    return name


def why_no_kind(returned: list) -> str:
    texts = []
    for value in returned:
        texts.append(short_text(value))
    why = ("it returns no `Actions.ActOn...<Kind>(...)` value, nor only what one other function of the file returns;"
           " it returns: " + "; ".join(texts))
    if not returned:
        why = "it returns no value"
    return why


def flags_set_by(definition: Definition) -> list:
    """Rule 3: each statement of the parsing function that names
    `Scope::<flag>`, with the tests it stands under."""
    settings = []
    statements = statements_under_tests(body_of(definition))
    for statement, tests in statements:
        flags = SCOPE_FLAG.findall(statement.text)
        if not flags:
            continue
        setting = {
            "flags": flags,
            "at": where(PARSE_STATEMENTS, statement.line),
            "statement": statement.text,
            "under": tests_written(tests),
        }
        add_scope_made_from_it(setting, statement, statements)
        settings.append(setting)
    return settings


def add_scope_made_from_it(setting: dict, statement, statements: list) -> None:
    """When the flags go into a variable, the `ParseScope` made from it."""
    written = FLAGS_WRITTEN_TO.match(statement.text)
    if written is None:
        return
    variable = written.group(1)
    setting["made_into_a_scope_at"] = None
    for other, _tests in statements:
        made = SCOPE_MADE_FROM.match(other.text)
        if made is not None and made.group(1) == variable:
            setting["made_into_a_scope_at"] = where(PARSE_STATEMENTS, other.line)
            return


def add_stacks_changed(given: dict, definition: Definition, sema_definitions: tuple) -> None:
    """Rule 4: for each Sema function the parsing function calls, the stacks
    it pushes or pops."""
    calls = sema_calls_in(definition.node)
    for name, line in calls:
        sema_name = "Sema::" + name
        found = definitions_named(sema_definitions, sema_name)
        if not found:
            add_once(given["sema_calls_not_in_SemaStmt"], sema_name)
            continue
        add_once(given["sema_calls_read"], sema_name)
        add_changes_of(given, found, line)


def add_changes_of(given: dict, sema_definitions: list, called_on_line: int) -> None:
    for sema_definition in sema_definitions:
        changes = stack_changes_in(sema_definition)
        for change in changes:
            change["called_at"] = where(PARSE_STATEMENTS, called_on_line)
            given["stacks_changed"].append(change)


def sema_calls_in(node) -> list:
    """(function, line) for each call `Actions.<function>(...)`."""
    found = []
    calls = calls_in(node)
    for call in calls:
        name = sema_function_called(call)
        if name is not None:
            found.append((name, call.start_point[0] + 1))
    return found


def stack_changes_in(definition: Definition) -> list:
    """Each `push_back` or `pop_back` the Sema function calls on a name it
    does not declare itself."""
    changes = []
    declared_here = names_declared_in(definition.node)
    calls = calls_in(definition.node)
    for call in calls:
        change = stack_change(call, declared_here, definition)
        if change is not None:
            changes.append(change)
    return changes


def stack_change(call, declared_here: list, definition: Definition):
    change = None
    callee = call.child_by_field_name("function")
    if callee is None or callee.type != "field_expression":
        return change
    how = callee.child_by_field_name("field").text.decode()
    if how not in STACK_CHANGES:
        return change
    stack, held_by = stack_named_by(callee.child_by_field_name("argument"))
    if stack is None:
        return change
    if held_by == "" and stack in declared_here:
        return change
    change = {
        "stack": stack,
        "held_by": held_by,
        "how": how,
        "in": definition.name,
        "at": where(SEMA_STATEMENTS, call.start_point[0] + 1),
    }
    return change


def stack_named_by(target) -> tuple:
    """`getCurFunction()->SwitchStack` -> (SwitchStack, getCurFunction());
    `CaseVals` -> (CaseVals, ""); anything else -> (None, "")."""
    named = (None, "")
    if target.type == "field_expression":
        stack = target.child_by_field_name("field").text.decode()
        held_by = target.child_by_field_name("argument").text.decode()
        named = (stack, held_by)
    if target.type == "identifier":
        named = (target.text.decode(), "")
    return named


# join_asks_and_gives (rules 5 and 6)


def join_asks_and_gives(checkout: str, asks: dict, gives: dict) -> dict:
    """kind -> the kinds that give what it asks (its places), through the
    link clang's scope code makes between a getter, a member and a flag, or
    through the stack it asks for; with each step's file and line. A kind
    whose ask cannot be joined is kept in "not_joined", with the reason."""
    link = read_scope_link(checkout)
    stands = {"by_kind": {}, "not_joined": {}, "left_out": []}
    add_all(stands["left_out"], gives["left_out"])
    for kind, kind_asks in asks.items():
        add_stand(stands, checkout, kind, kind_asks, gives["by_kind"], link)
    return stands


def add_stand(stands: dict, checkout: str, kind: str, kind_asks: list, gives_by_kind: dict, link: dict) -> None:
    if len(kind_asks) != 1:
        why = f"its checking function refuses it {len(kind_asks)} times for where it stands; the reader reads one"
        stands["not_joined"][kind] = left_out(kind, kind_asks[0]["refusal_at"], why)
        return
    ask = kind_asks[0]
    what = ask["asks"]["what"]
    if what == ASKS_FOR_A_SCOPE:
        stands["by_kind"][kind] = stand_by_scope(ask, gives_by_kind, link)
        return
    if what == ASKS_FOR_A_STACK:
        stands["by_kind"][kind] = stand_by_stack(checkout, ask, gives_by_kind)
        return
    why = "what its test asks for is not read: " + ask["asks"]["why"]
    stands["not_joined"][kind] = left_out(kind, ask["refusal_at"], why)


def stand_by_scope(ask: dict, gives_by_kind: dict, link: dict) -> dict:
    """getter -> member -> the flags that set it -> the kinds that set a flag;
    and the flags that stop the member being passed on."""
    steps = []
    member = add_getter_step(steps, ask["asks"]["getter"], link)
    flags = add_flag_steps(steps, member, link)
    stop_flags = add_passing_steps(steps, member, link)
    places = givers_of_flags(flags, gives_by_kind)
    stoppers = givers_of_flags(stop_flags, gives_by_kind)
    stand = {
        "asks": ask,
        "link": steps,
        "places": places,
        "passed_on_unless": {"flags": stop_flags, "kinds_that_set_them": stoppers},
    }
    return stand


def stand_by_stack(checkout: str, ask: dict, gives_by_kind: dict) -> dict:
    """stack -> the kinds that push it; and what holds the stack."""
    steps = []
    add_holder_step(steps, checkout, ask["asks"]["held_by"])
    places = pushers_of(ask["asks"]["stack"], gives_by_kind)
    stand = {
        "asks": ask,
        "link": steps,
        "places": places,
        "passed_on_unless": {"flags": [], "kinds_that_set_them": {},
                             "not_read": "a stack has no flag; it is held by " + ask["asks"]["held_by"]},
    }
    return stand


def add_getter_step(steps: list, getter: str, link: dict):
    member = None
    if getter not in link["getters"]:
        steps.append({"step": "the getter returns a member", "getter": getter, "not_read": "no such getter in Scope.h"})
        return member
    returned = link["getters"][getter]
    member = returned["member"]
    steps.append({"step": "the getter returns a member", "getter": getter, "member": member, "at": returned["at"],
                  "text": returned["text"]})
    return member


def add_flag_steps(steps: list, member, link: dict) -> list:
    flags = []
    settings = link["members_set_by_flags"].get(member, [])
    for setting in settings:
        steps.append(setting)
        add_once(flags, setting["flag"])
    return flags


def add_passing_steps(steps: list, member, link: dict) -> list:
    stop_flags = []
    passings = link["members_passed_on"].get(member, [])
    for passing in passings:
        steps.append(passing)
        add_all_once(stop_flags, passing["unless"])
    return stop_flags


def add_holder_step(steps: list, checkout: str, held_by: str) -> None:
    """`getCurFunction()`: what Sema.h's getCurFunction returns."""
    step = {"step": "what holds the stack", "held_by": held_by}
    called = re.match(r"^(\w+)\(\)$", held_by)
    if called is None:
        step["not_read"] = "not a call with no arguments"
        steps.append(step)
        return
    returned = returns_of(checkout, SEMA_HEADER, called.group(1))
    step.update(returned)
    steps.append(step)


def givers_of_flags(flags: list, gives_by_kind: dict) -> dict:
    """kind -> its flag settings that set any of `flags`."""
    givers = {}
    for kind, given in gives_by_kind.items():
        settings = settings_with_flags(given["flags_set"], flags)
        if settings:
            givers[kind] = settings
    return givers


def settings_with_flags(settings: list, flags: list) -> list:
    found = []
    for setting in settings:
        if shares_one(setting["flags"], flags):
            found.append(setting)
    return found


def pushers_of(stack: str, gives_by_kind: dict) -> dict:
    """kind -> its pushes and pops of `stack`, for each kind that pushes it."""
    pushers = {}
    for kind, given in gives_by_kind.items():
        changes = changes_of_stack(given["stacks_changed"], stack)
        if pushed_in(changes):
            pushers[kind] = changes
    return pushers


def changes_of_stack(changes: list, stack: str) -> list:
    found = []
    for change in changes:
        if change["stack"] == stack:
            found.append(change)
    return found


def pushed_in(changes: list) -> bool:
    pushed = False
    for change in changes:
        if change["how"] == "push_back":
            pushed = True
    return pushed


# The scope link (rule 5)


def read_scope_link(checkout: str) -> dict:
    """The getters of Scope.h, each with the member it returns; and from
    Scope.cpp, the flags that set each member, and how a new scope takes it."""
    link = {
        "getters": getters_in(checkout, SCOPE_HEADER),
        "members_set_by_flags": members_set_by_flags(checkout, SCOPE_SOURCE),
        "members_passed_on": members_passed_on(checkout, SCOPE_SOURCE),
    }
    return link


def getters_in(checkout: str, relative: str) -> dict:
    """getter -> the member it returns, for each function whose body is only
    `return <name>;`."""
    getters = {}
    definitions = read_every_function(checkout, relative)
    for definition in definitions:
        statements = statements_under_tests(body_of(definition))
        if len(statements) != 1:
            continue
        returned = RETURNS_A_NAME.match(statements[0][0].text)
        if returned is None:
            continue
        getters[definition.name] = {"member": returned.group(1), "at": where(relative, statements[0][0].line),
                                    "text": statements[0][0].text}
    return getters


def members_set_by_flags(checkout: str, relative: str) -> dict:
    """member -> each place where a flag sets it to its own scope: `if (X &
    Flag) Member = this;`."""
    members = {}
    definitions = read_every_function(checkout, relative)
    for definition in definitions:
        statements = statements_under_tests(body_of(definition))
        for statement, tests in statements:
            add_member_set_by_a_flag(members, statement, tests, definition, relative)
    return members


def add_member_set_by_a_flag(members: dict, statement, tests: tuple, definition: Definition, relative: str) -> None:
    set_here = MEMBER_SET_TO_ITS_OWN_SCOPE.match(statement.text)
    if set_here is None or not tests:
        return
    test = tests[-1]
    flag = flag_tested_on(test.code)
    if flag is None or test.taken != "true":
        return
    member = set_here.group(1)
    setting = {
        "step": "a flag sets the member to its own scope",
        "flag": flag,
        "member": member,
        "in": definition.name,
        "at": where(relative, statement.line),
        "text": statement.text,
        "test": test.code.text,
        "test_at": where(relative, test.code.line),
    }
    add_to_list(members, member, setting)


def members_passed_on(checkout: str, relative: str) -> dict:
    """member -> each place where a new scope takes it from the scope around
    it, `Member = parent->Member;`, with the flags whose `!(X & Flag)` in the
    test stops that."""
    members = {}
    definitions = read_every_function(checkout, relative)
    for definition in definitions:
        statements = statements_under_tests(body_of(definition))
        for statement, tests in statements:
            add_member_passed_on(members, statement, tests, definition, relative)
    return members


def add_member_passed_on(members: dict, statement, tests: tuple, definition: Definition, relative: str) -> None:
    taken = MEMBER_TAKEN_FROM_THE_SCOPE_AROUND.match(statement.text)
    if taken is None or taken.group(1) != taken.group(2) or not tests:
        return
    test = tests[-1]
    if test.taken != "true":
        return
    member = taken.group(1)
    unless = flags_tested_off(test.code)
    passing = {
        "step": "a new scope takes the member from the scope around it",
        "member": member,
        "in": definition.name,
        "at": where(relative, statement.line),
        "text": statement.text,
        "test": test.code.text,
        "test_at": where(relative, test.code.line),
        "unless": unless,
    }
    add_to_list(members, member, passing)


def flag_tested_on(code):
    """`X & Flag` -> Flag; anything else -> None."""
    flag = None
    if code.form == "binary" and code.parts[0] == "&" and code.parts[2].form == "name":
        flag = code.parts[2].parts[0]
    return flag


def flags_tested_off(code) -> list:
    """Every Flag in a `!(X & Flag)` inside a test."""
    flags = []
    collect_flags_tested_off(code, flags)
    return flags


def collect_flags_tested_off(code, flags: list) -> None:
    if not isinstance(code, cpp_code.Code):
        return
    if code.form == "not":
        flag = flag_tested_on(code.parts[0])
        if flag is not None:
            flags.append(flag)
    for part in code.parts:
        collect_flags_tested_off(part, flags)


def returns_of(checkout: str, relative: str, name: str) -> dict:
    """What a function `name` of `relative` returns, when its body is one
    `return` statement."""
    returned = {"not_read": f"no function {name} in {relative} with a body of one `return`"}
    definitions = definitions_named(read_every_function(checkout, relative), name)
    for definition in definitions:
        statements = statements_under_tests(body_of(definition))
        if len(statements) == 1 and statements[0][0].form == "return":
            returned = {"function": name, "at": where(relative, statements[0][0].line), "text": statements[0][0].text}
    return returned


# read_function_rules (rules 7 to 10)


def read_function_rules(checkout: str, gives: dict) -> dict:
    """What `goto m;`, `&&m` and `goto *a;` need in the function they stand
    in, and the places a jump may not enter, read from clang's code."""
    kinds = concrete_kinds(checkout)
    texts = diagnostic_texts(checkout)
    label = read_label_rule(checkout, gives, kinds, texts)
    address = read_address_rule(checkout, kinds, texts)
    protected = read_protected_places(checkout, texts, address)
    rules = {"label_in_the_function": label, "address_taken_in_the_function": address,
             "places_a_jump_may_not_enter": protected}
    return rules


# Rule 7: a label of the same name in the function


def read_label_rule(checkout: str, gives: dict, kinds: dict, texts: dict) -> dict:
    """Rule 7: `goto m;` and `&&m` need the label statement `m:` in the same
    function."""
    refusals = refusals_named(checkout, SEMA_DECLARATIONS, LABEL_REFUSAL, texts)
    refused_when = values_of_the_name_tested(checkout, refusals)
    checked_from = calls_of(checkout, SEMA_DECLARATIONS, functions_of(refusals))
    popped_from = calls_of(checkout, PARSER, functions_of(checked_from))
    made_in = uses_of_name(checkout, SEMA_LOOKUP, LABEL_MADE)
    held_by = scopes_a_label_is_pushed_onto(checkout, made_in)
    link = link_of_the_scopes(checkout, held_by, gives)
    users = label_users(checkout, kinds, functions_of(statements_read(made_in)))
    givers = label_givers(checkout, refused_when, kinds)
    outside = refusals_named(checkout, PARSE_EXPRESSIONS, OUTSIDE_A_FUNCTION_REFUSAL, texts)
    rule = {
        "refusal": refusals,
        "refused_when_the_label_is_given": refused_when,
        "checked_when_its_scope_is_popped": checked_from,
        "scopes_popped_by": popped_from,
        "made_by": statements_read(made_in),
        "held_by": held_by,
        "the_scope_that_holds_it": link,
        "looked_up_by": users,
        "given_its_statement_by": givers,
        "refusal_outside_a_function": outside,
        "about": kinds_of_users(users, givers, False),
        "needs": kinds_of_users(users, givers, True),
    }
    return rule


def values_of_the_name_tested(checkout: str, refusals: list) -> list:
    """When a refusal's innermost test is a name (`if (Diagnose)`), each value
    its function gives that name, with the tests it stands under."""
    values = []
    for refusal in refusals:
        add_values_of_the_name_tested(values, checkout, refusal)
    return values


def add_values_of_the_name_tested(values: list, checkout: str, refusal: dict) -> None:
    if not refusal["under"]:
        return
    name = refusal["under"][-1]["test"]
    if re.match(r"^\w+$", name) is None:
        return
    definition = definition_at(checkout, refusal["file"], refusal["in"], refusal["function_line"])
    given = values_given_to_names(definition.node)
    for value in given.get(name, []):
        values.append(value_read(refusal["file"], definition, name, value))


def value_read(relative: str, definition: Definition, name: str, value) -> dict:
    read = {
        "name": name,
        "value": short_text(value),
        "in": definition.name,
        "at": where(relative, line_of(value)),
        "under": tests_around(value, relative),
        "getters_called": getters_called_in(value),
    }
    return read


def getters_called_in(node) -> list:
    """`L->getStmt() == nullptr` -> [getStmt]."""
    getters = []
    calls = calls_in(node)
    for call in calls:
        callee = call.child_by_field_name("function")
        if callee is None or callee.type != "field_expression":
            continue
        field = callee.child_by_field_name("field").text.decode()
        if field.startswith("get"):
            add_once(getters, field)
    return getters


def scopes_a_label_is_pushed_onto(checkout: str, made_in: list) -> list:
    """In each function that makes a label, every `PushOnScopeChains(Res, S,
    ...)`, with each value given to `S` under the same tests."""
    pushes = []
    functions = definitions_of_uses(made_in)
    for definition in functions:
        add_pushes_in(pushes, checkout, definition)
    return pushes


def add_pushes_in(pushes: list, checkout: str, definition: Definition) -> None:
    calls = calls_named(definition.node, PUSHED_ONTO_A_SCOPE)
    given = values_given_to_names(definition.node)
    for call in calls:
        pushes.append(push_read(definition, call, given))


def push_read(definition: Definition, call, given: dict) -> dict:
    arguments = arguments_of(call)
    scope = ""
    if len(arguments) > 1:
        scope = arguments[1].text.decode()
    under = tests_around(call, SEMA_LOOKUP)
    read = {
        "in": definition.name,
        "at": where(SEMA_LOOKUP, line_of(call)),
        "text": short_text(statement_of(call)),
        "under": under,
        "scope": scope,
        "scope_is": values_under_the_same_tests(given.get(scope, []), under),
    }
    return read


def values_under_the_same_tests(values: list, under: list) -> list:
    """The values given under exactly the tests `under`."""
    found = []
    for value in values:
        if tests_texts(tests_around(value, SEMA_LOOKUP)) == tests_texts(under):
            found.append({"value": short_text(value), "at": where(SEMA_LOOKUP, line_of(value)),
                          "getters_called": getters_called_in(value)})
    return found


def link_of_the_scopes(checkout: str, held_by: list, gives: dict) -> list:
    """For each scope a label is pushed onto that a getter returns
    (`CurScope->getFnParent()`): rule 5's link, and the statements that name
    the flag that sets the getter's member."""
    links = []
    link = read_scope_link(checkout)
    getters = getters_of_pushes(held_by)
    for getter in getters:
        links.append(link_of_a_getter(checkout, getter, link, gives))
    return links


def getters_of_pushes(held_by: list) -> list:
    getters = []
    for push in held_by:
        for value in push["scope_is"]:
            add_all_once(getters, value["getters_called"])
    return getters


def link_of_a_getter(checkout: str, getter: str, link: dict, gives: dict) -> dict:
    steps = []
    member = add_getter_step(steps, getter, link)
    flags = add_flag_steps(steps, member, link)
    stop_flags = add_passing_steps(steps, member, link)
    read = {
        "getter": getter,
        "link": steps,
        "flags": flags,
        "passed_on_unless": stop_flags,
        "statements_that_set_the_flags": givers_of_flags(flags, gives["by_kind"]),
        "set_outside_the_statements_in": flags_named_in(checkout, PARSER, flags),
    }
    return read


def flags_named_in(checkout: str, relative: str, flags: list) -> list:
    """Every statement of `relative` that names `Scope::<flag>`."""
    found = []
    for flag in flags:
        uses = uses_of_name(checkout, relative, "Scope::" + flag)
        add_all(found, statements_read(uses))
    return found


def label_users(checkout: str, kinds: dict, label_functions: list) -> list:
    """Each parsing function that looks a label up (`Actions.<F>(...)`, F the
    function that makes a label), with the Sema call it passes the label to,
    and that call's kind."""
    users = []
    names = short_names(label_functions)
    for relative in (PARSE_STATEMENTS, PARSE_EXPRESSIONS):
        for name in names:
            add_label_users(users, checkout, kinds, relative, name)
    return users


def add_label_users(users: list, checkout: str, kinds: dict, relative: str, name: str) -> None:
    uses = uses_of_name(checkout, relative, name)
    for use in uses:
        users.append(label_user(checkout, kinds, use))


def label_user(checkout: str, kinds: dict, use: Use) -> dict:
    call = enclosing_call(use.node)
    given_to = name_given(call)
    user = statement_read(use)
    user["label_given_to"] = given_to
    user["passed_to"] = []
    if given_to is None:
        user["not_read"] = "the label it looks up is given to no name"
        return user
    sema_calls = sema_calls_taking(use.definition.node, given_to)
    for sema_call in sema_calls:
        user["passed_to"].append(sema_call_read(checkout, kinds, use.relative, sema_call))
    return user


def sema_calls_taking(node, name: str) -> list:
    """Each `Actions.ActOn...(...)` call under `node` with `name` among its
    arguments."""
    found = []
    calls = calls_in(node)
    for call in calls:
        called = sema_function_called(call)
        if called is None or BUILDING_CALL.match(called) is None:
            continue
        if argument_named(call, name):
            found.append(call)
    return found


def sema_call_read(checkout: str, kinds: dict, relative: str, call) -> dict:
    """The kind a Sema call builds: by rule 3's ending of its name, or else
    by what the Sema function returns."""
    called = sema_function_called(call)
    read = {"call": "Actions." + called, "at": where(relative, line_of(call)), "kind": None}
    kind = kind_ending(BUILDING_CALL.match(called).group(1), kinds)
    if kind is not None:
        read["kind"] = kind
        read["kind_read_from"] = "the call's name (rule 3)"
        return read
    returned = kinds_a_sema_function_returns(checkout, kinds, "Sema::" + called)
    if len(returned) == 1:
        read["kind"] = returned[0]["kind"]
        read["kind_read_from"] = "what " + "Sema::" + called + " returns, " + returned[0]["at"]
    return read


def kinds_a_sema_function_returns(checkout: str, kinds: dict, name: str) -> list:
    """The kinds `new (Context) <Kind>(...)` or `<Kind>::Create(...)` that a
    Sema function of SemaStmt.cpp or SemaExpr.cpp returns."""
    found = []
    for relative in (SEMA_STATEMENTS, SEMA_EXPRESSIONS):
        definitions = definitions_named(read_every_function(checkout, relative), name)
        for definition in definitions:
            add_kinds_returned(found, definition, kinds, relative)
    return found


def add_kinds_returned(found: list, definition: Definition, kinds: dict, relative: str) -> None:
    returned = returned_values(definition.node)
    for value in returned:
        kind = kind_made_by(value, kinds)
        if kind is not None:
            found.append({"kind": kind, "at": where(relative, line_of(value))})


def kind_made_by(value, kinds: dict):
    """`new (Context) AddrLabelExpr(...)` -> AddrLabelExpr; `CaseStmt::Create(...)` -> CaseStmt."""
    kind = None
    made = None
    if value.type == "new_expression":
        made = value.child_by_field_name("type")
    if value.type == "call_expression":
        made = created_by(value)
    if made is not None and made.text.decode() in kinds:
        kind = made.text.decode()
    return kind


def created_by(call):
    """`K::Create(...)` -> the node of K; anything else -> None."""
    made = None
    callee = call.child_by_field_name("function")
    if callee is None or callee.type != "qualified_identifier":
        return made
    name = callee.child_by_field_name("name")
    if name is not None and name.text.decode() == "Create":
        made = callee.child_by_field_name("scope")
    return made


def label_givers(checkout: str, refused_when: list, kinds: dict) -> list:
    """For each `getX` a refusal's values call on the label, each Sema
    function of SemaStmt.cpp that calls `setX`, with its kind (rule 3's
    ending of its name)."""
    givers = []
    getters = getters_of_values(refused_when)
    for getter in getters:
        add_givers_of(givers, checkout, kinds, "set" + getter[3:])
    return givers


def getters_of_values(values: list) -> list:
    getters = []
    for value in values:
        add_all_once(getters, value["getters_called"])
    return getters


def add_givers_of(givers: list, checkout: str, kinds: dict, setter: str) -> None:
    uses = uses_of_name(checkout, SEMA_STATEMENTS, setter)
    for use in uses:
        giver = statement_read(use)
        giver["setter"] = setter
        giver["kind"] = kind_named_by(use.definition.name, CHECKING_FUNCTION, "", kinds)
        givers.append(giver)


def kinds_of_users(users: list, givers: list, giving: bool) -> list:
    """The kinds the label rule is about (`giving` False: the ones that look
    the label up and do not give it its statement) or the kinds they need
    (`giving` True)."""
    giving_kinds = kinds_of_givers(givers)
    found = []
    for user in users:
        for passed in user["passed_to"]:
            kind = passed["kind"]
            if kind is not None and (kind in giving_kinds) == giving:
                add_once(found, kind)
    return found


def kinds_of_givers(givers: list) -> list:
    kinds = []
    for giver in givers:
        if giver["kind"] is not None:
            add_once(kinds, giver["kind"])
    return kinds


# Rule 8: some label's address taken in the function


def read_address_rule(checkout: str, kinds: dict, texts: dict) -> dict:
    """Rule 8: `goto *a;` needs some label's address taken in the same
    function."""
    refusals = refusals_named(checkout, JUMPS, ADDRESS_REFUSAL, texts)
    returns_before = returns_before_refusals(checkout, refusals)
    needs_lists = lists_found_empty(refusals)
    about_lists = lists_found_empty(returns_before)
    filled = lists_filled(checkout, kinds, needs_lists + about_lists)
    walked_from = where_the_lists_are_filled_from(checkout, refusals, filled)
    started = where_the_checker_is_started(checkout, functions_of(walked_from))
    rule = {
        "refusal": refusals,
        "returns_before_it": returns_before,
        "lists_filled": filled,
        "filled_by_walking": walked_from,
        "the_checker_is_started": started,
        "about": kinds_pushed_onto(filled, about_lists),
        "needs": kinds_pushed_onto(filled, needs_lists),
    }
    return rule


def returns_before_refusals(checkout: str, refusals: list) -> list:
    """Each `return` of a refusal's function that comes before it, with its
    tests."""
    found = []
    for refusal in refusals:
        definition = definition_at(checkout, refusal["file"], refusal["in"], refusal["function_line"])
        returns = return_statements(definition.node)
        for statement in returns:
            if line_of(statement) < refusal["line"]:
                found.append(read_node(refusal["file"], definition, statement))
    return found


def lists_found_empty(reads: list) -> list:
    """Each `X` of a test `X.empty()` taken true that one of `reads` stands
    under: the lists empty where it stands."""
    lists = []
    for read in reads:
        for test in read["under"]:
            add_list_found_empty(lists, test)
    return lists


def add_list_found_empty(lists: list, test: dict) -> None:
    found = LIST_FOUND_EMPTY.match(test["test"])
    if found is not None and test["taken"] == "true":
        add_once(lists, found.group(1))


def lists_filled(checkout: str, kinds: dict, lists: list) -> dict:
    """list -> each `list.push_back(...)` of JumpDiagnostics.cpp, with the
    kind of the case it stands in, and the tests that skip it."""
    filled = {}
    for name in lists:
        filled[name] = pushes_onto(checkout, kinds, name)
    return filled


def pushes_onto(checkout: str, kinds: dict, name: str) -> list:
    pushes = []
    uses = member_calls(checkout, JUMPS, name, "push_back")
    for use in uses:
        push = statement_read(use)
        push["kinds"] = kinds_of_cases(push["under"], kinds)
        push["skipped_when"] = leaving_tests_before(use.node, JUMPS)
        pushes.append(push)
    return pushes


def kinds_of_cases(under: list, kinds: dict) -> list:
    """The kinds of the `case Stmt::<Kind>Class:` a statement stands in."""
    found = []
    for test in under:
        if test["taken"] != "this case":
            continue
        named = CASE_OF_A_KIND.findall(test["test"])
        for kind in named:
            if kind in kinds:
                add_once(found, kind)
    return found


def kinds_pushed_onto(filled: dict, lists: list) -> list:
    found = []
    for name in lists:
        for push in filled.get(name, []):
            add_all_once(found, push["kinds"])
    return found


def where_the_lists_are_filled_from(checkout: str, refusals: list, filled: dict) -> list:
    """The function that calls both the function the lists are filled in and
    the refusal's function: its calls of each, and their arguments."""
    found = []
    fillers = short_names(functions_of_pushes(filled))
    refusing = short_names(functions_of(refusals))
    definitions = read_every_function(checkout, JUMPS)
    for definition in definitions:
        if calls_one_of(definition, fillers) and calls_one_of(definition, refusing):
            add_calls_in(found, definition, fillers + refusing)
    return found


def functions_of_pushes(filled: dict) -> list:
    functions = []
    for pushes in filled.values():
        add_all_once(functions, functions_of(pushes))
    return functions


def calls_one_of(definition: Definition, names: list) -> bool:
    found = False
    for name in names:
        if calls_named(definition.node, name):
            found = True
    return found


def add_calls_in(found: list, definition: Definition, names: list) -> None:
    for name in names:
        calls = calls_named(definition.node, name)
        for call in calls:
            read = read_node(JUMPS, definition, call)
            read["parameters"] = parameters_text(definition)
            found.append(read)


def where_the_checker_is_started(checkout: str, walking: list) -> dict:
    """Where the walking function's class is made (`Sema::DiagnoseInvalidJumps`),
    where that function is called (SemaDecl.cpp), and when (ScopeInfo.h)."""
    classes = classes_of(walking)
    made = uses_outside_their_class(checkout, JUMPS, classes)
    called = calls_of(checkout, SEMA_DECLARATIONS, functions_of(made))
    when = named_function_returns(checkout, SCOPE_INFO, tested_function_names(called))
    started = {"made_in": made, "called_in": called, "runs_when": when}
    return started


def tested_function_names(reads: list) -> list:
    """`FSI->NeedsScopeChecking() && ...` -> [NeedsScopeChecking]."""
    names = []
    for read in reads:
        for test in read["under"]:
            found = re.findall(r"->(\w+)\(\)", test["test"])
            add_all_once(names, found)
    return names


def named_function_returns(checkout: str, relative: str, names: list) -> list:
    found = []
    definitions = read_every_function(checkout, relative)
    for definition in definitions:
        if definition.name not in names:
            continue
        returns = return_statements(definition.node)
        for statement in returns:
            found.append(read_node(relative, definition, statement))
    return found


# Rules 9 and 10: the places a jump may not enter


def read_protected_places(checkout: str, texts: dict, address: dict) -> dict:
    """Rule 9: each place JumpDiagnostics.cpp records with an in-note, and
    the in-notes that are only a warning in C; rule 10: the refusals for a
    jump into a place, and the jumps each refuses."""
    notes = notes_recorded(checkout, texts)
    warned = in_notes_only_warned_in_c(checkout)
    refusals = entering_refusals(checkout, texts, address)
    protected = {
        "places": notes_of_role(notes, "in"),
        "out_notes": notes_of_role(notes, "out"),
        "other_notes": notes_of_role(notes, "other"),
        "only_a_warning_in_c": warned,
        "refusals": refusals,
        "leaving": not_read("the out-notes and the tests that use them are kept as evidence;"
                            " whether a jump may leave a place is not drawn from them"),
    }
    return protected


def notes_recorded(checkout: str, texts: dict) -> list:
    """Each `diag::note_...` JumpDiagnostics.cpp names, with its role (rule 9)."""
    notes = []
    uses = uses_matching(checkout, JUMPS, NOTE)
    for use in uses:
        notes.append(note_read(use, texts))
    return notes


def note_read(use: Use, texts: dict) -> dict:
    note = NOTE.match(use.node.text.decode()).group(1)
    read = statement_read(use)
    read["note"] = note
    read["says"] = texts.get(note, {}).get("text")
    read["says_at"] = texts.get(note, {}).get("at")
    read["role"], read["recorded_by"] = role_of_a_note(use)
    return read


def role_of_a_note(use: Use) -> tuple:
    """("in" or "out", the recording call's text), or ("other", "")."""
    role = role_in_a_record(use.node)
    if role[0] != "other":
        return role
    name = name_given(use.node)
    if name is None:
        return role
    records = calls_passing(use.definition.node, name)
    for record in records:
        role = role_in_a_record(record)
    return role


def role_in_a_record(node) -> tuple:
    """The role of the argument `node` stands in, in a `GotoScope(...)`,
    `ScopePair(...)` or `Scopes.emplace_back(...)`."""
    role = ("other", "")
    argument, call = argument_and_call(node)
    while call is not None:
        record = record_named(call)
        if record is not None:
            role = role_at(record, argument_index(call, argument), call)
            break
        argument, call = argument_and_call(call)
    return role


def role_at(record: str, index: int, call) -> tuple:
    in_at, out_at = SCOPE_RECORDS[record]
    role = ("other", short_text(call))
    if index == in_at:
        role = ("in", short_text(call))
    if index == out_at:
        role = ("out", short_text(call))
    return role


def record_named(call):
    """`GotoScope(...)`, `ScopePair(...)`, `X.emplace_back(...)` -> its name."""
    record = None
    callee = call.child_by_field_name("function")
    if callee is None:
        return record
    name = callee.text.decode()
    if callee.type == "field_expression":
        name = callee.child_by_field_name("field").text.decode()
    if name in SCOPE_RECORDS:
        record = name
    return record


def calls_passing(node, name: str) -> list:
    """Each call under `node` with the name `name` as an argument, and a
    record's role for it."""
    found = []
    calls = calls_in(node)
    for call in calls:
        if record_named(call) is not None and argument_named(call, name):
            found.append(argument_node_named(call, name))
    return found


def notes_of_role(notes: list, role: str) -> list:
    found = []
    for note in notes:
        if note["role"] == role:
            found.append(note)
    return found


def in_notes_only_warned_in_c(checkout: str) -> list:
    """Rule 9: each `Is...Warning` function whose return, and the tests of its
    calls, hold in C (`!S.getLangOpts().CPlusPlus`, nothing that needs C++),
    with the notes it names."""
    warned = []
    definitions = read_every_function(checkout, JUMPS)
    for definition in definitions:
        if WARNING_FUNCTION.match(definition.name) is None:
            continue
        warned.append(warning_function_read(checkout, definition))
    return warned


def warning_function_read(checkout: str, definition: Definition) -> dict:
    returns = return_statements(definition.node)
    texts = []
    notes = []
    for statement in returns:
        texts.append(short_text(statement))
        add_all_once(notes, notes_named_in(statement))
    calls = calls_of(checkout, JUMPS, [definition.name])
    for call in calls:
        texts.append(call["condition"])
    read = {
        "function": definition.name,
        "at": where(JUMPS, definition.line),
        "returns": texts[:len(returns)],
        "called_under": calls,
        "notes": notes,
        "holds_in_c": holds_in_c(texts),
    }
    return read


def holds_in_c(texts: list) -> bool:
    says_c = False
    needs_cpp = False
    for text in texts:
        if text is None:
            continue
        if NEEDS_C in text:
            says_c = True
        if NEEDS_CPP.search(text) is not None:
            needs_cpp = True
    holds = says_c and not needs_cpp
    return holds


def notes_named_in(node) -> list:
    notes = []
    names = nodes_matching(node, NOTE)
    for name in names:
        add_once(notes, NOTE.match(name.text.decode()).group(1))
    return notes


def entering_refusals(checkout: str, texts: dict, address: dict) -> dict:
    """Rule 10: refusal -> the way to it, the jumps it refuses, and whether a
    test on the way names the in-note."""
    refusals = {}
    for diagnostic in ENTERING_REFUSALS:
        refusals[diagnostic] = entering_refusal(checkout, texts, address, diagnostic)
    return refusals


def entering_refusal(checkout: str, texts: dict, address: dict, diagnostic: str) -> dict:
    named = refusals_named(checkout, JUMPS, diagnostic, texts)
    way = []
    jumps = []
    for read in named:
        add_way_and_jumps(way, jumps, checkout, read, address)
    tests = tests_on_the_way(named + way)
    read = {
        "says": texts.get(diagnostic, {}).get("text"),
        "says_at": texts.get(diagnostic, {}).get("at"),
        "named_at": named,
        "the_way_to_it": way,
        "jumps": jumps,
        "tests_the_in_note": tests_naming(tests, IN_NOTE_TESTED),
        "tests_the_out_note": tests_naming(tests, OUT_NOTE_TESTED),
    }
    return read


def add_way_and_jumps(way: list, jumps: list, checkout: str, read: dict, address: dict) -> None:
    """One statement naming the refusal: its way (rule 10), and the jumps it
    refuses: the kinds its own tests name, or when they name none, the kinds
    the tests on its way name."""
    own_way = []
    add_way_of(own_way, checkout, read)
    add_all_once(way, own_way)
    own = kinds_in_tests(checkout, read["under"])
    if own:
        add_all_once(jumps, own)
        return
    add_all_once(jumps, jumps_refused(checkout, tests_on_the_way(own_way), own_way, address))


def kinds_in_tests(checkout: str, tests: list) -> list:
    found = []
    for test in tests:
        add_all_once(found, kinds_named_in_text(checkout, test["test"]))
    return found


def add_way_of(way: list, checkout: str, read: dict) -> None:
    """When the statement passes the refusal to a function of the file, that
    function's statements naming the parameter that receives it, and the
    pushes onto the lists their tests check; when it emits it, the calls of
    the function it stands in, two deep."""
    receivers = functions_receiving(checkout, read)
    if receivers:
        add_way_through_a_parameter(way, receivers, read["argument_of"]["index"])
        return
    if read["emitted"]:
        add_calls_back(way, checkout, [read["in"]], 2)


def functions_receiving(checkout: str, read: dict) -> list:
    """The definitions in JumpDiagnostics.cpp of the function a refusal is
    passed to (`CheckJump(..., diag::err_goto_into_protected_scope, ...)`)."""
    found = []
    passed = read["argument_of"]
    if passed is None or passed["call"] is None:
        return found
    definitions = read_every_function(checkout, JUMPS)
    for definition in definitions:
        if definition.name.split("::")[-1] == passed["call"]:
            found.append(definition)
    return found


def add_way_through_a_parameter(way: list, receivers: list, index: int) -> None:
    for definition in receivers:
        parameter = parameter_name_at(definition, index)
        if parameter is None:
            continue
        uses = uses_in_definition(definition, parameter, JUMPS)
        for use in uses:
            add_parameter_use(way, use, parameter)


def add_parameter_use(way: list, use: Use, parameter: str) -> None:
    read = statement_read(use)
    read["names_the_parameter"] = parameter
    add_once(way, read)
    lists = lists_in_tests([read])
    for name in lists:
        uses = member_calls_in(use.definition, name, "push_back", JUMPS)
        add_all_once(way, statements_read(uses))


def add_calls_back(way: list, checkout: str, functions: list, depth: int) -> None:
    if depth == 0:
        return
    calls = calls_of(checkout, JUMPS, functions)
    add_all_once(way, calls)
    add_calls_back(way, checkout, functions_of(calls), depth - 1)


def lists_in_tests(reads: list) -> list:
    """Each `X` of an `X.empty()` that a test of `reads` names."""
    lists = []
    for read in reads:
        for test in read["under"]:
            add_all_once(lists, LIST_TESTED.findall(test["test"]))
    return lists


def tests_on_the_way(reads: list) -> list:
    tests = []
    for read in reads:
        for test in read["under"]:
            add_once(tests, test)
    return tests


def tests_naming(tests: list, pattern) -> list:
    found = []
    for test in tests:
        if pattern.search(test["test"]) is not None:
            found.append(test)
    return found


def jumps_refused(checkout: str, tests: list, reads: list, address: dict) -> list:
    """The kinds the tests on a way name (an abstract kind stands for the
    kinds below it), and rule 8's dependents where the way passes through the
    function of rule 8's refusal."""
    jumps = kinds_in_tests(checkout, tests)
    if shares_one(functions_of(reads), functions_of(address["refusal"])):
        add_all_once(jumps, address["about"])
    return jumps


def kinds_named_in_text(checkout: str, text: str) -> list:
    """Each kind a text names in `dyn_cast<K>`, `cast<K>`, `isa<K>`, or as the
    type of a name it declares (`SwitchCase *SC = ...`); an abstract kind
    stands for the kinds below it."""
    found = []
    named = KIND_CAST.findall(text) + KIND_DECLARED.findall(text)
    for name in named:
        add_all_once(found, concrete_kinds_below(checkout, name))
    return found


# read_switch_rules (rule 11)


def read_switch_rules(checkout: str) -> dict:
    """Rule 11: refusal -> where clang refuses a `case` or `default` for the
    others of its switch, and the kinds it is about."""
    texts = diagnostic_texts(checkout)
    rules = {}
    for diagnostic in SWITCH_REFUSALS:
        rules[diagnostic] = switch_rule(checkout, texts, diagnostic)
    return rules


def switch_rule(checkout: str, texts: dict, diagnostic: str) -> dict:
    refusals = refusals_named(checkout, SEMA_STATEMENTS, diagnostic, texts)
    about = []
    for refusal in refusals:
        add_all_once(about, kinds_a_refusal_is_about(checkout, refusal))
    added_by = uses_of_name(checkout, SEMA_STATEMENTS, "addSwitchCase")
    rule = {
        "says": texts.get(diagnostic, {}).get("text"),
        "says_at": texts.get(diagnostic, {}).get("at"),
        "refusal": refusals,
        "about": about,
        "a_case_is_added_to_its_switch_by": statements_read(added_by),
    }
    return rule


def kinds_a_refusal_is_about(checkout: str, refusal: dict) -> list:
    """Rule 11, over the `if` tests the refusal stands under (not its loops):
    the kinds a test casts to (`dyn_cast<DefaultStmt>(SC)`), the declared type
    of a name that is the whole test (`TheDefaultStmt`), and the declared
    types of the values pushed onto a list a test uses (`CaseVals`)."""
    definition = definition_at(checkout, refusal["file"], refusal["in"], refusal["function_line"])
    types = declared_types(definition.node)
    found = []
    tests = branch_tests(refusal["under"])
    for test in tests:
        add_kinds_of_a_test(found, checkout, definition, types, test["test"])
    return found


def branch_tests(under: list) -> list:
    found = []
    for test in under:
        if test["taken"] in ("true", "false"):
            found.append(test)
    return found


def add_kinds_of_a_test(found: list, checkout: str, definition: Definition, types: dict, text: str) -> None:
    for name in KIND_CAST.findall(text):
        add_all_once(found, concrete_kinds_below(checkout, name))
    whole = A_NAME.match(text)
    if whole is not None:
        add_all_once(found, kinds_in_types(checkout, types.get(whole.group(1), [])))
    for name in A_LIST_USED.findall(text):
        add_kinds_pushed_onto(found, checkout, definition, types, name)


def add_kinds_pushed_onto(found: list, checkout: str, definition: Definition, types: dict, name: str) -> None:
    pushed = member_calls_in(definition, name, "push_back", "")
    for use in pushed:
        call = enclosing_call(use.node)
        for argument in names_in_node(arguments_node(call)):
            add_all_once(found, kinds_in_types(checkout, types.get(argument, [])))


def kinds_in_types(checkout: str, types: list) -> list:
    found = []
    for written in types:
        for word in WORD.findall(written):
            add_all_once(found, concrete_kinds_below(checkout, word))
    return found


def declared_types(node) -> dict:
    """name -> the types it is declared with under `node`, its own and the
    `*` of its declarator (`CaseStmt *CS`)."""
    types = {}
    declarations = nodes_of_type(node, ("declaration", "parameter_declaration"))
    for declaration in declarations:
        add_declared_types(types, declaration)
    return types


def add_declared_types(types: dict, declaration) -> None:
    written = declaration.child_by_field_name("type")
    if written is None:
        return
    declarators = declaration.children_by_field_name("declarator")
    for declarator in declarators:
        name = cpp_code.declared_name(declarator)
        if name:
            add_to_list(types, name, written.text.decode())


# combine


def combine(stands: dict, function_wide: dict, switch_wide: dict, listings_path: str,
            label_address_path: str) -> dict:
    """One result per dependent listing: placed by the statements around it
    (rules 1 to 6), or by a rule over the whole function (rules 7 and 8);
    with what clang refuses among one switch's (rule 11) and the places a
    jump may not enter (rules 9 and 10), where they apply."""
    listings = dependent_candidates(listings_path, label_address_path)
    places = {"by_listing": {}, "left_out": [], "function_rules": function_wide, "switch_rules": switch_wide}
    add_all(places["left_out"], stands["left_out"])
    listed_kinds = []
    for listing in listings:
        add_listing(places, listing, stands, function_wide, switch_wide, listed_kinds)
    add_kinds_with_no_listing(places, stands, listed_kinds)
    return places


def dependent_candidates(listings_path: str, label_address_path: str) -> list:
    listings = read_listings(listings_path)
    listings.append(label_address_listing(label_address_path))
    return listings


def label_address_listing(label_address_path: str) -> dict:
    """label_address.json's `&&m`, shaped as a listing of kinds_forms.json."""
    with open(label_address_path, encoding="utf-8") as label_address_file:
        operator = json.load(label_address_file)["operator"]
    listing = {
        "position": None,
        "name": operator["name"],
        "template": operator["template"],
        "parsed_as_written": operator["parsed_as_written"],
        "listed_in": os.path.basename(label_address_path),
    }
    return listing


def add_listing(places: dict, listing: dict, stands: dict, function_wide: dict, switch_wide: dict,
                listed_kinds: list) -> None:
    kind = listing["name"]
    combined = None
    if kind in stands["by_kind"]:
        combined = placed_listing(listing, stands["by_kind"][kind])
    if kind in stands["not_joined"]:
        combined = unplaced_listing(listing, stands["not_joined"][kind])
    if combined is None:
        combined = listing_by_function_rules(listing, function_wide)
    if combined is None:
        return
    add_once(listed_kinds, kind)
    combined["one_switch"] = switch_rules_about(kind, switch_wide)
    combined["may_not_enter"] = entering_rules_about(kind, function_wide)
    places["by_listing"][listing["template"]] = combined


def placed_listing(listing: dict, stand: dict) -> dict:
    placed = {
        "position": listing["position"],
        "kind": listing["name"],
        "parsed_as_written": listing["parsed_as_written"],
        "placed": BY_THE_SCOPES_AROUND_IT,
        "places": list(stand["places"]),
        "asks": stand["asks"],
        "link": stand["link"],
        "givers": stand["places"],
        "passed_on_unless": stand["passed_on_unless"],
        "needs_in_the_same_function": None,
    }
    return placed


def unplaced_listing(listing: dict, not_joined: dict) -> dict:
    unplaced = {
        "position": listing["position"],
        "kind": listing["name"],
        "parsed_as_written": listing["parsed_as_written"],
        "placed": None,
        "places": None,
        "not_read": not_joined,
        "needs_in_the_same_function": None,
    }
    return unplaced


def listing_by_function_rules(listing: dict, function_wide: dict):
    """A listing rule 7 or rule 8 is about: what it needs in the function."""
    combined = None
    kind = listing["name"]
    label = function_wide["label_in_the_function"]
    address = function_wide["address_taken_in_the_function"]
    if kind in label["about"]:
        combined = needing_listing(listing, label, True)
    if kind in address["about"]:
        combined = needing_listing(listing, address, False)
    return combined


def needing_listing(listing: dict, rule: dict, with_the_same_label: bool) -> dict:
    needing = {
        "position": listing["position"],
        "kind": listing["name"],
        "parsed_as_written": listing["parsed_as_written"],
        "placed": BY_THE_WHOLE_FUNCTION,
        "places": None,
        "needs_in_the_same_function": {
            "kinds": rule["needs"],
            "with_the_same_label": with_the_same_label,
            "refusal": refusal_names(rule["refusal"]),
            "refusal_at": refusal_places(rule["refusal"]),
        },
    }
    return needing


def switch_rules_about(kind: str, switch_wide: dict) -> list:
    found = []
    for diagnostic, rule in switch_wide.items():
        if kind in rule["about"]:
            found.append({"refusal": diagnostic, "says": rule["says"], "at": refusal_places(rule["refusal"])})
    return found


def entering_rules_about(kind: str, function_wide: dict) -> list:
    found = []
    refusals = function_wide["places_a_jump_may_not_enter"]["refusals"]
    for diagnostic, refusal in refusals.items():
        if kind in refusal["jumps"]:
            found.append({"refusal": diagnostic, "says": refusal["says"],
                          "tests_the_in_note": len(refusal["tests_the_in_note"]) > 0,
                          "at": refusal_places(refusal["named_at"])})
    return found


def refusal_names(refusals: list) -> list:
    names = []
    for refusal in refusals:
        add_once(names, refusal["refusal"])
    return names


def refusal_places(refusals: list) -> list:
    found = []
    for refusal in refusals:
        found.append(refusal["at"])
    return found


def add_kinds_with_no_listing(places: dict, stands: dict, listed_kinds: list) -> None:
    for kind, stand in stands["by_kind"].items():
        if kind not in listed_kinds:
            places["left_out"].append(left_out(kind, stand["asks"]["refusal_at"], "no GNU C listing has this kind"))
    for kind, not_joined in stands["not_joined"].items():
        if kind not in listed_kinds:
            why = "no GNU C listing has this kind; and " + not_joined["why"]
            places["left_out"].append(left_out(kind, not_joined["at"], why))


def read_listings(listings_path: str) -> list:
    with open(listings_path, encoding="utf-8") as listings_file:
        listings = json.load(listings_file)["operators"]
    return listings


# which_parts_are_bodies (Block B, step 3: rules 12 to 20)


def which_parts_are_bodies(checkout: str, listings_path: str) -> dict:
    """Each listing of `listings_path`, with each of its parts: how clang
    writes it, where clang's control-flow builder runs it, and whether it is a
    body; and N, how many of its parts are bodies (rules 12 to 20)."""
    branches = read_branches(checkout)
    parts = read_where_each_part_runs(checkout, branches)
    written = read_how_each_part_is_written(checkout)
    bodies = combine_bodies(parts, written, listings_path)
    return bodies


# read_branches (rules 12 to 16)


@functools.lru_cache(maxsize=None)
def read_branches(checkout: str) -> dict:
    """kind -> the function of clang's control-flow builder the dispatch sends
    it to (rule 12), each path through it (rules 13 to 15), with the blocks it
    makes and links, their terminators and the parts it adds, and whether a
    path makes a branch (rule 16)."""
    dispatch = read_dispatch(checkout)
    stores = read_store_links(checkout)
    kinds = concrete_kinds(checkout)
    branches = {
        "dispatch": dispatch["evidence"],
        "read_through": dispatch["read_through"],
        "stores": stores,
        "label_prefixes": label_prefixes(checkout),
        "by_kind": {},
    }
    for kind in kinds:
        branches["by_kind"][kind] = branches_of(checkout, kind, dispatch, stores)
    return branches


def branches_of(checkout: str, kind: str, dispatch: dict, stores: dict) -> dict:
    sent = sent_to(dispatch, kind)
    through = dispatch["read_through"].get(kind)
    paths = builder_paths(checkout, kind, sent, through)
    marked = paths_with_branches(checkout, paths, kind, stores)
    found = {
        "sent_to": sent,
        "read_through": through,
        "paths": marked,
        "makes_a_branch": makes_a_branch(marked),
    }
    return found


# Rule 12: the dispatch


def read_dispatch(checkout: str) -> dict:
    """Rule 12: CFGBuilder::Visit. kind -> the returns of its case; `default:`'s
    for every other kind; the returns before the switch that a test of the
    node's kind lets a kind reach (OpenMP's directives); and the kinds an
    expression is read through first (`S = E->IgnoreParens();`)."""
    visit = the_dispatch(checkout)
    switch = nodes_of_type(visit.node, ("switch_statement",))[0]
    cases = cases_of_the_dispatch(switch)
    dispatch = {
        "evidence": {"function": visit.name, "at": where(BUILDER, visit.line),
                     "switch_at": where(BUILDER, line_of(switch))},
        "by_kind": cases["by_kind"],
        "default": cases["default"],
        "early": returns_before_the_switch(checkout, visit, switch),
        "read_through": read_through_kinds(checkout, visit),
    }
    return dispatch


def the_dispatch(checkout: str) -> Definition:
    definitions = definitions_named(read_every_function(checkout, BUILDER), DISPATCH)
    visit = definitions[0]
    return visit


def cases_of_the_dispatch(switch) -> dict:
    """Each `case Stmt::<Kind>Class:` with the returns of the statements after
    it; a case with none falls to the next."""
    cases = {"by_kind": {}, "default": None}
    pending = []
    for case in switch.child_by_field_name("body").named_children:
        add_dispatch_case(cases, case, pending)
    return cases


def add_dispatch_case(cases: dict, case, pending: list) -> None:
    if case.type != "case_statement":
        return
    value = case.child_by_field_name("value")
    if value is not None:
        add_kind_of_a_case(pending, value)
    returns = returns_of_a_case(case)
    if not returns:
        return
    sent = {"returns": returns, "case_at": where(BUILDER, line_of(case))}
    if value is None:
        cases["default"] = sent
    for kind in pending:
        cases["by_kind"][kind] = sent
    pending.clear()


def add_kind_of_a_case(pending: list, value) -> None:
    named = CLASS_NAME_OF_A_KIND.match(value.text.decode())
    if named is not None:
        pending.append(named.group(1))


def returns_of_a_case(case) -> list:
    """Each `return` among the statements a case holds: what it calls, and the
    `if` tests it stands under."""
    found = []
    returns = return_statements(case)
    for statement in returns:
        found.append(dispatch_return(statement))
    return found


def dispatch_return(statement) -> dict:
    value = returned_value(statement)
    called = None
    count = 0
    if value is not None and value.type == "call_expression":
        called = called_name(value)
        count = len(arguments_of(value))
    read = {
        "calls": called,
        "arguments": count,
        "at": where(BUILDER, line_of(statement)),
        "text": short_text(statement),
        "under": branch_tests(tests_around(statement, BUILDER)),
    }
    return read


def returns_before_the_switch(checkout: str, visit: Definition, switch) -> dict:
    """kind -> each `return` of Visit before its switch that a test of the
    node's kind lets that kind reach (`dyn_cast<OMPExecutableDirective>(S)`)."""
    early = {}
    returns = return_statements(visit.node)
    for statement in returns:
        if not is_inside(statement, switch):
            add_early_return(early, checkout, statement)
    return early


def is_inside(node, holder) -> bool:
    inside = node.start_byte >= holder.start_byte and node.end_byte <= holder.end_byte
    return inside


def add_early_return(early: dict, checkout: str, statement) -> None:
    read = dispatch_return(statement)
    kinds = kinds_in_tests(checkout, read["under"])
    for kind in kinds:
        add_to_list(early, kind, read)


def sent_to(dispatch: dict, kind: str) -> dict:
    """The returns that may take a node of `kind`: the early ones a test of its
    kind lets it reach, then its case's, or `default:`'s."""
    case = dispatch["default"]
    by_default = True
    if kind in dispatch["by_kind"]:
        case = dispatch["by_kind"][kind]
        by_default = False
    returns = []
    add_all(returns, dispatch["early"].get(kind, []))
    add_all(returns, case["returns"])
    sent = {"case_at": case["case_at"], "by_default": by_default, "returns": returns}
    return sent


def read_through_kinds(checkout: str, visit: Definition) -> dict:
    """Rule 12: kind -> the part `IgnoreParens()` hands back for a node of it,
    and the tests it does so under (IgnoreParensSingleStep), when the dispatch
    reads an expression through `IgnoreParens()` before its switch."""
    found = {}
    calls = calls_named(visit.node, READ_THROUGH)
    if not calls:
        return found
    in_the_dispatch = where(BUILDER, line_of(calls[0]))
    ignore_parens = read_through_defined(checkout)
    steps = definitions_named(read_every_function(checkout, IGNORE_EXPRESSIONS), READ_THROUGH_STEP)
    for statement in return_statements(steps[0].node):
        add_read_through(found, checkout, statement, in_the_dispatch, ignore_parens)
    return found


def read_through_defined(checkout: str) -> dict:
    """`Expr::IgnoreParens` (Expr.cpp): the step it repeats."""
    read = {"not_read": f"no Expr::{READ_THROUGH} in {EXPRESSION_SOURCE}"}
    definitions = definitions_named(read_every_function(checkout, EXPRESSION_SOURCE), "Expr::" + READ_THROUGH)
    for definition in definitions:
        read = {"function": definition.name, "at": where(EXPRESSION_SOURCE, definition.line),
                "text": short_text(definition.node.child_by_field_name("body"))}
    return read


def add_read_through(found: dict, checkout: str, statement, in_the_dispatch: str, ignore_parens: dict) -> None:
    value = returned_value(statement)
    if value is None or value.type != "call_expression":
        return
    tests = branch_tests(tests_around(statement, IGNORE_EXPRESSIONS))
    kind, holder = kind_cast_in_tests(checkout, tests)
    if kind is None:
        return
    found[kind] = {
        "getter": called_name(value),
        "when": tests_on_the_holder(tests, holder),
        "at": where(IGNORE_EXPRESSIONS, line_of(statement)),
        "text": short_text(statement),
        "read_through_in_the_dispatch_at": in_the_dispatch,
        "ignore_parens": ignore_parens,
    }


def kind_cast_in_tests(checkout: str, tests: list) -> tuple:
    """(kind, the name it is held in) for the test `auto *PE =
    dyn_cast<ParenExpr>(E)` taken true; (None, None) when there is none."""
    found = (None, None)
    kinds = concrete_kinds(checkout)
    for test in tests:
        cast = CAST_DECLARED.match(test["test"])
        if cast is not None and test["taken"] == "true" and cast.group(2) in kinds:
            found = (cast.group(2), cast.group(1))
    return found


def tests_on_the_holder(tests: list, holder: str) -> list:
    """The other tests taken true that name the holder, the holder written as
    Node: `UO->getOpcode() == UO_Extension` -> `Node->getOpcode() == UO_Extension`."""
    found = []
    for test in tests:
        if test["taken"] != "true" or CAST_DECLARED.match(test["test"]) is not None:
            continue
        if re.search(rf"\b{re.escape(holder)}\b", test["test"]) is not None:
            found.append(re.sub(rf"\b{re.escape(holder)}\b", cpp_code.NODE, test["test"]))
    return found


def label_prefixes(checkout: str) -> list:
    """Rule 14c: the prefixes the lists' `#define`s paste on an entry's name to
    make its label (`#define BINARY_OPERATION(Name, Spelling) BO_##Name,`)."""
    prefixes = []
    for relative in ENUM_FILES:
        add_label_prefixes(prefixes, file_text(checkout, relative))
    add_all_once(prefixes, builtin_label_prefixes())
    return prefixes


def add_label_prefixes(prefixes: list, text: str) -> None:
    for _macro, _parameters, prefix, _pasted in clang_reader.CLANG_ENUM_MACRO.findall(text):
        add_once(prefixes, prefix)


@functools.lru_cache(maxsize=None)
def file_text(checkout: str, relative: str) -> str:
    with open(declaring_file_path(checkout, relative), encoding="utf-8") as read_file:
        text = read_file.read()
    return text


@functools.lru_cache(maxsize=None)
def builder_members(checkout: str) -> tuple:
    """The names class CFGBuilder (CFG.cpp) declares as fields: they keep
    their values from one of its functions to the next (rule 13)."""
    names = []
    classes = nodes_of_type(parsed_file(checkout, BUILDER).root_node, ("class_specifier",))
    for node in classes:
        add_fields_of_the_builder(names, node)
    found = tuple(names)
    return found


def add_fields_of_the_builder(names: list, node) -> None:
    name = node.child_by_field_name("name")
    body = node.child_by_field_name("body")
    if name is None or body is None or name.text.decode() != BUILDER_CLASS:
        return
    for field in body.named_children:
        if field.type == "field_declaration":
            add_field_names(names, field)


def add_field_names(names: list, field) -> None:
    for declarator in field.children_by_field_name("declarator"):
        if not nodes_of_type(declarator, ("function_declarator",)):
            add_once(names, cpp_code.declared_name(declarator))


def builder_function(checkout: str, name: str, count: int):
    """The builder's function `name` that takes `count` arguments: the one with
    that many parameters, else the first with more (defaults); None if none."""
    found = None
    definitions = definitions_named(read_every_function(checkout, BUILDER), BUILDER_CLASS + "::" + name)
    for definition in definitions:
        if parameter_count(definition) == count:
            found = definition
            return found
    for definition in definitions:
        if parameter_count(definition) > count:
            found = definition
            return found
    return found


def parameter_count(definition: Definition) -> int:
    count = 0
    parameters = cpp_code.function_declarator(definition.node).child_by_field_name("parameters")
    for parameter in parameters.named_children:
        if parameter.type in ("parameter_declaration", "optional_parameter_declaration"):
            count += 1
    return count


# Rule 13: the paths through a kind's builder function


def builder_paths(checkout: str, kind: str, sent: dict, through) -> list:
    """Every path the builder takes a node of `kind` (rule 13): read through to
    one of its parts, when IgnoreParens hands one back (rule 12); through the
    function each return of its case calls, when it does not."""
    paths = []
    add_read_through_path(paths, kind, through)
    for returned in sent["returns"]:
        add_all(paths, paths_of_a_return(checkout, kind, returned, through))
    return paths


def add_read_through_path(paths: list, kind: str, through) -> None:
    """The node read through: the part IgnoreParens hands back is visited in
    its place, in the block `Block` holds; the tests it is handed back under
    held."""
    if through is None:
        return
    tests = []
    for text in through["when"]:
        tests.append(test_of_a_dispatch_text(text, True, through["at"]))
    path = BuilderPath(values=first_values(), events=(("added", through["getter"], AFTER_BLOCK, through["at"], ()),),
                     tests=tuple(tests), status="return", returned=("block", AFTER_BLOCK), made=0, frames=(), why="")
    paths.append(path_as_record(path, kind + " read through to " + through["getter"] + " (" + through["at"] + ")"))


def paths_of_a_return(checkout: str, kind: str, returned: dict, through) -> list:
    tests = dispatch_tests(returned, through)
    if returned["calls"] is None:
        path = BuilderPath(values=first_values(), events=(), tests=tests, status="return",
                         returned=("block", AFTER_BLOCK), made=0, frames=(), why="")
        found = [path_as_record(path, returned["text"] + " (" + returned["at"] + ")")]
        return found
    definition = builder_function(checkout, returned["calls"], returned["arguments"])
    if definition is None:
        path = builder_stopped(first_builder_path(tests),
                              f"no builder function {returned['calls']} of {returned['arguments']} arguments")
        found = [path_as_record(path, returned["text"])]
        return found
    walked = walked_builder_function(checkout, kind, definition, tests)
    found = []
    for path in walked:
        found.append(path_as_record(path, definition.name + " (" + where(BUILDER, definition.line) + ")"))
    return found


def dispatch_tests(returned: dict, through) -> tuple:
    """The tests the dispatch's return stands under, and, for a kind
    IgnoreParens hands a part back for, that it does not."""
    tests = []
    for test in returned["under"]:
        tests.append((DISPATCH_TEST, test["test"], test["taken"] == "true", test["at"], ()))
    if through is not None:
        tests.append(test_of_a_dispatch_text(" && ".join(through["when"]), False, through["at"]))
    found = tuple(tests)
    return found


def test_of_a_dispatch_text(text: str, taken: bool, at: str) -> tuple:
    """A test IgnoreParensSingleStep makes (rule 12), as a walk records it: of
    the node's list entry when it compares a getter of the node with a label
    (`Node->getOpcode() == UO_Extension`), else of the node."""
    test = (NODE_TEST, text, taken, at, ())
    compared = re.match(r"^Node->\w+\(\)\s*(==|!=)\s*(\w+)$", text)
    if compared is not None:
        test = (ENTRY_TEST, text, taken, at, ("compares", compared.group(1), compared.group(2)))
    return test


def walked_builder_function(checkout: str, kind: str, definition: Definition, tests: tuple) -> list:
    """Every path through one builder function handed a node of `kind` as its
    first parameter (rule 13)."""
    walk = walk_of(checkout, kind, definition, 0, 0)
    start = with_parameters(first_builder_path(tests), definition, (NODE_VALUE,))
    start = with_event(start, ("walked", definition.name, "", where(BUILDER, definition.line), ()))
    try:
        paths = walked_block(walk, definition.node.child_by_field_name("body"), start)
    except TooManyBuilderPaths:
        paths = [builder_stopped(start, f"more than {BUILDER_PATH_LIMIT} paths at once")]
    finished = finished_builder_paths(paths)
    return finished


def walk_of(checkout: str, kind: str, definition: Definition, depth: int, index: int) -> Walk:
    walk = Walk(checkout, kind, node_parameter(definition, index), definition.name, builder_members(checkout),
                depth)
    return walk


def node_parameter(definition: Definition, index: int) -> str:
    """The name of the parameter that holds the node: a builder function's
    first; a helper's where the node is handed (`isBuiltinAssumeWithSideEffects(
    FD->getASTContext(), C)`: its second)."""
    name = parameter_name_at(definition, index)
    if name is None:
        name = ""
    return name


def first_values() -> tuple:
    """Rule 15a: on entry `Block` holds "after", the block of the code after
    the node, and `Succ` "after it"; `badCFG` is false (rule 14a)."""
    values = (("Block", ("block", AFTER_BLOCK)), ("Succ", ("block", AFTER_IT)), ("badCFG", ("truth", False)))
    return values


def first_builder_path(tests: tuple) -> BuilderPath:
    path = BuilderPath(values=first_values(), events=(), tests=tests, status="", returned=NONE_VALUE, made=0,
                     frames=(), why="")
    return path


def with_parameters(path: BuilderPath, definition: Definition, arguments: tuple) -> BuilderPath:
    given = path
    count = parameter_count(definition)
    for index in range(count):
        name = parameter_name_at(definition, index)
        given = with_value(given, name, argument_at(arguments, index, name))
    return given


def argument_at(arguments: tuple, index: int, name: str) -> tuple:
    value = ("unknown", name)
    if index < len(arguments):
        value = arguments[index]
    return value


def finished_builder_paths(paths: list) -> list:
    """The paths that end: a path that sets badCFG builds no CFG and is dropped
    (rule 14a); a `return` ends the function; a path that falls off its end
    hands back none."""
    finished = []
    for path in paths:
        if path.status == "dropped":
            continue
        finished.append(finished_builder_path(path))
    return finished


def finished_builder_path(path: BuilderPath) -> BuilderPath:
    finished = path
    if path.status == "return":
        finished = path._replace(status="")
    if path.status in ("break", "continue"):
        finished = builder_stopped(path, f"a `{path.status}` outside any loop")
    return finished


def builder_stopped(path: BuilderPath, why: str) -> BuilderPath:
    stopped = path._replace(status="stop", why=why)
    return stopped


def with_event(path: BuilderPath, event: tuple) -> BuilderPath:
    done = path._replace(events=path.events + (event,))
    return done


def with_value(path: BuilderPath, name: str, value: tuple) -> BuilderPath:
    values = dict(path.values)
    values[name] = value
    given = path._replace(values=sorted_pairs(values))
    return given


def sorted_pairs(values: dict) -> tuple:
    pairs = tuple(sorted(values.items(), key=name_of_a_pair))
    return pairs


def name_of_a_pair(pair: tuple) -> str:
    name = pair[0]
    return name


def value_of(path: BuilderPath, name: str):
    value = dict(path.values).get(name)
    return value


# Rule 13: a builder function's statements


def walked_block(walk: Walk, node, path: BuilderPath) -> list:
    """The statements of a `{ ... }` in order; the members a SaveAndRestore
    inside it saved are put back when a path leaves it (rule 15h)."""
    opened = path._replace(frames=path.frames + ((),))
    paths = walked_statements(walk, statements_of(node), opened)
    closed = []
    for each in paths:
        closed.append(with_frame_closed(each))
    return closed


def statements_of(node) -> list:
    found = []
    for part in node.named_children:
        if part.type != "comment":
            found.append(part)
    return found


def with_frame_closed(path: BuilderPath) -> BuilderPath:
    frame = path.frames[-1]
    closed = path._replace(frames=path.frames[:-1])
    for member, value in reversed(frame):
        closed = with_value(closed, member, value)
    return closed


def walked_statements(walk: Walk, statements: list, path: BuilderPath) -> list:
    paths = [path]
    for statement in statements:
        paths = walked_in_each(walk, statement, paths)
    return paths


def walked_in_each(walk: Walk, statement, paths: list) -> list:
    after = []
    for path in paths:
        add_all(after, walked_one(walk, statement, path))
    merged = merged_paths(after)
    if len(merged) > BUILDER_PATH_LIMIT:
        raise TooManyBuilderPaths()
    return merged


def walked_one(walk: Walk, statement, path: BuilderPath) -> list:
    if path.status:
        found = [path]
        return found
    walker = STATEMENT_WALKS.get(statement.type, walked_unread_statement)
    found = walker(walk, statement, path)
    return found


def walked_unread_statement(walk: Walk, node, path: BuilderPath) -> list:
    why = f"a statement the rules do not read: `{short_text(node)}` ({where(BUILDER, line_of(node))})"
    found = [builder_stopped(path, why)]
    return found


def walked_nothing(walk: Walk, node, path: BuilderPath) -> list:
    found = [path]
    return found


def walked_declaration(walk: Walk, node, path: BuilderPath) -> list:
    declared_type = type_of_a_declaration(node)
    paths = [path]
    for declarator in node.children_by_field_name("declarator"):
        paths = declared_in_each(walk, declared_type, declarator, paths)
    return paths


def type_of_a_declaration(node) -> str:
    written = node.child_by_field_name("type")
    text = ""
    if written is not None:
        text = written.text.decode()
    return text


def declared_in_each(walk: Walk, declared_type: str, declarator, paths: list) -> list:
    after = []
    for path in paths:
        add_all(after, declared(walk, declared_type, declarator, path))
    return after


def declared(walk: Walk, declared_type: str, declarator, path: BuilderPath) -> list:
    """One name declared: a SaveAndRestore saves the member it names (rule
    15h); a value is given to the name; no value leaves it unset (a TryResult
    not known, rule 14h)."""
    name = cpp_code.declared_name(declarator)
    value = initial_value_of(declarator)
    if declared_type == SAVE_AND_RESTORE:
        found = [saved_member(path, name, value)]
        return found
    if value is None:
        found = [with_value(path, name, unset_value(declared_type))]
        return found
    if value.type == "argument_list":
        found = [with_value(path, name, constructed_value(declared_type, value))]
        return found
    found = []
    for evaluated_path, evaluated_value in evaluated(walk, value, path):
        found.append(with_value(evaluated_path, name, evaluated_value))
    return found


def initial_value_of(declarator):
    value = None
    if declarator.type == "init_declarator":
        value = declarator.child_by_field_name("value")
    return value


def saved_member(path: BuilderPath, name: str, arguments) -> BuilderPath:
    """`SaveAndRestore save_Block(Block)`: Block's value now, put back when the
    path leaves the braces (rule 15h)."""
    member = ""
    if arguments is not None and arguments.named_children:
        member = arguments.named_children[0].text.decode()
    held = value_of(path, member)
    if held is None:
        held = ("member", member)
    frames = path.frames[:-1] + (path.frames[-1] + ((member, held),),)
    saved = with_value(path._replace(frames=frames), name, ("saved", member, held))
    return saved


def unset_value(declared_type: str) -> tuple:
    value = ("unset",)
    if TRY_RESULT in declared_type:
        value = ("known", None)
    return value


def constructed_value(declared_type: str, arguments) -> tuple:
    """`TryResult KnownVal(true)`: known true (rule 14h)."""
    value = ("unknown", declared_type)
    if TRY_RESULT not in declared_type:
        return value
    value = ("known", None)
    written = arguments.text.decode()
    if written == "(true)":
        value = ("known", True)
    if written == "(false)":
        value = ("known", False)
    return value


def walked_expression_statement(walk: Walk, node, path: BuilderPath) -> list:
    expressions = statements_of(node)
    found = [path]
    if expressions:
        found = paths_only(evaluated(walk, expressions[0], path))
    return found


def paths_only(pairs: list) -> list:
    found = []
    for path, _value in pairs:
        found.append(path)
    return found


def walked_if(walk: Walk, node, path: BuilderPath) -> list:
    found = []
    for tested_path, truth in tested_clause(walk, node.child_by_field_name("condition"), path):
        add_all(found, walked_side(walk, node, tested_path, truth))
    return found


def walked_side(walk: Walk, node, path: BuilderPath, truth: bool) -> list:
    found = [path]
    if path.status:
        return found
    if truth:
        found = walked_one(walk, node.child_by_field_name("consequence"), path)
        return found
    alternative = node.child_by_field_name("alternative")
    if alternative is not None:
        found = walked_one(walk, statements_of(alternative)[0], path)
    return found


def tested_clause(walk: Walk, clause, path: BuilderPath) -> list:
    value = clause.child_by_field_name("value")
    if value is not None and value.type == "declaration":
        found = declared_and_tested(walk, value, path)
        return found
    found = tested(walk, value, path)
    return found


def declared_and_tested(walk: Walk, declaration, path: BuilderPath) -> list:
    """`if (Stmt *I = F->getInc())`: I given the value, and the value tested."""
    name = cpp_code.declared_name(declaration.child_by_field_name("declarator"))
    value = declaration.child_by_field_name("value")
    found = []
    for evaluated_path, evaluated_value in evaluated(walk, value, path):
        named = with_value(evaluated_path, name, evaluated_value)
        add_all(found, truths_of(walk, evaluated_value, named, value))
    return found


def walked_return(walk: Walk, node, path: BuilderPath) -> list:
    values = statements_of(node)
    if not values:
        found = [path._replace(status="return", returned=NONE_VALUE)]
        return found
    found = []
    for evaluated_path, value in evaluated(walk, values[0], path):
        found.append(returned_with(evaluated_path, value))
    return found


def returned_with(path: BuilderPath, value: tuple) -> BuilderPath:
    returned = path
    if not path.status:
        returned = path._replace(status="return", returned=value)
    return returned


def walked_break(walk: Walk, node, path: BuilderPath) -> list:
    found = [path._replace(status="break")]
    return found


def walked_continue(walk: Walk, node, path: BuilderPath) -> list:
    found = [path._replace(status="continue")]
    return found


def walked_do(walk: Walk, node, path: BuilderPath) -> list:
    """`do { ... } while (false);`: its body once, a `break` leaving it; a do
    loop with another test is not read."""
    condition = without_parentheses(node.child_by_field_name("condition"))
    if condition is None or condition.type != "false":
        found = [builder_stopped(path, f"a do loop whose test is not `false` ({where(BUILDER, line_of(node))})")]
        return found
    found = loops_left(walked_one(walk, node.child_by_field_name("body"), path))
    return found


def loops_left(paths: list) -> list:
    left = []
    for path in paths:
        left.append(loop_left(path))
    return left


def loop_left(path: BuilderPath) -> BuilderPath:
    left = path
    if path.status in ("break", "continue"):
        left = path._replace(status="")
    return left


def walked_while(walk: Walk, node, path: BuilderPath) -> list:
    """A while loop: its test decides; a test the rules do not decide gives a
    path with no turn and a path with one (rule 13)."""
    found = []
    for tested_path, truth in tested_clause(walk, node.child_by_field_name("condition"), path):
        add_all(found, walked_turn(walk, node, tested_path, truth))
    return found


def walked_turn(walk: Walk, node, path: BuilderPath, truth: bool) -> list:
    found = [path]
    if truth and not path.status:
        found = loops_left(walked_one(walk, node.child_by_field_name("body"), path))
    return found


def walked_for(walk: Walk, node, path: BuilderPath) -> list:
    """`for (init; test; step) body`: no turn, or one turn, as the test goes
    (rule 13)."""
    paths = [path]
    initializer = node.child_by_field_name("initializer")
    if initializer is not None:
        paths = walked_part_of_a_for(walk, initializer, path)
    found = []
    for each in paths:
        add_all(found, walked_for_turn(walk, node, each))
    return found


def walked_part_of_a_for(walk: Walk, part, path: BuilderPath) -> list:
    if part.type == "declaration":
        found = walked_declaration(walk, part, path)
        return found
    found = paths_only(evaluated(walk, part, path))
    return found


def walked_for_turn(walk: Walk, node, path: BuilderPath) -> list:
    condition = node.child_by_field_name("condition")
    if condition is None:
        found = [builder_stopped(path, f"a for loop with no test ({where(BUILDER, line_of(node))})")]
        return found
    found = []
    for tested_path, truth in tested_any(walk, condition, path):
        add_all(found, walked_for_body(walk, node, tested_path, truth))
    return found


def tested_any(walk: Walk, condition, path: BuilderPath) -> list:
    if condition.type == "condition_clause":
        found = tested_clause(walk, condition, path)
        return found
    found = tested(walk, condition, path)
    return found


def walked_for_body(walk: Walk, node, path: BuilderPath, truth: bool) -> list:
    found = [path]
    if not truth or path.status:
        return found
    paths = loops_left(walked_one(walk, node.child_by_field_name("body"), path))
    update = node.child_by_field_name("update")
    found = paths
    if update is not None:
        found = updated_in_each(walk, update, paths)
    return found


def updated_in_each(walk: Walk, update, paths: list) -> list:
    found = []
    for path in paths:
        add_all(found, paths_only(evaluated(walk, update, path)))
    return found


def walked_range_loop(walk: Walk, node, path: BuilderPath) -> list:
    """`for (Stmt *S : llvm::reverse(C->body()))`: over a part of the node, S
    holds each part of it, one turn read; over anything else, no turn and one
    turn (rule 13)."""
    name = cpp_code.declared_name(node.child_by_field_name("declarator"))
    found = []
    for evaluated_path, value in evaluated(walk, node.child_by_field_name("right"), path):
        add_all(found, walked_range_turns(walk, node, evaluated_path, name, value))
    return found


def walked_range_turns(walk: Walk, node, path: BuilderPath, name: str, value: tuple) -> list:
    body = node.child_by_field_name("body")
    if value[0] == "part":
        each = with_value(path, name, ("part", value[1]))
        found = loops_left(walked_one(walk, body, each))
        return found
    found = [path]
    turned = with_value(path, name, ("unknown", name))
    add_all(found, loops_left(walked_one(walk, body, turned)))
    return found


# Rules 14, 15 and 18: what an expression of a builder function holds


def evaluated(walk: Walk, node, path: BuilderPath) -> list:
    """(path, value) for each path an expression can go. A value is a block,
    none, the node, a part of it named by its getter (rule 18), a truth, what
    tryEvaluateBool knows (rule 14h), or unknown."""
    reader = EXPRESSION_READS.get(node.type, evaluated_unknown)
    found = reader(walk, node, path)
    return found


def evaluated_unknown(walk: Walk, node, path: BuilderPath) -> list:
    found = [(path, ("unknown", short_text(node)))]
    return found


def evaluated_name(walk: Walk, node, path: BuilderPath) -> list:
    name = node.text.decode()
    value = value_of(path, name)
    if value is None:
        value = name_not_given(walk, name)
    found = [(path, value)]
    return found


def name_not_given(walk: Walk, name: str) -> tuple:
    """A member not given a value in the walk, or a name the function does
    not declare (a label: `BO_LOr`)."""
    value = ("name", name)
    if name in walk.members:
        value = ("member", name)
    if name == "NULL":
        value = NONE_VALUE
    return value


def evaluated_null(walk: Walk, node, path: BuilderPath) -> list:
    found = [(path, NONE_VALUE)]
    return found


def evaluated_true(walk: Walk, node, path: BuilderPath) -> list:
    found = [(path, ("truth", True))]
    return found


def evaluated_false(walk: Walk, node, path: BuilderPath) -> list:
    found = [(path, ("truth", False))]
    return found


def evaluated_this(walk: Walk, node, path: BuilderPath) -> list:
    found = [(path, ("this",))]
    return found


def evaluated_inside(walk: Walk, node, path: BuilderPath) -> list:
    found = evaluated(walk, statements_of(node)[0], path)
    return found


def evaluated_qualified_name(walk: Walk, node, path: BuilderPath) -> list:
    found = [(path, ("name", node.text.decode()))]
    return found


def evaluated_pointer(walk: Walk, node, path: BuilderPath) -> list:
    """`&cfg->getExit()`, `*C->body_rbegin()`: what the operand holds."""
    found = evaluated(walk, node.child_by_field_name("argument"), path)
    return found


def evaluated_field(walk: Walk, node, path: BuilderPath) -> list:
    """`JT.block`: the block a jump target holds; `.first` of a pair."""
    field = node.child_by_field_name("field").text.decode()
    found = []
    for evaluated_path, value in evaluated(walk, node.child_by_field_name("argument"), path):
        found.append((evaluated_path, field_of(value, field, node)))
    return found


def field_of(value: tuple, field: str, node) -> tuple:
    found = ("unknown", short_text(node))
    if value[0] == "jump" and field == "block":
        found = value[1]
    if value[0] == "member" and field == "block":
        found = ("block", "held by " + value[1])
    if value[0] == "pair" and field == "first":
        found = value[1]
    if value[0] == "pair" and field == "second":
        found = value[2]
    return found


def evaluated_assignment(walk: Walk, node, path: BuilderPath) -> list:
    """`X = e`: X given e's value, each of a chain the same; `badCFG = true`
    drops the path (rule 14a); a member given a block stores it (rule 15i)."""
    operator = node.child_by_field_name("operator").text.decode()
    found = []
    for evaluated_path, value in evaluated(walk, node.child_by_field_name("right"), path):
        found.append(assigned(walk, node, operator, evaluated_path, value))
    return found


def assigned(walk: Walk, node, operator: str, path: BuilderPath, value: tuple) -> tuple:
    left = node.child_by_field_name("left")
    given = value
    if operator != "=":
        given = ("unknown", short_text(node))
    if left.type == "identifier":
        found = (given_to_a_name(walk, path, left.text.decode(), given, node), given)
        return found
    if left.type == "call_expression" and called_name(left) == "std::tie":
        found = (given_to_a_tie(path, left, given), given)
        return found
    found = (path, given)
    return found


def given_to_a_name(walk: Walk, path: BuilderPath, name: str, value: tuple, node) -> BuilderPath:
    given = with_value(path, name, value)
    if name == "badCFG" and value == ("truth", True):
        given = given._replace(status="dropped")
        return given
    if name in walk.members and name not in WALK_MEMBERS and value[0] == "block":
        given = with_event(given, ("stored", name, value[1], where(BUILDER, line_of(node)), ()))
    return given


def given_to_a_tie(path: BuilderPath, tie, value: tuple) -> BuilderPath:
    """`std::tie(A, B) = <pair>`: A and B given the pair's two values."""
    given = path
    names = arguments_of(tie)
    if value[0] != "pair" or len(names) != 2:
        return given
    given = with_value(given, names[0].text.decode(), value[1])
    given = with_value(given, names[1].text.decode(), value[2])
    return given


def evaluated_choice(walk: Walk, node, path: BuilderPath) -> list:
    """`test ? a : b`: the side the test takes."""
    found = []
    for tested_path, truth in tested(walk, node.child_by_field_name("condition"), path):
        add_all(found, evaluated(walk, chosen_side(node, truth), tested_path))
    return found


def chosen_side(node, truth: bool):
    side = node.child_by_field_name("alternative")
    if truth:
        side = node.child_by_field_name("consequence")
    return side


def evaluated_unary(walk: Walk, node, path: BuilderPath) -> list:
    operator = node.child_by_field_name("operator").text.decode()
    if operator != "!":
        found = [(path, ("unknown", short_text(node)))]
        return found
    found = []
    for tested_path, truth in tested(walk, node.child_by_field_name("argument"), path):
        found.append((tested_path, ("truth", not truth)))
    return found


def evaluated_binary(walk: Walk, node, path: BuilderPath) -> list:
    operator = node.child_by_field_name("operator").text.decode()
    if operator not in TESTING_OPERATORS:
        found = [(path, ("unknown", short_text(node)))]
        return found
    found = []
    for tested_path, truth in tested(walk, node, path):
        found.append((tested_path, ("truth", truth)))
    return found


# Calls


def evaluated_call(walk: Walk, node, path: BuilderPath) -> list:
    callee = node.child_by_field_name("function")
    reader = call_reader(callee)
    found = reader(walk, node, callee, path)
    return found


def call_reader(callee):
    reader = evaluated_unknown_call
    if callee.type == "identifier":
        reader = CALL_READS.get(callee.text.decode(), evaluated_named_call)
    if callee.type == "field_expression":
        reader = evaluated_member_call
    if callee.type == "template_function":
        reader = evaluated_kind_cast
    if callee.type == "qualified_identifier":
        reader = evaluated_qualified_call
    return reader


def evaluated_unknown_call(walk: Walk, node, callee, path: BuilderPath) -> list:
    found = [(path, ("unknown", short_text(node)))]
    return found


def evaluated_arguments(walk: Walk, node, path: BuilderPath) -> list:
    """(path, values) for each path a call's arguments can go, in order."""
    found = [(path, ())]
    for argument in arguments_of(node):
        found = with_one_more_argument(walk, argument, found)
    return found


def with_one_more_argument(walk: Walk, argument, pairs: list) -> list:
    found = []
    for path, values in pairs:
        add_argument_values(found, walk, argument, path, values)
    return found


def add_argument_values(found: list, walk: Walk, argument, path: BuilderPath, values: tuple) -> None:
    for evaluated_path, value in evaluated(walk, argument, path):
        found.append((evaluated_path, values + (value,)))


def first_of_values(values: tuple) -> tuple:
    first = ("unknown", "no argument")
    if values:
        first = values[0]
    return first


def made_block_call(walk: Walk, node, callee, path: BuilderPath) -> list:
    """Rule 15b: `createBlock()` makes a block linked to the one `Succ` holds;
    `createBlock(false)` one with no link."""
    found = []
    for argued_path, values in evaluated_arguments(walk, node, path):
        found.append(made_block(argued_path, values != (("truth", False),), line_of(node), "createBlock"))
    return found


def made_block(path: BuilderPath, linked: bool, line: int, how: str) -> tuple:
    """(path, the new block)."""
    number = path.made + 1
    block = "b" + str(number)
    at = where(BUILDER, line)
    made = with_event(path._replace(made=number), ("made", how, block, at, ()))
    succ = value_of(made, "Succ")
    if linked and succ is not None and block_of(succ) is not None:
        made = with_event(made, ("link", block, block_of(succ), at, how + " links it to the block Succ holds"))
    found = (made, ("block", block))
    return found


def made_no_return_block_call(walk: Walk, node, callee, path: BuilderPath) -> list:
    """Rule 15b: `createNoReturnBlock()` makes a block linked to the exit."""
    made, block = made_block(path, False, line_of(node), "createNoReturnBlock")
    made = with_event(made, ("link", block[1], EXIT_BLOCK, where(BUILDER, line_of(node)),
                             "createNoReturnBlock links it to the exit"))
    found = [(made, block)]
    return found


def auto_created_block_call(walk: Walk, node, callee, path: BuilderPath) -> list:
    found = [(auto_created(path, line_of(node)), NONE_VALUE)]
    return found


def auto_created(path: BuilderPath, line: int) -> BuilderPath:
    """Rule 15c: a block made, as by `createBlock()`, when `Block` holds none."""
    created = path
    held = value_of(path, "Block")
    if held is not None and held[0] == "block":
        return created
    created, block = made_block(path, True, line, "autoCreateBlock")
    created = with_value(created, "Block", block)
    return created


def added_call(walk: Walk, node, callee, path: BuilderPath) -> list:
    """Rule 15d: `addStmt(P)` or `Visit(P, ...)` adds a part to the block
    `Block` holds, made first when it holds none; the call hands that block
    back. A part that is none drops the path (`Visit` sets badCFG)."""
    found = []
    for argued_path, values in evaluated_arguments(walk, node, path):
        found.append(added_to_block(walk, argued_path, first_of_values(values), line_of(node)))
    return found


def added_to_block(walk: Walk, path: BuilderPath, value: tuple, line: int) -> tuple:
    if value == NONE_VALUE:
        found = (path._replace(status="dropped"), NONE_VALUE)
        return found
    created = auto_created(path, line)
    block = value_of(created, "Block")
    added = with_event(created, addition_event(walk, created, value, block_of(block), line))
    found = (added, block)
    return found


def addition_event(walk: Walk, path: BuilderPath, value: tuple, block, line: int) -> tuple:
    at = where(BUILDER, line)
    event = ("other added", value_text(value), block, at, ())
    if value[0] == "part":
        event = ("added", value[1], block, at, stores_held(path, walk.members))
    if value == NODE_VALUE:
        event = ("node added", "", block, at, ())
    return event


def stores_held(path: BuilderPath, members: tuple) -> tuple:
    """(member, block) for each member other than Block and Succ that holds a
    block now (rule 15i)."""
    held = []
    for name, value in path.values:
        if name in members and name not in WALK_MEMBERS and value[0] == "block":
            held.append((name, value[1]))
    found = tuple(held)
    return found


def appended_call(walk: Walk, node, callee, path: BuilderPath) -> list:
    """`appendStmt(X, S)`, `appendCall(X, S)`: S added to X, the node itself or
    a part."""
    found = []
    for argued_path, values in evaluated_arguments(walk, node, path):
        found.append((appended(walk, argued_path, values, line_of(node)), NONE_VALUE))
    return found


def appended(walk: Walk, path: BuilderPath, values: tuple, line: int) -> BuilderPath:
    found = path
    if len(values) >= 2:
        found = with_event(path, addition_event(walk, path, values[1], block_of(values[0]), line))
    return found


def linked_call(walk: Walk, node, callee, path: BuilderPath) -> list:
    """Rule 15f: `addSuccessor(X, Y, ...)` links X to Y; Y may be none."""
    found = []
    for argued_path, values in evaluated_arguments(walk, node, path):
        found.append((linked(argued_path, values, node), NONE_VALUE))
    return found


def linked(path: BuilderPath, values: tuple, node) -> BuilderPath:
    found = path
    if len(values) >= 2:
        found = with_event(path, ("link", block_of(values[0]), block_of(values[1]), where(BUILDER, line_of(node)),
                                 short_text(node)))
    return found


def block_of(value: tuple):
    """The block a value names: a block made in the walk, one it starts with, a
    member's, or one made elsewhere; None for none."""
    block = None
    if value[0] == "block":
        block = value[1]
    if value[0] == "member":
        block = "held by " + value[1]
    if value[0] in ("unknown", "name", "unset"):
        block = "elsewhere: " + value_text(value)
    return block


def every_part_added_call(walk: Walk, node, callee, path: BuilderPath) -> list:
    """`VisitChildren(S)`: every part of the node added to the block `Block`
    holds (rule 15d)."""
    created = auto_created(path, line_of(node))
    block = value_of(created, "Block")
    added = with_event(created, ("every part added", "", block_of(block), where(BUILDER, line_of(node)), ()))
    found = [(added, block)]
    return found


def not_known_call(walk: Walk, node, callee, path: BuilderPath) -> list:
    """Rule 14h: `tryEvaluateBool(...)` does not know a test of a listing's
    parts, which are not constants."""
    found = [(path, ("known", None))]
    return found


def jump_call(walk: Walk, node, callee, path: BuilderPath) -> list:
    """`JumpTarget(B, ...)`, `JumpSource(B, ...)`: a pair whose `.block` is B."""
    found = []
    for argued_path, values in evaluated_arguments(walk, node, path):
        found.append((argued_path, ("jump", first_of_values(values))))
    return found


def nothing_call(walk: Walk, node, callee, path: BuilderPath) -> list:
    found = [(path, NONE_VALUE)]
    return found


def evaluated_named_call(walk: Walk, node, callee, path: BuilderPath) -> list:
    """A builder function named Visit... handed the node is walked in place
    (rule 13); handed a part, it adds that part (rule 15d); any other call is
    read as making no block, and kept as a call not read."""
    name = callee.text.decode()
    found = []
    for argued_path, values in evaluated_arguments(walk, node, path):
        add_all(found, named_call_with(walk, node, name, argued_path, values))
    return found


def named_call_with(walk: Walk, node, name: str, path: BuilderPath, values: tuple) -> list:
    first = first_of_values(values)
    if name.startswith("Visit") and first == NODE_VALUE:
        found = walked_into(walk, name, builder_function(walk.checkout, name, len(values)), 0, values, path)
        return found
    if name.startswith("Visit") and first[0] == "part":
        found = [added_to_block(walk, path, first, line_of(node))]
        return found
    index = index_of_the_node(values)
    helper = function_of_the_builders_file(walk.checkout, name, len(values))
    if index is not None and helper is not None:
        found = walked_into(walk, name, helper, index, values, path)
        return found
    not_read = with_event(path, ("call not read", name, "", where(BUILDER, line_of(node)), ()))
    found = [(not_read, ("unknown", short_text(node)))]
    return found


def index_of_the_node(values: tuple):
    index = None
    for position in range(len(values)):
        if values[position] == NODE_VALUE and index is None:
            index = position
    return index


def function_of_the_builders_file(checkout: str, name: str, count: int):
    """A function CFG.cpp defines outside the builder's class, of `count`
    parameters (`isBuiltinAssumeWithSideEffects`); None if none."""
    found = None
    for definition in definitions_named(read_every_function(checkout, BUILDER), name):
        if parameter_count(definition) == count:
            found = definition
    return found


def walked_into(walk: Walk, name: str, definition, index: int, values: tuple, path: BuilderPath) -> list:
    """Rule 13: a function of CFG.cpp handed the node, walked in place: its
    parameters given the arguments, the one at `index` holding the node; the
    caller's own names put back after."""
    if definition is None or walk.depth >= WALK_DEPTH:
        why = f"`{name}` of {len(values)} arguments, handed the node, is not walked"
        found = [(builder_stopped(path, why), NONE_VALUE)]
        return found
    inner = walk_of(walk.checkout, walk.kind, definition, walk.depth + 1, index)
    callers = names_of_a_function(path, walk.members)
    entering = with_parameters(with_names(path, walk.members, ()), definition, values)
    entering = with_event(entering, ("walked", definition.name, "", where(BUILDER, definition.line), ()))
    found = []
    for each in walked_block(inner, definition.node.child_by_field_name("body"), entering):
        found.append(back_in_the_caller(each, walk.members, callers))
    return found


def names_of_a_function(path: BuilderPath, members: tuple) -> tuple:
    """The names a path holds that are not members: the function's own."""
    own = []
    for name, value in path.values:
        if name not in members:
            own.append((name, value))
    found = tuple(own)
    return found


def with_names(path: BuilderPath, members: tuple, names: tuple) -> BuilderPath:
    """The path holding its members, and `names` as its function's own."""
    values = {}
    for name, value in path.values:
        if name in members:
            values[name] = value
    for name, value in names:
        values[name] = value
    held = path._replace(values=sorted_pairs(values))
    return held


def back_in_the_caller(path: BuilderPath, members: tuple, callers: tuple) -> tuple:
    value = NONE_VALUE
    back = path
    if path.status == "return":
        value = path.returned
        back = path._replace(status="", returned=NONE_VALUE)
    back = with_names(back, members, callers)
    found = (back, value)
    return found


def evaluated_member_call(walk: Walk, node, callee, path: BuilderPath) -> list:
    method = callee.child_by_field_name("field").text.decode()
    found = []
    for held_path, held in evaluated(walk, callee.child_by_field_name("argument"), path):
        reader = member_call_reader(held, method)
        add_all(found, reader(walk, node, method, held_path, held))
    return found


def member_call_reader(held: tuple, method: str):
    reader = unknown_member_call
    if held[0] in ("block", "member") and method in BLOCK_MARKS:
        reader = block_marked_call
    if held == NODE_VALUE:
        reader = node_call
    if held[0] == "part":
        reader = part_call
    if held[0] == "known":
        reader = known_call
    if held[0] == "saved" and method == "get":
        reader = saved_call
    if held == ("member", "cfg"):
        reader = cfg_call
    if held[0] == "member" and method == "push_back":
        reader = stored_in_a_list_call
    return reader


def unknown_member_call(walk: Walk, node, method: str, path: BuilderPath, held: tuple) -> list:
    found = [(path, ("unknown", normalized(walk, short_text(node))))]
    return found


def block_marked_call(walk: Walk, node, method: str, path: BuilderPath, held: tuple) -> list:
    """Rule 15g: `X->setTerminator(T)`, `X->setLoopTarget(T)`, `X->setLabel(L)`."""
    found = []
    for argued_path, values in evaluated_arguments(walk, node, path):
        found.append((block_marked(argued_path, held, method, values, node), NONE_VALUE))
    return found


def block_marked(path: BuilderPath, held: tuple, method: str, values: tuple, node) -> BuilderPath:
    first = first_of_values(values)
    what = value_text(first)
    if first == NODE_VALUE:
        what = "node"
    marked = with_event(path, (BLOCK_MARKS[method], what, block_of(held), where(BUILDER, line_of(node)), ()))
    return marked


def node_call(walk: Walk, node, method: str, path: BuilderPath, held: tuple) -> list:
    """Rule 18: a getter of the node names a part (`F->getInc()`); any other
    call is a test of the node (`I->isConsteval()`)."""
    value = ("node test", normalized(walk, short_text(node)), method)
    if method.startswith("get") or method in RANGE_GETTERS:
        value = ("part", method)
    found = [(path, value)]
    return found


def part_call(walk: Walk, node, method: str, path: BuilderPath, held: tuple) -> list:
    """`RHS->IgnoreParens()` is the same part; anything else of a part is not
    read."""
    value = ("unknown", normalized(walk, short_text(node)))
    if method in PART_KEEPING:
        value = held
    found = [(path, value)]
    return found


def known_call(walk: Walk, node, method: str, path: BuilderPath, held: tuple) -> list:
    """Rule 14h: what a TryResult knows."""
    known = held[1]
    value = ("unknown", short_text(node))
    if method == "isKnown":
        value = ("truth", known is not None)
    if method == "isTrue":
        value = ("truth", known is True)
    if method == "isFalse":
        value = ("truth", known is False)
    found = [(path, value)]
    return found


def saved_call(walk: Walk, node, method: str, path: BuilderPath, held: tuple) -> list:
    """`sv.get()`: the value a SaveAndRestore saved."""
    found = [(path, held[2])]
    return found


def cfg_call(walk: Walk, node, method: str, path: BuilderPath, held: tuple) -> list:
    """`cfg->getExit()`, the exit block; `cfg->getIndirectGotoBlock()`, the
    CFG's indirect-goto block; `cfg->setIndirectGotoBlock(B)` stores B there
    (rule 15i)."""
    found = []
    for argued_path, values in evaluated_arguments(walk, node, path):
        found.append(cfg_call_with(argued_path, method, values, node))
    return found


def cfg_call_with(path: BuilderPath, method: str, values: tuple, node) -> tuple:
    value = ("unknown", short_text(node))
    given = path
    if method == "getExit":
        value = ("block", EXIT_BLOCK)
    if method == "getIndirectGotoBlock":
        value = ("block", INDIRECT_GOTO_BLOCK)
    if method == "setIndirectGotoBlock":
        given = with_event(path, ("stored", INDIRECT_GOTO_BLOCK, block_of(first_of_values(values)),
                                 where(BUILDER, line_of(node)), ()))
    found = (given, value)
    return found


def stored_in_a_list_call(walk: Walk, node, method: str, path: BuilderPath, held: tuple) -> list:
    """`BackpatchBlocks.push_back(JumpSource(Block, ScopePos))`: the block
    stored in that list (rule 15i)."""
    found = []
    for argued_path, values in evaluated_arguments(walk, node, path):
        found.append((stored_in_a_list(argued_path, held, values, node), NONE_VALUE))
    return found


def stored_in_a_list(path: BuilderPath, held: tuple, values: tuple, node) -> BuilderPath:
    first = first_of_values(values)
    stored = path
    if first[0] == "jump" and block_of(first[1]) is not None:
        stored = with_event(path, ("stored", held[1], block_of(first[1]), where(BUILDER, line_of(node)), ()))
    return stored


def evaluated_kind_cast(walk: Walk, node, callee, path: BuilderPath) -> list:
    """Rules 14b and 14e: `dyn_cast<K>(x)`, `isa<K>(x)`, `cast<K>(x)`."""
    cast = callee.child_by_field_name("name").text.decode()
    kind = type_argument(callee)
    found = []
    for argued_path, values in evaluated_arguments(walk, node, path):
        found.append((argued_path, kind_cast_value(walk, cast, kind, first_of_values(values), node)))
    return found


def type_argument(template_function) -> str:
    arguments = template_function.child_by_field_name("arguments")
    text = ""
    if arguments.named_children:
        text = arguments.named_children[0].text.decode()
    written = re.sub(r"\bconst\b|\*", "", text).strip()
    return written


def kind_cast_value(walk: Walk, cast: str, kind: str, value: tuple, node) -> tuple:
    if cast in IDENTITY_CASTS:
        return value
    holds = kind_cast_holds(walk, kind, value)
    found = ("unknown", normalized(walk, short_text(node)))
    if holds is None:
        return found
    if cast in TESTING_CASTS:
        found = ("truth", holds)
        return found
    found = value
    if cast in FINDING_CASTS and not holds:
        found = NONE_VALUE
    return found


def kind_cast_holds(walk: Walk, kind: str, value: tuple):
    """Rule 14b: the node is of `kind` when `kind` is its kind or one above it
    in StmtNodes.td. Rule 14e: a listing's part is of no kind but the roots
    (`Expr`, `Stmt`)."""
    holds = None
    if value == NODE_VALUE:
        holds = kind in clang_reader.chain_of(walk.kind, stmt_nodes(walk.checkout))
    if value[0] == "part":
        holds = kind in ROOT_KINDS
    if value == NONE_VALUE:
        holds = False
    return holds


def evaluated_qualified_call(walk: Walk, node, callee, path: BuilderPath) -> list:
    name = callee.text.decode()
    found = []
    for argued_path, values in evaluated_arguments(walk, node, path):
        found.append((argued_path, qualified_call_value(name, values, node)))
    return found


def qualified_call_value(name: str, values: tuple, node) -> tuple:
    value = ("unknown", short_text(node))
    if name == "std::make_pair" and len(values) == 2:
        value = ("pair", values[0], values[1])
    if name == "llvm::reverse" and values:
        value = values[0]
    return value


def value_text(value: tuple) -> str:
    text = value[0]
    if len(value) > 1 and isinstance(value[1], str):
        text = value[0] + " " + value[1]
    return text


def normalized(walk: Walk, text: str) -> str:
    """A test's text with the node's own name written Node, as StmtPrinter's
    walk writes it."""
    written = text
    if walk.node_name:
        written = re.sub(rf"\b{re.escape(walk.node_name)}\b", cpp_code.NODE, text)
    return written


# Rule 14: tests


def tested(walk: Walk, node, path: BuilderPath) -> list:
    """(path, True or False) for each path a test can go."""
    reader = test_reader(node)
    found = reader(walk, node, path)
    return found


def test_reader(node):
    reader = tested_value
    if node.type == "parenthesized_expression":
        reader = tested_inside
    if node.type == "unary_expression" and node.child_by_field_name("operator").text.decode() == "!":
        reader = tested_not
    if node.type == "binary_expression":
        reader = BINARY_TESTS.get(node.child_by_field_name("operator").text.decode(), tested_value)
    return reader


def tested_inside(walk: Walk, node, path: BuilderPath) -> list:
    found = tested(walk, statements_of(node)[0], path)
    return found


def tested_not(walk: Walk, node, path: BuilderPath) -> list:
    found = []
    for tested_path, truth in tested(walk, node.child_by_field_name("argument"), path):
        found.append((tested_path, not truth))
    return found


def tested_and(walk: Walk, node, path: BuilderPath) -> list:
    found = []
    for left_path, left in tested(walk, node.child_by_field_name("left"), path):
        add_all(found, after_the_left(walk, node, left_path, left, False))
    return found


def tested_or(walk: Walk, node, path: BuilderPath) -> list:
    found = []
    for left_path, left in tested(walk, node.child_by_field_name("left"), path):
        add_all(found, after_the_left(walk, node, left_path, left, True))
    return found


def after_the_left(walk: Walk, node, path: BuilderPath, left: bool, deciding: bool) -> list:
    """`a && b` is false when `a` is (deciding False); `a || b` true when `a`
    is (deciding True); otherwise `b` decides."""
    if left == deciding:
        found = [(path, deciding)]
        return found
    found = tested(walk, node.child_by_field_name("right"), path)
    return found


def tested_value(walk: Walk, node, path: BuilderPath) -> list:
    found = []
    for evaluated_path, value in evaluated(walk, node, path):
        add_all(found, truths_of(walk, value, evaluated_path, node))
    return found


def truths_of(walk: Walk, value: tuple, path: BuilderPath, node) -> list:
    """Rule 14: a value decided by what it holds; a part there or not, a test
    of the node or anything else not decided forks, its outcome kept for the
    path (a test met again goes the same path)."""
    truth = decided_truth(value)
    if truth is not None:
        found = [(path, truth)]
        return found
    test = test_of_a_value(walk, value, node)
    found = forked(path, test)
    return found


def decided_truth(value: tuple):
    truth = None
    if value[0] == "truth":
        truth = value[1]
    if value == NONE_VALUE:
        truth = False
    if value[0] in ("block", "node", "this", "pair", "jump"):
        truth = True
    return truth


def test_of_a_value(walk: Walk, value: tuple, node) -> tuple:
    """(what, text, at, detail): a part there (rule 14d), a test of the node,
    of its list entry (rule 14c, 14i), or another."""
    at = where(BUILDER, line_of(node))
    test = (OTHER_TEST, normalized(walk, short_text(node)), at, ())
    if value[0] == "part":
        test = (THERE, value[1], at, ())
    if value[0] == "node test":
        test = node_test_of(walk, value, at)
    return test


def node_test_of(walk: Walk, value: tuple, at: str) -> tuple:
    """`B->isLogicalOp()`: of the node's list entry when the kind's class (or
    one above it) defines it as a test of the entry (`static bool
    isLogicalOp(Opcode Opc) { return ...; }`); else of the node."""
    test = (NODE_TEST, value[1], at, ())
    predicate = entry_predicate(walk.checkout, walk.kind, value[2])
    if predicate is not None:
        test = (ENTRY_TEST, value[1], at, ("predicate",) + predicate)
    return test


def entry_predicate(checkout: str, kind: str, method: str):
    """(its parameter, its test, where) for `static bool method(Opcode Opc) {
    return <test>; }` in the kind's class or one above it; None if none."""
    found = None
    functions = class_functions(checkout)
    for owner in clang_reader.chain_of(kind, stmt_nodes(checkout)):
        for defined in functions.get(owner, {}).get(method, []):
            if len(defined["parameters"]) == 1 and defined["returns"] is not None:
                found = (defined["parameters"][0], defined["returns"], defined["at"])
                return found
    return found


def forked(path: BuilderPath, test: tuple) -> list:
    what, text, at, detail = test
    earlier = earlier_outcome(path, what, text)
    if earlier is not None:
        found = [(path, earlier)]
        return found
    held = path._replace(tests=path.tests + ((what, text, True, at, detail),))
    failed = path._replace(tests=path.tests + ((what, text, False, at, detail),))
    found = [(held, True), (failed, False)]
    return found


def earlier_outcome(path: BuilderPath, what: str, text: str):
    outcome = None
    for test in path.tests:
        if test[0] == what and test[1] == text:
            outcome = test[2]
    return outcome


def tested_comparison(walk: Walk, node, path: BuilderPath) -> list:
    """Rule 14: `X == Y`, `X != Y`."""
    equal = node.child_by_field_name("operator").text.decode() == "=="
    found = []
    for left_path, left in evaluated(walk, node.child_by_field_name("left"), path):
        add_all(found, compared_with(walk, node, left_path, left, equal))
    return found


def compared_with(walk: Walk, node, path: BuilderPath, left: tuple, equal: bool) -> list:
    found = []
    for right_path, right in evaluated(walk, node.child_by_field_name("right"), path):
        add_all(found, comparison_outcomes(walk, node, right_path, left, right, equal))
    return found


def comparison_outcomes(walk: Walk, node, path: BuilderPath, left: tuple, right: tuple, equal: bool) -> list:
    """Two values the same or not; a part against none is the part there or
    not; a getter of the node against a label tests its list entry (rule
    14c); anything else forks."""
    same = values_the_same(walk, left, right)
    if same is not None:
        found = [(path, same == equal)]
        return found
    part = part_against_none(left, right)
    if part is not None:
        found = []
        for tested_path, there in forked(path, (THERE, part[1], where(BUILDER, line_of(node)), ())):
            found.append((tested_path, there != equal))
        return found
    found = forked(path, comparison_test(walk, node, left, right))
    return found


def values_the_same(walk: Walk, left: tuple, right: tuple):
    same = None
    if left == right and left[0] in ("none", "node", "truth", "block", "part"):
        same = True
    if left[0] == "block" and right[0] == "block" and MADE_BLOCK.match(left[1]) and MADE_BLOCK.match(right[1]):
        same = left == right
    if (left == NONE_VALUE and right[0] == "block") or (right == NONE_VALUE and left[0] == "block"):
        same = False
    if left[0] == "part" and right[0] == "part" and left != right:
        same = parts_the_same(walk, left[1], right[1])
    return same


def parts_the_same(walk: Walk, first: str, second: str):
    """Two getters of the node that read one slot are one part; two that read
    different slots may still hold one value (`trueExpr != opaqueValue`), so
    that is not decided."""
    same = None
    first_slot = slot_of(walk.checkout, walk.kind, first)["slot"]
    second_slot = slot_of(walk.checkout, walk.kind, second)["slot"]
    if first_slot is not None and first_slot == second_slot:
        same = True
    return same


def part_against_none(left: tuple, right: tuple):
    found = None
    if left[0] == "part" and right == NONE_VALUE:
        found = left
    if right[0] == "part" and left == NONE_VALUE:
        found = right
    return found


def comparison_test(walk: Walk, node, left: tuple, right: tuple) -> tuple:
    """Rule 14c: a getter of the node against a name the function does not
    declare (`B->getOpcode() == BO_LOr`), or anything against a label of
    clang's builtin lists (`FD->getBuiltinID() == Builtin::BI__builtin_object_size`:
    the builtin the call names, its listing's entry), tests the list entry."""
    text = normalized(walk, short_text(node))
    at = where(BUILDER, line_of(node))
    operator = node.child_by_field_name("operator").text.decode()
    test = (OTHER_TEST, text, at, ())
    if right[0] == "name" and (left[0] == "part" or is_a_builtin_label(right[1])):
        test = (ENTRY_TEST, text, at, ("compares", operator, right[1]))
    if left[0] == "name" and (right[0] == "part" or is_a_builtin_label(left[1])):
        test = (ENTRY_TEST, text, at, ("compares", operator, left[1]))
    return test


def is_a_builtin_label(name: str) -> bool:
    """`Builtin::BI__builtin_object_size`: an entry of one of clang's builtin
    lists, in the namespace operator_reader reads it in (clang.BUILTIN_LISTS)."""
    found = False
    for prefix in builtin_label_prefixes():
        if name.startswith(prefix + "BI"):
            found = True
    return found


def builtin_label_prefixes() -> list:
    prefixes = []
    for _listed_in, namespace, _included_as in clang_reader.BUILTIN_LISTS:
        prefixes.append(namespace + "::")
    return prefixes


# Merging paths


def merged_paths(paths: list) -> list:
    """Paths that hold the same names, did the same, stand at the same status
    and took the tests a listing decides the same path (rule 14c, 14d, 14i)
    are one path; it keeps the other tests they all took the same path."""
    kept = []
    keys = []
    for path in paths:
        add_merged(kept, keys, path)
    return kept


def add_merged(kept: list, keys: list, path: BuilderPath) -> None:
    key = (path.values, path.events, path.status, path.returned, path.made, path.frames, path.why, tests_decided(path.tests))
    if key in keys:
        index = keys.index(key)
        kept[index] = kept[index]._replace(tests=shared_tests(kept[index].tests, path.tests))
        return
    keys.append(key)
    kept.append(path)


def tests_decided(tests: tuple) -> tuple:
    """The tests a listing can decide: of a part there, of the node's list
    entry, of the node (with the outcomes)."""
    decided = []
    for test in tests:
        if test[0] in (THERE, ENTRY_TEST, NODE_TEST):
            decided.append((test[0], test[1], test[2]))
    found = tuple(sorted(decided))
    return found


def shared_tests(first: tuple, second: tuple) -> tuple:
    shared = []
    for test in first:
        if test in second:
            shared.append(test)
    found = tuple(shared)
    return found


# What each statement and expression is read by (rules 13 to 15)


STATEMENT_WALKS = {
    "compound_statement": walked_block,
    "declaration": walked_declaration,
    "expression_statement": walked_expression_statement,
    "if_statement": walked_if,
    "return_statement": walked_return,
    "do_statement": walked_do,
    "while_statement": walked_while,
    "for_statement": walked_for,
    "for_range_loop": walked_range_loop,
    "break_statement": walked_break,
    "continue_statement": walked_continue,
    "comment": walked_nothing,
}

EXPRESSION_READS = {
    "identifier": evaluated_name,
    "null": evaluated_null,
    "true": evaluated_true,
    "false": evaluated_false,
    "this": evaluated_this,
    "parenthesized_expression": evaluated_inside,
    "qualified_identifier": evaluated_qualified_name,
    "field_expression": evaluated_field,
    "call_expression": evaluated_call,
    "assignment_expression": evaluated_assignment,
    "conditional_expression": evaluated_choice,
    "unary_expression": evaluated_unary,
    "pointer_expression": evaluated_pointer,
    "binary_expression": evaluated_binary,
}

CALL_READS = {
    "createBlock": made_block_call,
    "createNoReturnBlock": made_no_return_block_call,
    "autoCreateBlock": auto_created_block_call,
    "addStmt": added_call,
    "Visit": added_call,
    "appendStmt": appended_call,
    "appendCall": appended_call,
    "addSuccessor": linked_call,
    "VisitChildren": every_part_added_call,
    "tryEvaluateBool": not_known_call,
    "tryEvaluate": not_known_call,
    "JumpTarget": jump_call,
    "JumpSource": jump_call,
    "assert": nothing_call,
}

BINARY_TESTS = {
    "&&": tested_and,
    "||": tested_or,
    "==": tested_comparison,
    "!=": tested_comparison,
}


# Rule 15i: the stores of blocks across the builder's functions


def read_store_links(checkout: str) -> dict:
    """store -> each `addSuccessor(B, ...)` a builder function adds from a
    block it takes out of that store: a member of the builder other than
    Block and Succ (`SwitchTerminatedBlock`), a list of blocks walked in a
    loop (`BackpatchBlocks`), or the CFG's indirect-goto block."""
    members = builder_members(checkout)
    stores = {}
    for definition in read_every_function(checkout, BUILDER):
        add_store_links_in(stores, definition, members)
    return stores


def add_store_links_in(stores: dict, definition: Definition, members: tuple) -> None:
    calls = calls_named(definition.node, "addSuccessor")
    for call in calls:
        add_store_link(stores, definition, members, call)


def add_store_link(stores: dict, definition: Definition, members: tuple, call) -> None:
    arguments = arguments_of(call)
    if not arguments:
        return
    store = store_taken_from(arguments[0], members, call)
    if store is None:
        return
    read = read_node(BUILDER, definition, call)
    read["kinds_tested"] = kind_names_tested(read["under"])
    read["loops"] = loops_of(read["under"])
    add_to_list(stores, store, read)


def store_taken_from(argument, members: tuple, call):
    """The store the block `argument` names comes from, or None."""
    store = None
    if argument.type != "identifier":
        return store
    name = argument.text.decode()
    if name in members and name not in WALK_MEMBERS:
        store = name
        return store
    value = scoped_value_of(name, call)
    if value is None:
        return store
    if "getIndirectGotoBlock" in value:
        store = INDIRECT_GOTO_BLOCK
        return store
    store = list_a_block_is_taken_from(value, call, members)
    return store


def list_a_block_is_taken_from(value: str, call, members: tuple):
    """`I->block`, where I is the loop's `BackpatchBlocks.begin()`: that list."""
    found = None
    held = BLOCK_HELD_IN.match(value)
    if held is None:
        return found
    for test in tests_around(call, BUILDER):
        listed = re.search(LOOP_OVER_A_MEMBER.format(re.escape(held.group(1))), test["test"])
        if test["taken"] == "each turn of the loop" and listed is not None and listed.group(1) in members:
            found = listed.group(1)
    return found


def scoped_value_of(name: str, call):
    """The value given to `name` by its declaration nearest before `call`, in
    the braces, `if` or loop that hold the call."""
    inner = call
    current = call.parent
    while current is not None and current.type != "function_definition":
        value = declared_before(current, inner, name)
        if value is not None:
            return value
        inner = current
        current = current.parent
    value = None
    return value


def declared_before(scope, inner, name: str):
    value = None
    if scope.type in ("if_statement", "while_statement"):
        value = declared_in_a_condition(scope.child_by_field_name("condition"), name)
    if scope.type == "for_statement":
        value = declared_in_a_declaration(scope.child_by_field_name("initializer"), name)
    if scope.type == "compound_statement":
        value = declared_in_braces_before(scope, inner, name)
    return value


def declared_in_a_condition(clause, name: str):
    value = None
    declaration = None
    if clause is not None:
        declaration = clause.child_by_field_name("value")
    if declaration is None or declaration.type != "declaration":
        return value
    if cpp_code.declared_name(declaration.child_by_field_name("declarator")) == name:
        value = short_text(declaration.child_by_field_name("value"))
    return value


def declared_in_a_declaration(declaration, name: str):
    value = None
    if declaration is None or declaration.type != "declaration":
        return value
    for declarator in declaration.children_by_field_name("declarator"):
        given = initial_value_of(declarator)
        if given is not None and cpp_code.declared_name(declarator) == name:
            value = short_text(given)
    return value


def declared_in_braces_before(braces, inner, name: str):
    value = None
    for part in braces.named_children:
        if part.start_byte >= inner.start_byte:
            break
        given = declared_in_a_declaration(part, name)
        if given is not None:
            value = given
    return value


def kind_names_tested(tests: list) -> list:
    """The kinds a test taken true casts the block's terminator to
    (`dyn_cast<GCCAsmStmt>(B->getTerminator())`)."""
    found = []
    for test in tests:
        if test["taken"] == "true" and TERMINATOR_TESTED in test["test"]:
            add_all_once(found, KIND_CAST.findall(test["test"]))
    return found


def loops_of(tests: list) -> list:
    found = []
    for test in tests:
        if test["taken"] == "each turn of the loop":
            found.append({"loop": test["test"], "at": test["at"]})
    return found


# Rule 16: a branch


def paths_with_branches(checkout: str, paths: list, kind: str, stores: dict) -> list:
    marked = []
    for path in paths:
        marked.append(path_with_its_branch(checkout, path, kind, stores))
    return marked


def path_with_its_branch(checkout: str, path: dict, kind: str, stores: dict) -> dict:
    """Rule 16: each block the path gives the node as its terminator, with its
    links: those the path adds, and those other functions add to a store the
    path put it in. A branch has two or more."""
    marked = dict(path)
    marked["terminators"] = terminators_of_the_node(checkout, path, kind, stores)
    marked["branch"] = None
    for terminator in marked["terminators"]:
        if terminator["is_a_branch"] and marked["branch"] is None:
            marked["branch"] = terminator
    return marked


def terminators_of_the_node(checkout: str, path: dict, kind: str, stores: dict) -> list:
    found = []
    for event in path["events"]:
        if event["event"] == "terminator" and event["what"] == "node":
            found.append(terminator_read(checkout, path, event, kind, stores))
    return found


def terminator_read(checkout: str, path: dict, event: dict, kind: str, stores: dict) -> dict:
    block = event["block"]
    here = links_from(path, block)
    elsewhere = links_through_stores(checkout, path, block, kind, stores)
    read = {
        "block": block,
        "terminator_at": event["at"],
        "links_here": here,
        "links_elsewhere": elsewhere,
        "is_a_branch": len(here) + len(elsewhere) >= 2,
        "branch_when": branch_when(here, elsewhere),
    }
    return read


def branch_when(here: list, elsewhere: list) -> str:
    """A link another function adds is added once each time that function
    runs for the stored block (VisitCaseStmt: once per case label inside a
    switch's body), or once per turn of a loop (buildCFG: once per label of
    an `asm goto`): with links of its own fewer than two, the block is a
    branch only when those add the rest."""
    when = "always: the path adds two or more links itself"
    if len(here) >= 2:
        return when
    added_how = []
    for link in elsewhere:
        added_how.append(link_added_how(link))
    when = (f"when the links other functions add come to {2 - len(here)} or more: "
            + "; ".join(added_how))
    return when


def link_added_how(link: dict) -> str:
    how = f"once each time {link['in']} runs for it ({link['at']})"
    if link["loops"]:
        how = f"once per turn of `{link['loops'][-1]['loop']}` in {link['in']} ({link['at']})"
    return how


def links_from(path: dict, block: str) -> list:
    found = []
    for event in path["events"]:
        if event["event"] == "link" and event["from"] == block:
            found.append({"to": event["to"], "at": event["at"], "text": event["text"]})
    return found


def links_through_stores(checkout: str, path: dict, block: str, kind: str, stores: dict) -> list:
    """The links other builder functions add to the stores the path put
    `block` in, kept when the tests over them name no kind, or a kind at or
    above the node's."""
    found = []
    chain = clang_reader.chain_of(kind, stmt_nodes(checkout))
    walked = walked_functions(path)
    for event in path["events"]:
        if event["event"] == "stored" and event["block"] == block:
            add_store_sites(found, stores.get(event["what"], []), walked, chain)
    return found


def add_store_sites(found: list, sites: list, walked: list, chain: list) -> None:
    for site in sites:
        if site["in"] in walked:
            continue
        if site["kinds_tested"] and not shares_one(site["kinds_tested"], chain):
            continue
        found.append({"in": site["in"], "at": site["at"], "text": site["text"], "loops": site["loops"]})


def walked_functions(path: dict) -> list:
    found = []
    for event in path["events"]:
        if event["event"] == "walked":
            add_once(found, event["what"])
    return found


def makes_a_branch(marked: list) -> str:
    """"yes" when every path read makes one, "in some paths", "no", or "not read"
    when no path is read to its end."""
    read = 0
    branching = 0
    for path in marked:
        if path["status"] == "stop":
            continue
        read += 1
        if path["branch"] is not None:
            branching += 1
    answer = "no"
    if branching > 0:
        answer = "in some paths"
    if branching == read and read > 0:
        answer = "yes"
    if read == 0:
        answer = "not read"
    return answer


# A path as it is kept


def path_as_record(path: BuilderPath, through: str) -> dict:
    status = path.status
    if status == "return":
        status = ""
    record = {
        "through": through,
        "status": status,
        "why": path.why,
        "tests": tests_as_records(path.tests),
        "events": events_as_records(path.events),
        "returned": value_text(path.returned),
        "first_block": first_block_of(path.returned),
    }
    return record


def first_block_of(value: tuple):
    """The block a function hands back: the HiOp's first (a pair's first)."""
    block = None
    if value[0] == "pair":
        block = block_of(value[1])
    if value[0] in ("block", "member"):
        block = block_of(value)
    return block


def tests_as_records(tests: tuple) -> list:
    records = []
    for what, text, taken, at, detail in tests:
        records.append({"what": what, "text": text, "taken": taken, "at": at, "detail": list(detail)})
    return records


def events_as_records(events: tuple) -> list:
    records = []
    for event in events:
        records.append(event_as_record(event))
    return records


def event_as_record(event: tuple) -> dict:
    """("link", from, to, at, text); every other event (what happened, what,
    the block, at, more)."""
    happened, first, second, at, more = event
    if happened == "link":
        record = {"event": happened, "from": first, "to": second, "at": at, "text": more}
        return record
    record = {"event": happened, "what": first, "block": second, "at": at}
    if happened == "added":
        record["stores_held"] = list(more)
    return record


# read_where_each_part_runs (rules 17 and 18)


def read_where_each_part_runs(checkout: str, branches: dict) -> dict:
    """kind -> each path the builder takes a node of it, with where each part
    that path adds runs, to the path's branch (rule 17); each part named by its
    getter and the slot that getter returns (rule 18). In a path with no
    branch, every part added is at "no branch"."""
    parts = {"label_prefixes": branches["label_prefixes"], "by_kind": {}}
    for kind, found in branches["by_kind"].items():
        parts["by_kind"][kind] = parts_of_a_kind(checkout, kind, found, branches["stores"])
    return parts


def parts_of_a_kind(checkout: str, kind: str, found: dict, stores: dict) -> dict:
    paths = []
    for path in found["paths"]:
        paths.append(parts_of_a_path(checkout, kind, path, stores))
    read = {"sent_to": found["sent_to"], "read_through": found["read_through"],
            "makes_a_branch": found["makes_a_branch"], "paths": paths}
    return read


def parts_of_a_path(checkout: str, kind: str, path: dict, stores: dict) -> dict:
    links = graph_of_a_path(path, stores)
    placed = {
        "through": path["through"],
        "status": path["status"],
        "why": path["why"],
        "tests": tests_with_slots(checkout, kind, path["tests"]),
        "branch": path["branch"],
        "parts": {},
        "every_part": None,
    }
    for event in path["events"]:
        add_placed_event(placed, checkout, kind, event, links, path, stores)
    return placed


def tests_with_slots(checkout: str, kind: str, tests: list) -> list:
    """A test that a part is there, with the slot its getter returns (rule
    18), so combine_bodies can match it to a listing's parts."""
    found = []
    for test in tests:
        kept = dict(test)
        if test["what"] == THERE:
            kept["slot"] = slot_of(checkout, kind, test["text"])["slot"]
        found.append(kept)
    return found


def add_placed_event(placed: dict, checkout: str, kind: str, event: dict, links: dict, path: dict,
                     stores: dict) -> None:
    if event["event"] == "added" and event["what"] not in placed["parts"]:
        placed["parts"][event["what"]] = part_placed(checkout, kind, event, links, path, stores)
    if event["event"] == "every part added" and placed["every_part"] is None:
        placed["every_part"] = part_placed(checkout, kind, event, links, path, stores)


def part_placed(checkout: str, kind: str, event: dict, links: dict, path: dict, stores: dict) -> dict:
    """Rule 17: a part's place, with the lines that decide it: for a part
    behind the branch only through the labels inside it, the lines of the
    other function's links (VisitCaseStmt)."""
    place = NO_BRANCH
    decided_by = []
    branch = path["branch"]
    if branch is not None:
        place = place_of(links, START, END, branch["block"], event["block"])
        decided_by = lines_deciding(path, links, branch, event["block"], place)
    if place == BEHIND and not decided_by:
        decided_by = label_link_lines(event, stores, path)
    read = {
        "getter": event["what"],
        "slot": slot_of(checkout, kind, event["what"])["slot"],
        "place": place,
        "block": event["block"],
        "added_at": event["at"],
        "decided_by": decided_by,
    }
    return read


def graph_of_a_path(path: dict, stores: dict) -> dict:
    """block -> the blocks it links to, over one path: its links; the start
    linked to the block the function hands back; every block not made in
    the path (after, after it, the exit, one made elsewhere) linked to the
    end; and a block held in a member store linked to the parts added while
    it held it, when another function links that store to the labels inside
    them (VisitCaseStmt for a switch's body, rule 15i)."""
    links = {}
    for event in path["events"]:
        add_link_of_an_event(links, event, stores, path)
    if path["first_block"] is not None:
        add_to_list(links, START, path["first_block"])
    add_links_to_the_end(links)
    return links


def add_link_of_an_event(links: dict, event: dict, stores: dict, path: dict) -> None:
    if event["event"] == "link" and event["from"] is not None and event["to"] is not None:
        add_to_list(links, event["from"], event["to"])
    if event["event"] == "added":
        add_links_through_labels(links, event, stores, path)


def add_links_through_labels(links: dict, event: dict, stores: dict, path: dict) -> None:
    walked = walked_functions(path)
    for member, block in event["stores_held"]:
        if labelled_elsewhere(stores.get(member, []), walked):
            add_to_list(links, block, event["block"])


def label_link_lines(event: dict, stores: dict, path: dict) -> list:
    found = []
    walked = walked_functions(path)
    for member, _block in event.get("stores_held", []):
        for site in stores.get(member, []):
            if site["in"] not in walked and site["in"].startswith(BUILDER_CLASS + "::Visit"):
                add_once(found, site["at"])
    return found


def labelled_elsewhere(sites: list, walked: list) -> bool:
    """Whether a function the dispatch sends a kind to, and the path did not
    walk, links the store (VisitCaseStmt: `addSuccessor(SwitchTerminatedBlock,
    CaseBlock, ...)`)."""
    found = False
    for site in sites:
        if site["in"] not in walked and site["in"].startswith(BUILDER_CLASS + "::Visit"):
            found = True
    return found


def add_links_to_the_end(links: dict) -> None:
    blocks = []
    for source, targets in links.items():
        add_once(blocks, source)
        add_all_once(blocks, targets)
    for block in blocks:
        if block not in (START, END) and MADE_BLOCK.match(block) is None:
            add_to_list(links, block, END)


def lines_deciding(path: dict, links: dict, branch: dict, block: str, place: str) -> list:
    """The lines that decide a place: the branch's terminator for a part
    tested; the link back to the test for one run again; the links from the
    branch block that lead to it for one behind; its links for one before."""
    found = []
    if place == TESTED:
        found.append(branch["terminator_at"])
    if place == RUN_AGAIN:
        add_link_lines(found, path, block, branch["block"], links, False)
    if place == BEHIND:
        add_link_lines(found, path, branch["block"], block, links, True)
    if place == BEFORE:
        add_link_lines(found, path, block, branch["block"], links, True)
    return found


def add_link_lines(found: list, path: dict, source: str, target: str, links: dict, leading: bool) -> None:
    """The lines of `source`'s links: to `target`, or (leading) to a block
    from which `target` is reached."""
    for link in links_from(path, source):
        if link["to"] is None:
            continue
        if link["to"] == target or (leading and target in reached(links, link["to"], None)):
            add_once(found, link["at"])


# Rule 17: a place, over one graph of blocks and links


def place_of(links: dict, start: str, end: str, branch: str, block: str) -> str:
    """Where `block` runs to the branch block: tested (it is the branch block);
    run again before the test (reached from the branch block, and linked back
    to it); behind the branch (every chain of links from the start to it
    passes the branch block, and some chain to it does not pass the join);
    before (the
    branch block is reached from it, and it is not reached from the branch
    block); after the join (reached from the branch block, not behind it);
    not reached. The check reads clang's dump with this same function."""
    if block == branch:
        place = TESTED
        return place
    from_branch = reached(links, branch, None)
    if block in from_branch and branch in links.get(block, []):
        place = RUN_AGAIN
        return place
    join = join_of(links, branch, end)
    if is_behind(links, start, branch, join, block):
        place = BEHIND
        return place
    place = NOT_REACHED
    if block in from_branch:
        place = AFTER
    if block not in from_branch and branch in reached(links, block, None):
        place = BEFORE
    return place


def is_behind(links: dict, start: str, branch: str, join, block: str) -> bool:
    reachable = block in reached(links, start, None)
    passes_the_branch = block not in reached(links, start, branch)
    avoids_the_join = join is None or block in reached(links, start, join)
    behind = reachable and passes_the_branch and avoids_the_join
    return behind


def join_of(links: dict, branch: str, end: str):
    """The join: the nearest block every chain of links from the branch block to
    the end passes; None when no chain from the branch block reaches the end."""
    join = None
    if end not in reached(links, branch, None):
        return join
    for candidate in blocks_in_reach_order(links, branch):
        if candidate != branch and end not in reached(links, branch, candidate):
            join = candidate
            break
    return join


def reached(links: dict, block: str, removed) -> list:
    """The blocks reached from `block`, itself among them, never entering
    `removed`."""
    found = []
    if block == removed:
        return found
    pending = [block]
    while pending:
        current = pending.pop(0)
        if current in found:
            continue
        found.append(current)
        add_next_blocks(pending, links, current, removed)
    return found


def add_next_blocks(pending: list, links: dict, block: str, removed) -> None:
    for target in links.get(block, []):
        if target != removed:
            pending.append(target)


def blocks_in_reach_order(links: dict, block: str) -> list:
    found = reached(links, block, None)
    return found


# Rule 18: the slot a getter returns


def slot_of(checkout: str, kind: str, getter) -> dict:
    """The slot `getter` returns for a node of `kind`: the `return` of its body
    in the kind's class or the first class above it that defines it, read
    through casts and a `? ... : nullptr` (`return cast<Expr>(SubExprs[LHS]);`
    -> `SubExprs[LHS]`)."""
    slot = {"slot": None, "at": None}
    if getter is None or kind not in stmt_nodes(checkout):
        return slot
    functions = class_functions(checkout)
    for owner in clang_reader.chain_of(kind, stmt_nodes(checkout)):
        defined = getter_defined(functions, owner, getter)
        if defined is not None:
            slot = {"slot": slot_text(defined["returns"]), "at": defined["at"], "class": owner}
            break
    return slot


def getter_defined(functions: dict, owner: str, getter: str):
    found = None
    for defined in functions.get(owner, {}).get(getter, []):
        if defined["returns"] is not None and found is None:
            found = defined
    return found


def slot_text(returned: str) -> str:
    text = returned
    stripped = slot_stripped_once(text)
    while stripped != text:
        text = stripped
        stripped = slot_stripped_once(text)
    return text


def slot_stripped_once(text: str) -> str:
    stripped = text
    chosen = SLOT_CHOICE.match(text)
    if chosen is not None:
        stripped = chosen.group(1).strip()
        return stripped
    cast = SLOT_CAST.match(text)
    if cast is not None:
        stripped = cast.group(1).strip()
    return stripped


@functools.lru_cache(maxsize=None)
def class_functions(checkout: str) -> dict:
    """class -> function -> [{parameters, returns, at}], for each function a
    class of Stmt.h, Expr.h or ExprCXX.h defines in its braces, and each
    `Class::function` they define outside them; `returns` is the text of its
    first `return`."""
    functions = {}
    for relative in CLASS_FILES:
        add_class_functions_of_a_file(functions, checkout, relative)
    return functions


def add_class_functions_of_a_file(functions: dict, checkout: str, relative: str) -> None:
    root = parsed_file(checkout, relative).root_node
    for node in nodes_of_type(root, ("class_specifier", "struct_specifier")):
        add_functions_of_a_class(functions, node, relative)
    for node in root.named_children:
        if node.type == "function_definition":
            add_function_outside_its_class(functions, node, relative)


def add_functions_of_a_class(functions: dict, node, relative: str) -> None:
    name = node.child_by_field_name("name")
    body = node.child_by_field_name("body")
    if name is None or body is None:
        return
    for part in body.named_children:
        if part.type == "function_definition":
            add_class_function(functions, name.text.decode(), part, relative)


def add_function_outside_its_class(functions: dict, node, relative: str) -> None:
    declarator = cpp_code.function_declarator(node)
    if declarator is None:
        return
    written = cpp_code.collapsed(declarator.child_by_field_name("declarator").text.decode())
    if "::" in written:
        add_class_function(functions, written.split("::")[0], node, relative)


def add_class_function(functions: dict, owner: str, node, relative: str) -> None:
    declarator = cpp_code.function_declarator(node)
    if declarator is None or node.child_by_field_name("body") is None:
        return
    name = cpp_code.collapsed(declarator.child_by_field_name("declarator").text.decode()).split("::")[-1]
    defined = {
        "parameters": parameter_names(declarator),
        "returns": first_return_text(node),
        "at": where(relative, line_of(node)),
    }
    if owner not in functions:
        functions[owner] = {}
    add_to_list(functions[owner], name, defined)


def parameter_names(declarator) -> list:
    names = []
    parameters = declarator.child_by_field_name("parameters")
    for parameter in parameters.named_children:
        if parameter.type in ("parameter_declaration", "optional_parameter_declaration"):
            names.append(cpp_code.declared_name(parameter.child_by_field_name("declarator")))
    return names


def first_return_text(node):
    text = None
    returns = return_statements(node.child_by_field_name("body"))
    for statement in returns:
        value = returned_value(statement)
        if value is not None:
            text = cpp_code.collapsed(value.text.decode(errors="replace"))
            break
    return text


# read_how_each_part_is_written (rule 19)


@functools.lru_cache(maxsize=None)
def read_how_each_part_is_written(checkout: str) -> dict:
    """kind -> each path of operator_reader's walk through clang's write-back code (StmtPrinter.cpp),
    through operator_reader's walk (rule 19): each part with how it is written
    (as a statement, `PrintStmt`; as an operand, `PrintExpr` or `Visit`), the
    getter that takes it, the slot that getter returns, and the call."""
    functions = write_back_functions(checkout)
    names = write_back_names(functions)
    written = {"by_kind": {}, "left_out": []}
    for kind in concrete_kinds(checkout):
        add_written_kind(written, checkout, kind, functions, names)
    return written


def write_back_functions(checkout: str) -> dict:
    """StmtPrinter.cpp's functions, as operator_reader reads them, with no list
    clang's build makes (so AtomicExpr's switch over one is not read)."""
    functions = cpp_code.read_functions(checkout, STMT_PRINTER, ())
    return functions


def add_written_kind(written: dict, checkout: str, kind: str, functions: dict, names: dict) -> None:
    owner = clang_reader.printer_owner(kind, stmt_nodes(checkout), functions)
    if owner is None:
        written["left_out"].append(left_out(kind, "", "clang has no StmtPrinter function that writes it"))
        return
    function = functions[clang_reader.PRINTER_CLASS + "::Visit" + owner]
    if MADE_LIST_INCLUDE in function.body.text:
        why = "its write-back code switches over a list clang's build makes (an `#include` of clang-tblgen's)"
        written["by_kind"][kind] = written_without_paths(function, functions, why)
        return
    table = written_table(kind, functions, names)
    found, reason = operator_walk.ways_of(function.body, table, clang_reader.WAY_LIMIT)
    if reason is not None:
        written["by_kind"][kind] = written_without_paths(function, functions, reason)
        return
    written["by_kind"][kind] = written_paths(checkout, kind, function, found)


def written_without_paths(function, functions: dict, why: str) -> dict:
    """A kind whose paths are not read: whether its code writes any part as a
    statement at all (a call of PrintStmt in it or the helpers it calls)."""
    record = {
        "function": function.name,
        "at": where(STMT_PRINTER, function.line),
        "paths": [],
        "stopped": [],
        "not_read": why,
        "writes_a_statement": statement_call_in(function.body, functions, []),
    }
    return record


def statement_call_in(code, functions: dict, seen: list) -> bool:
    """Whether `code`, or a function of StmtPrinter it calls, calls PrintStmt."""
    found = False
    if code.form == "call":
        found = statement_call_in_a_call(code, functions, seen)
    for inner in operator_walk.inner_codes(code):
        if statement_call_in(inner, functions, seen):
            found = True
    return found


def statement_call_in_a_call(code, functions: dict, seen: list) -> bool:
    callee = code.parts[0]
    found = False
    if callee.form != "name":
        return found
    name = callee.parts[0]
    if name == clang_reader.STATEMENT_CALL:
        found = True
        return found
    called = functions.get(clang_reader.PRINTER_CLASS + "::" + name)
    if called is None:
        called = functions.get(name)
    if called is not None and name not in seen:
        seen.append(name)
        found = statement_call_in(called.body, functions, seen)
    return found


def written_paths(checkout: str, kind: str, function, found: tuple) -> dict:
    record = {"function": function.name, "at": where(STMT_PRINTER, function.line), "paths": [], "stopped": [],
              "not_read": None}
    for walked in found:
        add_written_path(record, checkout, kind, walked)
    return record


def add_written_path(record: dict, checkout: str, kind: str, walked) -> None:
    if walked.status == "stop":
        record["stopped"].append(walked.reason)
        return
    try:
        spelling, letters = spelling_of(walked.pieces)
    except ValueError as too_many:
        record["stopped"].append(str(too_many))
        return
    parts = []
    for letter, piece in zip(letters, pieces_not_text(walked.pieces)):
        parts.append(written_part(checkout, kind, letter, piece))
    record["paths"].append({"spelling": spelling, "parts": parts, "decided": decided_records(walked.decided)})


def pieces_not_text(pieces: tuple) -> list:
    found = []
    for piece in pieces:
        if piece[0] != "text":
            found.append(piece)
    return found


def decided_records(decided: tuple) -> dict:
    records = {}
    for condition, outcome in decided:
        records[condition] = outcome
    return records


def written_part(checkout: str, kind: str, letter: str, piece: tuple) -> dict:
    """One letter of a path of operator_reader's walk: a type or a name; or an operand piece, with how it
    is written, the getter, the slot, and the call (rule 19)."""
    part = {"letter": letter, "written_as": WRITTEN_AS_OF_A_SORT.get(piece[0], AS_OPERAND), "getter": None}
    if piece[0] != "operand" or len(piece) < 7:
        return part
    _sort, how, getter, argument, line, call, through = piece
    part["written_as"] = how
    part["getter"] = getter
    part["argument"] = argument
    part["call"] = call
    part["at"] = where(STMT_PRINTER, line)
    part["through"] = list(through)
    part["slot"] = slot_of(checkout, kind, getter)["slot"]
    return part


def written_table(kind: str, functions: dict, names: dict):
    """operator_reader's table for `kind` (clang.table_for), with each operand
    piece kept with its call and the part it writes, a helper handed a part
    keeping that part, no list entry chosen (so no list is read), and a
    written entry's spelling read as any text (rule 19)."""
    table = clang_reader.table_for(kind, functions)
    statement = functools.partial(statement_with_its_call, table, names)
    item = functools.partial(item_with_entry_text, table, names)
    written = operator_walk.Table(statement, item, no_list_entry, table.decide, table.follow, table.turns)
    return written


def no_list_entry(code):
    entries = None
    return entries


def item_with_entry_text(table, names: dict, code, walked):
    """A written item operator_reader reads; or, for a call that writes an
    entry's spelling (`BinaryOperator::getOpcodeStr(...)`), or a name the
    function gives such a call's value (`const char *Spelling =
    getTraitSpelling(Node->getKind());`), any text."""
    piece = table.item(code, walked)
    if piece is None and writes_an_entrys_spelling(code, names):
        piece = ("text", ENTRY_TEXT)
    return piece


def writes_an_entrys_spelling(code, names: dict) -> bool:
    written = code.text
    if code.form == "name":
        written = names_at_line(names, code.line).get(code.parts[0])
    if written is None:
        written = ""
    called = ENTRY_SPELLING_CALL.match(written)
    writes = called is not None and called.group(1) in clang_reader.SPELLING_CALLS
    return writes


def statement_with_its_call(table, names: dict, code, walked):
    """What operator_reader reads an expression run as a statement to do,
    each operand piece kept with its call, and each helper handed a part
    keeping that part."""
    effects = table.statement(code, walked)
    if effects is None:
        return effects
    kept = []
    for effect in effects:
        kept.append(effect_with_its_call(effect, code, walked, names))
    found = tuple(kept)
    return found


def effect_with_its_call(effect: tuple, code, walked, names: dict) -> tuple:
    if effect == OPERAND_EFFECT:
        found = ("piece", operand_piece(code, walked, names))
        return found
    if effect[0] == "follow":
        found = follow_keeping_the_part(effect, code, walked, names)
        return found
    return effect


def operand_piece(code, walked, names: dict) -> tuple:
    """("operand", how, getter, argument, line, call, through): `PrintStmt(x)`
    writes x as a statement, `PrintExpr(x)` and `Visit(x)` as an operand."""
    callee, arguments = code.parts
    how = AS_OPERAND
    if callee.parts[0] == clang_reader.STATEMENT_CALL:
        how = AS_STATEMENT
    argument = argument_resolved(arguments[0], code.line, walked, names)
    through = dict(walked.types).get(THROUGH, ())
    piece = ("operand", how, getter_named_in(argument), argument, code.line, callee.parts[0], through)
    return piece


def follow_keeping_the_part(effect: tuple, code, walked, names: dict) -> tuple:
    """A helper the walk follows (`PrintControlledStmt(Node->getBody())`): it
    keeps the helper's name, and, when it is handed a part, that part, for the
    pieces it writes."""
    callee, arguments = code.parts
    through = dict(walked.types).get(THROUGH, ()) + (callee.text + " (" + where(STMT_PRINTER, code.line) + ")",)
    declared = ()
    if len(effect) > 2:
        declared = effect[2]
    kept = declared + ((THROUGH, through),)
    if dict(declared).get(cpp_code.NODE) == clang_reader.PART and arguments:
        kept = kept + ((HANDED, argument_resolved(arguments[0], code.line, walked, names)),)
    found = ("follow", effect[1], kept)
    return found


def argument_resolved(argument, line: int, walked, names: dict) -> str:
    """The part an argument names: `Node` in a helper handed a part is that
    part; a name the function declares is its value (`Stmt *Else =
    If->getElse()`; a loop's `I` over `Node->body()` is each of it); a cast
    around it is read through."""
    text = cast_read_through(argument.text)
    handed = dict(walked.types).get(HANDED)
    if text == cpp_code.NODE and handed is not None:
        resolved = handed
        return resolved
    declared = names_at_line(names, line)
    resolved = text
    if declared.get(text) is not None:
        resolved = declared[text]
    return resolved


def cast_read_through(text: str) -> str:
    inside = text
    cast = A_CAST_AROUND.match(inside)
    while cast is not None:
        inside = cast.group(1).strip()
        cast = A_CAST_AROUND.match(inside)
    return inside


def getter_named_in(argument: str):
    getter = None
    named = GETTER_OF_THE_NODE.match(argument)
    if named is not None:
        getter = named.group(1)
    return getter


def write_back_names(functions: dict) -> dict:
    """For each StmtPrinter function: the lines it spans, and each name it
    declares with the value it is given (a loop over a range: each of it)."""
    names = {"spans": [], "declared": {}}
    for name, function in functions.items():
        add_write_back_names(names, name, function)
    return names


def add_write_back_names(names: dict, name: str, function) -> None:
    names["spans"].append((function.line, last_line_of(function.body), name))
    declared = {}
    collect_write_back_names(function.body, declared)
    names["declared"][name] = declared


def last_line_of(code) -> int:
    last = code.line
    for inner in operator_walk.inner_codes(code):
        last = max(last, last_line_of(inner))
    return last


def collect_write_back_names(code, declared: dict) -> None:
    if code.form == "declare":
        add_declared_values(declared, code)
    if code.form == "loop":
        add_range_name(declared, code)
    for inner in operator_walk.inner_codes(code):
        collect_write_back_names(inner, declared)


def add_declared_values(declared: dict, code) -> None:
    """A name declared twice with two values is not read (None)."""
    for name, _declared_type, value in code.parts:
        if value is None:
            continue
        if name in declared and declared[name] != value.text:
            declared[name] = None
            continue
        declared[name] = value.text


def add_range_name(declared: dict, code) -> None:
    ranged = RANGE_LOOP_HEADER.match(code.text)
    if ranged is not None:
        declared[ranged.group(1)] = "each of " + ranged.group(2)


def names_at_line(names: dict, line: int) -> dict:
    """The names declared by the function whose lines hold `line`."""
    found = {}
    first_of_the_span = -1
    for first, last, name in names["spans"]:
        if first <= line <= last and first > first_of_the_span:
            found = names["declared"][name]
            first_of_the_span = first
    return found


# combine_bodies (rule 20)


def combine_bodies(parts: dict, written: dict, listings_path: str) -> dict:
    """Rule 20: one result per listing of `listings_path`: each part (named by
    its letter in the listing's `template`), how clang writes it, where the
    builder runs it, and whether it is a body; and N, how many are bodies."""
    listings = listings_of_a_file(listings_path)
    bodies = {"file": os.path.basename(listings_path), "listings": []}
    for listing in listings:
        bodies["listings"].append(bodies_of_a_listing(listing, parts, written))
    return bodies


def listings_of_a_file(listings_path: str) -> list:
    """kinds_forms.json's and kinds_builtins.json's `operators`; or
    label_address.json's one, shaped as theirs."""
    with open(listings_path, encoding="utf-8") as listings_file:
        held = json.load(listings_file)
    listings = held.get("operators")
    if listings is None:
        listings = [label_address_listing(listings_path)]
    return listings


def bodies_of_a_listing(listing: dict, parts: dict, written: dict) -> dict:
    kind = listing["name"].split(".")[0]
    found = {
        "position": listing.get("position"),
        "name": listing["name"],
        "template": listing["template"],
        "kind": kind,
        "parsed_as_written": listing["parsed_as_written"],
    }
    if not listing["parsed_as_written"]:
        found["read"] = False
        found["why_not_read"] = "clang did not parse it as written"
        return found
    found["read"] = True
    letters = letters_of_a_listing(listing, kind, written)
    kept = builder_paths_of_a_listing(listing, kind, letters, parts)
    found.update(bodies_of_the_letters(kind, letters, kept, parts))
    return found


# Rule 19: the letters of a listing, and the parts StmtPrinter writes there


def letters_of_a_listing(listing: dict, kind: str, written: dict) -> dict:
    """Each letter of the listing's `template`, matched to the part a path of
    StmtPrinter writes in its place: the paths whose writing is the listing's
    `template`, an entry's spelling read as any text. A builtin's operands
    are its call's arguments."""
    letters = placeholders_of(listing["template"])
    kind_written = written["by_kind"].get(kind)
    if kind_written is None:
        found = letters_not_read(letters, "clang has no StmtPrinter function that writes it", None)
        return found
    if listing["name"].startswith("CallExpr.BI"):
        found = builtin_letters(letters, kind_written)
        return found
    matched = paths_writing(kind_written["paths"], listing["template"])
    if not matched:
        found = letters_without_a_path(letters, kind_written)
        return found
    found = letters_of_the_paths(letters, matched, kind_written)
    return found


def paths_writing(paths: list, written: str) -> list:
    matched = []
    for path in paths:
        if writes_the_listing(path["spelling"], written):
            matched.append(path)
    return matched


def writes_the_listing(spelling: str, written: str) -> bool:
    """A path writes a listing when its writing is the `template`; an entry's
    spelling it writes stands for any text."""
    if ENTRY_TEXT not in spelling:
        same = spelling == written
        return same
    pieces = []
    for piece in spelling.split(ENTRY_TEXT):
        pieces.append(re.escape(piece))
    same = re.fullmatch("(.+?)".join(pieces), written) is not None
    return same


def letters_of_the_paths(letters: list, matched: list, kind_written: dict) -> dict:
    found = []
    for letter in letters:
        found.append(letter_across_paths(letter, matched))
    record = {
        "letters": found,
        "paths_matched": len(matched),
        "decided": tests_decided_by_all(matched),
        "kind_getters": getters_written_for_the_kind(kind_written),
    }
    return record


def letter_across_paths(letter: str, matched: list) -> dict:
    """The part a letter stands for in every path that writes the listing; not
    read when two paths write it as different parts."""
    seen = []
    for path in matched:
        add_once(seen, part_of_a_letter(path, letter))
    if len(seen) == 1:
        found = dict(seen[0])
        return found
    found = {"letter": letter, "written_as": None, "getter": None,
             "not_read": "the paths that write this listing write this letter as different parts: " + json.dumps(seen)}
    return found


def part_of_a_letter(path: dict, letter: str) -> dict:
    found = {"letter": letter, "written_as": None, "getter": None, "not_read": "no part of the path has this letter"}
    for part in path["parts"]:
        if part["letter"] == letter:
            found = part
    return found


def tests_decided_by_all(matched: list) -> dict:
    """The tests of the node every matched path decided, the same path."""
    decided = dict(matched[0]["decided"])
    for path in matched[1:]:
        for condition in list(decided):
            if path["decided"].get(condition) != decided[condition]:
                del decided[condition]
    return decided


def getters_written_for_the_kind(kind_written: dict) -> list:
    """Every getter, and the slot it returns, that some path of the kind writes."""
    found = []
    for path in kind_written["paths"]:
        for part in path["parts"]:
            if part.get("getter") is not None:
                add_once(found, (part["getter"], part.get("slot")))
    return found


def builtin_letters(letters: list, kind_written: dict) -> dict:
    """A builtin call writes its name, then its arguments, each by
    PrintCallArgs's call (`PrintExpr(Node->getArg(i))`): the argument of the
    path that writes `a(b)`."""
    argument = None
    for path in kind_written["paths"]:
        if path["spelling"] == "a(b)" and len(path["parts"]) == 2:
            argument = path["parts"][1]
    if argument is None:
        found = letters_not_read(letters, "no path of CallExpr writes `a(b)`", kind_written)
        return found
    found_letters = []
    for letter in letters:
        part = dict(argument)
        part["letter"] = letter
        part["argument"] = "each argument (" + argument.get("argument", "") + ")"
        found_letters.append(part)
    found = {"letters": found_letters, "paths_matched": 1, "decided": {},
             "kind_getters": getters_written_for_the_kind(kind_written)}
    return found


def letters_without_a_path(letters: list, kind_written: dict) -> dict:
    """No path of StmtPrinter writes the listing (its walk is not read, or none
    matches). When the kind's code calls no PrintStmt, every value letter is
    written as an operand all the same; else the letters are not read."""
    why = kind_written.get("not_read")
    if why is None:
        why = "no path of StmtPrinter writes this listing"
    if kind_written.get("writes_a_statement") is not False or kind_written["paths"]:
        found = letters_not_read(letters, why, kind_written)
        return found
    found_letters = []
    for letter in letters:
        found_letters.append(letter_with_no_statement_call(letter, why))
    found = {"letters": found_letters, "paths_matched": 0, "decided": {}, "kind_getters": []}
    return found


def letter_with_no_statement_call(letter: str, why: str) -> dict:
    written_as = AS_OPERAND
    if letter in TYPE_LETTERS:
        written_as = AS_TYPE
    if letter in NAME_LETTERS:
        written_as = AS_NAME
    found = {"letter": letter, "written_as": written_as, "getter": None,
             "how_read": "its kind's write-back code calls no PrintStmt (" + why + ")"}
    return found


def letters_not_read(letters: list, why: str, kind_written) -> dict:
    found_letters = []
    for letter in letters:
        found_letters.append({"letter": letter, "written_as": None, "getter": None, "not_read": why})
    kind_getters = []
    if kind_written is not None:
        kind_getters = getters_written_for_the_kind(kind_written)
    found = {"letters": found_letters, "paths_matched": 0, "decided": {}, "kind_getters": kind_getters}
    return found


# Rule 14d and 14i: the builder's paths that fit a listing


def builder_paths_of_a_listing(listing: dict, kind: str, letters: dict, parts: dict) -> list:
    """The builder's paths for the listing's kind whose every test holds for
    the listing, as far as the listing decides it: its list entry (rule 14c),
    the parts it writes (14d), the tests of the node its written path took
    (14i)."""
    kept = []
    kind_parts = parts["by_kind"].get(kind)
    if kind_parts is None:
        return kept
    fit = listing_fit(listing, letters, parts["label_prefixes"], kind_parts["paths"])
    for path in kind_parts["paths"]:
        if path_fits(path, fit) and adds_the_parts_it_can(path, fit):
            kept.append(path)
    return kept


def listing_fit(listing: dict, letters: dict, prefixes: list, paths: list) -> dict:
    entry = None
    if "." in listing["name"]:
        entry = listing["name"].split(".", 1)[1]
    fit = {
        "entry": entry,
        "prefixes": prefixes,
        "decided": letters["decided"],
        "written": parts_written(letters["letters"]),
        "kind_getters": letters["kind_getters"],
        "added_by_the_kind": parts_added_in(paths),
    }
    return fit


def parts_added_in(paths: list) -> list:
    """(getter, slot) of every part some path of the kind adds."""
    found = []
    for path in paths:
        for part in path["parts"].values():
            add_once(found, (part["getter"], part["slot"]))
    return found


def adds_the_parts_it_can(path: dict, fit: dict) -> bool:
    """Rule 14d: a path that adds none of a part the listing writes, when
    another path of the kind adds it, is a path for a node without that part
    (`if (opaqueValue)` for `a ?: b`), and does not fit the listing."""
    fits = True
    if path["every_part"] is not None or path["status"] == "stop":
        return fits
    for getter, slot in fit["written"]:
        added_somewhere = same_part_in(getter, slot, fit["added_by_the_kind"])
        if added_somewhere and part_in_a_path({"getter": getter, "slot": slot}, path["parts"]) is None:
            fits = False
    return fits


def parts_written(letters: list) -> list:
    found = []
    for letter in letters:
        if letter.get("getter") is not None:
            found.append((letter["getter"], letter.get("slot")))
    return found


def path_fits(path: dict, fit: dict) -> bool:
    fits = True
    for test in path["tests"]:
        holds = test_holds_for(test, fit)
        if holds is not None and holds != test["taken"]:
            fits = False
    return fits


def test_holds_for(test: dict, fit: dict):
    """Whether the listing makes a test hold; None when it does not decide."""
    holds = None
    if test["what"] == THERE:
        holds = part_there_for(test, fit)
    if test["what"] == ENTRY_TEST:
        holds = entry_test_for(test, fit)
    if test["what"] == NODE_TEST:
        holds = fit["decided"].get(test["text"])
    return holds


def part_there_for(test: dict, fit: dict):
    """Rule 14d: a part is there when the listing writes it; not there when
    some path of its kind writes it and the listing does not; else not
    decided (`F->getConditionVariable()`)."""
    there = None
    if same_part_in(test["text"], test.get("slot"), fit["written"]):
        there = True
        return there
    if same_part_in(test["text"], test.get("slot"), fit["kind_getters"]):
        there = False
    return there


def same_part_in(getter: str, slot, getters: list) -> bool:
    found = False
    for written_getter, written_slot in getters:
        if written_getter == getter or (slot is not None and written_slot == slot):
            found = True
    return found


def entry_test_for(test: dict, fit: dict):
    """Rule 14c: a comparison with a label, or a predicate over the entry,
    for the listing's entry (`LAnd`: label `BO_LAnd`)."""
    holds = None
    entry = fit["entry"]
    detail = test["detail"]
    if entry is None or not detail:
        return holds
    if detail[0] == "compares":
        same = label_names_entry(detail[2], entry, fit["prefixes"])
        holds = same == (detail[1] == "==")
    if detail[0] == "predicate":
        holds = entry_predicate_holds(detail[2], detail[1], entry, fit["prefixes"])
    return holds


def label_names_entry(label: str, entry: str, prefixes: list) -> bool:
    names = False
    for prefix in prefixes:
        if label == prefix + entry:
            names = True
    return names


def entry_predicate_holds(test_text: str, variable: str, entry: str, prefixes: list):
    """A predicate's `return` (`Opc == BO_LAnd || Opc==BO_LOr`) for one entry:
    comparisons by `==` and `!=`, joined by `||` and `&&`; any other is not
    read (None)."""
    holds = False
    for alternative in test_text.split("||"):
        outcome = alternative_holds(alternative, variable, entry, prefixes)
        if outcome is None:
            return outcome
        if outcome:
            holds = True
    return holds


def alternative_holds(alternative: str, variable: str, entry: str, prefixes: list):
    holds = True
    for term in alternative.split("&&"):
        outcome = term_holds(term, variable, entry, prefixes)
        if outcome is None:
            return outcome
        if not outcome:
            holds = False
    return holds


def term_holds(term: str, variable: str, entry: str, prefixes: list):
    holds = None
    compared = ENTRY_COMPARED.match(term.strip().strip("()"))
    if compared is None or compared.group(1) != variable:
        return holds
    same = label_names_entry(compared.group(3), entry, prefixes)
    holds = same == (compared.group(2) == "==")
    return holds


# Rule 20: a body


def bodies_of_the_letters(kind: str, letters: dict, kept: list, parts: dict) -> dict:
    kind_parts = parts["by_kind"].get(kind, {"paths": [], "sent_to": None, "makes_a_branch": "not read"})
    read = []
    for letter in letters["letters"]:
        read.append(body_of_a_letter(letter, kept))
    found = {
        "builder": kind_parts["sent_to"],
        "kind_makes_a_branch": kind_parts["makes_a_branch"],
        "listing_makes_a_branch": branch_in_the_paths(kept),
        "builder_paths_kept": len(kept),
        "builder_paths_of_the_kind": len(kind_parts["paths"]),
        "letters_matched_by": letters["paths_matched"],
        "parts": read,
        "bodies": letters_where(read, True),
        "N": len(letters_where(read, True)),
        "not_read": letters_where(read, None),
    }
    return found


def branch_in_the_paths(kept: list) -> str:
    read = 0
    branching = 0
    for path in kept:
        if path["status"] == "stop":
            continue
        read += 1
        if path["branch"] is not None:
            branching += 1
    answer = "no"
    if branching > 0:
        answer = "in some paths"
    if branching == read and read > 0:
        answer = "yes"
    if read == 0:
        answer = "not read"
    return answer


def body_of_a_letter(letter: dict, kept: list) -> dict:
    """Rule 20: a part written as a statement is a body; one written as an
    operand is a body when it runs behind the branch or again before the
    test; a type, a name, or an operand tested, before, after or with no
    branch is not."""
    record = dict(letter)
    places = places_of_a_letter(letter, kept)
    record["places"] = places
    record["place"] = one_place(places)
    body, why = body_decided(record["written_as"], places)
    record["body"] = body
    record["why"] = why
    return record


def places_of_a_letter(letter: dict, kept: list) -> list:
    """The letter's part in each path kept: where it runs, with the lines; a
    path not read to its end gives "not read"."""
    places = []
    if letter.get("written_as") in (AS_TYPE, AS_NAME):
        places.append({"place": NOT_ADDED, "why": letter["written_as"] + ": the builder adds statements and"
                       " expressions, the node's parts (rule 18), and no " + letter["written_as"][2:]})
        return places
    for path in kept:
        add_once(places, place_in_a_path(letter, path))
    return places


def place_in_a_path(letter: dict, path: dict) -> dict:
    if path["status"] == "stop":
        found = {"place": "not read", "why": path["why"]}
        return found
    part = part_in_a_path(letter, path["parts"])
    if part is not None:
        found = {"place": part["place"], "getter": part["getter"], "added_at": part["added_at"],
                 "decided_by": part["decided_by"]}
        return found
    if path["every_part"] is not None:
        found = {"place": path["every_part"]["place"], "getter": "every part (VisitChildren)",
                 "added_at": path["every_part"]["added_at"], "decided_by": path["every_part"]["decided_by"]}
        return found
    found = {"place": NOT_ADDED, "through": path["through"]}
    return found


def part_in_a_path(letter: dict, path_parts: dict):
    """The part a path adds that is the letter's: the same getter, or a getter
    that returns the same slot (rule 18)."""
    found = None
    getter = letter.get("getter")
    slot = letter.get("slot")
    for part in path_parts.values():
        if getter is not None and (part["getter"] == getter or (slot is not None and part["slot"] == slot)):
            found = part
    return found


def one_place(places: list) -> str:
    seen = []
    for place in places:
        add_once(seen, place["place"])
    found = "not read"
    if len(seen) == 1:
        found = seen[0]
    if len(seen) > 1:
        found = DIFFERS_BY_PATH + ": " + ", ".join(seen)
    return found


def body_decided(written_as, places: list) -> tuple:
    if written_as is None:
        found = (None, "how clang writes it is not read")
        return found
    if written_as == AS_STATEMENT:
        found = (True, "written as a statement (PrintStmt)")
        return found
    if written_as != AS_OPERAND:
        found = (False, "written as " + written_as)
        return found
    found = operand_body_decided(places)
    return found


def operand_body_decided(places: list) -> tuple:
    """An operand: a body in every path read, or in none; else not read."""
    answers = []
    for place in places:
        add_once(answers, place["place"] in BODY_PLACES)
    if not places or any_not_read(places):
        found = (None, "an operand whose place is not read in every path")
        return found
    if answers == [True]:
        found = (True, "an operand " + places[0]["place"])
        return found
    if answers == [False]:
        found = (False, "an operand " + one_place(places))
        return found
    found = (None, "an operand, a body in some paths and not in others: " + one_place(places))
    return found


def any_not_read(places: list) -> bool:
    found = False
    for place in places:
        if place["place"] == "not read":
            found = True
    return found


def letters_where(read: list, body) -> list:
    found = []
    for letter in read:
        if letter["body"] is body:
            found.append(letter["letter"])
    return found


# Step 3 across the vocabulary: every listing file, and every kind that branches


def bodies_of_the_files(checkout: str, listing_files: tuple) -> dict:
    """file -> which_parts_are_bodies for each listing it holds."""
    bodies = {}
    for listings_path in listing_files:
        bodies[os.path.basename(listings_path)] = which_parts_are_bodies(checkout, listings_path)
    return bodies


def kinds_that_branch(checkout: str, bodies: dict) -> list:
    """Every kind a path of the builder makes a branch for, with the GNU C
    listings that hold it: in the files read, in gnu_c_sort.json, and in
    pass_a_forms.json (its `accepted` of its `cells`)."""
    branches = read_branches(checkout)
    elsewhere = listed_elsewhere()
    found = []
    for kind, read in branches["by_kind"].items():
        if read["makes_a_branch"] in ("yes", "in some paths"):
            found.append(kind_and_its_listings(kind, read, bodies, elsewhere))
    return found


def listed_elsewhere() -> dict:
    with open(SORTED_LISTINGS, encoding="utf-8") as sorted_file:
        sorted_listings = json.load(sorted_file)["operators"]
    with open(PASS_A_LISTINGS, encoding="utf-8") as pass_a_file:
        pass_a = json.load(pass_a_file)["operators"]
    found = {"gnu_c_sort.json": sorted_listings, "pass_a_forms.json": pass_a}
    return found


def kind_and_its_listings(kind: str, read: dict, bodies: dict, elsewhere: dict) -> dict:
    found = {
        "kind": kind,
        "makes_a_branch": read["makes_a_branch"],
        "builder": read["sent_to"],
        "read_through": read["read_through"],
        "branches": branch_evidence(read["paths"]),
        "listings": listings_of_a_kind(kind, bodies),
        "in_gnu_c_sort": sorted_names_of_a_kind(kind, elsewhere["gnu_c_sort.json"]),
        "in_pass_a_forms": pass_a_forms_of_a_kind(kind, elsewhere["pass_a_forms.json"]),
    }
    return found


def branch_evidence(paths: list) -> list:
    """For each path with a branch: what the path went through, its tests, and
    the branch block's terminator and links."""
    found = []
    for path in paths:
        if path["branch"] is not None:
            found.append({"through": path["through"], "tests": tests_written_short(path["tests"]),
                          "branch": path["branch"]})
    return found


def tests_written_short(tests: list) -> list:
    found = []
    for test in tests:
        found.append(f"{test['text']}: {test['taken']} ({test['at']})")
    return found


def listings_of_a_kind(kind: str, bodies: dict) -> list:
    found = []
    for file_name, read in bodies.items():
        add_listings_of_a_kind(found, kind, file_name, read["listings"])
    return found


def add_listings_of_a_kind(found: list, kind: str, file_name: str, listings: list) -> None:
    for listing in listings:
        if listing["kind"] == kind:
            found.append({"file": file_name, "template": listing["template"], "name": listing["name"],
                          "parsed_as_written": listing["parsed_as_written"],
                          "makes_a_branch": listing.get("listing_makes_a_branch")})


def sorted_names_of_a_kind(kind: str, sorted_listings: list) -> list:
    found = []
    for listing in sorted_listings:
        if listing["operator"].split(".")[0] == kind:
            found.append(listing["operator"])
    return found


def pass_a_forms_of_a_kind(kind: str, pass_a: list) -> list:
    found = []
    for listing in pass_a:
        if listing["name"].split(".")[0] == kind:
            found.append({"template": listing["template"], "accepted": listing["accepted"], "cells": listing["cells"]})
    return found


def calls_apart(checkout: str) -> dict:
    """What VisitCallExpr treats apart, read from its tests: the builtins
    whose arguments it does not add (`Builtin::BI...` named in its tests),
    and the builtins Builtins.td marks NoReturn, whose call ends a block
    (createNoReturnBlock)."""
    omitted = []
    definitions = definitions_named(read_every_function(checkout, BUILDER), BUILDER_CLASS + "::VisitCallExpr")
    for name in re.findall(r"\bBuiltin::BI(\w+)", definitions[0].node.text.decode()):
        add_once(omitted, name)
    side_effects = definitions_named(read_every_function(checkout, BUILDER), "isBuiltinAssumeWithSideEffects")
    for name in re.findall(r"\bBuiltin::BI(\w+)", side_effects[0].node.text.decode()):
        add_once(omitted, name)
    found = {"named_in_its_tests": omitted, "at": where(BUILDER, definitions[0].line),
             "no_return": no_return_builtins(checkout)}
    return found


def no_return_builtins(checkout: str) -> list:
    """The spellings Builtins.td gives the builtins whose Attributes hold
    NoReturn."""
    found = []
    text = file_text(checkout, BUILTIN_LIST)
    for defined in NO_RETURN_BUILTIN.finditer(text):
        add_no_return_spellings(found, defined.group(1))
    return found


def add_no_return_spellings(found: list, body: str) -> None:
    attributes = BUILTIN_ATTRIBUTES.search(body)
    spellings = BUILTIN_SPELLINGS.search(body)
    if attributes is None or spellings is None or NO_RETURN not in attributes.group(1):
        return
    for spelling in re.findall(r'"([^"]+)"', spellings.group(1)):
        add_once(found, spelling)
    if "AddBuiltinPrefixedAlias = 1" in body:
        for spelling in re.findall(r'"([^"]+)"', spellings.group(1)):
            add_once(found, "__builtin_" + spelling)


# Writing step 3


def with_what_bodies_read(bodies: dict, branching: list, checkout: str) -> dict:
    """Step 3's answer, with the files it was read from and their sha256."""
    recorded = {
        "what": "which parts of each GNU C listing are bodies, read from clang's control-flow builder (CFG.cpp)"
                " and its write-back code (StmtPrinter.cpp) (dependent_HiOp_reader, step 3: rules 12 to 20)",
        "clang_source": os.path.join(os.environ.get("PSEUDOARCH_SOURCES", ""), checkout),
        "clang_files_read": body_file_hashes(checkout),
        "listings": listing_hashes(),
        "the_eight": the_eight(bodies),
        "counts": counts_of_the_files(bodies),
        "kinds_that_branch": branching,
        "calls_treated_apart": calls_apart(checkout),
        "read_through": read_branches(checkout)["read_through"],
        "written_left_out": read_how_each_part_is_written(checkout)["left_out"],
        "by_file": bodies,
    }
    return recorded


def body_file_hashes(checkout: str) -> dict:
    hashes = {}
    for relative in BODY_FILES:
        hashes[relative] = sha256_of(declaring_file_path(checkout, relative))
    return hashes


def listing_hashes() -> dict:
    hashes = {}
    for path in LISTING_FILES + (PASS_A_LISTINGS, SORTED_LISTINGS):
        hashes[path] = sha256_of(path)
    return hashes


def the_eight(bodies: dict) -> list:
    """The 8 listings of step 3, as kinds_forms.json holds them."""
    found = []
    for listing in bodies[os.path.basename(LISTINGS)]["listings"]:
        if listing["template"] in THE_EIGHT and listing["parsed_as_written"]:
            found.append(listing)
    return found


def counts_of_the_files(bodies: dict) -> dict:
    counts = {}
    for file_name, read in bodies.items():
        counts[file_name] = counts_of_a_file(read["listings"])
    return counts


def counts_of_a_file(listings: list) -> dict:
    """The whole and its parts: listings read and not; of those read, with a
    branch and without; N per listing where N > 0; letters not read."""
    counts = {"listings": len(listings), "read": 0, "not_read": {}, "with_a_branch": 0, "with_no_branch": 0,
              "branch_not_read": 0, "with_bodies": {}, "letters_not_read": {}}
    for listing in listings:
        add_listing_count(counts, listing)
    return counts


def add_listing_count(counts: dict, listing: dict) -> None:
    key = f"{listing['position']}: {listing['template']} ({listing['name']})"
    if not listing["read"]:
        add_to_list(counts["not_read"], listing["why_not_read"], key)
        return
    counts["read"] += 1
    if listing["listing_makes_a_branch"] in ("yes", "in some paths"):
        counts["with_a_branch"] += 1
    if listing["listing_makes_a_branch"] == "no":
        counts["with_no_branch"] += 1
    if listing["listing_makes_a_branch"] == "not read":
        counts["branch_not_read"] += 1
    if listing["N"] > 0:
        counts["with_bodies"][key] = listing["N"]
    if listing["not_read"]:
        counts["letters_not_read"][key] = listing["not_read"]


def print_bodies(recorded: dict) -> None:
    print("step 3: which parts are bodies")
    for listing in recorded["the_eight"]:
        print_listing_bodies(listing)
    for file_name, counts in recorded["counts"].items():
        print_file_counts(file_name, counts)
    print(f"kinds the builder makes a branch for: {len(recorded['kinds_that_branch'])}")
    for kind in recorded["kinds_that_branch"]:
        print_kind_that_branches(kind)


def print_kind_that_branches(kind: dict) -> None:
    """A kind, the GNU C listings of it (parsed as written, and of those, the
    ones with a branch), and the other two lists."""
    parsed = 0
    branching = []
    for listing in kind["listings"]:
        if listing["parsed_as_written"]:
            parsed += 1
        if listing["makes_a_branch"] in ("yes", "in some paths"):
            branching.append(listing["template"])
    accepted = []
    for form in kind["in_pass_a_forms"]:
        if form["accepted"] > 0:
            accepted.append(f"{form['template']} (`accepted` {form['accepted']} of `cells` {form['cells']})")
    print(f"  {kind['kind']:26s} {kind['makes_a_branch']:13s} listings {len(kind['listings'])}, parsed as written"
          f" {parsed}, with a branch {len(branching)}: {joined_or_none(branching, ', ')};"
          f" gnu_c_sort.json {len(kind['in_gnu_c_sort'])}; pass_a_forms.json {len(kind['in_pass_a_forms'])} forms,"
          f" with `accepted` above 0 {len(accepted)}: {joined_or_none(accepted, '; ')}")


def joined_or_none(items: list, joiner: str) -> str:
    written = "none"
    if items:
        written = joiner.join(items)
    return written


def print_listing_bodies(listing: dict) -> None:
    print(f"  {listing['template']:20s} {listing['name']:28s} N = {listing['N']}: {', '.join(listing['bodies'])}"
          f"  (not read: {joined_or_none(listing['not_read'], ', ')})")
    for part in listing["parts"]:
        print(f"      {part['letter']}  {str(part.get('getter')):14s} {str(part['written_as']):10s}"
              f" {part['place']:28s} body: {part['body']}  ({part['why']})")


def print_file_counts(file_name: str, counts: dict) -> None:
    whole = counts["listings"]
    not_read = whole - counts["read"]
    print(f"{file_name}: {whole} listings; read {counts['read']} of {whole}; not read {not_read} of {whole}")
    for why, listings in counts["not_read"].items():
        print(f"  not read, {why}: {len(listings)}")
    print(f"  of the {counts['read']} read: with a branch {counts['with_a_branch']}, with none"
          f" {counts['with_no_branch']}, not read {counts['branch_not_read']}")
    print(f"  with N > 0: {len(counts['with_bodies'])} of {counts['read']}")
    for key, count in counts["with_bodies"].items():
        print(f"    N = {count}: {key}")
    print(f"  with a letter not read: {len(counts['letters_not_read'])} of {counts['read']}")


# Reading C++ with tree-sitter


@functools.lru_cache(maxsize=None)
def cpp_parser():
    import tree_sitter
    import tree_sitter_cpp
    parser = tree_sitter.Parser(tree_sitter.Language(tree_sitter_cpp.language()))
    return parser


@functools.lru_cache(maxsize=None)
def parsed_file(checkout: str, relative: str):
    path = declaring_file_path(checkout, relative)
    with open(path, "rb") as source_file:
        tree = cpp_parser().parse(source_file.read())
    return tree


@functools.lru_cache(maxsize=None)
def read_every_function(checkout: str, relative: str) -> tuple:
    """Every function `relative` defines, in the file's order. Unlike
    cpp_code.read_functions, which keeps one definition per name, it keeps
    every one (clang defines `getBreakParent` twice in Scope.h and
    `ParseCompoundStatement` twice in ParseStmt.cpp)."""
    tree = parsed_file(checkout, relative)
    definitions = []
    collect_definitions(tree.root_node, definitions)
    found = tuple(definitions)
    return found


def collect_definitions(node, definitions: list) -> None:
    if node.type == "function_definition":
        add_definition(definitions, node)
        return
    for part in node.children:
        collect_definitions(part, definitions)


def add_definition(definitions: list, node) -> None:
    declarator = cpp_code.function_declarator(node)
    if declarator is None or node.child_by_field_name("body") is None:
        return
    name = cpp_code.collapsed(declarator.child_by_field_name("declarator").text.decode())
    definitions.append(Definition(name, node.start_point[0] + 1, node))


def body_of(definition: Definition):
    """The function's body as cpp_code's Code, every name as written (no
    first parameter renamed to `Node`)."""
    reader = cpp_code.Reader("", cpp_parser())
    body = reader.statement(definition.node.child_by_field_name("body"))
    return body


def definitions_named(definitions: tuple, name: str) -> list:
    found = []
    for definition in definitions:
        if definition.name == name:
            found.append(definition)
    return found


def definition_at(checkout: str, relative: str, name: str, line: int) -> Definition:
    found = None
    definitions = definitions_named(read_every_function(checkout, relative), name)
    for definition in definitions:
        if definition.line == line:
            found = definition
    return found


def calls_in(node) -> list:
    """Every call expression inside a tree-sitter node."""
    calls = []
    collect_calls(node, calls)
    return calls


def collect_calls(node, calls: list) -> None:
    if node.type == "call_expression":
        calls.append(node)
    for part in node.children:
        collect_calls(part, calls)


def names_declared_in(node) -> list:
    """Every name a function declares: its parameters and its locals."""
    names = []
    collect_declared_names(node, names)
    return names


def collect_declared_names(node, names: list) -> None:
    if node.type in ("declaration", "parameter_declaration"):
        declarators = node.children_by_field_name("declarator")
        for declarator in declarators:
            add_once(names, cpp_code.declared_name(declarator))
    for part in node.children:
        collect_declared_names(part, names)


def statements_under_tests(code) -> list:
    """(statement, tests) for every statement in `code` that holds no other
    statement; the tests it stands under, outermost first."""
    found = []
    collect_statements(code, (), found)
    return found


def collect_statements(code, tests: tuple, found: list) -> None:
    if code is None:
        return
    if code.form == "block":
        for part in code.parts:
            collect_statements(part, tests, found)
        return
    if code.form == "if":
        collect_statements(code.parts[1], tests + (Test(code.parts[0], "true"),), found)
        collect_statements(code.parts[2], tests + (Test(code.parts[0], "false"),), found)
        return
    if code.form == "loop":
        collect_statements(code.parts[1], tests + (Test(code, "each turn of the loop"),), found)
        return
    if code.form == "switch":
        collect_from_cases(code, tests, found)
        return
    found.append((code, tests))


def collect_from_cases(code, tests: tuple, found: list) -> None:
    for case in code.parts[1]:
        for statement in case.parts[1]:
            collect_statements(statement, tests + (Test(case, "this case"),), found)


def tests_written(tests: tuple) -> list:
    written = []
    for test in tests:
        written.append({"test": test_text(test), "taken": test.taken})
    return written


def test_text(test: Test) -> str:
    """An `if`'s condition or a loop's header as written; a case as
    `case <its labels>` (its own text holds its whole body)."""
    text = test.code.text
    if test.code.form == "case":
        text = "case " + labels_text(test.code.parts[0])
    return text


def labels_text(labels) -> str:
    text = "default"
    if labels is not None:
        text = ", ".join(label_texts(labels))
    return text


def label_texts(labels) -> list:
    texts = []
    for label in labels:
        texts.append(label.text)
    return texts


# Reading C++ with tree-sitter, step 2: names, the statements and tests
# around them, the values a function returns and gives its names


def uses_of_name(checkout: str, relative: str, name: str) -> list:
    """Each place a function of `relative` names `name` (`diag::err_...`,
    `CheckPoppedLabel`, `Scope::FnScope`), in the file's order."""
    uses = []
    definitions = read_every_function(checkout, relative)
    for definition in definitions:
        if name in definition.node.text.decode(errors="replace"):
            add_all(uses, uses_in_definition(definition, name, relative))
    return uses


def uses_in_definition(definition: Definition, name: str, relative: str) -> list:
    uses = []
    body = definition.node.child_by_field_name("body")
    nodes = nodes_named(body, name)
    for node in nodes:
        uses.append(Use(definition, node, relative))
    return uses


def uses_matching(checkout: str, relative: str, pattern) -> list:
    """Each place a function of `relative` names a name that `pattern`
    matches."""
    uses = []
    definitions = read_every_function(checkout, relative)
    for definition in definitions:
        nodes = nodes_matching(definition.node.child_by_field_name("body"), pattern)
        for node in nodes:
            uses.append(Use(definition, node, relative))
    return uses


def nodes_named(node, name: str) -> list:
    found = []
    pending = [node]
    while pending:
        current = pending.pop()
        if current.type in NAME_NODES and current.text.decode() == name:
            found.append(current)
            continue
        pending.extend(current.children)
    found.sort(key=start_of)
    return found


def nodes_matching(node, pattern) -> list:
    found = []
    pending = [node]
    while pending:
        current = pending.pop()
        if current.type in NAME_NODES and pattern.match(current.text.decode()) is not None:
            found.append(current)
            continue
        pending.extend(current.children)
    found.sort(key=start_of)
    return found


def nodes_of_type(node, types: tuple) -> list:
    found = []
    pending = [node]
    while pending:
        current = pending.pop()
        if current.type in types:
            found.append(current)
        pending.extend(current.children)
    found.sort(key=start_of)
    return found


def start_of(node) -> int:
    start = node.start_byte
    return start


def line_of(node) -> int:
    line = node.start_point[0] + 1
    return line


def short_text(node) -> str:
    text = cpp_code.collapsed(node.text.decode(errors="replace"))
    if len(text) > 160:
        text = text[:157] + "..."
    return text


def callee_text(call) -> str:
    callee = call.child_by_field_name("function")
    text = callee.text.decode()
    return text


def statement_of(node):
    """The statement a node stands in: the nearest expression statement,
    return, declaration or jump around it."""
    found = node
    current = node
    while current is not None and current.type not in STATEMENT_NODES and current.type != "function_definition":
        current = current.parent
    if current is not None and current.type in STATEMENT_NODES:
        found = current
    return found


def statement_read(use: Use) -> dict:
    """Where a name stands: its function, its statement, the tests around it."""
    read = read_node(use.relative, use.definition, use.node)
    return read


def statements_read(uses: list) -> list:
    reads = []
    for use in uses:
        reads.append(statement_read(use))
    return reads


def read_node(relative: str, definition: Definition, node) -> dict:
    """Where a name or a call stands: `at` is its own line (the line that
    names a diagnostic), `statement_at` the first line of its statement."""
    statement = statement_of(node)
    read = {
        "in": definition.name,
        "function_line": definition.line,
        "file": relative,
        "line": line_of(node),
        "at": where(relative, line_of(node)),
        "statement_at": where(relative, line_of(statement)),
        "text": short_text(statement),
        "under": tests_around(node, relative),
        "condition": condition_around(node),
        "argument_of": argument_of(node),
        "emitted": is_emitted(node),
    }
    return read


def argument_of(node):
    """{"call": the called name, "index": the argument's place} for the call
    `node` is an argument of; None when it is an argument of none."""
    found = None
    argument, call = argument_and_call(node)
    if call is not None:
        found = {"call": called_name(call), "index": argument_index(call, argument)}
    return found


def is_emitted(node) -> bool:
    """Whether `node` stands inside the arguments of a call named `...Diag`
    (`Diag(...)`, `S.Diag(...)`, `S.PDiag(...)`)."""
    emitted = False
    argument, call = argument_and_call(node)
    while call is not None:
        name = called_name(call)
        if name is not None and EMITTING_CALL.search(name) is not None:
            emitted = True
            break
        argument, call = argument_and_call(call)
    return emitted


def tests_around(node, relative: str) -> list:
    """The tests `node` stands under, outermost first: each `if` (and the
    branch it stands in), loop, case and `? :` around it, up to its function."""
    tests = []
    child = node
    parent = node.parent
    while parent is not None and parent.type != "function_definition":
        add_test_of(tests, parent, child, relative)
        child = parent
        parent = parent.parent
    tests.reverse()
    return tests


def add_test_of(tests: list, parent, child, relative: str) -> None:
    if parent.type == "if_statement":
        add_branch_test(tests, parent, child, relative)
    if parent.type in LOOP_NODES and is_the_field(parent, "body", child):
        tests.append(test_read(loop_header(parent), "each turn of the loop", line_of(parent), relative))
    if parent.type == "case_statement" and not is_the_field(parent, "value", child):
        tests.append(test_read(case_text(parent), "this case", line_of(parent), relative))
    if parent.type == "conditional_expression":
        add_choice_test(tests, parent, child, relative)


def add_branch_test(tests: list, statement, child, relative: str) -> None:
    condition = statement.child_by_field_name("condition")
    text = condition_text(condition)
    if is_the_field(statement, "consequence", child):
        tests.append(test_read(text, "true", line_of(condition), relative))
    if is_the_field(statement, "alternative", child):
        tests.append(test_read(text, "false", line_of(condition), relative))


def add_choice_test(tests: list, choice, child, relative: str) -> None:
    condition = choice.child_by_field_name("condition")
    text = short_text(condition)
    if is_the_field(choice, "consequence", child):
        tests.append(test_read(text, "true", line_of(condition), relative))
    if is_the_field(choice, "alternative", child):
        tests.append(test_read(text, "false", line_of(condition), relative))


def test_read(text: str, taken: str, line: int, relative: str) -> dict:
    read = {"test": text, "taken": taken, "at": where(relative, line)}
    return read


def tests_texts(tests: list) -> list:
    texts = []
    for test in tests:
        texts.append((test["test"], test["taken"]))
    return texts


def condition_text(condition) -> str:
    """An `if`'s condition without its parentheses."""
    text = short_text(condition)
    if text.startswith("(") and text.endswith(")"):
        text = text[1:-1].strip()
    return text


def condition_around(node):
    """The whole condition a node stands in, when it stands in one
    (`if (S.getLangOpts().MSVCCompat && ... && IsMicrosoftJumpWarning(...))`)."""
    condition = None
    current = node.parent
    while current is not None and current.type != "function_definition":
        if current.type == "condition_clause":
            condition = condition_text(current)
            break
        current = current.parent
    return condition


def loop_header(node) -> str:
    body = node.child_by_field_name("body")
    text = short_text(node)
    if body is not None:
        text = cpp_code.collapsed(node.text[: body.start_byte - node.start_byte].decode(errors="replace"))
    return text


def case_text(node) -> str:
    value = node.child_by_field_name("value")
    text = "default"
    if value is not None:
        text = "case " + value.text.decode()
    return text


def is_the_field(parent, field: str, child) -> bool:
    found = parent.child_by_field_name(field)
    answer = found is not None and found.id == child.id
    return answer


def leaving_tests_before(node, relative: str) -> list:
    """The `if (...) goto/break/return` statements before `node`'s statement
    in the case or block it stands in: the tests that skip it."""
    skipped = []
    statement = statement_of(node)
    holder = statement.parent
    if holder is None:
        return skipped
    for part in holder.named_children:
        if part.start_byte >= statement.start_byte:
            break
        add_leaving_test(skipped, part, relative)
    return skipped


def add_leaving_test(skipped: list, part, relative: str) -> None:
    if part.type != "if_statement":
        return
    consequence = part.child_by_field_name("consequence")
    if consequence is None or consequence.type not in LEAVING_NODES:
        return
    condition = part.child_by_field_name("condition")
    skipped.append({"test": condition_text(condition), "then": short_text(consequence),
                    "at": where(relative, line_of(part))})


def argument_and_call(node) -> tuple:
    """The argument `node` stands in, and the call it is an argument of;
    (None, None) when it stands in none."""
    child = node
    current = node.parent
    while current is not None and current.type not in STATEMENT_NODES:
        if current.type == "argument_list" and current.parent is not None and current.parent.type in (
                "call_expression", "new_expression"):
            found = (child, current.parent)
            return found
        child = current
        current = current.parent
    found = (None, None)
    return found


def argument_index(call, argument) -> int:
    index = -1
    arguments = arguments_of(call)
    for position in range(len(arguments)):
        if arguments[position].id == argument.id:
            index = position
    return index


def arguments_node(call):
    arguments = call.child_by_field_name("arguments")
    return arguments


def arguments_of(call) -> list:
    found = []
    arguments = arguments_node(call)
    if arguments is None:
        return found
    for part in arguments.named_children:
        if part.type != "comment":
            found.append(part)
    return found


def argument_named(call, name: str) -> bool:
    found = argument_node_named(call, name) is not None
    return found


def argument_node_named(call, name: str):
    found = None
    arguments = arguments_of(call)
    for argument in arguments:
        if argument.type == "identifier" and argument.text.decode() == name:
            found = argument
    return found


def names_in_node(node) -> list:
    names = []
    identifiers = nodes_of_type(node, ("identifier",))
    for identifier in identifiers:
        add_once(names, identifier.text.decode())
    return names


def enclosing_call(node):
    """The call whose function `node` names (`Actions.LookupOrCreateLabel(...)`,
    `CaseVals.push_back(...)`); None when a statement comes first."""
    call = None
    current = node.parent
    while current is not None and current.type not in STATEMENT_NODES:
        if current.type == "call_expression":
            call = current
            break
        current = current.parent
    return call


def name_given(node):
    """The name a value is given to: `LabelDecl *LD = <node>` or `X = <node>`
    -> LD or X; else None."""
    name = None
    current = node
    while current is not None and current.type not in STATEMENT_NODES:
        if current.type == "init_declarator":
            name = cpp_code.declared_name(current.child_by_field_name("declarator"))
            break
        if current.type == "assignment_expression":
            name = assigned_name(current)
            break
        current = current.parent
    return name


def assigned_name(assignment):
    name = None
    left = assignment.child_by_field_name("left")
    if left is not None and left.type == "identifier":
        name = left.text.decode()
    return name


def calls_named(node, name: str) -> list:
    """Each call under `node` of a function named `name`, plainly or as a
    member (`PushOnScopeChains(...)`, `Actions.ActOnPopScope(...)`)."""
    found = []
    calls = calls_in(node)
    for call in calls:
        if called_name(call) == name:
            found.append(call)
    return found


def called_name(call):
    name = None
    callee = call.child_by_field_name("function")
    if callee is None:
        return name
    if callee.type in ("identifier", "qualified_identifier"):
        name = callee.text.decode()
    if callee.type == "field_expression":
        name = callee.child_by_field_name("field").text.decode()
    return name


def calls_of(checkout: str, relative: str, functions: list) -> list:
    """Each call, in `relative`, of one of `functions` (by the name after its
    class)."""
    calls = []
    names = short_names(functions)
    definitions = read_every_function(checkout, relative)
    for definition in definitions:
        for name in names:
            add_calls_named(calls, definition, name, relative)
    return calls


def add_calls_named(calls: list, definition: Definition, name: str, relative: str) -> None:
    found = calls_named(definition.node.child_by_field_name("body"), name)
    for call in found:
        calls.append(read_node(relative, definition, call))


def member_calls(checkout: str, relative: str, holder: str, method: str) -> list:
    """Each `holder.method(...)` in `relative`."""
    uses = []
    definitions = read_every_function(checkout, relative)
    for definition in definitions:
        add_all(uses, member_calls_in(definition, holder, method, relative))
    return uses


def member_calls_in(definition: Definition, holder: str, method: str, relative: str) -> list:
    uses = []
    fields = nodes_of_type(definition.node, ("field_expression",))
    for field in fields:
        if is_member_call(field, holder, method):
            uses.append(Use(definition, field.child_by_field_name("field"), relative))
    return uses


def is_member_call(field, holder: str, method: str) -> bool:
    argument = field.child_by_field_name("argument")
    name = field.child_by_field_name("field")
    answer = False
    if argument is None or name is None or field.parent is None:
        return answer
    if argument.text.decode() == holder and name.text.decode() == method:
        answer = field.parent.type == "call_expression"
    return answer


def uses_outside_their_class(checkout: str, relative: str, classes: list) -> list:
    """Each place a function outside the class `C` names `C` (the class made
    and run: `JumpScopeChecker(Body, *this)`)."""
    uses = []
    for name in classes:
        found = uses_of_name(checkout, relative, name)
        for use in found:
            if not use.definition.name.startswith(name + "::"):
                uses.append(use)
    reads = statements_read(uses)
    return reads


def classes_of(functions: list) -> list:
    classes = []
    for function in functions:
        if "::" in function:
            add_once(classes, function.split("::")[0])
    return classes


def parameter_name_at(definition: Definition, index: int):
    name = None
    declarator = cpp_code.function_declarator(definition.node)
    parameters = declarator.child_by_field_name("parameters")
    found = []
    for parameter in parameters.named_children:
        if parameter.type == "parameter_declaration":
            found.append(cpp_code.declared_name(parameter.child_by_field_name("declarator")))
    if 0 <= index < len(found):
        name = found[index]
    return name


def parameters_text(definition: Definition) -> str:
    declarator = cpp_code.function_declarator(definition.node)
    text = short_text(declarator.child_by_field_name("parameters"))
    return text


def functions_of(reads: list) -> list:
    functions = []
    for read in reads:
        add_once(functions, read["in"])
    return functions


def definitions_of_uses(uses: list) -> list:
    found = []
    lines = []
    for use in uses:
        if use.definition.line not in lines:
            lines.append(use.definition.line)
            found.append(use.definition)
    return found


def short_names(functions: list) -> list:
    """`Sema::ActOnPopScope` -> ActOnPopScope."""
    names = []
    for function in functions:
        add_once(names, function.split("::")[-1])
    return names


def refusals_named(checkout: str, relative: str, diagnostic: str, texts: dict) -> list:
    """Each statement of `relative` that names `diag::<diagnostic>`, with its
    function, tests, and the words of the diagnostic."""
    refusals = []
    uses = uses_of_name(checkout, relative, "diag::" + diagnostic)
    for use in uses:
        refusal = statement_read(use)
        refusal["refusal"] = diagnostic
        refusal["says"] = texts.get(diagnostic, {}).get("text")
        refusal["says_at"] = texts.get(diagnostic, {}).get("at")
        refusals.append(refusal)
    return refusals


# The values a function returns, and gives its names (rule 3)


def returned_values(function_node) -> list:
    """The values a function hands back: the value of each `return` (not one
    inside a lambda), and for a returned name, every value given to that
    name, followed through other names (`Res = Actions.ActOnGotoStmt(...)`
    ... `return Res;`; `TopLevelCase = Case;`)."""
    values = []
    names = []
    returns = return_statements(function_node)
    for statement in returns:
        add_returned(values, names, statement)
    given = values_given_to_names(function_node)
    add_values_of_names(values, names, given)
    return values


def return_statements(node) -> list:
    """Every `return` under `node`, but none inside a lambda."""
    found = []
    collect_returns(node, found)
    return found


def collect_returns(node, found: list) -> None:
    if node.type == "lambda_expression":
        return
    if node.type == "return_statement":
        found.append(node)
    for part in node.children:
        collect_returns(part, found)


def add_returned(values: list, names: list, statement) -> None:
    value = returned_value(statement)
    if value is None:
        return
    if value.type == "identifier":
        add_once(names, value.text.decode())
        return
    values.append(value)


def returned_value(statement):
    """The expression a `return` hands back, without its parentheses; None for
    `return;`."""
    value = None
    for part in statement.named_children:
        if part.type != "comment":
            value = without_parentheses(part)
            break
    return value


def add_values_of_names(values: list, names: list, given: dict) -> None:
    pending = list(names)
    seen = []
    while pending:
        name = pending.pop()
        if name in seen:
            continue
        seen.append(name)
        for value in given.get(name, []):
            add_given_value(values, pending, value)


def add_given_value(values: list, pending: list, value) -> None:
    if value.type == "identifier":
        pending.append(value.text.decode())
        return
    values.append(value)


def values_given_to_names(node) -> dict:
    """name -> every value a declaration or an `=` under `node` gives it,
    lambdas included (`[&]() { R = ParseCompoundStatementBody(...); }`)."""
    given = {}
    collect_given_values(node, given)
    return given


def collect_given_values(node, given: dict) -> None:
    if node.type == "init_declarator":
        add_initial_values(given, node)
    if node.type == "assignment_expression":
        add_assigned_value(given, node)
    for part in node.children:
        collect_given_values(part, given)


def add_initial_values(given: dict, node) -> None:
    name = cpp_code.declared_name(node.child_by_field_name("declarator"))
    value = node.child_by_field_name("value")
    if not name or value is None:
        return
    if value.type in ("argument_list", "initializer_list"):
        for part in value.named_children:
            add_to_list(given, name, without_parentheses(part))
        return
    add_to_list(given, name, without_parentheses(value))


def add_assigned_value(given: dict, node) -> None:
    operator = node.child_by_field_name("operator")
    name = assigned_name(node)
    if operator is None or operator.text.decode() != "=" or name is None:
        return
    add_to_list(given, name, without_parentheses(node.child_by_field_name("right")))


def without_parentheses(node):
    current = node
    while current is not None and current.type == "parenthesized_expression" and len(current.named_children) == 1:
        current = current.named_children[0]
    return current


def is_one_of(node, nodes: list) -> bool:
    found = False
    for other in nodes:
        if other.id == node.id:
            found = True
    return found


# clang's kinds, and the words of its diagnostics


def concrete_kinds(checkout: str) -> dict:
    """kind -> the line StmtNodes.td declares it on, for every kind that is
    not abstract."""
    kinds = {}
    nodes = clang_reader.read_clang_stmt_nodes(checkout, STMT_NODES)
    for kind, (_base, is_abstract, line) in nodes.items():
        if not is_abstract:
            kinds[kind] = line
    return kinds


def statement_kinds(checkout: str) -> list:
    """Every kind StmtNodes.td declares that is not an expression (not Expr,
    nor below Expr)."""
    statements = []
    nodes = clang_reader.read_clang_stmt_nodes(checkout, STMT_NODES)
    for kind in nodes:
        if "Expr" not in clang_reader.chain_of(kind, nodes):
            statements.append(kind)
    return statements


def concrete_kinds_below(checkout: str, name: str) -> list:
    """`GotoStmt` -> [GotoStmt]; `SwitchCase` -> [CaseStmt, DefaultStmt],
    the concrete kinds below an abstract one; a root (Stmt, ValueStmt, Expr)
    or anything else -> []."""
    found = []
    nodes = stmt_nodes(checkout)
    if name not in nodes or name in ROOT_KINDS:
        return found
    for kind, (_base, is_abstract, _line) in nodes.items():
        if not is_abstract and name in clang_reader.chain_of(kind, nodes):
            found.append(kind)
    return found


@functools.lru_cache(maxsize=None)
def stmt_nodes(checkout: str) -> dict:
    nodes = clang_reader.read_clang_stmt_nodes(checkout, STMT_NODES)
    return nodes


def kind_named_by(name: str, pattern, suffix: str, kinds: dict):
    """`Sema::ActOnBreakStmt` -> BreakStmt, when StmtNodes.td declares the
    kind; else None."""
    kind = None
    named = pattern.match(name)
    if named is not None and named.group(1) + suffix in kinds:
        kind = named.group(1) + suffix
    return kind


@functools.lru_cache(maxsize=None)
def diagnostic_texts(checkout: str) -> dict:
    """name -> its words and where they are, for every diagnostic of
    DiagnosticSemaKinds.td and DiagnosticParseKinds.td."""
    texts = {}
    for relative in DIAGNOSTIC_FILES:
        add_diagnostic_texts(texts, checkout, relative)
    return texts


def add_diagnostic_texts(texts: dict, checkout: str, relative: str) -> None:
    path = declaring_file_path(checkout, relative)
    with open(path, encoding="utf-8") as diagnostics_file:
        written = diagnostics_file.read()
    for defined in DIAGNOSTIC_DEFINED.finditer(written):
        words = words_after(written, defined.end())
        if words is None:
            continue
        line = written.count("\n", 0, defined.start()) + 1
        texts[defined.group(1)] = {"kind": defined.group(2), "text": words, "at": where(relative, line)}


def words_after(written: str, start: int):
    """The quoted words right after `def name : Kind<`, pieces joined."""
    pieces = []
    position = start
    found = QUOTED.match(written, position)
    while found is not None:
        pieces.append(found.group(1))
        position = found.end()
        found = QUOTED.match(written, position)
    words = None
    if pieces:
        words = "".join(pieces)
    return words


# Small helpers


def where(relative: str, line: int) -> str:
    place = f"{relative}:{line}"
    return place


def not_read(why: str) -> dict:
    kept = {"what": None, "why": why}
    return kept


def left_out(what: str, at: str, why: str) -> dict:
    kept = {"what": what, "at": at, "why": why}
    return kept


def add_once(items: list, item) -> None:
    if item not in items:
        items.append(item)


def add_to_list(lists: dict, key: str, item) -> None:
    if key not in lists:
        lists[key] = []
    lists[key].append(item)


def add_all(items: list, more: list) -> None:
    for item in more:
        items.append(item)


def add_all_once(items: list, more: list) -> None:
    for item in more:
        add_once(items, item)


def shares_one(first: list, second: list) -> bool:
    shared = False
    for item in first:
        if item in second:
            shared = True
    return shared


# Writing


def with_what_was_read(places: dict, checkout: str, listings_path: str, label_address_path: str) -> dict:
    """The answer, with the files it was read from and their sha256."""
    recorded = {
        "what": "where each dependent-HiOp of GNU C may stand and what it needs, read from clang's source"
                " (dependent_HiOp_reader, steps 1 and 2)",
        "clang_source": os.path.join(os.environ.get("PSEUDOARCH_SOURCES", ""), checkout),
        "clang_files_read": file_hashes(checkout),
        "listings": listings_path,
        "listings_sha256": sha256_of(listings_path),
        "label_address": label_address_path,
        "label_address_sha256": sha256_of(label_address_path),
        "by_listing": places["by_listing"],
        "function_rules": places["function_rules"],
        "switch_rules": places["switch_rules"],
        "left_out": places["left_out"],
    }
    return recorded


def file_hashes(checkout: str) -> dict:
    hashes = {}
    for relative in CLANG_FILES:
        hashes[relative] = sha256_of(declaring_file_path(checkout, relative))
    return hashes


def sha256_of(path: str) -> str:
    with open(path, "rb") as read_file:
        digest = hashlib.sha256(read_file.read()).hexdigest()
    return digest


def write_json(record: dict, path: str) -> None:
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as written_file:
        json.dump(record, written_file, indent=1)
        written_file.write("\n")


def print_places(places: dict) -> None:
    listings = places["by_listing"]
    placed = count_placed(listings)
    print(f"dependent listings: {len(listings)}; read {placed} of {len(listings)}, not read {len(listings) - placed}")
    for listing, found in listings.items():
        print_one_listing(listing, found)
    print_function_rules(places["function_rules"])
    print(f"left out: {len(places['left_out'])}")
    for kept in places["left_out"]:
        print(f"  {kept['what']} ({kept['at']}): {kept['why']}")


def count_placed(listings: dict) -> int:
    placed = 0
    for found in listings.values():
        if found["placed"] is not None:
            placed += 1
    return placed


def print_one_listing(listing: str, found: dict) -> None:
    if found["placed"] is None:
        print(f"  {listing:20s} {found['kind']}: not read ({found['not_read']['at']}): {found['not_read']['why']}")
        return
    if found["placed"] == BY_THE_WHOLE_FUNCTION:
        print_needing_listing(listing, found)
    else:
        print_placed_listing(listing, found)
    for rule in found["one_switch"]:
        print(f"      in one switch: {rule['refusal']} ({', '.join(rule['at'])}): {rule['says']}")
    for rule in found["may_not_enter"]:
        print(f"      may not enter: {rule['refusal']} ({', '.join(rule['at'])}); tests the in-note: {rule['tests_the_in_note']}")


def print_placed_listing(listing: str, found: dict) -> None:
    asks = found["asks"]
    print(f"  {listing:20s} {found['kind']}: refused by {asks['refusal']} ({asks['refusal_at']})")
    print(f"      asks for {asks['asks']['what']}: {asks['asks']['text']} ({asks['asks']['at']})")
    for step in found["link"]:
        print(f"      link: {step['step']}: {step.get('text', '')} ({step.get('at', '')})")
    print(f"      places: {len(found['places'])}: {', '.join(found['places'])}")
    for kind, evidence in found["givers"].items():
        print(f"        {kind}: {', '.join(places_of_evidence(evidence))}")


def print_needing_listing(listing: str, found: dict) -> None:
    needs = found["needs_in_the_same_function"]
    same = ""
    if needs["with_the_same_label"]:
        same = ", with the same label"
    print(f"  {listing:20s} {found['kind']}: refused by {', '.join(needs['refusal'])} ({', '.join(needs['refusal_at'])})")
    print(f"      needs in the same function: {', '.join(needs['kinds'])}{same}")


def print_function_rules(rules: dict) -> None:
    protected = rules["places_a_jump_may_not_enter"]
    print(f"places a jump may not enter (in-notes): {len(protected['places'])}")
    for place in protected["places"]:
        print(f"  {place['note']:45s} {place['at']}  {place['says']}")
    for warned in protected["only_a_warning_in_c"]:
        print(f"  {warned['function']} ({warned['at']}): holds in C: {warned['holds_in_c']}; notes {', '.join(warned['notes'])}")
    for diagnostic, refusal in protected["refusals"].items():
        print(f"  {diagnostic}: jumps {', '.join(refusal['jumps'])}; tests the in-note at"
              f" {', '.join(places_of_evidence(refusal['tests_the_in_note']))}")


def places_of_evidence(evidence: list) -> list:
    lines = []
    for item in evidence:
        add_once(lines, item["at"])
    return lines


if __name__ == "__main__":
    main()
