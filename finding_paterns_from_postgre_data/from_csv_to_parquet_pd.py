import pandas as pd
import os

headers = ['time', 'repeated_hour', 'secs', 'class', 'severity', 'area', 'reference_name', 'point_name', 'message', 'value', 'nvalue', 'station_id', 'attachment', 'p_equip', 'flag', 'origin', 'aor_mask1', 'aor_mask2', 'aor_mask3', 'aor_mask4', 'record', 'u_time', 'mod_time', 'site_id']
folder_path = r'input'

for filename in os.listdir(folder_path):
    if filename.endswith('.csv'):
        full_path_csv = os.path.join(folder_path, filename)
        full_path_parquet = full_path_csv.split('.')[0] + '.parquet'

        if not os.path.exists(full_path_parquet):
            try:
                df = pd.read_csv(full_path_csv, names=headers)
            except UnicodeDecodeError:
                print(f'⚠️  Encoding with "latin1" because UT8 did not work in {filename}\n')
                df = pd.read_csv(full_path_csv, encoding='latin1', names=headers)

            df.to_parquet(full_path_parquet, engine='pyarrow')