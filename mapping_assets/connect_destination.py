import pandas as pd

if __name__ == '__main__':
    extraction_path = r'output\extraction.xlsx'
    extracted_df = pd.read_excel(extraction_path, engine='openpyxl')

    info_path = r'input\file.xlsx'
    info_df = pd.read_excel(info_path, engine='openpyxl')

    # 1. Primary Merge: Match 'Code' with 'Código SAP Activo'
    # Use how='left' to keep all rows in base_df
    extracted_df = extracted_df.merge(
        info_df[['Código SAP Activo', 'Destino']], 
        left_on='Code', 
        right_on='Código SAP Activo', 
        how='left'
    ).rename(columns={'Destino': 'destiny'})

    # 2. Cleanup: Remove the extra join column
    extracted_df.drop(columns=['Código SAP Activo'], inplace=True)

    # 3. Secondary Match: For rows where Code is 'NO TIENE', match on serial number
    # We create a mapping dictionary from info_df for quick lookup
    serie_map = info_df.set_index('Serie')['Destino'].to_dict()

    # Identify rows where destiny is missing AND Code is "NO TIENE"
    mask = (extracted_df['destiny'].isna()) & (extracted_df['Code'] == 'NO TIENE')

    # Update those specific rows using the map
    extracted_df.loc[mask, 'destiny'] = extracted_df.loc[mask, 'serie_number'].map(serie_map)

    extracted_df.to_excel(r"output\detection.xlsx", index=False)