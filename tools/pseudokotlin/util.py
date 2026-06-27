"""Small rendering helpers shared by the handler mixins."""

INDENT = "    "


def indent(text: str, n: int = 1) -> str:
    """Prefix every (non-empty) line of `text` with n levels of 4-space indent."""
    pad = INDENT * n
    out = []
    for line in text.split("\n"):
        out.append(pad + line if line else line)
    return "\n".join(out)


def block(rendered_stmts) -> str:
    """Join already-rendered statement strings into an indented Python suite,
    falling back to `pass` for an empty body."""
    lines = [s for s in rendered_stmts if s is not None and s != ""]
    body = "\n".join(lines) if lines else "pass"
    return indent(body)
