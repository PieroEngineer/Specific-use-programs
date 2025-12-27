# Mini Project: Collect and Organize Meter XLS Files

This mini project provides a robust utility to **find specific `.xls` files** under a source tree (Path A), skip unwanted folders, and **copy them into organized subfolders** under a destination tree (Path B). It auto-renames duplicates and prints detailed trace information.

Main script:
- **`getMedidores_mod2.py`** – Function `collect_required_xls()` walks the source, filters by required filenames, ignores specified directories, and copies the files into a destination folder whose first-level names mirror the first folder in the file’s relative path.

---

## What the script does

1. **Search & filter**
   - Validates that Path A exists.
   - Keeps only requested **`.xls`** filenames (warns if non-`.xls`).
   - Supports **case-insensitive** matching.
   - Skips any folders listed in `ignore_dirs`.

2. **Organize & copy**
   - For each match, determines the **relative path** (to Path A).
   - Extracts the **first folder name** ("Name A").
   - Creates a subfolder under Path B named **Name A** and copies the file there.
   - If a duplicate filename exists, auto-renames: `name (1).xls`, `name (2).xls`, etc.

3. **Summary output**
   - Prints how many files were copied per **Name A** and their destination paths.

---

## Inputs & Outputs

- **Inputs:**
  - `required_filenames`: tuple of exact `.xls` filenames to search.
  - `path_a`: source root (Path A).
  - `path_b`: destination root (Path B).
  - `ignore_dirs`: tuple of folder names to skip.
  - `case_sensitive`: whether to match filenames case-sensitively.

- **Output:**
  - Files copied into `path_b/<Name A>/...` with duplicate-safe renaming.
  - Printed summary of results.

---

## Quick start

1. Create and activate a virtual environment (recommended):
```bash
python -m venv .venv
# Windows
.venv\\Scripts\\activate
# macOS/Linux
source .venv/bin/activate
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Run the script:
```bash
python getMedidores_mod2.py
```

Edit variables at the bottom of the script:
```python
searched_files = (
    'names_of_meters.xls',
)
year_path   = r"Z:\\2025"     # Path A
output_path = r"Output\\2025"  # Path B
ignored_folders = ('Excluded files',)
collect_required_xls(
    searched_files,
    year_path,
    output_path,
    ignore_dirs=ignored_folders,
    case_sensitive=False,
)
```

---

## Suggested structure
```
.
├── getMedidores_mod2.py
├── Output/
│   └── 2025/
└── requirements.txt
```

---

## Troubleshooting
- **No files copied**: Check that filenames are exact and exist under Path A; confirm case sensitivity setting.
- **Permission denied**: Ensure read access to Path A and write access to Path B.
- **Large trees**: Consider narrowing `ignore_dirs` or running during off-hours.

---

## Credits
- Built by **Piero Olivas**.
