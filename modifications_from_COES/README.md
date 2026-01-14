# Mini Project: COES Data Downloader & Organizer

This mini project automates the download of Excel reports from the **COES** website (A public Peru’s System Economic Operation Committee), merges EO/EPO datasets, cleans and enriches fields, and outputs a consolidated Excel file ready for analysis.

It consists of one main script:

- **`data_organization.py`** – Uses Selenium to navigate COES pages, export Excel files per project type (EO/EPO), concatenates them, standardizes columns and statuses, enriches power values from a local mapping, and saves a final workbook.

---

## What the script does

1. **Web automation with Selenium**
   - Opens the COES EO/EPO pages.
   - Selects a **project type** in the dropdown (e.g., *Generación Convencional*, *Generación No Convencional*, *Transmisión*, *Demanda*).
   - Clicks **Buscar** then **Exportar** to download the Excel report.
   - Handles headless Chrome and automatic download directory.

2. **Data cleaning & integration**
   - Concatenates EO and EPO data by project type.
   - Normalizes fields (e.g., removes trailing parentheses in *Nombre del Estudio*, renames *Zona de Proyecto* → *Zona*).
   - Filters studies by year thresholds depending on EO/EPO code.
   - Recomputes the **Estado** based on *Estado* and *Vigencia* rules.
   - Updates *Nombre del Estudio* and *Estado* in a base Excel.
   - Adds new rows for codes not present in the base and infers **Tipo de Energía** from name prefixes (`C.S.F.` → Solar, `C.H.` → Hidráulica, `C.T.` → Térmica, `C.E.` → Eólica).
   - Enriches **Potencia(MW)** using `input/Potencias.xlsx` for approved or in-review generation studies.

3. **Utility functions**
   - `remove_tildes(text)`: removes accent marks using Unicode normalization.
   - `print_repeated_strings(df, column)`: prints repeated values in a column with counts.

---

## Inputs & Outputs

- **Inputs (downloaded automatically):** COES Excel files per project type, saved under `output/Medium/EO/<tipo>` and `output/Medium/EPO/<tipo>`.
- **Local inputs:**
  - `input/Consulta_Web_EPO_EO_Cambio_J.xlsx` – base workbook used to align and complete fields.
  - `input/Potencias.xlsx` – mapping of *Centrales* to *Potencia Instalada (MW)*.
- **Output:**
  - `output/t20.xlsx` – consolidated Excel with cleaned and enriched data.

---

## Quick start

> **Prerequisites**
> - Google Chrome installed.
> - **ChromeDriver** compatible with your Chrome version at `google_driver/chromedriver-win64/chromedriver.exe` (adjust path if needed).
> - The COES site reachable from your network.

1. Create and activate a virtual environment (recommended):
```bash
python -m venv .venv
# Windows
.venv\Scripts\activate
# macOS/Linux
source .venv/bin/activate
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Prepare folders and files:
```
.
├── data_organization.py
├── input/
│   ├── Consulta_Web_EPO_EO_Cambio_J.xlsx
│   └── Potencias.xlsx
├── output/
│   └── Medium/
│       ├── EO/
│       └── EPO/
├── resources/
│   └── logo-2.jpg
└── google_driver/
    └── chromedriver-win64/
        └── chromedriver.exe
```

4. Run the script:
```bash
python data_organization.py
```
This will:
- Print an ASCII logo.
- Loop project types: `Generación Convencional`, `Generación No Convencional`, `Transmisión`, `Demanda`.
- Download EO/EPO Excel files for each.
- Concatenate, clean, enrich, and save `output/t20.xlsx`.

---

## Configuration notes

- **Headless mode** is enabled by default (`--headless`). Remove it if you need to visually debug browser actions.
- The **download directory** is created under your current working directory.
- If the COES page changes HTML IDs/classes (e.g., spinner or button IDs), you may need to adjust selectors: `cboTipoProyecto`, `btnBuscar`, `btnExportar`, `.spinner`.
- The code expects sheet names like `Consulta_Web_EO`/`Consulta_Web_PO` when reading the exported Excel.

---

## Troubleshooting

- **Chrome/Driver mismatch**: Ensure `chromedriver.exe` matches your installed Chrome version.
- **`selenium.common.exceptions` during clicks**: The page may not be ready; increase waits or use JS click fallback as already implemented.
- **Downloads not appearing**: Confirm the download path exists and that headless Chrome has permission to write.
- **`openpyxl` errors reading Excel**: Verify the file path and sheet names; the code uses `engine='openpyxl'`.
- **Encoding/accents issues**: Use `remove_tildes` to normalize and ensure your data sources are UTF-8.
- **Column not found**: The site/base Excel schema may have changed—check column names expected by the `order_data` logic.

---

## Credits
- Built by **Piero Olivas**.
