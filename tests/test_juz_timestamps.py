import unittest
from unittest.mock import MagicMock
import os
import sys

# Add project root to sys.path
sys.path.append(os.getcwd())

# We want to test the logic that determines the offsets passed to generate_juz_details
# In mushaf_video.py, this happens in prepare_juz_data_package and generate_juz_video

class TestJuzTimestamps(unittest.TestCase):
    def test_offset_calculation_logic(self):
        """
        Simulate the logic in mushaf_video.py to ensure offsets include intro silence.
        """
        # Simulation parameters (in MS)
        intro_silence_ms = 5000
        bsml_ms = 4500 # Simulated basmallah duration
        bsml_silence_ms = 1000
        surah_durations_ms = {
            1: 120000, # 2 mins
            2: 300000  # 5 mins
        }
        
        # Current Logic (Simplified)
        offsets = {}
        current_offset_ms = 0
        
        # 1. prepare_juz_data_package logic
        for s_num in [1, 2]:
            if s_num != 1: # Basmallah injection
                current_offset_ms += bsml_ms
                current_offset_ms += bsml_silence_ms
            
            offsets[s_num] = current_offset_ms
            current_offset_ms += surah_durations_ms[s_num]
            
        # 2. generate_juz_video logic (The shift)
        recitation_start_offset_ms = 5000
        
        # BUG: This shift is currently only applied to all_wbw_timestamps, NOT to 'offsets'
        # Let's see what happens if we apply it to offsets too
        final_offsets = {s_num: off + recitation_start_offset_ms for s_num, off in offsets.items()}
        
        # Expected:
        # Surah 1: 0 + 5000 = 5000ms (00:05)
        # Surah 2: (0 + 120000 + 4500 + 1000) + 5000 = 130500ms (02:10.5)
        
        self.assertEqual(final_offsets[1], 5000)
        self.assertEqual(final_offsets[2], 130500)

if __name__ == "__main__":
    unittest.main()
