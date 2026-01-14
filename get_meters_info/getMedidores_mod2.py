import os
import shutil
from pathlib import Path
from typing import Dict, List, Tuple

def collect_required_xls(
    required_filenames: Tuple[str, ...],
    path_a: str | Path,
    path_b: str | Path,
    ignore_dirs: Tuple[str, ...] = (),
    *,
    case_sensitive: bool = True
) -> Dict[str, List[Path]]:
    """
    Recursively search Path A for the required .xls files, skipping any folders
    whose names are in `ignore_dirs`. For every file found:
      - Determine the relative path (to Path A) where it was found (*print*),
      - Take the first folder name in that relative path "Name A" (*print*),
      - Create a folder under Path B named "Name A" (*print*; this is the 'folder extra'),
      - Copy the file into that folder. If a duplicate filename exists, auto-rename.

    Prints tracking lines for the steps marked with '*' and some extra info.

    Parameters
    ----------
    required_filenames : Tuple[str, ...]
        Exact filenames (including extension) to search for. Must be `.xls`.
    path_a : str | Path
        Root directory to search in (source).
    path_b : str | Path
        Root directory where copies will be created (destination).
    ignore_dirs : Tuple[str, ...], optional
        Folder names to skip anywhere in the tree (matched by exact name).
    case_sensitive : bool, optional
        If False, match required filenames case-insensitively.

    Returns
    -------
    Dict[str, List[Path]]
        Mapping from 'Name A' (first folder within Path A) to the list of copied file paths in Path B.
        Uses '__ROOT__' for files that sit directly under Path A (no subfolder).

    Raises
    ------
    FileNotFoundError
        If path_a does not exist or is not a directory.
    """

    # --- Resolve & validate roots
    src_root = Path(path_a).resolve()
    dst_root = Path(path_b).resolve()

    if not src_root.exists() or not src_root.is_dir():
        raise FileNotFoundError(f"Path A does not exist or is not a directory: {src_root}")

    dst_root.mkdir(parents=True, exist_ok=True)

    # --- Normalize required filenames
    def norm(s: str) -> str:
        return s if case_sensitive else s.lower()

    # Keep only .xls (warn about others)
    required_xls = []
    for name in required_filenames:
        if name.lower().endswith(".xls"):
            required_xls.append(name)
        else:
            print(f"[WARN] Skipping non-.xls required name: {name}")

    if not required_xls:
        print("[INFO] No valid .xls filenames provided. Nothing to do.")
        return {}

    required_set = set(norm(n) for n in required_xls)
    ignore_set = set(ignore_dirs)  # directory names, matched exactly

    print("=== SEARCH SETTINGS ===")
    print(f"Path A (source): {src_root}")
    print(f"Path B (destination base): {dst_root}")
    print(f"Required .xls filenames: {required_xls}")
    print(f"Ignored folder names: {sorted(ignore_set) if ignore_set else '(none)'}")
    print(f"Case-sensitive matching: {case_sensitive}")
    print("=======================\n")

    copied_index: Dict[str, List[Path]] = {}

    def safe_copy(src: Path, dst_dir: Path) -> Path:
        """
        Copy `src` into `dst_dir`. If a file with the same name already exists,
        append ' (1)', ' (2)', ... before the extension.
        Returns the final destination path.
        """
        dst_dir.mkdir(parents=True, exist_ok=True)
        candidate = dst_dir / src.name
        if not candidate.exists():
            shutil.copy2(src, candidate)
            return candidate

        stem, suffix = src.stem, src.suffix
        k = 1
        while True:
            candidate = dst_dir / f"{stem} ({k}){suffix}"
            if not candidate.exists():
                shutil.copy2(src, candidate)
                return candidate
            k += 1

    # Walk the tree
    for root, dirnames, filenames in os.walk(src_root):
        # Prune ignored dirs in-place for os.walk
        pruned = [d for d in dirnames if d in ignore_set]
        if pruned:
            for d in pruned:
                print(f"[SKIP] Ignoring directory: {Path(root) / d}")
        dirnames[:] = [d for d in dirnames if d not in ignore_set]

        # Prepare filename comparison
        if case_sensitive:
            candidates = set(filenames)
        else:
            # map lower->originals to preserve original name for display
            lower_map = {fn.lower(): fn for fn in filenames}
            candidates = set(lower_map.keys())

        # Check each required filename
        for req in required_set:
            hit = None
            if case_sensitive:
                if req in candidates:
                    hit = req
            else:
                if req in candidates:
                    hit = lower_map[req]

            if hit is None:
                continue  # not found in this folder

            # Build paths
            src_file = Path(root) / (hit if case_sensitive else lower_map[req])

            # * Print: file found path
            print(f"[*] File found*: {src_file}")

            # Compute relative path to Path A
            rel_dir = src_file.parent.relative_to(src_root)
            # * Print: relative path
            print(f"[*] Relative path* (to Path A): {rel_dir if str(rel_dir) != '.' else '(.)'}")

            # Extract first folder name (Name A)
            parts = rel_dir.parts
            name_a = parts[0] if len(parts) > 0 else "__ROOT__"  # fallback if file is at the root of Path A
            # * Print: first folder name
            print(f"[*] First folder name* (Name A): {name_a}")

            # Destination folder inside Path B (this is the "folder extra")
            dst_dir = dst_root / name_a
            # * Print: folder extra path
            print(f"[*] Folder extra* to create/use: {dst_dir}")

            # Copy (with duplicate-safe rename)
            final_dst = safe_copy(src_file, dst_dir)
            if final_dst.name != src_file.name:
                print(f"[COPY] Duplicate detected. Copied with rename to: {final_dst}")
            else:
                print(f"[COPY] Copied to: {final_dst}")

            # Track results
            copied_index.setdefault(name_a, []).append(final_dst)

        # Optional: extra trace line per visited folder
        # print(f"[TRACE] Visited: {root}")

    # Summary
    print("\n=== SUMMARY ===")
    if not copied_index:
        print("No required files were found.")
    else:
        total = sum(len(v) for v in copied_index.values())
        print(f"Total files copied: {total}")
        for k, v in copied_index.items():
            print(f"  - {k}: {len(v)} file(s)")
            for p in v:
                print(f"      • {p}")
    print("================\n")

    return copied_index


if __name__ == "__main__":
    # # Example usage (replace with your actual paths and filenames)
    # required = ("Report.xls", "Data.xls", "Metrics.xls")
    # path_A = r"/path/to/search/root"     # Path A
    # path_B = r"/path/to/destination"     # Path B
    # ignore = ("node_modules", ".git", "__pycache__")

    searched_files = (
    'names_of_meters.xls',
    )

    year_path = r"Z:\2025"

    output_path = r'Output\2025'

    ignored_folders = ('Excluded files')

    collect_required_xls(searched_files, year_path, output_path, ignore_dirs=ignored_folders, case_sensitive=False)