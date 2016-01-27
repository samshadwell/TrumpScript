# Parser for TrumpScript
# 1/16/2016

from ast import *

from trumpscript.constants import *


class Parser:

    def __init__(self):
        self._token_to_function_map = {
            T_Word: self.handle_word,
            T_Make: self.handle_make,
            T_LBrace: self.handle_brace,
            T_LParen: self.handle_paren,
            T_If: self.handle_if,
            T_While: self.handle_while,
            T_Print: self.handle_print,
            T_True: self.handle_true,
            T_False: self.handle_false,
            T_Not: self.handle_not,
            T_Quote: self.handle_quote,
            T_Num: self.handle_num,
            T_Less: self.handle_ineq,
            T_Greater: self.handle_ineq
        }

    def _get_value_from_word_token(self, tokens):
        token = self.consume(tokens, T_Word)
        return Name(id=token["value"], ctx=Load())

    def parse(self, tokens) -> AST:
        filtered = self.filter_tokens(tokens)
        # Build the entirety of the Abstract Syntax tree
        return self.handle_module(filtered)

    @staticmethod
    def _temporary_error(msg="error", error_value="error"):
        print(msg)
        # TODO: get real errors srsly
        return error_value

    @staticmethod
    def filter_tokens(tokens) -> list:
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

    @staticmethod
    def peek(tokens):
        return tokens[0]["type"]

    @staticmethod
    def on_line(tokens):
        return tokens[0]["line"]

    def consume(self, tokens, t_type) -> dict:
        if self.peek(tokens) == t_type:
            return tokens.pop(0)
        else:
            print("failed to consume " + str(t_type) + ", got " + str(self.peek(tokens)) + " instead on line " + str(self.on_line(tokens)) + ".")
            pass

    # Mod
    def handle_module(self, tokens) -> Module:
        body_list = []
        while len(tokens) > 1:
            # print("module main loop")
            state, tokens = self.handle_anything(tokens)
            if isinstance(state, expr):
                state = Expr(value=state)
            body_list.append(state)
        for statement in body_list:
            # print(statement)
            fix_missing_locations(statement)

        return Module(body=body_list)

    # Obnoxious coverage
    def handle_anything(self, tokens):
        start = self.peek(tokens)
        try:
            return self._token_to_function_map[start](tokens)
        except KeyError:
            tokens.pop(0)
            return Pass(), tokens

    # Stmt
    def handle_brace(self, tokens) -> (stmt, list):
        brace_contents = []
        cur_token = tokens.pop(0)
        while cur_token["type"] != T_RBrace :
            # TODO edge case error
            brace_contents.append(cur_token)
            cur_token = tokens.pop(0)
        brace_contents.append(cur_token)

        self.consume(brace_contents, T_LBrace)
        statements = []
        while self.peek(brace_contents) != T_RBrace:
            if self.peek(brace_contents) == T_End:
                # TODO: real error functionality please
                print("Called handle_brace on a non-terminated brace")
            res, contents = self.handle_anything(brace_contents)
            if isinstance(res, expr):
                res = Expr(value=res) #TODO: does it make sense to cast expressions to statements here?
            statements.append(res)
        return statements, tokens

    # Expr
    def handle_paren(self, tokens) -> (expr, list):
        paren_contents = []
        cur_token = tokens.pop(0)
        while cur_token["type"] != T_RParen :
            paren_contents.append(cur_token)
            cur_token = tokens.pop(0)
        paren_contents.append(cur_token)

        self.consume(paren_contents, T_LParen)
        expression, contents = self.handle_anything(paren_contents)
        if self.peek(contents) != T_RParen :
            #TODO: real erros
            print("passed in parenthetical with more than one expression")
        self.consume(contents, T_RParen)
        return expression, tokens

    # Assign
    def handle_make(self, tokens) -> (stmt, list):
        valid_tokens = [T_LParen, T_True, T_False, T_Not, T_Quote, T_Num]

        self.consume(tokens, T_Make)
        if self.peek(tokens) != T_Word :
            #TODO: write this fucking error
            print("Ooh, what you making there? It sure isn't a variable, that's for goddamn sure!")
        variable = self.consume(tokens, T_Word)

        followup = self.peek(tokens)  # Check the type of the next token to see if it's acceptable
        if followup == T_Word:
            val = self._get_value_from_word_token(follwup)
        elif followup in valid_tokens:
            val, tokens = self._token_to_function_map[followup](tokens)
        else:
            val = self._temporary_error(msg="make_error")

        target = Name(id=variable["value"], ctx=Store())
        return Assign(targets=[target], value=val), tokens

    # Both Assign and EQ because why the hell not guys
    # Note that this does not have type signature because it can be expr or stmt (yeah it blows))
    def handle_is(self, left, tokens):
        valid_tokens = [T_LParen, T_True, T_False, T_Not, T_Quote, T_Num]
        self.consume(tokens, T_Is)
        followup = self.peek(tokens)  # Check the type of the next token to see if it's acceptable
        if followup == T_Word:
            right = self._get_value_from_word_token(tokens)
        elif followup in valid_tokens:
            right, tokens = self._token_to_function_map[followup](tokens)
        else:
            right = self._temporary_error(msg="is_error")

        if self.peek(tokens) == T_Question:
            self.consume(tokens, T_Question)
            first = None
            if left['type'] == T_Num:
                first = Num(left['value'])
            elif left['type'] == T_Quote:
                first = Str(left['value'])
            else:
                first = Name(id=left["value"], ctx=Load())
            return Compare(left=first, ops=[Eq()], comparators=[right]), tokens
        else:
            if left["type"] == T_Word:
                target = Name(id=left["value"], ctx=Store())
                return Assign(targets=[target], value=right), tokens
            else:
                target = self._temporary_error(msg="is_error")
                return Pass(), tokens

    def handle_ineq(self, left, tokens):
        valid_tokens = [T_LParen, T_True, T_False, T_Quote, T_Num]
        token_to_argument_map = {T_Less: Lt, T_Greater: Gt}
        
        cmpop = None
        op = self.peek(tokens)
        try:
            cmpop = token_to_argument_map[op]()
            self.consume(tokens, op)
        except KeyError:
            cmpop = self._temporary_error(msg='ineq_error')
        
        followup = self.peek(tokens)
        if followup == T_Word:
            right = self._get_value_from_word_token(tokens)
        elif followup in valid_tokens:
            right, tokens = self._token_to_function_map[followup](tokens)
        else:
            right = self._temporary_error(msg="ineq_error")

        first = None
        if left['type'] == T_Num:
            first = Num(left['value'])
        elif left['type'] == T_Quote:
            first = Str(left['value'])
        else:
            first = Name(id=left["value"], ctx=Load())
        return Compare(left=first, ops=[cmpop], comparators=[right]), tokens

    # Print
    def handle_print(self, tokens) -> (stmt, list):
        valid_tokens = [T_Quote, T_LParen, T_Num, T_True, T_False, T_Word]
        self.consume(tokens, T_Print)
        followup = self.peek(tokens)
        if followup in valid_tokens:
            output, tokens = self._token_to_function_map[followup](tokens)
        else:
            output = self._temporary_error(msg="print_error")

        return Call(func=Name(id="print", ctx=Load()), args=[output], keywords=[]), tokens

    # While
    def handle_while(self, tokens) -> (stmt, list):
        self.consume(tokens, T_While)
        conditional, tokens = self.handle_paren(tokens)
        body, tokens = self.handle_brace(tokens)
        return While(test=conditional,body=body, orelse=[]), tokens

    # If
    def handle_if(self, tokens) -> (stmt, list):
        self.consume(tokens, T_If)
        conditional, tokens = self.handle_paren(tokens)
        body, tokens = self.handle_brace(tokens)
        if self.peek(tokens) == T_Else:
            orelse, tokens = self.handle_else(tokens)
        else:
            orelse = []
        return If(test=conditional,body=body, orelse=orelse), tokens

    # orelse piece of if
    def handle_else(self, tokens) -> (stmt, list):
        self.consume(tokens, T_Else)
        if self.peek(tokens) == T_If:
            return self.handle_if(tokens)
        else:
            return self.handle_brace(tokens)

    # BinOp(s)
    # TODO: what the fuck is going on here? I wrote this at 9am after nigh 24 hours of wakefulness
    def handle_binop(self, left, op, tokens):
        valid_tokens = [T_LParen, T_Quote, T_Num]
        tokens.pop(0)
        nxt = self.peek(tokens)
        if nxt == T_Word:
            right = self._get_value_from_word_token(tokens)
        elif nxt in valid_tokens:
            right, tokens = self._token_to_function_map[nxt](tokens)
        else:
            right = self._temporary_error(msg="binop_error")

        return BinOp(left=left, op=op, right=right), tokens

    # Not
    def handle_not(self, tokens):
        valid_tokens = [T_LParen, T_Word, T_False, T_True]
        self.consume(tokens, T_Not)
        nxt = self.peek(tokens)
        if nxt in valid_tokens:
            result, tokens = self._token_to_function_map[nxt](tokens)
        else:
            result = self._temporary_error(msg="not_error")

        return UnaryOp(op=Not(),operand=result), tokens

    # Num
    def handle_num(self, tokens):
        token_to_argument_map = {T_Plus: Add, T_Minus: Sub, T_Times: Mult, T_Over: Div}
        token = self.consume(tokens, T_Num)
        nxt = self.peek(tokens)
        if nxt == T_Is:
            return self.handle_is(token, tokens)
        if nxt == T_Less or nxt == T_Greater:
            return self.handle_ineq(token, tokens)
        else:
            num = Num(token["value"])
            if nxt in token_to_argument_map:
                return self.handle_binop(num, token_to_argument_map[nxt](), tokens)
            else:
                return num, tokens
        # TODO: check for a longer expression

    # Str
    def handle_quote(self, tokens):
        token = self.consume(tokens, T_Quote)
        text = token["value"]
        # TODO: check for a longer expression
        nxt = self.peek(tokens)
        if nxt == T_Is:
            return self.handle_is(token, tokens)
        elif nxt == T_Less or nxt == T_Greater:
            return self.handle_ineq(token, tokens)
        else:
            return Str(text), tokens

    # Name
    def handle_word(self, tokens):
        token_to_argument_map = {T_Plus: Add, T_Minus: Sub, T_Times: Mult, T_Over: Div}
        token = self.consume(tokens, T_Word)
        nxt = self.peek(tokens)
        if nxt == T_Is:
            return self.handle_is(token, tokens)
        elif nxt == T_Less or nxt == T_Greater:
            return self.handle_ineq(token, tokens)
        else:
            word_var = Name(id=token["value"], ctx=Load())
            if nxt in token_to_argument_map:
                return self.handle_binop(word_var, token_to_argument_map[nxt](), tokens)
            else:
                return word_var, tokens

    # True
    def handle_true(self, tokens):
        self.consume(tokens, T_True)
        return NameConstant(value=True), tokens

    # False
    def handle_false(self, tokens):
        self.consume(tokens, T_False)
        return NameConstant(value=False), tokens
