# COES Project Data Extraction

A web scraping tool to extract and process project data from the COES (Comité de Operación Económica del Sistema Interconectado Nacional) platform. The tool automates browser interactions to download Excel files, extracts additional metadata from interactive tables, and processes the data into a unified format.

## Overview

This project consists of three Python modules that work together to:

1. **Extract data** from the new COES platform (`get_data_from_new_coes.py`) using Selenium automation
2. **Extract data** from the legacy COES platform (`get_data_from_old_coes.py`)
3. **Orchestrate the extraction** and combine results (`main_getter.py`)

## Files

| File | Description |
|------|-------------|
| `get_data_from_new_coes.py` | Extracts project data from the modern COES platform (EPO/EO), including downloading Excel files and scraping detailed project information |
| `get_data_from_old_coes.py` | Extracts data from the legacy COES platform by selecting project types and exporting reports |
| `main_getter.py` | Orchestrates both extraction methods, processes the data, and generates final Excel outputs |

## Features

- Automated browser control with Selenium WebDriver (Chrome)
- Handles dynamic loading animations and pagination
- Downloads Excel files automatically to specified directories
- Extracts additional metadata (power, type, third-party names) from interactive tables
- Post-processes data: normalizes dates, assigns energy types, standardizes status values
- Groups similar project names using sequence matching
- Stores extraction records as Parquet files for reproducibility

## Requirements

- Python 3.8+
- Chrome browser
- ChromeDriver (compatible with your Chrome version)
- Required Python packages:
  - `selenium`
  - `pandas`
  - `numpy`
  - `openpyxl`
  - `pyarrow`

## Directory Structure

```
project/
├── get_data_from_new_coes.py
├── get_data_from_old_coes.py
├── main_getter.py
├── Other_drivers/
│   └── v146/
│       └── chromedriver-win64/
│           └── chromedriver.exe
├── input/
│   ├── base/
│   │   └── Consulta_Web_EPO_EO_Cambio 1.xlsx
│   ├── downloaded_file/
│   └── Potencias.xlsx
├── output/
│   ├── extraction_record/
│   ├── from_new_source/
│   ├── final_extraction/
│   └── similar/
```

## Usage

### Run the complete extraction

```bash
python main_getter.py
```

When prompted:
- Type `c` to access COES directly (requires browser automation)
- Type `f` to read previously extracted data from Parquet files

### Individual module usage

**New COES platform:**
```python
from get_data_from_new_coes import provide_automation_drivers, run_browser_extraction

main_paths = {
    'webpage_url': 'https://plataformadeproyectos.coes.org.pe/iniciar-sesion',
    'chromedriver_path': 'path/to/chromedriver.exe',
    'relative_download_dir': 'input/downloaded_file'
}
wait_driver, driver = provide_automation_drivers(**main_paths)
epo_path, eo_path, ... = run_browser_extraction(main_paths, wait_driver, driver)
```

**Old COES platform:**
```python
from get_data_from_old_coes import get_specific_data_from_coes

df = get_specific_data_from_coes(is_eo=True, project_type="Generación Convencional")
```

## Key Functions

### From `get_data_from_new_coes.py`

| Function | Description |
|----------|-------------|
| `provide_automation_drivers()` | Initializes Chrome WebDriver with download preferences |
| `run_browser_extraction()` | Main extraction routine for EPO and EO data |
| `data_postprocessing()` | Cleans and standardizes extracted data |
| `assign_latest_reference()` | Groups similar project names and assigns latest version as reference |
| `write_df_in_excel()` | Saves DataFrames to Excel with retry logic for open files |

### From `get_data_from_old_coes.py`

| Function | Description |
|----------|-------------|
| `get_specific_data_from_coes()` | Downloads Excel for a specific project type (EO or EPO) |
| `order_data()` | Processes raw data, updates power values, and merges with base file |

### From `main_getter.py`

| Function | Description |
|----------|-------------|
| `get_data_from_new_source()` | Orchestrates extraction from the new platform |
| `get_data_from_old_source()` | Orchestrates extraction from the legacy platform |

## Data Processing

The extracted data undergoes several transformations:

1. **Status mapping**: Raw status values are mapped to standardized categories (Aprobado, En revisión, No vigente, Rechazado)
2. **Energy type assignment**: Determined from project name prefixes (C.S.F. → Solar, C.H. → Hidráulica, etc.)
3. **Date formatting**: Converts to `dd/mm/yyyy` format
4. **Power formatting**: Adds "MW" suffix for generation/demand projects
5. **Similarity grouping**: Groups projects with similar names (85% similarity threshold)

## Output Files

- `output/from_new_source/final_output_by_new_coes_<timestamp>.xlsx` - Processed data from new platform
- `output/final_extraction/final_output_by_old_coes_<timestamp>.xlsx` - Final combined output from old platform
- `output/extraction_record/<timestamp>.parquet` - Raw extraction record for reproducibility

## Notes

- The script runs Chrome in headless mode by default for efficiency
- Excel files will not be overwritten if open; the script waits until the file is closed
- Similarity grouping results are saved to text files in `output/similar/`
- The old COES platform extraction includes delays (`time.sleep(8)`) between requests to avoid rate limiting