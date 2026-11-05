"""accepted_signatures -- for each builtin with custom typechecking (clang's
list marks it `t`: "signature is meaningless, use custom typechecking"), the holders
each argument can take on a path clang's checking code accepts, tested
against the conditions checking_reader read on that path: the signatures
extract() tries for the builtin, each then judged by clang.

the owner, 2026-10-15: "is it not possible to use tree-sitter to identify where
these operator definitions start and end, and then extract all the accepted
signatures or the holders it processes? ... those holder list become the
possible variant to check if GNU-C accepts it." And 2026-10-16: "why would i
solve problems with the reader and not use those solutions in extract? ...
do it now."

    facts = holder_facts(domain, work)               # each holder as clang sees it
    for rule in read[builtin]["accepted"]:            # one accepting path's conditions
        for argument of the call:
            if a condition of the rule names the argument:
                candidates = [h for h in domain if the rule's conditions on it alone hold]
            else:
                candidates = the holders the grid crosses for the operator
        if the operator has at most two slots:        # as the grid: every holder kept, every combination
            signatures += [s for s in product(candidates) if the rule's conditions on two or more arguments hold]
        else:                                         # as the grid's small sets: fewer combinations
            signatures += [each candidate once, beside the first candidates of the other arguments that fit it]

The domain is the holders the grid keeps, and a pointer to each of them
(`domain_of`): a condition on what an argument points to (`pointee(type(arg0))`)
is met only by pointers, and the grid's own holders hold ten. A condition the
evaluator cannot decide is taken to hold, so the holder is tried and clang
decides; a condition the walk left unread is not in the rules at all
(checking_reader's `unread`).

The evaluator is compose's (`Research/extract_lang_vocabulary/complex_signature_reader/compose.py`,
, with the kinds of type C holds that compose's domain did not
(enums, _BitInt, structs, unions, complex numbers, arrays, functions), with
each argument also seen as C passes it (an array as a pointer to its first
element, an _Atomic as its value), and with each holder's facts read from
clang in the grid's own compile, where compose read the widths from clang's
TargetInfo and kept a table of its twenty basic holders.
"""

import itertools
import json
import os
import re
import subprocess
import time
from typing import NamedTuple, Optional

from ... import mask_maker as mask_code
from .. import Holder
from . import holder_reader

UNDECIDED = "undecided"


class Held(NamedTuple):
    """One holder as clang's checks see it: what kind of type it is, its sign,
    its size in bytes on the target, what it points to or holds (a pointer's
    pointee, an _Atomic's value, an array's, vector's or complex number's
    element), its qualifiers, a _BitInt's width, an array's or vector's
    length."""

    spelling: str
    kind: str
    signed: bool
    size: Optional[int]
    inner: object = None
    const: bool = False
    volatile: bool = False
    bits: int = 0
    count: int = 0


# ---- each holder's facts, as clang gives them in the grid's own compile ----

# The three declarations asked of clang for each spelling: the type, its size
# and its sign. The dump filter keeps the declarations whose names hold
# FACT_NAME.
FACT_NAME = "holder_fact_"
FACT_LINES = (
    "typedef __typeof__({spelling}) holder_fact_{number};",
    "char holder_fact_size_{number}[sizeof(holder_fact_{number})];",
    "char holder_fact_sign_{number}[((holder_fact_{number})-1 < (holder_fact_{number})0) + 1];",
)
# A type's inner types are asked in rounds: a pointer to a pointer to a
# holder needs three.
FACT_ROUNDS = 4
# clang's sugar: nodes that name a type another node under them is.
SUGAR = {"TypedefType", "ElaboratedType", "ParenType", "TypeOfType", "TypeOfExprType", "AttributedType",
         "MacroQualifiedType", "UsingType", "BTFTagAttributedType", "CountAttributedType", "AdjustedType",
         "DecayedType"}
# The kinds of the nodes clang writes for a type that is not sugar, and the
# kind each is here.
NODE_KINDS = {"PointerType": "pointer", "ConstantArrayType": "array", "VectorType": "vector",
              "ExtVectorType": "extvector", "ComplexType": "complex", "AtomicType": "atomic",
              "EnumType": "enum", "BitIntType": "bitint", "FunctionProtoType": "function",
              "FunctionNoProtoType": "function"}
# The types clang's checking code names by its context's members
# (`Context.IntTy`), as C spells them.
CONTEXT_TYPES = {"IntTy": "int", "UnsignedIntTy": "unsigned int", "LongTy": "long", "UnsignedLongTy": "unsigned long",
                 "LongLongTy": "long long", "UnsignedLongLongTy": "unsigned long long", "DoubleTy": "double",
                 "FloatTy": "float", "BoolTy": "_Bool", "CharTy": "char", "ShortTy": "short",
                 "LongDoubleTy": "long double", "SizeType": "unsigned long", "getSizeType()": "unsigned long",
                 "VoidPtrTy": "void *", "VoidTy": "void"}


def builtin_kinds() -> dict:
    """spelling -> kind, for clang's builtin types: `bool` from Bool, an
    integer for the kinds after Bool up to Int128, a floating type from Half
    to Ibm128, `void` for Void, in the order clang's BuiltinType::Kind
    declares them (holder_reader), which is the order clang's own tests read
    (Type.h: isIntegerType is Bool <= kind <= Int128)."""
    holders = holder_reader.read_holders("c")
    names = []
    for holder in holders:
        names.append(holder.name)
    first_integer = names.index("Bool")
    last_integer = names.index("Int128")
    first_floating = names.index("Half")
    last_floating = names.index("Ibm128")
    kinds = {}
    for position, holder in enumerate(holders):
        kind = "builtin_other"
        if holder.name == "Void":
            kind = "void"
        elif holder.name == "Bool":
            kind = "bool"
        elif first_integer < position <= last_integer:
            kind = "integer"
        elif first_floating <= position <= last_floating:
            kind = "floating"
        kinds.setdefault(holder.spelling, kind)
    return kinds


def holder_facts(spellings: list, directory: str, preamble: tuple = ()) -> dict:
    """spelling -> Held, for each spelling and every type it points to or
    holds, read from clang's syntax tree in the grid's own compile
    (DRY_mask_maker.JUDGE_COMMAND): each type declared once, with its size
    and its sign; `preamble`, the declarations a spelling outside the
    grid's preamble needs (the trace loop's `ev4sf`). A spelling clang
    cannot declare has no facts (None): clang's recovery gave it int's
    (2026-10-23, run riscv64-runner_l13: `ev4sf` and `wchar_t`)."""
    kinds = builtin_kinds()
    nodes = {}
    sizes = {}
    signs = {}
    asked = []
    for spelling in spellings:
        if spelling not in asked:
            asked.append(spelling)
    for round_number in range(FACT_ROUNDS):
        new = []
        for spelling in asked:
            if spelling not in nodes:
                new.append(spelling)
        if not new:
            break
        read_round(new, os.path.join(directory, f"facts_{round_number}.c"), nodes, sizes, signs, preamble)
        for spelling in new:
            for inner in inner_spellings(nodes.get(spelling)):
                if inner not in asked:
                    asked.append(inner)
    facts = {}
    for spelling in asked:
        held_of(spelling, nodes, sizes, signs, kinds, facts)
    return facts


def holder_facts_kept(spellings: list, directory: str, path: str, preamble: tuple = ()) -> dict:
    """holder_facts, read from `path` when every spelling is there, else
    asked of clang once and written to `path` 
    facts loaded without clang on every import)."""
    if os.path.exists(path):
        facts = facts_read(path)
        missing = []
        for spelling in spellings:
            if spelling not in facts:
                missing.append(spelling)
        if not missing:
            return facts
    facts = holder_facts(spellings, directory, preamble)
    facts_written(facts, path)
    return facts


def facts_written(facts: dict, path: str) -> None:
    """spelling -> its Held as a dict, what it points to or holds by its
    spelling; None for a spelling clang gave no type."""
    data = {}
    for spelling, held in facts.items():
        if held is None:
            data[spelling] = None
            continue
        entry = held._asdict()
        entry["inner"] = held.inner.spelling if held.inner is not None else None
        data[spelling] = entry
    with open(path + ".writing", "w", encoding="utf-8") as written:
        json.dump(data, written, indent=1, sort_keys=True)
        written.write("\n")
    os.replace(path + ".writing", path)


def facts_read(path: str) -> dict:
    with open(path, encoding="utf-8") as read:
        data = json.load(read)
    facts = {}
    for spelling in data:
        held_read(spelling, data, facts)
    return facts


def held_read(spelling: str, data: dict, facts: dict):
    if spelling in facts:
        return facts[spelling]
    entry = data.get(spelling)
    if entry is None:
        facts[spelling] = None
        return None
    inner = None
    if entry["inner"] is not None:
        inner = held_read(entry["inner"], data, facts)
    held = Held(entry["spelling"], entry["kind"], entry["signed"], entry["size"], inner, entry["const"],
                entry["volatile"], entry["bits"], entry["count"])
    facts[spelling] = held
    return held


def read_round(spellings: list, path: str, nodes: dict, sizes: dict, signs: dict, preamble: tuple = ()) -> None:
    """One compile: each spelling's three declarations, and what clang's dump
    says of them."""
    os.makedirs(os.path.dirname(path), exist_ok=True)
    lines = list(mask_code.PREAMBLE["c"])
    for line in preamble:
        if line not in lines:
            lines.append(line)
    for number, spelling in enumerate(spellings):
        for line in FACT_LINES:
            lines.append(line.format(spelling=spelling, number=number))
    with open(path, "w", encoding="utf-8") as source:
        source.write("\n".join(lines) + "\n")
    command = mask_code.JUDGE_COMMAND["c"].split() + ["-Xclang", "-ast-dump=json", "-Xclang",
                                                      f"-ast-dump-filter={FACT_NAME}", path]
    with open(path + ".ast.json", "w") as tree_file, open(path + ".diag", "w") as diagnostics:
        subprocess.run(command, stdout=tree_file, stderr=diagnostics, check=False)
    declarations = read_declarations(path + ".ast.json")
    for number, spelling in enumerate(spellings):
        typedef = declarations.get(f"{FACT_NAME}{number}")
        if typedef is not None and typedef.get("inner") and not typedef.get("isInvalid"):
            nodes[spelling] = typedef["inner"][0]
        sizes[spelling] = array_length(declarations.get(f"{FACT_NAME}size_{number}"))
        signs[spelling] = array_length(declarations.get(f"{FACT_NAME}sign_{number}"))


def read_declarations(path: str) -> dict:
    """name -> declaration, from clang's filtered JSON dump: one document per
    declaration, one after another (as DRY_mask_maker.read_syntax_trees reads
    the functions)."""
    with open(path, encoding="utf-8") as dump:
        text = dump.read()
    decoder = json.JSONDecoder()
    declarations = {}
    position = 0
    while position < len(text):
        while position < len(text) and text[position] in " \n\r\t":
            position += 1
        if position >= len(text):
            break
        declaration, position = decoder.raw_decode(text, position)
        name = declaration.get("name")
        if name is not None:
            declarations[name] = declaration
    return declarations


ARRAY_OF_CHAR = re.compile(r"^char \[(\d+)\]$|^char\[(\d+)\]$")


def array_length(declaration) -> Optional[int]:
    """N for a declaration clang typed `char[N]`; None when clang refused it."""
    if declaration is None or declaration.get("isInvalid"):
        return None
    found = ARRAY_OF_CHAR.match(declaration.get("type", {}).get("qualType", ""))
    if found is None:
        return None
    length = int(found.group(1) or found.group(2))
    return length


def canonical(node: dict) -> tuple:
    """(the node under clang's sugar, its qualifiers): the type a spelling
    names, through typedefs, `struct`, parentheses and __typeof__."""
    qualifiers = []
    while node is not None:
        kind = node.get("kind")
        if kind == "QualType":
            qualifiers.extend(node.get("qualifiers", "").split())
            node = last_type_node(node)
            continue
        if kind in SUGAR:
            node = last_type_node(node)
            continue
        break
    found = (node, qualifiers)
    return found


def last_type_node(node: dict):
    """The type a sugar node stands for: its last inner node that is a type."""
    chosen = None
    for inner in node.get("inner", []):
        if inner.get("kind", "").endswith("Type"):
            chosen = inner
    return chosen


def inner_spellings(node) -> list:
    """The spellings of what a type points to or holds: a pointer's pointee,
    an array's, vector's or complex number's element, an _Atomic's value, a
    function's result."""
    if node is None:
        return []
    node, _qualifiers = canonical(node)
    if node is None or node.get("kind") not in NODE_KINDS:
        return []
    inner = node.get("inner", [])
    if not inner:
        return []
    spelling = inner[0].get("type", {}).get("qualType")
    if spelling is None:
        return []
    return [spelling]


BIT_INT = re.compile(r"_BitInt\((\d+)\)")


def held_of(spelling: str, nodes: dict, sizes: dict, signs: dict, kinds: dict, facts: dict):
    """The Held of one spelling, from its node; None when clang gave none."""
    if spelling in facts:
        return facts[spelling]
    facts[spelling] = None
    node = nodes.get(spelling)
    if node is None:
        return None
    node, qualifiers = canonical(node)
    if node is None:
        return None
    node_kind = node.get("kind")
    written = node.get("type", {}).get("qualType", spelling)
    kind = "other"
    if node_kind == "BuiltinType":
        kind = kinds.get(written, "builtin_other")
    elif node_kind == "RecordType":
        kind = "union" if written.startswith("union ") else "struct"
    elif node_kind in NODE_KINDS:
        kind = NODE_KINDS[node_kind]
    inner = None
    for inner_spelling in inner_spellings(nodes.get(spelling)):
        inner = held_of(inner_spelling, nodes, sizes, signs, kinds, facts)
    sign = signs.get(spelling)
    signed = sign == 2
    bits = 0
    count = 0
    if kind == "bitint":
        found = BIT_INT.search(written)
        if found is not None:
            bits = int(found.group(1))
    if kind == "array":
        count = int(node.get("size", 0) or 0)
    if kind in ("vector", "extvector"):
        count = int(node.get("numElements", 0) or 0)
    held = Held(spelling, kind, signed, sizes.get(spelling), inner, "const" in qualifiers, "volatile" in qualifiers,
                bits, count)
    facts[spelling] = held
    return held


# ---- the domain: the holders kept, and a pointer to each ----

def pointer_spelling(spelling: str) -> str:
    """How C writes a pointer to the type `spelling` writes: `short *`,
    `int **`, `fnptr *`."""
    if spelling.endswith("*"):
        return spelling + "*"
    return spelling + " *"


def domain_of(kept_spellings: list) -> tuple:
    """(every spelling a condition is tested on, the pointers among them the
    grid's holders do not hold): the holders kept, then a pointer to each."""
    domain = list(kept_spellings)
    added = []
    for spelling in kept_spellings:
        pointer = pointer_spelling(spelling)
        if pointer in domain:
            continue
        domain.append(pointer)
        added.append(pointer)
    found = (domain, added)
    return found


# ---- the evaluator: a condition's structure, on holders (compose's, extended) ----

INTEGER_KINDS = ("integer", "bool", "enum", "bitint")
ARITHMETIC_KINDS = ("integer", "bool", "enum", "bitint", "floating", "complex")
VECTOR_KINDS = ("vector", "extvector")
# The kinds of node clang's checks cast a type to (`getAs<PointerType>`), and
# the kinds of holder each matches. The other kinds clang's checking code
# names are not C's: no holder is one.
AS_KINDS = {"PointerType": ("pointer",), "VectorType": VECTOR_KINDS, "ExtVectorType": ("extvector",),
            "AtomicType": ("atomic",), "BuiltinType": ("integer", "bool", "floating", "void", "builtin_other"),
            "BitIntType": ("bitint",), "EnumType": ("enum",), "RecordType": ("struct", "union"),
            "ComplexType": ("complex",), "ConstantArrayType": ("array",), "ArrayType": ("array",),
            "FunctionProtoType": ("function",), "FunctionType": ("function",)}
NOT_C_KINDS = {"MemberPointerType", "ConstantMatrixType", "MatrixType", "ObjCObjectPointerType", "BlockPointerType",
               "ReferenceType", "LValueReferenceType", "RValueReferenceType", "getAsCXXRecordDecl",
               "IncompleteArrayType", "VariableArrayType", "DependentSizedArrayType", "TemplateSpecializationType"}


def type_predicate(name: str, t):
    """clang's Type::is... answered for one holder, as clang 21 defines it
    for C (clang/include/clang/AST/Type.h); UNDECIDED for a test not
    answered here."""
    if t is UNDECIDED:
        return UNDECIDED
    if name == "isNull":
        return t is None
    if t is None:
        return False
    answers = type_answers(t)
    answer = answers.get(name, UNDECIDED)
    return answer


def type_answers(t) -> dict:
    """Every test type_predicate answers, for one holder (not None)."""
    integer = t.kind in INTEGER_KINDS
    floating = t.kind == "floating"
    complex_any = t.kind == "complex"
    complex_floating = complex_any and t.inner is not None and t.inner.kind == "floating"
    vector = t.kind in VECTOR_KINDS
    vector_integer = vector and t.inner is not None and t.inner.kind in INTEGER_KINDS
    vector_floating = vector and t.inner is not None and t.inner.kind == "floating"
    pointer = t.kind == "pointer"
    record = t.kind in ("struct", "union")
    complete = t.size is not None and t.kind not in ("void", "function")
    answers = {
        "isIntegerType": integer, "isIntegralOrEnumerationType": integer,
        "isIntegralOrUnscopedEnumerationType": integer, "isIntegralType": integer,
        "isSignedIntegerType": integer and t.signed, "isUnsignedIntegerType": integer and not t.signed,
        "isSignedIntegerOrEnumerationType": integer and t.signed,
        "isUnsignedIntegerOrEnumerationType": integer and not t.signed,
        "isBooleanType": t.kind == "bool", "isCharType": t.spelling in ("char", "signed char", "unsigned char"),
        "isRealFloatingType": floating, "isFloatingType": floating or complex_floating,
        "isHalfType": t.spelling in ("__fp16", "half"), "isFloat16Type": t.spelling == "_Float16",
        "isBFloat16Type": t.spelling == "__bf16", "isFloat128Type": t.spelling == "__float128",
        "isArithmeticType": integer or floating or complex_any, "isRealType": integer or floating,
        "isScalarType": integer or floating or complex_any or pointer,
        "isPointerType": pointer, "isAnyPointerType": pointer, "isPointerOrReferenceType": pointer,
        "isFunctionPointerType": pointer and t.inner is not None and t.inner.kind == "function",
        "isVoidPointerType": pointer and t.inner is not None and t.inner.kind == "void",
        "isVectorType": vector, "isExtVectorType": t.kind == "extvector",
        "isExtVectorBoolType": t.kind == "extvector" and t.inner is not None and t.inner.kind == "bool",
        "isSubscriptableVectorType": vector and not (t.kind == "extvector" and t.inner is not None and t.inner.kind == "bool"),
        "isAtomicType": t.kind == "atomic", "isVoidType": t.kind == "void",
        "isConstQualified": t.const, "isVolatileQualified": t.volatile, "isRestrictQualified": False,
        "hasQualifiers": t.const or t.volatile,
        "isPromotableIntegerType": t.kind in ("bool", "enum") or (t.kind == "integer" and t.size is not None and t.size < 4),
        "PromotionType.isNull": not (t.spelling in ("_Float16", "__fp16", "__bf16") or (t.kind == "complex" and t.inner is not None and t.inner.spelling in ("_Float16", "__fp16", "__bf16"))),
        "promotionTy.isNull": not (t.spelling in ("_Float16", "__fp16", "__bf16") or (t.kind == "complex" and t.inner is not None and t.inner.spelling in ("_Float16", "__fp16", "__bf16"))),
        "PromoteType.isNull": not (t.kind in ("bool", "enum") or (t.kind == "integer" and t.size is not None and t.size < 4) or t.spelling == "float"),
        "typesAreCompatible_PromoteType": t.kind == "enum",
        "elementSize.isOne": t.size == 1 or t.kind in ("void", "function"),
        "isSpecificBuiltinType": t.spelling == "float",
        "isTriviallyCopyableType": complete, "isTriviallyCopyConstructibleType": complete,
        "isValidElementType": integer or floating,
        "hasIntegerRepresentation": integer or vector_integer,
        "hasSignedIntegerRepresentation": (integer and t.signed) or (vector_integer and t.inner.signed),
        "hasUnsignedIntegerRepresentation": (integer and not t.signed) or (vector_integer and not t.inner.signed),
        "hasFloatingRepresentation": floating or complex_floating or vector_floating,
        "isSizelessVectorType": False, "isSizelessType": False, "isSizelessBuiltinType": False,
        "isSVESizelessBuiltinType": False, "isRVVSizelessBuiltinType": False, "isWebAssemblyTableType": False,
        "isBlockPointerType": False, "isObjCObjectPointerType": False, "isObjCIdType": False,
        "isObjCClassType": False, "isObjCRetainableType": False, "isNullPtrType": False,
        "isMemberPointerType": False, "isMemberDataPointerType": False, "isMemberFunctionPointerType": False,
        "isRecordType": record, "isStructureType": t.kind == "struct", "isUnionType": t.kind == "union",
        "isStructureOrClassType": t.kind == "struct", "isClassType": False,
        "isArrayType": t.kind == "array", "isConstantArrayType": t.kind == "array",
        "isIncompleteArrayType": False, "isVariableArrayType": False,
        "isFunctionType": t.kind == "function", "isFunctionProtoType": t.kind == "function",
        "isEnumeralType": t.kind == "enum", "isUnscopedEnumerationType": t.kind == "enum",
        "isScopedEnumeralType": False, "isBitIntType": t.kind == "bitint",
        "isComplexType": complex_floating, "isAnyComplexType": complex_any,
        "isComplexIntegerType": complex_any and not complex_floating,
        "isIncompleteType": not complete and t.kind != "function", "isObjectType": t.kind not in ("function", "void"),
        "isIncompleteOrObjectType": t.kind != "function",
        "isDependentType": False, "isInstantiationDependentType": False, "isUndeducedType": False,
        "isFixedPointType": False, "isFixedPointOrIntegerType": integer, "isMatrixType": False,
        "isConstantMatrixType": False, "isOpenCLSpecificType": False, "isImageType": False, "isPipeType": False,
        "isSamplerT": False, "isEventT": False, "isClkEventT": False, "isQueueT": False, "isReserveIDT": False,
        "isHLSLSpecificType": False,
    }
    answers.update(llvm_type_answers(t))
    return answers


def llvm_type_answers(t) -> dict:
    """CodeGen's tests of the llvm::Type clang converts a holder to
    (CodeGenTypes::ConvertType; llvm/include/llvm/IR/Type.h): a pointer
    becomes `ptr`; an integer, a bool, an enum and a _BitInt an integer type;
    a floating type a floating-point type; a GNU or ext vector a vector type;
    a struct, a union, an array and a complex number an aggregate (a complex
    number is `{ T, T }`). 
    integer = t.kind in INTEGER_KINDS
    floating = t.kind == "floating"
    vector = t.kind in VECTOR_KINDS
    vector_floating = vector and t.inner is not None and t.inner.kind == "floating"
    answers = {
        "isPointerTy": t.kind == "pointer", "isIntegerTy": integer, "isFloatingPointTy": floating,
        "isFPOrFPVectorTy": floating or vector_floating, "isVectorTy": vector,
        "isAggregateType": t.kind in ("struct", "union", "array", "complex"),
        "isStructTy": t.kind in ("struct", "union", "complex"),
    }
    return answers


def as_passed(t, pointer_size):
    """An argument as C passes it (C17 6.3.2.1): an array as a pointer to its
    first element, a function as a pointer to it, an _Atomic as its value,
    without its qualifiers."""
    if t is UNDECIDED or t is None:
        return t
    if t.kind == "array":
        return Held(t.spelling, "pointer", False, pointer_size, t.inner)
    if t.kind == "function":
        return Held(t.spelling, "pointer", False, pointer_size, t)
    if t.kind == "atomic" and t.inner is not None:
        return t.inner._replace(const=False, volatile=False)
    if t.const or t.volatile:
        return t._replace(const=False, volatile=False)
    return t


QUALIFIER_WORDS = re.compile(r"\b(const|volatile|restrict)\b\s*")


def unqualified(spelling: str) -> str:
    """A spelling without its qualifier words: `const struct S` -> `struct S`."""
    bare = QUALIFIER_WORDS.sub("", spelling).strip()
    return bare


def convertible(source, target, pointer_size):
    """Whether clang 21 converts a value of `source` to `target` in C without
    an error: arithmetic types into each other, a pointer into a pointer (a
    warning when they differ) or into a bool, a struct or union only into
    itself; an integer into a pointer, or a pointer into an integer, is an
    error since clang 15, and nothing converts from or to void. UNDECIDED
    for the rest (vectors)."""
    if source is UNDECIDED or target is UNDECIDED:
        return UNDECIDED
    if source is None or target is None:
        return False
    source = as_passed(source, pointer_size)
    if target.kind == "atomic" and target.inner is not None:
        target = target.inner
    if source.kind == "void" or target.kind == "void":
        return False
    if source.kind in ("struct", "union") or target.kind in ("struct", "union"):
        return unqualified(source.spelling) == unqualified(target.spelling)
    if source.kind in ARITHMETIC_KINDS and target.kind in ARITHMETIC_KINDS:
        return True
    if source.kind == "pointer" and target.kind == "pointer":
        return True
    if source.kind == "pointer" and target.kind == "bool":
        return True
    if source.kind == "pointer" and target.kind in ARITHMETIC_KINDS:
        return False
    if source.kind in ARITHMETIC_KINDS and target.kind == "pointer":
        return False
    if unqualified(source.spelling) == unqualified(target.spelling):
        return True
    return UNDECIDED


class Evaluator:
    """Answers a condition's structure for holders: the facts of every
    spelling, and the builtin's result type."""

    def __init__(self, facts: dict, result=UNDECIDED):
        self.facts = facts
        self.result = result
        pointer = facts.get("void *")
        self.pointer_size = pointer.size if pointer is not None else UNDECIDED

    def by_name(self, spelling: str):
        found = self.facts.get(spelling)
        if found is None:
            return UNDECIDED
        return found

    def text_type(self, text: str, slots):
        """A type written as the walk renders it: `pointee(type(arg0) as
        PointerType)`, `Context.IntTy`, `int`."""
        text = text.strip()
        found = re.match(r"^(?:(pointee|element|value type)\()?type\(arg(\d+)\)(?: as (\w+))?\)?(?: as (\w+))?$", text)
        if found:
            wrapper, number, kind, outer_kind = found.groups()
            number = int(number)
            t = slots[number] if number < len(slots) else UNDECIDED
            if kind:
                t = self.as_kind(kind, t)
            if wrapper:
                t = self.wrapped(wrapper, t)
            if outer_kind:
                t = self.as_kind(outer_kind, t)
            return t
        found = re.match(r"^(?:Context|Node\.Context|S\.Context|getASTContext\(\))\.(\w+(?:\(\))?)$", text)
        if found and found.group(1) in CONTEXT_TYPES:
            return self.by_name(CONTEXT_TYPES[found.group(1)])
        if text in self.facts:
            return self.by_name(text)
        return UNDECIDED

    @staticmethod
    def as_kind(kind, t):
        if t is UNDECIDED or t is None:
            return t
        if kind in AS_KINDS:
            if t.kind in AS_KINDS[kind]:
                return t
            return None
        if kind in NOT_C_KINDS:
            return None
        return UNDECIDED

    @staticmethod
    def wrapped(wrapper, t):
        if t is UNDECIDED or t is None:
            return t
        if wrapper == "pointee":
            return t.inner if t.kind == "pointer" else None
        if wrapper in ("element", "elem"):
            return t.inner if t.kind in VECTOR_KINDS + ("array", "complex") else None
        return t.inner if t.kind == "atomic" else None

    def type_of(self, node, slots):
        """The holder a structured type expression names; None for a null
        type; UNDECIDED when it cannot be told."""
        if not isinstance(node, list) or not node:
            return UNDECIDED
        kind = node[0]
        if kind == "type":
            inner = node[1] if len(node) > 1 else None
            if isinstance(inner, list) and inner[:1] == ["arg"] and isinstance(inner[1], int):
                return slots[inner[1]] if inner[1] < len(slots) else UNDECIDED
            if inner == ["call"]:
                return self.result
            if isinstance(inner, list) and inner[:1] == ["converted"] and len(inner) > 2:
                return self.text_type(str(inner[2]), slots)
            return UNDECIDED
        if kind in ("pointee", "elem", "value"):
            return self.wrapped({"pointee": "pointee", "elem": "element", "value": "value"}[kind],
                                self.type_of(node[1], slots))
        if kind == "as" and len(node) > 2:
            return self.as_kind(node[1], self.type_of(node[2], slots))
        if kind == "ctype" and len(node) > 1:
            return self.text_type(f"Context.{node[1]}", slots)
        if kind == "valuetype" and len(node) > 1:
            t = self.type_of(node[1], slots)
            return t.inner if isinstance(t, Held) and t.kind == "atomic" else t
        return UNDECIDED

    def number(self, node, slots, arity):
        if isinstance(node, bool):
            return node
        if isinstance(node, int):
            return node
        if isinstance(node, list) and node:
            if node == ["arity"]:
                return arity
            if node[0] == "size" and len(node) > 1:
                t = self.type_of(node[1], slots)
                if t is UNDECIDED or t is None:
                    return t
                return t.size if t.size is not None else UNDECIDED
            if node[0] == "bits" and len(node) > 1:
                t = self.type_of(node[1], slots)
                if t is UNDECIDED or t is None:
                    return t
                return t.bits if t.kind == "bitint" else UNDECIDED
        if isinstance(node, str):
            return node
        return UNDECIDED

    def value(self, node, slots, arity):
        """A comparison's side: a number, a holder, or text."""
        if isinstance(node, list) and node and node[0] in ("type", "pointee", "elem", "value", "as", "ctype"):
            return self.type_of(node, slots)
        return self.number(node, slots, arity)

    def truth(self, node, slots, arity, constants):
        """True, False or UNDECIDED for one condition's structure."""
        if isinstance(node, bool):
            return node
        if not isinstance(node, list) or not node:
            return UNDECIDED
        kind = node[0]
        if kind == "not":
            inner = self.truth(node[1], slots, arity, constants)
            return inner if inner is UNDECIDED else (not inner)
        if kind == "opaque":
            return UNDECIDED
        if kind == "pred":
            name, subject = node[1], node[2]
            if name in ("==", "!=", "<", ">", "<=", ">=") and isinstance(subject, list) and len(subject) == 2:
                left = self.value(subject[0], slots, arity)
                right = self.value(subject[1], slots, arity)
                if left is UNDECIDED or right is UNDECIDED:
                    return UNDECIDED
                if isinstance(left, Held) or isinstance(right, Held) or left is None or right is None:
                    if name == "==":
                        return left == right
                    if name == "!=":
                        return left != right
                    return UNDECIDED
                if isinstance(left, str) or isinstance(right, str):
                    same = str(left).split("::")[-1] == str(right).split("::")[-1]
                    return same if name == "==" else (not same) if name == "!=" else UNDECIDED
                return {"==": left == right, "!=": left != right, "<": left < right, ">": left > right,
                        "<=": left <= right, ">=": left >= right}[name]
            if name.startswith("not convertible to "):
                target = self.text_type(name[len("not convertible to "):], slots)
                if isinstance(subject, list) and subject[:1] == ["arg"] and isinstance(subject[1], int):
                    source_type = slots[subject[1]] if subject[1] < len(slots) else UNDECIDED
                else:
                    source_type = UNDECIDED
                answer = convertible(source_type, target, self.pointer_size)
                return answer if answer is UNDECIDED else (not answer)
            if name in ("isPowerOf2_64", "isPowerOf2_32"):
                number = self.number(subject, slots, arity)
                if isinstance(number, int) and not isinstance(number, bool):
                    return number > 0 and number & (number - 1) == 0
                return UNDECIDED
            return type_predicate(name, self.type_of(subject, slots))
        if kind == "arity" and len(node) >= 3:
            if node[1] == "range" and len(node) >= 4:
                return node[2] <= arity <= node[3]
            return {"==": arity == node[2], ">=": arity >= node[2], "<=": arity <= node[2]}.get(node[1], UNDECIDED)
        if kind == "ice":
            # the standard form writes a constant only where clang's type
            # letters ask for one (`I`); every other argument is a field,
            # never an integer constant expression
            number = node[1] if len(node) > 1 else None
            if not isinstance(number, int):
                return UNDECIDED
            return number in constants
        if kind in ("type", "pointee", "elem", "value", "as", "ctype"):
            t = self.type_of(node, slots)
            return t if t is UNDECIDED else (t is not None)
        return UNDECIDED


def arguments_in(node) -> set:
    """The argument numbers a structure mentions."""
    found = set()
    if isinstance(node, list):
        if len(node) == 2 and node[0] == "arg" and isinstance(node[1], int):
            found.add(node[1])
        for part in node:
            found |= arguments_in(part)
    elif isinstance(node, str):
        for number in re.findall(r"\barg(\d+)\b", node):
            found.add(int(number))
    return found


class Condition(NamedTuple):
    text: str        # the condition as the walk renders it
    taken: bool      # the side the accepting path took
    shape: object    # its structure
    arguments: frozenset


def conditions_of(rule: list, structures: dict) -> list:
    made = []
    for _source_text, taken, rendered in rule:
        shape = structures.get(rendered, ["opaque", rendered])
        made.append(Condition(rendered, taken, shape, frozenset(arguments_in(shape) | arguments_in(rendered))))
    return made


def holds(evaluator: Evaluator, condition: Condition, slots: list, arity: int, constants: dict):
    """True when the condition takes the path's side for these holders, False
    when it takes the other, UNDECIDED when it cannot be told."""
    got = evaluator.truth(condition.shape, slots, arity, constants)
    if got is UNDECIDED:
        return UNDECIDED
    return got == condition.taken


def holds_either_way(evaluator: Evaluator, conditions: list, slots: list, arity: int, constants: dict) -> bool:
    """No condition false for the holders as written, or none false for them
    as C passes them."""
    for view in (slots, [as_passed(t, evaluator.pointer_size) for t in slots]):
        false = False
        for condition in conditions:
            if holds(evaluator, condition, view, arity, constants) is False:
                false = True
                break
        if not false:
            return True
    return False


# ---- the signatures of one operator ----

def call_arguments(spelling: str) -> list:
    """The arguments of a call's template, as written: `__sync_fetch_and_add_4(a, b)`
    gives ["a", "b"]."""
    start = spelling.index("(")
    end = spelling.rindex(")")
    inside = spelling[start + 1:end]
    arguments = []
    depth = 0
    current = ""
    for character in inside:
        if character in "([{":
            depth += 1
        elif character in ")]}":
            depth -= 1
        if character == "," and depth == 0:
            arguments.append(current.strip())
            current = ""
            continue
        current += character
    if current.strip():
        arguments.append(current.strip())
    return arguments


class Signatures(NamedTuple):
    """What the reading gave one operator: its accepting rules, the rules
    that fit its arguments, the holders each slot takes in the signatures
    (None for a slot no rule names, which takes the grid's own holders), and
    the signatures, each a holder spelling per slot."""

    rules: int
    fitting: int
    candidates: list
    signatures: list


# Up to this many slots, every combination of the holders each slot takes is
# a signature. With more, every holder each slot takes is tried at least once,
# beside the first holders of the other slots that fit it (each_holder_once):
# the product grows as the holders to the power of the slots
# (__builtin_fpclassify's six would be about 25 ** 5 * 5), as the grid steps
# down from every holder kept (up to two slots) to its small sets (three and
# more, holders_for).
EVERY_COMBINATION_UP_TO = 2
# How many holders first_fit tries before it gives a holder up.
FIT_TRIES = 20000


def signatures_of(operator, read: dict, evaluator: Evaluator, domain: list, defaults: list, slots: tuple) -> Signatures:
    """The signatures the reading accepts for one operator, in slot order:
    for each accepting rule that fits the operator's arguments, the holders
    each argument takes, combined (every_combination, or each_holder_once
    past EVERY_COMBINATION_UP_TO slots)."""
    arity, slot_of_argument, constants = argument_places(operator, slots)
    structures = read.get("structures", {})
    found = []
    seen = set()
    fitting = 0
    named_anywhere = set()
    for rule in read.get("accepted", []):
        conditions = conditions_of(rule, structures)
        if not rule_fits(evaluator, conditions, arity, constants):
            continue
        fitting += 1
        per_argument, named = holders_each_argument_takes(evaluator, conditions, arity, constants, domain, defaults)
        named_anywhere |= named
        tied = []
        for condition in conditions:
            if len(condition.arguments) > 1:
                tied.append(condition)
        if len(slots) <= EVERY_COMBINATION_UP_TO:
            combinations = every_combination(evaluator, per_argument, tied, arity, constants)
        else:
            combinations = each_holder_once(evaluator, per_argument, tied, arity, constants)
        for combination in combinations:
            signature = signature_of(combination, slot_of_argument, len(slots))
            if signature in seen:
                continue
            seen.add(signature)
            found.append(signature)
    candidates = holders_by_slot(found, slot_of_argument, named_anywhere, len(slots))
    made = Signatures(len(read.get("accepted", [])), fitting, candidates, found)
    return made


def argument_places(operator, slots: tuple) -> tuple:
    """(how many arguments the call writes, argument position -> slot, argument
    position -> the constant written there)."""
    arguments = call_arguments(operator.spelling)
    slot_of_argument = {}
    constants = {}
    for position, argument in enumerate(arguments):
        if argument in slots:
            slot_of_argument[position] = slots.index(argument)
        else:
            constants[position] = argument
    places = (len(arguments), slot_of_argument, constants)
    return places


def rule_fits(evaluator: Evaluator, conditions: list, arity: int, constants: dict) -> bool:
    """Whether a rule can hold for the call as written: no condition names an
    argument past its last, and no condition on the arguments' number fails."""
    for condition in conditions:
        for number in condition.arguments:
            if number >= arity:
                return False
        if not condition.arguments and holds(evaluator, condition, [], arity, constants) is False:
            return False
    return True


def holders_each_argument_takes(evaluator: Evaluator, conditions: list, arity: int, constants: dict, domain: list,
                                defaults: list) -> tuple:
    """(per argument, the holders it takes: those of the domain for which no
    condition on that argument alone is false; the grid's own holders for an
    argument no condition names; [None] for a constant. The arguments the
    conditions name.)"""
    named = set()
    for condition in conditions:
        named |= condition.arguments
    int_held = evaluator.by_name("int")
    per_argument = []
    for position in range(arity):
        if position in constants:
            per_argument.append([None])
            continue
        if position not in named:
            per_argument.append(list(defaults))
            continue
        alone = []
        for condition in conditions:
            if condition.arguments == frozenset({position}):
                alone.append(condition)
        chosen = []
        for spelling in domain:
            slots_now = [int_held] * arity
            slots_now[position] = evaluator.by_name(spelling)
            if holds_either_way(evaluator, alone, slots_now, arity, constants):
                chosen.append(spelling)
        per_argument.append(chosen)
    found = (per_argument, named)
    return found


def held_slots(evaluator: Evaluator, combination: list, constants: dict) -> list:
    """The holders of a combination as the evaluator reads them: a constant
    is an int, an argument not chosen yet is UNDECIDED."""
    int_held = evaluator.by_name("int")
    slots_now = []
    for position, spelling in enumerate(combination):
        if position in constants:
            slots_now.append(int_held)
        elif spelling is None:
            slots_now.append(UNDECIDED)
        else:
            slots_now.append(evaluator.by_name(spelling))
    return slots_now


def every_combination(evaluator: Evaluator, per_argument: list, tied: list, arity: int, constants: dict) -> list:
    """Every combination of the holders each argument takes, but those a
    condition on two or more arguments makes false."""
    combinations = []
    for combination in itertools.product(*per_argument):
        slots_now = held_slots(evaluator, list(combination), constants)
        if tied and not holds_either_way(evaluator, tied, slots_now, arity, constants):
            continue
        combinations.append(list(combination))
    return combinations


def each_holder_once(evaluator: Evaluator, per_argument: list, tied: list, arity: int, constants: dict) -> list:
    """For each argument and each holder it takes, one combination: that
    holder there, and in the other arguments the first holders, in order,
    that no condition on two or more arguments makes false with it."""
    combinations = []
    for position in range(arity):
        if position in constants:
            continue
        for spelling in per_argument[position]:
            combination = first_fit(evaluator, per_argument, position, spelling, tied, arity, constants)
            if combination is not None:
                combinations.append(combination)
    return combinations


def first_fit(evaluator: Evaluator, per_argument: list, position: int, spelling: str, tied: list, arity: int,
              constants: dict):
    """The first combination, argument by argument in order, with `spelling`
    at `position` and no condition on two or more arguments false; None when
    there is none within FIT_TRIES tries."""
    combination = [None] * arity
    combination[position] = spelling
    order = []
    for other in range(arity):
        if other != position and other not in constants:
            order.append(other)
    tries = [0]

    def place(index: int) -> bool:
        if index == len(order):
            return True
        other = order[index]
        for candidate in per_argument[other]:
            tries[0] += 1
            if tries[0] > FIT_TRIES:
                return False
            combination[other] = candidate
            if fits_so_far(evaluator, combination, tied, arity, constants) and place(index + 1):
                return True
        combination[other] = None
        return False

    if not fits_so_far(evaluator, combination, tied, arity, constants):
        return None
    if not place(0):
        return None
    return combination


def fits_so_far(evaluator: Evaluator, combination: list, tied: list, arity: int, constants: dict) -> bool:
    """No condition whose arguments are all chosen is false (for the
    holders as written, or as C passes them)."""
    chosen = []
    for condition in tied:
        complete = True
        for number in condition.arguments:
            if number not in constants and combination[number] is None:
                complete = False
                break
        if complete:
            chosen.append(condition)
    if not chosen:
        return True
    slots_now = held_slots(evaluator, combination, constants)
    fits = holds_either_way(evaluator, chosen, slots_now, arity, constants)
    return fits


def signature_of(combination: list, slot_of_argument: dict, slot_count: int) -> tuple:
    """A combination of the call's arguments as a signature: one holder
    spelling per slot."""
    signature = [None] * slot_count
    for position, slot in slot_of_argument.items():
        signature[slot] = combination[position]
    found = tuple(signature)
    return found


def holders_by_slot(found: list, slot_of_argument: dict, named: set, slot_count: int) -> list:
    """Per slot, the holders it takes in the signatures, in their order;
    None for a slot no rule names (it takes the grid's own holders)."""
    candidates = []
    for slot in range(slot_count):
        position = None
        for argument, at in slot_of_argument.items():
            if at == slot:
                position = argument
        if position not in named:
            candidates.append(None)
            continue
        taken = []
        for signature in found:
            if signature[slot] not in taken:
                taken.append(signature[slot])
        candidates.append(taken)
    return candidates


def result_type(letters: str, evaluator: Evaluator):
    """The result type a builtin's type letters give (Builtins.td), for a
    condition on the call's own type; UNDECIDED when not read. compose's,
    as it was."""
    found = re.match(r"^([LUSZWNOI]*)([vbcsihxyfdzYw])(\*?)", letters or "")
    if not found:
        return UNDECIDED
    prefix, letter, pointer = found.groups()
    longs = prefix.count("L")
    unsigned = "U" in prefix
    name = {"v": "void", "b": "_Bool", "c": "char", "s": "short", "h": "__fp16", "x": "_Float16", "y": "__bf16",
            "f": "float", "d": "double", "z": "unsigned long", "Y": "long", "w": "int"}.get(letter)
    if letter == "i":
        name = {0: "int", 1: "long", 2: "long long", 3: "__int128"}[min(longs, 3)]
        if "W" in prefix:
            name = "long"
        if "O" in prefix:
            name = "long long"
    if letter == "d" and longs:
        name = "long double"
    if letter == "c" and "S" in prefix:
        name = "signed char"
    if unsigned and name in ("int", "long", "long long", "__int128", "short", "char"):
        name = "unsigned " + name
    if pointer or name is None:
        return UNDECIDED
    return evaluator.by_name(name)


# ---- the signatures of every builtin with custom typechecking, for extract() ----

class Read(NamedTuple):
    """What extract() takes from the reading: the pointers the domain adds
    (as Holders, for the grid's holder list), per operator, by its name and
    template, what the reading gave it, what checking_reader read, and each
    holder's facts as clang gave them; then, once extract() has judged the
    added holders, the positions in the grid's holder list of those clang
    keeps in a field."""

    added: tuple
    by_operator: dict
    checks: dict
    facts: dict
    kept_added: tuple = ()


def enumerator_of(operator):
    """The enumerator clang's list names a builtin's call by: `BI__sync_fetch_and_add_4`."""
    for prefix in ("CallExpr.BI", "AtomicExpr.AO"):
        if operator.name.startswith(prefix):
            return "BI" + operator.name[len(prefix):]
    return None


def read_signatures(operators: list, kept_spellings: list, defaults_of, directory: str) -> Read:
    """For every operator whose builtin has custom typechecking, the signatures
    its checking code accepts, read from that code (checking_reader) and
    tested on the holders kept and a pointer to each (domain_of)."""
    from ...complex_signature_reader import checking_reader
    from ..HiOps.operator_reader import clang as clang_reader
    builtins = clang_reader.made_builtins(clang_reader.BUILTINS_TD)
    letters_of = {}
    custom_typechecked = set()
    for builtin in builtins:
        letters_of[builtin.enumerator] = builtin.type
        if "t" in builtin.attributes:
            custom_typechecked.add(builtin.enumerator)
    wanted = []
    for operator in operators:
        enumerator = enumerator_of(operator)
        if enumerator in custom_typechecked and enumerator not in wanted:
            wanted.append(enumerator)
    checks = checking_reader.read_checks(wanted)
    domain, added = domain_of(kept_spellings)
    asked = list(domain) + sorted(set(CONTEXT_TYPES.values()) - {"void"})
    facts = holder_facts(asked, directory)
    by_operator = {}
    started = time.time()
    said = started
    for operator in operators:
        enumerator = enumerator_of(operator)
        if enumerator not in checks:
            continue
        if time.time() - said >= checking_reader.PROGRESS_SECONDS:
            said = time.time()
            print(f"[signatures] {len(by_operator)} builtin forms done, {said - started:.0f} s; now "
                  f"{operator.spelling}", flush=True)
        evaluator = Evaluator(facts)
        evaluator.result = result_type(letters_of.get(enumerator, ""), evaluator)
        usable = []
        for spelling in domain:
            if facts.get(spelling) is not None:
                usable.append(spelling)
        slots = mask_code.slots_of(operator)
        made = signatures_of(operator, checks[enumerator], evaluator, usable, defaults_of(operator), slots)
        by_operator[(operator.name, operator.spelling)] = made
    holders = []
    for spelling in added:
        pointee = spelling[:-1].rstrip()
        holders.append(Holder("c", "PointerType", spelling,
                              f"a pointer to `{pointee}`: complex_signature_reader.accepted_signatures, for the "
                              f"conditions clang's checking code sets on what an argument points to"))
    found = Read(tuple(holders), by_operator, checks, facts)
    return found
