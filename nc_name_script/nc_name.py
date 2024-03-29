#!/usr/bin/env python3
"""
Author : Kai
Date   : 2021-03-16
Purpose: Parse SI formatted inputs
Leverages the SI brochure 9th edition: https://www.bipm.org/utils/common/pdf/si-brochure/SI-Brochure-9.pdf

Run:

Test
./nc_name.py -d data/test/test1.csv -o output/test/test1.ttl -s input_mappings/input_dicts/input_ucum_dict.csv -p input_mappings/input_dicts/prefixes.csv -e input_mappings/input_dicts/exponents.csv -u1 input_mappings/UCUM/om_ucum_mapping.csv -u2 input_mappings/UCUM/qudt_ucum_mapping.csv -u3 input_mappings/UCUM/uo_ucum_mapping.csv -u4 input_mappings/UCUM/oboe_ucum_mapping.csv -u5 input_mappings/UCUM/nerc_p06_ucum_mapping.csv
./nc_name.py -d data/test/test2.csv -o output/test/test2.ttl -s input_mappings/input_dicts/input_ucum_dict.csv -p input_mappings/input_dicts/prefixes.csv -e input_mappings/input_dicts/exponents.csv -u1 input_mappings/UCUM/om_ucum_mapping.csv -u2 input_mappings/UCUM/qudt_ucum_mapping.csv -u3 input_mappings/UCUM/uo_ucum_mapping.csv -u4 input_mappings/UCUM/oboe_ucum_mapping.csv -u4 input_mappings/UCUM/oboe_ucum_mapping.csv -u5 input_mappings/UCUM/nerc_p06_ucum_mapping.csv
./nc_name.py -d data/test/test3.csv -o output/test/test3.ttl -s input_mappings/input_dicts/input_ucum_dict.csv -p input_mappings/input_dicts/prefixes.csv -e input_mappings/input_dicts/exponents.csv -u1 input_mappings/UCUM/om_ucum_mapping.csv -u2 input_mappings/UCUM/qudt_ucum_mapping.csv -u3 input_mappings/UCUM/uo_ucum_mapping.csv -u4 input_mappings/UCUM/oboe_ucum_mapping.csv -u4 input_mappings/UCUM/oboe_ucum_mapping.csv -u5 input_mappings/UCUM/nerc_p06_ucum_mapping.csv
./nc_name.py -d data/test/test4.csv -o output/test/test4.ttl -s input_mappings/input_dicts/input_ucum_dict.csv -p input_mappings/input_dicts/prefixes.csv -e input_mappings/input_dicts/exponents.csv -u1 input_mappings/UCUM/om_ucum_mapping.csv -u2 input_mappings/UCUM/qudt_ucum_mapping.csv -u3 input_mappings/UCUM/uo_ucum_mapping.csv -u4 input_mappings/UCUM/oboe_ucum_mapping.csv -u4 input_mappings/UCUM/oboe_ucum_mapping.csv -u5 input_mappings/UCUM/nerc_p06_ucum_mapping.csv
./nc_name.py -d data/test/test5.csv -o output/test/test5.ttl -s input_mappings/input_dicts/input_ucum_dict.csv -p input_mappings/input_dicts/prefixes.csv -e input_mappings/input_dicts/exponents.csv -u1 input_mappings/UCUM/om_ucum_mapping.csv -u2 input_mappings/UCUM/qudt_ucum_mapping.csv -u3 input_mappings/UCUM/uo_ucum_mapping.csv -u4 input_mappings/UCUM/oboe_ucum_mapping.csv -u4 input_mappings/UCUM/oboe_ucum_mapping.csv -u5 input_mappings/UCUM/nerc_p06_ucum_mapping.csv
./nc_name.py -d data/test/test6.csv -o output/test/test6.ttl -s input_mappings/input_dicts/input_ucum_dict.csv -p input_mappings/input_dicts/prefixes.csv -e input_mappings/input_dicts/exponents.csv -u1 input_mappings/UCUM/om_ucum_mapping.csv -u2 input_mappings/UCUM/qudt_ucum_mapping.csv -u3 input_mappings/UCUM/uo_ucum_mapping.csv -u4 input_mappings/UCUM/oboe_ucum_mapping.csv -u4 input_mappings/UCUM/oboe_ucum_mapping.csv -u5 input_mappings/UCUM/nerc_p06_ucum_mapping.csv


UCUM list from QUDT OM UO OBOE and NERC
./nc_name.py -d data/production/working_pooled_unit_codes.csv -o output/production/working_output.ttl -s input_mappings/input_dicts/input_ucum_dict.csv -p input_mappings/input_dicts/prefixes.csv -e input_mappings/input_dicts/exponents.csv -u1 input_mappings/UCUM/om_ucum_mapping.csv -u2 input_mappings/UCUM/qudt_ucum_mapping.csv -u3 input_mappings/UCUM/uo_ucum_mapping.csv -u4 input_mappings/UCUM/oboe_ucum_mapping.csv -u5 input_mappings/UCUM/nerc_p06_ucum_mapping.csv

"""

import argparse
import sys
#sys.setrecursionlimit(10000) #if flatten causes memory issue from recursion
import csv
import collections.abc
import re
from lark import Lark, Tree, Transformer
from itertools import permutations
from urllib import parse

prefix_dict_list = [
    {'prefix': 'rdf:', 'namespace': 'http://www.w3.org/1999/02/22-rdf-syntax-ns#'},
    {'prefix': 'rdfs:', 'namespace': 'http://www.w3.org/2000/01/rdf-schema#'},
    {'prefix': 'xsd:', 'namespace': 'http://www.w3.org/2001/XMLSchema#'},
    {'prefix': 'owl:', 'namespace': 'http://www.w3.org/2002/07/owl#'},
    {'prefix': 'IAO:', 'namespace': 'http://purl.obolibrary.org/obo/IAO_'},
    {'prefix': 'unit:', 'namespace': 'https://w3id.org/units/'},
    {'prefix': 'UO:', 'namespace': 'http://purl.obolibrary.org/obo/UO_'},
    {'prefix': 'OM:', 'namespace': 'http://www.ontology-of-units-of-measure.org/resource/om-2/'},
    {'prefix': 'QUDT:', 'namespace': 'http://qudt.org/vocab/unit/'},
    {'prefix': 'OBOE:', 'namespace': 'http://ecoinformatics.org/oboe/oboe.1.2/oboe-standards.owl#'},
    {'prefix': 'NERC_P06:', 'namespace': 'http://vocab.nerc.ac.uk/collection/P06/current/'},
    {'prefix': 'skos:', 'namespace': 'http://www.w3.org/2004/02/skos/core#'}
]


# --------------------------------------------------
def get_args():
    """get command-line arguments"""
    parser = argparse.ArgumentParser(
        description='Argparse Python script',
        formatter_class=argparse.ArgumentDefaultsHelpFormatter)

    parser.add_argument(
        '-d',
        '--input',
        help='input data csv file',
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

    parser.add_argument(
        '-u5',
        '--ucum5',
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

    def CONVENTIONAL(self, args):
        #print(args[:])
        return {
          "type": "conventional",
          "unit": args[:],
        }

    def CONVENTIONAL_BRACKETS(self, args):
        #print(args[:])
        return {
          "type": "conventional",
          "unit": args[:],
        }

    def CONVENTIONAL_MIXED_BRACKETS(self, args):
        #print(args[:])
        return {
          "type": "conventional",
          "unit": args[:],
        }

    def EXCEPTION(self, args):
        #print(args[:])
        return {
          "prefix": "d",
          "type": "metric",
          "unit": 'ar',
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
            | CONVENTIONAL
            | CONVENTIONAL_BRACKETS
            | CONVENTIONAL_MIXED_BRACKETS
            | EXCEPTION
annotatable: simple_unit exponent
           | simple_unit
component: annotatable
         | factor
term: term OPERATOR component
    | component
start: "/" term | term
OPERATOR: /\.|\//
PREFIX: "Y" | "Z" | "E" | "P"| "T" | "G" | "M" | "k" | "h" | "da" | "d" | "c" | "m" | "u" | "n" | "p" | "f" | "a" | "z" | "y"
METRIC: "ar" | "A"| "Bq" | "B" | "cd" | "C" |  "eV" | "F" | "Gy" | "g" | "Hz" | "H" | "J"| "kat" | "K" | "lm" | "lx" | "L" | "mol" |  "m" | "Np" | "N" | "Ohm" | "Pa" | "rad" | "Sv" | "sr" | "s" | "S" | "T" | "t"| "u" | "V" | "Wb" | "W" | "''" 
NON_PRE_METRIC: "AU" | "Cel" | "deg" | "d" | "h" | "min" | "'" 
CONVENTIONAL: "%" | "a_g" | "a_j" | "a_t" | "Ao" | "atm" | "att" | "a" | "bar" | "Bd" | "Bi" | "bit_s" | "bit" | "By" | "b" | "cal_IT" | "cal_m" | "cal_th" | "cal" | "Ci" | "circ" | "dyn" | "eq" | "erg" | "g%" | "Gal" | "Gb" | "gf" | "gon" | "G" | "Ky" | "Lmb" |  "mho" | "mo_g" | "mo_j" | "mo_s" | "mo" | "Mx" | "Oe" | "osm" | "pc" | "ph" | "P" | "RAD" | "REM" | "R" | "sb" | "sph" | "St" | "st" | "tex" | "U" | "wk"
CONVENTIONAL_BRACKETS: "[acr_br]" | "[acr_us]" | "[Amb'a'1'U]" | "[anti'Xa'U]" | "[APL'U]" | "[arb'U]" | "[AU]" | "[BAU]" | "[bbl_us]" | "[bdsk'U]" | "[beth'U]" | "[bf_i]" | "[Btu_39]" | "[Btu_59]" | "[Btu_60]" | "[Btu_IT]" | "[Btu_m]" | "[Btu_th]" | "[Btu]" | "[bu_br]" | "[bu_us]" | "[c]" | "[Cal]" | "[car_Au]" | "[car_m]" | "[CCID_50]" | "[cft_i]" | "[CFU]" | "[ch_br]" | "[ch_us]" | "[Ch]" | "[cicero]" | "[cin_i]" | "[cml_i]" | "[cr_i]" | "[crd_us]" | "[cup_m]" | "[cup_us]" | "[cyd_i]" | "[D'ag'U]" | "[degF]" | "[degR]" | "[degRe]" | "[den]" | "[didot]" | "[diop]" | "[dpt_us]" | "[dqt_us]" | "[dr_ap]" | "[dr_av]" | "[drp]" | "[dye'U]" | "[e]" | "[EID_50]" | "[ELU]" | "[eps_0]" | "[EU]" | "[fdr_br]" | "[fdr_us]" | "[FEU]" | "[FFU]" | "[foz_br]" | "[foz_m]" | "[foz_us]" | "[ft_br]" | "[ft_i]" | "[ft_us]" | "[fth_br]" | "[fth_i]" | "[fth_us]" | "[fur_us]" | "[G]" | "[g]" | "[gal_br]" | "[gal_us]" | "[gal_wi]" | "[gil_br]" | "[gil_us]" | "[GPL'U]" | "[gr]" | "[h]" | "[hd_i]" | "[hnsf'U]" | "[hp_C]" | "[hp_M]" | "[hp_Q]" | "[hp_X]" | "[hp'_C]" | "[hp'_M]" | "[hp'_Q]" | "[hp'_X]" | "[HP]" | "[HPF]" | "[in_br]" | "[in_i'H2O]" | "[in_i'Hg]" | "[in_i]" | "[in_us]" | "[IR]" | "[IU]" | "[iU]" | "[k]" | "[ka'U]" | "[kn_br]" | "[kn_i]" | "[knk'U]" | "[kp_C]" | "[kp_M]" | "[kp_Q]" | "[kp_X]" | "[lb_ap]" | "[lb_av]" | "[lb_tr]" | "[lbf_av]" | "[lcwt_av]" | "[Lf]" | "[ligne]" | "[lk_br]" | "[lk_us]" | "[lne]" | "[LPF]" | "[lton_av]" | "[ly]" | "[m_e]" | "[m_p]" |  "[mclg'U]" | "[mesh_i]" | "[MET]" | "[mi_br]" | "[mi_i]" | "[mi_us]" | "[mil_i]" | "[mil_us]" | "[min_br]" | "[min_us]" | "[MPL'U]" | "[mu_0]" | "[nmi_br]" | "[nmi_i]" | "[oz_ap]" | "[oz_av]" | "[oz_m]" | "[oz_tr]" | "[p'diop]" | "[pc_br]" | "[pca_pr]" | "[pca]" | "[PFU]" | "[pH]" | "[pi]" | "[pied]" | "[pk_br]" | "[pk_us]" | "[pnt_pr]" | "[pnt]" | "[PNU]" | "[pouce]" | "[ppb]" | "[ppm]" | "[ppth]" | "[pptr]" | "[PRU]" | "[psi]" | "[pt_br]" | "[pt_us]" | "[pwt_tr]" | "[qt_br]" | "[qt_us]" | "[rch_us]" | "[rd_br]" | "[rd_us]" | "[rlk_us]" | "[S]" | "[sc_ap]" | "[sct]" | "[scwt_av]" | "[sft_i]" | "[sin_i]" | "[smgy'U]" | "[smi_us]" | "[smoot]" | "[srd_us]" | "[ston_av]" | "[stone_av]" | "[syd_i]" | "[tb'U]" | "[tbs_m]" | "[tbs_us]" | "[TCID_50]" | "[todd'U]" | "[tsp_m]" | "[tsp_us]" | "[twp]" | "[USP'U]" | "[wood'U]" | "[yd_br]" | "[yd_i]" | "[yd_us]"
CONVENTIONAL_MIXED_BRACKETS: "%[slope]" | "B[10.nV]" | "B[kW]" | "B[mV]" | "B[SPL]" | "B[uV]" | "B[V]" | "B[W]" | "cal_[15]" | "cal_[20]" | "m[H2O]" | "m[Hg]" 
EXCEPTION: "dar"
%ignore " "           // Disregard spaces in text
''')
# Note the rules need to be in order if we have  "m" | "mol" then mol won't be found
# removed conventional UCUM codes:  "10*" | "10^" | "[m/s2/Hz^(1/2)]" #TODO as as grammar

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
        if "exponent" in result and original[0] == '/':
            exponent = int('-' + str(result['exponent']))
        elif "exponent" in result:
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
    try:
        code = result['prefix'] + unit
        result.update({code_str: code})
    except:
        print(f"No SI code for '{result}'")


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
def gen_label_parts(result, SI_unit_label_dict, prefix_dict, exponents_dict, label_lan):
    """
    Create labels from units and prefixes
    TODO add special case for unit = are to print hectare instead of hectoare etc
    Have a temporary workaround for hectare and decare but open question if are should
    be crossable with all prefixes see https://github.com/kaiiam/UO_revamp/issues/6
    """

    unit = get_value(result['unit'], SI_unit_label_dict)

    if get_value(result['prefix'], prefix_dict) is not None:
        prefix = get_value(result['prefix'], prefix_dict)
    else:
        prefix = ''

    if unit == 'are':
        prefix = get_value(result['prefix'], prefix_dict)
        if prefix == None:
            prefix = ''
        if prefix == 'hecto':
            prefix = 'hect'
        if prefix == 'deca':
            prefix = 'dec'

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
def retrieve_exponent(in_arg, exponents_en_dict):
    power = str(in_arg['exponent'])
    power = power.replace('-', '')
    power = get_value(power, exponents_en_dict)
    return power


# --------------------------------------------------
def canonical_en_definition_helper(units_list, unit_label_en_dict, exponents_en_dict, prefix_numbers_dict):
    return_lst = []
    for u in units_list:
        unit = get_value(u['unit'], unit_label_en_dict)
        power = retrieve_exponent(u, exponents_en_dict)
        if get_value(key=u['prefix'], dict=prefix_numbers_dict) is not None:
            prefix_num = get_value(key=u['prefix'], dict=prefix_numbers_dict)
            prefix_val = f'10{prefix_num}'
        else:
            prefix_val = '1'
        if power is None:
            return_lst.append(f'{prefix_val} {unit}')
        else:
            return_lst.append(f'{prefix_val} {power} {unit}')
    return return_lst


# --------------------------------------------------
def canonical_en_definition(numerator_list, denominator_list, unit_def_dict, prefix_numbers_dict, ucum_unit_label_en_dict, exponents_en_dict, label_lan):
    definition = None
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
                si_label = get_value(key=n['unit'], dict=ucum_unit_label_en_dict)
                prefix_num = get_value(key=n['prefix'], dict=prefix_numbers_dict)
                definition = f'A unit which is equal to 10{prefix_num} {si_label}.'
    # Case 2 no denominators
    elif not denominator_list:
        return_lst = canonical_en_definition_helper(units_list=numerator_list, unit_label_en_dict=ucum_unit_label_en_dict,
                                                    exponents_en_dict=exponents_en_dict,
                                                    prefix_numbers_dict=prefix_numbers_dict)
        def_start = 'A unit which is equal to '
        definition_mid = ' by '.join(return_lst)
        definition = def_start + definition_mid + '.'
    # Case 3 no numerators
    elif not numerator_list:
        return_lst = canonical_en_definition_helper(units_list=denominator_list, unit_label_en_dict=ucum_unit_label_en_dict,
                                                    exponents_en_dict=exponents_en_dict,
                                                    prefix_numbers_dict=prefix_numbers_dict)
        def_start = 'A unit which is equal to the reciprocal of '
        definition_mid = ' by '.join(return_lst)
        definition = def_start + definition_mid + '.'
    # Case 4 mix of numerators and denominators
    else:
        num_list = canonical_en_definition_helper(units_list=numerator_list, unit_label_en_dict=ucum_unit_label_en_dict,
                                                    exponents_en_dict=exponents_en_dict,
                                                    prefix_numbers_dict=prefix_numbers_dict)

        denom_list = canonical_en_definition_helper(units_list=denominator_list,
                                                    unit_label_en_dict=ucum_unit_label_en_dict,
                                                    exponents_en_dict=exponents_en_dict,
                                                    prefix_numbers_dict=prefix_numbers_dict)
        def_start = 'A unit which is equal to '
        def_num = ' by '.join(num_list)
        def_denom = ' by '.join(denom_list)
        definition = def_start + def_num + ' per ' + def_denom + '.'

    return definition


# --------------------------------------------------
def canonical_si_code(numerator_list, denominator_list):
    # TODO use a dict of exponents mapping to f string superscript numbers to write out exponents as superscript
    # OR use the prefix_numbers_dict
    # str = 'cm'
    # print(f'{str}\N{SUPERSCRIPT MINUS}\N{SUPERSCRIPT SEVEN}')
    return_lst = []
    for n in numerator_list:
        if 'si_code' in n:
            if str(n['exponent']) == '1':
                return_lst.append(n['si_code'])
            else:
                return_lst.append(n['si_code'] + str(n['exponent']))
        else:
            return None
    for n in denominator_list:
        if 'si_code' in n:
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
    nerc_regex = r"(http://vocab.nerc.ac.uk/collection/P06/current/)(.*)(/)"

    qudt_list = []
    om_list = []
    uo_list = []
    oboe_list = []
    nerc_list = []

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
        if re.search(nerc_regex, m):
            match = re.search(nerc_regex, m)
            nerc_id = match.group(2)
            nerc_id = 'NERC_P06:' + nerc_id
            nerc_list.append(nerc_id)

    iri = '{}{}\n'.format('unit:', parse.quote(iri))
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

    [return_list.append('  {}exactMatch {}'.format('skos:', x)) for x in nerc_list if nerc_list]

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
    nerc_ucum = args.ucum5

    # Read in SI units
    SI_list = []
    # open and save input file as list of dictionaries
    with open(SI_file, mode='r', encoding='utf-8-sig') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            SI_list.append(row)

    ucum_si_units_dict = {}
    for i in SI_list:
        ucum_si_units_dict[i['UCUM_symbol']] = i['SI_symbol']

    ucum_unit_label_en_dict = {}
    for i in SI_list:
        ucum_unit_label_en_dict[i['UCUM_symbol']] = i['label_en']

    ucum_unit_def_en_dict = {}
    for i in SI_list:
        ucum_unit_def_en_dict[i['UCUM_symbol']] = i['definition_en']

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

    nerc_ucum_list = []
    # open and save input file as list of dictionaries
    with open(nerc_ucum, mode='r', encoding='utf-8-sig') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            nerc_ucum_list.append(row)

    # Join all the input ontology to UCUM mappings into single list of dict
    ontology_mapping_list = om_ucum_list + qudt_ucum_list + uo_ucum_list + oboe_ucum_list + nerc_ucum_list

    valid_SI_input_list = []

    # # breakup input list one term at a time
    for u in input_list:
        try:
            tree = si_grammar.parse(u)
            #result = transformer().transform(tree)
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
        try:
            res_flat = flatten(result)
        except:
            print(f"Ran into error with flatten when processing '{u}'")
        # print(u, res_flat)

        new_dict_list = []
        # Convert the inputs into a preprocessed list of dict
        for r in res_flat:
            pre_process_unit_list(r, u, new_dict_list)

        # Determine type SI vs conventional
        # to optionally Add SI codes in next step
        # TODO could probably do this better
        type_list = []
        for r in new_dict_list:
            type_list.append(r['type'])

        # Add codes to dict:
        for r in new_dict_list:
            # Optionally Add SI codes
            if 'conventional' not in type_list:
                # create the SI code from prefix and unit
                gen_symbol_code(result=r, mapping_dict=ucum_si_units_dict, code_str='si_code')

            # create the UCUM codes from prefix and unit
            code = r['prefix'] + r['unit']
            r.update({'ucum_code': code})
        # print(u, new_dict_list)

        # Function to generate list of UCUM codes from results dict list
        # Permute Possible UCUM strings
        UCUM_SI_list = gen_si_ucum_list(dict_list=new_dict_list)
        # print(UCUM_SI_list)

        # Function to create labels from units and prefixes
        # pass in desired language SI unit, prefix and exponents dicts + label_lan
        for r in new_dict_list:
            gen_label_parts(result=r, SI_unit_label_dict=ucum_unit_label_en_dict, prefix_dict=prefix_en_dict, exponents_dict=exponents_en_dict, label_lan='label_en')
        # print(u, new_dict_list)

        # Function to split numerator and denominator into two lists
        numerator_list = []
        denominator_list = []
        for r in new_dict_list:
            split_num_denom(result=r, numerator_list=numerator_list, denominator_list=denominator_list)
        # print(u, 'num:', numerator_list, 'denom:', denominator_list)

        # # Sort in canonical alphabetical order
        try:
            numerator_list = sorted(numerator_list, key=lambda k: (k['ucum_code'].casefold(), k))
            denominator_list = sorted(denominator_list, key=lambda k: (k['ucum_code'].casefold(), k))
            # print(u, numerator_list, denominator_list)
        except:
            print(f"Could not process '{u}' at sorting step")

        # # Generate canonical term label
        label = canonical_nc_label(numerator_list=numerator_list, denominator_list=denominator_list, label_lan='label_en')

        # Generate canonical english definition
        definition_en = canonical_en_definition(numerator_list=numerator_list, denominator_list=denominator_list,
                                                unit_def_dict=ucum_unit_def_en_dict, prefix_numbers_dict=prefix_numbers_dict, ucum_unit_label_en_dict=ucum_unit_label_en_dict, exponents_en_dict=exponents_en_dict, label_lan='label_en')

        # Generate canonical SI code e.g. `Pa s`
        # First pass complete, Later can fix superscript issue with fstrings TODO
        # print(u, '->', canonical_si_code(numerator_list=numerator_list,denominator_list=denominator_list))
        si_code = canonical_si_code(numerator_list=numerator_list, denominator_list=denominator_list)

        # Generate canonical UCUM code
        ucum_code = canonical_ucum_code(numerator_list=numerator_list, denominator_list=denominator_list)
        #print(ucum_code)

        # Map UCUM codes to external Ontologies
        # LATER TODO change this to use the mappings of canonical UCUM strings by calling phase 2 on Simon’s mappings
        mapping_list = temp_ucum_map(ucum_list=UCUM_SI_list, ontology_mapping_list=ontology_mapping_list)
        #print(mapping_list)

        # Format ttl for SI parser results
        # We can alternatively pass ucum_code instead of si_nc_name_iri
        # as iri to circumvent NC name mapping
        print(format_si_ttl(iri=ucum_code, label=label, si_code=si_code, ucum_code=ucum_code, definition_en=definition_en, mapping_list=mapping_list), file=f)


        # --------------------------------------------------
if __name__ == '__main__':
    main()