# Sensor Data Processing & Comparison Tool

A small Python toolkit for processing sensor measurement data (density and temperature) from Parquet files, consolidating it into Excel, and generating visual comparisons between two datasets.

## Overview

This project consists of three scripts that form a pipeline for:
1. Converting individual Parquet files to Excel
2. Aggregating training data from multiple sensor folders
3. Comparing two versions of the data through detailed time-series charts

The data appears to come from industrial/process sensors (e.g., `L_2218_R`, `L_2219_S`, `SE_2301_T`, `TV216`, etc.), containing `densidad` (density) and `temperatura` (temperature) readings with millisecond timestamps.

## Files

### 1. `from_parquet_to_excel.py`
Converts a single Parquet file to Excel format and adds a human-readable datetime column.

**Key features:**
- Reads `.parquet` file using pandas
- Converts `timestamp_ms` to `timestamp_datetime`
- Exports to `.xlsx` with `openpyxl` engine

### 2. `sinthetizing_measure_data.py`
Main data aggregation script. Scans multiple sensor subfolders and extracts density and temperature measurements from training Parquet files.

**Key features:**
- Automatically finds `*train*.parquet` files in specified subfolders
- Extracts `densidad` and `temperatura` columns
- Builds a wide-format DataFrame with columns like `densidad_L_2218_R`, `temperatura_L_2219_S`, etc.
- Aligns data by timestamp
- Saves consolidated result as Excel

### 3. `generate_comparison_graphs_v2.py`
Generates professional comparison charts between two datasets (e.g., "imported" vs "extracted").

**Key features:**
- Plots Version 1 and Version 2 on primary axis
- Shows absolute difference on secondary axis (red line)
- Creates one chart per sensor group (density + temperature)
- Saves high-resolution PNG files
- Handles missing data gracefully by only plotting overlapping timestamps
