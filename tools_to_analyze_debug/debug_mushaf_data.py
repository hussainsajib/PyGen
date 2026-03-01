from db_ops.crud_mushaf import get_mushaf_page_data
import sys
import os

sys.path.append(os.getcwd())

def debug_page(page_num):
    print(f"--- Page {page_num} ---")
    data = get_mushaf_page_data(page_num)
    for line in data:
        sn = line['surah_number']
        print(f"Line {line['line_number']}: Type={line['line_type']}, Surah={sn} (Type: {type(sn)})")

if __name__ == "__main__":
    debug_page(1)