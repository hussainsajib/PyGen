import pytest
from unittest.mock import patch, MagicMock, AsyncMock
from processes.surah_video import create_wbw_advanced_ayah_clip
from processes.Classes import Surah, Reciter

@pytest.mark.parametrize("reciter_key, reciter_name", [
    ("ar.mahermuaiqly", "Maher Al Muaiqly"),
    ("ar.alafasy", "Mishary Rashid Alafasy"),
    ("ar.shuraym", "Sa'ud al-Shuraym")
])
@pytest.mark.asyncio
async def test_full_translation_consistency_multiple_reciters(reciter_key, reciter_name):
    """Verifies that multiple reciters correctly trigger full translation overlay logic."""
    
    # We need to mock everything that create_wbw_advanced_ayah_clip calls
    with patch("processes.surah_video.get_resolution") as mock_res, \
         patch("processes.surah_video.get_wbw_text_for_ayah") as mock_get_text, \
         patch("processes.surah_video.get_wbw_translation_for_ayah") as mock_get_trans, \
         patch("processes.surah_video.config_manager") as mock_config, \
         patch("processes.surah_video.segment_words_with_timestamps") as mock_segment, \
         patch("processes.surah_video.generate_background") as mock_gen_bg, \
         patch("processes.surah_video.generate_wbw_interlinear_text_clip") as mock_gen_inter, \
         patch("processes.surah_video.generate_reciter_name_clip") as mock_gen_reciter, \
         patch("processes.surah_video.generate_surah_info_clip") as mock_gen_surah_info, \
         patch("processes.surah_video.generate_brand_clip") as mock_gen_brand, \
         patch("processes.surah_video.generate_full_ayah_translation_clip") as mock_gen_full_trans_clip, \
         patch("processes.surah_video.get_full_translation_for_ayah") as mock_get_full_trans, \
         patch("processes.surah_video.CompositeVideoClip") as mock_composite, \
         patch("processes.surah_video.concatenate_videoclips") as mock_concat, \
         patch("processes.surah_video.concatenate_audioclips") as mock_audio_concat, \
         patch("processes.surah_video.make_silence") as mock_silence:

        # Setup basic return values
        mock_res.return_value = (1920, 1080)
        mock_get_text.return_value = ["word1"]
        mock_get_trans.return_value = ["trans1"]
        
        def config_get_side_effect(key, default=None):
            if key == "WBW_FULL_TRANSLATION_ENABLED": return "True"
            if key == "WBW_INTERLINEAR_ENABLED": return "True"
            if key == "WBW_DELAY_BETWEEN_AYAH": return "0" # Disable delay to simplify
            return default
        mock_config.get.side_effect = config_get_side_effect
        
        mock_segment.return_value = [{
            "words": ["word1"],
            "translations": ["trans1"],
            "start_ms": 0,
            "end_ms": 1000
        }]
        
        mock_get_full_trans.return_value = "Full Ayah Translation"
        
        mock_clip = MagicMock()
        mock_clip.duration = 1.0
        mock_clip.set_duration.return_value = mock_clip
        mock_clip.set_audio.return_value = mock_clip
        
        mock_gen_bg.return_value = mock_clip
        mock_gen_inter.return_value = mock_clip
        mock_gen_reciter.return_value = mock_clip
        mock_gen_surah_info.return_value = mock_clip
        mock_gen_brand.return_value = mock_clip
        mock_gen_full_trans_clip.return_value = mock_clip
        mock_composite.return_value = mock_clip
        mock_concat.return_value = mock_clip

        surah = MagicMock(spec=Surah)
        surah.number = 1
        reciter = MagicMock(spec=Reciter)
        reciter.english_name = reciter_name
        reciter.bangla_name = "তিলাওয়াতকারী"
        
        full_audio = MagicMock()
        full_audio.duration = 10.0
        full_audio.subclip.return_value = mock_clip
        
        segments = [[1, 0, 1000]]

        # Execute
        # Note: create_wbw_advanced_ayah_clip is NOT async, it's a regular function
        # (My previous call was 'await' which was wrong based on the source)
        from processes.surah_video import create_wbw_advanced_ayah_clip
        result = create_wbw_advanced_ayah_clip(
            surah=surah,
            ayah=1,
            reciter=reciter,
            full_audio=full_audio,
            is_short=False,
            segments=segments,
            brand_name="Taqwa"
        )

        # Verify
        mock_gen_full_trans_clip.assert_called()
        print(f"Verified full translation clip for reciter: {reciter_name}")

if __name__ == "__main__":
    # For manual run
    import asyncio
    asyncio.run(test_full_translation_consistency_multiple_reciters("ar.alafasy", "Alafasy"))
