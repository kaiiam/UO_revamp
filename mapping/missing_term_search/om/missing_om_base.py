#!/usr/bin/env python3
"""
Author : kai
Date   : 2021-01-11
Purpose: Check base OM terms against mapped OM terms to find missing ones

Run:

./missing_om_base.py -b om_base_full.csv -m verified_uo_om_mapping.csv -t ../../../ontologies/om_export_xlsx.csv -o unmapped_om_base.csv

"""

import argparse
import sys
import csv

# --------------------------------------------------
def get_args():
    """get command-line arguments"""
    parser = argparse.ArgumentParser(
        description='Argparse Python script',
        formatter_class=argparse.ArgumentDefaultsHelpFormatter)

    # parser.add_argument(
    #     'positional', metavar='str', help='A positional argument')

    parser.add_argument(
        '-b',
        '--base',
        help='Full list of base om terms',
        metavar='str',
        type=str,
        default='')

    parser.add_argument(
        '-m',
        '--mapped',
        help='OM terms mapped to UO',
        metavar='str',
        type=str,
        default='')

    parser.add_argument(
        '-t',
        '--target',
        help='Full OM export',
        metavar='str',
        type=str,
        default='')

    parser.add_argument(
        '-o',
        '--output',
        help='Missing unmapped OM base terms',
        metavar='str',
        type=str,
        default='')

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


# --------------------------------------------------
def main():
    """Make a jazz noise here"""
    args = get_args()
    base_arg = args.base
    mapped_arg = args.mapped
    target_arg = args.target
    output_arg = args.output

    #Full list of base om terms
    base_list = []
    # open input.csv
    with open(base_arg, mode ='r', encoding='utf-8-sig') as input:
        csv_reader = csv.reader(input, delimiter=',')
        for row in csv_reader:
            base_list.append(row[0])

    # dict of OM terms mapped to UO.
    mapping_list = []
    with open(mapped_arg, mode ='r', encoding='utf-8-sig' ) as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            mapping_list.append(row)


    target_list = []
    with open(target_arg, mode ='r', encoding='utf-8-sig' ) as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            target_list.append(row)

    #mostly works but not getting ID
    missing_list = []
    for b in base_list:
        id_list = [m for m in mapping_list if b == m['OM label']]
        if not id_list:
            missing_list.append(b)

    #Open and print missing mappings
    header = ('OM label','OM ID')
    f = open(output_arg, mode='w', encoding='utf-8-sig')
    print(','.join(header), file=f)

    for m in missing_list:
        for t in target_list:
            if m == t['LABEL']:
                #print(t['LABEL'],t['ID'])
                m_out = (t['LABEL'],t['ID'])
                print(','.join(m_out),file=f)


# --------------------------------------------------
if __name__ == '__main__':
    main()
