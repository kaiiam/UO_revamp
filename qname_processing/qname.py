#!/usr/bin/env python3
"""
Author : Kai
Date   : 2021-03-01
Purpose: script to take a QNames string and return a Turtle file with annotations
and links to UO, OM, QUDT, UCUM

e.g.: given `m.s-2` or `m/s2` return the following:

unit:m.s-2
  rdfs:label "metre per square second"@en ;
  skos:exactMatch QUDT:M-PER-SEC2 ;
  skos:exactMatch OM:metrePerSecond-TimeSquared ;
  skos:exactMatch UO:0000077 ;
  unit:ucum_code "m.s-2" ;
  unit:ucum_code "m/s2" .

test run:

./qname.py -i input/test6.csv -u1 input_mappings/UCUM/om_ucum_mapping.csv -u2 input_mappings/UCUM/qudt_ucum_mapping.csv -u3 input_mappings/UCUM/uo_ucum_mapping.csv -u4 input_mappings/UCUM/oboe_ucum_mapping.csv -o out.ttl -q input_mappings/QName/qname_labels.csv

Run with full set from all ontologies:
./qname.py -i input/from_existing_ontologies.csv -u1 input_mappings/UCUM/om_ucum_mapping.csv -u2 input_mappings/UCUM/qudt_ucum_mapping.csv -u3 input_mappings/UCUM/uo_ucum_mapping.csv -u4 input_mappings/UCUM/oboe_ucum_mapping.csv -o out_full.ttl -q input_mappings/QName/qname_labels.csv

"""

import argparse
import sys
import csv
import re

# Global Variables

prefix_dict_list = [
    {'prefix': 'rdf:', 'namespace': 'http://www.w3.org/1999/02/22-rdf-syntax-ns#'},
    {'prefix': 'rdfs:', 'namespace': 'http://www.w3.org/2000/01/rdf-schema#'},
    {'prefix': 'xsd:', 'namespace': 'http://www.w3.org/2001/XMLSchema#'},
    {'prefix': 'owl:', 'namespace': 'http://www.w3.org/2002/07/owl#'},
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
        '-o',
        '--output',
        help='outfile',
        metavar='str',
        type=str,
        default='')

    parser.add_argument(
        '-q',
        '--qname',
        help='Input qname string to labels mapping',
        metavar='str',
        type=str,
        default='')

    return parser.parse_args()


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
def ham_dist(s1, s2):
    """Haming distance calculation function MAY NOT NEED THIS"""

    dist = abs(len(s1) - len(s2))
    for c1, c2 in zip(s1, s2):
        if c1 != c2:
            dist += 1
    return dist


# --------------------------------------------------
def reverse(text):
    """https://stackoverflow.com/questions/7961499/best-way-to-loop-over-a-python-string-backwards"""
    rev = ''
    for i in range(len(text), 0, -1):
        rev += text[i - 1]
    return rev


# --------------------------------------------------
def extract_qname_symbol(in_str, unit_keys):
    """Given an input string extract and return any existing unit_key
    else return None
    """
    val = ''
    key = ''
    for x in reverse(in_str):
        val += x
        rev_val = reverse(val)
        if rev_val in unit_keys:
            key = rev_val

    if key is not '':
        return key
    else:
        return None


# --------------------------------------------------
def extract_label(in_str, unit_keys, prefix_dict, units_dict):
    """given qsymbol string will return its label
     e.g. given mmol will return millimole
     """
    # Call function to extract base symbol
    unit_symbol = extract_qname_symbol(in_str, unit_keys)

    if unit_symbol is not None:
        match = re.search("(.*)({})".format(unit_symbol), in_str)
        unit = get_value(key=match.group(2), dict=units_dict)
        if match.group(1) is '':
            return '{}'.format(unit)
        else:
            prefix = get_value(key=match.group(1), dict=prefix_dict)
        if prefix is None:
            pass
        else:
            return '{}{}'.format(prefix, unit)
    else:
        return None


# --------------------------------------------------
def extract_label_with_symbol(in_str, unit_keys, prefix_dict, units_dict, powers_dict):
    """Given strings like ng1 or L3 return nanogram or cubic litre"""
    match = re.search("(.*)(\d)", in_str)
    symbols = match.group(1)
    power = match.group(2)
    symb_label = extract_label(symbols, unit_keys, prefix_dict, units_dict)
    power_label = get_value(key=power, dict=powers_dict)
    if power_label is None:
        return '{}'.format(symb_label)
    else:
        return '{} {}'.format(power_label, symb_label)


# --------------------------------------------------
def gen_qname_label(qname_str, qname_mapping_list):
    """
    Perhaps here we can call a function that assembles the label based on the qname_str
    # To do this I'll need to load in files with mappings between base terms labels and qname strings
    # will need to pass above mapping file(s) to qname as additional arg(s)
    """
    # Use one dict with unit qname symbols as keys and english labels as values
    # and a second dict with prefix qname symbols as keys and english labels as values
    # https://www.guru99.com/python-dictionary-append.html
    units_dict = {}
    for i in qname_mapping_list:
        if i['prefix'] == 'FALSE':
            units_dict[i['qname']] = i['label_en']
    prefix_dict = {}
    for i in qname_mapping_list:
        if i['prefix'] == 'TRUE':
            prefix_dict[i['qname']] = i['label_en']
    unit_keys = list(units_dict.keys())
    powers_dict = {'1': None, '2': 'square', '3': 'cubic', '4': 'quartic', '5': 'quintic', '6': 'sextic', '7': 'septic',
                   '8': 'octic', '9': 'nonic', '10': 'decic'}

    # QName string has no "." separators
    if '.' not in qname_str:
        # Case with denominators and digits
        if '-' in qname_str:
            dash_free_qname = qname_str.replace('-', '', 1)
            lab = extract_label_with_symbol(in_str=dash_free_qname, unit_keys=unit_keys, prefix_dict=prefix_dict,
                                            units_dict=units_dict, powers_dict=powers_dict)
            return 'reciprocal {}'.format(lab)
        # Case with digits
        elif any(c.isdigit() for c in qname_str):
            return extract_label_with_symbol(in_str=qname_str, unit_keys=unit_keys, prefix_dict=prefix_dict,
                                             units_dict=units_dict, powers_dict=powers_dict)
        # Case without denominators or digits
        else:
            return extract_label(qname_str, unit_keys, prefix_dict, units_dict)
    else:
        unit_parts_list = qname_str.split('.')
        # Case 1 all numerators
        if '-' not in qname_str:
            names_list = []
            for x in unit_parts_list:
                if any(c.isdigit() for c in x):
                    label = extract_label_with_symbol(in_str=x, unit_keys=unit_keys, prefix_dict=prefix_dict,
                                                      units_dict=units_dict, powers_dict=powers_dict)
                else:
                    label = extract_label(x, unit_keys, prefix_dict, units_dict)
                names_list.append(label)
            return ' '.join(names_list)
        # Case 2 if all denominators
        elif len(unit_parts_list) == qname_str.count('-'):
            names_list = []
            for x in unit_parts_list:
                dash_free_qname = x.replace('-', '', 1)
                label = extract_label_with_symbol(in_str=dash_free_qname, unit_keys=unit_keys, prefix_dict=prefix_dict,
                                                  units_dict=units_dict, powers_dict=powers_dict)
                names_list.append(label)
            return 'reciprocal ' + ' '.join(names_list)
        # Case 3 Mix Numerators and denominators
        else:
            num_list = []
            denom_list = []
            for x in unit_parts_list:
                if '-' in x:
                    denom_list.append(x)
                else:
                    num_list.append(x)

            num_names_list = []
            for x in num_list:
                if any(c.isdigit() for c in x):
                    label = extract_label_with_symbol(in_str=x, unit_keys=unit_keys, prefix_dict=prefix_dict,
                                                      units_dict=units_dict, powers_dict=powers_dict)
                else:
                    label = extract_label(x, unit_keys, prefix_dict, units_dict)
                num_names_list.append(label)

            denom_names_list = []
            for x in denom_list:
                dash_free_qname = x.replace('-', '', 1)
                label = extract_label_with_symbol(in_str=dash_free_qname, unit_keys=unit_keys, prefix_dict=prefix_dict,
                                                  units_dict=units_dict, powers_dict=powers_dict)
                denom_names_list.append(label)
            return ' '.join(num_names_list) + ' per ' + ' '.join(denom_names_list)


# --------------------------------------------------
def ucum_str_to_qname_str(in_str, unit_keys, qname_ucum_map_dict):
    """
    convert just % to PCT
    Might need to update the regex string as new qname/UCUM mappings are made
    """
    match = re.search(r"^([a-zA-Z%#_']+)([-]?[0-9]{0,2})$", in_str)
    code = match.group(1)
    ucum_code_symbol = extract_qname_symbol(code, unit_keys)
    qname_code = get_value(ucum_code_symbol,qname_ucum_map_dict)
    qstr_out = in_str.replace(ucum_code_symbol, qname_code)
    return qstr_out


# --------------------------------------------------
def ucum_to_qname(in_str, qname_mapping_list):
    """
    Function to convert UCUM strings to Qname string
    e.g. `%` to `PCT`
    """
    qname_ucum_map_dict = {}
    for i in qname_mapping_list:
        if i['prefix'] == 'FALSE':
            qname_ucum_map_dict[i['ucum']] = i['qname']
    unit_keys = list(qname_ucum_map_dict.keys())

    if '.' not in in_str:
        return ucum_str_to_qname_str(in_str, unit_keys, qname_ucum_map_dict)
    else:
        unit_parts_list = in_str.split('.')
        new_list = []
        for x in unit_parts_list:
            new_list.append(ucum_str_to_qname_str(x, unit_keys, qname_ucum_map_dict))
        return '.'.join(new_list)


# --------------------------------------------------
def qname_to_ucum(in_str, qname_mapping_list):
    """
    Function to convert Qname strings to UCUM string
    e.g.`PCT` to `%`
    """
    qname_ucum_map_dict = {}
    for i in qname_mapping_list:
        if i['prefix'] == 'FALSE':
            qname_ucum_map_dict[i['qname']] = i['ucum']
    unit_keys = list(qname_ucum_map_dict.keys())

    if '.' not in in_str:
        return ucum_str_to_qname_str(in_str, unit_keys, qname_ucum_map_dict)
    else:
        unit_parts_list = in_str.split('.')
        new_list = []
        for x in unit_parts_list:
            new_list.append(ucum_str_to_qname_str(x, unit_keys, qname_ucum_map_dict))
        return '.'.join(new_list)


# --------------------------------------------------
def get_ucum_dash_str(in_str):
    """
    # Converts from the instr with . to the form with /s
    # for example m/s/d to m.s-1.d-1
    kindof like the opposite of backslash_case() and reformat_backslash()
    """
    if re.search('/', in_str):
        # print(in_str, 'case with /')
        return in_str

    if re.search('.', in_str):
        #print(in_str, 'case with .')

        if not re.search('-', in_str):
            #print(in_str, 'case with . and no -')
            return in_str.replace('.', '/')

        if in_str.count('-') == in_str.count('.'):
            #print(in_str, 'case with . and - are equal')
            if in_str.count('-') == 1:
                # print(in_str, 'case with . and - are equal one of them')
                match = re.search(r"^([a-zA-Z%#_']+[0-9]{0,2})[.]([a-zA-Z%#_']+)[-]?([0-9]{0,2})", in_str)
                #three = match.group(3)
                if match.group(3) == '1':
                    three = ''
                else:
                    three = match.group(3)
                return_str = match.group(1) + '/' + match.group(2) + three
                return return_str
            # case with two - and .
            if in_str.count('-') == 2:
                # TODO fix this regex for the two . case e.g. J.mm-2.d-1 or m.s-1.d-1
                match = re.search(r"^([a-zA-Z%#_']+[0-9]{0,2})[.]?([a-zA-Z%#_']+)[-]?([0-9]{0,2})[.]?([a-zA-Z%#_']+)[-]?([0-9]{0,2})", in_str)
                if match.group(3) == '1':
                    three = ''
                else:
                    three = match.group(3)
                if match.group(5) == '1':
                    five = ''
                else:
                    five = match.group(3)
                return_str = match.group(1) + '/' + match.group(2) + three + '/' + match.group(4) + five
                return return_str

        if in_str.count('-') > in_str.count('.'):
            if in_str.count('-') == 1:
                # x-n case e.g. mT-1
                match = re.search(r"^([a-zA-Z%#_']+)[-]([0-9]{0,2})$", in_str)

                if match.group(2) == '1':
                    two = ''
                else:
                    two = match.group(2)
                return_str = '/' + match.group(1) + two
                return return_str
        ## TODO add case like `/nN/E`



# --------------------------------------------------
def qname(in_str, ontology_mapping_list, om_ucum_list, qudt_ucum_list, uo_ucum_list, oboe_ucum_list, qname_mapping_list):
    """Parse input mappings to find UCUM, QUDT, OM, UO IDs/strings.
    For now we're assuming that the in_str has been checked to be a correct "UCUM" style string
    Will need to add such a check prior to passing in_str into this qname function.
    """
    # List of UCUM strings
    ucum_id_list = []
    qudt_iri = ''
    om_iri = ''
    uo_iri = ''
    oboe_iri = ''

    # Convert UCUM style in_str to a proper QName str
    qname_str = ucum_to_qname(in_str, qname_mapping_list)
    # Generate label from qname str
    qname_label = gen_qname_label(qname_str, qname_mapping_list)
    # Map ucum string to QName
    ucum_from_qname = qname_to_ucum(qname_str, qname_mapping_list)

    # This works but it's a bit big
    for x in ontology_mapping_list:
        if 'qudt' in x['IRI']:
            if in_str == x['UCUM1'] or in_str == x['UCUM2'] or in_str == x['UCUM3'] or in_str == x['UCUM4']:
                ucum_id_list.append(x['UCUM1'])
                ucum_id_list.append(x['UCUM2'])
                qudt_iri = x['IRI']
            if ucum_from_qname == x['UCUM1'] or ucum_from_qname == x['UCUM2'] or ucum_from_qname == x['UCUM3'] or ucum_from_qname == x['UCUM4']:
                ucum_id_list.append(x['UCUM1'])
                ucum_id_list.append(x['UCUM2'])
                qudt_iri = x['IRI']
        if 'ontology-of-units-of-measure.org' in x['IRI']:
            if in_str == x['UCUM1'] or in_str == x['UCUM2']:
                ucum_id_list.append(x['UCUM1'])
                ucum_id_list.append(x['UCUM2'])
                om_iri = x['IRI']
            if ucum_from_qname == x['UCUM1'] or ucum_from_qname == x['UCUM2']:
                ucum_id_list.append(x['UCUM1'])
                ucum_id_list.append(x['UCUM2'])
                om_iri = x['IRI']
        if 'obolibrary.org/obo/UO_' in x['IRI']:
            if in_str == x['UCUM1'] or in_str == x['UCUM2']:
                ucum_id_list.append(x['UCUM1'])
                ucum_id_list.append(x['UCUM2'])
                uo_iri = x['IRI']
            if ucum_from_qname == x['UCUM1'] or ucum_from_qname == x['UCUM2']:
                ucum_id_list.append(x['UCUM1'])
                ucum_id_list.append(x['UCUM2'])
                uo_iri = x['IRI']
        if '/oboe/oboe.' in x['IRI']:
            if in_str == x['UCUM1'] or in_str == x['UCUM2']:
                ucum_id_list.append(x['UCUM1'])
                ucum_id_list.append(x['UCUM2'])
                oboe_iri = x['IRI']
            if ucum_from_qname == x['UCUM1'] or ucum_from_qname == x['UCUM2']:
                ucum_id_list.append(x['UCUM1'])
                ucum_id_list.append(x['UCUM2'])
                oboe_iri = x['IRI']

    # Maybe we can also call a fn that:
    # Converts from the instr with . to the form with /s
    # for example m/s/d to m.s-1.d-1
    ucum_id_list.append(ucum_from_qname)
    for x in ucum_id_list:
        get_ucum_dash_str(x)

    # Clean up parsed info:
    ucum_id_list = list(set([i for i in ucum_id_list if i]))

    return (format_ttl(qname_str=qname_str, ucum_id_list=ucum_id_list, qudt_iri=qudt_iri, om_iri=om_iri,
                       uo_iri=uo_iri, oboe_iri=oboe_iri, qname_label=qname_label))


# --------------------------------------------------
def backslash_case(in_str):
    """Convert the s2 from `m/s2` to s-2 from `m.s-2`"""
    match = re.search(r"(\D*)(\d)*", in_str)
    if match.group(2) is None:
        return '{}-1'.format(match.group(1))
    else:
        return '{}-{}'.format(match.group(1), match.group(2))


# --------------------------------------------------
def reformat_backslash(in_str):
    """Verify if input is a valid QName string. If not convert it to one.
    Input should be a UCUM or QName string
    Outputs a QName string

    Maybe rename this along the lines of converting UCUM to QName?
    TODO add more checks to validate input
    """
    # Input contains "/"
    if re.search('/', in_str):
        if in_str.count("/") == 3:
            match = re.search(r"(.*)/(.*)/(.*)/(.*)", in_str)
            return ('{}.{}.{}.{}'.format(match.group(1), backslash_case(match.group(2)), backslash_case(match.group(3)),
                                         backslash_case(match.group(4))))
        if in_str.count("/") == 2:
            match = re.search(r"(.*)/(.*)/(.*)", in_str)
            return '{}.{}.{}'.format(match.group(1), backslash_case(match.group(2)), backslash_case(match.group(3)))
        if in_str.count("/") == 1:
            match = re.search(r"(.*)/(.*)", in_str)
            if match.group(1) is '':
                return '{}'.format(backslash_case(match.group(2)))
            else:
                return '{}.{}'.format(match.group(1), backslash_case(match.group(2)))

    # Input contains a "."
    # Will need to flush this out to include all checks for QName conventions
    if re.search('.', in_str):
        return in_str


# --------------------------------------------------
def format_ttl(qname_str, ucum_id_list, qudt_iri, om_iri, uo_iri, oboe_iri, qname_label):
    """Format parsed IDs and UCUM codes into ttl"""
    qudt_id = ''
    om_id = ''
    uo_id = ''
    oboe_id = ''
    qudt_regex = r"(http://qudt.org/vocab/unit/)(.*)"
    om_regex = r"(http://www.ontology-of-units-of-measure.org/resource/om-2/)(.*)"
    uo_regex = r"(http://purl.obolibrary.org/obo/UO_)(.*)"
    oboe_regex = r"(http://ecoinformatics.org/oboe/oboe.1.2/oboe-standards.owl#)(.*)"

    if re.search(qudt_regex, qudt_iri):
        match = re.search(qudt_regex, qudt_iri)
        qudt_id = match.group(2)
        qudt_id = 'QUDT:' + qudt_id
    if re.search(om_regex, om_iri):
        match = re.search(om_regex, om_iri)
        om_id = match.group(2)
        om_id = 'OM:' + om_id
    if re.search(uo_regex, uo_iri):
        match = re.search(uo_regex, uo_iri)
        uo_id = match.group(2)
        uo_id = 'UO:' + uo_id
    if re.search(oboe_regex, oboe_iri):
        match = re.search(oboe_regex, oboe_iri)
        oboe_id = match.group(2)
        oboe_id = 'OBOE:' + oboe_id

    # TODO could maybe add some more checks to ensure we only get correctly formatted QName strings
    prefixed_qname = '{}{}\n'.format('unit:', qname_str)
    return_str = ''
    return_str += prefixed_qname
    return_list = []

    if qname_label:
        return_list.append('  {}label "{}"@en'.format('rdfs:', qname_label))
    if qudt_id:
        return_list.append('  {}exactMatch {}'.format('skos:', qudt_id))
    if om_id:
        return_list.append('  {}exactMatch {}'.format('skos:', om_id))
    if uo_id:
        return_list.append('  {}exactMatch {}'.format('skos:', uo_id))
    if oboe_id:
        return_list.append('  {}exactMatch {}'.format('skos:', oboe_id))

    [return_list.append('  {}ucum_code "{}"'.format('unit:', u)) for u in ucum_id_list]

    if not return_list:
        print('Warning: "{}" was not added'.format(qname_str))
        return None

    # Add ; and . for ttl formatting
    for i, has_more in lookahead(return_list):
        if has_more:
            return_str += (i + ' ;\n')
        else:
            return_str += (i + ' .\n')
    return return_str


# --------------------------------------------------
def main():
    """Make a jazz noise here"""
    args = get_args()
    input_file = args.input
    om_ucum = args.ucum1
    qudt_ucum = args.ucum2
    uo_ucum = args.ucum3
    oboe_ucum = args.ucum4
    out_file = args.output
    qname_mapping = args.qname

    # Read in argument input files
    input_list = []
    # open and save input data file as list of strings
    with open(input_file, mode='r', encoding='utf-8-sig') as input:
        csv_reader = csv.reader(input, delimiter=',')
        for row in csv_reader:
            input_list.append(row[0])

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
    # print(ontology_mapping_list)





    qname_mapping_list = []
    # open and save input file as list of dictionaries
    with open(qname_mapping, mode='r', encoding='utf-8-sig') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            qname_mapping_list.append(row)

    # Open outfile
    f = open(out_file, mode='w', encoding='utf-8-sig')

    # write out prefixes followed by linebreak
    for p in prefix_dict_list:
        print('@prefix {} <{}> .'.format(p['prefix'], p['namespace']), file=f)
    print('', file=f)

    # Convert from / formats to . formats
    input_list = [reformat_backslash(i) for i in input_list]
    # Remove duplicates
    input_list = list(set(input_list))
    # Sort alphabetically
    input_list.sort()

    for i in input_list:
        # get qname string label
        # TODO write a function similar to modify gen_qname_label()
        # to make input strings unique by alphabetizing "." separated terms
        # In order to get to unique qnames e.g. `Cel-1.d-1` == `d-1.Cel-1`
        # Can maybe call this function on all of input_list prior to sorting/removing duplicates and
        # Calling qname on the whole list as to make sure we have a list of unique qnames prior to printing a new one

        # Perhaps not the best way to handle the None values returned from the previous functions
        call = qname(in_str=i, ontology_mapping_list=ontology_mapping_list, om_ucum_list=om_ucum_list, qudt_ucum_list=qudt_ucum_list,
                     uo_ucum_list=uo_ucum_list, oboe_ucum_list=oboe_ucum_list,
                     qname_mapping_list=qname_mapping_list)
        if call is not None:
            print(call, file=f)


# --------------------------------------------------
if __name__ == '__main__':
    main()
