import pandas as pd
import matplotlib.pyplot as plt
import os

def generate_comparison_charts(df1, df2, subgroups, output_folder):
    """
    df1, df2: Identical DataFrames (except content). First column must be datetime.
    subgroups: Dictionary { "Group Title": ["col_name_1", "col_name_2", ...] }
    """
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)

    # Set the first column (datetime) as the index for plotting
    time_col = df1.columns[0]

    df1_idx = df1.set_index(time_col)
    df2_idx = df2.set_index(time_col)

    for group_title, columns in subgroups.items():
        
        df1_idx[columns] = df1_idx[columns].apply(pd.to_numeric, errors='coerce')
        df2_idx[columns] = df2_idx[columns].apply(pd.to_numeric, errors='coerce')
        
        n_plots = len(columns)
        # Create a figure with a subplot for each column in the subgroup
        fig, axes = plt.subplots(n_plots, 1, figsize=(24, 5 * n_plots), constrained_layout=True)
        
        # Ensure axes is always a list even if there's only 1 plot
        if n_plots == 1:
            axes = [axes]

        fig.suptitle(f"{group_title}", fontsize=18, fontweight='bold')

        for i, col in enumerate(columns):
            ax1 = axes[i]
            
            # Primary Y-Axis: Version 1 and Version 2
            v1_data = df1_idx[col]
            v2_data = df2_idx[col]

            diff_data = (v1_data - v2_data).abs()
            
            # 1. Identify the 'mask' where both columns have valid numeric data
            # .notna() finds non-empty cells; & (AND) finds the intersection
            valid_mask = v1_data.notna() & v2_data.notna()

            # 2. "Strip" the data: Keep values only where the mask is True
            # Data outside the overlap becomes NaN, making it invisible in the chart
            v1_stripped = v1_data.where(valid_mask)
            v2_stripped = v2_data.where(valid_mask)
            diff_stripped = diff_data.where(valid_mask)

            # 3. Plot using these stripped versions
            line1, = ax1.plot(df1_idx.index, v1_stripped, label="Version 1", color='#1f77b4', linewidth=2)
            line2, = ax1.plot(df1_idx.index, v2_stripped, label="Version 2", color='#ff7f0e', linewidth=2, linestyle='--')
            
            ax1.set_ylabel("Valores", fontsize=10)
            ax1.set_title(f"{col}", fontsize=14, pad=10) # Subtitle
            ax1.grid(True, linestyle=':', alpha=0.6)

            # Secondary Y-Axis: Absolute Difference
            ax2 = ax1.twinx()
            line3, = ax2.plot(df1_idx.index, diff_stripped, label="Diferencia absoluta", color='#d62728', linewidth=1.5, alpha=0.7)
            
            ax2.set_ylabel("Diferencia absoluta", color='#d62728', fontsize=10)
            ax2.tick_params(axis='y', labelcolor='#d62728')

            # Combine legends from both axes
            lines = [line1, line2, line3]
            labels = [l.get_label() for l in lines]
            ax1.legend(lines, labels, loc='upper left', frameon=True)

        # Save the group image
        filename = f"{group_title.replace(' ', '_')}.png"
        save_path = os.path.join(output_folder, filename)
        plt.savefig(save_path, dpi=150)
        plt.close(fig)
        print(f"Saved subgroup chart: {save_path}")


# Main
extracted_data_path = r'output\testing\t1.xlsx'
imported_data_path = r'output\imported measures 2.xlsx'

df_v1 = pd.read_excel(imported_data_path)
df_v2 = pd.read_excel(extracted_data_path)

groups = {
    "L_2218_R": ['densidad L_2218_R', 'temperatura L_2218_R'],
    "L_2218_S": ['densidad L_2218_S', 'temperatura L_2218_S'],
    "L_2218_T": ['densidad L_2218_T', 'temperatura L_2218_T'],
    
    "L_2219_R": ['densidad L_2219_R', 'temperatura L_2219_R'],
    "L_2219_S": ['densidad L_2219_S', 'temperatura L_2219_S'],
    "L_2219_T": ['densidad L_2219_T', 'temperatura L_2219_T'],

    "L_2226_R": ['densidad L_2226_R', 'temperatura L_2226_R'],
    "L_2226_S": ['densidad L_2226_S', 'temperatura L_2226_S'],
    "L_2226_T": ['densidad L_2226_T', 'temperatura L_2226_T'],

    "SE_2301_R": ['densidad SE_2301_R', 'temperatura SE_2301_R'],
    "SE_2301_S": ['densidad SE_2301_S', 'temperatura SE_2301_S'],
    "SE_2301_T": ['densidad SE_2301_T', 'temperatura SE_2301_T'],

    "TV216": ['densidad TV216', 'temperatura TV216'],
}

output_path = r'output\charts'
generate_comparison_charts(df_v1, df_v2, groups, output_path)