# Mini Project: Search and Move XLS Files

This mini project provides a simple utility to **search for specific `.xls` files** within a directory (including subfolders) and copy them to a destination folder while preserving metadata.

---

## What the script does
- Accepts:
  - A list of `.xls` filenames to find (case-insensitive).
  - A source directory to search recursively.
  - A destination directory to copy found files.
- Creates the destination folder if it does not exist.
- Copies files using `shutil.copy2` to preserve original metadata.
- Prints each copied file path and a summary count.

---

## Inputs & Outputs
- **Inputs:**
  - `file_names`: list of filenames (e.g., `['report.xls', 'summary.xls']`).
  - `source_folder`: path to search (including subfolders).
  - `destination_folder`: path where files will be copied.
- **Output:**
  - Files copied to the destination folder.
  - Console log showing copied files and total count.

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
python SearchAndMove.py
```
Edit the variables at the bottom of the script:
```python
files_to_find = ['files_to_find.xls']
source_dir = r"source_dir"
destination_dir = r"C:\\destination_dir"
```

---

## Example usage inside Python
```python
from SearchAndMove import copy_xls_files

files_to_find = ['report.xls', 'summary.xls']
source_dir = r"D:\\data"
destination_dir = r"D:\\backup"

copy_xls_files(files_to_find, source_dir, destination_dir)
```

---

## Troubleshooting
- **File not found**: Ensure filenames match exactly (case-insensitive).
- **Permission errors**: Run with appropriate permissions for source/destination paths.
- **Large directories**: For very large trees, consider adding logging or progress indicators.

---

## Credits
- Built by **Piero Olivas**.
