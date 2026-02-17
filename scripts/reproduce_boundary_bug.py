import os
import sys
import json

sys.path.append(os.getcwd())

from db_ops.crud_mushaf import get_mushaf_page_data, align_mushaf_lines_with_timestamps

def reproduce():
    surah_number = 53
    # Simulating wbw_timestamps
    # We know Surah 53 starts on line 15 of Page 525 (surah_name)
    # and Line 1 of Page 526 (basmallah), Line 2 (ayah 1)
    
    print(f"--- Reproduction for Surah {surah_number} ---")
    
    pages = [525, 526]
    lines_by_page = {}
    
    # Mock timestamps for Surah 53 Ayah 1 (which is on page 526)
    # Ayah 1 starts around 5 seconds in real life
    wbw_timestamps = {
        1: [[1, 5000, 6000]] # Ayah 1, Word 1: 5s to 6s
    }
    
    for p_num in pages:
        p_data = get_mushaf_page_data(p_num)
        filtered = [l for l in p_data if l["surah_number"] == surah_number or (l["words"] and any(w["surah"] == surah_number for w in l["words"]))]
        aligned = align_mushaf_lines_with_timestamps(filtered, wbw_timestamps)
        lines_by_page[p_num] = aligned
        
        print(f"Page {p_num} has {len(aligned)} lines for Surah {surah_number}")
        for l in aligned:
            print(f"  Line {l['line_number']}: {l['line_type']} (Start: {l['start_ms']}, End: {l['end_ms']})")

    # Analyzing current grouping behavior (simulating processes/mushaf_video.py logic)
    print("\n--- Current Grouping Simulation ---")
    for p_idx, p_num in enumerate(sorted(lines_by_page.keys())):
        chunk = lines_by_page[p_num]
        valid_starts = [l["start_ms"] for l in chunk if l["start_ms"] is not None]
        valid_ends = [l["end_ms"] for l in chunk if l["end_ms"] is not None]
        
        if not valid_starts or not valid_ends:
            if p_idx == 0:
                print(f"Page {p_num} is the FIRST page but has NO TIMESTAMPS. Grouping might fail or use fallback.")
            else:
                print(f"Page {p_num} has NO TIMESTAMPS. Grouping will SKIP this page in mushaf_video.py!")
        else:
            print(f"Page {p_num} groups correctly (Start: {min(valid_starts)}, End: {max(valid_ends)})")

if __name__ == "__main__":
    reproduce()
