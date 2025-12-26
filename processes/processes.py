from processes.video_utils import generate_video
from processes.youtube_utils import upload_to_youtube
from processes.screenshot import extract_frame
from processes.surah_video import generate_surah
from config_manager import config_manager

def create_and_post(surah: int, start_verse: int, end_verse:int, 
                    reciter: str, is_short:bool = False):
    video_details = generate_video(surah, start_verse, end_verse, reciter, is_short)
    
    if not video_details:
        raise Exception("Error generating video")
    
    screenshot_path = extract_frame(video_path=video_details["video"])
    video_details["screenshot"] = screenshot_path
    
    # Upload to YouTube if enabled in config
    if config_manager.get("UPLOAD_TO_YOUTUBE") == "True":
        try:
            upload_to_youtube(video_details)
        except Exception as e:
            print(f"YouTube upload failed: {e}")


def manual_upload_to_youtube(video_filename: str, reciter_key: str, playlist_id: str, details_filename: str):
    import os
    from processes.youtube_utils import upload_to_youtube
    
    video_path = os.path.join("exported_data/videos", video_filename)
    details_path = os.path.join("exported_data/details", details_filename)
    
    # Try to find screenshot
    # Need to infer surah and rest from filename to match screenshot pattern
    import re
    match = re.match(r'quran_video_(\d+)_(.+)\.mp4', video_filename)
    screenshot_path = None
    if match:
        surah_num = match.group(1)
        rest = match.group(2)
        screenshot_dir = "exported_data/screenshots"
        # Try exact and normalized matches like in discover_assets
        potential_path = os.path.join(screenshot_dir, f"screenshot_quran_video_{surah_num}_{rest}.png")
        if os.path.exists(potential_path):
            screenshot_path = potential_path
        else:
            def normalize(s):
                return re.sub(r'[^a-z0-9]', '', s.lower())
            for s_file in os.listdir(screenshot_dir):
                if s_file.startswith(f"screenshot_quran_video_{surah_num}_") and normalize(s_file) == normalize(f"screenshot_quran_video_{surah_num}_{rest}.png"):
                    screenshot_path = os.path.join(screenshot_dir, s_file)
                    break

    video_details = {
        "video": video_path,
        "info": details_path,
        "screenshot": screenshot_path,
        "reciter": reciter_key,
        "is_short": False # Manual upload for now assumes full videos
    }
    
    # Existing upload_to_youtube expects a specific structure and uses its own internal playlist mapping
    # We might need to override the playlist_id if it's provided manually
    
    # To avoid changing youtube_utils.py too much, let's temporarily patch its 'playlist' dict or handle it here
    from processes import youtube_utils
    original_playlist = youtube_utils.playlist.copy()
    if playlist_id:
        youtube_utils.playlist[reciter_key] = playlist_id
    
    try:
        upload_to_youtube(video_details)
    finally:
        # Restore original playlist map
        youtube_utils.playlist = original_playlist
        
def create_surah_video(surah: int, reciter: str):
    video_details = generate_surah(surah, reciter)
    if not video_details:
        raise Exception("Error generating video")
    
    screenshot_path = extract_frame(video_path=video_details["video"])
    video_details["screenshot"] = screenshot_path
    
    # Upload to YouTube if enabled in config
    if config_manager.get("UPLOAD_TO_YOUTUBE") == "True":
        try:
            upload_to_youtube(video_details)
        except Exception as e:
            print(f"YouTube upload failed: {e}")