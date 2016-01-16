# TrumpScript Tokenizer
# 1/16/2016

# Token types
T_Plus = 0
T_Minus = 1
T_Times = 2
T_Over = 3
T_LParen = 4
T_RParen = 5 
T_LBrace = 6
T_RBrace = 7
T_Is = 8
T_If = 9
T_Else = 10
T_And = 11
T_Or = 12
T_Word = 13

class tokenizer():

	def tokenizeFile(self, filename): 
		with open(filename, 'r') as src:
			data = src.read()
			tokens = []
			line = 1
			i = 0
			while i < len(data):

				c = data[i]

				#Spaces, newlines, and periods
				if c.isspace() or c == ".":
					if c == "\n":
						line += 1
					pass()

				# Operators (special symbol form) and punctuation
		        elif c == "+":
		            tokens.append(toke(T_Plus, None, line))
		        elif c == "-":
		            tokens.append(toke(T_Minus, None, line))
		        elif c == "*":
		            tokens.append(toke(T_Times, None, line))
		        elif c == "/":
		            tokens.append(toke(T_Over, None, line))

		        # Closures and precedence
		        elif c == ",":
		            tokens.append(toke(T_LParen, None, line))
		        elif c == ";":
		            tokens.append(toke(T_RParen, None, line))
		        elif c == ":":
		            tokens.append(toke(T_LBrace, None, line))
		        elif c == "!":
		            tokens.append(toke(T_RBrace, None, line))

		        # Integers (no floating point)
		        elif c.isdigit():
		            num = ""
		            while s[i].isdigit():
		                num += s[i]
		                i += 1
		            else:
		                tokens.append(toke(T_Num, int(num), line))
		            i -= 1 # Read one char too many, readjust.

		        # Words and keywords
		        elif c.isalpha():
		            word = ""
		            while s[i].isalnum():
		                word += s[i]
		                i += 1
		            i -= 1 # Read one char too many, readjust.

		            # Keywords
		           	if word == "is":
		           		tokens.append(toke(T_Is, None, line))
		           	elif word == "if":
		           		tokens.append(toke(T_If, None, line))
		           	elif word == "else" or word == "otherwise":
		           		tokens.append(toke(T_Else, None, line))
		           	elif word == "and":
		           		tokens.append(toke(T_And, None, line))
		           	elif word == "or":
		           		tokens.append(toke(T_Or, None, line))

		           	#English form of the operators
		            elif word == "plus":
			            tokens.append(toke(T_Plus, None, line))
			        elif word == "minus":
			            tokens.append(toke(T_Minus, None, line))
			        elif word == "times":
			            tokens.append(toke(T_Times, None, line))
			        elif word == "over":
			            tokens.append(toke(T_Over, None, line))

			        # Otherwise, it's just a word, interpreting is the lexer's job
		            else:
		                tokens.append(tok(T_Word, word, line))
		        else:
		        	pass()
		        	#TODO: errors
		            #error("invalid character: %r" % c)
		        i += 1
		    return tokens

	def toke(tokentype, tokenvalue, line):
		return {"type" : tokentype, "value" : tokenvalue , "line" : line}
