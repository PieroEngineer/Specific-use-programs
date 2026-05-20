import polars as pl
import matplotlib.pyplot as plt
import os
import numpy as np

folder_path = r'output\data'
chart_output_path = r'output\charts'

os.makedirs(chart_output_path, exist_ok=True)

for filename in os.listdir(folder_path):
    if filename.endswith('.parquet'):
        full_path_parquet = os.path.join(folder_path, filename)
        base_name = filename.split('.')[0]

        # 1. Process data - Extracting day number
        df_full = (
            pl.scan_parquet(full_path_parquet)
            .with_columns(
                pl.col("time").str.to_datetime("%Y-%m-%d %H:%M:%S").dt.day().alias("day_num")
            )
            .group_by(["day_num", "name"])
            .len()
            .collect()
            .pivot(index="day_num", on="name", values="len")
            .sort("day_num")
            .fill_null(0)
        )

        # 2. Logic to split the days into 3 segments
        unique_days = df_full["day_num"].to_list()
        
        # Use numpy to split the list into 3 parts as evenly as possible
        day_segments = np.array_split(unique_days, 3)

        for i, segment in enumerate(day_segments, 1):
            if len(segment) == 0: continue # Skip if not enough days to fill 3 parts

            # Filter data for the specific days in this segment
            df_segment = df_full.filter(pl.col("day_num").is_in(segment))
            pdf = df_segment.to_pandas().set_index("day_num")

            # 3. Plotting
            ax = pdf.plot(
                kind="bar", 
                figsize=(12, 6), 
                width=0.8, 
                edgecolor='white',
                linewidth=0.5
            )

            # Styling
            title_part = f"{base_name.replace('_', ' ')} - Part {i}"
            plt.title(title_part, pad=20, fontsize=14)
            plt.xlabel("Day of Month", fontsize=12)
            plt.ylabel("Count", fontsize=12)
            plt.xticks(rotation=0) 
            plt.grid(axis='y', linestyle='--', alpha=0.7)

            # Legend on the right
            plt.legend(title="Names", bbox_to_anchor=(1.05, 1), loc='upper left', borderaxespad=0.)
            plt.tight_layout()

            # 4. Save
            save_path = os.path.join(chart_output_path, f"{base_name}_part_{i}.png")
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
            plt.close()

        print(f"Split {filename} into {i} images.")
