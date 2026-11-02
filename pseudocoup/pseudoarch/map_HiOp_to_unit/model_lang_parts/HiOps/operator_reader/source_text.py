"""source_text -- small readers of a lowerer's source as plain text, used by
more than one lowerer's module: one function's body found by its first line,
comments dropped, a statement split outside quotes and brackets, quoted text
emptied or decoded.
"""

import codecs
import re

from ... import declaring_file_path


def read_function_body(checkout: str, relative: str, start: str) -> tuple:
    """(text, first line) of the function that begins with `start`."""
    path = declaring_file_path(checkout, relative)
    lines = []
    first_line = 0
    with open(path, encoding="utf-8") as source_file:
        for line_number, line in enumerate(source_file, start=1):
            if first_line == 0:
                if line.strip() == start:
                    first_line = line_number
                continue
            if line.strip() == "}":
                break
            lines.append(line)
    if first_line == 0:
        message = f"read_operators: `{start}` is not in {relative}"
        raise LookupError(message)
    body = "".join(lines)
    return body, first_line


def strip_comments(text: str) -> str:
    """The text with its C++ comments blanked."""
    without_blocks = re.sub(r"/\*.*?\*/", " ", text, flags=re.S)
    without_lines = re.sub(r"//[^\n]*", " ", without_blocks)
    return without_lines


def split_outside_literals(text: str, separator: str) -> list:
    """`text` split on `separator` wherever it sits outside a string, a
    character literal and any parentheses."""
    pieces = []
    current = []
    quote = None
    depth = 0
    index = 0
    while index < len(text):
        character = text[index]
        if quote is not None:
            current.append(character)
            if character == "\\":
                current.append(text[index + 1])
                index += 2
                continue
            if character == quote:
                quote = None
            index += 1
            continue
        if character in "\"'":
            quote = character
        elif character == "(":
            depth += 1
        elif character == ")":
            depth -= 1
        elif depth == 0 and text.startswith(separator, index):
            pieces.append("".join(current).strip())
            current = []
            index += len(separator)
            continue
        current.append(character)
        index += 1
    pieces.append("".join(current).strip())
    kept = [piece for piece in pieces if piece]
    return kept


def without_literals(text: str) -> str:
    """The text with every string and character literal emptied."""
    emptied = re.sub(r'"(?:[^"\\]|\\.)*"', '""', text)
    emptied = re.sub(r"'(?:[^'\\]|\\.)*'", "''", emptied)
    return emptied


def literal_text(item: str):
    """The text of a string or character literal, or None."""
    if len(item) >= 2 and item[0] == item[-1] and item[0] in "\"'":
        decoded = codecs.decode(item[1:-1], "unicode_escape")
        return decoded
    return None
