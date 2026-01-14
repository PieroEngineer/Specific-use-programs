import pyodbc
import pandas as pd
from datetime import datetime, timedelta

def get_pme_report(source: str, measurements: list, start_time: str, end_time: str) -> pd.DataFrame:
    """
    Fetch PME tabular report data as a pandas DataFrame, adjusted for 5-hour offset and pivoted.
    
    Parameters:
    - source: str, device name (e.g., 'Meter1')
    - measurements: list, measurement names (e.g., ['Vln A', 'Vln B'])
    - start_time: str, start of reporting period (e.g., '2025-08-01 00:00')
    - end_time: str, end of reporting period (e.g., '2025-08-31 23:59')
    
    Returns:
    - pandas DataFrame with Time as rows and Measurements as columns (pivoted wide format)
    """

    def change_to_local_time(dt_str):
        # Parse to datetime
        dt = datetime.strptime(dt_str, "%Y-%m-%d %H:%M:%S")

        # Offset by -5 hours
        offset_dt = dt + timedelta(hours=5, minutes = 15)

        # Convert back to string
        return offset_dt.strftime("%Y-%m-%d %H:%M:%S")
    
    start_time = change_to_local_time(start_time)
    end_time = change_to_local_time(end_time)

    # Connection string (update with your details)
    conn_str = (
        r'DRIVER={ODBC Driver 18 for SQL Server};'
        r'SERVER=SERVER;'   # Data removed for confidentiality
        r'DATABASE=DATABASE;'   # Data removed for confidentiality
        r'UID=UID;' # Data removed for confidentiality
        r'PWD=PWD;' # Data removed for confidentiality
        r'Trusted_Connection=no;'  # Explicitly use SQL Authentication
        r'Encrypt=yes;'  # Enable encryption for security
        r'TrustServerCertificate=yes;'
        r'Connection Timeout=30;'  # Increase timeout to 30 seconds
    )

    try:
        # Connect to the database
        conn = pyodbc.connect(conn_str)
        cursor = conn.cursor()

        # Build SQL query
        # Escape single quotes in source and measurements
        source_escaped = source.replace("'", "''")
        measurements_escaped = [m.replace("'", "''") for m in measurements]
        measurements_str = ", ".join(f"'{m}'" for m in measurements_escaped)
        
        query = f"""
        SELECT 
            dl.TimestampUTC AS Time,
            s.Name AS Device,
            q.Name AS Measurement,
            dl.Value
        FROM 
            DataLog2 dl
        INNER JOIN 
            Source s ON dl.SourceID = s.ID
        INNER JOIN 
            Quantity q ON dl.QuantityID = q.ID
        WHERE 
            s.Name = '{source_escaped}'
            AND q.Name IN ({measurements_str})
            --AND dl.QuantityID IN (170)
            AND dl.TimestampUTC BETWEEN '{start_time}' AND '{end_time}'
        ORDER BY 
            dl.TimestampUTC
        """

        # Execute query and load into DataFrame
        df = pd.read_sql(query, conn)

        # Close connection
        cursor.close()
        conn.close()

        if df.empty:
            return df
        
        print(f'\ndf columns: {df.columns}\n')

        # Convert Time to datetime
        df['Time'] = pd.to_datetime(df['Time'])

        # Adjust for 5-hour offset (subtract 5 hours to match local time)
        df['Time'] = df['Time'] - pd.Timedelta(hours=5)

        # Pivot the DataFrame: Time as index, Measurements as columns, Values as data
        df_pivoted = df.pivot(index='Time', columns='Measurement', values='Value').reset_index()

        df_pivoted = df_pivoted[:-1] 

        return df_pivoted

    except pyodbc.Error as e:
        print(f"Database error: {e}")
        return pd.DataFrame()
    except Exception as e:
        print(f"Unexpected error: {e}")
        return pd.DataFrame()



# Example usage
source = "source"   # Data removed for confidentiality
measurements = ['measurement']  # Data removed for confidentiality

start_time = "2024-10-01 00:00:00"  # Format: YYYY-MM-DD HH:MM:SS
end_time = "2024-11-01 00:00:00"

df = get_pme_report(source, measurements, start_time, end_time)
if not df.empty:
    print(f'Source: {source}\nMeasurements: {measurements}\n')
    print(df.head(10), '\n')
    print(df.tail(10))
else:
    print(f"\nNo data returned or an error occurred for\nSource: {source}\nMeasurements: {measurements}\n")