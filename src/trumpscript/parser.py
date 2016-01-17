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

        def peek():
            return tokens[0]["type"]

        def consume(t_type):
            if peek() == t_type:
                return tokens.pop(0)
            else:
                # TODO: Error
                pass

        # Stmt
        def handle_brace():
            # Todo
            return 1

        # Expr
        def handle_paren():
            # Todo
            return 1

        # Assign
        def handle_make():
            token = consume(T_Make)
            variable = consume(T_Word)
            followup = peek()           # Check the type of the next token to see if it's acceptable
            # TODO: enumerate all the cases here
            pass

        ##Both Assign and EQ because why the hell not guys
        def handle_is():
            #TODO: this whole thing
            pass

        #Print
        def handle_print():
            consume(T_Print)
            followup = peek()
            if followup == T_Quote:
                output = handle_quote()
            elif followup == T_LParen:
                output = handle_paren()
            elif followup == T_Num:
                output = handle_num()
            elif followup == T_True:
                output = handle_true()
            elif followup == T_False:
                output = handle_false()
            elif followup == T_Word:
                output = handle_word()
            else:
                output = "error"
                # TODO: real errors

            return Call(func=Name(idx="print", ctx=Load),args=output, keywords=[])

        #While
        def handle_while():
            token = consume(T_While)
            conditional = handle_paren()
            body = handle_brace()
            # TODO: build tree from outputs

        #If
        def handle_if():
            token = consume(T_If)
            conditional = handle_paren()
            body = handle_brace()
            if peek() == T_Else:
                orelse = handle_else()
            else:
                orelse = []
            return If(conditional, body, orelse)

        #orelse piece of if
        def handle_else():
            consume(T_Else)
            if peek() == T_If:
                return handle_if()
            else:
                return handle_brace()

        #BoolOp(s)
        def handle_boolop():
            # TODO: take care of and / or
            pass

        #BinOp(s)
        def handle_binop():
            # TODO: this mess
            pass

        #Not
        def handle_not():
            # TODO: handle not
            pass

        #Compare
        def handle_compare():
            # TODO: handle compare
            pass

        #Num
        def handle_num():
            token = consume(T_Num)
            num = token["value"]
            return Num(num)

        #Str
        def handle_quote():
            token = consume(T_Quote)
            text = token["value"]
            return Str(text)

        #Name
        def handle_word():
            #TODO: this whole shit
            pass

        #True
        def handle_true():
            token = consume(T_True)
            return Name(idx = "True", ctx = Load)

        #False
        def handle_false():
            token = consume(T_False)
            return Name(idx = "False", ctx = Load)



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



