"""model_contexts -- a context's model: the lowerer's logic for a place,
modelled once and applied the same way to every HiOp. Today it holds the
bit-field place, learned by automation on riscv64 (PCHQ log 479).

Plan: `.../node_0_0_0_0_2_8_model_HiOps/node_0_0_0_0_2_8_1_model_contexts/`
(made 2026-10-15).

the owner, 2026-10-15: "the way the context changes things is logic defined within
the lowerer. i want the way that context changes things to be modelled. thats
what context is. context could change a bunch of things but it changes it
according to its model. if the context model is not HiOp specific, it make
changes to arch-opcodes is a simple way."

A place's model is the words the lowerer writes for the place alone: its
fetch, in a statement that does nothing else (`p->r = q->a;`), and its store,
in a statement that does nothing else (`q->r = p->a;`). The lowerer writes
them once, and no rule is written by hand. Applied to a HiOp's function, the
model replaces the access to the plain field the holder stood in, and nothing
else changes.

	def with_places(function, holders, model):
		for holder in holders:
			access = plain_access(function, holder)                         # 1
			words = renamed(model[holder], access, free_registers(function))   # 2
			function = replaced(function, access, words)                    # 3
		return function

- Line 1: the function's own fetch of the holder from its plain field (riscv64
  `lw` or `lwu` through the register that holds the struct's address), or its
  store into the plain field (`sw`).
- Line 2: the model's value register becomes the access's; every other register
  the model uses becomes one the function never uses (t0 to t6).
- Line 3: everything else stays as the lowerer wrote it.

	place_alone_source   the place's fetches and stores, each alone, in the
	                     shape of the HiOps' functions (same signature and
	                     local, so the same frame)
	read_model           the words clang wrote for each of them
	with_places          one function of a HiOp with its holders in the place

Checked (log 479, runs elv2_l171 and elv2_l172): `struct Q { int a : 13; int b :
13; int r : 13; }`, riscv64, the 12 `int` operators in the 91 combinations of
places with a bit-field: C's value in 1,092 of 1,092 functions, 34,944 of
34,944 inputs. The check is `Research/lower_HiOp/make_samples_l170.py` and
`read_samples_l170.py`; the splice that ran is `Research/lower_HiOp/splice_l170.py`,
which this module repeats word for word.

Reads clang's riscv64 assembly (`clang -S -g`), whose `.loc` records give each
word's source line.
"""

import re

STATEMENT_LINE = 2
OPERAND_LINE = 3
KEPT_REGISTERS = ("zero", "ra", "sp", "gp", "tp", "s0", "fp")
FREE_POOL = ("t0", "t1", "t2", "t3", "t4", "t5", "t6")
REGISTER = re.compile(r"\b(zero|ra|sp|gp|tp|fp|t[0-6]|s[0-9]|s1[01]|a[0-7])\b")
LOCAL_LABEL = re.compile(r"(\.L[A-Za-z_]+[0-9]+)")
MEMORY = re.compile(r"^(-?[0-9]+)\(([a-z0-9]+)\)$")
STORES = ("sb", "sh", "sw", "sd", "fsw", "fsd")
NO_DESTINATION = ("ret", "j", "jr", "call", "tail", "nop", "fence", "ecall")


# ---------------------------------------------------------- the model

def place_alone_source(signature: str, local: str, fetches: dict, stores: dict) -> str:
	"""One function per fetch and per store of the place, each a statement
	with nothing else in it. `fetches`: holder -> (plain destination, the
	place); `stores`: holder -> (the place, plain source)."""
	lines = []
	for holder in fetches:
		destination, place = fetches[holder]
		lines.extend(alone_function("c_fetch_" + holder, signature, local, destination, place))
	for holder in stores:
		place, source = stores[holder]
		lines.extend(alone_function("c_store_" + holder, signature, local, place, source))
	source_text = "\n".join(lines)
	return source_text


def alone_function(name: str, signature: str, local: str, left: str, right: str) -> list:
	"""`left = right;` written over two lines, so the debug table files the
	store's words under the first line and the operand's under the second."""
	lines = [
		"",
		f"void {name}{signature} {{",
		"\t" + local,
		f"\t{left} =",
		f"\t\t{right};",
		"}",
	]
	return lines


def read_model(assembly: str, fetches: list, stores: list) -> dict:
	"""For each holder, the words clang wrote for the place alone and the
	register that carries the value."""
	model = {}
	for holder in fetches:
		model[holder] = fetch_words(assembly, "c_fetch_" + holder)
	for holder in stores:
		model[holder] = store_words(assembly, "c_store_" + holder)
	return model


def fetch_words(assembly: str, name: str) -> dict:
	"""The words under the operand's line; the value is in the last word's destination."""
	items = parse_block(function_block(assembly, name))
	opening = opening_line(items)
	words = words_on_line(items, opening + OPERAND_LINE)
	value = destination_of(words[-1])
	place_model = {"words": words, "value": value, "line": opening + OPERAND_LINE}
	return place_model


def store_words(assembly: str, name: str) -> dict:
	"""The words under the statement's line; the value arrives in the register
	the operand's line loaded it into."""
	items = parse_block(function_block(assembly, name))
	opening = opening_line(items)
	operand = words_on_line(items, opening + OPERAND_LINE)
	words = words_on_line(items, opening + STATEMENT_LINE)
	value = destination_of(operand[-1])
	place_model = {"words": words, "value": value, "line": opening + STATEMENT_LINE}
	return place_model


# ------------------------------------------------- the model applied

def with_places(block: list, base_name: str, new_name: str, holders: list, model: dict, layout: dict, number: int) -> dict:
	"""The base function's lines, renamed, with each holder's plain access
	replaced by the place's words. `layout`: holder -> (its part's line, counted
	from the function's own line, and its plain field's offset)."""
	record = {"function": new_name, "base": base_name, "status": "spliced", "replaced": []}
	items = parse_block(block)
	accesses = plain_accesses(items, layout)
	free = free_registers(items)
	replacements = {}
	for holder in holders:
		found = accesses.get(holder)
		if found is None:
			record["status"] = f"no plain access found for {holder}"
			return record
		index, value_register = found
		words, mapping = renamed(model[holder], value_register, free)
		replacements[index] = words
		record["replaced"].append({"holder": holder, "access": items[index]["text"], "words": words, "registers": mapping})
	record["lines"] = rewritten_lines(items, replacements, base_name, new_name, number)
	return record


def plain_accesses(items: list, layout: dict) -> dict:
	"""For each holder: (the item's index, its value register) of its access
	to its plain field through the register that holds the struct's address."""
	opening = opening_line(items)
	pointer = pointer_slot(items)
	holds_pointer = set()
	accesses = {}
	for index in range(len(items)):
		item = items[index]
		if item["kind"] != "word":
			continue
		for holder in layout:
			part_offset, field_offset = layout[holder]
			if item["line"] != opening + part_offset:
				continue
			if is_plain_access(item, holder, field_offset, holds_pointer):
				accesses[holder] = (index, item["operands"][0])
		note_pointer(item, pointer, holds_pointer)
	return accesses


def pointer_slot(items: list):
	"""Where the function keeps its first argument, the struct's address: the
	frame slot of its first `sd a0`."""
	for item in items:
		if item["kind"] != "word":
			continue
		if item["mnemonic"] == "sd" and len(item["operands"]) == 2 and item["operands"][0] == "a0":
			return item["operands"][1]
	return None


def note_pointer(item: dict, pointer, holds_pointer: set) -> None:
	operands = item["operands"]
	destination = destination_of(item)
	if item["mnemonic"] == "ld" and len(operands) == 2 and operands[1] == pointer:
		holds_pointer.add(operands[0])
		return
	if destination is not None:
		holds_pointer.discard(destination)


def is_plain_access(item: dict, holder: str, field_offset: int, holds_pointer: set) -> bool:
	operands = item["operands"]
	if len(operands) != 2:
		return False
	place = MEMORY.match(operands[1])
	if place is None:
		return False
	offset = int(place.group(1))
	base = place.group(2)
	if base not in holds_pointer or offset != field_offset:
		return False
	if holder == "r":
		return item["mnemonic"] == "sw"
	return item["mnemonic"] in ("lw", "lwu")


def renamed(place_model: dict, value_register: str, free: list) -> tuple:
	"""The place's words, its value register renamed to the access's and every
	other register it uses renamed to a free one."""
	mapping = {place_model["value"]: value_register}
	spare = list(free)
	for word in place_model["words"]:
		for register in REGISTER.findall(word["text"]):
			if register in KEPT_REGISTERS:
				continue
			if register in mapping:
				continue
			mapping[register] = spare.pop(0)
	words = []
	for word in place_model["words"]:
		words.append(rename_registers(word["text"], mapping))
	return words, mapping


def rename_registers(text: str, mapping: dict) -> str:
	pieces = []
	position = 0
	for found in REGISTER.finditer(text):
		register = found.group(1)
		pieces.append(text[position:found.start()])
		pieces.append(mapping.get(register, register))
		position = found.end()
	pieces.append(text[position:])
	renamed_text = "".join(pieces)
	return renamed_text


def free_registers(items: list) -> list:
	used = set()
	for item in items:
		if item["kind"] != "word":
			continue
		for register in REGISTER.findall(item["text"]):
			used.add(register)
	free = []
	for register in FREE_POOL:
		if register not in used:
			free.append(register)
	return free


def rewritten_lines(items: list, replacements: dict, base_name: str, new_name: str, number: int) -> list:
	"""The block again: its new name, local labels made its own, no line
	records or file records, and each replaced access swapped for the place's
	words."""
	lines = []
	for index in range(len(items)):
		item = items[index]
		if item["kind"] == "loc":
			continue
		if item["raw"].startswith("\t.file"):
			continue
		if index in replacements:
			lines.append(f"\t# {new_name}: the bit-field place's words, in place of: {item['text'].strip()}")
			for word in replacements[index]:
				lines.append("\t" + word)
			continue
		line = item["raw"].replace(base_name, new_name)
		line = rename_labels(line, number)
		lines.append(line)
	return lines


def rename_labels(line: str, number: int) -> str:
	pieces = []
	position = 0
	for found in LOCAL_LABEL.finditer(line):
		pieces.append(line[position:found.start()])
		pieces.append(found.group(1) + "_m" + str(number))
		position = found.end()
	pieces.append(line[position:])
	renamed_line = "".join(pieces)
	return renamed_line


# --------------------------------------------- reading clang's assembly

def function_names(assembly: str) -> list:
	names = []
	for line in assembly.split("\n"):
		found = re.match(r"^\t\.globl\t(\S+)", line)
		if found:
			names.append(found.group(1))
	return names


def function_block(assembly: str, name: str) -> list:
	"""From `.globl name` to the line that ends the function."""
	block = []
	inside = False
	for line in assembly.split("\n"):
		if re.match(r"^\t\.globl\t" + re.escape(name) + r"(\s|$)", line):
			inside = True
		if not inside:
			continue
		block.append(line)
		if "-- End function" in line:
			break
	return block


def header_lines(assembly: str) -> list:
	"""The lines before the first function that the assembler needs."""
	header = []
	for line in assembly.split("\n"):
		if line.startswith("\t.globl"):
			break
		if line.startswith("\t.attribute") or line.startswith("\t.option") or line.startswith("\t.text"):
			header.append(line)
	return header


def parse_block(block: list) -> list:
	"""Each line as a word with its source line, a line record, or other."""
	items = []
	line_number = 0
	for raw in block:
		loc = re.match(r"^\t\.loc\t[0-9]+ ([0-9]+) ", raw)
		if loc:
			line_number = int(loc.group(1))
			items.append({"kind": "loc", "raw": raw, "line": line_number})
			continue
		word = parse_word(raw, line_number)
		if word is not None:
			items.append(word)
			continue
		items.append({"kind": "other", "raw": raw, "line": line_number})
	return items


def parse_word(raw: str, line_number: int):
	stripped = raw.split("#")[0].rstrip()
	found = re.match(r"^\t([a-z][a-z0-9.]*)(\t(.*))?$", stripped)
	if found is None:
		return None
	mnemonic = found.group(1)
	operand_text = found.group(3)
	text = mnemonic
	if operand_text:
		text = mnemonic + "\t" + operand_text
	operands = split_operands(operand_text)
	word = {"kind": "word", "raw": raw, "line": line_number, "mnemonic": mnemonic, "operands": operands, "text": text}
	return word


def split_operands(text) -> list:
	operands = []
	if not text:
		return operands
	for piece in text.split(","):
		piece = piece.strip()
		if piece:
			operands.append(piece)
	return operands


def opening_line(items: list) -> int:
	"""The function's own line: its first line record."""
	for item in items:
		if item["kind"] == "loc":
			return item["line"]
	return 0


def words_on_line(items: list, line: int) -> list:
	words = []
	for item in items:
		if item["kind"] == "word" and item["line"] == line:
			words.append(item)
	return words


def destination_of(item: dict):
	mnemonic = item["mnemonic"]
	if mnemonic in STORES or mnemonic in NO_DESTINATION or mnemonic.startswith("b"):
		return None
	if not item["operands"]:
		return None
	destination = item["operands"][0]
	return destination
