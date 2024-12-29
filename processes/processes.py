from processes.video_utils import generate_video
from processes.youtube_utils import upload_to_youtube
from processes.screenshot import extract_frame

def create_and_post(surah: int, start_verse: int, end_verse:int, 
                    reciter: str, is_short:bool = False):
    video_path = generate_video(surah, start_verse, end_verse, reciter, is_short)
    
    if not video_path:
        raise Exception("Error generating video")
    
    extract_frame(video_path)
    
    # Upload to YouTube
    # try:
    #     youtube_url = upload_to_youtube(video_path)
    #     print(youtube_url)
    # except Exception as e:
    #     print(str(e))