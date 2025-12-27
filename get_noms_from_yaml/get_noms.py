import pandas as pd

import json

if __name__ == '__main__':

    # Get data
    collected_df = pd.read_parquet(r'input\in_parquet\collected_data.parquet')
    collected_df = collected_df.set_index('nombre')

    af_df = pd.read_parquet(r'input\in_parquet\af_df.parquet')
    af_df = af_df.set_index('BAHIA')
    af_df['NOM'] = None

    with open(r'output\homologated_names_t5.json', 'r') as file:
        homologation:dict = json.load(file)

    # Put TC
    for collected_df_index, af_df_index in homologation.items():
        af_df.at[af_df_index, 'NOM'] = collected_df.at[collected_df_index, 'nom']

    print(af_df)

    # Generate new AF data with column
    excel_file_path = r'output\modified_excel_t2.xlsx'
    af_df.to_excel(excel_file_path, index=False)