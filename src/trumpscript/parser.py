# Parser for TrumpScript
# 1/16/2016

from ast import *

from trumpscript.constants import *


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
                state = handle_anything()
                if isinstance(state, expr):
                    state = Expr(value=state)
                body_list.append(state)
            for statement in body_list:
                # print(statement)
                fix_missing_locations(statement)

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
            elif start == T_While:
                return handle_while()
            elif start == T_Print:
                return handle_print()
            elif start == T_True:
                return handle_true()
            elif start == T_False:
                return handle_false()
            elif start == T_Not:
                return handle_not()
            elif start == T_Quote:
                return handle_quote()
            elif start == T_Num:
                return handle_num()
            else:
                # Silent errors
                tokens.pop(0)
                return Pass()

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
        def handle_paren() -> expr:
            consume(T_LParen)
            expression = handle_anything()
            consume(T_RParen)
            return expression

        # Assign
        def handle_make():
            token = consume(T_Make)

            variable = consume(T_Word)
            followup = peek()  # Check the type of the next token to see if it's acceptable
            if followup == T_Word:
                tok = consume(T_Word)
                val = Name(id=tok["value"], ctx=Load())
            elif followup == T_LParen:
                val = handle_paren()
            elif followup == T_True:
                val = handle_true()
                print(val)
            elif followup == T_False:
                val = handle_false()
            elif followup == T_Not:
                val = handle_not()
            elif followup == T_Quote:
                val = handle_quote()
            elif followup == T_Num:
                val = handle_num()
            else:
                print("make error")
                # TODO: get real errors srsly
                val = "garbageerror"
            target = Name(id=variable["value"], ctx=Store())
            return Assign(targets=[target], value=val)

        ##Both Assign and EQ because why the hell not guys
        def handle_is(left):
            consume(T_Is)
            followup = peek()  # Check the type of the next token to see if it's acceptable
            if followup == T_Word:
                tok = consume(T_Word)
                right = Name(id=tok["value"], ctx=Load())
            elif followup == T_LParen:
                right = handle_paren()
            elif followup == T_True:
                right = handle_true()
            elif followup == T_False:
                right = handle_false()
            elif followup == T_Not:
                right = handle_not()
            elif followup == T_Quote:
                right = handle_quote()
            elif followup == T_Num:
                right = handle_num()
            else:
                right = "ERROR"
                # TODO: real errors
                print("is_error")
            if peek() == T_Question:
                consume(T_Question)
                first = Name(id=left["value"], ctx=Load())
                return Compare(left=first, ops=[Eq()], comparators=[right])
            else:
                target = Name(id=left["value"], ctx=Store())
                return Assign(targets=[target], value=right)

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
                print("Print broke")
                # TODO: real errors

            return Call(func=Name(id="print", ctx=Load()), args=[output], keywords=[])

        # While
        def handle_while():
            token = consume(T_While)
            conditional = handle_paren()
            body = handle_brace()
            return While(test=conditional, body=body, orelse=[])

        # If
        def handle_if():
            token = consume(T_If)
            conditional = handle_paren()
            body = handle_brace()
            if peek() == T_Else:
                orelse = handle_else()
            else:
                orelse = []
            return If(test=conditional, body=body, orelse=orelse)

        # orelse piece of if
        def handle_else():
            consume(T_Else)
            if peek() == T_If:
                return handle_if()
            else:
                return handle_brace()

                # TODO: make this not necessary
                # BoolOp(s)
                # def handle_boolop():
                # TODO: take care of and / or
                # pass

        # BinOp(s)
        def handle_binop(left, op):
            tokens.pop(0)
            nxt = peek()
            if nxt == T_LParen:
                right = handle_paren()
            elif nxt == T_Word:
                word = consume(T_Word)
                right = Name(id=word["value"], ctx=Load())
            elif nxt == T_Quote:
                right = handle_quote()
            elif nxt == T_Num:
                right = handle_num()
            else:
                right = "boooo"
                print("not valid binary op target error")
                # TODO: should have built an error method
            return BinOp(left=left, op=op, right=right)

        # Not
        def handle_not():
            consume(T_Not)
            nxt = peek()
            if nxt == T_LParen:
                result = handle_paren()
            elif nxt == T_Word:
                result = handle_word()
            elif nxt == T_False:
                result = handle_false()
            elif nxt == T_True:
                result = handle_true()
            else:
                result = "error"
                print("Error in not")
                # TODO: real errors, seriously.
            return UnaryOp(op=Not(), operand=result)

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
            token = consume(T_Word)
            nxt = peek()
            if nxt == T_Is:
                return handle_is(token)
            else:
                word_var = Name(id=token["value"], ctx=Load())
                if nxt == T_Plus:
                    return handle_binop(word_var, Add())
                elif nxt == T_Minus:
                    return handle_binop(word_var, Sub())
                elif nxt == T_Times:
                    return handle_binop(word_var, Mult())
                elif nxt == T_Over:
                    return handle_binop(word_var, FloorDiv())
                else:
                    return word_var

        # True
        def handle_true():
            token = consume(T_True)
            return NameConstant(value=True)

        # False
        def handle_false():
            token = consume(T_False)
            return NameConstant(value=False)

        # Build the entirety of the Abstract Syntax tree
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
                # TODO: make this not necessary
                if token[t] == T_Less or token[t] == T_Greater or token[t] == T_And or token[t] == T_Or:
                    tokens.pop(i)
                    i -= 1  # Just back that up a touch
            i += 1

        return tokens
