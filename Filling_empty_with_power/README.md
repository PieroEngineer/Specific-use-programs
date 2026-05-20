# Electrical Asset Data Processor

A Python tool for processing electrical measurement data (P, Q, I2, U2) from Excel into structured time-aligned outputs with derived energy values (kWh, kVARh).

## Overview

This project processes raw electrical asset data from Excel, converts it to Parquet, resamples it into 15-minute intervals, and generates final reports with calculated active/reactive energy values (delivered/received) and quadrant-based reactive power.

## Files

### 1. `generating_parquet.py`
Converts specific column ranges from an Excel sheet into separate Parquet files for each measurement type.

**Features:**
- Loads data from columns D:F (P), G:I (Q), J:L (I2), M:O (U2)
- Skips the first data row
- Exports clean Parquet files: `df_{ASSET}_P.parquet`, etc.

### 2. `resyncing_to_fill.py`
Main processing script. Resamples data to 15-minute intervals and computes derived energy metrics.

**Key Features:**
- Custom 15-minute binning aligned to a specific start time
- Uses median for resampling
- Calculates:
  - kWh delivered/received
  - kVARh per quadrant (Q1–Q4) based on P/Q signs
  - Fundamental voltage and current
- Outputs two Excel files:
  - Compressed/resampled data
  - Final structured report
