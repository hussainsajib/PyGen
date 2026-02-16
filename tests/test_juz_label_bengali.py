import pytest
from factories.single_clip import e2b

def test_juz_label_bengali_conversion():
    # Test Juz 1 to Para 1 in Bengali
    juz_num = 1
    label = f"পারা {e2b(str(juz_num))}"
    assert label == "পারা ১"
    
    # Test Juz 30 to Para 30 in Bengali
    juz_num = 30
    label = f"পারা {e2b(str(juz_num))}"
    assert label == "পারা ৩০"

def test_e2b_directly():
    assert e2b("1") == "১"
    assert e2b("2") == "২"
    assert e2b("3") == "৩"
    assert e2b("4") == "৪"
    assert e2b("5") == "৫"
    assert e2b("6") == "৬"
    assert e2b("7") == "৭"
    assert e2b("8") == "৮"
    assert e2b("9") == "৯"
    assert e2b("0") == "০"
    assert e2b("10") == "১০"
