import os
import re
import time
import pprint
import pandas as pd
import numpy as np
from datetime import datetime
from pathlib import Path
from difflib import SequenceMatcher

from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import Select

#--- Data functions ------------------------------------------------------
def write_df_in_excel(dfs: dict[str, pd.DataFrame], filename = 'output_excel'):

    # 2. Use ExcelWriter as a context manager to write the DataFrames
    excel_file_name = fr'output\from_new_source\{filename}.xlsx'

    excel_opened = True
    while excel_opened:
        try:
            with pd.ExcelWriter(excel_file_name, engine='openpyxl') as writer:
                for df_name, df_data in dfs.items():
                    df_data.to_excel(writer, sheet_name=df_name, index=False)
            excel_opened = False
        except PermissionError:
            print(f'🟥 The excel is opened, please close the excel')
            time.sleep(8)

    print(f"✅  Successfully created '{excel_file_name}' with sheets {dfs.keys()}")

def get_newest_excel_file_path(folder_path):
    """
    Gets the absolute path of the newest Excel file (both .xlsx and .xls) 
    within the specified folder based on modification time.

    Args:
        folder_path (str or Path): The path to the directory to search.

    Returns:
        Path or None: The path of the newest Excel file as a Path object, 
                      or None if no Excel files are found.
    """
    # Create a Path object for the directory
    directory = Path(folder_path)

    # Use rglob for recursive search, or glob for only the top level
    # We create a list of all matching files
    excel_files = list(directory.rglob("*.xlsx")) + list(directory.rglob("*.xls"))

    # If no files are found, return None
    if not excel_files:
        return None

    # Use max() to find the file with the most recent modification time (st_mtime)
    # The key is a lambda function that returns the modification timestamp for each file
    newest_file = max(excel_files, key=lambda file: file.stat().st_mtime)

    return newest_file

def wait_for_new_downloaded_excel_path(download_path, timeout = 45):

    def count_file_in_folder():
        return len([f for f in os.listdir(download_path) if f.endswith(f'.xlsx')])

    i = 0
    initial_amount_of_files = count_file_in_folder()
    print(f'✅🗃️  initial amount of files: {initial_amount_of_files} \n')
    while initial_amount_of_files == count_file_in_folder() and i<timeout:
        time.sleep(1)
        i += 1

    print(f'✅⏱️  The download took less than {i} seconds and now there are {count_file_in_folder()} files\n')

    return get_newest_excel_file_path(download_path)

def generate_record(df: pd.DataFrame):
    parquet_file_path = fr'output\extraction_record\{datetime.now().strftime("%Y%m%d%H%M%S")}.parquet'
    df.to_parquet(parquet_file_path, engine='pyarrow', compression='snappy')

def read_latest_parquet_pathlib(folder_path = r'output\extraction_record'):
    # Create a Path object for the directory
    directory = Path(folder_path)
    
    # Get all .parquet files in the folder (use .rglob if you need to search subfolders)
    files = list(directory.glob("*.parquet"))
    
    if not files:
        print("No Parquet files found.")
        return None
    
    # Get the latest file based on last modification time (st_mtime)
    # Use st_ctime if you specifically want 'creation' time (OS dependent)
    latest_file = max(files, key=lambda f: f.stat().st_mtime)
    
    # Path objects are natively supported by pandas.read_parquet
    return pd.read_parquet(latest_file)

#--- Control functions ------------------------------------------------------
def provide_automation_drivers(webpage_url, chromedriver_path, relative_download_dir, headless = False):   
    absolute_download_dir = os.path.abspath(relative_download_dir)
    prefs = {
        "download.default_directory": absolute_download_dir, # Set the folder
        "download.prompt_for_download": False,               # Disable "Save As" prompt
        "download.directory_upgrade": True,
        "safebrowsing.enabled": True                         # Prevents blocking "risky" files
    }

    options = webdriver.ChromeOptions()
    options.add_experimental_option("prefs", prefs)
    if headless:
        options.add_argument('--headless=new')  # Run headless for efficiency

    service = Service(chromedriver_path)

    driver = webdriver.Chrome(service=service, options=options)
    driver.get(webpage_url)

    return WebDriverWait(driver, 10), driver

def keep_table_with_max_number_of_elements(wait_driver):
    select_element = wait_driver.until(EC.presence_of_element_located((By.CSS_SELECTOR, "select[aria-label='Filas por página']")))
    select = Select(select_element)
    highest_option = max(select.options, key=lambda opt: int(opt.text))
    select.select_by_visible_text(highest_option.text)
    print("✅🖱️🎫  Combobox element clicked successfully to see more row per page\n")

def wait_for_loading(driver):
    print("⌚  Loading Started")

    # Define the locator for your loading screen
    # This XPath finds the <span> containing 'Loading...' inside your specific div structure
    loader_locator = (By.XPATH, "//span[text()='Loading...']/ancestor::div[contains(@class, 'fixed')]")

    # Wait up to 30 seconds for the animation to disappear
    WebDriverWait(driver, 30).until(
        EC.invisibility_of_element_located(loader_locator)
    )

    # Execution will now only continue once the animation is gone
    print("⌚  Loading finished\n")


#--- Main functions ------------------------------------------------------

#--- Web automation functions
def get_info_from_project_page(wait_driver):
    project_name_field = wait_driver.until(EC.visibility_of_element_located((By.ID, "nameProject")))
    project_name = project_name_field.get_attribute("value")
    print(f"✅🪟  Project name: {project_name}")

    power_field = wait_driver.until(EC.visibility_of_element_located((By.ID, "nominal")))
    power_value = power_field.get_attribute("value")
    print(f"✅🪟  Nominal power (MW): {power_value}\n")

    project_type_field = wait_driver.until(EC.visibility_of_element_located((By.ID, "typeProjectText")))
    type_value = project_type_field.get_attribute("value")
    print(f"✅🪟  Type of project : {type_value}\n")

    third_data_tab = wait_driver.until(EC.element_to_be_clickable((By.XPATH, "//button[text()='Datos del Tercero']")))
    third_data_tab.click()
    print("✅🖱️  Tab of third data was clicked\n")

    ## Sometimes a message of waiting appears here

    loading_stopping = True
    while loading_stopping:
        try:
            cells = wait_driver.until(EC.presence_of_all_elements_located(
                (By.CSS_SELECTOR, ".rdt_TableBody [role='cell'] [data-tag='allowRowEvents']")
            ))
            third_names = ', '.join([cell.text.strip() for cell in cells])
            loading_stopping = False
            print(f"✅👷‍♂️  Third  names collected {third_names}\n")
        except Exception as e:
            print(f"⚠️👷‍♂️  Third  names not collected yet by loading | {e}\n")
            time.sleep(3)
    
    return project_name, power_value, type_value, third_names   #TODO: group into a dictionary

def navigate_to_page(target_page_i: int, wait_driver, driver):
    print(f'📄  Keeping page {target_page_i+1}\n')

    current_page_i = int((int(driver.find_element(By.CSS_SELECTOR, "span.sc-irEpRR.sc-dJDBYC.ipSHVm.YIXGw").text.split('-')[0])-1)/30)

    for _ in range(target_page_i-current_page_i):
        trying_to_nav_page = True
        while trying_to_nav_page:
            try:
                button = wait_driver.until(EC.element_to_be_clickable((By.ID, "pagination-next-page")))
                button.click()
                print("✅🖱️  Button to go to the next page was enabled and clicked\n")
                
                trying_to_nav_page = False
            except TimeoutException as e:
                print(f"⚠️🖱️  Button to go to the next page wasn't enabled and clicked. Fallback: refreshing page | The error was {e}\n")
                driver.refresh()

            wait_for_loading(driver)
            

def get_info_from_entire_table(wait_driver, driver):
    
    collected_powers = {}
    collected_types = {}
    colllected_third_names = {}

    wait_for_loading(driver)

    # Iterator per page (Button ID to go to the other page is id="pagination-next-page")
    # Selects the span that has ALL of these classes
    n_items = int(driver.find_element(By.CSS_SELECTOR, "span.sc-irEpRR.sc-dJDBYC.ipSHVm.YIXGw").text.split(' ')[-1])
    print(n_items)

    n_pages = -(n_items//-30)

    for page_i in range(n_pages):
        print(f'📄  Entering to page {page_i+1}')

        navigate_to_page(page_i, wait_driver, driver)

        # Wait for the select element to be present
        keep_table_with_max_number_of_elements(wait_driver)

        wait_for_loading(driver)

        # Wait for the table body to load
        wait_driver.until(EC.presence_of_element_located((By.CLASS_NAME, "rdt_TableBody")))

        # # Find all rows within the table body (excluding the header)
        # rows = driver.find_elements(By.XPATH, "//div[@role='row' and contains(@class, 'rdt_TableRow')]")
        # print(f"✅🧾  Found {len(rows)} rows to process.\n")

        wait_for_loading(driver)

        # Iterate through each row
        row_count = len(driver.find_elements(By.XPATH, "//div[@role='row' and contains(@class, 'rdt_TableRow')]"))
        print(f"✅🧮  Row count: {row_count}\n")
        for i in range(1, row_count + 1):

            # try:
            row_xpath = f"(//div[@role='row' and contains(@class, 'rdt_TableRow')])[{i}]"
            wait_driver.until(EC.visibility_of_element_located((By.XPATH, row_xpath)))
            print(f"✅🧾  Row found.\n")

            icon_xpath = f"{row_xpath}//div[@data-column-id='13']//*[local-name()='svg']"
            icon = wait_driver.until(EC.element_to_be_clickable((By.XPATH, icon_xpath)))
            print(f"✅🧾  Icon found.\n")
    
            # Scroll the row into view
            driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", icon)
            print(f"✅↔️  scroll found and slided.\n")
    
            # Click the icon
            driver.execute_script("arguments[0].dispatchEvent(new MouseEvent('click', {bubbles: true, cancelable: true, view: window}));", icon)
            print(f"✅🖱️  Clicked row {i} of the page {page_i+1}\n")

            wait_for_loading(driver)

            project_name, power_value, type_value, third_names = get_info_from_project_page(wait_driver)

            # Saving data in the dictionary
            collected_powers[project_name] = power_value
            collected_types[project_name] = type_value
            colllected_third_names[project_name] = third_names

            driver.back()
            print(f"✅↙️  Going back\n")

            wait_for_loading(driver)
            
            navigate_to_page(page_i, wait_driver, driver)

            keep_table_with_max_number_of_elements(wait_driver)

            wait_for_loading(driver)
            
            # except Exception as e:
            #     print(f"🟥🧾  Could not click row {index + 1}: {e}\n")
        
    return collected_powers, collected_types, colllected_third_names

def run_browser_extraction(main_paths: dict[str, str], wait_driver, driver):
    # Running browser automation
    try:

        # Accesing as guess
        button = wait_driver.until(EC.element_to_be_clickable((By.XPATH, "//span[text()='Ingresar como invitado']")))
        button.click()
        print("✅🖱️🕵️  Button clicked successfully to enter as guess\n")

        wait_for_loading(driver)

        # Download the file in EPO (Page always opens EPO first)
        download_icon = wait_driver.until(EC.element_to_be_clickable((By.XPATH, "(//div[contains(@class, 'flex items-center')]//span[contains(@class, 'bg-yellow-300')])[2]")))
        download_icon.click()
        print("✅🖱️🗃️  Button clicked successfully to download the file\n")

        wait_for_loading(driver)

        epo_path = wait_for_new_downloaded_excel_path(main_paths['relative_download_dir'])

        collected_epo_powers, collected_epo_types, colllected_epo_third_names = get_info_from_entire_table(wait_driver, driver)

        print(f'🔰  Collected power from EPO:\n')
        pprint.pprint(collected_epo_powers, indent=4, sort_dicts=False)
        print('\n')

        print(f'🔰  Collected type from EPO:\n')
        pprint.pprint(collected_epo_types, indent=4, sort_dicts=False)
        print('\n')

        print(f'🔰  Collected third names from EPO:\n')
        pprint.pprint(colllected_epo_third_names, indent=4, sort_dicts=False)
        print('\n')

        # Going to EO page
        eo_url = 'https://plataformadeproyectos.coes.org.pe/presentacion-estudio/EO'
        driver.get(eo_url)
        print("✅🛩️  Navigation to EO successfully\n")

        wait_for_loading(driver)
        # time.sleep(8)

        # Download the file in EO
        download_icon = wait_driver.until(EC.element_to_be_clickable((By.XPATH, "(//div[contains(@class, 'flex items-center')]//span[contains(@class, 'bg-yellow-300')])[2]")))
        download_icon.click()
        print("✅🖱️🗃️  Button clicked successfully to download the file\n")

        eo_path = wait_for_new_downloaded_excel_path(main_paths['relative_download_dir'])

        collected_eo_powers, collected_eo_types, colllected_eo_third_names = get_info_from_entire_table(wait_driver, driver)

        print(f'🔰  Collected power from EO:\n')
        pprint.pprint(collected_eo_powers, indent=4, sort_dicts=False)
        print('\n')

        print(f'🔰  Collected type from EO:\n')
        pprint.pprint(collected_eo_types, indent=4, sort_dicts=False)
        print('\n')

    finally:
        # Close the browser
        driver.quit()

        return                                                                           \
        epo_path, collected_epo_powers, collected_epo_types, colllected_epo_third_names,  \
        eo_path, collected_eo_powers, collected_eo_types, colllected_eo_third_names         #TODO: group into a dictionary
    

#--- Procession functions
def update_column(df: pd.DataFrame, column_name: str, mapping_dict: dict[str, list[str]]):
    inv_map = {val: key for key, val_list in mapping_dict.items() for val in val_list}
    df[column_name] = df[column_name].map(inv_map).fillna(df[column_name])
    return df

def assigning_maturity(df: pd.DataFrame):
    maturity_names = {
        'PEP': 'EPO',
        'PEO': 'EO'
    }
    df['Grado de Madurez'] = df['Código'].str[:3].map(maturity_names).fillna('')
    return df

def assigning_energy_type_by_asset_name(df:pd.DataFrame, col_name: str, category_map: dict[str, list[str]]):
    def clean_strings_fast(df: pd.DataFrame, column_name: str):
        # Normalize to Unicode NFKD (separates 'ó' into 'o' + '´')
        # Encode to ASCII and ignore errors to drop the accent marks
        # Decode back to utf-8, lowercase, and remove all whitespace
        uniformized_colum = (
            df[column_name]
            .str.normalize('NFKD')
            .str.encode('ascii', errors='ignore')
            .str.decode('utf-8')
            .str.lower()
            # .str.replace(r'\s+', '', regex=True)
        )
        return uniformized_colum

    # Create a Regex pattern that captures the prefix at the start (^)
    # We sort prefixes by length (longest first) to ensure 'ABCD' matches before 'A'
    all_prefixes = sorted([p for sublist in category_map.values() for p in sublist], key=len, reverse=True)
    pattern = f"^({'|'.join(map(re.escape, all_prefixes))})"
    
    # Create the flattened mapping for the extracted strings
    flat_map = {pref: key for key, pref_list in category_map.items() for pref in pref_list}
    
    # Extract the matching prefix and map it to the category key
    df['Tipo de Energía'] = clean_strings_fast(df, col_name).str.extract(pattern, expand=False).map(flat_map)
    return df

def assigning_energy_type_by_page_info(df: pd.DataFrame, energy_mapping: dict[str, list[str]]):
    # Iterate through the dictionary: key is the category, value is the list of sources
    for energy_type, possible_sources in energy_mapping.items():
        # Create a mask for rows that are empty/NaN and match the current group of sources
        mask = (
            ((df['Tipo de Energía'] == '') | (df['Tipo de Energía'].isna())) & 
            (df['Tipo'].isin(possible_sources))
        )
        # Assign the dictionary key as the value for matching rows
        df.loc[mask, 'Tipo de Energía'] = energy_type
        
    return df

def formatting_power(df: pd.DataFrame, types_with_power):
    mask = df['Tipo'].isin(types_with_power)
    df['Potencia Nominal (MW)'] = np.where(mask, df['Potencia Nominal (MW)'].astype(str) + ' MW', "0.0 MW")
    return df

def data_postprocessing(df: pd.DataFrame):
    reassigned_state_names = {
        'Aprobado': ['ATENDIDO_SIN_NECESIDAD_DE_ESTUDIO', 'VIGENTE'],
        'En revisión': ['ATENDIDO_CON_ALCANCE', 'ATENDIDO_OBSERVADO', 'BORRADOR_COMPLETADO', 'EN_ABSOLUCION', 'EN_REVISION_POR_TERCEROS_Y_COES', 'EN_REVISION_POR_TERCEROS_COES', 'EN_VALIDACION', 'PENDIENTES', 'BORRADOR'],
        'No vigente': ['DESAPROBADO', 'NO_VIGENTE'],
        'Rechazado': ['RECHAZADO']
    }

    energy_source_mapping = {   ## Consider use by containing and not a starting with
        'Eólica': [],
        'Hidráulica': [],
        'Solar': [],
        'Térmica': []
    }

    generation_names_ = ['Eólico', 'Hidroeléctrico', 'Solar', 'Térmica']
    generation_names = {'Eólico': ['Eólico'], 'Hidráulica': ['Hidroeléctrico'], 'Solar': ['Solar'], 'Térmica': ['Térmica']}

    types_with_power = ['Demanda', 'Generación', 'No vigente']
    datetime_column = 'Fecha de Presentación'

    df = update_column(df, 'Estado', reassigned_state_names)

    df = assigning_maturity(df)

    df = assigning_energy_type_by_asset_name(df, 'Nombre', energy_source_mapping)

    df = assigning_energy_type_by_page_info(df, generation_names)

    df = update_column(df, 'Tipo', {'Generación': generation_names_})

    # Updating date format
    df[datetime_column] = df[datetime_column].str[8:10] + '/' + df[datetime_column].str[5:7] + '/' + df[datetime_column].str[:4]

    # Keep only one element in zone
    df['Zona de Proyecto'] = df['Zona de Proyecto'].str.partition(' / ')[0]

    df = formatting_power(df, types_with_power)

    return df

#--- Placeholder ------------------------------------------------------------------------
def assign_latest_reference(df: pd.DataFrame, name_col='Nombre del Estudio', date_col='Fecha de Presentación', threshold=0.805):
    # 1. Standardize dates to datetime objects
    df[date_col] = pd.to_datetime(df[date_col], format='%d/%m/%Y')
    
    # 2. Extract unique names to build similarity groups
    df_no_rejected = df['Estado'].str.contains('Rechazado')
    df_no_rejected = '' #Continue here
    unique_names = df[name_col].unique().tolist()
    groups = []
    visited = set()

    for i, s1 in enumerate(unique_names):
        if s1 in visited: continue
        current_group = [s1]
        visited.add(s1)
        for s2 in unique_names[i+1:]:
            if s2 not in visited and SequenceMatcher(None, str(s1), str(s2)).ratio() >= threshold:
                current_group.append(s2)
                visited.add(s2)
        groups.append(current_group)

    save_to_text(groups, threshold)
    # 3. Create 'Referencia' column based on the latest date in each group
    df['Referencia'] = None
    for group in groups:
        # Filter rows belonging to this similarity group
        group_rows = df[df[name_col].isin(group)]
        
        # Find the row with the max (latest) date
        # If multiple rows have the same max date, .iloc[0] takes the first one found
        latest_entry_name = group_rows.sort_values(by=date_col, ascending=False).iloc[0][name_col]
        
        # Assign this name as the reference for all members of the group
        df.loc[df[name_col].isin(group), 'Referencia'] = latest_entry_name
    
    return df

def save_to_text(groups, precision_from_data_process):
    """
    Saves the list of tuples to a text file with a clean visual hierarchy.
    """
    file_path = fr'output\similar\similar_{precision_from_data_process}_{datetime.now().strftime("%Y%m%d%H%M%S")}.txt'
    with open(file_path, "w", encoding='UTF-8') as f:
        f.write("SIMILARITY GROUPING REPORT\n" + "="*30 + "\n\n")
        for i, group in enumerate(groups, 1):
            f.write(f"GROUP {i}:\n")
            for item in group:
                f.write(f"  • {item}\n")
            f.write("-" * 20 + "\n")

#--- Main ------------------------------------------------------------------------
if __name__ == '__main__':

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

    write_df_in_excel({'last_data': updated_df}, f'final_output_{datetime.now().strftime("%Y%m%d%H%M%S")}')