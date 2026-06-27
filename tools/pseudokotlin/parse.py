"""
parse.py — the tree-sitter Kotlin frontend. tree-sitter is the TRUTH; everything
downstream routes off the concrete syntax tree it produces.

The dispatch surface is the set of NAMED node kinds (operators/punctuation are
anonymous kinds, read inside a parent handler, never dispatched). `named_kinds()`
enumerates them live from the compiled grammar — that enumeration is what the
coverage gate checks the router against.
"""
from tree_sitter import Language, Parser
import tree_sitter_kotlin as tsk

_LANG = Language(tsk.language())


def language():
    return _LANG


def build_parser() -> Parser:
    try:
        return Parser(_LANG)
    except TypeError:  # older py-tree-sitter API
        p = Parser()
        p.language = _LANG
        return p


def parse(source: bytes):
    return build_parser().parse(source)


def named_kinds() -> set:
    """Every named grammar node kind — the full routing surface."""
    lang = _LANG
    return {
        lang.node_kind_for_id(i)
        for i in range(lang.node_kind_count)
        if lang.node_kind_is_named(i)
    }
