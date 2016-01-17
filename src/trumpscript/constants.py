__author__ = 'github.com/samshadwell'

# Token constants
T_Plus = 0
T_Minus = 1
T_Times = 2
T_Over = 3
T_Less = 4
T_Greater = 5

T_LParen = 10
T_RParen = 11
T_LBrace = 12
T_RBrace = 13

T_Is = 20
T_If = 21
T_Else = 22

T_True = 30
T_False = 31
T_And = 32
T_Or = 33
T_Not = 34

T_Word = 40
T_Num = 41
T_Quote = 42

T_Make = 50
T_Question = 51
T_Print = 52
T_While = 53

# Error messages
ERROR_CODES = {
    'unterminated_quote': ["And, believe me, if I win, if I become President, that will end.", "Anyone who thinks my \
                           story is near over is sadly mistaken."],
    'nonword': ["This is a country where we speak English",
                "We have a country where to assimilate you have to speak English"],
    'badword': ["Trump doesn't want to hear it"],
    'default': ["You know, it really doesn’t matter what the media write as long as you’ve got a young and beautiful \
                piece of ass.", "The concept of global warming was created by and for the Chinese in order to make \
                U.S. manufacturing non-competitive.", "Listen you motherfucker, we're going to tax you 25 percent!"],
    'os': ["Windows? 'The big problem this country has is being PC'"],
    'freedom': ["Trump will ensure that 'America is great'"]
}
