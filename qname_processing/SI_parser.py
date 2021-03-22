#!/usr/bin/env python3
"""
Author : kai
Date   : 2021-03-16
Purpose: Parse SI formatted inputs

Run:

./SI_parser.py -s input_mappings/SI/metric_labels.csv -p input_mappings/SI/prefixes.csv

"""

import argparse
import sys
import csv
import collections.abc
from lark import Lark, Tree, Transformer


# --------------------------------------------------
def get_args():
    """get command-line arguments"""
    parser = argparse.ArgumentParser(
        description='Argparse Python script',
        formatter_class=argparse.ArgumentDefaultsHelpFormatter)

    parser.add_argument(
        '-s',
        '--SI',
        help='SI unit labels and codes mapping csv',
        metavar='str',
        type=str,
        default='')

    parser.add_argument(
        '-p',
        '--prefix',
        help='SI prefixes labels and codes mapping csv',
        metavar='str',
        type=str,
        default='')

    # parser.add_argument(
    #     '-f', '--flag', help='A boolean flag', action='store_true')

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
simple_unit: METRIC
            | PREFIX? METRIC
annotatable: simple_unit exponent
           | simple_unit
component: annotatable
         | factor
term: term OPERATOR component
    | component
start: "/" term | term
OPERATOR: /\.|\//
PREFIX: "Y" | "Z" | "E" | "P"| "T" | "G" | "M" | "k" | "h" | "da" | "d" | "c" | "m" | "u" | "n" | "p" | "f" | "a" | "z" | "y"
METRIC: "A"| "au" | "a" | "Bq" | "B" | "C" | "°C" | "°" | "cd" | "d" | "Da" | "eV" | "F" | "Gy" | "g" | "h"| "Hz" | "H" | "J"| "kat" | "K" | "lm" | "lx" | "l" | "L" | "mol" | "min" | "m" | "Np" | "N" | "Ω" | "Pa" | "rad" | "Sv" | "sr" | "s" | "S" | "T" | "t"| "V" | "Wb" | "W" | "′′" | "′"  
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
def gen_nc_code(result, mapping_dict):
    """
    Add nc_code based on prefix and unit
    """
    nc_unit = get_value(result['unit'], mapping_dict)
    nc_code = result['prefix'] + nc_unit
    result.update({'nc_code': nc_code})


# --------------------------------------------------
def gen_label_parts(result, SI_unit_label_dict, prefix_dict, powers_dict,label_lan):
    if get_value(result['prefix'], prefix_dict) is not None:
        prefix = get_value(result['prefix'], prefix_dict)
    else:
        prefix = ''
    unit = get_value(result['unit'], SI_unit_label_dict)
    power = str(result['exponent'])
    power = power.replace('-', '')
    power = get_value(power, powers_dict)
    if power is None:
        label_str = prefix + unit
    else:
        label_str = power + ' ' + prefix + unit
    result.update({label_lan: label_str})


# --------------------------------------------------
def split_num_denom(result, numerator_list, denominator_list):
    """
    Separate input list into numerator and denominator lists
    """
    # split based on result['exponent']
    if str(result['exponent'])[0] == "-":
        #print('denominator_list')
        denominator_list.append(result)
    else:
        #print('numerator_list')
        numerator_list.append(result)


# --------------------------------------------------
def canonical_nc_label(numerator_list, denominator_list):
    return_lst = []
    for n in numerator_list:
        if str(n['exponent']) == '1':
            return_lst.append(n['nc_code'])
        else:
            return_lst.append(n['nc_code'] + str(n['exponent']))
    for n in denominator_list:
        return_lst.append(n['nc_code'] + str(n['exponent']))
    return '.'.join(return_lst)


# --------------------------------------------------
def main():
    """Main function to test if input is SI or UCUM then parse and covert and post"""
    args = get_args()
    #input_file = args.input
    SI_file = args.SI
    prefix_file = args.prefix

    # Read in SI units
    SI_list = []
    # open and save input file as list of dictionaries
    with open(SI_file, mode='r', encoding='utf-8-sig') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            SI_list.append(row)

    SI_NC_units_dict = {}
    for i in SI_list:
        SI_NC_units_dict[i['SI_symbol']] = i['NC_symbol']

    SI_unit_label_en_dict = {}
    for i in SI_list:
        SI_unit_label_en_dict[i['SI_symbol']] = i['label_en']

    # Read in SI prefixes
    prefix_list = []
    # open and save input file as list of dictionaries
    with open(prefix_file, mode='r', encoding='utf-8-sig') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            prefix_list.append(row)

    prefix_en_dict = {}
    for i in prefix_list:
        prefix_en_dict[i['symbol']] = i['label_en']

    powers_en_dict = {'1': None, '2': 'square', '3': 'cubic', '4': 'quartic', '5': 'quintic', '6': 'sextic', '7': 'septic',
                   '8': 'octic', '9': 'nonic', '10': 'decic'}

    # test_list = ["cm", "m.s", "m/s", "/g", "K2", "s-1", "dam", "Gg/um", "ccd" , "mmol/Ecd", "nmol/pm/ms", "°C"]
    test_list = ["cBq", "m.F", "m/s", "/g", "Gy2", "s-1", "dam", "Gg/um", "ccd", "mlm/Hz", "nH/plm/mΩ", "°C",
                 "aSv/zS/dasr", "YWb/mΩ", "°", "m′", "′′", "mmin", "dd/hh", "ha", "aau", "L/l", "TT/t/daDa", "eV.V-1",
                 "Np/nN", "B.Bq-2", "Pa.lm-1", "aau/aa/A"]

    # test_list = ["cm", "m.s", "m/s", "/g", "K2", "s-1", "m/s/T", "N/Wb/W", "Gy2.lm.lx-1"]
    # test_list = ["m.s-1", "m/s", "N.V-2", "N/V2" ]
    # test_list = ["m.s-1", "m/s", "N.V-2", "N/V2", "A/N/W", "A.N-1.W-1"]
    # test_list = ["A.N-1.W-1"]
    # test_list = ["A.B-1.C-1.d-1.eV-1"]
    # test_list = ["A2/B/C/d"]
    # test_list = ["aA/aB/aC"]
    # test_list = ["/ng/l"]
    # test_list = ["L/l"]
    # test_list = ['Pa.aa-1']
    # test_list = ['m2.g.W-2.A-1', 'g.m2.A-1.W-2']
    # test_list = ["nm.us-2"]
    # test_list = ['m.F']

    # # breakup input list one term at a time
    for u in test_list:
        tree = si_grammar.parse(u)
        result = transformer().transform(tree)
        res_flat = flatten(result)
        #print(u, res_flat)

        new_dict_list = []
        # Convert the inputs into a preprocessed list of dict
        for r in res_flat:
            pre_process_unit_list(r, u, new_dict_list)

        # # Function to create the NCname code from prefix and unit
        for r in new_dict_list:
            gen_nc_code(result=r, mapping_dict=SI_NC_units_dict)
        # print(u, new_dict_list)

        # Function to create labels from units and prefixes
        # pass in desired language SI unit, prefix and powers dicts + label_lan
        for r in new_dict_list:
            gen_label_parts(result=r, SI_unit_label_dict=SI_unit_label_en_dict, prefix_dict=prefix_en_dict, powers_dict=powers_en_dict, label_lan='label_en')
        print(u, new_dict_list)

        # Function to split numerator and denominator into two lists
        numerator_list = []
        denominator_list = []
        for r in new_dict_list:
            split_num_denom(result=r, numerator_list=numerator_list, denominator_list=denominator_list)
        #print(u, 'num:', numerator_list, 'denom:', denominator_list)

        # Sort in canonical alphebetical order
        numerator_list = sorted(numerator_list, key=lambda k: k['nc_code'])
        denominator_list = sorted(denominator_list, key=lambda k: k['nc_code'])
        #print(u, numerator_list, denominator_list)

        # Print canonical nc_name code
        #print(u, '->', canonical_nc_label(numerator_list=numerator_list,denominator_list=denominator_list))



    # --------------------------------------------------
if __name__ == '__main__':
    main()