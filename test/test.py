from src.trumpscript.constants import *
from src.trumpscript.tokenizer import Tokenizer

__author__ = 'github.com/samshadwell'


def test_file(filename, expected):
    """
    Parse the file and verify that the types are what we expect
    :param expected: the expected sequence of type codes coming from the parser
    :param filename: the file to read and parse
    :return: True indicating the parsed tokens match the expected, false otherwise
    """

    tokens = Tokenizer.tokenize(filename)
    if len(tokens) != len(expected):
        print("Tokens and expected are different lengths\n")
        return False

    for idx in range(len(expected)):
        if tokens[idx]['type'] != expected[idx]:
            print("Difference at index: " + str(idx) + "\n")
            return False

    print("All tests pass\n")
    return True


test_file("test_files/toupee.txt", [T_Make, T_Word, T_Num,
                                    T_While, T_LBrace, T_Word, T_Less, T_Num, T_RBrace,
                                    T_Word, T_Print, T_Word, T_LBrace, T_Num, T_Minus, T_Word, T_RBrace,
                                    T_Make, T_Word, T_LBrace, T_Word, T_Plus, T_Num, T_RBrace,
                                    T_Make, T_Word, T_Word])

# These two exit the program (correctly)
# test_file("test_files/nonterm_quote.txt", [])
# test_file("test_files/nonenglish.txt", [])
