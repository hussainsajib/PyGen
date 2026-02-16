import pytest
from db_ops.crud_mushaf import get_mushaf_page_data
from factories.mushaf_utils import assemble_mushaf_line_text

def test_pause_sign_logical_order():
    """
    Verifies that we identify words with multiple glyphs (like pause signs) 
    and that they are in the expected logical order in the database.
    """
    # Surah 110:3, Word 4
    page_603 = get_mushaf_page_data(603)
    line_110_3 = next(l for l in page_603 if l["line_number"] == 10)
    word_4 = next(w for w in line_110_3["words"] if w["word"] == 4)
    
    # Logical order should be [Word Glyph, Pause Sign Glyph]
    assert word_4["text"] == "ﱲﱳ"
    
    # Surah 2:5, Word 5
    page_2 = get_mushaf_page_data(2)
    line_2_5 = next(l for l in page_2 if l["line_number"] == 7)
    word_5 = next(w for w in line_2_5["words"] if w["word"] == 5)
    
    assert word_5["text"] == "ﱧﱨ"

def test_assemble_mushaf_line_text_correctness():
    """
    Verifies that assemble_mushaf_line_text correctly reverses the line 
    while also reversing glyphs within words by virtue of reversing the whole string.
    """
    page_603 = get_mushaf_page_data(603)
    line_110_3 = next(l for l in page_603 if l["line_number"] == 10)
    words = line_110_3["words"]
    
    text = assemble_mushaf_line_text(words)
    
    # Word 4: ﱲﱳ -> Reversed: ﱳﱲ
    # Word 8 Ayah end: ﱷ -> Reversed: ﱷ
    # Order: 4 5 6 7 8 -> Reversed: 8 7 6 5 4
    assert text.endswith("ﱳﱲ")
    assert text.startswith("ﱷ")

def test_empty_words():
    assert assemble_mushaf_line_text([]) == ""
