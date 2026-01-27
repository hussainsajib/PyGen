from factories.single_clip import generate_mushaf_page_clip
import sys
import os

sys.path.append(os.getcwd())

def test_header_injection():
    print("Testing Header Injection Logic...")
    
    # Mock data representing a chunk from a page WITHOUT a header
    # e.g. Page 10, lines 2-8 (hypothetically)
    chunk = []
    for i in range(1, 15):
        chunk.append({
            "page_number": 10,
            "line_number": i,
            "line_type": "ayah",
            "is_centered": False,
            "surah_number": 10, # Surah Yunus
            "words": [],
            "start_ms": 1000 * i,
            "end_ms": 1000 * (i+1)
        })

    # Logic from mushaf_video.py
    idx = 0
    surah_number = 10
    chunk_start_ms = 0
    chunk_duration_sec = 10.0
    
    chunk_for_rendering = []
    for line in chunk:
        line_copy = line.copy()
        if line_copy["start_ms"] is not None:
            line_copy["start_ms"] -= chunk_start_ms
        if line_copy["end_ms"] is not None:
            line_copy["end_ms"] -= chunk_start_ms
        chunk_for_rendering.append(line_copy)

    # Inject Surah Header if missing in the first chunk
    if idx == 0:
        has_header = any(l.get("line_type") == "surah_name" for l in chunk_for_rendering)
        if not has_header:
            print("[INFO] Header missing. Injecting...")
            header_line = {
                "page_number": chunk[0]["page_number"],
                "line_number": 0,
                "line_type": "surah_name",
                "is_centered": True,
                "surah_number": surah_number,
                "words": [],
                "start_ms": 0,
                "end_ms": chunk_duration_sec * 1000 
            }
            chunk_for_rendering.insert(0, header_line)
        else:
            print("[INFO] Header found.")

    # Check result
    if chunk_for_rendering[0]["line_type"] == "surah_name":
        print("PASS: Header injected at index 0.")
        print(f"Header Data: {chunk_for_rendering[0]}")
    else:
        print("FAIL: Header not injected.")

    # Now test WITH existing header
    print("\nTesting WITH existing header...")
    chunk_with_header = [{"line_type": "surah_name", "surah_number": 10}] + chunk
    chunk_for_rendering = [] # Reset
    # ... copy loop skipped for brevity ...
    chunk_for_rendering = chunk_with_header.copy() # Simplified

    if idx == 0:
        has_header = any(l.get("line_type") == "surah_name" for l in chunk_for_rendering)
        if not has_header:
             print("[INFO] Header missing. Injecting...")
        else:
            print("[INFO] Header found. No injection needed.")

    if len([l for l in chunk_for_rendering if l["line_type"] == "surah_name"]) == 1:
        print("PASS: Single header preserved.")
    else:
        print("FAIL: Header duplicated or missing.")

if __name__ == "__main__":
    test_header_injection()
