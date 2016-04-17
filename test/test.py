from src.trumpscript.compiler import Compiler
from src.trumpscript.tokenizer import Tokenizer

__author__ = 'github.com/samshadwell'


def test_tokenize_file(filename, expected):
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
            print("Expected: " + str(expected[idx]))
            print("Received: " + str(tokens[idx]))
            return False

    print("Tokenizer tests pass\n")
    return True


def test_compile(filename):
    Compiler().compile(filename)

# Bad tests. They break things (but on purpose)
# test_compile("test_files/debatevsdark.txt") # Infinite loop
# test_compile("test_files/not_english.txt") # Not english
# test_compile("test_files/not_patriotic.txt") # America is great error
# test_compile("test_files/nonterm_quote.txt") # Topical error

# The few test files that actually work
test_compile("test_files/math.txt") # Math
test_compile("test_files/debate_vs_rubio.txt") # Simple hello world
test_compile("test_files/debate_vs_hillary.txt")
test_compile("test_files/debatesvdebates.txt") # Complex hello world
test_compile("test_files/haiku.txt") #Haiku
test_compile("test_files/huge_test.tr") #Huuuuge?
test_compile("test_files/fizz_buzz.txt") # Fizzbuzz
test_compile("test_files/99-bottles.tr") # 99 Bottles of Beer song
# test_tokenize_file("test_files/toupee.txt", [T_Make, T_Word, T_Num,
#                                              T_While, T_LParen, T_Word, T_Less, T_Num, T_RParen,
#                                              T_Print, T_LParen, T_Num, T_Minus, T_Word, T_RParen,
#                                              T_Make, T_Word, T_LParen, T_Word, T_Plus, T_Num, T_RParen])
#
# test_tokenize_file("test_files/test_1.txt", [T_Make, T_Word, T_LParen, T_Not, T_False, T_RParen,
#                                              T_If, T_Word, T_Is, T_True, T_LBrace,
#                                              T_Word, T_Print, T_Word, T_Quote, T_RBrace])

