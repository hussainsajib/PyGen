from db_ops.crud_mushaf import get_mushaf_page_data

def find_lines():
    # 110:3
    print("--- Page 603 (Surah 110) ---")
    data_603 = get_mushaf_page_data(603)
    for l in data_603:
        words_110_3 = [w for w in l["words"] if w["surah"] == 110 and w["ayah"] == 3]
        if words_110_3:
            text = "".join([w["text"] for w in words_110_3])
            print(f"Line {l['line_number']}: {text}")
            for w in words_110_3:
                print(f"Word {w['word']}: {w['text']}")

    # 2:5
    print("--- Page 2 (Surah 2) ---")
    data_2 = get_mushaf_page_data(2)
    for l in data_2:
        words_2_5 = [w for w in l["words"] if w["surah"] == 2 and w["ayah"] == 5]
        if words_2_5:
            text = "".join([w["text"] for w in words_2_5])
            print(f"Line {l['line_number']}: {text}")
            for w in words_2_5:
                print(f"Word {w['word']}: {w['text']}")

if __name__ == "__main__":
    find_lines()
