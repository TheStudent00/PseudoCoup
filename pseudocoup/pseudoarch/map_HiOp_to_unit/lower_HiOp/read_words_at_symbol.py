"""read_words_at_symbol -- reads the machine words (`Word`) and relocations of
`op_<key>` from an object file (`MachineCode`) into a `LoHiOp`.

Plan: `.../node_0_0_0_0_2_2_lower_HiOp/node_0_0_0_0_2_2_1_read_words_at_symbol/`.
"""

import os
from . import (
    LoHiOp,
    MachineCode,
    Word,
    read_words_at_symbol,
    words_of_object,
)

__all__ = [
    "LoHiOp",
    "MachineCode",
    "Word",
    "read_words_at_symbol",
    "words_of_object",
]
