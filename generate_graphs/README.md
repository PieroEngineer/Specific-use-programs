# Mini Project: Batch Graph Generator (Local & SharePoint)

This mini project scans Excel/CSV files either **from a local folder** or **from SharePoint**, computes three power series (`Pact`, `Prea`, `Ps`) from input columns, and **generates line charts** saved by category.

Main script:
- **`generate_graphs.py`** – Uses PyQt dialogs to select folders, reads files, computes derived metrics, and saves charts. It can also authenticate to SharePoint to list and process files remotely.

---

## What the script does

1. **Data access**
   - **Local mode**: recursively maps files in a selected folder and reads `.csv`, `.xls`, `.xlsx` (CSV is expected with `;` separator).
   - **SharePoint mode**: authenticates with `office365` client, walks folders, and streams each file into memory for processing.

2. **Computation (`calculation_function`)**
   - Calculates:
     - `Pact = (Column1 - Column2) * 0.004`
     - `Prea = (Column3 + Column4 - Column5 - Column6) * 0.004`
     - `Ps = sqrt(Pact^2 + Prea^2)`
   - Returns a dataframe with the first column (time/index) plus `Pact`, `Prea`, `Ps`.

3. **Chart generation**
   - For each metric, creates a line chart (`matplotlib`) and saves a PNG into subfolders:
     - `Potencia activa` (Pact)
     - `Potencia reactiva` (Prea)
     - `Potencia aparente` (Ps)
   - Filenames follow: `<base_filename>_<metric>.png`.

4. **Progress & logs**
   - Displays a CLI progress bar with `colorama`.
   - Prints a summary of successes/failures.

---

## Inputs & Outputs

- **Input (local)**: Any folder containing `.csv`, `.xls`, `.xlsx` files. CSV must use `;` as separator.
- **Input (SharePoint)**: Files under your SharePoint site (script uses server-relative URLs).
- **Output**: PNG charts saved under the selected output folder, grouped by metric.

Folder structure (example):
```
.
├── generate_graphs.py
├── resources/ (optional)
└── output/
    ├── Potencia activa/
    ├── Potencia reactiva/
    └── Potencia aparente/
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

3. Run (Local mode):
```bash
python generate_graphs.py
```
- When prompted, select the **input** folder and then the **output** folder.

4. Run (SharePoint mode):
- In `main()`, set `from_local = False` and provide your `mail`/`password`.
- Then run:
```bash
python generate_graphs.py
```
- Choose the **output** folder when prompted.

---

## Configuration notes

- **PyQt file dialogs** open native folder pickers; no CLI args are required.
- **Excel reading** uses `pandas.read_excel`; ensure your files have the expected columns: `Column1`–`Column6` and a first column that can be parsed as time.
- **CSV reading** uses `sep=';'`.
---

## Troubleshooting

- **Missing columns**: Ensure input files contain `Column1`–`Column6`. Rename columns or adapt `calculation_function`.
- **No charts generated**: Check the first column parses as datetime; invalid times can prevent plotting.
- **SharePoint auth errors**: Verify credentials and that your user has permission to the site/library.
- **PyQt issues on servers**: GUI dialogs require a desktop environment; run locally or replace with CLI args if needed.

---

## Credits
- Built by **Piero Olivas**.
