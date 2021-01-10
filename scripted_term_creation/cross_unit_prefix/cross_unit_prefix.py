#!/usr/bin/env python3
"""
Author : Kai
Date   : 2021-01-02
Purpose: Cross metric prefies with units to generate Robot template input

Run: ./cross_unit_prefix.py -p in_csv/prefix.csv -i in_csv/units_to_cross.csv

test_run: ./cross_unit_prefix.py -p in_csv/prefix.csv -i in_csv/temp_cross.csv -t in_csv/uo_template.csv -o temp_out.csv

"""

import argparse
import sys
import csv



# global var:
# have 1100000 - 1101000 be the range for named units I add like atmosphere or farad
id_int = 1101000

# --------------------------------------------------
def get_args():
    """get command-line arguments"""
    parser = argparse.ArgumentParser(
        description='Argparse Python script',
        formatter_class=argparse.ArgumentDefaultsHelpFormatter)

    # parser.add_argument(
    #     'positional', metavar='str', help='A positional argument')

    parser.add_argument(
        '-p',
        '--prefix',
        help='input prefix csv',
        metavar='str',
        type=str,
        default='')

    parser.add_argument(
        '-i',
        '--input',
        help='input units to cross csv',
        metavar='str',
        type=str,
        default='')

    parser.add_argument(
        '-t',
        '--template',
        help='input UO template csv file to check for existing terms',
        metavar='str',
        type=str,
        default='')

    parser.add_argument(
        '-o',
        '--output',
        help='robot template outfile',
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

# --------------------------------------------------
def print_robot_template(Id,Ilabel,SC,UCUMbase,Plabel,Pnum,Psym,Tlist):
    """print Robot template input for prefix unit combinations"""

    label = '{}{}'.format(Plabel,Ilabel)

    #note for `megaHertz` the H is capitalized might want to lowercase the t and tlabels
    id_list = [t for t in Tlist if label == t['label']]

    # Assign new or find existing ontology_ID
    if len(id_list) == 0:
        ontology_ID = assign_new_ID()
    else:
        ontology_ID = id_list[0]['ontology ID']
        #print(id_list[0]['ontology ID'])
        if len(id_list) > 1:
            #print(label)
            ids = [x['ontology ID'] for x in id_list]
            duplicate_str = ','.join(ids)
            warn(msg='Warning {} has multiple IDs: {}'.format(label, duplicate_str))


        #     duplicate_str = ','.join(id_list['ontology ID'])
        #     warn(msg=duplicate_str)


    subclass = Ilabel
    equivalence = "{} and ('has prefix' some {})".format(Ilabel,Plabel)
    definition = 'A unit which is equal to {} {}.'.format(Pnum,Ilabel)
    ucum = '{}{}'.format(Psym,UCUMbase)

    outline= (ontology_ID,label,subclass,equivalence,definition,ucum)
    return(outline)




# --------------------------------------------------
def assign_new_ID():
    """outputs a new unique UO curie"""
    global id_int

    outstr = ''
    if id_int < 10:
        outstr = 'UO:000000{}'.format(id_int)
    elif id_int < 100:
        outstr = 'UO:00000{}'.format(id_int)
    elif id_int < 1000:
        outstr = 'UO:0000{}'.format(id_int)
    elif id_int < 10000:
        outstr = 'UO:000{}'.format(id_int)
    elif id_int < 100000:
        outstr = 'UO:00{}'.format(id_int)
    elif id_int < 1000000:
        outstr = 'UO:0{}'.format(id_int)
    elif id_int < 10000000:
        outstr = 'UO:{}'.format(id_int)
    id_int += 1
    return(outstr)
# --------------------------------------------------




# --------------------------------------------------
def main():
    """Make a jazz noise here"""
    args = get_args()
    prefix_arg = args.prefix
    input_arg = args.input
    template_arg = args.template
    out_file = args.output


    prefix_list = []
    # open and save prefix file as list of OrderedDict
    with open(prefix_arg, mode ='r', encoding='utf-8-sig' ) as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            prefix_list.append(row)


    input_list = []
    # open and save input file of units to cross as list of OrderedDict
    with open(input_arg, mode ='r', encoding='utf-8-sig' ) as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            input_list.append(row)

    template_list = []
    # open and save uo_template file as list of OrderedDict
    with open(template_arg, mode ='r', encoding='utf-8-sig' ) as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            template_list.append(row)



    #open outfile1 and print
    header_1 = ('Ontology ID', 'label', 'parent class', 'equivalence axiom' , 'definition', 'UCUM code')
    header_2 =('ID', 'AL rdfs:label@en', 'SC %','EC %', 'AL IAO:0000115@en', 'A oboInOwl:hasDbXref SPLIT=|')
    f = open(out_file, mode='a', encoding='utf-8-sig' )
    print(','.join(header_1), file=f)
    print(','.join(header_2), file=f)




    # Loop through input_list and cross with prefixes
    for i in input_list:
        #print(i['ontology ID'])
        for p in prefix_list:
            print(','.join(print_robot_template(Id=i['ontology ID'],Ilabel=i['label'],SC=i['SubClass Of'], UCUMbase=i['UCUM base'], Plabel=p['label'],Pnum=p['prefix_num'],Psym=p['prefix_symbol'],Tlist=template_list)), file=f)






# --------------------------------------------------
if __name__ == '__main__':
    main()
