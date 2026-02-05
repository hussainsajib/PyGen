import os

def test_profiling_scripts_exist():
    assert os.path.exists("scripts/profile_text_rendering.py")
