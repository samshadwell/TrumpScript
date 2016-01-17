# TrumpScript Tokenizer
# 1/16/2016

import re
import sys
import random
from src.trumpscript.constants import *


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
    def tokenize_file(filename) -> list:
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
                    while data[i].isalpha() or data[i] == "'":
                        word += data[i]
                        i += 1
                    if not endword.match(data[i]):
                        Tokenizer._error(line, 'nonword')
                    i -= 1  # Read one char too many, readjust.

                    # Keywords
                    if word == "is" or word == "are":
                        tokens.append(Tokenizer.toke(T_Is, None, line))
                    elif word == "if":
                        tokens.append(Tokenizer.toke(T_If, None, line))
                    elif word == "else" or word == "otherwise":
                        tokens.append(Tokenizer.toke(T_Else, None, line))
                    elif word == "true" or word == "facts" or word == "truth":
                        tokens.append(Tokenizer.toke(T_True, None, line))
                    elif word == "false" or word == "lies" or word == "nonsense":
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
                    # TODO: errors
                    # error("invalid character: %r" % c)
                i += 1
            return tokens

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
