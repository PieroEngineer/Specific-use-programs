import pandas as pd
import os
import glob

def process_train_data(base_path, subfolders, output_file):
    """
    Processes subfolders to extract 'densidad' and 'temperatura' columns 
    from 'train' parquet files and saves them to an Excel file.
    """
    all_folder_dfs = []

    for subfolder in subfolders:
        folder_path = os.path.join(base_path, subfolder)
        
        # Search for parquet files containing "train" in their name
        search_pattern = os.path.join(folder_path, "*train*.parquet")
        parquet_files = glob.glob(search_pattern)
        
        densidad_col = None
        temperatura_col = None
        
        for file in parquet_files:
            try:
                # Load the parquet file
                df = pd.read_parquet(file)
                df['timestamp_datetime'] = pd.to_datetime(df['timestamp_ms'], unit='ms')
                
                # Take 'densidad' if we haven't found it yet in this subfolder
                if densidad_col is None and "densidad" in df.columns:
                    densidad_col = df["densidad"].reset_index(drop=True)

                # Take 'temperatura' if we haven't found it yet in this subfolder
                if temperatura_col is None and "temperatura" in df.columns:
                    temperatura_col = df["temperatura"].reset_index(drop=True)
                
                # If both are found, stop checking other files in this subfolder
                if densidad_col is not None and temperatura_col is not None:
                    break
            except Exception as e:
                print(f"Error reading {file}: {e}")

        # If data was found, rename and prepare for concatenation
        if densidad_col is not None or temperatura_col is not None:
            folder_data = pd.DataFrame()
            if densidad_col is not None:
                folder_data[f"densidad_{subfolder}"] = densidad_col
            if temperatura_col is not None:
                folder_data[f"temperatura_{subfolder}"] = temperatura_col
            
            folder_data.index = df['timestamp_datetime']

            all_folder_dfs.append(folder_data)

    if all_folder_dfs:
        # Concatenate all folder results horizontally
        final_dataframe = pd.concat(all_folder_dfs, axis=1)
        # print(f'df index:\n{final_dataframe.index}\n')
        # print(f'df:\n{final_dataframe.columns}\n')
        # print(f'df:\n{final_dataframe}\n')

        # Save to Excel
        final_dataframe.to_excel(output_file)
        print(f"Success! Data saved to {output_file}")
        return final_dataframe
    else:
        print("No matching data found in the specified folders.")
        return None

# --- Example Usage ---
sensor_names = ["", "", "", "", "", "", "", "", "", "", "", "", ""]
input_path = r'input\data_train'
ouput_file_path = r"output\imported measures 2.xlsx"
process_train_data(input_path, sensor_names, ouput_file_path)
