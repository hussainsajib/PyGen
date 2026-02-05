import os

def test_benchmark_script_exists():
    assert os.path.exists("scripts/benchmark_mushaf_gen.py")
