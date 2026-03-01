import os
import sys
sys.path.append(os.getcwd())
from db_ops.crud_mushaf import get_mushaf_page_data

def test_propagation():
    page_num = 531
    data = get_mushaf_page_data(page_num)
    
    print("--- Before Propagation (current crud) ---")
    for l in data:
        print(f"Line {l['line_number']}: Type={l['line_type']}, Surah={l['surah_number']}")
        
    print("\n--- After Propagation (simulated) ---")
    last_known_surah = None
    for l in data:
        if l['surah_number'] and l['surah_number'] != '':
            last_known_surah = l['surah_number']
        elif l['words']:
            last_known_surah = l['words'][0]['surah']
            l['surah_number'] = last_known_surah
        elif last_known_surah:
            l['surah_number'] = last_known_surah
            
        print(f"Line {l['line_number']}: Type={l['line_type']}, Surah={l['surah_number']}")

if __name__ == "__main__":
    test_propagation()
