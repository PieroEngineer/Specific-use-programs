import pandas as pd

from generating_parquet import ASSET

#--- Complementary functions ---------
def elements_not_in_other_df(df1, col1, df2, col2):
    # Use isin() to create a boolean mask: True if the element IS in df2[col2]
    mask = df1[col1].isin(df2[col2])
    
    # Select elements where the mask is False (i.e., NOT in df2[col2])
    # Use .unique() to get only unique values, and .tolist() to convert to a list
    elements_only_in_df1 = df1[col1][~mask].unique().tolist()
    
    return elements_only_in_df1

#--- Main function ---------
def generate_dataframe_with_times(other_columns: list[str], start_str: str, end_str: str, freq: str = "15min") -> pd.DataFrame:
    try:
        start_dt = pd.to_datetime(start_str, format='%d-%m-%Y %H:%M:%S')
        end_dt = pd.to_datetime(end_str, format='%d-%m-%Y %H:%M:%S')

        time_series = pd.date_range(start=start_dt, end=end_dt, freq=freq)

        # Creating the DataFrame (or you can assign this series to an existing one)
        df = pd.DataFrame({"timestamp": time_series} | {column_name:None for column_name in other_columns})
        
        return df

    except Exception as e:
        print(f"Error processing dates: {e}")
        return pd.DataFrame()

def load_custom_excel(file_path: str, sheet: str, start_col: int) -> pd.DataFrame:
    df:pd.DataFrame = pd.read_excel(
        file_path, 
        sheet_name=sheet,
        usecols= start_col
    )

    # Delete the first row of data (index 0) and reset the index
    df = df.drop(df.index[0]).reset_index(drop=True)

    return df

def resample_custom_intervals(df: pd.DataFrame, time_col: str, value_col: str, start_time_str: str) -> pd.DataFrame:
    """
    Groups data into 15-min intervals starting from a specific reference time.
    Returns mean values indexed by the END of each interval.
    """
    # 1. Ensure time column is datetime type
    df[time_col] = pd.to_datetime(df[time_col], format='%d-%m-%Y %H:%M:%S')
    start_time = pd.to_datetime(start_time_str, format='%d-%m-%Y %H:%M:%S')
    
    # 2. Filter data to only include records after or equal to starting_time
    # This prevents historical data from affecting the first group
    df_filtered = df[df[time_col] >= start_time].copy()

    # 3. Create the 'bins'. 
    # We calculate the number of 15-min minutes passed since start_time.
    # Formula: (CurrentTime - StartTime) // 15min
    delta = (df_filtered[time_col] - start_time).dt.total_seconds()
    df_filtered['group_idx'] = (delta // (15 * 60)).astype(int)

    # 4. Group by the index and calculate the mean
    grouped = df_filtered.groupby('group_idx')[value_col].median().reset_index()

    # 5. Map the group_idx back to the "End Time" of the interval
    # StartTime + (group_idx + 1) * 15min
    grouped['timestamp'] = grouped['group_idx'].apply(
        lambda x: start_time + pd.Timedelta(minutes=(x + 1) * 15)
    )

    # Return only the requested columns
    return grouped[['timestamp', value_col]]

if __name__ == '__main__':
    #--- Create output base ---------

    # Fill column names
    columns_in_context = ['', '', '', '', '', '', '']
    start_time = "01-10-2025 00:00:00"

    #--- Process data ---------

    # Import data
    asset = ASSET
    measurements = {'P': 'P/0.004', 'Q': 'Q/0.004', 'I2': 'I2', 'U2': 'U2'}

    compressed_df_assets = []
    for measurement, multiply in measurements.items(): 

        df_asset = pd.read_parquet(fr'input\df_{asset}_{measurement}.parquet', engine='pyarrow')
        compressed_df_asset = resample_custom_intervals(df_asset, f'{measurement} Time', measurements[measurement], start_time).set_index('timestamp')

        compressed_df_assets.append(compressed_df_asset)

    #--- Fill data Kwh del and rec in output ---------
    df_asset_compressed: pd.DataFrame = pd.concat(compressed_df_assets, axis = 1)
    df_asset_compressed.fillna(0)
    df_asset_compressed.to_excel(fr'output\testing\df_asset_compressed_{asset}.xlsx', index=False)
    print(f'🔎  df_asset_compressed:\n{df_asset_compressed}\n\n')

    p_ = measurements['P']
    q_ = measurements['Q']
    u2_ = measurements['U2']
    i2_ = measurements['I2']

    new_data_content = []
    for index, row in df_asset_compressed.iterrows():

        # Pre-stablished values
        q_values = {'kVARh Q1 int': 0, 'kVARh Q2 int': 0, 'kVARh Q3 int': 0, 'kVARh Q4 int': 0}
        kwh_values = {'kWh del int': 0, 'kWh rec int': 0}

        # Logic for fundamental values
        fundamental_values = {'Voltaje': row[u2_], 'Corriente': row[i2_]}

        # Logic for Q# values
        if (row[p_]>0) and (row[q_]>0):
            q_values['kVARh Q1 int'] = abs(row[q_])
        elif (row[p_]<0) and (row[q_]>0):
            q_values['kVARh Q2 int'] = abs(row[q_])
        elif (row[p_]<0) and (row[q_]<0):
            q_values['kVARh Q3 int'] = abs(row[q_])
        elif (row[p_]>0) and (row[q_]<0):
            q_values['kVARh Q4 int'] = abs(row[q_])
        else:
            print(f'🚧  For {asset} in {index}\nP: {row[p_]} | Q: {row[q_]}\n')
            
        # Logic for Del and Rec values
        if row[p_]>0:
            kwh_values['kWh del int'] = abs(row[p_])
        elif row[p_]<0:
            kwh_values['kWh rec int'] = abs(row[p_])

        new_data_content.append({'Local Time': index} | q_values | kwh_values | fundamental_values)
    output_df = pd.DataFrame(new_data_content)

    #--- Save output in excel ---------
    output_df.to_excel(fr'output\final_data_{asset}.xlsx', index=False)
    print(f'🔎  output_df:\n{output_df}\n\n')