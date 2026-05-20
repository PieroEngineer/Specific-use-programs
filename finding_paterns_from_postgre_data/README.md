# Activity Monitoring & Visualization Toolkit

A Python project for processing large alarm/activity logs, generating time-based activity metrics, and creating insightful visualizations (heatmaps and bar charts).

## Overview

This tool processes high-volume Parquet files containing timestamped events (likely alarms or system activities). It performs data enrichment via metadata joins, calculates activity intensity over time, and generates rich visualizations to help analyze daily and monthly patterns.

## Files

### 1. `processing_data.py`
Pre-processes raw event data by enriching it with metadata.

**Features:**
- Uses **Polars** for efficient lazy processing of large Parquet files
- Joins main events table with `data_definitions.parquet` and `Alarms_groups.parquet`
- Adds descriptive `name` and `p_alarm_group` columns
- Filters and prepares data for downstream analysis

### 2. `generating_heat_gradient_chart.py`
Main analysis and visualization script. Generates activity heatmaps and daily status reports.

**Key Features:**
- Calculates minute-by-minute activity counts per month
- Computes rolling window averages (default: 10 minutes)
- Creates **gradient heatmaps** showing activity intensity across days and hours
- Generates **stacked percentage bar charts** showing daily distribution of status levels:
  - Robust (avg < 1)
  - Stable (1–2)
  - Reactive (2–10)
  - Overloaded (10+)

### 3. `generating_accumulated_bars_chart.py`
Creates accumulated daily bar charts split by name/category.

**Features:**
- Aggregates event counts per day and per `name`
- Splits the month into 3 segments for better readability
- Generates grouped bar charts showing daily activity volume per category

## Dependencies

```bash
pandas
polars
matplotlib
numpy
pyarrow
