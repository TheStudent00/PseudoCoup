#!/usr/bin/env python3
"""enumerate_branch_candidates.py -- every branch of a test in clang's code that
no context of an operator has taken, read from the binary and the lines
records, its condition read from clang's source, the holder (or constant,
width, shape, option) that would take it written as a context (a HiOp
variant-candidate), traced with the owner's method, and looped until every branch
is taken or shown closed (PCHQ plan: research/trace_logical_paths,
enumerate_branch_candidates; log 492 §2.2.7, log 493 §4).

the owner, 2026-10-21 (to Gemini): "i talked about enumerating every path so that
the branching structure is flattened into a bunch of straight paths." And
2026-10-18, 04:26 UTC (the conversation of research node trace_logical_paths):
"the conditions of the control flow branches, the things that we are using
to enumerate all the paths, are the things we use to construct the HiOp
variant-candidates (supposed HiOps that could be accepted or refused)".

Written 2026-10-21 from take_every_side.py (its first version, kept beside it
as it was): the same logic, with the owner's word, branch, in every name, record
and message, and the record branch_candidates.json. Two of the first version's
closings are gone, at the owner's word through logs 493 and 494: a test of clang's
insert point (HaveInsertPoint, GetInsertBlock) stays open, since a statement
before the operator reaches it (PCHQ log 489 §25).

the owner, 2026-10-20: "RUN IT": every line of clang's code that the method could
take and no run has taken is run on, by the method itself.

A branch's outcome is one of four (the owner, 2026-10-20):
    taken          a context (one of the records' or a candidate, of this
                   operator or another) ran it
    cannot reach   the method cannot take it; the reason is its badge: the
                   standard form never writes it, the target (not on
                   riscv64), clang's own bookkeeping
    not needed     another language than GNU C: C++, Objective-C, OpenMP,
                   OpenCL, HLSL, CUDA, ...
    open           a candidate was traced and did not take it (the candidate
                   that failed it is kept), or its condition is not read yet

The record, under OUT: branch_candidates.json (per operator, every branch with its
function, file, test line, untaken block, condition, kind, change,
candidates and outcome), paths.json (the brute force's form, the candidates
traced) and lines.json (the lines run's form, the candidates' lines), each
written after every round of every operator.

usage (in a run):
    enumerate_branch_candidates.py CLANG_DIR OUT --keys FILE [--rounds N] [--resume]

--rounds is the most rounds of the loop per operator (default 6); 0 lists
the branches and closes what their conditions close, tracing nothing (the
plan's run A). --resume continues the record already in OUT: an operator
done there is skipped, the others go on from their recorded rounds (a
continuation lane finishes what the instance's ceiling cut).

2026-10-20, run l159 read (the owner: "i want every one of these run"; on the
option branches: "if it wasnt used, use it"): an option branch is traced under
its option; a branch some context of any operator ran (every lines record) is
taken; the other languages are "not needed".
"""

import glob
import json
import os
import re
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
RESEARCH_CLONE = os.path.normpath(os.path.join(HERE, '..', '..', '..', '..', '..', 'Research', 'trace_logical_paths_clone'))
if RESEARCH_CLONE not in sys.path:
    sys.path.insert(0, RESEARCH_CLONE)
if HERE not in sys.path:
    sys.path.insert(0, HERE)

import branch_trees  # noqa: E402
import check_trace_logical_paths as check  # noqa: E402
import trace_lines_on_the_paths as lines_run_of_paths  # noqa: E402
from context import KEY, Context, Setup, our_setup, standard_source  # noqa: E402
from lines_run import blocks_in, function_ranges, listing_of, successors_in  # noqa: E402
from trace import names_of, recording_of  # noqa: E402

ROUNDS = 6
SAY_EVERY = 60
# The holders clang accepts somewhere (run elv2_l177): the pool a condition's
# holder is taken from (§4.3).
HOLDERS_FILE = os.path.normpath(os.path.join(HERE, "..", "extract_lang_vocabulary", "reader_joined", "elv2_l177",
                                             "holders.json"))
IN_HIOP_SPANS_FILE = os.environ.get("PSEUDOIR_IN_HIOP_SPANS", os.path.join(HERE, "in_hiop_spans.json"))
# clang's source: the text the traced binary was built from when it is on
# this machine (/persist/traced_clang_src on the VM), otherwise the checkout
# under PSEUDOIR_SOURCES (the run script exports /sources) or the laptop's.
SOURCES_CHECKOUT = "llvm-project-21.1.8"
SOURCES_DEFAULT = os.environ.get("PSEUDOCOUP_SOURCES_DIR", "/sources")
SOURCES_PREFIXES = ("/persist/traced_clang_src/", "/sources/llvm-project-21.1.8/")
# How far a test's statement is read above and below its line.
STATEMENT_REACH = 8
# A branch keeps this many of the contexts that ran its test, for the record.
RAN_BY_KEPT = 4
# A bit-field's width when a condition reads a width (log 479's places).
WIDTH = 13
# The literals a constant part is written as; the trace says which branch each takes.
LITERALS = ("1", "0")

# ---------------------------------------------------------------------------
# §4.2 and the owner's outcome rule. Our setup gives clang no option beyond
# lower_HiOp's command, so a test that reads an option is always decided our
# setup's way, and its other branch needs the option. the owner, 2026-10-20, on the
# option branches: "if it wasnt used, use it": an option branch is traced under
# the option (OPTION_NAMES, the sanitizers), and the trace says taken or
# open. The names that close a branch are the other languages ("not needed")
# and what no program of the standard form has ("cannot reach").
MATRIX_TYPES = ("typedef int m2 __attribute__((matrix_type(2, 2)));",)
# (a name in the test's text, the options a candidate is traced under, the
# holder the option's type needs ("" for none), the declarations it needs)
OPTION_NAMES = [
    ("SOB_Trapping", ("-ftrapv",), "", ()),
    ("isSignedOverflowTrapping", ("-ftrapv",), "", ()),
    ("SOB_Defined", ("-fwrapv",), "", ()),
    ("isSignedOverflowDefined", ("-fwrapv",), "", ()),
    ("isConstantMatrixType", ("-fenable-matrix",), "m2", MATRIX_TYPES),
    ("isMatrixType", ("-fenable-matrix",), "m2", MATRIX_TYPES),
    ("MatrixTypes", ("-fenable-matrix",), "m2", MATRIX_TYPES),
    ("isFixedPointOp", ("-ffixed-point",), "_Accum", ()),
    ("isFixedPointType", ("-ffixed-point",), "_Accum", ()),
    ("FixedPoint", ("-ffixed-point",), "_Accum", ()),
    ("isNullPtrType", ("-std=gnu2x",), "nullptr_t", ("typedef __typeof__(nullptr) nullptr_t;",)),
    ("SanitizeBase", ("-fsanitize=shift",), "", ()),
    ("SanitizeExponent", ("-fsanitize=shift",), "", ()),
    ("FastMath", ("-ffast-math",), "", ()),
    ("getFPEvalMethod", ("-ffp-eval-method=double",), "", ()),
    ("NativeHalfType", ("-Xclang -fnative-half-type",), "", ()),
    ("StrictFloatCastOverflow", ("-fno-strict-float-cast-overflow",), "", ()),
    # 2026-10-21, the owner: "if it runs on it next, run it". The profile and
    # coverage options the eight functions' tests read.
    # CGExprScalar.cpp 5225, VisitBinLAnd: `InstrumentRegions = ...hasProfileClangInstr()`
    ("hasProfileClangInstr", ("-fprofile-instr-generate",), "", ()),
    # CGExprScalar.cpp 5247 and 5312, VisitBinLAnd: `if (InstrumentRegions &&
    # CodeGenFunction::isInstrumentedCondition(E->getRHS()))`; the right part
    # is no `&&` or `||` in the standard form, so the option alone takes it
    ("InstrumentRegions", ("-fprofile-instr-generate",), "", ()),
    ("isInstrumentedCondition", ("-fprofile-instr-generate",), "", ()),
    # CGExprScalar.cpp 5533, 5655, 5675, 5698, VisitAbstractConditionalOperator:
    # `if (llvm::EnableSingleByteCoverage)`, an llvm option clang's CodeGen
    # declares (CoverageMappingGen.cpp 35), so -mllvm hands it on
    ("EnableSingleByteCoverage", ("-mllvm -enable-single-byte-coverage",), "", ()),
    # Options.td 1741, CodeGenOpts' DebugInfoForProfiling, read beside the
    # debug information our -g gives
    ("DebugInfoForProfiling", ("-fdebug-info-for-profiling",), "", ()),
    # CGBuiltin.cpp 2826, 3050, 3063, 3765, 3797: Builder.getIsFPConstrained()
    ("getIsFPConstrained", ("-ffp-exception-behavior=strict",), "", ()),
    ("IsFPConstrained", ("-ffp-exception-behavior=strict",), "", ()),
    # SemaChecking.cpp 5256, 5298, 5304: FPO.getNoHonorInfs(), FPO.getNoHonorNaNs()
    ("getNoHonorInfs", ("-ffast-math",), "", ()),
    ("getNoHonorNaNs", ("-ffast-math",), "", ()),
    ("NoHonorInfs", ("-ffast-math",), "", ()),
    ("NoHonorNaNs", ("-ffast-math",), "", ()),
    ("tryUseTestFPKind", ("-ffp-exception-behavior=strict",), "", ()),
]
# The sanitizers: every SanitizerKind the condition names is traced under
# -fsanitize=<kind>, and under -fsanitize-trap=<kind> beside it; the names
# are read from clang's Sanitizers.def. A condition reading SanOpts with no
# kind named is traced under the undefined-behaviour group.
SANITIZERS_FILE = "/persist/traced_clang_src/clang/include/clang/Basic/Sanitizers.def"
SANITIZER_LINE = re.compile(r"^SANITIZER(?:_GROUP)?\(\"([^\"]+)\",\s*(\w+)")
SANITIZER_KIND = re.compile(r"SanitizerKind::(?:SO_)?(\w+)")
SANITIZERS_UNNAMED = "undefined"
# The other languages: "not needed" (the owner, 2026-10-20).
LANGUAGE_NAMES = [
    ("CPlusPlus", "not GNU C: C++"),
    ("isReferenceType", "not GNU C: C++"),
    ("isMemberPointerType", "not GNU C: C++"),
    ("MemberPointerType", "not GNU C: C++"),
    ("inTemplateInstantiation", "not GNU C: C++"),
    ("IsResultDependent", "not GNU C: C++"),
    ("containsUnexpandedParameterPack", "not GNU C: C++"),
    ("isDependentType", "not GNU C: C++"),
    ("CXXRecordDecl", "not GNU C: C++"),
    ("CXXDestructorDecl", "not GNU C: C++"),
    ("CXXConstructorDecl", "not GNU C: C++"),
    ("CXXThisExpr", "not GNU C: C++"),
    ("IsBaseCXXThis", "not GNU C: C++"),
    ("IsDerivedFrom", "not GNU C: C++"),
    ("getCXXOverloadedOperator", "not GNU C: C++"),
    ("wasNotFoundInCurrentInstantiation", "not GNU C: C++"),
    ("isOverloadedResult", "not GNU C: C++"),
    ("isUnresolvableResult", "not GNU C: C++"),
    ("isNonOverloadPlaceholderType", "not GNU C: C++"),
    ("ParenListExpr", "not GNU C: C++"),
    ("ElideConstructors", "not GNU C: C++"),
    ("NRVOCandidate", "not GNU C: C++"),
    ("NonTriviallyCopyableCXXRecord", "not GNU C: C++"),
    ("isNonTrivialToPrimitive", "not GNU C: C++ / ObjC ARC"),
    ("hasNonTrivialToPrimitiveDestructiveMove", "not GNU C: C++ / ObjC ARC"),
    ("hasNonTrivialToPrimitiveDefaultInitialize", "not GNU C: C++ / ObjC ARC"),
    ("hasNonTrivialToPrimitiveCopy", "not GNU C: C++ / ObjC ARC"),
    ("getAsCXXRecordDecl", "not GNU C: C++"),
    ("getConditionVariable", "not GNU C: C++ condition variable declaration"),
    ("ExprWithCleanups", "not GNU C: C++ / ObjC ARC / Blocks cleanups"),
    ("ObjC", "not GNU C: Objective-C"),
    ("ObjCObjectPointerType", "not GNU C: Objective-C"),
    ("BlockExpr", "not GNU C: Blocks extension"),
    ("isBlockPointerType", "not GNU C: Blocks extension"),
    ("OpenMP", "not GNU C: OpenMP"),
    ("OpenACC", "not GNU C: OpenACC"),
    ("isInOpenACCComputeConstructScope", "not GNU C: OpenACC"),
    ("OpenACCUpdateConstruct", "not GNU C: OpenACC"),
    ("ArraySection", "not GNU C: OpenMP/OpenACC array section"),
    ("OpenCL", "not GNU C: OpenCL"),
    ("CUDA", "not GNU C: CUDA"),
    ("HIP", "not GNU C: HIP"),
    ("SYCL", "not GNU C: SYCL"),
    ("HLSL", "not GNU C: HLSL"),
    ("Consteval", "not GNU C: C++"),
    ("IfStatementKind::Constexpr", "not GNU C: C++"),
    ("TypeRequiresBuiltinLaunder", "not GNU C: C++"),
    ("compositeType", "not GNU C: Objective-C"),
    ("S.getInit()", "not GNU C: C++17 switch initializer statement"),
    ("ConditionScope.requiresCleanups()", "not GNU C: C++ condition variable destructor cleanups"),
    ("ForScope.requiresCleanups()", "not GNU C: C++ for-scope destructor cleanups"),
    ("requiresCleanups", "not GNU C: C++ destructor cleanups"),
    ("ExitBlock != LoopExit.getBlock()", "not GNU C: ExitBlock only differs from LoopExit when C++ condition scope requires cleanups"),
    ("EHStack.hasNormalCleanups()", "not GNU C: lexical scope cleanups in standard form"),
    ("tryToConvertMemberExprToDeclRefExpr", "not GNU C: C++ static data member or enum constant member"),
    ("tryEmitAsConstant", "not GNU C: C++ constexpr or static constant member"),
    ("OffsetOfNode::Base", "not GNU C: C++ base class in offsetof"),
    ("MSPropertyDecl", "not GNU C: Microsoft __declspec(property)"),
]
INSTRUMENTATION = "instrumentation (profiling, coverage): like debug-specific lowering, not needed"
# the owner, 2026-10-20: a feature not on all three architectures ("i only care
# about the paths that are supported on all three architectures") and an
# optimization done later ("optimizations are done later") are "not needed".
# the owner, 2026-10-20, 23:30 UTC, on a ruling widened past its instance ("if i
# inform you of an incorrect label ... it makes the page's completeness
# incomplete"): only what the ruling named is closed by name; a test that
# reads the target in general stays open until traced with each of the three
# targets (riscv64, x86-64, aarch64), the method's own way to settle it.
NOT_NEEDED_NAMES = [
    ("PointerAuth", "not on all three architectures: pointer authentication"),
    ("isSveVLSBuiltinType", "not on all three architectures: ARM SVE"),
    ("isSVESizelessBuiltinType", "not on all three architectures: ARM SVE"),
    ("areCompatibleSveTypes", "not on all three architectures: ARM SVE"),
    ("areLaxCompatibleSveTypes", "not on all three architectures: ARM SVE"),
    ("isRVVVLSBuiltinType", "not on all three architectures: RISC-V V"),
    ("isRVVSizelessBuiltinType", "not on all three architectures: RISC-V V"),
    ("areCompatibleRVVTypes", "not on all three architectures: RISC-V V"),
    ("areLaxCompatibleRVVTypes", "not on all three architectures: RISC-V V"),
    ("ScalableVectorType", "not on all three architectures: scalable vector type"),
    ("SrcTypeSize.isScalable", "not on all three architectures: scalable vector type"),
    ("hasBPFPreserveStaticOffset", "not on all three architectures: BPF"),
    ("wrapWithBPFPreserveStaticOffset", "not on all three architectures: BPF"),
    ("BPFPreserveAccessIndexAttr", "not on all three architectures: BPF"),
    ("isPPC", "not on all three architectures: PowerPC"),
    ("isOSAIX", "not on all three architectures: AIX"),
    ("anyAltivecTypes", "not on all three architectures: PowerPC AltiVec"),
    ("AltiVecVector", "not on all three architectures: PowerPC AltiVec"),
    ("unsupportedTypeConversion", "not on all three architectures: PowerPC __ibm128"),
    ("isCmseNSCall", "not on all three architectures: ARMv8-M CMSE"),
    ("EmitCMSEClearRecord", "not on all three architectures: ARMv8-M CMSE"),
    ("isWindowsArm64EC", "not on all three architectures: Windows Arm64EC"),
    ("X86_VectorCall", "not on all three architectures: x86 vectorcall"),
    ("isSEHTryScope", "not on all three architectures: Windows SEH"),
    ("currentFunctionUsesSEHTry", "not on all three architectures: Windows SEH"),
    ("IsOutlinedSEHHelper", "not on all three architectures: Windows SEH"),
    ("EHAsynch", "not on all three architectures: Windows MSVC async EH"),
    ("isMSVCXXPersonality", "not on all three architectures: MSVC C++ personality"),
    ("CC_SwiftAsync", "not GNU C: Swift async calling convention"),
    ("tryEmitFMulAdd", "an optimization done later: the fused multiply-add"),
    # the owner, 2026-10-21, 05:50 UTC, on instrumentation being "not needed,
    # unless a run takes it": "sure." The option of OPTION_NAMES is traced
    # first; this closing is the outcome when it does not take the branch (the
    # pattern PointerAuth has). CGExprScalar.cpp 5225, 5247, 5312 (VisitBinLAnd),
    # 5533, 5655, 5675, 5698 (VisitAbstractConditionalOperator), 2039 (VisitMemberExpr).
    ("hasProfileClangInstr", INSTRUMENTATION),
    ("InstrumentRegions", INSTRUMENTATION),
    ("isInstrumentedCondition", INSTRUMENTATION),
    ("EnableSingleByteCoverage", INSTRUMENTATION),
    ("DebugInfoForProfiling", INSTRUMENTATION),
    ("ShouldXRayInstrumentFunction", INSTRUMENTATION),
    ("haveRegionCounts", INSTRUMENTATION),
    ("SwitchWeights", INSTRUMENTATION),
    ("ConvertHalfVec", "not on all three architectures: ARM NEON half-vector intrinsic"),
    ("ZVector", "not on all three architectures: SystemZ vector"),
    ("AltiVecBool", "not on all three architectures: PowerPC AltiVec"),
    ("isWebAssemblyTableType", "not on all three architectures: WebAssembly"),
    ("isSizelessVectorType", "not on all three architectures: sizeless vector type"),
    ("MicrosoftExt", "not GNU C: Microsoft extension"),
    ("isMicrosoftABI", "not on all three architectures: Microsoft ABI"),
    ("MSVaListType", "not on all three architectures: Microsoft ABI"),
    ("IsMSPropertySubscript", "not GNU C: Microsoft property subscript"),
    ("shouldEmitConvergenceTokens", "not GNU C: convergence tokens (SPIR-V/HLSL/CUDA)"),
    ("tryUseTestFPKind", "not on all three architectures: target hook testFPKind"),
    ("AAS != EAS", "not on all three architectures: non-default alloca address space"),
    ("ArgValue.isValid()", "not on all three architectures: x86-64, aarch64, and riscv64 all implement aggregate and complex va_arg"),
    ("AtomicUsesUnsupportedLibcall", "not on all three architectures: taken on none of riscv64, x86-64, aarch64"),
    ("delete DefaultBlock", "clang's own guard: DefaultBlock is non-null from createBasicBlock"),
    ("!ArgTInfo", "clang's own guard: GetTypeFromParser always populates ArgTInfo"),
]
# What no program of the standard form has: "cannot reach".
CANNOT_REACH_NAMES = [
    ("OptimizationLevel", "the optimizer stays off: -O0 -g is fixed for lowerings"),
    ("SwitchLikelihood", "the optimizer stays off: SwitchLikelihood is only populated when OptimizationLevel > 0"),
    ("isMayAlias()", "the optimizer stays off: TBAA info is only populated when OptimizationLevel > 0"),
    ("getDebugInfo", "clang's own bookkeeping: nothing in the program decides it"),
    ("EmitStopPoint", "clang's own bookkeeping: nothing in the program decides it"),
    ("requiresReturnValueCheck", "the standard form's op_k has no returns_nonnull or _Nonnull return attribute"),
    ("isVariableArrayType", "the standard form's struct P_k cannot hold a variable-length array"),
    ("getAsVariableArrayType", "the standard form's struct P_k cannot hold a variable-length array"),
    ("isVariablyModifiedType", "the standard form's struct P_k cannot hold a variable-length array"),
    ("checkArgCount(", "entry_info: the call is written with the arity in entry_info"),
    ("IsInPreservedAIRegion", "entry_info: single-HiOp __builtin_preserve_access_index is not nested inside another"),
    ("std::get<0>(LHC)", "entry_info: standard-form IfStmt branches carry no likelihood attributes"),
    ("getLikelihoodAttr", "entry_info: standard-form statement bodies carry no likelihood attributes"),
    ("warn_comma_operator", "entry_info: standard-form loop condition is not a comma operator"),
    ("isa<NullStmt>(Body)", "entry_info: standard-form loop body is an inert call, not a NullStmt"),
    ("BreakContinueStack.empty()", "entry_info: single-HiOp SwitchStmt is not nested inside an outer loop or switch"),
    ("SwitchInsn", "entry_info: in standard form, CaseStmt and DefaultStmt sit inside a non-constant switch"),
    ("isReservedInAllContexts", "entry_info: the standard form names its label m, not a reserved identifier"),
]


# the owner, 2026-10-20 23:30 UTC: a ruling closes only its instance; the rest is
# settled by a run. A test that reads the target is traced on the other two
# of the three architectures ("i only care about the paths that are
# supported on all three architectures"); riscv64, our setup, is the third,
# and its contexts are the base.
TARGET_NAMES = ("PointerAuth", "getTarget()", "getTargetInfo()", "getTriple()", "Target.", "isTargetAddressSpace",
                "getTargetAddressSpace", "hasFeature(", "getCPU", "getABI", "tryUseTestFPKind")
BASE_TARGET = ("riscv64", "riscv64-unknown-linux-gnu")
OTHER_TARGETS = [("x86-64", "x86_64-unknown-linux-gnu"), ("aarch64", "aarch64-unknown-linux-gnu")]
TARGET_OPTION = re.compile(r"--target=(\S+)")


def closing_names() -> list:
    """(name, outcome, badge) of every name that closes a branch, in the order read."""
    names = []
    for name, why in LANGUAGE_NAMES:
        names.append((name, "not needed", why))
    for name, why in NOT_NEEDED_NAMES:
        names.append((name, "not needed", why))
    for name, why in CANNOT_REACH_NAMES:
        names.append((name, "cannot reach", why))
    return names


CLOSING_NAMES = closing_names()
# the owner, 2026-10-21, 01:20 UTC, on the lines of the eight functions that only a
# C++ throw expression reaches (an arm of a conditional giving a null value):
# "if its outside of GNU-C, then yes 'not needed: outside GNU C'". A ruled
# branch is one function and the text of its test; the ruling closes that
# instance only (the owner, 2026-10-20, 23:30 UTC).
RULED_SIDES = [
    ("ScalarExprEmitter::VisitAbstractConditionalOperator", "if (!Result && !E->getType()->isVoidType())",
     "not needed", "not GNU C: only a C++ throw expression gives a null value here"),
    ("ScalarExprEmitter::VisitAbstractConditionalOperator", "if (!LHS)",
     "not needed", "not GNU C: only a C++ throw expression gives a null value here"),
    ("ScalarExprEmitter::VisitAbstractConditionalOperator", "if (!RHS)",
     "not needed", "not GNU C: only a C++ throw expression gives a null value here"),
    # the owner, 2026-10-21, 01:20 UTC ("if its outside of GNU-C, then yes 'not needed:
    # outside GNU C'"): the AST argument order is used only when clang rebuilds
    # an atomic expression in C++ template instantiation; every atomic
    # operator's compile took the other arm (log 489 §26).
    ("Sema::BuildAtomicExpr", "if (ArgOrder == Sema::AtomicArgumentOrder::AST)",
     "not needed", "not GNU C: the AST argument order is used only by C++ template instantiation"),
    # the owner, 2026-10-22: Sema::CheckConditionalOperands refuses a GNU vector
    # ('v4si') as the condition in C (SemaExpr.cpp:8053; ext_vector_type takes
    # the earlier branch at 5554), so only C++ CXXCheckConditionalOperands
    # reaches 5594.
    ("ScalarExprEmitter::VisitAbstractConditionalOperator",
     "if (condExpr->getType()->isVectorType() || condExpr->getType()->isSveVLSBuiltinType())",
     "not needed", "not GNU C: clang refuses a GNU vector ('v4si') as the condition in C; only C++ reaches it"),
    ("Sema::BuildMemberExpr",
     "if (auto *FPT = Ty->getAs<FunctionProtoType>())",
     "not needed", "not GNU C: a struct or union member cannot have function type in C; only C++ member functions reach it"),
    ("CodeGenFunction::EmitCaseStmtRange",
     "if (Rem)",
     "not needed", INSTRUMENTATION),
    ("Sema::PerformObjectMemberConversion",
     "if (!RD)",
     "not needed", "not GNU C: PerformObjectMemberConversion is a C++ object-member conversion helper"),
]


def ruled_kinds(function: str, text: str) -> list:
    """("closing", test text) for every ruled branch of this function whose test the text holds."""
    kinds = []
    for ruled_function, test, outcome, why in RULED_SIDES:
        if ruled_function == function and test in text:
            kinds.append(("closing", test))
    return kinds


def closing_named(name: str):
    """(outcome, badge) of a closing name: the tables' names first, then the ruled branches."""
    for closing_name, outcome, why in CLOSING_NAMES:
        if closing_name == name:
            found = (outcome, why)
            return found
    for ruled_function, test, outcome, why in RULED_SIDES:
        if test == name:
            found = (outcome, why)
            return found
    return None
# Any other language or code generation option: traced when OPTION_NAMES
# names its flag; otherwise open, the option named from the text.
GENERIC_OPTIONS = ("getLangOpts()", "LangOpts.", "getCodeGenOpts()", "CodeGenOpts.")
OPTION_MEMBER = re.compile(r"(?:getLangOpts\(\)|LangOpts|getCodeGenOpts\(\)|CodeGenOpts)\s*\.\s*(\w+)")

# §4.2: the names that read a constant part, a width, or the part's shape.
CONSTANT_NAMES = ("ConstantFoldsToSimpleInteger", "EvaluateAsInt", "isIntegerConstantExpr", "isCXX11ConstantExpr",
                  "EvaluateKnownConstInt", "isValueDependent", "isa<llvm::ConstantInt>",
                  "dyn_cast<llvm::ConstantInt>", "ConstantInt", "getConstantTarget", "EmitBoolCondBranch")
WIDTH_NAMES = ("isBitField", "getBitWidth", "BitFieldInfo")
SHAPE_NAMES = [
    ("isCheapEnoughToEvaluateUnconditionally", "literal"),
    ("IgnoreParens", "parenthesis"),
    ("getOpcode()", "literal"),
    ("isGLValue()", "place"),
    # 2026-10-21: the kinds of place clang loads a part from (PLACE_FORMS).
    # CGExpr.cpp 2350, EmitLoadOfBitfieldLValue: `if (Info.IsSigned)`
    ("Info.IsSigned", "signed bit-field"),
    # CGExpr.cpp 2301, EmitLoadOfLValue: `if (LV.isVectorElt())`
    ("isVectorElt", "vector element"),
    # CGExpr.cpp 2310, EmitLoadOfLValue: `if (LV.isExtVectorElt())`
    ("isExtVectorElt", "ext vector element"),
    ("isa<ExtVectorElementExpr>", "ext vector element"),
    ("ExtVectorElementExpr", "ext vector element"),
    # CGExpr.cpp 2315, EmitLoadOfLValue: `if (LV.isGlobalReg())`
    ("isGlobalReg", "global register"),
    # CGExpr.cpp 2318, EmitLoadOfLValue: `if (LV.isMatrixElt())`
    ("isMatrixElt", "matrix element"),
]
# 2026-10-21, how program_of writes a part as each kind of place above: the
# part's holder, the field P_k holds it in ("" for none) and how op_k reads
# it. The standard form writes a part only as a field (`p->a`), so these are
# written into the program, as a bit-field's width is.
PLACE_FORMS = {
    # a bit-field of a signed holder: clang's Info.IsSigned (the records' bit-fields were unsigned)
    "signed bit-field": ("signed int", "{holder} {name} : " + str(WIDTH) + ";", "p->{name}"),
    # a subscripted GNU vector: an LValue of kind VectorElt
    "vector element": ("v4si", "{holder} {name};", "p->{name}[1]"),
    # an element of clang's ext vector, by its name: an LValue of kind
    # ExtVectorElt (clang's own extension, not GCC's C: the label is the owner's)
    "ext vector element": ("ev4si", "{holder} {name};", "p->{name}.x"),
    # an element of a matrix (-fenable-matrix): an LValue of kind MatrixElt
    "matrix element": ("m2", "{holder} {name};", "p->{name}[0][1]"),
    # a global register variable, declared at file scope: an LValue of kind GlobalReg
    "global register": ("long", "", "reg_" + KEY + "_{name}"),
}
# What a place form declares before P_k, and the option it needs ("" for none).
PLACE_DECLARATIONS = {
    "matrix element": (MATRIX_TYPES, "-fenable-matrix"),
    "global register": (("register {holder} reg_" + KEY + "_{name} __asm__(\"{register}\");",), ""),
}
# The register a global register variable names on each of the three
# architectures: the stack pointer, which none of them allocates (clang's
# backends refuse an allocatable one, "Invalid register name global variable").
GLOBAL_REGISTERS = {"riscv64": "sp", "x86-64": "rsp", "aarch64": "sp"}

# §4.3, the table from a holder property to the holder that makes it true
# and the one that makes it false, checked against clang's Type.h; the llvm
# type's own spellings, which CodeGen's tests read (`isPointerTy`,
# `isFPOrFPVectorTy`), after them.
CHANGE_FOR = [
    ("isVoidPointerType", "void *", "int *"),
    ("isVoidType", "void *", "int *"),
    ("isFunctionPointerType", "fnptr", "int *"),
    ("isFunctionType", "fntype", "int"),
    ("isFunctionProtoType", "fntype", "int"),
    ("isObjectType", "int", "fntype"),
    ("isAnyPointerType", "int *", "int"),
    ("isPointerType", "int *", "int"),
    ("isArrayType", "arr4", "int"),
    ("isRealFloatingType", "double", "int"),
    ("isFloatingType", "double", "int"),
    ("isHalfType", "__fp16", "double"),
    ("isFloat16Type", "_Float16", "double"),
    ("isBFloat16Type", "__bf16", "double"),
    ("isComplexIntegerType", "_Complex int", "double _Complex"),
    ("isAnyComplexType", "double _Complex", "double"),
    ("isComplexType", "double _Complex", "double"),
    ("isExtVectorType", "ev4si", "v4si"),
    ("isExtVectorBoolType", "ev4b", "ev4si"),
    ("isSubscriptableVectorType", "v4si", "int *"),
    ("isVectorType", "v4si", "int"),
    ("isBooleanType", "_Bool", "int"),
    ("isEnumeralType", "enum E", "int"),
    ("isUnionType", "union U", "struct S"),
    ("isRecordType", "struct S", "int"),
    ("isStructureType", "struct S", "int"),
    ("isAtomicType", "_Atomic int", "int"),
    ("isBitIntType", "_BitInt(37)", "int"),
    ("hasUnsignedIntegerRepresentation", "unsigned int", "int"),
    ("isUnsignedIntegerType", "unsigned int", "int"),
    ("isUnsignedIntegerType", "v4ui", "v4si"),
    ("isSignedIntegerOrEnumerationType", "int", "unsigned int"),
    ("InputSigned", "v4si", "v4ui"),
    ("isPromotableIntegerType", "short", "int"),
    ("isSpecificBuiltinType", "float", "double"),
    ("PromotionType.isNull", "double", "_Float16"),
    ("promotionTy.isNull", "double _Complex", "cf16"),
    ("PromoteType.isNull", "int", "short"),
    ("elementSize.isOne", "char *", "int *"),
    ("isWideCharType", "wchar_t", "char"),
    ("isCharType", "char", "int"),
    ("isInt128", "__int128", "long"),
    ("isConstQualified", "const int", "int"),
    ("isVolatileQualified", "volatile int", "int"),
    ("hasQualifiers", "const int", "int"),
    ("isIncompleteType", "struct I *", "struct S"),
    ("isIncompleteType", "struct I", "struct S"),
    ("isIntegralOrEnumerationType", "int", "double"),
    ("isIntegerType", "int", "double"),
    ("hasIntegerRepresentation", "int", "double"),
    ("isArithmeticType", "int", "int *"),
    ("isScalarType", "int", "struct S"),
    ("isRealType", "double", "double _Complex"),
    ("isFPOrFPVectorTy", "double", "int"),
    ("isFloatingPointTy", "double", "int"),
    ("isPointerTy", "int *", "int"),
    ("isVectorTy", "v4si", "int"),
    ("isIntegerTy", "int", "double"),
    # 2026-10-21. CGExprScalar.cpp 5579, VisitAbstractConditionalOperator,
    # inside the ext vector condition's block (5554): `if
    # (rhsVTy->getElementType()->isFloatingPointTy())`, the arms' element: a
    # float ext vector in both arms (PART_NAMES: rhsVTy); the condition stays
    # an int ext vector, which clang requires of a vector condition
    ("isFloatingPointTy", "ev4sf", "ev4si"),
    # 2026-10-21. CGExprScalar.cpp 5588: `if (wasCast)`, set at 5582 exactly
    # when 5579's test holds: the same holders
    ("wasCast", "ev4sf", "ev4si"),
    # 2026-10-21. CGExprScalar.cpp 4461, EmitAdd under -ftrapv: `if
    # (CanElideOverflowCheck(CGF.getContext(), op))`, true when both parts
    # are narrower than the int they are promoted to (CGExprScalar.cpp 232 to
    # 246): both parts short (PART_NAMES: every part at once)
    ("CanElideOverflowCheck", "short", "int"),
    ("HasSideEffects", "volatile int", "int"),
    ("NoDeref", "noderef_int_ptr", "int *"),
    ("NoDeref", "noderef_struct_ptr", "struct S *"),
    ("FieldDecl", "struct S", "struct S_anon"),
    ("IndirectFieldDecl", "struct S_anon", "struct S"),
    ("IndirectMemberDecl", "struct S_anon", "struct S"),
]
# A holder of the table that the pool lacks, with what declares it (§4.3:
# "wchar_t, add to the pool if absent").
HOLDER_PREAMBLE = {
    "wchar_t": ("#include <stddef.h>",),
    # 2026-10-21, for CGExprScalar.cpp 5579 and 5588: a float ext vector,
    # named as the standard form names its int one (ev4si) and its float GNU
    # vector (v4sf)
    "ev4sf": ("typedef float ev4sf __attribute__((ext_vector_type(4)));",),
    "v4ui": ("typedef unsigned int v4ui __attribute__((vector_size(16)));",),
    "ev4b": ("typedef _Bool ev4b __attribute__((ext_vector_type(4)));",),
    "v4df": ("typedef double v4df __attribute__((vector_size(32)));",),
    "cf16": ("typedef _Complex _Float16 cf16;",),
    "_Complex _Float16": (),
    "char *": (),
    "fntype": (),
    "struct I": (),
    "void": (),
    "const v4si": (),
    "volatile int": (),
    "noderef_int_ptr": ("typedef int __attribute__((noderef)) *noderef_int_ptr;",),
    "noderef_struct_ptr": ("typedef struct S __attribute__((noderef)) *noderef_struct_ptr;",),
    "struct S_anon": ("struct S_anon { struct { int m; }; };",),
    "struct S_anon *": ("struct S_anon { struct { int m; }; };",),
    "va_list": ("#include <stdarg.h>",),
}

# §4.3, which part a test reads: a name in the test's text and the part it
# names, an index or every part at once (the result's type follows them all).
PART_NAMES = [
    ("getLHS", 0), ("LHS", 0), ("getRHS", 1), ("RHS", 1),
    ("condExpr", 0), ("getCond", 0), ("lhsExpr", 1), ("getTrueExpr", 1), ("rhsExpr", 2), ("getFalseExpr", 2),
    ("getSubExpr", 0), ("getSrcExpr", 0),
    ("op.Ty", "every"), ("ResultTy", "every"), ("E->getType()", "every"), ("elementSize", "every"),
    ("elementType", "every"),
    # 2026-10-21. CGExprScalar.cpp 4461: CanElideOverflowCheck reads both
    # parts' unpromoted types (CGExprScalar.cpp 232 to 238)
    ("CanElideOverflowCheck", "every"),
    # 2026-10-21. CGExprScalar.cpp 5578 and 5579: rhsVTy is the false arm's
    # type after the arms are made one type, so both arms (parts 1 and 2) at
    # once; 5588's wasCast follows it
    ("rhsVTy", (1, 2)), ("wasCast", (1, 2)),
    # 2026-10-25: in-HiOp derived_info local variable names derived from entry_info
    ("Op", 0), ("Input", 0), ("Arg", 0), ("Base", 0), ("BaseExpr", 0), ("First", 0), ("Second", 1),
    ("Cond", 0), ("ControllingExpr", 0), ("Order", 0), ("ord", 0), ("Ord", 0), ("Scp", 1),
    ("V", 0), ("SrcTy", 0), ("SrcType", 0), ("SrcEltType", 0), ("SrcEltTy", 0), ("InputSigned", 0),
    ("DstTy", 1), ("DstType", 1), ("DstEltType", 1), ("DstEltTy", 1), ("OutputSigned", 1),
    ("VaListType", 0), ("OrigExpr", 0), ("TInfo", 1), ("UnderlyingType", 1), ("PromoteType", 1),
    ("ValType", 0), ("AtomTy", 0), ("IndexExpr", 1),
]
ARGUMENT = re.compile(r"getArg\((\d+)\)")

STATE = {"said": 0.0, "counts_of_name": None, "operators": None, "writer": None, "in_hiop": False,
         "in_hiop_spans": None}


# ---------------------------------------------------------------------------
# Block A: the loop, one operator at a time

def enumerate_every_path(operator, record, lines: dict, binary: dict, pool: set, rounds: int):
    """Block A. The plan's `while True`, bounded by `rounds` (--rounds)."""
    key = key_for(operator)
    contexts = record.contexts(key, lines)
    for round_number in range(record.rounds_done(key) + 1, rounds + 1):
        branches = unreached_branches(operator, lines, binary)
        branches = still_open(branches, record)
        check.say(f"[{key}] round {round_number}: {len(branches)} branches open")
        if not branches:
            break
        candidates = []
        tried = []
        for branch in branches:
            condition = condition_of(branch)
            change = change_for(condition, pool)
            if change["closed"] and change["outcome"] != "open":
                record.close(key, branch, condition, change, round_number)
                continue
            written, change = candidates_for(operator, branch, change, contexts, pool)
            if change["closed"]:
                record.close(key, branch, condition, change, round_number)
                continue
            tried.append((branch, condition, change, written))
            candidates = with_new(candidates, written, contexts)
        record.write()
        if not candidates:
            record.add(key, tried, None, lines, round_number)
            break
        results = trace_and_check(key, candidates, binary, record.results_of(key, binary),
                                  record.paths_written(key))
        record.add(key, tried, results, lines, round_number)
        contexts = contexts + candidates
        record.write()
    else:
        # the rounds' bound reached (or 0 rounds: run A, the branches only): the
        # branches left are listed too, so the record holds every branch; each is
        # closed when its condition closes it, else open, not tried
        branches = still_open(unreached_branches(operator, lines, binary), record)
        for branch in branches:
            condition = condition_of(branch)
            change = change_for(condition, pool)
            if not change["closed"] and change["closing"] is not None:
                change["closed"] = True
                change["outcome"] = change["closing"][0]
                change["why"] = change["closing"][1]
            if not change["closed"]:
                change = not_tried(rounds)
            record.close(key, branch, condition, change, rounds + 1)
    record.finish(key)
    record.write()
    return record


def candidates_for(operator, branch: dict, change: dict, contexts: list, pool: set) -> tuple:
    """(the candidates, the change as the record shows it). PCHQ log 503
    §2, Table 1: the branch's function's tree (branch_trees, run tlp1_l13)
    unlocks it (branch_trees.unlock_branch): the chain of ways from the
    function's entry to the branch, each way's unlocking set intersected in
    turn, each state left written once. The tables' change (write_candidate)
    when the function has no tree or no context ran the branch's test. A
    branch the tree gives no candidate is closed open, with the reason (the
    page reads it as not reached: the condition is not read yet)."""
    base = change["base"]
    special = operator_candidates(operator, branch, base)
    tree = None
    if base is not None:
        tree = branch_trees.tree_of_branch(branch)
    if tree is None:
        if change["closed"]:
            found = ([], change)
            return found
        written = with_new(special, write_candidate(operator, contexts, change), special)
        if not written and change["closing"] is not None:
            closed = dict(change)
            closed["closed"] = True
            closed["outcome"] = change["closing"][0]
            closed["why"] = change["closing"][1]
            return ([], closed)
        found = (written, change)
        return found
    writer = branch_writer(pool)
    written = branch_trees.unlock_branch(branch, base, tree, writer)
    if special:
        written = with_new(list(special), written, list(special))
    if not change["closed"]:
        fallback = write_candidate(operator, contexts, change)
        if fallback:
            written = with_new(written, fallback, written)
    chain = branch_trees.BranchTree.super_chain_of_branch(tree, branch["test"], branch["first"])
    unlocked = dict(change)
    unlocked["closed"] = False
    unlocked["outcome"] = ""
    unlocked["why"] = ""
    unlocked["alternatives"] = [{"kind": "unlocked", "function": tree.function_name,
                                 "chain": branch_trees.chain_shown(chain), "candidates": len(written)}]
    if not written:
        unlocked["closed"] = True
        if unlocked["closing"] is not None:
            unlocked["outcome"] = unlocked["closing"][0]
            unlocked["why"] = unlocked["closing"][1]
        else:
            unlocked["outcome"] = "open"
            unlocked["why"] = "no candidate from the branch tree: " + branch_trees.why_none(branch, base, tree, writer)
    found = (written, unlocked)
    return found


def operator_candidates(operator, branch: dict, base) -> list:
    """Targeted candidates for specific in-HiOp branches whose unlocking requires
    compound AST shapes or multi-part setups."""
    if base is None:
        return []
    key = branch["key"]
    pair = (branch["test"], branch["first"])
    cmd = base.setup.command
    pre = list(base.setup.preamble)
    found = []
    if key == "ArraySubscriptExpr" and pair == (5335, 5336):
        found.append(Context(operator, ("int *", "char"), base.setup,
                             "struct P_k { int * a; char b; int result; };\n"
                             "void op_k(struct P_k *p) { p->result = (p->a[(char)0]); }"))
        found.append(Context(operator, ("int *", "char"), base.setup,
                             "struct P_k { int * a; char b; int result; };\n"
                             "void op_k(struct P_k *p) { p->result = (p->a[(char)-1]); }"))
    elif key == "BinaryOperator.Shl" and pair[0] >= 4768:
        for holders, flags in (
            (("int", "int"), "-fsanitize=shift-base"),
            (("long long", "int"), "-fsanitize=shift-base -fsanitize=shift-exponent"),
            (("unsigned int", "int"), "-fsanitize=unsigned-shift-base"),
            (("int", "int"), "-fsanitize=shift-exponent"),
        ):
            found.append(Context(operator, holders, Setup(cmd + " " + flags, tuple(pre))))
    elif key == "CallExpr.BI__builtin_counted_by_ref":
        found.append(Context(operator, ("int *",), base.setup,
                             "struct P_k { int count; int a[] __attribute__((counted_by(count))); };\n"
                             "void op_k(struct P_k *p) { (void)(__builtin_counted_by_ref(p->a)); }"))
    elif key == "CallExpr.BI__scoped_atomic_thread_fence":
        for a_expr, b_expr in (
            ("0", "99"), ("2", "2"), ("3", "2"), ("4", "2"), ("5", "2"),
            ("0", "p->b"), ("2", "p->b"), ("3", "p->b"), ("4", "p->b"), ("5", "p->b"),
            ("p->a", "2"), ("p->a", "99"),
        ):
            found.append(Context(operator, ("int", "int"), base.setup,
                                 "struct P_k { int a; int b; };\n"
                                 f"void op_k(struct P_k *p) {{ (void)(__scoped_atomic_thread_fence({a_expr}, {b_expr})); }}"))
    elif key == "CaseStmt (2 parts)" and pair[0] in (1877, 1878, 1879):
        enum_pre = tuple(pre + ([] if "enum E_case { E0 = 0 };" in pre else ["enum E_case { E0 = 0 };"]))
        for extra in ("", " -g", " -gline-tables-only"):
            found.append(Context(operator, ("int", "void"),
                                 Setup(cmd + extra if extra else cmd, enum_pre),
                                 "enum E_case { E0 = 0 };\nvoid part_k_b(void);\n"
                                 "struct P_k { int a; };\n"
                                 "void op_k(struct P_k *p) { switch (p->a) { case E0: part_k_b(); } }"))
    elif key == "CaseStmt (3 parts)":
        for holder, r_lo, r_hi in (
            ("int", "1", "0"),
            ("int", "0", "100"),
            ("unsigned int", "1U", "0U"),
            ("unsigned int", "0U", "1U"),
        ):
            found.append(Context(operator, ("int", "int", "void"), base.setup,
                                 "void part_k_c(void);\n"
                                 f"struct P_k {{ {holder} a; }};\n"
                                 f"void op_k(struct P_k *p) {{ switch (p->a) {{ case {r_lo} ... {r_hi}: part_k_c(); }} }}"))
    elif key == "ConditionalOperator" and pair[0] in (8615, 8617, 8619, 8636):
        found.append(Context(operator, ("int", "void", "void"), base.setup,
                             "int part_k_a(void);\nvoid part_k_b(void);\nvoid part_k_c(void);\n"
                             "struct P_k { char unused_; };\n"
                             "void op_k(struct P_k *p) { (void)(part_k_a() ? part_k_b() : part_k_c()); }"))
        found.append(Context(operator, ("int", "int", "void"), base.setup,
                             "void part_k_c(void);\n"
                             "struct P_k { int a; int b; };\n"
                             "void op_k(struct P_k *p) { (void)(p->a ? p->b : part_k_c()); }"))
        found.append(Context(operator, ("int", "void", "int"), base.setup,
                             "void part_k_b(void);\n"
                             "struct P_k { int a; int c; };\n"
                             "void op_k(struct P_k *p) { (void)(p->a ? part_k_b() : p->c); }"))
        np_pre = tuple(pre + ([] if "typedef __typeof__(nullptr) nullptr_t;" in pre else ["typedef __typeof__(nullptr) nullptr_t;"]))
        np_setup = Setup(cmd + " -std=gnu2x", np_pre)
        found.append(Context(operator, ("int", "nullptr_t", "nullptr_t"), np_setup,
                             "typedef __typeof__(nullptr) nullptr_t;\n"
                             "struct P_k { int a; nullptr_t b; nullptr_t c; nullptr_t result; };\n"
                             "void op_k(struct P_k *p) { p->result = (p->a ? p->b : p->c); }"))
        found.append(Context(operator, ("int", "nullptr_t", "int *"), np_setup,
                             "typedef __typeof__(nullptr) nullptr_t;\n"
                             "struct P_k { int a; nullptr_t b; int * c; int * result; };\n"
                             "void op_k(struct P_k *p) { p->result = (p->a ? p->b : p->c); }"))
    elif key == "ConvertVectorExpr":
        found.append(Context(operator, ("ev4b", "v4si"), setup_for_holders(base.setup, ["ev4b", "v4si"])))
        v4hi_pre = tuple(pre + ([] if "typedef short v4hi __attribute__((vector_size(8)));" in pre else ["typedef short v4hi __attribute__((vector_size(8)));"]))
        found.append(Context(operator, ("v4si", "v4si"), Setup(cmd, v4hi_pre),
                             "typedef short v4hi __attribute__((vector_size(8)));\n"
                             "typedef int v4si __attribute__((vector_size(16)));\n"
                             "struct P_k { v4hi a; v4si result; };\n"
                             "void op_k(struct P_k *p) { p->result = (__builtin_convertvector(p->a, v4si)); }"))
    elif key == "IndirectGotoStmt":
        found.append(Context(operator, ("void *",), base.setup,
                             "void part_k_label(void);\n"
                             "struct P_k { void * a; };\n"
                             "void op_k(struct P_k *p) { goto *&&m; m: part_k_label(); }"))
    elif key == "MemberExpr (2 parts)":
        found.append(Context(operator, ("struct S_anon",), setup_for_holders(base.setup, ["struct S_anon"])))
        found.append(Context(operator, ("noderef_struct_ptr",), setup_for_holders(base.setup, ["noderef_struct_ptr"]),
                             "struct S { int m; int n; };\n"
                             "typedef struct S __attribute__((noderef)) *noderef_struct_ptr;\n"
                             "struct P_k { noderef_struct_ptr a; int result; };\n"
                             "void op_k(struct P_k *p) { p->result = (p->a->m); }"))
        found.append(Context(operator, ("struct S",), Setup(cmd + " -fdebug-info-for-profiling -g", tuple(pre))))
    elif key == "OffsetOfExpr (2 parts)":
        found.append(Context(operator, ("struct S_anon",), setup_for_holders(base.setup, ["struct S_anon"])))
        sa_pre = tuple(pre + ([] if "struct SA { int pad; int m[4]; };" in pre else ["struct SA { int pad; int m[4]; };"]))
        found.append(Context(operator, ("struct S",), Setup(cmd, sa_pre),
                             "struct SA { int pad; int m[4]; };\n"
                             "struct P_k { int a; unsigned long result; };\n"
                             "void op_k(struct P_k *p) { p->result = (__builtin_offsetof(struct SA, m[p->a])); }"))
    elif key == "UnaryOperator.Deref":
        found.append(Context(operator, ("noderef_int_ptr",), setup_for_holders(base.setup, ["noderef_int_ptr"])))
        arr_pre = tuple(pre + ([] if "typedef int __attribute__((noderef)) (*noderef_arr_ptr)[4];" in pre else ["typedef int __attribute__((noderef)) (*noderef_arr_ptr)[4];"]))
        found.append(Context(operator, ("int *",), Setup(cmd, arr_pre),
                             "typedef int __attribute__((noderef)) (*noderef_arr_ptr)[4];\n"
                             "struct P_k { noderef_arr_ptr a; };\n"
                             "void op_k(struct P_k *p) { (void)(*p->a); }"))
        found.append(Context(operator, ("void *",), base.setup,
                             "struct P_k { void * a; };\n"
                             "void op_k(struct P_k *p) { (void)(*p->a); }"))
    elif key == "WhileStmt":
        found.append(Context(operator, ("int", "void"), base.setup,
                             "void part_k_b(void);\n"
                             "struct P_k { int a; };\n"
                             "void op_k(struct P_k *p) { while (1) part_k_b(); }"))
    return found


def branch_writer(pool=None):
    """branch_trees' writer for the pool, made once (the holder facts read
    from the run that saved them)."""
    if STATE["writer"] is None:
        if pool is None:
            pool = pool_of(HOLDERS_FILE)
        STATE["writer"] = branch_trees.writer_of(pool)
    return STATE["writer"]


def not_tried(rounds: int) -> dict:
    change = {"closed": True, "outcome": "open", "why": f"not tried: the bound of {rounds} rounds was reached",
              "alternatives": [], "closing": None, "base": None}
    return change


# ---------------------------------------------------------------------------
# 2 unreached_branches: the blocks no context ran, with their test

def unreached_branches(operator, lines: dict, binary: dict) -> list:
    """Every successor block of one of the operator's path functions that no
    path of the operator ran, whose predecessor some path ran (§4.1). A block
    is run when every one of its lines is run (lines.json holds lines, not
    blocks). Under --in-hiop (or PSEUDOIR_IN_HIOP=1), restricted to the
    operator's in-HiOp functions and line spans."""
    key = key_for(operator)
    paths = lines.get(key, [])
    spans = in_hiop_spans_of(key)
    functions = in_hiop_functions(paths, spans)
    branches = []
    started = time.time()
    for number in range(len(functions)):
        function = functions[number]
        tick(f"[{key}] reading the blocks of {function}", number, len(functions), started)
        blocks, successors = blocks_and_successors(binary, function)
        ran = lines_of_function(paths, function)
        run = blocks_run(blocks, ran)
        found = branches_of_function(key, function, blocks, successors, run, paths)
        branches = branches + found
    accepted = first_accepted(paths)
    for branch in branches:
        branch["first_accepted"] = accepted
    return branches


def in_hiop_spans_of(key: str):
    """The in-HiOp [function, first, last] spans of `key` when --in-hiop or
    PSEUDOIR_IN_HIOP is active; None when running in-file across all functions."""
    if not STATE.get("in_hiop") and not os.environ.get("PSEUDOIR_IN_HIOP"):
        return None
    if STATE["in_hiop_spans"] is None:
        loaded = read_json(IN_HIOP_SPANS_FILE)
        if loaded is None:
            loaded = {}
        STATE["in_hiop_spans"] = loaded
    spans = STATE["in_hiop_spans"].get(key, [])
    return spans


def in_hiop_functions(paths: list, spans) -> list:
    """The functions of `paths` that hold the operator's in-HiOp spans."""
    all_functions = path_functions(paths)
    if spans is None:
        return all_functions
    wanted = []
    for item in spans:
        function = item[0]
        if function not in wanted:
            wanted.append(function)
    functions = []
    for function in all_functions:
        if function in wanted:
            functions.append(function)
    return functions


def branch_in_hiop(spans, function: str, test_line: int, first_line: int) -> bool:
    """Whether a branch (function, test_line, first_line) lies in one of the
    operator's in-HiOp spans: both test_line and first_line inside a span, or
    test_line on a single-line naming test."""
    if spans is None:
        return True
    for span_function, start, end in spans:
        if span_function != function:
            continue
        if start == end and test_line == start:
            return True
        if start < end and start <= test_line <= end and start <= first_line <= end:
            return True
    return False


def first_accepted(paths: list):
    """The operator's first accepted context: the base of a candidate when no
    context with known holders ran the branch's test."""
    for path in paths:
        if path["context"] is not None and path["accepted"]:
            return path["context"]
    for path in paths:
        if path["context"] is not None:
            operator = path["context"].operator
            if operator.name in ("AtomicExpr.AO__atomic_test_and_set", "AtomicExpr.AO__atomic_clear"):
                seeded = Context(operator, ("char *", "int"), our_setup())
                return seeded
            return path["context"]
    return None


def path_functions(paths: list) -> list:
    """The checking and lowering functions of every path, in first-seen order."""
    functions = []
    for path in paths:
        for function in path["checking"] + path["lowering"]:
            if function not in functions:
                functions.append(function)
    return functions


def blocks_and_successors(binary: dict, function: str) -> tuple:
    """The function's blocks and where each goes, read from the binary's
    listing once (every overload of the name)."""
    cache = binary["cache"]
    if function in cache:
        found = cache[function]
        return found
    blocks = {}
    successors = {}
    ranges = function_ranges(binary["names"], [function])
    for name, start, end in ranges:
        listing = listing_of(binary["path"], start, end)
        blocks.update(blocks_in(listing, name))
        successors.update(successors_in(listing, name))
    found = (blocks, successors)
    cache[function] = found
    return found


def lines_of_function(paths: list, function: str) -> set:
    ran = set()
    for path in paths:
        for line in path["lines"].get(function, ()):
            ran.add(line)
    return ran


def block_ran(block, ran: set) -> bool:
    if not block.lines:
        return False
    for line in block.lines:
        if line not in ran:
            return False
    return True


def blocks_run(blocks: dict, ran: set) -> set:
    run = set()
    for offset, block in blocks.items():
        if block_ran(block, ran):
            run.add(offset)
    return run


def branches_of_function(key: str, function: str, blocks: dict, successors: dict, run: set, paths: list) -> list:
    """Every branch of one function; each carries the function's lines of code
    and the lines the operator's paths ran, for the lines inside it
    (inside_of_branch)."""
    branches = []
    seen = set()
    code = code_lines(blocks)
    ran = lines_of_function(paths, function)
    spans = in_hiop_spans_of(key)
    for offset in sorted(run):
        test = blocks[offset]
        for to in successors.get(offset, []):
            if to in run or to not in blocks or not blocks[to].lines:
                continue
            untaken = blocks[to]
            if not branch_in_hiop(spans, function, test.last, untaken.first):
                continue
            name = f"{function}:{test.last}->{untaken.first}"
            if name in seen:
                continue
            seen.add(name)
            branch = branch_of(key, name, function, test, untaken, paths)
            branch["code"] = code
            branch["ran"] = ran
            branches.append(branch)
    return branches


def code_lines(blocks: dict) -> dict:
    """The function's lines of code, by file: every line of its blocks (a
    block of a function inlined into it is filed under its own file)."""
    lines = {}
    for block in blocks.values():
        found = lines.setdefault(block.file, set())
        for line in block.lines:
            found.add(line)
    return lines


def branch_of(key: str, name: str, function: str, test, untaken, paths: list) -> dict:
    """A branch: its function and file, the test's line, the untaken block's
    lines, and the lines records' paths that ran the test, each with its
    context (a candidate is built from one)."""
    ran_by = []
    for path in paths:
        if path["context"] is None:
            continue
        if block_ran(test, set(path["lines"].get(function, ()))):
            ran_by.append(path)
    branch = {"key": key, "id": name, "function": function, "file": untaken.file, "test": test.last,
            "test_lines": list(test.lines), "first": untaken.first, "lines": list(untaken.lines), "ran_by": ran_by}
    return branch


# ---------------------------------------------------------------------------
# 3 still_open: the branches the record has not settled

def still_open(branches: list, record) -> list:
    """The branches with no outcome in the record yet: a branch closed, or open
    after its candidate was traced, is not tried again (it is the owner's list)."""
    kept = []
    for branch in branches:
        if not record.has_branch(branch):
            kept.append(branch)
    return kept


# ---------------------------------------------------------------------------
# 4 condition_of: what the test reads

def condition_of(branch: dict) -> dict:
    """The test's text at its line and the statement it is in (an `if` that
    spans lines read whole), the case labels above the untaken block when
    the test is a `switch`, and the kinds of the names it reads (§4.2). The
    test's own line is read first, since -O0 gives each part of an `&&` its
    own block; the whole statement when the line alone reads nothing."""
    source = source_lines(branch["file"])
    own = text_at(source, branch["test"])
    statement = statement_at(source, branch["test"])
    cases = case_labels_above(source, branch["first"])
    text = own
    kinds = kinds_of(own + " " + cases)
    # either branch of an `||` can take the branch, so the whole statement is read
    if not kinds or "||" in statement:
        text = statement
        kinds = kinds_of(statement + " " + cases)
    kinds = kinds + ruled_kinds(branch["function"], text)
    parts = parts_named(text)
    joined = joined_parts(statement)
    if len(joined) > 1 and joined not in parts:
        parts.append(joined)
    condition = {"branch": branch, "text": text, "own_line": own, "statement": statement, "cases": cases,
                 "kinds": kinds, "parts": parts}
    return condition


def joined_parts(statement: str) -> list:
    """2026-10-21: the parts an `&&` statement names, as one set: every one
    of its tests must hold, so its parts change together (CGExprScalar.cpp
    5613: `isCheapEnoughToEvaluateUnconditionally(lhsExpr, CGF) &&
    isCheapEnoughToEvaluateUnconditionally(rhsExpr, CGF)`, both arms
    literal). Empty when the statement has no `&&`."""
    joined = []
    if "&&" not in statement:
        return joined
    for named in parts_named(statement):
        for part in named:
            if part == "every":
                continue
            if part not in joined:
                joined.append(part)
    joined.sort()
    return joined


def source_path(file: str) -> str:
    if os.path.exists(file):
        return file
    root = os.path.join(os.environ.get("PSEUDOIR_SOURCES", SOURCES_DEFAULT), SOURCES_CHECKOUT)
    for prefix in SOURCES_PREFIXES:
        if file.startswith(prefix):
            path = os.path.join(root, file[len(prefix):])
            return path
    return file


SOURCE_LINES = {}


def source_lines(file: str) -> list:
    if file in SOURCE_LINES:
        lines = SOURCE_LINES[file]
        return lines
    lines = []
    path = source_path(file)
    if os.path.exists(path):
        with open(path, encoding="utf-8", errors="replace") as read:
            lines = read.read().split("\n")
    SOURCE_LINES[file] = lines
    return lines


def text_at(lines: list, number: int) -> str:
    if 0 < number <= len(lines):
        text = lines[number - 1].strip()
        return text
    return ""


# starts_test and open_parentheses as the first node's
# trace_the_pages_routes.py writes them (§4.2 names them).
def starts_test(text: str) -> bool:
    test = text.startswith("if (") or text.startswith("else if (") or text.startswith("} else if (")
    return test


def open_parentheses(text: str) -> int:
    count = text.count("(") - text.count(")")
    return count


def continues_above(above: str, here: str) -> bool:
    """Whether the line `here` continues a statement begun on `above`."""
    ends = above.endswith("&&") or above.endswith("||") or above.endswith("(") or above.endswith(",")
    starts = here.startswith("&&") or here.startswith("||") or here.startswith(")")
    found = (ends or starts) and not starts_test(here)
    return found


def statement_at(lines: list, number: int) -> str:
    first = number
    while first > 1 and number - first < STATEMENT_REACH:
        if not continues_above(text_at(lines, first - 1), text_at(lines, first)):
            break
        first -= 1
    count = 0
    for line in range(first, number + 1):
        count += open_parentheses(text_at(lines, line))
    last = number
    while count > 0 and last - number < STATEMENT_REACH:
        last += 1
        count += open_parentheses(text_at(lines, last))
    parts = []
    for line in range(first, last + 1):
        parts.append(text_at(lines, line))
    text = " ".join(parts)
    return text


def case_labels_above(lines: list, number: int) -> str:
    """The `case` labels just above a block (a switch's branch names its value:
    `case LangOptions::SOB_Trapping:` above line 4461 of CGExprScalar.cpp)."""
    labels = []
    line = number - 1
    while line > 0 and number - line <= STATEMENT_REACH:
        text = text_at(lines, line)
        if text.startswith("case ") or text.startswith("default:"):
            labels.append(text)
        elif text and not text.startswith("[[fallthrough]]") and not text.startswith("//"):
            break
        line -= 1
    joined = " ".join(labels)
    return joined


def kinds_of(text: str) -> list:
    """(kind, name) for every name of §4.2's table the text holds: the
    options (OPTION_NAMES, every sanitizer kind named, an option with no flag
    in the table), the names that close a branch, the constants, widths,
    holder properties and shapes."""
    kinds = []
    for name, options, holder, preamble in OPTION_NAMES:
        if name in text:
            kinds.append(("option", name))
    kinds = kinds + sanitizer_kinds(text)
    for name in TARGET_NAMES:
        if name in text:
            kinds.append(("target", name))
    for found in OPTION_MEMBER.finditer(text):
        member = found.group(1)
        if not option_named(member):
            kinds.append(("option without a flag", member))
    for name, outcome, why in CLOSING_NAMES:
        if name in text:
            kinds.append(("closing", name))
    for name in CONSTANT_NAMES:
        if name in text:
            kinds.append(("constant", name))
    for name in WIDTH_NAMES:
        if name in text:
            kinds.append(("width", name))
    for predicate, true_holder, false_holder in CHANGE_FOR:
        # a predicate with two rows in the table (isFloatingPointTy) is one kind
        if re.search(r"\b" + predicate + r"\b", text) and ("holder", predicate) not in kinds:
            kinds.append(("holder", predicate))
    for name, shape in SHAPE_NAMES:
        if name in text:
            kinds.append(("shape", name))
    return kinds


def option_named(name: str) -> bool:
    for option_name, options, holder, preamble in OPTION_NAMES:
        if option_name == name:
            return True
    return False


def sanitizer_kinds(text: str) -> list:
    """("sanitizer", flag name) for every SanitizerKind the text names; the
    undefined-behaviour group when it reads SanOpts and names none."""
    kinds = []
    flags = sanitizer_flags()
    for found in SANITIZER_KIND.finditer(text):
        flag = flags.get(found.group(1))
        if flag and ("sanitizer", flag) not in kinds:
            kinds.append(("sanitizer", flag))
    if not kinds and "SanOpts" in text:
        kinds.append(("sanitizer", SANITIZERS_UNNAMED))
    return kinds


def sanitizer_flags() -> dict:
    """SanitizerKind's name -> the -fsanitize= name, from Sanitizers.def."""
    if STATE.get("sanitizers") is not None:
        flags = STATE["sanitizers"]
        return flags
    flags = {}
    for line in source_lines(SANITIZERS_FILE):
        found = SANITIZER_LINE.match(line.strip())
        if found:
            flags[found.group(2)] = found.group(1)
    STATE["sanitizers"] = flags
    return flags


def parts_named(text: str) -> list:
    """The part sets a candidate changes: the parts the text names, one set
    each, every part at once for the result's type; empty when it names none
    (then each part in turn)."""
    named = []
    for name, part in PART_NAMES:
        if name not in text:
            continue
        parts = [part]
        if isinstance(part, tuple):
            parts = list(part)
        if parts not in named:
            named.append(parts)
    for found in ARGUMENT.finditer(text):
        part = int(found.group(1))
        if [part] not in named:
            named.append([part])
    return named


# ---------------------------------------------------------------------------
# 5 change_for: the holder, constant, width, shape or option that takes the branch

def change_for(condition: dict, pool: set) -> dict:
    """The change §4.3 names for each kind the condition reads. Closed when
    the condition reads only closing names (an option, another language, the
    target, clang's bookkeeping); open, for the owner, when it reads no name the
    tables know. A closing name beside other kinds is kept: when the other
    kinds' candidates fail, it names the branch's outcome."""
    if is_a_refusal(condition["branch"]):
        change = {"closed": True, "outcome": NO_EXIT_TO_LLVM[0], "why": NO_EXIT_TO_LLVM[1], "alternatives": [],
                  "closing": NO_EXIT_TO_LLVM, "base": base_of(condition["branch"])}
        return change
    if is_clangs_own_guard(condition["branch"]):
        change = {"closed": True, "outcome": CLANGS_OWN_GUARD[0], "why": CLANGS_OWN_GUARD[1], "alternatives": [],
                  "closing": CLANGS_OWN_GUARD, "base": base_of(condition["branch"])}
        return change
    if is_one_arg_has_fallback(condition):
        change = {"closed": True, "outcome": "cannot reach",
                  "why": "entry_info: HasFallback is only true for 2-argument __builtin_ctzg or __builtin_clzg",
                  "alternatives": [], "closing": ("cannot reach", "entry_info: HasFallback is false for 1 argument"),
                  "base": base_of(condition["branch"])}
        return change
    unreachable_why = entry_info_unreachable(condition)
    if unreachable_why:
        not_needed_prefixes = (
            "not on all three architectures:",
            "another language:",
            "not GNU C:",
            "clang's own bookkeeping:",
            "diagnostic only:",
            "optimization:",
            "instrumentation:",
            "no exit to LLVM:",
        )
        outcome = "not needed" if unreachable_why.startswith(not_needed_prefixes) else "cannot reach"
        change = {"closed": True, "outcome": outcome, "why": unreachable_why,
                  "alternatives": [], "closing": (outcome, unreachable_why),
                  "base": base_of(condition["branch"])}
        return change
    if is_closing_brace_block(condition["branch"]):
        change = {"closed": True, "outcome": "not needed", "why": INSTRUMENTATION,
                  "alternatives": [], "closing": ("not needed", INSTRUMENTATION),
                  "base": base_of(condition["branch"])}
        return change
    closing = closing_of(condition["kinds"], condition["text"] + " " + condition["cases"])
    alternatives = []
    for kind, name in condition["kinds"]:
        alternatives = alternatives + alternatives_of(kind, name, condition, pool)
    change = {"closed": False, "outcome": "", "why": "", "alternatives": alternatives, "closing": closing,
              "base": base_of(condition["branch"])}
    if alternatives:
        # a target name's closing (PointerAuth) stays as the fallback: a target
        # that takes the branch is the verdict (taken, or "not needed: taken on
        # x86-64"); when no target takes it, the ruled closing is the outcome
        # (the owner, 2026-10-20: pointer authentication is "not needed"). Until
        # 2026-10-21 04:40 UTC the fallback was dropped here, and l189 left
        # the owner's ruled instances "open".
        return change
    change["closed"] = True
    if closing is not None:
        change["outcome"] = closing[0]
        change["why"] = closing[1]
        return change
    change["outcome"] = "open"
    change["why"] = "the condition is not read: for the owner"
    unflagged = options_without_a_flag(condition["kinds"])
    if unflagged:
        change["why"] = "it reads an option with no flag in the table yet: " + ", ".join(unflagged)
    elif has_candidate_kind(condition["kinds"]):
        change["why"] = "no candidate could be written: no context of the records with known holders ran its test, " \
                        "or the part is not written as a value"
    return change


# ---------------------------------------------------------------------------
# the owner, 2026-10-21, 05:50 UTC, on a branch whose untaken block is a diagnostic
# and a refusal ("no exit to LLVM"): "yes, i believe thats correct." Read
# from the block's own lines, not from a name in the test; a block that also
# holds code reaching LLVM is not one.
NO_EXIT_TO_LLVM = ("not needed", "no exit to LLVM: clang refusing an ill-formed program")
# A diagnostic: `Diag(...)`, `S.Diag(...)`, `SemaRef.Diag(...)`, `return Diag(...)`.
DIAGNOSTIC = re.compile(r"^(?:return\s+)?(?:\w+(?:\.|->))?Diag\(")
# A refusal at any place: `return ExprError(...)`, `return StmtError(...)`, `return QualType(...)`.
REFUSAL = re.compile(r"^return\s+(?:ExprError|StmtError|QualType)\(")
# A refusal only right after a diagnostic: `return true;`, `return false;`, `return nullptr;`.
REFUSAL_AFTER_A_DIAGNOSTIC = ("return true", "return false", "return nullptr")


def is_a_refusal(branch: dict) -> bool:
    """Whether the branch's untaken block (its lines, and the lines after them
    inside the block its `if` guards) is only diagnostics and refusals: every
    statement a Diag or a refusal, a `return true/false/nullptr` only after a
    Diag, and at least one refusal."""
    statements = statements_of_block(branch)
    if not statements:
        return False
    diagnosed = False
    refused = False
    for statement in statements:
        if DIAGNOSTIC.match(statement):
            diagnosed = True
            refused = refused or statement.startswith("return")
        elif REFUSAL.match(statement):
            refused = True
        elif diagnosed and statement in REFUSAL_AFTER_A_DIAGNOSTIC:
            refused = True
        else:
            return False
    return refused


# the owner, 2026-10-21, 01:20 UTC (PCHQ log 489 §23), on a branch whose block is
# `llvm_unreachable`: "is that needed?" (it lowers nothing; no program reaches
# it: clang's own guard), and log 494's list of the owner's rules keeps it. A branch
# whose untaken block is only that guard is "not needed".
CLANGS_OWN_GUARD = ("not needed", "clang's own guard: llvm_unreachable, no program reaches it")
UNREACHABLE = re.compile(r"^(?:llvm_unreachable|__builtin_unreachable|LLVM_BUILTIN_UNREACHABLE|llvm::report_fatal_error|report_fatal_error)\b")
# A `case X:` or `default:` label in front of a statement (a switch's branch).
LABEL = re.compile(r"^(?:default\s*:|case\s+[\w:]+\s*:(?!:))\s*")


def is_clangs_own_guard(branch: dict) -> bool:
    """Whether the branch's untaken block is only `llvm_unreachable(...)`,
    after its `case` or `default` labels."""
    statements = statements_of_block(branch)
    if not statements:
        return False
    for statement in statements:
        unlabelled = without_labels(statement)
        if not UNREACHABLE.match(unlabelled):
            return False
    return True


def is_closing_brace_block(branch: dict) -> bool:
    """Whether every line of the branch's untaken block is only a closing
    brace `}` (a jump or cleanup merge block at the end of a scope that carries
    no statement of its own)."""
    if not branch["lines"]:
        return False
    source = source_lines(branch["file"])
    for line in branch["lines"]:
        if code_of(text_at(source, line)) != "}":
            return False
    return True


def is_one_arg_has_fallback(condition: dict) -> bool:
    """CGBuiltin.cpp 3340, 3372: `if (!HasFallback)` in BI__builtin_ctz* and
    BI__builtin_clz*. HasFallback is `BuiltinID == BI__builtin_ctzg &&
    E->getNumArgs() > 1` (or BI__builtin_clzg), so its false branch (lines 3346
    and 3378) cannot be reached by any 1-argument operator."""
    branch = condition["branch"]
    if "HasFallback" not in condition["text"]:
        return False
    if branch["first"] not in (3346, 3378):
        return False
    found = "(2 parts)" not in branch["key"]
    return found


def entry_info_unreachable(condition: dict) -> str:
    """When a branch inside an in-HiOp span tests an entry_info property
    (arity, BuiltinID, Opcode, ExprKind) that is fixed to the opposite value
    by the HiOp itself."""
    branch = condition["branch"]
    key = branch["key"]
    fn = branch["function"]
    pair = (branch["test"], branch["first"])
    if key == "ShuffleVectorExpr (2 parts)" and pair in ((5483, 5495), (5483, 5490), (5483, 5484), (5497, 5498), (1889, 1925)):
        return "entry_info: ShuffleVectorExpr (2 parts) has getNumArgs() == 2"
    if key == "CallExpr.BI__builtin_va_end" and pair == (3205, 3206):
        return "entry_info: BuiltinID is BI__builtin_va_end != BI__va_start"
    if key == "CallExpr.BI__builtin_cpu_init" and pair == (1087, 1089):
        return "entry_info: BuiltinID is BI__builtin_cpu_init"
    if key == "UnaryOperator.Imag" and pair == (3387, 3390):
        return "entry_info: getOpcode() is UO_Imag != UO_Real"
    if key == "UnaryOperator.Real" and pair == (3387, 3390):
        return "not GNU C: in C __real on a real scalar is an rvalue handled by VisitReal without calling EmitUnaryOpLValue"
    if key == "UnaryExprOrTypeTraitExpr.SizeOf" and pair in ((4269, 4270), (4269, 4271), (4732, 4733)):
        return "entry_info: ExprKind is UETT_SizeOf"
    if key == "ReturnStmt (0 parts)" and pair == (1678, 1679):
        return "entry_info: ReturnStmt (0 parts) has no return expression (RV is nullptr)"
    if fn == "CodeGenFunction::EmitCompoundStmtWithoutScope" and pair == (589, 595):
        return "entry_info: CompoundStmt is not a GNU statement expression (GetLast is false)"
    if key == "CallExpr.BI__builtin_flt_rounds" and pair == (4245, 4246):
        return "entry_info: llvm.get.rounding returns i32 which equals ResultType (int) on all 64-bit targets"
    if key in ("CallExpr.BI__builtin_reduce_max", "CallExpr.BI__builtin_reduce_min") and pair in ((4113, 4115), (4131, 4133)):
        return "not on all three architectures: sizeless vector type"
    if fn == "Sema::CreateBuiltinArraySubscriptExpr" and pair in ((5295, 5301), (5310, 5312)):
        return "not GNU C: DefaultFunctionArrayLvalueConversion decays array operands to pointers in C before lines 5295 and 5310"
    if fn == "CodeGenFunction::EmitArraySubscriptExpr" and pair == (4504, 4505):
        return "entry_info: ScalarExprEmitter::VisitArraySubscriptExpr handles vector bases before EmitArraySubscriptExpr"
    if fn == "Sema::CreateBuiltinBinOp" and pair == (15082, 15084):
        return "entry_info: LHSExpr of the isolated binary operator is a slot operand, not a nested comparison BinaryOperator"
    if fn == "Sema::CheckInvalidBuiltinCountedByRef" and pair == (6012, 6015):
        return "entry_info: BuiltinID is BI__builtin_counted_by_ref"
    if fn == "CodeGenFunction::EmitBuiltinExpr" and pair == (3646, 3649):
        return "clang's own bookkeeping: EmitBuiltinExpr constant-folds __builtin_constant_p(Arg) to 0 at line 2589 via ExprConstant.cpp:13144 whenever Arg->HasSideEffects(getContext()) is true"
    if fn == "CodeGenFunction::EmitBuiltinExpr" and pair == (3684, 3686):
        return "clang's own bookkeeping: Sema::BuiltinCountedByRef requires dyn_cast<MemberExpr>(Arg) and rejects UnaryOperator arguments"
    if fn == "CodeGenFunction::EmitBuiltinExpr" and pair == (3697, 3700):
        return "clang's own bookkeeping: Sema::BuiltinCountedByRef already verified FAMDecl->findCountedByField() is non-null"
    if fn == "CodeGenFunction::EmitBuiltinExpr" and pair == (4741, 4745):
        return "not on all three architectures: IntPtrTy->getBitWidth() is 64 on all three 64-bit targets (riscv64, x86-64, aarch64)"
    if fn == "CodeGenFunction::EmitCaseStmt" and pair == (1934, 1935):
        return "entry_info: CaseStmt (2 parts) has a single case label whose sub-statement is not another CaseStmt"
    if fn == "CodeGenFunction::EmitCaseStmt" and pair == (1957, 1958):
        return "entry_info: the CaseStmt sub-statement is a call statement, not a nested DefaultStmt"
    if fn == "CodeGenFunction::EmitCaseStmtRange" and pair == (1800, 1801):
        return "instrumentation: Rem is getProfileCount(&S) % NCases, only non-zero under PGO profile instrumentation"
    if fn == "CodeGenFunction::EmitCaseStmtRange" and pair == (1843, 1846):
        return "entry_info: the CaseStmt sub-statement is a call expression (part_k_c()), which does not clear the insertion point"
    if fn == "CodeGenFunction::EmitBranchOnBoolExpr" and pair == (2035, 2037):
        return "entry_info: Cond of the isolated ConditionalOperator is a slot operand, not a nested ConditionalOperator"
    if fn == "Sema::DiagnoseConditionalForNull" and pair == (8016, 8019):
        return "diagnostic only: -Wnon-literal-null-conversion in DiagnoseConditionalForNull"
    if fn == "Sema::CheckConditionalOperands" and pair == (8588, 8589):
        return "no exit to LLVM: clang refusing an ill-formed program"
    if fn == "Sema::CheckConditionalOperands" and pair == (8680, 8681):
        return "cannot reach: after arithmetic conversions, void/pointer/record/scalar checks, and checkConditionalNullPointer, two remaining operands cannot have the same type"
    if fn == "Sema::PerformObjectMemberConversion" and pair == (2995, 2998):
        return "not GNU C: PerformObjectMemberConversion is a C++ object-member conversion helper"
    if fn == "Sema::ActOnFinishSwitchStmt" and pair == (1381, 1382):
        return "cannot reach: TheDefaultStmt is only non-null when a previous DefaultStmt already existed in the same switch"
    if fn == "Sema::ActOnForStmt" and pair == (2271, 2275):
        return "entry_info: the first part of ForStmt is an expression or omitted, not a DeclStmt"
    if fn == "Sema::CreateGenericSelectionExpr" and pair in ((1830, 1831), (1948, 1949)):
        return "no exit to LLVM: clang refusing an ill-formed program"
    if fn == "Sema::ActOnLabelStmt" and pair == (601, 602):
        return "no exit to LLVM: clang refusing an ill-formed program (redefinition of label)"
    if fn == "CodeGenFunction::EmitLabel" and pair == (728, 735):
        return "entry_info: the isolated LabelStmt has no preceding forward goto reference"
    if fn == "Sema::BuildMemberReferenceExpr" and pair in ((692, 693), (1001, 1003)):
        return "not GNU C: Base / BaseExpr is only null for an implicit C++ or Objective-C member access"
    if fn == "Sema::BuildMemberReferenceExpr" and pair == (1038, 1039):
        return "no exit to LLVM: clang refusing an ill-formed program"
    if fn == "Sema::BuildMemberReferenceExpr" and pair == (1065, 1076):
        return "not GNU C: in C a struct or union member is either a FieldDecl or an IndirectFieldDecl"
    if fn == "ScalarExprEmitter::VisitMemberExpr" and pair == (2027, 2028):
        return "not GNU C: EvaluateAsInt on a MemberExpr after tryEmitAsConstant only succeeds in C++"
    if fn == "CodeGenFunction::EmitMemberExpr" and pair == (4988, 5003):
        return "not GNU C: in C a MemberExpr's member declaration is always a FieldDecl"
    if fn == "Sema::BuildBuiltinOffsetOf" and pair in ((16178, 16180), (16178, 16182), (16182, 16186)):
        return "no exit to LLVM: clang refusing an ill-formed program"
    if fn == "ScalarExprEmitter::VisitOffsetOfExpr" and pair in ((3526, 3530), (3526, 3533)):
        return "clang's own bookkeeping: MemberDecl is always found in RD->fields() before Field == FieldEnd"
    if fn == "Sema::CheckUnaryExprOrTypeTraitOperand" and pair in ((4359, 4360), (4374, 4375)):
        return "diagnostic only: -Wsizeof-array-argument and -Wsizeof-array-decay on a parameter or binary operator"
    if "PromotionType.isNull()" in condition["statement"] and pair in ((3672, 3674), (3411, 3413), (675, 679), (3391, 3393), (652, 656), (3633, 3635)):
        return "cannot reach: PromotionType is only non-null for _Float16, which is promoted to float by Sema before CodeGen in C"
    if fn == "ScalarExprEmitter::VisitImag" and pair == (3706, 3707):
        return "cannot reach: Sema applies DefaultLvalueConversion to real scalar operands of __imag in C, so Op is always an rvalue"
    if fn == "Sema::BuildVAArgExpr" and pair in ((16790, 16792), (16793, 16795)):
        return "cannot reach: getPromotedIntegerType returns signed int for < 32-bit types (incompatible with < 32-bit UnderlyingType) and preserves signedness for >= 32-bit types"
    return ""


def without_labels(statement: str) -> str:
    text = statement
    found = LABEL.match(text)
    while found is not None and found.end() > 0:
        text = text[found.end():]
        found = LABEL.match(text)
    return text


def statements_of_block(branch: dict) -> list:
    """The statements of the branch's untaken block, from its first line to its
    last line of code (the guarded block's too), read whole to their `;`,
    without comments and braces."""
    source = source_lines(branch["file"])
    block, inside = inside_of_branch(branch)
    last = max(list(branch["lines"]) + inside)
    first = min(list(branch["lines"]) + [branch["first"]])
    parts = []
    for line in range(first, last + 1):
        parts.append(code_of(text_at(source, line)))
    line = last
    while parts and not parts[-1].endswith(";") and line - last < STATEMENT_REACH:
        line += 1
        parts.append(code_of(text_at(source, line)))
    text = " ".join(parts)
    statements = []
    for statement in text.split(";"):
        statement = statement.replace("{", " ").replace("}", " ").strip()
        if statement:
            statements.append(" ".join(statement.split()))
    return statements


def has_target_alternative(alternatives: list) -> bool:
    for alternative in alternatives:
        if alternative["kind"] == "target":
            return True
    return False


def closing_is_a_target_name(condition: dict) -> bool:
    """Whether the condition's first closing name is one of TARGET_NAMES."""
    for kind, name in condition["kinds"]:
        if kind == "closing":
            found = name in TARGET_NAMES
            return found
    return False


def options_without_a_flag(kinds: list) -> list:
    found = []
    for kind, name in kinds:
        if kind == "option without a flag" and name not in found:
            found.append(name)
    return found


def has_candidate_kind(kinds: list) -> bool:
    for kind, name in kinds:
        if kind != "closing":
            return True
    return False


def closing_of(kinds: list, text: str):
    """The first closing name's outcome and badge."""
    for kind, name in kinds:
        if kind != "closing":
            continue
        found = closing_named(name)
        if found is not None:
            return found
    return None


def base_of(branch: dict):
    """The context a candidate is built from: one that ran the branch's test."""
    if branch["ran_by"]:
        base = branch["ran_by"][0]["context"]
        return base
    base = branch.get("first_accepted")
    return base


def part_sets(condition: dict, base) -> list:
    """The part sets to change: the named ones, or each part in turn."""
    count = 0
    if base is not None:
        count = len(base.holders)
    sets = []
    for named in condition["parts"]:
        if named == ["every"]:
            every = []
            for part in range(count):
                every.append(part)
            sets.append(every)
        elif max(named) < count:
            sets.append(named)
    if sets:
        return sets
    for part in range(count):
        sets.append([part])
    return sets


def alternatives_of(kind: str, name: str, condition: dict, pool: set) -> list:
    base = base_of(condition["branch"])
    alternatives = []
    if base is None:
        return alternatives
    sets = part_sets(condition, base)
    if kind == "holder":
        alternatives = holder_alternatives(name, sets, base, pool)
    elif kind == "constant":
        alternatives = program_alternatives("constant", sets, LITERALS)
    elif kind == "width":
        alternatives = program_alternatives("width", sets, (str(WIDTH),))
    elif kind == "shape":
        alternatives = program_alternatives(shape_of(name), sets, ("1",))
    elif kind == "option":
        alternatives = option_alternatives(name, sets, base, pool)
    elif kind == "sanitizer":
        alternatives = sanitizer_alternatives(name)
    elif kind == "target":
        alternatives = target_alternatives(name)
    return alternatives


def target_alternatives(name: str) -> list:
    """The base context on x86-64 and on aarch64 (write_candidate drops the
    second name's copies of the same two)."""
    alternatives = []
    for target, triple in OTHER_TARGETS:
        alternatives.append({"kind": "target", "name": name, "target": target, "triple": triple, "parts": [],
                             "holders": []})
    return alternatives


def option_alternatives(name: str, sets: list, base, pool: set) -> list:
    """The option alone, and with the holder its type needs in each part set
    and in every part at once (a matrix under -fenable-matrix, an _Accum
    under -ffixed-point)."""
    alternatives = []
    every = []
    for part in range(len(base.holders)):
        every.append(part)
    if len(every) > 1 and every not in sets:
        sets = sets + [every]
    for option_name, options, holder, preamble in OPTION_NAMES:
        if option_name != name:
            continue
        for option in options:
            alternatives.append({"kind": "option", "name": name, "option": option, "preamble": list(preamble),
                                 "parts": [], "holders": list(base.holders)})
            if not holder:
                continue
            for parts in sets:
                holders = list(base.holders)
                for part in parts:
                    holders[part] = holder
                alternatives.append({"kind": "option", "name": name, "option": option, "preamble": list(preamble),
                                     "parts": parts, "holders": holders})
    return alternatives


def sanitizer_alternatives(flag: str) -> list:
    """-fsanitize=<kind>, and -fsanitize-trap=<kind> beside it."""
    alternatives = []
    for option in ("-fsanitize=" + flag, "-fsanitize=" + flag + " -fsanitize-trap=" + flag):
        alternatives.append({"kind": "option", "name": "SanitizerKind " + flag, "option": option, "preamble": [],
                             "parts": [], "holders": []})
    return alternatives


def shape_of(name: str) -> str:
    for shape_name, shape in SHAPE_NAMES:
        if shape_name == name:
            return shape
    return "literal"


def holder_alternatives(predicate: str, sets: list, base, pool: set) -> list:
    """The base's holders with the part set replaced by the holder that makes
    the predicate true, and by the one that makes it false: the base took one
    branch, the trace says which the other takes."""
    alternatives = []
    for true_holder, false_holder in holders_of_predicate(predicate):
        for holder in (true_holder, false_holder):
            if holder not in pool and holder not in HOLDER_PREAMBLE:
                continue
            for parts in sets:
                holders = list(base.holders)
                for part in parts:
                    holders[part] = holder
                if tuple(holders) == tuple(base.holders):
                    continue
                alternatives.append({"kind": "holder", "name": predicate, "parts": parts, "holders": holders})
    return alternatives


def holders_of_predicate(predicate: str) -> list:
    found = []
    for name, true_holder, false_holder in CHANGE_FOR:
        if name == predicate:
            found.append((true_holder, false_holder))
    return found


def program_alternatives(kind: str, sets: list, values: tuple) -> list:
    """A part set rewritten in the program: one alternative a part set and a
    value (a constant part is tried as 1 and as 0); every part of the set
    takes the value (2026-10-21: until then a set of two parts was dropped,
    and 5613's two literal arms were never written)."""
    alternatives = []
    for parts in sets:
        for value in values:
            alternatives.append({"kind": kind, "parts": parts, "value": value})
    return alternatives


# ---------------------------------------------------------------------------
# 6 write_candidate: a context, new holders or its own program

def write_candidate(operator, contexts: list, change: dict) -> list:
    """Every candidate the change's alternatives give (§4.4): a holder change
    through the standard form; a constant, width or shape change as the
    standard form's program with the one part rewritten (program_of); an
    option change as our setup with the option added. The caller drops the
    ones already traced."""
    base = change["base"]
    written = []
    seen = set()
    for alternative in change["alternatives"]:
        candidate = candidate_of(operator, base, alternative)
        if candidate is None:
            continue
        key = check.key_of(candidate)
        if key in seen:
            continue
        seen.add(key)
        written.append(candidate)
    return written


def candidate_of(operator, base, alternative: dict):
    kind = alternative["kind"]
    if kind == "holder":
        setup = setup_for_holders(base.setup, alternative["holders"])
        candidate = Context(operator, tuple(alternative["holders"]), setup)
        if base.program:
            # PCHQ log 503 §2, line 16: a base written in its own program (a
            # place, a constant) keeps it, each part in its place with its new
            # holder where the holder fits the place; until 2026-10-22 the
            # program was dropped (run tlp1_l10's bit-field and global
            # register bases)
            candidate = holders_in_place(operator, base, alternative["holders"], setup)
        if candidate is None or not writes(candidate):
            return None
        return candidate
    if kind == "option":
        candidate = option_candidate(operator, base, alternative)
        return candidate
    if kind == "target":
        setup = Setup(with_target(base.setup.command, alternative["triple"]), base.setup.preamble)
        candidate = Context(operator, base.holders, setup, base.program)
        return candidate
    text = program_of(base, alternative["parts"], kind, alternative["value"])
    if not text:
        return None
    holders = place_holders(base.holders, alternative["parts"], kind)
    candidate = Context(operator, holders, setup_for_place(base.setup, kind), text)
    return candidate


def holders_in_place(operator, base, holders: list, setup):
    """The base's program, its parts' holders changed: a changed part keeps
    its place and value form (branch_trees.base_reading) when its new holder
    fits the place, else it is a field; the other parts stay as they are."""
    writer = branch_writer()
    reading = branch_trees.base_reading(base)
    choices = []
    for index in range(len(reading["parts"])):
        holder, place, form = reading["parts"][index]
        if index < len(holders) and holders[index] != base.holders[index]:
            holder = holders[index]
            if not branch_trees.fits(holder, place, writer.held_facts):
                place = "field"
        choices.append((holder, place, form))
    reading["preamble"] = list(setup.preamble)
    context = branch_trees.written_context(operator, choices, reading["options"], reading["target"], reading, writer)
    return context


def place_holders(holders: tuple, parts: list, kind: str) -> tuple:
    """The base's holders, with a place form's holder in each part it
    rewrites (PLACE_FORMS: the vector a vector element is read from); the
    other program changes keep the base's holders."""
    if kind not in PLACE_FORMS:
        return holders
    found = list(holders)
    for part in parts:
        if part < len(found):
            found[part] = place_holder(kind, found[part])
    found = tuple(found)
    return found


def setup_for_place(setup, kind: str):
    """The base's setup, with the option a place form needs (PLACE_DECLARATIONS:
    a matrix element needs -fenable-matrix)."""
    option = ""
    if kind in PLACE_DECLARATIONS:
        option = PLACE_DECLARATIONS[kind][1]
    if not option or option in setup.command.split():
        return setup
    found = Setup(setup.command + " " + option, setup.preamble)
    return found


def option_candidate(operator, base, alternative: dict):
    """§4.4's option change, setup_with(option, preamble) on the base's own
    command (so an option a round before keeps): the base's holders and
    program, or the holders the option's type needs through the standard form."""
    preamble = list(base.setup.preamble)
    for line in alternative["preamble"]:
        if line not in preamble:
            preamble.append(line)
    setup = Setup(base.setup.command + " " + alternative["option"], tuple(preamble))
    if not alternative["parts"]:
        candidate = Context(operator, base.holders, setup, base.program)
        return candidate
    candidate = Context(operator, tuple(alternative["holders"]), setup)
    if not writes(candidate):
        return None
    return candidate


def with_target(command: str, triple: str) -> str:
    """The command with its --target replaced (setup_with only appends; clang
    takes the last --target, but one --target in the record reads plainly)."""
    if TARGET_OPTION.search(command):
        replaced = TARGET_OPTION.sub(lambda found: "--target=" + triple, command, count=1)
        return replaced
    added = command + " --target=" + triple
    return added


def target_of(context) -> str:
    """Which of the three architectures a context is compiled for."""
    found = TARGET_OPTION.search(context.setup.command)
    if found is None:
        return BASE_TARGET[0]
    for target, triple in [BASE_TARGET] + OTHER_TARGETS:
        if found.group(1) == triple:
            return target
    return found.group(1)


def setup_for_holders(setup, holders: list):
    """The base's setup, with the declaration a holder outside the pool needs."""
    preamble = list(setup.preamble)
    for holder in holders:
        for line in HOLDER_PREAMBLE.get(holder, ()):
            if line not in preamble:
                preamble.append(line)
    found = Setup(setup.command, tuple(preamble))
    return found


def writes(context) -> bool:
    """Whether the standard form writes this context (it refuses some
    holder sets by name)."""
    try:
        standard_source(context)
    except Exception as error:
        check.say(f"[candidate] the writer cannot write {context.operator.name} with "
                  f"{list(context.holders)}: {str(error)[:120]}")
        return False
    return True


def program_of(base, parts: list, kind: str, value: str) -> str:
    """variant_candidates.program_of generalized (§4.4): the base's program
    (its own, or the standard form's) with each part of the set rewritten: a
    constant or a literal shape where the part was, the part in parentheses,
    the part as a place (a field of P_k), as a bit-field of WIDTH bits, or as
    one of the kinds of place of PLACE_FORMS (with what it declares before
    P_k). The struct and op_k keep their names, so every reader of the
    records works. A part not written as a value the body holds (a type, or
    a literal already) is left as it is; empty when no part changed."""
    text = base.program or standard_source(base)
    lines = text.split("\n")
    body_at = index_of_line(lines, "op_" + KEY + "(")
    struct_at = index_of_line(lines, "struct P_" + KEY + " {")
    slots = slots_of_operator(base.operator)
    if body_at < 0:
        return ""
    declarations = []
    for part in parts:
        if part >= len(slots):
            continue
        name = slots[part]
        spelling = spelling_in(lines[body_at], name)
        if not spelling:
            continue
        holder = base.holders[part]
        if kind in ("constant", "literal"):
            if holder in ("struct S", "union U", "const struct S"):
                lines[body_at] = rewritten(lines[body_at], spelling, f"(({holder}){{0}})")
            elif holder != "int" and holder not in ("fntype", "void", "struct I"):
                lines[body_at] = rewritten(lines[body_at], spelling, f"(({holder}){value})")
            else:
                lines[body_at] = rewritten(lines[body_at], spelling, value)
        elif kind == "parenthesis":
            lines[body_at] = rewritten(lines[body_at], spelling, "(" + spelling + ")")
        elif kind in ("place", "width"):
            if struct_at < 0:
                return ""
            lines[body_at] = rewritten(lines[body_at], spelling, "p->" + name)
            lines[struct_at] = with_field(lines[struct_at], holder, name, kind == "width")
        elif kind in PLACE_FORMS:
            if struct_at < 0:
                return ""
            if branch_trees.place_and_form(lines[body_at], lines[struct_at], name)[0] == kind:
                # already in this place: run tlp1_l10 wrote `p->a[0][1][0][1]`
                # from a base whose part 0 was a matrix element
                continue
            placed_holder = place_holder(kind, holder)
            lines[body_at], lines[struct_at] = placed(lines[body_at], lines[struct_at], spelling, name, kind,
                                                      placed_holder)
            declarations = declarations + place_declarations(kind, name, target_of(base), placed_holder)
    lines = with_declarations(lines, struct_at, declarations)
    changed = "\n".join(lines)
    if changed == text:
        return ""
    return changed


def place_holder(kind: str, holder: str) -> str:
    """The holder a part is written with in a place form (PCHQ log 503 §2,
    line 16): its own holder when it fits the place (a pointer or an
    integer of at most 8 bytes in a global register, a signed integer in a
    signed bit-field), the vector or matrix whose element it is for an
    element place; the form's own holder (PLACE_FORMS) otherwise. Until
    2026-10-22 the form's own holder always."""
    writer = branch_writer()
    if kind in branch_trees.ELEMENT_HOLDERS:
        element = branch_trees.ELEMENT_OF.get(holder, holder)
        kept = branch_trees.ELEMENT_HOLDERS[kind].get(element)
        if kept:
            return kept
        return PLACE_FORMS[kind][0]
    if branch_trees.fits(holder, kind, writer.held_facts):
        return holder
    return PLACE_FORMS[kind][0]


def placed(body: str, struct: str, spelling: str, name: str, kind: str, holder: str) -> tuple:
    """op_k's line reading the part as the place form says, and P_k's line
    holding it in the form's field with the part's holder (a global register
    has no field: P_k's line stays); a signed bit-field no wider than its
    holder (branch_trees.width_of)."""
    form_holder, field, read = PLACE_FORMS[kind]
    body = rewritten(body, spelling, read.format(name=name))
    if kind == "signed bit-field":
        field = "{holder} {name} : " + str(branch_trees.width_of(holder, branch_writer())) + ";"
    if field:
        struct = with_field_text(struct, name, field.format(holder=holder, name=name))
    found = (body, struct)
    return found


def place_declarations(kind: str, name: str, target: str, holder: str) -> list:
    """What the place form declares before P_k (PLACE_DECLARATIONS), with
    the part's holder and name and the architecture's register filled in
    (`register int *reg_k_a __asm__("sp");`)."""
    declarations = []
    if kind not in PLACE_DECLARATIONS:
        return declarations
    if kind == "global register":
        declarations.append(branch_trees.register_declaration(holder, name, target))
        return declarations
    register = GLOBAL_REGISTERS.get(target, GLOBAL_REGISTERS[BASE_TARGET[0]])
    for line in PLACE_DECLARATIONS[kind][0]:
        line = line.replace("{holder}", holder).replace("{name}", name).replace("{register}", register)
        declarations.append(line)
    return declarations


def with_declarations(lines: list, struct_at: int, declarations: list) -> list:
    """The program's lines with the declarations a place form needs just
    before P_k, each once (a matrix type the base already declares is kept as
    it is)."""
    if struct_at < 0 or not declarations:
        return lines
    added = []
    for line in declarations:
        if line not in lines and line not in added:
            added.append(line)
    found = lines[:struct_at] + added + lines[struct_at:]
    return found


def index_of_line(lines: list, start: str) -> int:
    for index in range(len(lines)):
        if start in lines[index]:
            return index
    return -1


def slots_of_operator(operator) -> tuple:
    from PseudoIR.map_HiOp_to_unit.lower_HiOp.standard_HiOp_wrapper import slots_of
    slots = slots_of(operator)
    return slots


def spelling_in(body: str, name: str) -> str:
    """How the standard form writes the part in op_k: a field, `p->a`, or an
    inert part held as a call, `part_k_a()`."""
    for spelling in ("p->" + name, "part_" + KEY + "_" + name + "()"):
        if re.search(re.escape(spelling) + r"(?!\w)", body):
            return spelling
    return ""


def rewritten(body: str, spelling: str, new: str) -> str:
    """The body with the part's spelling replaced, past the `p->result =`."""
    marker = "p->result = "
    at = body.find(marker)
    head = ""
    tail = body
    if at >= 0:
        head = body[:at + len(marker)]
        tail = body[at + len(marker):]
    # the new text given as a function, so re.sub reads no backslash in it
    tail = re.sub(re.escape(spelling) + r"(?!\w)", lambda found: new, tail, count=1)
    text = head + tail
    return text


def with_field(struct: str, holder: str, name: str, width: bool) -> str:
    """P_k's line with the part as a field (`int a;`), a bit-field of WIDTH
    bits when a width is read (`int a : 13;`)."""
    field = f"{holder} {name};"
    if width:
        field = f"{holder} {name} : {WIDTH};"
    text = with_field_text(struct, name, field)
    return text


def with_field_text(struct: str, name: str, field: str) -> str:
    """P_k's line with the part's field replaced by `field` (a plain field or
    a bit-field, `b : 13;`, since 2026-10-21: before, a base whose part was a
    bit-field got a second field of the same name), or added first."""
    plain = re.search(r"(?<=[{;]) ?[^;{}]*\b" + re.escape(name) + r"(?:\s*:\s*\d+)?;", struct)
    if plain:
        text = struct[:plain.start()] + " " + field + struct[plain.end():]
        return text
    opening = "struct P_" + KEY + " { "
    text = struct.replace(opening, opening + field + " ", 1)
    return text


def with_new(candidates: list, written: list, contexts: list) -> list:
    """The round's candidates with the written ones not traced before."""
    known = set()
    for context in contexts + candidates:
        known.add(check.key_of(context))
    kept = list(candidates)
    for candidate in written:
        key = check.key_of(candidate)
        if key not in known:
            kept.append(candidate)
            known.add(key)
    return kept


# ---------------------------------------------------------------------------
# 7 trace_and_check: the owner's method on the candidates, and their lines

def trace_and_check(key: str, candidates: list, binary: dict, earlier: list, first: int) -> dict:
    """The candidates traced (check_trace_logical_paths.run_all), the five
    checks on every candidate of the operator so far (analyze), and the lines
    of clang's code each ran. One compile of each candidate gives both its
    path and its lines (PCHQ Gemini copy, log 493 §4, line 2): run_all hands
    each record to the lines step (trace_lines_on_the_paths.lines_of_trace),
    which finds the path's checking and lowering functions anew from it, so a
    function a candidate enters first is read."""
    check.say(f"[{key}] tracing {len(candidates)} candidates")
    warm_blocks(binary)
    results = check.run_all(candidates, binary["clang"], binary["names"], binary["recording"], binary["work"],
                            lines_of=lines_run_of_paths.lines_of_trace)
    lines = lines_of_results(key, candidates, results, first)
    every = renumbered(earlier + results)
    results_by_context = {}
    paths = []
    for result in every:
        results_by_context[check.key_of(result["path"].context)] = result
        paths.append(result["path"])
    analysis = check.analyze(key, paths, results_by_context, binary["path"], binary["names"], binary["work"], False)
    traced = {"results": results, "every": every, "analysis": analysis, "lines": lines}
    return traced


def warm_blocks(binary: dict) -> None:
    """The blocks the loop has read (binary["cache"], filled by
    unreached_branches) handed to the lines step's cache before run_all's
    workers fork, so no worker reads again a function's listing the loop has
    read once."""
    cache = lines_run_of_paths.STATE.setdefault("blocks_by_function", {})
    for function, found in binary["cache"].items():
        if function not in cache:
            cache[function] = found[0]


def lines_of_results(key: str, candidates: list, results: list, first: int) -> list:
    """The lines of each candidate in the lines run's form (trace_one's),
    numbered after the operator's earlier candidates, taken out of run_all's
    results (each candidate's place in `results` is its place in
    `candidates`: run_all returns them in order)."""
    found = []
    for number in range(len(results)):
        result = results[number]
        line_result = {"key": key, "path": first + number, "contexts": 1}
        line_result.update(result.pop("lines_of_path"))
        line_result["context"] = candidates[number]
        found.append(line_result)
    return found


def renumbered(results: list) -> list:
    for number in range(len(results)):
        results[number]["number"] = number
    return results


# ---------------------------------------------------------------------------
# 1 and 8: the record

class Record:
    """What is known and what this run adds: the contexts traced so far (the
    lines records' paths), every branch with its outcome (branch_candidates.json),
    the candidates' paths (paths.json) and lines (lines.json), under OUT; and
    every lines record's lines by function and operator (`everywhere`), so a
    branch some context of any operator ran is taken."""

    def __init__(self, out: str, binary: dict, keys: list, everywhere: dict, resume: bool):
        self.out = out
        self.keys = keys
        self.everywhere = everywhere
        self.started = time.time()
        self.last_write = 0.0
        self.branches = {"clang": binary["path"], "setup": our_setup().command, "in_hiop": bool(STATE.get("in_hiop")),
                         "operators": {}, "progress": {"operators_done": 0, "operators": len(keys), "seconds": 0}}
        self.paths = {"clang": binary["path"], "setup": our_setup().command, "operators": {}}
        self.lines = {"clang": binary["path"], "setup": our_setup().command, "small": False, "functions": {},
                      "operators": {}, "progress": {"paths_done": 0, "paths": 0, "seconds": 0}}
        self.results = {}
        self.candidates = {}
        self.resumed = {}
        if resume:
            self.resume()

    def resume(self) -> None:
        """--resume: the record already in OUT read back; each operator's
        candidates (lines.json's paths, with their holders, setup and
        program) are traced again for the checks when its loop goes on."""
        branches = read_json(os.path.join(self.out, "branch_candidates.json"))
        if branches is None:
            check.say(f"[resume] no branch_candidates.json in {self.out}: a new record")
            return
        self.branches["operators"] = branches["operators"]
        paths = read_json(os.path.join(self.out, "paths.json"))
        if paths is not None:
            self.paths["operators"] = paths["operators"]
        lines = read_json(os.path.join(self.out, "lines.json"))
        if lines is not None:
            self.lines["functions"] = lines["functions"]
            self.lines["operators"] = lines["operators"]
        for key, entry in self.lines["operators"].items():
            self.resumed[key] = resumed_candidates(key, entry, self.candidates.setdefault(key, {}))
        done = 0
        for entry in self.branches["operators"].values():
            if entry.get("done"):
                done += 1
        check.say(f"[resume] {len(self.branches['operators'])} operators in the record, {done} done")

    def contexts(self, key: str, lines: dict) -> list:
        """Block A's line 1: the contexts traced so far, with their lines."""
        found = []
        for path in lines.get(key, []):
            if path["context"] is not None:
                found.append(path["context"])
        return found

    def operator_entry(self, key: str) -> dict:
        if key not in self.branches["operators"]:
            self.branches["operators"][key] = {"rounds": 0, "done": False, "branches": {}, "counts": {}}
        entry = self.branches["operators"][key]
        return entry

    def rounds_done(self, key: str) -> int:
        rounds = self.operator_entry(key)["rounds"]
        return rounds

    def is_done(self, key: str) -> bool:
        entry = self.branches["operators"].get(key, {})
        done = bool(entry.get("done"))
        return done

    def finish(self, key: str) -> None:
        entry = self.operator_entry(key)
        entry["done"] = True
        close_inside(entry)
        entry["counts"] = counts_of(entry["branches"])

    def has_branch(self, branch: dict) -> bool:
        entry = self.branches["operators"].get(branch["key"], {"branches": {}})
        found = branch["id"] in entry["branches"]
        return found

    def results_of(self, key: str, binary: dict) -> list:
        """The operator's candidates traced so far; after a resume, the
        recorded candidates are traced again here, once, for the checks."""
        if key in self.results or not self.resumed.get(key):
            found = self.results.get(key, [])
            return found
        check.say(f"[{key}] {len(self.resumed[key])} candidates of the record traced again for the checks")
        found = check.run_all(self.resumed[key], binary["clang"], binary["names"], binary["recording"],
                              binary["work"])
        self.results[key] = found
        return found

    def paths_written(self, key: str) -> int:
        """How many paths of the operator lines.json holds: the next
        candidate's number."""
        count = len(self.lines["operators"].get(key, {"paths": []})["paths"])
        return count

    def close(self, key: str, branch: dict, condition: dict, change: dict, round_number: int) -> None:
        """A branch the method does not trace a candidate for: closed with its
        reason, or open (unless another operator's contexts ran it)."""
        entry = self.operator_entry(key)
        shown = branch_record(branch, condition, change, [], round_number)
        shown["outcome"] = change["outcome"]
        shown["why"] = change["why"]
        if shown["outcome"] == "open":
            taken_elsewhere(shown, self.everywhere)
        entry["branches"][branch["id"]] = shown

    def add(self, key: str, tried: list, traced, lines: dict, round_number: int) -> None:
        """Block A's line 8: the candidates' paths and lines into the record,
        the lines into `lines` (the next round sees the blocks they ran), and
        each tried branch's outcome read from the lines."""
        entry = self.operator_entry(key)
        entry["rounds"] = round_number
        if traced is not None:
            self.results[key] = traced["every"]
            self.paths["operators"][key] = traced["analysis"]
            self.add_lines(key, traced["lines"], lines)
        for branch, condition, change, written in tried:
            entry["branches"][branch["id"]] = branch_record(branch, condition, change, self.numbered(key, written),
                                                     round_number)
        settle_branches(entry, lines.get(key, []), self.everywhere)

    def numbered(self, key: str, written: list) -> list:
        """The candidates with the number their path has in lines.json."""
        numbers = self.candidates.setdefault(key, {})
        found = []
        for candidate in written:
            number = numbers.get(check.key_of(candidate))
            found.append((number, candidate))
        return found

    def add_lines(self, key: str, results: list, lines: dict) -> None:
        numbers = self.candidates.setdefault(key, {})
        for result in results:
            context = result_context(result)
            lines_run_of_paths.add_result(self.lines, result)
            if target_of(context) != BASE_TARGET[0]:
                drop_non_base_function_lines(self.lines, result)
            path = self.lines["operators"][key]["paths"][-1]
            path["holders"] = list(context.holders)
            path["setup"] = context.setup.command
            path["preamble"] = list(context.setup.preamble)
            path["program"] = context.program
            numbers[check.key_of(context)] = result["path"]
            lines.setdefault(key, []).append(lines_path(path, context, os.path.basename(self.out)))
            add_everywhere(self.everywhere, key, path)

    def write(self, force: bool = False) -> None:
        now = time.time()
        if not force and len(self.keys) > 64 and now - self.last_write < 30.0:
            return
        self.last_write = now
        seconds = now - self.started
        done = 0
        for key in self.keys:
            if self.is_done(key):
                done += 1
        self.branches["progress"] = {"operators_done": done, "operators": len(self.keys), "seconds": seconds}
        paths_done = 0
        for entry in self.lines["operators"].values():
            paths_done += len(entry["paths"])
        self.lines["progress"] = {"paths_done": paths_done, "paths": paths_done, "seconds": seconds}
        for entry in self.branches["operators"].values():
            if not entry.get("done") or "counts" not in entry or not entry["counts"] and entry["branches"]:
                close_inside(entry)
                entry["counts"] = counts_of(entry["branches"])
        write_json(self.branches, os.path.join(self.out, "branch_candidates.json"))
        write_json(self.paths, os.path.join(self.out, "paths.json"))
        write_json(self.lines, os.path.join(self.out, "lines.json"))


def read_json(path: str):
    if not os.path.exists(path):
        return None
    with open(path, encoding="utf-8") as read:
        data = json.load(read)
    return data


def resumed_candidates(key: str, entry: dict, numbers: dict) -> list:
    """The candidates of one operator's lines.json paths, numbered as there."""
    operator = operator_of(key)
    found = []
    if operator is None:
        return found
    for path in entry["paths"]:
        if "holders" not in path:
            continue
        setup = Setup(path["setup"], tuple(path.get("preamble", ())))
        context = Context(operator, tuple(path["holders"]), setup, path.get("program", ""))
        numbers[check.key_of(context)] = path["path"]
        found.append(context)
    return found


def result_context(result: dict):
    """The candidate a lines result was traced for (lines_of_results)."""
    context = result["context"]
    return context


def branch_record(branch: dict, condition: dict, change: dict, candidates: list, round_number: int) -> dict:
    """One branch as branch_candidates.json holds it. `ran_by` names each path
    by its lines record and its number there, as `taken_by` does: the context
    itself is in that record (2026-10-21: written whole on every branch, it
    was two thirds of the record, 1.6 MB an operator)."""
    ran_by = []
    for path in branch["ran_by"][:RAN_BY_KEPT]:
        ran_by.append({"run": path["run"], "path": path["path"]})
    shown = []
    for number, candidate in candidates:
        shown.append(candidate_record(number, candidate))
    kinds = []
    for kind, name in condition["kinds"]:
        kinds.append(f"{kind}: {name}")
    closing = None
    if change["closing"] is not None:
        closing = {"outcome": change["closing"][0], "why": change["closing"][1]}
    block, inside = inside_of_branch(branch)
    record = {"operator": branch["key"], "function": branch["function"], "file": branch["file"], "test": branch["test"], "first": branch["first"],
              "lines": branch["lines"], "condition": condition["text"], "statement": condition["statement"],
              "cases": condition["cases"], "kinds": kinds, "change": changes_shown(change),
              "closing": closing, "ran_by": ran_by, "candidates": shown, "round": round_number,
              "outcome": "open", "why": "", "taken_by": [], "targets": [], "block": block, "inside": inside}
    return record


# ---------------------------------------------------------------------------
# 2026-10-21, the owner: "if it runs on it next, run it". What lies inside a branch
# closed as not needed or cannot reach takes that branch's closing: a branch
# whose test lies in the block the closed branch's test guards, and the
# block's lines of code no branch holds (a test inside an untaken block never
# ran, so it is no branch of its own: CGExpr.cpp 2281 inside 2279's
# Objective-C block, and its lines 2282 to 2288).

# How far a guarded block is read below its test.
BLOCK_REACH = 400


def inside_of_branch(branch: dict) -> tuple:
    """([first, last] line of the block the branch's `if` guards, the lines of
    code in it after the branch's own lines that the operator's paths did not
    run); ([], []) when the untaken block is not that guarded block (the
    branch after an `if`, an `else`, a `switch`'s case)."""
    source = source_lines(branch["file"])
    start, end = guarded_block(source, branch["test"])
    if not start or not start < branch["first"] <= end or (branch["first"] == end and code_of(text_at(source, end)) == "}"):
        found = ([], [])
        return found
    code = branch.get("code", {}).get(branch["file"], set())
    ran = branch.get("ran", set())
    inside = []
    for line in sorted(code):
        if start < line <= end and line not in branch["lines"] and line not in ran:
            inside.append(line)
    found = ([start, end], inside)
    return found


def guarded_block(source: list, test: int) -> tuple:
    """(the `if`'s first line, the last line of the body it guards): the
    closing brace that matches the body's opening one, or the line ending
    the body's one statement; (0, 0) when the test is no `if`."""
    start = test
    while start > 1 and test - start < STATEMENT_REACH:
        if not continues_above(text_at(source, start - 1), text_at(source, start)):
            break
        start -= 1
    if not starts_test(text_at(source, start)):
        found = (0, 0)
        return found
    end = block_end(source, start)
    found = (start, end)
    return found


def block_end(source: list, start: int) -> int:
    """The line the body of the `if` on line `start` ends on (0 if not found
    within BLOCK_REACH)."""
    depth = 0
    opened = False
    for line in range(start, min(len(source), start + BLOCK_REACH) + 1):
        text = code_of(text_at(source, line))
        if line == start and text.startswith("}"):
            text = text[1:]
        for character in text:
            if character == "{":
                depth += 1
                opened = True
            elif character == "}":
                depth -= 1
            if opened and depth == 0:
                return line
        if not opened and line > start and text.endswith(";"):
            return line
    return 0


def code_of(text: str) -> str:
    """A line of C++ without its comment and its string and character
    literals, so a brace in them is not counted."""
    text = re.sub(r'"(?:\\.|[^"\\])*"', '""', text)
    text = re.sub(r"'(?:\\.|[^'\\])*'", "''", text)
    at = text.find("//")
    if at >= 0:
        text = text[:at]
    text = text.strip()
    return text


def close_inside(entry: dict) -> None:
    """Each closed branch's closing given to what lies inside it: an open branch
    whose test lies in its block, and its lines of code no branch holds, as a
    record of their own (`<branch> inside`), so the page labels them. The
    records of the lines are made again at every write, from the branches as
    they stand."""
    branches = entry["branches"]
    for name in list(branches):
        if branches[name].get("inside_of"):
            del branches[name]
    held = lines_held(branches)
    for name in list(branches):
        branch = branches[name]
        if branch["outcome"] not in ("not needed", "cannot reach") or not branch.get("block"):
            continue
        close_branches_inside(branches, branch)
        inside = []
        for line in branch.get("inside", []):
            if line not in held.get(branch["function"], set()):
                inside.append(line)
        if inside:
            branches[name + " inside"] = record_of_lines_inside(name, branch, inside)


def lines_held(branches: dict) -> dict:
    """function -> the lines some branch holds."""
    held = {}
    for branch in branches.values():
        found = held.setdefault(branch["function"], set())
        for line in branch["lines"]:
            found.add(line)
    return held


def why_inside(branch: dict) -> str:
    why = "inside a branch closed as " + branch["outcome"]
    if branch["why"]:
        why = why + ": " + branch["why"]
    return why


def close_branches_inside(branches: dict, closed: dict) -> None:
    """An open branch of the same function that lies in the closed branch's
    block takes its closing: its test is in the block, or every line of its
    untaken block is (SemaChecking.cpp 4310 to 4339, the cases of a `switch
    (Form)` inside 4308's `if (ArgOrder == Sema::AtomicArgumentOrder::AST)`,
    which the switches at 3998, 4356 and 4423 share in the binary)."""
    start, end = closed["block"]
    for branch in branches.values():
        if branch is closed or branch["function"] != closed["function"] or branch["outcome"] != "open":
            continue
        if start < branch["test"] <= end or lines_inside(branch["lines"], start, end):
            branch["outcome"] = closed["outcome"]
            branch["why"] = why_inside(closed)


def lines_inside(lines: list, start: int, end: int) -> bool:
    """Whether every one of the lines lies after `start` and up to `end`."""
    if not lines:
        return False
    for line in lines:
        if not start < line <= end:
            return False
    return True


def record_of_lines_inside(name: str, closed: dict, inside: list) -> dict:
    """The lines inside a closed branch, as branch_candidates.json holds a branch:
    the closed branch's function, file and test, its closing, and these lines."""
    record = dict(closed)
    record["first"] = inside[0]
    record["lines"] = inside
    record["inside"] = []
    record["candidates"] = []
    record["taken_by"] = []
    record["targets"] = []
    record["why"] = why_inside(closed)
    record["inside_of"] = name
    return record


def changes_shown(change: dict) -> list:
    shown = []
    for alternative in change["alternatives"]:
        if alternative["kind"] == "unlocked":
            shown.append(f"unlocked in {alternative['function']}: the chain {alternative['chain']}, "
                         f"{alternative['candidates']} candidates")
        elif alternative["kind"] == "holder":
            shown.append(f"{alternative['name']}: parts {alternative['parts']} as {alternative['holders']}")
        elif alternative["kind"] == "option":
            shown.append(f"{alternative['name']}: {alternative['option']}, holders {alternative['holders']}")
        elif alternative["kind"] == "target":
            shown.append(f"{alternative['name']}: --target={alternative['triple']}")
        elif alternative["kind"] in PLACE_FORMS:
            shown.append(f"{alternative['kind']}: parts {alternative['parts']} as a {alternative['kind']}")
        elif len(alternative["parts"]) == 1:
            shown.append(f"{alternative['kind']}: part {alternative['parts'][0]} as {alternative['value']}")
        else:
            shown.append(f"{alternative['kind']}: parts {alternative['parts']} as {alternative['value']}")
    return shown


def candidate_record(number, context) -> dict:
    """A context as the record shows it: its holders, its program's own lines
    (those after the standard preamble, the struct and op_k), its setup."""
    own = []
    if context.program:
        for line in context.program.split("\n"):
            if line.startswith("struct P_" + KEY) or line.startswith("void op_" + KEY) or line.startswith("__typeof__"):
                own.append(line)
            elif line.startswith("register ") or line in MATRIX_TYPES:
                # a place form's declaration (PLACE_DECLARATIONS), 2026-10-21
                own.append(line)
    record = {"path": number, "holders": list(context.holders), "program": own, "setup": context.setup.command,
              "preamble": list(context.setup.preamble)}
    return record


def settle_branches(entry: dict, paths: list, everywhere: dict) -> None:
    """Each branch's outcome from the lines now known: taken when a path runs
    every line of its block; a branch a candidate was traced for and missed is
    open, or closed by the closing name its condition also reads; an open
    branch some context of any operator ran is taken (taken_elsewhere)."""
    for name, branch in entry["branches"].items():
        taken_by, targets = paths_taking(branch, paths)
        branch["targets"] = targets
        if BASE_TARGET[0] in targets:
            branch["outcome"] = "taken"
            branch["why"] = ""
            branch["taken_by"] = taken_by
            continue
        if targets:
            branch["outcome"] = "not needed"
            branch["why"] = "not on all three architectures: taken on " + ", ".join(targets)
            branch["taken_by"] = taken_by
            continue
        if branch["candidates"]:
            branch["outcome"] = "open"
            branch["why"] = "the candidates traced did not take it"
            if branch["closing"] is not None:
                branch["outcome"] = branch["closing"]["outcome"]
                branch["why"] = branch["closing"]["why"] + "; the candidates traced did not take it"
        if branch["outcome"] == "open":
            taken_elsewhere(branch, everywhere)
        if branch["outcome"] == "open" and traced_on_the_other_targets(branch):
            branch["outcome"] = "not needed"
            branch["why"] = TAKEN_ON_NO_TARGET
            branch["targets"] = []


# the owner, 2026-10-21, 05:50 UTC, on a branch whose test reads the target and that
# no target takes (l190: isPPC64, isWasm, X86_VectorCall,
# areArgsDestroyedLeftToRightInCallee, useFP16ConversionIntrinsics twice,
# EmitCall 5490): "correct."
TAKEN_ON_NO_TARGET = "not on all three architectures: taken on none of riscv64, x86-64, aarch64"


def traced_on_the_other_targets(branch: dict) -> bool:
    """Whether the branch's candidates include its base on each of the other
    two architectures (target_alternatives): with riscv64's own contexts,
    every one of the three was traced. A candidate the record numbers None
    was traced before (a context already known), so it counts."""
    traced = set()
    for candidate in branch["candidates"]:
        found = TARGET_OPTION.search(candidate["setup"])
        if found is not None:
            traced.add(found.group(1))
    for target, triple in OTHER_TARGETS:
        if triple not in traced:
            return False
    return True


def taken_elsewhere(branch: dict, everywhere: dict) -> bool:
    """the owner, 2026-10-20 (run l159 read): a branch any run took is taken. The
    branch's block is run when every one of its lines was run by some context
    of one operator, in any lines record (the clang's-code page's
    merged_lines() merges the same records); the dispatches on the
    expression's kind (`switch (E->getStmtClass())`) are settled so."""
    for key, ran in everywhere.get(branch["function"], {}).items():
        every = True
        for line in branch["lines"]:
            if line not in ran:
                every = False
                break
        if not every:
            continue
        branch["outcome"] = "taken"
        branch["why"] = "by another operator's contexts"
        if key == branch.get("operator", ""):
            branch["why"] = "by this operator's contexts in another lines record"
        branch["taken_by"] = [{"operator": key}]
        return True
    return False


def add_everywhere(everywhere: dict, key: str, path: dict) -> None:
    """One path's lines into `everywhere`: function -> operator -> lines run;
    a path compiled for another target than riscv64 is left out, so a branch
    the union takes is taken on riscv64."""
    found = TARGET_OPTION.search(path.get("setup", ""))
    if found is not None and found.group(1) != BASE_TARGET[1]:
        return
    for function, numbers in path["lines"].items():
        by_operator = everywhere.setdefault(function, {})
        ran = by_operator.setdefault(key, set())
        for number in numbers:
            ran.add(number)


def drop_non_base_function_lines(record: dict, result: dict) -> None:
    """Removes a non-riscv64 path's line counts from record['functions'] so
    only riscv64 paths count as covered lines on riscv64."""
    for function, ran in result["lines"].items():
        entry = record["functions"].get(function)
        if entry is None:
            continue
        entry["paths"] -= 1
        entry["contexts"] -= result["contexts"]
        for line in ran["lines"]:
            key = str(line)
            left = entry["lines"].get(key, 0) - result["contexts"]
            if left > 0:
                entry["lines"][key] = left
            elif key in entry["lines"]:
                del entry["lines"][key]


def paths_taking(branch: dict, paths: list) -> tuple:
    """(the paths that run every line of the branch's block, the architectures
    they were compiled for, of the three)."""
    wanted = branch["lines"]
    taking = []
    targets = []
    for path in paths:
        ran = path["lines"].get(branch["function"], set())
        every = True
        for line in wanted:
            if line not in ran:
                every = False
                break
        if not every:
            continue
        target = BASE_TARGET[0]
        if path["context"] is not None:
            target = target_of(path["context"])
        if target not in targets:
            targets.append(target)
        if path["context"] is None:
            taking.append({"run": path["run"], "path": path["path"]})
            continue
        taking.append(candidate_record(path["path"], path["context"]))
    found = (taking, targets)
    return found


def counts_of(branches: dict) -> dict:
    counts = {}
    for branch in branches.values():
        counts[branch["outcome"]] = counts.get(branch["outcome"], 0) + 1
    return counts


def write_json(data: dict, path: str) -> None:
    """Written whole or not at all: beside, then put in place."""
    beside = path + ".writing"
    with open(beside, "w", encoding="utf-8") as written:
        json.dump(data, written, default=list)
        written.write("\n")
    os.replace(beside, path)


# ---------------------------------------------------------------------------
# the lines records, merged, with the context each path is

def records_of_the_pruned_binary() -> set:
    """The lines records made with fable1's first traced clang (no `no-prune`:
    a block with no recorder lumps its lines with a neighbour's; log 489 §16),
    listed in lines_records_of_the_pruned_binary_2026-10-20.txt; skipped."""
    names = set()
    path = os.path.join(HERE, "lines_records_of_the_pruned_binary_2026-10-20.txt")
    if not os.path.exists(path):
        return names
    with open(path, encoding="utf-8") as read:
        for line in read:
            name = line.strip()
            if name and not name.startswith("#"):
                names.add(name)
    return names


# The run folders that hold records: fable1's (logs 487 to 489) and, from
# 2026-10-21, those of tlp1, the instance that runs this copy's code (log 493
# §4, line 7).
RUN_FOLDERS = ("fable1_*", "tlp1_*")


def records_named(name: str) -> list:
    """Every run folder's file of this name."""
    found = []
    for folder in RUN_FOLDERS:
        for file in glob.glob(os.path.join(HERE, folder, name)):
            found.append(file)
    return found


def lines_records() -> list:
    """Every lines run's lines.json, oldest first (the clang's-code page's
    order), the pruned binary's records left out."""
    skipped = records_of_the_pruned_binary()
    files = []
    for file in records_named("lines.json"):
        if os.path.basename(os.path.dirname(file)) in skipped:
            continue
        files.append(file)
    files.sort(key=os.path.getmtime)
    return files


def paths_records(before: float) -> list:
    """The brute force's paths.json records older than `before`, oldest
    first, without the by-hand ones (the lines run's rule)."""
    files = records_named("paths.json")
    kept = []
    for file in files:
        if os.path.getmtime(file) < before and not lines_run_of_paths.is_by_hand(file):
            kept.append(file)
    kept.sort(key=os.path.getmtime)
    return kept


def lines_of(keys: list, lines_files: list, everywhere: dict) -> dict:
    """key -> paths: every lines record's paths of the operators, each with
    its lines per function (sets), its checking and lowering functions, and
    its context: the holders the record of its time gave the path (a lines
    record's path N is variant N of the latest paths.json before it), or the
    holders, setup and program a lines record of this step wrote beside it."""
    records = []
    started = time.time()
    for number in range(len(lines_files)):
        file = lines_files[number]
        tick("[lines] reading the lines records", number, len(lines_files), started)
        records.append(lines_record_of(file, keys, everywhere))
    paths_files = paths_records(needs_paths_before(records))
    check.say(f"[lines] {len(lines_files)} lines records; {len(paths_files)} paths records older than them")
    known = known_paths(keys, paths_files)
    lines = {}
    for record in records:
        add_lines_record(lines, record, known)
    return lines


def lines_record_of(file: str, keys: list, everywhere: dict) -> dict:
    """One lines record's paths of the operators, with its folder and time;
    every operator's lines into `everywhere`."""
    with open(file, encoding="utf-8") as read:
        data = json.load(read)
    for key, entry in data.get("operators", {}).items():
        for path in entry["paths"]:
            add_everywhere(everywhere, key, path)
    kept = {}
    for key in keys:
        entry = data.get("operators", {}).get(key)
        if entry is not None:
            kept[key] = entry
    record = {"folder": os.path.basename(os.path.dirname(file)), "written": os.path.getmtime(file),
              "operators": kept}
    return record


def needs_paths_before(records: list) -> float:
    """The time of the newest lines record whose paths name no holders (this
    step's own records name them)."""
    newest = 0.0
    for record in records:
        for entry in record["operators"].values():
            for path in entry["paths"]:
                if "holders" not in path:
                    newest = max(newest, record["written"])
    return newest


def known_paths(keys: list, files: list) -> dict:
    """key -> [(time, the holder sets of each variant)], from every paths
    record that holds the key (a record is parsed only when its text names
    one of the keys)."""
    known = {}
    started = time.time()
    keys_set = set(keys)
    for number in range(len(files)):
        file = files[number]
        tick("[paths] reading the paths records", number, len(files), started)
        if len(keys) <= 64:
            wanted = keys_in_file(file, keys)
            if not wanted:
                continue
        with open(file, encoding="utf-8") as read:
            data = json.load(read)
        operators = data.get("operators", {})
        if len(keys) > 64:
            wanted = [k for k in operators if k in keys_set]
        for key in wanted:
            entry = operators.get(key)
            if entry is None:
                continue
            variants = []
            for variant in entry["variants"]:
                variants.append(variant["contexts"])
            known.setdefault(key, []).append((os.path.getmtime(file), variants))
    return known


def keys_in_file(file: str, keys: list) -> list:
    with open(file, "rb") as read:
        text = read.read()
    found = []
    for key in keys:
        if json.dumps(key).encode("utf-8") + b": {" in text:
            found.append(key)
    return found


def add_lines_record(lines: dict, record: dict, known: dict) -> None:
    for key, entry in record["operators"].items():
        variants = matching_variants(known.get(key, []), entry["paths"], record["written"])
        operator = operator_of(key)
        for path in entry["paths"]:
            context = context_of_path(operator, path, variants)
            lines.setdefault(key, []).append(lines_path(path, context, record["folder"]))


def matching_variants(records: list, paths: list, written: float) -> list:
    """The variants of the latest paths record before the lines record whose
    variants have the lines record's counts of contexts."""
    for recorded, variants in reversed(records):
        if recorded >= written:
            continue
        if counts_match(variants, paths):
            return variants
    return []


def counts_match(variants: list, paths: list) -> bool:
    for path in paths:
        number = path["path"]
        if number >= len(variants) or len(variants[number]) != path["contexts"]:
            return False
    return True


def context_of_path(operator, path: dict, variants: list):
    if operator is None:
        return None
    if "holders" in path:
        setup = Setup(path["setup"], tuple(path.get("preamble", ())))
        context = Context(operator, tuple(path["holders"]), setup, path.get("program", ""))
        return context
    if path["path"] < len(variants) and variants[path["path"]]:
        holders = variants[path["path"]][0]
        if len(holders) == len(operator.operands):
            return Context(operator, tuple(holders), our_setup())
        like = Context(operator, (), our_setup())
        context = lines_run_of_paths.context_from_record(like, holders)
        return context
    return None


def lines_path(path: dict, context, folder: str) -> dict:
    ran = {}
    for function, numbers in path["lines"].items():
        ran[function] = set(numbers)
    found = {"run": folder, "path": path["path"], "contexts": path["contexts"], "checking": path["checking"],
             "lowering": path["lowering"], "lines": ran, "context": context, "accepted": path.get("accepted", True)}
    return found


# ---------------------------------------------------------------------------
# the operators, the pool, the binary

def key_for(operator) -> str:
    """The record's key of an operator (check.group_by_operator's rule)."""
    if STATE["counts_of_name"] is None:
        counts = {}
        for each in check.vocabulary_operators():
            counts.setdefault(each.name, set()).add(len(each.operands))
        STATE["counts_of_name"] = counts
    key = check.key_of_operator(operator, STATE["counts_of_name"])
    return key


def operator_of(key: str):
    if STATE["operators"] is None:
        operators = {}
        all_operators = {}
        for operator in check.vocabulary_operators():
            k = key_for(operator)
            if "template " not in operator.spelling:
                all_operators.setdefault(k, []).append(operator)
            if k.startswith("GenericSelectionExpr") and k in operators:
                continue
            if "template " in operator.spelling and k in operators:
                continue
            operators[k] = operator
        STATE["operators"] = operators
        STATE["all_operators"] = all_operators
    operator = STATE["operators"].get(key)
    return operator


def operators_of(key: str) -> list:
    if STATE.get("all_operators") is None:
        operator_of(key)
    found = STATE["all_operators"].get(key) or ([STATE["operators"][key]] if key in STATE["operators"] else [])
    return found


def keys_of(file: str) -> list:
    keys = []
    with open(file, encoding="utf-8") as read:
        for line in read:
            key = line.strip()
            if key and not key.startswith("#"):
                keys.append(key)
    return keys


def pool_of(file: str) -> set:
    """The holders clang accepts somewhere (§4.3); the table's own holders
    when the file is not on this machine, said."""
    pool = set()
    if not os.path.exists(file):
        check.say(f"[pool] {file} not found: the change table's holders are the pool")
        for predicate, true_holder, false_holder in CHANGE_FOR:
            pool.add(true_holder)
            pool.add(false_holder)
        return pool
    with open(file, encoding="utf-8") as read:
        data = json.load(read)
    for holder in data["holders"]:
        if holder.get("accepted"):
            pool.add(holder["spelling"])
    return pool


def binary_of(clang_dir: str, work: str) -> dict:
    """traced_clang: its wrapper, its binary, its functions' names, the
    recording that starts at the program's start, and the blocks read so far."""
    path = os.path.join(clang_dir, "bin", "clang.real")
    check.say("[names] the binary's functions, from its symbol table")
    names = names_of(path)
    recording = recording_of(path, names, work, True)
    binary = {"path": path, "clang": os.path.join(clang_dir, "bin", "clang"), "names": names,
              "recording": recording, "work": work, "cache": {}}
    lines_run_of_paths.set_state(binary["clang"], path, names, recording, work)
    return binary


def tick(what: str, done: int, total: int, started: float) -> None:
    """A line every SAY_EVERY seconds: the time (check.say), what is being
    done, how far, the pace."""
    now = time.time()
    if now - STATE["said"] < SAY_EVERY:
        return
    STATE["said"] = now
    spent = now - started
    pace = 0.0
    if spent > 0:
        pace = done / spent
    check.say(f"{what}: {done} of {total}, {spent:.0f} s, {pace:.2f} a second")


def each_operator(keys: list, record, lines: dict, binary: dict, pool: set, rounds: int) -> None:
    started = time.time()
    for number in range(len(keys)):
        key = keys[number]
        operator = operator_of(key)
        if operator is None:
            check.say(f"[{key}] not an operator of the vocabulary; skipped")
            continue
        if key not in lines:
            check.say(f"[{key}] no lines record holds it; skipped")
            continue
        if record.is_done(key):
            check.say(f"[{key}] done in the record already ({record.rounds_done(key)} rounds); skipped")
            continue
        enumerate_every_path(operator, record, lines, binary, pool, rounds)
        record.write()
        spent = time.time() - started
        counts = record.operator_entry(key)["counts"]
        check.say(f"[operators] {number + 1} of {len(keys)} done, {spent:.0f} s, "
                  f"{(number + 1) / max(spent, 1e-9) * 60:.2f} a minute; {key}: {counts}")


def arguments_of(words: list):
    words = list(words)
    resume = "--resume" in words
    if resume:
        words.remove("--resume")
    in_hiop = "--in-hiop" in words
    if in_hiop:
        words.remove("--in-hiop")
    STATE["in_hiop"] = in_hiop or bool(os.environ.get("PSEUDOIR_IN_HIOP"))
    rounds = ROUNDS
    if "--rounds" in words:
        at = words.index("--rounds")
        rounds = int(words[at + 1])
        del words[at:at + 2]
    keys = ""
    if "--keys" in words:
        at = words.index("--keys")
        keys = words[at + 1]
        del words[at:at + 2]
    if len(words) != 2 or not keys:
        return None
    found = {"clang_dir": words[0], "out": words[1], "keys": keys, "rounds": rounds, "resume": resume,
             "in_hiop": STATE["in_hiop"]}
    return found


def main() -> int:
    arguments = arguments_of(sys.argv[1:])
    if arguments is None:
        print(__doc__)
        return 2
    os.makedirs(arguments["out"], exist_ok=True)
    work = os.environ.get("TLP_WORK", "/work/enumerate_every_path")
    os.makedirs(work, exist_ok=True)
    keys = keys_of(arguments["keys"])
    binary = binary_of(arguments["clang_dir"], work)
    everywhere = {}
    lines = lines_of(keys, lines_records(), everywhere)
    check.say(f"[lines] {len(lines)} of {len(keys)} operators hold paths; {len(everywhere)} functions of clang's run")
    record = Record(arguments["out"], binary, keys, everywhere, arguments["resume"])
    pool = pool_of(HOLDERS_FILE)
    branch_writer(pool)
    each_operator(keys, record, lines, binary, pool, arguments["rounds"])
    record.write(force=True)
    check.say(f"[done] {record.branches['progress']}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
