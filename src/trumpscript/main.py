import sys
import os
import src.trumpscript.compiler

__author__ = 'github.com/samshadwell'


def main():
    if len(sys.argv) != 2:
        print("Invalid usage. Provide a TrumpScript file name to compile and run")
        print("Example: ./trumpscript trump_file.ts")
        return

    if not os.path.isfile(sys.argv[1]):
        print("Invalid file specified")
        return

    src.trumpscript.compiler.Compiler().compile(sys.argv[1])

if __name__ == "__main__":
    main()
