import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime
import shutil

from office365.sharepoint.client_context import ClientContext
from office365.runtime.auth.authentication_context import AuthenticationContext

from PyQt6.QtWidgets import QApplication, QFileDialog

import os
import io
import time
import sys
from colorama import Fore

#M ---------------- Acces to file from Sharepoint ----------------

def Write_filecontent_from_sharepoint(Token, site_url):
    """"This read the writer content and return a dataframe"""
    relative_path = f"Relative path"
    #print(f'\nIt searches in   --->    {relative_path}\n')
    ctx = ClientContext(site_url, Token)
    file = ctx.web.get_file_by_server_relative_url(relative_path)
    file_content = io.BytesIO()
    file.download(file_content)
    ctx.execute_query()
    file_content.seek(0)  # Reset the stream position
    
    return pd.read_excel(file_content, sheet_name=-1)

#M ---------------- Acces to Sharepoint ----------------

def Create_token_to_sharepoint(username, password):
    """"This verify in the credentials are correct"""
    site_url = "https://BusinessLink"
    ctx_auth = AuthenticationContext(site_url)
    ctx_auth.acquire_token_for_user(username, password)
    return ctx_auth

# ---------------- Loading Bar configuration ----------------

def loading_bar(current, total, color=Fore.GREEN):
    percent_int = int(100 * current / total)
    percent = 100 * current / total
    bar = '█' * (percent_int // 2) + '-' * ((100 - percent_int) // 2)
    sys.stdout.write(f"\r{color}[{bar}] {percent:.2f}% ({current} de {total})")
    sys.stdout.flush()

# ---------------- Calculation in context ----------------

def calculation_function(df):
    df["Pact"] = (df["Column1"] - df["Column2"]) * 0.004
    df["Prea"] = (df["Column3"] + df["Column4"] - df["Column5"] - df["Column6"]) * 0.004
    df["Ps"] = ((df["Pact"] ** 2 + df["Prea"] ** 2) ** 0.5)
    return df[[df.columns[0], 'Pact', 'Prea', 'Ps']]

# ---------------- Call Some folder manually ----------------

def select_folder(mssg_to_user):
    app = QApplication([])
    source_folder = QFileDialog.getExistingDirectory(
        None,
        mssg_to_user
    )
    return source_folder

# ---------------- Map all folders and find Excel/CSV files ----------------

def map_folders_in_local(base_path):
    excel_files = []
    for root, dirs, files in os.walk(base_path):
        for file in files:
            if file.endswith(('.csv', '.xls', '.xlsx')):
                excel_files.append(os.path.join(root, file))
    return excel_files

# ---------------- Process a single Excel file in local computer----------------

def bring_from_sharepoint(file_path, token_auth):
    site_url = "https://BusinessLink"
    ctx = ClientContext(site_url, token_auth)
    file = ctx.web.get_file_by_server_relative_url(file_path)
    file_content = io.BytesIO()
    file.download(file_content)
    ctx.execute_query()
    file_content.seek(0)  # Reset the stream position

    if file_path.endswith('.csv'):
        df = pd.read_csv(file_content, sep=';')
    else:
        df = pd.read_excel(file_content)##, engine='openpyxl')
    return calculation_function(df)
    
# ---------------- Process a single Excel file in Sharepoint----------------

def map_sharepoint_excel_files(ctx_auth: ClientContext) -> list:
    excel_files = []

    def walk_folder(folder_url, ctx):
        folder = ctx.web.get_folder_by_server_relative_url(folder_url)
        folders = folder.folders
        files = folder.files
        ctx.load(folders)
        ctx.load(files)
        ctx.execute_query()

        # Filter Excel files
        for f in files:
            if f.name.endswith(('.csv', '.xls', '.xlsx')):
                excel_files.append((f.name, f.serverRelativeUrl))

        # Recurse into subfolders
        for subfolder in folders:
            walk_folder(subfolder.serverRelativeUrl)

    root_folder_url = f'Plan/root_folder_url/'
    ctx_ = ClientContext(root_folder_url, ctx_auth)
    walk_folder(root_folder_url, ctx_)
    return excel_files


# ---------------- Plot and save charts ----------------

def generate_and_save_line_charts(df, base_filename, output_path):
    x = pd.to_datetime(df.iloc[:, 0])  # First column as datetime

    # Define mapping from y_label to folder names
    folder_map = {
        'Pact': 'Potencia activa',
        'Prea': 'Potencia reactiva',
        'Ps': 'Potencia aparente'
    }

    for i in range(1, 4):
        y = df.iloc[:, i]
        y_label = df.columns[i]

        # Map y_label to folder
        folder_name = folder_map.get(y_label)
        if not folder_name:
            continue  # Skip unknown labels

        # Create folder if it doesn't exist
        full_folder_path = os.path.join(output_path, folder_name)
        os.makedirs(full_folder_path, exist_ok=True)

        # Create the plot
        plt.figure(figsize=(18, 5))
        plt.plot(x, y, marker='o', linestyle='-', linewidth=0.3)
        plt.xticks(rotation=60, ha='left')
        plt.xlabel(df.columns[0])
        plt.ylabel(y_label)
        plt.title(f"{y_label} over {df.columns[0]}")
        plt.grid(True)
        plt.tight_layout()

        # Save in respective folder
        filename = f"{base_filename}_{y_label}.png"
        filepath = os.path.join(full_folder_path, filename)
        plt.savefig(filepath)

        plt.close()


# ---------------- Main program ----------------

def main():
    mail = 'mail'
    password = 'password'

    errors = []

    from_local = True

    if from_local:
        base_path = select_folder('📂 SELECCIONA FOLDER DE ENTRADA')
        files = map_folders_in_local(base_path)

        print(f"🔍 Found {len(files)} Excel/CSV files.\n")

        output_folder = select_folder('📂 SELECCIONA FOLDER DE DONDE SE GUARDARÁ')
        os.makedirs(output_folder, exist_ok=True)

        amount = len(files)
        er = 0
        for i, path in enumerate(files):
            try:
                loading_bar(i, len(files), color=Fore.CYAN)

                name = os.path.splitext(os.path.basename(path))[0]
                df = pd.read_excel(path) if path.endswith(('.xls', '.xlsx')) else pd.read_csv(path, sep=';')
                if df is not None:
                    df = calculation_function(df)
                    generate_and_save_line_charts(df, name, output_folder)

            except Exception as e:
                print(f"\n❌ Error al intentar graficar {path}: \n{e}\n")
                errors.append(name)
                er += 1
                pass
        loading_bar(amount, amount, color=Fore.CYAN)

    else:
        token_auth = Create_token_to_sharepoint(mail, password)

        output_folder = select_folder('📂 SELECCIONA FOLDER DE DONDE SE GUARDARÁ')
        os.makedirs(output_folder, exist_ok=True)

        name_address_files = map_sharepoint_excel_files(token_auth)

        print(f"🔍 Found {len(name_address_files)} Excel/CSV files.\n")

        cntg = 0
        amount = len(name_address_files)
        for name, address in name_address_files:
            try:
                loading_bar(cntg, amount, color=Fore.GREEN)
                cntg += 1
                df = bring_from_sharepoint(address[35:], token_auth)
                if df is not None:
                    generate_and_save_line_charts(df, name[:-4], output_folder)
            except Exception as e:
                print(f"\n❌ Error al intentar traer/graficar a {name[:-4]}: \n{e}\n")
                pass
    print(f'\n\nEl {100 - (100*er/amount)}% de los archivos fueron graficados con éxito ({er} fallidos)')
    if er != 0:
        print('Hubo error para las siguientes subestaciones: \n')
        for err in errors:
            print(err)

# ---------------- Entry Point ----------------

if __name__ == "__main__":
    main()


