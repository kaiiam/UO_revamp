#!/usr/bin/env python3
"""
Author : Kai
Date   : 2021-03-16
Purpose: Parse SI formatted inputs
Leverages the SI brochure 9th edition: https://www.bipm.org/utils/common/pdf/si-brochure/SI-Brochure-9.pdf

Run:

Test
./SI_parser.py -i input/SI/special_named_si_charcters.csv -o test_out.ttl -s input_mappings/SI/metric_labels.csv -p input_mappings/SI/prefixes.csv -e input_mappings/SI/exponents.csv -u1 input_mappings/UCUM/om_ucum_mapping.csv -u2 input_mappings/UCUM/qudt_ucum_mapping.csv -u3 input_mappings/UCUM/uo_ucum_mapping.csv -u4 input_mappings/UCUM/oboe_ucum_mapping.csv
./SI_parser.py -i input/SI/test5.csv -o test_out.ttl -s input_mappings/SI/metric_labels.csv -p input_mappings/SI/prefixes.csv -e input_mappings/SI/exponents.csv -u1 input_mappings/UCUM/om_ucum_mapping.csv -u2 input_mappings/UCUM/qudt_ucum_mapping.csv -u3 input_mappings/UCUM/uo_ucum_mapping.csv -u4 input_mappings/UCUM/oboe_ucum_mapping.csv

UCUM list from QUDT OM UO and OBOE
./SI_parser.py -i input/SI/prelim_list.csv -o working_out.ttl -s input_mappings/SI/metric_labels.csv -p input_mappings/SI/prefixes.csv -e input_mappings/SI/exponents.csv -u1 input_mappings/UCUM/om_ucum_mapping.csv -u2 input_mappings/UCUM/qudt_ucum_mapping.csv -u3 input_mappings/UCUM/uo_ucum_mapping.csv -u4 input_mappings/UCUM/oboe_ucum_mapping.csv


"""

import argparse
import sys
import csv
import collections.abc
import re
from lark import Lark, Tree, Transformer
from itertools import permutations

prefix_dict_list = [
    {'prefix': 'rdf:', 'namespace': 'http://www.w3.org/1999/02/22-rdf-syntax-ns#'},
    {'prefix': 'rdfs:', 'namespace': 'http://www.w3.org/2000/01/rdf-schema#'},
    {'prefix': 'xsd:', 'namespace': 'http://www.w3.org/2001/XMLSchema#'},
    {'prefix': 'owl:', 'namespace': 'http://www.w3.org/2002/07/owl#'},
    {'prefix': 'IAO:', 'namespace': 'http://purl.obolibrary.org/obo/IAO_'},
    {'prefix': 'unit:', 'namespace': 'http://purl.obolibrary.org/obo/unit_'},
    {'prefix': 'UO:', 'namespace': 'http://purl.obolibrary.org/obo/UO_'},
    {'prefix': 'OM:', 'namespace': 'http://www.ontology-of-units-of-measure.org/resource/om-2/'},
    {'prefix': 'QUDT:', 'namespace': 'http://qudt.org/vocab/unit/'},
    {'prefix': 'OBOE:', 'namespace': 'http://ecoinformatics.org/oboe/oboe.1.2/oboe-standards.owl#'},
    {'prefix': 'skos:', 'namespace': 'http://www.w3.org/2004/02/skos/core#'}
]


# --------------------------------------------------
def get_args():
    """get command-line arguments"""
    parser = argparse.ArgumentParser(
        description='Argparse Python script',
        formatter_class=argparse.ArgumentDefaultsHelpFormatter)

    parser.add_argument(
        '-i',
        '--input',
        help='input csv file',
        metavar='str',
        type=str,
        default='')

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

    parser.add_argument(
        '-e',
        '--exponents',
        help='Exponent labels csv',
        metavar='str',
        type=str,
        default='')

    parser.add_argument(
        '-o',
        '--output',
        help='ttl output file',
        metavar='str',
        type=str,
        default='')

    parser.add_argument(
        '-u1',
        '--ucum1',
        help='UCUM mapping keys',
        metavar='str',
        type=str,
        default='')

    parser.add_argument(
        '-u2',
        '--ucum2',
        help='UCUM mapping keys',
        metavar='str',
        type=str,
        default='')

    parser.add_argument(
        '-u3',
        '--ucum3',
        help='UCUM mapping keys',
        metavar='str',
        type=str,
        default='')

    parser.add_argument(
        '-u4',
        '--ucum4',
        help='UCUM mapping keys',
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

    def NON_PRE_METRIC(self, args):
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
            | NON_PRE_METRIC
annotatable: simple_unit exponent
           | simple_unit
component: annotatable
         | factor
term: term OPERATOR component
    | component
start: "/" term | term
OPERATOR: /\.|\//
PREFIX: "Y" | "Z" | "E" | "P"| "T" | "G" | "M" | "k" | "h" | "da" | "d" | "c" | "m" | "u" | "n" | "p" | "f" | "a" | "z" | "y"
METRIC: "A"| "a" | "Bq" | "B" | "cd" | "C" |  "Da" | "eV" | "F" | "Gy" | "g" | "Hz" | "H" | "J"| "kat" | "K" | "lm" | "lx" | "l" | "L" | "mol" |  "m" | "Np" | "N" | "Ω" | "Pa" | "rad" | "Sv" | "sr" | "s" | "S" | "T" | "t"| "V" | "Wb" | "W" | "′′" 
NON_PRE_METRIC: "au" | "°C" | "°" | "d" | "h" | "min" | "′"
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
def gen_symbol_code(result, mapping_dict, code_str):
    """
    Add code_str based on prefix and unit
    """
    unit = get_value(result['unit'], mapping_dict)
    code = result['prefix'] + unit
    result.update({code_str: code})


# --------------------------------------------------
def gen_si_ucum_list(dict_list):
    """
    Create permutations of possible UCUM strings for input unit list
    E.g., 'm.s-1' -> ['m.s-1', 's-1.m']
    https://www.geeksforgeeks.org/generate-all-the-permutation-of-a-list-in-python/
    At the moment only handels the ucum "." cases not the "/" cases
    TODO add the / UCUM cases
    """
    return_list = []
    code_exp_list = []
    for d in dict_list:
        if d['exponent'] == 1:
            exp = ''
        else:
            exp = str(d['exponent'])
        x = d['ucum_code'] + exp
        code_exp_list.append(x)
    code_exp_list = list(permutations(code_exp_list))

    for p in code_exp_list:
        ucum_str_list = []
        for i in p:
            ucum_str_list.append(i)
        outstr = '.'.join(ucum_str_list)
        return_list.append(outstr)
    return return_list


# --------------------------------------------------
def gen_label_parts(result, SI_unit_label_dict, prefix_dict, exponents_dict,label_lan):
    """
    Create labels from units and prefixes
    TODO add special case for unit = are to print hectare instead of hectoare etc
    deci might be the only exception
    """
    if get_value(result['prefix'], prefix_dict) is not None:
        prefix = get_value(result['prefix'], prefix_dict)
    else:
        prefix = ''
    unit = get_value(result['unit'], SI_unit_label_dict)
    power = str(result['exponent'])
    power = power.replace('-', '')
    power = get_value(power, exponents_dict)
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
        denominator_list.append(result)
    else:
        numerator_list.append(result)


# --------------------------------------------------
def canonical_nc_iri(numerator_list, denominator_list):
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
def canonical_nc_label(numerator_list, denominator_list, label_lan):
    return_lst = []
    # Case 1 no denominators
    if not denominator_list:
        for n in numerator_list:
            return_lst.append(n[label_lan])
    # case 2 no numerators
    elif not numerator_list:
        return_lst.append('reciprocal')
        for d in denominator_list:
            return_lst.append(d[label_lan])
    # Case 3 mix of numerators and denominators
    else:
        for n in numerator_list:
            return_lst.append(n[label_lan])
        return_lst.append('per')
        for d in denominator_list:
            return_lst.append(d[label_lan])
    return ' '.join(return_lst)


# --------------------------------------------------
def canonical_en_definition(numerator_list, denominator_list, unit_def_dict, prefix_numbers_dict, SI_unit_label_en_dict, label_lan):
    definition = None

    #print(numerator_list)

    # Case 1 no denominators, and only a SI base unit with no exponent
    if not denominator_list and len(numerator_list) == 1 and numerator_list[0]['exponent'] == 1:
        # Without prefix:
        if numerator_list[0]['prefix'] == '':
            for n in numerator_list:
                definition = get_value(key=n['unit'], dict=unit_def_dict)
        # special case for kg
        elif numerator_list[0]['prefix'] == 'k' and numerator_list[0]['unit'] == 'g':
            kilogram_def_en = 'An SI base unit which 1) is the SI unit of mass and 2) is defined by taking the fixed numerical value of the Planck constant, h, to be 6.626 070 15 × 10⁻³⁴ when expressed in the unit joule second, which is equal to kilogram square metre per second, where the metre and the second are defined in terms of c and ∆νCs.'
            definition = kilogram_def_en
        # Regular With prefix case
        elif numerator_list[0]['prefix'] != '':
            for n in numerator_list:
                si_label = get_value(key=n['unit'], dict=SI_unit_label_en_dict)
                prefix_num = get_value(key=n['prefix'], dict=prefix_numbers_dict)
                definition = f'A unit which is equal to 10{prefix_num} {si_label}.'

    # something like: 'An SI derived unit which is equal to ...'

    #print(numerator_list)

    return definition


# --------------------------------------------------
def canonical_si_code(numerator_list, denominator_list):
    # TODO use a dict of exponents mapping to f string superscript numbers to write out exponents as superscript
    # str = 'cm'
    # print(f'{str}\N{SUPERSCRIPT MINUS}\N{SUPERSCRIPT SEVEN}')
    return_lst = []
    for n in numerator_list:
        if str(n['exponent']) == '1':
            return_lst.append(n['si_code'])
        else:
            return_lst.append(n['si_code'] + str(n['exponent']))
    for n in denominator_list:
        return_lst.append(n['si_code'] + str(n['exponent']))
    return ' '.join(return_lst)


# --------------------------------------------------
def canonical_ucum_code(numerator_list, denominator_list):
    return_lst = []
    for n in numerator_list:
        if str(n['exponent']) == '1':
            return_lst.append(n['ucum_code'])
        else:
            return_lst.append(n['ucum_code'] + str(n['exponent']))
    for n in denominator_list:
        return_lst.append(n['ucum_code'] + str(n['exponent']))
    return '.'.join(return_lst)


# --------------------------------------------------
def lookahead(iterable):
    """Pass through all values from the given iterable, augmented by the
    information if there are more values to come after the current one
    (True), or if it is the last value (False).
    https://stackoverflow.com/questions/1630320/what-is-the-pythonic-way-to-detect-the-last-element-in-a-for-loop
    """
    # Get an iterator and pull the first value.
    it = iter(iterable)
    last = next(it)
    # Run the iterator to exhaustion (starting from the second value).
    for val in it:
        # Report the *previous* value (more to come).
        try:
            yield last, True
            last = val
        except StopIteration:
            return
    # Report the last value.
    try:
        yield last, False
    except StopIteration:
        return


# --------------------------------------------------
def temp_ucum_map(ucum_list, ontology_mapping_list):
    """
    Temporary lookup to UCUM to ontology mappings. Later version will use the phase 2
    UCUM parser to parse the UCUM mappings (first column at least) and convert those to
    canonical UCUM string via our function to do so, then look those up based on input
    """
    return_list = []
    for u in ucum_list:
        for x in ontology_mapping_list:
            if u == x['UCUM1'] or u == x['UCUM2'] or u == x['UCUM3'] or u == x['UCUM4']:
                return_list.append(x['IRI'])
    return return_list


# --------------------------------------------------
def format_si_ttl(iri, label, si_code, ucum_code, definition_en, mapping_list):
    qudt_regex = r"(http://qudt.org/vocab/unit/)(.*)"
    om_regex = r"(http://www.ontology-of-units-of-measure.org/resource/om-2/)(.*)"
    uo_regex = r"(http://purl.obolibrary.org/obo/UO_)(.*)"
    oboe_regex = r"(http://ecoinformatics.org/oboe/oboe.1.2/oboe-standards.owl#)(.*)"
    qudt_list = []
    om_list = []
    uo_list = []
    oboe_list = []

    for m in mapping_list:
        if re.search(qudt_regex, m):
            match = re.search(qudt_regex, m)
            qudt_id = match.group(2)
            qudt_id = 'QUDT:' + qudt_id
            qudt_list.append(qudt_id)
        if re.search(om_regex, m):
            match = re.search(om_regex, m)
            om_id = match.group(2)
            om_id = 'OM:' + om_id
            om_list.append(om_id)
        if re.search(uo_regex, m):
            match = re.search(uo_regex, m)
            uo_id = match.group(2)
            uo_id = 'UO:' + uo_id
            uo_list.append(uo_id)
        if re.search(oboe_regex, m):
            match = re.search(oboe_regex, m)
            oboe_id = match.group(2)
            oboe_id = 'OBOE:' + oboe_id
            oboe_list.append(oboe_id)

    iri = '{}{}\n'.format('unit:', iri)
    return_str = ''
    return_str += iri
    return_list = []

    # Assert that this is an owl instance
    return_list.append('  a owl:NamedIndividual')

    if label:
        return_list.append('  {}label "{}"@en'.format('rdfs:', label))

    if definition_en:
        return_list.append('  {}0000115 "{}"@en'.format('IAO:', definition_en))

    if si_code:
        return_list.append('  {}SI_code "{}"'.format('unit:', si_code))

    if ucum_code:
        return_list.append('  {}ucum_code "{}"'.format('unit:', ucum_code))

    [return_list.append('  {}exactMatch {}'.format('skos:', x)) for x in qudt_list if qudt_list]

    [return_list.append('  {}exactMatch {}'.format('skos:', x)) for x in om_list if om_list]

    [return_list.append('  {}exactMatch {}'.format('skos:', x)) for x in uo_list if uo_list]

    [return_list.append('  {}exactMatch {}'.format('skos:', x)) for x in oboe_list if oboe_list]

    # [return_list.append('  {}ucum_code "{}"'.format('unit:', u)) for u in ucum_list]

    # Add ; and . for ttl formatting
    for i, has_more in lookahead(return_list):
        if has_more:
            return_str += (i + ' ;\n')
        else:
            return_str += (i + ' .\n')
    return return_str


# --------------------------------------------------
def main():
    """Main function to test if input is SI or UCUM then parse and covert and post"""
    args = get_args()
    input_file = args.input
    SI_file = args.SI
    prefix_file = args.prefix
    exponents_file = args.exponents
    out_file = args.output

    # Read in argument input files
    input_list = []
    # open and save input data file as list of strings
    with open(input_file, mode='r', encoding='utf-8-sig') as input:
        csv_reader = csv.reader(input, delimiter=',')
        for row in csv_reader:
            input_list.append(row[0])

    om_ucum = args.ucum1
    qudt_ucum = args.ucum2
    uo_ucum = args.ucum3
    oboe_ucum = args.ucum4

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

    SI_SI_can_units_dict = {}
    for i in SI_list:
        SI_SI_can_units_dict[i['SI_symbol']] = i['SI_symbol_canonical']

    SI_UCUM_units_dict = {}
    for i in SI_list:
        SI_UCUM_units_dict[i['SI_symbol']] = i['UCUM_symbol']

    SI_unit_label_en_dict = {}
    for i in SI_list:
        SI_unit_label_en_dict[i['SI_symbol']] = i['label_en']

    SI_unit_def_en_dict = {}
    for i in SI_list:
        SI_unit_def_en_dict[i['SI_symbol']] = i['definition_en']

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

    prefix_numbers_dict = {}
    for i in prefix_list:
        prefix_numbers_dict[i['symbol']] = i['prefix_num']

    # Read in powers
    exponents_list = []
    # open and save input file as list of dictionaries
    with open(exponents_file, mode='r', encoding='utf-8-sig') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            exponents_list.append(row)

    exponents_en_dict = {}
    for i in exponents_list:
        exponents_en_dict[i['power']] = i['label_en']

    ###### Mappings #######################################
    # Read in ontology to UCUM mappings
    om_ucum_list = []
    # open and save input file as list of dictionaries
    with open(om_ucum, mode='r', encoding='utf-8-sig') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            om_ucum_list.append(row)

    qudt_ucum_list = []
    # open and save input file as list of dictionaries
    with open(qudt_ucum, mode='r', encoding='utf-8-sig') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            qudt_ucum_list.append(row)

    uo_ucum_list = []
    # open and save input file as list of dictionaries
    with open(uo_ucum, mode='r', encoding='utf-8-sig') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            uo_ucum_list.append(row)

    oboe_ucum_list = []
    # open and save input file as list of dictionaries
    with open(oboe_ucum, mode='r', encoding='utf-8-sig') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            oboe_ucum_list.append(row)

    # Join all the input ontology to UCUM mappings into single list of dict
    ontology_mapping_list = om_ucum_list + qudt_ucum_list + uo_ucum_list + oboe_ucum_list
    #print(ontology_mapping_list)

    # test_list = ["cm", "m.s", "m/s", "/g", "K2", "s-1", "m/s/T", "N/Wb/W", "Gy2.lm.lx-1"]
    # test_list = ["m.s-1", "m/s", "N.V-2", "N/V2" ]
    # test_list = ["m.s-1", "m/s", "N.V-2", "N/V2", "A/N/W", "A.N-1.W-1"]
    # test_list = ["A.N-1.W-1"]
    # test_list = ["A.B-1.C-1.d-1.eV-1"]
    # test_list = ["A2/B3/C4/d5"]
    # test_list = ["aA/aB/aC"]
    # test_list = ["/ng/l"]
    # test_list = ["L/l"]
    # test_list = ['Pa.aa-1']
    # test_list = ['m2.g.W-2.A-1', 'g.m2.A-1.W-2']
    # test_list = ["nm.us-2"]
    # test_list = ['/mg/as']
    # test_list = ['mg-1.as-1']
    # test_list = ['A2.mN']
    # test_list = ['mm2.Gg.pW-2.yA-1']
    test_list = ['m.s-1', 'asdf']

    valid_SI_input_list = []

    # # breakup input list one term at a time
    for u in input_list:
    # for u in test_list:
        try:
            tree = si_grammar.parse(u)
            result = transformer().transform(tree)
            valid_SI_input_list.append(u)
        except:
            print(f"Could not process '{u}' with SI parser")

    # Open outfile
    f = open(out_file, mode='w', encoding='utf-8-sig')

    # write out prefixes followed by linebreak
    for p in prefix_dict_list:
        print('@prefix {} <{}> .'.format(p['prefix'], p['namespace']), file=f)
    print('', file=f)
    print('IAO:0000115 a rdf:Property ;', file=f)
    print('	rdfs:label "definition" .', file=f)
    print('', file=f)



    for u in valid_SI_input_list:
        tree = si_grammar.parse(u)
        result = transformer().transform(tree)
        res_flat = flatten(result)
        # print(u, res_flat)

        new_dict_list = []
        # Convert the inputs into a preprocessed list of dict
        for r in res_flat:
            pre_process_unit_list(r, u, new_dict_list)

        # Add codes to dict:
        for r in new_dict_list:
            # Create the NCname code from prefix and unit
            gen_symbol_code(result=r, mapping_dict=SI_NC_units_dict, code_str='nc_code' )
            # create the SI code from prefix and unit
            gen_symbol_code(result=r, mapping_dict=SI_SI_can_units_dict, code_str='si_code')
            # create the UCUM codes from prefix and unit
            gen_symbol_code(result=r, mapping_dict=SI_NC_units_dict, code_str='ucum_code')

        # print(u, new_dict_list)

        # Function to generate list of UCUM codes from results dict list
        # Permute Possible UCUM strings
        UCUM_SI_list = gen_si_ucum_list(dict_list=new_dict_list)
        #print(UCUM_SI_list)

        # Function to create labels from units and prefixes
        # pass in desired language SI unit, prefix and exponents dicts + label_lan
        for r in new_dict_list:
            gen_label_parts(result=r, SI_unit_label_dict=SI_unit_label_en_dict, prefix_dict=prefix_en_dict, exponents_dict=exponents_en_dict, label_lan='label_en')
        # print(u, new_dict_list)

        # Function to split numerator and denominator into two lists
        numerator_list = []
        denominator_list = []
        for r in new_dict_list:
            split_num_denom(result=r, numerator_list=numerator_list, denominator_list=denominator_list)
        # print(u, 'num:', numerator_list, 'denom:', denominator_list)

        # # Sort in canonical alphabetical order
        numerator_list = sorted(numerator_list, key=lambda k: (k['nc_code'].casefold(), k))
        denominator_list = sorted(denominator_list, key=lambda k: (k['nc_code'].casefold(), k))
        # print(u, numerator_list, denominator_list)

        # # Generate canonical nc_name code
        # print(u, '->', canonical_nc_iri(numerator_list=numerator_list,denominator_list=denominator_list))
        si_nc_name_iri = canonical_nc_iri(numerator_list=numerator_list,denominator_list=denominator_list)

        # # Generate canonical term label
        # print(u, '->', canonical_nc_label(numerator_list=numerator_list, denominator_list=denominator_list, label_lan='label_en'))
        label = canonical_nc_label(numerator_list=numerator_list, denominator_list=denominator_list, label_lan='label_en')

        # Generate canonical english definition
        # SI_unit_def_en_dict
        # TODO/WORKING
        definition_en = canonical_en_definition(numerator_list=numerator_list, denominator_list=denominator_list,
                                                unit_def_dict=SI_unit_def_en_dict, prefix_numbers_dict=prefix_numbers_dict, SI_unit_label_en_dict=SI_unit_label_en_dict, label_lan='label_en')
        #print(definition_en)

        # Generate canonical SI code e.g. `Pa s`
        # First pass complete, Later can fix superscript issue with fstrings TODO
        # print(u, '->', canonical_si_code(numerator_list=numerator_list,denominator_list=denominator_list))
        si_code = canonical_si_code(numerator_list=numerator_list,denominator_list=denominator_list)

        # Generate canonical UCUM code
        ucum_code = canonical_ucum_code(numerator_list=numerator_list, denominator_list=denominator_list)
        #print(ucum_code)

        # Map UCUM codes to external Ontologies
        # LATER TODO change this to use the mappings of canonical UCUM strings by calling phase 2 on Simon’s mappings
        mapping_list = temp_ucum_map(ucum_list=UCUM_SI_list, ontology_mapping_list=ontology_mapping_list)
        #print(mapping_list)

        # Format ttl for SI parser results
        print(format_si_ttl(iri=si_nc_name_iri, label=label, si_code=si_code, ucum_code=ucum_code, definition_en=definition_en, mapping_list=mapping_list), file=f)


        # --------------------------------------------------
if __name__ == '__main__':
    main()