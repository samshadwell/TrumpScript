# Parser for TrumpScript
# 1/16/2016

from ast import *

from src.trumpscript.constants import *


class Parser:

    def parse(self, tokens) -> AST:
        tokens = self.pre_parse(tokens)

        def peek():
            return tokens[0]["type"]

        def consume(t_type):
            if peek() == t_type:
                return tokens.pop(0)
            else:
                print("failed to consume " + str(t_type) + ", got " + str(peek()) + "instead.")
                pass

        # Mod
        def handle_mod():
            body_list = []
            while len(tokens) > 1:  # TODO: determine whether we are keeping the end marker
                # print("anything")
                body_list.append(handle_anything())
            return Module(body=body_list)

        # Obnoxious coverage
        def handle_anything():
            start = peek()
            # print("Start = " + str(start))
            if start == T_Word:
                return handle_word()
            elif start == T_Make:
                return handle_make()
            elif start == T_LBrace:
                return handle_brace()
            elif start == T_LParen:
                return handle_paren()
            elif start == T_If:
                return handle_if()
            elif start == T_Print:
                return handle_print()
            elif start == T_True:
                return handle_true()
            else:
                print("fuck that's wrong :" + str(start))
                quit()
                return None
                #TODO: finish this

        # Stmt
        def handle_brace():
            consume(T_LBrace)
            statements = []
            while peek() != T_RBrace:
                res = handle_anything()
                if isinstance(res, expr):
                    res = Expr(value=res)
                statements.append(res)

            consume(T_RBrace)
            return statements

        # Expr
        def handle_paren():
            consume(T_LParen)
            expression = handle_anything()
            consume(T_RParen)
            return expression

        # Assign
        def handle_make():
            token = consume(T_Make)
            variable = consume(T_Word)
            followup = peek()  # Check the type of the next token to see if it's acceptable
            # TODO: enumerate all the cases here
            pass

        ##Both Assign and EQ because why the hell not guys
        def handle_is():
            # TODO: this whole thing
            pass

        # Print
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
                print("Print fucked up")
                # TODO: real errors

            return Call(func=Name(id="print", ctx=Load()), args=[output], keywords=[])

        # While
        def handle_while():
            token = consume(T_While)
            conditional = handle_paren()
            body = handle_brace()
            return While(test=conditional,body=body, orelse=[])

        # If
        def handle_if():
            token = consume(T_If)
            conditional = handle_paren()
            body = handle_brace()
            if peek() == T_Else:
                orelse = handle_else()
            else:
                orelse = []
            return If(test=conditional,body=body, orelse=orelse)

        # orelse piece of if
        def handle_else():
            consume(T_Else)
            if peek() == T_If:
                return handle_if()
            else:
                return handle_brace()

        # BoolOp(s)
        def handle_boolop():
            # TODO: take care of and / or
            pass

        # BinOp(s)
        def handle_binop():
            # TODO: this mess
            pass

        # Not
        def handle_not():
            # TODO: handle not
            pass

        # Compare
        def handle_compare():
            # TODO: handle compare
            pass

        # Num
        def handle_num():
            token = consume(T_Num)
            num = token["value"]
            return Num(num)

        # Str
        def handle_quote():
            token = consume(T_Quote)
            text = token["value"]
            return Str(text)

        # Name
        def handle_word():
            # TODO: this whole shit
            pass

        # True
        def handle_true():
            token = consume(T_True)
            return Name(id="True", ctx=Load())

        # False
        def handle_false():
            token = consume(T_False)
            return Name(id="False", ctx=Load())

        #Build the entirety of the Abstract Syntax tree
        return handle_mod()

    @staticmethod
    def pre_parse(tokens) -> list:
        tokens = list(tokens)
        t = "type"
        t_null = {t: -1, "value": "NAN", "line": "NAN"}
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
                if token["value"] not in variables:
                    if prev[t] == T_Make:
                        variables.add(token["value"])
                    elif nxt[t] == T_Is:
                        variables.add(token["value"])
                    else:
                        tokens.pop(i)
                        i -= 1  # Just back that up a touch
            i += 1

        return tokens
