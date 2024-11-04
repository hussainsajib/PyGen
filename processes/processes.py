from processes.video_utils import generate_video
from processes.youtube_utils import upload_to_youtube

def create_and_post(surah: int, start_verse: int = 1, end_verse:int = 1):
    video_path = generate_video(surah, start_verse, end_verse)
    
    if not video_path:
        raise Exception("Error generating video")
    
    # Upload to YouTube
    #youtube_url = upload_to_youtube(video_path)