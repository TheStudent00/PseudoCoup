---
id: hq.projects.pseudocoup.pseudoarch.map_HiOp_to_unit.lower_HiOp.standard_HiOp_wrapper.support.standard_form_for_any_language
status: draft
---

# SUPPORT — standard_form_for_any_language

The standard-form for any language: how it forms around one HiOp, the HiOps it
holds, and the HiOps it must stand inside. Rules first, then code that is
close to an implementation but written to be read, in the form of PCHQ log
373.

Written by Claude (Opus 5.5) on 2026-10-09, first as §2 of
`Planning/CORE_0_0_0_pseudocoup.md, at
Dee's request:

> what might be useful is something like log 373 style. not perfectly literal
> but very descriptive and nearly actual code implementation. but
> descriptive-ness being the primary objective of it.

Put here at Dee's word, the same day (log 405):

> if you could please put that in a SUPPORT file in its proper node location,
> thatd be appreciated. i want to be able to reference it and perhaps use it
> to explain this idea later.

Whose is what:

- Dee's: the standard-form itself, a container the caller owns in place of the
  bare function (log 302); the inert parts (2026-10-08); the definition of a
  HiOp.
- Claude's: the five steps, the wording of the rules, and every name in
  Block A. None of the names is a sub-node.
- GNU C's code does all of it today: `DRY_mask_maker`, since log 405 (the
  last section).

## the rules

A HiOp is one operator of a language, with its holders (Dee's definition).
Every placeholder of its operator is one of three kinds of thing to the HiOp.
It is a value the HiOp reads. Or it is code the HiOp runs, which in a real
program is other HiOps. Or it is a name or a type the HiOp refers to.

- a standard source is the smallest program, in the HiOp's own language, in which
  the lowerer must write the HiOp's own words. the words are read at one
  symbol: the standard function's name.
- the container holds each value the HiOp reads in a field, and the HiOp's
  answer in a result field. the caller owns the container, so the lowerer
  cannot drop a write the caller can see (the standard-form, log 302).
- the standard function is given only a reference to the container.
- a control HiOp is a statement, or an expression whose parts run only on
  some paths (`a && b`, `a || b`, `a ? b : c`, `a ?: b`). its parts are held
  as inert calls: calls to functions declared and never defined, so the
  lowerer keeps each call and cannot see inside (Dee, 2026-10-08). a body's
  call answers nothing, so its holder never shows; a value's call answers the
  value read from its holder.
- a context is a HiOp that this HiOp can only stand inside: `break;` and
  `continue;` inside a loop, `case` inside a switch, `goto m;` beside its
  label, `goto *a;` beside a label whose address is taken. a context's own
  placeholders are held as parts, inert. the lowerer states each context in
  its own checks (clang: "'break' statement not in loop or switch
  statement").
- a part can need a context too: a switch's body is reached only through a
  case label, so it stands inside one.
- the standard function answers nothing, except for `return a;`: its function
  answers the value `a` reads (clang refuses a value returned from a function
  that answers nothing: "void function ... should not return a value").
- a jump needs reached code between it and its target. so every HiOp that
  jumps stands behind an inert test, with an inert call after it (logs 400,
  402, 405).
- an operand the lowerer must answer while compiling is written as a
  constant of the value its holder holds, where the HiOp reads it, and it has
  no field (logs 399, 405).
- an operand the lowerer accepts in only one form is written in that form (a
  flexible array member, log 402).
- the answer goes where the lowerer must write it: into the result field,
  whose type is the answer's own type as a field can take it. a HiOp that
  answers nothing stands as a statement. an answer the lowerer refuses to
  store is used the way the lowerer allows.
- the steps are the same for every language. each language gives one row of
  words, and the row decides nothing.

## the code

Block A. The standard-form for any language, in log 373's form. Descriptive
first: near an implementation, not one.

```python

"""
the standard-form, for any language

around one HiOp, it writes the smallest program in the HiOp's language in which
the lowerer must write the HiOp's own words, and it puts those words at one
symbol: the standard function's name
	* the steps are the same for every language
	* each language gives one LanguageRow: the words it writes each step in
	* GNU C's row is DRY_mask_maker.standard_cell_lines in log 405; since log 454, standard_HiOp_wrapper.standard_HiOp_wrapper
"""


def standard_HiOp_wrapper(row: LanguageRow, hiop: HiOp, key: str):
	held = Held(key)
	hold_each_placeholder(row, hiop, held)
	applied = apply_the_hiop(row, hiop, held)
	statement = keep_the_answer(row, hiop, held, applied)
	statement = stand_it_where_it_can_stand(row, hiop, held, statement)
	standard_source = write_the_held_source(row, hiop, held, statement)
	return standard_source


def hold_each_placeholder(row: LanguageRow, hiop: HiOp, held: Held):
	# each placeholder is held where the lowerer must keep it, by what it is to
	# the HiOp (its role): in a field the caller owns, or as an inert call
	for placeholder in hiop.placeholders:
		role = hiop.roles[placeholder]
		holder = hiop.holders.get(placeholder)
		text = hold_one_placeholder(row, hiop, held, placeholder, role, holder)
		held.text_of[placeholder] = text


def hold_one_placeholder(row, hiop, held, placeholder, role, holder):
	if role == "body":
		# code the HiOp runs: in a real program, other HiOps
		text = held.add_inert_part(row, placeholder, answers=row.nothing)
		# a body reached only through a label stands inside one (a switch's body)
		for context in hiop.part_contexts.get(placeholder, []):
			text = stand_inside(row, held, context, text)
	elif role == "value" and hiop.is_control:
		# a value a control HiOp reads (a test, a value it hands on): read from
		# an inert call, so the lowerer cannot know it and must keep the test
		text = held.add_inert_part(row, placeholder, answers=row.value_read(holder))
	elif role == "value":
		# a value an expression always reads: a field of the container
		text = held.add_field(row, placeholder, holder)
	elif role == "constant":
		# a value the lowerer must know while compiling (a case label, a size):
		# written where the HiOp reads it, so it has no field
		text = row.constant(row.value_read(holder))
	elif role == "one form only":
		# an operand the lowerer takes in one form only (a flexible array member)
		text = held.add_field_in_its_form(row, placeholder, holder)
	else:
		# a "name" (a label) or a "type" (sizeof's operand): written as it is
		text = row.as_written(placeholder, holder)
	return text


def apply_the_hiop(row: LanguageRow, hiop: HiOp, held: Held):
	# the HiOp's template, each placeholder replaced by the text it is held as
	applied = hiop.template.fill(held.text_of)
	return applied


def keep_the_answer(row: LanguageRow, hiop: HiOp, held: Held, applied):
	# the HiOp's answer goes where the lowerer must write it
	if hiop.is_statement:
		statement = applied                            # a statement answers nothing
	elif hiop.answers_nothing:
		statement = row.as_statement(applied)          # no field can hold nothing
	elif hiop.answer_may_not_be_stored:
		statement = row.store_through(applied)         # used as the lowerer allows
	else:
		held.add_result_field(row, row.result_type(hiop))
		statement = row.store_result(applied)
	return statement


def stand_it_where_it_can_stand(row: LanguageRow, hiop: HiOp, held: Held, statement):
	# a jump first: behind an inert test, an inert call after it, so the code
	# between the jump and its target is reached and the lowerer writes it
	if hiop.jumps:
		statement = jump_over_reached_code(row, held, statement)
	# then every HiOp it can only stand inside, innermost first, each with its
	# own placeholders held as inert parts
	for context in hiop.contexts:
		statement = stand_inside(row, held, context, statement)
	return statement


def jump_over_reached_code(row: LanguageRow, held: Held, statement):
	test = held.add_inert_part(row, "test", answers=row.truth)
	skipped = held.add_inert_part(row, "skipped", answers=row.nothing)
	guarded = row.when(test, statement) + row.call_as_statement(skipped)
	return guarded


def stand_inside(row: LanguageRow, held: Held, context: HiOp, statement):
	# the context's own placeholders are held as parts, inert, and the HiOp
	# goes where the context has room for it
	text_of = {}
	for placeholder in context.placeholders:
		if placeholder == context.where_the_hiop_goes:
			continue
		role = context.roles[placeholder]
		holder = context.holders.get(placeholder)
		text_of[placeholder] = hold_one_placeholder(row, context, held, placeholder, role, holder)
	text_of[context.where_the_hiop_goes] = statement
	surrounded = context.template.fill(text_of)
	return surrounded


def write_the_held_source(row: LanguageRow, hiop: HiOp, held: Held, statement):
	declarations = row.declare_never_defined(held.inert_parts)
	container = row.container(held.key, held.fields)
	answers = row.nothing
	if hiop.function_answers is not None:
		# `return a;`: the standard function answers the value its placeholder reads
		answers = row.type_of(held.text_of[hiop.function_answers])
	function = row.held_function(held.key, answers, statement)
	standard_source = StandardSource(row.join(declarations, container, function), row.symbol(held.key))
	return standard_source


class HiOp:
	"""
		one operator of a language, with its holders (Dee's definition). every
		field below is read from the lowerer, or from the language as the
		lowerer takes it, never written by hand: what each placeholder is, and
		where the HiOp may stand, are in the lowerer's own checks and lowering
		code (log 394)
		
		operator:	the lowerer's own name for it: clang's `ForStmt`, `BinaryOperator.Add`
		template:	how a program writes it, its placeholders in order: "for (a; b; c) d;"
		holders:	one holder for each placeholder that holds a value: {"b": "int"}
		roles:		what each placeholder is to the HiOp:
				"value"		a value it reads; its holder matters
				"body"		code it runs (in a real program, other HiOps); its holder never shows
				"constant"	a value the lowerer must know while compiling
				"one form only"	an operand the lowerer takes in one form only
				"name", "type"	what it refers to: a label, a type
		is_statement:	it answers nothing, by what it is (`for`, `break;`)
		is_control:	it is a statement, or an expression whose parts run only on some
				paths (`&&`, `||`, `?:`): its parts are held as inert calls
		answers_nothing:	an expression that answers nothing (a builtin typed `void`)
		answer_may_not_be_stored:	the lowerer refuses its answer stored (`__builtin_counted_by_ref`)
		jumps:		it moves control somewhere else (`break;`, `continue;`, `goto m;`,
				`goto *a;`, `return`)
		contexts:	the HiOps it can only stand inside, innermost first: a loop for
				`break;` and `continue;`, a switch for `case`, its label for `goto m;`,
				a label whose address is taken for `goto *a;`. each context is itself
				a HiOp, with a placeholder where this one goes
		part_contexts:	for a part, the HiOps it can only be reached inside: a switch's
				body, inside a case label
		function_answers:	the placeholder whose value the standard function answers:
				`a` for `return a;`. none for every other HiOp, whose function
				answers nothing
		where_the_hiop_goes:	in a HiOp used as a context, that placeholder: `x` in
				`for (;;) { x }`
	"""


class Held:
	"""
		what the standard-form has made so far for one HiOp
		
		key:		names the standard function and every inert part, so the words can be
				read at one symbol
		text_of:	what each placeholder is held as: a field read, an inert call, a constant
		fields:		the container's fields: the values read, then the answer
		inert_parts:	the functions declared and never defined, and what each answers
	"""


class LanguageRow:
	"""
		what one language gives the standard-form: the words it writes each step in.
		every entry is text with holes, filled by the steps above; no entry decides
		anything. GNU C's words, as standard_cell_lines wrote them in log 405 (standard_HiOp_wrapper since log 454):
		
		container:		"struct P_<key> { <fields> };", with "char unused_;" when there are no fields
		field:			"<holder> <name>;"
		held_function:		"<answers> op_<key>(struct P_<key> *p) { <statement> }"
		symbol:			"op_<key>"
		inert declaration:	"<answers> part_<key>_<name>(void);"	declared, never defined
		inert call:		"part_<key>_<name>()"
		nothing, truth:		"void", "int"
		value_read(holder):	"__typeof__(((void)0, (*(<holder> *)0)))"
				the comma drops const, volatile and _Atomic, and an array comes back as
				its pointer
		type_of(text):		"__typeof__(((void)0, <text>))"
		result_type(hiop):	"__typeof__(((void)0, <the HiOp over its holders>))"
				and "__typeof_unqual__(...)" for the three builtins whose answer keeps
				its operand's qualifiers (log 402)
		constant(value type):	"((<value type>)0)"
		field in its form:	"int count; __typeof__((*(<holder> *)0)[0]) <name>[] __attribute__((counted_by(count)));"
		store_result:		"p->result = (<applied>);"
		store_through:		"*<applied> = 0;"
		as_statement:		"(void)(<applied>);"
		call_as_statement:	"<call>;"
		when(test, statement):	"if (<test>) <statement>"
		join:			two lines: the declarations and the container, then the standard function
				(the grid reads each standard source by its two lines)
	"""


class HeldSource:
	"""
		what the standard-form hands on to lower_HiOp
		
		text:	the standard source
		symbol:	the standard function's name, where lower_HiOp reads the words
	"""


# instances, GNU C. each comment is what held_HiOp_wrapper writes for it, the
# declarations and the container on one line, the held function on the next,
# as DRY_mask_maker writes them since log 405, with the keys of elv2_l113

add = HiOp(
	operator="BinaryOperator.Add", template="a + b", holders={"a": "int", "b": "int"},
	roles={"a": "value", "b": "value"},
	is_statement=False, is_control=False, answers_nothing=False, answer_may_not_be_stored=False,
	jumps=False, contexts=[], part_contexts={}, function_answers=None)
# struct P_1970 { int a; int b; __typeof__(((void)0, (*(int *)0) + (*(int *)0))) result; };
# void op_1970(struct P_1970 *p) { p->result = (p->a + p->b); }

if_then = HiOp(
	operator="IfStmt", template="if (a) b;", holders={"a": "int", "b": "int"},
	roles={"a": "value", "b": "body"},
	is_statement=True, is_control=True, answers_nothing=False, answer_may_not_be_stored=False,
	jumps=False, contexts=[], part_contexts={}, function_answers=None)
# __typeof__(((void)0, (*(int *)0))) part_232_a(void); void part_232_b(void); struct P_232 { char unused_; };
# void op_232(struct P_232 *p) { if (part_232_a()) part_232_b(); }

case_label = HiOp(
	operator="CaseStmt", template="{ case 0: x; }", holders={},
	roles={"x": "body"}, where_the_hiop_goes="x",
	is_statement=True, is_control=True, answers_nothing=False, answer_may_not_be_stored=False,
	jumps=False, contexts=[], part_contexts={}, function_answers=None)

switch_on = HiOp(
	operator="SwitchStmt", template="switch (a) b;", holders={"a": "int", "b": "int"},
	roles={"a": "value", "b": "body"},
	is_statement=True, is_control=True, answers_nothing=False, answer_may_not_be_stored=False,
	jumps=False, contexts=[], part_contexts={"b": [case_label]}, function_answers=None)
# __typeof__(((void)0, (*(int *)0))) part_375_a(void); void part_375_b(void); struct P_375 { char unused_; };
# void op_375(struct P_375 *p) { switch (part_375_a()) { case 0: part_375_b(); }; }

loop = HiOp(
	operator="ForStmt", template="for (;;) { x }", holders={},
	roles={"x": "body"}, where_the_hiop_goes="x",
	is_statement=True, is_control=True, answers_nothing=False, answer_may_not_be_stored=False,
	jumps=False, contexts=[], part_contexts={}, function_answers=None)

break_out = HiOp(
	operator="BreakStmt", template="break;", holders={}, roles={},
	is_statement=True, is_control=True, answers_nothing=False, answer_may_not_be_stored=False,
	jumps=True, contexts=[loop], part_contexts={}, function_answers=None)
# int part_1554_test(void); void part_1554_skipped(void); struct P_1554 { char unused_; };
# void op_1554(struct P_1554 *p) { for (;;) { if (part_1554_test()) break; part_1554_skipped(); } }

continue_on = HiOp(
	operator="ContinueStmt", template="continue;", holders={}, roles={},
	is_statement=True, is_control=True, answers_nothing=False, answer_may_not_be_stored=False,
	jumps=True, contexts=[loop], part_contexts={}, function_answers=None)
# int part_1553_test(void); void part_1553_skipped(void); struct P_1553 { char unused_; };
# void op_1553(struct P_1553 *p) { for (;;) { if (part_1553_test()) continue; part_1553_skipped(); } }

return_value = HiOp(
	operator="ReturnStmt", template="return a;", holders={"a": "int"},
	roles={"a": "value"},
	is_statement=True, is_control=True, answers_nothing=False, answer_may_not_be_stored=False,
	jumps=True, contexts=[], part_contexts={}, function_answers="a")
# __typeof__(((void)0, (*(int *)0))) part_1555_a(void); int part_1555_test(void); void part_1555_skipped(void); struct P_1555 { char unused_; };
# __typeof__(((void)0, part_1555_a())) op_1555(struct P_1555 *p) { if (part_1555_test()) return part_1555_a(); part_1555_skipped(); }
# (a path that skips the return falls off the function's end: clang warns,
# "non-void function does not return a value in all control paths", and
# refuses nothing)

label_address_taken = HiOp(
	operator="LabelStmt", template="x m: (void)&&m;", holders={},
	roles={"x": "body"}, where_the_hiop_goes="x",
	is_statement=True, is_control=True, answers_nothing=False, answer_may_not_be_stored=False,
	jumps=False, contexts=[], part_contexts={}, function_answers=None)

goto_computed = HiOp(
	operator="IndirectGotoStmt", template="goto *a;", holders={"a": "char *"},
	roles={"a": "value"},
	is_statement=True, is_control=True, answers_nothing=False, answer_may_not_be_stored=False,
	jumps=True, contexts=[label_address_taken], part_contexts={}, function_answers=None)
# __typeof__(((void)0, (*(char * *)0))) part_31733_a(void); int part_31733_test(void); void part_31733_skipped(void); struct P_31733 { char unused_; };
# void op_31733(struct P_31733 *p) { if (part_31733_test()) goto *part_31733_a(); part_31733_skipped(); m: (void)&&m; }

lock_free = HiOp(
	operator="CallExpr.BI__atomic_always_lock_free", template="__atomic_always_lock_free(a, b)",
	holders={"a": "int", "b": "int *"}, roles={"a": "constant", "b": "value"},
	is_statement=False, is_control=False, answers_nothing=False, answer_may_not_be_stored=False,
	jumps=False, contexts=[], part_contexts={}, function_answers=None)
# struct P_98143 { int * b; __typeof__(((void)0, __atomic_always_lock_free((*(int *)0), (*(int * *)0)))) result; };
# void op_98143(struct P_98143 *p) { p->result = (__atomic_always_lock_free(((__typeof__(((void)0, (*(int *)0))))0), p->b)); }

counted_by_ref = HiOp(
	operator="CallExpr.BI__builtin_counted_by_ref", template="__builtin_counted_by_ref(a)",
	holders={"a": "arr4"}, roles={"a": "one form only"},
	is_statement=False, is_control=False, answers_nothing=False, answer_may_not_be_stored=True,
	jumps=False, contexts=[], part_contexts={}, function_answers=None)
# struct P_120455 { int count; __typeof__((*(arr4 *)0)[0]) a[] __attribute__((counted_by(count))); };
# void op_120455(struct P_120455 *p) { *__builtin_counted_by_ref(p->a) = 0; }

# an instance in another row: Python's `break`, which has the same steps
python_loop = HiOp(
	operator="While", template="while True:\n\tx", holders={},
	roles={"x": "body"}, where_the_hiop_goes="x",
	is_statement=True, is_control=True, answers_nothing=False, answer_may_not_be_stored=False,
	jumps=False, contexts=[], part_contexts={}, function_answers=None)

python_break = HiOp(
	operator="Break", template="break", holders={}, roles={},
	is_statement=True, is_control=True, answers_nothing=False, answer_may_not_be_stored=False,
	jumps=True, contexts=[python_loop], part_contexts={}, function_answers=None)
# def part_7_test(): ...
# def part_7_skipped(): ...
# def op_7(p):
# 	while True:
# 		if part_7_test():
# 			break
# 		part_7_skipped()


```

## what Block A says, in plain words

- `standard_HiOp_wrapper` is the whole standard-form in five steps, the same for every
  language: hold each placeholder; apply the HiOp; keep its answer; stand it
  where it can stand; write the standard source.
- `hold_one_placeholder` is where the standard-form decides, by the
  placeholder's role, never by the language. Only the words come from the row.
- `stand_it_where_it_can_stand` is where Dee's "dependent HiOps" live.
  - The HiOps a HiOp holds inside it in a real program (its body, its test)
    are its parts, each an inert call (`hold_one_placeholder`).
  - The HiOps it can only stand inside are its contexts, written around it,
    their own placeholders inert (`stand_inside`).
  - The jump rule comes first, so the guarded jump sits inside the loop:
    `for (;;) { if (test) break; skipped; }`.
- `HiOp`'s fields are what the lowerer must say about each HiOp. Today GNU C's
  row has them as tables written in `DRY_mask_maker` (`INERT_PART_ROLES`,
  `C_JUMPS`, `C_STATEMENT_CONTEXT`, `CONSTANT_OPERANDS`, `UNQUALIFIED_RESULTS`,
  `FLEXIBLE_ARRAY_OPERANDS`). Log 394's point is that the lowerer's own code
  says all of them, so they could be read from it instead.
- The Python instance gets the same five steps and only different words, as
  log 402 §4.3 showed CPython needs the same jump rule.

## GNU C's code, step by step

Table 1. Where `DRY_mask_maker` (in
`Projects/PseudoArch/map_HiOp_to_unit/`) does each step for GNU C, as of log
405. Line numbers are of that day. Since 2026-10-13 (log 454) the same code is
in `standard_HiOp_wrapper.py`, this node's own module, where `standard_cell_lines` is
named `standard_HiOp_wrapper`; the node's CORE gives its lines there.

| Block A | `DRY_mask_maker` |
|---|---|
| `standard_HiOp_wrapper` | `standard_cell_lines` (line 206), and for a statement `held_statement_lines` (line 495) |
| `hold_one_placeholder` | the loop in `standard_cell_lines` (fields, constants); `add_inert_part` (line 525) for parts; roles in `INERT_PART_ROLES` (line 367) |
| `part_contexts` | `switch_with_a_case_label` (line 583) |
| `keep_the_answer` | the end of `standard_cell_lines`; `result_type_of` (line 645), `flexible_array_lines` (line 656) |
| `jump_over_reached_code` | `jump_over_reached_code` (line 573), for every kind in `C_JUMPS` (line 467) |
| `stand_inside` | `statement_in_context` (line 551), contexts in `C_STATEMENT_CONTEXT` (line 476) |
| `function_answers` | `statement_returns` (line 593) |

## changes from log 404's draft

Made on 2026-10-09 (log 405), each by Claude, for the reason given:

- `is_control` now says what the CORE's control HiOp is: a statement, or
  `&&`, `||`, `?:`. Log 404's draft said "some of its placeholders run only on
  some paths", which would have held `return a;`'s and `goto *a;`'s value in
  a field; the code holds them as inert calls. `break_out` and
  `python_break` say `is_control=True` with it.
- Two fields the code already used and the draft lacked: `part_contexts`
  (a switch's body inside a case label) and `function_answers` (`return a;`).
  Without the first, clang writes nothing for the body (log 394, Table 1);
  without the second, it refuses the HiOp (clang 21.1.8,
  `DiagnosticSemaKinds.td` lines 10922 to 10925, an error by default).
- `goto *a;` has its context, a label whose address is taken: clang refuses
  it without one ("indirect goto in function with no address-of-label
  expressions", the same file, line 6700).
- `stand_inside` keeps a context's placeholders apart from the HiOp's own
  (log 404's wrote both into `held.text_of`, where a context's `a` would
  have overwritten the HiOp's).
- The instances `switch_on`, `continue_on`, `return_value` and
  `goto_computed` are new; `lock_free` lost its unused field, as the code
  did the same day.
- The jump rule now holds for every HiOp that jumps, in the code too:
  `continue;`, `goto *a;`, `return a;` and `return;` joined `break;` and
  `goto m;` (log 405, run elv2_l113).
