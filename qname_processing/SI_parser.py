#!/usr/bin/env python3
"""
Author : kai
Date   : 2021-03-16
Purpose: Parse SI formatted inputs

Run:

./SI_parser.py

"""

import argparse
import sys
import collections.abc
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


# SI grammar based on "Exhibit 1" https://ucum.org/ucum.html
si_grammar = Lark('''
SIGN: "-"
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
METRIC: "A"| "au" | "a" | "Bq" | "B" | "C" | "°C" | "°" | "cd" | "d" | "Da" | "eV" | "F" | "Gy" | "g" | "h"| "Hz" | "H" | "J"| "kat" | "K" | "lm" | "lx" | "l" | "L" | "mol" | "min" | "m" | "Np" | "N" | "Ω" | "Pa" | "P" | "rad" | "Sv" | "sr" | "s" | "S" | "T" | "t"| "V" | "Wb" | "W" | "′′" | "′"  
%ignore " "           // Disregard spaces in text
''')
# Note the rules need to be in order if we have  "m" | "mol" then mol won't be found


# --------------------------------------------------
def flatten(x):
    """
    https://stackoverflow.com/questions/42102473/parsing-values-from-a-list-of-dictionaries-with-nested-list-in-python
    """
    if isinstance(x, dict):
        return [x]
    elif isinstance(x, collections.abc.Iterable):
        return [a for i in x for a in flatten(i)]
    else:
        return [x]


# --------------------------------------------------
def get_key(val, dict):
    for key, value in dict.items():
        if val == value:
            return key
    return "key doesn't exist"


# --------------------------------------------------
def get_value(key, dict):
    for k, value in dict.items():
        if k == key:
            return value
    return None


# --------------------------------------------------
def pre_process_unit_list(result, original, dict_list):
    """
    Removes operators "." or "/" to get this back `'operator': '.',`
    Deals with start = "/" special case
    Writes out all terms with prefixes (empty string if none exist)
    Write out all terms with exponents (including 1 if none exist)
    """
    # Get prefix if existing:
    if "prefix" in result:
        prefix = result['prefix']
    else:
        prefix = ''

    if get_value(key="operator", dict=result) == "/":
        # if it doesn't have an exponent key create one at -1 else change exp to -
        if "exponent" not in result:
            x = {'prefix': prefix, 'type': result['type'], 'unit': result['unit'], 'exponent': int('-1')}
            dict_list.append(x)
        else:
            exp = int('-' + str(result['exponent']))
            x = {'prefix': prefix, 'type': result['type'], 'unit': result['unit'], 'exponent': exp}
            dict_list.append(x)
    # no operator or . case
    else:
        # Get or create exponent
        if "exponent" in result:
            exponent = result['exponent']
        elif original[0] == '/':
            exponent = -1
        else:
            exponent = 1
        x = {'prefix': prefix, 'type': result['type'], 'unit': result['unit'], 'exponent': exponent}
        dict_list.append(x)

    return dict_list


# --------------------------------------------------
def main():
    """Main function to test if input is SI or UCUM then parse and covert and post"""

    # test_list = ["cm", "m.s", "m/s", "/g", "K2", "s-1", "dam", "Gg/um", "ccd" , "mmol/Ecd", "nmol/pm/ms", "°C"]
    # test_list = ["cBq", "m.F", "m/s", "/g", "Gy2", "s-1", "dam", "Gg/um", "ccd", "mlm/Hz", "nH/plm/mΩ", "°C",
    #              "aSv/zS/dasr", "YWb/mΩ", "°", "m′", "′′", "mmin", "dd/hh", "ha", "aau", "L/l", "TT/t/daDa", "eV.V-1",
    #              "Np/nN", "B.Bq-2", "P.lm-1", "aau/aa/A"]

    # test_list = ["cm", "m.s", "m/s", "/g", "K2", "s-1", "m/s/T", "N/Wb/W", "Gy2.lm.lx-1"]
    # test_list = ["m.s-1", "m/s", "N.V-2", "N/V2" ]
    # test_list = ["m.s-1", "m/s", "N.V-2", "N/V2", "A/N/W", "A.N-1.W-1"]
    # test_list = ["m.s-1"]
    # test_list = ["A.N-1.W-1"]
    # test_list = ["A.B-1.C-1.d-1.eV-1"]
    # test_list = ["A2/B/C/d"]
    # test_list = ["aA/aB/aC"]
    test_list = ["/ng/L"]

    # # breakup input list one term at a time
    for u in test_list:
        tree = si_grammar.parse(u)
        result = transformer().transform(tree)
        res_flat = flatten(result)
        #print(u, res_flat)

        new_dict_list = []
        # Function to convert the x/y operator to the x.y-1 style
        for r in res_flat:
            #print(r)
            pre_process_unit_list(r, u, new_dict_list)
        print(u, new_dict_list)



# --------------------------------------------------
if __name__ == '__main__':
    main()