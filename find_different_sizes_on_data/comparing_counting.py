import pandas as pd

import json

def get_routes_from_df(df: pd.DataFrame):
    # Get the name of the first column
    first_column_name = df.columns[0]

    # Convert the first column to a list
    first_column_list = []
    for nom in df[first_column_name].tolist():
        if nom:
            first_column_list.append(nom.replace("\\\\server_name\\", ""))
        else:
            break

    #first_column_list = [s.replace("\\\\server_name\\", "") if s else s for s in df[first_column_name].tolist()]

    # Remove the first column from the DataFrame
    df = df.drop(columns=[first_column_name])

    return first_column_list, df

def count_non_empty_elements(dataframe: pd.DataFrame):
    """
    Counts the number of non-empty elements in each column of a Pandas DataFrame
    and returns the results in a dictionary.

    Args:
        dataframe (pd.DataFrame): The input DataFrame.

    Returns:
        dict: A dictionary where keys are column names and values are the
              count of non-empty elements in that column.
    """
    non_empty_counts = {}
    for col in dataframe.columns:
        # The .count() method in Pandas directly counts non-NaN values
        non_empty_counts[col] = int(dataframe[col].count())
    return non_empty_counts

def get_total_data_and_counting(subdata_sheets):
    counting_dict = {}
    general_df = pd.DataFrame()

    for subdata_sheet in subdata_sheets:
        # Import data
        current_path_file = fr'input\new\{subdata_sheet}.parquet'
        _current_df = pd.read_parquet(current_path_file)

        # Remove the first column of parquets and put it in a list (Remove "\\server_name\")
        nominations, current_df = get_routes_from_df(_current_df)

        # Delete even columns (See what to do with the devices without content)
        required_columns = [str(i) for i in range(1, current_df.shape[1], 2)]
        
        current_df = current_df[required_columns]

        current_df.columns = nominations

        general_df = pd.concat([general_df, current_df], axis=1)

        # Get the amount of no nan elements per column and relate them in a dictionary with the previous list by position (They should have the same lenght)
        current_counting_dict = count_non_empty_elements(current_df)

        counting_dict = counting_dict | current_counting_dict
    
    return general_df, counting_dict

def get_exclusive_datetimes(df1, col1, df2, col2):
    """
    Compares two datetime columns from different DataFrames and returns
    datetime elements present in one but not in both.

    Args:
        df1 (pd.DataFrame): The first DataFrame.
        col1 (str): The name of the datetime column in df1.
        df2 (pd.DataFrame): The second DataFrame.
        col2 (str): The name of the datetime column in df2.

    Returns:
        pd.Series: A Series containing datetime elements that are in one
                   column but not in both (symmetric difference).
    """
    # Convert columns to datetime series and drop NaT values
    series1 = pd.to_datetime(df1[col1], format="d%-m%-y% H%:M%:S%").dropna()
    series2 = pd.to_datetime(df2[col2], format="d%-m%-y% H%:M%:S%").dropna()

    # Convert series to sets for efficient set operations
    set1 = set(series1)
    set2 = set(series2)

    # Find elements unique to either set (symmetric difference)
    exclusive_elements = set1.symmetric_difference(set2)

    # Convert the result back to a Pandas Series
    return [str(elem) for elem in exclusive_elements]

if __name__ == '__main__':
    div_stablished = 4
    meter_subdata_sheets = [f'feature_{i}' for i in range(1, div_stablished+1)]
    connection_subdata_sheets = [f'connection_{i}' for i in range(1, div_stablished+1)]
    
    meter_df, meter_counting = get_total_data_and_counting(meter_subdata_sheets)
    connection_df, connection_counting = get_total_data_and_counting(connection_subdata_sheets)

    # Connect indexes with those that have the same -2 and -3 elements by ":" split
    mismatching_ones = []
    i = 0
    for meter_nom in meter_counting:
        for connection_nom in connection_counting:
            
            meter_nom_elems = meter_nom.split(':')
            connection_nom_elems = connection_nom.split(':')

            # if i in [0, 39, 100]:
            #     print(f'{i}\n')
            #     print(f'meter_nom_elems {meter_nom_elems}: {meter_counting[meter_nom]}\n')
            #     print(f'connection_nom_elems {connection_nom_elems}: {connection_counting[connection_nom]}\n')
            # i += 1

            # If the related ones don't have the same number of columns per column, check what datetimes doesn't match 
            if (meter_nom_elems[2] == connection_nom_elems[2]) and (meter_nom_elems[3] == connection_nom_elems[3])  and (meter_counting[meter_nom] != connection_counting[connection_nom]):
                mismatching_ones.append((meter_nom, connection_nom))


    comparison_dict = {}
    for mismatching_pair in mismatching_ones:

        #print(f'\nmismatching_pair: {mismatching_pair}\n')
        different_elems = get_exclusive_datetimes(meter_df, mismatching_pair[0], connection_df, mismatching_pair[1])
        comparison_dict[mismatching_pair[0]] = different_elems

    
    file_path = r'test(deletable)\mismatching elements.json'
    with open(file_path, 'w') as file:
        json.dump(mismatching_ones, file, indent=4)


    # Return a list of non-matching elments and their non-matching elements
    
    

    