from fuzzywuzzy import fuzz
import os

def fuzzy_match_files(file1_path: str, file2_path: str, output_path: str, threshold: int = 80):
    """
    Matches strings from two text files using fuzzy string matching.
    Saves pairs with similarity >= threshold to output file.
    
    Parameters:
    - file1_path: Path to first text file (one string per line)
    - file2_path: Path to second text file (one string per line)
    - output_path: Path for output file with matched pairs
    - threshold: Minimum similarity score (0-100) to consider a match
    """
    # Read and clean strings from both files
    def read_lines(filepath):
        if not os.path.exists(filepath):
            print(f"File not found: {filepath}")
            return []
        with open(filepath, 'r', encoding='utf-8') as f:
            return [line.strip() for line in f if line.strip()]
    
    lines1 = read_lines(file1_path)
    lines2 = read_lines(file2_path)
    
    if not lines1 or not lines2:
        print("One or both files are empty or not found.")
        return
    
    matches = []

    s2_already_found = []
    
    # Compare each string from file1 with each from file2
    for s1 in lines1:
        best_score = 0
        best_match = None
        
        for s2 in lines2:
            if s2 not in s2_already_found:
                score = fuzz.ratio(s1, s2[2:])  #.token_sort_ratio(s1, s2[2:])  # Can use fuzz.token_sort_ratio() for better results
                if score > best_score:
                    best_score = score
                    best_match = s2
        
        s2_already_found.append(best_match)

        # if best_score >= threshold:
        #     matches.append((s1, best_match, best_score))
        matches.append((s1, best_match, best_score))
    
    # Sort by similarity score (descending)
    matches.sort(key=lambda x: x[2], reverse=True)
    
    # Write results
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(f"Fuzzy Matches (threshold: {threshold}%)\n")
        f.write(f"{'='*60}\n")
        for s1, s2, score in matches:
            f.write(f"{score:3}% | {s1}  -->  {s2}\n")
    
    print(f"Matching complete. {len(matches)} pairs saved to {output_path}")

# Example usage
if __name__ == "__main__":
    fuzzy_match_files(
        file1_path=r"Homologating_names\input\txt\pme_names.txt",
        file2_path=r"Homologating_names\input\txt\zmeasure_names.txt",
        output_path=r"Homologating_names\output\related_v31.txt",
        threshold=50
    )