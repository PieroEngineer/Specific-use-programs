import pandas as pd
def excel_to_parquet(excel_file_path, parquet_file_path):
        """
        Converts an Excel file to a Parquet file.

        Args:
            excel_file_path (str): The path to the input Excel file (.xlsx or .xls).
            parquet_file_path (str): The path to the output Parquet file.
            sheet_name (str or int, optional): The name or index of the Excel sheet to read.
                                                 Defaults to 0 (the first sheet).
        """
        # try:
        # Read the Excel file into a pandas DataFrame
        df = pd.read_excel(excel_file_path, engine='openpyxl')

        df['Nombre Señal'] = df['Nombre Señal'].astype(str)

        df.to_parquet(parquet_file_path, index=False) # index=False prevents writing the DataFrame index to Parquet
        print(f"Successfully converted '{excel_file_path}' to '{parquet_file_path}'")

if __name__ == "__main__":
    # Example usage:
    excel_file_path = "input/ultimos_por_nombre.xlsx"
    output_parquet = "input/nominations.parquet"

    df_in = pd.read_parquet("input/nominations.parquet")
    print(df_in.columns)
    print(df_in.shape)
    #excel_to_parquet(excel_file_path, output_parquet)