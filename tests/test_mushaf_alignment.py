import pytest
from factories.single_clip import calculate_centered_y

def test_centering_logic_exists():
    assert calculate_centered_y is not None

@pytest.mark.parametrize("line_type, expected_adjustment", [
    ("ayah", 0),
    ("basmallah", 1.2), # 100 * 0.012
    ("surah_name", 1.2), # 100 * 0.012
])
def test_calculate_centered_y(line_type, expected_adjustment):
    y_pos = 100
    line_height = 100
    visual_height = 40
    
    # Simple centering: y_pos + (line_height / 2) - (visual_height / 2)
    # 100 + 50 - 20 = 130
    
    expected = 130 + expected_adjustment
    actual = calculate_centered_y(y_pos, line_height, visual_height, line_type)
    
    assert pytest.approx(actual) == expected

