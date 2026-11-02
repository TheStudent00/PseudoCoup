"""ways -- every way a lowerer's write-back code can run, each as the pieces
it writes. Shared by every lowerer: nothing here names a language.

A lowerer's module hands the walker the code of one function, read into
`Code` by the reader for the language the lowerer is written in
(cpp_code.py for clang), and a `Table` saying what its calls and writes mean.

A way is one run through the function, start to end:

    choice   if / else, `? :`, switch: each arm is its own way, unless the
             way has already decided it -- by the list entry it chose, or by
             a value it set
    repeat   a loop: 0, 1 or 2 times, each its own way -- or, when the list
             entry the way chose says how many times, that many
    lookup   a name from one of the lowerer's lists: each entry is its own
             way, chosen once and kept for every later use in that way
    follow   a call that hands the same node to another function of the
             same file: that function is walked in place
    piece    fixed text, an operand, a type, or a name

A way keeps every choice it made: a condition met again is decided the same
way, until the way sets a variable the condition reads.

A way stops, with its reason, at the first call or write the table does not
know. Three rules keep one way from being counted more than once, and none
of them compares what the ways write:

    a choice between writing spaces and writing nothing is not a choice:
    the arm that writes nothing is taken
    arms of a choice that write nothing and set nothing are one way
    a repeat that writes nothing and sets nothing is not counted
"""

import re
from typing import Callable, NamedTuple

# A loop is walked 0, 1 and 2 times: 2 is the fewest that shows what a
# repeat writes between two of its turns.
REPEATS = 2


class Code(NamedTuple):
    """One statement or expression of a lowerer's source.

    `form` says what it is (see FORMS), `text` is its source text with its
    whitespace collapsed, `parts` holds what it is made of, and `line` is
    where it starts."""

    form: str
    text: str
    parts: tuple
    line: int


FORMS = {
    # statements
    "block": "(statement, ...)",
    "do": "(expression,): an expression run for what it does",
    "declare": "((name, type, value or None), ...)",
    "if": "(condition, then, otherwise or None)",
    "switch": "(subject, (case, ...)); a case is Code('case', ..., (labels or None for default, statements))",
    "loop": "(counter name or '', body, fewest turns, what the counter runs up to or None)",
    "return": "()", "break": "()", "continue": "()", "empty": "()",
    "unread": "(): a statement the reader has no shape for",
    # expressions
    "text": "(the text a literal stands for,)",
    "number": "(digits,)", "truth": "(True or False,)", "nothing": "()",
    "name": "(identifier,)",
    "not": "(expression,)", "and": "(left, right)", "or": "(left, right)",
    "compare": "(operator, left, right)",
    "choose": "(condition, then, otherwise): `? :`",
    "call": "(callee, (argument, ...))",
    "member": "(object, field name)",
    "assign": "(target, value)",
    "binary": "(operator, left, right)",
    "declared": "(declare,): a condition that declares a name and tests it",
    "other": "()",
}


class Entry(NamedTuple):
    """One entry of one of the lowerer's lists."""

    name: str        # the lowerer's name for it: Mul, PostInc, SizeOf
    spelling: str    # the text written for it: *, ++, sizeof
    label: str       # how the lowerer's code names it in a comparison or a case: BO_Mul
    source: str      # file:line where it is declared


class Table(NamedTuple):
    """What one lowerer's write-back code means, for the walker.

        statement(code, way)  the effects of one expression run as a
                              statement, or None when the table does not
                              know it. An effect is ("write", items),
                              ("piece", piece) or ("follow", Code).
        item(code, way)       the piece one written item gives, or None
        lookup(code)          (what it is keyed on, its entries) for a call
                              that writes a name from one of the lists,
                              else None
        decide(code, way)     True or False for a condition the table can
                              decide from the entries the way chose, else
                              None
        follow(code)          the Code of the function a call hands the
                              same node to, else None
        turns(code, way)      (fewest, most) turns for a loop whose counter
                              runs up to `code`, when the table can say from
                              the entries the way chose; `most` None means
                              REPEATS more than the fewest. Else None.
    """

    statement: Callable
    item: Callable
    lookup: Callable
    decide: Callable
    follow: Callable
    turns: Callable = None


class Way(NamedTuple):
    """One run through the code, so far or to its end."""

    pieces: tuple    # ("text", s), ("operand",), ("type",), ("name",)
    chosen: tuple    # (what it is keyed on, Entry) for each list entry chosen
    taken: tuple     # (condition or loop, how it went) for each choice and repeat, for the record
    values: tuple    # (variable, value) the way has set: text, truth or number
    types: tuple     # (variable, declared type)
    status: str      # "" while running; "return", "break", "continue"; "stop"
    reason: str      # why the way stopped, when status is "stop"
    decided: tuple = ()   # (condition, True or False) for each choice the way made


class TooManyWays(Exception):
    """A function has more ways than the walker was asked to hold."""


def ways_of(body: Code, table: Table, limit: int) -> tuple:
    """(ways, reason): every way through the function `body`, or no ways and
    the reason when any one choice of list entries has more than `limit`.
    The list entries a way uses are chosen before it starts, so a condition
    met before the name is written is decided by the same entry."""
    walker = Walker(table, limit)
    walker.lists = lists_used(body, table)
    starts = [Way((), (), (), (), (), "", "")]
    for keyed_on, entries in walker.lists.items():
        chosen = []
        for way in starts:
            for entry in entries:
                chosen.append(way._replace(chosen=way.chosen + ((keyed_on, entry),)))
        starts = chosen
    finished = []
    try:
        for start in starts:
            ended = walker.walk(body, start)
            walker.count(len(ended))
            for way in ended:
                if way.status == "return":
                    way = way._replace(status="")
                finished.append(way)
    except TooManyWays:
        return (), f"its code has more than {limit} runs through it for one choice of list entries"
    return tuple(finished), None


def lists_used(body: Code, table: Table) -> dict:
    """keyed on -> entries, for every lookup in `body` and in the functions
    it follows, in the order first met."""
    found = {}
    seen = set()
    pending = [body]
    while pending:
        code = pending.pop(0)
        if not isinstance(code, Code) or id(code) in seen:
            continue
        seen.add(id(code))
        looked = table.lookup(code)
        if looked is not None and looked[0] not in found:
            found[looked[0]] = looked[1]
        followed = table.follow(code)
        if followed is not None:
            pending.append(followed)
        pending.extend(inner_codes(code))
    return found


def inner_codes(code: Code) -> list:
    """Every Code directly inside `code`'s parts, however nested in tuples."""
    inner = []
    stack = list(code.parts)
    while stack:
        part = stack.pop(0)
        if isinstance(part, Code):
            inner.append(part)
        elif isinstance(part, tuple):
            stack[0:0] = list(part)
    return inner


class Walker:
    """Walks one function's ways for one table. An instance, because every
    step of the walk reads the same three things (the table, the bound and
    the lists), and handing all three to every step is the only change a
    module of functions would make."""

    def __init__(self, table: Table, limit: int):
        self.table = table
        self.limit = limit
        self.lists = {}

    def count(self, ways: int) -> None:
        if ways > self.limit:
            raise TooManyWays()

    # statements

    def walk(self, code: Code, way: Way) -> list:
        """Every way `code` can run from `way`."""
        if way.status:
            return [way]
        form = code.form
        if form == "block":
            ways = [way]
            for statement in code.parts:
                after = []
                for current in ways:
                    after.extend(self.walk(statement, current))
                self.count(len(after))
                ways = after
            return ways
        if form in ("empty",):
            return [way]
        if form in ("return", "break", "continue"):
            return [way._replace(status=form)]
        if form == "declare":
            return [self.declare(code, way)]
        if form == "do":
            return self.run(code.parts[0], way)
        if form == "if":
            return self.choose(code, way)
        if form == "switch":
            return self.switch(code, way)
        if form == "loop":
            return self.repeat(code, way)
        return [stopped(way, f"its code has a statement the reader has no shape for: `{short(code.text)}`")]

    def declare(self, code: Code, way: Way) -> Way:
        values = dict(way.values)
        types = dict(way.types)
        for name, declared_type, value in code.parts:
            types[name] = declared_type
            known = self.value(value, way) if value is not None else None
            if known is None:
                values.pop(name, None)
            else:
                values[name] = known
            way = forget(way, name)
        declared = way._replace(values=tuple(values.items()), types=tuple(types.items()))
        return declared

    def run(self, expression: Code, way: Way) -> list:
        """An expression run as a statement: an assignment, or whatever the
        table says it does."""
        if expression.form == "assign":
            target, value = expression.parts
            if target.form != "name":
                return [stopped(way, f"its code assigns to `{short(target.text)}`")]
            values = dict(way.values)
            known = self.value(value, way)
            if known is None:
                values.pop(target.parts[0], None)
            else:
                values[target.parts[0]] = known
            return [forget(way, target.parts[0])._replace(values=tuple(values.items()))]
        effects = self.table.statement(expression, way)
        if effects is None:
            return [stopped(way, f"its code calls `{short(expression.text)}`")]
        ways = [way]
        for effect in effects:
            after = []
            for current in ways:
                after.extend(self.apply(effect, current))
            ways = after
        return ways

    def apply(self, effect: tuple, way: Way) -> list:
        if way.status:
            return [way]
        if effect[0] == "piece":
            return [add(way, effect[1])]
        if effect[0] == "follow":
            # The followed function has its own names: the caller's are put
            # back when it returns. A third part declares names inside it.
            declared = effect[2] if len(effect) > 2 else ()
            inside = way._replace(values=(), types=declared)
            returned = []
            for result in self.walk(effect[1], inside):
                if result.status == "return":
                    result = result._replace(status="")
                returned.append(result._replace(values=way.values, types=way.types))
            return returned
        ways = [way]
        for item in effect[1]:
            after = []
            for current in ways:
                after.extend(self.write(item, current))
            ways = after
        return ways

    def write(self, item: Code, way: Way) -> list:
        """The piece one written item gives, forking where the item chooses."""
        if way.status:
            return [way]
        if item.form == "choose":
            condition, then, otherwise = item.parts
            decided = self.truth(condition, way)
            if decided is True:
                return self.write(then, way)
            if decided is False:
                return self.write(otherwise, way)
            yes = self.write(then, took(way, condition, "yes", True))
            no = self.write(otherwise, took(way, condition, "no", False))
            return yes + no
        value = self.value(item, way)
        if isinstance(value, str):
            return [add(way, ("text", value))]
        if isinstance(value, int) and not isinstance(value, bool):
            return [add(way, ("text", str(value)))]
        piece = self.table.item(item, way)
        if piece is not None:
            return [add(way, piece)]
        return [stopped(way, f"its code writes `{short(item.text)}`")]

    def choose(self, code: Code, way: Way) -> list:
        condition, then, otherwise = code.parts
        if condition.form == "declared":
            # `if (auto *X = e)` holds when e does: the table may decide e.
            declaration = condition.parts[0]
            way = self.declare(declaration, way)
            values = [value for _name, _type, value in declaration.parts if value is not None]
            decided = self.truth(values[0], way) if len(values) == 1 else None
        else:
            decided = self.truth(condition, way)
        if decided is True:
            return self.walk(then, way)
        if decided is False:
            return self.walk(otherwise, way) if otherwise is not None else [way]
        yes_start = took(way, condition, "yes", True)
        no_start = took(way, condition, "no", False)
        yes = self.walk(then, yes_start) if not self.writes_only_spaces(then, way) else [yes_start]
        if otherwise is not None and not self.writes_only_spaces(otherwise, way):
            no = self.walk(otherwise, no_start)
        else:
            no = [no_start]
        silent = [result for result in yes + no
                  if result.status == way.status and wrote_and_set_nothing(way, result)]
        if len(silent) < 2:
            return yes + no
        # Arms that wrote nothing and set nothing are one way, and that way
        # made no choice here.
        kept = []
        for result in yes + no:
            if result is silent[0]:
                result = result._replace(taken=way.taken + ((short(condition.text), "either"),),
                                         decided=way.decided)
            elif any(result is other for other in silent):
                continue
            kept.append(result)
        return kept

    def writes_only_spaces(self, code: Code, way: Way) -> bool:
        """Whether `code` does nothing but write spaces."""
        if code.form == "block":
            return bool(code.parts) and all(self.writes_only_spaces(part, way) for part in code.parts)
        if code.form != "do":
            return False
        effects = self.table.statement(code.parts[0], way)
        if not effects:
            return False
        for effect in effects:
            if effect[0] != "write":
                return False
            for item in effect[1]:
                if item.form == "text" and item.parts[0].strip(" ") == "":
                    continue
                piece = self.table.item(item, way) if item.form != "text" else None
                if piece is not None and piece[0] == "text" and piece[1].strip() == "":
                    continue
                return False
        return True

    def switch(self, code: Code, way: Way) -> list:
        subject, cases = code.parts
        groups = merged_cases(cases)
        entry = chosen_entry(way, subject.text)
        if entry is not None:
            start = None
            for index, (labels, _statements) in enumerate(groups):
                if labels is not None and any(label.text == entry.label for label in labels):
                    start = index
                    break
            if start is None:
                start = next((index for index, (labels, _s) in enumerate(groups) if labels is None), None)
            if start is None:
                return [way]
            return [unbreak(result) for result in self.walk_from(groups, start, way)]
        results = []
        for index, (labels, _statements) in enumerate(groups):
            how = "default" if labels is None else "case " + " ".join(label.text for label in labels)
            results.extend(unbreak(result) for result in self.walk_from(groups, index, took(way, subject, how)))
        if all(labels is not None for labels, _statements in groups):
            results.append(took(way, subject, "no case"))
        return results

    def walk_from(self, groups: list, start: int, way: Way) -> list:
        """The statements of case `start` and of every case after it, as a
        switch runs them until a break."""
        statements = []
        for _labels, group_statements in groups[start:]:
            statements.extend(group_statements)
        block = Code("block", "", tuple(statements), 0)
        return self.walk(block, way)

    def repeat(self, code: Code, way: Way) -> list:
        counter, body, fewest, bound = code.parts
        most = REPEATS
        decided = None
        if bound is not None and self.table.turns is not None:
            decided = self.table.turns(bound, way)
        if decided is not None:
            fewest = max(fewest, decided[0])
            most = decided[1] if decided[1] is not None else fewest + REPEATS
        finished = []
        current = [way]
        for turns in range(most + 1):
            if turns >= fewest:
                for ended in current:
                    finished.append(took(ended, code, f"{turns} times"))
            if turns == most:
                break
            following = []
            for start in current:
                if counter:
                    values = dict(start.values)
                    values[counter] = turns
                    start = forget(start, counter)._replace(values=tuple(values.items()))
                for result in self.walk(body, start):
                    if result.status == "continue":
                        result = result._replace(status="")
                    if result.status in ("", "break") and wrote_and_set_nothing(start, result):
                        continue
                    if result.status == "break":
                        finished.append(took(result._replace(status=""), code, f"{turns + 1} times, left early"))
                        continue
                    if result.status:
                        finished.append(result)
                        continue
                    following.append(result)
            self.count(len(following) + len(finished))
            current = following
        return finished

    # expressions

    def value(self, code: Code, way: Way):
        """The text, truth or number an expression stands for, when the way
        knows it; else None."""
        form = code.form
        if form == "text":
            return code.parts[0]
        if form == "truth":
            return code.parts[0]
        if form == "number":
            digits = code.parts[0].rstrip("uUlL")
            if digits.isdigit():
                return int(digits, 10)
            return None
        if form == "name":
            return dict(way.values).get(code.parts[0])
        if form == "choose":
            decided = self.truth(code.parts[0], way)
            if decided is None:
                return None
            return self.value(code.parts[1] if decided else code.parts[2], way)
        looked = self.table.lookup(code)
        if looked is not None:
            entry = chosen_entry(way, looked[0])
            return entry.spelling if entry is not None else None
        return None

    def truth(self, code: Code, way: Way):
        """True or False when the way can decide `code`, else None."""
        for condition, outcome in way.decided:
            if condition == code.text:
                return outcome
        form = code.form
        if form == "truth":
            return code.parts[0]
        if form == "nothing":
            return False
        if form in ("number", "name"):
            value = self.value(code, way)
            if value is None:
                return None
            return bool(value)
        if form == "not":
            inner = self.truth(code.parts[0], way)
            return None if inner is None else not inner
        if form in ("and", "or"):
            left = self.truth(code.parts[0], way)
            right = self.truth(code.parts[1], way)
            if form == "and":
                if left is False or right is False:
                    return False
                return True if left is True and right is True else None
            if left is True or right is True:
                return True
            return False if left is False and right is False else None
        if form == "compare":
            return self.compare(code, way)
        return self.table.decide(code, way)

    def compare(self, code: Code, way: Way):
        operator, left, right = code.parts
        if operator not in ("==", "!="):
            left_value = self.value(left, way)
            right_value = self.value(right, way)
            if not all(isinstance(value, int) and not isinstance(value, bool) for value in (left_value, right_value)):
                return None
            ordered = {"<": left_value < right_value, ">": left_value > right_value,
                       "<=": left_value <= right_value, ">=": left_value >= right_value}
            return ordered[operator]
        equal = None
        for keyed, other in ((left, right), (right, left)):
            entry = chosen_entry(way, keyed.text)
            if entry is None:
                continue
            labels = {listed.label for listed in self.lists.get(keyed.text, ())}
            if other.text == entry.label:
                equal = True
            elif other.text in labels:
                equal = False
        if equal is None:
            left_value = self.value(left, way)
            right_value = self.value(right, way)
            if left_value is None or right_value is None:
                return None
            equal = left_value == right_value
        return equal if operator == "==" else not equal


def merged_cases(cases: tuple) -> list:
    """(labels, statements) per case, with labels that share their
    statements joined: `case A: case B: s;` is one case of two labels."""
    groups = []
    pending = []
    for case in cases:
        labels, statements = case.parts
        if labels is None:
            if pending:
                groups.append((tuple(pending), ()))
                pending = []
            groups.append((None, statements))
            continue
        pending.extend(labels)
        if statements:
            groups.append((tuple(pending), statements))
            pending = []
    if pending:
        groups.append((tuple(pending), ()))
    return groups


def chosen_entry(way: Way, keyed_on: str):
    """The entry `way` chose for what `keyed_on` names, or None."""
    for key, entry in way.chosen:
        if key == keyed_on:
            return entry
    return None


def wrote_and_set_nothing(start: Way, result: Way) -> bool:
    """Whether `result` wrote nothing and set nothing since `start`."""
    same = (len(result.pieces) == len(start.pieces) and result.values == start.values
            and result.chosen == start.chosen)
    return same


def add(way: Way, piece: tuple) -> Way:
    return way._replace(pieces=way.pieces + (piece,))


def took(way: Way, code: Code, how: str, outcome=None) -> Way:
    """The way, with how it went at `code` recorded; and, for a condition,
    the outcome kept, so the same condition met again goes the same way."""
    way = way._replace(taken=way.taken + ((short(code.text), how),))
    if outcome is None:
        return way
    while code.form == "not":
        code = code.parts[0]
        outcome = not outcome
    return way._replace(decided=way.decided + ((code.text, outcome),))


def forget(way: Way, name: str) -> Way:
    """The way without the choices whose condition reads `name`."""
    reads = re.compile(rf"\b{re.escape(name)}\b")
    kept = tuple((condition, outcome) for condition, outcome in way.decided if not reads.search(condition))
    return way._replace(decided=kept)


def stopped(way: Way, reason: str) -> Way:
    return way._replace(status="stop", reason=reason)


def unbreak(way: Way) -> Way:
    return way._replace(status="") if way.status == "break" else way


def short(text: str) -> str:
    return text if len(text) <= 70 else text[:67] + "..."
