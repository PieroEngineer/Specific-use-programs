# SAP Asset Data Extraction Tool

A Python tool for extracting asset information from SAP GUI using RPA (Robotic Process Automation). The tool automates SAP transactions, navigates through multiple tabs, and extracts asset attributes including status, classifications, dates, and cost center information.

## Overview

This project consists of two Python modules that work together to:

1. **Extract asset data from SAP** (`searching_by_code.py`) using SAP GUI scripting
2. **Map extracted data to destinations** (`connect_destination.py`) by matching codes and serial numbers

## Files

| File | Description |
|------|-------------|
| `searching_by_code.py` | Automates SAP GUI to extract asset information for a list of codes (IH08 transaction) |
| `connect_destination.py` | Processes extracted data, maps assets to destinations using SAP codes and serial numbers |

## Features

### SAP Automation (`searching_by_code.py`)
- Connects to SAP GUI via COM interface (Windows only)
- Automates login with user-provided credentials
- Navigates through SAP transaction `IH08`
- Extracts data from multiple tabs (Technical Object, Location, Cost Center, Classification)
- Handles tab navigation and field extraction automatically
- Exports results to Excel

### Data Mapping (`connect_destination.py`)
- Primary matching: `Code` → `Código SAP Activo`
- Secondary matching: For entries with `NO TIENE` code, matches via serial numbers
- Generates final Excel with destination information

## Requirements

- **Windows OS** (SAP GUI scripting only works on Windows)
- SAP GUI client installed and configured
- SAP GUI scripting enabled (see setup instructions below)
- Python 3.8+
- Required Python packages:
  - `pandas`
  - `openpyxl`
  - `pywin32` (for SAP COM interface)

## SAP GUI Scripting Setup

Before using this tool, you must enable SAP GUI scripting:

1. Open SAP GUI
2. Go to **Options** (Alt + F12 or click the SAP icon → Options)
3. Navigate to **Accessibility & Scripting** → **Scripting**
4. Check the following:
   - ✅ Enable scripting
   - ✅ Enable scripting for recording (optional)
   - ⚠️ Uncheck "Notify when a script attaches to SAP GUI" (to avoid popups)
5. Click **OK**

## Directory Structure

```
project/
├── searching_by_code.py
├── connect_destination.py
├── input/
│   ├── bases_with_codes.xlsx    # Source file with asset codes
│   └── file.xlsx                 # Destination mapping reference
├── output/
│   ├── extraction.xlsx           # Raw extracted SAP data
│   └── detection.xlsx            # Final data with destinations
```

## Usage

### 1. Extract data from SAP

```bash
python searching_by_code.py
```

You will be prompted for:
- **Username**: Your SAP username
- **Password**: Your SAP password (entered as plain text in this version)

The script will:
- Connect to the SAP system (`ERP_Productivo`)
- Navigate to transaction `IH08`
- For each code in `input/bases_with_codes.xlsx`:
  - Enter the code
  - Extract data from 4 tabs (class, manufacturer, cost center, asset classification)
  - Navigate back and continue
- Save results to `output/extraction.xlsx`

### 2. Map extracted data to destinations

```bash
python connect_destination.py
```

This script:
- Reads `output/extraction.xlsx` (extracted SAP data)
- Reads `input/file.xlsx` (destination mapping reference)
- Matches `Code` with `Código SAP Activo`
- For `NO TIENE` codes, matches by serial number (`serie_number`)
- Outputs `output/detection.xlsx` with destinations assigned

## Configuration in `searching_by_code.py`

The script requires specific SAP GUI element IDs to be configured. Currently, these are placeholders (`''`):

```python
nav_collection = {
    'transaction_combo_id': window_base + '',   # e.g., "wnd[0]/usr/ctxtOKCODE"
    'execution_button_id': window_base + '',    # e.g., "wnd[0]/usr/btnEXECUTE"
    'confirmation_button_id': window_base + '', # e.g., "wnd[0]/tbar[0]/btn[8]"
    'go_back_id': window_base + '',             # e.g., "wnd[0]/tbar[0]/btn[3]"
    'code_textfield_id': user_base + ''         # e.g., "wnd[0]/usr/ctxtEQUNR"
}

status_textfield_id = user_base + ''  # e.g., "wnd[0]/usr/ctxtSTATU"
```

### Finding SAP Element IDs

To configure the IDs:
1. Open SAP GUI transaction `IH08`
2. Press **Ctrl + Shift + F7** (or enable Script Recording via Options)
3. Perform the actions you want to automate
4. The script recording will show the element IDs
5. Update the configuration dictionaries accordingly

### Tab Configuration

The script extracts data from tabs in this order (positions 1, 2, 3, 5):

```python
text_field_collection = (
    # Tab 1 (General/Technical Object)
    {
        'class': tab_id(1) + '',           # Equipment class
        'manufacturer': tab_id(1) + '',    # Manufacturer
        'type_nomination': tab_id(1) + '', # Type/nomination
        'serie_number': tab_id(1) + '',    # Serial number
        'commissioning_date': tab_id(1) + ''  # Commissioning date
    },
    # Tab 2 (Location)
    {
        'site_center': tab_id(2) + ''      # Site/center
    },
    # Tab 3 (Cost Center)
    {
        'cost_center': tab_id(3) + '',     # Cost center
        'fixed_asset': tab_id(3) + ''      # Fixed asset number
    },
    # Tab 5 (Classification)
    {
        'ciber_asset_class': tab_id(5) + ''  # CIBER asset classification
    }
)
```

## Key Functions

### `searching_by_code.py`

| Function | Description |
|----------|-------------|
| `generate_sessions(username, password)` | Connects to SAP GUI and logs in |
| `select_to_transaction(combo_id, selection, session)` | Navigates to a SAP transaction code |
| `set_txt(field_id, text_value, session)` | Sets text in an input field |
| `click_btn(button_id, session)` | Clicks a button |
| `select_tab(selectable_id, session)` | Selects/activates a tab |
| `get_text(textfield_id, session)` | Reads text from a field |
| `get_credentials()` | Prompts user for SAP credentials |

### `connect_destination.py`

| Function/Logic | Description |
|----------------|-------------|
| `merge()` primary | Matches `Code` with `Código SAP Activo` |
| Secondary match | Maps `NO TIENE` codes via `serie_number` |
| Output generation | Creates final Excel with `destiny` column |

## Input File Formats

### `input/bases_with_codes.xlsx`
| Column | Description |
|--------|-------------|
| `Code` | SAP asset codes (e.g., `EQU-12345` or `NO TIENE`) |
| *Other columns* | Additional data preserved in output |

### `input/file.xlsx`
| Column | Description |
|--------|-------------|
| `Código SAP Activo` | SAP asset code for primary matching |
| `Serie` | Serial number for secondary matching |
| `Destino` | Destination/location for the asset |

## Output Files

| File | Description |
|------|-------------|
| `output/extraction.xlsx` | Raw SAP data including: Code, Status, class, manufacturer, type_nomination, serie_number, commissioning_date, site_center, cost_center, fixed_asset, ciber_asset_class |
| `output/detection.xlsx` | Merged data with `destiny` column added |

## Notes

- **Windows only**: SAP GUI COM interface only works on Windows
- **SAP GUI must be running**: The script connects to an existing SAP GUI instance
- **SAP GUI Scripting must be enabled**: See setup instructions above
- **Credentials**: Currently entered as plain text (consider using `getpass` for password masking)
- **Error handling**: Individual asset extraction failures are caught; script continues with next code
- **Empty IDs**: The script requires proper SAP GUI element IDs configured before use

## Troubleshooting

| Issue | Solution |
|-------|----------|
| `win32com.client.GetObject("SAPGUI")` fails | Install SAP GUI client and ensure it's running |
| Cannot find element IDs | Use SAP Script Recording (Ctrl+Shift+F7) to identify correct IDs |
| Connection timeout | Check network connectivity to ERP_Productivo system |
| Permission errors | Verify your SAP user has access to transaction IH08 |
| `NO TIENE` not matching | Ensure serial numbers in `file.xlsx` exactly match extracted `serie_number` |