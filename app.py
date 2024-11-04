import os

from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException, BackgroundTasks

from processes.video_utils import generate_video
from processes.youtube_utils import upload_to_youtube
from processes.processes import create_and_post

load_dotenv()
IMAGEMAGICK_BINARY=os.getenv("IMAGEMAGICK_BINARY")

app = FastAPI()

from moviepy.config import change_settings
change_settings({"IMAGEMAGICK_BINARY": IMAGEMAGICK_BINARY})


@app.get("/create-video")
async def create_video(surah: int, start_verse: int, end_verse: int, background_tasks: BackgroundTasks):
    background_tasks.add_task(create_and_post, surah, start_verse, end_verse)
    return {"message": "Video creation and posting is added to the queue"}
