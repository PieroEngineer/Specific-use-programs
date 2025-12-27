# Mini Project: IDCOS Anexo 2 Downloader & Merger

This mini project interactively downloads **IDCOS – Anexo 2 (Resumen de operación)** Excel files from the **COES** (A public Peru’s System Economic Operation Committee) website for a chosen day and its previous day, merges the two into a single, tidy sheet, and saves the result for analysis.

Main script:
- **`Get_data.py`** – Prompts for year/month/day (in Spanish), fetches two Excel files via HTTP, reads/cleans them with `pandas`, and writes the final consolidated workbook.

---

## What the script does

1. **User input loop** (in Spanish): asks for año, mes, día with validation.
2. **Builds COES download URLs** for the chosen day and the previous day, e.g.:
   `https://www.coes.org.pe/portal/browser/download?url=Post%20Operación/Reportes/IDCOS/<AÑO>/<MM>_<MES>/Día <DD>/Anexo2_Resumen_operacion_<AAAAMMDD>.xlsx`
3. **Downloads both Excel files** with `requests` and saves them into `output/`.
4. **Reads the sheets** using `pandas` (`openpyxl` engine), selecting rows/columns of interest.
5. **Merges** the last row of the previous-day file with the current day’s 48 records.
6. **Normalizes the first ‘HORA’ row** when it’s a `datetime` by keeping only the time.
7. **Writes** the final Excel to `output/final/Anexo2_Resumen_operacion_<YYYY>-<M>-<D>.xlsx`.

Utility function:
- `image_to_ascii(image_path, output_width=100)`: converts an image to ASCII (optional, for console branding).

---

## Inputs & Outputs

- **Input (downloaded automatically):** Two Excel files (chosen day and previous day) from COES.
- **Output:** `output/final/Anexo2_Resumen_operacion_<YYYY>-<M>-<D>.xlsx`

Folder structure (suggested):
```
.
├── Get_data.py
├── output/
│   ├── final/
│   └── (downloaded Excel files)
└── resources/
    └── (optional image for ASCII output)
```

---

## Quick start

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

3. Run the script:
```bash
python Get_data.py
```
Follow the prompts (año/mes/día). The script will download, merge, and save the final Excel.

---

## Configuration notes

- The URL path uses Spanish month names (`ENERO`, `FEBRERO`, ..., `DICIEMBRE`) and the *Día* directory under `Post Operación/Reportes/IDCOS`.
- Filenames are `Anexo2_Resumen_operacion_YYYYMMDD.xlsx`.
- Reading uses `skiprows=7`, `nrows=48`, and trims columns up to `MW`. Adjust these if COES changes the report layout.

---

## Troubleshooting

- **404 or download error**: The file may not yet be published for that day; try another date.
- **`openpyxl` read errors**: Verify the file is valid and not an HTML error page saved as `.xlsx`.
- **Unexpected columns/rows**: The report structure may have changed; adjust `skiprows`, `nrows`, and column slicing logic.

---

## Credits
- Built by **Piero Olivas**.
