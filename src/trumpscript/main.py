import argparse
import os
import sys

from trumpscript.compiler import *
from trumpscript.utils import *

__author__ = 'github.com/samshadwell'

def main():
    parser = argparse.ArgumentParser(prog='TRUMP', description='Making programming great again')
    parser.add_argument('--Wall', action='store_true', help='If set, prevents running program from Mexican locales')
    parser.add_argument('--shut_up', action='store_true', help='If set, ignore all system warnings and run program. '
                                                               'Overrides --Wall')
    parser.add_argument('program', nargs=1, help='TrumpScript program to run')
    args = parser.parse_args()

    if not os.path.isfile(args.program[0]):
        print("Invalid file specified,")
        return

    # Decide whether to ignore system warnings
    if not args.shut_up:
        Utils.verify_system(args.Wall)

    # Compile and go
    Compiler().compile(sys.argv[-1])

if __name__ == "__main__":
    main()
