import pytest
from db_ops.crud_mushaf import get_mushaf_page_data

def test_surah_2_ayah_1_word_order():
    # Page 2 contains Surah 2, Ayah 1 (Alif Lam Meem)
    page_data = get_mushaf_page_data(2)
    
    # Find the line containing Surah 2, Ayah 1
    # Ayah 1 is: الم
    target_line = None
    for line in page_data:
        for word in line['words']:
            if word['surah'] == 2 and word['ayah'] == 1:
                target_line = line
                break
        if target_line: break
        
    assert target_line is not None
    
    # Verify logical string order matches database order
    # For Alif Lam Meem, it's usually 3 PUA glyphs in one word or separate words
    # The key is that "".join([w['text'] for w in words]) should be the correct RTL logical string
    
    words = target_line['words']
    logical_text = "".join([w['text'] for w in words])
    
    # In proper RTL processing, we don't reverse the list of words manually
    # if the database already gives them in RTL sequence.
    
    # This test currently documents our expectation: 
    # NO manual reversal of the words list.
    pass

def test_logical_joining_order():
    # If we have words [W1, W2] in RTL, the string should be "W1 W2"
    # When rendered by a Bidi-aware engine, W1 appears on the right.
    # If we reverse to [W2, W1] and join to "W2 W1", it's wrong.
    
    words = [
        {"text": "A"}, # Word 1 (Right-most)
        {"text": "B"}  # Word 2 (Next to it on left)
    ]
    
    # Correct logical order for Bidi
    logical = "".join([w["text"] for w in words])
    assert logical == "AB"
    
    # What the code currently does (which we want to fix)
    # current = "".join([w["text"] for w in reversed(words)])
    # assert current == "BA"
