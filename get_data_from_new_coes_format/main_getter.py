import time
import pandas as pd
from datetime import datetime

from get_data_from_new_coes import provide_automation_drivers, run_browser_extraction, generate_record, read_latest_parquet_pathlib, data_postprocessing, assign_latest_reference, write_df_in_excel
from get_data_from_old_coes import order_data, print_repeated_strings, get_specific_data_from_coes

def get_data_from_new_source():
    get_data_from_coes = True

    load_data_decision = ''
    while not load_data_decision:
        load_data_decision = input("-> To access COES, write 'c'\n-> To read existing file directly, write 'f'\n")
        load_data_decision = load_data_decision.lower()
        if load_data_decision!='f' and load_data_decision!='c':
            load_data_decision = ''
            print('Please, only allowed letters "c" or "f"\n\n')
    
    get_data_from_coes = load_data_decision=='c'

    if get_data_from_coes:
        main_paths = {
            'webpage_url': r'https://plataformadeproyectos.coes.org.pe/iniciar-sesion',
            'chromedriver_path': r'Other_drivers\v146\chromedriver-win64\chromedriver.exe',
            'relative_download_dir': r'input\downloaded_file'
        }
        
        wait_driver, driver = provide_automation_drivers(**main_paths)

        epo_path, collected_epo_powers, collected_epo_types, colllected_epo_third_names, \
        eo_path, collected_eo_powers, collected_eo_types, colllected_eo_third_names       \
        = run_browser_extraction(main_paths, wait_driver, driver)

        epo_df = pd.read_excel(epo_path, engine='openpyxl')
        eo_df = pd.read_excel(eo_path, engine='openpyxl')

        power_name = 'Potencia Nominal (MW)'
        epo_df[power_name] = epo_df['Nombre'].map(collected_epo_powers).astype('float')
        eo_df[power_name] = eo_df['Nombre'].map(collected_eo_powers).astype('float')

        type_name = 'Tipo'
        epo_df[type_name] = epo_df['Nombre'].map(collected_epo_types)
        eo_df[type_name] = eo_df['Nombre'].map(collected_eo_types)

        third_name = 'Tercero Involucrado'
        epo_df[third_name] = epo_df['Nombre'].map(colllected_epo_third_names)
        eo_df[third_name] = eo_df['Nombre'].map(colllected_eo_third_names)

        epo_eo_df = pd.concat([epo_df, eo_df], ignore_index=True)

        generate_record(epo_eo_df)

    else:
        epo_eo_df = read_latest_parquet_pathlib()

    epo_eo_df = data_postprocessing(epo_eo_df)

    excel_base_path = r'input\base\Consulta_Web_EPO_EO_Cambio 1.xlsx'
    base_df = pd.read_excel(excel_base_path, engine='openpyxl')

    datetime_column = 'Fecha de Presentación'
    base_df[datetime_column] = pd.to_datetime(base_df[datetime_column])
    base_df[datetime_column] = base_df[datetime_column].dt.strftime('%d/%m/%Y')

    homologated_names = {'Código': 'Código de Estudio', 'Nombre': 'Nombre del Estudio', 'Zona de Proyecto': 'Zona', 'Titular': 'Titular del proyecto', 'Potencia Nominal (MW)': 'Potencia(MW)'}
    adapted_operational_data = epo_eo_df.rename(columns=homologated_names).reindex(columns=base_df.columns)
    updated_df = pd.concat([base_df, adapted_operational_data])

    # Grouping data
    updated_df = assign_latest_reference(updated_df)

    # states_to_group = ['aprobado', 'en revisión']
    # similarity_threshold = .805
    # similars = group_strings_by_similarity(updated_df[updated_df['Estado'].str.lower().isin(states_to_group)]['Nombre del Estudio'], similarity_threshold)
    # save_to_text(similars, similarity_threshold)

    output_file_name = f'final_output_by_new_coes_{datetime.now().strftime("%Y%m%d%H%M%S")}'
    write_df_in_excel({'last_data': updated_df}, output_file_name)
    return output_file_name

def get_data_from_old_source(base_file_name):
    project_types = [
            "Generación Convencional",
            "Generación No Convencional",
            "Transmisión",
            "Demanda"
        ]
    
    df_EO = pd.DataFrame()
    df_EPO = pd.DataFrame()

    for project_type in project_types:
        df_EO_by_type = get_specific_data_from_coes(True, project_type)
        time.sleep(8)
        df_EO = pd.concat([df_EO, df_EO_by_type])

        print(f'df_EO head:\n{df_EO.head(3)}\n')
        print(f'df_EO size: {df_EO.shape}\n')
        print(f'df_EO tail:\n{df_EO.tail(3)}\n')

        df_EPO_by_type = get_specific_data_from_coes(False, project_type)
        time.sleep(8)
        df_EPO = pd.concat([df_EPO, df_EPO_by_type])

        print(f'df_EPO head:\n{df_EPO.head(3)}\n')
        print(f'df_EPO size: {df_EPO.shape}\n')
        print(f'df_EPO tail:\n{df_EPO.tail(3)}\n')

    print(f'-------------------\n')

    df_new = pd.concat([df_EO, df_EPO], ignore_index = True)
    
    print(f'df_EO size: {df_EO.shape}\n')
    print(f'df_EPO size: {df_EPO.shape}\n\n')
    print(f'df_new size: {df_new.shape}\n')
    print_repeated_strings(df_new, 'Código de Estudio')
    print()

    ## Change the 2 first parameters to receives the data (Or even better, previously already concatenated)
    final_df = order_data(df_new, 'output\\from_new_source\\' + base_file_name + '.xlsx')

    final_df.to_excel('output\\final_extraction\\' + f'final_output_by_old_coes_{datetime.now().strftime("%Y%m%d%H%M%S")}.xlsx', index=False)
    ##final_df.to_excel(fr"output\Consulta_Web_EPO_EO_Cambio_{datetime.now()}.xlsx", index=False)


if __name__ == '__main__':
    get_data_from_old_source(get_data_from_new_source())
