from selenium import webdriver 
from selenium.webdriver.common.by import By 
from selenium.webdriver.support.ui import Select
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC  


import unicodedata

import pandas as pd

import numpy as np

import re

from PIL import Image

import os 
import time
from datetime import datetime

#--Complementary--------------------------------------------------------

def remove_tildes(text: str) -> str:
    """
    Remove accent marks (tildes) from vowels in the given string.
    Works for Spanish and other Latin-based languages.
    """
    pattern = r"[áéíóúÁÉÍÓÚ]"
    if not bool(re.search(pattern, text)):
        # Normalize to NFD (decompose characters into base + diacritic)
        normalized = unicodedata.normalize('NFD', text)
        # Filter out diacritic marks (category 'Mn')
        without_tildes = ''.join(ch for ch in normalized if unicodedata.category(ch) != 'Mn')
        return without_tildes

def print_repeated_strings(df: pd.DataFrame, column: str) -> None:
    """
    Prints how many unique strings in the specified column are repeated,
    and lists which strings those are (with their counts).

    Assumes the column contains only strings (may include NaNs).
    """
    if column not in df.columns:
        raise KeyError(f"Column '{column}' not found in DataFrame.")

    # Drop NaNs just in case; keep exact string matching (case- and space-sensitive)
    counts = df[column].dropna().value_counts()

    # Keep only strings that appear more than once
    repeated = counts[counts > 1]

    print(f"{len(repeated)} unique strings are repeated in '{column}'.")
    if not repeated.empty:
        print("Repeated strings (with counts):")
        for value, cnt in repeated.items():
            print(f"  - {value}: {cnt}")

def image_to_ascii(output_width=100):
    """
    Converts an image to ASCII art.

    Args:
        image_path (str): The path to the input image file.
        output_width (int): The desired width of the ASCII art output.
                           The height will be scaled proportionally.

    Returns:
        str: The ASCII art representation of the image.
    """

    image_path = r'resources\logo-2.jpg'

    # Define ASCII characters for different brightness levels
    ASCII_CHARS = "@%#*+=-:. "

    try:
        img = Image.open(image_path)
    except FileNotFoundError:
        return "Error: Image file not found."
    except Exception as e:
        return f"Error opening image: {e}"

    # Convert to grayscale
    img = img.convert("L")

    # Resize the image to fit the desired output width
    width, height = img.size
    aspect_ratio = height / width
    output_height = int(output_width * aspect_ratio * 0.55) # Adjust for character aspect ratio
    img = img.resize((output_width, output_height))

    # Get pixel data
    pixels = img.getdata()

    # Map pixel brightness to ASCII characters
    ascii_art = ""
    for pixel_value in pixels:
        # Scale pixel value (0-255) to the range of ASCII_CHARS
        index = int((pixel_value / 255) * (len(ASCII_CHARS) - 1))
        ascii_art += ASCII_CHARS[index]

    # Format into lines
    formatted_ascii_art = ""
    for i in range(0, len(ascii_art), output_width):
        formatted_ascii_art += ascii_art[i:i + output_width] + "\n"

    return formatted_ascii_art

#--Data functions--------------------------------------------------------

# Save Excel files to 'output' folder in the current directory.
def get_specific_data_from_coes(is_eo, project_type):
    """
    Downloads an Excel file from the COES page by selecting a project type and clicking buttons.
    Args:
        url (str): Page URL
        project_type (str): Combobox option (e.g., 'Generación Convencional')
        output_path (str): Folder for downloads (default: 'output')
    """
    output_path = os.path.join('output\Medium', "EO" if is_eo else "EPO", project_type)
    file_path = os.path.join(output_path, f'Consulta_Web_E{"" if is_eo else "P"}O.xlsx')
    
    if os.path.exists(file_path):
        os.remove(file_path)
        print(f"File deleted: {file_path}")
    else:
        print(f"File not found: {file_path}")

    
    print(f'Accessing to data {"EO" if is_eo else "EPO"} to "{project_type}"\n')
    download_path = os.path.join(os.getcwd(), output_path)
    if not os.path.exists(download_path):
        os.makedirs(download_path)
    print(f"\n✅  Downloads will be saved to: {download_path}")

    # Step 3: Configure Chrome options for automatic downloads
    # Set download path and disable save-as dialog.
    options = webdriver.ChromeOptions()
    options.add_argument('--headless')  # Run headless for efficiency
    # Remove '--headless' to debug visually if errors occur
    options.add_experimental_option(
        "prefs",
        {
            "download.default_directory": download_path,
            "download.prompt_for_download": False,
            "download.directory_upgrade": True,
            "safebrowsing.enabled": True
        }
    )

    # Step 4: Initialize WebDriver
    # Launch Chrome with configured options.
    chromedriver_path = r"google_driver/chromedriver-win64/chromedriver.exe"
    try:
        #Xdriver = webdriver.Chrome(options=options)
        #Xdriver = webdriver.Chrome(executable_path=chromedriver_path, options=options)
        service = Service(chromedriver_path)
        driver = webdriver.Chrome(service=service, options=options)
        ##print("\n✅ Browser initialized.")
    except Exception as e:
        print(f"\n‼️  Error initializing browser: {e}")
        raise

    url = fr"https://www.coes.org.pe/Portal/Planificacion/NuevosProyectos/Consultawebe{"" if is_eo else "p"}o"
    print(f'✅  Looking in {url}\n')

    try:
        # Step 5: Navigate to the page
        driver.get(url)
        ##print("\n✅ Page loaded.")

        # Step 6: Select option from combobox
        # Use Select class to handle <select id="cboTipoProyecto">.
        try:
            combobox = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.ID, 'cboTipoProyecto'))
            )
            select = Select(combobox)
            select.select_by_visible_text(project_type)  # Select option (e.g., 'Generación Convencional')
            print(f"\n✅  Selected project type: {project_type}")
        except Exception as e:
            print(f"\n‼️  Error selecting combobox option: {e}")
            with open("page_source.html", "w", encoding="utf-8") as f:
                f.write(driver.page_source)
            ##print("\n✅ Saved page source to page_source.html for debugging.")
            raise

        # Step 7: Click the "Buscar" button
        # Wait for button to be clickable and handle the ~5-second loading animation.
        try:
            buscar_button = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((By.ID, 'btnBuscar'))
            )
            driver.execute_script("arguments[0].scrollIntoView(true);", buscar_button)
            time.sleep(0.5)  # Brief pause for scroll
            if buscar_button.is_displayed() and buscar_button.is_enabled():
                buscar_button.click()
                ##print("\n✅ Buscar button clicked.")
            else:
                print("\n‼️  Buscar button not visible or enabled.")
                raise Exception("Buscar button not interactable")

            ## Maybe this part isn't necessary or should be changed by a wait
            # Wait for loading animation (~5 seconds) to disappear
            # *** Placeholder: Replace with actual spinner class/ID if known ***
            try:
                WebDriverWait(driver, 10).until(
                    EC.invisibility_of_element((By.CLASS_NAME, 'spinner'))  # Adjust with actual selector
                )
                ##print("\n✅ Loading animation gone.")
            except:
                print("\n⚠️  No spinner detected or timeout.")

        except Exception as e:
            print(f"\n‼️  Error clicking Buscar button: {e}")
            with open("page_source.html", "w", encoding="utf-8") as f:
                f.write(driver.page_source)
            print("\n✅ Saved page source to page_source.html.")
            raise

        # Step 8: Click the "Exportar" button
        # Retry up to 3 times to handle dynamic issues.
        max_attempts = 3
        for attempt in range(max_attempts):
            try:
                exportar_button = WebDriverWait(driver, 10).until(
                    EC.element_to_be_clickable((By.ID, 'btnExportar'))
                )
                driver.execute_script("arguments[0].scrollIntoView(true);", exportar_button)
                time.sleep(0.5)  # Brief pause for scroll
                if exportar_button.is_displayed() and exportar_button.is_enabled():
                    try:
                        exportar_button.click()
                        ##print("\n✅ Exportar button clicked.")
                        break
                    except Exception as e:
                        print("\n⚠️   Normal click failed (attempt {attempt + 1}): {e}. Trying JavaScript click.")
                        driver.execute_script("arguments[0].click();", exportar_button)
                        print("\n✅ JavaScript click executed.")
                        break
                else:
                    print("\n‼️  Exportar button not visible or enabled.")
                    raise Exception("Exportar button not interactable")
            except Exception as e:
                print("\n⚠️   Attempt {attempt + 1} failed: {e}")
                if attempt == max_attempts - 1:
                    print("\n‼️  Max attempts reached for Exportar button.")
                    with open("page_source.html", "w", encoding="utf-8") as f:
                        f.write(driver.page_source)
                    print("\n✅ Saved page source to page_source.html.")
                    raise
                time.sleep(1)  # Wait before retry

        # Step 9: Wait for the Excel file to download
        timeout = 30 # Max wait time
        start_time = time.time()
        downloaded = False
        while time.time() - start_time < timeout:
            files = [f for f in os.listdir(download_path) if f.endswith(f'{"EO" if is_eo else "PO"}.xlsx')]
            if files:
                ##print(f"\n✅  Downloaded Excel file: {files[0]}")
                print(f"\n✅  Current files {os.listdir(download_path)}\n")
                downloaded = True
                break
            time.sleep(1)
        if not downloaded:
            print("\n‼️  Download failed or timed out.")

        # Step 10: Save current data in a dataframe
        
        df_out = pd.read_excel(file_path, sheet_name= f'Consulta_Web_E{"" if is_eo else "P"}O',engine= 'openpyxl', header=0, skiprows=3)
        df_out['Tipo'] = project_type if not project_type[:10] == 'Generación' else 'Generación'

    finally:
        # Step 11: Clean up
        driver.quit()
        print("\n✅ Browser closed.")

    return df_out

# Web scrapping function
def get_full_data_from_coes(url, output_path = "output"):
    download_path = os.path.join(os.getcwd(), output_path)  # Creates 'output' folder in current directory
    if not os.path.exists(download_path):
        os.makedirs(download_path)  # Create folder if it doesn’t exist
    print(f"Downloads will be saved to: {download_path}")

    # Configure Chrome options for automatic downloads
    options = webdriver.ChromeOptions()
    options.add_argument('--headless')  # Run headless for efficiency
    options.add_experimental_option(
        "prefs",
        {
            "download.default_directory": download_path, 
            "download.prompt_for_download": False,
            "download.directory_upgrade": True,
            "safebrowsing.enabled": True 
        }
    )

    # Initialize WebDriver
    try:
        driver = webdriver.Chrome(options=options)
        print("Browser initialized.")  
    except Exception as e:
        print(f"Error initializing browser: {e}")
        exit()
    
    try:
        driver.get(url)
        print("Page loaded.")  
    except Exception as e:
        print(f"Error loading page: {e}")
        driver.quit()
        exit()

    # Find and click the download button
    try:

        # Find the button with id="btnExportar"
        button = WebDriverWait(driver, 5).until(
            EC.element_to_be_clickable((By.ID, 'btnExportar'))
        )
        print("Download button (btnExportar) found and clickable.")
        # Scroll to the button to ensure it’s in view
        driver.execute_script("arguments[0].scrollIntoView(true);", button)
        print("Scrolled to button.")
        time.sleep(0.5)  # Brief pause to ensure scroll completes

        # Check button state before clicking
        if button.is_displayed() and button.is_enabled():
            try:
                button.click()  # Attempt normal click
                print("Download button clicked.")  
            except Exception as e:
                print(f"Normal click failed: {e}. Trying JavaScript click.")  
                # Fallback: Use JavaScript to click, bypassing UI issues
                driver.execute_script("arguments[0].click();", button)
                print("JavaScript click executed.")  
        else:
            print("Button is not visible or enabled.")
            driver.quit()
            exit()

    except Exception as e:
        print(f"Error finding/clicking button: {e}")  # Handle errors
        with open("page_source.html", "w", encoding="utf-8") as f:
            f.write(driver.page_source)
        print("Saved page source to page_source.html for debugging.")
        driver.quit()
        exit()

    # Wait for the Excel file to download
    timeout = 30  # Max wait time for download
    start_time = time.time()
    downloaded = False
    while time.time() - start_time < timeout:
        files = [f for f in os.listdir(download_path) if f.endswith('.xlsx')]  # Look for .xlsx files
        if files:
            print(f"Downloaded Excel file: {files[0]}")
            downloaded = True
            break
        time.sleep(1)  # Check every second
    if not downloaded:
        print("Download failed or timed out.")  

    # Step 7: Clean up
    driver.quit()
    print("Browser closed.")



# Order extracted data
def order_data(df_in, base_excel_path): # Main modification 
    
    # Get data
    df_out = pd.read_excel(base_excel_path, engine='openpyxl', header=0, usecols=list(range(17)))

    print(f'df_out size: {df_in.shape}\n')
    print(f'df_out["Tipo"]:\n{df_in["Tipo"].head(30)}\n')
    print(f'df_out:\n{df_in}\n')

    # Copy DataFrames to avoid modifying originals
    df_in = df_in.copy()
    df_out = df_out.copy()
    
    # Clean 'Nombre del Estudio' in df_in by removing trailing parentheses
    df_in['Nombre del Estudio'] = df_in['Nombre del Estudio'].str.replace(r'\s*\([^)]*\)$', '', regex=True)

    get_year = lambda y: True if (y.split('-')[0]=="EPO" and int(y.split('-')[1])>=2018) or (y.split('-')[0]=="EO" and int(y.split('-')[1])>=2022) else False

    ##def get_year(y_str)

    df_in['extra'] = df_in['Código de Estudio'].apply(get_year)
    df_in = df_in[df_in['extra'] == True]

    df_in.drop('extra', axis=1, inplace=True)

    df_in = df_in.rename(columns = {'Zona de Proyecto' :'Zona'})

    # Set 'Código de Estudio' as index for both DataFrames
    df_in.set_index("Código de Estudio", inplace=True)
    df_out.set_index("Código de Estudio", inplace=True)

    # Modify create "Estado" from excel logic
    # Update 'Estado' column based on formula logic using 'Estado' and 'Vigencia'
    condition1 = df_in['Estado'] == 'En Revisión'
    condition2 = (df_in['Estado'] == 'No Vigente') | (df_in['Vigencia'] == 'No Vigente')
    condition3 = df_in['Estado'] == 'Con Conformidad'
    condition4 = df_in['Vigencia'] == 'Vigente'
    
    df_in['Estado'] = np.where(condition1, 'En Revisión',
                               np.where(condition2, 'No Vigente',
                                        np.where(condition3,
                                                 np.where(condition4, 'Aprobado', 'Rechazado'),
                                                 'Rechazado')))
    
    #--Update 'Nombre del Estudio' for common keys
    common_codes = df_in.index.intersection(df_out.index)
    if not common_codes.empty:
        df_out.loc[common_codes, 'Nombre del Estudio'] = df_in.loc[common_codes, 'Nombre del Estudio']
        df_out.loc[common_codes, 'Estado'] = df_in.loc[common_codes, 'Estado']
    
    #--Identify new keys in df_in not in df_out
    new_codes = df_in.index.difference(df_out.index)
    if not new_codes.empty:
        # Create new rows with NaN values
        new_df = pd.DataFrame(index=new_codes, columns=df_out.columns)
        
        # Columns to fill from df_in for new rows
        cols_to_fill = [
            "Nombre del Estudio", "Fecha de Presentación", "Fecha de Conformidad",
            "Punto de Conexión", "Año de puesta de servicio", "Comentarios",
            "Tercero Involucrado", "Zona", "Estado", "Tipo" # Tipo was already fixed before
        ]
        
        # Fill specified columns
        new_df[cols_to_fill] = df_in.loc[new_codes, cols_to_fill]
        # Including exception
        new_df['Titular del proyecto'] = df_in.loc[new_codes, 'Gestor del Proyecto']
        
        #X Set 'Tipos' and 'Tipo de Energía' for new rows based on 'Nombre del Estudio'  ## Here I could connect "Tipos de energía"
        #X Now depends of the input data
        # new_df['Tipos'] = new_df['Nombre del Estudio'].apply(
        #     lambda x: 'Generación' if x.startswith(('C.S.F.', 'C.H.', 'C.T.', 'C.E.')) else '' 
        # )
        new_df['Tipo de Energía'] = new_df['Nombre del Estudio'].apply( # This is still like this
            lambda x: 'Solar' if x.startswith('C.S.F.') else
                      'Hidráulica' if x.startswith('C.H.') else
                      'Térmica' if x.startswith('C.T.') else
                      'Eólica' if x.startswith('C.E.') else ''
        )

        # 
        new_df.loc[new_codes, 'Fecha de Conformidad'] = np.where(df_in.loc[new_codes, 'Estado'] == 'Aprobado', df_in.loc[new_codes, 'Fecha de Conformidad'], '')
        
        # Concatenate new rows to df_out
        df_out = pd.concat([df_out, new_df])

        #--

    #--Update all power values

    file_path = 'input/Potencias.xlsx'
    df_potencias = pd.read_excel(file_path, header=0)

    for i, central in enumerate(df_potencias['Centrales']):
        # Build elementwise mask (note the & and the parentheses)
        mask = (
            (df_out['Potencia(MW)'] != '0.0 MW') &
            (df_out['Tipo'].eq('Generación')) &
            (df_out['Estado'].eq('Aprobado') | df_out['Estado'].eq('En Revisión')) &
            (df_out['Nombre del Estudio']
                .str.contains(remove_tildes(central), na=False, regex=False))
        )

        # Get the value from df_potencias row i (use .loc or .at; .iat is position-only)
        potencia = df_potencias.loc[i, 'Potencia Instalada (MW)']  # or: df_potencias.at[i, 'Potencia Instalada (MW)']

        # Assign only where mask is True
        df_out.loc[mask, 'Potencia(MW)'] = f'{potencia} MW'

    # Reset index to restore 'Código de Estudio' as a column
    df_out.reset_index(inplace=True)

    return df_out
    

#--Main--------------------------------------------------------
if __name__ == '__main__':
    
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
    final_df = order_data(df_new, r'input\Consulta_Web_EPO_EO_Cambio_J.xlsx')

    final_df.to_excel(r"output\t20.xlsx", index=False)
    ##final_df.to_excel(fr"output\Consulta_Web_EPO_EO_Cambio_{datetime.now()}.xlsx", index=False)

    
