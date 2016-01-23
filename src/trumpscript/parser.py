# Parser for TrumpScript
# 1/16/2016

from ast import *

from src.trumpscript.constants import *

class Parser:

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
        # print("Start = " + str(start))
        if start == T_Word:
            return self.handle_word(tokens)
        elif start == T_Make:
            return self.handle_make(tokens)
        elif start == T_LBrace:
            return self.handle_brace(tokens)
        elif start == T_LParen:
            return self.handle_paren(tokens)
        elif start == T_If:
            return self.handle_if(tokens)
        elif start == T_While:
            return self.handle_while(tokens)
        elif start == T_Print:
            return self.handle_print(tokens)
        elif start == T_True:
            return self.handle_true(tokens)
        elif start == T_False:
            return self.handle_false(tokens)
        elif start == T_Not:
            return self.handle_not(tokens)
        elif start == T_Quote:
            return self.handle_quote(tokens)
        elif start == T_Num:
            return self.handle_num(tokens)
        #elif start == T_End:
            #Exit method call
            #return Call(func=Name(id="exit", ctx = Load()), args=[], keywords=[], starargs=None, kwargs=None), []
        else:
            # Silent errors
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
        token = self.consume(tokens, T_Make)
        if self.peek(tokens) != T_Word :
            #TODO: write this fucking error
            print("Ooh, what you making there? It sure isn't a variable, that's for goddamn sure!")
        variable = self.consume(tokens, T_Word)
        followup = self.peek(tokens)  # Check the type of the next token to see if it's acceptable
        if followup == T_Word:
            tok = self.consume(tokens, T_Word)
            val = Name(id=tok["value"], ctx=Load())
        elif followup == T_LParen:
            val, tokens = self.handle_paren(tokens)
        elif followup == T_True:
            val, tokens = self.handle_true(tokens)
        elif followup == T_False:
            val, tokens = self.handle_false(tokens)
        elif followup == T_Not:
            val, tokens = self.handle_not(tokens)
        elif followup == T_Quote:
            val, tokens = self.handle_quote(tokens)
        elif followup == T_Num:
            val, tokens = self.handle_num(tokens)
        else:
            print("make error")
            # TODO: get real errors srsly
            val = "garbageerror"
        target = Name(id=variable["value"], ctx=Store())
        return Assign(targets=[target], value=val), tokens

    # Both Assign and EQ because why the hell not guys
    # Note that this does not have type signature because it can be expr or stmt (yeah it blows))
    def handle_is(self, left, tokens):
        self.consume(tokens, T_Is)
        followup = self.peek(tokens)  # Check the type of the next token to see if it's acceptable
        if followup == T_Word:
            tok = self.consume(tokens, T_Word)
            right = Name(id=tok["value"], ctx=Load())
        elif followup == T_LParen:
            right, tokens = self.handle_paren(tokens)
        elif followup == T_True:
            right, tokens = self.handle_true(tokens)
        elif followup == T_False:
            right, tokens = self.handle_false(tokens)
        elif followup == T_Not:
            right, tokens = self.handle_not(tokens)
        elif followup == T_Quote:
            right, tokens = self.handle_quote(tokens)
        elif followup == T_Num:
            right, tokens = self.handle_num(tokens)
        else:
            right = "ERROR"
            # TODO: real errors
            print("is_error")
        if self.peek(tokens) == T_Question:
            self.consume(tokens, T_Question)
            first = Name(id=left["value"], ctx=Load())
            return Compare(left=first, ops=[Eq()], comparators=[right]), tokens
        else:
            target = Name(id=left["value"], ctx=Store())
            return Assign(targets=[target], value=right), tokens

    # Print
    def handle_print(self, tokens) -> (stmt, list):
        self.consume(tokens, T_Print)
        followup = self.peek(tokens)
        if followup == T_Quote:
            output, tokens = self.handle_quote(tokens)
        elif followup == T_LParen:
            output, tokens = self.handle_paren(tokens)
        elif followup == T_Num:
            output, tokens = self.handle_num(tokens)
        elif followup == T_True:
            output, tokens = self.handle_true(tokens)
        elif followup == T_False:
            output, tokens = self.handle_false(tokens)
        elif followup == T_Word:
            output, tokens = self.handle_word(tokens)
        else:
            output = "error"
            print("Print broke")
            # TODO: real errors

        return Call(func=Name(id="print", ctx=Load()), args=[output], keywords=[]), tokens

    # While
    def handle_while(self, tokens) -> (stmt, list):
        token = self.consume(tokens, T_While)
        conditional, tokens = self.handle_paren(tokens)
        body, tokens = self.handle_brace(tokens)
        return While(test=conditional,body=body, orelse=[]), tokens

    # If
    def handle_if(self, tokens) -> (stmt, list):
        token = self.consume(tokens, T_If)
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

    # TODO: make this not necessary
    # BoolOp(s)
    # def handle_boolop():
        # TODO: take care of and / or
        # pass

    # BinOp(s)
    # TODO: what the fuck is going on here? I wrote this at 9am after nigh 24 hours of wakefulness
    def handle_binop(self, left, op, tokens):
        tokens.pop(0)
        nxt = self.peek(tokens)
        if nxt == T_LParen:
            right, tokens = self.handle_paren(tokens)
        elif nxt == T_Word:
            word = self.consume(tokens, T_Word)
            right = Name(id=word["value"],ctx=Load())
        elif nxt == T_Quote:
            right, tokens = self.handle_quote(tokens)
        elif nxt == T_Num:
            right, tokens = self.handle_num(tokens)
        else:
            right = "boooo"
            print("not valid binary op target error")
            # TODO: should have built an error method
        return BinOp(left=left, op=op, right=right), tokens

    # Not
    def handle_not(self, tokens):
        self.consume(tokens, T_Not)
        nxt = self.peek(tokens)
        if nxt == T_LParen:
            result, tokens = self.handle_paren(tokens)
        elif nxt == T_Word:
            result, tokens = self.handle_word(tokens)
        elif nxt == T_False:
            result, tokens = self.handle_false(tokens)
        elif nxt == T_True:
            result, tokens = self.handle_true(tokens)
        else:
            result = "error"
            print("Error in not")
            #TODO: real errors, seriously.
        return UnaryOp(op=Not(),operand=result), tokens

    # Num
    def handle_num(self, tokens):
        token = self.consume(tokens, T_Num)
        num = token["value"]
        #TODO: check for a longer expression
        return Num(num), tokens

    # Str
    def handle_quote(self, tokens):
        token = self.consume(tokens, T_Quote)
        text = token["value"]
        #TODO: check for a longer expression
        return Str(text), tokens

    # Name
    def handle_word(self, tokens):
        token = self.consume(tokens, T_Word)
        nxt = self.peek(tokens)
        if nxt == T_Is:
            return self.handle_is(token, tokens)
        else:
            word_var = Name(id=token["value"], ctx=Load())
            if nxt == T_Plus:
                return self.handle_binop(word_var, Add(), tokens)
            elif nxt == T_Minus:
                return self.handle_binop(word_var, Sub(), tokens)
            elif nxt == T_Times:
                return self.handle_binop(word_var, Mult(), tokens)
            elif nxt == T_Over:
                return self.handle_binop(word_var, Div(), tokens)
            else:
                return word_var, tokens

    # True
    def handle_true(self, tokens):
        token = self.consume(tokens, T_True)
        return NameConstant(value=True), tokens

    # False
    def handle_false(self, tokens):
        token = self.consume(tokens, T_False)
        return NameConstant(value=False), tokens
