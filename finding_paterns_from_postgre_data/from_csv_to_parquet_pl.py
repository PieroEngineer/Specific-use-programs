import polars as pl

# Your list of headers
headers = ['time', 'repeated_hour', 'secs', 'class', 'severity', 'area', 'reference_name', 'point_name', 'message', 'value', 'nvalue', 'station_id', 'attachment', 'p_equip', 'flag', 'origin', 'aor_mask1', 'aor_mask2', 'aor_mask3', 'aor_mask4', 'record', 'u_time', 'mod_time', 'site_id']

month = 'FEBRERO'
year = '2026'

file_name = fr"ALARMAS_{month}_{year}"

# Initialize a lazy scan
lazy_df = pl.scan_csv(
    'input\\' + file_name + '.csv',
    has_header = False,                       # Tell Polars there are no headers in the file
    with_column_names = lambda _ : headers,   # Apply your custom list as column names
    encoding="utf8",                          # Common for Excel/Windows-exported CSVs
    low_memory = True                         # Optimize for memory-constrained environments
).filter(pl.col("site_id") != 2)

# Stream the data directly to a Parquet file
# This processes the file in batches (streaming)
lazy_df.sink_parquet('input\\' + file_name + '.parquet')

# This executes the plan for ONLY the first 5 rows
print(lazy_df.head(5).collect())