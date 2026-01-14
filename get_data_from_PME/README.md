# Mini Project: Fuzzy Name Matching & PME Data Extraction

This mini project contains two small, focused scripts:

1. **`matching_names_ml.py`** – Performs fuzzy matching between lines in two text files and writes the best match per line with a similarity score.
2. **`ConnectionAttemptExtractingData.py`** – Connects to a PME (SQL Server) database using ODBC, queries measurements for a device in a time window, and returns a pivoted `pandas.DataFrame` suitable for analysis.

---

## 1) `matching_names_ml.py`

### What it does
- Reads two UTF-8 text files (one entry per line).
- For each line in **file 1**, finds the **best fuzzy match** in **file 2**.
- Uses `fuzzywuzzy.fuzz.ratio` to compute similarity (0–100).
- Writes ordered results (by highest score first) to an output text file.

> **Note**: The script currently slices `s2[2:]` when comparing (to skip the first two characters of each candidate in file 2). Keep or remove this based on your data format.

### Inputs & Outputs
- **Inputs**: 
  - `file1_path`: path to first text file (names list A)
  - `file2_path`: path to second text file (names list B)
  - `threshold`: minimum similarity score (currently logged but not filtering the output list)
- **Output**:
  - `output_path`: text file with lines like: `95% | John Doe  -->  Jhon Doe`

### Quick start
```bash
python matching_names_ml.py
```
The script includes an example call in the `__main__` block. Adjust the paths to your local folders.

### Usage tips
- If your data in `file2` does **not** need trimming, replace `fuzz.ratio(s1, s2[2:])` with `fuzz.ratio(s1, s2)`.
- To enforce the minimum threshold, uncomment the lines that append only when `best_score >= threshold`.
- For potentially better matching on multi-word names, you can try `fuzz.token_sort_ratio(s1, s2)`.
- The script avoids reusing the same `file2` entry by keeping a list of already matched strings.

---

## 2) `ConnectionAttemptExtractingData.py`

### What it does
- Connects to SQL Server via ODBC (PME schema) and queries `DataLog2`, `Source`, and `Quantity` tables.
- Filters by `source` (device name), `measurements` (quantity names), and a UTC time range.
- Adjusts the time to local (subtracts **5 hours**) after reading.
- Returns a **pivoted wide** dataframe: rows = time, columns = measurement, values = reading.

### Inputs & Outputs
- **Inputs**: 
  - `source`: device name
  - `measurements`: list of quantity names (e.g., `['Vln A', 'Vln B']`)
  - `start_time`, `end_time`: string timestamps in `YYYY-MM-DD HH:MM:SS` (UTC window)
- **Output**:
  - `pandas.DataFrame` pivoted by measurement. Example columns: `['Time', 'Vln A', 'Vln B', ...]`

### Configure connection
Update the `conn_str` in the script with your server, database, and credentials:
```python
conn_str = (
    r'DRIVER={ODBC Driver 18 for SQL Server};'
    r'SERVER=your_server;'
    r'DATABASE=your_database;'
    r'UID=your_user;'
    r'PWD=your_password;'
    r'Trusted_Connection=no;'
    r'Encrypt=yes;'
    r'TrustServerCertificate=yes;'
    r'Connection Timeout=30;'
)
```

> **Timezone note**: The helper `change_to_local_time` adds 5h15m to the input strings before querying, and later the dataframe subtracts **5 hours** from `Time`. Confirm this logic against your PME setup and local timezone needs.

### Quick start
```bash
python ConnectionAttemptExtractingData.py
```
Edit the example `source`, `measurements`, `start_time`, and `end_time` at the bottom of the script to suit your test.

### Usage tips
- If your database stores local time, remove or adjust the time-shift logic.
- If you need to limit by `QuantityID` instead of names, uncomment and adapt the `AND dl.QuantityID IN (...)` clause.
- If you expect large result sets, consider adding date chunking, server-side filtering, or indexes.

---

## Installation

1. **Create a virtual environment (recommended)**
```bash
python -m venv .venv
# Windows
.venv\\Scripts\\activate
# macOS/Linux
source .venv/bin/activate
```

2. **Install dependencies**
```bash
pip install -r requirements.txt
```

3. **ODBC driver (for SQL Server)**
- Install **ODBC Driver 18 for SQL Server** on your machine.
- Ensure you can connect to your PME database using the same credentials.

---

## Project structure (suggested)
```
.
├── matching_names_ml.py
├── ConnectionAttemptExtractingData.py
├── input/
│   └── txt/
│       ├── pme_names.txt
│       └── zmeasure_names.txt
├── output/
│   └── related_v31.txt
└── requirements.txt
```

---

## Troubleshooting
- **`pyodbc.Error: ...`** – Verify DSN/driver installation and network access to the SQL Server.
- **Empty dataframe** – Check device name, measurement names, and time range; verify data exists in PME.
- **Slow fuzzy matching** – Install `python-Levenshtein` to accelerate `fuzzywuzzy`.
- **Encoding issues** – Ensure input text files are UTF-8 and lines are non-empty.

---

## Credits
- Built by **Piero Olivas**.
