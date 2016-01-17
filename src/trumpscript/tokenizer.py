# TrumpScript Tokenizer
# 1/16/2016

import os
import random
import re
import sys

from src.trumpscript.allowed_words import ALLOWED
from src.trumpscript.constants import *
from src.trumpscript.disallowed_words import DISALLOWED


class Tokenizer:
    @staticmethod
    def toke(token_type, token_value, line) -> dict:
        """
        Create a mapping for the given token
        :param token_type: the type of the token
        :param token_value: The token's value
        :param line: The line number for this token
        :return: A mapping of the properties to their values
        """
        return {"type": token_type, "value": token_value, "line": line}

    @staticmethod
    def tokenize(filename):
        """
        Tokenize the given file
        :param filename:
        :return: The tokens in the file
        """

        Tokenizer._no_pc()
        tokens = Tokenizer._first_pass(filename)
        tokens = Tokenizer._second_pass(tokens)

        return tokens

    @staticmethod
    def _no_pc() -> None:
        """
        Make sure the currently-running OS is not Windows
        :return:
        """
        if os.name == 'nt':
            Tokenizer._error(0, 'os')

    @staticmethod
    def _first_pass(filename) -> list:
        """
        Tokenize the given file
        :param filename: the file to tokenize
        :return: The tokens in the file
        """

        endword = re.compile("[:!,;\.\s\?]")

        with open(filename, 'r') as src:
            data = src.read().lower()
            tokens = []
            line = 1
            i = 0
            while i < len(data):

                c = data[i]

                # Spaces, newlines, and periods
                if c.isspace() or c == ".":
                    if c == "\n":
                        line += 1
                    pass

                # Operators (special symbol form) and punctuation
                elif c == "+":
                    tokens.append(Tokenizer.toke(T_Plus, None, line))
                elif c == "-":
                    tokens.append(Tokenizer.toke(T_Minus, None, line))
                elif c == "*":
                    tokens.append(Tokenizer.toke(T_Times, None, line))
                elif c == "/":
                    tokens.append(Tokenizer.toke(T_Over, None, line))
                elif c == "<":
                    tokens.append(Tokenizer.toke(T_Less, None, line))
                elif c == ">":
                    tokens.append(Tokenizer.toke(T_Greater, None, line))

                # Closures and precedence
                elif c == ",":
                    tokens.append(Tokenizer.toke(T_LParen, None, line))
                elif c == ";":
                    tokens.append(Tokenizer.toke(T_RParen, None, line))
                elif c == ":":
                    tokens.append(Tokenizer.toke(T_LBrace, None, line))
                elif c == "!":
                    tokens.append(Tokenizer.toke(T_RBrace, None, line))

                # Don't forget question marks
                elif c == "?":
                    tokens.append(Tokenizer.toke(T_Question, None, line))

                # Integers (no floating point)
                elif c.isdigit():
                    num = ""
                    while data[i].isdigit():
                        num += data[i]
                        i += 1
                    else:
                        tokens.append(Tokenizer.toke(T_Num, int(num), line))
                    i -= 1  # Read one char too many, readjust.

                # Words and keywords
                elif c.isalpha():
                    word = ""
                    while i < len(data) and (data[i].isalpha() or data[i] == "'"):
                        word += data[i]
                        i += 1
                    if i < len(data) and not endword.match(data[i]):
                        Tokenizer._error(line, 'nonword')
                    i -= 1  # Read one char too many, readjust.

                    # Keywords
                    if word == "is" or word == "are":
                        tokens.append(Tokenizer.toke(T_Is, None, line))
                    elif word == "if":
                        tokens.append(Tokenizer.toke(T_If, None, line))
                    elif word == "else" or word == "otherwise":
                        tokens.append(Tokenizer.toke(T_Else, None, line))
                    elif word == "true" or word == "facts" or word == "truth" or word == "fact":
                        tokens.append(Tokenizer.toke(T_True, None, line))
                    elif word == "false" or word == "lies" or word == "nonsense" or word == "lie":
                        tokens.append(Tokenizer.toke(T_False, None, line))
                    elif word == "not":
                        tokens.append(Tokenizer.toke(T_Not, None, line))
                    elif word == "and":
                        tokens.append(Tokenizer.toke(T_And, None, line))
                    elif word == "or":
                        tokens.append(Tokenizer.toke(T_Or, None, line))
                    elif word == "make":
                        tokens.append(Tokenizer.toke(T_Make, None, line))
                    elif word == "tell" or word == "say":
                        tokens.append(Tokenizer.toke(T_Print, None, line))

                    # English form of the operators
                    elif word == "plus":
                        tokens.append(Tokenizer.toke(T_Plus, None, line))
                    elif word == "minus":
                        tokens.append(Tokenizer.toke(T_Minus, None, line))
                    elif word == "times":
                        tokens.append(Tokenizer.toke(T_Times, None, line))
                    elif word == "over":
                        tokens.append(Tokenizer.toke(T_Over, None, line))
                    elif word == "less" or word == "fewer" or word == "smaller":
                        tokens.append(Tokenizer.toke(T_Less, None, line))
                    elif word == "more" or word == "greater" or word == "larger":
                        tokens.append(Tokenizer.toke(T_Greater, None, line))

                    # Otherwise, it's just a word, interpreting is the lexer's job
                    else:
                        tokens.append(Tokenizer.toke(T_Word, word, line))

                # Strings
                elif c == '"':
                    i += 1
                    quote = ""
                    while data[i] != '"':
                        quote += data[i]
                        i += 1
                        if i >= len(data):
                            Tokenizer._error(line, 'unterminated_quote')
                            pass
                    tokens.append(Tokenizer.toke(T_Quote, quote, line))

                else:
                    pass
                    Tokenizer._error(line, 'nonword')
                i += 1
            return tokens

    @staticmethod
    def _second_pass(tokens):
        """
        Makes the second pass for tokenization purposes
        :param tokens: The tokens on which we're taking a second pass
        :return: The tokens after the second pass
        """

        # Make sure we do "America is great"
        if not Tokenizer._check_for_freedom(tokens):
            Tokenizer._error(tokens[-1]['line'], 'freedom')

        # Convert "as long as" to while
        tokens = Tokenizer._combine_whiles(tokens)

        # Ensure words are English
        Tokenizer._ensure_freedom(tokens)

        # Check for disallowed words
        Tokenizer._get_rid_of_commies(tokens)

        return tokens

    @staticmethod
    def _ensure_freedom(tokens) -> None:
        """
        Make sure all the variables are in our corpus of allowed words
        :param tokens: the tokens to filter
        :return: None, throws error upon infraction of rule
        """

        for token in tokens:
            if token['type'] == T_Word and token['value'] not in ALLOWED:
                Tokenizer._error(token['line'], 'nonword')

    @staticmethod
    def _get_rid_of_commies(tokens) -> None:
        """
        Make sure none of our word tokens are in the corpus of disallowed words
        :param tokens: the tokens to filter
        :return: None, throws error upon infraction of rule
        """

        for token in tokens:
            if token['type'] == T_Word and token['value'] in DISALLOWED:
                Tokenizer._error(token['line'], 'disallowed')

    @staticmethod
    def _combine_whiles(tokens) -> list:
        """
        Combine the words "as long as" to make a while token
        :param tokens: The tokens to combine on
        :return: The tokens with
        """

        combine_at = []

        for idx in range(len(tokens)):
            if tokens[idx]['type'] == T_Word and tokens[idx]['value'] == 'as' and idx + 2 < len(tokens):
                if (tokens[idx + 1]['type'] == T_Word and tokens[idx + 1]['value'] == 'long') and (
                                tokens[idx + 2]['type'] == T_Word and tokens[idx + 2]['value'] == 'as'):
                    combine_at.append(idx)

        # Cover the degenerate case like "as long as long as"
        non_overlapping = []
        for value in combine_at:
            if value - 2 not in non_overlapping:
                non_overlapping.append(value)

        # Now combine the tokens and return
        for idx in reversed(non_overlapping):
            line = tokens[idx]['line']
            for dummy in range(3):
                tokens.pop(idx)

            tokens.insert(idx, Tokenizer.toke(T_While, None, line))

        return tokens

    @staticmethod
    def _check_for_freedom(tokens) -> bool:
        """
        Make sure that in the tokens passed, the last three are tokens representing the phrase "America is great"
        :param tokens: The tokens to verify
        :return: True if the check holds, false otherwise
        """

        last_three = tokens[-3:]
        if len(last_three) != 3:
            return False

        # Tokens for "America is great"
        expected = [Tokenizer.toke(T_Word, 'america', 0),
                    Tokenizer.toke(T_Is, None, 0),
                    Tokenizer.toke(T_Word, 'great', 0)]

        # Make sure our types and values match each of the expected
        for idx in range(3):
            if expected[idx]['type'] != last_three[idx]['type'] or expected[idx]['value'] != last_three[idx]['value']:
                return False

        for idx in range(3):
            tokens.pop()

        return True

    @staticmethod
    def _error(line, message_code) -> None:
        """
        Prints the error message and then aborts the program
        :param line: The line the error occurred on
        :param message_code: String code associated with the error message
        :return: None
        """

        print("Parsing error:")
        print("What are you doing on line " + str(line) + "?")
        if message_code in ERROR_CODES:
            print(random.choice(ERROR_CODES[message_code]))
        else:
            print(random.choice(ERROR_CODES['default']))
        sys.exit(2)
