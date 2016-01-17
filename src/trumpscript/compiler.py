# Compiler for TrumpScript
# 1/17/2016

from ast import *

from src.trumpscript.parser import *
from src.trumpscript.tokenizer import *


class Compiler:

    def compile(self, source):
        tk = Tokenizer()
        prs = Parser()

        modu = prs.parse(tk.tokenize(source))

        fix_missing_locations(modu)
        exec(compile(modu, filename="<ast>", mode="exec"))
