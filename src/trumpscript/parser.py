# Parser for TrumpScript
# 1/16/2016

from ast import *

from src.trumpscript.constants import *


class Parser:

    def __init__(self):
        self.token_to_function_map = {
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
                T_Num: self.handle_num
        }

    def parse(self, tokens) -> AST:
        filtered = self.filter_tokens(tokens)
        # Build the entirety of the Abstract Syntax tree
        return self.handle_module(filtered)

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

    def consume(self, tokens, t_type) -> dict:
        if self.peek(tokens) == t_type:
            return tokens.pop(0)
        else:
            print("failed to consume " + str(t_type) + ", got " + str(self.peek(tokens)) + "instead.")
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
            return self.token_to_function_map[start](tokens)
        except KeyError:
            tokens.pop(0)
            return Pass(), tokens

    # Stmt
    def handle_brace(self, tokens) -> (stmt, list):
        brace_contents = []
        cur_token = tokens.pop(0)
        while cur_token["type"] != T_RBrace:
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
                res = Expr(value=res)  # TODO: does it make sense to cast expressions to statements here?
            statements.append(res)
        return statements, tokens

    # Expr
    def handle_paren(self, tokens) -> (expr, list):
        paren_contents = []
        cur_token = tokens.pop(0)
        while cur_token["type"] != T_RParen:
            paren_contents.append(cur_token)
            cur_token = tokens.pop(0)
        paren_contents.append(cur_token)

        self.consume(paren_contents, T_LParen)
        expression, contents = self.handle_anything(paren_contents)
        if self.peek(contents) != T_RParen:
            # TODO: real erros
            print("passed in parenthetical with more than one expression")
        self.consume(contents, T_RParen)
        return expression, tokens

    # Assign
    def handle_make(self, tokens) -> (stmt, list):
        valid_tokens = [T_Word, T_LParen, T_True, T_False, T_Not, T_Quote, T_Num]
        self.consume(tokens, T_Make)
        variable = self.consume(tokens, T_Word)
        next_token = self.peek(tokens)  # Check the type of the next token to see if it's acceptable
        if next_token == T_Word:
            val = self._get_value_from_word_token(tokens)
        elif next_token in valid_tokens:
            val = self.token_to_function_map[next_token](tokens)
        else:
            val = _temporary_error(msg="garbageerror")
        target = Name(id=variable["value"], ctx=Store())
        return Assign(targets=[target], value=val), tokens

    # Both Assign and EQ because why the hell not guys
    # Note that this does not have type signature because it can be expr or stmt (yeah it blows))
    def handle_is(self, left, tokens):
        valid_tokens = [T_Word, T_LParen, T_True, T_False, T_Not, T_Quote, T_Num]
        self.consume(tokens, T_Is)
        next_token = self.peek(tokens)  # Check the type of the next token to see if it's acceptable
        if next_token == T_Word:
            right = self._get_value_from_word_token(tokens)
        elif next_token in valid_tokens:
            right = self.token_to_function_map[next_token](tokens)
        else:
            right = _temporary_error(msg="is_error")
        if self.peek(tokens) == T_Question:
            self.consume(tokens, T_Question)
            first = Name(id=left["value"], ctx=Load())
            return Compare(left=first, ops=[Eq()], comparators=[right]), tokens
        else:
            target = Name(id=left["value"], ctx=Store())
            return Assign(targets=[target], value=right), tokens

    # Print
    def handle_print(self, tokens) -> (stmt, list):
        valid_tokens = [T_Quote, T_LParen, T_Num, T_True, T_False, T_Word]
        self.consume(tokens, T_Print)
        next_token = self.peek(tokens)
        if next_token in valid_tokens:
            output = self.token_to_function_map[next_token](tokens)
        else:
            output = _temporary_error(msg="Print broke")
        return Call(func=Name(id="print", ctx=Load()), args=[output], keywords=[]), tokens

    # While
    def handle_while(self, tokens) -> (stmt, list):
        self.consume(tokens, T_While)
        conditional, tokens = self.handle_paren(tokens)
        body, tokens = self.handle_brace(tokens)
        return While(test=conditional, body=body, orelse=[]), tokens

    # If
    def handle_if(self, tokens) -> (stmt, list):
        self.consume(tokens, T_If)
        conditional, tokens = self.handle_paren(tokens)
        body, tokens = self.handle_brace(tokens)
        if self.peek(tokens) == T_Else:
            orelse, tokens = self.handle_else(tokens)
        else:
            orelse = []
        return If(test=conditional, body=body, orelse=orelse), tokens

    # orelse piece of if
    def handle_else(self, tokens) -> (stmt, list):
        self.consume(tokens, T_Else)
        if self.peek(tokens) == T_If:
            return self.handle_if(tokens)
        else:
            return self.handle_brace(tokens)

    # BinOp(s)
    def handle_binop(self, left, op, tokens):
        valid_tokens = [T_LParen, T_Quote, T_Num, T_Word]
        tokens.pop(0)
        next_token = self.peek(tokens)
        if next_token in valid_tokens:
            right = self.token_to_function_map[next_token](tokens)
        else:
            right = _temporary_error(msg="not valid binary op target error")
        return BinOp(left=left, op=op, right=right), tokens

    # Not
    def handle_not(self, tokens):
        valid_tokens = [T_LParen, T_Word, T_False, T_True]
        self.consume(tokens, T_Not)
        next_token = self.peek(tokens)
        if next_token in valid_tokens:
            result = self.token_to_function_map[next_token](tokens)
        else:
            result = _temporary_error(msg="Error in not")
        return UnaryOp(op=Not(), operand=result), tokens

    # Num
    def handle_num(self, tokens):
        token = self.consume(tokens, T_Num)
        num = token["value"]
        # TODO: check for a longer expression
        return Num(num), tokens

    # Str
    def handle_quote(self, tokens):
        token = self.consume(tokens, T_Quote)
        text = token["value"]
        # TODO: check for a longer expression
        return Str(text), tokens

    # Name
    def handle_word(self, tokens):
        token_to_argument_map = {T_Plus: Add, T_Minus: Sub, T_Times: Mult, T_Over: FloorDiv}
        token = self.consume(tokens, T_Word)
        next_token = self.peek(tokens)
        if next_token == T_Is:
            return self.handle_is(token, tokens)
        else:
            word_var = Name(id=token["value"], ctx=Load())
            if next_token in token_to_argument_map:
                return handle_binop(word_var, token_to_argument_map[next_token](), tokens)
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

    def _get_value_from_word_token(self, tokens):
        token = self.consume(tokens, T_Word)
        return Name(id=token["value"], ctx=Load())

    @staticmethod
    def _temporary_error(msg="error", error_value="error"):
        print(msg)
        # TODO: get real errors srsly
        return error_value
