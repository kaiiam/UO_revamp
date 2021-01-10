#!/usr/bin/env python3
"""
Author : Kai
Date   : 2021-01-07
Purpose: Automate mapping between units ontologies UO against OM and QUDT

Run with OM:

./mapping_uo_to_om.py -b ../../uo_template/uo_template.csv -t ../../ontologies/om_export_xlsx.csv -o output_uo_to_om_mapping.csv -m unmapped_uo_to_om.csv -n unmapped_om_to_uo.csv -s suggestions_uo_to_om.csv

OLD ~~~Test UO-> OM ./mapping.py -b test_inputs/test_uo.csv -t ../ontologies/om_export_xlsx.csv -o output_mapping_test.csv -m missing_test.csv

"""

import argparse
import sys
import csv
import re

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
        help='Base ontology to map from (UO)',
        metavar='str',
        type=str,
        default='')

    parser.add_argument(
        '-t',
        '--target',
        help='Target ontology to map to (OM)',
        metavar='str',
        type=str,
        default='')

    parser.add_argument(
        '-o',
        '--output',
        help='Output UO to OM mapping',
        metavar='str',
        type=str,
        default='')

    parser.add_argument(
        '-m',
        '--missing',
        help='Unmapped UO terms',
        metavar='str',
        type=str,
        default='')

    parser.add_argument(
        '-n',
        '--unmapped',
        help='Unmapped OM terms',
        metavar='str',
        type=str,
        default='')

    parser.add_argument(
        '-s',
        '--suggestions',
        help='Suggested mappings for unmapped UO terms',
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
def print_mapping(BaseID,BaseLabel,TargetLabel,TargetID):
    """Format mapping input to print"""
    outline=(BaseID,BaseLabel,TargetLabel,TargetID)
    return(outline)

# --------------------------------------------------
def ham_dist(s1, s2):
    """Haming distance calculation function"""

    dist = abs(len(s1) - len(s2))
    for c1, c2 in zip(s1, s2):
        if c1 != c2:
            dist +=1
    #logging.debug('s1 = {} s2 = {} d = {}'.format(s1, s2, dist))
    return(dist)

# --------------------------------------------------
def remove_tup_duplicates(lst):
    """Remove duplicates from list of tuples"""
    return [t for t in (set(tuple(i) for i in lst))]


# --------------------------------------------------
#
def sort_tuples(tup):
    """Function to sort a list of tuples """
    # reverse = None (Sorts in Ascending order)
    # key is set to sort using first element of
    # sublist lambda has been used
    tup.sort(key = lambda x: x[0])
    return tup


# --------------------------------------------------
def main():
    """Map UO to OM"""
    args = get_args()
    base_ont = args.base
    target_ont = args.target
    out_file = args.output
    m_file = args.missing
    n_file = args.unmapped
    s_file = args.suggestions


    # make sure to remove the 2nd row aka the template strings will screw thing up! Did for the test but not the main uo file
    base_list = []
    # open and save input file of base ontology to map to target
    with open(base_ont, mode ='r', encoding='utf-8-sig' ) as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            base_list.append(row)


    target_list = []
    # open and save input file of target ontology to map against base
    with open(target_ont, mode ='r', encoding='utf-8-sig' ) as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            target_list.append(row)

    #Open and print mappings
    #(BaseID,BaseLabel,TargetLabel,TargetID)
    header = ('UO ID', 'UO label', 'OM label','OM ID')
    f = open(out_file, mode='w', encoding='utf-8-sig')
    print(','.join(header), file=f)





    # regex patterns:
    regex_OM_ID = r"(http://www.ontology-of-units-of-measure.org/resource/om-2/)([\w]*)$"

    #Mapping
    for b in base_list:
        if (b['Type'] == 'class') and b['ontology ID'].startswith('UO:') and b['label'] != '':
            exact_syn_list = b['exact synonym'].split('|')
            exact_syn_list = list(filter(None, exact_syn_list))
            related_syn_list = b['related synonym'].split('|')
            related_syn_list = list(filter(None, related_syn_list))

            for t in target_list:
                #Exact match for Base label vs Target label or alt label
                if (b['label'] == t['LABEL']) or (b['label'] == t['alternative label']) :
                    print(','.join(print_mapping(BaseID=b['ontology ID'],BaseLabel=b['label'],TargetID=t['ID'],TargetLabel=t['LABEL'])), file=f)

                # elif ham_dist(b['label'],t['LABEL']) == 0:
                #     print(','.join(print_mapping(BaseID=b['ontology ID'],BaseLabel=b['label'],TargetID=t['ID'],TargetLabel=t['LABEL'])), file=f)

                # # # #Exact match for Base exact synonym vs Target LABEL (works) ### Don't add syn against alt label that cause bugs
                elif t['LABEL'] in exact_syn_list:
                    for s in exact_syn_list:
                        if s == t['LABEL']:
                            print(','.join(print_mapping(BaseID=b['ontology ID'],BaseLabel=b['label'],TargetID=t['ID'],TargetLabel=t['LABEL'])), file=f)

                elif t['LABEL'] in related_syn_list:
                    for s in related_syn_list:
                        if s == t['LABEL']:
                            print(','.join(print_mapping(BaseID=b['ontology ID'],BaseLabel=b['label'],TargetID=t['ID'],TargetLabel=t['LABEL'])), file=f)

                # this removes many of the remaining cases as it checks for anything that matches.
                # try the hamming distances with everyting that is in missing
                elif re.search(regex_OM_ID, t['ID']):
                    match = re.search(regex_OM_ID, t['ID'])
                    ID_label = match.group(2)
                    #adding the .lower() makes it a little more permissive we could remove them to be more strict
                    if (b['label'].lower() == ID_label.lower()) and (b['label'] != ''):
                        print(','.join(print_mapping(BaseID=b['ontology ID'],BaseLabel=b['label'],TargetID=t['ID'],TargetLabel=t['LABEL'])), file=f)

                # # Hamming distance doesn't get as many here but it seems to get a few
                # elif (b['label'] != '') and (t['LABEL'] != ''):
                #     d = ham_dist(b['label'],t['LABEL'])
                #     if d < 3:
                #         print(d, b['ontology ID'],b['label'],t['LABEL'],t['ID'])
                #
                # elif (b['label'] != '') and (t['LABEL'] != ''):
                #     d = ham_dist(b['label'],t['LABEL'])
                #     if d < 3:
                #         print(d, b['ontology ID'],b['label'],t['LABEL'],t['ID'])


                else:
                    pass





    # Close and reopen mapping output file
    f.close()
    output_list = []
    with open(out_file, mode ='r', encoding='utf-8-sig' ) as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            output_list.append(row)

    #Open and print unmapped UO terms
    m_header = ('UO ID', 'UO label')
    f2 = open(m_file, mode='w', encoding='utf-8-sig')
    print(','.join(m_header), file=f2)

    #Loop through base_ont and make a list of what UO terms are missing in the mapping
    for b in base_list:
        if b['ontology ID'].startswith('UO:'):
            id_list = [o for o in output_list if b['ontology ID'] == o['UO ID']]
            if not id_list:
                m_out = (b['ontology ID'],b['label'])
                print(','.join(m_out),file=f2)

    #Open and read missing UO terms from mappings
    f2.close()

    f3 = open(m_file, mode='r', encoding='utf-8-sig')

    missing_list = []
    with open(m_file, mode ='r', encoding='utf-8-sig' ) as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            missing_list.append(row)
    f3.close()


    initial_mapping_om_ids = [o['OM ID'] for o in output_list]
    #print(initial_mapping_om_ids)

    #Open and write suggestions file
    s_header = ('Hamm dist','UO ID', 'UO label', 'OM label','OM ID')
    f4 = open(s_file, mode='w', encoding='utf-8-sig')
    print(','.join(s_header), file=f4)

    for m in missing_list:
        for t in target_list:
            if t['ID'] not in initial_mapping_om_ids:
                #Hamming distance
                if (m['UO label'] != '') and (t['LABEL'] != ''):
                    d = ham_dist(m['UO label'],t['LABEL'])
                    if d < 3:
                        s_out = (str(d), m['UO ID'],m['UO label'],t['LABEL'],t['ID'])
                        print(','.join(s_out),file=f4)
    f4.close()



    #Open and write unmapped OM terms
    n_header = ('OM label', 'OM ID')
    f5 = open(n_file, mode='w', encoding='utf-8-sig')
    print(','.join(n_header), file=f5)

    unmaped_OM = [(t['LABEL'],t['ID']) for t in target_list if t['ID'] not in initial_mapping_om_ids]
    unmaped_OM = remove_tup_duplicates(unmaped_OM)
    unmaped_OM = sort_tuples(unmaped_OM)

    #[x for x in unmaped_OM]

    for x in unmaped_OM:
        print(','.join(x),file=f5)


    #set(unmaped_OM_Ids)
    #[stuff for x in set(unmaped_OM_Ids)]

    # for t in target_list:
    #     if t['ID'] in set(unmaped_OM_Ids):
    #         n_out = (t['ID'],t['LABEL'])
    #         print(','.join(n_out),file=f5)

    # for x in set(unmaped_OM_Ids):
    #     if x ==

    # set(OM_list)
    # print(OM_list)






#### OLD

### WORKING
# # #Exact match for Base exact synonym vs Target symbol
### This sort of works but its more permissive then we want instead try matching labels and syns with the string after http://www.ontology-of-units-of-measure.org/resource/om-2/ in OM
# if b['exact synonym'] == t['symbol']:
#     print(','.join(print_mapping(BaseID=b['ontology ID'],BaseLabel=b['label'],TargetID=t['ID'],TargetLabel=t['LABEL'])), file=f)

# #Exact match for Base exact synonym vs Target alternative label WORKING
# if b['exact synonym'] == t['alternative label']:
#     print(b['ontology ID'],b['exact synonym'],t['alternative label'])






# --------------------------------------------------
if __name__ == '__main__':
    main()
