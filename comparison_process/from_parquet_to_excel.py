import pandas as pd

def parquet_to_excel(parquet_file, excel_file):
    """
    Converts a Parquet file to an Excel file using pandas.
    
    Args:
        parquet_file (str): The path to the input .parquet file.
        excel_file (str): The path to the output .xlsx file.
    """
    try:
        # Read the Parquet file into a pandas DataFrame
        df = pd.read_parquet(parquet_file)

        df['timestamp_datetime'] = pd.to_datetime(df['timestamp_ms'], unit='ms')
        
        # Write the DataFrame to an Excel file
        # index=False prevents writing the DataFrame index as a column in Excel
        df.to_excel(excel_file, index=False, engine='openpyxl')
        
        print(f"Successfully converted '{parquet_file}' to '{excel_file}'")
    except Exception as e:
        print(f"An error occurred: {e}")

# Example Usage:
# input_parquet = r'input\data_train\L_2218_R\df_den_train.parquet'
input_parquet = r'input\data_train\L_2219_R\df_temp_train.parquet'
output_excel = r'output\t3.xlsx'
parquet_to_excel(input_parquet, output_excel)
