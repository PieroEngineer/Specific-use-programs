"""
Excel to Parquet + Device-tuple validation
==========================================

Steps performed
---------------
1. Load a specific sheet from an .xlsx file into a DataFrame.
2. Save the DataFrame to a Parquet file.
3. Re-load the sheet **starting at row 2** (no header, raw strings).
4. Extract the first column into a Python list.
5. Parse each entry of that list with ":" and keep the **-2** and **-3** parts.
6. Group the row indexes that share the same (A, B) pair → list of "device tuples".
7. Rename DataFrame columns → dates_1, values_1, dates_2, values_2, ...
8. For every device tuple (n, m) check that the first value of column *values_n*
   equals the first value of *values_m*.
   - If they differ → record index n in ``issues_found_list``.
   - Record the dates from *dates_n* that are **not** present in *dates_m*
     in ``mismatching_dates_dict``.
9. Return ``issues_found_list`` and ``mismatching_dates_dict``.
"""

from __future__ import annotations 

import os
from pathlib import Path
from typing import List, Tuple, Dict, Any

import pandas as pd


# --------------------------------------------------------------------------- #
# 1. Load sheet & write parquet
# --------------------------------------------------------------------------- #
def load_sheet_to_parquet(
    excel_path: str | Path,
    sheet_name: str,
    parquet_path: str | Path,
) -> pd.DataFrame:
    """
    Load a sheet into a DataFrame and immediately write it to Parquet.

    Parameters
    ----------
    excel_path: path to the .xlsx file
    sheet_name: name of the sheet to read
    parquet_path: where the parquet file will be created

    Returns
    -------
    DataFrame with the original data (header = first row)
    """
    df = pd.read_excel(excel_path, sheet_name=sheet_name)
    
    # Convert object columns to string
    df = df.apply(lambda col: col.astype(str) if col.dtype == 'object' else col)

    df.to_parquet(parquet_path, index=False)
    return df


# --------------------------------------------------------------------------- #
# 2. Load raw data (skip header) and extract first column
# --------------------------------------------------------------------------- #
def load_raw_data(
    excel_path: str | Path,
    sheet_name: str,
) -> Tuple[pd.DataFrame, List[str]]:
    """
    Load the sheet **starting at row 2** (no header) and return
    the DataFrame together with the first column as a Python list.

    Returns
    -------
    df_raw: DataFrame without the first column
    first_col_list: list of strings from the first column
    """
    # ``header=None`` → all rows are data, ``skiprows=1`` removes the header row
    df_full = pd.read_excel(excel_path, sheet_name=sheet_name, header=None, skiprows=1)

    # Separate first column
    first_col_list = df_full.iloc[:, 0].astype(str).tolist()
    df_raw = df_full.iloc[:, 1:]                     # drop the first column
    return df_raw, first_col_list


# --------------------------------------------------------------------------- #
# 3. Parse first-column entries → (A, B) pairs
# --------------------------------------------------------------------------- #
def parse_first_column(first_col_list: List[str]) -> List[Tuple[str, str]]:
    """
    Split each entry by ':' and keep the **-2** (A) and **-3** (B) parts.

    Example
    -------
    "device:group:site:code:extra" → A = "site", B = "code"
    """
    parsed = []
    for entry in first_col_list:
        parts = [p.strip() for p in entry.split(":")]
        if len(parts) < 3:
            # not enough parts → treat as empty to avoid index errors
            parsed.append(("", ""))
            continue
        A = parts[-2]      # second-to-last
        B = parts[-3]      # third-to-last
        parsed.append((A, B))
    return parsed


# --------------------------------------------------------------------------- #
# 4. Build device-tuple list (indexes that share the same (A,B))
# --------------------------------------------------------------------------- #
def build_device_tuples(
    parsed_ab: List[Tuple[str, str]],
) -> List[Tuple[int, int]]:
    """
    Group row indexes that have identical (A, B) pairs.
    Only pairs with **at least two** rows are kept.

    Returns
    -------
    List of (index_n, index_m) tuples, ordered as they appear in the file.
    """
    from collections import defaultdict

    ab_to_idxs: Dict[Tuple[str, str], List[int]] = defaultdict(list)
    for idx, ab in enumerate(parsed_ab):
        ab_to_idxs[ab].append(idx)

    device_tuples: List[Tuple[int, int]] = []
    for idx_list in ab_to_idxs.values():
        if len(idx_list) >= 2:
            # create all pairwise combinations (n < m)
            for i in range(len(idx_list)):
                for j in range(i + 1, len(idx_list)):
                    device_tuples.append((idx_list[i], idx_list[j]))
    return device_tuples


# --------------------------------------------------------------------------- #
# 5. Rename DataFrame columns to the required pattern
# --------------------------------------------------------------------------- #
def rename_columns(df_raw: pd.DataFrame) -> pd.DataFrame:
    """
    Rename columns → dates_1, values_1, dates_2, values_2, ...

    The original file is assumed to have alternating date/value columns.
    """
    new_names = []
    col_idx = 1
    for i in range(0, df_raw.shape[1], 2):
        new_names.append(f"dates_{col_idx}")
        new_names.append(f"values_{col_idx}")
        col_idx += 1
    # In case the last column is a single date column
    if df_raw.shape[1] % 2 == 1:
        new_names.append(f"dates_{col_idx}")

    df = df_raw.copy()
    df.columns = new_names
    return df


# --------------------------------------------------------------------------- #
# 6. Core validation for each device tuple
# --------------------------------------------------------------------------- #
def validate_device_tuples(
    df: pd.DataFrame,
    device_tuples: List[Tuple[int, int]],
) -> Tuple[List[int], Dict[int, List[Any]]]:
    """
    For every (n, m) tuple:
      • Compare the **first** value of ``values_n`` with ``values_m``.
      • If they differ → add n to ``issues_found_list``.
      • Collect dates from ``dates_n`` that are **missing** in ``dates_m``.

    Returns
    -------
    issues_found_list, mismatching_dates_dict
    """
    issues_found_list: List[int] = []
    mismatching_dates_dict: Dict[int, List[Any]] = {}

    for n, m in device_tuples:
        # Column names for the two devices
        val_n_col = f"values_{n + 1}"   # +1 because device index is 0-based
        val_m_col = f"values_{m + 1}"
        date_n_col = f"dates_{n + 1}"
        date_m_col = f"dates_{m + 1}"

        # ------------------------------------------------------------------- #
        # 1. First-value equality test
        # ------------------------------------------------------------------- #
        first_val_n = df.at[0, val_n_col]
        first_val_m = df.at[0, val_m_col]

        if pd.isna(first_val_n) or pd.isna(first_val_m):
            # If any is NaN we cannot compare → treat as mismatch
            if n not in issues_found_list:
                issues_found_list.append(n)
            continue

        if first_val_n != first_val_m:
            if n not in issues_found_list:
                issues_found_list.append(n)

        # ------------------------------------------------------------------- #
        # 2. Missing dates collection (only when first values differ)
        # ------------------------------------------------------------------- #
        if first_val_n != first_val_m:
            dates_n = set(df[date_n_col].dropna())
            dates_m = set(df[date_m_col].dropna())
            missing = sorted(dates_n - dates_m)
            if missing:
                mismatching_dates_dict[n] = missing

    return issues_found_list, mismatching_dates_dict


# --------------------------------------------------------------------------- #
# MAIN orchestration function
# --------------------------------------------------------------------------- #
def process_excel_file(
    excel_path: str | Path,
    sheet_name: str,
    parquet_path: str | Path | None = None,
) -> Tuple[List[int], Dict[int, List[Any]]]:
    """
    Execute the whole pipeline and return the validation results.

    Parameters
    ----------
    excel_path: path to the input .xlsx
    sheet_name: sheet that contains the data
    parquet_path: optional path for the intermediate parquet file

    Returns
    -------
    issues_found_list, mismatching_dates_dict
    """
    excel_path = Path(excel_path)

    # ------------------------------------------------------------------- #
    # 1. Load + parquet (optional)
    # ------------------------------------------------------------------- #
    if parquet_path:
        load_sheet_to_parquet(excel_path, sheet_name, parquet_path)

    # ------------------------------------------------------------------- #
    # 2. Load raw data (skip header) + extract first column
    # ------------------------------------------------------------------- #
    df_raw, first_col_list = load_raw_data(excel_path, sheet_name)

    # ------------------------------------------------------------------- #
    # 3. Parse first column → (A, B)
    # ------------------------------------------------------------------- #
    parsed_ab = parse_first_column(first_col_list)

    # ------------------------------------------------------------------- #
    # 4. Build device tuples
    # ------------------------------------------------------------------- #
    device_tuples = build_device_tuples(parsed_ab)

    # ------------------------------------------------------------------- #
    # 5. Rename columns
    # ------------------------------------------------------------------- #
    df = rename_columns(df_raw)

    # ------------------------------------------------------------------- #
    # 6. Validate
    # ------------------------------------------------------------------- #
    issues, mismatch_dict = validate_device_tuples(df, device_tuples)

    return issues, mismatch_dict


# --------------------------------------------------------------------------- #
# Example usage
# --------------------------------------------------------------------------- #
if __name__ == "__main__":
    EXCEL_FILE = r"input\Analisis_de_estados.xlsx"
    SHEET = "Hoja6"
    PARQUET_FILE = r"input/Análisis_de_estados.parquet"

    issues_list, mismatch_dict = process_excel_file(
        excel_path=EXCEL_FILE,
        sheet_name=SHEET,
        parquet_path=PARQUET_FILE,
    )

    print("\nIssues found (device indexes):", issues_list)
    print("\nMismatching dates per device:")
    for dev, dates in mismatch_dict.items():
        print(f"  Device {dev}: {dates}")