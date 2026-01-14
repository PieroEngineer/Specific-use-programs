import os
import shutil

def copy_xls_files(file_names, source_folder, destination_folder):
    """
    Search for .xls files by name inside source_folder (including subfolders)
    and copy them to destination_folder.

    Parameters:
    - file_names (list[str]): List of .xls filenames to search for (case-insensitive).
    - source_folder (str): Path to search in (including subfolders).
    - destination_folder (str): Path where found files will be copied.
    """
    # Normalize file names for case-insensitive match
    file_names_lower = [name.lower() for name in file_names]

    if not os.path.exists(destination_folder):
        os.makedirs(destination_folder)

    found_count = 0

    for root, _, files in os.walk(source_folder):
        for file in files:
            if file.lower() in file_names_lower:
                source_path = os.path.join(root, file)
                dest_path = os.path.join(destination_folder, file)

                shutil.copy2(source_path, dest_path)  # keep metadata
                found_count += 1
                print(f"Copied: {source_path} → {dest_path}")

    print(f"Total files copied: {found_count}/{len(file_names)}")

files_to_find = [
    'files_to_find.xls'
]

source_dir = r"source_dir"
destination_dir = r"C:\destination_dir"

copy_xls_files(files_to_find, source_dir, destination_dir)

