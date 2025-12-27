from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.cluster import KMeans, AgglomerativeClustering
from sklearn.metrics import pairwise_distances_argmin_min

import numpy as np
import pandas as pd

def get_parquet_column_as_list(parquet_filepath: str, column_name: str) -> list:
    """
    Reads a Parquet file and extracts a specified column's data into a Python list.

    Args:
        parquet_filepath (str): The path to the Parquet file.
        column_name (str): The name of the column to extract.

    Returns:
        list: A Python list containing the data from the specified column.
              Returns an empty list if the column is not found or the file is empty.
    """
    try:
        # Read the Parquet file into a pandas DataFrame
        df = pd.read_parquet(parquet_filepath)

        # Check if the column exists in the DataFrame
        if column_name in df.columns:
            # Extract the column and convert it to a list
            column_data = df[column_name].tolist()
            return column_data
        else:
            print(f"Error: Column '{column_name}' not found in the Parquet file.")
            return []
    except FileNotFoundError:
        print(f"Error: Parquet file not found at '{parquet_filepath}'")
        return []
    except Exception as e:
        print(f"An error occurred: {e}")
        return []

def save_clusters_to_text(dataframe, value_col_name, cluster_col_name, output_filepath):
    """
    Saves cluster-separated data from a DataFrame to a single text file.

    Args:
        dataframe (pd.DataFrame): The input DataFrame.
        value_col_name (str): The name of the column containing the values.
        cluster_col_name (str): The name of the column containing the cluster numbers.
        output_filepath (str): The path to the output text file.
    """
    with open(output_filepath, 'w') as f:
        # Get unique cluster numbers and sort them for consistent output
        unique_clusters = sorted(dataframe[cluster_col_name].unique())

        for cluster_num in unique_clusters:
            # Filter the DataFrame for the current cluster
            cluster_data = dataframe[dataframe[cluster_col_name] == cluster_num]

            # Write a header for the current cluster
            f.write(f"--- Cluster {cluster_num} ---\n")

            # Write each value from the current cluster
            for value in cluster_data[value_col_name]:
                f.write(f"{value}\n")
            f.write("\n") # Add a blank line for separation between clusters


texts = get_parquet_column_as_list(r"input/nominations.parquet", 'Nombre Señal')

# Convert texts to numerical vectors
vectorizer = TfidfVectorizer(analyzer='char', ngram_range=(2, 4))  # use char-level n-grams for typo tolerance
X = vectorizer.fit_transform(texts)
print('Convertion to numerical vectors is ready')

# Cluster using KMeans
n_clusters = 600
kmeans = KMeans(n_clusters=n_clusters, random_state=42, n_init='auto')
kmeans.fit(X)
print('Clustering ready')

# View clusters
df = pd.DataFrame({"Names": texts, "cluster": kmeans.labels_})

# print(df.sort_values("cluster"))

# Generating txt to show clusters
save_clusters_to_text(df, 'Names', "cluster", fr'output\{n_clusters}cluster_results.txt')