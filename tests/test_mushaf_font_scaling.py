import pytest
from factories.single_clip import calculate_mushaf_font_size

def test_font_size_function_exists():
    assert calculate_mushaf_font_size is not None

def test_font_size_ayah_scaling():
    width = 1000
    line_height = 100
    l_type = "ayah"
    
    # Baseline: 0.7 * line_height = 70
    # Scale 1.0
    size_1 = calculate_mushaf_font_size(width, line_height, l_type, 1.0)
    assert size_1 == 70
    
    # Scale 0.8
    size_08 = calculate_mushaf_font_size(width, line_height, l_type, 0.8)
    assert size_08 == 56 # 70 * 0.8 = 56
    
    # Scale 1.5
    size_15 = calculate_mushaf_font_size(width, line_height, l_type, 1.5)
    assert size_15 == 105 # 70 * 1.5 = 105

def test_font_size_headers_no_scaling():
    # Headers should NOT be affected by MUSHAF_FONT_SCALE based on my assumption, 
    # but the prompt said "make the normal text 20% smaller". 
    # Usually headers are distinct. The spec says "Scope: ... Arabic text rendered in the Mushaf grid (Ayah lines)".
    
    width = 1000
    line_height = 100
    
    # Surah Header: width * 0.15 = 150
    size_header = calculate_mushaf_font_size(width, line_height, "surah_name", 0.5)
    assert size_header == 150
    
    # Bismillah: line_height * 1.3 = 130
    size_bsml = calculate_mushaf_font_size(width, line_height, "basmallah", 0.5)
    assert size_bsml == 130
