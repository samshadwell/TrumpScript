import sys
import os
import src.trumpscript.compiler
import locale

__author__ = 'github.com/samshadwell'


def main():
    if "CN" in locale.getdefaultlocale()[0].upper():
        print("We can't let China beat us!")
        return
    if len(sys.argv) != 2:
        print("Invalid usage. Provide a TrumpScript file name to compile and run")
        print("Example: TRUMP trump_file.tr")
        return

    if not os.path.isfile(sys.argv[1]):
        print("Invalid file specified")
        return

    src.trumpscript.compiler.Compiler().compile(sys.argv[1])

if __name__ == "__main__":
    main()
