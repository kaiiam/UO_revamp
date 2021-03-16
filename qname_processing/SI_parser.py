#!/usr/bin/env python3
"""
Author : kai
Date   : 2021-03-16
Purpose: Rock the Casbah
"""

import argparse
import sys
from lark import Lark, Tree, Transformer


# --------------------------------------------------
def get_args():
    """get command-line arguments"""
    parser = argparse.ArgumentParser(
        description='Argparse Python script',
        formatter_class=argparse.ArgumentDefaultsHelpFormatter)

    parser.add_argument(
        'positional', metavar='str', help='A positional argument')

    parser.add_argument(
        '-a',
        '--arg',
        help='A named string argument',
        metavar='str',
        type=str,
        default='')

    parser.add_argument(
        '-i',
        '--int',
        help='A named integer argument',
        metavar='int',
        type=int,
        default=0)

    parser.add_argument(
        '-f', '--flag', help='A boolean flag', action='store_true')

    return parser.parse_args()


# --------------------------------------------------
def warn(msg):
    """Print a message to STDERR"""
    print(msg, file=sys.stderr)


# --------------------------------------------------
def die(msg='Something bad happened'):
    """warn() and exit with error"""
    warn(msg)
    sys.exit(1)


# # --------------------------------------------------
# def main():
#     """Make a jazz noise here"""
#     args = get_args()
#     str_arg = args.arg
#     int_arg = args.int
#     flag_arg = args.flag
#     pos_arg = args.positional
#
#     print('str_arg = "{}"'.format(str_arg))
#     print('int_arg = "{}"'.format(int_arg))
#     print('flag_arg = "{}"'.format(flag_arg))
#     print('positional = "{}"'.format(pos_arg))


# # --------------------------------------------------
# if __name__ == '__main__':
#     main()


# Crude Transformer based on examples
# https://lark-parser.readthedocs.io/en/latest/visitors.html#transformer
class transformer(Transformer):
    def SIGN(self, args):
        return args[0]

    def DIGIT(self, args):
        return args[0]

    def digits(self, args):
        return "".join(args)

    def factor(self, args):
        return args[0]

    def exponent(self, args):
        if len(args) == 1:
            return {
                "exponent": int(args[0]),
            }
        if len(args) == 2:
            return {
                "exponent": int("".join(args)),
            }

    def start(self, args):
        return args

    def term(self, args):
        if len(args) == 1:
            return args[0]
        elif len(args) == 3:
            return [args[0], {**args[1], **args[2]}]

    def component(self, args):
        return args[0]

    def simple_unit(self, args):
        if len(args) == 1:
            return args[0]
        elif len(args) == 2:
            return {**args[0], **args[1]}

    def annotatable(self, args):
        if len(args) == 1:
            return args[0]
        elif len(args) == 2:
            return {**args[0], **args[1]}

    # def annotation(self, args):
    #     return args[0]

    def OPERATOR(self, args):
        return {
            "operator": args[0],
        }

    def PREFIX(self, args):
        if args == 'da':
            return {
                "prefix": args[0:2],
            }
        else:
            return {
                "prefix": args[0],
            }

    def METRIC(self, args):
        #print(args[:])
        return {
          "type": "metric",
          "unit": args[:],
        }


    # def ANNOTATION(self, args):
    #     return {
    #       "type": "non-unit",
    #       "unit": "".join(args)
    #     }


# UCUM grammar based on "Exhibit 1" https://ucum.org/ucum.html
# WARN: This is a weird hybrid of the given grammar with Lark idioms.
# If it were more Lark-y, the Transformer would be nicer.
ucum_grammar = Lark('''
SIGN: "+" | "-"
DIGIT: "0" | "1" | "2" | "3" | "4" | "5" | "6" | "7" | "8" | "9"
digits: DIGIT digits | DIGIT
factor: digits
exponent: SIGN digits | digits
simple_unit: PREFIX? METRIC
annotatable: simple_unit exponent
           | simple_unit
component: annotatable
         | factor
term: term OPERATOR component
    | component
start: "/" term | term
OPERATOR: /\.|\//
PREFIX: "Y" | "Z" | "E" | "P"| "T" | "G" | "M" | "k" | "h" | "da" | "d" | "c" | "m" | "u" | "n" | "p" | "f" | "a" | "z" | "y"
METRIC: "A"| "au" | "a" | "Bq" | "B" | "C" | "°C" | "°" | "cal" | "cd" | "dyn" | "d" | "Da" | "erg" | "eV" | "F" | "Gy" | "g" | "h"| "Hz" | "H" | "J"| "kat" | "K" | "lm" | "lx" | "ly" | "l" | "mol" | "min" | "m" | "Np" | "N" | "Ω" | "Pa" | "P" | "rad" | "Sv" | "sb" | "sr" | "s" | "S" | "T" | "t"| "V" | "Wb" | "W" | "μ"  | "′′" | "′"  
%ignore " "           // Disregard spaces in text
''')

# Note the rules need to be in order if we have  "m" | "mol" then mol won't be found

# test_list = ["cm", "m.s", "m/s", "/g", "K2", "s-1", "dam", "Gg/um", "ccd" , "mmol/Ecd", "nmol/pm/ms", "°C"]

test_list = ["cBq", "m.F", "m/s", "/g", "Gy2", "s-1", "dam", "Gg/um", "ccd" , "mlm/Hz", "nH/plm/mΩ", "°C", "aSv/zS/dasr", "YWb/mΩ", "°", "m′", "′′", "mmin", "dd/hh", "ha", "aau", "ly/l", "TT/t/daDa", "eV.V-1", "Np/nN", "B.Bq-2", "μ/erg", "P.dyn-1", "kcal/sb", "aau/aa/A"]

for u in test_list:
    tree = ucum_grammar.parse(u)
    result = transformer().transform(tree)
    if isinstance(result[0], list):
        result = result[0]
    print(u, result)
