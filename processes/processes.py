from processes.video_utils import generate_video
from processes.youtube_utils import upload_to_youtube
from processes.screenshot import extract_frame
from crud.youtubevideo import add_youtubevideo_record
from settings.database import async_session

def create_and_post(surah: int, start_verse: int, end_verse:int, 
                    reciter: str, is_short:bool = False):
    video_details = generate_video(surah, start_verse, end_verse, reciter, is_short)
    
    if not video_details:
        raise Exception("Error generating video")
    
    screenshot_path = extract_frame(video_path=video_details["video"])
    
    # Add metdata to video details
    video_details["screenshot"] = screenshot_path
    video_details["surah"] = surah
    video_details["start_verse"] = start_verse
    video_details["end_verse"] = end_verse
    video_details["reciter"] = reciter
    video_details["is_short"] = is_short
    
    #Upload to YouTube
    try:
        yt_video_details = upload_to_youtube(video_details)
        with async_session() as session:
            add_youtubevideo_record(session, yt_video_details)
        
    except Exception as e:
        print(str(e))