import pandas as pd

import re

import json

from collections import Counter


def write_dict_to_txt_json(dictionary, filename):
    try:
        with open(filename, 'w') as file:
            json.dump(dictionary, file, indent=4) # indent for pretty printing
        print(f"Dictionary successfully written to '{filename}' in JSON format.")
    except IOError as e:
        print(f"Error writing to file '{filename}': {e}")

def only_num(input_string):
    return re.sub(r'[^0-9]', '', input_string)

def multiple_replace(text, replacements):
    # Create a regex pattern with all keys
    pattern = re.compile("|".join(re.escape(k) for k in replacements.keys()))
    # Replace using the dictionary
    return pattern.sub(lambda match: replacements[match.group(0)], text)


if __name__ == '__main__':
    # Get data and set indexes
    collected_df = pd.read_parquet(r'input\in_parquet\collected_data.parquet')
    collected_df = collected_df.set_index('nombre')

    af_df = pd.read_parquet(r'input\in_parquet\af_df.parquet')
    af_df = af_df.set_index('BAHIA')

    # Relate indexes by containing of idBarra in BAHIA and by only numbers of idBarra and IDELEMENT
    related_ones = {}
    coll_already_found = []
    af_already_found = []

    exception_nominations_in_af = {
        'Name1': 'correction1',
        'Name2': 'correction2'
    }

    for coll_index, coll_values in collected_df.iterrows():
        if coll_index not in coll_already_found:
            for af_index, af_values in af_df.iterrows():

                if af_index not in af_already_found:

                    coll_cod = only_num(coll_values['Cellcode'])
                    af_cod = only_num(af_values['IDELEMENT'])

                    if ((coll_values['idBarra'] in multiple_replace(af_index, exception_nominations_in_af)) or                                        
                        (coll_index.startswith('name3') and (coll_values['idBarra'].replace('CHMB', 'CHIM') in af_index)) or     
                        (af_values['NOMBRESUBESTACION']=='Place 1')
                        ) and \
                       (((coll_cod in af_cod) and (len(coll_cod)>2)) or
                        ((af_cod.startswith(coll_cod)) and (len(coll_cod)<3)) or
                        (abs(int(coll_cod) - int(af_cod))<3)
                        )\
                    :
                    #if coll_index.startswith(af_values['NOMBRESUBESTACION']) and (only_num(coll_values['codCelda']) in only_num(af_values['IDELEMENT'])):
                        
                        related_ones[coll_index] = af_index
                        
                        coll_already_found.append(coll_index)
                        af_already_found.append(af_index)
                        break

    not_in_af_records = ['place_exceptions']
    #not_in_af_records = []
    coll_not_found = [coll for coll in collected_df.index if (coll not in coll_already_found) and (coll.split()[0] not in not_in_af_records)]
    af_not_found = [af for af in af_df.index if af not in af_already_found]

    coll_not_found_init = [a.split()[0] for a in coll_not_found]
    repetitions = Counter(coll_not_found_init)

    print(f'🟨  {len(coll_not_found)} coll_not_found: \n{coll_not_found}\n')
    print(f'repetitions_not_found_collect:\n{repetitions}\n')
    
    print(f'🟨  {len(af_not_found)} af_not_found: \n{af_not_found}\n')
            
    #write_dict_to_txt_json(related_ones, r'output\homologated_names_t5.json')
