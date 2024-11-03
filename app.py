import os

from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from video_utils import generate_video
from youtube_utils import upload_to_youtube

load_dotenv()
IMAGEMAGICK_BINARY=os.getenv("IMAGEMAGICK_BINARY")

app = FastAPI()

from moviepy.config import change_settings
change_settings({"IMAGEMAGICK_BINARY": IMAGEMAGICK_BINARY})


@app.get("/create-video")
async def create_video(surah: int, start_verse: int, end_verse: int):
    # Fetch video file path after video generation
    video_path = generate_video(surah, start_verse, end_verse)
    
    if not video_path:
        raise HTTPException(status_code=500, detail="Error generating video")
    
    # Upload to YouTube
    #youtube_url = upload_to_youtube(video_path)
    return {"youtube_url": "youtube_url"}
