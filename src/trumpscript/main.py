import os
import sys

from trumpscript.compiler import *
from trumpscript.utils import *

__author__ = 'github.com/samshadwell'

def main():
    valid = True
    wall = False
    if len(sys.argv) == 1:
        valid = False
    elif len(sys.argv) == 3:
        if sys.argv[1] == '-Wall':
            wall = True
        else:
            valid = False

    if not valid:
        print("Invalid usage. Provide a TrumpScript file name to compile and run")
        print("Specifying the Wall flag prevents the program from running from "
            "Mexican locales")
        print("Example: TRUMP -Wall trump_file.tr")
        return

    if not os.path.isfile(sys.argv[-1]):
        print("Invalid file specified")
        return

    # Decide whether to ignore system warnings
    shut_up = os.getenv('TRUMP_SHUT_UP')
    try:
        shut_up = int(shut_up) != 0 if shut_up else False
    except ValueError:
        shut_up = False

    Utils.verify_system(not shut_up, wall)

    # Compile and go
    Compiler().compile(sys.argv[-1])

if __name__ == "__main__":
    main()
