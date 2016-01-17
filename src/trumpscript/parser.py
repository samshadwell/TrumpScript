# Parser for TrumpScript
# 1/16/2016

from ast import *
from src.trumpscript.constants import *


class Parser:

    def parse(self, tokens):
        tokens = self.pre_parse(tokens)
        body_list = []
        i = 0
        while len(tokens) > 1:
            pass

        def make():
            token = tokens.pop(0)
            if token["type"] == T_Make:
                variable = tokens.pop(0)
                if variable["type"] != T_Word:
                    # TODO: ERROR
                    pass
                else:
                    # TODO: this logic
                    pass
            else:
                # TODO: ERROR
                pass
        return body_list

    @staticmethod
    def pre_parse(tokens) -> list:
        tokens = list(tokens)
        t = "type"
        t_null = {type: -1, "value": "NAN", "line" : "NAN"}
        i = 0
        variables = set()
        token = t_null
        tokens.append(t_null)
        while i < len(tokens) - 1:
            prev = token
            token = tokens[i]
            nxt = tokens[i + 1]

            # Check if we need to drop a junk word
            if token[t] == T_Word:
                if token["value"] not in vars:
                    if prev[t] == T_Make:
                        variables.add([token["value"]])
                    elif nxt[t] == T_Is:
                        variables.add(token["value"])
                    else:
                        tokens.remove(i)
                        i -= 1  # Just back that up a touch
                i += 1

        return tokens



