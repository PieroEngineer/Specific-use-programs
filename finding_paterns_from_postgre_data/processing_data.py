import os
import polars as pl


folder_path = r'input'

for filename in os.listdir(folder_path):
    if filename.endswith('.parquet'):
        full_path_parquet = os.path.join(folder_path, filename)

        # Start Lazy Scans for all 3 tables
        # Using scan_parquet ensures we don't load the full 12GB into RAM
        df1_lazy = pl.scan_parquet(full_path_parquet)
        df2_lazy = pl.scan_parquet(r"input\metadata\data_definitions.parquet")
        df3_lazy = pl.scan_parquet(r"input\metadata\Alarms_groups.parquet")

        # Build the transformation pipeline
        # Step A: Start with Table 1 and select only the required columns
        final_query = (
            df1_lazy.select([
                pl.col("time"),#.cast(pl.Utf8),    # Ensure time is string
                pl.col("reference_name")#.cast(pl.Utf8)  # Ensure reference_name is string
            ])
            
            # Step B: Map Table 1 to Table 2 using "reference_name" 
            # This adds the "p_alarm_group" column
            .join(
                df2_lazy.select(["reference_name", "p_alarm_group"]), 
                on="reference_name", 
                how="left"
            )
            
            # Step C: Map the result to Table 3 using "p_alarm_group"
            # This adds the "name" column
            .join(
                df3_lazy.select(["p_alarm_group", "name"]), 
                on="p_alarm_group", 
                how="left"
            )

            .with_columns(
                pl.col("name").fill_null("")
            )
        )

        # Save the result to a new Parquet file
        # .sink_parquet() streams the join process directly to the disk
        # final_query.sink_parquet('output\data\\' + filename)

        print(final_query.head(20).collect())