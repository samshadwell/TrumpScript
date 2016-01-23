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
            try:
                return token_to_function_map[start]()
            except KeyError:
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
            valid_tokens = [T_Word, T_LParen, T_True, T_False, T_Not, T_Quote, T_Num]
            consume(T_Make)
            variable = consume(T_Word)
            next_token = peek()  # Check the type of the next token to see if it's acceptable
            if next_token == T_Word:
                val = _get_value_from_word_token()
            elif next_token in valid_tokens:
                val = token_to_function_map[next_token]()
            else:
                val = _temporary_error(msg="garbageerror")
            target = Name(id=variable["value"], ctx=Store())
            return Assign(targets=[target], value=val)

        # Both Assign and EQ because why the hell not guys
        def handle_is(left):
            valid_tokens = [T_Word, T_LParen, T_True, T_False, T_Not, T_Quote, T_Num]
            consume(T_Is)
            next_token = peek()  # Check the type of the next token to see if it's acceptable
            if next_token == T_Word:
                right = _get_value_from_word_token()
            elif next_token in valid_tokens:
                right = token_to_function_map[next_token]()
            else:
                right = _temporary_error(msg="is_error")
            if peek() == T_Question:
                consume(T_Question)
                first = Name(id=left["value"], ctx=Load())
                return Compare(left=first, ops=[Eq()], comparators=[right])
            else:
                target = Name(id=left["value"], ctx=Store())
                return Assign(targets=[target], value=right)

        # Print
        def handle_print():
            valid_tokens = [T_Quote, T_LParen, T_Num, T_True, T_False, T_Word]
            consume(T_Print)
            next_token = peek()
            if next_token in valid_tokens:
                output = token_to_function_map[next_token]()
            else:
                output = _temporary_error(msg="Print broke")
            return Call(func=Name(id="print", ctx=Load()), args=[output], keywords=[])

        # While
        def handle_while():
            consume(T_While)
            conditional = handle_paren()
            body = handle_brace()
            return While(test=conditional, body=body, orelse=[])

        # If
        def handle_if():
            consume(T_If)
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

        # BinOp(s)
        def handle_binop(left, op):
            valid_tokens = [T_LParen, T_Quote, T_Num, T_Word]
            tokens.pop(0)
            next_token = peek()
            if next_token in valid_tokens:
                right = token_to_function_map[next_token]()
            else:
                right = _temporary_error(msg="not valid binary op target error")
            return BinOp(left=left, op=op, right=right)

        # Not
        def handle_not():
            valid_tokens = [T_LParen, T_Word, T_False, T_True]
            consume(T_Not)
            next_token = peek()
            if next_token in valid_tokens:
                result = token_to_function_map[next_token]()
            else:
                result = _temporary_error(msg="Error in not")
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
            token_to_argument_map = {T_Plus: Add, T_Minus: Sub, T_Times: Mult, T_Over: FloorDiv}
            token = consume(T_Word)
            next_token = peek()
            if next_token == T_Is:
                return handle_is(token)
            else:
                word_var = Name(id=token["value"], ctx=Load())
                if next_token in token_to_argument_map:
                    return handle_binop(word_var, token_to_argument_map[next_token]())
                else:
                    return word_var

        # True
        def handle_true():
            consume(T_True)
            return NameConstant(value=True)

        # False
        def handle_false():
            consume(T_False)
            return NameConstant(value=False)

        token_to_function_map = {
            T_Word: handle_word,
            T_Make: handle_make,
            T_LBrace: handle_brace,
            T_LParen: handle_paren,
            T_If: handle_if,
            T_While: handle_while,
            T_Print: handle_print,
            T_True: handle_true,
            T_False: handle_false,
            T_Not: handle_not,
            T_Quote: handle_quote,
            T_Num: handle_num
        }

        def _get_value_from_word_token():
            token = consume(T_Word)
            return Name(id=token["value"], ctx=Load())

        def _temporary_error(msg="error", error_value="error"):
            print(msg)
            # TODO: get real errors srsly
            return error_value

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
