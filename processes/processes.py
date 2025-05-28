from sqlite3 import Connection

from processes.video_utils import generate_video
from processes.youtube_utils import upload_to_youtube
from processes.screenshot import extract_frame
from processes.surah_video import generate_surah


def create_and_post(surah: int, start_verse: int, end_verse:int, 
                    reciter: str, is_short:bool = False):
    video_details = generate_video(surah, start_verse, end_verse, reciter, is_short)
    
    if not video_details:
        raise Exception("Error generating video")
    
    screenshot_path = extract_frame(video_path=video_details["video"])
    video_details["screenshot"] = screenshot_path
    
    #Upload to YouTube
    # try:
    #     upload_to_youtube(video_details)
    # except Exception as e:
    #     print(str(e))
        
def create_surah_video(surah: int, reciter: str):
    video_details = generate_surah(surah, reciter)
    if not video_details:
        raise Exception("Error generating video")
    
    screenshot_path = extract_frame(video_path=video_details["video"])
    video_details["screenshot"] = screenshot_path
    
    #Upload to YouTube
    try:
        upload_to_youtube(video_details)
    except Exception as e:
        print(str(e))
    