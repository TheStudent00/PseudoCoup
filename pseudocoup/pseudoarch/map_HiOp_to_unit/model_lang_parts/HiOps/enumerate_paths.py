"""enumerate_paths -- every holder context of one HiOp traced, the contexts
grouped by identical path, and for each path the tests at which it parts
from the others, with the holder each test reads (PCHQ plan:
research/trace_logical_paths/enumerate_paths).

    variants = enumerate_paths(paths)

A test is where two paths part: the last branch both took before their
steps differ, with the frames open there, each with the last branch it took
itself (the test is decided in the innermost of clang's own frames; the
check names it). Every context whose path takes the same steps up to the
test reaches it, and takes one of its sides; a test reads a holder when two
of those contexts that differ in that holder alone take different sides.
Each variant, with its holders, is one HiOp variant's lowering.

The paths are compared in the order of their signatures, so that each
parting needs only the common prefix of two neighbours: the paths form a
tree, the parting points along one path are the shortest common prefixes
it has with the paths on either side of it, and the contexts that reach a
test are a run of neighbours.
"""

from typing import NamedTuple

from ...lang_models.gnu_c.trace.logical_path import KIND_CODE, KIND_OF_CODE, STEP, signature, step_columns

SEPARATOR = KIND_CODE["separator"]
ENTER = KIND_CODE["enter"]
RETURN = KIND_CODE["return"]
BRANCH = KIND_CODE["branch"]


class Test(NamedTuple):
    offset: int
    sides: tuple
    holders: tuple
    frames: tuple


class Variant(NamedTuple):
    signature: bytes
    paths: list
    exits: tuple
    tests: list


def group_paths(paths: list) -> list:
    """The paths grouped by signature, in signature order."""
    groups = {}
    for path in paths:
        key = signature(path)
        if key not in groups:
            groups[key] = []
        groups[key].append(path)
    keys = sorted(groups)
    variants = []
    for key in keys:
        first = groups[key][0]
        variants.append(Variant(key, groups[key], first.exits, []))
    return variants


def common_steps(a: bytes, b: bytes) -> int:
    """How many steps two signatures share from their start."""
    low = 0
    high = min(len(a), len(b)) // STEP.size
    while low < high:
        middle = (low + high + 1) // 2
        size = middle * STEP.size
        if a[:size] == b[:size]:
            low = middle
        else:
            high = middle - 1
    return low


def last_branch_before(steps, index: int) -> int:
    """The offset of the last branch among steps[:index], or 0 (`steps`
    packed: logical_path.step_columns)."""
    kinds = steps.kinds
    offsets = steps.offsets
    position = index - 1
    while position >= 0:
        if kinds[position] == BRANCH:
            return offsets[position]
        position -= 1
    return 0


def open_frames(steps, index: int) -> tuple:
    """The frames open at steps[index], outermost first, each as (its entry's
    offset, the offset of the last branch it took itself before index, or 0).
    A branch is a frame's own when the frame's function holds it (the step's
    owner); a function's first branch is recorded just before its entry.
    `steps` packed (logical_path.step_columns), read as its arrays."""
    kinds = steps.kinds
    offsets = steps.offsets
    owners = steps.owners
    frames = []
    for position in range(index):
        kind = kinds[position]
        if kind == SEPARATOR:
            frames = []
        elif kind == ENTER:
            first = 0
            if position > 0 and kinds[position - 1] == BRANCH and owners[position - 1] == offsets[position]:
                first = offsets[position - 1]
            frames.append([offsets[position], first])
        elif kind == RETURN:
            if frames:
                frames.pop()
        elif kind == BRANCH:
            if frames and frames[-1][0] == owners[position]:
                frames[-1][1] = offsets[position]
    found = []
    for entry, branch in frames:
        found.append((entry, branch))
    return tuple(found)


def differing_parts(a, b) -> list:
    """The parts in which two holder contexts differ. A part one context
    has and the other lacks differs (the vocabulary holds one name with
    two part counts, `__arithmetic_fence`; run fable1_l10)."""
    parts = []
    shared = min(len(a), len(b))
    for position in range(shared):
        if a[position] != b[position]:
            parts.append(position)
    for position in range(shared, max(len(a), len(b))):
        parts.append(position)
    return parts


def reaching(index: int, length: int, prefixes: list) -> tuple:
    """The variants that take the first `length` steps of variant `index`: a
    run of neighbours in signature order, as (first, last)."""
    first = index
    while first > 0 and prefixes[first - 1] >= length:
        first -= 1
    last = index
    while last < len(prefixes) and prefixes[last] >= length:
        last += 1
    found = (first, last)
    return found


def side_at(variant: Variant, length: int) -> bytes:
    """The step a variant takes after its first `length`: its side of the
    test there (empty at the path's end)."""
    side = variant.signature[length * STEP.size:(length + 1) * STEP.size]
    return side


def holders_read_at(variants: list, run: tuple, length: int) -> tuple:
    """The parts whose holder alone moves a context from one side of the
    test to another, among the contexts that reach it."""
    first, last = run
    parts = []
    for one in range(first, last + 1):
        for other in range(one + 1, last + 1):
            if side_at(variants[one], length) == side_at(variants[other], length):
                continue
            for a in variants[one].paths:
                for b in variants[other].paths:
                    differing = differing_parts(a.context.holders, b.context.holders)
                    if len(differing) == 1 and differing[0] not in parts:
                        parts.append(differing[0])
    parts.sort()
    found = tuple(parts)
    return found


def parting_test(index: int, partner: int, variants: list, prefixes: list, steps_by_variant: dict, read: dict) -> Test:
    """The test at which two variants' paths part."""
    first = variants[index]
    second = variants[partner]
    shared = common_steps(first.signature, second.signature)
    if index not in steps_by_variant:
        steps_by_variant[index] = step_columns(first.paths[0])
    if partner not in steps_by_variant:
        steps_by_variant[partner] = step_columns(second.paths[0])
    first_steps = steps_by_variant[index]
    second_steps = steps_by_variant[partner]
    offset = last_branch_before(first_steps, shared)
    sides = []
    for steps in (first_steps, second_steps):
        if shared < len(steps):
            sides.append((KIND_OF_CODE[steps.kinds[shared]], steps.offsets[shared]))
        else:
            sides.append(("end", 0))
    run = reaching(index, shared, prefixes)
    key = (run[0], run[1], shared)
    if key not in read:
        read[key] = holders_read_at(variants, run, shared)
    test = Test(offset, tuple(sides), read[key], open_frames(first_steps, shared))
    return test


def neighbour_prefixes(variants: list) -> list:
    """The common steps of each variant with the next one in signature
    order."""
    prefixes = []
    for index in range(len(variants) - 1):
        prefixes.append(common_steps(variants[index].signature, variants[index + 1].signature))
    return prefixes


def partners_of(index: int, variants: list, prefixes: list) -> list:
    """For one variant, one other variant at each point where its path parts
    from another: walking outwards in signature order, the common prefix
    only shrinks, and each new, shorter prefix is a parting point."""
    partners = []
    seen = []
    shortest = None
    position = index
    while position > 0:
        prefix = prefixes[position - 1]
        if shortest is None or prefix < shortest:
            shortest = prefix
        if shortest not in seen:
            seen.append(shortest)
            partners.append(position - 1)
        position -= 1
    shortest = None
    position = index
    while position < len(variants) - 1:
        prefix = prefixes[position]
        if shortest is None or prefix < shortest:
            shortest = prefix
        if shortest not in seen:
            seen.append(shortest)
            partners.append(position + 1)
        position += 1
    return partners


def enumerate_paths(paths: list) -> list:
    """The variants of one HiOp's paths, each with its parting tests."""
    variants = group_paths(paths)
    prefixes = neighbour_prefixes(variants)
    steps_by_variant = {}
    read = {}
    for index in range(len(variants)):
        for partner in partners_of(index, variants, prefixes):
            variants[index].tests.append(parting_test(index, partner, variants, prefixes, steps_by_variant, read))
    return variants
