import pandas as pd

def load_custom_excel(file_path: str, sheet: str, start_col: int) -> pd.DataFrame:
    df:pd.DataFrame = pd.read_excel(
        file_path, 
        sheet_name=sheet,
        usecols= start_col
    )

    # Delete the first row of data (index 0) and reset the index
    df = df.drop(df.index[0]).reset_index(drop=True)

    return df

# Excel datasheet name
ASSET = ''  

df_asset_P = load_custom_excel(fr'input\Data.xlsx', ASSET, 'D:F').dropna()
df_asset_P.to_parquet(fr'input\df_{ASSET}_P.parquet', engine='pyarrow', index=False)
df_asset_Q = load_custom_excel(fr'input\Data.xlsx', ASSET, 'G:I').dropna()
df_asset_Q.to_parquet(fr'input\df_{ASSET}_Q.parquet', engine='pyarrow', index=False)
df_asset_I2 = load_custom_excel(fr'input\Data.xlsx', ASSET, 'J:L').dropna()
df_asset_I2.to_parquet(fr'input\df_{ASSET}_I2.parquet', engine='pyarrow', index=False)
df_asset_U2 = load_custom_excel(fr'input\Data.xlsx', ASSET, 'M:O').dropna()
df_asset_U2.to_parquet(fr'input\df_{ASSET}_U2.parquet', engine='pyarrow', index=False)