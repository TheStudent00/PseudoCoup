---
id: hq.projects.pseudocoup.pseudoarch.map_HiOp_to_unit.dict_of_lang_HiOps.support.declared_vocabularies
status: draft
---

# SUPPORT — declared_vocabularies

Where each language's lowerer declares its own operators, its own holders,
and, where it writes them down as data, the pairings between them. Every
path is under `~/Programming/SOURCES/`. Rows were read in the source named,
on 2026-09-23 and 2026-09-28.

## the rule this settles

**The dict is DERIVED from the language, never hand-written.** Every one of
the twelve declares its operators and its holders in its lowerer's own
source. The dict is filled from the lowerer's verdict on operators x holders
(`extract_lang_vocabulary/DRY_mask_maker`, which makes
`grid_mask_of_knowns`). Pairings a language writes
down as data are an ORACLE for that verdict, not its source.

## per language

| language | operators | holders | pairings written down as data |
|---|---|---|---|
| c, cpp | clang `include/clang/Basic/StmtNodes.td`, every expression kind, written out by `lib/AST/StmtPrinter.cpp`; the opcodes of `include/clang/AST/OperationKinds.def` (33 binary, 14 unary). Read at clang 21.1.8: 75 operators (log 307) | clang `include/clang/AST/Type.h`, the `BuiltinType::Kind` enum built from 9 `.def` files (`BuiltinTypes.def` is one), spelled by `lib/AST/Type.cpp` `BuiltinType::getName`. At 21.1.8: 509 types, 514 spellings | none: the usual arithmetic conversions are code in clang's `Sema` |
| go | the compiler's own: `cmd/compile/internal/syntax/tokens.go` (Operators, spellings, precedence groups), `nodes.go`, `printer.go`, `parser.go` (unary); the library's `go/token/token.go` holds the same (48). Read at go1.26.0: 48 operators (log 307 §9) | `cmd/compile/internal/types2/universe.go` (`Typ`, `basicAliases`, `error`/`any`/`comparable`); the library's `go/types/basic.go` `BasicKind` is the same table. At go1.26.0: 32 spellings | `go/types/expr.go:761` `binaryOpPredicates` (`ADD: allNumericOrString`, `REM: allInteger`, `LAND: allBoolean`) crossed with each kind's class bits; comparisons (`:483` `Checker.comparison`) and shifts (`:618` `Checker.shift`) are code, and `:664` gates a signed shift count on go1.13 |
| java | javac `tree/JCTree.java` (the JC classes, the `Tag` enum), classed by `tree/TreeInfo.java` `opPrec`, spelled and written out by `tree/Pretty.java`. Read at javac 25.0.4: 44 operators (log 307 §9d) | javac `code/Symtab.java` `initType` (primitives and their boxes) and the class types `comp/Operators.java` names; `code/TypeTag.java` is the tag list. At 25.0.4: 21 | javac `com/sun/tools/javac/comp/Operators.java`: `addBinaryOperator(lhs, rhs, result, bytecode)` |
| csharp | RuntimeBinder `Semantics/BinOpKind.cs`, and `UnaOpKind` in `Semantics/ExpressionBinder.cs:63` | RuntimeBinder `Syntax/PredefinedType.cs` | RuntimeBinder `Semantics/Operators.cs:87` `InitBinopSignatures`: lhs, rhs and the operator group per row -- the rules C#'s `dynamic` applies, ported from the compiler (roslyn itself is not on disk) |
| rust | the compiler's own: `compiler/rustc_ast/src/ast.rs` (`ExprKind`; `BinOpKind`, `AssignOpKind`, `UnOp` with `as_str`), written out by `rustc_ast_pretty`'s `expr.rs`; the library's traits in `library/core/src/ops/arith.rs`, `bit.rs`, `cmp.rs`. Read at rustc 1.96.1: 41 operators (log 307 §9b) | `compiler/rustc_hir/src/hir.rs`, `PrimTy::from_name`: 19; also the type lists of `core`'s impl macros, e.g. `arith.rs:113` `add_impl! { usize u8 ... f128 }` | the impls themselves: the impl set IS the grid |
| swift | `swift-6.0.3-RELEASE/stdlib/public/core/Policy.swift` | `IntegerTypes.swift.gyb`, `FloatingPointTypes.swift.gyb` | the operator functions each type declares, expanded from the same two files |
| dart | `sdk/sdk/lib/core/num.dart`, `int.dart`, `double.dart`, `bool.dart` | the same classes; `int` and `double` both `extends num` (`int.dart:28`, `double.dart:24`) | the signatures: `num operator +(num other)` covers int and double on both sides; `double operator /(num other)`; `int operator &(int other)` |
| ruby | `ruby-3.3.6/gems/rbs-3.4.0.gem`: `core/integer.rbs`, `core/float.rbs` and kin | the same, one file per class | the signatures: `integer.rbs:251` `def +: (Integer) -> Integer \| (Float) -> Float \| (Rational) -> Rational \| (Complex) -> Complex`; `numeric.c:3942` `fix_plus` branches on the same types |
| php | `php-8.4.0/Zend/zend_vm_opcodes.h` (`ZEND_ADD` ...) | `php-8.4.0/Zend/zend_types.h:600-610` (`IS_UNDEF` ... `IS_REFERENCE`) | `Zend/zend_operators.c:1090` `TYPE_PAIR(IS_LONG, IS_DOUBLE)` and its kin; every other pair goes through the conversion switch at `zend_operators.c:325-366`, which is code |
| python | `Python-3.12.7/Lib/opcode.py:289` `_nb_ops` and `:24` `cmp_op`; `Include/opcode.h` `UNARY_*`. Also asked of the running interpreter: its `ast` module's kinds, printed by `ast.unparse` (read that way at CPython 3.13.15: 53 operators, log 307 §9c) | `Python/bltinmodule.c:3121-3144` (`SETBUILTIN`), each type with its slot table (`Objects/longobject.c:6265` `long_as_number`) | none: `CHECK_BINOP` (`longobject.c:1547`) and `CONVERT_TO_DOUBLE` (`floatobject.c:358`) are code |
| javascript | V8 `chromium_src/src/v8/src/common/operation.h` `OPERATION_LIST` | V8 `src/compiler/turbofan-types.h` (Number, BigInt, String, Boolean, Null, Undefined, Symbol, Receiver ...) | none: the conversions are code |

## where an operator list carries no spellings

The spelling is in the same lowerer's token table. It is a label: it writes
the probe and is never a key.

| language | spelling table |
|---|---|
| javascript | V8 `src/parsing/token.h:47` `E(T, Add, "+", 12)` |
| java | javac `com/sun/tools/javac/parser/Tokens.java:187` `PLUS("+")` |
| csharp | RuntimeBinder `Syntax/TokenFacts.cs:55` `TokenKind.Plus => "+"` |
| python | `Lib/opcode.py:289` `("NB_ADD", "+")`; `:24` `cmp_op` |

## pairings kept only as code: c, cpp, python, javascript

Nothing to read for these four, and nothing is missing: the lowerer judges
the grid, the same as for the other eight. For c and cpp the rule in the code
is the usual arithmetic conversions -- before `a + b` on two types, both are
converted to one common type by a fixed rule in the C standard (narrower
than int becomes int; then double wins, then long, and so on).

## what the declared vocabularies say about the counts we have

| | declared by the language | used by the dict today |
|---|---|---|
| c holders | 74 builtin types, 11 of them placeholders (read 2026-09-28; the 59 of 2026-09-23 left out the placeholders and the 4 plain `char` and `wchar_t` entries) | 6 |
| go holders | 15 concrete numeric types, plus bool | 5 numeric, plus bool |
| go operators | 48 (`go/token`) | fewer |
| python operator methods on `int` | 21 (asked of the running interpreter, 2026-09-23) | — |
| ruby operator methods on `Integer` | 25 (asked of the running interpreter, 2026-09-23) | — |

Narrow signed and unsigned widths are absent everywhere (`i8`, `i16`, `u8`,
`u16`, `u32`), and **no nullable holder exists at all** — which is why dart's
`a ?? b` and `a!` came out degenerate: at a non-nullable holder they are
identities, and the language never had a chance to show the operation.

## corrections, 2026-09-28

- **ruby and python were listed as "runtime"**, their holders to be probed.
  Wrong: ruby ships its signatures (the rbs gem), and python's operator and
  type lists are in its source.
- **javascript was missing** from the table.
- **"Eleven of twelve declare the operator x holder grid"** was wrong as
  stated: all twelve declare both lists; eight write some pairings down as
  data, four keep them only as code.
- **php's row cited only the `TYPE_PAIR` fast path.** The other pairs are in
  the conversion switch of the same file, not in a second source.
- **The shapes table** (five ways a language writes its pairings down) is
  superseded, with the five readers it described.

*(2026-09-27: the go gates, swift, rust and csharp rows were read by Fable's
run of 2026-09-26, which is reverted; each file and line above was checked
against the source on disk before it was kept.)*
