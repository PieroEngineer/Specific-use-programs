# Mini Project: Name Clustering & Excel-to-Parquet Converter

This mini-project combines two scripts:

1. **`clustering_names_with_ml.py`** – Clusters names using machine learning (K-Means) for typo-tolerant grouping.
2. **`Get_data.py`** – Converts Excel files to Parquet format for faster processing.

---

## 1) `clustering_names_with_ml.py`

### What it does
- Reads a Parquet file containing names (column: `Nombre Señal`).
- Converts names into numerical vectors using **TF-IDF** with character-level n-grams (2–4) for typo tolerance.
- Applies **K-Means clustering** to group similar names.
- Saves clusters to a text file, grouped by cluster number.

### Inputs & Outputs
- **Input:** `input/nominations.parquet` (must contain column `Nombre Señal`).
- **Output:** `output/<n_clusters>cluster_results.txt` listing names grouped by cluster.

### Quick start
```bash
python clustering_names_with_ml.py
```

### Usage tips
- Adjust `n_clusters` to control the number of clusters.
- For better typo handling, tweak `ngram_range` in `TfidfVectorizer`.
- Ensure the Parquet file is UTF-8 encoded and contains the expected column.

---

## 2) `Get_data.py`

### What it does
- Reads an Excel file and converts it to Parquet format.
- Ensures the column `Nombre Señal` is treated as string.
- Saves the Parquet file for faster downstream processing.

### Inputs & Outputs
- **Input:** Excel file (e.g., `input/ultimos_por_nombre.xlsx`).
- **Output:** Parquet file (e.g., `input/nominations.parquet`).

### Quick start
```bash
python Get_data.py
```
Edit the paths inside the script or call `excel_to_parquet(excel_file_path, parquet_file_path)` programmatically.

---

## Installation
1. Create and activate a virtual environment:
```bash
python -m venv .venv
source .venv/bin/activate  # macOS/Linux
.venv\\Scripts\\activate     # Windows
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

---

## Suggested structure
```
.
├── clustering_names_with_ml.py
├── Get_data.py
├── input/
│   ├── ultimos_por_nombre.xlsx
│   └── nominations.parquet
├── output/
│   └── cluster_results.txt
└── requirements.txt
```

---

## Troubleshooting
- **Empty clusters file**: Check that the Parquet file has the correct column name.
- **Conversion errors**: Ensure Excel file exists and has `Nombre Señal` column.
- **Performance**: For large datasets, consider reducing `n_clusters` or using `MiniBatchKMeans`.

---


## Credits
- Built by **Piero Olivas**.
