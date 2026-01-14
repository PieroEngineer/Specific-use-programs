import calendar

import os

import requests

import pandas as pd

from datetime import datetime, date, timedelta

from typing import Tuple

from PIL import Image


def previous_day_date(day: int, month: int, year: int) -> Tuple[int, int, int]:
    """
    Return (day, month, year) for the calendar day before the given date.
    Raises ValueError if the input date is invalid.
    """
    d = date(year, month, day) - timedelta(days=1)
    return d.day, d.month, d.year

def image_to_ascii(image_path, output_width=100):
    """
    Converts an image to ASCII art.

    Args:
        image_path (str): The path to the input image file.
        output_width (int): The desired width of the ASCII art output.
                           The height will be scaled proportionally.

    Returns:
        str: The ASCII art representation of the image.
    """
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

def get_days_in_month(year: int, month: int) -> list[int]:
    if month < 1 or month > 12:
        raise ValueError("Month must be between 1 and 12.")
    
    num_days = calendar.monthrange(year, month)[1]
    return list(range(1, num_days + 1))

def get_excel_from_coes(month_i, year, day, save_directory):
    ##
    # year = 2025
    # month_i = 0
    # day = 10
    """
    Downloads a zip file from a given month and year and saves it to a specified directory.

    Args:
        url (str): The direct URL of the zip file.
        save_directory (str): The path to the directory where the file will be saved.
    """
    
    months = ['ENERO', 'FEBRERO', 'MARZO', 'ABRIL', 'MAYO', 'JUNIO', 'JULIO', 'AGOSTO', 'SETIEMBRE', 'OCTUBRE', 'NOVIEMBRE', 'DICIEMBRE']

    month_i_str = '0'+ f'{month_i+1}' if month_i < 9 else f'{month_i+1}'
    day_str = '0'+ f'{day}' if day < 9 else f'{day}'
    #        https://www.coes.org.pe/portal/browser/download?url=Post%20Operaci%C3%B3n%2FReportes%2FIDCOS%2F2025%2F07_JULIO%2FD%C3%ADa%2002%2FAnexo2_Resumen_operacion_20250702.xlsx
    url = fr'https://www.coes.org.pe/portal/browser/download?url=Post%20Operaci%C3%B3n%2FReportes%2FIDCOS%2F{year}%2F{month_i_str}_{months[month_i]}%2FD%C3%ADa%20{day_str}%2FAnexo2_Resumen_operacion_{year}{month_i_str}{day_str}.xlsx'
    #        https://www.coes.org.pe/portal/browser/download?url=Post%20Operaci%C3%B3n%2FReportes%2FIDCOS%2F 2025 %2F 07          _ JULIO          %2FD%C3%ADa%20 29  %2FAnexo2_Resumen_operacion_ 2025  07           29  .xlsx
    filename = f'Anexo2_Resumen_operacion_{year}{month_i_str}{day_str}.xlsx'

    try:
        # Create the full path for saving the file
        save_path = os.path.join(save_directory, filename)

        if not os.path.isfile(save_path):
            # Send a GET request to the URL
            response = requests.get(url, stream=True)
            response.raise_for_status()  # Raise an exception for bad status codes

            # Ensure the save directory exists
            os.makedirs(save_directory, exist_ok=True)

            # Write the content to the file in chunks to handle large files efficiently
            with open(save_path, 'wb') as f:
                f.write(response.content)

        return save_path

    except requests.exceptions.RequestException as e:
        print(f"Error downloading file: {e}")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")


if __name__ == '__main__':  
    print('👷‍♂️  Bienvenido Inge!! Este programa extraerá la data IDCOS (Anexo 2 del resumen de operación) desde COES 📚\n\n')
    # ascii_output = image_to_ascii(image_file, output_width=120)
    while 1:
        # print(ascii_output)
        year_accepted = False
        while not year_accepted:

            year = input('🔎  Ingresa el año: ')
            if not year.isdigit():
                print('     🧐  El año debe ser un entero positivo\n')
            else:
                year_accepted = True

        year = int(year)

        print('\n\n')

        month_accepted = False
        spanish_months = ['Enero', 'Febrero', 'Marzo', 'Abril', 'Mayo', 'Junio', 'Julio', 'Agosto', 'Setiembre', 'Octubre', 'Noviembre', 'Diciembre']
        while not month_accepted:

            for i, es_month in enumerate(spanish_months):
                print(f'{i+1}: {es_month}' )

            month = input('🔎  Escribe el número del mes que desees: ')
            if not month.isdigit():
                print('     🧐  El mes debe ser un entero positivo\n')
            elif int(month)>12 or not int(month):
                    print(f'     🧐   No hay un mes en la posición {month}\n')
            else:
                month_accepted = True

        month = int(month)

        print('\n\n')

        day_accepted = False
        available_days = get_days_in_month(year, month)
        while not day_accepted:

            print(f'Los días disponibles para {spanish_months[month-1]} son del 1 hasta el {available_days[-1]}\n')

            day = input('🔎  Escribe el número del día que desees: ')
            if not day.isdigit():
                print('     🧐  El mes debe ser un entero positivo\n')
            elif int(day)>available_days[-1] or not int(day):
                    print(f'     🧐  No hay un día en la posición {day}, solo entre 1 y  {available_days[-1]}\n')
            else:
                day_accepted = True

        day = int(day)

        print(f'\n🫡  Se escogió la data del {day} de {spanish_months[month-1]} del {year}\n\n 🙂‍↕️ Empezará la carga paso a paso, por favor espere...')

        # For month, one less (e.g. Januar is 0)
        save_path_1 = get_excel_from_coes(month-1, year, day, 'output')
        print(f'\n✅  Primera data extraida')

        prev_day, prev_month, prev_year = previous_day_date(day, month, year)
        save_path_2 = get_excel_from_coes(prev_month-1, prev_year, prev_day, 'output')
        print(f'\n✅  Segunda data extraida')

        try:
            df_1 = pd.read_excel(save_path_1, skiprows= 7, nrows = 48, engine='openpyxl')
            print(f'\n✅  Primera data registrada')
            df_2 = pd.read_excel(save_path_2, skiprows= 7, nrows = 48, engine='openpyxl')
            print(f'\n✅  Segunda data registrada')

            df_1 = df_1.iloc[:-1, :df_1.columns.get_loc('MW')]
            df_2 = df_2.iloc[:, :df_2.columns.get_loc('MW')]

            df_2 = df_2.iloc[[df_2.shape[0]-1]]

            df = pd.concat([df_2.reindex(columns=df_1.columns), df_1], ignore_index=True, copy=False)

            rows_to_change = [0]
            df.loc[rows_to_change, 'HORA'] = df.loc[rows_to_change, 'HORA'].apply(
            lambda x: x.time() if isinstance(x, datetime) else x
            )

            save_directory = f'output\\final\\Anexo2_Resumen_operacion_{year}-{month}-{day}.xlsx'
            df.to_excel(save_directory, index=False)

            print(f'\n✅  Se registró la nueva data')
        except Exception as e:
            print('🤕  Hubo un error en la extracción de la data, verificar si la data está disponible en línea con este link (CTRL + CLICK)')
            print('https://www.coes.org.pe/Portal/PostOperacion/Reportes/Idcos#')

            print(f'\nEl error encontrado fue "{str(e)}"\n')
