
# Translate PDF First Pages to a Word Document

This utility extracts the **first page** of every PDF in a folder, converts each to a PNG image using **pdf2image** (Poppler required), and inserts those images into a single **Word (.docx)** file with a custom header and footer. It is implemented in Python using `python-docx` and writes the output into a `Resultado` directory. citeturn2search1

---

## Features
- Scans a folder for `*.pdf` files and builds a list of paths. citeturn2search1
- Converts **only the first page** of each PDF to a PNG image (fast preview workflow). citeturn2search1
- Creates a Word document with **zero margins** and inserts **header** and **footer** images from the `standart` folder. citeturn2search1
- Places each PDF image **centered** on its own page, at **Inches(5)** width. citeturn2search1

---

## Prerequisites
- **Python 3.9+** (tested with modern versions)
- **Poppler** installed on your system:
  - Windows: set `poppler_path` to the `bin` directory (e.g., `poppler-24.08.0\\Library\\bin`) or update the script accordingly. citeturn2search1
  - macOS/Linux: install Poppler via your package manager (ensure `pdftoppm`/`pdftocairo` are on `PATH`), then **remove** or **adapt** the `poppler_path` argument in `convert_from_path(...)` in the script. citeturn2search1

---

## Installation
1. Create and activate a virtual environment (optional but recommended).
2. Install Python dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Prepare the following folders **next to the script** (they are referenced explicitly by the code):
   - `Entrada` — place input PDFs here. citeturn2search1
   - `Resultado` — output folder where `document_file.docx` will be saved. *(Create it if it doesn't exist)*. citeturn2search1
   - `standart` — place `header.png` and `footer.png` used by the Word header/footer. citeturn2search1

Folder layout example:
```
project/
├─ translate_pictures_to_pdfs.py
├─ requirements.txt
├─ Entrada/
│  ├─ file1.pdf
│  └─ file2.pdf
├─ Resultado/
└─ standart/
   ├─ header.png
   └─ footer.png
```

---

## Usage
### Option A: Run as a script (defaults)
The script uses `Entrada` as the input folder and writes `document_file.docx` to `Resultado` by default:
```bash
python translate_pictures_to_pdfs.py
```
You will see a success or error message printed to the console. citeturn2search1

### Option B: Call from another Python module
```python
from translate_pictures_to_pdfs import process_folder_to_word

# Use a custom folder and output file name
output_path = process_folder_to_word(
    folder_path=r"Entrada",
    output_doc_name="my_document.docx",
)
print(output_path)
```
- `process_folder_to_word(folder_path, output_doc_name)` raises `FileNotFoundError` if there are no PDFs. citeturn2search1

---

## Configuration notes
- **Poppler path**: The script passes `poppler_path=r'poppler-24.08.0\\Library\\bin'` to `convert_from_path(...)`. Adjust this to your machine or remove the parameter if Poppler is on `PATH`. citeturn2search1
- **Header & footer images**: The script expects `standart/header.png` and `standart/footer.png`. Width is set to `Inches(9.0)`. citeturn2search1
- **Word page margins**: All margins (top/bottom/left/right, header/footer distances) are set to `0`. citeturn2search1
- **Image width**: Each PDF preview image is inserted at `Inches(5)` and centered. citeturn2search1

---

## Troubleshooting
- **No PDF files found**: Ensure PDFs are inside `Entrada`. The function throws `FileNotFoundError` when the list is empty. citeturn2search1
- **Poppler not found / conversion fails**: Confirm Poppler is installed and the path is correct. On Unix, ensure `pdftoppm` is on `PATH`.
- **Header/footer not displayed**: Verify `standart/header.png` and `standart/footer.png` exist and are valid images. Paths are hard‑coded. citeturn2search1
- **Output folder missing**: Create `Resultado` manually; the script does not auto‑create it. citeturn2search1

---

## Credits
- Built by **Piero Olivas**.
