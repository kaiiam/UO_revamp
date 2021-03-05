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

RUN:

./qname.py -i input/test1.csv -u1 input_mappings/UCUM/om_ucum_mapping.csv -u2 input_mappings/UCUM/qudt_ucum_mapping.csv -u3 input_mappings/UCUM/uo_ucum_mapping.csv -o out.ttl -q input_mappings/QName/qname_labels.csv

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
        help='UCUM keys',
        metavar='str',
        type=str,
        default='')

    parser.add_argument(
        '-u2',
        '--ucum2',
        help='UCUM keys',
        metavar='str',
        type=str,
        default='')

    parser.add_argument(
        '-u3',
        '--ucum3',
        help='UCUM keys',
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
def qname(in_str, qname_label, om_ucum_list, qudt_ucum_list, uo_ucum_list, qname_mapping_list):
    """Parse input mappings to find UCUM, QUDT, OM, UO IDs/strings.
    For now we're assuming that the in_str has been checked to be a correct "UCUM" style string
    Will need to add such a check prior to passing in_str into this qname function.
    """
    ucum_id_list = []
    qudt_iri = ''
    om_iri = ''
    uo_iri = ''

    for q in qudt_ucum_list:
        if in_str == q['UCUM1'] or in_str == q['UCUM2']:
            ucum_id_list.append(q['UCUM1'])
            ucum_id_list.append(q['UCUM2'])
            qudt_iri = q['IRI']
    for o in om_ucum_list:
        if in_str == o['UCUM1'] or in_str == o['UCUM2']:
            ucum_id_list.append(o['UCUM1'])
            ucum_id_list.append(o['UCUM2'])
            om_iri = o['IRI']
    for u in uo_ucum_list:
        if in_str == u['UCUM1'] or in_str == u['UCUM2']:
            ucum_id_list.append(u['UCUM1'])
            ucum_id_list.append(u['UCUM2'])
            uo_iri = u['IRI']

    ucum_id_list.append(in_str)

    # Clean up parsed info:
    ucum_id_list = list(set([i for i in ucum_id_list if i]))

    return (format_ttl(qname_str=in_str, ucum_id_list=ucum_id_list, qudt_iri=qudt_iri, om_iri=om_iri,
                       uo_iri=uo_iri, qname_label=qname_label))


# --------------------------------------------------
def backslash_case(in_str):
    """Convert the s2 from `m/s2` to s-2 from `m.s-2`"""
    match = re.search(r"(\D*)(\d)*", in_str)
    if match.group(2) is None:
        return '{}-1'.format(match.group(1))
    else:
        return '{}-{}'.format(match.group(1), match.group(2))


# --------------------------------------------------
def ucum_to_qname(in_str):
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
def format_ttl(qname_str, ucum_id_list, qudt_iri, om_iri, uo_iri, qname_label):
    """Format parsed IDs and UCUM codes into ttl"""
    qudt_id = ''
    om_id = ''
    uo_id = ''
    qudt_regex = r"(http://qudt.org/vocab/unit/)(.*)"
    om_regex = r"(http://www.ontology-of-units-of-measure.org/resource/om-2/)(.*)"
    uo_regex = r"(http://purl.obolibrary.org/obo/UO_)(.*)"

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
    out_file = args.output
    qname_mapping = args.qname

    # Read in argument input files
    input_list = []
    # open and save input data file as list of strings
    with open(input_file, mode ='r', encoding='utf-8-sig') as input:
        csv_reader = csv.reader(input, delimiter=',')
        for row in csv_reader:
            input_list.append(row[0])

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
    input_list = [ucum_to_qname(i) for i in input_list]
    # Remove duplicates
    input_list = list(set(input_list))
    # Sort alphabetically
    input_list.sort()

    for i in input_list:
        # get qname string label
        # TODO can modify gen_qname_label() to make input strings unique by alphabetizing "." separated terms
        # In order to get to unique qnames e.g. `Cel-1.d-1` == `d-1.Cel-1`
        # Can maybe call this function on all of input_list prior to sorting/removing duplicates and
        # Calling qname on the whole list as to make sure we have a list of unique qnames prior to printing a new one
        qname_str = gen_qname_label(i, qname_mapping_list)

        # Perhaps not the best way to handle the None values returned from the previous functions.
        call = qname(in_str=i, qname_label=qname_str, om_ucum_list=om_ucum_list, qudt_ucum_list=qudt_ucum_list, uo_ucum_list=uo_ucum_list,
                     qname_mapping_list=qname_mapping_list)
        if call is not None:
            print(call, file=f)


# --------------------------------------------------
if __name__ == '__main__':
    main()