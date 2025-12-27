import pandas as pd

df = pd.read_excel('Data.xlsx', header= None)

df = df[[0, 8, 6, 15, 7, 16, 27, 38]]
expected_columns = ['IDELEMEN', 'EMPRESA', 'SUBESTACION', 'NIVELTENSIONPRIMARIO', 'ELEMENTOEQUIPO', 'CAPACIDADNOMINALPRIMARIO', 'CAPACIDADNOMINALSECUNDARIO', 'CAPACIDADNOMINALTERCIARIO']
df.columns = expected_columns
df['SUBESTACION'] = df['SUBESTACION'].str[:4]

df_grp = df.groupby('SUBESTACION')

data_collection = []
for tp in list(df_grp):
    tp_n = tp[1].stack(dropna = False).to_frame().T
    list_columns = []
    for i in range(len(tp[1])):
        list_columns.extend([column + f'{i+1}' for column in expected_columns])
    tp_n.columns = list_columns
    data_collection.append(tp_n)
    
df_final = pd.concat(data_collection, ignore_index = True)

df_final.to_excel('Data_processed.xlsx', index = False)