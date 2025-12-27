# Mini Project: Data Consistency Checks across Meter/Connection Sheets

This mini-project contains two complementary scripts to validate and compare time-series data extracted from Excel/Parquet files:

1. **`comparing_counting.py`** – Concatenates multiple Parquet sheets, counts non-empty values per device/route, compares meter vs. connection series, and outputs mismatching pairs and exclusive datetimes.
2. **`finding_different_size.py`** – End-to-end pipeline: loads an Excel sheet, writes to Parquet, parses device identifiers from the first column, groups devices by `(A, B)` tuple, renames alternating date/value columns, and validates per-device pairs (first-value equality + missing dates).

---

## 1) `comparing_counting.py`

### What it does
- Reads several **Parquet** files from `input/new/<sheet>.parquet`.
- Extracts the first column (device route), trimming a fixed prefix (`\\server_name\\`).
- Keeps **odd** columns (1, 3, 5, ...) which represent data series and sets their column names to the extracted routes.
- Counts **non-empty** elements in each series.
- Compares **meter** vs **connection** counts for devices with the same `-3` and `-2` parts of their route (split by `:`). If counts differ, computes the **symmetric difference** of their datetime columns.
- Saves the list of mismatching pairs to `test(deletable)/mismatching elements.json` and returns the exclusive datetimes.

### Quick start
```bash
python comparing_counting.py
```
> Ensure the required Parquet files exist under `input/new/` and follow the naming pattern used in the script (e.g., `feature_1.parquet`, `connection_1.parquet`, ...).

---

## 2) `finding_different_size.py`

### What it does (pipeline)
1. **Load → Parquet:** Reads an Excel sheet and immediately writes a Parquet copy (optional).
2. **Raw load (skip header):** Loads the same sheet starting at row 2 (`header=None`, `skiprows=1`).
3. **Parse identifiers:** Splits entries in the first column by `:` and keeps **-2** (A) and **-3** (B) parts.
4. **Group devices:** Builds index tuples `(n, m)` where rows share identical `(A, B)`.
5. **Rename columns:** Assumes alternating date/value columns → `dates_1, values_1, dates_2, values_2, ...`.
6. **Validate tuples:**
   - Check equality of the **first** entry in `values_n` vs `values_m`.
   - If different → record the device index in `issues_found_list` and collect **missing dates** from `dates_n` not present in `dates_m`.
7. Returns `issues_found_list` and `mismatching_dates_dict`.

### Quick start
```bash
python finding_different_size.py
```
Edit the constants at the bottom as needed:
```python
EXCEL_FILE = r"input/Analisis_de_estados.xlsx"
SHEET = "Hoja6"
PARQUET_FILE = r"input/Análisis_de_estados.parquet"
```

---

## Installation

1. **Create and activate a virtual environment**
```bash
python -m venv .venv
# Windows
.venv\Scripts\activate
# macOS/Linux
source .venv/bin/activate
```

2. **Install dependencies**
```bash
pip install -r requirements.txt
```

---

## Troubleshooting
- **Parquet read errors**: Ensure the Parquet files exist and are written with `pyarrow` or compatible engine.
- **Header / column alignment**: If the Excel layout changes, adjust `skiprows`, `header=None`, and the alternating date/value assumption.
- **Identifier parsing**: If routes don’t contain enough `:` parts, parsing `(A,B)` will yield empty strings; adapt `parse_first_column` logic accordingly.
- **Different locales**: Datetime parsing/format may differ; confirm formats when computing symmetric differences.

---

## Credits
- Built by **Piero Olivas**.
