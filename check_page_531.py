import os
import sys
sys.path.append(os.getcwd())
from db_ops.crud_mushaf import get_mushaf_page_data

def check():
    page_num = 531
    print(f"--- Data for Page {page_num} ---")
    data = get_mushaf_page_data(page_num)
    for l in data:
        print(f"Line {l['line_number']}: Type={l['line_type']}, Surah={l['surah_number']}, Words={len(l['words'])}")

if __name__ == "__main__":
    check()
