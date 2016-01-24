import os
import sys

from trumpscript.compiler import *
from trumpscript.utils import *

__author__ = 'github.com/samshadwell'

def main():
    if len(sys.argv) != 2:
        print("Invalid usage. Provide a TrumpScript file name to compile and run")
        print("Example: TRUMP trump_file.tr")
        return

    if not os.path.isfile(sys.argv[1]):
        print("Invalid file specified")
        return

    # Decide whether to ignore system warnings
    shut_up = os.getenv('TRUMP_SHUT_UP')
    try:
        shut_up = int(shut_up) != 0 if shut_up else False
    except ValueError:
        shut_up = False

    Utils.verify_system(not shut_up)

    # Compile and go
    Compiler().compile(sys.argv[1])

if __name__ == "__main__":
    main()
