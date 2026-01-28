import pytest
from factories.single_clip import calculate_mushaf_content_y_positions

def test_vertical_centering_full_page():
    height = 1920
    num_lines = 15
    line_height = (height * 0.8) / 15 # 102.4
    
    # If 15 lines, it should perfectly fit the 0.8 usable height area, 
    # so top_margin should remain height * 0.1 = 192
    
    positions = calculate_mushaf_content_y_positions(height, num_lines, has_header_gap=False)
    assert positions[0] == pytest.approx(192.0)

def test_vertical_centering_partial_page():
    height = 1000
    num_lines = 2
    # Standard line_height would be (1000 * 0.8) / 15 = 53.33
    line_height = 53.333333333333336
    
    # Total content height = 2 * 53.33 = 106.66
    # Center Y = 500
    # Start Y = 500 - (106.66 / 2) = 500 - 53.33 = 446.67
    
    positions = calculate_mushaf_content_y_positions(height, num_lines, has_header_gap=False)
    assert positions[0] == pytest.approx(446.6666666666667)

def test_header_gap_increment():
    height = 1920
    num_lines = 3
    # has_header_gap=True should add 20px between line 0 and line 1
    
    positions = calculate_mushaf_content_y_positions(height, num_lines, has_header_gap=True)
    
    # Standard line_height = 102.4
    # Content height = (3 * 102.4) + 20 = 307.2 + 20 = 327.2
    # Start Y = 960 - (327.2 / 2) = 960 - 163.6 = 796.4
    
    assert positions[0] == pytest.approx(796.4)
    # Line 1 should be at Start Y + line_height + 20
    assert positions[1] == pytest.approx(796.4 + 102.4 + 20)
    # Line 2 should be at Start Y + 2*line_height + 20
    assert positions[2] == pytest.approx(796.4 + 2 * 102.4 + 20)
