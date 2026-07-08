import sys
from pseudocoup.cli import Compiler
compiler = Compiler()
compiler.compile("temp_src.py", "python", "dart")
