import pytest
from db.models.media_asset import MediaAsset

def test_create_media_asset():
    asset = MediaAsset(
        video_path="videos/test.mp4",
        screenshot_path="screenshots/test.png",
        details_path="details/test.txt",
        surah_number=1,
        start_ayah=1,
        end_ayah=7,
        reciter_key="ar.alafasy",
        generation_status="success"
    )
    assert asset.video_path == "videos/test.mp4"
    assert asset.surah_number == 1
