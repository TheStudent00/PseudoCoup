"""holder_reader -- the module that reads the holder types one language's
lowerer declares, from the lowerer's own source, in the order it declares
them. Its function `read_holders(lang)` returns them.

Plan: `.../node_0_0_0_0_2_4_1_holder_reader/`.

    c, cpp      llvm-project  clang/include/clang/AST/Type.h, BuiltinType::Kind,
                              built from nine .def files
    go          go            src/go/types/basic.go, BasicKind
    java        jdk           com/sun/tools/javac/code/TypeTag.java
    csharp      runtime       RuntimeBinder Syntax/PredefinedType.cs
    rust        rust          library/core/src/ops/arith.rs: the impl macros' type lists
    swift       swift         stdlib/public/core/IntegerTypes.swift.gyb,
                              FloatingPointTypes.swift.gyb
    dart        sdk           sdk/lib/core: the num, int, double and bool classes
    ruby        ruby          gems/rbs-*.gem: core/*.rbs, one file per class
    php         php-src       Zend/zend_types.h, IS_NULL .. IS_REFERENCE
    python      cpython       Python/bltinmodule.c, SETBUILTIN
    javascript  v8            src/compiler/turbofan-types.h

This reports every type the lowerer declares. Which of them are distinct
holders is decided by what they lower to, never here.
"""

import os
import re
import shlex
import subprocess
import tempfile

from .. import Declaration, Holder, declaration_of, declaring_file_path


# The preprocessor that reads clang's .def files. Configuration: clang's own
# by default, at the version the judge runs.
PREPROCESSOR_VARIABLE = "PSEUDOIR_PREPROCESSOR"
DEFAULT_PREPROCESSOR = "clang -E"

# clang declares its builtin types as ONE enum, BuiltinType::Kind in
# clang/include/clang/AST/Type.h, which the preprocessor builds from nine
# files:
#
#     #define RVV_TYPE(Name, Id, SingletonId) Id,
#     #include "clang/Basic/RISCVVTypes.def"
#     ...
#     #define BUILTIN_TYPE(Id, SingletonId) Id,
#     #include "clang/AST/BuiltinTypes.def"
#
# Its type printer, BuiltinType::getName in clang/lib/AST/Type.cpp, spells
# eight of those files through a macro template of its own and the ninth,
# BuiltinTypes.def, case by case:
#
#     #define RVV_TYPE(Name, Id, SingletonId) \
#       case Id:                              \
#         return Name;
#     #include "clang/Basic/RISCVVTypes.def"
#
#     case UInt:
#       return "unsigned int";
#
# The .def files use conditionals and token pasting, so they are read the
# way clang reads them, by the preprocessor. Each enum entry's macro is given
# its file's printer template, and the preprocessor writes one
# HOLDER(Id, spelling) per type, with the file and line it came from.
#
# Where the printer has two spellings for one type, both are reported. Which
# one a language accepts is the lowerer's call when the grid is judged.
CLANG_ENUM_CLASS = "class BuiltinType : public Type {"
CLANG_ENUM_START = "enum Kind {"
CLANG_PRINTER_START = "StringRef BuiltinType::getName(const PrintingPolicy &Policy) const {"
CLANG_DEFINE = re.compile(r"^\s*#define\s+(\w+)\(([^)]*)\)\s*(.*)$")
CLANG_INCLUDE = re.compile(r'^\s*#include\s+"([^"]+)"')
CLANG_PRINTER_CASE = re.compile(r"^\s*case (?:BuiltinType::)?(\w+):")
CLANG_PRINTER_RETURN = re.compile(r"^\s*return (.*);")
CLANG_TEMPLATE_BODY = re.compile(r"^\s*case\s+\w+\s*:\s*return\s+(.*);\s*$")
CLANG_STRING = re.compile(r'"((?:[^"\\]|\\.)*)"')
CLANG_LINE_MARKER = re.compile(r'^#\s+(\d+)\s+"([^"]+)"')
CLANG_HOLDER = re.compile(r'HOLDER\(\s*(\w+)\s*,\s*((?:"(?:[^"\\]|\\.)*"\s*)*)\)')


def read_clang_enum(checkout: str, relative: str) -> list:
    """(include file, [(macro, parameters, body), ...]) for every #include
    inside BuiltinType::Kind, in the order the enum includes them."""
    path = declaring_file_path(checkout, relative)
    included = []
    pending_macros = []
    inside_class = False
    inside_enum = False
    with open(path, encoding="utf-8") as enum_file:
        for line in enum_file:
            if not inside_class:
                inside_class = line.startswith(CLANG_ENUM_CLASS)
                continue
            if not inside_enum:
                inside_enum = line.strip().startswith(CLANG_ENUM_START)
                continue
            if line.strip() == "};":
                break
            define = CLANG_DEFINE.match(line)
            if define is not None:
                pending_macros.append((define.group(1), define.group(2), define.group(3)))
                continue
            include = CLANG_INCLUDE.match(line)
            if include is not None:
                included.append((include.group(1), pending_macros))
                pending_macros = []
    return included


def read_clang_printer(checkout: str, relative: str) -> tuple:
    """The printer BuiltinType::getName, read two ways:

        spelled_by_case      type name -> ((spelling, line), ...)
        spelled_by_template  include file -> (macro, parameters, spelling, line)
    """
    path = declaring_file_path(checkout, relative)
    spelled_by_case = {}
    spelled_by_template = {}
    pending_names = []
    macro_text = None
    macro_line = 0
    template = None
    inside_printer = False
    with open(path, encoding="utf-8") as printer_file:
        for line_number, line in enumerate(printer_file, start=1):
            if not inside_printer:
                inside_printer = line.startswith(CLANG_PRINTER_START)
                continue
            if line.startswith("}"):
                break
            stripped = line.rstrip("\n")
            if macro_text is not None:
                macro_text += " " + stripped.rstrip("\\").strip()
                if not stripped.endswith("\\"):
                    template = (macro_text, macro_line)
                    macro_text = None
                continue
            if stripped.lstrip().startswith("#define"):
                macro_text = stripped.rstrip("\\").strip()
                macro_line = line_number
                if not stripped.endswith("\\"):
                    template = (macro_text, macro_line)
                    macro_text = None
                continue
            include = CLANG_INCLUDE.match(stripped)
            if include is not None:
                if template is not None:
                    define = CLANG_DEFINE.match(template[0])
                    body = CLANG_TEMPLATE_BODY.match(define.group(3))
                    spelled = (define.group(1), define.group(2), body.group(1), template[1])
                    spelled_by_template[include.group(1)] = spelled
                template = None
                continue
            case = CLANG_PRINTER_CASE.match(stripped)
            if case is not None:
                pending_names.append(case.group(1))
                continue
            returned = CLANG_PRINTER_RETURN.match(stripped)
            if returned is None:
                continue
            spelled = []
            for spelling in CLANG_STRING.findall(returned.group(1)):
                spelled.append((spelling, line_number))
            for name in pending_names:
                spelled_by_case[name] = tuple(spelled)
            pending_names = []
    printer = (spelled_by_case, spelled_by_template)
    return printer


def clang_preprocessor_input(included: list, spelled_by_template: dict) -> str:
    """The text the preprocessor expands: the enum's own includes, with every
    entry macro rewritten to HOLDER(Id, spelling)."""
    lines = []
    for include, macros in included:
        template = spelled_by_template.get(include)
        if template is not None:
            macro, parameters, spelling, _line = template
            lines.append(f"#define {macro}({parameters}) HOLDER(Id, {spelling})")
            lines.append(f'#include "{include}"')
            lines.append(f"#undef {macro}")
            continue
        # An entry macro is one the enum expands to `Id,`. Any other is a
        # marker, such as LAST_BUILTIN_TYPE's `LastKind = Id`, and expands
        # to nothing here.
        for macro, parameters, body in macros:
            if body.strip() == "Id,":
                lines.append(f'#define {macro}({parameters}) HOLDER(Id, "")')
            else:
                lines.append(f"#define {macro}({parameters})")
        lines.append(f'#include "{include}"')
        for macro, _parameters, _body in macros:
            lines.append(f"#undef {macro}")
    text = "\n".join(lines) + "\n"
    return text


def run_clang_preprocessor(checkout: str, text: str) -> str:
    """The preprocessor's expansion of `text`, with clang's own include root."""
    include_root = declaring_file_path(checkout, "clang/include/clang/AST/Type.h")
    include_root = include_root[: -len("clang/AST/Type.h")]
    preprocessor = os.environ.get(PREPROCESSOR_VARIABLE, DEFAULT_PREPROCESSOR)
    with tempfile.NamedTemporaryFile("w", suffix=".c", delete=False) as input_file:
        input_file.write(text)
        input_path = input_file.name
    command = shlex.split(preprocessor) + ["-nostdinc", "-I", include_root, "-x", "c", input_path]
    try:
        finished = subprocess.run(command, capture_output=True, text=True, check=False)
    finally:
        os.unlink(input_path)
    if finished.returncode != 0:
        message = f"read_holders: the preprocessor refused clang's .def files: {finished.stderr[:400]}"
        raise RuntimeError(message)
    return finished.stdout


def read_clang_holder_lines(checkout: str, expanded: str) -> list:
    """(type name, spelling, declaring file, line) for every HOLDER the
    preprocessor wrote, in the order it wrote them."""
    checkout_root = declaring_file_path(checkout, "clang/include/clang/AST/Type.h")
    checkout_root = checkout_root[: -len("clang/include/clang/AST/Type.h")]
    found = []
    current_file = ""
    current_line = 0
    for output_line in expanded.split("\n"):
        marker = CLANG_LINE_MARKER.match(output_line)
        if marker is not None:
            current_line = int(marker.group(1))
            current_file = marker.group(2)
            continue
        for holder in CLANG_HOLDER.finditer(output_line):
            name = holder.group(1)
            pieces = CLANG_STRING.findall(holder.group(2))
            spelling = "".join(pieces)
            relative = current_file
            if relative.startswith(checkout_root):
                relative = relative[len(checkout_root):]
            found.append((name, spelling, relative, current_line))
        current_line += 1
    return found


def read_clang_types(lang: str, declaration: Declaration) -> tuple:
    """clang's builtin types: every entry of BuiltinType::Kind, each with
    every spelling its printer gives it."""
    enum_relative = declaration.files[0]
    printer_relative = declaration.files[1]
    included = read_clang_enum(declaration.checkout, enum_relative)
    spelled_by_case, spelled_by_template = read_clang_printer(declaration.checkout, printer_relative)
    text = clang_preprocessor_input(included, spelled_by_template)
    expanded = run_clang_preprocessor(declaration.checkout, text)
    holders = []
    for name, spelling, declared_in, line in read_clang_holder_lines(declaration.checkout, expanded):
        declared_at = f"{declared_in}:{line}"
        if spelling:
            template = spelled_by_template[declared_in.split("include/", 1)[-1]]
            source = f"{declared_at}, spelled at {printer_relative}:{template[3]}"
            holder = Holder(lang, name, spelling, source)
            holders.append(holder)
            continue
        spelled = spelled_by_case.get(name)
        if not spelled:
            message = f"read_holders: clang declares {name} but its printer does not spell it"
            raise LookupError(message)
        for case_spelling, printer_line in spelled:
            source = f"{declared_at}, spelled at {printer_relative}:{printer_line}"
            holder = Holder(lang, name, case_spelling, source)
            holders.append(holder)
    declared = tuple(holders)
    return declared


# go's compiler declares its predeclared types in
# src/cmd/compile/internal/types2/universe.go: the basic types as a table,
#
#     Int8:          {Int8, IsInteger, "int8"},
#
# the two aliases as another,
#
#     {Byte, IsInteger | IsUnsigned, "byte"},
#
# and the named ones in code, `NewTypeName(nopos, nil, "error", nil)`. The
# string is the name a program writes. The untyped kinds are in the table
# too; no program can write one, and the judge says so.
GO_BASIC = re.compile(r'^\t(\w+):\s*\{\w+,\s*[^,]*,\s*"([^"]+)"\},')
GO_ALIAS = re.compile(r'^\t\{(\w+),\s*[^,]*,\s*"([^"]+)"\},')
GO_NAMED = re.compile(r'NewTypeName\(nopos, nil, "(\w+)"')


def read_go_types(lang: str, declaration: Declaration) -> tuple:
    """go's predeclared types: the basic table, the aliases, the named."""
    relative = declaration.files[0]
    path = declaring_file_path(declaration.checkout, relative)
    holders = []
    with open(path, encoding="utf-8") as declaring_file:
        for line_number, line in enumerate(declaring_file, start=1):
            source = f"{relative}:{line_number}"
            basic = GO_BASIC.match(line)
            if basic is not None:
                holders.append(Holder(lang, basic.group(1), basic.group(2), source))
                continue
            alias = GO_ALIAS.match(line)
            if alias is not None:
                holders.append(Holder(lang, alias.group(1), alias.group(2), source))
                continue
            named = GO_NAMED.search(line)
            if named is not None:
                holders.append(Holder(lang, named.group(1), named.group(1), source))
    declared = tuple(holders)
    return declared


# The go the judge runs is go1.26.0, whose own source is in the runner image
# at /usr/lib/go-1.26/src; read with PSEUDOIR_SOURCES=/usr/lib.
GO_TYPES = Declaration(
    checkout="go-1.26",
    files=("src/cmd/compile/internal/types2/universe.go",),
    parse=read_go_types,
)


# rustc names its primitive types in compiler/rustc_hir/src/hir.rs,
# `PrimTy::from_name`, the one place a written name becomes a type:
#
#     sym::i8 => Self::Int(IntTy::I8),
#
# The name after `sym::` is the spelling a program writes.
RUST_FROM_NAME_START = "    pub fn from_name(name: Symbol) -> Option<Self> {"
RUST_FROM_NAME_ARM = re.compile(r"^\s+sym::(\w+) => Self::(\w+)(?:\(\w+::(\w+)\))?,")


def read_rust_types(lang: str, declaration: Declaration) -> tuple:
    """rust's primitive types, from PrimTy::from_name."""
    relative = declaration.files[0]
    path = declaring_file_path(declaration.checkout, relative)
    holders = []
    inside = False
    with open(path, encoding="utf-8") as declaring_file:
        for line_number, line in enumerate(declaring_file, start=1):
            if not inside:
                inside = line.rstrip("\n") == RUST_FROM_NAME_START
                continue
            if line.startswith("    }"):
                break
            arm = RUST_FROM_NAME_ARM.match(line)
            if arm is None:
                continue
            name = arm.group(3) or arm.group(2)
            holders.append(Holder(lang, name, arm.group(1), f"{relative}:{line_number}"))
    declared = tuple(holders)
    return declared


RUST_TYPES = Declaration(
    checkout="rust-1.96.1",
    files=("compiler/rustc_hir/src/hir.rs",),
    parse=read_rust_types,
)


# python's types are asked of the interpreter too: every name in `builtins`
# whose value is a type. The name is the spelling.
def read_python_types(lang: str, declaration: Declaration) -> tuple:
    """python's built-in types, from the running interpreter."""
    import builtins
    import sys
    version = sys.version.split()[0]
    if declaration.checkout != f"python-{version}":
        message = f"read_holders: python must be read by the python that judges ({declaration.checkout}); this is {version}"
        raise LookupError(message)
    holders = []
    for name in sorted(dir(builtins)):
        value = getattr(builtins, name)
        if isinstance(value, type):
            holders.append(Holder(lang, name, name, f"builtins.{name} (Python {version})"))
    declared = tuple(holders)
    return declared


PYTHON_TYPES = Declaration(
    checkout="python-3.13.15",
    files=(),
    parse=read_python_types,
)


# javac names its primitive types, and each one's box class, in
# com/sun/tools/javac/code/Symtab.java, `initType(intType, "int", "Integer")`.
# Its operator table (comp/Operators.java) is declared over those and over
# the class types it names as `syms.stringType` and kin, which Symtab enters
# as `stringType = enterClass("java.lang.String")`. Those are the holders.
JAVA_INIT_TYPE = re.compile(r'^\s+initType\((\w+), "([^"]+)"(?:, "(\w+)")?\);')
JAVA_OPERATOR_TYPE = re.compile(r"\bsyms\.(\w+Type)\b")
JAVA_ENTER_CLASS = re.compile(r'^\s+(\w+Type) = enterClass\("([\w.]+)"\);')


def read_java_types(lang: str, declaration: Declaration) -> tuple:
    """java's holders: the primitives and their boxes, and the class types
    javac's operator table is declared over."""
    symtab_file, operators_file = declaration.files
    holders = []
    initialized = set()
    entered = {}
    with open(declaring_file_path(declaration.checkout, symtab_file), encoding="utf-8") as symtab:
        for line_number, line in enumerate(symtab, start=1):
            init = JAVA_INIT_TYPE.match(line)
            if init is not None:
                source = f"{symtab_file}:{line_number}"
                holders.append(Holder(lang, init.group(1), init.group(2), source))
                initialized.add(init.group(1))
                if init.group(3):
                    holders.append(Holder(lang, f"{init.group(1)} box", f"java.lang.{init.group(3)}", source))
                continue
            enter = JAVA_ENTER_CLASS.match(line)
            if enter is not None:
                entered[enter.group(1)] = (enter.group(2), line_number)
    named = []
    with open(declaring_file_path(declaration.checkout, operators_file), encoding="utf-8") as operators_source:
        for match in JAVA_OPERATOR_TYPE.finditer(operators_source.read()):
            if match.group(1) not in named:
                named.append(match.group(1))
    for type_name in named:
        if type_name in initialized or type_name not in entered:
            continue
        spelling, line_number = entered[type_name]
        holders.append(Holder(lang, type_name, spelling, f"{symtab_file}:{line_number}, named in {operators_file}"))
    declared = tuple(holders)
    return declared


JAVA_TYPES = Declaration(
    checkout="jdk-25.0.4",
    files=(
        "src/jdk.compiler/share/classes/com/sun/tools/javac/code/Symtab.java",
        "src/jdk.compiler/share/classes/com/sun/tools/javac/comp/Operators.java",
    ),
    parse=read_java_types,
)


# The clang the judge runs is 21.1.8, so the declaring files are 21.1.8's:
# a type one version declares and the other lacks would otherwise read as
# the language refusing it.
CLANG_TYPES = Declaration(
    checkout="llvm-project-21.1.8",
    files=(
        "clang/include/clang/AST/Type.h",
        "clang/lib/AST/Type.cpp",
    ),
    parse=read_clang_types,
)

# One entry per language: the checkout, the declaring files, and the parse
# that reads them. The parse is the spelling of the files and nothing else.
DECLARATIONS = {
    "c": CLANG_TYPES,
    "cpp": CLANG_TYPES,
    "go": GO_TYPES,
    "rust": RUST_TYPES,
    "python": PYTHON_TYPES,
    "java": JAVA_TYPES,
}


CLANG_TYPE_NODE = re.compile(r"^\s*def\s+(\w+)\s*:\s*TypeNode<\s*(\w+)\s*(?:,\s*(1))?\s*>")
CLANG_TYPE_NODES_TD = "clang/include/clang/Basic/TypeNodes.td"


def read_type_constructors(lang: str) -> tuple:
    """Every concrete type-constructor AST node the lowerer declares in
    clang/include/clang/Basic/TypeNodes.td, as (node_name, base_name, source)."""
    declaration = declaration_of(DECLARATIONS, lang, "read_type_constructors")
    if declaration.checkout != "llvm-project-21.1.8":
        return ()
    path = declaring_file_path(declaration.checkout, CLANG_TYPE_NODES_TD)
    constructors = []
    with open(path, encoding="utf-8") as td_file:
        for line_number, line in enumerate(td_file, start=1):
            match = CLANG_TYPE_NODE.match(line)
            if match is None or match.group(3) == "1":
                continue
            node_name = match.group(1) + "Type"
            base_name = match.group(2)
            constructors.append((node_name, base_name, f"{CLANG_TYPE_NODES_TD}:{line_number}"))
    return tuple(constructors)


def read_holders(lang: str) -> tuple:
    """Every Holder `lang`'s lowerer declares, in the order it declares
    them. Refuses by name when a source is not on disk."""
    declaration = declaration_of(DECLARATIONS, lang, "read_holders")
    holders = declaration.parse(lang, declaration)
    return holders


def sources(lang: str) -> tuple:
    """The files read for `lang`, so a run is attributable to a version of
    the lowerer rather than to the language's name."""
    declaration = declaration_of(DECLARATIONS, lang, "read_holders")
    paths = []
    for relative in declaration.files:
        path = declaring_file_path(declaration.checkout, relative)
        paths.append(path)
    read = tuple(paths)
    return read


# ADJACENT, NOT YET CODED:
#
#   The lists hold more than holders: clang's placeholder types, java's
#   BOT, dart's Object, V8's Hole. This reader reports them all. A type no
#   program can hold a value of drops out when the grid is judged, and
#   that is the lowerer's call, not ours.
#
#   The type constructors are holders too: pointer, array, vector,
#   `_Complex`, `_Atomic`, `_BitInt(N)`, struct and enum, declared in
#   clang/include/clang/Basic/TypeNodes.td. Each builds a holder from another
#   holder and a number or a nesting, so there is no finite list to read.
#   The rule for which to take is still open; the owner's lead is to model
#   the primitive holders first and build the structures from them.
#
#   Nullable holders are made, not listed: dart `int?`, csharp `int?`,
#   swift `Int?`. The lowerer builds each from a listed type by its own
#   rule. The dict has none today, which is why dart's `a ?? b` and `a!`
#   came out as identities. Where each language declares that rule is
#   still to be read.
