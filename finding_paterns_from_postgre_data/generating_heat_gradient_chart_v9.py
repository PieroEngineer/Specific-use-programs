import pandas as pd
import os
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.colors import ListedColormap, BoundaryNorm
import numpy as np


def process_parquet_files(input_folder, average_window_size, output_folder):
    """
    Processes parquet files to calculate minute-by-minute activity 
    and windowed averages.
    """
    # Create output directory if it doesn't exist
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)

    for filename in os.listdir(input_folder):
        if filename.endswith(".parquet"):
            # 1. Load data
            file_path = os.path.join(input_folder, filename)
            df = pd.read_parquet(file_path)

            # 2. Filter system names and convert time
            df['time'] = pd.to_datetime(df['time'])
            df = df[~df['name'].isin(['', ''])]

            # 3. Determine the full month range (Exact start and end)
            # Assumes each file contains data for exactly one month
            start_month = df['time'].min().replace(day=1, hour=0, minute=0, second=0, microsecond=0)
            end_month = (start_month + pd.offsets.MonthEnd(0)).replace(hour=23, minute=59, second=59)
            
            # Create a range of every exact minute in that month
            full_minute_range = pd.date_range(start=start_month, end=end_month, freq='min')

            # 4. Generate Table 2: Minute Activity ("account")
            # Floor original timestamps to the nearest minute
            df['minute_floor'] = df['time'].dt.floor('min')
            
            # Count occurrences per minute and reindex to include all minutes in the month
            minute_counts = (df.groupby('minute_floor').size()
                             .reindex(full_minute_range, fill_value=0)
                             .reset_index())
            minute_counts.columns = ['datetime', 'account']

            # 5. Generate Table 3: Window Averages
            # Resample by the custom window size and calculate the mean of 'account'
            windowed_df = (minute_counts.resample(f'{average_window_size}min', on='datetime', label='left')
                           .agg({'account': 'mean'})
                           .reset_index())
            windowed_df.columns = ['window_datetime', 'average']

            # 6. Save final table
            output_path = os.path.join(output_folder, f"avg_{filename}")
            windowed_df.to_parquet(output_path, index=False)
            print(f"✅  Successfully processed and saved: {output_path}")

def generate_heatmap_images(input_folder: str, image_output_folder: str):
    """
    Creates a grid visualization (heatmap) for each parquet file based on 
    average activity levels.
    """
    if not os.path.exists(image_output_folder):
        os.makedirs(image_output_folder)

    # Define the colors and threshold boundaries
    # Colors: Robust, Stable, Reactive, Overloaded
    colors = ["#00af50", "#9fbd67", "#ffff00", "#ce543f"]
    # Boundaries: 0-1, 1-2, 2-10, 10+
    boundaries = [0, 1, 2, 10, 1000] 
    
    cmap = ListedColormap(colors)
    norm = BoundaryNorm(boundaries, ncolors=len(colors))

    legend_data = [
        ('Robust (avg < 1)', "#00af50"),
        ('Stable (1 ≤ avg < 2)', "#9fbd67"),
        ('Reactive (2 ≤ avg < 10)', "#ffff00"),
        ('Overloaded (10 ≤ avg)', "#ce543f")
    ]

    for filename in os.listdir(input_folder):
        if filename.endswith(".parquet"):
            file_path = os.path.join(input_folder, filename)
            df = pd.read_parquet(file_path)
            
            # 1. Extract Day and Time for pivoting
            df['window_datetime'] = pd.to_datetime(df['window_datetime'])
            df['day'] = df['window_datetime'].dt.day
            df['time_str'] = df['window_datetime'].dt.strftime('%H:%M')
            
            # Pivot the data so days are rows and time windows are columns
            pivot_df = df.pivot(index='day', columns='time_str', values='average')
            
            # 2. Create the Plot
            fig, ax = plt.subplots(figsize=(20, 10))
            
            # Use imshow to create the grid
            im = ax.imshow(pivot_df, cmap=cmap, norm=norm, aspect='auto')

            # 3. Axis Formatting
            # Y-axis: Show only the day number
            ax.set_yticks(np.arange(len(pivot_df.index)))
            ax.set_yticklabels(pivot_df.index)
            ax.set_ylabel('Day of Month')

            # X-axis: Show only the time
            # We skip labels to avoid overlap if there are many windows (e.g., 144)
            label_step = max(1, len(pivot_df.columns) // 24) # Label approx every hour
            ax.set_xticks(np.arange(0, len(pivot_df.columns), label_step))
            ax.set_xticklabels(pivot_df.columns[::label_step], rotation=45)
            ax.set_xlabel('Time (HH:MM)')

            # Create minor ticks centered between the cells to draw the grid lines
            ax.set_xticks(np.arange(-.5, len(pivot_df.columns), 1), minor=True)
            ax.set_yticks(np.arange(-.5, len(pivot_df.index), 1), minor=True)

            # Style the grid: color, thickness, and visible lines
            ax.grid(which='minor', color='w', linestyle='-', linewidth=1)
            
            # Hide the minor tick marks themselves so they don't poke out
            ax.tick_params(which='minor', bottom=False, left=False)

            # 4. Add the Custom Legend
            patches = [mpatches.Patch(color=c, label=l) for l, c in legend_data]
            ax.legend(handles=patches, bbox_to_anchor=(1.01, 1), loc='upper left', borderaxespad=0.)

            plt.title(f"Activity Heatmap (10 min avg) - {filename}")    ## Become it dynamic
            plt.tight_layout()
            
            # 5. Save the image
            image_name = filename.replace('.parquet', '.png')
            save_path = os.path.join(image_output_folder, image_name)
            plt.savefig(save_path, dpi=300)
            plt.close()
            print(f"✅  Saved: {save_path}")

def generate_percentage_charts(input_folder, image_output_folder):
    """
    Generates a stacked bar chart for each month showing the percentage 
    of daily time spent in each status category.
    """
    if not os.path.exists(image_output_folder):
        os.makedirs(image_output_folder)

    # Status configuration
    status_map = [
        ('Robust (avg < 1)', "#00af50"),
        ('Stable (1 ≤ avg < 2)', "#9fbd67"),
        ('Reactive (2 ≤ avg < 10)', "#ffff00"),
        ('Overloaded (10 ≤ avg)', "#ce543f")
    ]

    for filename in os.listdir(input_folder):
        if filename.endswith(".parquet"):
            df = pd.read_parquet(os.path.join(input_folder, filename))
            df['window_datetime'] = pd.to_datetime(df['window_datetime'])
            df['day'] = df['window_datetime'].dt.day

            # 1. Categorize each window average
            def categorize(val):
                if val < 1: return 'Robust (avg < 1)'
                if val < 2: return 'Stable (1 ≤ avg < 2)'
                if val < 10: return 'Reactive (2 ≤ avg < 10)'
                return 'Overloaded (10 ≤ avg)'

            df['status'] = df['average'].apply(categorize)

            # 2. Calculate percentages per day
            # Group by day and status, count them, then divide by total windows in that day
            pivot_counts = df.groupby(['day', 'status']).size().unstack(fill_value=0)
            daily_percentages = pivot_counts.div(pivot_counts.sum(axis=1), axis=0) * 100

            # Ensure all status columns exist even if 0% for a specific day
            for status, _ in status_map:
                if status not in daily_percentages.columns:
                    daily_percentages[status] = 0.0
            
            # Reorder columns to match the desired legend stack
            daily_percentages = daily_percentages[[s[0] for s in status_map]]

            # 3. Plotting
            fig, ax = plt.subplots(figsize=(12, 7))
            colors = [s[1] for s in status_map]
            
            daily_percentages.plot(
                kind='bar', 
                stacked=True, 
                ax=ax, 
                color=colors, 
                width=0.8,
                edgecolor='white',
                linewidth=0.5
            )

            # 4. Formatting
            ax.set_title(f"Daily Status Composition - {filename}", fontsize=14)
            ax.set_xlabel("Day of Month", fontsize=12)
            ax.set_ylabel("Percentage of Day (%)", fontsize=12)
            ax.set_ylim(0, 100)
            ax.legend(title="Status", bbox_to_anchor=(1.05, 1), loc='upper left')
            
            plt.tight_layout()
            
            # 5. Save
            save_path = os.path.join(image_output_folder, f"percent_{filename.replace('.parquet', '.png')}")
            plt.savefig(save_path, dpi=300)
            plt.close()
            print(f"✅  Saved percentage chart: {save_path}")

# --- Example Usage ---
input_dir = r'output\data\intially_processed'
output_dir = r'output\data\averages\10min'
gradient_image_folder = r'output\charts\gradient\attemps\8'
status_image_folder = r'output\charts\status_proportions'

window_size = 10

# process_parquet_files(input_dir, window_size, output_dir)
generate_heatmap_images(output_dir, gradient_image_folder)
# generate_percentage_charts(output_dir, status_image_folder)