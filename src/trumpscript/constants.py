__author__ = 'github.com/samshadwell'

# Token constants
T_End = -1

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
T_Input = 54

T_Mod = 55

# Error messages
ERROR_CODES = {
    # For quotes that didn't get terminated
    'unterminated_quote': ["And, believe me, if I win, if I become President, that will end.", "Anyone who thinks my " +
                           "story is near over is sadly mistaken."],
    # If they try to use a word that isn't common English
    'nonword': ["This is a country where we speak English",
                "We have a country where to assimilate you have to speak English"],
    # If they try to use a word that we've explicitly banned
    'badword': ["Trump doesn't want to hear it"],
    # Generic errors for when we're lazy
    'default': ["You know, it really doesn’t matter what the media write as long as you’ve got a young and beautiful " +
                "piece of ass.", "The concept of global warming was created by and for the Chinese in order to make " +
                "U.S. manufacturing non-competitive.", "Listen you motherfucker, we're going to tax you 25 percent!"],
    # If they try to run on a PC
    'os': ["Windows? 'The big problem this country has is being PC'"],
    # If they try to run on a Mac
    'boycott': ["Mac? 'Boycott all Apple products  until such time as Apple " +
                "gives cellphone info to authorities regarding radical " +
                "Islamic terrorist couple from Cal'"],
    # They had better let us know that 'America is great.'
    'freedom': ["Trump will ensure that 'America is great'"],
    # Don't even try to make numbers smaller than 1,000,000
    'too_small': ["I'm really rich.", "Part of the beauty of me is I'm very rich."],
    # Let them know we don't need to run as root
    'root': ['America doesn\'t need root to be great.'],
    # If we're not happy with one of this process's SSL certificates
    'ssl': ["An 'extremely credible source' has called my office and told me that one of this process's SSL certificates is a fraud."]
}
